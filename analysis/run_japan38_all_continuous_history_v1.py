#!/usr/bin/env python3
"""Compare primary continuous capitulum phenotypes across Japan38 evolutionary history.

Primary estimand: phenotype × phylogenetic history, not phenotype × function.

The script consumes the exact-concept bridge exported from the frozen Azami GEB-v2
continuous-trait artifact. Continuous traits are never discretized. The main evidence
threshold requires >=2 frozen image observations per concept; >=5 is a high-depth
sensitivity. Candidate involucre/armature endpoints are not promoted when they fail
minimum-taxon coverage.

Outputs include:
- unit-specific Pagel-lambda diagnostics for scalar traits;
- two-sided label-permutation tests relating patristic distance to phenotype distance;
- circular-hue chord-distance diagnostics;
- BH correction across eight primary inferential units;
- a common-concept branch-change analysis testing whether standardized changes in
  different phenotype units concentrate on the same phylogenetic branches.

Branch lengths are substitutions/site. Branch-change scaling is therefore a
phylogram-normalized structural diagnostic, not an evolutionary rate per unit time.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from Bio import Phylo
from scipy.stats import spearmanr

import run_japan38_colour_continuous_history_pilot_v1 as base

PRIMARY_SCALAR_UNITS = [
    "orientation_image_vertical_angle",
    "corolla_lab_lightness",
    "corolla_lab_chroma",
    "capitulum_outline_aspect_ratio",
    "capitulum_outline_circularity",
    "capitulum_outline_solidity",
    "capitulum_width_profile_cv",
]
HUE_SIN = "corolla_hue_sin"
HUE_COS = "corolla_hue_cos"
HUE_UNIT = "corolla_hue"
PRIMARY_UNITS = [
    "orientation_image_vertical_angle",
    "corolla_lab_lightness",
    "corolla_lab_chroma",
    HUE_UNIT,
    "capitulum_outline_aspect_ratio",
    "capitulum_outline_circularity",
    "capitulum_outline_solidity",
    "capitulum_width_profile_cv",
]
UNIT_MODULE = {
    "orientation_image_vertical_angle": "orientation",
    "corolla_lab_lightness": "colour",
    "corolla_lab_chroma": "colour",
    HUE_UNIT: "colour",
    "capitulum_outline_aspect_ratio": "shape",
    "capitulum_outline_circularity": "shape",
    "capitulum_outline_solidity": "shape",
    "capitulum_width_profile_cv": "shape",
}
THRESHOLDS = (2, 5)
MIN_TAXA = 6
PERMUTATIONS = 10000
CSV_FLOAT_FORMAT = "%.12g"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--bridge", type=Path, required=True)
    p.add_argument("--tree", type=Path, required=True)
    p.add_argument("--concept-map", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--permutations", type=int, default=PERMUTATIONS)
    p.add_argument("--seed", type=int, default=20260827)
    p.add_argument(
        "--exclude-concept",
        action="append",
        default=[],
        help="Concept ID to exclude for a separately declared provenance sensitivity; repeatable.",
    )
    return p.parse_args()


def read_bridge(path: Path) -> pd.DataFrame:
    x = pd.read_csv(path, low_memory=False)
    required = {
        "paper_japan_member_id", "paper_taxon_concept", "endpoint_id", "module",
        "analysis_tier", "n_observations", "value_median",
    }
    missing = sorted(required.difference(x.columns))
    if missing:
        raise ValueError(f"bridge missing columns: {missing}")
    x["n_observations"] = pd.to_numeric(x["n_observations"], errors="raise").astype(int)
    x["value_median"] = pd.to_numeric(x["value_median"], errors="raise")
    if x.duplicated(["paper_japan_member_id", "endpoint_id"]).any():
        raise ValueError("bridge has duplicate concept/endpoint rows")
    return x


def apply_concept_exclusions(bridge: pd.DataFrame, exclusions: list[str]) -> pd.DataFrame:
    clean = sorted({str(x).strip() for x in exclusions if str(x).strip()})
    if not clean:
        return bridge.copy()
    available = set(bridge["paper_japan_member_id"].astype(str))
    missing = sorted(set(clean).difference(available))
    if missing:
        raise ValueError(f"requested concept exclusions absent from bridge: {missing}")
    return bridge.loc[~bridge["paper_japan_member_id"].astype(str).isin(clean)].copy()


def load_concept_tree(tree_path: Path, cmap: dict[str, list[str]], allowed: dict[str, bool], ids: list[str]):
    ids = list(ids)
    tree = Phylo.read(str(tree_path), "newick")
    base._validate_raw_tree(tree, cmap)

    terminals = {t.name for t in tree.get_terminals()}
    for mid, tips in cmap.items():
        if len(tips) > 1:
            if mid in ids:
                raise ValueError(f"replicated non-monophyly-sensitive concept {mid} cannot enter continuous primary history")
            for tip in tips:
                if tip in terminals:
                    tree.prune(target=tip)
                    terminals = {t.name for t in tree.get_terminals()}

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

    if "OUTGROUP_saff" in {t.name for t in tree.get_terminals()}:
        tree.prune(target="OUTGROUP_saff")
    for tip in list(tree.get_terminals()):
        if tip.name not in ids:
            tree.prune(target=tip)
    final = {t.name for t in tree.get_terminals()}
    if final != set(ids):
        raise ValueError(f"continuous-tree tip mismatch missing={sorted(set(ids)-final)} extra={sorted(final-set(ids))}")
    if any(t.branch_length is None for t in tree.find_clades() if t is not tree.root):
        raise ValueError("continuous history requires branch lengths")
    return tree


def values_for_endpoint(bridge: pd.DataFrame, endpoint: str, threshold: int) -> dict[str, float]:
    g = bridge[(bridge["endpoint_id"] == endpoint) & (bridge["n_observations"] >= threshold)]
    return dict(zip(g["paper_japan_member_id"], g["value_median"].astype(float)))


def hue_values(bridge: pd.DataFrame, threshold: int) -> dict[str, np.ndarray]:
    s = values_for_endpoint(bridge, HUE_SIN, threshold)
    c = values_for_endpoint(bridge, HUE_COS, threshold)
    ids = sorted(set(s) & set(c))
    out = {}
    for mid in ids:
        v = np.array([s[mid], c[mid]], float)
        norm = float(np.linalg.norm(v))
        if norm <= 1e-12:
            continue
        out[mid] = v / norm
    return out


def circular_rho(tree, ids: list[str], vectors: list[np.ndarray]) -> float:
    pairs, pdist = base.patristic_vector(tree, ids)
    tdist = np.asarray([float(np.linalg.norm(vectors[i] - vectors[j])) for j, i in pairs])
    return base._rho(pdist, tdist)


def circular_signal(tree, ids: list[str], vectors_by_id: dict[str, np.ndarray], permutations: int, seed: int) -> dict:
    ids = list(ids)
    vectors = [vectors_by_id[mid] for mid in ids]
    observed = circular_rho(tree, ids, vectors)
    statistic = lambda assigned: circular_rho(tree, ids, list(assigned))
    null, mode, exact, total = base.build_permutation_null(vectors, statistic, permutations, seed)
    p_pos, p_neg, p_two = base.permutation_tails(observed, null, exact)

    loo = {}
    for omitted in ids:
        keep = [mid for mid in ids if mid != omitted]
        if len(keep) < 4:
            continue
        sub = base.prune_to_ids(tree, keep)
        loo[omitted] = circular_rho(sub, keep, [vectors_by_id[mid] for mid in keep])
    vals = [v for v in loo.values() if math.isfinite(v)]
    return {
        "spearman_patristic_vs_trait_distance": observed,
        "p_positive": p_pos,
        "p_negative": p_neg,
        "p_two_sided": p_two,
        "permutation_mode": mode,
        "permutations_usable": len(null),
        "permutations_requested_or_exact_total": total,
        "loo_min_rho": min(vals) if vals else None,
        "loo_max_rho": max(vals) if vals else None,
        "loo_all_positive": bool(vals) and all(v > 0 for v in vals),
        "loo_all_negative": bool(vals) and all(v < 0 for v in vals),
    }


def bh(values: list[float]) -> list[float]:
    a = np.asarray(values, float)
    n = len(a)
    order = np.argsort(a)
    ranked = a[order]
    q = np.empty(n, float)
    running = 1.0
    for i in range(n - 1, -1, -1):
        rank = i + 1
        running = min(running, ranked[i] * n / rank)
        q[i] = running
    out = np.empty(n, float)
    out[order] = np.clip(q, 0, 1)
    return out.tolist()


def write_stable_csv(frame: pd.DataFrame, path: Path) -> None:
    """Serialize scientific floats without platform-specific tail digits."""
    frame.to_csv(path, index=False, float_format=CSV_FLOAT_FORMAT)


def scalar_unit_summary(bridge, tree_path, cmap, allowed, endpoint, threshold, permutations, seed):
    values = values_for_endpoint(bridge, endpoint, threshold)
    ids = sorted(values)
    if len(ids) < MIN_TAXA:
        return None
    tree = load_concept_tree(tree_path, cmap, allowed, ids)
    C, scale = base.covariance_matrix(tree, ids)
    lam = base.fit_pagel_lambda([values[mid] for mid in ids], C)
    sig = base.pairwise_signal(tree, ids, values, permutations, seed)
    return {
        "scope": f"nobs_ge_{threshold}",
        "threshold": threshold,
        "unit_id": endpoint,
        "module": UNIT_MODULE[endpoint],
        "unit_type": "scalar",
        "n_concepts": len(ids),
        "concept_ids": "|".join(ids),
        "lambda_mle": lam["lambda_mle"],
        "delta_loglik_vs_lambda0": lam["delta_loglik_vs_lambda0"],
        "delta_loglik_vs_lambda1": lam["delta_loglik_vs_lambda1"],
        "brownian_covariance_scale": scale,
        "rho_patristic_vs_trait_distance": sig["spearman_patristic_vs_absolute_trait_difference"],
        "p_positive": sig["one_sided_label_permutation_p_positive_structure"],
        "p_negative": sig["one_sided_label_permutation_p_negative_structure"],
        "p_two_sided": sig["two_sided_label_permutation_p"],
        "loo_min_rho": sig["leave_one_taxon_out"]["min_rho"],
        "loo_max_rho": sig["leave_one_taxon_out"]["max_rho"],
        "loo_all_positive": sig["leave_one_taxon_out"]["all_positive"],
        "loo_all_negative": sig["leave_one_taxon_out"]["all_negative"],
        "permutation_mode": sig["permutation_mode"],
    }


def hue_unit_summary(bridge, tree_path, cmap, allowed, threshold, permutations, seed):
    values = hue_values(bridge, threshold)
    ids = sorted(values)
    if len(ids) < MIN_TAXA:
        return None
    tree = load_concept_tree(tree_path, cmap, allowed, ids)
    sig = circular_signal(tree, ids, values, permutations, seed)
    return {
        "scope": f"nobs_ge_{threshold}",
        "threshold": threshold,
        "unit_id": HUE_UNIT,
        "module": "colour",
        "unit_type": "circular_chord",
        "n_concepts": len(ids),
        "concept_ids": "|".join(ids),
        "lambda_mle": np.nan,
        "delta_loglik_vs_lambda0": np.nan,
        "delta_loglik_vs_lambda1": np.nan,
        "brownian_covariance_scale": np.nan,
        "rho_patristic_vs_trait_distance": sig["spearman_patristic_vs_trait_distance"],
        "p_positive": sig["p_positive"],
        "p_negative": sig["p_negative"],
        "p_two_sided": sig["p_two_sided"],
        "loo_min_rho": sig["loo_min_rho"],
        "loo_max_rho": sig["loo_max_rho"],
        "loo_all_positive": sig["loo_all_positive"],
        "loo_all_negative": sig["loo_all_negative"],
        "permutation_mode": sig["permutation_mode"],
    }


def shared_depth(tree, left, right) -> float:
    mrca = tree.common_ancestor(left, right)
    return float(tree.distance(tree.root, mrca))


def bm_states(tree, ids: list[str], values_by_id: dict[str, float]) -> dict:
    ids = list(ids)
    tips = {t.name: t for t in tree.get_terminals()}
    C, _ = base.covariance_matrix(tree, ids)
    # base.covariance_matrix rescales C by median root-tip depth; that scalar cancels
    # in the conditional mean, so use it directly for numerical stability.
    y = np.asarray([values_by_id[mid] for mid in ids], float)
    inv = np.linalg.pinv(C)
    one = np.ones(len(ids))
    mu = float((one @ inv @ y) / (one @ inv @ one))

    # Recover the same scaling used in C so node-to-tip covariance is compatible.
    raw_diag = np.asarray([float(tree.distance(tree.root, tips[mid])) for mid in ids])
    scale = float(np.median(raw_diag))
    states = {tree.root: mu}
    for clade in tree.find_clades(order="preorder"):
        if clade is tree.root:
            continue
        if clade.is_terminal():
            states[clade] = float(values_by_id[clade.name])
            continue
        cov = []
        for mid in ids:
            cov.append(shared_depth(tree, clade, tips[mid]) / scale)
        states[clade] = float(mu + np.asarray(cov) @ inv @ (y - mu))
    return states


def zscore(values: dict[str, float]) -> dict[str, float]:
    ids = sorted(values)
    a = np.asarray([values[mid] for mid in ids], float)
    sd = float(np.std(a, ddof=1))
    if not math.isfinite(sd) or sd <= 1e-12:
        raise ValueError("cannot standardize constant trait")
    mean = float(np.mean(a))
    return {mid: (float(values[mid]) - mean) / sd for mid in ids}


def branch_ids(tree):
    clades = list(tree.find_clades(order="preorder"))
    labels = {}
    counter = 0
    for c in clades:
        if c.is_terminal():
            labels[c] = c.name
        else:
            labels[c] = f"NODE_{counter:03d}"
            counter += 1
    rows = []
    for parent in clades:
        for child in parent.clades:
            bl = float(child.branch_length or 0.0)
            rows.append((parent, child, f"{labels[parent]}->{labels[child]}", labels[parent], labels[child], bl))
    return rows


def common_primary_ids(bridge: pd.DataFrame, threshold: int) -> list[str]:
    sets = []
    for endpoint in [*PRIMARY_SCALAR_UNITS, HUE_SIN, HUE_COS]:
        vals = values_for_endpoint(bridge, endpoint, threshold)
        sets.append(set(vals))
    common = set.intersection(*sets)
    return sorted(common)


def branch_change_analysis(bridge, tree_path, cmap, allowed, threshold, permutations, seed):
    ids = common_primary_ids(bridge, threshold)
    if len(ids) < MIN_TAXA:
        raise ValueError(f"common primary continuous panel too small: {len(ids)}")
    tree = load_concept_tree(tree_path, cmap, allowed, ids)
    branches = branch_ids(tree)
    branch_frame = pd.DataFrame({
        "branch_id": [x[2] for x in branches],
        "parent_id": [x[3] for x in branches],
        "child_id": [x[4] for x in branches],
        "branch_length_substitutions_per_site": [x[5] for x in branches],
    })

    # Scalar units: absolute standardized BM conditional change / sqrt(branch length).
    for endpoint in PRIMARY_SCALAR_UNITS:
        raw = values_for_endpoint(bridge, endpoint, threshold)
        vals = {mid: raw[mid] for mid in ids}
        states = bm_states(tree, ids, zscore(vals))
        magnitudes = []
        for parent, child, *_rest, bl in branches:
            if bl <= 0:
                magnitudes.append(np.nan)
            else:
                magnitudes.append(abs(states[child] - states[parent]) / math.sqrt(bl))
        branch_frame[endpoint] = magnitudes

    # Circular hue: reconstruct sine/cosine components, normalize node vectors, then chord change.
    sin_raw = values_for_endpoint(bridge, HUE_SIN, threshold)
    cos_raw = values_for_endpoint(bridge, HUE_COS, threshold)
    sin_states = bm_states(tree, ids, {mid: sin_raw[mid] for mid in ids})
    cos_states = bm_states(tree, ids, {mid: cos_raw[mid] for mid in ids})
    hue_mag = []
    for parent, child, *_rest, bl in branches:
        if bl <= 0:
            hue_mag.append(np.nan)
            continue
        vp = np.array([sin_states[parent], cos_states[parent]], float)
        vc = np.array([sin_states[child], cos_states[child]], float)
        npv, ncv = float(np.linalg.norm(vp)), float(np.linalg.norm(vc))
        if npv <= 1e-12 or ncv <= 1e-12:
            hue_mag.append(np.nan)
        else:
            hue_mag.append(float(np.linalg.norm(vp / npv - vc / ncv)) / math.sqrt(bl))
    branch_frame[HUE_UNIT] = hue_mag

    unit_frame = branch_frame[PRIMARY_UNITS].copy()
    corr = unit_frame.corr(method="spearman")
    upper = corr.to_numpy(float)[np.triu_indices(len(PRIMARY_UNITS), 1)]
    observed_global = float(np.nanmean(upper))

    rng = np.random.default_rng(seed)
    null = []
    arr = unit_frame.to_numpy(float)
    for _ in range(permutations):
        p = arr.copy()
        for j in range(p.shape[1]):
            good = np.flatnonzero(np.isfinite(p[:, j]))
            p[good, j] = p[rng.permutation(good), j]
        pc = pd.DataFrame(p, columns=PRIMARY_UNITS).corr(method="spearman").to_numpy(float)
        null.append(float(np.nanmean(pc[np.triu_indices(len(PRIMARY_UNITS), 1)])))
    p_global = float((1 + sum(x >= observed_global for x in null)) / (len(null) + 1))

    def module_contrast(mapping):
        within, between = [], []
        for i, left in enumerate(PRIMARY_UNITS):
            for right in PRIMARY_UNITS[i + 1:]:
                v = float(corr.loc[left, right])
                (within if mapping[left] == mapping[right] else between).append(v)
        return float(np.nanmean(within) - np.nanmean(between)), float(np.nanmean(within)), float(np.nanmean(between))

    observed_contrast, within_mean, between_mean = module_contrast(UNIT_MODULE)
    labels = [UNIT_MODULE[u] for u in PRIMARY_UNITS]
    unique_perms = set(itertools.permutations(labels))
    null_contrast = []
    for perm in unique_perms:
        mapping = dict(zip(PRIMARY_UNITS, perm))
        null_contrast.append(module_contrast(mapping)[0])
    p_module = float(sum(x >= observed_contrast - 1e-15 for x in null_contrast) / len(null_contrast))

    matrix_rows = []
    for i, left in enumerate(PRIMARY_UNITS):
        for right in PRIMARY_UNITS[i + 1:]:
            matrix_rows.append({
                "left": left,
                "right": right,
                "left_module": UNIT_MODULE[left],
                "right_module": UNIT_MODULE[right],
                "spearman_branch_change_magnitude": float(corr.loc[left, right]),
            })

    summary = {
        "threshold": threshold,
        "common_concepts": len(ids),
        "concept_ids": ids,
        "branches": int(len(branch_frame)),
        "units": PRIMARY_UNITS,
        "global_mean_pairwise_branch_change_rho": observed_global,
        "global_shared_lability_permutation_p_positive": p_global,
        "within_module_mean_rho": within_mean,
        "between_module_mean_rho": between_mean,
        "within_minus_between_module_contrast": observed_contrast,
        "module_label_exact_permutation_p_positive": p_module,
        "module_label_permutations": len(unique_perms),
        "branch_change_definition": "absolute BM-conditional phenotype change standardized by tip SD (scalar units) or hue chord distance, divided by sqrt(substitution-length branch)",
        "claim_boundary": "Shared branch-change diagnostic only; substitutions/site are not absolute time, ancestral states are BM conditional expectations, and positive coupling would not prove genetic/developmental modularity or common selection.",
    }
    return branch_frame, pd.DataFrame(matrix_rows), summary


def main() -> int:
    a = parse_args()
    if a.permutations < 999:
        raise ValueError("permutations must be >=999")
    exclusions = sorted(set(a.exclude_concept))
    bridge = apply_concept_exclusions(read_bridge(a.bridge), exclusions)
    cmap, allowed = base.read_concept_map(a.concept_map)
    out = a.out_dir
    out.mkdir(parents=True, exist_ok=True)

    # Candidate continuous endpoints are coverage-audited but not silently promoted.
    candidate = bridge[bridge["analysis_tier"] == "candidate"]
    candidate_cov = (
        candidate.groupby(["endpoint_id", "module"])
        .apply(lambda g: pd.Series({
            "n1": int((g["n_observations"] >= 1).sum()),
            "n2": int((g["n_observations"] >= 2).sum()),
            "n5": int((g["n_observations"] >= 5).sum()),
        }), include_groups=False)
        .reset_index()
    )
    write_stable_csv(candidate_cov, out / "candidate_continuous_history_coverage.csv")

    rows = []
    for threshold in THRESHOLDS:
        for endpoint in PRIMARY_SCALAR_UNITS:
            r = scalar_unit_summary(
                bridge, a.tree, cmap, allowed, endpoint, threshold, a.permutations,
                a.seed + threshold * 100 + PRIMARY_SCALAR_UNITS.index(endpoint),
            )
            if r is not None:
                rows.append(r)
        r = hue_unit_summary(bridge, a.tree, cmap, allowed, threshold, a.permutations, a.seed + threshold * 100 + 99)
        if r is not None:
            rows.append(r)

    units = pd.DataFrame(rows)
    if units.empty:
        raise ValueError("no continuous primary unit passed minimum taxon coverage")
    for scope, idx in units.groupby("scope").groups.items():
        q = bh(units.loc[idx, "p_two_sided"].astype(float).tolist())
        units.loc[idx, "q_two_sided_bh"] = q
    units["history_support_class"] = np.where(
        units["q_two_sided_bh"].astype(float) < 0.05,
        np.where(units["rho_patristic_vs_trait_distance"].astype(float) > 0, "positive_phylogenetic_structure", "anti_phylogenetic_structure"),
        "two_sided_not_supported",
    )
    write_stable_csv(units, out / "continuous_primary_phylogenetic_structure_v1.csv")

    branch_frame, coupling, coupling_summary = branch_change_analysis(
        bridge, a.tree, cmap, allowed, threshold=2, permutations=a.permutations, seed=a.seed + 5000
    )
    write_stable_csv(branch_frame, out / "continuous_primary_branch_change_magnitudes_v1.csv")
    write_stable_csv(coupling, out / "continuous_primary_branch_change_coupling_v1.csv")
    (out / "continuous_primary_branch_change_summary_v1.json").write_text(
        json.dumps(coupling_summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    main_scope = units[units["threshold"] == 2].copy()
    sensitivity = units[units["threshold"] == 5].copy()
    report = {
        "contract_version": "japan38_all_continuous_history_v1",
        "primary_threshold_n_observations": 2,
        "high_depth_threshold_n_observations": 5,
        "minimum_taxa_per_unit": MIN_TAXA,
        "excluded_concepts": exclusions,
        "primary_units_expected": PRIMARY_UNITS,
        "primary_units_executed_n2": main_scope["unit_id"].tolist(),
        "primary_units_executed_n5": sensitivity["unit_id"].tolist(),
        "n2_history_classes": main_scope.groupby("history_support_class").size().to_dict(),
        "n5_history_classes": sensitivity.groupby("history_support_class").size().to_dict(),
        "candidate_endpoint_decision": "coverage_audit_only_not_promoted_to_phylogenetic_history",
        "branch_change_shared_lability": coupling_summary,
        "tree_semantics": "substitutions/site; not absolute time",
        "claim_boundary": (
            "Continuous phenotype phylogenetic-structure and branch-change diagnostics only. "
            "No functional interpretation, adaptation, absolute evolutionary rate, convergence, "
            "or unique generating mechanism is inferred."
        ),
    }
    (out / "japan38_all_continuous_history_summary_v1.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
