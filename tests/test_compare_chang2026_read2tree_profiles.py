import csv
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "analysis" / "compare_chang2026_read2tree_profiles.py"
SPEC = importlib.util.spec_from_file_location("profile_compare", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
sys.modules["profile_compare"] = mod
SPEC.loader.exec_module(mod)


def detail_rows(classifications, statuses=None):
    thresholds = ("0", "50", "70", "90")
    statuses = statuses or ["scored_focal_monophyletic"] * 4
    return {
        threshold: {
            "support_threshold": threshold,
            "analysis_status": status,
            "classification": classification,
        }
        for threshold, status, classification in zip(
            thresholds, statuses, classifications
        )
    }


class ProfileComparisonTests(unittest.TestCase):
    def test_all_threshold_candidate_concordance(self):
        a = detail_rows(["published_best"] * 4)
        b = detail_rows(["published_best"] * 4)
        rows = mod.comparison_rows(a, b)
        summary = mod.overall_summary(rows, profile_a="static", profile_b="browser")
        self.assertEqual(
            summary["overall_classification"],
            "concordant_candidate_regain_across_thresholds",
        )
        self.assertEqual(summary["concordant_candidate_regain_threshold_count"], 4)

    def test_direct_candidate_loss_conflict_dominates(self):
        a = detail_rows(["published_best"] * 4)
        b = detail_rows(
            ["published_best", "loss_only_best", "published_best", "published_best"]
        )
        rows = mod.comparison_rows(a, b)
        summary = mod.overall_summary(rows, profile_a="static", profile_b="browser")
        self.assertEqual(summary["overall_classification"], "marker_profile_conflict")
        self.assertEqual(summary["direct_conflict_threshold_count"], 1)

    def test_support_sensitive_candidate_concordance(self):
        a = detail_rows(
            [
                "published_best",
                "published_best",
                "tie_published_loss_only",
                "tie_published_loss_only",
            ]
        )
        b = detail_rows(
            [
                "published_best",
                "published_best",
                "tie_published_loss_only",
                "tie_published_loss_only",
            ]
        )
        summary = mod.overall_summary(
            mod.comparison_rows(a, b), profile_a="static", profile_b="browser"
        )
        self.assertEqual(
            summary["overall_classification"],
            "support_sensitive_concordant_candidate_regain",
        )

    def test_one_decisive_profile_is_not_concordance(self):
        a = detail_rows(["published_best"] * 4)
        b = detail_rows(
            ["not_scored"] * 4,
            statuses=["focal_not_monophyletic_raw_tree"] * 4,
        )
        summary = mod.overall_summary(
            mod.comparison_rows(a, b), profile_a="static", profile_b="browser"
        )
        self.assertEqual(
            summary["overall_classification"], "marker_profile_partial_disagreement"
        )
        self.assertEqual(summary["partial_disagreement_threshold_count"], 4)

    def test_threshold_direction_change_is_flagged(self):
        a = detail_rows(
            ["published_best", "published_best", "loss_only_best", "loss_only_best"]
        )
        b = detail_rows(
            ["published_best", "published_best", "loss_only_best", "loss_only_best"]
        )
        summary = mod.overall_summary(
            mod.comparison_rows(a, b), profile_a="static", profile_b="browser"
        )
        self.assertEqual(
            summary["overall_classification"], "support_threshold_direction_change"
        )

    def test_details_reader_rejects_missing_threshold(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "details.csv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=["support_threshold", "analysis_status", "classification"],
                )
                writer.writeheader()
                writer.writerows(
                    [
                        {
                            "support_threshold": value,
                            "analysis_status": "scored_focal_monophyletic",
                            "classification": "published_best",
                        }
                        for value in ("0", "50", "70")
                    ]
                )
            with self.assertRaisesRegex(ValueError, "expected thresholds"):
                mod.validate_details(path)


if __name__ == "__main__":
    unittest.main()
