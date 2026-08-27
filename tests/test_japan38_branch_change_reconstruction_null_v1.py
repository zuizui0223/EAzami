from __future__ import annotations

import sys
from io import StringIO
from pathlib import Path

import numpy as np
from Bio import Phylo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))

import run_japan38_all_continuous_history_v1 as hist
import run_japan38_branch_change_reconstruction_null_v1 as target


def test_linear_weights_reproduce_bm_conditional_branch_changes():
    tree = Phylo.read(StringIO("((A:1,B:1):1,(C:1,D:1):1);"), "newick")
    ids = ["A", "B", "C", "D"]
    values = {"A": -1.0, "B": 0.5, "C": 1.5, "D": -0.25}

    weights, branches = target.conditional_state_weights(tree, ids)
    y = np.asarray([values[x] for x in ids], float)
    got = target.scalar_magnitudes(weights, branches, y)

    states = hist.bm_states(tree, ids, values)
    nodes = list(tree.find_clades(order="preorder"))
    node_index = {node: i for i, node in enumerate(nodes)}
    expected = []
    for parent in nodes:
        for child in parent.clades:
            bl = float(child.branch_length)
            expected.append(abs(states[child] - states[parent]) / np.sqrt(bl))
    assert np.allclose(got, np.asarray(expected), rtol=1e-10, atol=1e-10)


def test_mean_pairwise_spearman_detects_shared_rank_order():
    x = np.asarray(
        [
            [1.0, 10.0, 2.0],
            [2.0, 20.0, 4.0],
            [3.0, 30.0, 6.0],
            [4.0, 40.0, 8.0],
        ]
    )
    assert abs(target.mean_pairwise_spearman(x) - 1.0) < 1e-12
