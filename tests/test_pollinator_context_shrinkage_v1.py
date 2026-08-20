import csv
import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis" / "validate_pollinator_context_shrinkage_v1.py"
TARGETS = ROOT / "data" / "evidence" / "capitulum_pattern_reduction_targets_v2.csv"
FROZEN = ROOT / "data" / "evidence" / "pollinator_context_shrinkage_v1.json"
BOUT = ROOT / "sampling" / "aim2_capitulum_observation_bout_ledger_v1.csv"
PROTOCOL = ROOT / "docs" / "AIM2_TRANCHE1_JOINT_OBSERVATION_PROTOCOL_2026-08-20.md"

spec = importlib.util.spec_from_file_location("pollinator_context_shrinkage", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class PollinatorContextShrinkageTest(unittest.TestCase):
    def test_frozen_result_and_predictive_guardrail(self):
        observed = mod.run(TARGETS)
        frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
        for key in [
            "source_id",
            "observed_slopes",
            "selected_lambda",
            "shared_loo_log_rmse",
            "partial_pooling_loo_log_rmse",
            "predictive_rmse_improvement_fraction",
            "partial_pooling_effective_df",
            "full_data_coefficients",
            "full_data_fitted_slopes",
            "loo_predicted_slopes",
            "decision",
        ]:
            self.assertEqual(observed[key], frozen[key], key)

        self.assertLess(observed["partial_pooling_loo_log_rmse"], observed["shared_loo_log_rmse"])
        self.assertGreater(observed["predictive_rmse_improvement_fraction"], 0.0)
        self.assertLess(observed["predictive_rmse_improvement_fraction"], 0.05)
        self.assertGreater(observed["partial_pooling_effective_df"], 2.0)
        self.assertLess(observed["partial_pooling_effective_df"], 3.0)
        self.assertEqual(observed["decision"], "do_not_promote_unpooled_temporal_context_parameters")

        beta = observed["full_data_coefficients"]
        self.assertLess(abs(beta["year_1998"]), 0.10)
        self.assertLess(abs(beta["year_1998_x_low_density"]), 0.02)

    def test_field_schema_can_measure_the_missing_context(self):
        with BOUT.open(encoding="utf-8", newline="") as handle:
            fields = next(csv.reader(handle))
        required = {
            "phenology_census_id",
            "focal_open_capitula_current",
            "density_context_id",
            "density_measurement_area_m2",
            "local_conspecific_flowering_plants",
            "local_conspecific_open_capitula",
            "pollinator_visit_count",
            "heads_probed_total",
            "effective_contact_count",
            "time_window_class",
        }
        self.assertTrue(required <= set(fields), required - set(fields))
        self.assertEqual(len(fields), len(set(fields)))

        protocol = PROTOCOL.read_text(encoding="utf-8")
        for phrase in [
            "heads probed per visit = heads_probed_total / pollinator_visit_count",
            "do not fit one unconstrained pollinator-response parameter per year or site",
            "no subjective density class when quantitative counts/area are feasible",
        ]:
            self.assertIn(phrase, protocol)


if __name__ == "__main__":
    unittest.main()
