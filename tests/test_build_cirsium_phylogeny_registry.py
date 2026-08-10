#!/usr/bin/env python3
"""Tests for validation and merging of curated phylogeny registries."""

from __future__ import annotations

import csv
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "analysis" / "build_cirsium_phylogeny_registry.py"
SPEC = importlib.util.spec_from_file_location("build_cirsium_phylogeny_registry", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
registry = importlib.util.module_from_spec(SPEC)
sys.modules["build_cirsium_phylogeny_registry"] = registry
SPEC.loader.exec_module(registry)


def make_row(key: str, doi: str = "", tier: str = "A", year: str = "2025") -> dict[str, str]:
    return {
        "citation_key": key,
        "year": year,
        "scale": "regional_phylogeny",
        "region": "East_Asia",
        "title": f"Study {key}",
        "doi": doi,
        "evidence_type": "target_capture",
        "markers_or_loci": "350 nuclear loci",
        "sampling": "10 taxa",
        "principal_inference": "A supported relationship.",
        "known_limit": "Limited population sampling.",
        "EAzami_relevance": "Backbone evidence.",
        "evidence_tier": tier,
        "data_or_access": "public",
    }


def write_registry(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(registry.EXPECTED_FIELDS))
        writer.writeheader()
        writer.writerows(rows)


class RegistryBuilderTests(unittest.TestCase):
    def test_merge_valid_registries_and_normalize_doi(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = root / "first.csv"
            second = root / "second.csv"
            write_registry(first, [make_row("Later", "https://doi.org/10.1000/LATER", year="2026")])
            write_registry(second, [make_row("Earlier", "doi:10.1000/EARLIER", tier="B", year="2020")])
            rows = registry.merge_registries((first, second))
            self.assertEqual([row["citation_key"] for row in rows], ["Earlier", "Later"])
            self.assertEqual(rows[0]["doi"], "10.1000/earlier")
            self.assertEqual(rows[1]["doi"], "10.1000/later")

    def test_conflicting_duplicate_key_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = root / "first.csv"
            second = root / "second.csv"
            write_registry(first, [make_row("Same", "10.1000/one")])
            changed = make_row("Same", "10.1000/two")
            changed["title"] = "A conflicting study"
            write_registry(second, [changed])
            with self.assertRaisesRegex(ValueError, "Conflicting duplicate citation_key"):
                registry.merge_registries((first, second))

    def test_duplicate_doi_with_different_keys_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = root / "first.csv"
            second = root / "second.csv"
            write_registry(first, [make_row("One", "10.1000/shared")])
            write_registry(second, [make_row("Two", "https://doi.org/10.1000/SHARED")])
            with self.assertRaisesRegex(ValueError, "assigned to both"):
                registry.merge_registries((first, second))

    def test_invalid_tier_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.csv"
            write_registry(path, [make_row("BadTier", tier="Z")])
            with self.assertRaisesRegex(ValueError, "evidence_tier"):
                registry.merge_registries((path,))

    def test_unexpected_header_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad_header.csv"
            path.write_text("citation_key,title\nX,Y\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unexpected header"):
                registry.read_registry(path)


if __name__ == "__main__":
    unittest.main()
