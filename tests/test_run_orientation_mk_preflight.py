from __future__ import annotations

import importlib.util
import json
import math
import random
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / "analysis/run_orientation_mk_preflight.py"
SPEC = importlib.util.spec_from_file_location("orientation_mk", MOD)
assert SPEC and SPEC.loader
m = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = m
SPEC.loader.exec_module(m)


class OrientationMkPreflightTests(unittest.TestCase):
    def test_sankoff_transition_lower_bound(self):
        root = m.mk.Parser("((A:0.2,B:0.2):0.3,(C:0.2,D:0.2):0.3);").parse()
        states = {"A": "U", "B": "U", "C": "D", "D": "D"}
        self.assertEqual(m.sankoff_min_transitions(root, states), 1)

    def test_missing_tip_state_remains_missing_not_forced(self):
        root = m.mk.Parser("((A:0.2,B:0.2):0.3,(C:0.2,D:0.2):0.3);").parse()
        states = {"A": "U", "B": "U", "D": "D"}
        self.assertEqual(m.sankoff_min_transitions(root, states), 1)

    def test_symmetric_root_probability_is_half(self):
        root = m.mk.Parser("((A:0.5,B:0.5):0.2,(C:0.5,D:0.5):0.2);").parse()
        states = {"A": "U", "B": "U", "C": "D", "D": "D"}
        p = m.conditional_root_probability(root, states, 0.4, 0.4, "flat")
        self.assertTrue(math.isclose(p, 0.5, rel_tol=0, abs_tol=1e-12))

    def test_simulation_is_seed_reproducible(self):
        root = m.mk.Parser("(A:0.5,B:0.5);").parse()
        x = m.simulate_tip_states(root, 0.3, 0.2, "equilibrium", random.Random(9))
        y = m.simulate_tip_states(root, 0.3, 0.2, "equilibrium", random.Random(9))
        self.assertEqual(x, y)
        self.assertEqual(set(x), {"A", "B"})
        self.assertTrue(set(x.values()) <= {"U", "D"})

    def test_tree_acceptance_gate_is_mandatory(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            summary = root / "summary.json"
            acceptance = root / "acceptance.json"
            summary.write_text(json.dumps({
                "fixed_state_counts": {"upward_or_erect": 9, "downward_or_nodding": 8},
                "execution_gates": {"orientation_mk_preflight_allowed_after_accepted_tree": True},
            }))
            acceptance.write_text(json.dumps({"tree_gate_ready": False}))
            with self.assertRaisesRegex(RuntimeError, "accepted branch-length tree"):
                m.require_gates(summary, acceptance)

    def test_state_balance_gate_is_mandatory(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            summary = root / "summary.json"
            acceptance = root / "acceptance.json"
            summary.write_text(json.dumps({
                "fixed_state_counts": {"upward_or_erect": 9, "downward_or_nodding": 4},
                "execution_gates": {"orientation_mk_preflight_allowed_after_accepted_tree": True},
            }))
            acceptance.write_text(json.dumps({"tree_gate_ready": True}))
            with self.assertRaisesRegex(RuntimeError, "at least five fixed tips"):
                m.require_gates(summary, acceptance)

    def test_adequacy_requires_nontrivial_simulation_count(self):
        root = m.mk.Parser("(A:0.5,B:0.5);").parse()
        with self.assertRaisesRegex(ValueError, "at least 100"):
            m.adequacy_diagnostics(root, {"A": "U", "B": "D"}, 0.2, 0.2, "flat", 99, 1)


if __name__ == "__main__":
    unittest.main()
