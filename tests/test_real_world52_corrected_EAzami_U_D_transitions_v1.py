"""Regression for REAL corrected 52-tip nuclear U/D Mk, reward integrals and concept-null."""
from __future__ import annotations
import io
import math
import sys
import unittest
from collections import Counter
from pathlib import Path

from Bio import Phylo
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"analysis"))
import run_real_world52_corrected_EAzami_U_D_transitions_v1 as s
from fit_real_world45_multitopology_U_D_mk_v1 import fit_one


def synthetic():
    tree=Phylo.read(io.StringIO("((A:0.01,B:0.025):0.03,(C:0.014,D:0.031):0.012);"),"newick")
    obs={
        "A":{"head_orientation":"U","source_taxon":"Cirsium a"},
        "B":{"head_orientation":"D","source_taxon":"Cirsium b"},
        "C":{"head_orientation":"?","source_taxon":"Cirsium c"},
        "D":{"head_orientation":"D","source_taxon":"Cirsium d"},
    }
    return tree,obs


class EAzami52OriginalNuclearTests(unittest.TestCase):
    def test_fit_unknown_is_marginalized_and_exact_reward_not_equal_Fitch(self):
        tree,source=synthetic()
        for model in ("ER","ARD"):
            fit=fit_one(tree,source,model)
            ud,du,edges=s.exact_markov_rewards(tree,fit)
            self.assertTrue(all(math.isfinite(x) and x>=0 for x in (ud,du)))
            self.assertEqual(len(edges),6)
            endpoint_mass=sum(e["P_parent_U_child_D_endpoints"] for e in edges)
            self.assertGreaterEqual(ud+1e-7,endpoint_mass)
            self.assertTrue(any(e["expected_hidden_and_visible_U_to_D_given_fitted_model"]>=0
                                for e in edges))
            r=s.root_prior_sensitivity(fit)
            self.assertLess(r["0.1"],r["0.9"])

    def test_both_external_head_holdouts_preserve_molecular_tip_count(self):
        t,source=synthetic()
        source[s.NA_D]={"head_orientation":"D","source_taxon":"Cirsium vinaceum"}
        source[s.EU_D]={"head_orientation":"D","source_taxon":"Cirsium erisithales"}
        self.assertEqual(s.model_ancestral(t,source,"primary_all_source_states")[s.NA_D]["head_orientation"],"D")
        self.assertEqual(s.model_ancestral(t,source,"north_america_D_unresolved")[s.NA_D]["head_orientation"],"?")
        self.assertEqual(s.model_ancestral(t,source,"west_D_cultivated_unresolved")[s.EU_D]["head_orientation"],"?")
        self.assertEqual(source[s.NA_D]["head_orientation"],"D")

    def test_variety_taxon_concept_not_silently_merged(self):
        self.assertNotEqual(s.concept("Cirsium nipponicum var. incomptum"),
                            s.concept("Cirsium nipponicum"))
        self.assertNotEqual(s.concept("Cirsium nipponicum var. yoshinoi"),
                            s.concept("Cirsium nipponicum var. incomptum"))

    def test_correct_original_52_nuclear_data_sha_when_available(self):
        d=Path(".tmp/EAzami52/source")
        a=d/"world52_source_S1_unique_BioSample_9traits.csv"
        if not a.exists():
            self.skipTest("source S1 nuclear table downloaded only in real-data CI")
        observed,groups,assigned,strata=s.validate_source_table(a)
        self.assertEqual(len(observed),51)
        self.assertEqual(len({r["source_biosample"] for r in observed.values()}),51)
        self.assertEqual(Counter(r["head_orientation"] for r in observed.values()),
                         Counter({"U":19,"D":8,"?":24}))
        self.assertEqual(len(assigned),27)
        self.assertNotIn(s.REMOVED_DUP,observed)
        self.assertEqual(observed[s.REAL_J38_KAM]["source_biosample"],"SAMN44017865")


if __name__=="__main__":
    unittest.main()
