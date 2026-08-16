import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "japan_radiation_meta",
    ROOT / "analysis" / "summarize_japan_radiation_existing_data_meta.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class TestJapanRadiationExistingDataMeta(unittest.TestCase):
    def test_frozen_metrics(self):
        summary = MODULE.build_summary(ROOT)
        self.assertEqual(summary["radiation_success_asymmetry"]["japanese_taxa_sampled"], 38)
        self.assertEqual(summary["radiation_success_asymmetry"]["dominant_radiation_sampled_taxa"], 36)
        self.assertAlmostEqual(summary["radiation_success_asymmetry"]["dominant_fraction"], 36 / 38)
        self.assertEqual(summary["radiation_success_asymmetry"]["dominant_to_all_exceptions_sampled_richness_ratio"], 18.0)
        self.assertEqual(summary["population_trait_resolution"]["reviewed_polymorphic_systems"], 4)
        self.assertEqual(summary["population_trait_resolution"]["morph_genotype_linked_systems"], 1)
        self.assertEqual(summary["population_trait_resolution"]["transition_rate_testable_systems"], 0)
        self.assertEqual(summary["population_trait_resolution"]["takaoense_minimum_count_ratio"], 2.0)
        self.assertEqual(summary["cytogenetic_scope"]["dominant_radiation_observed_ploidy_levels"], [2, 4, 6])
        self.assertEqual(summary["macro_trait_scope"]["azami_endpoints"], 9)
        self.assertEqual(summary["current_verdict"]["adaptive_radiation"], "unresolved_requires_comparative_plus_replicated_fitness_evidence")

    def test_committed_summary_matches_regeneration(self):
        generated = MODULE.build_summary(ROOT)
        frozen = json.loads(
            (ROOT / "data" / "evidence" / "japan_radiation_existing_data_meta_v1.json").read_text(encoding="utf-8")
        )
        self.assertEqual(generated, frozen)


if __name__ == "__main__":
    unittest.main()
