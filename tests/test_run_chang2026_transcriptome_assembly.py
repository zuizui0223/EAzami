#!/usr/bin/env python3
"""Tests for Chang 2026 official-layout SRA-to-proteome planning."""

from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from pathlib import Path

ANALYSIS_DIR = Path(__file__).resolve().parents[1] / "analysis"
if str(ANALYSIS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_DIR))

import run_chang2026_layout_aware_transcriptome_assembly as mod  # noqa: E402


class RunTranscriptomeAssemblyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.panel = self.root / "panel.csv"
        fields = [
            "sample_id",
            "taxon",
            "morph",
            "panel_role",
            "matched_run",
            "library_layout",
            "run_match_confidence",
            "preferred_sequence_source",
            "de_novo_required",
            "read_count_relation",
        ]
        rows = []
        for index in range(19):
            run = f"SRR{index + 1:06d}"
            rows.append(
                {
                    "sample_id": f"sample{index + 1:02d}",
                    "taxon": "C. japonicum var. takaoense"
                    if index < 6
                    else "C. lineare",
                    "morph": "W" if index < 3 else "BP" if index < 6 else "",
                    "panel_role": "focal_colour_morph" if index < 6 else "outgroup",
                    "matched_run": run,
                    "library_layout": "PAIRED",
                    "run_match_confidence": "verified",
                    "preferred_sequence_source": run,
                    "de_novo_required": "true",
                    # Deliberately heterogeneous: official layout, not this
                    # diagnostic, determines the command path.
                    "read_count_relation": (
                        "exact_paired_end_raw_reads_equals_2x_spots"
                        if index < 9
                        else "not_matching_reported_raw_reads"
                    ),
                }
            )
        with self.panel.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def first_row(self):
        return mod.validate_panel(self.panel)[0]

    def make_plan(self):
        return mod.command_plan(
            self.first_row(),
            outdir=self.root / "results",
            fasterq_threads=4,
            fastp_threads=4,
            trinity_threads=8,
            trinity_memory_gb=64,
            fasterq_executable="fasterq-dump",
            pigz_executable="pigz",
            fastp_executable="fastp",
            trinity_executable="Trinity",
            transdecoder_longorfs_executable="TransDecoder.LongOrfs",
            transdecoder_predict_executable="TransDecoder.Predict",
            python_executable="python",
            prefix_script=ANALYSIS_DIR / "prefix_fasta_headers.py",
        )

    def rewrite(self, rows):
        with self.panel.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    def test_validates_nineteen_unique_officially_paired_runs(self) -> None:
        rows = mod.validate_panel(self.panel)
        self.assertEqual(len(rows), 19)
        self.assertEqual(len({row["matched_run"] for row in rows}), 19)
        self.assertEqual({row["library_layout"] for row in rows}, {"PAIRED"})

    def test_validates_balanced_six_sample_focal_pilot(self) -> None:
        rows = mod.read_csv(self.panel)[:6]
        self.rewrite(rows)
        pilot = mod.validate_panel(self.panel, expected_samples=6)
        self.assertEqual(len(pilot), 6)
        self.assertEqual(
            {row["panel_role"] for row in pilot},
            {"focal_colour_morph"},
        )
        self.assertEqual(sum(row["morph"] == "W" for row in pilot), 3)
        self.assertEqual(sum(row["morph"] == "BP" for row in pilot), 3)

    def test_unbalanced_six_sample_pilot_fails(self) -> None:
        rows = mod.read_csv(self.panel)[:6]
        rows[0]["morph"] = "BP"
        self.rewrite(rows)
        with self.assertRaisesRegex(ValueError, "three BP and three W"):
            mod.validate_panel(self.panel, expected_samples=6)

    def test_selects_one_stable_sample_after_full_panel_validation(self) -> None:
        rows = mod.validate_panel(self.panel)
        selected = mod.select_panel_rows(rows, ["sample04"])
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]["sample_id"], "sample04")

    def test_unknown_or_duplicate_selected_sample_fails(self) -> None:
        rows = mod.validate_panel(self.panel)
        with self.assertRaisesRegex(ValueError, "absent"):
            mod.select_panel_rows(rows, ["missing"])
        with self.assertRaisesRegex(ValueError, "unique"):
            mod.select_panel_rows(rows, ["sample01", "sample01"])

    def test_mismatched_read_counts_do_not_override_official_layout(self) -> None:
        rows = mod.validate_panel(self.panel)
        mismatched = [
            row for row in rows if row["read_count_relation"] == "not_matching_reported_raw_reads"
        ]
        self.assertEqual(len(mismatched), 10)
        self.assertTrue(all(row["library_layout"] == "PAIRED" for row in mismatched))

    def test_wrong_panel_size_fails(self) -> None:
        rows = mod.read_csv(self.panel)[:-1]
        self.rewrite(rows)
        with self.assertRaises(ValueError):
            mod.validate_panel(self.panel)

    def test_duplicate_run_fails(self) -> None:
        rows = mod.read_csv(self.panel)
        rows[1]["matched_run"] = rows[0]["matched_run"]
        rows[1]["preferred_sequence_source"] = rows[0]["matched_run"]
        self.rewrite(rows)
        with self.assertRaises(ValueError):
            mod.validate_panel(self.panel)

    def test_missing_official_layout_fails_fast(self) -> None:
        rows = mod.read_csv(self.panel)
        rows[0]["library_layout"] = ""
        self.rewrite(rows)
        with self.assertRaisesRegex(ValueError, "lack official SRA LibraryLayout"):
            mod.validate_panel(self.panel)

    def test_single_end_layout_is_not_coerced_to_paired(self) -> None:
        rows = mod.read_csv(self.panel)
        rows[0]["library_layout"] = "SINGLE"
        rows[0]["read_count_relation"] = "exact_paired_end_raw_reads_equals_2x_spots"
        self.rewrite(rows)
        with self.assertRaisesRegex(ValueError, "not PAIRED"):
            mod.validate_panel(self.panel)

    def test_command_plan_contains_all_six_stages(self) -> None:
        plan = self.make_plan()
        self.assertEqual(plan["library_layout"], "PAIRED")
        self.assertIn("--split-files", plan["fasterq"])
        self.assertIn("--detect_adapter_for_pe", plan["fastp"])
        self.assertIn("--max_memory", plan["trinity"])
        self.assertIn("--single_best_only", plan["predict"])
        self.assertIn("--sample-id", plan["prefix"])
        self.assertTrue(str(plan["prefixed_proteome_fasta"]).endswith(".faa"))

    def test_dry_run_does_not_require_external_tools(self) -> None:
        result = mod.run_one(
            self.make_plan(),
            outdir=self.root / "results",
            dry_run=True,
            force=False,
            keep_raw_reads=False,
        )
        self.assertEqual(result["status"], "planned_dry_run")
        self.assertEqual(result["library_layout"], "PAIRED")
        self.assertEqual(result["error"], "")

    def test_existing_prefixed_proteome_is_skipped(self) -> None:
        plan = self.make_plan()
        prefixed = Path(str(plan["prefixed_proteome_fasta"]))
        prefixed.parent.mkdir(parents=True)
        prefixed.write_text(">sample01|x\nMPEPTIDE\n", encoding="utf-8")
        result = mod.run_one(
            plan,
            outdir=self.root / "results",
            dry_run=False,
            force=False,
            keep_raw_reads=False,
        )
        self.assertEqual(result["status"], "skipped_existing_prefixed_proteome")
        self.assertEqual(result["library_layout"], "PAIRED")

    def test_summary_counts_failures_layouts_and_subset_provenance(self) -> None:
        summary = mod.build_summary(
            [
                {
                    "sample_id": "sample01",
                    "status": "completed",
                    "library_layout": "PAIRED",
                },
                {
                    "sample_id": "sample02",
                    "status": "skipped_existing_prefixed_proteome",
                    "library_layout": "PAIRED",
                },
                {
                    "sample_id": "sample03",
                    "status": "failed",
                    "library_layout": "PAIRED",
                },
            ],
            dry_run=False,
            keep_raw_reads=False,
            input_panel_sample_count=6,
            selected_sample_ids=["sample01", "sample02", "sample03"],
        )
        self.assertEqual(summary["sample_count"], 3)
        self.assertEqual(summary["completed_or_existing_proteome_count"], 2)
        self.assertEqual(summary["failed_count"], 1)
        self.assertEqual(summary["official_library_layout_counts"], {"PAIRED": 3})
        self.assertEqual(summary["library_layout_source"], "official NCBI SRA LibraryLayout")
        self.assertEqual(summary["input_panel_sample_count"], 6)
        self.assertEqual(summary["selected_sample_count"], 3)
        self.assertEqual(
            summary["selected_sample_ids"],
            ["sample01", "sample02", "sample03"],
        )
        self.assertTrue(summary["subset_execution"])

    def test_jobs_must_be_positive(self) -> None:
        with self.assertRaises(ValueError):
            mod.execute(
                [],
                outdir=self.root,
                jobs=0,
                dry_run=True,
                force=False,
                keep_raw_reads=False,
            )


if __name__ == "__main__":
    unittest.main()
