import json
import math
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "data/evidence/chang_rnaseq_comp1061_crossstudy_overlap_v1.json"


class ChangRNASeqComp1061CrossStudyOverlapTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.x = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    def test_sources_are_independent_study_pilots(self):
        p = self.x["source_pilots"]
        self.assertEqual(len(p), 2)
        self.assertEqual({x["study"] for x in p}, {"Chang2025", "Chang2026"})
        self.assertEqual([x["recovered_frozen241_loci"] for x in p], [237, 238])

    def test_overlap_arithmetic_is_consistent(self):
        o = self.x["crossstudy_overlap"]
        self.assertEqual(o["intersection_loci"], 236)
        self.assertEqual(o["union_loci"], 239)
        self.assertEqual(237 + 238 - 236, 239)
        self.assertEqual(len(o["chang2025_only_loci"]), 1)
        self.assertEqual(len(o["chang2026_only_loci"]), 2)
        self.assertEqual(o["missing_from_both_count"], 2)
        self.assertTrue(math.isclose(o["intersection_fraction_of_frozen_241"], 236 / 241, rel_tol=0, abs_tol=1e-15))
        self.assertTrue(math.isclose(o["jaccard"], 236 / 239, rel_tol=0, abs_tol=1e-15))

    def test_decision_stops_more_single_sample_pilots(self):
        d = self.x["decision"]
        self.assertFalse(d["additional_single_sample_compatibility_pilots_needed"])
        self.assertTrue(d["full_20_tip_recovery_qc_is_next"])

    def test_claim_boundary_stays_pre_tree(self):
        b = self.x["claim_boundary"]
        self.assertIn("does not establish >=16/20 occupancy", b)
        self.assertIn("paralog", b)
        self.assertIn("branch-length topology", b)
        self.assertIn("transition rates", b)
        self.assertIn("ancestral-state direction", b)


if __name__ == "__main__":
    unittest.main()
