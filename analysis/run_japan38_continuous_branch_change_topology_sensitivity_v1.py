#!/usr/bin/env python3
"""Topology-only sensitivity for coordinated continuous capitulum change.

This analysis is a held-out robustness layer for the ML-phylogram branch-change
result produced by ``run_japan38_all_continuous_history_v1.py``.  It asks whether
coordinated branch-wise phenotype change remains positive when branch lengths are
removed and the raw UFBoot topology ensemble is used.

For every bootstrap topology:
  * root on the frozen safflower outgroup;
  * prune unresolved replicated JPN_20 and trait-disallowed JPN_31;
  * prune to the frozen n>=2 common continuous panel;
  * set every non-root branch length to exactly 1.0;
  * reconstruct BM conditional internal states for seven scalar units and circular
    hue components;
  * calculate absolute standardized parent-child change (no time-rate claim);
  * summarize cross-trait Spearman correlation of branch-change magnitude.

The decision rule is frozen in code: global coordinated change is called
``topology_robust_positive`` only when >=95% of usable bootstrap topologies have a
positive global mean pairwise rho and the empirical 5th percentile is >0.  Module
specificity uses the same rule for the within-minus-between module contrast.
"""
from __future__ import annotations

import argparse
import io
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from Bio import Phylo

import run_japan38_colour_continuous_history_pilot_v1 as base
import run_japan38_all_continuous_history_v1 as hist


