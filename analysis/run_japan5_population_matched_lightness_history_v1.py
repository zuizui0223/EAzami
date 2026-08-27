#!/usr/bin/env python3
"""Five-concept population-matched Japan38 continuous-lightness history test.

This analysis is deliberately narrow and was frozen before seeing its result.
It asks whether the previously observed *directional* anti-phylogenetic lightness
pattern (negative association between patristic distance and absolute L* difference)
replicates after restricting colour evidence to five identity-resolved Japan-local
concept proxies.

Primary directional replication gate:
  rho < 0
  exact negative-tail label-permutation p <= 0.05
  all five leave-one-taxon-out rho values < 0

A stricter two-sided robustness flag additionally requires exact two-sided p <= 0.05.
Neither flag licenses convergence, adaptation, transition direction, rate, or dating.
"""
from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
from pathlib import Path

import numpy as np
from Bio import Phylo
from scipy.stats import spearmanr

TARGET_IDS = ["JPN_17", "JPN_23", "JPN_30", "JPN_36", "JPN_37"]


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_input(path: Path):
    rows = read_csv(path)
    if [r["paper_japan_member_id"] for r in rows] != TARGET_IDS:
        raise ValueError(f"target panel/order changed: {[r['paper_japan_member_id'] for r in rows]}")
    out = {}
    for row in rows:
        mid = row["paper_japan_member_id"]
        if row.get("identity_resolved", "").lower() != "true" or row.get("primary_analysis_allowed", "").lower() != "true":
            raise ValueError(f"identity/analysis gate failed for {mid}")
        value = float(row["local_lightness"])
        if not math.isfinite(value):
            raise ValueError(f"invalid L* for {mid}")
        out[mid] = {**row, "local_lightness": value, "local_population_or_observation_count": int(row["local_population_or_observation_count"])}
    return out


def read_concept_map(path: Path):
    rows = read_csv(path)
    if len(rows) != 38:
        raise ValueError(f"expected 38 concepts, found {len(rows)}")
    cmap = {}
    for row in rows:
        tips = [x for x in row["tip_ids"].split("|") if x]
        cmap[row["paper_japan_member_id"]] = tips
    for mid in TARGET_IDS:
        tips = cmap.get(mid, [])
        if len(tips) != 1:
            raise ValueError(f"{mid} requires exactly one nuclear tip, got {tips}")
    return cmap


def validate_tree(tree, cmap):
    names = {t.name for t in tree.get_terminals()}
    expected_all = {tip for tips in cmap.values() for tip in tips} | {"OUTGROUP_saff"}
    if names != expected_all:
        raise ValueError(f"tree tip mismatch missing={sorted(expected_all-names)} extra={sorted(names-expected_all)}")
    for clade in tree.find_clades():
        if clade is not tree.root and clade.branch_length is None:
            raise ValueError("canonical tree must retain substitution/site branch lengths")


def pair_vectors(tree, raw_tip_by_mid, mids, values):
    tips = {t.name: t for t in tree.get_terminals()}
    patristic = []
    trait_diff = []
    pair_rows = []
    for i, a in enumerate(mids):
        for j in range(i):
            b = mids[j]
            pa = raw_tip_by_mid[a]
            pb = raw_tip_by_mid[b]
            d = float(tree.distance(tips[pa], tips[pb]))
            td = abs(float(values[a]) - float(values[b]))
            patristic.append(d)
            trait_diff.append(td)
            pair_rows.append({"concept_a": b, "concept_b": a, "patristic_distance": d, "absolute_lightness_difference": td})
    return np.asarray(patristic, dtype=float), np.asarray(trait_diff, dtype=float), pair_rows


def rho(tree, raw_tip_by_mid, mids, values):
    p, t, _ = pair_vectors(tree, raw_tip_by_mid, mids, values)
    if len(p) < 3 or np.allclose(p, p[0]) or np.allclose(t, t[0]):
        return math.nan
    return float(spearmanr(p, t).statistic)


