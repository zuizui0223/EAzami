import csv
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
    def test_exact_structure_saturation_and_provenance_audit(self):
        observed = mod.run(TARGETS, draws=100000)
        frozen = json.loads(FROZEN.read_text(encoding="utf-8"))

        self.assertEqual(
            observed["contract_version"],
            "pollinator_regime_structure_v1_exact_df_provenance_audit",
        )
        self.assertEqual(observed["raw_distance_ranking"], frozen["raw_distance_ranking"])
        self.assertEqual(observed["nonsaturated_raw_ranking"], frozen["nonsaturated_raw_ranking"])
        self.assertEqual(observed["observation_count"], 4)

        design = observed["source_design"]
        self.assertEqual(design["source_id"], "10.1046/j.1365-2435.2002.00644.x")
        self.assertEqual(design["taxonomic_scope"], "Cirsium_purpuratum")
        self.assertEqual(design["driver"], "flowering_heads")
        self.assertEqual(design["response"], "heads_probed_per_visit")
        self.assertEqual(design["target_kind"], "linear_slope")
        self.assertEqual(design["design"], "2 years x 2 density stands")

        with TARGETS.open(encoding="utf-8", newline="") as handle:
            registry = {row["target_id"]: row for row in csv.DictReader(handle)}
        selected = [registry[target_id] for target_id in mod.TARGET_IDS]
        for field in mod.COMPARABILITY_FIELDS:
            self.assertEqual(len({row[field] for row in selected}), 1, field)
        for row, expected_context in zip(selected, mod.EXPECTED_CONTEXT_LABELS):
            self.assertIn(expected_context, row["claim_boundary"])

        for mode, expected in frozen["results"].items():
            got = observed["results"][mode]
            self.assertAlmostEqual(got["exact_min_distance"], expected["exact_min_distance"], places=12)
            self.assertEqual(got["parameter_count"], expected["parameter_count"])
            self.assertEqual(got["residual_df"], 4 - got["parameter_count"])
            self.assertTrue(got["parameter_bounds_ok"])
            self.assertGreaterEqual(
                got["random_search_best_distance"] + 1e-12,
                got["exact_min_distance"],
            )
            self.assertAlmostEqual(
                got["random_search_best_distance"],
                expected["random_search_best_distance"],
                places=10,
            )

        saturated = observed["results"]["YEAR_MEAN_YEAR_RATIO"]
        self.assertEqual(saturated["residual_df"], 0)
        self.assertAlmostEqual(saturated["exact_min_distance"], 0.0, places=14)
        self.assertEqual(
            saturated["exact_predicted_slopes"],
            list(observed["observed_slopes"].values()),
        )

        shared = observed["results"]["COMMON_MEAN_COMMON_RATIO"]
        year_mean = observed["results"]["YEAR_MEAN_COMMON_RATIO"]
        year_ratio = observed["results"]["COMMON_MEAN_YEAR_RATIO"]
        self.assertEqual(shared["residual_df"], 2)
        self.assertEqual(year_mean["residual_df"], 1)
        self.assertEqual(year_ratio["residual_df"], 1)
        self.assertGreater(year_mean["raw_distance_reduction_vs_shared"], 0.60)
        self.assertGreater(year_ratio["raw_distance_reduction_vs_shared"], 0.35)
        self.assertLess(
            year_mean["exact_min_distance"],
            year_ratio["exact_min_distance"],
        )


if __name__ == "__main__":
    unittest.main()
