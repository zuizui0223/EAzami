import csv
import importlib.util
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "analysis"
sys.path.insert(0, str(ANALYSIS))
import simulate_macro_interaction_pattern_reduction_v2 as v2


class PatternReductionV2Test(unittest.TestCase):
    def test_target_registry_has_observation_and_interaction_layers(self):
        path = ROOT / "data/evidence/macro_interaction_pattern_targets_v2.csv"
        rows = list(csv.DictReader(path.open(encoding="utf-8", newline="")))
        self.assertGreaterEqual(len(rows), 30)
        roles = {r["simulation_role"] for r in rows}
        self.assertTrue({"fit_target", "heldout_numeric", "heldout_sign", "context_target", "structural_gap"} <= roles)
        ids = {r["target_id"] for r in rows}
        for key in [
            "AZ_VAR_RANGE", "INT_HERB_RR", "INT_PURP_VISIT_R2", "INT_PITCHERI_WEEVIL_RR",
            "INT_CREM_NODDING_ACHENE_RR", "INT_SCENT_DUAL_GUILDS", "INT_STICKINESS_NULL",
        ]:
            self.assertIn(key, ids)

    def test_small_run_is_deterministic_and_has_all_families(self):
        path = ROOT / "data/evidence/macro_interaction_pattern_targets_v2.csv"
        a = v2.run(path, draws_per_seed=4, seeds=[101, 202], accept_fraction=0.25)
        b = v2.run(path, draws_per_seed=4, seeds=[101, 202], accept_fraction=0.25)
        self.assertEqual(a, b)
        self.assertEqual(len(a["families"]), 5)
        self.assertEqual(set(a["ranking"]), set(v2.v1.FAMILIES))
        self.assertEqual(a["heldout_checks_represented"], 5)
        self.assertIn("orientation_time_window", a["structural_gaps"])


if __name__ == "__main__":
    unittest.main()
