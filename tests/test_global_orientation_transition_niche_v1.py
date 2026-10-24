"""Safety and numerical smoke tests for the gated global U->D workflow."""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))

import run_global_nuclear_orientation_transition_niche_v1 as runner  # noqa: E402
from run_global_nuclear_orientation_transition_niche_v1 import (  # noqa: E402
    FIELDS, load_tip_table, read_tree_ensemble, run,
)
from run_chapter2_orientation_transition_regime_hypothesis_v1 import (  # noqa: E402
    branchwise_stats, brownian_internal_values,
)

TREE1 = "(((A:0.2,B:0.2):0.2,(C:0.15,D:0.15):0.25):0.3,(E:0.2,F:0.2):0.5,OUT:0.4);"
TREE2 = "(((A:0.2,C:0.2):0.19,(B:0.18,D:0.18):0.23):0.29,(E:0.15,F:0.15):0.4,OUT:0.45);"


def sample_rows():
    values = [
        ("A", "U", 0.0, 11.0, "North"),
        ("B", "U", 0.5, 10.0, "South"),
        ("C", "D", 2.0, 5.0, "North"),
        ("D", "D", 3.0, 6.0, "South"),
        ("E", "U", 0.2, 9.0, "North"),
        ("F", "U", 0.4, 10.5, "South"),
    ]
    return [{
        "tip_id": tip, "accepted_taxon": "Synthetic_" + tip,
        "orientation_state": state, "bio15": str(bio15), "bio1": str(bio1),
        "biogeographic_region": region,
        "orientation_source": "synthetic_human_labels",
        "climate_source": "synthetic_centroid_values", "exclusion_reason": "",
    } for tip, state, bio15, bio1, region in values]


class GlobalOrientationWorkflowTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.trees = self.root / "trees.nwk"
        self.table = self.root / "tips.csv"
        self.trees.write_text(TREE1 + "\n" + TREE2 + "\n", encoding="utf-8")
        self.put_rows(sample_rows())

    def put_rows(self, rows):
        with self.table.open("w", newline="", encoding="utf-8") as h:
            w = csv.DictWriter(h, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(rows)

    def args(self, outdir="out", strata="region"):
        return argparse.Namespace(
            trees=self.trees, tip_table=self.table, outgroup="OUT",
            outdir=self.root / outdir, min_taxa=6, permutations=99,
            permutation_strata=strata, exact_limit=3000, seed=2317,
        )

    def test_exact_region_null_and_edge_joint_normalization(self):
        result = run(self.args())
        self.assertEqual(result["n_resolved_taxa"], 6)
        self.assertEqual(result["states"], {"U": 4, "D": 2})
        self.assertEqual(result["n_trees"], 2)
        self.assertEqual(result["null"]["unique_possible_maps"], 9)
        self.assertEqual(result["null"]["draws"], 9)
        self.assertEqual(result["null"]["method"], "exact_count_preserving")
        self.assertTrue(math.isfinite(result["observed"]["median_composite"]))
        self.assertTrue(0 < result["null"]["one_sided_rank"] <= 1)
        with (self.root / "out" / "edge_joint_posteriors.csv").open(encoding="utf-8") as h:
            rows = list(csv.DictReader(h))
        self.assertEqual(len(rows), 2 * (2 * 6 - 2))
        for r in rows:
            pu, pd = float(r["p_parent_U_child_D"]), float(r["p_parent_D_child_U"])
            self.assertTrue(0 <= pu <= 1 and 0 <= pd <= 1)
            self.assertAlmostEqual(float(r["p_endpoint_discordance"]), pu + pd, places=12)
        self.assertIn("historical_climate_on_transition_branch", result["not_estimated"])
        self.assertEqual(json.loads((self.root / "out" / "result.json").read_text())["status"],
                         "completed_present_niche_reconstruction_only")

    def test_global_null_is_independently_count_preserving(self):
        result = run(self.args(outdir="out_global", strata="global"))
        self.assertEqual(result["null"]["unique_possible_maps"], 15)
        self.assertEqual(result["null"]["draws"], 15)

    def test_missing_tree_tip_must_fail(self):
        self.trees.write_text("((A:0.2,B:0.2):0.3,(C:0.2,D:0.2):0.3,OUT:0.3);\n")
        with self.assertRaisesRegex(ValueError, "tree/metadata mismatch"):
            run(self.args())

    def test_undocumented_unresolved_tip_must_fail(self):
        rows = sample_rows()
        rows[1]["orientation_state"] = "unresolved"
        with self.assertRaisesRegex(ValueError, "explicit exclusion_reason"):
            self.put_rows(rows)
            load_tip_table(self.table)

    def test_pseudoreplicate_taxon_must_fail(self):
        rows = sample_rows()
        rows[1]["accepted_taxon"] = rows[0]["accepted_taxon"]
        self.put_rows(rows)
        with self.assertRaisesRegex(ValueError, "duplicate accepted_taxon"):
            run(self.args())

    def test_unverifiable_phenotype_must_fail(self):
        rows = sample_rows()
        rows[0]["orientation_source"] = ""
        self.put_rows(rows)
        with self.assertRaisesRegex(ValueError, "orientation_source missing"):
            run(self.args())

    def test_negative_branch_length_must_fail(self):
        self.trees.write_text(TREE1.replace("A:0.2", "A:-0.2") + "\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "non-positive/nonfinite"):
            run(self.args())

    def test_discrete_state_not_invented(self):
        rows = sample_rows()
        rows[0]["orientation_state"] = "?"
        self.put_rows(rows)
        with self.assertRaisesRegex(ValueError, "orientation_state must be"):
            run(self.args())

    def test_reproduces_frozen_east_asian_branchwise_formula(self):
        from run_global_nuclear_orientation_transition_niche_v1 import zscore
        rows = sample_rows()
        states = {r["tip_id"]: int(r["orientation_state"] == "D") for r in rows}
        vals15 = zscore([float(r["bio15"]) for r in rows])
        vals1 = zscore([float(r["bio1"]) for r in rows])
        climate15 = {r["tip_id"]: float(v) for r, v in zip(rows, vals15)}
        climate1 = {r["tip_id"]: float(v) for r, v in zip(rows, vals1)}
        trees = read_tree_ensemble(self.trees, {r["tip_id"] for r in rows}, "OUT", set(states))
        for i, tree in enumerate(trees, 1):
            _, d15 = brownian_internal_values(tree, climate15)
            _, d1 = brownian_internal_values(tree, climate1)
            original = branchwise_stats(tree, states, d15, d1)
            current, _ = runner.branch_statistics(tree, states, d15, d1, i)
            for key in ("q", "bio15", "bio1", "composite"):
                new_key = "q_symmetric_per_substitution_length" if key == "q" else key
                self.assertAlmostEqual(original[key], current[new_key], places=10)

    def test_climate_is_reconstructed_once_per_tree_not_once_per_null_map(self):
        with patch.object(runner, "brownian_internal_values", wraps=brownian_internal_values) as mocked:
            result = run(self.args(outdir="out_cached"))
            self.assertEqual(result["null"]["draws"], 9)
            self.assertEqual(mocked.call_count, 4)

    def test_brownian_unit_is_not_palaeo_exposure(self):
        result = run(self.args())
        self.assertEqual(result["model"]["branch_length_unit"],
                         "input phylogram substitutions/site, not calendar time")
        self.assertIn("transition_age", result["not_estimated"])


if __name__ == "__main__":
    unittest.main()
