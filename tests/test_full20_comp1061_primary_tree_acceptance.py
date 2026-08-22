import hashlib
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "data" / "evidence" / "full20_comp1061_primary_tree_acceptance_v1.json"
TREE = ROOT / "data" / "evidence" / "full20_comp1061_primary_tree_v1.nwk"


class Full20Comp1061PrimaryTreeAcceptanceTest(unittest.TestCase):
    def test_frozen_tree_and_promotion_boundary(self):
        x = json.loads(EVIDENCE.read_text())
        tree = TREE.read_text()

        self.assertEqual(x["contract_version"], "full20_comp1061_primary_tree_acceptance_v1")
        self.assertEqual(hashlib.sha256(TREE.read_bytes()).hexdigest(), x["accepted_tree"]["sha256"])
        self.assertEqual(x["frozen_inputs"]["tree_loci"], 153)
        self.assertEqual(x["frozen_inputs"]["tree_tips"], 21)
        self.assertEqual(x["accepted_tree"]["branch_length_edge_count"], 39)
        self.assertTrue(x["accepted_tree"]["focal_monophyly_passed"])
        self.assertTrue(x["accepted_tree"]["tree_gate_ready"])
        self.assertEqual(x["iqtree"]["version"], "3.1.3")
        self.assertEqual(x["iqtree"]["best_fit_model_bic"], "TIM3+F+R3")
        self.assertEqual(x["colour_atlas"]["eligible_state_counts"], {"C": 17, "W": 3})
        self.assertFalse(x["colour_atlas"]["transition_rate_fit_ready"])
        self.assertEqual(x["colour_atlas"]["readiness_blockers"], ["minimum_white_tips"])
        self.assertTrue(x["promotion_boundary"]["primary_branch_length_tree_completed"])
        self.assertFalse(x["promotion_boundary"]["topology_sensitivity_completed"])
        self.assertFalse(x["promotion_boundary"]["rate_fit_execution_allowed"])
        self.assertEqual(x["promotion_boundary"]["remaining_blockers"], ["topology_sensitivity", "minimum_white_tips"])

        tips = re.findall(r"(?<=[(,])([A-Za-z0-9_]+):", tree)
        self.assertEqual(len(tips), 21)
        self.assertEqual(len(set(tips)), 21)
        self.assertIn("OUTGROUP_saff", tips)
        self.assertEqual(sum(t.startswith("Cirsium_") for t in tips), 20)


if __name__ == "__main__":
    unittest.main()
