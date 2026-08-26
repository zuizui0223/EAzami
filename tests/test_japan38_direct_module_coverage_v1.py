import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "cov", ROOT / "analysis/audit_japan38_direct_module_coverage_v1.py"
)
assert SPEC and SPEC.loader
cov = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cov)


class TestJapan38DirectModuleCoverage(unittest.TestCase):
    def test_concept_key_preserves_infraspecific_rank(self):
        self.assertEqual(
            cov.concept_key("Cirsium japonicum Fisch. ex DC. var. horridum Nakai"),
            "Cirsium japonicum var. horridum",
        )
        self.assertEqual(
            cov.concept_key("Cirsium matsumurae Nakai var. dubium Kitam."),
            "Cirsium matsumurae var. dubium",
        )
        self.assertNotEqual(
            cov.concept_key("Cirsium japonicum var. albescens"),
            cov.concept_key("Cirsium japonicum var. horridum"),
        )

    def test_near_name_species_is_not_joined(self):
        audit = [
            {
                "paper_japan_member_id": "JPN_24",
                "paper_taxon_concept": "Cirsium pseudosuffultum Kadota",
            }
        ]
        display = [
            {
                "taxon": "Cirsium suffultum",
                "region": "Japan",
                "size_metric": "involucre_live_diameter",
            }
        ]
        out = cov.display_audit(audit, display)
        self.assertEqual(out["exact_japan38_concepts"], 0)
        self.assertEqual(len(out["unmatched_source_rows"]), 1)

    def test_exact_species_match_retains_metric_class(self):
        audit = [
            {
                "paper_japan_member_id": "JPN_03",
                "paper_taxon_concept": "Cirsium alpicola Nakai",
            },
            {
                "paper_japan_member_id": "JPN_09",
                "paper_taxon_concept": "Cirsium gyojanum Kitam.",
            },
        ]
        display = [
            {
                "taxon": "Cirsium alpicola",
                "region": "Japan",
                "size_metric": "involucre_live_diameter",
                "diameter_cm": "1.8-2.0",
                "source": "source A",
            },
            {
                "taxon": "Cirsium gyojanum",
                "region": "Japan",
                "size_metric": "involucre_live_diameter",
                "diameter_cm": "0.6-0.8",
                "source": "source B",
            },
        ]
        out = cov.display_audit(audit, display)
        self.assertEqual(out["exact_japan38_concepts"], 2)
        self.assertEqual(out["largest_comparable_metric_group"], "involucre_live_diameter")
        self.assertEqual(out["largest_comparable_metric_group_n"], 2)
        self.assertEqual(
            out["metric_groups"]["involucre_live_diameter"]["paper_japan_member_ids"],
            ["JPN_03", "JPN_09"],
        )

    def test_high_leverage_targets_are_checked_without_imputation(self):
        readiness = {
            "trait_completion_design": {
                "observed_state_validation": {
                    "cross_module_first": "JPN_36",
                    "stickiness_second": "JPN_06",
                },
                "orientation": {"primary": "JPN_34"},
                "phyllary": {"primary": "JPN_15"},
                "stickiness": {"primary": "JPN_24"},
            }
        }
        rows = cov.high_leverage_targets(readiness, {"JPN_06"})
        by = {r["paper_japan_member_id"]: r for r in rows}
        self.assertTrue(by["JPN_06"]["existing_direct_display_size"])
        self.assertFalse(by["JPN_36"]["existing_direct_display_size"])
        self.assertFalse(by["JPN_34"]["existing_direct_display_size"])


if __name__ == "__main__":
    unittest.main()
