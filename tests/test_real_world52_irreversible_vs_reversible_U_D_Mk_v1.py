"""Tests for directional vs reversible EAzami real-52 S1 nuclear Mk hypotheses."""
from __future__ import annotations
import math
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"analysis"))
import run_real_world52_irreversible_vs_reversible_U_D_Mk_v1 as m  # noqa


class OneWayMkReal52(unittest.TestCase):
    def test_UD_only_is_absorbing_at_D(self):
        P=m.transition(3.,0.,.4)
        self.assertAlmostEqual(float(P[1,0]),0.,places=14)
        self.assertAlmostEqual(float(P[1,1]),1.,places=14)
        self.assertGreater(P[0,1],0.)
        np.testing.assert_allclose(P.sum(axis=1),1.,atol=1.e-12)

    def test_DU_only_is_absorbing_at_U(self):
        P=m.transition(0.,3.,.4)
        self.assertAlmostEqual(float(P[0,1]),0.,places=14)
        self.assertAlmostEqual(float(P[0,0]),1.,places=14)
        self.assertGreater(P[1,0],0.)
        np.testing.assert_allclose(P.sum(axis=1),1.,atol=1.e-12)

    def test_missing_trait_probability_is_the_sum_of_two_exclusive_cases(self):
        compiled={"n_nodes":3,"tips":{"A":1,"B":2},
                  "children":[[(1,.2),(2,.3)],[],[]],"postorder":[1,2,0]}
        base={"A":"U","B":"?"}
        unknown=m.likelihood(compiled,base,2.,1.5,.5)
        knownU=m.likelihood(compiled,{"A":"U","B":"U"},2.,1.5,.5)
        knownD=m.likelihood(compiled,{"A":"U","B":"D"},2.,1.5,.5)
        self.assertAlmostEqual(math.exp(unknown),math.exp(knownU)+math.exp(knownD),places=12)

    def test_irreversible_UD_very_small_time_transition(self):
        t=1.e-11
        P=m.transition(4.,0.,t)
        self.assertAlmostEqual(float(P[0,1]),4*t,delta=4*t*1.e-8)
        self.assertAlmostEqual(float(P[1,0]),0.)

    def test_original_BioSample_identity_and_flower_CSV(self):
        p=Path(".tmp/EAzami52/source/world52_source_S1_unique_BioSample_9traits.csv")
        if not p.is_file():
            self.skipTest("source archive not mounted for an offline isolated unit test")
        records=m.source_traits(p)
        self.assertEqual(len(records),51)
        self.assertEqual(sum(x["head_orientation"]=="D" for x in records.values()),8)
        self.assertEqual(sum(x["head_orientation"]=="U" for x in records.values()),19)
        self.assertEqual(sum(x["head_orientation"]=="?" for x in records.values()),24)

    def test_taxon_concept_keeps_variety_not_just_species(self):
        self.assertEqual(m.taxon_concept("Cirsium fontinale var. campylon"),
                         "Cirsium fontinale var. campylon")
        self.assertEqual(m.taxon_concept("Cirsium alpicola Nakai"),
                         "Cirsium alpicola")

    def test_input_expected_corrected_tree_fingerprints_frozen(self):
        self.assertEqual(len(m.PINS),3)
        self.assertEqual(m.PHENOTYPE_SHA,"1a4629347007b73b900db5b7c36fba345933281b9868d1c9555f4a1906100962")


if __name__=="__main__":
    unittest.main()
