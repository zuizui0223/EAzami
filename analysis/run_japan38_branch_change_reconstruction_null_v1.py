#!/usr/bin/env python3
"""Structure-aware null for cross-trait continuous branch-change coordination.

Unlike the earlier branch-value permutation, this null independently permutes tip
phenotype assignments for each continuous unit and then reruns the same Brownian
conditional ancestral reconstruction. It therefore preserves common tree geometry
and reconstruction leverage while destroying cross-trait concordance of tip labels.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata

import run_japan38_all_continuous_history_v1 as hist

EXPECTED_OBSERVED = 0.40800627943485085


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--bridge", type=Path, required=True)
    p.add_argument("--tree", type=Path, required=True)
    p.add_argument("--concept-map", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--null-out", type=Path, required=True)
    p.add_argument("--threshold", type=int, default=2)
    p.add_argument("--permutations", type=int, default=9999)
    p.add_argument("--seed", type=int, default=20260827)
    return p.parse_args()


def conditional_state_weights(tree, ids: list[str]):
    """Return linear weights mapping tip values to BM conditional node states."""
    ids = list(ids)
    tips = {t.name: t for t in tree.get_terminals()}
    C, _ = hist.base.covariance_matrix(tree, ids)
    inv = np.linalg.pinv(C)
    one = np.ones(len(ids), dtype=float)
    mu_w = (one @ inv) / float(one @ inv @ one)

    raw_diag = np.asarray([float(tree.distance(tree.root, tips[mid])) for mid in ids], float)
    scale = float(np.median(raw_diag))
    if not math.isfinite(scale) or scale <= 0:
        raise ValueError("invalid Brownian covariance scale")

    nodes = list(tree.find_clades(order="preorder"))
    node_index = {node: i for i, node in enumerate(nodes)}
    weights = np.zeros((len(nodes), len(ids)), dtype=float)
    id_index = {mid: i for i, mid in enumerate(ids)}

    for node in nodes:
        i = node_index[node]
        if node is tree.root:
            weights[i] = mu_w
        elif node.is_terminal():
            if node.name not in id_index:
                raise ValueError(f"unexpected terminal {node.name}")
            weights[i, id_index[node.name]] = 1.0
        else:
            cov = np.asarray(
                [hist.shared_depth(tree, node, tips[mid]) / scale for mid in ids],
                dtype=float,
            )
            a = cov @ inv
            weights[i] = a + (1.0 - float(a @ one)) * mu_w

    branches = []
    for parent in nodes:
        for child in parent.clades:
            bl = float(child.branch_length or 0.0)
            if bl <= 0:
                raise ValueError("reconstruction-null analysis requires positive branch lengths")
            branches.append((node_index[parent], node_index[child], bl))
    return weights, branches


def scalar_magnitudes(weights, branches, y: np.ndarray) -> np.ndarray:
    states = weights @ np.asarray(y, float)
    return np.asarray(
        [abs(states[c] - states[p]) / math.sqrt(bl) for p, c, bl in branches],
        float,
    )


def hue_magnitudes(weights, branches, paired: np.ndarray) -> np.ndarray:
    paired = np.asarray(paired, float)
    if paired.ndim != 2 or paired.shape[1] != 2:
        raise ValueError("hue assignment must be n_tip x 2 sine/cosine pairs")
    sin_states = weights @ paired[:, 0]
    cos_states = weights @ paired[:, 1]
    out = []
    for p, c, bl in branches:
        vp = np.asarray([sin_states[p], cos_states[p]], float)
        vc = np.asarray([sin_states[c], cos_states[c]], float)
        npv = float(np.linalg.norm(vp))
        ncv = float(np.linalg.norm(vc))
        if npv <= 1e-12 or ncv <= 1e-12:
            raise ValueError("undefined reconstructed hue vector")
        out.append(float(np.linalg.norm(vp / npv - vc / ncv)) / math.sqrt(bl))
    return np.asarray(out, float)


def mean_pairwise_spearman(branch_by_unit: np.ndarray) -> float:
    x = np.asarray(branch_by_unit, float)
    if x.ndim != 2 or x.shape[1] < 2:
        raise ValueError("expected branch x unit matrix")
    ranks = rankdata(x, axis=0, method="average")
    corr = np.corrcoef(ranks, rowvar=False)
    upper = corr[np.triu_indices(corr.shape[0], 1)]
    if np.any(~np.isfinite(upper)):
        raise ValueError("non-finite pairwise branch-change correlation")
    return float(np.mean(upper))


def input_assignments(bridge: pd.DataFrame, ids: list[str], threshold: int):
    scalar = {}
    for endpoint in hist.PRIMARY_SCALAR_UNITS:
        raw = hist.values_for_endpoint(bridge, endpoint, threshold)
        vals = {mid: raw[mid] for mid in ids}
        z = hist.zscore(vals)
        scalar[endpoint] = np.asarray([z[mid] for mid in ids], float)

    sin_raw = hist.values_for_endpoint(bridge, hist.HUE_SIN, threshold)
    cos_raw = hist.values_for_endpoint(bridge, hist.HUE_COS, threshold)
    hue = np.asarray([[sin_raw[mid], cos_raw[mid]] for mid in ids], float)
    return scalar, hue


def branch_matrix(weights, branches, scalar, hue) -> np.ndarray:
    cols = []
    for unit in hist.PRIMARY_UNITS:
        if unit == hist.HUE_UNIT:
            cols.append(hue_magnitudes(weights, branches, hue))
        else:
            cols.append(scalar_magnitudes(weights, branches, scalar[unit]))
    return np.column_stack(cols)


def quantile_summary(values: np.ndarray) -> dict:
    a = np.asarray(values, float)
    return {
        "n": int(len(a)),
        "mean": float(np.mean(a)),
        "median": float(np.median(a)),
        "q01": float(np.quantile(a, 0.01)),
        "q05": float(np.quantile(a, 0.05)),
        "q95": float(np.quantile(a, 0.95)),
        "q99": float(np.quantile(a, 0.99)),
        "min": float(np.min(a)),
        "max": float(np.max(a)),
    }


def compute_reconstruction_null(
    bridge: pd.DataFrame,
    tree_path: Path,
    cmap: dict[str, list[str]],
    allowed: dict[str, bool],
    threshold: int,
    permutations: int,
    seed: int,
    *,
    expected_common_concepts: int | None = None,
    expected_branches: int | None = None,
    expected_observed: float | None = None,
) -> tuple[dict, np.ndarray]:
    ids = hist.common_primary_ids(bridge, threshold)
    if expected_common_concepts is not None and len(ids) != expected_common_concepts:
        raise ValueError(
            f"contract expects exactly {expected_common_concepts} common concepts, found {len(ids)}"
        )
    tree = hist.load_concept_tree(tree_path, cmap, allowed, ids)
    weights, branches = conditional_state_weights(tree, ids)
    if expected_branches is not None and len(branches) != expected_branches:
        raise ValueError(f"contract expects {expected_branches} branches, found {len(branches)}")

    scalar, hue = input_assignments(bridge, ids, threshold)
    observed_matrix = branch_matrix(weights, branches, scalar, hue)
    observed = mean_pairwise_spearman(observed_matrix)
    if expected_observed is not None and abs(observed - expected_observed) > 1e-10:
        raise ValueError(
            f"observed statistic drifted from frozen analysis: {observed} vs {expected_observed}"
        )

    rng = np.random.default_rng(seed)
    null = np.empty(permutations, dtype=float)
    n = len(ids)
    for i in range(permutations):
        perm_scalar = {
            unit: values[rng.permutation(n)]
            for unit, values in scalar.items()
        }
        perm_hue = hue[rng.permutation(n), :]
        matrix = branch_matrix(weights, branches, perm_scalar, perm_hue)
        null[i] = mean_pairwise_spearman(matrix)

    exceed = int(np.sum(null >= observed - 1e-15))
    p = float((1 + exceed) / (permutations + 1))
    null_summary = quantile_summary(null)
    empirical_percentile = float(
        (np.sum(null < observed) + 0.5 * np.sum(null == observed)) / len(null)
    )
    decision = "PASS" if p < 0.05 else "FAIL"
    result = {
        "contract_version": "japan38_branch_change_reconstruction_null_v1",
        "status": "outcome_frozen",
        "threshold": threshold,
        "concept_ids": ids,
        "common_concepts": len(ids),
        "branches": len(branches),
        "units": hist.PRIMARY_UNITS,
        "permutations": permutations,
        "seed": seed,
        "observed_global_mean_pairwise_branch_change_rho": observed,
        "null": null_summary,
        "observed_minus_null_median": float(observed - null_summary["median"]),
        "observed_empirical_percentile": empirical_percentile,
        "one_sided_reconstruction_null_p": p,
        "null_exceedances": exceed,
        "decision": decision,
        "pass_rule": "one_sided_reconstruction_null_p < 0.05",
        "null_definition": (
            "independent tip-label permutation for every scalar phenotype; paired sine/cosine "
            "hue vectors permuted together; each permutation reruns the same BM conditional "
            "ancestral reconstruction on the same substitution-length phylogram"
        ),
        "claim_boundary": (
            "A PASS establishes excess shared branch-localization information beyond common "
            "tree/reconstruction geometry. It does not establish shared genetics, development, "
            "selection, adaptation, convergence, absolute timing, or evolutionary rate."
        ),
    }
    return result, null


def main() -> int:
    a = parse_args()
    if a.permutations != 9999:
        raise ValueError("v1 contract fixes permutations at exactly 9999")
    if a.threshold != 2:
        raise ValueError("v1 contract fixes the common-panel threshold at 2")

    bridge = hist.read_bridge(a.bridge)
    cmap, allowed = hist.base.read_concept_map(a.concept_map)
    result, null = compute_reconstruction_null(
        bridge,
        a.tree,
        cmap,
        allowed,
        a.threshold,
        a.permutations,
        a.seed,
        expected_common_concepts=8,
        expected_branches=14,
        expected_observed=EXPECTED_OBSERVED,
    )

    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    a.null_out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"permutation_index": np.arange(a.permutations), "null_global_mean_rho": null}).to_csv(
        a.null_out, index=False
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
