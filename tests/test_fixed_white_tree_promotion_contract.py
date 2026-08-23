import importlib.util
import json
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis" / "validate_fixed_white_tree_promotion_contract.py"
CONTRACT = ROOT / "data" / "evidence" / "fixed_white_tree_promotion_contract_v0_2.json"
ATLAS = ROOT / "analysis" / "cirsium_flower_colour_atlas_v0_3_readiness.json"
TREE = ROOT / "data" / "evidence" / "flower_colour_rate_tree_contract_v0_2.json"
PANEL = ROOT / "sampling" / "FIXED_WHITE_TARGET_CAPTURE_PANEL_V0_1.csv"
PRIORITY = ROOT / "data" / "evidence" / "fixed_white_a1_priority_v2.csv"

spec = importlib.util.spec_from_file_location("fixed_white_tree_promotion", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class FixedWhiteTreePromotionContractTest(unittest.TestCase):
    def validate(self, contract=CONTRACT):
        return mod.validate(contract, ATLAS, TREE, PANEL, PRIORITY)

    def test_active_contract_is_fail_closed_and_ready_for_data_acquisition(self):
        x = self.validate()
        self.assertEqual(x["contract_version"], "fixed_white_tree_promotion_v0_2")
        self.assertEqual(x["a1_taxa"], ["Cirsium boninense", "Cirsium wulongense"])
        self.assertEqual(x["current_state_counts"], {"C": 17, "W": 3})
        self.assertEqual(x["external_samples_available"], 0)
        self.assertEqual(x["sample_intake_manifest"], "sampling/FIXED_WHITE_A1_SAMPLE_INTAKE_V0_1.csv")
        self.assertEqual(x["placement_min_sample_tips"], 24)
        self.assertEqual(x["frozen_loci"], 153)
        self.assertEqual(x["minimum_clean_recovered_loci_per_individual"], 123)
        self.assertEqual(x["minimum_passing_individuals_per_taxon"], 2)
        self.assertEqual(x["recovery_qc_evaluator"], "analysis/evaluate_fixed_white_a1_recovery_qc.py")
        self.assertEqual(x["final_states"], {"C": 17, "W": 5})
        self.assertEqual(x["final_taxa"], 22)
        self.assertEqual(x["target_tree_tips_with_root"], 23)
        self.assertFalse(x["current_rate_fit_execution_allowed"])
        self.assertEqual(x["next_gate"], "populate_mandatory_A1_intake_slots")
        self.assertTrue(x["valid"])

    def test_clean_locus_threshold_cannot_be_relaxed_posthoc(self):
        c = json.loads(CONTRACT.read_text())
        c["individual_recovery_gate"]["minimum_clean_recovered_loci"] = 122
        with tempfile.TemporaryDirectory() as td:
            p = pathlib.Path(td) / "contract.json"
            p.write_text(json.dumps(c))
            with self.assertRaisesRegex(ValueError, "ceil\\(0.8\\*153\\)=123"):
                self.validate(p)

    def test_posthoc_locus_removal_cannot_be_enabled(self):
        c = json.loads(CONTRACT.read_text())
        c["individual_recovery_gate"]["posthoc_locus_removal_allowed"] = True
        with tempfile.TemporaryDirectory() as td:
            p = pathlib.Path(td) / "contract.json"
            p.write_text(json.dumps(c))
            with self.assertRaisesRegex(ValueError, "post hoc locus reselection"):
                self.validate(p)

    def test_intake_manifest_cannot_be_swapped_after_data_arrive(self):
        c = json.loads(CONTRACT.read_text())
        c["a1_panel"]["sample_intake_manifest"] = "sampling/OTHER.csv"
        with tempfile.TemporaryDirectory() as td:
            p = pathlib.Path(td) / "contract.json"
            p.write_text(json.dumps(c))
            with self.assertRaisesRegex(ValueError, "canonical A1 intake manifest"):
                self.validate(p)

    def test_expanded_tree_cannot_skip_reacceptance(self):
        c = json.loads(CONTRACT.read_text())
        c["expanded_tree_gate"]["rate_fit_unlock_requires_expanded_tree_reacceptance"] = False
        with tempfile.TemporaryDirectory() as td:
            p = pathlib.Path(td) / "contract.json"
            p.write_text(json.dumps(c))
            with self.assertRaisesRegex(ValueError, "reacceptance"):
                self.validate(p)

    def test_public_priority_cannot_prematurely_promote_a1_tip(self):
        rows = PRIORITY.read_text()
        self.assertIn("Cirsium boninense", rows)
        self.assertIn("Cirsium wulongense", rows)
        self.assertIn("rate_fit_tip_promotion_allowed", rows.splitlines()[0])


if __name__ == "__main__":
    unittest.main()
