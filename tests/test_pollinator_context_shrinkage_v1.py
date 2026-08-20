import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis" / "validate_pollinator_context_shrinkage_v1.py"
TARGETS = ROOT / "data" / "evidence" / "capitulum_pattern_reduction_targets_v2.csv"
FROZEN = ROOT / "data" / "evidence" / "pollinator_context_shrinkage_v1.json"

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

        # Context flexibility should help prediction only modestly, not justify the saturated fit.
        self.assertLess(observed["partial_pooling_loo_log_rmse"], observed["shared_loo_log_rmse"])
        self.assertGreater(observed["predictive_rmse_improvement_fraction"], 0.0)
        self.assertLess(observed["predictive_rmse_improvement_fraction"], 0.05)
        self.assertGreater(observed["partial_pooling_effective_df"], 2.0)
        self.assertLess(observed["partial_pooling_effective_df"], 3.0)
        self.assertEqual(observed["decision"], "do_not_promote_unpooled_temporal_context_parameters")

        # Shrinkage should pull context terms close to zero rather than reproduce the saturated solution.
        beta = observed["full_data_coefficients"]
        self.assertLess(abs(beta["year_1998"]), 0.10)
        self.assertLess(abs(beta["year_1998_x_low_density"]), 0.02)


if __name__ == "__main__":
    unittest.main()
