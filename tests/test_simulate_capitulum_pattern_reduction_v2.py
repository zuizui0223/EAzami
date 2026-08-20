import csv
import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis" / "simulate_capitulum_pattern_reduction_v2.py"
TARGETS = ROOT / "data" / "evidence" / "capitulum_pattern_reduction_targets_v2.csv"
FROZEN = ROOT / "data" / "evidence" / "capitulum_pattern_reduction_simulation_v2_summary.json"

spec = importlib.util.spec_from_file_location("pattern_reduction_v2", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class PatternReductionV2Test(unittest.TestCase):
    def test_registry_layers_and_added_numeric_patterns(self):
        rows = list(csv.DictReader(TARGETS.open(encoding="utf-8", newline="")))
        self.assertEqual(len(rows), 36)
        by = {r["target_id"]: r for r in rows}
        self.assertEqual(sum(r["evidence_layer"] == "azami_global" for r in rows), 8)
        self.assertEqual(sum(r["evidence_layer"].startswith("cirsium_") for r in rows), 17)
        self.assertEqual(sum(r["evidence_layer"] == "asteraceae_primary" for r in rows), 10)
        self.assertAlmostEqual(float(by["CIR_DISPLAY_VISIT_R2_01"]["estimate"]), 0.637)
        self.assertAlmostEqual(float(by["CIR_DISPLAY_PROBE_R2_01"]["estimate"]), 0.533)
        self.assertAlmostEqual(float(by["AST_ALPINE_SIZE_ALLPRED_01"]["estimate"]), 0.676)
        self.assertAlmostEqual(
            float(by["CIR_DISPLAY_PRED_NIKKO"]["estimate"]) /
            float(by["CIR_DISPLAY_PRED_KAWA"]["estimate"]),
            8.4,
        )

    def test_weighted_factorial_ranking_is_deterministic(self):
        observed = mod.run(TARGETS, draws=1500)
        frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
        self.assertEqual(observed["target_registry"]["rows"], frozen["target_registry_rows"])
        self.assertEqual(observed["target_registry"]["layer_counts"], frozen["target_layers"])
        self.assertEqual(observed["overall_ranking_best_distance"], frozen["overall_ranking"])
        self.assertEqual(observed["full_model_factorial_ranking"], frozen["full_factorial_ranking"])
        for model, expected in frozen["model_best_distance"].items():
            self.assertAlmostEqual(observed["models"][model]["best_distance"], expected, places=6)
        for model, expected in frozen["model_distance_p01"].items():
            self.assertAlmostEqual(observed["models"][model]["distance_p01"], expected, places=6)

        models = observed["models"]
        self.assertLess(models["FULL_MODULAR_GLOBAL"]["best_distance"], models["FULL_COUPLED_GLOBAL"]["best_distance"])
        self.assertLess(models["FULL_COUPLED_HET"]["best_distance"], models["FULL_COUPLED_GLOBAL"]["best_distance"])
        self.assertLess(models["FULL_MODULAR_HET"]["best_distance"], models["FULL_MODULAR_GLOBAL"]["best_distance"])
        self.assertLess(models["FULL_MODULAR_HET"]["best_distance"], models["FULL_COUPLED_HET"]["best_distance"])
        best = models["FULL_MODULAR_HET"]
        self.assertEqual(
            max(best["best_distance_components"], key=best["best_distance_components"].get),
            "cirsium_population_pollinator_regime",
        )


if __name__ == "__main__":
    unittest.main()
