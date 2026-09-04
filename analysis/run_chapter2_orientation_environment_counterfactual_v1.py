#!/usr/bin/env python3
"""Counterfactual orientation-environment falsification for Chapter 2.

Enumerate every 5U/4D assignment across the frozen nine-taxon ecological panel,
recompute PGLS correspondence on the same six accepted topologies, and compare
observed effects with counterfactuals that preserve the observed recurrence
profile and closely match topology-only relative-depth geometry.

This is a post-result sensitivity/falsification analysis. Exact rank fractions
are conditional randomization ranks, not independent confirmatory P values.
"""
from __future__ import annotations

import argparse
import copy
import csv
import itertools
import json
import math
import statistics
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd
from Bio import Phylo
from scipy.stats import t as student_t

AXES = ("chelsa_bio15", "chelsa_bio01")
TOL = 1e-12


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--contract", type=Path, required=True)
    p.add_argument("--occurrences", type=Path, nargs="+", required=True)
    p.add_argument("--orientation", type=Path, required=True)
    p.add_argument("--au-trees", type=Path, required=True)
    p.add_argument("--frozen-ecology", type=Path, required=True)
    p.add_argument("--out-json", type=Path, required=True)
    p.add_argument("--out-csv", type=Path, required=True)
    return p.parse_args()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_tip(x: str) -> str:
    import re
    return re.sub(r"[^A-Za-z0-9_]+", "", x.replace(" ", "_").replace(".", ""))


