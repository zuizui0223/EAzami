import csv
import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis" / "simulate_capitulum_pattern_reduction_v1.py"
TARGETS = ROOT / "data" / "evidence" / "capitulum_pattern_reduction_targets_v1.csv"
FROZEN = ROOT / "data" / "evidence" / "capitulum_pattern_reduction_simulation_v1.json"

spec = importlib.util.spec_from_file_location("pattern_reduction", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class PatternReductionTest(unittest.TestCase):
    def test_target_registry_layers_and_critical_values(self):
        rows = list(csv.DictReader(TARGETS.open(encoding="utf-8", newline="")))
        self.assertEqual(len(rows), 26)
        by_id = {r["target_id"]: r for r in rows}
        self.assertEqual(sum(r["evidence_layer"] == "azami_global" for r in rows), 8)
        self.assertEqual(sum(r["evidence_layer"].startswith("cirsium_") for r in rows), 14)
        self.assertEqual(sum(r["evidence_layer"] == "asteraceae_primary" for r in rows), 4)
        self.assertAlmostEqual(float(by_id["CIR_HERB_RR_01"]["estimate"]), 2.67364, places=5)
        self.assertAlmostEqual(float(by_id["CIR_HERB_RR_01"]["lower"]), 2.38833, places=5)
        self.assertAlmostEqual(float(by_id["CIR_DISPLAY_PRED_NIKKO"]["estimate"]), 0.000063, places=8)
        self.assertAlmostEqual(float(by_id["CIR_DISPLAY_PRED_KAWA"]["estimate"]), 0.0000075, places=9)
        self.assertAlmostEqual(float(by_id["AST_NOD_ACHENE_01"]["estimate"]), 56.3 / 15.7, places=5)
        self.assertEqual(by_id["AST_NOD_ACHENE_01"]["use_in_simulation"], "hard")
        self.assertIn("External Asteraceae calibration", by_id["AST_NOD_ACHENE_01"]["claim_boundary"])

    def test_rebuild_matches_frozen_and_failure_sequence(self):
        observed = mod.run(TARGETS, draws=500)
        frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
        self.assertEqual(observed, frozen)
        models = observed["models"]
        self.assertEqual([models[x]["accepted"] for x in [
            "ENV_ONLY", "ENV_POLL", "ENV_ANT", "FULL_COUPLED", "FULL_MODULAR"
        ]], [0, 0, 0, 0, 2])
        self.assertEqual(models["FULL_COUPLED"]["best"]["violations"], ["AZ_LAB_01"])
        self.assertEqual(models["FULL_MODULAR"]["best"]["violations"], [])
        self.assertLess(abs(models["FULL_MODULAR"]["best"]["summary"]["lability"]), 0.15)


if __name__ == "__main__":
    unittest.main()
