#!/usr/bin/env python3
"""Locate identifiable Japan38 trait transitions and prioritize missing trait states.

The existing parsimony screen asks how many unordered state changes are required.
This script asks a different question: which branches are forced to change in every
minimum-cost reconstruction, which branches remain optional, and which unresolved
taxon-concept trait states would most reduce that localization ambiguity.

The completion-priority score is a topology-conditioned design heuristic.  For each
fully unresolved concept, every allowed state is inserted in turn and the reduction
in edges that can be either changed or unchanged across equally optimal Sankoff
reconstructions is recorded.  No probability is assigned to hypothetical states.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import statistics
from collections import Counter, defaultdict
from io import StringIO
from pathlib import Path

from Bio import Phylo

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "japan38_parsimony_base",
    ROOT / "analysis/summarize_japan38_multitrait_parsimony_v1.py",
)
assert SPEC and SPEC.loader
BASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BASE)


def edge_id(child):
    return "|".join(sorted(t.name for t in child.get_terminals()))


def sankoff_diagnostics(tree, state_map, universe):
    states = tuple(sorted(universe))
    inf = 10**9
    down = {}
    for node in tree.find_clades(order="postorder"):
        if node.is_terminal():
            allowed = set(state_map.get(node.name, set(universe)))
            down[node] = {s: (0 if s in allowed else inf) for s in states}
            continue
        costs = {}
        for s in states:
            costs[s] = sum(
                min(down[child][t] + (0 if s == t else 1) for t in states)
                for child in node.clades
            )
        down[node] = costs

    optimum = min(down[tree.root].values())
    root_states = sorted(s for s, c in down[tree.root].items() if c == optimum)
    outside = {tree.root: {s: 0 for s in states}}
    edges = []

    for parent in tree.find_clades(order="preorder"):
        if parent.is_terminal():
            continue
        for child in parent.clades:
            siblings = [s for s in parent.clades if s is not child]
            sibling_cost = {
                ps: sum(
                    min(down[sib][u] + (0 if ps == u else 1) for u in states)
                    for sib in siblings
                )
                for ps in states
            }
            child_outside = {}
            optimal_pairs = []
            for cs in states:
                child_outside[cs] = min(
                    outside[parent][ps]
                    + sibling_cost[ps]
                    + (0 if ps == cs else 1)
                    for ps in states
                )
                for ps in states:
                    total = (
                        outside[parent][ps]
                        + sibling_cost[ps]
                        + (0 if ps == cs else 1)
                        + down[child][cs]
                    )
                    if total == optimum:
                        optimal_pairs.append((ps, cs))
            outside[child] = child_outside
            same_possible = any(a == b for a, b in optimal_pairs)
            change_possible = any(a != b for a, b in optimal_pairs)
            forced_change = bool(optimal_pairs) and change_possible and not same_possible
            edges.append(
                {
                    "edge_id": edge_id(child),
                    "child_label": child.name,
                    "forced_change": forced_change,
                    "change_possible": change_possible,
                    "same_possible": same_possible,
                    "optimal_state_pairs": [f"{a}->{b}" for a, b in optimal_pairs],
                }
            )

    return {
        "minimum_steps": optimum,
        "minimum_root_state_set": root_states,
        "forced_change_edges": [e for e in edges if e["forced_change"]],
        "optional_change_edges": [
            e for e in edges if e["change_possible"] and e["same_possible"]
        ],
        "no_change_edges": [e for e in edges if not e["change_possible"]],
    }


def prepare_tree(raw_tree, by, allowed, trait_states):
    raw_tree.root_with_outgroup("OUTGROUP_saff")
    tree, diag = BASE.prepare_trait_tree(raw_tree, by, allowed, trait_states)
    if not diag["trait_asr_ready"]:
        raise ValueError(f"trait tree blocked: {diag}")
    return tree, diag


def quantile(values, p):
    x = sorted(values)
    if not x:
        return None
    return x[min(len(x) - 1, max(0, round((len(x) - 1) * p)))]


def summarize_counts(values):
    return {
        "n": len(values),
        "min": min(values) if values else None,
        "q05": quantile(values, 0.05),
        "median": statistics.median(values) if values else None,
        "q95": quantile(values, 0.95),
        "max": max(values) if values else None,
    }


def completion_priorities(tree, by, allowed, trait_states):
    names = {}
    for row in BASE.read_csv(args.concept_map):
        names[row["paper_japan_member_id"]] = row.get("paper_taxon_concept") or ""
    final_tips = {t.name for t in tree.get_terminals()}
    out = {}
    for trait, universe in BASE.STATE_UNIVERSE.items():
        baseline = sankoff_diagnostics(tree, trait_states[trait], universe)
        baseline_ambiguous = len(baseline["optional_change_edges"])
        candidates = []
        for concept in sorted(final_tips):
            current = trait_states[trait].get(concept, set(universe))
            if set(current) != set(universe):
                continue
            scenarios = []
            for state in sorted(universe):
                hypothetical = dict(trait_states[trait])
                hypothetical[concept] = {state}
                diag = sankoff_diagnostics(tree, hypothetical, universe)
                ambiguous = len(diag["optional_change_edges"])
                scenarios.append(
                    {
                        "state": state,
                        "minimum_steps": diag["minimum_steps"],
                        "root_state_count": len(diag["minimum_root_state_set"]),
                        "ambiguous_change_edges": ambiguous,
                        "forced_change_edges": len(diag["forced_change_edges"]),
                        "ambiguous_edge_reduction": baseline_ambiguous - ambiguous,
                    }
                )
            reductions = [s["ambiguous_edge_reduction"] for s in scenarios]
            candidates.append(
                {
                    "paper_japan_member_id": concept,
                    "paper_taxon_concept": names.get(concept, ""),
                    "mean_ambiguous_edge_reduction": sum(reductions) / len(reductions),
                    "worst_case_ambiguous_edge_reduction": min(reductions),
                    "best_case_ambiguous_edge_reduction": max(reductions),
                    "minimum_step_range": [
                        min(s["minimum_steps"] for s in scenarios),
                        max(s["minimum_steps"] for s in scenarios),
                    ],
                    "hypothetical_states": scenarios,
                }
            )
        candidates.sort(
            key=lambda x: (
                x["worst_case_ambiguous_edge_reduction"],
                x["mean_ambiguous_edge_reduction"],
                x["paper_japan_member_id"],
            ),
            reverse=True,
        )
        out[trait] = {
            "baseline_ambiguous_change_edges": baseline_ambiguous,
            "priority_rule": "descending worst-case then mean reduction in ambiguous transition-placement edges under uniform state enumeration",
            "candidates": candidates,
        }
    return out


def main():
    global args
    p = argparse.ArgumentParser()
    p.add_argument("--tree", type=Path, required=True)
    p.add_argument("--bootstrap-trees", type=Path, required=True)
    p.add_argument("--concept-map", type=Path, required=True)
    p.add_argument("--trait-seed", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()

    by, allowed = BASE.concept_info(args.concept_map)
    trait_states = BASE.trait_states(args.trait_seed)

    ml_raw = Phylo.read(str(args.tree), "newick")
    ml_tree, tree_diag = prepare_tree(ml_raw, by, allowed, trait_states)
    ml = {
        trait: sankoff_diagnostics(ml_tree, trait_states[trait], universe)
        for trait, universe in BASE.STATE_UNIVERSE.items()
    }

    boot_steps = {t: [] for t in BASE.STATE_UNIVERSE}
    boot_forced_counts = {t: [] for t in BASE.STATE_UNIVERSE}
    boot_root_sets = {t: Counter() for t in BASE.STATE_UNIVERSE}
    boot_forced_edges = {t: defaultdict(int) for t in BASE.STATE_UNIVERSE}
    total = 0

    for raw in args.bootstrap_trees.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        total += 1
        raw_tree = Phylo.read(StringIO(line), "newick")
        tree, _ = prepare_tree(raw_tree, by, allowed, trait_states)
        for trait, universe in BASE.STATE_UNIVERSE.items():
            diag = sankoff_diagnostics(tree, trait_states[trait], universe)
            boot_steps[trait].append(diag["minimum_steps"])
            boot_forced_counts[trait].append(len(diag["forced_change_edges"]))
            boot_root_sets[trait]["|".join(diag["minimum_root_state_set"])] += 1
            for edge in diag["forced_change_edges"]:
                boot_forced_edges[trait][edge["edge_id"]] += 1

    if total == 0:
        raise ValueError("no bootstrap trees found")

    bootstrap = {}
    for trait in BASE.STATE_UNIVERSE:
        top_edges = sorted(
            boot_forced_edges[trait].items(), key=lambda x: (-x[1], x[0])
        )[:20]
        bootstrap[trait] = {
            "minimum_step_distribution": summarize_counts(boot_steps[trait]),
            "forced_change_edge_count_distribution": summarize_counts(
                boot_forced_counts[trait]
            ),
            "minimum_root_state_set_frequencies": dict(
                sorted(boot_root_sets[trait].items(), key=lambda x: (-x[1], x[0]))
            ),
            "top_forced_edge_frequencies": [
                {
                    "edge_id": edge,
                    "count": count,
                    "fraction": count / total,
                }
                for edge, count in top_edges
            ],
        }

    result = {
        "contract_version": "japan38_transition_identifiability_v1",
        "tree_diagnostic": tree_diag,
        "ml_minimum_reconstructions": ml,
        "bootstrap_trees_total": total,
        "bootstrap_identifiability": bootstrap,
        "trait_completion_priorities": completion_priorities(
            ml_tree, by, allowed, trait_states
        ),
        "interpretation_gate": (
            "Minimum step counts and transition localization are separate claims. A repeated-state lower bound may be topology-robust even when no individual branch is forced to change. Completion priorities are deterministic design heuristics under the current compatibility topology, not probabilities of biological importance or adaptation."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
