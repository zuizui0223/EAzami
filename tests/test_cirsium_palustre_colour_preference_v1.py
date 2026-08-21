import csv
import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis" / "reconstruct_cirsium_palustre_colour_preference_v1.py"
CASES = ROOT / "data" / "evidence" / "cirsium_palustre_colour_preference_fig24_v1.csv"
FROZEN = ROOT / "data" / "evidence" / "cirsium_palustre_colour_preference_fig24_v1.json"
REGISTRY = ROOT / "data" / "evidence" / "capitulum_pattern_reduction_targets_v2.csv"

spec = importlib.util.spec_from_file_location("colour_pref", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ColourPreferenceTest(unittest.TestCase):
    def test_reconstruction_and_registry_contract(self):
        observed = mod.run(CASES)
        frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
        self.assertEqual(observed, frozen)
        self.assertEqual(observed["n_significant_white_preference_cases"], 6)
        self.assertGreater(observed["minimum_selection_ratio"], 1.0)
        self.assertEqual(observed["decision"], "use_as_soft_significance_conditioned_range_not_pooled_effect")

        rows = list(csv.DictReader(REGISTRY.open(encoding="utf-8", newline="")))
        row = {r["target_id"]: r for r in rows}["CIR_COLOUR_01"]
        self.assertEqual(row["target_kind"], "selection_ratio_conditional_range")
        self.assertAlmostEqual(float(row["estimate"]), observed["geometric_mean_selection_ratio"], places=6)
        self.assertAlmostEqual(float(row["lower"]), observed["minimum_selection_ratio"], places=6)
        self.assertAlmostEqual(float(row["upper"]), observed["maximum_selection_ratio"], places=6)
        self.assertEqual(row["use_in_simulation"], "soft")
        self.assertIn("significance-conditioned", row["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
