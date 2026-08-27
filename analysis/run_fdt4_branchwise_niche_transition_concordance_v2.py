#!/usr/bin/env python3
"""Branchwise orientation-transition versus niche-shift concordance.

The v1 result was frozen without executable source. This v2 implementation makes
the declared method reproducible: symmetric binary CTMC edge posteriors,
Brownian squared-change ancestral niche reconstruction, and fixed-count tip-state
permutations propagated across every AU-nonrejected optimized topology.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from Bio import Phylo
from Bio.Phylo.BaseTree import Clade, Tree
from scipy.optimize import minimize_scalar

from run_fdt4_orientation_niche_pgls_v1 import normalize_tip, read_optimized_trees


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transition_matrix(q: float, length: float) -> np.ndarray:
    if q <= 0 or length < 0:
        raise ValueError("CTMC rate must be positive and branch length nonnegative")
    decay = math.exp(-2.0 * q * length)
    same = 0.5 * (1.0 + decay)
    different = 0.5 * (1.0 - decay)
    return np.array([[same, different], [different, same]], dtype=float)


def prune_tree(tree: Tree, tip_names: list[str]) -> Tree:
    out = copy.deepcopy(tree)
    wanted = set(tip_names)
    present = {tip.name for tip in out.get_terminals()}
    missing = sorted(wanted.difference(present))
    if missing:
        raise ValueError(f"Tips absent from topology: {missing}")
    for tip in list(out.get_terminals()):
        if tip.name not in wanted:
            out.prune(tip)
    if {tip.name for tip in out.get_terminals()} != wanted:
        raise AssertionError("Tree pruning changed the requested tip set")
    for clade in out.find_clades(order="preorder"):
        if clade is out.root:
            continue
        if clade.branch_length is None or clade.branch_length <= 0:
            raise ValueError("Every retained branch must have a positive length")
    return out


def conditional_likelihoods(tree: Tree, states: dict[str, int], q: float) -> dict[Clade, np.ndarray]:
    conditional: dict[Clade, np.ndarray] = {}
    for node in tree.find_clades(order="postorder"):
        if node.is_terminal():
            state = states[node.name]
            conditional[node] = np.array([1.0, 0.0]) if state == 0 else np.array([0.0, 1.0])
            continue
        like = np.ones(2, dtype=float)
        for child in node.clades:
            matrix = transition_matrix(q, float(child.branch_length))
            like *= matrix @ conditional[child]
        conditional[node] = like
    return conditional


def er_log_likelihood(tree: Tree, states: dict[str, int], q: float) -> float:
    root_like = conditional_likelihoods(tree, states, q)[tree.root]
    likelihood = float(0.5 * root_like.sum())
    return math.log(max(likelihood, np.finfo(float).tiny))


def fit_er_rate(tree: Tree, states: dict[str, int]) -> float:
    result = minimize_scalar(
        lambda log_q: -er_log_likelihood(tree, states, math.exp(float(log_q))),
        bounds=(-12.0, 16.0),
        method="bounded",
        options={"xatol": 1e-10},
    )
    if not result.success:
        raise RuntimeError(f"ER rate optimization failed: {result.message}")
    return math.exp(float(result.x))


def edge_transition_posteriors(tree: Tree, states: dict[str, int], q: float) -> list[dict]:
    conditional = conditional_likelihoods(tree, states, q)
    outside: dict[Clade, np.ndarray] = {tree.root: np.array([0.5, 0.5], dtype=float)}
    root_total = float(outside[tree.root] @ conditional[tree.root])
    if root_total <= 0:
        raise ValueError("Zero conditional likelihood")
    rows: list[dict] = []
    for parent in tree.find_clades(order="preorder"):
        if parent.is_terminal():
            continue
        for child in parent.clades:
            sibling_product = np.ones(2, dtype=float)
            for sibling in parent.clades:
                if sibling is child:
                    continue
                sibling_product *= transition_matrix(q, float(sibling.branch_length)) @ conditional[sibling]
            matrix = transition_matrix(q, float(child.branch_length))
            joint = (
                outside[parent][:, None]
                * sibling_product[:, None]
                * matrix
                * conditional[child][None, :]
            ) / root_total
            outside[child] = (outside[parent] * sibling_product) @ matrix
            rows.append({
                "parent": parent,
                "child": child,
                "p_U_to_D": float(joint[0, 1]),
                "p_D_to_U": float(joint[1, 0]),
                "p_state_change": float(joint[0, 1] + joint[1, 0]),
            })
    return rows


def squared_change_ancestral_states(tree: Tree, tip_values: dict[str, float]) -> dict[Clade, float]:
    nodes = list(tree.find_clades(order="preorder"))
    index = {node: i for i, node in enumerate(nodes)}
    precision = np.zeros((len(nodes), len(nodes)), dtype=float)
    for parent in tree.find_clades(order="preorder"):
        for child in parent.clades:
            weight = 1.0 / float(child.branch_length)
            i, j = index[parent], index[child]
            precision[i, i] += weight
            precision[j, j] += weight
            precision[i, j] -= weight
            precision[j, i] -= weight
    tip_nodes = [node for node in nodes if node.is_terminal()]
    internal_nodes = [node for node in nodes if not node.is_terminal()]
    tip_indices = [index[node] for node in tip_nodes]
    internal_indices = [index[node] for node in internal_nodes]
    tip_vector = np.array([tip_values[node.name] for node in tip_nodes], dtype=float)
    q_ii = precision[np.ix_(internal_indices, internal_indices)]
    q_it = precision[np.ix_(internal_indices, tip_indices)]
    internal_vector = np.linalg.solve(q_ii, -q_it @ tip_vector)
    result = {node: float(value) for node, value in zip(tip_nodes, tip_vector)}
    result.update({node: float(value) for node, value in zip(internal_nodes, internal_vector)})
    return result


def directional_statistic(edge_rows: list[dict], node_values: dict[Clade, float]) -> tuple[float, float]:
    numerator = 0.0
    denominator = 0.0
    for row in edge_rows:
        shift = node_values[row["child"]] - node_values[row["parent"]]
        numerator += (row["p_U_to_D"] - row["p_D_to_U"]) * shift
        denominator += row["p_state_change"]
    if denominator <= 0:
        raise ValueError("Expected transition count is zero")
    return float(numerator / denominator), float(denominator)


def analyze_topology(
    tree: Tree,
    taxa: list[str],
    states: np.ndarray,
    standardized_axes: dict[str, np.ndarray],
    *,
    permutations: int,
    seed: int,
) -> list[dict]:
    tip_names = [normalize_tip(taxon) for taxon in taxa]
    pruned = prune_tree(tree, tip_names)
    observed_states = dict(zip(tip_names, states.astype(int)))
    q = fit_er_rate(pruned, observed_states)
    edge_rows = edge_transition_posteriors(pruned, observed_states, q)

    observed: dict[str, tuple[float, float]] = {}
    reconstructed = {}
    for axis, values in standardized_axes.items():
        tip_values = dict(zip(tip_names, values.astype(float)))
        node_values = squared_change_ancestral_states(pruned, tip_values)
        reconstructed[axis] = node_values
        observed[axis] = directional_statistic(edge_rows, node_values)

    rng = np.random.default_rng(seed)
    null = {axis: [] for axis in standardized_axes}
    for _ in range(permutations):
        permuted = rng.permutation(states).astype(int)
        permuted_states = dict(zip(tip_names, permuted))
        permuted_q = fit_er_rate(pruned, permuted_states)
        permuted_edges = edge_transition_posteriors(pruned, permuted_states, permuted_q)
        for axis in standardized_axes:
            stat, _ = directional_statistic(permuted_edges, reconstructed[axis])
            null[axis].append(stat)

    rows = []
    for axis, (stat, expected) in observed.items():
        values = np.asarray(null[axis], dtype=float)
        p_value = float((1 + np.sum(np.abs(values) >= abs(stat))) / (permutations + 1))
        rows.append({
            "axis": axis,
            "er_rate": q,
            "expected_orientation_transitions": expected,
            "directional_shift_sd": stat,
            "two_sided_permutation_p": p_value,
            "permutations": permutations,
            "seed": seed,
        })
    return rows


def analyze(
    occurrence_paths: list[Path],
    orientation_path: Path,
    au_trees_path: Path,
    *,
    nonrejected_count: int,
    min_n: int,
    axes: list[str],
    permutations: int,
    seed: int,
) -> tuple[pd.DataFrame, dict]:
    if permutations < 99:
        raise ValueError("At least 99 fixed-count permutations are required")
    occ = pd.concat([pd.read_csv(path) for path in occurrence_paths], ignore_index=True)
    if "environment_complete" in occ.columns:
        occ = occ.loc[occ["environment_complete"].astype(bool)].copy()
    missing_axes = sorted(set(axes).difference(occ.columns))
    if missing_axes:
        raise ValueError(f"Occurrence files are missing axes: {missing_axes}")
    counts = occ.groupby("scientific_name_query").size()
    orientation = pd.read_csv(orientation_path)
    orientation = orientation.loc[orientation["analysis_state"].isin(["U", "D"])].copy()
    state_by_taxon = dict(zip(orientation["accepted_taxon"], orientation["analysis_state"]))
    taxa = sorted(taxon for taxon, count in counts.items() if count >= min_n and taxon in state_by_taxon)
    if len(taxa) < 6:
        raise ValueError(f"Too few usable resolved taxa: {len(taxa)}")
    centroids = occ.groupby("scientific_name_query")[axes].mean().loc[taxa]
    standardized = {}
    for axis in axes:
        values = centroids[axis].to_numpy(float)
        sd = float(np.std(values, ddof=1))
        if not np.isfinite(sd) or sd <= 0:
            raise ValueError(f"Axis {axis} has no usable variance")
        standardized[axis] = (values - float(np.mean(values))) / sd
    states = np.array([0 if state_by_taxon[taxon] == "U" else 1 for taxon in taxa], dtype=int)
    trees = read_optimized_trees(au_trees_path, nonrejected_count)
    rows = []
    for topology_index, tree in enumerate(trees, start=1):
        topology_rows = analyze_topology(
            tree, taxa, states, standardized,
            permutations=permutations,
            seed=seed + topology_index * 1000,
        )
        for row in topology_rows:
            rows.append({
                "topology_index": topology_index,
                "n_taxa": len(taxa),
                "n_U": int((states == 0).sum()),
                "n_D": int((states == 1).sum()),
                **row,
            })
    frame = pd.DataFrame(rows)
    summary = {
        "contract_version": "fdt4_branchwise_niche_transition_concordance_v2",
        "method_recovery_note": "v1 was frozen as a result JSON without executable source; v2 implements the method declared in that contract and freezes all previously unstated computational choices",
        "taxa": taxa,
        "n_taxa": len(taxa),
        "n_U": int((states == 0).sum()),
        "n_D": int((states == 1).sum()),
        "min_environment_complete_occurrences_per_taxon": min_n,
        "topologies": nonrejected_count,
        "axes": axes,
        "permutations_per_topology": permutations,
        "base_seed": seed,
        "permutation_p": "two-sided absolute directional statistic with plus-one correction",
        "edge_transition_probability": "joint parent-child posterior under a refitted symmetric two-state CTMC with flat root prior",
        "continuous_reconstruction": "Brownian squared-change reconstruction on the pruned relative-branch-length tree",
        "claim_boundary": "Exploratory present-day branchwise concordance. This does not date transitions, reconstruct historical range, validate same-voucher orientation, demonstrate convergence/adaptation, or identify ecological causation.",
    }
    return frame, summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--occurrences", type=Path, nargs="+", required=True)
    parser.add_argument("--orientation", type=Path, required=True)
    parser.add_argument("--au-trees", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--nonrejected-count", type=int, default=6)
    parser.add_argument("--min-n", type=int, default=10)
    parser.add_argument("--axes", nargs="+", default=["chelsa_bio15", "chelsa_bio01"])
    parser.add_argument("--permutations", type=int, default=499)
    parser.add_argument("--seed", type=int, default=20260825)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    frame, summary = analyze(
        args.occurrences, args.orientation, args.au_trees,
        nonrejected_count=args.nonrejected_count,
        min_n=args.min_n,
        axes=args.axes,
        permutations=args.permutations,
        seed=args.seed,
    )
    args.out_dir.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.out_dir / "fdt4_branchwise_niche_transition_by_topology_v2.csv", index=False)
    ranges = {}
    for axis, group in frame.groupby("axis"):
        ranges[axis] = {
            "directional_shift_sd_range": [float(group["directional_shift_sd"].min()), float(group["directional_shift_sd"].max())],
            "two_sided_permutation_p_range": [float(group["two_sided_permutation_p"].min()), float(group["two_sided_permutation_p"].max())],
            "expected_orientation_transitions_range": [float(group["expected_orientation_transitions"].min()), float(group["expected_orientation_transitions"].max())],
        }
    summary["results_across_topologies"] = ranges
    summary["inputs"] = {
        "occurrences": [{"path": path.as_posix(), "sha256": sha256(path)} for path in args.occurrences],
        "orientation": {"path": args.orientation.as_posix(), "sha256": sha256(args.orientation)},
        "au_trees": {"path": args.au_trees.as_posix(), "sha256": sha256(args.au_trees)},
    }
    (args.out_dir / "fdt4_branchwise_niche_transition_concordance_v2.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
