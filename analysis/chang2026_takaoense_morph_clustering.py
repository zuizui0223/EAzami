#!/usr/bin/env python3
"""Exact balanced-label clustering test on the Chang 2026 six-tip topology.

The official Figure 1 directly labels three var. takaoense samples BP and three W.
Conditional on the displayed six-tip topology and exactly three BP labels, there
are only C(6, 3) = 20 possible label allocations. This script enumerates all 20,
calculates the Fitch score for each, and asks how often a random allocation is at
least as clustered as the observed labels.

The test is descriptive and topology-conditional. It does not account for weak
node support, geography, altitude, reticulation or non-random sampling.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from itertools import combinations
from math import comb
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from chang2026_takaoense_sample_colour_history import C, W, TAKAOENSE_SIX, fitch

DEFAULT_OUTPUT = Path("analysis/chang2026_takaoense_morph_clustering_permutations.csv")
DEFAULT_SUMMARY = Path(
    "data/evidence/generated/chang2026_takaoense_morph_clustering_summary.json"
)

OBSERVED_BP = frozenset({"NH_3835_BP", "TJ_3807_BP", "FC_3559_BP"})
OBSERVED_W = frozenset({"LT_3839_W", "FB_3629_W", "WY_3560_W"})

OUTPUT_FIELDS = (
    "allocation_index",
    "bp_tips",
    "w_tips",
    "fitch_changes",
    "fitch_root_states",
    "is_observed_oriented_assignment",
    "is_observed_unordered_partition",
    "is_at_least_as_clustered_as_observed",
)


def tip_names(tree) -> list[str]:
    if isinstance(tree, str):
        return [tree]
    return tip_names(tree[0]) + tip_names(tree[1])


def allocation_rows() -> list[dict[str, object]]:
    tips = sorted(tip_names(TAKAOENSE_SIX))
    if len(tips) != 6 or len(set(tips)) != 6:
        raise ValueError(f"Expected six unique tips, observed {tips!r}")
    if set(tips) != set(OBSERVED_BP | OBSERVED_W):
        raise ValueError("Observed W/BP labels and topology tips disagree")

    observed_states = {
        tip: ({C} if tip in OBSERVED_BP else {W})
        for tip in tips
    }
    _, observed_score = fitch(TAKAOENSE_SIX, observed_states)

    rows: list[dict[str, object]] = []
    for index, bp_tuple in enumerate(combinations(tips, 3), start=1):
        bp = frozenset(bp_tuple)
        white = frozenset(set(tips) - set(bp))
        states = {tip: ({C} if tip in bp else {W}) for tip in tips}
        root_states, score = fitch(TAKAOENSE_SIX, states)
        oriented = bp == OBSERVED_BP
        unordered = {bp, white} == {OBSERVED_BP, OBSERVED_W}
        rows.append(
            {
                "allocation_index": index,
                "bp_tips": "|".join(sorted(bp)),
                "w_tips": "|".join(sorted(white)),
                "fitch_changes": score,
                "fitch_root_states": "|".join(sorted(root_states)),
                "is_observed_oriented_assignment": "yes" if oriented else "no",
                "is_observed_unordered_partition": "yes" if unordered else "no",
                "is_at_least_as_clustered_as_observed": (
                    "yes" if score <= observed_score else "no"
                ),
            }
        )
    return rows


def summarize(rows: Sequence[Mapping[str, object]]) -> dict[str, object]:
    expected_allocations = comb(6, 3)
    if len(rows) != expected_allocations:
        raise ValueError(
            f"Expected {expected_allocations} balanced allocations, observed {len(rows)}"
        )
    observed = [
        row for row in rows
        if row["is_observed_oriented_assignment"] == "yes"
    ]
    if len(observed) != 1:
        raise ValueError("Expected one oriented observed assignment")
    observed_score = int(observed[0]["fitch_changes"])
    at_least = [
        row for row in rows
        if row["is_at_least_as_clustered_as_observed"] == "yes"
    ]
    unordered = [
        row for row in rows
        if row["is_observed_unordered_partition"] == "yes"
    ]
    distribution = Counter(int(row["fitch_changes"]) for row in rows)

    return {
        "topology": "(((((NH_BP,TJ_BP),FC_BP),LT_W),FB_W),WY_W)",
        "balanced_label_allocations": expected_allocations,
        "observed_bp_tips": sorted(OBSERVED_BP),
        "observed_w_tips": sorted(OBSERVED_W),
        "observed_fitch_changes": observed_score,
        "minimum_possible_fitch_changes": min(distribution),
        "score_distribution": {
            str(score): distribution[score] for score in sorted(distribution)
        },
        "oriented_observed_allocations": len(observed),
        "unordered_observed_partition_allocations": len(unordered),
        "allocations_at_least_as_clustered_as_observed": len(at_least),
        "exact_oriented_assignment_probability": len(observed) / expected_allocations,
        "exact_unordered_partition_probability": len(unordered) / expected_allocations,
        "exact_at_least_as_clustered_probability": len(at_least) / expected_allocations,
        "interpretation": (
            "The observed three-BP/three-W allocation has the minimum possible Fitch "
            "score of one. Only the observed orientation and its colour-swapped complement "
            "produce a one-change partition: 2 of 20 balanced allocations."
        ),
        "caveat": (
            "This exact random-label calculation is conditional on the transcribed tree "
            "and fixed 3:3 state counts. It does not control altitude, geography, ancestry, "
            "node support, reticulation or sampling design."
        ),
    }


def write_csv(
    path: Path,
    rows: Iterable[Mapping[str, object]],
    fields: Sequence[str] = OUTPUT_FIELDS,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = allocation_rows()
    payload = summarize(rows)
    write_csv(args.output, rows)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"balanced_label_allocations={payload['balanced_label_allocations']}")
    print(f"observed_fitch_changes={payload['observed_fitch_changes']}")
    print("score_distribution=" + json.dumps(payload["score_distribution"], sort_keys=True))
    print(
        "exact_oriented_assignment_probability="
        f"{payload['exact_oriented_assignment_probability']:.6f}"
    )
    print(
        "exact_unordered_partition_probability="
        f"{payload['exact_unordered_partition_probability']:.6f}"
    )
    print(
        "exact_at_least_as_clustered_probability="
        f"{payload['exact_at_least_as_clustered_probability']:.6f}"
    )
    print(args.output)
    print(args.summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
