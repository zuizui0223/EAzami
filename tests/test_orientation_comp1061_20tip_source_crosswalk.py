import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CROSSWALK = ROOT / "data/evidence/orientation_comp1061_20tip_source_crosswalk_v1.csv"
SUMMARY = ROOT / "data/evidence/orientation_comp1061_20tip_source_crosswalk_summary_v1.json"
TREE_PANEL = ROOT / "data/evidence/colour_rate_comp1061_bridge_artifact_contract_v1.json"


class OrientationComp106120TipCrosswalkTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with CROSSWALK.open(encoding="utf-8", newline="") as handle:
            cls.rows = list(csv.DictReader(handle))
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        cls.tree_panel = json.loads(TREE_PANEL.read_text(encoding="utf-8"))

    def test_crosswalk_matches_frozen_tree_panel_exactly(self):
        crosswalk_tips = {row["tip_id"] for row in self.rows}
        tree_tips = {row["tip_id"] for row in self.tree_panel["primary_tips"]}
        self.assertEqual(len(self.rows), 20)
        self.assertEqual(len(crosswalk_tips), 20)
        self.assertEqual(crosswalk_tips, tree_tips)

    def test_fixed_binary_state_counts_are_balanced_and_frozen(self):
        resolved = [row for row in self.rows if row["analysis_state"] in {"U", "D"}]
        upward = [row for row in resolved if row["analysis_state"] == "U"]
        downward = [row for row in resolved if row["analysis_state"] == "D"]
        self.assertEqual(len(resolved), 17)
        self.assertEqual(len(upward), 9)
        self.assertEqual(len(downward), 8)

    def test_unresolved_taxa_are_not_forced_into_binary_states(self):
        unresolved = {row["tip_id"] for row in self.rows if row["analysis_state"] == "?"}
        self.assertEqual(
            unresolved,
            {
                "Cirsium_fanjingshanense",
                "Cirsium_maritimum",
                "Cirsium_nipponicum_var_incomptum",
            },
        )

    def test_no_exact_primary_voucher_orientation_is_claimed(self):
        self.assertTrue(self.rows)
        self.assertTrue(
            all(row["same_primary_voucher_state_verified"].lower() == "false" for row in self.rows)
        )

    def test_summary_matches_crosswalk_and_preserves_execution_gates(self):
        self.assertEqual(self.summary["panel_taxa"], 20)
        self.assertEqual(self.summary["fixed_binary_orientation_taxa"], 17)
        self.assertEqual(self.summary["fixed_state_counts"]["upward_or_erect"], 9)
        self.assertEqual(self.summary["fixed_state_counts"]["downward_or_nodding"], 8)
        self.assertTrue(
            self.summary["tree_reuse_decision"]["same_comp1061_branch_length_tree_is_informative_for_orientation"]
        )
        self.assertFalse(
            self.summary["tree_reuse_decision"]["additional_orientation_only_nuclear_tree_needed"]
        )
        gates = self.summary["execution_gates"]
        self.assertFalse(gates["branch_length_tree_completed"])
        self.assertTrue(gates["orientation_state_balance_gate_ge5_each"])
        self.assertFalse(gates["orientation_mk_preflight_execution_allowed_now"])
        self.assertTrue(gates["orientation_mk_preflight_allowed_after_accepted_tree"])
        self.assertFalse(gates["parallel_or_convergent_evolution_claim_allowed"])


if __name__ == "__main__":
    unittest.main()
