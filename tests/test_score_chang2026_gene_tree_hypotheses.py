#!/usr/bin/env python3
"""Tests for per-gene Chang 2026 topology-hypothesis scoring."""

from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

ANALYSIS_DIR = Path(__file__).resolve().parents[1] / "analysis"
if str(ANALYSIS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_DIR))

import score_chang2026_gene_tree_hypotheses as mod  # noqa: E402


PANEL_ROWS = [
    {
        "sample_id": "FC_ccy3559",
        "taxon": "C. japonicum var. takaoense",
        "code": "FC",
        "voucher": "ccy3559",
        "morph": "BP",
        "panel_role": "focal_colour_morph",
    },
    {
        "sample_id": "TJ_ccy3807",
        "taxon": "C. japonicum var. takaoense",
        "code": "TJ",
        "voucher": "ccy3807",
        "morph": "BP",
        "panel_role": "focal_colour_morph",
    },
    {
        "sample_id": "NH_ccy3835",
        "taxon": "C. japonicum var. takaoense",
        "code": "NH",
        "voucher": "ccy3835",
        "morph": "BP",
        "panel_role": "focal_colour_morph",
    },
    {
        "sample_id": "WY_ccy3560",
        "taxon": "C. japonicum var. takaoense",
        "code": "WY",
        "voucher": "ccy3560",
        "morph": "W",
        "panel_role": "focal_colour_morph",
    },
    {
        "sample_id": "FB_ccy3629",
        "taxon": "C. japonicum var. takaoense",
        "code": "FB",
        "voucher": "ccy3629",
        "morph": "W",
        "panel_role": "focal_colour_morph",
    },
    {
        "sample_id": "LT_ccy3839",
        "taxon": "C. japonicum var. takaoense",
        "code": "LT",
        "voucher": "ccy3839",
        "morph": "W",
        "panel_role": "focal_colour_morph",
    },
    {
        "sample_id": "BT_ccy1000",
        "taxon": "C. japonicum var. albescens",
        "code": "BT",
        "voucher": "ccy1000",
        "morph": "",
        "panel_role": "white_sister_control",
    },
    {
        "sample_id": "AU_ccy2000",
        "taxon": "C. japonicum var. australe",
        "code": "AU",
        "voucher": "ccy2000",
        "morph": "",
        "panel_role": "coloured_flanking_introgression_control",
    },
    {
        "sample_id": "LN_ccy3000",
        "taxon": "C. lineare",
        "code": "LN",
        "voucher": "ccy3000",
        "morph": "",
        "panel_role": "outgroup",
    },
]

PUBLISHED = (
    "(((((NH_3835_BP,TJ_3807_BP),FC_3559_BP),LT_3839_W),"
    "FB_3629_W),WY_3560_W);"
)
LOSS_ONLY = (
    "(((((FB_3629_W,WY_3560_W),LT_3839_W),FC_3559_BP),"
    "TJ_3807_BP),NH_3835_BP);"
)


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


class GeneTreeHypothesisScorerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.panel_path = self.root / "panel.csv"
        self.hypothesis_path = self.root / "hypotheses.csv"
        write_csv(self.panel_path, PANEL_ROWS)
        write_csv(
            self.hypothesis_path,
            [
                {
                    "hypothesis_id": "H_REG_PUBLISHED",
                    "history_class": "topology_supported_candidate_regain",
                    "topology_newick": PUBLISHED,
                },
                *[
                    {
                        "hypothesis_id": f"H_LOSS_ONLY_RF4_{index:02d}",
                        "history_class": "nearest_loss_only_topology",
                        "topology_newick": LOSS_ONLY
                        if index == 1
                        else self._alternative_loss(index),
                    }
                    for index in range(1, 8)
                ],
            ],
        )
        self.focal, self.roles, self.morphs = mod.panel_metadata(
            self.panel_path
        )
        self.hypotheses = mod.hypothesis_metadata(self.hypothesis_path)

    def tearDown(self) -> None:
        self.temp.cleanup()

    @staticmethod
    def _alternative_loss(index: int) -> str:
        bp = ["FC_3559_BP", "TJ_3807_BP", "NH_3835_BP"]
        shift = index % 3
        bp = bp[shift:] + bp[:shift]
        return (
            f"(((((FB_3629_W,WY_3560_W),LT_3839_W),{bp[0]}),"
            f"{bp[1]}),{bp[2]});"
        )

    @staticmethod
    def published_sample_tree(support: str = "100") -> str:
        return (
            "(((((NH_ccy3835,TJ_ccy3807)"
            f"{support},FC_ccy3559){support},LT_ccy3839){support},"
            f"FB_ccy3629){support},WY_ccy3560);"
        )

    @staticmethod
    def loss_sample_tree() -> str:
        return (
            "(((((FB_ccy3629,WY_ccy3560)100,LT_ccy3839)100,"
            "FC_ccy3559)100,TJ_ccy3807)100,NH_ccy3835);"
        )

    def score(self, newick: str, threshold: float = 0.0):
        return mod.score_one_tree(
            gene_id="OG0001",
            tree_file="OG0001.treefile",
            tree=mod.parse_newick(newick),
            threshold=threshold,
            focal_labels=self.focal,
            roles=self.roles,
            morphs=self.morphs,
            hypotheses=self.hypotheses,
        )

    def test_support_parser_uses_ufboot_component(self) -> None:
        self.assertEqual(mod.parse_support("95/100"), 100.0)
        self.assertEqual(mod.parse_support("0.87"), 87.0)
        self.assertIsNone(mod.parse_support("node_name"))

    def test_newick_parser_handles_quotes_comments_and_lengths(self) -> None:
        tree = mod.parse_newick(
            "(('FC_ccy3559':0.1,'TJ_ccy3807':0.2)95/100[&x],NH_ccy3835);"
        )
        self.assertEqual(tree.children[0].support, 100.0)
        self.assertEqual(
            {leaf.name for leaf in mod.iter_leaves(tree)},
            {"FC_ccy3559", "TJ_ccy3807", "NH_ccy3835"},
        )

    def test_panel_labels_match_published_hypothesis(self) -> None:
        self.assertEqual(self.focal["FC_ccy3559"], "FC_3559_BP")
        self.assertEqual(self.focal["WY_ccy3560"], "WY_3560_W")
        self.assertEqual(len(self.focal), 6)

    def test_exact_published_gene_tree_is_published_best(self) -> None:
        detail, hypothesis_rows = self.score(self.published_sample_tree())
        self.assertEqual(detail["analysis_status"], "complete_single_copy")
        self.assertEqual(detail["classification"], "published_best")
        self.assertEqual(detail["exact_hypothesis_match"], "H_REG_PUBLISHED")
        published = next(
            row
            for row in hypothesis_rows
            if row["hypothesis_id"] == "H_REG_PUBLISHED"
        )
        self.assertEqual(published["rooted_rf_distance"], 0)
        self.assertEqual(published["conflicting_gene_clusters"], 0)

    def test_exact_loss_only_gene_tree_is_loss_only_best(self) -> None:
        detail, _ = self.score(self.loss_sample_tree())
        self.assertEqual(detail["classification"], "loss_only_best")
        self.assertIn("H_LOSS_ONLY_RF4_", detail["exact_hypothesis_match"])
        self.assertGreater(int(detail["published_rooted_rf_distance"]), 0)

    def test_star_tree_is_not_evidence(self) -> None:
        detail, _ = self.score(
            "(FC_ccy3559,TJ_ccy3807,NH_ccy3835,WY_ccy3560,"
            "FB_ccy3629,LT_ccy3839);"
        )
        self.assertEqual(detail["classification"], "unresolved_all_hypotheses_tie")
        self.assertEqual(detail["gene_cluster_count"], 0)

    def test_low_support_branches_collapse_at_high_threshold(self) -> None:
        low = self.published_sample_tree(support="40")
        detail_zero, _ = self.score(low, threshold=0)
        detail_high, _ = self.score(low, threshold=70)
        self.assertEqual(detail_zero["classification"], "published_best")
        self.assertEqual(
            detail_high["classification"], "unresolved_all_hypotheses_tie"
        )

    def test_missing_focal_sample_is_excluded(self) -> None:
        detail, rows = self.score(
            "((((NH_ccy3835,TJ_ccy3807),FC_ccy3559),LT_ccy3839),FB_ccy3629);"
        )
        self.assertEqual(detail["analysis_status"], "incomplete_focal_samples")
        self.assertIn("WY_ccy3560", detail["missing_focal_samples"])
        self.assertEqual(rows, [])

    def test_duplicate_focal_sample_is_excluded(self) -> None:
        detail, rows = self.score(
            "((((((NH_ccy3835,TJ_ccy3807),FC_ccy3559|a),FC_ccy3559|b),"
            "LT_ccy3839),FB_ccy3629),WY_ccy3560);"
        )
        self.assertEqual(detail["analysis_status"], "multicopy_focal_samples")
        self.assertIn("FC_ccy3559", detail["duplicate_focal_samples"])
        self.assertEqual(rows, [])

    def test_external_sister_affinity_is_descriptive(self) -> None:
        full_tree = (
            "(LN_ccy3000,(BT_ccy1000,("
            + self.published_sample_tree().rstrip(";")
            + ",AU_ccy2000)));"
        )
        detail, _ = self.score(full_tree)
        self.assertEqual(detail["analysis_status"], "complete_single_copy")
        self.assertIn(
            "coloured_flanking_introgression_control",
            detail["bp_external_sister_affinity"],
        )

    def test_threshold_validation(self) -> None:
        self.assertEqual(mod.thresholds_from_text("70,0,50,70"), (0.0, 50.0, 70.0))
        with self.assertRaises(ValueError):
            mod.thresholds_from_text("-1,50")

    def test_summary_separates_complete_and_excluded(self) -> None:
        published, _ = self.score(self.published_sample_tree(), threshold=70)
        incomplete, _ = self.score(
            "((((NH_ccy3835,TJ_ccy3807),FC_ccy3559),LT_ccy3839),FB_ccy3629);",
            threshold=70,
        )
        summary = mod.summarize([published, incomplete])
        self.assertEqual(summary[0]["tree_files"], 2)
        self.assertEqual(summary[0]["complete_single_copy_gene_trees"], 1)
        self.assertEqual(summary[0]["incomplete_focal_gene_trees"], 1)
        self.assertEqual(summary[0]["published_best"], 1)


if __name__ == "__main__":
    unittest.main()
