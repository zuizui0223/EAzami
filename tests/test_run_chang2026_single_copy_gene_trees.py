#!/usr/bin/env python3
"""Tests for restartable MAFFT/ClipKIT/IQ-TREE planning."""

from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from pathlib import Path

ANALYSIS_DIR = Path(__file__).resolve().parents[1] / "analysis"
if str(ANALYSIS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_DIR))

import run_chang2026_single_copy_gene_trees as mod  # noqa: E402


class RunSingleCopyGeneTreesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.panel = self.root / "panel.csv"
        with self.panel.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle, fieldnames=["sample_id", "panel_role"]
            )
            writer.writeheader()
            writer.writerows(
                [
                    {"sample_id": "sampleA", "panel_role": "focal_colour_morph"},
                    {"sample_id": "lineare1", "panel_role": "outgroup"},
                    {"sample_id": "lineare2", "panel_role": "outgroup"},
                ]
            )
        self.fasta = self.root / "OG0001.fa"
        self.fasta.write_text(
            ">sampleA\nAAAA\n>lineare1\nCCCC\n>lineare2\nGGGG\n",
            encoding="utf-8",
        )
        self.manifest = self.root / "manifest.csv"
        with self.manifest.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["orthogroup_id", "normalized_fasta", "status"],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "orthogroup_id": "OG0001",
                    "normalized_fasta": str(self.fasta),
                    "status": "complete_single_copy",
                }
            )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_reads_exactly_two_outgroups(self) -> None:
        self.assertEqual(
            mod.read_outgroups(self.panel), ["lineare1", "lineare2"]
        )

    def test_invalid_outgroup_count_fails(self) -> None:
        with self.panel.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle, fieldnames=["sample_id", "panel_role"]
            )
            writer.writeheader()
            writer.writerow({"sample_id": "lineare1", "panel_role": "outgroup"})
        with self.assertRaises(ValueError):
            mod.read_outgroups(self.panel)

    def test_command_plan_is_rooted_and_reproducible(self) -> None:
        row = mod.complete_manifest_rows(self.manifest)[0]
        plan = mod.command_plan(
            row,
            outdir=self.root / "results",
            outgroups=["lineare1", "lineare2"],
            threads_per_gene=2,
            bootstrap_replicates=1000,
            alrt_replicates=1000,
            mafft_executable="mafft",
            clipkit_executable="clipkit",
            iqtree_executable="iqtree2",
        )
        self.assertEqual(plan["orthogroup_id"], "OG0001")
        self.assertIn("--auto", plan["mafft"])
        self.assertIn("smart-gap", plan["clipkit"])
        self.assertIn("-B", plan["iqtree"])
        self.assertIn("--alrt", plan["iqtree"])
        self.assertIn("lineare1,lineare2", plan["iqtree"])
        self.assertTrue(str(plan["tree_file"]).endswith("OG0001.treefile"))

    def test_dry_run_writes_planned_status_without_external_tools(self) -> None:
        row = mod.complete_manifest_rows(self.manifest)[0]
        plan = mod.command_plan(
            row,
            outdir=self.root / "results",
            outgroups=["lineare1", "lineare2"],
            threads_per_gene=1,
            bootstrap_replicates=100,
            alrt_replicates=100,
            mafft_executable="missing-mafft",
            clipkit_executable="missing-clipkit",
            iqtree_executable="missing-iqtree",
        )
        result = mod.run_one(
            plan,
            outdir=self.root / "results",
            dry_run=True,
            force=False,
        )
        self.assertEqual(result["status"], "planned_dry_run")
        self.assertEqual(result["error"], "")

    def test_existing_tree_is_skipped(self) -> None:
        row = mod.complete_manifest_rows(self.manifest)[0]
        plan = mod.command_plan(
            row,
            outdir=self.root / "results",
            outgroups=["lineare1", "lineare2"],
            threads_per_gene=1,
            bootstrap_replicates=100,
            alrt_replicates=100,
            mafft_executable="mafft",
            clipkit_executable="clipkit",
            iqtree_executable="iqtree2",
        )
        tree_file = Path(str(plan["tree_file"]))
        tree_file.parent.mkdir(parents=True)
        tree_file.write_text("(lineare1,(lineare2,sampleA));\n", encoding="utf-8")
        result = mod.run_one(
            plan,
            outdir=self.root / "results",
            dry_run=False,
            force=False,
        )
        self.assertEqual(result["status"], "skipped_existing_tree")

    def test_manifest_rejects_missing_normalized_fasta(self) -> None:
        self.fasta.unlink()
        with self.assertRaises(FileNotFoundError):
            mod.complete_manifest_rows(self.manifest)

    def test_summary_counts_failures(self) -> None:
        summary = mod.build_summary(
            [
                {"status": "completed"},
                {"status": "skipped_existing_tree"},
                {"status": "failed"},
            ],
            outgroups=["lineare1", "lineare2"],
            dry_run=False,
        )
        self.assertEqual(summary["orthogroup_count"], 3)
        self.assertEqual(summary["completed_or_existing_tree_count"], 2)
        self.assertEqual(summary["failed_count"], 1)

    def test_jobs_must_be_positive(self) -> None:
        with self.assertRaises(ValueError):
            mod.execute([], outdir=self.root, jobs=0, dry_run=True, force=False)


if __name__ == "__main__":
    unittest.main()
