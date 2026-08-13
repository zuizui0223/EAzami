#!/usr/bin/env python3
"""Tests for the capitulum-trait evidence contract."""

from __future__ import annotations

import csv
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "analysis"
    / "validate_capitulum_trait_records.py"
)
SPEC = importlib.util.spec_from_file_location(
    "validate_capitulum_trait_records", MODULE_PATH
)
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
sys.modules["validate_capitulum_trait_records"] = validator
SPEC.loader.exec_module(validator)


def valid_row() -> dict[str, str]:
    row = dict.fromkeys(validator.EXPECTED_FIELDS, "")
    row.update(
        {
            "record_id": "cap-0001",
            "individual_id": "ind-0001",
            "population_id": "pop-0001",
            "voucher_id": "KYO-example-1",
            "accepted_taxon": "Cirsium example",
            "source_taxon_name": "Cirsium example",
            "observation_level": "individual",
            "orientation_class": "nodding",
            "orientation_angle_deg": "145",
            "capitulum_diameter_mm": "32.5",
            "replicate_count": "3",
            "measurement_protocol": "field protocol v1",
            "source_type": "field_sheet",
            "source_citation": "EAzami field record 2026",
            "evidence_locator": "sheet-1 row-4",
            "evidence_status": "direct_field_measurement",
            "phylogeny_tip_id": "tip-example-1",
            "model_eligible": "true",
        }
    )
    return row


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(validator.EXPECTED_FIELDS))
        writer.writeheader()
        writer.writerows(rows)


class CapitulumTraitRecordTests(unittest.TestCase):
    def test_header_only_seed_schema_is_valid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "traits.csv"
            write_rows(path, [])
            self.assertEqual(validator.validate_records(path), [])

    def test_valid_individual_record(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "traits.csv"
            write_rows(path, [valid_row()])
            rows = validator.validate_records(path)
            self.assertEqual(rows[0]["record_id"], "cap-0001")

    def test_duplicate_record_id_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "traits.csv"
            write_rows(path, [valid_row(), valid_row()])
            with self.assertRaisesRegex(ValueError, "duplicate record_id"):
                validator.validate_records(path)

    def test_orientation_angle_outside_range_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "traits.csv"
            row = valid_row()
            row["orientation_angle_deg"] = "181"
            write_rows(path, [row])
            with self.assertRaisesRegex(ValueError, "outside"):
                validator.validate_records(path)

    def test_unreviewed_record_cannot_be_model_eligible(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "traits.csv"
            row = valid_row()
            row["evidence_status"] = "source_backed_rule_extracted_unreviewed"
            write_rows(path, [row])
            with self.assertRaisesRegex(ValueError, "cannot be model eligible"):
                validator.validate_records(path)

    def test_ineligible_record_requires_reason(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "traits.csv"
            row = valid_row()
            row["model_eligible"] = "false"
            write_rows(path, [row])
            with self.assertRaisesRegex(ValueError, "exclusion_reason"):
                validator.validate_records(path)


if __name__ == "__main__":
    unittest.main()
