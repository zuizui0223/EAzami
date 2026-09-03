#!/usr/bin/env python3
"""Join the environment-free spatial-breadth pilot to frozen temporal-depth results.

No composite breadth-depth score is computed. The purpose is to place the
component estimands side by side and test whether the two-axis Chapter 2 frame is
empirically usable for the same discrete trait modules.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--spatial-json", type=Path, required=True)
    p.add_argument("--time-json", type=Path, required=True)
    p.add_argument("--out-json", type=Path, required=True)
    p.add_argument("--out-csv", type=Path, required=True)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    spatial = json.loads(args.spatial_json.read_text(encoding="utf-8"))
    time = json.loads(args.time_json.read_text(encoding="utf-8"))
    spatial_by = {x["trait"]: x for x in spatial["traits"]}
    rows = []
    for trait in ["orientation", "phyllary", "stickiness"]:
        s = spatial_by[trait]
        states = json.loads(s["state_breadth_json"])
        q90 = [v["centroid_pairwise_q90_km"] for v in states.values() if v["centroid_pairwise_q90_km"] is not None]
        maxd = [v["centroid_pairwise_max_km"] for v in states.values() if v["centroid_pairwise_max_km"] is not None]
        ml = time["ml_relative_event_depth"][trait]
        ub = time["ufboot1000_relative_event_depth"][trait]
        ms = ub["metric_summaries"]["minimum_steps"]
        lo = ub["metric_summaries"]["mean_relative_lineage_depth_lower_bound"]
        hi = ub["metric_summaries"]["mean_relative_lineage_depth_upper_bound"]
        rows.append({
            "trait": trait,
            "space_n_singleton_state_taxa": s["n_singleton_state_taxa_with_spatial_support"],
            "space_states_present": s["states_present"],
            "space_segregation_statistic_km": s["spatial_segregation_statistic_km"],
            "space_segregation_permutation_p": s["spatial_segregation_permutation_p"],
            "space_max_state_q90_centroid_distance_km": None if not q90 else max(q90),
            "space_max_state_max_centroid_distance_km": None if not maxd else max(maxd),
            "space_status": "evaluable_descriptive" if s["n_singleton_state_taxa_with_spatial_support"] >= 6 else "limited_singleton_state_coverage",
            "time_ml_minimum_steps": ml["minimum_steps"],
            "time_ufboot_min_steps_min": ms["min"],
            "time_ufboot_min_steps_median": ms["median"],
            "time_ufboot_min_steps_max": ms["max"],
            "time_relative_depth_lower_median": lo["median"],
            "time_relative_depth_upper_median": hi["median"],
            "time_fraction_trees_require_terminal_change": ub["fraction_trees_requiring_terminal_change_in_every_minimum_history"],
            "time_fraction_trees_require_internal_change": ub["fraction_trees_requiring_internal_change_in_every_minimum_history"],
            "cross_axis_status": "descriptive_pairing_only_no_n3_regression" if s["n_singleton_state_taxa_with_spatial_support"] >= 6 else "space_axis_limited_no_cross_axis_claim",
        })
    result = {
        "contract_version": "chapter2_space_time_pilot_synthesis_v1",
        "status_date": "2026-09-01",
        "scope": "internal two-axis feasibility diagnostic; environment-free space breadth joined to frozen discrete temporal depth",
        "rows": rows,
        "decision": "two_axis_framework_empirically_usable_for_orientation_and_stickiness_phyllary_space_axis_still_limited",
        "interpretation": (
            "The pilot shows that present spatial breadth and evolutionary time depth can be estimated as separate evidence dimensions. "
            "Orientation and stickiness both have geographically broad current state distributions, yet their temporal histories differ in depth structure; "
            "phyllary posture retains strong temporal information but insufficient singleton-state spatial coverage for a comparable spatial inference."
        ),
        "claim_boundary": [
            "No cross-trait regression is fit with only three modules.",
            "No composite space-time score is constructed.",
            "Current geography is not historical range and does not identify adaptation.",
            "The pilot may remain outside the final manuscript Results."
        ]
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    pd.DataFrame(rows).to_csv(args.out_csv, index=False)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
