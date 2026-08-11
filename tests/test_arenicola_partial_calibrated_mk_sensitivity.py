from __future__ import annotations

import importlib.util
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "analysis"
if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))
MODULE = ANALYSIS / "arenicola_partial_calibrated_mk_sensitivity.py"
SPEC = importlib.util.spec_from_file_location("arenicola_partial_calibrated_mk_sensitivity", MODULE)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


class PartialCalibratedMkTests(unittest.TestCase):
    def setUp(self):
        self.tips = mod.parsimony.load_tip_states(
            ROOT / "data/evidence/arenicola_flower_colour_history_evidence_v1.csv"
        )
        self.ages = mod.load_published_median_ages(
            ROOT / "data/evidence/arenicola_published_node_age_constraints_v1.csv"
        )

    def test_published_median_ages_are_source_locked(self):
        self.assertEqual(
            self.ages,
            {"AREN_NIPP_ROOT": 1.02, "AREN_MRCA": 0.93, "NIPP_MRCA": 0.79},
        )

    def test_transition_matrix_rows_normalize(self):
        matrix = mod.transition_matrix(0.3, 0.7, 0.42)
        self.assertAlmostEqual(sum(matrix[0]), 1.0, places=12)
        self.assertAlmostEqual(sum(matrix[1]), 1.0, places=12)
        self.assertTrue(all(0.0 <= value <= 1.0 for row in matrix for value in row))

    def posterior(self, *, total, ratio, core=0.30, fraction=0.50, variant="published_pengii_basal", prior="flat"):
        branches = mod.branch_table(
            variant,
            self.ages,
            core_age=core,
            crown_fraction=fraction,
        )
        q_cw, q_wc = mod.rates_from_total_ratio(total, ratio)
        return mod.exact_internal_posterior(
            branches,
            self.tips,
            q_cw=q_cw,
            q_wc=q_wc,
            root_prior_mode=prior,
        )

    def test_low_symmetric_rate_recovers_parsimony_direction(self):
        result = self.posterior(total=0.01, ratio=1.0)
        self.assertGreater(result["p_C"], 0.99)
        self.assertAlmostEqual(result["p_C"] + result["p_W"], 1.0, places=12)

    def test_fast_symmetric_rate_erases_direction(self):
        result = self.posterior(total=10.0, ratio=1.0)
        self.assertGreater(result["p_C"], 0.49)
        self.assertLess(result["p_C"], 0.51)

    def test_asymmetric_rate_and_root_prior_can_reverse_direction(self):
        result = self.posterior(
            total=3.0,
            ratio=4.0,
            core=0.15,
            fraction=0.25,
            variant="alternative_kawakamii_basal",
            prior="equilibrium",
        )
        self.assertLess(result["p_C"], 0.30)
        self.assertGreater(result["p_W"], 0.70)

    def test_default_grid_has_expected_symmetric_ranges_and_reversal(self):
        rows = mod.scenario_rows(
            self.tips,
            self.ages,
            core_ages=mod.DEFAULT_CORE_AGES,
            crown_fractions=mod.DEFAULT_CROWN_FRACTIONS,
            total_rates=mod.DEFAULT_TOTAL_RATES,
            loss_regain_ratios=mod.DEFAULT_LOSS_REGAIN_RATIOS,
            root_priors=mod.DEFAULT_ROOT_PRIORS,
        )
        self.assertEqual(len(rows), 1440)
        summary = mod.summarize(rows, self.ages)
        expected = {
            "0.1": (0.9558, 0.9828),
            "0.3": (0.8767, 0.9418),
            "1": (0.6852, 0.7733),
            "3": (0.5215, 0.5355),
        }
        for rate, (lo, hi) in expected.items():
            item = summary["symmetric_rate_summary"][rate]
            self.assertTrue(item["all_prefer_C"])
            self.assertGreaterEqual(item["min_p_arenicola_C"], lo)
            self.assertLessEqual(item["max_p_arenicola_C"], hi)
        self.assertTrue(summary["all_grid_summary"]["direction_reversal_exists"])
        self.assertLess(summary["all_grid_summary"]["min_p_arenicola_C"], 0.30)
        self.assertGreater(summary["all_grid_summary"]["max_p_arenicola_C"], 0.99)

    def test_invalid_time_order_is_rejected(self):
        with self.assertRaises(ValueError):
            mod.branch_table(
                "published_pengii_basal",
                self.ages,
                core_age=0.80,
                crown_fraction=0.5,
            )


if __name__ == "__main__":
    unittest.main()
