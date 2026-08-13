#!/usr/bin/env python3
"""Tests for exporting reproducible Moreyra public locus sets."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "analysis" / "export_moreyra_locus_manifests.py"
SPEC = importlib.util.spec_from_file_location("export_moreyra_locus_manifests", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
sys.modules["export_moreyra_locus_manifests"] = mod
SPEC.loader.exec_module(mod)


class MoreyraLocusManifestTests(unittest.TestCase):
    @staticmethod
    def row(
        locus: str,
        warning: str,
        occupancy: bool,
        passes: bool,
    ) -> dict[str, str]:
        return {
            "locus": locus,
            "paralog_warning_class": warning,
            "occupancy_ge_0_80": str(occupancy),
            "passes_reproducible_warning_and_occupancy_screen": str(passes),
            "final_350_membership": "unresolved_manual_tree_and_alignment_filter",
        }

    def test_build_sets(self) -> None:
        rows = [
            self.row("gene_clean", "no_paralog_warning", True, True),
            self.row(
                "gene_review",
                "manual_gene_tree_review_1_to_10_warnings",
                True,
                True,
            ),
            self.row("gene_low_occupancy", "no_paralog_warning", False, False),
            self.row(
                "gene_discard",
                "discard_gt10_paralog_warnings",
                True,
                False,
            ),
        ]
        sets = mod.build_sets(rows)
        self.assertEqual(
            sets["public_1061"],
            ["gene_clean", "gene_discard", "gene_low_occupancy", "gene_review"],
        )
        self.assertEqual(sets["reproducible_531"], ["gene_clean", "gene_review"])
        self.assertEqual(sets["conservative_241"], ["gene_clean"])
        self.assertEqual(sets["manual_review_290"], ["gene_review"])

    def test_candidate_partition_mismatch_fails(self) -> None:
        rows = [
            self.row("gene_clean", "no_paralog_warning", True, False),
        ]
        with self.assertRaises(ValueError):
            mod.build_sets(rows)

    def test_write_outputs_never_exports_exact_350(self) -> None:
        sets = {
            "public_1061": ["gene1", "gene2"],
            "reproducible_531": ["gene1"],
            "conservative_241": ["gene1"],
            "manual_review_290": [],
        }
        with tempfile.TemporaryDirectory() as tmp:
            summary = mod.write_outputs(Path(tmp), sets)
            self.assertFalse(summary["exact_moreyra_350_exported"])
            self.assertEqual(
                (Path(tmp) / "moreyra_public_1061_loci.txt").read_text(
                    encoding="utf-8"
                ),
                "gene1\ngene2\n",
            )
            self.assertTrue((Path(tmp) / "locus_set_manifest.csv").exists())
            self.assertTrue((Path(tmp) / "locus_set_manifest.json").exists())

    def test_parse_bool(self) -> None:
        for value in ("True", "1", "yes", "Y"):
            self.assertTrue(mod.parse_bool(value))
        for value in ("False", "0", "", "no"):
            self.assertFalse(mod.parse_bool(value))


if __name__ == "__main__":
    unittest.main()
