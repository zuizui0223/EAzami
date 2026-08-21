import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis" / "diagnose_arenicola_dated_asr_identifiability_v1.py"
SCAFFOLD = ROOT / "data" / "evidence" / "arenicola_dated_asr_scaffold_v1.json"
FROZEN = ROOT / "data" / "evidence" / "arenicola_dated_asr_rate_identifiability_v1.json"
spec = importlib.util.spec_from_file_location("asr_ident", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ArenicolaDatedASRIdentifiabilityTest(unittest.TestCase):
    def test_transition_probability_is_valid(self):
        self.assertAlmostEqual(mod.transition_probability(mod.W, mod.W, 0.0, 1.0), 1.0)
        self.assertAlmostEqual(mod.transition_probability(mod.W, mod.C, 0.0, 1.0), 0.0)
        self.assertGreater(mod.transition_probability(mod.W, mod.C, 1.0, 1.0), 0.0)
        self.assertLess(mod.transition_probability(mod.W, mod.C, 1.0, 1.0), 0.5)

    def test_frozen_result_and_rate_identifiability_boundary(self):
        result = mod.run(SCAFFOLD)
        frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
        self.assertEqual(result, frozen)
        self.assertEqual(len(result["profiles"]), 3)
        primary = result["primary_topology_key_results"]
        self.assertGreater(primary["P_C_arenicola_at_q_0_2"], 0.90)
        self.assertGreater(primary["P_C_arenicola_at_q_0_5"], 0.75)
        self.assertLess(primary["P_C_arenicola_at_q_1"], 0.65)
        self.assertTrue(primary["profile_LR95_hits_upper_rate_boundary"])
        self.assertTrue(result["diagnostics"]["all_topology_variants_support_coloured_MRCA_if_q_0_2"])
        self.assertTrue(result["diagnostics"]["all_topology_variants_profile_support_spans_coloured_to_uninformative"])
        self.assertFalse(result["diagnostics"]["rate_is_identified_from_six_tip_colour_pattern"])
        self.assertFalse(result["diagnostics"]["ancestral_state_is_identified_without_rate_constraint"])
        self.assertEqual(result["sampling_implication"]["immediate_new_focal_populations"], 0)
        self.assertIn("hybrid published-node-age sensitivity scaffold", result["claim_boundary"])

    def test_primary_threshold_is_not_a_hard_ancestral_probability(self):
        result = mod.run(SCAFFOLD)
        primary = result["profiles"][0]
        q75 = primary["q_where_P_C_arenicola_first_below_0_75"]
        self.assertGreater(q75, 0.45)
        self.assertLess(q75, 0.70)
        lo, hi = primary["profile_LR95_P_C_arenicola_range"]
        self.assertLessEqual(lo, 0.51)
        self.assertGreater(hi, 0.90)


if __name__ == "__main__":
    unittest.main()
