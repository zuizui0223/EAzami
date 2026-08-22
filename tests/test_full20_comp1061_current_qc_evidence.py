import hashlib
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "data" / "evidence" / "full20_comp1061_current_qc_evidence_v1.json"
LOCI = ROOT / "data" / "evidence" / "full20_comp1061_current_conservative_206_loci_v1.txt"


class Full20Comp1061CurrentQcEvidenceTest(unittest.TestCase):
    def test_frozen_gate_and_strict_locus_list(self):
        x = json.loads(EVIDENCE.read_text())
        loci = [line.strip() for line in LOCI.read_text().splitlines() if line.strip()]
        strict = x["sets"]["conservative_241"]

        self.assertEqual(x["contract_version"], "full20_comp1061_current_qc_evidence_v1")
        self.assertEqual(x["panel"]["primary_tips"], 20)
        self.assertEqual(x["gate"]["minimum_present_tips"], 16)
        self.assertEqual(x["gate"]["result"], "PASS")
        self.assertEqual(strict["current_eligible_count"], 206)
        self.assertGreaterEqual(strict["current_eligible_count"], x["gate"]["minimum_conservative_241_eligible_loci"])
        self.assertTrue(strict["all_20_taxa_represented"])
        self.assertEqual(strict["absolute_library_type_median_gap"], 0.0)

        self.assertEqual(len(loci), 206)
        self.assertEqual(len(set(loci)), 206)
        self.assertEqual(hashlib.sha256(LOCI.read_bytes()).hexdigest(), x["strict_locus_list"]["sha256"])

        self.assertTrue(x["pilot_reproducibility"]["pr48_cirsium_suffultum"]["exact_recovered_locus_set_match"])
        self.assertTrue(x["pilot_reproducibility"]["pr49_cirsium_japonicum_var_albescens"]["exact_recovered_locus_set_match"])
        self.assertFalse(x["promotion_boundary"]["tree_matrix_auto_promotion_allowed"])
        self.assertFalse(x["promotion_boundary"]["rate_fit_execution_allowed"])


if __name__ == "__main__":
    unittest.main()
