#!/usr/bin/env python3
"""Held-out falsification of the frozen NULL_COUPLED v3 winner.

This script never re-ranks v1 model families. It generates only NULL_COUPLED
prior-predictive responses, applies the same nested multivariate R2 and
Freedman-Lane support logic used by the Azami incremental environment analysis,
and asks how often the predeclared held-out support geometry is reproduced.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from simulate_azami_capitulum_v3_conditional import generate


def stable_rng(seed: int, *parts: str) -> np.random.Generator:
    payload = "|".join([str(seed), *parts]).encode()
    return np.random.default_rng(int.from_bytes(hashlib.sha256(payload).digest()[:8], "little"))


def bh_adjust(values: pd.Series) -> pd.Series:
    p = values.to_numpy(float)
    if len(p) == 0:
        return pd.Series(index=values.index, dtype=float)
    order = np.argsort(p)
    ranked = p[order]
    adj = ranked * len(p) / np.arange(1, len(p) + 1)
    adj = np.minimum.accumulate(adj[::-1])[::-1]
    out = np.empty(len(p), float)
    out[order] = np.clip(adj, 0, 1)
    return pd.Series(out, index=values.index)


def weighted_standardize(a: np.ndarray, weights: np.ndarray) -> np.ndarray:
    w = weights / weights.sum()
    mu = (w[:, None] * a).sum(axis=0)
    var = (w[:, None] * (a - mu) ** 2).sum(axis=0)
    sd = np.sqrt(var)
    if np.any(~np.isfinite(sd)) or np.any(sd <= 0):
        raise ValueError("zero/invalid weighted standard deviation")
    return (a - mu) / sd


def standardize(a: np.ndarray) -> np.ndarray:
    a = np.asarray(a, float)
    sd = a.std(axis=0, ddof=0)
    if np.any(~np.isfinite(sd)) or np.any(sd <= 0):
        raise ValueError("zero/invalid standard deviation")
    return (a - a.mean(axis=0)) / sd


def fit_wls(y: np.ndarray, x: np.ndarray, weights: np.ndarray) -> tuple[float, np.ndarray, np.ndarray]:
    sw = np.sqrt(weights)[:, None]
    beta = np.linalg.lstsq(x * sw, y * sw, rcond=None)[0]
    fitted = x @ beta
    residual = y - fitted
    sse = float((weights[:, None] * residual ** 2).sum())
    sst = float((weights[:, None] * y ** 2).sum())
    return float(1.0 - sse / sst), fitted, residual


def fit_ols(y: np.ndarray, x: np.ndarray) -> tuple[float, np.ndarray, np.ndarray]:
    beta = np.linalg.lstsq(x, y, rcond=None)[0]
    fitted = x @ beta
    residual = y - fitted
    sse = float((residual ** 2).sum())
    sst = float((y ** 2).sum())
    return float(1.0 - sse / sst), fitted, residual


def prepare_within(
    table: pd.DataFrame, endpoints: list[str], core: list[str], extension: list[str]
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    groups = table["taxon_name"].astype(str)
    ydf = table[endpoints].astype(float)
    xc = table[core].astype(float)
    xe = table[extension].astype(float)
    y = (ydf - ydf.groupby(groups).transform("mean")).to_numpy(float)
    xcore = (xc - xc.groupby(groups).transform("mean")).to_numpy(float)
    xext = (xe - xe.groupby(groups).transform("mean")).to_numpy(float)
    counts = table.groupby("taxon_name").size()
    weights = 1.0 / table["taxon_name"].map(counts).to_numpy(float)
    return (
        weighted_standardize(y, weights),
        weighted_standardize(xcore, weights),
        weighted_standardize(xext, weights),
        weights,
        groups.to_numpy(),
    )


def prepare_among(
    table: pd.DataFrame, endpoints: list[str], core: list[str], extension: list[str]
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    med = table.groupby("taxon_name")[endpoints + core + extension].median().dropna()
    return (
        standardize(med[endpoints].to_numpy(float)),
        standardize(med[core].to_numpy(float)),
        standardize(med[extension].to_numpy(float)),
    )


def nested_wls(y: np.ndarray, xc: np.ndarray, xe: np.ndarray, weights: np.ndarray):
    r2c, fitted, residual = fit_wls(y, xc, weights)
    r2f, _, _ = fit_wls(y, np.column_stack([xc, xe]), weights)
    return r2c, r2f, max(0.0, r2f - r2c), fitted, residual


def nested_ols(y: np.ndarray, xc: np.ndarray, xe: np.ndarray):
    r2c, fitted, residual = fit_ols(y, xc)
    r2f, _, _ = fit_ols(y, np.column_stack([xc, xe]))
    return r2c, r2f, max(0.0, r2f - r2c), fitted, residual


def permute_rows_within(values: np.ndarray, groups: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    out = values.copy()
    for group in np.unique(groups):
        idx = np.flatnonzero(groups == group)
        out[idx] = values[rng.permutation(idx)]
    return out


def freedman_lane_within(
    y: np.ndarray,
    xc: np.ndarray,
    xe: np.ndarray,
    weights: np.ndarray,
    groups: np.ndarray,
    observed_delta: float,
    fitted: np.ndarray,
    residual: np.ndarray,
    permutations: int,
    rng: np.random.Generator,
) -> float:
    full = np.column_stack([xc, xe])
    exceed = 0
    for _ in range(permutations):
        yp = fitted + permute_rows_within(residual, groups, rng)
        r2c, _, _ = fit_wls(yp, xc, weights)
        r2f, _, _ = fit_wls(yp, full, weights)
        if (r2f - r2c) >= observed_delta - 1e-15:
            exceed += 1
    return float((exceed + 1) / (permutations + 1))


def freedman_lane_among(
    y: np.ndarray,
    xc: np.ndarray,
    xe: np.ndarray,
    observed_delta: float,
    fitted: np.ndarray,
    residual: np.ndarray,
    permutations: int,
    rng: np.random.Generator,
) -> float:
    full = np.column_stack([xc, xe])
    exceed = 0
    for _ in range(permutations):
        yp = fitted + residual[rng.permutation(len(residual))]
        r2c, _, _ = fit_ols(yp, xc)
        r2f, _, _ = fit_ols(yp, full)
        if (r2f - r2c) >= observed_delta - 1e-15:
            exceed += 1
    return float((exceed + 1) / (permutations + 1))


def observed_support_from_csv(path: Path) -> dict[tuple[str, str, str], bool]:
    x = pd.read_csv(path, low_memory=False)
    required = {"scope", "scale", "test_id", "supported_0_05"}
    if not required.issubset(x.columns):
        raise ValueError(f"observed support file missing {sorted(required.difference(x.columns))}")
    truth = x["supported_0_05"].astype(str).str.lower().map({"true": True, "false": False})
    if truth.isna().any():
        raise ValueError("observed support contains non-boolean supported_0_05")
    return {
        (str(r.scope), str(r.scale), str(r.test_id)): bool(s)
        for r, s in zip(x.itertuples(index=False), truth)
    }


def contract_support_vector(contract: dict) -> dict[tuple[str, str, str], bool]:
    out: dict[tuple[str, str, str], bool] = {}
    for scope, scales in contract["observed_support_vector"].items():
        for scale, tests in scales.items():
            for test_id, supported in tests.items():
                out[(scope, scale, test_id)] = bool(supported)
    return out


def validate_observed_vector(contract: dict, observed_path: Path) -> dict[tuple[str, str, str], bool]:
    observed = observed_support_from_csv(observed_path)
    expected = contract_support_vector(contract)
    if observed != expected:
        missing = sorted(set(expected).difference(observed))
        extra = sorted(set(observed).difference(expected))
        mismatched = sorted(k for k in set(expected).intersection(observed) if expected[k] != observed[k])
        raise ValueError(f"held-out observed support vector mismatch: missing={missing}, extra={extra}, mismatched={mismatched}")
    if len(expected) != 20:
        raise ValueError(f"expected 20 held-out support cells, found {len(expected)}")
    return expected


def run_draw(
    design: pd.DataFrame,
    generator_contract: dict,
    estimand_contract: dict,
    heldout_contract: dict,
    seed: int,
) -> pd.DataFrame:
    observations = generate(design, "NULL_COUPLED", seed, generator_contract, strict_frozen_design=True)
    endpoints = estimand_contract["response_endpoints"]
    inc = estimand_contract["incremental_environment_estimands"]
    core = inc["core_predictors"]
    specs = inc["tests"]
    permutations = int(heldout_contract["nested_test"]["permutations_per_test"])
    alpha = float(heldout_contract["nested_test"]["support_threshold"])
    rows: list[dict[str, Any]] = []

    for threshold in [5, 2]:
        counts = observations.groupby("taxon_name").size()
        keep = counts[counts >= threshold].index
        table = observations[observations["taxon_name"].isin(keep)].copy()
        scope = f"complete18_env_min{threshold}"
        for spec in specs:
            test_id = spec["test_id"]
            family = spec["family"]
            ext = spec["extension_predictors"]

            yw, xcw, xew, weights, groups = prepare_within(table, endpoints, core, ext)
            r2c, r2f, delta, fitted, residual = nested_wls(yw, xcw, xew, weights)
            pw = freedman_lane_within(
                yw, xcw, xew, weights, groups, delta, fitted, residual, permutations,
                stable_rng(seed, scope, test_id, "within_freedman_lane"),
            )
            rows.append({
                "seed": seed, "scope": scope, "scale": "within_taxon", "test_id": test_id,
                "test_family": family, "r2_core4": r2c, "r2_full": r2f,
                "delta_r2": delta, "partial_r2": delta / max(1e-15, 1.0 - r2c),
                "permutation_p": pw,
            })

            ya, xca, xea = prepare_among(table, endpoints, core, ext)
            r2c, r2f, delta, fitted, residual = nested_ols(ya, xca, xea)
            pa = freedman_lane_among(
                ya, xca, xea, delta, fitted, residual, permutations,
                stable_rng(seed, scope, test_id, "among_freedman_lane"),
            )
            rows.append({
                "seed": seed, "scope": scope, "scale": "among_taxon", "test_id": test_id,
                "test_family": family, "r2_core4": r2c, "r2_full": r2f,
                "delta_r2": delta, "partial_r2": delta / max(1e-15, 1.0 - r2c),
                "permutation_p": pa,
            })

    result = pd.DataFrame(rows)
    result["q_bh_block_specific"] = np.nan
    block = result["test_family"].eq("block_specific")
    for (_scope, _scale), idx in result[block].groupby(["scope", "scale"]).groups.items():
        result.loc[idx, "q_bh_block_specific"] = bh_adjust(result.loc[idx, "permutation_p"].astype(float))
    result["supported_0_05"] = False
    omni = result["test_family"].eq("omnibus")
    result.loc[omni, "supported_0_05"] = result.loc[omni, "permutation_p"].lt(alpha)
    result.loc[block, "supported_0_05"] = result.loc[block, "q_bh_block_specific"].lt(alpha)
    if len(result) != 20:
        raise RuntimeError(f"draw {seed} produced {len(result)} tests instead of 20")
    return result


def primary_cells(contract: dict) -> list[tuple[str, str, str, bool]]:
    return [tuple(x) for x in contract["primary_held_out_pattern"]["required_cells"]]


def summarize_draws(test_ledger: pd.DataFrame, observed: dict, contract: dict) -> pd.DataFrame:
    pcells = primary_cells(contract)
    rows = []
    for seed, g in test_ledger.groupby("seed", sort=True):
        got = {(r.scope, r.scale, r.test_id): bool(r.supported_0_05) for r in g.itertuples(index=False)}
        full_matches = sum(got[k] == observed[k] for k in observed)
        primary_match = all(got[(scope, scale, test)] == bool(expected) for scope, scale, test, expected in pcells)
        exact_match = full_matches == len(observed)
        row = {
            "seed": int(seed),
            "primary_pattern_match": bool(primary_match),
            "exact_20_cell_match": bool(exact_match),
            "matching_cells_out_of_20": int(full_matches),
        }
        for scope in ["complete18_env_min5", "complete18_env_min2"]:
            for scale in ["within_taxon", "among_taxon"]:
                row[f"supported_count__{scope}__{scale}"] = int(sum(
                    got[(scope, scale, test)] for test in contract["nested_test"]["tests"]
                ))
        rows.append(row)
    return pd.DataFrame(rows)


def cell_frequencies(test_ledger: pd.DataFrame, observed: dict) -> pd.DataFrame:
    rows = []
    for (scope, scale, test_id), g in test_ledger.groupby(["scope", "scale", "test_id"], sort=True):
        freq = float(g["supported_0_05"].mean())
        obs = bool(observed[(scope, scale, test_id)])
        rows.append({
            "scope": scope, "scale": scale, "test_id": test_id,
            "observed_supported": obs,
            "null_support_frequency": freq,
            "null_frequency_of_observed_state": freq if obs else 1.0 - freq,
        })
    return pd.DataFrame(rows)


def wilson_interval(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n <= 0:
        return float("nan"), float("nan")
    p = k / n
    den = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, centre - half), min(1.0, centre + half)


def final_decision(draw_summary: pd.DataFrame, contract: dict) -> dict:
    n = len(draw_summary)
    k = int(draw_summary["primary_pattern_match"].sum())
    full = int(draw_summary["exact_20_cell_match"].sum())
    lo, hi = wilson_interval(k, n)
    if k <= 1:
        classification = "not_reproduced_or_exceptional"
    elif k <= 6:
        classification = "rare"
    else:
        classification = "compatible_frequency"
    return {
        "status": "completed_held_out_validation",
        "frozen_v1_winner": "NULL_COUPLED",
        "v1_winner_changed": False,
        "validation_draws": n,
        "permutations_per_test": int(contract["nested_test"]["permutations_per_test"]),
        "primary_pattern_matches": k,
        "primary_pattern_frequency": k / n,
        "primary_pattern_wilson95_low": lo,
        "primary_pattern_wilson95_high": hi,
        "primary_pattern_classification": classification,
        "exact_20_cell_matches": full,
        "exact_20_cell_frequency": full / n,
        "median_matching_cells_out_of_20": float(draw_summary["matching_cells_out_of_20"].median()),
        "claim_boundary": contract["claim_boundary"],
        "stop_rule": contract["stop_rule"],
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--design", required=True, type=Path)
    p.add_argument("--observed-incremental", required=True, type=Path)
    p.add_argument("--generator-contract", type=Path, default=Path("data/evidence/azami_capitulum_v3_generator_contract_v1.json"))
    p.add_argument("--estimand-contract", type=Path, default=Path("data/evidence/azami_capitulum_v3_estimand_contract_v1.json"))
    p.add_argument("--heldout-contract", type=Path, default=Path("data/evidence/azami_capitulum_v3_null_heldout_support_contract_v1.json"))
    p.add_argument("--out-dir", required=True, type=Path)
    args = p.parse_args()

    generator_contract = json.loads(args.generator_contract.read_text(encoding="utf-8"))
    estimand_contract = json.loads(args.estimand_contract.read_text(encoding="utf-8"))
    heldout_contract = json.loads(args.heldout_contract.read_text(encoding="utf-8"))
    if heldout_contract["status"] != "frozen_before_held_out_null_support_simulation":
        raise ValueError("held-out contract is not in frozen pre-simulation state")
    observed = validate_observed_vector(heldout_contract, args.observed_incremental)
    design = pd.read_csv(args.design, low_memory=False)
    seeds = [int(x) for x in heldout_contract["validation_draws"]["seeds"]]
    if len(seeds) != int(heldout_contract["validation_draws"]["count"]):
        raise ValueError("validation draw count does not equal frozen seed count")

    ledgers = []
    for seed in seeds:
        ledgers.append(run_draw(design, generator_contract, estimand_contract, heldout_contract, seed))
    ledger = pd.concat(ledgers, ignore_index=True)
    draws = summarize_draws(ledger, observed, heldout_contract)
    cells = cell_frequencies(ledger, observed)
    decision = final_decision(draws, heldout_contract)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    ledger.to_csv(args.out_dir / "azami_capitulum_v3_null_heldout_support_test_ledger_v1.csv", index=False)
    draws.to_csv(args.out_dir / "azami_capitulum_v3_null_heldout_support_draw_summary_v1.csv", index=False)
    cells.to_csv(args.out_dir / "azami_capitulum_v3_null_heldout_support_cell_frequencies_v1.csv", index=False)
    (args.out_dir / "azami_capitulum_v3_null_heldout_support_decision_v1.json").write_text(
        json.dumps(decision, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(decision, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
