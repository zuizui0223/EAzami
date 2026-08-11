#!/usr/bin/env python3
"""Tests for exact SRA metadata and transparent resource planning."""

from __future__ import annotations

import csv
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ANALYSIS_DIR = Path(__file__).resolve().parents[1] / "analysis"
MODULE_PATH = ANALYSIS_DIR / "build_chang2026_resource_plan.py"
SPEC = importlib.util.spec_from_file_location(
    "build_chang2026_resource_plan", MODULE_PATH
)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
sys.modules["build_chang2026_resource_plan"] = mod
SPEC.loader.exec_module(mod)


class ChangResourcePlanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.panel, self.runinfo = self.make_inputs()

    def tearDown(self) -> None:
        self.temp.cleanup()

    @staticmethod
    def make_inputs():
        panel = []
        runinfo = []
        for index in range(1, 20):
            run = f"SRR{index:08d}"
            spots = 1000 + index
            focal = index <= 6
            panel.append(
                {
                    "sample_id": f"sample{index:02d}",
                    "taxon": "C. japonicum var. takaoense" if focal else "C. lineare",
                    "morph": "W" if index <= 3 else "BP" if focal else "",
                    "panel_role": "focal_colour_morph" if focal else "outgroup",
                    "matched_run": run,
                    "library_layout": "PAIRED",
                    "matched_spots": str(spots),
                }
            )
            runinfo.append(
                {
                    "Run": run,
                    "LibraryLayout": "PAIRED",
                    "spots": str(spots),
                    "spots_with_mates": str(spots),
                    "bases": str(spots * 300),
                    "avgLength": "300",
                    "size_MB": str(100 + index),
                }
            )
        return panel, runinfo

    def build(self):
        return mod.build_plan(
            self.panel,
            self.runinfo,
            fastq_bytes_per_base_min=2.2,
            fastq_bytes_per_base_max=3.0,
            working_disk_multiplier=2.5,
        )

    def test_builds_six_sample_pilot_and_full_nineteen_panel(self) -> None:
        rows = self.build()
        self.assertEqual(len(rows), 19)
        focal = [row for row in rows if row["execution_group"] == "takaoense6_pilot"]
        self.assertEqual(len(focal), 6)
        first = next(row for row in rows if row["sample_id"] == "sample01")
        self.assertEqual(first["spots"], 1001)
        self.assertEqual(first["paired_read_count"], 2002)
        self.assertEqual(first["bases"], 300300)
        self.assertEqual(first["derived_average_read_length"], "150.000")
        self.assertGreater(
            float(first["estimated_uncompressed_fastq_max_gib"]),
            float(first["estimated_uncompressed_fastq_min_gib"]),
        )
        self.assertGreater(
            float(first["estimated_working_disk_gib"]),
            float(first["estimated_uncompressed_fastq_max_gib"]),
        )

    def test_group_summary_retains_exact_metadata_totals(self) -> None:
        rows = self.build()
        focal = [row for row in rows if row["execution_group"] == "takaoense6_pilot"]
        summary = mod.group_summary(focal)
        expected_spots = sum(1000 + index for index in range(1, 7))
        self.assertEqual(summary["sample_count"], 6)
        self.assertEqual(summary["total_spots"], expected_spots)
        self.assertEqual(summary["total_paired_reads"], 2 * expected_spots)
        self.assertEqual(summary["total_bases"], expected_spots * 300)
        self.assertGreater(summary["recommended_free_disk_gib_rounded_up"], 0)

    def test_summary_freezes_inputs_and_execution_gate(self) -> None:
        rows = self.build()
        panel_path = self.root / "panel.csv"
        runinfo_path = self.root / "runinfo.csv"
        for path, values in ((panel_path, self.panel), (runinfo_path, self.runinfo)):
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(values[0]))
                writer.writeheader()
                writer.writerows(values)
        summary = mod.build_summary(
            rows,
            panel=panel_path,
            runinfo=runinfo_path,
            fastq_bytes_per_base_min=2.2,
            fastq_bytes_per_base_max=3.0,
            working_disk_multiplier=2.5,
        )
        self.assertEqual(summary["resource_plan_version"], "chang2026_resource_plan_v1")
        self.assertEqual(summary["takaoense6_pilot"]["sample_count"], 6)
        self.assertEqual(summary["full19_panel"]["sample_count"], 19)
        self.assertEqual(
            summary["workflow_resource_request"]["initial_parallel_sample_jobs"],
            1,
        )
        self.assertEqual(len(summary["panel_sha256"]), 64)
        self.assertEqual(len(summary["complete_runinfo_sha256"]), 64)

    def test_layout_mismatch_fails(self) -> None:
        self.runinfo[0]["LibraryLayout"] = "SINGLE"
        with self.assertRaisesRegex(ValueError, "LibraryLayout mismatch"):
            self.build()

    def test_spot_mismatch_fails(self) -> None:
        self.panel[0]["matched_spots"] = "999"
        with self.assertRaisesRegex(ValueError, "Spot-count mismatch"):
            self.build()

    def test_missing_runinfo_fails(self) -> None:
        self.runinfo.pop()
        with self.assertRaisesRegex(ValueError, "absent from complete runinfo"):
            self.build()

    def test_invalid_fastq_bounds_fail(self) -> None:
        with self.assertRaisesRegex(ValueError, "bounds"):
            mod.build_plan(
                self.panel,
                self.runinfo,
                fastq_bytes_per_base_min=3.0,
                fastq_bytes_per_base_max=2.0,
                working_disk_multiplier=2.5,
            )


if __name__ == "__main__":
    unittest.main()
