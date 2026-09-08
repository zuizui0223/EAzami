#!/usr/bin/env python3
"""Post-result spatial-scale decomposition of the fixed orientation transition-regime H1.

No predictor or hypothesis direction is changed.  The n>=5 12-taxon panel is
split into the frozen Japan-source and Taiwan-source groups.  Full-panel
standardized BIO15/BIO1 centroids are decomposed additively into between-region
(region-mean) and within-region (taxon minus region mean) components.  The same
CTMC/Brownian transition-regime statistic is then evaluated under (i) all
count-preserving maps and (ii) maps preserving the observed U/D counts within
each region.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from run_chapter2_orientation_transition_regime_hypothesis_v1 import (
    AX1,
    AX15,
    brownian_internal_values,
    build_panel_environment,
    exact_panel_test,
    normalize_tip,
    observed_topology_stats,
    panel_state_map,
    prepare_topology_assets,
    prune_to_panel,
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


def prepare_assets_from_columns(raw_trees, taxa, env, c15, c1):
    tip15 = {normalize_tip(t): float(env.loc[t, c15]) for t in taxa}
    tip1 = {normalize_tip(t): float(env.loc[t, c1]) for t in taxa}
    out = []
    for raw in raw_trees:
        tr = prune_to_panel(raw, taxa)
        _, d15 = brownian_internal_values(tr, tip15)
        _, d1 = brownian_internal_values(tr, tip1)
        out.append((tr, d15, d1))
    return out


def observed_summary(assets, states):
    stats = observed_topology_stats(assets, states)
    return {
        "topology_composite": [float(x["composite"]) for x in stats],
        "topology_bio15": [float(x["bio15"]) for x in stats],
        "topology_bio1": [float(x["bio1"]) for x in stats],
        "composite_median": float(np.median([x["composite"] for x in stats])),
        "bio15_median": float(np.median([x["bio15"] for x in stats])),
        "bio1_median": float(np.median([x["bio1"] for x in stats])),
    }


def constrained_region_maps(taxa, region_by_taxon, observed_states, assets_by_component, expected_maps):
    norm_taxa = [normalize_tip(t) for t in taxa]
    idx_by_region = {}
    for i, t in enumerate(taxa):
        idx_by_region.setdefault(region_by_taxon[t], []).append(i)

    region_specs = []
    for region in sorted(idx_by_region):
        idxs = idx_by_region[region]
        d = sum(observed_states[norm_taxa[i]] for i in idxs)
        region_specs.append((region, idxs, d, list(itertools.combinations(idxs, d))))

    n_maps = math.prod(len(x[3]) for x in region_specs)
    if n_maps != expected_maps:
        raise AssertionError(("region-preserving map-count drift", n_maps, expected_maps))

    observed_component = {
        name: observed_summary(assets, observed_states)
        for name, assets in assets_by_component.items()
    }
    rows = []
    for choices in itertools.product(*(x[3] for x in region_specs)):
        dset = set(i for ch in choices for i in ch)
        states = {t: (1 if i in dset else 0) for i, t in enumerate(norm_taxa)}
        row = {
            "null": "region_frequency_preserving",
            "assignment_id": "".join("D" if i in dset else "U" for i in range(len(taxa))),
            "observed": bool(all(states[t] == observed_states[t] for t in norm_taxa)),
        }
        for name, assets in assets_by_component.items():
            s = observed_topology_stats(assets, states)
            row[f"{name}_composite_median"] = float(np.median([x["composite"] for x in s]))
        rows.append(row)
    frame = pd.DataFrame(rows)
    if int(frame["observed"].sum()) != 1:
        raise AssertionError("observed map not unique in region-preserving universe")

    ranks = {}
    for name in assets_by_component:
        col = f"{name}_composite_median"
        obs = observed_component[name]["composite_median"]
        count = int((frame[col].astype(float) >= obs - 1e-12).sum())
        ranks[name] = {
            "count_at_least_observed": count,
            "n_maps": int(len(frame)),
            "exact_fraction": float(count / len(frame)),
        }
    return {"observed": observed_component, "ranks": ranks}, frame


def run_single_region(name, taxa, expected, occ, raw_trees, crosswalk):
    states = panel_state_map(crosswalk, taxa)
    state_values = list(states.values())
    if (len(taxa), state_values.count(0), state_values.count(1)) != (
        expected["expected_n"], expected["expected_U"], expected["expected_D"]
    ):
        raise AssertionError(("single-region state-count drift", name))
    counts, env = build_panel_environment(occ, taxa)
    if any(int(counts.get(t, 0)) < 5 for t in taxa):
        raise AssertionError(("single-region occurrence threshold drift", name))
    assets = prepare_topology_assets(raw_trees, taxa, env)
    result, frame = exact_panel_test(name, taxa, states, assets, int(expected["expected_maps"]))
    return result, frame


def main():
    args = parse_args()
    contract = read_json(args.contract)
    h1 = read_json(args.hypothesis_result)
    coverage = read_json(args.coverage_audit)
    if contract["version"] != "chapter2_orientation_regional_scale_contract_v1":
        raise AssertionError("contract version drift")
    if h1["version"] != "chapter2_orientation_transition_regime_hypothesis_result_v1":
        raise AssertionError("H1 result version drift")
    if coverage["version"] != "chapter2_orientation_occurrence_coverage_audit_result_v1":
        raise AssertionError("coverage version drift")

    crosswalk = pd.read_csv(args.orientation)
    jp = pd.read_csv(args.japan_occurrences)
    tw = pd.read_csv(args.taiwan_occurrences)
    all_occ = pd.concat([jp, tw], ignore_index=True)
    raw_trees = read_trees(args.au_trees, 6)

    panel = contract["panel"]
    taxa = list(coverage["threshold_summaries"]["5"]["taxa"])
    if set(taxa) != set(panel["japan"]["taxa"] + panel["taiwan"]["taxa"]):
        raise AssertionError("declared region groups do not partition frozen n>=5 panel")
    taxa = list(panel["japan"]["taxa"] + panel["taiwan"]["taxa"])
    states = panel_state_map(crosswalk, taxa)
    vals = list(states.values())
    if (len(taxa), vals.count(0), vals.count(1)) != (panel["expected_n"], panel["expected_U"], panel["expected_D"]):
        raise AssertionError("full-panel state-count drift")

    # Verify the declared groups are actually recoverable from their intended frozen source assets.
    jp_counts = jp.groupby("scientific_name_query").size()
    tw_counts = tw.groupby("scientific_name_query").size()
    source_membership = {}
    for t in taxa:
        source_membership[t] = {"japan_rows": int(jp_counts.get(t, 0)), "taiwan_rows": int(tw_counts.get(t, 0))}
    for t in panel["japan"]["taxa"]:
        if source_membership[t]["japan_rows"] < panel["threshold"]:
            raise AssertionError(("Japan-group taxon lacks frozen Japan coverage", t, source_membership[t]))
    for t in panel["taiwan"]["taxa"]:
        if source_membership[t]["taiwan_rows"] < panel["threshold"]:
            raise AssertionError(("Taiwan-group taxon lacks frozen Taiwan coverage", t, source_membership[t]))

    counts, env = build_panel_environment(all_occ, taxa)
    if any(int(counts.get(t, 0)) < panel["threshold"] for t in taxa):
        raise AssertionError("full-panel occurrence threshold drift")

    region_by_taxon = {t: "Japan" for t in panel["japan"]["taxa"]}
    region_by_taxon.update({t: "Taiwan" for t in panel["taiwan"]["taxa"]})
    env["region"] = [region_by_taxon[t] for t in env.index]
    for base in ("z15", "z1"):
        env[f"between_{base}"] = env.groupby("region")[base].transform("mean")
        env[f"within_{base}"] = env[base] - env[f"between_{base}"]
        err = float(np.max(np.abs(env[base] - env[f"between_{base}"] - env[f"within_{base}"])))
        if err > 1e-12:
            raise AssertionError(("decomposition additivity failed", base, err))

    total_assets = prepare_topology_assets(raw_trees, taxa, env)
    between_assets = prepare_assets_from_columns(raw_trees, taxa, env, "between_z15", "between_z1")
    within_assets = prepare_assets_from_columns(raw_trees, taxa, env, "within_z15", "within_z1")

    total, total_frame = exact_panel_test("total_all_maps", taxa, states, total_assets, panel["expected_all_count_preserving_maps"])
    between, between_frame = exact_panel_test("between_region_all_maps", taxa, states, between_assets, panel["expected_all_count_preserving_maps"])
    within, within_frame = exact_panel_test("within_region_all_maps", taxa, states, within_assets, panel["expected_all_count_preserving_maps"])

    frozen = h1["n5_primary"]
    if abs(total["observed"]["composite_median"] - float(frozen["observed_composite_median"])) > 1e-10:
        raise AssertionError(("H1 total reproduction failed", total["observed"]["composite_median"], frozen["observed_composite_median"]))
    if total["exact_primary_rank"]["count_at_least_observed"] != int(frozen["exact_primary_rank"]["count_at_least_observed"]):
        raise AssertionError("H1 rank reproduction failed")

    constrained, constrained_frame = constrained_region_maps(
        taxa,
        region_by_taxon,
        states,
        {"total": total_assets, "between": between_assets, "within": within_assets},
        int(panel["expected_region_frequency_preserving_maps"]),
    )

    japan, japan_frame = run_single_region("japan_only_n5", panel["japan"]["taxa"], panel["japan"], jp, raw_trees, crosswalk)
    taiwan, taiwan_frame = run_single_region("taiwan_only_n5", panel["taiwan"]["taxa"], panel["taiwan"], tw, raw_trees, crosswalk)

    between_p = between["exact_primary_rank"]["exact_fraction"]
    within_p = within["exact_primary_rank"]["exact_fraction"]
    constrained_total_p = constrained["ranks"]["total"]["exact_fraction"]
    between_positive = all(x > 0 for x in between["observed"]["topology_composite"])
    within_positive = all(x > 0 for x in within["observed"]["topology_composite"])

    if constrained_total_p <= 0.05 and within_positive and within_p <= 0.05:
        classification = "regional_composition_not_sufficient_within_region_signal_retained"
    elif constrained_total_p <= 0.05:
        classification = "regional_composition_not_sufficient_mixed_or_between_scale"
    elif between_positive and between_p <= 0.05 and not (within_positive and within_p <= 0.05):
        classification = "between_region_dominant_regional_composition_accounts_for_exceptionality"
    else:
        classification = "mixed_scale_or_low_resolution"

    out = {
        "version": "chapter2_orientation_regional_scale_result_v1",
        "status_date": "2026-09-08",
        "classification": classification,
        "fixed_hypothesis": contract["fixed_hypothesis"],
        "panel": {"taxa": taxa, "region_by_taxon": region_by_taxon, "source_membership": source_membership},
        "all_count_preserving": {"total": total, "between_region": between, "within_region": within},
        "region_frequency_preserving": constrained,
        "leave_one_region_out": {"japan": japan, "taiwan": taiwan},
        "claim_ceiling": contract["claim_ceiling"],
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    frames = [total_frame, between_frame, within_frame, constrained_frame, japan_frame, taiwan_frame]
    pd.concat(frames, ignore_index=True, sort=False).to_csv(args.out_csv, index=False)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
