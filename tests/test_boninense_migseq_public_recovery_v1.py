import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis" / "validate_boninense_migseq_public_recovery_v1.py"
RECOVERY = ROOT / "data" / "evidence" / "boninense_migseq_public_recovery_v1.json"
PRIORITY = ROOT / "data" / "evidence" / "fixed_white_a1_priority_v2.csv"
spec = importlib.util.spec_from_file_location("bon_mig", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class BoninenseMigseqPublicRecoveryTest(unittest.TestCase):
    def test_updated_recovery_state(self):
        x = mod.validate(RECOVERY, PRIORITY)
        self.assertEqual(x["boninense_method_confirmed"], "MIG-seq")
        self.assertEqual(x["comparison_taxa_count"], 5)
        self.assertFalse(x["sample_count_recovered"])
        self.assertFalse(x["raw_or_genotype_data_recovered"])
        self.assertFalse(x["compositae1061_tip_recovered"])
        self.assertFalse(x["rate_fit_tip_promotion_allowed"])
        self.assertEqual(x["new_core190_populations"], 0)


if __name__ == "__main__":
    unittest.main()
