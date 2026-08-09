#!/usr/bin/env python3
"""Validate the East Asian Cirsium flower-colour atlas.

Usage:
    python analysis/validate_colour_atlas.py data/flower_colour_records.csv
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

REQUIRED_COLUMNS = {
    "record_id",
    "accepted_taxon",
    "country",
    "evidence_type",
    "evidence_source",
    "assessable",
    "colour_state",
    "review_status",
}

ALLOWED_COLOURS = {
    "white",
    "near_white",
    "pale_pink",
    "pink",
    "purple",
    "blue_purple",
    "polymorphic",
    "unknown",
}

ALLOWED_ASSESSABLE = {"yes", "no", "unknown"}
ALLOWED_REVIEW = {"pending", "reviewed", "rejected"}


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def validate(path: Path) -> None:
    if not path.exists():
        fail(f"file not found: {path}")

    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            fail("missing header")

        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            fail(f"missing required columns: {sorted(missing)}")

        seen_ids: set[str] = set()
        n = 0
        problems: list[str] = []

        for line_no, row in enumerate(reader, start=2):
            n += 1
            rid = (row.get("record_id") or "").strip()
            if not rid:
                problems.append(f"line {line_no}: empty record_id")
            elif rid in seen_ids:
                problems.append(f"line {line_no}: duplicate record_id {rid}")
            seen_ids.add(rid)

            colour = (row.get("colour_state") or "").strip()
            if colour not in ALLOWED_COLOURS:
                problems.append(
                    f"line {line_no}: invalid colour_state {colour!r}; "
                    f"allowed={sorted(ALLOWED_COLOURS)}"
                )

            assessable = (row.get("assessable") or "").strip().lower()
            if assessable not in ALLOWED_ASSESSABLE:
                problems.append(
                    f"line {line_no}: invalid assessable {assessable!r}; "
                    f"allowed={sorted(ALLOWED_ASSESSABLE)}"
                )

            review = (row.get("review_status") or "").strip().lower()
            if review not in ALLOWED_REVIEW:
                problems.append(
                    f"line {line_no}: invalid review_status {review!r}; "
                    f"allowed={sorted(ALLOWED_REVIEW)}"
                )

            if assessable == "yes" and not (row.get("accepted_taxon") or "").strip():
                problems.append(f"line {line_no}: assessable record lacks accepted_taxon")

            if assessable == "yes" and not (row.get("evidence_source") or "").strip():
                problems.append(f"line {line_no}: assessable record lacks evidence_source")

            lat = (row.get("latitude") or "").strip()
            lon = (row.get("longitude") or "").strip()
            if bool(lat) != bool(lon):
                problems.append(f"line {line_no}: latitude/longitude must be supplied together")
            if lat and lon:
                try:
                    lat_f = float(lat)
                    lon_f = float(lon)
                    if not -90 <= lat_f <= 90:
                        problems.append(f"line {line_no}: latitude out of range")
                    if not -180 <= lon_f <= 180:
                        problems.append(f"line {line_no}: longitude out of range")
                except ValueError:
                    problems.append(f"line {line_no}: non-numeric coordinates")

        if problems:
            print("\n".join(problems))
            fail(f"validation failed with {len(problems)} problem(s)")

    print(f"OK: {n} records validated in {path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        fail("usage: validate_colour_atlas.py <flower_colour_records.csv>")
    validate(Path(sys.argv[1]))
