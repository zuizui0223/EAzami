#!/usr/bin/env python3
"""Phylogeny-corrected orientation × present-day niche screen across accepted topologies.

This is an FDT4 screening analysis, not a historical-range or adaptation test.
It combines taxon-level climate centroids with fixed binary orientation states and
fits a Brownian PGLS separately on every AU-nonrejected optimized topology.

Expected tree input is IQ-TREE ``au.trees``. Only the first N trees declared by
``--nonrejected-count`` are used; for the frozen Comp1061 AU result N=6.
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


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--occurrences", type=Path, nargs="+", required=True)
    p.add_argument("--orientation", type=Path, required=True)
    p.add_argument("--au-trees", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--min-n", type=int, default=10)
    p.add_argument("--nonrejected-count", type=int, default=6)
    return p.parse_args()


def normalize_tip(taxon: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]+", "", taxon.replace(" ", "_").replace(".", ""))


def read_optimized_trees(path: Path, n: int):
    trees = []
    lines = [x.strip() for x in path.read_text().splitlines() if x.strip()]
    if len(lines) < n:
        raise ValueError(f"Need at least {n} optimized trees, found {len(lines)}")
    for line in lines[:n]:
        if line.startswith("[") and "]" in line:
            line = line.split("]", 1)[1].strip()
        tree = Phylo.read(StringIO(line), "newick")
        names = {t.name for t in tree.get_terminals()}
        if "OUTGROUP_saff" not in names:
            raise ValueError("OUTGROUP_saff missing from optimized topology")
        tree.root_with_outgroup({"name": "OUTGROUP_saff"})
        trees.append(tree)
    return trees


def brownian_covariance(tree, tip_names: list[str]) -> np.ndarray:
    terminals = {x.name: x for x in tree.get_terminals()}
    missing = [x for x in tip_names if x not in terminals]
    if missing:
        raise ValueError(f"Tips absent from topology: {missing}")
    tips = [terminals[x] for x in tip_names]
    ingroup_root = tree.common_ancestor(tips)
    n = len(tips)
    cov = np.zeros((n, n), dtype=float)
    for i, a in enumerate(tips):
        for j, b in enumerate(tips):
            if i == j:
                cov[i, j] = tree.distance(ingroup_root, a)
            else:
                mrca = tree.common_ancestor(a, b)
                cov[i, j] = tree.distance(ingroup_root, mrca) if mrca != ingroup_root else 0.0
    cov += np.eye(n) * 1e-10
    return cov


def fit_pgls(y: np.ndarray, state: np.ndarray, cov: np.ndarray) -> dict[str, float]:
    X = np.column_stack([np.ones(len(state)), state])
    inv = np.linalg.inv(cov)
    xtvi = X.T @ inv
    beta = np.linalg.solve(xtvi @ X, xtvi @ y)
    resid = y - X @ beta
    dof = len(y) - X.shape[1]
    if dof <= 0:
        raise ValueError("PGLS needs at least three taxa")
    sigma2 = float(resid.T @ inv @ resid / dof)
    cov_beta = sigma2 * np.linalg.inv(xtvi @ X)
    se = np.sqrt(np.diag(cov_beta))
    t_value = float(beta[1] / se[1])
    p_value = float(2 * student_t.sf(abs(t_value), dof))
    return {"beta_D_minus_U_sd": float(beta[1]), "se": float(se[1]), "t": t_value, "p": p_value, "dof": int(dof), "sigma2": sigma2}


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    occurrence_frames = [pd.read_csv(p) for p in args.occurrences]
    occ = pd.concat(occurrence_frames, ignore_index=True)
    if "environment_complete" in occ.columns:
        occ = occ.loc[occ["environment_complete"].astype(bool)].copy()
    counts = occ.groupby("scientific_name_query").size()
    usable = counts[counts >= args.min_n].index.tolist()
    orientation = pd.read_csv(args.orientation)
    orientation = orientation.loc[orientation["analysis_state"].isin(["U", "D"])].copy()
    state_by_taxon = dict(zip(orientation["accepted_taxon"], orientation["analysis_state"]))
    usable = sorted(t for t in usable if t in state_by_taxon)
    if len(usable) < 6:
        raise ValueError(f"Too few usable resolved taxa: {len(usable)}")
    centroids = occ.groupby("scientific_name_query")[AXES].mean().loc[usable]
    state = np.array([0.0 if state_by_taxon[t] == "U" else 1.0 for t in usable])
    tip_names = [normalize_tip(t) for t in usable]
    trees = read_optimized_trees(args.au_trees, args.nonrejected_count)
    rows = []
    for tree_i, tree in enumerate(trees, start=1):
        cov = brownian_covariance(tree, tip_names)
        for axis in AXES:
            y = centroids[axis].to_numpy(dtype=float)
            sd = float(np.std(y, ddof=1))
            if not np.isfinite(sd) or sd <= 0:
                continue
            y = (y - float(np.mean(y))) / sd
            result = fit_pgls(y, state, cov)
            rows.append({"topology_index": tree_i, "axis": axis, "n_taxa": len(usable), "n_U": int((state == 0).sum()), "n_D": int((state == 1).sum()), **result})
    result_df = pd.DataFrame(rows)
    result_df.to_csv(args.out_dir / "fdt4_orientation_niche_pgls_by_topology_v1.csv", index=False)
    summary = result_df.groupby("axis").agg(beta_min=("beta_D_minus_U_sd", "min"), beta_max=("beta_D_minus_U_sd", "max"), p_min=("p", "min"), p_max=("p", "max")).reset_index()
    summary.to_csv(args.out_dir / "fdt4_orientation_niche_pgls_summary_v1.csv", index=False)
    payload = {"contract_version": "fdt4_orientation_niche_pgls_v1", "usable_taxa": usable, "n_taxa": len(usable), "n_U": int((state == 0).sum()), "n_D": int((state == 1).sum()), "topologies_propagated": args.nonrejected_count, "min_occurrence_n_per_taxon": args.min_n, "axes": AXES, "interpretation_boundary": "Present-day taxon niche centroids tested with Brownian phylogenetic covariance. This is a topology-sensitive screening association, not ancestral niche reconstruction, historical range inference, parallel adaptation, or causal evidence."}
    (args.out_dir / "fdt4_orientation_niche_pgls_manifest_v1.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
