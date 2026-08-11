#!/usr/bin/env python3
"""Quantify topology sensitivity of the current Chang 2026 takaoense Figure 1
sample topology and recover the nearest no-regain alternatives.

This implementation deliberately imports the current source of truth from
``chang2026_takaoense_sample_colour_history.py`` and the current exhaustive-tree
enumerator from ``chang2026_takaoense_topology_uncertainty.py``.  It replaces a
stale historical implementation that referenced superseded symbols and could no
longer be executed from the repository head.

Rooted Robinson-Foulds distance is defined here as the symmetric difference in
nontrivial rooted descendant clusters.  No branch lengths are used.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Callable, Iterable, Mapping, Sequence

from chang2026_takaoense_sample_colour_history import (
    C,
    SINOCIRSIUM_STATES,
    TAKAOENSE_SIX,
    TAKAOENSE_STATES,
    fitch,
    minimum_summary,
)
from chang2026_takaoense_topology_uncertainty import (
    BP_TIPS,
    TIP_NAMES,
    W_TIPS,
    all_rooted_binary_trees,
    canonical,
    descendant_sets,
    is_monophyletic,
    sinocirsium_tree,
    tree_key,
)

NH_TJ_CHERRY = frozenset(("NH_3835_BP", "TJ_3807_BP"))
DEFAULT_ALL_OUTPUT = Path("data/evidence/generated/chang2026_takaoense_topology_robustness_all.csv")
DEFAULT_GROUP_OUTPUT = Path("analysis/chang2026_takaoense_topology_robustness_groups.csv")
DEFAULT_NEAREST_OUTPUT = Path("analysis/chang2026_takaoense_nearest_no_regain_topologies.csv")
DEFAULT_SUMMARY_OUTPUT = Path("analysis/chang2026_takaoense_topology_robustness_summary.json")

ALL_FIELDS = (
    "topology_id","sample_topology_newick","rooted_rf_distance_from_published",
    "is_published_topology","bp_monophyletic","w_monophyletic","nh_tj_cherry_preserved",
    "six_tip_fitch_minimum_changes","six_tip_fitch_root_states",
    "sinocirsium_coloured_root_minimum_changes","sinocirsium_coloured_root_optimal_histories",
    "regain_required_at_global_minimum","minimum_no_regain_changes","no_regain_penalty",
)
GROUP_FIELDS = (
    "group","topology_count","regain_required_count","regain_required_fraction",
    "no_regain_equal_optimum_count","no_regain_penalty_1_count","no_regain_penalty_2_count",
    "minimum_change_2_count","minimum_change_3_count","minimum_change_4_count","interpretation",
)
NEAREST_FIELDS = (
    "topology_id","sample_topology_newick","rooted_rf_distance_from_published",
    "bp_monophyletic","w_monophyletic","nh_tj_cherry_preserved",
    "sinocirsium_coloured_root_minimum_changes","sinocirsium_coloured_root_optimal_histories",
    "minimum_no_regain_changes","no_regain_penalty","interpretation",
)


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def nontrivial_rooted_clusters(tree) -> frozenset[frozenset[str]]:
    full, clades = descendant_sets(tree)
    return frozenset(clade for clade in clades if 1 < len(clade) < len(full))


def rooted_rf_distance(left, right) -> int:
    return len(nontrivial_rooted_clusters(left) ^ nontrivial_rooted_clusters(right))


def history_text(values: Sequence[tuple[int, int]]) -> str:
    return "|".join(f"{losses}L+{regains}R" for losses, regains in values)


def analyse_topologies() -> list[dict[str, object]]:
    topologies = all_rooted_binary_trees(TIP_NAMES)
    if len(topologies) != 945:
        raise ValueError(f"Expected 945 rooted six-tip topologies, observed {len(topologies)}")
    published = canonical(TAKAOENSE_SIX)
    published_clusters = nontrivial_rooted_clusters(published)
    rows: list[dict[str, object]] = []
    for index, topology in enumerate(topologies, start=1):
        fitch_states, fitch_changes = fitch(topology, TAKAOENSE_STATES)
        result = minimum_summary(sinocirsium_tree(topology), SINOCIRSIUM_STATES, C)
        clusters = nontrivial_rooted_clusters(topology)
        rows.append({
            "topology_id": f"T{index:04d}",
            "sample_topology_newick": tree_key(topology) + ";",
            "rooted_rf_distance_from_published": len(clusters ^ published_clusters),
            "is_published_topology": bool_text(topology == published),
            "bp_monophyletic": bool_text(is_monophyletic(topology, BP_TIPS)),
            "w_monophyletic": bool_text(is_monophyletic(topology, W_TIPS)),
            "nh_tj_cherry_preserved": bool_text(is_monophyletic(topology, NH_TJ_CHERRY)),
            "six_tip_fitch_minimum_changes": fitch_changes,
            "six_tip_fitch_root_states": "|".join(sorted(fitch_states)),
            "sinocirsium_coloured_root_minimum_changes": result["minimum_changes"],
            "sinocirsium_coloured_root_optimal_histories": history_text(result["directional_combinations"]),
            "regain_required_at_global_minimum": bool_text(bool(result["regain_required_at_global_minimum"])),
            "minimum_no_regain_changes": result["minimum_no_regain_changes"],
            "no_regain_penalty": result["no_regain_change_penalty"],
        })
    return rows


def as_bool(row: Mapping[str, object], field: str) -> bool:
    return str(row[field]).casefold() == "true"


def group_summary(rows: Sequence[Mapping[str, object]], group: str,
                  predicate: Callable[[Mapping[str, object]], bool],
                  interpretation: str) -> dict[str, object]:
    selected = [row for row in rows if predicate(row)]
    penalties = Counter(int(row["no_regain_penalty"]) for row in selected)
    minima = Counter(int(row["sinocirsium_coloured_root_minimum_changes"]) for row in selected)
    required = sum(as_bool(row, "regain_required_at_global_minimum") for row in selected)
    return {
        "group": group,
        "topology_count": len(selected),
        "regain_required_count": required,
        "regain_required_fraction": f"{required / len(selected):.6f}" if selected else "0.000000",
        "no_regain_equal_optimum_count": penalties.get(0, 0),
        "no_regain_penalty_1_count": penalties.get(1, 0),
        "no_regain_penalty_2_count": penalties.get(2, 0),
        "minimum_change_2_count": minima.get(2, 0),
        "minimum_change_3_count": minima.get(3, 0),
        "minimum_change_4_count": minima.get(4, 0),
        "interpretation": interpretation,
    }


def build_group_summaries(rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    return [
        group_summary(rows,"all_rooted_binary_topologies",lambda row: True,
                      "Worst-case topology uncertainty across all 945 rooted binary resolutions."),
        group_summary(rows,"bp_monophyletic",lambda row: as_bool(row,"bp_monophyletic"),
                      "All three bluish-purple tips form one clade, but their position relative to white tips is unrestricted."),
        group_summary(rows,"w_monophyletic",lambda row: as_bool(row,"w_monophyletic"),
                      "All three white tips form one clade; a loss-only explanation remains available."),
        group_summary(rows,"nh_tj_cherry",lambda row: as_bool(row,"nh_tj_cherry_preserved"),
                      "The published NH-TJ sister pair is preserved, while other relationships vary."),
        group_summary(rows,"bp_monophyletic_and_nh_tj_cherry",
                      lambda row: as_bool(row,"bp_monophyletic") and as_bool(row,"nh_tj_cherry_preserved"),
                      "The full BP clade and its NH-TJ internal pair are preserved."),
        group_summary(rows,"published_plus_single_split_perturbations",
                      lambda row: int(row["rooted_rf_distance_from_published"]) <= 2,
                      "Published topology plus every rooted topology differing by rooted RF distance at most two."),
        group_summary(rows,"published_plus_two_split_perturbations",
                      lambda row: int(row["rooted_rf_distance_from_published"]) <= 4,
                      "Published topology plus wider local rearrangements up to rooted RF distance four."),
        group_summary(rows,"published_topology",lambda row: as_bool(row,"is_published_topology"),
                      "Exact Figure 1 sample topology."),
    ]


def nearest_no_regain_rows(rows: Sequence[Mapping[str, object]]) -> tuple[int, list[dict[str, object]]]:
    candidates = [row for row in rows if int(row["no_regain_penalty"]) == 0]
    minimum_distance = min(int(row["rooted_rf_distance_from_published"]) for row in candidates)
    selected: list[dict[str, object]] = []
    for row in candidates:
        if int(row["rooted_rf_distance_from_published"]) != minimum_distance:
            continue
        selected.append({
            "topology_id": row["topology_id"],
            "sample_topology_newick": row["sample_topology_newick"],
            "rooted_rf_distance_from_published": minimum_distance,
            "bp_monophyletic": row["bp_monophyletic"],
            "w_monophyletic": row["w_monophyletic"],
            "nh_tj_cherry_preserved": row["nh_tj_cherry_preserved"],
            "sinocirsium_coloured_root_minimum_changes": row["sinocirsium_coloured_root_minimum_changes"],
            "sinocirsium_coloured_root_optimal_histories": row["sinocirsium_coloured_root_optimal_histories"],
            "minimum_no_regain_changes": row["minimum_no_regain_changes"],
            "no_regain_penalty": row["no_regain_penalty"],
            "interpretation": "Nearest rooted resolution in which a no-regain history is globally optimal under the current Figure 1 topology and coloured-root Sinocirsium scaffold.",
        })
    return minimum_distance, selected


def build_summary(rows: Sequence[Mapping[str, object]], groups: Sequence[Mapping[str, object]],
                  minimum_escape_distance: int, nearest: Sequence[Mapping[str, object]]) -> dict[str, object]:
    published = next(row for row in rows if as_bool(row,"is_published_topology"))
    group_index = {str(row["group"]): row for row in groups}
    rf_distribution = Counter(int(row["rooted_rf_distance_from_published"]) for row in rows)
    return {
        "analysis": "Chang 2026 var. takaoense six-tip topology robustness",
        "root_assumption": "Sinocirsium root fixed coloured",
        "branch_lengths_used": False,
        "tip_count": 6,
        "rooted_binary_topology_count": len(rows),
        "published_topology_id": published["topology_id"],
        "published_topology_newick": published["sample_topology_newick"],
        "published_minimum_changes": int(published["sinocirsium_coloured_root_minimum_changes"]),
        "published_optimal_histories": published["sinocirsium_coloured_root_optimal_histories"],
        "published_no_regain_minimum_changes": int(published["minimum_no_regain_changes"]),
        "published_no_regain_penalty": int(published["no_regain_penalty"]),
        "rooted_rf_definition": "symmetric difference in nontrivial rooted descendant clusters",
        "rooted_rf_distance_distribution": {str(k): v for k, v in sorted(rf_distribution.items())},
        "minimum_rf_distance_to_no_regain_optimum": minimum_escape_distance,
        "nearest_no_regain_topology_count": len(nearest),
        "nearest_no_regain_topology_ids": [row["topology_id"] for row in nearest],
        "all_topologies_regain_required_count": int(group_index["all_rooted_binary_topologies"]["regain_required_count"]),
        "all_topologies_regain_required_fraction": int(group_index["all_rooted_binary_topologies"]["regain_required_count"]) / len(rows),
        "bp_monophyletic_regain_required_count": int(group_index["bp_monophyletic"]["regain_required_count"]),
        "bp_monophyletic_topology_count": int(group_index["bp_monophyletic"]["topology_count"]),
        "w_monophyletic_regain_required_count": int(group_index["w_monophyletic"]["regain_required_count"]),
        "w_monophyletic_topology_count": int(group_index["w_monophyletic"]["topology_count"]),
        "single_split_perturbation_regain_required_count": int(group_index["published_plus_single_split_perturbations"]["regain_required_count"]),
        "single_split_perturbation_topology_count": int(group_index["published_plus_single_split_perturbations"]["topology_count"]),
        "audit_note": "The nearest loss-only set was recalculated from the current Figure 1 pectinate topology. Earlier stale RF4 IDs were invalid because the robustness script referenced superseded symbols/topology state.",
        "interpretation": {
            "local_robustness": "Every topology at rooted RF distance <=2 from Figure 1 still requires a regain in all minimum-change histories.",
            "global_sensitivity": "Across all 945 rooted binary resolutions, 270 require a regain and 675 permit a no-regain optimum; topology weights must therefore come from empirical gene-tree/network evidence.",
            "critical_structure": "BP monophyly enriches regain support (36/45), whereas W monophyly always permits a loss-only optimum (0/45 require regain).",
            "claim_limit": "This remains a topology-supported candidate regain. Introgression, ancestral polymorphism and molecular pathway reactivation are untested.",
        },
    }


def write_csv(path: Path, rows: Iterable[Mapping[str, object]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), extrasaction="ignore")
        writer.writeheader(); writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all-output", type=Path, default=DEFAULT_ALL_OUTPUT)
    parser.add_argument("--group-output", type=Path, default=DEFAULT_GROUP_OUTPUT)
    parser.add_argument("--nearest-output", type=Path, default=DEFAULT_NEAREST_OUTPUT)
    parser.add_argument("--summary-output", type=Path, default=DEFAULT_SUMMARY_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = analyse_topologies()
    groups = build_group_summaries(rows)
    minimum_distance, nearest = nearest_no_regain_rows(rows)
    summary = build_summary(rows, groups, minimum_distance, nearest)
    write_csv(args.all_output, rows, ALL_FIELDS)
    write_csv(args.group_output, groups, GROUP_FIELDS)
    write_csv(args.nearest_output, nearest, NEAREST_FIELDS)
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"rooted_binary_topologies={len(rows)}")
    print(f"published_topology_id={summary['published_topology_id']}")
    print(f"published_no_regain_penalty={summary['published_no_regain_penalty']}")
    print(f"nearest_no_regain_ids={'|'.join(summary['nearest_no_regain_topology_ids'])}")
    print(f"single_split_perturbations_requiring_regain={summary['single_split_perturbation_regain_required_count']}/{summary['single_split_perturbation_topology_count']}")
    print(f"all_topologies_requiring_regain={summary['all_topologies_regain_required_count']}/{summary['rooted_binary_topology_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
