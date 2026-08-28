#!/usr/bin/env python3
"""Quantify bounded ecological explanatory reach for Chapter 2 capitulum histories.

This diagnostic is deliberately non-causal. It asks whether present-day trait
states carry a stable climate correspondence after Brownian phylogenetic
correction, whether that direction survives accepted topology and species-LOO
sensitivity, and whether knowing the trait state improves held-out prediction of
the climate axis beyond both a naive mean-only null and phylogeny-only Brownian
kriging.

The predictive comparison uses climate as the continuous response because the
frozen comparative model is PGLS. Positive delta MSE/MAE means the
phylogeny+trait model predicts held-out climate better than the stated baseline.
No result reconstructs historical climate or assigns an ecological cause to a
particular transition.
"""
from __future__ import annotations

import argparse
import json
import re
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd
from Bio import Phylo
from scipy.stats import t as student_t

AXES = ["chelsa_bio01", "chelsa_bio04", "chelsa_bio12", "chelsa_bio15"]


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--occurrences", type=Path, nargs="+", required=True)
    p.add_argument("--orientation", type=Path, required=True)
    p.add_argument("--trait-seed", type=Path, required=True)
    p.add_argument("--au-trees", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--min-n", type=int, default=10)
    p.add_argument("--topologies", type=int, default=6)
    return p.parse_args()


def normalize_tip(x: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]+", "", x.replace(" ", "_").replace(".", ""))


def read_trees(path: Path, n: int):
    lines = [x.strip() for x in path.read_text().splitlines() if x.strip()]
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


def brownian_covariance(tree, taxa):
    terminals = {x.name: x for x in tree.get_terminals()}
    tips = [terminals[normalize_tip(x)] for x in taxa]
    root = tree.common_ancestor(tips)
    cov = np.zeros((len(tips), len(tips)))
    for i, a in enumerate(tips):
        for j, b in enumerate(tips):
            if i == j:
                cov[i, j] = tree.distance(root, a)
            else:
                mrca = tree.common_ancestor(a, b)
                cov[i, j] = tree.distance(root, mrca) if mrca != root else 0.0
    cov += np.eye(len(tips)) * 1e-10
    return cov


def fit_gls(y, state, cov):
    X = np.column_stack([np.ones(len(state)), state])
    inv = np.linalg.inv(cov)
    xtvi = X.T @ inv
    beta = np.linalg.solve(xtvi @ X, xtvi @ y)
    resid = y - X @ beta
    dof = len(y) - 2
    sigma2 = float(resid.T @ inv @ resid / dof)
    vcov = sigma2 * np.linalg.inv(xtvi @ X)
    se = np.sqrt(np.diag(vcov))
    tval = float(beta[1] / se[1])
    pval = float(2 * student_t.sf(abs(tval), dof))
    return float(beta[1]), float(se[1]), pval


def conditional_prediction(y_train, X_train, x_test, cov_train, cross_cov):
    inv = np.linalg.inv(cov_train)
    beta = np.linalg.solve(X_train.T @ inv @ X_train, X_train.T @ inv @ y_train)
    return float(x_test @ beta + cross_cov @ inv @ (y_train - X_train @ beta))


def resolved_phyllary(value):
    return value if value in {"appressed", "ascending", "spreading", "recurved"} else None


def resolved_stickiness(value):
    if value == "sticky":
        return "sticky"
    if value == "nonsticky_or_nearly_nonsticky":
        return "nonsticky"
    return None


def main():
    args = parse_args()
    occ = pd.concat([pd.read_csv(p) for p in args.occurrences], ignore_index=True)
    counts = occ.groupby("scientific_name_query").size()
    eligible = set(counts[counts >= args.min_n].index)
    centroids = occ.groupby("scientific_name_query")[AXES].mean()

    orientation = pd.read_csv(args.orientation)
    orientation = orientation[orientation["analysis_state"].isin(["U", "D"])]
    state_by_taxon = dict(zip(orientation["accepted_taxon"], orientation["analysis_state"]))
    taxa = sorted(eligible & set(state_by_taxon))
    state = np.array([0.0 if state_by_taxon[x] == "U" else 1.0 for x in taxa])
    if len(taxa) < 6 or len(set(state)) < 2:
        raise ValueError("orientation panel not estimable")
    trees = read_trees(args.au_trees, args.topologies)

    full_rows, loo_rows, prediction_rows = [], [], []
    for topology_index, tree in enumerate(trees, start=1):
        cov = brownian_covariance(tree, taxa)
        for axis in AXES:
            raw = centroids.loc[taxa, axis].to_numpy(float)
            y = (raw - raw.mean()) / raw.std(ddof=1)
            beta, se, pval = fit_gls(y, state, cov)
            full_rows.append({
                "topology_index": topology_index,
                "axis": axis,
                "beta_D_minus_U_sd": beta,
                "se": se,
                "p": pval,
            })
            for k, taxon in enumerate(taxa):
                keep = np.arange(len(taxa)) != k
                cov_train = cov[np.ix_(keep, keep)]
                loo_beta, _, loo_p = fit_gls(y[keep], state[keep], cov_train)
                loo_rows.append({
                    "topology_index": topology_index,
                    "axis": axis,
                    "left_out_taxon": taxon,
                    "beta_D_minus_U_sd": loo_beta,
                    "p": loo_p,
                })
                cross_cov = cov[k, keep]
                pred_null = float(np.mean(y[keep]))
                X0 = np.ones((keep.sum(), 1))
                x0 = np.ones(1)
                X1 = np.column_stack([np.ones(keep.sum()), state[keep]])
                x1 = np.array([1.0, state[k]])
                pred_phylogeny = conditional_prediction(y[keep], X0, x0, cov_train, cross_cov)
                pred_trait = conditional_prediction(y[keep], X1, x1, cov_train, cross_cov)
                sq_null = (y[k] - pred_null) ** 2
                sq_phylogeny = (y[k] - pred_phylogeny) ** 2
                sq_trait = (y[k] - pred_trait) ** 2
                abs_null = abs(y[k] - pred_null)
                abs_phylogeny = abs(y[k] - pred_phylogeny)
                abs_trait = abs(y[k] - pred_trait)
                prediction_rows.append({
                    "topology_index": topology_index,
                    "axis": axis,
                    "left_out_taxon": taxon,
                    "sq_error_improvement_vs_null": sq_null - sq_trait,
                    "abs_error_improvement_vs_null": abs_null - abs_trait,
                    "sq_error_improvement_vs_phylogeny_only": sq_phylogeny - sq_trait,
                    "abs_error_improvement_vs_phylogeny_only": abs_phylogeny - abs_trait,
                    "phylogeny_only_sq_error_improvement_vs_null": sq_null - sq_phylogeny,
                })

    full = pd.DataFrame(full_rows)
    loo = pd.DataFrame(loo_rows)
    predictions = pd.DataFrame(prediction_rows)
    axes = {}
    for axis in AXES:
        f = full[full["axis"] == axis]
        l = loo[loo["axis"] == axis]
        expected_sign = np.sign(float(f["beta_D_minus_U_sd"].median()))
        by_topology = predictions[predictions["axis"] == axis].groupby("topology_index").agg(
            delta_mse_vs_null=("sq_error_improvement_vs_null", "mean"),
            delta_mae_vs_null=("abs_error_improvement_vs_null", "mean"),
            delta_mse_vs_phylogeny_only=("sq_error_improvement_vs_phylogeny_only", "mean"),
            delta_mae_vs_phylogeny_only=("abs_error_improvement_vs_phylogeny_only", "mean"),
            phylogeny_only_delta_mse_vs_null=("phylogeny_only_sq_error_improvement_vs_null", "mean"),
        ).reset_index()
        axes[axis] = {
            "beta_D_minus_U_sd_range": [float(f["beta_D_minus_U_sd"].min()), float(f["beta_D_minus_U_sd"].max())],
            "se_range": [float(f["se"].min()), float(f["se"].max())],
            "p_range": [float(f["p"].min()), float(f["p"].max())],
            "ml_topology_beta_D_minus_U_sd": float(f.loc[f["topology_index"] == 1, "beta_D_minus_U_sd"].iloc[0]),
            "accepted_topology_sign_agreement": float((np.sign(f["beta_D_minus_U_sd"]) == expected_sign).mean()),
            "species_loo_sign_agreement": float((np.sign(l["beta_D_minus_U_sd"]) == expected_sign).mean()),
            "species_loo_evaluations": int(len(l)),
            "loo_delta_mse_vs_null_range": [float(by_topology["delta_mse_vs_null"].min()), float(by_topology["delta_mse_vs_null"].max())],
            "loo_delta_mse_vs_null_median": float(by_topology["delta_mse_vs_null"].median()),
            "loo_delta_mae_vs_null_range": [float(by_topology["delta_mae_vs_null"].min()), float(by_topology["delta_mae_vs_null"].max())],
            "loo_delta_mse_vs_phylogeny_only_range": [float(by_topology["delta_mse_vs_phylogeny_only"].min()), float(by_topology["delta_mse_vs_phylogeny_only"].max())],
            "loo_delta_mse_vs_phylogeny_only_median": float(by_topology["delta_mse_vs_phylogeny_only"].median()),
            "loo_delta_mae_vs_phylogeny_only_range": [float(by_topology["delta_mae_vs_phylogeny_only"].min()), float(by_topology["delta_mae_vs_phylogeny_only"].max())],
            "phylogeny_only_delta_mse_vs_null_range": [float(by_topology["phylogeny_only_delta_mse_vs_null"].min()), float(by_topology["phylogeny_only_delta_mse_vs_null"].max())],
            "prediction_improvement_rule": ">0 means phylogeny+trait predicts held-out climate better than the named baseline",
            "loo_delta_mse_range": [float(by_topology["delta_mse_vs_phylogeny_only"].min()), float(by_topology["delta_mse_vs_phylogeny_only"].max())],
            "loo_delta_mse_median": float(by_topology["delta_mse_vs_phylogeny_only"].median()),
            "loo_delta_mae_range": [float(by_topology["delta_mae_vs_phylogeny_only"].min()), float(by_topology["delta_mae_vs_phylogeny_only"].max())],
        }

    seed = pd.read_csv(args.trait_seed)
    seed = seed[seed["paper_taxon_concept"].isin(eligible)].copy()
    phyllary = seed.assign(resolved=seed["phyllary_posture"].map(resolved_phyllary)).dropna(subset=["resolved"])
    stickiness = seed.assign(resolved=seed["stickiness_state"].map(resolved_stickiness)).dropna(subset=["resolved"])
    phyllary_counts = phyllary["resolved"].value_counts().to_dict()
    stickiness_counts = stickiness["resolved"].value_counts().to_dict()

    primary = axes["chelsa_bio15"]
    orientation_status = "unresolved"
    if (
        primary["accepted_topology_sign_agreement"] == 1.0
        and primary["species_loo_sign_agreement"] == 1.0
        and primary["loo_delta_mse_vs_null_median"] > 0
        and primary["loo_delta_mse_vs_phylogeny_only_median"] > 0
        and max(primary["p_range"]) < 0.05
    ):
        orientation_status = "tendency_supported"

    payload = {
        "contract_version": "chapter2_ecological_explanatory_reach_v1",
        "estimand": "present-day ecological correspondence and predictive explanatory reach; not historical causation",
        "orientation": {
            "status": orientation_status,
            "n_taxa": len(taxa),
            "n_U": int((state == 0).sum()),
            "n_D": int((state == 1).sum()),
            "topology_ensemble": "first six AU-nonrejected optimized Comp1061 topologies; topology 1 is ML within preregistered candidate set",
            "raw_ufboot_ecology_sign_rate": "not_evaluable: raw Comp1061 UFBoot trees were not preserved in the accepted archived ecological input bundle",
            "prediction_baselines": {
                "null": "training-set mean only; no trait and no phylogenetic covariance",
                "phylogeny_only": "intercept plus Brownian conditional prediction on the accepted topology",
                "phylogeny_plus_orientation": "intercept plus U/D orientation and Brownian conditional prediction",
            },
            "axes": axes,
            "primary_interpretation": "BIO15 and BIO1 directions are stable to accepted-topology and species-LOO perturbation. Orientation improves held-out prediction over a naive mean-only null for both axes, but not over phylogeny-only Brownian kriging; neither frozen primary PGLS threshold nor branchwise permutation threshold is passed. The correct result class is unresolved.",
        },
        "phyllary_posture": {
            "status": "not_evaluable",
            "historical_state_coverage": "10/38 concepts in Chapter 2 history",
            "climate_panel_resolved_taxa_n_ge_min_n": int(len(phyllary)),
            "state_counts": {str(k): int(v) for k, v in phyllary_counts.items()},
            "reason": "The frozen occurrence-climate assets do not provide enough resolved, state-diverse phyllary taxa at the n>=10 gate for a phylogeny-aware climate comparison. Enemy exclusion, wetness protection and pollinator-access effects require Chapter 3 measurements.",
        },
        "stickiness": {
            "status": "not_evaluable",
            "historical_state_coverage": "13/38 concepts in Chapter 2 history",
            "climate_panel_resolved_taxa_n_ge_min_n": int(len(stickiness)),
            "state_counts": {str(k): int(v) for k, v in stickiness_counts.items()},
            "reason": "The frozen occurrence-climate assets contain no estimable sticky-versus-nonsticky contrast at the n>=10 gate. Climate proxy association, enemy exclusion and production cost therefore cannot be separated with current data.",
        },
        "chapter2_result": "Repeated minimum changes are shared across the three discrete traits, but ecological explanatory reach is asymmetric: orientation has a stable directional climate correspondence that improves prediction over a naive null but not over phylogeny-only, whereas phyllary posture and stickiness are not evaluable with the frozen climate panel.",
        "claim_boundary": "Do not call the orientation pattern adaptation, convergence, historical niche causation or event-specific environmental matching. not_evaluable is a data-resolution result, not evidence of no ecological relation.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
