import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis" / "diagnose_pollinator_regime_structure_v1.py"
TARGETS = ROOT / "data" / "evidence" / "capitulum_pattern_reduction_targets_v2.csv"
FROZEN = ROOT / "data" / "evidence" / "pollinator_regime_structure_v1.json"

spec = importlib.util.spec_from_file_location("poll_regime", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class PollinatorRegimeStructureTest(unittest.TestCase):
    def test_exact_structure_ranking_and_random_convergence(self):
        observed = mod.run(TARGETS, draws=100000)
        frozen = json.loads(FROZEN.read_text(encoding="utf-8"))

        self.assertEqual(observed["contract_version"], "pollinator_regime_structure_v1_exact")
        self.assertEqual(observed["ranking"], frozen["ranking"])

        for mode, expected in frozen["results"].items():
            got = observed["results"][mode]
            self.assertAlmostEqual(got["exact_min_distance"], expected["exact_min_distance"], places=12)
            self.assertEqual(got["parameter_bounds_ok"], True)
            self.assertGreaterEqual(got["random_search_best_distance"] + 1e-12, got["exact_min_distance"])
            self.assertAlmostEqual(got["random_search_best_distance"], expected["random_search_best_distance"], places=10)

        full = observed["results"]["YEAR_MEAN_YEAR_RATIO"]
        self.assertAlmostEqual(full["exact_min_distance"], 0.0, places=14)
        self.assertEqual(full["exact_predicted_slopes"], list(observed["observed_slopes"].values()))

        shared = observed["results"]["COMMON_MEAN_COMMON_RATIO"]
        self.assertGreater(shared["exact_min_distance"], 0.48)
        self.assertLess(observed["results"]["YEAR_MEAN_COMMON_RATIO"]["exact_min_distance"], shared["exact_min_distance"])
        self.assertLess(observed["results"]["COMMON_MEAN_YEAR_RATIO"]["exact_min_distance"], shared["exact_min_distance"])


if __name__ == "__main__":
    unittest.main()
