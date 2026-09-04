#!/usr/bin/env python3
"""Specific falsification of transition-regime H1 after linear geography residualization."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from run_chapter2_orientation_transition_regime_hypothesis_v1 import (
    AX15, AX1, normalize_tip, read_trees, prune_to_panel, brownian_internal_values,
    panel_state_map, exact_panel_test, zscore,
)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--contract", type=Path, required=True)
    p.add_argument("--coverage-audit", type=Path, required=True)
    p.add_argument("--orientation", type=Path, required=True)
    p.add_argument("--japan-occurrences", type=Path, required=True)
    p.add_argument("--taiwan-occurrences", type=Path, required=True)
    p.add_argument("--au-trees", type=Path, required=True)
    p.add_argument("--out-json", type=Path, required=True)
    p.add_argument("--out-csv", type=Path, required=True)
    return p.parse_args()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def residualize(v: np.ndarray, lat: np.ndarray, lon: np.ndarray):
    X = np.column_stack([np.ones(len(v)), lat, lon])
    beta, *_ = np.linalg.lstsq(X, v, rcond=None)
    resid = v - X @ beta
    return zscore(resid), beta, resid


def build_residual_environment(occ: pd.DataFrame, taxa: list[str]):
    counts = occ.groupby("scientific_name_query").size()
    env = occ.groupby("scientific_name_query")[["latitude", "longitude", AX15, AX1]].mean().loc[taxa].copy()
    lat = env["latitude"].to_numpy(float)
    lon = env["longitude"].to_numpy(float)
    z15, b15, r15 = residualize(env[AX15].to_numpy(float), lat, lon)
    z1, b1, r1 = residualize(env[AX1].to_numpy(float), lat, lon)
    env["z15"] = z15
    env["z1"] = z1
    diagnostics = {
        "bio15_geo_beta": [float(x) for x in b15],
        "bio1_geo_beta": [float(x) for x in b1],
        "bio15_residual_sum": float(r15.sum()),
        "bio1_residual_sum": float(r1.sum()),
        "bio15_residual_sd": float(r15.std(ddof=1)),
        "bio1_residual_sd": float(r1.std(ddof=1)),
    }
    return counts, env, diagnostics


def prepare_assets(raw_trees, taxa, env):
    tip15 = {normalize_tip(t): float(env.loc[t, "z15"]) for t in taxa}
    tip1 = {normalize_tip(t): float(env.loc[t, "z1"]) for t in taxa}
    assets = []
    for raw in raw_trees:
        tr = prune_to_panel(raw, taxa)
        _, d15 = brownian_internal_values(tr, tip15)
        _, d1 = brownian_internal_values(tr, tip1)
        assets.append((tr, d15, d1))
    return assets


def main():
    args = parse_args()
    contract = read_json(args.contract)
    coverage = read_json(args.coverage_audit)
    if contract["version"] != "chapter2_orientation_transition_regime_geography_residual_contract_v1":
        raise AssertionError("contract version drift")
    if coverage["version"] != "chapter2_orientation_occurrence_coverage_audit_result_v1":
        raise AssertionError("coverage version drift")

    crosswalk = pd.read_csv(args.orientation)
    jp = pd.read_csv(args.japan_occurrences)
    tw = pd.read_csv(args.taiwan_occurrences)
    occ = pd.concat([jp, tw], ignore_index=True)
    raw_trees = read_trees(args.au_trees, 6)
    threshold_taxa = {str(k): list(v["taxa"]) for k, v in coverage["threshold_summaries"].items()}

    panel_results = {}
    frames = []
    for panel_name, threshold_key in (("strict_n10_primary", "10"), ("n5_sensitivity", "5")):
        spec = contract["panels"][panel_name]
        taxa = threshold_taxa[threshold_key]
        ss = crosswalk.set_index("accepted_taxon").loc[taxa, "analysis_state"]
        got = (len(taxa), int((ss == "U").sum()), int((ss == "D").sum()))
        exp = (spec["expected_n"], spec["expected_U"], spec["expected_D"])
        if got != exp:
            raise AssertionError(("panel drift", panel_name, got, exp))
        counts, env, diag = build_residual_environment(occ, taxa)
        if any(int(counts.get(t, 0)) < int(spec["threshold"]) for t in taxa):
            raise AssertionError(("occurrence threshold drift", panel_name))
        states = panel_state_map(crosswalk, taxa)
        assets = prepare_assets(raw_trees, taxa, env)
        result, frame = exact_panel_test(panel_name, taxa, states, assets, int(spec["exact_state_maps"]))
        result["geography_residualization"] = diag
        panel_results[panel_name] = result
        frames.append(frame)

    primary = panel_results["strict_n10_primary"]
    topo = primary["observed"]["topology_composite"]
    frac = primary["exact_primary_rank"]["exact_fraction"]
    if all(x > 0 for x in topo) and frac <= 0.05:
        classification = "transition_regime_concordance_persists_after_linear_geography_residualization"
    elif all(x > 0 for x in topo):
        classification = "transition_regime_direction_persists_but_exceptionality_is_geography_sensitive"
    else:
        classification = "transition_regime_direction_is_explained_by_or_unstable_after_linear_geography_residualization"

    out = {
        "version": "chapter2_orientation_transition_regime_geography_residual_result_v1",
        "analysis_role": contract["analysis_role"],
        "fixed_hypothesis": contract["fixed_hypothesis"],
        "classification": classification,
        "panels": panel_results,
        "claim_ceiling": contract["claim_ceiling"],
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    pd.concat(frames, ignore_index=True).to_csv(args.out_csv, index=False)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
