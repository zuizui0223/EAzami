import json
import math
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "data/evidence/chang2026_rnaseq_comp1061_empirical_pilot_v1.json"


class Chang2026RNASeqComp1061PilotTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.x = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    def test_provenance_is_frozen(self):
        self.assertEqual(self.x["contract_version"], "chang2026_rnaseq_comp1061_empirical_pilot_v1")
        self.assertEqual(self.x["source_pr"], 49)
        self.assertEqual(self.x["workflow_run_id"], 32449218055)
        self.assertEqual(self.x["artifact"]["id"], 9436346282)
        self.assertEqual(
            self.x["artifact"]["digest"],
            "sha256:ec4436e47131de26f0f15526b5f1539a2fe6584d240c481db9711107d1dfdc7b",
        )

    def test_selected_sample_is_exact(self):
        s = self.x["sample"]
        self.assertEqual(s["tip_id"], "Cirsium_japonicum_var_albescens")
        self.assertEqual(s["run"], "SRR35152728")
        self.assertEqual(s["source_study"], "Chang2026")
        self.assertEqual(s["source_bioproject"], "PRJNA1311153")
        self.assertEqual(s["data_type"], "leaf_rnaseq")
        self.assertEqual(s["binary_colour_code"], "W")
        self.assertEqual(s["spots"], 21983186)

    def test_empirical_gate_passed(self):
        r = self.x["observed_result"]
        self.assertEqual(r["all_retrieved_loci"], 993)
        self.assertEqual(r["frozen_241_retrieved_loci"], 238)
        self.assertTrue(r["engineering_pass_ge_100_loci"])
        self.assertGreaterEqual(r["frozen_241_retrieved_loci"], 100)
        self.assertTrue(math.isclose(r["frozen_241_recovery_fraction"], 238 / 241, rel_tol=0, abs_tol=1e-15))

    def test_scientific_stop_rules_remain_explicit(self):
        boundary = self.x["claim_boundary"]
        self.assertIn("does not establish 20-tip", boundary)
        self.assertIn("paralog", boundary)
        self.assertIn("branch lengths", boundary)
        self.assertIn("transition-rate readiness", boundary)


if __name__ == "__main__":
    unittest.main()
