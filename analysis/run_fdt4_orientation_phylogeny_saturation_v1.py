#!/usr/bin/env python3
"""Exhaust public phylogeny/topology sensitivity for FDT4 orientation-climate correspondence.

Layers are kept distinct:
1) all optimized candidate topologies, with AU-nonrejected candidates flagged;
2) concatenated-data ultrafast-bootstrap trees;
3) individual public Comp1061 locus trees (complete-panel primary and varying-panel exploratory);
4) an optional independently published topology encoded with equal branch lengths.

P<0.05 fractions across bootstrap/gene trees are descriptive only. They are never
interpreted as independent replications. Equal-branch analyses isolate topology from
branch-length geometry. Branch-length-aware locus-tree analyses are explicitly a
single-locus covariance stress test, not a preferred species-level Brownian model.
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

AXES = ["chelsa_bio01", "chelsa_bio15"]
EXPECTED_SIGN = {"chelsa_bio01": -1, "chelsa_bio15": 1}


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--japan-occ", type=Path, required=True)
    p.add_argument("--taiwan-gbif", type=Path, required=True)
    p.add_argument("--tbn-native", type=Path, required=True)
    p.add_argument("--tbn-broad", type=Path, required=True)
    p.add_argument("--orientation", type=Path, required=True)
    p.add_argument("--au-trees", type=Path, required=True)
    p.add_argument("--accepted-count", type=int, default=6)
    p.add_argument("--ufboot-trees", type=Path, required=True)
    p.add_argument("--gene-trees", type=Path, required=True)
    p.add_argument("--independent-tree", type=Path)
    p.add_argument("--independent-label", default="independent_equal_branch_topology")
    p.add_argument("--min-n", type=int, default=10)
    p.add_argument("--out-dir", type=Path, required=True)
    return p.parse_args()


def norm(x: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]+", "", x.replace(" ", "_").replace(".", ""))


def read_tree(line: str):
    line = line.strip()
    if line.startswith("[") and "]" in line:
        line = line.split("]", 1)[1].strip()
    tr = Phylo.read(StringIO(line), "newick")
    names = {x.name for x in tr.get_terminals()}
    if "OUTGROUP_saff" in names:
        tr.root_with_outgroup({"name": "OUTGROUP_saff"})
    return tr


def read_trees(path: Path):
    return [read_tree(x) for x in path.read_text().splitlines() if x.strip()]


def states_from_file(path: Path):
    d = pd.read_csv(path)
    d = d[d["analysis_state"].isin(["U", "D"])]
    return dict(zip(d["accepted_taxon"], d["analysis_state"]))


def build_panels(args, states):
    j = pd.read_csv(args.japan_occ)
    tw = pd.read_csv(args.taiwan_gbif)
    native = pd.read_csv(args.tbn_native)
    broad = pd.read_csv(args.tbn_broad)
    panels = {
        "gbif": [j, tw],
        "native_tbn": [j, tw, native],
        "broad_non_gbif_tbn": [j, tw, broad],
    }
    out = {}
    for name, frames in panels.items():
        d = pd.concat(frames, ignore_index=True)
        if "environment_complete" in d.columns:
            d = d[d["environment_complete"].astype(bool)].copy()
        counts = d.groupby("scientific_name_query").size()
        taxa = sorted(t for t, n in counts.items() if n >= args.min_n and t in states)
        cent = d.groupby("scientific_name_query")[AXES].mean().loc[taxa]
        state = np.array([0.0 if states[t] == "U" else 1.0 for t in taxa])
        out[name] = {
            "data": d,
            "taxa": taxa,
            "centroids": cent,
            "state": state,
            "n_U": int((state == 0).sum()),
            "n_D": int((state == 1).sum()),
        }
    return out


def equalize(tr):
    tr = Phylo.read(StringIO(tr.format("newick")), "newick")
    for cl in tr.find_clades(order="level"):
        if cl is tr.root:
            continue
        cl.branch_length = 1.0
    return tr


def covariance(tr, taxa, equal=False):
    if equal:
        tr = equalize(tr)
    terms = {x.name: x for x in tr.get_terminals()}
    missing = [t for t in taxa if norm(t) not in terms]
    if missing:
        raise KeyError(missing)
    tips = [terms[norm(t)] for t in taxa]
    root = tr.common_ancestor(tips)
    n = len(tips)
    cov = np.zeros((n, n), float)
    for i, a in enumerate(tips):
        for j, b in enumerate(tips):
            if i == j:
                cov[i, j] = tr.distance(root, a)
            else:
                mrca = tr.common_ancestor(a, b)
                cov[i, j] = tr.distance(root, mrca) if mrca != root else 0.0
    scale = max(float(np.nanmax(np.diag(cov))), 1.0)
    cov += np.eye(n) * scale * 1e-8
    return cov


def fit_pgls(y, state, cov):
    X = np.column_stack([np.ones(len(state)), state])
    inv = np.linalg.pinv(cov, rcond=1e-10)
    matrix = X.T @ inv @ X
    beta = np.linalg.pinv(matrix, rcond=1e-10) @ (X.T @ inv @ y)
    resid = y - X @ beta
    dof = len(y) - 2
    if dof <= 0:
        raise ValueError("need >=3 taxa")
    sigma2 = float(resid.T @ inv @ resid / dof)
    vcov = sigma2 * np.linalg.pinv(matrix, rcond=1e-10)
    se = float(np.sqrt(max(float(vcov[1, 1]), 0.0)))
    if se <= 0 or not math.isfinite(se):
        return float(beta[1]), se, float("nan")
    tval = float(beta[1] / se)
    return float(beta[1]), se, float(2 * student_t.sf(abs(tval), dof))


def fit_tree(tr, taxa, centroids, state, mode):
    cov = covariance(tr, taxa, equal=(mode == "equal"))
    rows = []
    for axis in AXES:
        raw = centroids.loc[taxa, axis].to_numpy(float)
        sd = float(np.std(raw, ddof=1))
        if not np.isfinite(sd) or sd <= 0:
            continue
        y = (raw - float(np.mean(raw))) / sd
        beta, se, pval = fit_pgls(y, state, cov)
        rows.append((axis, beta, se, pval))
    return rows


def qsummary(q):
    if q.empty:
        return {"n": 0}
    return {
        "n": int(len(q)),
        "expected_sign_rate": float((np.sign(q["beta"]) == q["axis"].map(EXPECTED_SIGN)).mean()),
        "beta_range": [float(q.beta.min()), float(q.beta.max())],
        "beta_q05_q50_q95": [float(q.beta.quantile(x)) for x in (0.05, 0.5, 0.95)],
        "p_range": [float(q.p.min()), float(q.p.max())],
        "p_q05_q50_q95": [float(q.p.quantile(x)) for x in (0.05, 0.5, 0.95)],
        "p_lt_0_05_fraction_descriptive": float((q.p < 0.05).mean()),
    }


def main():
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    states = states_from_file(args.orientation)
    panels = build_panels(args, states)
    au = read_trees(args.au_trees)
    boots = read_trees(args.ufboot_trees)
    genes = read_trees(args.gene_trees)
    rows = []
    coverage_rows = []

    def run_ensemble(label, trees, complete_required=True, accepted_boundary=None):
        for tree_i, tr in enumerate(trees, 1):
            names = {x.name for x in tr.get_terminals()}
            for panel, pdata in panels.items():
                full = pdata["taxa"]
                present = [t for t in full if norm(t) in names]
                complete = len(present) == len(full)
                present_states = [states[t] for t in present]
                estimable = len(present) >= 6 and len(set(present_states)) >= 2
                coverage_rows.append({
                    "ensemble": label,
                    "tree_index": tree_i,
                    "panel": panel,
                    "n_present": len(present),
                    "n_full": len(full),
                    "complete": complete,
                    "estimable": estimable,
                })
                if not estimable or (complete_required and not complete):
                    continue
                centroids = pdata["centroids"].loc[present]
                state = np.array([0.0 if states[t] == "U" else 1.0 for t in present])
                for mode in ("branch", "equal"):
                    try:
                        fitted = fit_tree(tr, present, centroids, state, mode)
                    except Exception:
                        continue
                    for axis, beta, se, pval in fitted:
                        rows.append({
                            "ensemble": label,
                            "tree_index": tree_i,
                            "accepted": (tree_i <= accepted_boundary) if accepted_boundary else None,
                            "panel": panel,
                            "complete": complete,
                            "mode": mode,
                            "axis": axis,
                            "n_taxa": len(present),
                            "n_U": int((state == 0).sum()),
                            "n_D": int((state == 1).sum()),
                            "beta": beta,
                            "se": se,
                            "p": pval,
                        })

    run_ensemble("au_candidates", au, complete_required=True, accepted_boundary=args.accepted_count)
    run_ensemble("concatenated_ufboot", boots, complete_required=True)
    run_ensemble("locus_tree_complete", genes, complete_required=True)
    run_ensemble("locus_tree_estimable", genes, complete_required=False)

    if args.independent_tree and args.independent_tree.exists():
        run_ensemble(args.independent_label, read_trees(args.independent_tree), complete_required=False)

    results = pd.DataFrame(rows)
    coverage = pd.DataFrame(coverage_rows)
    results.to_csv(args.out_dir / "orientation_phylogeny_saturation_by_tree_v1.csv", index=False)
    coverage.to_csv(args.out_dir / "orientation_phylogeny_saturation_tree_coverage_v1.csv", index=False)

    payload = {
        "contract_version": "fdt4_orientation_phylogeny_saturation_v1",
        "estimand": "sign and magnitude stability of present-day BIO1/BIO15 orientation correspondence across separable public phylogenetic uncertainty layers",
        "panel_gate": f">={args.min_n} independent thinned environment-complete occurrences per taxon",
        "panels": {
            k: {"n_taxa": len(v["taxa"]), "n_U": v["n_U"], "n_D": v["n_D"], "taxa": v["taxa"]}
            for k, v in panels.items()
        },
        "ensemble_sizes": {
            "au_candidates": len(au),
            "au_nonrejected": args.accepted_count,
            "concatenated_ufboot": len(boots),
            "public_locus_trees": len(genes),
        },
        "layers": {},
        "claim_boundaries": [
            "AU-rejected candidates are adversarial stress tests, not equal-weight accepted trees.",
            "Ultrafast-bootstrap trees are resamples of one concatenated matrix, not independent phylogenetic datasets.",
            "Locus-tree P-value fractions are descriptive and not independent replications.",
            "Equal-branch locus-tree analysis isolates topology; branch-length-aware locus-tree analysis is a covariance-geometry stress test because single-locus branch lengths are noisy species-level distance estimators.",
            "Independent published topologies are used only at their overlapping taxa and do not justify grafting heterogeneous marker systems into one tree.",
            "No layer establishes adaptation, historical niche causation, convergence or fitness effects.",
        ],
    }

    for ensemble in results.ensemble.unique():
        payload["layers"][ensemble] = {}
        for panel in panels:
            payload["layers"][ensemble][panel] = {}
            for mode in ("branch", "equal"):
                z = results[(results.ensemble == ensemble) & (results.panel == panel) & (results["mode"] == mode)]
                if z.empty:
                    continue
                payload["layers"][ensemble][panel][mode] = {
                    axis: qsummary(z[z.axis == axis].copy()) for axis in AXES
                }
                if ensemble == "au_candidates":
                    payload["layers"][ensemble][panel][mode]["accepted6"] = {
                        axis: qsummary(z[(z.axis == axis) & (z.accepted == True)].copy()) for axis in AXES
                    }
                    payload["layers"][ensemble][panel][mode]["rejected3"] = {
                        axis: qsummary(z[(z.axis == axis) & (z.accepted == False)].copy()) for axis in AXES
                    }

    payload["locus_tree_coverage"] = {}
    locus_cov = coverage[coverage.ensemble == "locus_tree_complete"]
    for panel in panels:
        z = locus_cov[locus_cov.panel == panel]
        payload["locus_tree_coverage"][panel] = {
            "complete_panel_gene_trees": int(z[z.complete].tree_index.nunique()),
            "estimable_gene_trees": int(z[z.estimable].tree_index.nunique()),
            "n_present_distribution": {str(k): int(v) for k, v in z.n_present.value_counts().sort_index().items()},
        }

    (args.out_dir / "fdt4_orientation_phylogeny_saturation_v1.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
