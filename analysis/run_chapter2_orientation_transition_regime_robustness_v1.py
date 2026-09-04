#!/usr/bin/env python3
"""Robustness tests for the frozen orientation transition-regime H1.

No new predictors or hypothesis directions are introduced. We reuse the exact
CTMC/Brownian estimator from v1 and test two stricter panels: original n>=10
coverage and Japan-only n>=5.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from run_chapter2_orientation_transition_regime_hypothesis_v1 import (
    build_panel_environment,
    exact_panel_test,
    panel_state_map,
    prepare_topology_assets,
    read_json,
    read_trees,
)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--contract", type=Path, required=True)
    p.add_argument("--hypothesis-result", type=Path, required=True)
    p.add_argument("--coverage-audit", type=Path, required=True)
    p.add_argument("--orientation", type=Path, required=True)
    p.add_argument("--japan-occurrences", type=Path, required=True)
    p.add_argument("--taiwan-occurrences", type=Path, required=True)
    p.add_argument("--au-trees", type=Path, required=True)
    p.add_argument("--out-json", type=Path, required=True)
    p.add_argument("--out-csv", type=Path, required=True)
    return p.parse_args()


def panel_pass(result: dict) -> bool:
    return (
        all(x > 0 for x in result["observed"]["topology_composite"])
        and result["exact_primary_rank"]["exact_fraction"] <= 0.05
    )


def run_panel(name, taxa, expected, occ, raw_trees, crosswalk):
    state_series = crosswalk.set_index("accepted_taxon").loc[taxa, "analysis_state"]
    observed_counts = {
        "n": len(taxa),
        "U": int((state_series == "U").sum()),
        "D": int((state_series == "D").sum()),
    }
    wanted = {"n": expected["expected_n"], "U": expected["expected_U"], "D": expected["expected_D"]}
    if observed_counts != wanted:
        raise AssertionError(("panel state-count drift", name, observed_counts, wanted))
    counts, env = build_panel_environment(occ, taxa)
    threshold = int(expected["threshold"])
    if any(int(counts.get(t, 0)) < threshold for t in taxa):
        raise AssertionError(("occurrence threshold drift", name, threshold))
    states = panel_state_map(crosswalk, taxa)
    assets = prepare_topology_assets(raw_trees, taxa, env)
    result, frame = exact_panel_test(name, taxa, states, assets, int(expected["exact_state_maps"]))
    result["passes_frozen_panel_rule"] = panel_pass(result)
    return result, frame


def main():
    args = parse_args()
    contract = read_json(args.contract)
    h1 = read_json(args.hypothesis_result)
    coverage = read_json(args.coverage_audit)
    if contract["version"] != "chapter2_orientation_transition_regime_robustness_contract_v1":
        raise AssertionError("contract version drift")
    if h1["version"] != "chapter2_orientation_transition_regime_hypothesis_result_v1":
        raise AssertionError("H1 source version drift")
    if h1["classification"] != "repeated_u_to_d_transition_regime_concordance_supported":
        raise AssertionError("H1 must be supported before robustness test")
    if coverage["version"] != "chapter2_orientation_occurrence_coverage_audit_result_v1":
        raise AssertionError("coverage source version drift")

    crosswalk = pd.read_csv(args.orientation)
    jp = pd.read_csv(args.japan_occurrences)
    tw = pd.read_csv(args.taiwan_occurrences)
    all_occ = pd.concat([jp, tw], ignore_index=True)
    raw_trees = read_trees(args.au_trees, 6)

    strict_spec = contract["tests"]["strict_n10"]
    strict_taxa = list(coverage["threshold_summaries"]["10"]["taxa"])
    strict, strict_frame = run_panel("strict_n10", strict_taxa, strict_spec, all_occ, raw_trees, crosswalk)

    jp_spec = contract["tests"]["japan_n5"]
    jp_taxa = list(jp_spec["taxa"])
    japan, japan_frame = run_panel("japan_n5", jp_taxa, jp_spec, jp, raw_trees, crosswalk)

    if strict["passes_frozen_panel_rule"] and japan["passes_frozen_panel_rule"]:
        classification = "transition_regime_concordance_robust_to_strict_coverage_and_japan_only"
    elif strict["passes_frozen_panel_rule"]:
        classification = "transition_regime_concordance_strict_coverage_robust_but_region_sensitive"
    else:
        classification = "transition_regime_concordance_depends_on_relaxed_coverage"

    out = {
        "version": "chapter2_orientation_transition_regime_robustness_result_v1",
        "analysis_role": contract["analysis_role"],
        "fixed_hypothesis": contract["fixed_hypothesis"],
        "classification": classification,
        "tests": {"strict_n10": strict, "japan_n5": japan},
        "claim_ceiling": contract["claim_ceiling"],
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    pd.concat([strict_frame, japan_frame], ignore_index=True).to_csv(args.out_csv, index=False)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
