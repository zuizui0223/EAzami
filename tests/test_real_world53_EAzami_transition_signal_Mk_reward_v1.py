"""Regression for actual world53 two-direction evolutionary history estimator."""
from __future__ import annotations

import io
import math
import sys
import unittest
from pathlib import Path

import numpy as np
from Bio import Phylo

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"analysis"))
from run_real_world53_EAzami_transition_signal_Mk_reward_v1 import (
    concept, exact_markov_rewards, fitch, compiled_fitch, root_prior_sensitivity,
)


class EAzamiWorld53MkEvidenceTests(unittest.TestCase):
    def test_variety_identity_is_distinct_from_species_identity(self):
        self.assertEqual(concept("Cirsium nipponicum Makino"),"Cirsium nipponicum")
        self.assertEqual(concept("Cirsium nipponicum var. incomptum (Maxim.) Kadota"),
                         "Cirsium nipponicum var. incomptum")
        self.assertEqual(concept("Cirsium nipponicum var. yoshinoi (Nakai) Kitam."),
                         "Cirsium nipponicum var. yoshinoi")
        self.assertEqual(concept("Cirsium fontinale var. campylon"),
                         "Cirsium fontinale var. campylon")

    def test_infraspecific_unknowns_must_remain_missing(self):
        tree=Phylo.read(io.StringIO(
            "((A:0.1,B:0.1):0.1,(C:0.1,D:0.1):0.1);"),"newick")
        source={
            "A":{"source_taxon":"Cirsium nipponicum Makino"},
            "B":{"source_taxon":"Cirsium nipponicum var. incomptum Kadota"},
            "C":{"source_taxon":"Cirsium nipponicum var. yoshinoi Kitam."},
            "D":{"source_taxon":"Cirsium kamtschaticum DC."},
        }
        compiled=compiled_fitch(tree,source)
        observed={"Cirsium nipponicum":"U","Cirsium kamtschaticum":"D"}
        self.assertEqual(fitch(compiled,observed),1)
        self.assertEqual(concept(source["B"]["source_taxon"]) in observed,False)
        self.assertEqual(concept(source["C"]["source_taxon"]) in observed,False)

    def test_van_loan_reward_on_short_branch_has_one_forward_event(self):
        import scipy.linalg
        qUD,qDU=.15,.3
        t=1e-5
        Q=np.array([[-qUD,qUD],[qDU,-qDU]])
        R=np.array([[0,qUD],[0,0.]])
        B=np.zeros((4,4))
        B[:2,:2]=Q
        B[2:,2:]=Q
        B[:2,2:]=R
        P=scipy.linalg.expm(Q*t)
        counts=scipy.linalg.expm(B*t)[:2,2:]
        # Conditioning on U start and D endpoint at a tiny time interval
        # implies one forward switch (all extra hidden reversals vanish O(t²)).
        self.assertAlmostEqual(counts[0,1]/P[0,1],1.,places=7)
        self.assertGreater(counts[0,0],0.)

    def test_equal_root_prior_with_flat_likelihood_is_uninformative(self):
        fits={"post":{"node_posterior":np.array([[0.5,0.5]])}}
        x=root_prior_sensitivity(fits)
        self.assertAlmostEqual(x["0.1"],.1)
        self.assertAlmostEqual(x["0.5"],.5)
        self.assertAlmostEqual(x["0.9"],.9)


if __name__=="__main__":
    unittest.main()
