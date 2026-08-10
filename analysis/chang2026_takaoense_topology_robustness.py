#!/usr/bin/env python3
"""Quantify topology sensitivity of the Chang 2026 takaoense regain signal.

The exact Figure 1 sample topology places the three bluish-purple (BP) tips
inside a grade of three white (W) tips.  With the broader Sinocirsium root fixed
as coloured, the exact topology has a two-change optimum containing one loss and
one regain; a no-regain history costs two additional changes.

This module asks how dependent that conclusion is on the six-tip topology.  It
enumerates every rooted binary topology for the six published morph-labelled
tips (945 resolutions), embeds each resolution in the same source-backed
Sinocirsium scaffold, and records:

* rooted Robinson-Foulds distance from the published topology;
* BP/W monophyly and the published NH-TJ sister pair;
* minimum changes under a coloured root;
* whether every globally optimal history requires at least one regain;
* the minimum no-regain score and its parsimony penalty.

No branch lengths are invented.  This is a topology-only robustness analysis,
not evidence that the molecular anthocyanin pathway was functionally restored.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from functools import lru_cache
from itertools import combinations
from pathlib import Path
from typing import Callable, Iterable, Mapping, Sequence

try:  # package import in tests
    from .chang2026_takaoense_sample_colour_history import (
        C,
        W,
        TIP_STATES,
        TAKA0ENSE_SAMPLE_TREE,
        Tree,
        fitch,
        format_histories,
        minimum_summary,
        to_newick,
    )
except ImportError:  # direct execution from analysis/
    from chang2026_takaoense_sample_colour_history import (
        C,
        W,
        TIP_STATES,
        TAKA0ENSE_SAMPLE_TREE,
        Tree,
        fitch,
        format_histories,
        minimum_summary,
        to_newick,
    )

# Compatibility guard for a possible future correction of the historical
# misspelling in the source module.  The current source exports
# ``TAKA0ENSE_SAMPLE_TREE`` with a zero.
PUBLISHED_SAMPLE_TREE: Tree = TAKA0ENSE_SAMPLE_TREE

SAMPLE_LABELS = tuple(
    sorted(
        (
            "FC_3559_BP",
            "TJ_3807_BP",
            "NH_3835_BP",
            "WY_3560_W",
            "FB_3629_W",
            "LT_3839_W",
        )
    )
)
BP_TIPS = frozenset(label for label in SAMPLE_LABELS if label.endswith("_BP"))
W_TIPS = frozenset(label for label in SAMPLE_LABELS if label.endswith("_W"))
NH_TJ_CHERRY = frozenset(("NH_3835_BP", "TJ_3807_BP"))

DEFAULT_ALL_OUTPUT = Path(
    "data/evidence/generated/chang2026_takaoense_topology_robustness_all.csv"
)
DEFAULT_GROUP_OUTPUT = Path(
    "analysis/chang2026_takaoense_topology_robustness_groups.csv"
)
DEFAULT_NEAREST_OUTPUT = Path(
    "analysis/chang2026_takaoense_nearest_no_regain_topologies.csv"
)
DEFAULT_SUMMARY_OUTPUT = Path(
    "analysis/chang2026_takaoense_topology_robustness_summary.json"
)

ALL_FIELDS = (
    "topology_id",
    "sample_topology_newick",
    "rooted_rf_distance_from_published",
    "is_published_topology",
    "bp_monophyletic",
    "w_monophyletic",
    "nh_tj_cherry_preserved",
    "six_tip_fitch_minimum_changes",
    "six_tip_fitch_root_states",
    "sinocirsium_coloured_root_minimum_changes",
    "sinocirsium_coloured_root_optimal_histories",
    "regain_required_at_global_minimum",
    "minimum_no_regain_changes",
    "no_regain_penalty",
)

GROUP_FIELDS = (
    "group",
    "topology_count",
    "regain_required_count",
    "regain_required_fraction",
    "no_regain_equal_optimum_count",
    "no_regain_penalty_1_count",
    "no_regain_penalty_2_count",
    "minimum_change_2_count",
    "minimum_change_3_count",
    "minimum_change_4_count",
    "interpretation",
)

NEAREST_FIELDS = (
    "topology_id",
    "sample_topology_newick",
    "rooted_rf_distance_from_published",
    "bp_monophyletic",
    "w_monophyletic",
    "nh_tj_cherry_preserved",
    "sinocirsium_coloured_root_minimum_changes",
    "sinocirsium_coloured_root_optimal_histories",
    "minimum_no_regain_changes",
    "no_regain_penalty",
    "interpretation",
)


def canonicalize(tree: Tree) -> Tree:
    """Return an unordered rooted tree with deterministic child ordering."""
    if isinstance(tree, str):
        return tree
    left = canonicalize(tree[0])
    right = canonicalize(tree[1])
    return (left, right) if to_newick(left) < to_newick(right) else (right, left)


@lru_cache(maxsize=None)
def all_rooted_binary_trees(labels: tuple[str, ...]) -> tuple[Tree, ...]:
    """Enumerate unique unordered rooted binary trees for labelled leaves."""
    labels = tuple(sorted(labels))
    if len(labels) == 1:
        return (labels[0],)

    first = labels[0]
    remaining = labels[1:]
    output: dict[str, Tree] = {}

    # Force the lexicographically first label into the left subset so each root
    # split is visited once rather than once per complementary partition.
    for left_size in range(1, len(labels)):
        for selected in combinations(remaining, left_size - 1):
            left_labels = tuple(sorted((first, *selected)))
            left_set = set(left_labels)
            right_labels = tuple(label for label in labels if label not in left_set)
            if not right_labels:
                continue
            for left_tree in all_rooted_binary_trees(left_labels):
                for right_tree in all_rooted_binary_trees(right_labels):
                    tree = canonicalize((left_tree, right_tree))
                    output[to_newick(tree)] = tree

    return tuple(output[key] for key in sorted(output))


def leaf_set(tree: Tree) -> frozenset[str]:
    if isinstance(tree, str):
        return frozenset((tree,))
    return leaf_set(tree[0]) | leaf_set(tree[1])


def nontrivial_rooted_clusters(tree: Tree) -> frozenset[frozenset[str]]:
    """Return rooted descendant clusters excluding leaves and the full set."""
    full = leaf_set(tree)
    clusters: set[frozenset[str]] = set()

    def walk(node: Tree) -> frozenset[str]:
        if isinstance(node, str):
            return frozenset((node,))
        descendants = walk(node[0]) | walk(node[1])
        if 1 < len(descendants) < len(full):
            clusters.add(descendants)
        return descendants

    walk(tree)
    return frozenset(clusters)


def rooted_rf_distance(left: Tree, right: Tree) -> int:
    """Symmetric difference in nontrivial rooted clusters."""
    return len(nontrivial_rooted_clusters(left) ^ nontrivial_rooted_clusters(right))


def sinocirsium_scaffold(sample_tree: Tree) -> Tree:
    """Embed a six-tip resolution in the source-backed Sinocirsium scaffold."""
    albescens_plus_takaoense: Tree = (
        ("albescens_BT_W", "albescens_KZ_W"),
        sample_tree,
    )
    return (
        "japonicum_C",
        (
            albescens_plus_takaoense,
            ("australe_C", "fukienense_C"),
        ),
    )


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def analyse_topologies() -> list[dict[str, object]]:
    published = canonicalize(PUBLISHED_SAMPLE_TREE)
    published_clusters = nontrivial_rooted_clusters(published)
    rows: list[dict[str, object]] = []

    trees = all_rooted_binary_trees(SAMPLE_LABELS)
    for index, sample_tree in enumerate(trees, start=1):
        clusters = nontrivial_rooted_clusters(sample_tree)
        six_fitch = fitch(sample_tree, TIP_STATES)
        scaffold = sinocirsium_scaffold(sample_tree)
        result = minimum_summary(scaffold, TIP_STATES, root_state=C)
        histories = list(result["minimum_histories"])
        regain_required = bool(histories) and all(regains > 0 for _, regains in histories)

        rows.append(
            {
                "topology_id": f"T{index:04d}",
                "sample_topology_newick": to_newick(sample_tree) + ";",
                "rooted_rf_distance_from_published": len(clusters ^ published_clusters),
                "is_published_topology": bool_text(sample_tree == published),
                "bp_monophyletic": bool_text(BP_TIPS in clusters),
                "w_monophyletic": bool_text(W_TIPS in clusters),
                "nh_tj_cherry_preserved": bool_text(NH_TJ_CHERRY in clusters),
                "six_tip_fitch_minimum_changes": six_fitch.changes,
                "six_tip_fitch_root_states": "|".join(sorted(six_fitch.root_states)),
                "sinocirsium_coloured_root_minimum_changes": result["minimum_changes"],
                "sinocirsium_coloured_root_optimal_histories": format_histories(histories),
                "regain_required_at_global_minimum": bool_text(regain_required),
                "minimum_no_regain_changes": result["minimum_no_regain_changes"],
                "no_regain_penalty": result["no_regain_penalty"],
            }
        )
    return rows


def as_bool(row: Mapping[str, object], field: str) -> bool:
    return str(row[field]).casefold() == "true"


def group_summary(
    rows: Sequence[Mapping[str, object]],
    group: str,
    predicate: Callable[[Mapping[str, object]], bool],
    interpretation: str,
) -> dict[str, object]:
    selected = [row for row in rows if predicate(row)]
    penalty_counts = Counter(int(row["no_regain_penalty"]) for row in selected)
    minimum_counts = Counter(
        int(row["sinocirsium_coloured_root_minimum_changes"]) for row in selected
    )
    regain_count = sum(
        as_bool(row, "regain_required_at_global_minimum") for row in selected
    )
    fraction = regain_count / len(selected) if selected else 0.0
    return {
        "group": group,
        "topology_count": len(selected),
        "regain_required_count": regain_count,
        "regain_required_fraction": f"{fraction:.6f}",
        "no_regain_equal_optimum_count": penalty_counts.get(0, 0),
        "no_regain_penalty_1_count": penalty_counts.get(1, 0),
        "no_regain_penalty_2_count": penalty_counts.get(2, 0),
        "minimum_change_2_count": minimum_counts.get(2, 0),
        "minimum_change_3_count": minimum_counts.get(3, 0),
        "minimum_change_4_count": minimum_counts.get(4, 0),
        "interpretation": interpretation,
    }


def build_group_summaries(rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    return [
        group_summary(
            rows,
            "all_rooted_binary_topologies",
            lambda row: True,
            "Worst-case topology uncertainty across all 945 rooted binary resolutions.",
        ),
        group_summary(
            rows,
            "bp_monophyletic",
            lambda row: as_bool(row, "bp_monophyletic"),
            "All three bluish-purple tips form one clade, but their position relative to white tips is unrestricted.",
        ),
        group_summary(
            rows,
            "w_monophyletic",
            lambda row: as_bool(row, "w_monophyletic"),
            "All three white tips form one clade; a loss-only explanation remains available.",
        ),
        group_summary(
            rows,
            "nh_tj_cherry",
            lambda row: as_bool(row, "nh_tj_cherry_preserved"),
            "The published NH-TJ sister pair is preserved, while other relationships vary.",
        ),
        group_summary(
            rows,
            "bp_monophyletic_and_nh_tj_cherry",
            lambda row: as_bool(row, "bp_monophyletic")
            and as_bool(row, "nh_tj_cherry_preserved"),
            "The full BP clade and its NH-TJ internal pair are preserved.",
        ),
        group_summary(
            rows,
            "published_plus_single_split_perturbations",
            lambda row: int(row["rooted_rf_distance_from_published"]) <= 2,
            "Published topology plus every rooted topology differing by at most one nontrivial cluster.",
        ),
        group_summary(
            rows,
            "published_plus_two_split_perturbations",
            lambda row: int(row["rooted_rf_distance_from_published"]) <= 4,
            "Published topology plus wider local rearrangements up to rooted RF distance four.",
        ),
        group_summary(
            rows,
            "published_topology",
            lambda row: as_bool(row, "is_published_topology"),
            "Exact Figure 1 sample topology.",
        ),
    ]


def nearest_no_regain_rows(
    rows: Sequence[Mapping[str, object]],
) -> tuple[int, list[dict[str, object]]]:
    candidates = [
        row
        for row in rows
        if int(row["no_regain_penalty"]) == 0
    ]
    minimum_distance = min(
        int(row["rooted_rf_distance_from_published"]) for row in candidates
    )
    output: list[dict[str, object]] = []
    for row in candidates:
        if int(row["rooted_rf_distance_from_published"]) != minimum_distance:
            continue
        output.append(
            {
                "topology_id": row["topology_id"],
                "sample_topology_newick": row["sample_topology_newick"],
                "rooted_rf_distance_from_published": minimum_distance,
                "bp_monophyletic": row["bp_monophyletic"],
                "w_monophyletic": row["w_monophyletic"],
                "nh_tj_cherry_preserved": row["nh_tj_cherry_preserved"],
                "sinocirsium_coloured_root_minimum_changes": row[
                    "sinocirsium_coloured_root_minimum_changes"
                ],
                "sinocirsium_coloured_root_optimal_histories": row[
                    "sinocirsium_coloured_root_optimal_histories"
                ],
                "minimum_no_regain_changes": row["minimum_no_regain_changes"],
                "no_regain_penalty": row["no_regain_penalty"],
                "interpretation": (
                    "Nearest rooted resolution in which a no-regain history is globally optimal."
                ),
            }
        )
    return minimum_distance, output


def write_csv(
    path: Path,
    rows: Iterable[Mapping[str, object]],
    fields: Sequence[str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def build_summary(
    rows: Sequence[Mapping[str, object]],
    groups: Sequence[Mapping[str, object]],
    minimum_escape_distance: int,
    nearest: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    published = next(row for row in rows if as_bool(row, "is_published_topology"))
    group_index = {str(row["group"]): row for row in groups}
    return {
        "analysis": "Chang 2026 var. takaoense six-tip topology robustness",
        "root_assumption": "Sinocirsium root fixed coloured",
        "branch_lengths_used": False,
        "tip_count": len(SAMPLE_LABELS),
        "rooted_binary_topology_count": len(rows),
        "published_topology_id": published["topology_id"],
        "published_topology_newick": published["sample_topology_newick"],
        "published_minimum_changes": int(
            published["sinocirsium_coloured_root_minimum_changes"]
        ),
        "published_optimal_histories": published[
            "sinocirsium_coloured_root_optimal_histories"
        ],
        "published_no_regain_minimum_changes": int(
            published["minimum_no_regain_changes"]
        ),
        "published_no_regain_penalty": int(published["no_regain_penalty"]),
        "minimum_rf_distance_to_no_regain_optimum": minimum_escape_distance,
        "nearest_no_regain_topology_count": len(nearest),
        "all_topologies_regain_required_count": int(
            group_index["all_rooted_binary_topologies"]["regain_required_count"]
        ),
        "all_topologies_regain_required_fraction": float(
            group_index["all_rooted_binary_topologies"]["regain_required_fraction"]
        ),
        "bp_monophyletic_regain_required_count": int(
            group_index["bp_monophyletic"]["regain_required_count"]
        ),
        "bp_monophyletic_topology_count": int(
            group_index["bp_monophyletic"]["topology_count"]
        ),
        "w_monophyletic_regain_required_count": int(
            group_index["w_monophyletic"]["regain_required_count"]
        ),
        "w_monophyletic_topology_count": int(
            group_index["w_monophyletic"]["topology_count"]
        ),
        "single_split_perturbation_regain_required_count": int(
            group_index["published_plus_single_split_perturbations"][
                "regain_required_count"
            ]
        ),
        "single_split_perturbation_topology_count": int(
            group_index["published_plus_single_split_perturbations"][
                "topology_count"
            ]
        ),
        "interpretation": {
            "local_robustness": (
                "Every topology at rooted RF distance <=2 from Figure 1 still requires "
                "a regain in all minimum-change histories."
            ),
            "global_sensitivity": (
                "Across all 945 rooted binary resolutions, only 270 require a regain; "
                "the inference is supported by the published local ordering, not by the "
                "3 BP / 3 W counts alone."
            ),
            "critical_structure": (
                "BP monophyly strongly enriches regain support (36/45), whereas W "
                "monophyly always permits a loss-only optimum (0/45 require regain)."
            ),
            "claim_limit": (
                "This remains a topology-supported candidate regain. Introgression, "
                "ancestral polymorphism and molecular pathway reactivation are untested."
            ),
        },
    }


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
    if len(rows) != 945:
        raise SystemExit(f"Expected 945 rooted binary topologies, observed {len(rows)}")

    groups = build_group_summaries(rows)
    minimum_distance, nearest = nearest_no_regain_rows(rows)
    summary = build_summary(rows, groups, minimum_distance, nearest)

    write_csv(args.all_output, rows, ALL_FIELDS)
    write_csv(args.group_output, groups, GROUP_FIELDS)
    write_csv(args.nearest_output, nearest, NEAREST_FIELDS)
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"rooted_binary_topologies={len(rows)}")
    print(f"published_topology_id={summary['published_topology_id']}")
    print(f"published_no_regain_penalty={summary['published_no_regain_penalty']}")
    print(
        "single_split_perturbations_requiring_regain="
        f"{summary['single_split_perturbation_regain_required_count']}/"
        f"{summary['single_split_perturbation_topology_count']}"
    )
    print(
        "all_topologies_requiring_regain="
        f"{summary['all_topologies_regain_required_count']}/"
        f"{summary['rooted_binary_topology_count']}"
    )
    print(
        "minimum_rf_distance_to_no_regain_optimum="
        f"{summary['minimum_rf_distance_to_no_regain_optimum']}"
    )
    print(args.group_output)
    print(args.nearest_output)
    print(args.summary_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
