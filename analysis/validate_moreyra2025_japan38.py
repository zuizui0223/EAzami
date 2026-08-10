#!/usr/bin/env python3
"""Validate the paper-level reconstruction of Moreyra et al. Japan-38 sampling."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

DEFAULT_INPUT = Path(
    "data/evidence/moreyra2025_japan_38_membership_audit_2026-08-10.csv"
)
REQUIRED_FIELDS = (
    "paper_japan_member_id",
    "paper_taxon_concept",
    "tree_codes",
    "biosamples",
    "runs",
    "sample_origin_class",
    "paper_japan_membership_confidence",
    "nuclear_coverage_status",
)
EXPECTED_ORIGIN_COUNTS = {
    "direct_Japan_sample_or_public_locality": 30,
    "paper_japan_concept_metadata_conflict": 1,
    "cultivated_Japanese_taxon": 4,
    "cultivated_Japanese_taxon_name_conflict": 1,
    "Japanese_distributed_taxon_sampled_outside_Japan": 2,
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = set(REQUIRED_FIELDS) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path}: missing required fields {sorted(missing)}")
        return [
            {key: (value or "").strip() for key, value in row.items()}
            for row in reader
            if any((value or "").strip() for value in row.values())
        ]


def validate(rows: list[dict[str, str]]) -> dict[str, object]:
    if len(rows) != 38:
        raise ValueError(f"Expected 38 paper taxon concepts, observed {len(rows)}")

    ids = [row["paper_japan_member_id"] for row in rows]
    concepts = [row["paper_taxon_concept"] for row in rows]
    if len(set(ids)) != 38:
        raise ValueError("paper_japan_member_id values are not unique")
    if len(set(concepts)) != 38:
        raise ValueError("paper_taxon_concept values are not unique")

    expected_ids = [f"JPN_{index:02d}" for index in range(1, 39)]
    if ids != expected_ids:
        raise ValueError("Japan-38 rows are not ordered JPN_01 through JPN_38")

    observed_counts = Counter(row["sample_origin_class"] for row in rows)
    if dict(observed_counts) != EXPECTED_ORIGIN_COUNTS:
        raise ValueError(
            f"Unexpected membership-class counts: {dict(observed_counts)}"
        )

    if any(not row["tree_codes"] for row in rows):
        raise ValueError("Every paper concept must retain at least one tree code")
    if any(not row["biosamples"] for row in rows):
        raise ValueError("Every paper concept must retain at least one BioSample")
    if any(not row["runs"] for row in rows):
        raise ValueError("Every paper concept must retain at least one public run")
    if any(row["nuclear_coverage_status"] != "moreyra_sample_membership_verified" for row in rows):
        raise ValueError("All 38 paper concepts must have verified Moreyra membership")

    conflicts = [
        row for row in rows
        if row["sample_origin_class"] == "paper_japan_concept_metadata_conflict"
    ]
    if len(conflicts) != 1 or conflicts[0]["tree_codes"] != "Cirsium yuki-uenoanum":
        raise ValueError("Expected one retained yuki-uenoanum metadata conflict")

    incomptum = [
        row for row in rows
        if row["paper_taxon_concept"].startswith("Cirsium nipponicum var. incomptum")
    ]
    if len(incomptum) != 1 or "Cirsium tanakae" not in incomptum[0]["tree_codes"] or "Cirsium tonense" not in incomptum[0]["tree_codes"]:
        raise ValueError("tanakae/tonense must remain collapsed to one published incomptum concept")

    return {
        "paper_taxon_concepts": len(rows),
        "origin_class_counts": dict(observed_counts),
        "metadata_conflicts": len(conflicts),
        "all_membership_rows_have_public_runs": True,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = validate(read_rows(args.input))
    for key, value in summary.items():
        print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
