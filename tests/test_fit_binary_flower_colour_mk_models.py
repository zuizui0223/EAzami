from __future__ import annotations

import importlib.util
import json
import math
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/'analysis/fit_binary_flower_colour_mk_models.py'
spec=importlib.util.spec_from_file_location('mkfit',MOD);assert spec and spec.loader
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class MkFitTests(unittest.TestCase):
    def test_transition_rows_sum_to_one(self):
        p=m.transition(0.7,0.2,0.5)
        self.assertAlmostEqual(sum(p[0]),1.0,12);self.assertAlmostEqual(sum(p[1]),1.0,12)

    def test_symmetric_two_tip_likelihood_is_state_swap_invariant(self):
        root=m.Parser('(A:1.0,B:1.0);').parse()
        x=m.log_likelihood(root,{'A':'C','B':'W'},0.3,0.3,'equilibrium')
        y=m.log_likelihood(root,{'A':'W','B':'C'},0.3,0.3,'equilibrium')
        self.assertAlmostEqual(x,y,12)

    def test_missing_outgroup_state_is_allowed(self):
        root=m.Parser('((A:0.2,B:0.2):0.3,OUT:0.5);').parse()
        ll=m.log_likelihood(root,{'A':'C','B':'W'},0.2,0.1,'equilibrium')
        self.assertTrue(math.isfinite(ll))

    def test_precondition_gate_refuses_current_blockers(self):
        with tempfile.TemporaryDirectory() as td:
            r=Path(td);p=r/'p.json';t=r/'t.json'
            p.write_text(json.dumps({'execution_allowed':False,'blockers':['atlas_minimum_white_tips']}));t.write_text(json.dumps({'tree_gate_ready':True}))
            with self.assertRaisesRegex(RuntimeError,'atlas_minimum_white_tips'):m.require_gates(p,t)

    def test_fit_recovers_finite_er_and_ard(self):
        try:
            import scipy  # noqa:F401
        except ImportError:
            self.skipTest('scipy unavailable')
        root=m.Parser('(((A:0.3,B:0.3):0.2,C:0.5):0.2,(D:0.4,E:0.4):0.3);').parse()
        result=m.fit_models(root,{'A':'C','B':'C','C':'W','D':'C','E':'W'})
        self.assertGreater(result['ER']['q_C_to_W'],0)
        self.assertGreater(result['ARD']['q_W_to_C'],0)
        self.assertTrue(math.isfinite(result['comparison']['LR_pvalue']))
        self.assertEqual(result['n_observed_tips'],5)

if __name__=='__main__':unittest.main()
