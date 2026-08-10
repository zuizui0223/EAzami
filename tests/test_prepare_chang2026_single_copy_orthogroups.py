#!/usr/bin/env python3
"""Tests for conservative OrthoFinder single-copy validation."""

from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from pathlib import Path

ANALYSIS_DIR = Path(__file__).resolve().parents[1] / "analysis"
if str(ANALYSIS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_DIR))

import prepare_chang2026_single_copy_orthogroups as mod  # noqa: E402


class PrepareSingleCopyOrthogroupsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.panel = self.root / "panel.csv"
        with self.panel.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["sample_id"])
            writer.writeheader()
            writer.writerows(
                [{"sample_id": "sampleA"}, {"sample_id": "sampleB"}, {"sample_id": "sampleC"}]
            )
        self.result_root = self.root / "orthofinder" / "Results_test"
        self.orthogroups = self.result_root / "Orthogroups"
        self.sequences = self.result_root / "Orthogroup_Sequences"
        self.orthogroups.mkdir(parents=True)
        self.sequences.mkdir(parents=True)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_single_copy_list(self, ids: list[str]) -> None:
        (self.orthogroups / "Orthogroups_SingleCopyOrthologues.txt").write_text(
            "\n".join(ids) + "\n", encoding="utf-8"
        )

    def write_fasta(self, orthogroup: str, records: list[tuple[str, str]]) -> None:
        (self.sequences / f"{orthogroup}.fa").write_text(
            "".join(f">{header}\n{sequence}\n" for header, sequence in records),
            encoding="utf-8",
        )

    def test_complete_one_sequence_per_sample_is_normalized(self) -> None:
        self.write_single_copy_list(["OG0001"])
        self.write_fasta(
            "OG0001",
            [
                ("sampleA|tx1", "AAAA"),
                ("sampleB|tx2", "CCCC"),
                ("sampleC|tx3", "GGGG"),
            ],
        )
        outdir = self.root / "out"
        manifest, summary = mod.prepare(self.root / "orthofinder", self.panel, outdir)
        self.assertEqual(manifest[0]["status"], "complete_single_copy")
        self.assertEqual(summary["complete_single_copy_count"], 1)
        self.assertEqual(
            (outdir / "fastas" / "OG0001.fa").read_text(encoding="utf-8"),
            ">sampleA\nAAAA\n>sampleB\nCCCC\n>sampleC\nGGGG\n",
        )

    def test_missing_sample_is_excluded(self) -> None:
        self.write_single_copy_list(["OG0001"])
        self.write_fasta(
            "OG0001",
            [("sampleA|tx1", "AAAA"), ("sampleB|tx2", "CCCC")],
        )
        manifest, summary = mod.prepare(
            self.root / "orthofinder", self.panel, self.root / "out"
        )
        self.assertEqual(manifest[0]["status"], "missing_panel_samples")
        self.assertEqual(manifest[0]["missing_samples"], "sampleC")
        self.assertEqual(summary["excluded_candidate_count"], 1)

    def test_duplicate_sample_sequence_is_excluded(self) -> None:
        self.write_single_copy_list(["OG0001"])
        self.write_fasta(
            "OG0001",
            [
                ("sampleA|tx1", "AAAA"),
                ("sampleA|tx2", "TTTT"),
                ("sampleB|tx3", "CCCC"),
                ("sampleC|tx4", "GGGG"),
            ],
        )
        manifest, _ = mod.prepare(
            self.root / "orthofinder", self.panel, self.root / "out"
        )
        self.assertEqual(manifest[0]["status"], "duplicate_sample_sequences")
        self.assertEqual(manifest[0]["duplicate_samples"], "sampleA")

    def test_unmapped_header_is_excluded(self) -> None:
        self.write_single_copy_list(["OG0001"])
        self.write_fasta(
            "OG0001",
            [
                ("sampleA|tx1", "AAAA"),
                ("sampleB|tx2", "CCCC"),
                ("mystery|tx3", "GGGG"),
            ],
        )
        manifest, _ = mod.prepare(
            self.root / "orthofinder", self.panel, self.root / "out"
        )
        self.assertEqual(manifest[0]["status"], "unmapped_headers")
        self.assertEqual(manifest[0]["unmapped_headers"], "mystery|tx3")

    def test_missing_source_fasta_is_audited(self) -> None:
        self.write_single_copy_list(["OG0001"])
        manifest, _ = mod.prepare(
            self.root / "orthofinder", self.panel, self.root / "out"
        )
        self.assertEqual(manifest[0]["status"], "source_fasta_missing")
        self.assertEqual(manifest[0]["observed_sequence_count"], 0)

    def test_multiple_result_sets_fail(self) -> None:
        self.write_single_copy_list(["OG0001"])
        other = self.root / "orthofinder" / "Results_other" / "Orthogroups"
        other.mkdir(parents=True)
        (other / "Orthogroups_SingleCopyOrthologues.txt").write_text(
            "OG0002\n", encoding="utf-8"
        )
        with self.assertRaises(ValueError):
            mod.find_single_copy_file(self.root / "orthofinder")

    def test_duplicate_panel_ids_fail(self) -> None:
        with self.panel.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["sample_id"])
            writer.writeheader()
            writer.writerows(
                [{"sample_id": "sampleA"}, {"sample_id": "sampleA"}]
            )
        with self.assertRaises(ValueError):
            mod.read_panel_samples(self.panel)


if __name__ == "__main__":
    unittest.main()
