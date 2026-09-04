#!/usr/bin/env python3
"""Geography-conditioned causal-boundary tests for Chapter 2 orientation ecology.

This follow-up asks whether the existing East-Asian orientation-BIO15
correspondence survives three progressively stronger geographic falsifications:
(1) removal of the Taiwan source region, (2) explicit coarse latitude/longitude
adjustment inside Brownian GLS, and (3) counterfactual trait maps matched for
recurrence plus coarse geography/history geometry.

The analysis is post-result and non-causal. It cannot establish climatic
selection, adaptation, plasticity, or transition-time historical cause.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd
from Bio import Phylo
from scipy.stats import t as student_t

TOL = 1e-12
AXES = ("chelsa_bio15", "chelsa_bio01")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--contract", type=Path, required=True)
    p.add_argument("--counterfactual-result", type=Path, required=True)
    p.add_argument("--counterfactual-assignments", type=Path, required=True)
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


def zscore(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    sd = x.std(ddof=1)
    if sd <= 0:
        raise ValueError("cannot standardize zero-variance vector")
    return (x - x.mean()) / sd


def fit_gls(y: np.ndarray, X: np.ndarray, cov: np.ndarray, coefficient_index: int = 1) -> tuple[float, float, float]:
    inv = np.linalg.inv(cov)
    xtvi = X.T @ inv
    beta = np.linalg.solve(xtvi @ X, xtvi @ y)
    resid = y - X @ beta
    dof = len(y) - X.shape[1]
    if dof <= 0:
        raise ValueError("non-positive GLS residual degrees of freedom")
    sigma2 = float(resid.T @ inv @ resid / dof)
    vcov = sigma2 * np.linalg.inv(xtvi @ X)
    se = float(np.sqrt(vcov[coefficient_index, coefficient_index]))
    b = float(beta[coefficient_index])
    p = float(2 * student_t.sf(abs(b / se), dof))
    return b, se, p


def effect_summary(values: list[float], pvals: list[float], prespecified_sign: int) -> dict:
    return {
        "beta_range": [float(min(values)), float(max(values))],
        "beta_median": float(np.median(values)),
        "p_range": [float(min(pvals)), float(max(pvals))],
        "topology_sign_agreement": f"{sum(np.sign(x) == prespecified_sign for x in values)}/{len(values)}",
    }


def rank_fraction(pool: pd.DataFrame, key: str, observed: float) -> dict:
    if len(pool) == 0:
        return {"status": "not_evaluable", "n": 0}
    count = int((pool[key].astype(float) >= observed - TOL).sum())
    return {"status": "evaluable", "n": int(len(pool)), "count_at_least_observed": count, "fraction": float(count / len(pool))}


def reverse_world(pool: pd.DataFrame, key: str) -> dict:
    if len(pool) == 0:
        return {"status": "not_evaluable", "n": 0}
    rev = pool[pool[key].astype(float) < -TOL]
    if len(rev) == 0:
        return {"status": "evaluable", "n": int(len(pool)), "opposite_direction_exists": False}
    row = rev.sort_values([key, "assignment_id"]).iloc[0]
    return {
        "status": "evaluable",
        "n": int(len(pool)),
        "opposite_direction_exists": True,
        "most_reverse_signed_statistic": float(row[key]),
        "assignment_id": str(row["assignment_id"]),
    }


def ordinal_normalized_rank(df: pd.DataFrame, value_col: str) -> dict[str, float]:
    ordered = df.sort_values([value_col, "assignment_id"]).reset_index(drop=True)
    if len(ordered) == 1:
        return {str(ordered.loc[0, "assignment_id"]): 0.0}
    vals = np.arange(len(ordered), dtype=float) / (len(ordered) - 1)
    return dict(zip(ordered["assignment_id"].astype(str), vals))


def main() -> int:
    args = parse_args()
    contract = read_json(args.contract)
    cf = read_json(args.counterfactual_result)
    assignments = pd.read_csv(args.counterfactual_assignments)

    if contract["version"] != "chapter2_orientation_geography_causal_boundary_contract_v1":
        raise AssertionError("contract version drift")
    if cf["version"] != "chapter2_orientation_environment_counterfactual_result_v1":
        raise AssertionError("counterfactual source version drift")
    if cf["panel"]["n_taxa"] != contract["frozen_panel"]["full_n"]:
        raise AssertionError("panel n drift")
    if len(assignments) != contract["tests"]["C_geography_conditioned_counterfactual"]["base_maps"]:
        raise AssertionError("counterfactual assignment count drift")

    jp = pd.read_csv(args.japan_occurrences).assign(source_region="JP")
    tw = pd.read_csv(args.taiwan_occurrences).assign(source_region="TW")
    occ = pd.concat([jp, tw], ignore_index=True)
    taxa = list(cf["panel"]["taxa"])
    d_taxa = set(cf["panel"]["observed_d_taxa"])
    state = np.array([1.0 if t in d_taxa else 0.0 for t in taxa])

    counts = occ.groupby("scientific_name_query").size()
    if any(int(counts.get(t, 0)) < 10 for t in taxa):
        raise AssertionError("frozen n>=10 occurrence gate drift")

    env = occ.groupby("scientific_name_query")[["latitude", "longitude", *AXES]].mean().loc[taxa]
    region_by_taxon = {}
    for t in taxa:
        regs = set(occ.loc[occ["scientific_name_query"] == t, "source_region"])
        if len(regs) != 1:
            raise AssertionError(("taxon source-region ambiguity", t, sorted(regs)))
        region_by_taxon[t] = next(iter(regs))

    tw_taxa = sorted(t for t in taxa if region_by_taxon[t] == "TW")
    if tw_taxa != sorted(contract["frozen_panel"]["taiwan_taxa_in_full_panel"]):
        raise AssertionError(("Taiwan panel drift", tw_taxa))

    trees = read_trees(args.au_trees, 6)

    axis_meta = {
        "chelsa_bio15": {"sign": +1, "label": "BIO15 precipitation seasonality"},
        "chelsa_bio01": {"sign": -1, "label": "BIO1 annual mean temperature"},
    }

    # A: Japan-only regional persistence.
    japan_taxa = [t for t in taxa if region_by_taxon[t] == "JP"]
    japan_state = np.array([1.0 if t in d_taxa else 0.0 for t in japan_taxa])
    if len(japan_taxa) != contract["frozen_panel"]["japan_only_n"]:
        raise AssertionError("Japan-only n drift")
    if {"U": int((japan_state == 0).sum()), "D": int((japan_state == 1).sum())} != contract["frozen_panel"]["japan_only_state_counts"]:
        raise AssertionError("Japan-only state-count drift")

    japan_result = {}
    for axis in AXES:
        y = zscore(env.loc[japan_taxa, axis].to_numpy(float))
        betas, ps, loo_betas, loo_ps = [], [], [], []
        for tree in trees:
            cov = brownian_covariance(tree, japan_taxa)
            X = np.column_stack([np.ones(len(japan_taxa)), japan_state])
            b, _, p = fit_gls(y, X, cov)
            betas.append(b); ps.append(p)
            for k in range(len(japan_taxa)):
                keep = np.arange(len(japan_taxa)) != k
                b2, _, p2 = fit_gls(y[keep], X[keep], cov[np.ix_(keep, keep)])
                loo_betas.append(b2); loo_ps.append(p2)
        sign = axis_meta[axis]["sign"]
        res = effect_summary(betas, ps, sign)
        res.update({
            "n_taxa": int(len(japan_taxa)),
            "n_U": int((japan_state == 0).sum()),
            "n_D": int((japan_state == 1).sum()),
            "species_loo_sign_agreement": f"{sum(np.sign(x) == sign for x in loo_betas)}/{len(loo_betas)}",
            "species_loo_beta_range": [float(min(loo_betas)), float(max(loo_betas))],
            "species_loo_p_range": [float(min(loo_ps)), float(max(loo_ps))],
        })
        japan_result[axis] = res

    # B: coarse geography adjustment on full n=9.
    lat = zscore(env["latitude"].to_numpy(float))
    lon = zscore(env["longitude"].to_numpy(float))
    tw_indicator = np.array([1.0 if region_by_taxon[t] == "TW" else 0.0 for t in taxa])
    geography_adjusted = {}
    for axis in AXES:
        y = zscore(env[axis].to_numpy(float))
        sign = axis_meta[axis]["sign"]
        model_outputs = {}
        for model_name, X in {
            "lat_lon": np.column_stack([np.ones(len(taxa)), state, lat, lon]),
            "taiwan_indicator": np.column_stack([np.ones(len(taxa)), state, tw_indicator]),
        }.items():
            betas, ps, loo_betas = [], [], []
            for tree in trees:
                cov = brownian_covariance(tree, taxa)
                b, _, p = fit_gls(y, X, cov)
                betas.append(b); ps.append(p)
                for k in range(len(taxa)):
                    keep = np.arange(len(taxa)) != k
                    b2, _, _ = fit_gls(y[keep], X[keep], cov[np.ix_(keep, keep)])
                    loo_betas.append(b2)
            res = effect_summary(betas, ps, sign)
            res["species_loo_sign_agreement"] = f"{sum(np.sign(x) == sign for x in loo_betas)}/{len(loo_betas)}"
            res["species_loo_beta_range"] = [float(min(loo_betas)), float(max(loo_betas))]
            model_outputs[model_name] = res
        geography_adjusted[axis] = model_outputs

    # C: recurrence + geography and joint history/geography counterfactuals.
    centroid = env[["latitude", "longitude"]]
    geo_rows = []
    for row in assignments.to_dict("records"):
        ds = str(row["d_taxa"]).split("|")
        g = centroid.loc[ds]
        geo_rows.append({
            "assignment_id": str(row["assignment_id"]),
            "mean_lat": float(g["latitude"].mean()),
            "mean_lon": float(g["longitude"].mean()),
            "sd_lat": float(g["latitude"].std(ddof=1)),
            "sd_lon": float(g["longitude"].std(ddof=1)),
        })
    geo = pd.DataFrame(geo_rows)
    feature_cols = ["mean_lat", "mean_lon", "sd_lat", "sd_lon"]
    for c in feature_cols:
        geo[c + "_z"] = zscore(geo[c].to_numpy(float))
    observed_id = str(assignments.loc[assignments["observed"] == True, "assignment_id"].iloc[0])
    obs = geo.set_index("assignment_id").loc[observed_id, [c + "_z" for c in feature_cols]].to_numpy(float)
    zmat = geo[[c + "_z" for c in feature_cols]].to_numpy(float)
    geo["geographic_distance"] = np.sqrt(((zmat - obs) ** 2).sum(axis=1))

    merged = assignments.merge(geo[["assignment_id", "geographic_distance"]], on="assignment_id", validate="one_to_one")
    recurrence = merged[merged["recurrence_profile_match"] == True].copy()
    if len(recurrence) < 10:
        raise AssertionError("recurrence-matched geography pool too small")
    k = max(1, math.ceil(len(recurrence) * 0.25))
    geography_nearest = recurrence.sort_values(["geographic_distance", "assignment_id"]).head(k).copy()

    depth_rank = ordinal_normalized_rank(recurrence, "depth_distance")
    geo_rank = ordinal_normalized_rank(recurrence, "geographic_distance")
    recurrence["joint_distance"] = recurrence["assignment_id"].astype(str).map(depth_rank) + recurrence["assignment_id"].astype(str).map(geo_rank)
    joint_nearest = recurrence.sort_values(["joint_distance", "assignment_id"]).head(k).copy()

    observed_row = merged[merged["observed"] == True].iloc[0]
    cf_result = {}
    for axis, key in (("chelsa_bio15", "bio15_signed_median"), ("chelsa_bio01", "bio1_signed_median")):
        observed_stat = float(observed_row[key])
        pools = {
            "recurrence_profile_matched": recurrence,
            "geography_nearest_quartile_within_recurrence": geography_nearest,
            "joint_history_geography_nearest_quartile": joint_nearest,
        }
        cf_result[axis] = {
            "observed_signed_statistic": observed_stat,
            "pools": {
                name: {
                    "rank": rank_fraction(pool, key, observed_stat),
                    "reverse_world": reverse_world(pool, key),
                    "assignment_ids": list(pool["assignment_id"].astype(str)),
                }
                for name, pool in pools.items()
            },
        }

    bio15_japan_ok = japan_result["chelsa_bio15"]["topology_sign_agreement"] == "6/6" and japan_result["chelsa_bio15"]["species_loo_sign_agreement"] == "42/42"
    bio15_geo_ok = geography_adjusted["chelsa_bio15"]["lat_lon"]["topology_sign_agreement"] == "6/6"
    joint_fraction = cf_result["chelsa_bio15"]["pools"]["joint_history_geography_nearest_quartile"]["rank"]["fraction"]
    if not (bio15_japan_ok and bio15_geo_ok):
        classification = "bio15_correspondence_geographically_fragile"
    elif joint_fraction <= 0.05:
        classification = "bio15_persists_beyond_coarse_geography_and_history"
    else:
        classification = "bio15_persists_regionally_but_not_beyond_joint_history_geography"

    result = {
        "version": "chapter2_orientation_geography_causal_boundary_result_v1",
        "analysis_role": contract["analysis_role"],
        "classification": classification,
        "panel": {
            "taxa": taxa,
            "observed_d_taxa": sorted(d_taxa),
            "region_by_taxon": region_by_taxon,
            "taxon_centroids": {
                t: {
                    "latitude": float(env.loc[t, "latitude"]),
                    "longitude": float(env.loc[t, "longitude"]),
                }
                for t in taxa
            },
        },
        "japan_only": japan_result,
        "geography_adjusted": geography_adjusted,
        "counterfactual_geography": {
            "recurrence_matched_n": int(len(recurrence)),
            "quartile_n": int(k),
            "geographic_features": feature_cols,
            "axes": cf_result,
        },
        "interpretation": {
            "bio15": "The BIO15 orientation contrast retains its prespecified direction after excluding Taiwan and after explicit coarse latitude/longitude adjustment, so the signal is not reducible to a simple Taiwan-versus-Japan or centroid-geography contrast. However, its magnitude is not exceptional among counterfactual maps jointly near the observed recurrence/depth and geographic configuration; coarse geography and historical placement therefore remain entangled with the association.",
            "causal_boundary": "This strengthens regional/geographic persistence of the present correspondence but does not identify precipitation seasonality as the cause of orientation evolution.",
        },
        "claim_ceiling": contract["claim_ceiling"],
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    merged_out = merged.copy()
    merged_out["geography_nearest"] = merged_out["assignment_id"].isin(set(geography_nearest["assignment_id"]))
    merged_out["joint_nearest"] = merged_out["assignment_id"].isin(set(joint_nearest["assignment_id"]))
    merged_out.to_csv(args.out_csv, index=False)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
