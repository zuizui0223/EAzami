#!/usr/bin/env python3
"""Compute the 62 Azami capitulum handoff estimands from model observation rows.

This is a statistics adapter, not a simulator.  It deliberately requires a model
to emit the same 18 response endpoints and nine environmental predictors before
any Azami target becomes scoreable.  The formulas mirror Azami PR #72's frozen
functional-space, environmental-block and nested-increment analyses, omitting
bootstrap/permutation uncertainty because EAzami model distance uses the frozen
observed scalar target values.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

HUE_COMPONENTS = ["corolla_hue_sin", "corolla_hue_cos"]
HUE_UNIT = "corolla_hue"


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


def weighted_corr(frame: pd.DataFrame, weights: np.ndarray) -> pd.DataFrame:
    a = frame.to_numpy(float)
    w = np.asarray(weights, float)
    w = w / w.sum()
    mu = (w[:, None] * a).sum(axis=0)
    z = a - mu
    cov = (w[:, None] * z).T @ z
    sd = np.sqrt(np.diag(cov))
    denom = np.outer(sd, sd)
    corr = np.divide(cov, denom, out=np.zeros_like(cov), where=denom > 0)
    np.fill_diagonal(corr, 1.0)
    return pd.DataFrame(corr, index=frame.columns, columns=frame.columns)


def hue_multiple_r(corr: pd.DataFrame, other: str) -> float:
    r = corr.loc[other, HUE_COMPONENTS].to_numpy(float)
    rx = corr.loc[HUE_COMPONENTS, HUE_COMPONENTS].to_numpy(float)
    r2 = float(r @ np.linalg.pinv(rx) @ r)
    return float(np.sqrt(max(0.0, min(1.0, r2))))


def unit_strength(corr: pd.DataFrame, left: str, right: str) -> float:
    if left == HUE_UNIT:
        return hue_multiple_r(corr, right)
    if right == HUE_UNIT:
        return hue_multiple_r(corr, left)
    return abs(float(corr.loc[left, right]))


def unit_matrix(corr: pd.DataFrame, units: list[str]) -> pd.DataFrame:
    out = pd.DataFrame(np.eye(len(units)), index=units, columns=units, dtype=float)
    for i, left in enumerate(units):
        for right in units[i + 1 :]:
            v = unit_strength(corr, left, right)
            out.loc[left, right] = v
            out.loc[right, left] = v
    return out


def upper_values(matrix: pd.DataFrame) -> np.ndarray:
    a = matrix.to_numpy(float)
    return a[np.triu_indices_from(a, k=1)]


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    ar = pd.Series(a).rank(method="average").to_numpy(float)
    br = pd.Series(b).rank(method="average").to_numpy(float)
    return float(np.corrcoef(ar, br)[0, 1])


def module_contrast(matrix: pd.DataFrame, module_by_unit: dict[str, str]) -> float:
    within, between = [], []
    names = list(matrix.index)
    for i, left in enumerate(names):
        for right in names[i + 1 :]:
            (within if module_by_unit[left] == module_by_unit[right] else between).append(
                float(matrix.loc[left, right])
            )
    return float(np.mean(within) - np.mean(between))


def fit_weighted_block(y: np.ndarray, x: np.ndarray, weights: np.ndarray) -> tuple[float, np.ndarray]:
    yz = weighted_standardize(y, weights)
    xz = weighted_standardize(x, weights)
    sw = np.sqrt(weights)[:, None]
    beta = np.linalg.lstsq(xz * sw, yz * sw, rcond=None)[0]
    fitted = xz @ beta
    r2 = float((weights[:, None] * fitted ** 2).sum() / (weights[:, None] * yz ** 2).sum())
    return r2, beta


def fit_unweighted_block(y: np.ndarray, x: np.ndarray) -> tuple[float, np.ndarray]:
    yz = standardize(y)
    xz = standardize(x)
    beta = np.linalg.lstsq(xz, yz, rcond=None)[0]
    fitted = xz @ beta
    r2 = float((fitted ** 2).sum() / (yz ** 2).sum())
    return r2, beta


def fit_wls_standardized(y: np.ndarray, x: np.ndarray, weights: np.ndarray) -> float:
    sw = np.sqrt(weights)[:, None]
    beta = np.linalg.lstsq(x * sw, y * sw, rcond=None)[0]
    residual = y - x @ beta
    sse = float((weights[:, None] * residual ** 2).sum())
    sst = float((weights[:, None] * y ** 2).sum())
    return float(1.0 - sse / sst)


def fit_ols_standardized(y: np.ndarray, x: np.ndarray) -> float:
    beta = np.linalg.lstsq(x, y, rcond=None)[0]
    residual = y - x @ beta
    return float(1.0 - float((residual ** 2).sum()) / float((y ** 2).sum()))


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    a = a.reshape(-1)
    b = b.reshape(-1)
    den = float(np.linalg.norm(a) * np.linalg.norm(b))
    return float(np.dot(a, b) / den) if den > 0 else float("nan")


def validate_rows(df: pd.DataFrame, contract: dict) -> tuple[list[str], list[str], dict[str, str], list[str]]:
    schema = contract["observation_schema"]
    endpoints = schema["response_endpoints"]
    env = schema["environment_predictors"]
    required = ["obs_id", "taxon_name", *endpoints, *env]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError("model observation table missing exact v3 columns: " + ", ".join(missing))
    if df["obs_id"].astype(str).duplicated().any():
        raise ValueError("obs_id must be unique")
    for col in [*endpoints, *env]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    units = schema["inferential_units"]
    module = schema["endpoint_modules"].copy()
    module[HUE_UNIT] = module[HUE_COMPONENTS[0]]
    module_by_unit = {u: module[u] for u in units}
    return endpoints, env, module_by_unit, units


def retained_response_table(df: pd.DataFrame, endpoints: list[str], threshold: int) -> pd.DataFrame:
    x = df.dropna(subset=endpoints).copy()
    counts = x.groupby("taxon_name").size()
    keep = counts[counts >= threshold].index
    x = x[x["taxon_name"].isin(keep)].copy()
    if x["taxon_name"].nunique() < 3:
        raise ValueError(f"too few taxa after complete18_min{threshold} filtering")
    return x


def within_raw(table: pd.DataFrame, cols: list[str]) -> tuple[np.ndarray, np.ndarray]:
    frame = table[cols].astype(float)
    centered = frame - frame.groupby(table["taxon_name"]).transform("mean")
    counts = table.groupby("taxon_name").size()
    weights = 1.0 / table["taxon_name"].map(counts).to_numpy(float)
    return centered.to_numpy(float), weights


def among_raw(table: pd.DataFrame, cols: list[str]) -> np.ndarray:
    return table.groupby("taxon_name")[cols].median().to_numpy(float)


def structure_rows(table: pd.DataFrame, endpoints: list[str], units: list[str], module_by_unit: dict[str, str], threshold: int) -> list[dict]:
    x = table[endpoints].astype(float)
    centered = x - x.groupby(table["taxon_name"]).transform("mean")
    counts = table.groupby("taxon_name").size()
    weights = 1.0 / table["taxon_name"].map(counts).to_numpy(float)
    within_corr = weighted_corr(centered, weights)
    among_corr = table.groupby("taxon_name")[endpoints].median().corr()
    within_units = unit_matrix(within_corr, units)
    among_units = unit_matrix(among_corr, units)
    scope = f"complete18_min{threshold}"
    return [
        {"target_id": "capitulum_within_module_integration_contrast", "scope": scope, "scale": "within_taxon", "value": module_contrast(within_units, module_by_unit), "target_class": "structure"},
        {"target_id": "capitulum_among_module_integration_contrast", "scope": scope, "scale": "among_taxon", "value": module_contrast(among_units, module_by_unit), "target_class": "structure"},
        {"target_id": "capitulum_cross_scale_association_matrix_similarity", "scope": scope, "scale": "within_vs_among", "value": spearman(upper_values(within_units), upper_values(among_units)), "target_class": "structure"},
    ]


def environment_rows(table: pd.DataFrame, endpoints: list[str], contract: dict, threshold: int) -> list[dict]:
    scope = f"complete18_env_min{threshold}"
    rows = []
    for block in contract["environment_blocks"]:
        predictors = block["predictors"]
        work = table.dropna(subset=predictors).copy()
        if len(work) / len(table) < 0.98:
            raise ValueError(f"environment coverage below 0.98 for {scope}/{block['block_id']}")
        y = work[endpoints].astype(float)
        x = work[predictors].astype(float)
        yc = (y - y.groupby(work["taxon_name"]).transform("mean")).to_numpy(float)
        xc = (x - x.groupby(work["taxon_name"]).transform("mean")).to_numpy(float)
        counts = work.groupby("taxon_name").size()
        weights = 1.0 / work["taxon_name"].map(counts).to_numpy(float)
        rw, bw = fit_weighted_block(yc, xc, weights)
        med = work.groupby("taxon_name")[endpoints + predictors].median().dropna()
        ra, ba = fit_unweighted_block(med[endpoints].to_numpy(float), med[predictors].to_numpy(float))
        rows.extend([
            {"target_id": f"environment_block_r2:{block['block_id']}", "scope": scope, "scale": "within_taxon", "value": rw, "target_class": "environment_block_r2"},
            {"target_id": f"environment_block_r2:{block['block_id']}", "scope": scope, "scale": "among_taxon", "value": ra, "target_class": "environment_block_r2"},
            {"target_id": f"environment_block_cross_scale_cosine:{block['block_id']}", "scope": scope, "scale": "within_vs_among", "value": cosine(bw, ba), "target_class": "environment_geometry"},
        ])
    return rows


def nested_partial_r2(table: pd.DataFrame, endpoints: list[str], core: list[str], ext: list[str], scale: str) -> tuple[float, float]:
    work = table.dropna(subset=core + ext).copy()
    if scale == "within_taxon":
        y = work[endpoints].astype(float)
        xc = work[core].astype(float)
        xe = work[ext].astype(float)
        y = (y - y.groupby(work["taxon_name"]).transform("mean")).to_numpy(float)
        xc = (xc - xc.groupby(work["taxon_name"]).transform("mean")).to_numpy(float)
        xe = (xe - xe.groupby(work["taxon_name"]).transform("mean")).to_numpy(float)
        counts = work.groupby("taxon_name").size()
        weights = 1.0 / work["taxon_name"].map(counts).to_numpy(float)
        yz = weighted_standardize(y, weights)
        xcz = weighted_standardize(xc, weights)
        xez = weighted_standardize(xe, weights)
        r2c = fit_wls_standardized(yz, xcz, weights)
        r2f = fit_wls_standardized(yz, np.column_stack([xcz, xez]), weights)
    else:
        med = work.groupby("taxon_name")[endpoints + core + ext].median().dropna()
        yz = standardize(med[endpoints].to_numpy(float))
        xcz = standardize(med[core].to_numpy(float))
        xez = standardize(med[ext].to_numpy(float))
        r2c = fit_ols_standardized(yz, xcz)
        r2f = fit_ols_standardized(yz, np.column_stack([xcz, xez]))
    delta = max(0.0, r2f - r2c)
    partial = delta / max(1e-15, 1.0 - r2c)
    return delta, partial


def incremental_rows(table: pd.DataFrame, endpoints: list[str], contract: dict, threshold: int) -> list[dict]:
    scope = f"complete18_env_min{threshold}"
    spec = contract["incremental_environment_estimands"]
    core = spec["core_predictors"]
    rows = []
    for test in spec["tests"]:
        for scale in ["within_taxon", "among_taxon"]:
            delta, partial = nested_partial_r2(table, endpoints, core, test["extension_predictors"], scale)
            rows.append({
                "target_id": f"environment_incremental:{test['test_id']}",
                "scope": scope,
                "scale": scale,
                "value": partial,
                "delta_r2": delta,
                "target_class": "environment_incremental",
            })
    return rows


def compute(df: pd.DataFrame, contract: dict) -> pd.DataFrame:
    endpoints, _env, module_by_unit, units = validate_rows(df, contract)
    out = []
    for s in contract["scopes"]:
        threshold = int(s["minimum_complete_observations_per_taxon"])
        table = retained_response_table(df, endpoints, threshold)
        out += structure_rows(table, endpoints, units, module_by_unit, threshold)
        out += environment_rows(table, endpoints, contract, threshold)
        out += incremental_rows(table, endpoints, contract, threshold)
    result = pd.DataFrame(out)
    if len(result) != 62:
        raise RuntimeError(f"exact v3 adapter must emit 62 target rows; emitted {len(result)}")
    if result.duplicated(["target_id", "scope", "scale"]).any():
        raise RuntimeError("duplicate v3 target key")
    return result.sort_values(["target_id", "scope", "scale"]).reset_index(drop=True)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--observations", required=True, type=Path)
    p.add_argument("--contract", type=Path, default=Path("data/evidence/azami_capitulum_v3_estimand_contract_v1.json"))
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    df = pd.read_csv(args.observations, low_memory=False)
    result = compute(df, contract)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.out, index=False)
    print(json.dumps({
        "status": "exact_estimand_adapter_completed",
        "rows": len(result),
        "structure": int((result.target_class == "structure").sum()),
        "environment_block_r2": int((result.target_class == "environment_block_r2").sum()),
        "environment_geometry": int((result.target_class == "environment_geometry").sum()),
        "environment_incremental": int((result.target_class == "environment_incremental").sum()),
        "claim_boundary": "statistics adapter only; model adequacy is not evaluated here",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
