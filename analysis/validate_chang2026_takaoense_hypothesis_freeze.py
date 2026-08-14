#!/usr/bin/env python3
"""Validate the frozen Chang 2026 six-tip hypothesis set against current sources."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Mapping, Sequence

import build_chang2026_gene_tree_panel as panel_builder

DEFAULT_NEAREST = Path("analysis/chang2026_takaoense_nearest_no_regain_topologies.csv")
DEFAULT_ROBUSTNESS = Path("analysis/chang2026_takaoense_topology_robustness_summary.json")
DEFAULT_FROZEN = Path("analysis/chang2026_takaoense_gene_tree_hypotheses_v1.csv")
FIELDS = panel_builder.HYPOTHESIS_FIELDS


def clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [{k: clean(v) for k, v in row.items()} for row in csv.DictReader(handle)]


def normalize(rows: Sequence[Mapping[str, object]]) -> list[dict[str, str]]:
    return [{field: clean(row.get(field, "")) for field in FIELDS} for row in rows]


def expected_rows(nearest: Path, robustness: Path) -> list[dict[str, str]]:
    generated = panel_builder.build_hypotheses(
        read_csv(nearest),
        json.loads(robustness.read_text(encoding="utf-8")),
    )
    return normalize(generated)


def validate(nearest: Path, robustness: Path, frozen: Path) -> list[dict[str, str]]:
    expected = expected_rows(nearest, robustness)
    observed = normalize(read_csv(frozen))
    if len(observed) != 8:
        raise ValueError(f"Frozen hypothesis set must contain eight rows, observed {len(observed)}")
    if observed != expected:
        for index, (left, right) in enumerate(zip(observed, expected), start=1):
            if left != right:
                differing = [field for field in FIELDS if left[field] != right[field]]
                raise ValueError(
                    f"Frozen hypothesis row {index} differs from current sources in {differing}: "
                    f"frozen={left!r}, current={right!r}"
                )
        if len(observed) != len(expected):
            raise ValueError("Frozen and generated hypothesis row counts differ")
        raise ValueError("Frozen hypothesis set differs from current sources")
    ids = [row["hypothesis_id"] for row in observed]
    if ids[0] != "H_REG_PUBLISHED":
        raise ValueError("Published candidate-regain hypothesis must remain first")
    if ids[1:] != [f"H_LOSS_ONLY_RF4_{index:02d}" for index in range(1, 8)]:
        raise ValueError(f"Unexpected frozen loss-only hypothesis IDs/order: {ids[1:]}")
    return observed


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--nearest", type=Path, default=DEFAULT_NEAREST)
    p.add_argument("--robustness", type=Path, default=DEFAULT_ROBUSTNESS)
    p.add_argument("--frozen", type=Path, default=DEFAULT_FROZEN)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    rows = validate(args.nearest, args.robustness, args.frozen)
    print(f"validated_hypotheses={len(rows)}")
    print("hypothesis_ids=" + "|".join(row["hypothesis_id"] for row in rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
