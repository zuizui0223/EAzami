#!/usr/bin/env python3
"""Tests for Chang 2026 SRA-to-proteome assembly planning."""

from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from pathlib import Path

ANALYSIS_DIR = Path(__file__).resolve().parents[1] / "analysis"
if str(ANALYSIS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_DIR))

import run_chang2026_transcriptome_assembly as mod  # noqa: E402


class RunTranscriptomeAssemblyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.panel = self.root / "panel.csv"
        fields = [
            "sample_id",
            "taxon",
            "morph",
            "matched_run",
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
                    "matched_run": run,
                    "run_match_confidence": "verified",
                    "preferred_sequence_source": run,
                    "de_novo_required": "true",
                    "read_count_relation": "exact_paired_end_raw_reads_equals_2x_spots",
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

    def test_validates_nineteen_unique_paired_runs(self) -> None:
        rows = mod.validate_panel(self.panel)
        self.assertEqual(len(rows), 19)
        self.assertEqual(len({row["matched_run"] for row in rows}), 19)

    def test_wrong_panel_size_fails(self) -> None:
        rows = mod.read_csv(self.panel)[:-1]
        with self.panel.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        with self.assertRaises(ValueError):
            mod.validate_panel(self.panel)

    def test_duplicate_run_fails(self) -> None:
        rows = mod.read_csv(self.panel)
        rows[1]["matched_run"] = rows[0]["matched_run"]
        rows[1]["preferred_sequence_source"] = rows[0]["matched_run"]
        with self.panel.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        with self.assertRaises(ValueError):
            mod.validate_panel(self.panel)

    def test_nonpaired_input_fails_fast(self) -> None:
        rows = mod.read_csv(self.panel)
        rows[0]["read_count_relation"] = "exact_single_end_raw_reads_equals_spots"
        with self.panel.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        with self.assertRaises(ValueError):
            mod.validate_panel(self.panel)

    def test_command_plan_contains_all_six_stages(self) -> None:
        plan = self.make_plan()
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

    def test_summary_counts_failures(self) -> None:
        summary = mod.build_summary(
            [
                {"status": "completed"},
                {"status": "skipped_existing_prefixed_proteome"},
                {"status": "failed"},
            ],
            dry_run=False,
            keep_raw_reads=False,
        )
        self.assertEqual(summary["sample_count"], 3)
        self.assertEqual(summary["completed_or_existing_proteome_count"], 2)
        self.assertEqual(summary["failed_count"], 1)

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
