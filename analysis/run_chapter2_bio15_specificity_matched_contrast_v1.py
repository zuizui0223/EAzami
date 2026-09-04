#!/usr/bin/env python3
"""BIO15 specificity and phylogenetically matched opposite-state contrasts.

Post-result, fail-closed Chapter 2 diagnostic. Uses only frozen BIO15/BIO1,
latitude/longitude, the fixed nine-taxon orientation panel and six accepted
topologies. It does not establish causation, adaptation or a hydric mechanism.
"""
from __future__ import annotations

import argparse
import itertools
import json
import re
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd
from Bio import Phylo
from scipy.stats import t as student_t

AX15 = "chelsa_bio15"
AX1 = "chelsa_bio01"
TOL = 1e-12


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--contract", type=Path, required=True)
    p.add_argument("--geography-result", type=Path, required=True)
    p.add_argument("--japan-occurrences", type=Path, required=True)
    p.add_argument("--taiwan-occurrences", type=Path, required=True)
    p.add_argument("--au-trees", type=Path, required=True)
    p.add_argument("--out-json", type=Path, required=True)
    p.add_argument("--out-pairs", type=Path, required=True)
    return p.parse_args()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_tip(x: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]+", "", x.replace(" ", "_").replace(".", ""))


def read_trees(path: Path, n: int = 6):
    lines = [x.strip() for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    if len(lines) < n:
        raise ValueError(f"need {n} trees, found {len(lines)}")
    out = []
    for line in lines[:n]:
        if line.startswith("[") and "]" in line:
            line = line.split("]", 1)[1].strip()
        tree = Phylo.read(StringIO(line), "newick")
        tree.root_with_outgroup({"name": "OUTGROUP_saff"})
        out.append(tree)
    return out


def brownian_covariance(tree, taxa: list[str]) -> np.ndarray:
    terminals = {x.name: x for x in tree.get_terminals()}
    tips = [terminals[normalize_tip(x)] for x in taxa]
    root = tree.common_ancestor(tips)
    cov = np.zeros((len(tips), len(tips)), dtype=float)
    for i, a in enumerate(tips):
        for j, b in enumerate(tips):
            if i == j:
                cov[i, j] = tree.distance(root, a)
            else:
                mrca = tree.common_ancestor(a, b)
                cov[i, j] = tree.distance(root, mrca) if mrca != root else 0.0
    cov += np.eye(len(tips)) * 1e-10
    return cov


def zscore(x) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    sd = float(x.std(ddof=1))
    if not np.isfinite(sd) or sd <= 0:
        raise ValueError("cannot z-score zero/nonfinite variance")
    return (x - float(x.mean())) / sd


def fit_gls(y: np.ndarray, X: np.ndarray, cov: np.ndarray, coefficient_index: int = 1):
    inv = np.linalg.inv(cov)
    xtvi = X.T @ inv
    info = xtvi @ X
    beta = np.linalg.solve(info, xtvi @ y)
    resid = y - X @ beta
    dof = len(y) - X.shape[1]
    if dof <= 0:
        raise ValueError("non-positive GLS residual degrees of freedom")
    sigma2 = float(resid.T @ inv @ resid / dof)
    vcov = sigma2 * np.linalg.inv(info)
    se = float(np.sqrt(vcov[coefficient_index, coefficient_index]))
    b = float(beta[coefficient_index])
    p = float(2 * student_t.sf(abs(b / se), dof))
    return b, se, p


def conditional_prediction(y_train, X_train, x_test, cov_train, cross_cov) -> float:
    inv = np.linalg.inv(cov_train)
    beta = np.linalg.solve(X_train.T @ inv @ X_train, X_train.T @ inv @ y_train)
    return float(x_test @ beta + cross_cov @ inv @ (y_train - X_train @ beta))


def effect_summary(betas: list[float], pvals: list[float], loo_betas: list[float], sign: int) -> dict:
    return {
        "beta_range": [float(min(betas)), float(max(betas))],
        "beta_median": float(np.median(betas)),
        "p_range": [float(min(pvals)), float(max(pvals))],
        "topology_sign_agreement": f"{sum(np.sign(x) == sign for x in betas)}/{len(betas)}",
        "species_loo_sign_agreement": f"{sum(np.sign(x) == sign for x in loo_betas)}/{len(loo_betas)}",
        "species_loo_beta_range": [float(min(loo_betas)), float(max(loo_betas))],
    }


def closest_opposite_state_matching(tree, d_taxa: list[str], u_taxa: list[str]):
    terminals = {x.name: x for x in tree.get_terminals()}
    d_sorted = sorted(d_taxa)
    u_sorted = sorted(u_taxa)
    best = None
    for perm in itertools.permutations(u_sorted, len(d_sorted)):
        total = 0.0
        distances = []
        for d, u in zip(d_sorted, perm):
            dist = float(tree.distance(terminals[normalize_tip(d)], terminals[normalize_tip(u)]))
            total += dist
            distances.append(dist)
        key = (round(total, 12), tuple(perm))
        if best is None or key < best[0]:
            best = (key, list(zip(d_sorted, perm, distances)), total)
    if best is None:
        raise ValueError("no matching")
    return best[1], float(best[2])


def pair_rows_for_panel(tree, topology_index: int, panel_name: str, taxa: list[str], d_set: set[str], env: pd.DataFrame):
    d_taxa = [t for t in taxa if t in d_set]
    u_taxa = [t for t in taxa if t not in d_set]
    pairs, total = closest_opposite_state_matching(tree, d_taxa, u_taxa)
    rows = []
    for pair_index, (d, u, pdist) in enumerate(pairs, start=1):
        rows.append({
            "panel": panel_name,
            "topology_index": topology_index,
            "pair_index": pair_index,
            "d_taxon": d,
            "u_taxon": u,
            "patristic_distance": float(pdist),
            "matching_total_patristic_distance": total,
            "bio15_D_minus_U": float(env.loc[d, "z_bio15"] - env.loc[u, "z_bio15"]),
            "bio1_D_minus_U": float(env.loc[d, "z_bio1"] - env.loc[u, "z_bio1"]),
        })
    return rows


def summarize_pairs(df: pd.DataFrame) -> dict:
    by_topology = []
    for ti, g in df.groupby("topology_index", sort=True):
        by_topology.append({
            "topology_index": int(ti),
            "n_pairs": int(len(g)),
            "bio15_positive_pairs": int((g["bio15_D_minus_U"] > 0).sum()),
            "bio15_all_pairs_positive": bool((g["bio15_D_minus_U"] > 0).all()),
            "bio15_median_D_minus_U": float(g["bio15_D_minus_U"].median()),
            "bio15_range_D_minus_U": [float(g["bio15_D_minus_U"].min()), float(g["bio15_D_minus_U"].max())],
            "bio1_negative_pairs": int((g["bio1_D_minus_U"] < 0).sum()),
            "bio1_all_pairs_negative": bool((g["bio1_D_minus_U"] < 0).all()),
            "bio1_median_D_minus_U": float(g["bio1_D_minus_U"].median()),
            "bio1_range_D_minus_U": [float(g["bio1_D_minus_U"].min()), float(g["bio1_D_minus_U"].max())],
            "matching_total_patristic_distance": float(g["matching_total_patristic_distance"].iloc[0]),
        })
    unique_matchings = sorted({tuple(zip(g.sort_values("pair_index")["d_taxon"], g.sort_values("pair_index")["u_taxon"])) for _, g in df.groupby("topology_index")})
    return {
        "n_topologies": int(df["topology_index"].nunique()),
        "unique_matching_count": len(unique_matchings),
        "unique_matchings": [[{"D": d, "U": u} for d, u in m] for m in unique_matchings],
        "all_topologies_all_bio15_pairs_positive": bool(all(x["bio15_all_pairs_positive"] for x in by_topology)),
        "all_topologies_all_bio1_pairs_negative": bool(all(x["bio1_all_pairs_negative"] for x in by_topology)),
        "topology_summaries": by_topology,
    }


def main() -> int:
    args = parse_args()
    contract = read_json(args.contract)
    geo = read_json(args.geography_result)
    if contract["version"] != "chapter2_bio15_specificity_matched_contrast_contract_v1":
        raise AssertionError("contract version drift")
    if geo["version"] != "chapter2_orientation_geography_causal_boundary_result_v1":
        raise AssertionError("geography result version drift")
    if geo["classification"] != "bio15_persists_regionally_but_not_beyond_joint_history_geography":
        raise AssertionError("geography source classification drift")

    jp = pd.read_csv(args.japan_occurrences).assign(source_region="JP")
    tw = pd.read_csv(args.taiwan_occurrences).assign(source_region="TW")
    occ = pd.concat([jp, tw], ignore_index=True)

    taxa = list(geo["panel"]["taxa"])
    d_set = set(geo["panel"]["observed_d_taxa"])
    if len(taxa) != contract["frozen_panel"]["n_taxa"]:
        raise AssertionError("panel n drift")
    state = np.array([1.0 if t in d_set else 0.0 for t in taxa])
    if {"U": int((state == 0).sum()), "D": int((state == 1).sum())} != contract["frozen_panel"]["state_counts"]:
        raise AssertionError("state counts drift")

    counts = occ.groupby("scientific_name_query").size()
    if any(int(counts.get(t, 0)) < 10 for t in taxa):
        raise AssertionError("n>=10 occurrence gate drift")

    env = occ.groupby("scientific_name_query")[["latitude", "longitude", AX15, AX1]].mean().loc[taxa].copy()
    env["z_lat"] = zscore(env["latitude"])
    env["z_lon"] = zscore(env["longitude"])
    env["z_bio15"] = zscore(env[AX15])
    env["z_bio1"] = zscore(env[AX1])

    region_by_taxon = geo["panel"]["region_by_taxon"]
    japan_taxa = [t for t in taxa if region_by_taxon[t] == "JP"]
    if len(japan_taxa) != 7:
        raise AssertionError("Japan-only panel drift")

    trees = read_trees(args.au_trees, 6)

    # A — conditional environmental-axis specificity.
    y15 = env["z_bio15"].to_numpy(float)
    y1 = env["z_bio1"].to_numpy(float)
    lat = env["z_lat"].to_numpy(float)
    lon = env["z_lon"].to_numpy(float)

    models = {
        "bio15_given_bio1_geography": {
            "y": y15,
            "X": np.column_stack([np.ones(len(taxa)), state, y1, lat, lon]),
            "sign": +1,
        },
        "bio1_given_bio15_geography": {
            "y": y1,
            "X": np.column_stack([np.ones(len(taxa)), state, y15, lat, lon]),
            "sign": -1,
        },
    }
    conditional = {}
    for name, spec in models.items():
        betas, pvals, loo_betas = [], [], []
        for tree in trees:
            cov = brownian_covariance(tree, taxa)
            b, _, p = fit_gls(spec["y"], spec["X"], cov, 1)
            betas.append(b); pvals.append(p)
            for k in range(len(taxa)):
                keep = np.arange(len(taxa)) != k
                b2, _, _ = fit_gls(spec["y"][keep], spec["X"][keep], cov[np.ix_(keep, keep)], 1)
                loo_betas.append(b2)
        conditional[name] = effect_summary(betas, pvals, loo_betas, spec["sign"])

    # B — held-out incremental prediction for BIO15 beyond BIO1 + geography.
    prediction_rows = []
    X_base = np.column_stack([np.ones(len(taxa)), y1, lat, lon])
    X_trait = np.column_stack([np.ones(len(taxa)), y1, lat, lon, state])
    for ti, tree in enumerate(trees, start=1):
        cov = brownian_covariance(tree, taxa)
        for k, taxon in enumerate(taxa):
            keep = np.arange(len(taxa)) != k
            cov_train = cov[np.ix_(keep, keep)]
            cross_cov = cov[k, keep]
            pred_base = conditional_prediction(y15[keep], X_base[keep], X_base[k], cov_train, cross_cov)
            pred_trait = conditional_prediction(y15[keep], X_trait[keep], X_trait[k], cov_train, cross_cov)
            prediction_rows.append({
                "topology_index": ti,
                "left_out_taxon": taxon,
                "sq_error_improvement": float((y15[k] - pred_base) ** 2 - (y15[k] - pred_trait) ** 2),
                "abs_error_improvement": float(abs(y15[k] - pred_base) - abs(y15[k] - pred_trait)),
            })
    pred = pd.DataFrame(prediction_rows)
    pred_by_top = pred.groupby("topology_index").agg(
        delta_mse=("sq_error_improvement", "mean"),
        delta_mae=("abs_error_improvement", "mean"),
    ).reset_index()
    prediction = {
        "delta_mse_range": [float(pred_by_top["delta_mse"].min()), float(pred_by_top["delta_mse"].max())],
        "delta_mse_median": float(pred_by_top["delta_mse"].median()),
        "delta_mae_range": [float(pred_by_top["delta_mae"].min()), float(pred_by_top["delta_mae"].max())],
        "delta_mae_median": float(pred_by_top["delta_mae"].median()),
        "topologies_positive_delta_mse": int((pred_by_top["delta_mse"] > 0).sum()),
        "topologies_positive_delta_mae": int((pred_by_top["delta_mae"] > 0).sum()),
        "rule": "positive means orientation improves held-out BIO15 prediction beyond BIO1 + latitude + longitude + Brownian covariance",
    }

    # C — exact minimum-total patristic matching, environment-blind.
    pair_rows = []
    for ti, tree in enumerate(trees, start=1):
        pair_rows.extend(pair_rows_for_panel(tree, ti, "full9", taxa, d_set, env))
        pair_rows.extend(pair_rows_for_panel(tree, ti, "japan7", japan_taxa, d_set, env))
    pair_df = pd.DataFrame(pair_rows)
    pair_df.to_csv(args.out_pairs, index=False)
    matched = {
        "full9": summarize_pairs(pair_df[pair_df["panel"] == "full9"]),
        "japan7": summarize_pairs(pair_df[pair_df["panel"] == "japan7"]),
    }

    c15 = conditional["bio15_given_bio1_geography"]
    cond15_top = c15["topology_sign_agreement"] == "6/6"
    cond15_loo = c15["species_loo_sign_agreement"] == "54/54"
    full_match = matched["full9"]["all_topologies_all_bio15_pairs_positive"]
    jp_match = matched["japan7"]["all_topologies_all_bio15_pairs_positive"]

    if cond15_top and cond15_loo and full_match and jp_match:
        classification = "bio15_specificity_and_near_lineage_contrast_supported"
    elif cond15_top and cond15_loo:
        classification = "bio15_conditional_specificity_supported_but_near_lineage_contrasts_mixed"
    elif cond15_top:
        classification = "bio15_direction_persists_without_axis_specificity"
    else:
        classification = "bio15_specificity_not_supported_after_competing_axis_adjustment"

    payload = {
        "version": "chapter2_bio15_specificity_matched_contrast_result_v1",
        "analysis_role": contract["analysis_role"],
        "classification": classification,
        "conditional_specificity": conditional,
        "incremental_prediction": prediction,
        "phylogenetic_matched_pairs": matched,
        "interpretation_boundary": [
            "Conditioning BIO15 on BIO1 and coarse geography tests present-day axis specificity, not a historical causal mechanism.",
            "Matched extant opposite-state pairs are environment-blind sensitivity contrasts, not independent reconstructed transitions.",
            "Leave-one-out and topology sign stability do not convert the small n=9 panel into independent replication.",
            "No result establishes precipitation seasonality as selection, adaptation, plasticity or transition-time cause.",
        ],
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
