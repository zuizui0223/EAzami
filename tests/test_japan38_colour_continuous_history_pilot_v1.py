import importlib.util
import math
import tempfile
import unittest
from io import StringIO
from pathlib import Path

import numpy as np
from Bio import Phylo

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "colour_history", ROOT / "analysis/run_japan38_colour_continuous_history_pilot_v1.py"
)
assert SPEC and SPEC.loader
ch = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ch)


class TestJapan38ColourContinuousHistoryPilot(unittest.TestCase):
    def tree(self):
        return Phylo.read(StringIO("((A:1,B:1):1,(C:1,D:1):1);"), "newick")

    def test_covariance_uses_shared_root_path(self):
        tree = self.tree()
        C, scale = ch.covariance_matrix(tree, ["A", "B", "C", "D"])
        self.assertAlmostEqual(scale, 2.0)
        self.assertAlmostEqual(C[0, 0], 1.0)
        self.assertAlmostEqual(C[0, 1], 0.5)
        self.assertAlmostEqual(C[0, 2], 0.0)

    def test_pagel_lambda_fit_is_bounded_and_finite(self):
        tree = self.tree()
        C, _ = ch.covariance_matrix(tree, ["A", "B", "C", "D"])
        fit = ch.fit_pagel_lambda([0.0, 0.1, 2.0, 2.1], C)
        self.assertGreaterEqual(fit["lambda_mle"], 0.0)
        self.assertLessEqual(fit["lambda_mle"], 1.0)
        self.assertTrue(math.isfinite(fit["log_likelihood_mle"]))
        self.assertTrue(math.isfinite(fit["brownian_scale_parameter"]))

    def test_circular_hue_wrap_is_small(self):
        a = {"paper_japan_member_id": "A", "corolla_hue_sin_species_median": math.sin(math.radians(359)), "corolla_hue_cos_species_median": math.cos(math.radians(359))}
        b = {"paper_japan_member_id": "B", "corolla_hue_sin_species_median": math.sin(math.radians(1)), "corolla_hue_cos_species_median": math.cos(math.radians(1))}
        va = ch.normalized_hue_vector(a)
        vb = ch.normalized_hue_vector(b)
        self.assertLess(float(np.linalg.norm(va - vb)), 0.05)

    def test_exact_colour_tree_prunes_replicated_and_disallowed_concepts(self):
        raw = Phylo.read(
            StringIO("((((a:1,b:1):1,c:1):1,d:1):1,OUTGROUP_saff:1);"),
            "newick",
        )
        with tempfile.TemporaryDirectory() as td:
            tree_path = Path(td) / "x.nwk"
            Phylo.write(raw, tree_path, "newick")
            cmap = {
                "JPN_20": ["a", "b"],
                "JPN_31": ["c"],
                "JPN_36": ["d"],
            }
            allowed = {"JPN_20": True, "JPN_31": False, "JPN_36": True}
            # _validate_raw_tree normally expects the full Japan38 map, so test the
            # essential exclusion invariant directly on the loader helper with a
            # patched validator for this tiny synthetic tree.
            original = ch._validate_raw_tree
            try:
                ch._validate_raw_tree = lambda tree, cmap: tree.root_with_outgroup("OUTGROUP_saff")
                out = ch.load_colour_concept_tree(tree_path, cmap, allowed, {"JPN_36"})
            finally:
                ch._validate_raw_tree = original
        self.assertEqual({t.name for t in out.get_terminals()}, {"JPN_36"})


if __name__ == "__main__":
    unittest.main()