# Equal-branch pruning creates mathematically tied reconstructed changes.  Raw
# LAPACK round-off can otherwise break those ties differently across runners,
# which changes Spearman ranks and makes the committed diagnostic oscillate.
SPEARMAN_TIE_DECIMALS = 12


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--bridge", type=Path, required=True)
    p.add_argument("--ml-tree", type=Path, required=True)
    p.add_argument("--bootstrap-trees", type=Path, required=True)
    p.add_argument("--concept-map", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--threshold", type=int, default=2)
    return p.parse_args()


def load_equal_branch_tree_from_text(text: str, cmap, allowed, ids: list[str]):
    tree = Phylo.read(io.StringIO(text.strip()), "newick")
    base._validate_raw_tree(tree, cmap)

    terminals = {t.name for t in tree.get_terminals()}
    for mid, tips in cmap.items():
        if len(tips) > 1:
            if mid in ids:
                raise ValueError(f"replicated concept {mid} cannot enter continuous history")
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
        raise ValueError(f"tip mismatch missing={sorted(set(ids)-final)} extra={sorted(final-set(ids))}")

    for clade in tree.find_clades(order="preorder"):
        if clade is not tree.root:
            clade.branch_length = 1.0
    return tree


def unit_values(bridge: pd.DataFrame, ids: list[str], threshold: int):
    scalar = {}
    for endpoint in hist.PRIMARY_SCALAR_UNITS:
        raw = hist.values_for_endpoint(bridge, endpoint, threshold)
        scalar[endpoint] = {mid: raw[mid] for mid in ids}
    sin_raw = hist.values_for_endpoint(bridge, hist.HUE_SIN, threshold)
    cos_raw = hist.values_for_endpoint(bridge, hist.HUE_COS, threshold)
    return scalar, {mid: sin_raw[mid] for mid in ids}, {mid: cos_raw[mid] for mid in ids}


def stable_spearman(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Calculate Spearman correlations after deterministic near-tie collapse."""
    values = frame[columns].round(SPEARMAN_TIE_DECIMALS)
    return values.corr(method="spearman")


def topology_statistics(tree, ids, scalar_values, sin_values, cos_values):
    branches = hist.branch_ids(tree)
    frame = pd.DataFrame(index=np.arange(len(branches)))

    for endpoint in hist.PRIMARY_SCALAR_UNITS:
        states = hist.bm_states(tree, ids, hist.zscore(scalar_values[endpoint]))
        frame[endpoint] = [abs(states[child] - states[parent]) for parent, child, *_ in branches]

    sin_states = hist.bm_states(tree, ids, sin_values)
    cos_states = hist.bm_states(tree, ids, cos_values)
    hue = []
    for parent, child, *_ in branches:
        vp = np.array([sin_states[parent], cos_states[parent]], float)
        vc = np.array([sin_states[child], cos_states[child]], float)
        npv = float(np.linalg.norm(vp))
        ncv = float(np.linalg.norm(vc))
        if npv <= 1e-12 or ncv <= 1e-12:
            hue.append(np.nan)
        else:
            hue.append(float(np.linalg.norm(vp / npv - vc / ncv)))
    frame[hist.HUE_UNIT] = hue

    corr = stable_spearman(frame, hist.PRIMARY_UNITS)
    upper = corr.to_numpy(float)[np.triu_indices(len(hist.PRIMARY_UNITS), 1)]
    global_mean = float(np.nanmean(upper))

    within, between = [], []
    pairwise = {}
    for i, left in enumerate(hist.PRIMARY_UNITS):
        for right in hist.PRIMARY_UNITS[i + 1 :]:
            value = float(corr.loc[left, right])
            pairwise[f"{left}__{right}"] = value
            if hist.UNIT_MODULE[left] == hist.UNIT_MODULE[right]:
                within.append(value)
            else:
                between.append(value)
    within_mean = float(np.nanmean(within))
    between_mean = float(np.nanmean(between))
    return {
        "global_mean_pairwise_rho": global_mean,
        "within_module_mean_rho": within_mean,
        "between_module_mean_rho": between_mean,
        "within_minus_between": within_mean - between_mean,
        "pairwise": pairwise,
        "branches": len(branches),
    }


def summarize(values: list[float]) -> dict:
    a = np.asarray([x for x in values if math.isfinite(x)], float)
    if len(a) == 0:
        return {"n": 0}
    return {
        "n": int(len(a)),
        "min": float(np.min(a)),
        "q05": float(np.quantile(a, 0.05)),
        "q25": float(np.quantile(a, 0.25)),
        "median": float(np.median(a)),
        "q75": float(np.quantile(a, 0.75)),
        "q95": float(np.quantile(a, 0.95)),
        "max": float(np.max(a)),
        "fraction_positive": float(np.mean(a > 0)),
    }


def robust_positive(summary: dict) -> bool:
    return bool(summary.get("n", 0) > 0 and summary["q05"] > 0 and summary["fraction_positive"] >= 0.95)


def main() -> int:
    a = parse_args()
    bridge = hist.read_bridge(a.bridge)
    cmap, allowed = base.read_concept_map(a.concept_map)
    ids = hist.common_primary_ids(bridge, a.threshold)
    if len(ids) < hist.MIN_TAXA:
        raise ValueError(f"common continuous panel too small: {len(ids)}")
    scalar_values, sin_values, cos_values = unit_values(bridge, ids, a.threshold)

    ml_text = a.ml_tree.read_text(encoding="utf-8").strip()
    ml_equal = load_equal_branch_tree_from_text(ml_text, cmap, allowed, ids)
    ml_stats = topology_statistics(ml_equal, ids, scalar_values, sin_values, cos_values)

    raw_lines = [line.strip() for line in a.bootstrap_trees.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(raw_lines) != 1000:
        raise ValueError(f"expected 1000 UFBoot trees, found {len(raw_lines)}")

    stats = []
    failures = []
    for i, text in enumerate(raw_lines):
        try:
            tree = load_equal_branch_tree_from_text(text, cmap, allowed, ids)
            row = topology_statistics(tree, ids, scalar_values, sin_values, cos_values)
            row["bootstrap_index"] = i
            stats.append(row)
        except Exception as exc:
            failures.append({"bootstrap_index": i, "error": str(exc)})

    if len(stats) < 900:
        raise ValueError(f"fewer than 900 usable bootstrap topologies: {len(stats)}")

    global_summary = summarize([x["global_mean_pairwise_rho"] for x in stats])
    contrast_summary = summarize([x["within_minus_between"] for x in stats])
    within_summary = summarize([x["within_module_mean_rho"] for x in stats])
    between_summary = summarize([x["between_module_mean_rho"] for x in stats])

    pair_names = sorted(stats[0]["pairwise"])
    pairwise = {
        name: summarize([x["pairwise"][name] for x in stats if name in x["pairwise"]])
        for name in pair_names
    }

    global_robust = robust_positive(global_summary)
    module_robust = robust_positive(contrast_summary)
    result = {
        "contract_version": "japan38_continuous_branch_change_topology_sensitivity_v1",
        "purpose": "branch-length-free topology sensitivity for the ML-phylogram coordinated continuous-change result",
        "threshold_n_observations": a.threshold,
        "common_concepts": len(ids),
        "concept_ids": ids,
        "units": hist.PRIMARY_UNITS,
        "branch_length_contract": "all non-root branches fixed to 1.0 after pruning; no absolute-time or substitution-rate interpretation",
        "spearman_tie_contract": f"branch-change magnitudes rounded to {SPEARMAN_TIE_DECIMALS} decimal places before ranking so mathematically tied equal-branch changes do not depend on LAPACK round-off",
        "ml_equal_branch": ml_stats,
        "bootstrap_trees_total": len(raw_lines),
        "bootstrap_trees_usable": len(stats),
        "bootstrap_failures": failures,
        "global_mean_pairwise_rho_distribution": global_summary,
        "within_module_mean_rho_distribution": within_summary,
        "between_module_mean_rho_distribution": between_summary,
        "within_minus_between_distribution": contrast_summary,
        "pairwise_rho_distributions": pairwise,
        "predeclared_topology_robust_rule": "q05 > 0 and fraction_positive >= 0.95",
        "global_coordinated_change_decision": (
            "topology_robust_positive" if global_robust else "not_topology_robust_positive"
        ),
        "module_specificity_decision": (
            "topology_robust_positive" if module_robust else "not_topology_robust_positive"
        ),
        "claim_boundary": (
            "Equal-branch topology sensitivity only. Positive global coordination means that large BM-conditional changes tend to co-occur across continuous phenotype dimensions on bootstrap topologies; it does not identify a conserved syndrome, common genetic cause, shared selection, adaptation, convergence, or evolutionary rate."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
