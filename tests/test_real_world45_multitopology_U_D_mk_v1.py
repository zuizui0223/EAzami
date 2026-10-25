"""Regression and synthetic proof tests for real 45-tip nuclear Mk source model."""
from __future__ import annotations

import io
import math
import sys
import unittest
from pathlib import Path

from Bio import Phylo

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"analysis"))
import fit_real_world45_multitopology_U_D_mk_v1 as m  # noqa: E402


def make_rows(states):
    return {k:{"tip_id":k,"head_orientation":v,"head_source_url":"urn:synthetic"}
            for k,v in states.items()}


class GenuineWorld45MkRegression(unittest.TestCase):
    def test_asymmetric_transition_probability_semantics(self):
        P=m.transmat(5.,2.,.4)
        self.assertTrue(((P>=0)&(P<=1)).all())
        self.assertAlmostEqual(float(P[0].sum()),1.)
        self.assertAlmostEqual(float(P[1].sum()),1.)
        self.assertGreater(P[0,1],P[1,0])
        self.assertAlmostEqual(P[0,1]/P[1,0],2.5,places=8)

    def test_missing_source_tip_is_marginalized_not_coded_U(self):
        t=Phylo.read(io.StringIO("((A:0.2,B:0.2):0.2,(C:0.2,D:0.2):0.2);"),"newick")
        a=make_rows({"A":"U","B":"?","C":"D","D":"U"})
        missing,_=m.mk(t,a,2.,2.)
        a["B"]["head_orientation"]="U"
        observedU,_=m.mk(t,a,2.,2.)
        a["B"]["head_orientation"]="D"
        observedD,_=m.mk(t,a,2.,2.)
        self.assertAlmostEqual(math.exp(missing),
                               math.exp(observedU)+math.exp(observedD),places=10)

    def test_root_and_edges_are_normalized_under_seven_mixed_states(self):
        t=Phylo.read(io.StringIO("((A:0.1,B:0.3):0.15,(C:0.3,D:0.5):0.25);"),"newick")
        rows=make_rows({"A":"D","B":"U","C":"?","D":"D"})
        likelihood,posterior=m.mk(t,rows,3.5,2.,posterior=True)
        self.assertTrue(math.isfinite(likelihood))
        self.assertEqual(len(posterior["edge_joint"]),6)
        self.assertTrue(all(abs(float(J.sum())-1)<1e-8
                            for J in posterior["edge_joint"].values()))
        self.assertTrue(all(abs(float(p.sum())-1)<1e-8
                            for p in posterior["node_posterior"]))

    def test_synthetic_fitch_four_tips(self):
        t=Phylo.read(io.StringIO("((A:1,B:1):1,(C:1,D:1):1);"),"newick")
        rows=make_rows({"A":"U","B":"D","C":"U","D":"?"})
        self.assertEqual(m.fitch_minimum(t,rows),1)

    def test_real_original_S1_source_counts_and_region_evidence(self):
        p=Path(".tmp/realworld45-Mk-source/real_nuclear45_source_traits_v1.csv")
        if not p.exists():
            self.skipTest("original source evidence not fetched in offline test")
        rows=m.load_rows(p)
        self.assertEqual(len(rows),44)
        self.assertEqual(sum(r["head_orientation"]=="U" for r in rows.values()),17)
        self.assertEqual(sum(r["head_orientation"]=="D" for r in rows.values()),7)
        self.assertEqual(sum(r["head_orientation"]=="?" for r in rows.values()),20)
        self.assertEqual(rows[m.EU_D]["head_orientation"],"D")
        self.assertEqual(rows[m.NA_D]["head_orientation"],"D")


if __name__=="__main__":
    unittest.main()
