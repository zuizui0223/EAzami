#!/usr/bin/env python3
"""Validate the frozen public-image colour observation coordinate table.

This gate exists because the table is used as the sampling frame for public
WorldClim sensitivity analyses. It must remain byte-identical to the table
regenerated from the frozen Azami exhaustive-environment artifact.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

EXPECTED_SHA256 = "1eadba060f7fa57a87f06c53caaadd04dc5fb8604c4a4a7d3a990d9de49cb27b"
EXPECTED_COUNTS = {
    "JPN_17": 14,
    "JPN_23": 20,
    "JPN_29": 9,
    "JPN_36": 10,
    "JPN_37": 92,
    "JPN_38": 42,
}
EXPECTED_TAXA = {
    "JPN_17": "Cirsium maritimum",
    "JPN_23": "Cirsium oligophyllum",
    "JPN_29": "Cirsium verutum",
    "JPN_36": "Cirsium sieboldii",
    "JPN_37": "Cirsium kamtschaticum",
    "JPN_38": "Cirsium pendulum",
}
EXPECTED_COLUMNS = [
    "paper_japan_member_id",
    "taxon_name",
    "obs_id",
    "latitude",
    "longitude",
    "corolla_lab_lightness_median",
    "corolla_lab_lightness_n_usable_heads",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(csv_path: Path, provenance_path: Path | None = None) -> dict:
    digest = sha256(csv_path)
    if digest != EXPECTED_SHA256:
        raise AssertionError(f"coordinate CSV SHA256 drift: {digest} != {EXPECTED_SHA256}")

    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != EXPECTED_COLUMNS:
            raise AssertionError(f"column drift: {reader.fieldnames}")
        rows = list(reader)

    if len(rows) != 187:
        raise AssertionError(f"row count drift: {len(rows)} != 187")

    counts = Counter(row["paper_japan_member_id"] for row in rows)
    if dict(sorted(counts.items())) != EXPECTED_COUNTS:
        raise AssertionError(f"taxon counts drift: {dict(counts)}")

    obs_ids = [row["obs_id"] for row in rows]
    if len(set(obs_ids)) != len(obs_ids):
        raise AssertionError("obs_id must be unique")

    for row in rows:
        jpn = row["paper_japan_member_id"]
        if jpn not in EXPECTED_TAXA:
            raise AssertionError(f"unexpected taxon id: {jpn}")
        if row["taxon_name"] != EXPECTED_TAXA[jpn]:
            raise AssertionError(f"taxon-name mismatch for {jpn}: {row['taxon_name']}")
        lat = float(row["latitude"])
        lon = float(row["longitude"])
        light = float(row["corolla_lab_lightness_median"])
        usable = int(row["corolla_lab_lightness_n_usable_heads"])
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise AssertionError(f"invalid coordinates for obs {row['obs_id']}: {lat}, {lon}")
        if not (0 <= light <= 100):
            raise AssertionError(f"invalid L* for obs {row['obs_id']}: {light}")
        if usable <= 0:
            raise AssertionError(f"non-positive usable-head count for obs {row['obs_id']}")

    if provenance_path is not None:
        p = json.loads(provenance_path.read_text(encoding="utf-8"))
        if p["coordinate_csv_sha256"] != digest:
            raise AssertionError("provenance SHA does not match coordinate CSV")
        if p["row_count"] != len(rows):
            raise AssertionError("provenance row count does not match coordinate CSV")
        if p["taxon_counts"] != EXPECTED_COUNTS:
            raise AssertionError("provenance taxon counts do not match frozen contract")

    result = {
        "contract_version": "japan38_global_colour_observation_coordinates_v1",
        "sha256": digest,
        "row_count": len(rows),
        "taxon_counts": EXPECTED_COUNTS,
        "unique_obs_ids": len(set(obs_ids)),
        "status": "validated",
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--provenance", type=Path)
    args = parser.parse_args()
    print(json.dumps(validate(args.csv, args.provenance), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
