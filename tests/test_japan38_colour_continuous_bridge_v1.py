import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "colour_bridge", ROOT / "analysis/build_japan38_colour_continuous_bridge_v1.py"
)
assert SPEC and SPEC.loader
cb = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cb)


class TestJapan38ColourContinuousBridge(unittest.TestCase):
    def test_concept_key_preserves_variety(self):
        self.assertEqual(
            cb.concept_key("Cirsium japonicum Fisch. ex DC. var. horridum Nakai"),
            "Cirsium japonicum var. horridum",
        )
        self.assertNotEqual(
            cb.concept_key("Cirsium japonicum var. horridum"),
            cb.species_key("Cirsium japonicum"),
        )

    def test_broad_species_is_sensitivity_not_variety_assignment(self):
        members = [
            {
                "paper_japan_member_id": "JPN_12",
                "paper_taxon_concept": "Cirsium japonicum var. horridum",
            },
            {
                "paper_japan_member_id": "JPN_35",
                "paper_taxon_concept": "Cirsium nipponicum",
            },
            {
                "paper_japan_member_id": "JPN_20",
                "paper_taxon_concept": "Cirsium nipponicum var. incomptum",
            },
        ]
        obs = [
            {
                "taxon_name": "Cirsium japonicum",
                "corolla_lab_chroma_n_usable_heads": "1",
                "corolla_lab_lightness_median": "60",
                "corolla_lab_chroma_median": "20",
                "corolla_hue_sin_median": "0",
                "corolla_hue_cos_median": "1",
            },
            {
                "taxon_name": "Cirsium nipponicum",
                "corolla_lab_chroma_n_usable_heads": "1",
                "corolla_lab_lightness_median": "62",
                "corolla_lab_chroma_median": "28",
                "corolla_hue_sin_median": "-0.8",
                "corolla_hue_cos_median": "0.4",
            },
        ]
        rows, sensitivity = cb.build(members, obs)
        self.assertEqual([r["paper_japan_member_id"] for r in rows], ["JPN_35"])
        self.assertEqual(sensitivity, ["JPN_12", "JPN_20"])

    def test_median_and_mad_are_retained(self):
        members = [
            {
                "paper_japan_member_id": "JPN_36",
                "paper_taxon_concept": "Cirsium sieboldii Miq.",
            }
        ]
        obs = [
            {
                "taxon_name": "Cirsium sieboldii",
                "corolla_lab_chroma_n_usable_heads": "1",
                "corolla_lab_lightness_median": "50",
                "corolla_lab_chroma_median": "20",
                "corolla_hue_sin_median": "0",
                "corolla_hue_cos_median": "1",
            },
            {
                "taxon_name": "Cirsium sieboldii",
                "corolla_lab_chroma_n_usable_heads": "1",
                "corolla_lab_lightness_median": "70",
                "corolla_lab_chroma_median": "40",
                "corolla_hue_sin_median": "0",
                "corolla_hue_cos_median": "1",
            },
        ]
        rows, _ = cb.build(members, obs)
        row = rows[0]
        self.assertEqual(row["n_colour_usable_observations"], 2)
        self.assertEqual(row["corolla_lab_lightness_species_median"], 60)
        self.assertEqual(row["corolla_lab_lightness_species_mad"], 10)
        self.assertAlmostEqual(row["corolla_hue_degrees_species_circular"], 0.0)


if __name__ == "__main__":
    unittest.main()
