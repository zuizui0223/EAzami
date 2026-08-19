import unittest

import pandas as pd

from analysis.build_japan38_nmns_capitulum_trait_bridge import (
    build_bridge,
    classify_orientation,
    classify_phyllary,
    classify_stickiness,
    normalize_taxon,
)


class TestJapan38NMNSBridge(unittest.TestCase):
    def test_state_parsers(self):
        phrase = "頭花を下向きに咲かせ，総苞片が開出し，総苞が良く粘る"
        self.assertIn("downward_or_nodding", classify_orientation(phrase))
        self.assertIn("spreading", classify_phyllary(phrase))
        self.assertEqual(classify_stickiness(phrase), "sticky")

    def test_infraspecific_match_is_fail_closed(self):
        membership = pd.DataFrame([
            {"paper_japan_member_id": "J1", "paper_taxon_concept": "Cirsium alpha var. one"},
            {"paper_japan_member_id": "J2", "paper_taxon_concept": "Cirsium beta"},
        ])
        nmns = pd.DataFrame([
            {"種名": "Cirsium alpha", "変種名": "", "キャッチフレーズ": "頭花を上向きに咲かせる"},
            {"種名": "Cirsium beta", "変種名": "", "キャッチフレーズ": "頭花を下向きに咲かせる"},
        ])
        bridge, summary = build_bridge(membership, nmns)
        alpha = bridge.loc[bridge["paper_japan_member_id"].eq("J1")].iloc[0]
        beta = bridge.loc[bridge["paper_japan_member_id"].eq("J2")].iloc[0]
        self.assertEqual(alpha["nmns_taxon_concept"], "")
        self.assertIn("review_required", alpha["authority_match_status"])
        self.assertEqual(beta["authority_match_status"], "exact_authority_concept_match")
        self.assertIn("downward_or_nodding", beta["orientation_state_from_index"])
        self.assertEqual(summary["n_authority_matched_concepts"], 1)

    def test_normalization(self):
        self.assertEqual(normalize_taxon("C. alpha var. one Author"), "Cirsium alpha var. one")


if __name__ == "__main__":
    unittest.main()
