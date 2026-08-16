import unittest

import pandas as pd

from analysis.summarize_japan_radiation_pre_tree_trait_disparity import LINEAR_ENDPOINTS, build_summary


class TestPreTreeTraitDisparity(unittest.TestCase):
    def fixture(self):
        taxa = ["Cirsium a", "Cirsium b", "Cirsium c", "Cirsium lineare"]
        rows = []
        for i, taxon in enumerate(taxa):
            row = {"taxon_name": taxon, "n_observations_detector_positive": 12}
            for j, column in enumerate(LINEAR_ENDPOINTS.values()):
                row[column] = float((i + 1) * (j + 1) + (j % 2))
            rows.append(row)
        return pd.DataFrame(rows)

    def test_summary_has_fail_closed_scope(self):
        summary = build_summary(self.fixture(), min_observations=10)
        self.assertEqual(summary["n_eligible_trait_taxa"], 4)
        self.assertEqual(summary["n_dominant_radiation_trait_taxa"], 3)
        self.assertTrue(summary["circular_hue_components_excluded"])
        self.assertIn("does not estimate evolutionary rate", summary["claim_boundary"])

    def test_missing_secondary_fails(self):
        frame = self.fixture().loc[lambda x: ~x["taxon_name"].eq("Cirsium lineare")]
        with self.assertRaises(ValueError):
            build_summary(frame)


if __name__ == "__main__":
    unittest.main()
