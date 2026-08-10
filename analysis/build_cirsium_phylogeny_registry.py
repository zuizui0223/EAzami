#!/usr/bin/env python3
"""Validate and merge curated Cirsium phylogeny evidence registries.

The curated core and regional-addition files remain human-reviewable source files.
This script creates one current registry while preserving evidence tiers and failing
on duplicate citation keys or DOI conflicts instead of silently overwriting them.
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import Iterable, Mapping, Sequence

EXPECTED_FIELDS = (
    "citation_key",
    "year",
    "scale",
    "region",
    "title",
    "doi",
    "evidence_type",
    "markers_or_loci",
    "sampling",
    "principal_inference",
    "known_limit",
    "EAzami_relevance",
    "evidence_tier",
    "data_or_access",
)
DEFAULT_INPUTS = (
    Path("data/evidence/cirsium_phylogeny_literature_registry_2026-08-10.csv"),
    Path("data/evidence/cirsium_phylogeny_literature_registry_additions_2026-08-10.csv"),
)
DEFAULT_OUTPUT = Path(
    "data/evidence/generated/cirsium_phylogeny_literature_registry_current.csv"
)
VALID_TIERS = {"A", "B", "C", "D"}


def canonical_doi(value: str) -> str:
    value = (value or "").strip().casefold()
    value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value)
    value = re.sub(r"^doi:\s*", "", value)
    return value.rstrip(" .")


def read_registry(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != EXPECTED_FIELDS:
            raise ValueError(
                f"{path}: unexpected header. Expected {EXPECTED_FIELDS}, "
                f"observed {tuple(reader.fieldnames or ())}"
            )
        rows = [
            {field: (row.get(field) or "").strip() for field in EXPECTED_FIELDS}
            for row in reader
            if any((row.get(field) or "").strip() for field in EXPECTED_FIELDS)
        ]
    return rows


def validate_row(row: Mapping[str, str], source: Path, row_number: int) -> None:
    prefix = f"{source}:{row_number}"
    for field in ("citation_key", "year", "scale", "region", "title", "evidence_type"):
        if not row.get(field, "").strip():
            raise ValueError(f"{prefix}: required field {field!r} is empty")
    if not re.fullmatch(r"\d{4}", row["year"]):
        raise ValueError(f"{prefix}: year is not four digits: {row['year']!r}")
    if row["evidence_tier"] not in VALID_TIERS:
        raise ValueError(
            f"{prefix}: evidence_tier must be one of {sorted(VALID_TIERS)}, "
            f"observed {row['evidence_tier']!r}"
        )
    doi = canonical_doi(row.get("doi", ""))
    if doi and not doi.startswith("10."):
        raise ValueError(f"{prefix}: DOI is malformed: {row['doi']!r}")


def merge_registries(paths: Sequence[Path]) -> list[dict[str, str]]:
    by_key: dict[str, tuple[dict[str, str], Path]] = {}
    by_doi: dict[str, str] = {}

    for path in paths:
        rows = read_registry(path)
        for index, row in enumerate(rows, start=2):
            validate_row(row, path, index)
            key = row["citation_key"]
            if key in by_key:
                previous, previous_path = by_key[key]
                if previous != row:
                    raise ValueError(
                        f"Conflicting duplicate citation_key {key!r}: "
                        f"{previous_path} and {path}"
                    )
                continue

            doi = canonical_doi(row["doi"])
            row["doi"] = doi
            if doi:
                previous_key = by_doi.get(doi)
                if previous_key and previous_key != key:
                    raise ValueError(
                        f"DOI {doi!r} is assigned to both {previous_key!r} and {key!r}"
                    )
                by_doi[doi] = key
            by_key[key] = (row, path)

    return sorted(
        (entry[0] for entry in by_key.values()),
        key=lambda row: (int(row["year"]), row["citation_key"].casefold()),
    )


def write_registry(path: Path, rows: Iterable[Mapping[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(EXPECTED_FIELDS))
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        action="append",
        dest="inputs",
        help="Curated registry CSV; repeat for multiple files.",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    inputs = tuple(args.inputs) if args.inputs else DEFAULT_INPUTS
    rows = merge_registries(inputs)
    write_registry(args.output, rows)

    tier_counts = {tier: 0 for tier in sorted(VALID_TIERS)}
    for row in rows:
        tier_counts[row["evidence_tier"]] += 1
    print(f"curated_records={len(rows)}")
    for tier, count in tier_counts.items():
        print(f"tier_{tier}={count}")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
