"""Mathematical regressions for 52-tip source Mk-vs-IID saturation diagnostic."""
from __future__ import annotations
import math,sys,unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"analysis"))
from audit_world52_EAzami_Mk_vs_IID_saturation_v1 import concept,iid_fit


class MkSaturationVsIID(unittest.TestCase):
    def test_baseline_exact_eight_D_nineteen_U(self):
        a=iid_fit(19,8)
        self.assertEqual(a["n_named_taxon_concepts"],27)
        self.assertAlmostEqual(a["p_D_empirical"],8/27,places=12)
        self.assertAlmostEqual(a["IID_loglik"],-16.407722444515827,places=9)
        self.assertAlmostEqual(a["IID_AICc_k1"],34.97544488903165,places=9)

    def test_missing_held_D_is_not_misassigned(self):
        a=iid_fit(19,7)
        self.assertEqual(a["D"],7)
        self.assertEqual(a["n_named_taxon_concepts"],26)
        self.assertEqual(a["U"],19)

    def test_variety_retained_not_collapsed_into_species(self):
        self.assertEqual(concept("Cirsium nipponicum var. yoshinoi Kodota"),
                         "Cirsium nipponicum var. yoshinoi")
        self.assertNotEqual(concept("Cirsium nipponicum var. yoshinoi"),
                            concept("Cirsium nipponicum"))
        self.assertEqual(concept("Cirsium abukumense Kadota"),"Cirsium abukumense")

    def test_identification_rejects_invalid_species_concept(self):
        for name in ("", "Rosa canina","Cirsium 123"):
            with self.assertRaises(ValueError):
                concept(name)

    def test_monophyletic_phylogeny_is_not_proven_by_iid_goodness_of_fit(self):
        a=iid_fit(19,8)
        self.assertLess(a["IID_AICc_k1"],37.29178916200412)
        self.assertEqual(a["n_named_taxon_concepts"],27)


if __name__=="__main__":
    unittest.main()
