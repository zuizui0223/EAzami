#!/usr/bin/env python3
"""Global nuclear-tree U->D endpoint posterior x reconstructed modern-niche shifts.

This is an out-of-sample successor to the frozen East-Asian EAzami Chapter 2
test. It never treats reconstructed present-day niche differences as
palaeoclimatic change at the time a morphological transition occurred.

Requires a real rooted nuclear tree ensemble, explicit specimen/taxon crosswalk,
source-backed U/D labels, and source-backed modern BIO15/BIO1 centroids.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import itertools
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from Bio import Phylo

from run_chapter2_orientation_transition_regime_hypothesis_v1 import (
    brownian_internal_values,
    ctmc_likelihood_and_edge_joint,
    fit_symmetric_q,
    tree_structure,
)

FIELDS = (
    "tip_id", "accepted_taxon", "orientation_state", "bio15", "bio1",
    "biogeographic_region", "orientation_source", "climate_source", "exclusion_reason",
)
ALLOWED_STATES = {"U", "D", "unresolved"}
EPS = 1e-12


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_tip_table(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not set(FIELDS).issubset(set(reader.fieldnames)):
            raise ValueError("tip table missing columns: " + ", ".join(sorted(set(FIELDS) - set(reader.fieldnames or []))))
        rows = [{k: (v or "").strip() for k, v in row.items()} for row in reader]
    if not rows:
        raise ValueError("empty tip table")
    ids, resolved_taxa, included = set(), set(), []
    for row in rows:
        tip, taxon, state = row["tip_id"], row["accepted_taxon"], row["orientation_state"]
        if not tip or not taxon or any(c in tip for c in " ,:;()[]"):
            raise ValueError("tip_id must be a unique Newick-safe explicit identifier")
        if tip in ids:
            raise ValueError("duplicate tip_id: " + tip)
        ids.add(tip)
        if state not in ALLOWED_STATES:
            raise ValueError("orientation_state must be U/D/unresolved: " + tip)
        if state == "unresolved":
            if not row["exclusion_reason"]:
                raise ValueError("unresolved state needs explicit exclusion_reason: " + tip)
            continue
        if row["exclusion_reason"]:
            raise ValueError("resolved tip has exclusion_reason: " + tip)
        if taxon in resolved_taxa:
            raise ValueError("duplicate accepted_taxon in resolved panel: " + taxon)
        resolved_taxa.add(taxon)
        for key in ("orientation_source", "climate_source", "biogeographic_region"):
            if not row[key]:
                raise ValueError(key + " missing for included tip: " + tip)
        for key in ("bio15", "bio1"):
            try:
                value = float(row[key])
            except ValueError as e:
                raise ValueError("invalid numeric " + key + " for " + tip) from e
            if not math.isfinite(value):
                raise ValueError("nonfinite " + key + " for " + tip)
        included.append(row)
    return rows, included


def zscore(values):
    values = np.asarray(values, dtype=float)
    sd = float(np.std(values, ddof=1))
    if not np.isfinite(sd) or sd <= 0:
        raise ValueError("zero or invalid variation in climate input")
    return (values - float(np.mean(values))) / sd


def read_tree_ensemble(path: Path, expected_tips: set[str], outgroup: str, keep: set[str]):
    if outgroup in expected_tips:
        raise ValueError("outgroup must not also be a metadata tip")
    lines = [x.strip() for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    if not lines:
        raise ValueError("tree file empty")
    trees = []
    for i, line in enumerate(lines, 1):
        tree = Phylo.read(io.StringIO(line), "newick")
        names = [x.name for x in tree.get_terminals()]
        if any(x is None for x in names) or len(names) != len(set(names)):
            raise ValueError("unlabelled/duplicate tree tips at tree " + str(i))
        if set(names) != expected_tips | {outgroup}:
            raise ValueError(
                "tree/metadata mismatch at tree " + str(i) +
                ": missing " + repr(sorted(expected_tips | {outgroup} - set(names))[:8]) +
                ", extra " + repr(sorted(set(names) - expected_tips - {outgroup})[:8])
            )
        if tree.count_terminals() < 5:
            raise ValueError("tree has too few terminals")
        for child in tree.find_clades():
            if child is not tree.root and (child.branch_length is None or
                                           not math.isfinite(float(child.branch_length)) or
                                           float(child.branch_length) <= 0):
                raise ValueError("non-positive/nonfinite branch length in tree " + str(i))
        tree.root_with_outgroup({"name": outgroup})
        # Drop explicitly unresolved taxa and the outgroup; no implicit trait filling.
        for tip in list(tree.get_terminals()):
            if tip.name not in keep:
                tree.prune(tip)
        got = {x.name for x in tree.get_terminals()}
        if got != keep:
            raise ValueError("post-pruning tree differs from frozen resolved panel")
        while len(tree.root.clades) == 1:
            tree.root = tree.root.clades[0]
            tree.root.branch_length = None
        for child in tree.find_clades():
            if child is not tree.root and (child.branch_length is None or float(child.branch_length) <= 0):
                raise ValueError("non-positive branch after pruning; unresolved multifurcation")
        trees.append(tree)
    return trees


def branch_statistics(tree, states, climate15, climate1, index):
    nodes, children, parents, root, tips, post, pre = tree_structure(tree)
    _, d15 = brownian_internal_values(tree, climate15)
    _, d1 = brownian_internal_values(tree, climate1)
    q = fit_symmetric_q(tree, states)
    likelihood, joints = ctmc_likelihood_and_edge_joint(tree, states, q, need_joint=True)
    if joints is None:
        raise ValueError("CTMC likelihood/edge posterior unavailable")
    num15, num1, denom, rows = 0.0, 0.0, 0.0, []
    for child_index, J in joints.items():
        p_ud, p_du = float(J[0, 1]), float(J[1, 0])
        if not np.isfinite(J).all() or abs(float(np.sum(J)) - 1.0) > 1e-7:
            raise ValueError("invalid edge joint posterior; check tree/rate/model")
        signed = p_ud - p_du
        discordance = p_ud + p_du
        delta15, delta1 = d15[child_index], d1[child_index]
        num15 += signed * delta15
        num1 += signed * delta1
        denom += discordance
        descendant = sorted(x.name for x in nodes[child_index].get_terminals())
        clade = "C" + str(len(descendant)) + "_" + hashlib.sha256("|".join(descendant).encode()).hexdigest()[:16]
        rows.append({
            "tree_index": index,
            "child_clade_id": clade,
            "n_descendant_tips": len(descendant),
            "is_terminal_edge": len(descendant) == 1,
            "p_parent_U_child_D": p_ud,
            "p_parent_D_child_U": p_du,
            "p_endpoint_discordance": discordance,
            "signed_endpoint_posterior": signed,
            "delta_reconstructed_z_bio15": delta15,
            "delta_reconstructed_z_bio1": delta1,
            "weighted_bio15": signed * delta15,
            "weighted_bio1": signed * delta1,
        })
    if denom <= EPS:
        raise ValueError("near-zero endpoint discordance posterior mass")
    s15, s1 = num15 / denom, num1 / denom
    return {
        "tree_index": index,
        "q_symmetric_per_substitution_length": q,
        "data_likelihood": float(likelihood),
        "endpoint_discordance_mass": denom,
        "bio15": s15,
        "bio1": s1,
        "composite": (s15 - s1) / math.sqrt(2),
    }, rows


def summarise(assets, states, climate15, climate1, keep_edges=False):
    scores, edges = [], []
    for i, tree in enumerate(assets, 1):
        item, erows = branch_statistics(tree, states, climate15, climate1, i)
        scores.append(item)
        if keep_edges:
            edges.extend(erows)
    return {
        "median_composite": float(np.median([x["composite"] for x in scores])),
        "median_bio15": float(np.median([x["bio15"] for x in scores])),
        "median_bio1": float(np.median([x["bio1"] for x in scores])),
        "positive_tree_count": sum(x["composite"] > 0 for x in scores),
        "per_tree": scores,
    }, edges


def permutation_groups(included, mode):
    groups = defaultdict(list)
    for row in included:
        key = row["biogeographic_region"] if mode == "region" else "global"
        groups[key].append(row["tip_id"])
    return dict(groups)


def unique_map_count(states, groups):
    return math.prod(math.comb(len(tips), sum(states[t] == 1 for t in tips)) for tips in groups.values())


def random_states(states, groups, rng):
    shuffled = dict(states)
    for tips in groups.values():
        original = [states[t] for t in tips]
        rng.shuffle(original)
        shuffled.update(zip(tips, original))
    return shuffled


def exact_maps(states, groups):
    """Enumerate fixed-count maps only when total size is explicitly small."""
    parts = []
    for tips in groups.values():
        n_d = sum(states[t] for t in tips)
        parts.append((tips, list(itertools.combinations(range(len(tips)), n_d))))
    for choices in itertools.product(*(part[1] for part in parts)):
        assignment = {}
        for (tips, _), d_positions in zip(parts, choices):
            dset = set(d_positions)
            assignment.update({tip: int(i in dset) for i, tip in enumerate(tips)})
        yield assignment


def run(args):
    rows, included = load_tip_table(args.tip_table)
    if len(included) < args.min_taxa:
        raise ValueError("not enough source-backed resolved taxa: " + str(len(included)))
    states = {r["tip_id"]: 0 if r["orientation_state"] == "U" else 1 for r in included}
    counts = Counter(states.values())
    if min(counts.get(0, 0), counts.get(1, 0)) < 2:
        raise ValueError("both orientation states require at least two independent taxa")
    keep = set(states)
    trees = read_tree_ensemble(args.trees, {r["tip_id"] for r in rows}, args.outgroup, keep)
    vals15 = zscore([float(r["bio15"]) for r in included])
    vals1 = zscore([float(r["bio1"]) for r in included])
    climate15 = {r["tip_id"]: float(v) for r, v in zip(included, vals15)}
    climate1 = {r["tip_id"]: float(v) for r, v in zip(included, vals1)}
    observed, edges = summarise(trees, states, climate15, climate1, keep_edges=True)
    groups = permutation_groups(included, args.permutation_strata)
    possible = unique_map_count(states, groups)
    if possible < 2:
        raise ValueError("null design has only one attainable state map; change design, not data")
    rng = random.Random(args.seed)
    exact = possible <= args.exact_limit
    if exact:
        maps = exact_maps(states, groups)
        method = "exact_count_preserving"
    else:
        if args.permutations < 99:
            raise ValueError("Monte Carlo mode requires at least 99 permutations")
        maps = (random_states(states, groups, rng) for _ in range(args.permutations))
        method = "monte_carlo_count_preserving"
    perm_scores = []
    extreme = 0
    total = 0
    for mapping in maps:
        score, _ = summarise(trees, mapping, climate15, climate1)
        statistic = score["median_composite"]
        extreme += statistic >= observed["median_composite"] - 1e-12
        total += 1
        perm_scores.append({"iteration": total, "composite_median": statistic})
    p_value = extreme / total if exact else (extreme + 1) / (total + 1)
    summary = {
        "contract_version": "global_nuclear_orientation_transition_niche_v1",
        "status": "completed_present_niche_reconstruction_only",
        "claim_scope": "exploratory_global_candidate_until_nuclear_tree_and_worldwide_source_coverage_audited",
        "not_estimated": [
            "historical_climate_on_transition_branch", "transition_age", "causation",
            "evolutionary_rate_per_Myr", "selection", "fitness", "adaptation",
            "multiple_hidden_CTMC_changes_along_an_edge"
        ],
        "model": {
            "discrete": "ER symmetric 2-state CTMC; equal 0.5 root prior; endpoint joint posterior, not stochastic-map event count",
            "continuous": "Brownian squared-change reconstruction of standardized present-day taxon niche centroids",
            "statistic": "sum[(P(parent U,child D)-P(parent D,child U))*delta(zBIO15-zBIO1)] / (sqrt(2)*sum endpoint discordance)",
            "branch_length_unit": "input phylogram substitutions/site, not calendar time",
            "fixed_vector": {"bio15": 1, "bio1": -1},
        },
        "input_sha256": {"trees": digest(args.trees), "tip_table": digest(args.tip_table)},
        "n_trees": len(trees), "n_resolved_taxa": len(included),
        "n_explicitly_unresolved": len(rows) - len(included),
        "states": {"U": counts[0], "D": counts[1]},
        "observed": observed,
        "null": {
            "strata": args.permutation_strata, "seed": args.seed,
            "method": method, "unique_possible_maps": possible,
            "draws": total, "at_least_observed": extreme, "one_sided_rank": p_value,
        },
        "cautions": [
            "East-Asian BIO15/BIO1 vector was chosen using earlier results; this run is external testing only if global samples are independent.",
            "Present niche centroids cannot reconstruct actual paleoclimate where or when U->D originated.",
            "Regional count-preserving permutations are conditional sensitivity tests, not a full geographic or phylogenetic null.",
            "One resolved representative taxon per tree; population polymorphism and within-species replicate nuclear samples require a separate hierarchical model.",
            "No multiple-axis inference or post-hoc climate-variable search is performed.",
        ],
    }
    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / "result.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for filename, payload in (("edge_joint_posteriors.csv", edges), ("permutation_scores.csv", perm_scores), ("input_join_audit.csv", rows)):
        if not payload:
            raise ValueError("empty output: " + filename)
        with (args.outdir / filename).open("w", encoding="utf-8", newline="") as h:
            w = csv.DictWriter(h, fieldnames=list(payload[0]))
            w.writeheader()
            w.writerows(payload)
    return summary


def make_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trees", type=Path, required=True, help="One rooted-outgroup Newick per line; complete frozen taxon sample set")
    parser.add_argument("--tip-table", type=Path, required=True, help="Source-backed one-specimen-per-resolved-taxon table")
    parser.add_argument("--outgroup", required=True, help="Exact tree tip used to root each nuclear tree, not an ingroup trait observation")
    parser.add_argument("--permutation-strata", choices=("region", "global"), default="region")
    parser.add_argument("--permutations", type=int, default=999)
    parser.add_argument("--exact-limit", type=int, default=3000)
    parser.add_argument("--min-taxa", type=int, default=20)
    parser.add_argument("--seed", type=int, default=2317)
    parser.add_argument("--outdir", type=Path, required=True)
    return parser


def main():
    args = make_parser().parse_args()
    if args.min_taxa < 4 or args.exact_limit < 1 or args.permutations < 0:
        raise ValueError("invalid sampling/permutation settings")
    result = run(args)
    print(json.dumps({
        "status": result["status"], "taxa": result["n_resolved_taxa"],
        "topologies": result["n_trees"], "median_composite": result["observed"]["median_composite"],
        "null_rank": result["null"]["one_sided_rank"],
    }, indent=2))


if __name__ == "__main__":
    main()
