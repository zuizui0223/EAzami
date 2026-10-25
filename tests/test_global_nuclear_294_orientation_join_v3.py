"""Source-only integration tests: 294 unique BioSamples, no false transition replicates."""
from __future__ import annotations

import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))
from audit_global_nuclear_294_orientation_join_v3 import rebuild_panel_and_join  # noqa: E402


class Nuclear294HeadOrientationJoinTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report, cls.samples, cls.taxa = rebuild_panel_and_join()
        cls.by_taxon = {x["analysis_taxon_label"]: x for x in cls.taxa}

    def test_original_complete_nuclear_sample_registry_retained(self):
        r=self.report
        self.assertEqual(r["n_biosamples"], 294)
        self.assertEqual(r["n_public_run_accessions"], 295)
        self.assertEqual(r["n_source_taxon_labels"], 270)
        self.assertEqual(r["builder_contract"]["Chang_cross_paper_shared_samples"], 8)
        self.assertEqual(r["candidate_distinct_taxon_states"], {"U":29,"D":13})
        self.assertEqual(r["candidate_distinct_taxon_states_without_any_source_name_review"], {"U":24,"D":11})
        self.assertEqual(r["candidate_sample_states"], {"U":40,"D":21})
        self.assertEqual(r["candidate_sample_states_without_source_name_review"], {"U":30,"D":16})
        self.assertEqual(r["candidate_sample_inference_gates"]["hold_source_taxon_name_conflict"], 15)
        self.assertEqual(len({r["biosample"] for r in self.samples}), 294)
        self.assertEqual(len({r["panel_id"] for r in self.samples}), 294)

    def test_duplicate_biological_samples_not_evolutionary_transitions(self):
        for name in ("Cirsium brevicaule", "Cirsium irumtiense"):
            self.assertEqual(self.by_taxon[name]["n_biosamples"], 3)
            self.assertEqual(self.by_taxon[name]["needs_population_aware_or_one_representative_design"], "true")
        self.assertTrue(all(r["repeated_biosample_is_independent_trait_origin"] == "false" for r in self.samples))

    def test_source_based_candidates_have_audit_provenance(self):
        r=self.report
        self.assertGreaterEqual(r["candidate_distinct_taxon_states"]["U"], 23)
        self.assertGreaterEqual(r["candidate_distinct_taxon_states"]["D"], 7)
        for row in self.samples:
            if row["orientation_state_candidate"]:
                self.assertIn(row["orientation_state_candidate"], {"U","D"})
                self.assertTrue(row["orientation_evidence_source_urls"])
                self.assertTrue(row["orientation_evidence_lanes"])

    def test_historical_climate_and_voucher_status_never_implicitly_promoted(self):
        x=self.report
        self.assertFalse(x["public_source_inference_ready"])
        self.assertFalse(x["global_nuclear_tree_executed"])
        self.assertFalse(x["branchwise_climate_shift_estimable"])
        self.assertFalse(x["all_294_biosamples_same_voucher_head_state_verified"])
        self.assertTrue(all(row["same_voucher_orientation_confirmed"]=="false" for row in self.samples))

    def test_ambiguous_worldwide_source_not_forced_into_binary_label(self):
        name="Cirsium eatonii"
        self.assertEqual(self.by_taxon[name]["orientation_state_candidate"], "")
        name="Cirsium joannae"
        self.assertEqual(self.by_taxon[name]["orientation_state_candidate"], "")
        self.assertEqual(self.by_taxon["Cirsium vinaceum"]["orientation_state_candidate"], "D")
        self.assertEqual(self.by_taxon["Cirsium ownbeyi"]["orientation_state_candidate"], "U")

    def test_preserve_both_target_capture_and_transcriptome_assays(self):
        assays=Counter(r["assay"] for r in self.samples)
        self.assertEqual(assays["Compositae1061_target_capture"],256)
        self.assertEqual(assays["leaf_RNAseq_transcriptome"],38)


if __name__=="__main__":
    unittest.main()
