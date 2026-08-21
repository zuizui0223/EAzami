import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis" / "diagnose_east_asia_colour_rate_information_v1.py"
SCAFFOLD = ROOT / "data" / "evidence" / "east_asia_fixed_colour_dated_scaffold_v1.json"
spec = importlib.util.spec_from_file_location("east_asia_colour_rate", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class EastAsiaColourRateInformationTest(unittest.TestCase):
    def test_transition_matrix(self):
        m = mod.transition_matrix(0.5, 1.0)
        self.assertAlmostEqual(sum(m[0]), 1.0)
        self.assertAlmostEqual(sum(m[1]), 1.0)
        self.assertGreater(m[0][0], 0.5)
        self.assertLess(m[0][1], 0.5)

    def test_expanded_context_still_rate_unidentified(self):
        x = mod.run(SCAFFOLD)
        self.assertEqual(x["n_fixed_tips"], 10)
        self.assertEqual(x["state_counts"], {"C": 7, "W": 3})
        self.assertEqual(x["n_nuisance_topology_scenarios"], 36)
        self.assertTrue(x["all_profile_LR95_hit_upper_grid_boundary"])
        self.assertFalse(x["diagnostics"]["expanded_fixed_tip_context_identifies_transition_rate"])
        self.assertFalse(x["diagnostics"]["expanded_fixed_tip_context_identifies_arenicola_ancestor_without_rate_constraint"])
        lo, hi = x["profile_LR95_P_C_arenicola_global_range"]
        self.assertLessEqual(lo, 0.5000001)
        self.assertGreater(hi, 0.85)
        self.assertEqual(x["sampling_implication"]["immediate_new_core190_populations"], 0)

    def test_low_rate_coloured_signal_is_conditional_not_final(self):
        x = mod.run(SCAFFOLD)
        r02 = x["reference_P_C_arenicola_ranges"]["0.2"]
        r05 = x["reference_P_C_arenicola_ranges"]["0.5"]
        r10 = x["reference_P_C_arenicola_ranges"]["1.0"]
        self.assertGreater(r02[0], 0.95)
        self.assertGreater(r05[0], 0.80)
        self.assertLess(r10[1], 0.65)
        self.assertIn("not a guarantee", x["sampling_implication"]["white_tip_gate_interpretation"])
        self.assertIn("hybrid published-node-age sensitivity scaffold", x["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