def exact_permutation(tree, raw_tip_by_mid, mids, values):
    observed = rho(tree, raw_tip_by_mid, mids, values)
    ordered = [values[mid] for mid in mids]
    null = []
    for perm in itertools.permutations(ordered):
        assigned = {mid: float(v) for mid, v in zip(mids, perm)}
        r = rho(tree, raw_tip_by_mid, mids, assigned)
        if math.isfinite(r):
            null.append(r)
    if len(null) != math.factorial(len(mids)):
        raise ValueError(f"expected {math.factorial(len(mids))} usable exact permutations, got {len(null)}")
    denom = len(null)
    return {
        "rho": observed,
        "exact_permutations": denom,
        "negative_tail_p": sum(r <= observed for r in null) / denom,
        "positive_tail_p": sum(r >= observed for r in null) / denom,
        "two_sided_abs_p": sum(abs(r) >= abs(observed) for r in null) / denom,
        "null_min_rho": min(null),
        "null_max_rho": max(null),
    }


def leave_one_out(tree, raw_tip_by_mid, mids, values):
    by = {}
    for omitted in mids:
        keep = [mid for mid in mids if mid != omitted]
        by[omitted] = rho(tree, raw_tip_by_mid, keep, values)
    vals = list(by.values())
    return {
        "rho_by_omitted_concept": by,
        "min_rho": min(vals),
        "max_rho": max(vals),
        "all_negative": all(v < 0 for v in vals),
        "all_positive": all(v > 0 for v in vals),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--tree", type=Path, required=True)
    p.add_argument("--concept-map", type=Path, required=True)
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()

    evidence = read_input(args.input)
    cmap = read_concept_map(args.concept_map)
    tree = Phylo.read(str(args.tree), "newick")
    validate_tree(tree, cmap)
    raw_tip_by_mid = {mid: cmap[mid][0] for mid in TARGET_IDS}
    values = {mid: evidence[mid]["local_lightness"] for mid in TARGET_IDS}

    signal = exact_permutation(tree, raw_tip_by_mid, TARGET_IDS, values)
    loo = leave_one_out(tree, raw_tip_by_mid, TARGET_IDS, values)
    _, _, pairs = pair_vectors(tree, raw_tip_by_mid, TARGET_IDS, values)

    directional_pass = bool(signal["rho"] < 0 and signal["negative_tail_p"] <= 0.05 and loo["all_negative"])
    strict_two_sided_pass = bool(directional_pass and signal["two_sided_abs_p"] <= 0.05)

    result = {
        "contract_version": "japan5_population_matched_lightness_history_v1",
        "status_date": "2026-08-27",
        "question": "Does the directional anti-phylogenetic L* pattern replicate in the first five identity-resolved Japan-local continuous-colour concepts?",
        "concept_panel": TARGET_IDS,
        "n_concepts": 5,
        "lightness_values": values,
        "raw_tree_tips": raw_tip_by_mid,
        "evidence_sources": {mid: {
            "taxon_name": evidence[mid]["taxon_name"],
            "source_class": evidence[mid]["source_class"],
            "source_reference": evidence[mid]["source_reference"],
            "local_population_or_observation_count": evidence[mid]["local_population_or_observation_count"],
        } for mid in TARGET_IDS},
        "evidence_heterogeneity": "JPN17/JPN23/JPN36/JPN37 use Japan-window medians from the frozen Azami strict-spatial cohort; JPN30 uses a median across two direct licensed Japan-local locality medians.",
        "tree_contract": {
            "source": "frozen Japan38 Comp1061 compatibility ML tree",
            "branch_length_semantics": "substitutions/site; not absolute time",
            "analysis_uses": "patristic distances only; no dating or evolutionary-rate inference"
        },
        "primary_signal": signal,
        "leave_one_out": loo,
        "pairwise_values": pairs,
        "predeclared_gates": {
            "directional_replication_rule": "rho < 0 AND exact negative-tail p <= 0.05 AND all five leave-one-out rho < 0",
            "directional_replication_pass": directional_pass,
            "strict_two_sided_rule": "directional replication pass AND exact two-sided |rho| p <= 0.05",
            "strict_two_sided_replication_pass": strict_two_sided_pass,
            "thresholds_changed_after_result": False
        },
        "claim_boundary": "A passing negative-distance gate is an anti-phylogenetic/overdispersion diagnostic on a substitution-length tree. It does not identify convergence, adaptation, ancestral colour, discrete W/C transitions, evolutionary rate, molecular reactivation, or adaptive radiation. A failed gate is retained as a substantive result rather than repaired post hoc."
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
