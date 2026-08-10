#!/usr/bin/env python3
"""Tests for the Cirsium population-history evidence registry validator."""

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
    / "validate_cirsium_population_history_registry.py"
)
SPEC = importlib.util.spec_from_file_location(
    "validate_cirsium_population_history_registry", MODULE_PATH
)
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
sys.modules["validate_cirsium_population_history_registry"] = validator
SPEC.loader.exec_module(validator)


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(validator.EXPECTED_FIELDS))
        writer.writeheader()
        writer.writerows(rows)


def valid_row() -> dict[str, str]:
    return {
        "citation_key": "Example2020",
        "year": "2020",
        "taxon_or_system": "Cirsium example",
        "region": "Example_region",
        "study_scale": "population_genetics",
        "markers_or_data": "microsatellites",
        "sampling": "10 populations",
        "principal_finding": "Two genetic clusters were recovered.",
        "EAzami_relevance": "Tests ancestry alternatives.",
        "critical_limit": "Few loci.",
        "doi": "https://doi.org/10.1000/EXAMPLE",
        "data_or_access": "publisher",
    }


class PopulationHistoryRegistryTests(unittest.TestCase):
    def test_valid_registry_normalizes_doi(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "registry.csv"
            write_rows(path, [valid_row()])
            rows = validator.validate_registry(path)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["doi"], "10.1000/example")

    def test_duplicate_doi_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "registry.csv"
            first = valid_row()
            second = valid_row()
            second["citation_key"] = "Other2021"
            second["year"] = "2021"
            second["doi"] = "10.1000/example"
            write_rows(path, [first, second])
            with self.assertRaisesRegex(ValueError, "assigned to both"):
                validator.validate_registry(path)

    def test_empty_required_field_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "registry.csv"
            row = valid_row()
            row["sampling"] = ""
            write_rows(path, [row])
            with self.assertRaisesRegex(ValueError, "sampling"):
                validator.validate_registry(path)

    def test_header_drift_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "registry.csv"
            path.write_text("citation_key,year\nA,2020\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unexpected header"):
                validator.validate_registry(path)


if __name__ == "__main__":
    unittest.main()
