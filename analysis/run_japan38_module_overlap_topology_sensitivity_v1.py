#!/usr/bin/env python3
"""Topology-only sensitivity for Japan38 capitulum-module transition overlap.

Raw IQ-TREE ``-wbt`` ultrafast-bootstrap trees do not carry branch lengths.
They therefore cannot be passed directly into the branch-length-aware Mk
analysis without inventing branch lengths.  This sensitivity analysis keeps
that distinction explicit: every non-root branch is fixed to length 1.0, the
same symmetric Mk model is refit on each topology, and only the distribution
of pairwise transition-posterior rank correlations is summarized.

This is a topology-robustness diagnostic, not a replacement for the primary
branch-length-aware ML-tree analysis.  A positive overlap is considered
robust only when its direction is compatible across the two layers.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import statistics
from io import StringIO
from pathlib import Path

from Bio import Phylo

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "japan38_overlap_base",
    ROOT / "analysis/run_japan38_module_transition_overlap_v1.py",
)
assert SPEC and SPEC.loader
BASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BASE)


def prepare_analysis_tree(tree, cmap, allowed, states):
    """Mirror the frozen trait-tree gate without requiring branch lengths."""
    mid, two = BASE._validate_raw_tree(tree, cmap)
    mrca = tree.common_ancestor({"name": two[0]}, {"name": two[1]})
    descendants = {x.name for x in mrca.get_terminals()}
    monophyletic = descendants == set(two)
    replicate_resolved = BASE.resolved_for_any_trait(states, mid)
    excluded = []

    if replicate_resolved:
        if not monophyletic:
            raise ValueError(
                "JPN_20 biological replicates are not monophyletic but JPN_20 has an observed analysed trait"
            )
        mrca.clades = []
        mrca.name = mid
        replicate_mode = "collapsed_monophyletic_replicated_concept"
    else:
        for tip in two:
            tree.prune(target=tip)
        excluded.append(mid)
        replicate_mode = "pruned_fully_unresolved_replicated_concept"

    for concept, xs in cmap.items():
        if allowed.get(concept, True) or len(xs) != 1:
            continue
        names = {t.name for t in tree.get_terminals()}
        if xs[0] in names:
            tree.prune(target=xs[0])
        excluded.append(concept)

    reverse = {
        xs[0]: concept
        for concept, xs in cmap.items()
        if len(xs) == 1 and allowed.get(concept, True)
    }
    for tip in tree.get_terminals():
        if tip.name in reverse:
            tip.name = reverse[tip.name]

    tree.prune(target="OUTGROUP_saff")
    expected = {
        concept
        for concept in cmap
        if allowed.get(concept, True) and concept not in set(excluded)
    }
    final = {t.name for t in tree.get_terminals()}
    if final != expected:
        raise ValueError(
            f"analysis-tree tip mismatch missing={sorted(expected-final)} extra={sorted(final-expected)}"
        )

    for node in BASE.preorder(tree.root):
        if node is not tree.root:
            node.branch_length = 1.0

    return tree, {
        "replicate_monophyly": monophyletic,
        "replicate_resolved_for_any_trait": replicate_resolved,
        "replicate_mode": replicate_mode,
        "replicate_mrca_descendants": sorted(descendants),
        "excluded_concepts": sorted(set(excluded)),
        "concept_tips": len(final),
    }


def pairwise_rho(fits):
    out = {}
    traits = list(fits)
    for ai in range(len(traits)):
        for bi in range(ai + 1, len(traits)):
            a, b = traits[ai], traits[bi]
            ea = {
                r["edge_id"]: r
                for r in fits[a]["edges"]
                if r["informative"] and r["transition_posterior"] is not None
            }
            eb = {
                r["edge_id"]: r
                for r in fits[b]["edges"]
                if r["informative"] and r["transition_posterior"] is not None
            }
            keys = sorted(set(ea) & set(eb))
            x = [ea[k]["transition_posterior"] for k in keys]
            y = [eb[k]["transition_posterior"] for k in keys]
            out[f"{a}__{b}"] = {
                "shared_informative_edges": len(keys),
                "spearman_transition_posterior": BASE.spearman(x, y),
            }
    return out


def analyze_tree(tree, cmap, allowed, states):
    tree, diag = prepare_analysis_tree(tree, cmap, allowed, states)
    fits = {
        trait: BASE.fit_trait(tree, states[trait], universe)
        for trait, universe in BASE.STATE_UNIVERSE.items()
    }
    return diag, pairwise_rho(fits)


def q_nearest(values, p):
    x = sorted(values)
    if not x:
        return None
    return x[min(len(x) - 1, max(0, round((len(x) - 1) * p)))]


def summarize(values):
    vals = [float(v) for v in values if v is not None and math.isfinite(float(v))]
    if not vals:
        return {
            "n": 0,
            "min": None,
            "q05": None,
            "q25": None,
            "median": None,
            "q75": None,
            "q95": None,
            "max": None,
            "fraction_positive": None,
        }
    return {
        "n": len(vals),
        "min": min(vals),
        "q05": q_nearest(vals, 0.05),
        "q25": q_nearest(vals, 0.25),
        "median": statistics.median(vals),
        "q75": q_nearest(vals, 0.75),
        "q95": q_nearest(vals, 0.95),
        "max": max(vals),
        "fraction_positive": sum(v > 0 for v in vals) / len(vals),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--bootstrap-trees", type=Path, required=True)
    p.add_argument("--ml-tree", type=Path, required=True)
    p.add_argument("--concept-map", type=Path, required=True)
    p.add_argument("--trait-seed", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()

    cmap, allowed = BASE.concept_info(a.concept_map)
    states = BASE.trait_states(a.trait_seed)

    ml_tree = Phylo.read(str(a.ml_tree), "newick")
    ml_diag, ml_pairwise = analyze_tree(ml_tree, cmap, allowed, states)

    distributions = {
        pair: []
        for pair in (
            "orientation__phyllary",
            "orientation__stickiness",
            "phyllary__stickiness",
        )
    }
    total = 0
    jpn20_mono = 0
    for raw in a.bootstrap_trees.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        total += 1
        tree = Phylo.read(StringIO(line), "newick")
        diag, pairwise = analyze_tree(tree, cmap, allowed, states)
        if diag["replicate_monophyly"]:
            jpn20_mono += 1
        for pair in distributions:
            distributions[pair].append(pairwise[pair]["spearman_transition_posterior"])

    if total == 0:
        raise ValueError("no bootstrap trees found")

    result = {
        "contract_version": "japan38_module_overlap_topology_sensitivity_v1",
        "purpose": "branch-length-free topology sensitivity; not the primary Mk analysis",
        "branch_length_contract": "all non-root analysis-tree branches fixed to 1.0",
        "ml_topology_equal_branch": {
            "tree_diagnostic": ml_diag,
            "pairwise_overlap": ml_pairwise,
        },
        "bootstrap_topology_sensitivity": {
            "bootstrap_trees_total": total,
            "jpn20_monophyletic_trees": jpn20_mono,
            "jpn20_monophyly_fraction": jpn20_mono / total,
            "pairwise_spearman_distributions": {
                pair: summarize(values)
                for pair, values in distributions.items()
            },
        },
        "interpretation_gate": (
            "Do not call a shared-lability signal topology-robust when the branch-length-aware ML analysis and "
            "this equal-branch sensitivity disagree in sign, or when the bootstrap topology distribution does not "
            "remain predominantly positive. This sensitivity cannot establish developmental modularity or adaptation."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
