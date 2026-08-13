#!/usr/bin/env python3
"""Validate the curated Cirsium population-history evidence registry.

Population-history studies are kept separate from species-tree evidence because
microsatellite, AFLP, landscape-genetic, invasion-history and expression studies
answer different questions. This validator prevents malformed rows, duplicate
citation keys/DOIs and silent schema drift.
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import Mapping

EXPECTED_FIELDS = (
    "citation_key",
    "year",
    "taxon_or_system",
    "region",
    "study_scale",
    "markers_or_data",
    "sampling",
    "principal_finding",
    "EAzami_relevance",
    "critical_limit",
    "doi",
    "data_or_access",
)
DEFAULT_INPUT = Path(
    "data/evidence/cirsium_population_history_literature_2026-08-10.csv"
)


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
        observed = tuple(reader.fieldnames or ())
        if observed != EXPECTED_FIELDS:
            raise ValueError(
                f"{path}: unexpected header. Expected {EXPECTED_FIELDS}, "
                f"observed {observed}"
            )
        rows = [
            {field: (row.get(field) or "").strip() for field in EXPECTED_FIELDS}
            for row in reader
            if any((row.get(field) or "").strip() for field in EXPECTED_FIELDS)
        ]
    return rows


def validate_row(row: Mapping[str, str], path: Path, row_number: int) -> None:
    prefix = f"{path}:{row_number}"
    for field in EXPECTED_FIELDS:
        if not row.get(field, "").strip():
            raise ValueError(f"{prefix}: required field {field!r} is empty")
    if not re.fullmatch(r"\d{4}", row["year"]):
        raise ValueError(f"{prefix}: invalid four-digit year {row['year']!r}")
    doi = canonical_doi(row["doi"])
    if not doi.startswith("10."):
        raise ValueError(f"{prefix}: malformed DOI {row['doi']!r}")


def validate_registry(path: Path) -> list[dict[str, str]]:
    rows = read_registry(path)
    seen_keys: dict[str, int] = {}
    seen_dois: dict[str, str] = {}
    for row_number, row in enumerate(rows, start=2):
        validate_row(row, path, row_number)
        key = row["citation_key"]
        if key in seen_keys:
            raise ValueError(
                f"{path}:{row_number}: duplicate citation_key {key!r}; "
                f"first seen at row {seen_keys[key]}"
            )
        seen_keys[key] = row_number
        doi = canonical_doi(row["doi"])
        previous_key = seen_dois.get(doi)
        if previous_key and previous_key != key:
            raise ValueError(
                f"{path}:{row_number}: DOI {doi!r} assigned to both "
                f"{previous_key!r} and {key!r}"
            )
        seen_dois[doi] = key
        row["doi"] = doi
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = validate_registry(args.input)
    years = [int(row["year"]) for row in rows]
    print(f"population_history_records={len(rows)}")
    if years:
        print(f"year_min={min(years)}")
        print(f"year_max={max(years)}")
    print(args.input)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
