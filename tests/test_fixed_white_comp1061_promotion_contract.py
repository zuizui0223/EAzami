import importlib.util
import json
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis" / "validate_fixed_white_comp1061_promotion_contract.py"
CONTRACT = ROOT / "data" / "evidence" / "fixed_white_comp1061_promotion_contract_v1.json"
ATLAS = ROOT / "analysis" / "cirsium_flower_colour_atlas_v0_3_readiness.json"
TREE = ROOT / "data" / "evidence" / "flower_colour_rate_tree_contract_v0_2.json"
PANEL = ROOT / "sampling" / "FIXED_WHITE_TARGET_CAPTURE_PANEL_V0_1.csv"
PRIORITY = ROOT / "data" / "evidence" / "fixed_white_a1_priority_v2.csv"

spec = importlib.util.spec_from_file_location("fixed_white_promotion", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class FixedWhiteComp1061PromotionContractTest(unittest.TestCase):
    def validate(self, contract=CONTRACT):
        return mod.validate(contract, ATLAS, TREE, PANEL, PRIORITY)

    def test_current_contract_is_fail_closed_and_ready_for_data_acquisition(self):
        x = self.validate()
        self.assertEqual(x["a1_taxa"], ["Cirsium boninense", "Cirsium wulongense"])
        self.assertEqual(x["current_state_counts"], {"C": 17, "W": 3})
        self.assertEqual(x["frozen_loci"], 153)
        self.assertEqual(x["minimum_clean_recovered_loci_per_individual"], 123)
        self.assertEqual(x["minimum_passing_individuals_per_taxon"], 2)
        self.assertEqual(x["target_state_counts"], {"C": 17, "W": 5})
        self.assertEqual(x["target_focal_taxa"], 22)
        self.assertEqual(x["target_tree_tips_with_root"], 23)
        self.assertFalse(x["current_rate_fit_execution_allowed"])
        self.assertEqual(x["next_gate"], "recover_or_generate_homologous_A1_nuclear_data")

    def test_clean_locus_threshold_cannot_be_relaxed_posthoc(self):
        c = json.loads(CONTRACT.read_text())
        c["individual_recovery_gate"]["minimum_clean_recovered_loci"] = 122
        with tempfile.TemporaryDirectory() as td:
            p = pathlib.Path(td) / "contract.json"
            p.write_text(json.dumps(c))
            with self.assertRaisesRegex(ValueError, "ceil\\(0.8\\*153\\)=123"):
                self.validate(p)

    def test_expanded_tree_cannot_skip_reacceptance(self):
        c = json.loads(CONTRACT.read_text())
        c["expanded_tree_gate"]["rate_fit_unlock_requires_expanded_tree_reacceptance"] = False
        with tempfile.TemporaryDirectory() as td:
            p = pathlib.Path(td) / "contract.json"
            p.write_text(json.dumps(c))
            with self.assertRaisesRegex(ValueError, "reacceptance"):
                self.validate(p)


if __name__ == "__main__":
    unittest.main()
