#!/usr/bin/env python3
"""Post-heldout diagnostic for minimal additions to the frozen v3 snapshot null.

This is intentionally separate from the frozen v1 scalar-target ranking. It reuses
the held-out support-test implementation and asks whether four pre-existing process
families improve the replication-stable 8-cell support geometry over NULL_COUPLED.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import validate_azami_v3_null_heldout_support as hv
from simulate_azami_capitulum_v3_conditional import generate


def run_family_draw(
    design: pd.DataFrame,
    family: str,
    generator_contract: dict,
    estimand_contract: dict,
    heldout_contract: dict,
    seed: int,
) -> pd.DataFrame:
    observations = generate(design, family, seed, generator_contract, strict_frozen_design=True)
    endpoints = estimand_contract["observation_schema"]["response_endpoints"]
    incremental = estimand_contract["incremental_environment_estimands"]
    core = incremental["core_predictors"]
    specs = incremental["tests"]
    permutations = int(heldout_contract["nested_test"]["permutations_per_test"])
    alpha = float(heldout_contract["nested_test"]["support_threshold"])
    rows: list[dict[str, Any]] = []

    for threshold in (5, 2):
        counts = observations.groupby("taxon_name").size()
        keep = counts[counts >= threshold].index
        table = observations[observations["taxon_name"].isin(keep)].copy()
        scope = f"complete18_env_min{threshold}"
        for spec in specs:
            test_id = spec["test_id"]
            test_family = spec["family"]
            extension = spec["extension_predictors"]

            yw, xcw, xew, weights, groups = hv.prepare_within(table, endpoints, core, extension)
            r2c, r2f, delta, fitted, residual = hv.nested_wls(yw, xcw, xew, weights)
            pw = hv.freedman_lane_within(
                yw, xcw, xew, weights, groups, delta, fitted, residual, permutations,
                hv.stable_rng(seed, family, scope, test_id, "within_freedman_lane"),
            )
            rows.append({
                "family": family, "seed": seed, "scope": scope, "scale": "within_taxon",
                "test_id": test_id, "test_family": test_family, "r2_core4": r2c,
                "r2_full": r2f, "delta_r2": delta,
                "partial_r2": delta / max(1e-15, 1.0 - r2c), "permutation_p": pw,
            })

            ya, xca, xea = hv.prepare_among(table, endpoints, core, extension)
            r2c, r2f, delta, fitted, residual = hv.nested_ols(ya, xca, xea)
            pa = hv.freedman_lane_among(
                ya, xca, xea, delta, fitted, residual, permutations,
                hv.stable_rng(seed, family, scope, test_id, "among_freedman_lane"),
            )
            rows.append({
                "family": family, "seed": seed, "scope": scope, "scale": "among_taxon",
                "test_id": test_id, "test_family": test_family, "r2_core4": r2c,
                "r2_full": r2f, "delta_r2": delta,
                "partial_r2": delta / max(1e-15, 1.0 - r2c), "permutation_p": pa,
            })

    result = pd.DataFrame(rows)
    if len(result) != 20:
        raise RuntimeError(f"{family}/{seed} produced {len(result)} tests instead of 20")
    result["q_bh_block_specific"] = np.nan
    block = result["test_family"].eq("block_specific")
    for (_scope, _scale), idx in result[block].groupby(["scope", "scale"]).groups.items():
        result.loc[idx, "q_bh_block_specific"] = hv.bh_adjust(
            result.loc[idx, "permutation_p"].astype(float)
        )
    result["supported_0_05"] = False
    omnibus = result["test_family"].eq("omnibus")
    result.loc[omnibus, "supported_0_05"] = result.loc[omnibus, "permutation_p"].lt(alpha)
    result.loc[block, "supported_0_05"] = result.loc[block, "q_bh_block_specific"].lt(alpha)
    return result


def draw_diagnostics(ledger: pd.DataFrame, observed: dict, heldout_contract: dict) -> pd.DataFrame:
    required = hv.primary_cells(heldout_contract)
    rows = []
    for (family, seed), group in ledger.groupby(["family", "seed"], sort=True):
        got = {
            (r.scope, r.scale, r.test_id): bool(r.supported_0_05)
            for r in group.itertuples(index=False)
        }
        primary_matches = sum(
            got[(scope, scale, test_id)] == bool(expected)
            for scope, scale, test_id, expected in required
        )
        full_primary = primary_matches == len(required)
        all20 = sum(got[key] == observed[key] for key in observed)
        gsp_both = all(
            got[(scope, "among_taxon", "growing_season_water_input_beyond_core4")]
            for scope in ("complete18_env_min5", "complete18_env_min2")
        )
        omnibus_both = all(
            got[(scope, "among_taxon", "all_process_extension_beyond_core4")]
            for scope in ("complete18_env_min5", "complete18_env_min2")
        )
        within_clean = all(
            not got[(scope, "within_taxon", test_id)]
            for scope in ("complete18_env_min5", "complete18_env_min2")
            for test_id in (
                "all_process_extension_beyond_core4",
                "growing_season_water_input_beyond_core4",
            )
        )
        rows.append({
            "family": family,
            "seed": int(seed),
            "primary_cells_matched_out_of_8": int(primary_matches),
            "full_8_cell_pattern_match": bool(full_primary),
            "matching_cells_out_of_20": int(all20),
            "exact_20_cell_match": bool(all20 == 20),
            "among_gsp_supported_both_thresholds": bool(gsp_both),
            "among_omnibus_supported_both_thresholds": bool(omnibus_both),
            "within_omnibus_and_gsp_unsupported_both_thresholds": bool(within_clean),
        })
    return pd.DataFrame(rows)


def family_summary(draws: pd.DataFrame, diagnostic_contract: dict) -> pd.DataFrame:
    null = draws[draws["family"].eq("NULL_COUPLED")].set_index("seed")
    rows = []
    for family, group in draws.groupby("family", sort=True):
        aligned = group.set_index("seed").loc[null.index]
        delta = (
            aligned["primary_cells_matched_out_of_8"].to_numpy(float)
            - null["primary_cells_matched_out_of_8"].to_numpy(float)
        )
        rows.append({
            "family": family,
            "median_primary_cells_matched_out_of_8": float(group["primary_cells_matched_out_of_8"].median()),
            "mean_primary_cells_matched_out_of_8": float(group["primary_cells_matched_out_of_8"].mean()),
            "full_8_cell_pattern_matches": int(group["full_8_cell_pattern_match"].sum()),
            "full_8_cell_pattern_frequency": float(group["full_8_cell_pattern_match"].mean()),
            "exact_20_cell_matches": int(group["exact_20_cell_match"].sum()),
            "median_matching_cells_out_of_20": float(group["matching_cells_out_of_20"].median()),
            "among_gsp_both_frequency": float(group["among_gsp_supported_both_thresholds"].mean()),
            "among_omnibus_both_frequency": float(group["among_omnibus_supported_both_thresholds"].mean()),
            "within_clean_frequency": float(group["within_omnibus_and_gsp_unsupported_both_thresholds"].mean()),
            "paired_superiority_over_null_fraction": float(np.mean(delta > 0)) if family != "NULL_COUPLED" else 0.0,
            "paired_equal_to_null_fraction": float(np.mean(delta == 0)) if family != "NULL_COUPLED" else 1.0,
            "median_primary_cell_advantage_over_null": float(np.median(delta)) if family != "NULL_COUPLED" else 0.0,
        })
    summary = pd.DataFrame(rows)
    rule = diagnostic_contract["adequacy_rule"]
    summary["diagnostically_adequate"] = (
        ~summary["family"].eq("NULL_COUPLED")
        & summary["median_primary_cells_matched_out_of_8"].ge(float(rule["median_primary_cells_matched_minimum"]))
        & summary["full_8_cell_pattern_matches"].ge(int(rule["full_pattern_matches_minimum_out_of_24"]))
        & summary["paired_superiority_over_null_fraction"].ge(float(rule["paired_superiority_over_null_minimum"]))
    )
    return summary.sort_values(
        ["diagnostically_adequate", "median_primary_cells_matched_out_of_8", "full_8_cell_pattern_matches"],
        ascending=[False, False, False],
    ).reset_index(drop=True)


def decision(summary: pd.DataFrame, contract: dict) -> dict:
    adequate = set(summary.loc[summary["diagnostically_adequate"], "family"])
    minimal = next((f for f in contract["minimality_order_if_multiple_adequate"] if f in adequate), None)
    best = summary.iloc[0]
    return {
        "status": "diagnostic_minimal_structure_identified" if minimal else "no_diagnostically_adequate_addition",
        "frozen_v1_winner_unchanged": "NULL_COUPLED",
        "candidate_family_count": len(contract["candidate_families"]),
        "paired_draw_count": int(contract["paired_draws"]["count"]),
        "diagnostically_adequate_families": sorted(adequate),
        "minimal_diagnostically_adequate_family": minimal,
        "best_descriptive_family": str(best["family"]),
        "best_median_primary_cells_matched_out_of_8": float(best["median_primary_cells_matched_out_of_8"]),
        "best_full_8_cell_pattern_matches": int(best["full_8_cell_pattern_matches"]),
        "claim_boundary": contract["claim_boundary"],
        "stop_rule": contract["stop_rule"],
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--design", required=True, type=Path)
    p.add_argument("--observed-incremental", required=True, type=Path)
    p.add_argument("--diagnostic-contract", type=Path, default=Path("data/evidence/azami_capitulum_v3_support_geometry_diagnostic_contract_v1.json"))
    p.add_argument("--generator-contract", type=Path, default=Path("data/evidence/azami_capitulum_v3_generator_contract_v1.json"))
    p.add_argument("--estimand-contract", type=Path, default=Path("data/evidence/azami_capitulum_v3_estimand_contract_v1.json"))
    p.add_argument("--heldout-contract", type=Path, default=Path("data/evidence/azami_capitulum_v3_null_heldout_support_contract_v1.json"))
    p.add_argument("--out-dir", required=True, type=Path)
    args = p.parse_args()

    diagnostic = json.loads(args.diagnostic_contract.read_text())
    generator = json.loads(args.generator_contract.read_text())
    estimand = json.loads(args.estimand_contract.read_text())
    heldout = json.loads(args.heldout_contract.read_text())
    if diagnostic["status"] != "frozen_before_diagnostic_support_geometry_screen":
        raise ValueError("diagnostic contract is not frozen pre-screen")
    observed = hv.validate_observed_vector(heldout, args.observed_incremental)
    design = pd.read_csv(args.design, low_memory=False)
    families = diagnostic["candidate_families"]
    seeds = [int(x) for x in diagnostic["paired_draws"]["seeds"]]
    if len(seeds) != int(diagnostic["paired_draws"]["count"]):
        raise ValueError("paired draw count mismatch")

    ledger_parts = []
    for seed in seeds:
        for family in families:
            ledger_parts.append(run_family_draw(design, family, generator, estimand, heldout, seed))
    ledger = pd.concat(ledger_parts, ignore_index=True)
    draws = draw_diagnostics(ledger, observed, heldout)
    summary = family_summary(draws, diagnostic)
    result = decision(summary, diagnostic)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    ledger.to_csv(args.out_dir / "azami_capitulum_v3_support_geometry_diagnostic_test_ledger_v1.csv", index=False)
    draws.to_csv(args.out_dir / "azami_capitulum_v3_support_geometry_diagnostic_draws_v1.csv", index=False)
    summary.to_csv(args.out_dir / "azami_capitulum_v3_support_geometry_diagnostic_family_summary_v1.csv", index=False)
    (args.out_dir / "azami_capitulum_v3_support_geometry_diagnostic_decision_v1.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
