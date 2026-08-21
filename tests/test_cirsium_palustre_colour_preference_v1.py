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
MACRO_REGISTRY = ROOT / "data" / "evidence" / "macro_interaction_pattern_targets_v2.csv"
HEAD_LEDGER = ROOT / "sampling" / "aim2_capitulum_field_ledger_v1.csv"
BOUT_LEDGER = ROOT / "sampling" / "aim2_capitulum_observation_bout_ledger_v1.csv"
PROTOCOL = ROOT / "docs" / "AIM2_TRANCHE1_JOINT_OBSERVATION_PROTOCOL_2026-08-20.md"

spec = importlib.util.spec_from_file_location("colour_pref", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def header(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return next(csv.reader(handle))


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

        macro = list(csv.DictReader(MACRO_REGISTRY.open(encoding="utf-8", newline="")))
        macro_row = {r["target_id"]: r for r in macro}["INT_PALUSTRE_WHITE_PREF"]
        self.assertEqual(macro_row["target_kind"], "numeric_ratio_range")
        self.assertAlmostEqual(float(macro_row["target_value"]), observed["geometric_mean_selection_ratio"], places=6)
        self.assertAlmostEqual(float(macro_row["lower_bound"]), observed["minimum_selection_ratio"], places=6)
        self.assertAlmostEqual(float(macro_row["upper_bound"]), observed["maximum_selection_ratio"], places=6)
        self.assertEqual(macro_row["simulation_role"], "heldout_sign")
        self.assertIn("significance-conditioned", macro_row["notes"])

    def test_field_discriminator_contract(self):
        self.assertIn("colour_class", header(HEAD_LEDGER))
        bout = set(header(BOUT_LEDGER))
        required = {
            "colour_choice_context_id",
            "local_open_capitula_same_colour_class",
            "local_open_capitula_alternative_colour_class",
            "pollinator_visit_count",
            "effective_contact_count",
            "time_window_class",
            "density_context_id",
        }
        self.assertLessEqual(required, bout)
        protocol = PROTOCOL.read_text(encoding="utf-8")
        for phrase in [
            "Colour-choice update",
            "white selection ratio",
            "significance-conditioned calibration",
            "no `white always preferred` parameter",
            "no colour-preference claim without local morph availability",
        ]:
            self.assertIn(phrase, protocol)


if __name__ == "__main__":
    unittest.main()
