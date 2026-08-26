#!/usr/bin/env python3
"""Continuous-colour phylogenetic pilot on the frozen Japan38 compatibility tree.

This is deliberately a *continuous* diagnostic. It never converts image-derived
lightness/chroma/hue into C/W states and never reports transition counts.

For each evidence-depth subset, the script:
  1. prunes the frozen Japan38 ML tree to exact concept-level colour tips;
  2. fits Pagel's lambda under a Brownian covariance on ML branch lengths for
     L*, chroma, hue-sin and hue-cos separately;
  3. calculates a label-permutation diagnostic relating patristic distance to
     pairwise trait difference;
  4. treats circular hue separately with normalized sin/cos chord distance.

The tree is a compatibility phylogram, not a dated tree. Therefore lambda and
pairwise-distance diagnostics are evidence about phylogenetic structure only,
not evolutionary rates or timing. Heterogeneous image replication is handled
by explicit evidence-depth subsets rather than pseudo-precision weighting.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
from pathlib import Path

import numpy as np
from Bio import Phylo
from scipy.optimize import minimize_scalar
from scipy.stats import spearmanr

METRICS = (
    "corolla_lab_lightness_species_median",
    "corolla_lab_chroma_species_median",
    "corolla_hue_sin_species_median",
    "corolla_hue_cos_species_median",
)
SUBSET_THRESHOLDS = (1, 5, 10)


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as h:
        return list(csv.DictReader(h))


def read_concept_map(path: Path):
    rows = read_csv(path)
    if len(rows) != 38:
        raise ValueError(f"expected 38 concepts, found {len(rows)}")
    cmap = {
        r["paper_japan_member_id"]: [x for x in r["tip_ids"].split("|") if x]
        for r in rows
    }
    allowed = {
        r["paper_japan_member_id"]: (
            (r.get("trait_asr_primary_allowed") or "true").strip().lower() != "false"
        )
        for r in rows
    }
    return cmap, allowed


def read_colour_bridge(path: Path):
    rows = read_csv(path)
    by = {}
    for row in rows:
        mid = row["paper_japan_member_id"]
        if mid in by:
            raise ValueError(f"duplicate colour concept {mid}")
        parsed = dict(row)
        parsed["n_colour_usable_observations"] = int(row["n_colour_usable_observations"])
        for metric in METRICS:
            parsed[metric] = float(row[metric])
        by[mid] = parsed
    if len(by) != 14:
        raise ValueError(f"expected frozen exact colour bridge of 14 concepts, found {len(by)}")
    return by


def _validate_raw_tree(tree, cmap):
    names = {t.name for t in tree.get_terminals()}
    expected = {tip for tips in cmap.values() for tip in tips} | {"OUTGROUP_saff"}
    if names != expected:
        raise ValueError(
            f"tree tip mismatch missing={sorted(expected-names)} extra={sorted(names-expected)}"
        )
    tree.root_with_outgroup("OUTGROUP_saff")


def load_colour_concept_tree(tree_path: Path, cmap, allowed, colour_ids):
    tree = Phylo.read(str(tree_path), "newick")
    _validate_raw_tree(tree, cmap)

    # Replicated JPN_20 has no exact colour row. Its two non-monophyletic biological
    # tips are therefore pruned rather than collapsed.
    replicated = [(mid, tips) for mid, tips in cmap.items() if len(tips) > 1]
    if replicated != [("JPN_20", cmap["JPN_20"])]:
        raise ValueError(f"unexpected replicated concepts: {replicated}")
    if "JPN_20" in colour_ids:
        raise ValueError("JPN_20 must not enter the exact continuous-colour bridge")
    for tip in cmap["JPN_20"]:
        tree.prune(target=tip)

    reverse = {}
    for mid, tips in cmap.items():
        if len(tips) != 1:
            continue
        tip = tips[0]
        if not allowed.get(mid, True):
            if tip in {t.name for t in tree.get_terminals()}:
                tree.prune(target=tip)
            continue
        reverse[tip] = mid
    for tip in tree.get_terminals():
        if tip.name in reverse:
            tip.name = reverse[tip.name]

    tree.prune(target="OUTGROUP_saff")
    for tip in list(tree.get_terminals()):
        if tip.name not in colour_ids:
            tree.prune(target=tip)

    final = {t.name for t in tree.get_terminals()}
    if final != set(colour_ids):
        raise ValueError(
            f"colour-tree tip mismatch missing={sorted(set(colour_ids)-final)} "
            f"extra={sorted(final-set(colour_ids))}"
        )
    if any(t.branch_length is None for t in tree.find_clades() if t is not tree.root):
        raise ValueError("continuous pilot requires branch lengths on the ML tree")
    return tree


def prune_to_ids(tree, ids):
    # Round-trip through Newick to avoid mutating the original analysis tree.
    from io import StringIO
    buf = StringIO()
    Phylo.write(tree, buf, "newick")
    buf.seek(0)
    out = Phylo.read(buf, "newick")
    for tip in list(out.get_terminals()):
        if tip.name not in ids:
            out.prune(target=tip)
    final = {t.name for t in out.get_terminals()}
    if final != set(ids):
        raise ValueError("subset pruning failed")
    return out


def covariance_matrix(tree, ids):
    ids = list(ids)
    tips = {t.name: t for t in tree.get_terminals()}
    n = len(ids)
    C = np.zeros((n, n), dtype=float)
    for i, a in enumerate(ids):
        C[i, i] = float(tree.distance(tree.root, tips[a]))
        for j in range(i):
            b = ids[j]
            mrca = tree.common_ancestor(tips[a], tips[b])
            shared = float(tree.distance(tree.root, mrca))
            C[i, j] = C[j, i] = shared
    diag = np.diag(C)
    if np.any(~np.isfinite(C)) or np.any(diag <= 0):
        raise ValueError(f"invalid Brownian covariance diagonal: {diag}")
    scale = float(np.median(diag))
    if scale <= 0:
        raise ValueError("invalid covariance scale")
    return C / scale, scale


def gls_lambda_loglik(y, C, lam):
    y = np.asarray(y, dtype=float)
    n = len(y)
    V = np.array(C, dtype=float, copy=True)
    off = ~np.eye(n, dtype=bool)
    V[off] *= float(lam)
    # Tiny numerical nugget only; this is not a biological residual model.
    V[np.diag_indices(n)] += 1e-10
    sign, logdet = np.linalg.slogdet(V)
    if sign <= 0 or not math.isfinite(float(logdet)):
        return -math.inf, None, None
    try:
        inv = np.linalg.inv(V)
    except np.linalg.LinAlgError:
        return -math.inf, None, None
    one = np.ones(n)
    denom = float(one @ inv @ one)
    if denom <= 0:
        return -math.inf, None, None
    mu = float((one @ inv @ y) / denom)
    r = y - mu
    sigma2 = float((r @ inv @ r) / n)
    sigma2 = max(sigma2, 1e-12)
    ll = -0.5 * (
        n * math.log(2.0 * math.pi)
        + n * math.log(sigma2)
        + float(logdet)
        + n
    )
    return float(ll), mu, sigma2


def fit_pagel_lambda(y, C):
    def objective(lam):
        ll, _, _ = gls_lambda_loglik(y, C, lam)
        return -ll if math.isfinite(ll) else 1e100

    opt = minimize_scalar(objective, bounds=(0.0, 1.0), method="bounded", options={"xatol": 1e-6})
    candidates = [0.0, 1.0]
    if opt.success:
        candidates.append(float(opt.x))
    # Grid safety net for boundary/flat likelihoods.
    candidates.extend(float(x) for x in np.linspace(0.0, 1.0, 101))
    scored = []
    for lam in candidates:
        ll, mu, sigma2 = gls_lambda_loglik(y, C, lam)
        if math.isfinite(ll):
            scored.append((ll, lam, mu, sigma2))
    if not scored:
        raise ValueError("could not evaluate Pagel lambda likelihood")
    ll, lam, mu, sigma2 = max(scored, key=lambda x: x[0])
    ll0, _, _ = gls_lambda_loglik(y, C, 0.0)
    ll1, _, _ = gls_lambda_loglik(y, C, 1.0)
    return {
        "lambda_mle": float(lam),
        "log_likelihood_mle": float(ll),
        "gls_mean": float(mu),
        "brownian_scale_parameter": float(sigma2),
        "log_likelihood_lambda0": float(ll0),
        "log_likelihood_lambda1": float(ll1),
        "delta_loglik_vs_lambda0": float(ll - ll0),
        "delta_loglik_vs_lambda1": float(ll - ll1),
        "interpretation_boundary": "Phylogenetic-structure diagnostic on substitution-length ML tree; not an evolutionary-rate or dating estimate.",
    }


def patristic_vector(tree, ids):
    tips = {t.name: t for t in tree.get_terminals()}
    pairs = []
    dist = []
    for i, a in enumerate(ids):
        for j in range(i):
            b = ids[j]
            pairs.append((j, i))
            dist.append(float(tree.distance(tips[a], tips[b])))
    return pairs, np.asarray(dist, dtype=float)


def _rho(x, y):
    if len(x) < 3 or np.allclose(x, x[0]) or np.allclose(y, y[0]):
        return math.nan
    return float(spearmanr(x, y).statistic)


def pairwise_signal(tree, ids, values, permutations, seed):
    ids = list(ids)
    y = np.asarray([values[mid] for mid in ids], dtype=float)
    pairs, pdist = patristic_vector(tree, ids)

    def trait_dist(v):
        return np.asarray([abs(float(v[i] - v[j])) for j, i in pairs], dtype=float)

    observed = _rho(pdist, trait_dist(y))
    rng = random.Random(seed)
    null = []
    if math.isfinite(observed):
        for _ in range(permutations):
            z = list(y)
            rng.shuffle(z)
            rr = _rho(pdist, trait_dist(np.asarray(z, dtype=float)))
            if math.isfinite(rr):
                null.append(rr)
    p = None
    if null:
        p = (1 + sum(r >= observed for r in null)) / (len(null) + 1)
    return {
        "spearman_patristic_vs_absolute_trait_difference": observed,
        "one_sided_label_permutation_p_positive_structure": p,
        "permutations_requested": permutations,
        "permutations_usable": len(null),
        "direction": "positive rho means more-distant taxa tend to differ more in the continuous trait",
    }


def normalized_hue_vector(row):
    s = float(row["corolla_hue_sin_species_median"])
    c = float(row["corolla_hue_cos_species_median"])
    norm = math.hypot(s, c)
    if norm <= 1e-12:
        raise ValueError(f"undefined hue vector for {row['paper_japan_member_id']}")
    return np.array([s / norm, c / norm], dtype=float)


def circular_hue_pairwise_signal(tree, ids, bridge, permutations, seed):
    ids = list(ids)
    vecs = [normalized_hue_vector(bridge[mid]) for mid in ids]
    pairs, pdist = patristic_vector(tree, ids)

    def chord(vs):
        return np.asarray([float(np.linalg.norm(vs[i] - vs[j])) for j, i in pairs])

    observed = _rho(pdist, chord(vecs))
    rng = random.Random(seed)
    null = []
    if math.isfinite(observed):
        for _ in range(permutations):
            z = list(vecs)
            rng.shuffle(z)
            rr = _rho(pdist, chord(z))
            if math.isfinite(rr):
                null.append(rr)
    p = None
    if null:
        p = (1 + sum(r >= observed for r in null)) / (len(null) + 1)
    return {
        "spearman_patristic_vs_hue_chord_distance": observed,
        "one_sided_label_permutation_p_positive_structure": p,
        "permutations_requested": permutations,
        "permutations_usable": len(null),
        "hue_distance": "Euclidean chord distance after normalizing species median sin/cos to the unit circle",
    }


def summarize_subset(full_tree, ids, bridge, permutations, seed):
    ids = sorted(ids)
    tree = prune_to_ids(full_tree, ids)
    C, covariance_scale = covariance_matrix(tree, ids)
    out = {
        "n_concepts": len(ids),
        "paper_japan_member_ids": ids,
        "n_colour_usable_observations": {
            mid: bridge[mid]["n_colour_usable_observations"] for mid in ids
        },
        "ml_tree_median_root_to_tip_length_before_covariance_scaling": covariance_scale,
        "metrics": {},
    }
    for k, metric in enumerate(METRICS):
        vals = {mid: bridge[mid][metric] for mid in ids}
        y = [vals[mid] for mid in ids]
        out["metrics"][metric] = {
            "range": [float(min(y)), float(max(y))],
            "pagel_lambda": fit_pagel_lambda(y, C),
            "pairwise_signal": pairwise_signal(
                tree, ids, vals, permutations, seed + 1000 * (k + 1)
            ),
        }
    out["circular_hue_pairwise_signal"] = circular_hue_pairwise_signal(
        tree, ids, bridge, permutations, seed + 9000
    )
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--tree", type=Path, required=True)
    p.add_argument("--concept-map", type=Path, required=True)
    p.add_argument("--colour-bridge", type=Path, required=True)
    p.add_argument("--permutations", type=int, default=999)
    p.add_argument("--seed", type=int, default=20260826)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    if a.permutations < 0:
        raise ValueError("permutations must be non-negative")

    cmap, allowed = read_concept_map(a.concept_map)
    bridge = read_colour_bridge(a.colour_bridge)
    colour_ids = set(bridge)
    if "JPN_31" in colour_ids or "JPN_20" in colour_ids or "JPN_21" in colour_ids:
        raise ValueError("conflicted/variety sensitivity concepts must not enter exact colour tree")
    full_tree = load_colour_concept_tree(a.tree, cmap, allowed, colour_ids)

    subsets = {}
    for threshold in SUBSET_THRESHOLDS:
        ids = {
            mid for mid, row in bridge.items()
            if row["n_colour_usable_observations"] >= threshold
        }
        if len(ids) < 5:
            continue
        subsets[f"n_colour_usable_ge_{threshold}"] = summarize_subset(
            full_tree, ids, bridge, a.permutations, a.seed + threshold
        )

    result = {
        "contract_version": "japan38_colour_continuous_history_pilot_v1",
        "tree_contract": {
            "source": "frozen Japan38 Comp1061 compatibility ML tree",
            "branch_length_semantics": "substitution-length phylogram; not dated time",
            "exact_colour_concepts": len(colour_ids),
            "excluded_by_colour_contract": ["JPN_20", "JPN_21", "JPN_31"],
        },
        "trait_contract": {
            "continuous_only": True,
            "discrete_colour_state_frozen": False,
            "metrics": list(METRICS),
            "hue_rule": "fit sin/cos separately and use normalized sin/cos chord distance for circular pairwise sensitivity; do not model raw degrees linearly",
            "evidence_depth_rule": "repeat diagnostics at >=1, >=5 and >=10 colour-usable observations; do not precision-weight sparse image medians as if they were population means",
        },
        "subsets": subsets,
        "claim_boundary": (
            "Pilot evidence about continuous phylogenetic structure only. The compatibility tree is not dated; "
            "lambda is not an evolutionary rate. Image-derived species medians do not establish fixed population colour. "
            "No C/W discretization, ancestral-colour claim, transition count, loss/regain direction, adaptive convergence, or H2/H3 module-overlap claim is made here."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
