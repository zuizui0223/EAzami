import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "pattern_reduction", ROOT / "analysis" / "simulate_macro_interaction_pattern_reduction.py"
)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)
TARGETS = ROOT / "data" / "evidence" / "macro_interaction_pattern_targets_v1.csv"


class PatternReductionTest(unittest.TestCase):
    def test_target_registry_contract(self):
        rows, by_id = MOD.load_targets(TARGETS)
        self.assertGreaterEqual(len(rows), 20)
        self.assertEqual(sum(r["simulation_role"] == "fit_target" for r in rows), 11)
        self.assertIn("INT_HERB_RR", by_id)
        self.assertEqual(by_id["INT_HERB_RR"]["target_value"], "2.67364")

    def test_deterministic_small_run(self):
        a = MOD.run(TARGETS, draws=3, seed=20260820)
        b = MOD.run(TARGETS, draws=3, seed=20260820)
        self.assertEqual(a, b)
        self.assertEqual(a["simulation_targets_scored"], 11)
        self.assertEqual(len(a["families"]), 5)
        self.assertEqual(set(a["ranking"]), set(MOD.FAMILIES))
        for fam in a["families"]:
            self.assertLessEqual(fam["best_match_count"], fam["n_targets"])
            self.assertGreaterEqual(fam["best_pattern_distance"], 0)


if __name__ == "__main__":
    unittest.main()