def read_trees(path: Path, n: int):
    lines = [x.strip() for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    if len(lines) < n:
        raise ValueError(f"need {n} trees, found {len(lines)}")
    trees = []
    for line in lines[:n]:
        if line.startswith("[") and "]" in line:
            line = line.split("]", 1)[1].strip()
        tree = Phylo.read(StringIO(line), "newick")
        tree.root_with_outgroup({"name": "OUTGROUP_saff"})
        trees.append(tree)
    return trees


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


def fit_gls(y: np.ndarray, state: np.ndarray, cov: np.ndarray) -> tuple[float, float, float]:
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


def descendant_counts(tree) -> dict:
    counts = {}
    def walk(node):
        if node.is_terminal():
            counts[node] = 1
            return 1
        total = sum(walk(c) for c in node.clades)
        counts[node] = total
        return total
    walk(tree.root)
    return counts


def solve_secondary_bound(tree, state_map: dict[str, set[int]], maximize: bool) -> tuple[int, float]:
    states = (0, 1)
    counts = descendant_counts(tree)
    n = counts[tree.root]
    if n < 2:
        raise ValueError("history tree requires >=2 tips")

    def edge_depth(child) -> float:
        return (n - counts[child]) / (n - 1)

    inf = 10**9
    down: dict = {}

    def better(candidate, incumbent):
        if incumbent is None:
            return candidate
        if candidate[0] != incumbent[0]:
            return candidate if candidate[0] < incumbent[0] else incumbent
        if maximize:
            return candidate if candidate[1] > incumbent[1] else incumbent
        return candidate if candidate[1] < incumbent[1] else incumbent

    for node in tree.find_clades(order="postorder"):
        if node.is_terminal():
            allowed = state_map[node.name]
            down[node] = {s: ((0, 0.0) if s in allowed else (inf, 0.0)) for s in states}
            continue
        vals = {}
        for parent_state in states:
            total_steps = 0
            total_depth = 0.0
            for child in node.clades:
                chosen = None
                for child_state in states:
                    child_steps, child_depth = down[child][child_state]
                    changed = parent_state != child_state
                    candidate = (
                        child_steps + int(changed),
                        child_depth + (edge_depth(child) if changed else 0.0),
                    )
                    chosen = better(candidate, chosen)
                assert chosen is not None
                total_steps += chosen[0]
                total_depth += chosen[1]
            vals[parent_state] = (total_steps, total_depth)
        down[node] = vals

    best = None
    for s in states:
        best = better(down[tree.root][s], best)
    assert best is not None and best[0] < inf
    return int(best[0]), float(best[1])


def history_metrics(tree, state_map: dict[str, set[int]]) -> dict:
    lo_steps, lo_sum = solve_secondary_bound(tree, state_map, maximize=False)
    hi_steps, hi_sum = solve_secondary_bound(tree, state_map, maximize=True)
    if lo_steps != hi_steps:
        raise AssertionError("Sankoff optimum differs between secondary bounds")
    if lo_steps <= 0:
        raise ValueError("zero-step orientation history is not admissible here")
    return {
        "minimum_steps": lo_steps,
        "lower": lo_sum / lo_steps,
        "upper": hi_sum / hi_steps,
    }


def make_history_tree(tree, orientation_rows: pd.DataFrame):
    t = copy.deepcopy(tree)
    allowed = set(orientation_rows["tip_id"])
    for tip in list(t.get_terminals()):
        if tip.name not in allowed:
            t.prune(tip)
    observed = {x.name for x in t.get_terminals()}
    if observed != allowed:
        raise ValueError(f"orientation history tip mismatch missing={sorted(allowed-observed)} extra={sorted(observed-allowed)}")
    return t


def state_map_from_rows(rows: pd.DataFrame, cf_by_taxon: dict[str, str] | None = None) -> dict[str, set[int]]:
    out = {}
    cf_by_taxon = cf_by_taxon or {}
    for row in rows.to_dict("records"):
        state = cf_by_taxon.get(row["accepted_taxon"], row["analysis_state"])
        if state == "U":
            out[row["tip_id"]] = {0}
        elif state == "D":
            out[row["tip_id"]] = {1}
        else:
            out[row["tip_id"]] = {0, 1}
    return out


def assignment_id(taxa: list[str], d_taxa: set[str]) -> str:
    bits = "".join("D" if t in d_taxa else "U" for t in taxa)
    return bits


def exact_rank_fraction(rows: list[dict], key: str, observed: float) -> dict:
    if not rows:
        return {"status": "not_evaluable", "n": 0}
    n = len(rows)
    count = sum(float(r[key]) >= observed - TOL for r in rows)
    return {"status": "evaluable", "n": n, "count_at_least_observed": count, "fraction": count / n}


def reverse_calibration(rows: list[dict], key: str) -> dict:
    if not rows:
        return {"status": "not_evaluable", "n": 0}
    reverse = [r for r in rows if float(r[key]) < -TOL]
    if not reverse:
        return {"status": "evaluable", "n": len(rows), "opposite_direction_exists": False}
    best = min(reverse, key=lambda r: float(r[key]))
    return {
        "status": "evaluable",
        "n": len(rows),
        "opposite_direction_exists": True,
        "most_reverse_signed_statistic": float(best[key]),
        "assignment_id": best["assignment_id"],
        "d_taxa": best["d_taxa"],
        "depth_distance": float(best["depth_distance"]),
        "recurrence_profile_match": bool(best["recurrence_profile_match"]),
    }


def axis_key(axis: str) -> str:
    return "bio15_signed_median" if axis == "chelsa_bio15" else "bio1_signed_median"


def main() -> int:
    args = parse_args()
    contract = read_json(args.contract)
    if contract.get("status") != "frozen_before_counterfactual_result_inspection":
        raise ValueError("counterfactual contract is not frozen")

    frozen = read_json(args.frozen_ecology)
    if frozen["orientation"]["status"] != "unresolved":
        raise AssertionError("frozen orientation ecology classification drift")

    occ = pd.concat([pd.read_csv(p) for p in args.occurrences], ignore_index=True)
    min_n = 10
    counts = occ.groupby("scientific_name_query").size()
    eligible = set(counts[counts >= min_n].index)
    centroids = occ.groupby("scientific_name_query")[list(AXES)].mean()

    orientation = pd.read_csv(args.orientation)
    resolved = orientation[orientation["analysis_state"].isin(["U", "D"])]
    state_by_taxon = dict(zip(resolved["accepted_taxon"], resolved["analysis_state"]))
    taxa = sorted(eligible & set(state_by_taxon))
    observed_d = {t for t in taxa if state_by_taxon[t] == "D"}
    if len(taxa) != contract["frozen_panel"]["expected_taxa"]:
        raise AssertionError(f"ecology taxon count drift: {len(taxa)}")
    if (len(taxa) - len(observed_d), len(observed_d)) != (5, 4):
        raise AssertionError("observed U/D panel drift")

    trees = read_trees(args.au_trees, contract["frozen_sources"]["accepted_au_topologies"]["topologies_used"])
    covs = [brownian_covariance(t, taxa) for t in trees]
    hist_trees = [make_history_tree(t, orientation) for t in trees]

    y_by_axis = {}
    for axis in AXES:
        raw = centroids.loc[taxa, axis].to_numpy(float)
        y_by_axis[axis] = (raw - raw.mean()) / raw.std(ddof=1)

    assignments = []
    for combo in itertools.combinations(taxa, 4):
        dset = set(combo)
        state = np.array([1.0 if t in dset else 0.0 for t in taxa])
        cf_by_taxon = {t: ("D" if t in dset else "U") for t in taxa}
        hist_state = state_map_from_rows(orientation, cf_by_taxon)
        hist = [history_metrics(t, hist_state) for t in hist_trees]
        betas = {axis: [] for axis in AXES}
        ps = {axis: [] for axis in AXES}
        for cov in covs:
            for axis in AXES:
                beta, _, p = fit_gls(y_by_axis[axis], state, cov)
                betas[axis].append(beta)
                ps[axis].append(p)
        row = {
            "assignment_id": assignment_id(taxa, dset),
            "d_taxa": sorted(dset),
            "observed": dset == observed_d,
            "history": hist,
            "recurrence_profile": [h["minimum_steps"] for h in hist],
            "bio15_betas": betas["chelsa_bio15"],
            "bio1_betas": betas["chelsa_bio01"],
            "bio15_signed_median": float(statistics.median(betas["chelsa_bio15"])),
            "bio1_signed_median": float(-statistics.median(betas["chelsa_bio01"])),
            "bio15_p_range": [float(min(ps["chelsa_bio15"])), float(max(ps["chelsa_bio15"]))],
            "bio1_p_range": [float(min(ps["chelsa_bio01"])), float(max(ps["chelsa_bio01"]))],
        }
        assignments.append(row)

    if len(assignments) != contract["frozen_panel"]["counterfactual_assignments"]:
        raise AssertionError(f"assignment count drift: {len(assignments)}")
    observed_rows = [r for r in assignments if r["observed"]]
    if len(observed_rows) != 1:
        raise AssertionError("observed assignment not uniquely recovered")
    observed = observed_rows[0]

    # Reproduce the frozen observed ecological result exactly before interpreting counterfactuals.
    got15 = observed["bio15_betas"]
    got1 = observed["bio1_betas"]
    f15 = frozen["orientation"]["chelsa_bio15"]["beta_D_minus_U_sd_range"]
    f1 = frozen["orientation"]["chelsa_bio01"]["beta_D_minus_U_sd_range"]
    if abs(min(got15) - f15[0]) > 1e-10 or abs(max(got15) - f15[1]) > 1e-10:
        raise AssertionError(("BIO15 frozen reproduction drift", [min(got15), max(got15)], f15))
    if abs(min(got1) - f1[0]) > 1e-10 or abs(max(got1) - f1[1]) > 1e-10:
        raise AssertionError(("BIO1 frozen reproduction drift", [min(got1), max(got1)], f1))

    obs_profile = observed["recurrence_profile"]
    obs_hist = observed["history"]
    for row in assignments:
        row["recurrence_profile_match"] = row["recurrence_profile"] == obs_profile
        diffs = []
        for cf_h, ob_h in zip(row["history"], obs_hist):
            diffs.append(abs(cf_h["lower"] - ob_h["lower"]) + abs(cf_h["upper"] - ob_h["upper"]))
        row["depth_distance"] = float(statistics.median(diffs))

    all_pool = assignments
    recurrence_pool = [r for r in assignments if r["recurrence_profile_match"]]
    min_pool = int(contract["historical_counterfactual_rule"]["minimum_pool_size"])
    if len(recurrence_pool) >= min_pool:
        ordered = sorted(float(r["depth_distance"]) for r in recurrence_pool)
        k = max(1, math.ceil(len(ordered) * 0.25))
        cutoff = ordered[k - 1]
        history_pool = [r for r in recurrence_pool if float(r["depth_distance"]) <= cutoff + TOL]
    else:
        cutoff = None
        history_pool = []
    history_evaluable = len(history_pool) >= min_pool
    if not history_evaluable:
        history_pool = []

    pools = {
        "all_126_count_preserving": all_pool,
        "recurrence_profile_matched": recurrence_pool if len(recurrence_pool) >= min_pool else [],
        "history_nearest_quartile": history_pool,
    }

    axis_results = {}
    for axis in AXES:
        key = axis_key(axis)
        obs_stat = float(observed[key])
        pool_results = {}
        for pool_name, pool in pools.items():
            rank = exact_rank_fraction(pool, key, obs_stat)
            reverse = reverse_calibration(pool, key)
            topo = []
            if pool:
                for ti in range(len(trees)):
                    if axis == "chelsa_bio15":
                        obs_t = observed["bio15_betas"][ti]
                        vals = [r["bio15_betas"][ti] for r in pool]
                    else:
                        obs_t = -observed["bio1_betas"][ti]
                        vals = [-r["bio1_betas"][ti] for r in pool]
                    c = sum(v >= obs_t - TOL for v in vals)
                    topo.append({"topology_index": ti + 1, "n": len(vals), "count_at_least_observed": c, "fraction": c / len(vals)})
            pool_results[pool_name] = {
                "rank": rank,
                "reverse_world": reverse,
                "topology_rank_fractions": topo,
            }
        axis_results[axis] = {
            "observed_signed_statistic": obs_stat,
            "observed_beta_range": [float(min(observed["bio15_betas"] if axis == "chelsa_bio15" else observed["bio1_betas"])), float(max(observed["bio15_betas"] if axis == "chelsa_bio15" else observed["bio1_betas"]))],
            "pools": pool_results,
        }

    p15_all = axis_results["chelsa_bio15"]["pools"]["all_126_count_preserving"]["rank"]
    p15_rec = axis_results["chelsa_bio15"]["pools"]["recurrence_profile_matched"]["rank"]
    p15_hist = axis_results["chelsa_bio15"]["pools"]["history_nearest_quartile"]["rank"]
    rev_hist = axis_results["chelsa_bio15"]["pools"]["history_nearest_quartile"]["reverse_world"]

    if p15_rec.get("status") != "evaluable":
        classification = "counterfactual_correspondence_not_strengthened_beyond_history"
    elif p15_all["fraction"] <= 0.05 and p15_rec["fraction"] <= 0.05:
        if (
            p15_hist.get("status") == "evaluable"
            and p15_hist["fraction"] <= 0.05
            and rev_hist.get("opposite_direction_exists") is True
        ):
            classification = "counterfactual_correspondence_strongly_strengthened"
        else:
            classification = "counterfactual_correspondence_strengthened_but_history_overlap_remains"
    else:
        classification = "counterfactual_correspondence_not_strengthened_beyond_history"

    result = {
        "version": "chapter2_orientation_environment_counterfactual_result_v1",
        "analysis_role": contract["analysis_role"],
        "classification": classification,
        "panel": {
            "taxa": taxa,
            "observed_d_taxa": sorted(observed_d),
            "n_taxa": len(taxa),
            "n_assignments": len(assignments),
        },
        "frozen_result_reproduction": {
            "bio15_beta_range": [float(min(got15)), float(max(got15))],
            "bio1_beta_range": [float(min(got1)), float(max(got1))],
            "status": "exact_within_1e-10",
        },
        "observed_history": {
            "recurrence_profile_six_topologies": obs_profile,
            "history_metrics": obs_hist,
        },
        "history_matching": {
            "recurrence_profile_matched_n": len(recurrence_pool),
            "history_nearest_cutoff_depth_distance": cutoff,
            "history_nearest_n": len(history_pool),
            "minimum_pool_size": min_pool,
        },
        "axis_results": axis_results,
        "interpretation_boundary": contract["claim_boundary"],
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("w", encoding="utf-8", newline="") as handle:
        fields = [
            "assignment_id", "observed", "d_taxa", "recurrence_profile", "recurrence_profile_match",
            "depth_distance", "bio15_signed_median", "bio1_signed_median",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in assignments:
            writer.writerow({
                "assignment_id": row["assignment_id"],
                "observed": row["observed"],
                "d_taxa": "|".join(row["d_taxa"]),
                "recurrence_profile": "|".join(map(str, row["recurrence_profile"])),
                "recurrence_profile_match": row["recurrence_profile_match"],
                "depth_distance": row["depth_distance"],
                "bio15_signed_median": row["bio15_signed_median"],
                "bio1_signed_median": row["bio1_signed_median"],
            })

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
