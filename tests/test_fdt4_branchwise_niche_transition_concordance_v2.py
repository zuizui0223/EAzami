from io import StringIO

import numpy as np
from Bio import Phylo

from analysis import run_fdt4_branchwise_niche_transition_concordance_v2 as mod


def tree():
    return Phylo.read(StringIO("((A:1,B:1):1,(C:1,D:1):1);"), "newick")


def test_edge_posteriors_are_probabilities_and_expected_count_is_positive():
    subject = tree()
    states = {"A": 0, "B": 0, "C": 1, "D": 1}
    q = mod.fit_er_rate(subject, states)
    rows = mod.edge_transition_posteriors(subject, states, q)
    assert q > 0
    assert sum(row["p_state_change"] for row in rows) > 0
    for row in rows:
        assert 0 <= row["p_U_to_D"] <= 1
        assert 0 <= row["p_D_to_U"] <= 1
        assert 0 <= row["p_state_change"] <= 1


def test_squared_change_reconstruction_keeps_tip_values():
    subject = tree()
    values = {"A": -1.0, "B": -0.5, "C": 0.5, "D": 1.0}
    reconstructed = mod.squared_change_ancestral_states(subject, values)
    terminals = {tip.name: tip for tip in subject.get_terminals()}
    for name, value in values.items():
        assert reconstructed[terminals[name]] == value
    assert all(np.isfinite(list(reconstructed.values())))


def test_fixed_seed_permutation_result_is_reproducible():
    taxa = ["A", "B", "C", "D"]
    states = np.array([0, 0, 1, 1])
    axes = {"axis": np.array([-1.0, -0.5, 0.5, 1.0])}
    first = mod.analyze_topology(tree(), taxa, states, axes, permutations=99, seed=7)
    second = mod.analyze_topology(tree(), taxa, states, axes, permutations=99, seed=7)
    assert first == second
    assert 0 < first[0]["two_sided_permutation_p"] <= 1
