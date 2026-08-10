#!/usr/bin/env python3
"""Quantify how weak six-tip topology affects the takaoense regain inference.

The displayed Chang et al. (2026) Figure 1 topology nests a three-tip BP clade
inside successive white tips.  Under the source-backed coloured Sinocirsium root,
that exact resolution requires one W->C transition at the parsimony minimum.
Several internal sample branches are weakly supported, however.

This script enumerates all 945 rooted bifurcating topologies for the same six
labelled tips and repeats the same coloured-root Sinocirsium parsimony analysis.
The uniform topology count is a sensitivity diagnostic, not a posterior
probability distribution and not a substitute for gene-tree or network support.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from functools import lru_cache
from itertools import combinations
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from chang2026_takaoense_sample_colour_history import (
    ALBESCENS_TAKAOENSE_STATES,
    C,
    SINOCIRSIUM_STATES,
    TAKAOENSE_SIX,
    TAKAOENSE_STATES,
    W,
    minimum_summary,
)

DEFAULT_OUTPUT = Path(
    "analysis/chang2026_takaoense_topology_uncertainty.csv"
)
DEFAULT_SUMMARY = Path(
    "analysis/chang2026_takaoense_topology_uncertainty_summary.json"
)
DEFAULT_FULL_OUTPUT = Path(
    "data/evidence/generated/chang2026_takaoense_all_945_topologies.csv"
)

TIP_NAMES = tuple(sorted(TAKAOENSE_STATES))
BP_TIPS = frozenset(tip for tip, state in TAKAOENSE_STATES.items() if state == C)
W_TIPS = frozenset(tip for tip, state in TAKAOENSE_STATES.items() if state == W)

AGGREGATE_FIELDS = (
    "bp_monophyletic",
    "w_monophyletic",
    "regain_required_at_minimum",
    "no_regain_change_penalty",
    "n_topologies",
    "proportion_of_945",
    "interpretation",
)

FULL_FIELDS = (
    "topology_index",
    "takaoense_newick",
    "is_exact_displayed_topology",
    "bp_monophyletic",
    "w_monophyletic",
    "minimum_changes_coloured_sinocirsium_root",
    "optimal_directional_combinations",
    "regain_required_at_minimum",
    "minimum_no_regain_changes",
    "no_regain_change_penalty",
)


def tree_key(tree) -> str:
    if isinstance(tree, str):
        return tree
    return f"({tree_key(tree[0])},{tree_key(tree[1])})"


def canonical(tree):
    if isinstance(tree, str):
        return tree
    left = canonical(tree[0])
    right = canonical(tree[1])
    if tree_key(left) <= tree_key(right):
        return (left, right)
    return (right, left)


@lru_cache(maxsize=None)
def all_rooted_binary_trees(tips: tuple[str, ...]):
    """Return all unique rooted, unordered, fully bifurcating labelled trees."""
    tips = tuple(sorted(tips))
    if len(tips) == 1:
        return (tips[0],)

    first = tips[0]
    remainder = tips[1:]
    output = set()
    # Put the lexicographically first tip in the left partition to eliminate the
    # root left/right symmetry. Each child is canonicalized recursively.
    for extra_count in range(len(remainder)):
        for extra_left in combinations(remainder, extra_count):
            left_tips = tuple(sorted((first, *extra_left)))
            right_tips = tuple(sorted(set(remainder) - set(extra_left)))
            if not right_tips:
                continue
            for left in all_rooted_binary_trees(left_tips):
                for right in all_rooted_binary_trees(right_tips):
                    output.add(canonical((left, right)))
    return tuple(sorted(output, key=tree_key))


def descendant_sets(tree) -> tuple[frozenset[str], list[frozenset[str]]]:
    if isinstance(tree, str):
        return frozenset((tree,)), []
    left, left_clades = descendant_sets(tree[0])
    right, right_clades = descendant_sets(tree[1])
    current = left | right
    return current, [*left_clades, *right_clades, current]


def is_monophyletic(tree, target: frozenset[str]) -> bool:
    _, clades = descendant_sets(tree)
    return target in clades


def sinocirsium_tree(takaoense_tree):
    albescens_pair = ("albescens_BT_W", "albescens_KZ_W")
    albescens_plus_takaoense = (albescens_pair, takaoense_tree)
    return (
        "japonicum_C",
        (
            albescens_plus_takaoense,
            ("australe_C", "fukienense_C"),
        ),
    )


def directional_text(values: Sequence[tuple[int, int]]) -> str:
    return "|".join(
        f"losses={losses};regains={regains}" for losses, regains in values
    )


def analyze_topologies():
    topologies = all_rooted_binary_trees(TIP_NAMES)
    if len(topologies) != 945:
        raise ValueError(f"Expected 945 rooted six-tip topologies, observed {len(topologies)}")

    exact = canonical(TAKAOENSE_SIX)
    rows: list[dict[str, object]] = []
    for index, topology in enumerate(topologies, start=1):
        result = minimum_summary(
            sinocirsium_tree(topology),
            SINOCIRSIUM_STATES,
            C,
        )
        bp_monophyletic = is_monophyletic(topology, BP_TIPS)
        w_monophyletic = is_monophyletic(topology, W_TIPS)
        rows.append(
            {
                "topology_index": index,
                "takaoense_newick": tree_key(topology),
                "is_exact_displayed_topology": "yes" if topology == exact else "no",
                "bp_monophyletic": "yes" if bp_monophyletic else "no",
                "w_monophyletic": "yes" if w_monophyletic else "no",
                "minimum_changes_coloured_sinocirsium_root": result["minimum_changes"],
                "optimal_directional_combinations": directional_text(
                    result["directional_combinations"]
                ),
                "regain_required_at_minimum": (
                    "yes" if result["regain_required_at_global_minimum"] else "no"
                ),
                "minimum_no_regain_changes": result["minimum_no_regain_changes"],
                "no_regain_change_penalty": result["no_regain_change_penalty"],
            }
        )
    return rows


def interpretation(
    bp_monophyletic: str,
    w_monophyletic: str,
    regain_required: str,
    penalty: str,
) -> str:
    if regain_required == "yes":
        return (
            "Every minimum-change coloured-root history contains W->C; "
            f"best no-regain history costs +{penalty} change(s)"
        )
    return "At least one minimum-change coloured-root history contains no W->C"


def aggregate_rows(rows: Sequence[Mapping[str, object]]):
    counts: Counter[tuple[str, str, str, str]] = Counter()
    for row in rows:
        key = (
            str(row["bp_monophyletic"]),
            str(row["w_monophyletic"]),
            str(row["regain_required_at_minimum"]),
            str(row["no_regain_change_penalty"]),
        )
        counts[key] += 1

    output = []
    for key, count in sorted(counts.items()):
        bp, white, required, penalty = key
        output.append(
            {
                "bp_monophyletic": bp,
                "w_monophyletic": white,
                "regain_required_at_minimum": required,
                "no_regain_change_penalty": penalty,
                "n_topologies": count,
                "proportion_of_945": f"{count / 945:.9f}",
                "interpretation": interpretation(bp, white, required, penalty),
            }
        )
    return output


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


def build_summary(rows: Sequence[Mapping[str, object]]) -> dict[str, object]:
    exact_rows = [row for row in rows if row["is_exact_displayed_topology"] == "yes"]
    if len(exact_rows) != 1:
        raise ValueError(f"Expected one exact displayed topology, observed {len(exact_rows)}")
    exact = exact_rows[0]
    regain_required = [row for row in rows if row["regain_required_at_minimum"] == "yes"]
    no_regain_equal = [row for row in rows if row["regain_required_at_minimum"] == "no"]
    bp_mono = [row for row in rows if row["bp_monophyletic"] == "yes"]
    w_mono = [row for row in rows if row["w_monophyletic"] == "yes"]
    bp_only = [
        row
        for row in rows
        if row["bp_monophyletic"] == "yes" and row["w_monophyletic"] == "no"
    ]
    return {
        "tip_count": 6,
        "rooted_binary_topologies_enumerated": len(rows),
        "uniform_topology_enumeration_is_probability": False,
        "regain_required_topologies": len(regain_required),
        "regain_required_proportion": len(regain_required) / len(rows),
        "no_regain_allowed_at_minimum_topologies": len(no_regain_equal),
        "no_regain_allowed_at_minimum_proportion": len(no_regain_equal) / len(rows),
        "bp_monophyletic_topologies": len(bp_mono),
        "w_monophyletic_topologies": len(w_mono),
        "both_morphs_monophyletic_topologies": sum(
            row["bp_monophyletic"] == "yes" and row["w_monophyletic"] == "yes"
            for row in rows
        ),
        "bp_monophyletic_w_nonmonophyletic_topologies": len(bp_only),
        "bp_monophyletic_w_nonmonophyletic_regain_required": sum(
            row["regain_required_at_minimum"] == "yes" for row in bp_only
        ),
        "no_regain_penalty_counts_among_required": dict(
            sorted(
                Counter(
                    str(row["no_regain_change_penalty"])
                    for row in regain_required
                ).items()
            )
        ),
        "exact_displayed_topology": {
            "newick": exact["takaoense_newick"],
            "bp_monophyletic": exact["bp_monophyletic"],
            "w_monophyletic": exact["w_monophyletic"],
            "minimum_changes_coloured_sinocirsium_root": exact[
                "minimum_changes_coloured_sinocirsium_root"
            ],
            "optimal_directional_combinations": exact[
                "optimal_directional_combinations"
            ],
            "regain_required_at_minimum": exact["regain_required_at_minimum"],
            "minimum_no_regain_changes": exact["minimum_no_regain_changes"],
            "no_regain_change_penalty": exact["no_regain_change_penalty"],
        },
        "current_inference": (
            "The exact displayed pectinate topology requires W->C at the coloured-root "
            "Sinocirsium minimum, but 675 of 945 alternative rooted binary resolutions "
            "allow a no-regain history at the same minimum. Regain support is therefore "
            "topology-sensitive until weak internodes are resolved or modelled."
        ),
        "interpretation_limit": (
            "Uniform enumeration assigns no empirical weight to alternative topologies; "
            "it is a robustness boundary, not a posterior probability of regain."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--full-output", type=Path, default=DEFAULT_FULL_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    full = analyze_topologies()
    aggregate = aggregate_rows(full)
    summary = build_summary(full)
    write_csv(args.output, aggregate, AGGREGATE_FIELDS)
    write_csv(args.full_output, full, FULL_FIELDS)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"rooted_binary_topologies={summary['rooted_binary_topologies_enumerated']}")
    print(f"regain_required_topologies={summary['regain_required_topologies']}")
    print(
        "no_regain_allowed_topologies="
        f"{summary['no_regain_allowed_at_minimum_topologies']}"
    )
    print(f"regain_required_proportion={summary['regain_required_proportion']:.9f}")
    print(
        "exact_no_regain_penalty="
        f"{summary['exact_displayed_topology']['no_regain_change_penalty']}"
    )
    print(args.output)
    print(args.summary)
    print(args.full_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
