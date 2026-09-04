#!/usr/bin/env python3
"""Expanded-panel BIO15 specificity sensitivity for Chapter 2.

Uses only frozen occurrence assets, the fixed orientation crosswalk and six
accepted AU topologies. The n>=10 analysis remains primary. This script asks
whether the previously weak BIO15 axis specificity is simply a consequence of
n=9 by repeating the same mutually adjusted models at n>=5 and n>=3.
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

AX15 = "chelsa_bio15"
AX1 = "chelsa_bio01"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--contract", type=Path, required=True)
    p.add_argument("--coverage-audit", type=Path, required=True)
    p.add_argument("--n10-specificity", type=Path, required=True)
    p.add_argument("--orientation", type=Path, required=True)
    p.add_argument("--japan-occurrences", type=Path, required=True)
    p.add_argument("--taiwan-occurrences", type=Path, required=True)
    p.add_argument("--au-trees", type=Path, required=True)
    p.add_argument("--out-json", type=Path, required=True)
    p.add_argument("--out-csv", type=Path, required=True)
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
    missing = [t for t in taxa if normalize_tip(t) not in terminals]
    if missing:
        raise AssertionError(("taxa missing from topology", missing))
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
        "topology_sign_count": int(sum(np.sign(x) == sign for x in betas)),
        "topology_n": int(len(betas)),
        "species_loo_sign_count": int(sum(np.sign(x) == sign for x in loo_betas)),
        "species_loo_n": int(len(loo_betas)),
        "species_loo_beta_range": [float(min(loo_betas)), float(max(loo_betas))],
    }


def build_panel(threshold: int, audit: dict, crosswalk: pd.DataFrame, occ: pd.DataFrame):
    audit_row = audit["threshold_summaries"][str(threshold)]
    taxa = list(audit_row["taxa"])
    states = crosswalk.set_index("accepted_taxon")["analysis_state"].to_dict()
    if any(states.get(t) not in {"U", "D"} for t in taxa):
        raise AssertionError(("unresolved state in threshold panel", threshold))
    counts = occ.groupby("scientific_name_query").size()
    if any(int(counts.get(t, 0)) < threshold for t in taxa):
        raise AssertionError(("occurrence threshold drift", threshold))
    state = np.array([1.0 if states[t] == "D" else 0.0 for t in taxa])
    return taxa, state


def analyse_panel(name: str, threshold: int, audit: dict, crosswalk: pd.DataFrame, occ: pd.DataFrame, trees) -> tuple[dict, list[dict]]:
    taxa, state = build_panel(threshold, audit, crosswalk, occ)
    env = occ.groupby("scientific_name_query")[["latitude", "longitude", AX15, AX1]].mean().loc[taxa].copy()
    env["z_lat"] = zscore(env["latitude"])
    env["z_lon"] = zscore(env["longitude"])
    env["z_bio15"] = zscore(env[AX15])
    env["z_bio1"] = zscore(env[AX1])

    y15 = env["z_bio15"].to_numpy(float)
    y1 = env["z_bio1"].to_numpy(float)
    lat = env["z_lat"].to_numpy(float)
    lon = env["z_lon"].to_numpy(float)

    specs = {
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
    fit_rows: list[dict] = []
    for model_name, spec in specs.items():
        betas, pvals, loo_betas = [], [], []
        for ti, tree in enumerate(trees, start=1):
            cov = brownian_covariance(tree, taxa)
            b, _, p = fit_gls(spec["y"], spec["X"], cov, 1)
            betas.append(b)
            pvals.append(p)
            fit_rows.append({"panel": name, "threshold": threshold, "model": model_name, "topology_index": ti, "left_out_taxon": "", "beta_orientation": b, "p_orientation": p})
            for k, taxon in enumerate(taxa):
                keep = np.arange(len(taxa)) != k
                b2, _, p2 = fit_gls(spec["y"][keep], spec["X"][keep], cov[np.ix_(keep, keep)], 1)
                loo_betas.append(b2)
                fit_rows.append({"panel": name, "threshold": threshold, "model": model_name, "topology_index": ti, "left_out_taxon": taxon, "beta_orientation": b2, "p_orientation": p2})
        conditional[model_name] = effect_summary(betas, pvals, loo_betas, spec["sign"])

    # Supporting held-out prediction for BIO15.
    X_base = np.column_stack([np.ones(len(taxa)), y1, lat, lon])
    X_trait = np.column_stack([np.ones(len(taxa)), y1, lat, lon, state])
    pred_top = []
    for ti, tree in enumerate(trees, start=1):
        cov = brownian_covariance(tree, taxa)
        sq_improvements, abs_improvements = [], []
        for k in range(len(taxa)):
            keep = np.arange(len(taxa)) != k
            cov_train = cov[np.ix_(keep, keep)]
            cross_cov = cov[k, keep]
            pred_base = conditional_prediction(y15[keep], X_base[keep], X_base[k], cov_train, cross_cov)
            pred_trait = conditional_prediction(y15[keep], X_trait[keep], X_trait[k], cov_train, cross_cov)
            sq_improvements.append(float((y15[k] - pred_base) ** 2 - (y15[k] - pred_trait) ** 2))
            abs_improvements.append(float(abs(y15[k] - pred_base) - abs(y15[k] - pred_trait)))
        pred_top.append({"topology_index": ti, "delta_mse": float(np.mean(sq_improvements)), "delta_mae": float(np.mean(abs_improvements))})
    pred_df = pd.DataFrame(pred_top)
    prediction = {
        "delta_mse_range": [float(pred_df.delta_mse.min()), float(pred_df.delta_mse.max())],
        "delta_mse_median": float(pred_df.delta_mse.median()),
        "delta_mae_range": [float(pred_df.delta_mae.min()), float(pred_df.delta_mae.max())],
        "delta_mae_median": float(pred_df.delta_mae.median()),
        "topologies_positive_delta_mse": int((pred_df.delta_mse > 0).sum()),
        "topologies_positive_delta_mae": int((pred_df.delta_mae > 0).sum()),
    }

    return {
        "threshold": threshold,
        "n_taxa": int(len(taxa)),
        "n_U": int((state == 0).sum()),
        "n_D": int((state == 1).sum()),
        "taxa": taxa,
        "conditional_specificity": conditional,
        "incremental_prediction": prediction,
    }, fit_rows


def main() -> int:
    args = parse_args()
    contract = read_json(args.contract)
    audit = read_json(args.coverage_audit)
    n10 = read_json(args.n10_specificity)
    if contract["version"] != "chapter2_expanded_bio15_specificity_contract_v1":
        raise AssertionError("contract version drift")
    if audit["version"] != "chapter2_orientation_occurrence_coverage_audit_result_v1":
        raise AssertionError("coverage audit version drift")
    if audit["classification"] != "relaxed_existing_coverage_materially_expands_state_diverse_panel":
        raise AssertionError("coverage audit classification drift")
    if n10["version"] != "chapter2_bio15_specificity_matched_contrast_result_v1":
        raise AssertionError("n10 specificity version drift")
    if n10["classification"] != "bio15_direction_persists_without_axis_specificity":
        raise AssertionError("n10 specificity classification drift")

    crosswalk = pd.read_csv(args.orientation)
    crosswalk = crosswalk[crosswalk.analysis_state.isin(["U", "D"])].copy()
    jp = pd.read_csv(args.japan_occurrences)
    tw = pd.read_csv(args.taiwan_occurrences)
    occ = pd.concat([jp, tw], ignore_index=True)
    trees = read_trees(args.au_trees, 6)

    panels = {}
    all_fit_rows = []
    for name, threshold in (("n5", 5), ("n3", 3)):
        panel, rows = analyse_panel(name, threshold, audit, crosswalk, occ, trees)
        exp = contract["panels"][name]
        if (panel["n_taxa"], panel["n_U"], panel["n_D"]) != (exp["expected_n"], exp["expected_U"], exp["expected_D"]):
            raise AssertionError(("panel drift", name, panel["n_taxa"], panel["n_U"], panel["n_D"]))
        panels[name] = panel
        all_fit_rows.extend(rows)

    n5_b15 = panels["n5"]["conditional_specificity"]["bio15_given_bio1_geography"]
    if n5_b15["topology_sign_count"] == 6 and n5_b15["species_loo_sign_count"] == n5_b15["species_loo_n"]:
        classification = "expanded_n5_recovers_bio15_axis_specificity"
    elif n5_b15["topology_sign_count"] == 6:
        classification = "expanded_panels_retain_bio15_direction_without_specificity"
    else:
        classification = "expanded_panels_destabilize_bio15_direction"

    result = {
        "version": "chapter2_expanded_bio15_specificity_result_v1",
        "analysis_role": contract["analysis_role"],
        "classification": classification,
        "primary_reference_n10": {
            "classification": n10["classification"],
            "bio15_given_bio1_geography": n10["conditional_specificity"]["bio15_given_bio1_geography"],
            "bio1_given_bio15_geography": n10["conditional_specificity"]["bio1_given_bio15_geography"],
            "incremental_prediction": n10["incremental_prediction"],
        },
        "expanded_panels": panels,
        "interpretation_boundary": contract["claim_ceiling"],
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    pd.DataFrame(all_fit_rows).to_csv(args.out_csv, index=False)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
