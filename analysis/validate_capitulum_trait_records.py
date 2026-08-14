#!/usr/bin/env python3
"""Validate the population-aware capitulum-trait evidence contract."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Mapping


EXPECTED_FIELDS = (
    "record_id",
    "individual_id",
    "population_id",
    "voucher_id",
    "accepted_taxon",
    "source_taxon_name",
    "region",
    "locality",
    "latitude",
    "longitude",
    "observation_level",
    "observation_date",
    "phenophase",
    "capitulum_position",
    "orientation_class",
    "orientation_angle_deg",
    "capitulum_diameter_mm",
    "involucre_height_mm",
    "involucre_width_mm",
    "peduncle_length_mm",
    "phyllary_spine_length_mm",
    "phyllary_apex_class",
    "florets_per_capitulum",
    "replicate_count",
    "elevation_m",
    "habitat",
    "measurement_protocol",
    "source_type",
    "source_citation",
    "evidence_locator",
    "image_or_specimen_uri",
    "license",
    "evidence_status",
    "reviewer",
    "reviewed_date",
    "phylogeny_tip_id",
    "model_eligible",
    "exclusion_reason",
    "notes",
)

OBSERVATION_LEVELS = {"individual", "population_summary", "taxon_summary"}
ORIENTATION_CLASSES = {
    "erect",
    "inclined",
    "horizontal",
    "nodding",
    "pendulous",
    "variable",
    "not_observed",
}
EVIDENCE_STATES = {
    "direct_field_measurement",
    "direct_specimen_measurement",
    "direct_image_measurement",
    "source_reported",
    "source_backed_rule_extracted_unreviewed",
    "unresolved",
}
NONNEGATIVE_FIELDS = (
    "capitulum_diameter_mm",
    "involucre_height_mm",
    "involucre_width_mm",
    "peduncle_length_mm",
    "phyllary_spine_length_mm",
    "florets_per_capitulum",
    "replicate_count",
    "elevation_m",
)
DEFAULT_INPUT = Path("data/schema/capitulum_trait_records.csv")


def read_records(path: Path) -> list[dict[str, str]]:
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
        return [
            {field: (row.get(field) or "").strip() for field in EXPECTED_FIELDS}
            for row in reader
            if any((row.get(field) or "").strip() for field in EXPECTED_FIELDS)
        ]


def parse_number(
    row: Mapping[str, str], field: str, prefix: str
) -> float | None:
    value = row[field]
    if not value:
        return None
    try:
        return float(value)
    except ValueError as error:
        raise ValueError(f"{prefix}: {field} must be numeric, got {value!r}") from error


def validate_record(row: Mapping[str, str], path: Path, row_number: int) -> None:
    prefix = f"{path}:{row_number}"
    required = (
        "record_id",
        "accepted_taxon",
        "source_taxon_name",
        "observation_level",
        "orientation_class",
        "source_type",
        "source_citation",
        "evidence_locator",
        "evidence_status",
        "model_eligible",
    )
    for field in required:
        if not row[field]:
            raise ValueError(f"{prefix}: required field {field!r} is empty")

    if row["observation_level"] not in OBSERVATION_LEVELS:
        raise ValueError(f"{prefix}: invalid observation_level {row['observation_level']!r}")
    if row["orientation_class"] not in ORIENTATION_CLASSES:
        raise ValueError(f"{prefix}: invalid orientation_class {row['orientation_class']!r}")
    if row["evidence_status"] not in EVIDENCE_STATES:
        raise ValueError(f"{prefix}: invalid evidence_status {row['evidence_status']!r}")
    if row["model_eligible"] not in {"true", "false"}:
        raise ValueError(f"{prefix}: model_eligible must be 'true' or 'false'")

    latitude = parse_number(row, "latitude", prefix)
    longitude = parse_number(row, "longitude", prefix)
    angle = parse_number(row, "orientation_angle_deg", prefix)
    if latitude is not None and not -90 <= latitude <= 90:
        raise ValueError(f"{prefix}: latitude outside [-90, 90]")
    if longitude is not None and not -180 <= longitude <= 180:
        raise ValueError(f"{prefix}: longitude outside [-180, 180]")
    if angle is not None and not 0 <= angle <= 180:
        raise ValueError(f"{prefix}: orientation_angle_deg outside [0, 180]")

    for field in NONNEGATIVE_FIELDS:
        value = parse_number(row, field, prefix)
        if value is not None and value < 0:
            raise ValueError(f"{prefix}: {field} must be non-negative")

    if row["observation_level"] == "individual" and not (
        row["individual_id"] or row["voucher_id"]
    ):
        raise ValueError(
            f"{prefix}: individual observations require individual_id or voucher_id"
        )

    if row["model_eligible"] == "true":
        for field in ("measurement_protocol", "phylogeny_tip_id"):
            if not row[field]:
                raise ValueError(
                    f"{prefix}: model-eligible record requires {field!r}"
                )
        if row["evidence_status"] in {
            "source_backed_rule_extracted_unreviewed",
            "unresolved",
        }:
            raise ValueError(
                f"{prefix}: unreviewed or unresolved evidence cannot be model eligible"
            )
    elif not row["exclusion_reason"]:
        raise ValueError(f"{prefix}: ineligible record requires exclusion_reason")


def validate_records(path: Path) -> list[dict[str, str]]:
    rows = read_records(path)
    seen: dict[str, int] = {}
    for row_number, row in enumerate(rows, start=2):
        validate_record(row, path, row_number)
        record_id = row["record_id"]
        if record_id in seen:
            raise ValueError(
                f"{path}:{row_number}: duplicate record_id {record_id!r}; "
                f"first seen at row {seen[record_id]}"
            )
        seen[record_id] = row_number
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = validate_records(args.input)
    eligible = sum(row["model_eligible"] == "true" for row in rows)
    print(f"capitulum_trait_records={len(rows)}")
    print(f"model_eligible_records={eligible}")
    print(args.input)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
