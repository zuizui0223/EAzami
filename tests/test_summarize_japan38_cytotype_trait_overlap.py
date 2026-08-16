import unittest

import pandas as pd

from analysis.summarize_japan38_cytotype_trait_overlap import build


class TestJapan38CytotypeTraitOverlap(unittest.TestCase):
    def test_detects_non_deterministic_mapping(self):
        cytotypes = pd.DataFrame([
            {"paper_japan_member_id":"J1","taxon":"A","japan_origin_role":"dominant_main_japanese_radiation","chromosome_2n":"34","ploidy_x":"2"},
            {"paper_japan_member_id":"J2","taxon":"B","japan_origin_role":"dominant_main_japanese_radiation","chromosome_2n":"68","ploidy_x":"4"},
            {"paper_japan_member_id":"J3","taxon":"C","japan_origin_role":"dominant_main_japanese_radiation","chromosome_2n":"34","ploidy_x":"2"},
            {"paper_japan_member_id":"J4","taxon":"D","japan_origin_role":"secondary_japanese_arrival_candidate","chromosome_2n":"34","ploidy_x":"2"},
        ])
        traits = pd.DataFrame([
            {"paper_japan_member_id":"J1","orientation_state":"upward_or_erect","phyllary_posture":"unknown","stickiness_state":"unknown"},
            {"paper_japan_member_id":"J2","orientation_state":"upward_or_erect","phyllary_posture":"unknown","stickiness_state":"unknown"},
            {"paper_japan_member_id":"J3","orientation_state":"downward_or_nodding","phyllary_posture":"unknown","stickiness_state":"unknown"},
            {"paper_japan_member_id":"J4","orientation_state":"upward_or_erect","phyllary_posture":"unknown","stickiness_state":"unknown"},
        ])
        table, summary = build(cytotypes, traits)
        self.assertEqual(summary["dominant_radiation_ploidy_levels"], [2,4])
        self.assertEqual(set(summary["diploid_observed_orientation_states"]), {"upward_or_erect","downward_or_nodding"})
        self.assertEqual(set(summary["upward_or_ascending_observed_ploidy_levels"]), {2,4})
        self.assertGreater(len(table), 0)
        self.assertIn("does not estimate", summary["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
