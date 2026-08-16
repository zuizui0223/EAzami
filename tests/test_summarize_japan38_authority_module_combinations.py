import unittest

import pandas as pd

from analysis.summarize_japan38_authority_module_combinations import build


class TestAuthorityModuleCombinations(unittest.TestCase):
    def test_state_diversity_is_preserved(self):
        seed = pd.DataFrame([
            {"paper_japan_member_id":"JPN_01","paper_taxon_concept":"A","orientation_state":"upward_or_erect","phyllary_posture":"unknown","stickiness_state":"sticky"},
            {"paper_japan_member_id":"JPN_02","paper_taxon_concept":"B","orientation_state":"downward_or_nodding","phyllary_posture":"appressed","stickiness_state":"nonsticky_or_nearly_nonsticky"},
            {"paper_japan_member_id":"JPN_06","paper_taxon_concept":"Dips","orientation_state":"upward_or_erect","phyllary_posture":"spreading_or_recurved","stickiness_state":"nonsticky_or_nearly_nonsticky"},
            {"paper_japan_member_id":"JPN_15","paper_taxon_concept":"Lin","orientation_state":"upward_or_erect","phyllary_posture":"unknown","stickiness_state":"sticky"},
        ])
        table, summary = build(seed)
        self.assertEqual(summary["n_dominant_seed_concepts"], 2)
        self.assertEqual(summary["n_secondary_seed_concepts"], 2)
        self.assertEqual(summary["n_dominant_orientation_stickiness_combinations"], 2)
        self.assertEqual(summary["n_secondary_orientation_stickiness_combinations"], 2)
        self.assertIn("upward_or_erect", summary["dominant_orientation_counts"])
        self.assertIn("downward_or_nodding", summary["dominant_orientation_counts"])
        self.assertGreater(len(table), 0)
        self.assertIn("does not", summary["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
