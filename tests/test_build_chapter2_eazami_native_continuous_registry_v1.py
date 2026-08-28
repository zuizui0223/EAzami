#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))

import build_chapter2_eazami_native_continuous_registry_v1 as target


def canonical_text_bytes(path: Path) -> bytes:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n").encode("utf-8")


class NativeContinuousRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = ROOT / "data" / "evidence" / "chapter2_eazami_native_continuous_trait_registry_v1.csv"
        cls.summary_path = (
            ROOT / "data" / "evidence" / "chapter2_eazami_native_continuous_trait_registry_summary_v1.json"
        )
        with cls.registry.open(encoding="utf-8", newline="") as handle:
            cls.rows = list(csv.DictReader(handle))
        cls.summary = json.loads(cls.summary_path.read_text(encoding="utf-8"))

    def test_frozen_registry_counts_and_hash(self) -> None:
        self.assertEqual(len(self.rows), 45)
        self.assertEqual(len({row["record_id"] for row in self.rows}), 45)
        self.assertEqual(len({row["taxon_concept"] for row in self.rows}), 15)
        digest = hashlib.sha256(canonical_text_bytes(self.registry)).hexdigest()
        self.assertEqual(digest, "a8f472d57040522e0fba755e0153f64b389352b0d6819ffc8b018dd00c1ddb39")
        self.assertEqual(self.summary["registry_sha256"], digest)

    def test_ranges_are_never_admitted_as_scalars(self) -> None:
        admitted = [row for row in self.rows if row["admission_status"] == "admitted_comparable_scalar"]
        ranges = [row for row in self.rows if row["admission_status"] == "context_only_range_not_scalar"]
        self.assertEqual(len(admitted), 35)
        self.assertEqual(len(ranges), 10)
        self.assertTrue(all("-" not in row["value"] for row in admitted))
        self.assertTrue(all(row["exclusion_reason"] == "range_not_collapsed_to_midpoint" for row in ranges))

    def test_identity_rights_and_independence_fields_are_complete(self) -> None:
        required = set(target.REQUIRED_OUTPUT_FIELDS)
        self.assertTrue(required.issubset(self.rows[0]))
        for row in self.rows:
            self.assertTrue(row["taxon_concept"])
            self.assertTrue(row["source_locator"].startswith("http"))
            self.assertTrue(row["rights_status"])
            self.assertTrue(row["measurement_protocol"])
            joined = " ".join(row.values()).casefold()
            self.assertNotIn("azami-derived value", joined)
            self.assertNotIn("azami workflow artifact", joined)
            self.assertNotIn("azami significance filter", joined)

    def test_coverage_gates_are_not_silently_promoted(self) -> None:
        self.assertEqual(self.summary["japan38_mapped_taxa"], 5)
        self.assertEqual(self.summary["japan38_admitted_scalar_taxa"], 0)
        self.assertEqual(
            self.summary["seven_taxon_direct_panel_traits"],
            [
                "measured_capitulum_length_cm",
                "measured_capitulum_width_cm",
                "phyllary_length_cm",
                "phyllary_protrusion_mm",
            ],
        )

    def test_builder_is_byte_deterministic(self) -> None:
        display = target.read_csv(
            ROOT / "data" / "evidence" / "comp1061_display_size_direct_seed_v1.csv",
            target.DISPLAY_FIELDS,
        )
        phyllary = target.read_csv(
            ROOT / "data" / "evidence" / "comp1061_phyllary_direct_seed_v1.csv",
            target.PHYLLARY_FIELDS,
        )
        japan = target.membership_map(
            ROOT / "data" / "evidence" / "moreyra2025_japan_38_membership_audit_2026-08-10.csv"
        )
        tips, locators = target.tip_and_locator_maps(
            ROOT / "data" / "evidence" / "orientation_comp1061_20tip_source_crosswalk_v1.csv",
            ROOT / "data" / "evidence" / "japan38_nmns_capitulum_trait_seed_v1.csv",
        )
        records = target.build_records(display, phyllary, japan, tips, locators)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "registry.csv"
            digest = target.write_registry(output, records)
            self.assertEqual(canonical_text_bytes(output), canonical_text_bytes(self.registry))
            self.assertEqual(digest, self.summary["registry_sha256"])


if __name__ == "__main__":
    unittest.main()
