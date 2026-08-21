import json
import math
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "data/evidence/chang2025_rnaseq_comp1061_empirical_pilot_v1.json"


class Chang2025RNASeqComp1061PilotTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.x = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    def test_provenance_is_frozen(self):
        self.assertEqual(self.x["contract_version"], "chang2025_rnaseq_comp1061_empirical_pilot_v1")
        self.assertEqual(self.x["source_pr"], 48)
        self.assertEqual(self.x["workflow_run_id"], 32447450428)
        self.assertEqual(self.x["artifact"]["id"], 9435557235)
        self.assertEqual(
            self.x["artifact"]["digest"],
            "sha256:f60afe73d3d2a18f4b7ce52d0a851637d4234424a5cb0ba6f6fd67c4c57eb992",
        )

    def test_selected_sample_is_exact(self):
        s = self.x["sample"]
        self.assertEqual(s["tip_id"], "Cirsium_suffultum")
        self.assertEqual(s["run"], "SRR30617344")
        self.assertEqual(s["source_study"], "Chang2025")
        self.assertEqual(s["source_bioproject"], "PRJNA1158676")
        self.assertEqual(s["data_type"], "leaf_rnaseq")
        self.assertEqual(s["spots"], 19710680)

    def test_empirical_gate_passed(self):
        r = self.x["observed_result"]
        self.assertEqual(r["all_retrieved_loci"], 978)
        self.assertEqual(r["frozen_241_retrieved_loci"], 237)
        self.assertTrue(r["engineering_pass_ge_100_loci"])
        self.assertGreaterEqual(r["frozen_241_retrieved_loci"], 100)
        self.assertTrue(math.isclose(r["frozen_241_recovery_fraction"], 237 / 241, rel_tol=0, abs_tol=1e-15))

    def test_scientific_stop_rules_remain_explicit(self):
        boundary = self.x["claim_boundary"]
        self.assertIn("does not establish 20-tip", boundary)
        self.assertIn("paralog", boundary)
        self.assertIn("branch lengths", boundary)
        self.assertIn("transition-rate readiness", boundary)


if __name__ == "__main__":
    unittest.main()
