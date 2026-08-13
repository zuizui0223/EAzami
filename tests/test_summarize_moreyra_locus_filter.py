#!/usr/bin/env python3
"""Offline tests for the reproducible Moreyra locus-filter reconstruction."""

from __future__ import annotations

import csv
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "analysis" / "summarize_moreyra_locus_filter.py"
SPEC = importlib.util.spec_from_file_location("summarize_moreyra_locus_filter", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
sys.modules["summarize_moreyra_locus_filter"] = mod
SPEC.loader.exec_module(mod)


class MoreyraLocusFilterTests(unittest.TestCase):
    @staticmethod
    def write_csv(path: Path, rows: list[list[str]], delimiter: str = ",") -> None:
        with path.open("w", encoding="utf-8", newline="") as handle:
            csv.writer(handle, delimiter=delimiter).writerows(rows)

    def test_paralog_warning_classes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "paralog.csv"
            header = ["Species", "gene_discard", "gene_review", "gene_clean", "", ""]
            rows = [header]
            for index in range(12):
                rows.append(
                    [
                        f"sample_{index}",
                        "2" if index < 11 else "1",
                        "2" if index < 3 else "1",
                        "1",
                        "",
                        "",
                    ]
                )
            self.write_csv(path, rows)
            parsed, metadata = mod.parse_paralog_matrix(path)

        self.assertEqual(metadata["named_locus_columns"], 3)
        self.assertEqual(metadata["trailing_or_blank_columns"], 2)
        self.assertEqual(
            parsed["gene_discard"]["paralog_warning_class"],
            "discard_gt10_paralog_warnings",
        )
        self.assertEqual(
            parsed["gene_review"]["paralog_warning_class"],
            "manual_gene_tree_review_1_to_10_warnings",
        )
        self.assertEqual(parsed["gene_clean"]["paralog_warning_class"], "no_paralog_warning")
        self.assertEqual(parsed["gene_discard"]["samples_with_gt_one_copy"], 11)
        self.assertEqual(parsed["gene_review"]["samples_with_gt_one_copy"], 3)

    def test_seq_lengths_excludes_meanlength_reference_row(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "lengths.tsv"
            self.write_csv(
                path,
                [
                    ["Species", "gene1", "gene2"],
                    ["MeanLength", "100", "200"],
                    ["sample_a", "90", ""],
                    ["sample_b", "110", "220"],
                ],
                delimiter="\t",
            )
            parsed, metadata, names = mod.parse_seq_lengths(path)

        self.assertEqual(metadata["raw_rows"], 3)
        self.assertEqual(metadata["reference_meanlength_rows"], 1)
        self.assertEqual(metadata["biological_sample_rows"], 2)
        self.assertEqual(names, ["sample_a", "sample_b"])
        self.assertEqual(parsed["gene1"]["raw_sequence_occupancy"], 1.0)
        self.assertEqual(parsed["gene2"]["raw_sequence_occupancy"], 0.5)
        self.assertTrue(parsed["gene1"]["occupancy_ge_0_80"])
        self.assertFalse(parsed["gene2"]["occupancy_ge_0_80"])

    def test_reconstruct_combines_warning_and_occupancy_without_claiming_final_350(self) -> None:
        paralog = {
            "gene_clean": {"paralog_warning_class": "no_paralog_warning"},
            "gene_review": {
                "paralog_warning_class": "manual_gene_tree_review_1_to_10_warnings"
            },
            "gene_discard": {"paralog_warning_class": "discard_gt10_paralog_warnings"},
        }
        seq = {
            "gene_clean": {"occupancy_ge_0_80": True},
            "gene_review": {"occupancy_ge_0_80": False},
            "gene_discard": {"occupancy_ge_0_80": True},
        }
        rows = {row["locus"]: row for row in mod.reconstruct(paralog, seq)}
        self.assertTrue(rows["gene_clean"]["passes_reproducible_warning_and_occupancy_screen"])
        self.assertFalse(rows["gene_review"]["passes_reproducible_warning_and_occupancy_screen"])
        self.assertFalse(rows["gene_discard"]["passes_reproducible_warning_and_occupancy_screen"])
        self.assertEqual(
            rows["gene_clean"]["final_350_membership"],
            "unresolved_manual_tree_and_alignment_filter",
        )

    def test_locus_set_mismatch_fails(self) -> None:
        with self.assertRaises(ValueError):
            mod.reconstruct(
                {"gene1": {"paralog_warning_class": "no_paralog_warning"}},
                {"gene2": {"occupancy_ge_0_80": True}},
            )

    def test_sample_membership_difference(self) -> None:
        rows = mod.sample_difference_rows(
            ["sample_a", "sample_b"],
            ["sample_b", "sample_c", "sample_d"],
        )
        self.assertEqual(
            rows,
            [
                {"sample_name": "sample_c", "membership": "seq_lengths_only"},
                {"sample_name": "sample_d", "membership": "seq_lengths_only"},
                {"sample_name": "sample_a", "membership": "hybpiper_stats_only"},
            ],
        )

    def test_summary_preserves_unresolved_manual_filter(self) -> None:
        rows = [
            {
                "paralog_warning_class": "no_paralog_warning",
                "occupancy_ge_0_80": True,
                "passes_reproducible_warning_and_occupancy_screen": True,
            },
            {
                "paralog_warning_class": "manual_gene_tree_review_1_to_10_warnings",
                "occupancy_ge_0_80": True,
                "passes_reproducible_warning_and_occupancy_screen": True,
            },
            {
                "paralog_warning_class": "discard_gt10_paralog_warnings",
                "occupancy_ge_0_80": True,
                "passes_reproducible_warning_and_occupancy_screen": False,
            },
        ]
        summary = mod.build_summary(
            rows,
            {"sample_rows": 2},
            {"biological_sample_rows": 2},
            ["sample_a"],
            ["sample_a", "sample_b"],
        )
        self.assertEqual(summary["public_named_loci"], 3)
        self.assertEqual(summary["paper_vs_public_named_locus_difference"], 1061)
        self.assertEqual(summary["loci_warning_le_10_and_occupancy_ge_0_80"], 2)
        self.assertFalse(summary["exact_final_350_locus_names_recovered"])
        self.assertEqual(summary["seq_length_samples_not_in_hybpiper_stats"], ["sample_b"])

    def test_implicit_outputs_follow_custom_audit_directory(self) -> None:
        custom = Path("/tmp/custom_moreyra")
        output, summary, sample_diff = mod.resolve_output_paths(
            custom,
            mod.DEFAULT_OUTPUT,
            mod.DEFAULT_SUMMARY,
            mod.DEFAULT_SAMPLE_DIFF,
        )
        self.assertEqual(output, custom / "paralog_locus_filter_reconstruction.csv")
        self.assertEqual(summary, custom / "locus_filter_reconstruction_summary.json")
        self.assertEqual(sample_diff, custom / "sample_matrix_membership_difference.csv")

    def test_explicit_outputs_are_not_relocated(self) -> None:
        custom = Path("/tmp/custom_moreyra")
        explicit = Path("/tmp/explicit.csv")
        output, _, _ = mod.resolve_output_paths(
            custom,
            explicit,
            mod.DEFAULT_SUMMARY,
            mod.DEFAULT_SAMPLE_DIFF,
        )
        self.assertEqual(output, explicit)


if __name__ == "__main__":
    unittest.main()
