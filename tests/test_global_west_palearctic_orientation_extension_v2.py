"""Western independent orientation source audit: no retroactive alteration of 35."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"analysis"))
from audit_global_west_palearctic_orientation_extension_v2 import audit  # noqa: E402


class WestPalearcticNewSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report,cls.rows=audit()
        cls.by_name={x["molecular_source_taxon_label"]:x for x in cls.rows}

    def test_exact_molecular_literature_names_in_public_nuclear_registry(self):
        self.assertEqual(self.report["n_botanical_evidence_taxa"],3)
        self.assertEqual(self.report["n_molecular_exact_label_matches"],3)
        self.assertEqual(set(self.by_name),{
            "Cirsium erisithales","Cirsium eriophorum","Cirsium oleraceum",
        })
        self.assertTrue(all(x["n_biosamples"]>=1 for x in self.rows))

    def test_source_name_disagreement_not_silently_promoted(self):
        self.assertEqual(self.by_name["Cirsium eriophorum"]["prospective_admission"],
                         "source_name_review_hold")
        self.assertEqual(self.by_name["Cirsium erisithales"]["prospective_admission"],
                         "exact_source_candidate")
        self.assertEqual(self.by_name["Cirsium oleraceum"]["prospective_admission"],
                         "exact_source_candidate")
        self.assertEqual(self.report["name_review_holds"],1)
        self.assertEqual((self.report["clean_U"],self.report["clean_D"]),(1,1))

    def test_no_climate_or_history_admission(self):
        self.assertTrue(self.report["baseline_frozen_35_membership_unchanged"])
        self.assertFalse(self.report["native_origin_verified"])
        self.assertFalse(self.report["nuclear_tree_ready"])
        self.assertFalse(self.report["branchwise_transition_executed"])
        self.assertTrue(all(r["same_voucher_head_phenotype_verified"]=="false" for r in self.rows))
        self.assertTrue(all(r["BIO15_BIO1_opened"]=="false" for r in self.rows))


if __name__=="__main__":
    unittest.main()
