#!/usr/bin/env python3
"""Partition precipitation amount and seasonality in the orientation ecology result.

This analysis answers a narrow cross-scale question: does the current EAzami
orientation signal track annual precipitation amount (BIO12), precipitation
seasonality (BIO15), or a direction that survives adjustment for the other axis?

The script deliberately keeps phylogenetic uncertainty layers separate:

* optimized Comp1061 branch-length realizations;
* concatenated UFBoot topology resamples with equalized branches;
* public single-locus topologies, both equalized and as a branch-length stress test;
* external/coalescent topologies with equalized branches.

Partial models are small-panel diagnostics. They are not causal models and do not
turn present-day niche centroids into historical transition environments.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from io import StringIO
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from Bio import Phylo
from scipy.stats import t as student_t

BIO12 = "chelsa_bio12"
BIO15 = "chelsa_bio15"
AXES = [BIO12, BIO15]
MODEL_SPECS = {
    "bio12_unadjusted": (BIO12, None),
    "bio15_unadjusted": (BIO15, None),
    "bio12_adjusted_bio15": (BIO12, BIO15),
    "bio15_adjusted_bio12": (BIO15, BIO12),
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--japan-occ", type=Path, required=True)
    p.add_argument("--taiwan-gbif", type=Path, required=True)
    p.add_argument("--tbn-native", type=Path, required=True)
    p.add_argument("--tbn-broad", type=Path, required=True)
    p.add_argument(
        "--extra-panel",
        nargs=2,
        action="append",
        metavar=("LABEL", "UNION_CSV"),
        default=[],
        help="Additional already-deduplicated occurrence union supplied as one CSV.",
    )
    p.add_argument("--orientation", type=Path, required=True)
    p.add_argument("--au-trees", type=Path, required=True)
    p.add_argument("--accepted-count", type=int, default=6)
    p.add_argument("--ufboot-trees", type=Path, required=True)
    p.add_argument("--gene-trees", type=Path, required=True)
    p.add_argument(
        "--extra-tree",
        nargs=2,
        action="append",
        metavar=("LABEL", "PATH"),
        default=[],
    )
    p.add_argument("--min-n", type=int, default=10)
    p.add_argument("--out-dir", type=Path, required=True)
    return p.parse_args()


def norm(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]+", "", value.replace(" ", "_").replace(".", ""))


def as_bool(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    return series.astype(str).str.strip().str.casefold().isin({"true", "1", "yes"})


def read_tree(line: str):
    line = line.strip()
    if line.startswith("[") and "]" in line:
        line = line.split("]", 1)[1].strip()
    tree = Phylo.read(StringIO(line), "newick")
    if "OUTGROUP_saff" in {x.name for x in tree.get_terminals()}:
        tree.root_with_outgroup({"name": "OUTGROUP_saff"})
    return tree


def read_trees(path: Path) -> list:
    return [read_tree(line) for line in path.read_text().splitlines() if line.strip()]


def read_occurrence_union(paths: Iterable[Path]) -> pd.DataFrame:
    frames = []
    for path in paths:
        frame = pd.read_csv(path)
        if "environment_complete" in frame.columns:
            frame = frame.loc[as_bool(frame["environment_complete"])].copy()
        missing = [c for c in ("scientific_name_query", BIO12, BIO15) if c not in frame.columns]
        if missing:
            raise ValueError(f"{path} missing required columns {missing}")
        frames.append(frame)
    out = pd.concat(frames, ignore_index=True)
    # The source workflows already spatially thin and deduplicate each source tier.
    # When a stable record/cell identifier is present, avoid accidental repeated rows
    # created only by concatenating files.
    id_cols = [c for c in ("scientific_name_query", "thin_lat", "thin_lon") if c in out.columns]
    if len(id_cols) == 3:
        out = out.drop_duplicates(id_cols, keep="first")
    return out


def states_from_file(path: Path) -> dict[str, str]:
    frame = pd.read_csv(path)
    frame = frame.loc[frame["analysis_state"].isin(["U", "D"])].copy()
    return dict(zip(frame["accepted_taxon"], frame["analysis_state"]))


def build_panel(frame: pd.DataFrame, states: dict[str, str], min_n: int) -> dict:
    counts = frame.groupby("scientific_name_query").size()
    taxa = sorted(t for t, n in counts.items() if int(n) >= min_n and t in states)
    centroids = frame.groupby("scientific_name_query")[AXES].mean().loc[taxa]
    state = np.array([0.0 if states[t] == "U" else 1.0 for t in taxa], dtype=float)
    if len(taxa) < 6 or len(set(state)) < 2:
        raise ValueError(f"panel is not estimable: n={len(taxa)}, states={sorted(set(state))}")
    return {
        "taxa": taxa,
        "centroids": centroids,
        "state": state,
        "n_U": int((state == 0).sum()),
        "n_D": int((state == 1).sum()),
        "counts": {t: int(counts[t]) for t in taxa},
    }


def equalize(tree):
    clone = Phylo.read(StringIO(tree.format("newick")), "newick")
    for clade in clone.find_clades(order="level"):
        if clade is not clone.root:
            clade.branch_length = 1.0
    return clone


def complete_branch_lengths(tree) -> bool:
    values = [c.branch_length for c in tree.find_clades() if c is not tree.root]
    return bool(values) and all(v is not None and math.isfinite(float(v)) for v in values)


def brownian_covariance(tree, taxa: list[str], *, equal_branch: bool) -> np.ndarray:
    tree = equalize(tree) if equal_branch else tree
    if not equal_branch and not complete_branch_lengths(tree):
        raise ValueError("branch-aware covariance requested for a tree without complete branch lengths")
    terms = {x.name: x for x in tree.get_terminals()}
    missing = [taxon for taxon in taxa if norm(taxon) not in terms]
    if missing:
        raise KeyError(missing)
    tips = [terms[norm(t)] for t in taxa]
    root = tree.common_ancestor(tips)
    cov = np.zeros((len(tips), len(tips)), dtype=float)
    for i, a in enumerate(tips):
        for j, b in enumerate(tips):
            if i == j:
                cov[i, j] = tree.distance(root, a)
            else:
                mrca = tree.common_ancestor(a, b)
                cov[i, j] = tree.distance(root, mrca) if mrca != root else 0.0
    scale = max(float(np.nanmax(np.diag(cov))), 1.0)
    cov += np.eye(len(tips)) * scale * 1e-8
    return cov


def standardize(values: np.ndarray) -> np.ndarray:
    sd = float(np.std(values, ddof=1))
    if not math.isfinite(sd) or sd <= 0:
        raise ValueError("non-variable environmental axis")
    return (values - float(np.mean(values))) / sd


def fit_state_gls(y: np.ndarray, state: np.ndarray, cov: np.ndarray, covariate: np.ndarray | None) -> dict:
    columns = [np.ones(len(state)), state]
    if covariate is not None:
        columns.append(covariate)
    X = np.column_stack(columns)
    dof = len(y) - X.shape[1]
    if dof <= 0:
        raise ValueError("insufficient degrees of freedom")
    inv = np.linalg.pinv(cov, rcond=1e-10)
    information = X.T @ inv @ X
    information_inv = np.linalg.pinv(information, rcond=1e-10)
    beta = information_inv @ (X.T @ inv @ y)
    residual = y - X @ beta
    sigma2 = float(residual.T @ inv @ residual / dof)
    vcov = sigma2 * information_inv
    se = float(np.sqrt(max(float(vcov[1, 1]), 0.0)))
    t_value = float(beta[1] / se) if se > 0 else float("nan")
    p_value = float(2 * student_t.sf(abs(t_value), dof)) if math.isfinite(t_value) else float("nan")
    condition = float(np.linalg.cond(information))
    return {
        "beta_state_D_minus_U_sd": float(beta[1]),
        "se": se,
        "p": p_value,
        "dof": int(dof),
        "information_condition_number": condition,
    }


def topology_signature(tree, taxa: list[str]) -> str:
    clone = Phylo.read(StringIO(tree.format("newick")), "newick")
    keep = {norm(t) for t in taxa}
    for terminal in list(clone.get_terminals()):
        if terminal.name not in keep:
            try:
                clone.prune(terminal)
            except ValueError:
                pass
    present = {x.name for x in clone.get_terminals()}
    splits = []
    for clade in clone.get_nonterminals(order="preorder"):
        side = frozenset(x.name for x in clade.get_terminals())
        if len(side) <= 1 or len(side) >= len(present) - 1:
            continue
        other = frozenset(present - side)
        splits.append(min(tuple(sorted(side)), tuple(sorted(other))))
    return json.dumps(sorted(splits), separators=(",", ":"))


def model_rows(tree, panel: dict, mode: str) -> list[dict]:
    taxa = panel["taxa"]
    centroids = panel["centroids"].loc[taxa]
    state = panel["state"]
    cov = brownian_covariance(tree, taxa, equal_branch=(mode == "equal"))
    z = {axis: standardize(centroids[axis].to_numpy(float)) for axis in AXES}
    rows = []
    for model_name, (response, adjuster) in MODEL_SPECS.items():
        fitted = fit_state_gls(z[response], state, cov, z[adjuster] if adjuster else None)
        rows.append(
            {
                "model": model_name,
                "response_axis": response,
                "adjustment_axis": adjuster or "",
                **fitted,
            }
        )
    return rows


def summarize(frame: pd.DataFrame, reference_sign: int) -> dict:
    if frame.empty:
        return {"n": 0}
    beta = frame["beta_state_D_minus_U_sd"]
    p = frame["p"]
    cond = frame["information_condition_number"]
    return {
        "n": int(len(frame)),
        "reference_sign": int(reference_sign),
        "reference_sign_rate": float((np.sign(beta) == reference_sign).mean()),
        "beta_range": [float(beta.min()), float(beta.max())],
        "beta_q05_q50_q95": [float(beta.quantile(q)) for q in (0.05, 0.5, 0.95)],
        "p_range": [float(p.min()), float(p.max())],
        "p_q05_q50_q95": [float(p.quantile(q)) for q in (0.05, 0.5, 0.95)],
        "p_lt_0_05_fraction_descriptive": float((p < 0.05).mean()),
        "information_condition_number_q50_q95_max": [
            float(cond.quantile(0.5)),
            float(cond.quantile(0.95)),
            float(cond.max()),
        ],
    }


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    states = states_from_file(args.orientation)

    japan = args.japan_occ
    taiwan = args.taiwan_gbif
    panels = {
        "gbif": build_panel(read_occurrence_union([japan, taiwan]), states, args.min_n),
        "native_tbn": build_panel(read_occurrence_union([japan, taiwan, args.tbn_native]), states, args.min_n),
        "broad_non_gbif_tbn": build_panel(read_occurrence_union([japan, taiwan, args.tbn_broad]), states, args.min_n),
    }
    for label, path in args.extra_panel:
        if label in panels:
            raise ValueError(f"duplicate panel label {label}")
        panels[label] = build_panel(read_occurrence_union([Path(path)]), states, args.min_n)

    ensembles: list[tuple[str, list, tuple[str, ...], bool, int | None]] = [
        ("au_candidates", read_trees(args.au_trees), ("branch", "equal"), True, args.accepted_count),
        ("concatenated_ufboot", read_trees(args.ufboot_trees), ("equal",), True, None),
        ("public_locus_trees_complete", read_trees(args.gene_trees), ("branch", "equal"), True, None),
    ]
    for label, path in args.extra_tree:
        ensembles.append((label, read_trees(Path(path)), ("equal",), False, None))

    result_rows: list[dict] = []
    coverage_rows: list[dict] = []
    signatures: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))

    for ensemble, trees, modes, require_complete, accepted_count in ensembles:
        for tree_index, tree in enumerate(trees, start=1):
            tree_names = {x.name for x in tree.get_terminals()}
            for panel_name, panel in panels.items():
                full_taxa = panel["taxa"]
                present = [t for t in full_taxa if norm(t) in tree_names]
                complete = len(present) == len(full_taxa)
                estimable = len(present) >= 6 and len({states[t] for t in present}) >= 2
                coverage_rows.append(
                    {
                        "ensemble": ensemble,
                        "tree_index": tree_index,
                        "panel": panel_name,
                        "n_present": len(present),
                        "n_full": len(full_taxa),
                        "complete": complete,
                        "estimable": estimable,
                        "branch_lengths_complete": complete_branch_lengths(tree),
                    }
                )
                if not estimable or (require_complete and not complete):
                    continue
                local_panel = panel
                if not complete:
                    indices = [full_taxa.index(t) for t in present]
                    local_panel = {
                        "taxa": present,
                        "centroids": panel["centroids"].loc[present],
                        "state": panel["state"][indices],
                    }
                signatures[ensemble][panel_name].append(topology_signature(tree, present))
                for mode in modes:
                    try:
                        rows = model_rows(tree, local_panel, mode)
                    except Exception:
                        continue
                    for row in rows:
                        result_rows.append(
                            {
                                "ensemble": ensemble,
                                "tree_index": tree_index,
                                "accepted": (tree_index <= accepted_count) if accepted_count else None,
                                "panel": panel_name,
                                "mode": mode,
                                "complete": complete,
                                "n_taxa": len(present),
                                "n_U": int((local_panel["state"] == 0).sum()),
                                "n_D": int((local_panel["state"] == 1).sum()),
                                **row,
                            }
                        )

    results = pd.DataFrame(result_rows)
    coverage = pd.DataFrame(coverage_rows)
    results.to_csv(args.out_dir / "orientation_precipitation_partition_by_tree_v1.csv", index=False)
    coverage.to_csv(args.out_dir / "orientation_precipitation_partition_tree_coverage_v1.csv", index=False)

    payload: dict = {
        "contract_version": "fdt4_orientation_precipitation_partition_v1",
        "estimand": "orientation correspondence with precipitation amount and seasonality before and after mutual adjustment",
        "model_specs": {
            name: {"response": response, "adjustment": adjuster}
            for name, (response, adjuster) in MODEL_SPECS.items()
        },
        "panels": {},
        "ensembles": {},
        "topology_diversity": {},
        "claim_boundaries": [
            "BIO12 annual precipitation and BIO15 precipitation seasonality are related but non-equivalent estimands.",
            "Partial PGLS fits are low-n diagnostics, not causal decomposition.",
            "UFBoot and locus trees are uncertainty realizations, not independent ecological replications.",
            "Single-locus branch-length fits are covariance-geometry stress tests, not preferred species-tree distances.",
            "Present-day taxon centroids are not ancestral environments or event-specific exposure histories.",
            "Cross-scale adaptation language requires independent functional or fitness evidence.",
        ],
    }

    for panel_name, panel in panels.items():
        raw_corr = float(panel["centroids"][BIO12].corr(panel["centroids"][BIO15]))
        payload["panels"][panel_name] = {
            "n_taxa": len(panel["taxa"]),
            "n_U": panel["n_U"],
            "n_D": panel["n_D"],
            "taxa": panel["taxa"],
            "occurrence_counts": panel["counts"],
            "taxon_centroid_pearson_bio12_bio15": raw_corr,
        }

    # Reference signs are frozen to the median branch-aware AU result within each
    # panel/model. They summarize perturbation stability rather than define truth.
    reference_signs: dict[tuple[str, str], int] = {}
    for panel_name in panels:
        for model_name in MODEL_SPECS:
            ref = results[
                (results["ensemble"] == "au_candidates")
                & (results["panel"] == panel_name)
                & (results["mode"] == "branch")
                & (results["model"] == model_name)
                & (results["accepted"] == True)
            ]
            if ref.empty:
                ref = results[(results["panel"] == panel_name) & (results["model"] == model_name)]
            median = float(ref["beta_state_D_minus_U_sd"].median())
            reference_signs[(panel_name, model_name)] = 1 if median >= 0 else -1

    for ensemble in sorted(results["ensemble"].unique()):
        payload["ensembles"][ensemble] = {}
        for panel_name in panels:
            payload["ensembles"][ensemble][panel_name] = {}
            for mode in ("branch", "equal"):
                subset = results[
                    (results["ensemble"] == ensemble)
                    & (results["panel"] == panel_name)
                    & (results["mode"] == mode)
                ]
                if subset.empty:
                    continue
                payload["ensembles"][ensemble][panel_name][mode] = {}
                for model_name in MODEL_SPECS:
                    q = subset[subset["model"] == model_name]
                    payload["ensembles"][ensemble][panel_name][mode][model_name] = summarize(
                        q, reference_signs[(panel_name, model_name)]
                    )

    for ensemble, by_panel in signatures.items():
        payload["topology_diversity"][ensemble] = {}
        for panel_name, values in by_panel.items():
            counts = Counter(values)
            payload["topology_diversity"][ensemble][panel_name] = {
                "trees_with_estimable_signature": len(values),
                "unique_induced_topologies": len(counts),
                "largest_topology_frequency": max(counts.values()) if counts else 0,
            }

    # A compact sign-retention diagnostic for the two partial models.
    payload["partial_axis_diagnostic"] = {}
    for panel_name in panels:
        payload["partial_axis_diagnostic"][panel_name] = {}
        for model_name in ("bio12_adjusted_bio15", "bio15_adjusted_bio12"):
            layers = {}
            for ensemble, mode in (
                ("concatenated_ufboot", "equal"),
                ("public_locus_trees_complete", "equal"),
            ):
                q = results[
                    (results["ensemble"] == ensemble)
                    & (results["panel"] == panel_name)
                    & (results["mode"] == mode)
                    & (results["model"] == model_name)
                ]
                layers[f"{ensemble}:{mode}"] = summarize(q, reference_signs[(panel_name, model_name)])
            payload["partial_axis_diagnostic"][panel_name][model_name] = layers

    (args.out_dir / "fdt4_orientation_precipitation_partition_v1.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
