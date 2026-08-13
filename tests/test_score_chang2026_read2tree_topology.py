import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = REPO_ROOT / "analysis"
if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))

import score_chang2026_read2tree_topology as mod
import score_chang2026_gene_tree_hypotheses as scorer


class Read2TreeTopologyScorerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.panel = self.root / "panel.csv"
        self.refs = self.root / "refs.csv"
        rows = []
        for code, voucher, morph in [
            ("FC", "ccy3559", "BP"),
            ("TJ", "ccy3807", "BP"),
            ("NH", "ccy3835", "BP"),
            ("WY", "ccy3560", "W"),
            ("FB", "ccy3629", "W"),
            ("LT", "ccy3839", "W"),
        ]:
            rows.append(
                {
                    "sample_id": f"{code}_{voucher}",
                    "taxon": "C. japonicum var. takaoense",
                    "code": code,
                    "voucher": voucher,
                    "morph": morph,
                    "panel_role": "focal_colour_morph",
                }
            )
        self._write(self.panel, rows)
        self._write(
            self.refs,
            [
                {"oma_code": "CYNCS", "verified_in_oma": "true"},
                {"oma_code": "HELAN", "verified_in_oma": "true"},
                {"oma_code": "DAUCS", "verified_in_oma": "true"},
            ],
        )
        _, self.mapping = mod.read_panel(self.panel)
        _, self.ref_codes = mod.read_reference_manifest(self.refs)
        self.hypotheses = mod.build_hypotheses(
            REPO_ROOT / "analysis/chang2026_takaoense_nearest_no_regain_topologies.csv",
            REPO_ROOT / "analysis/chang2026_takaoense_topology_robustness_summary.json",
        )

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def _write(path: Path, rows):
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader(); writer.writerows(rows)

    def analyse_text(self, text: str, thresholds=(0.0,)):
        return mod.analyse(
            tree=scorer.parse_newick(text),
            focal_mapping=self.mapping,
            reference_codes=self.ref_codes,
            outgroup="DAUCS",
            hypotheses=self.hypotheses,
            thresholds=thresholds,
        )

    def test_published_topology_is_exact_best(self):
        tree = "(DAUCS,(HELAN,(CYNCS,(((((NH_ccy3835,TJ_ccy3807),FC_ccy3559),LT_ccy3839),FB_ccy3629),WY_ccy3560))));"
        details, per_h, payload = self.analyse_text(tree)
        self.assertTrue(payload["raw_focal_monophyletic"])
        self.assertEqual(details[0]["classification"], "published_best")
        self.assertEqual(details[0]["exact_hypothesis_match"], "H_REG_PUBLISHED")
        self.assertEqual(details[0]["published_rooted_rf_distance"], 0)
        self.assertEqual(len(per_h), 8)

    def test_nearest_loss_only_topology_is_loss_best(self):
        first = mod.read_csv(
            REPO_ROOT / "analysis/chang2026_takaoense_nearest_no_regain_topologies.csv"
        )[0]["sample_topology_newick"]
        replacement = {
            "FC_3559_BP": "FC_ccy3559",
            "TJ_3807_BP": "TJ_ccy3807",
            "NH_3835_BP": "NH_ccy3835",
            "WY_3560_W": "WY_ccy3560",
            "FB_3629_W": "FB_ccy3629",
            "LT_3839_W": "LT_ccy3839",
        }
        focal = first.rstrip(";")
        for old, new in replacement.items():
            focal = focal.replace(old, new)
        tree = f"(DAUCS,(HELAN,(CYNCS,{focal})));"
        details, _, _ = self.analyse_text(tree)
        self.assertEqual(details[0]["classification"], "loss_only_best")
        self.assertIn("H_LOSS_ONLY_RF4_", details[0]["exact_hypothesis_match"])

    def test_reference_nested_inside_focal_blocks_scoring(self):
        tree = "(DAUCS,(HELAN,((CYNCS,NH_ccy3835),((((TJ_ccy3807,FC_ccy3559),LT_ccy3839),FB_ccy3629),WY_ccy3560))));"
        details, per_h, payload = self.analyse_text(tree)
        self.assertFalse(payload["raw_focal_monophyletic"])
        self.assertEqual(details[0]["analysis_status"], "focal_not_monophyletic_raw_tree")
        self.assertEqual(details[0]["classification"], "not_scored")
        self.assertEqual(per_h, [])

    def test_low_support_focal_stem_blocks_high_threshold_only(self):
        focal = "(((((NH_ccy3835,TJ_ccy3807)100,FC_ccy3559)100,LT_ccy3839)100,FB_ccy3629)100,WY_ccy3560)20"
        tree = f"(DAUCS,(HELAN,(CYNCS,{focal})100)100);"
        details, _, payload = self.analyse_text(tree, thresholds=(0.0, 50.0))
        self.assertTrue(payload["raw_focal_monophyletic"])
        by_t = {row["support_threshold"]: row for row in details}
        self.assertEqual(by_t["0"]["classification"], "published_best")
        self.assertEqual(
            by_t["50"]["analysis_status"],
            "focal_monophyly_unresolved_at_threshold",
        )
        self.assertEqual(by_t["50"]["classification"], "not_scored")

    def test_unexpected_leaf_fails_contract(self):
        tree = "(DAUCS,(OTHER,(CYNCS,(((((NH_ccy3835,TJ_ccy3807),FC_ccy3559),LT_ccy3839),FB_ccy3629),WY_ccy3560))));"
        with self.assertRaisesRegex(ValueError, "unexpected"):
            self.analyse_text(tree)

    def test_reroot_works_when_input_root_is_arbitrary(self):
        # Same unrooted relationships as the published topology but the Newick
        # happens to start at HELAN rather than DAUCS.
        tree = "(HELAN,(DAUCS,(CYNCS,(((((NH_ccy3835,TJ_ccy3807),FC_ccy3559),LT_ccy3839),FB_ccy3629),WY_ccy3560))));"
        details, _, _ = self.analyse_text(tree)
        self.assertEqual(details[0]["classification"], "published_best")


if __name__ == "__main__":
    unittest.main()
