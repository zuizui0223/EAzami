"""Validate 45-tip Moreyra S1 specimen metadata × NMNS U/D and Siniscalchi 9 traits.

This test uses the real original Japan38 frozen 39-sample manifest and
immutable author 63-taxon traits.csv, not the inferred new tree topology.
"""
from __future__ import annotations

import os,sys,unittest
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"analysis"))
from annotate_real_world45_comp1061_S1_and_head_traits_v1 import overlay

class Real45MorphologicalIntake(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        org=os.environ.get("EAzami_J38_SRC")
        traits=os.environ.get("EAzami_NA_TRAITS")
        if not org or not traits:
            raise RuntimeError("Set explicit real source artefact EAzami_J38_SRC and EAzami_NA_TRAITS")
        cls.data=overlay(Path(org),Path("."),Path(traits))
        cls.m={r["tip_id"]:r for r in cls.data}

    def test_all_distinct_actual_molecular_source_S1_tips(self):
        self.assertEqual(len(self.data),44)
        self.assertEqual(len(self.m),44)
        self.assertEqual(sum(r["tip_id"].startswith("J38S") for r in self.data),39)
        self.assertEqual(sum(r["tip_id"].startswith("GLB_") for r in self.data),5)
        self.assertTrue(all(r["biosample"].startswith("SAMN") for r in self.data))
        self.assertTrue(all(r["run_accessions"].startswith("SRR") for r in self.data))

    def test_U_and_D_species_head_states_keep_documented_polymorphisms_unresolved(self):
        self.assertEqual(Counter(r["head_state"] for r in self.data),{"U":17,"D":7,"?":20})
        self.assertEqual(self.m["J38S037"]["head_state"],"?")  # C. sieboldii
        self.assertEqual(self.m["J38S017"]["head_state"],"?")  # C. maritimum
        self.assertEqual(self.m["GLB_SRR30887231_Cirsium_vinaceum"]["head_state"],"D")
        self.assertEqual(self.m["GLB_SRR30887186_Cirsium_erisithales"]["head_state"],"D")

    def test_NMNS_color_polymorphism_not_forced_as_white(self):
        self.assertEqual(Counter(r["corolla_colour_authority"] for r in self.data),{"?":36,"C":5,"P":3})
        for tip in ("J38S005","J38S037","J38S039"):
            self.assertEqual(self.m[tip]["corolla_colour_authority"],"P")
        self.assertTrue(all(r["trait_same_sequenced_voucher_confirmed"]=="false" for r in self.data))

    def test_2023_na_nine_morphologies_only_on_exact_matched_world_taxa(self):
        names=[r["source_taxon_label"] for r in self.data if r.get("Siniscalchi_head_position")]
        self.assertEqual(sorted(names),sorted(["Cirsium vinaceum","Cirsium flodmanii","Cirsium ownbeyi"]))
        for r in self.data:
            if r["source_taxon_label"] in names:
                self.assertTrue(r.get("Siniscalchi_style_branch_colour")!="")
            else:
                self.assertEqual(r.get("Siniscalchi_head_position",""),"")

if __name__=="__main__":
    unittest.main()
