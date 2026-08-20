import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis" / "sensitivity_capitulum_pattern_reduction_v2_replicates.py"
TARGETS = ROOT / "data" / "evidence" / "capitulum_pattern_reduction_targets_v2.csv"
FROZEN = ROOT / "data" / "evidence" / "capitulum_pattern_reduction_v2_replicate_sensitivity.json"

spec = importlib.util.spec_from_file_location("pattern_reduction_v2_rep", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ReplicateSensitivityTest(unittest.TestCase):
    def test_replicate_averaged_ranking(self):
        observed = mod.run(TARGETS, draws=600)
        frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
        self.assertEqual(observed["full_factorial_ranking"], frozen["full_factorial_ranking"])
        self.assertEqual(observed["overall_ranking"], frozen["overall_ranking"])
        for model, expected in frozen["model_best_mean_distance"].items():
            self.assertAlmostEqual(observed["models"][model]["best_mean_distance"], expected, places=6)
        for model, expected in frozen["model_mean_distance_p01"].items():
            self.assertAlmostEqual(observed["models"][model]["mean_distance_p01"], expected, places=6)
        self.assertEqual(observed["full_factorial_ranking"][0], "FULL_MODULAR_HET")
        self.assertLess(
            observed["models"]["FULL_MODULAR_HET"]["best_mean_distance"],
            observed["models"]["FULL_MODULAR_GLOBAL"]["best_mean_distance"],
        )
        self.assertLess(
            observed["models"]["FULL_MODULAR_GLOBAL"]["best_mean_distance"],
            observed["models"]["FULL_COUPLED_GLOBAL"]["best_mean_distance"],
        )


if __name__ == "__main__":
    unittest.main()
