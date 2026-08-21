import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis" / "build_doctoral_sampling_information_gate_v1.py"
ASR = ROOT / "analysis" / "arenicola_colour_history_sensitivity_v1.json"
NICHE = ROOT / "data" / "evidence" / "focal_occurrence_niche_sampling_decision_v1.csv"
MANIFEST = ROOT / "sampling" / "doctoral_field_tranche1_population_manifest_v1.csv"
FROZEN = ROOT / "data" / "evidence" / "doctoral_sampling_information_gate_v1.json"

spec = importlib.util.spec_from_file_location("sampling_gate", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class DoctoralSamplingInformationGateTest(unittest.TestCase):
    def test_gate_is_reproducible_and_does_not_expand_core_early(self):
        observed = mod.run(ASR, NICHE, MANIFEST)
        frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
        self.assertEqual(observed, frozen)
        self.assertEqual(observed["current_core_individuals"], 190)
        self.assertEqual(observed["immediate_new_population_additions"], [])
        self.assertEqual(observed["immediate_decision"], "keep_core190_no_new_population_count")

        slots = {x["population_id"]: x for x in observed["existing_slot_repositioning"]}
        self.assertIn("Yoron_or_Okinoerabu", slots["P003"]["required_region"])
        self.assertIn("Tokunoshima", slots["P004"]["required_region"])

        self.assertEqual(
            observed["asr_gate"]["sampling_implication"],
            "do_not_add_focal_population_count_to_solve_deep_ASR_polarity",
        )
        self.assertEqual(len(observed["conditional_additions"]), 1)
        conditional = observed["conditional_additions"][0]
        self.assertEqual(conditional["taxon"], "Cirsium sieboldii")
        self.assertEqual(conditional["additional_populations_if_triggered"], 2)
        self.assertEqual(conditional["additional_individuals_if_triggered"], 30)
        self.assertEqual(conditional["status"], "conditional_not_added_now")


if __name__ == "__main__":
    unittest.main()
