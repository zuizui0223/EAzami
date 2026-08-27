#!/usr/bin/env python3
"""Source-balanced seven-concept Japan-local continuous-lightness history.

The panel is frozen from the existing Azami strict-spatial production cohort before
this analysis. All seven concepts use the same detector/crop/continuous-colour
pipeline and satisfy the predeclared >=2 observations + >=2 analysis cells rule.

Primary anti-phylogenetic replication gate (unchanged from earlier local pilots):
  rho < 0
  exact negative-tail label-permutation p <= 0.05
  all concept leave-one-out rho < 0
  all sparse-observation leave-one-out rho < 0

The positive tail is reported descriptively because the observed direction is not
allowed to redefine the hypothesis after inspection. No result licenses convergence,
adaptation, ancestry, discrete W/C transitions, rate, or reactivation.
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
from scipy.stats import rankdata

TARGET_IDS = ["JPN_05", "JPN_17", "JPN_23", "JPN_27", "JPN_30", "JPN_36", "JPN_37"]
SPARSE_IDS = ["JPN_05", "JPN_27", "JPN_30"]


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_panel(path: Path):
    rows = read_csv(path)
    ids = [r["paper_japan_member_id"] for r in rows]
    if ids != TARGET_IDS:
        raise ValueError(f"frozen panel/order changed: {ids}")
    out = {}
    for row in rows:
        mid = row["paper_japan_member_id"]
        if row["identity_resolved"].lower() != "true" or row["primary_analysis_allowed"].lower() != "true":
            raise ValueError(f"identity/analysis gate failed for {mid}")
        nobs = int(row["japan_colour_usable_observations"])
        ncells = int(row["japan_distinct_analysis_cells"])
        if nobs < 2 or ncells < 2:
            raise ValueError(f"two-cell admission gate failed for {mid}: n={nobs} cells={ncells}")
        value = float(row["local_lightness"])
        if not math.isfinite(value):
            raise ValueError(f"invalid lightness for {mid}")
        out[mid] = {**row, "local_lightness": value, "nobs": nobs, "ncells": ncells}
    return out


def read_sparse(path: Path, panel):
    rows = read_csv(path)
    by = {mid: [] for mid in SPARSE_IDS}
    for row in rows:
        mid = row["paper_japan_member_id"]
        if mid not in by:
            raise ValueError(f"unexpected sparse concept: {mid}")
        value = float(row["corolla_lab_lightness_median"])
        if not math.isfinite(value):
            raise ValueError(f"nonfinite sparse lightness: {mid}/{row['obs_id']}")
        by[mid].append({**row, "lightness": value})
    for mid in SPARSE_IDS:
        expected = panel[mid]["nobs"]
        if len(by[mid]) != expected or not 2 <= expected <= 4:
            raise ValueError(f"sparse row count mismatch for {mid}: {len(by[mid])} vs {expected}")
        if len({r["analysis_cell"] for r in by[mid]}) != panel[mid]["ncells"]:
            raise ValueError(f"sparse analysis-cell mismatch for {mid}")
        med = float(np.median([r["lightness"] for r in by[mid]]))
        if abs(med - panel[mid]["local_lightness"]) > 1e-9:
            raise ValueError(f"sparse median does not reproduce panel for {mid}: {med}")
    return by


def read_concept_map(path: Path):
    rows = read_csv(path)
    if len(rows) != 38:
        raise ValueError(f"expected 38 concepts, found {len(rows)}")
    cmap = {r["paper_japan_member_id"]: [x for x in r["tip_ids"].split("|") if x] for r in rows}
    for mid in TARGET_IDS:
        if len(cmap.get(mid, [])) != 1:
            raise ValueError(f"{mid} requires exactly one nuclear tip: {cmap.get(mid)}")
    return cmap


def validate_tree(tree, cmap):
    names = {t.name for t in tree.get_terminals()}
    expected = {tip for tips in cmap.values() for tip in tips} | {"OUTGROUP_saff"}
    if names != expected:
        raise ValueError(f"tree tip mismatch missing={sorted(expected-names)} extra={sorted(names-expected)}")
    for clade in tree.find_clades():
        if clade is not tree.root and clade.branch_length is None:
            raise ValueError("canonical tree lost substitution/site branch lengths")


def pairwise_patristic(tree, raw_tip_by_mid, mids):
    terminals = {t.name: t for t in tree.get_terminals()}
    pairs = []
    distances = []
    for i, a in enumerate(mids):
        for j in range(i):
            b = mids[j]
            pairs.append((b, a))
            distances.append(float(tree.distance(terminals[raw_tip_by_mid[a]], terminals[raw_tip_by_mid[b]])))
    return pairs, np.asarray(distances, dtype=float)


def spearman_from_fixed_pairs(pairs, patristic, values):
    trait = np.asarray([abs(float(values[a]) - float(values[b])) for a, b in pairs], dtype=float)
    if len(trait) < 3 or np.allclose(trait, trait[0]) or np.allclose(patristic, patristic[0]):
        return math.nan
    xr = rankdata(patristic, method="average")
    yr = rankdata(trait, method="average")
    return float(np.corrcoef(xr, yr)[0, 1])


def rho(tree, raw_tip_by_mid, mids, values):
    pairs, patristic = pairwise_patristic(tree, raw_tip_by_mid, mids)
    return spearman_from_fixed_pairs(pairs, patristic, values)


def exact_permutation(tree, raw_tip_by_mid, mids, values):
    pairs, patristic = pairwise_patristic(tree, raw_tip_by_mid, mids)
    observed = spearman_from_fixed_pairs(pairs, patristic, values)
    ordered = [float(values[mid]) for mid in mids]
    null = []
    for perm in itertools.permutations(ordered):
        assigned = {mid: value for mid, value in zip(mids, perm)}
        rr = spearman_from_fixed_pairs(pairs, patristic, assigned)
        if math.isfinite(rr):
            null.append(rr)
    expected = math.factorial(len(mids))
    if len(null) != expected:
        raise ValueError(f"expected {expected} exact permutations, got {len(null)}")
    arr = np.asarray(null, dtype=float)
    return {
        "rho": observed,
        "exact_permutations": expected,
        "negative_tail_p": float(np.mean(arr <= observed)),
        "positive_tail_p_descriptive": float(np.mean(arr >= observed)),
        "two_sided_abs_p": float(np.mean(np.abs(arr) >= abs(observed))),
        "null_min_rho": float(np.min(arr)),
        "null_max_rho": float(np.max(arr)),
        "positive_tail_claim_boundary": "Reported descriptively only; the hypothesis direction was not redefined after inspecting the observed sign."
    }


def concept_leave_one_out(tree, raw_tip_by_mid, values):
    by = {}
    for omitted in TARGET_IDS:
        keep = [mid for mid in TARGET_IDS if mid != omitted]
        by[omitted] = rho(tree, raw_tip_by_mid, keep, values)
    vals = list(by.values())
    return {
        "rho_by_omitted_concept": by,
        "min_rho": min(vals),
        "max_rho": max(vals),
        "all_negative": all(v < 0 for v in vals),
        "all_positive": all(v > 0 for v in vals),
    }


def sparse_observation_leave_one_out(tree, raw_tip_by_mid, values, sparse):
    rows = []
    for mid in SPARSE_IDS:
        concept_rows = sparse[mid]
        for omitted in concept_rows:
            retained = [r for r in concept_rows if r["obs_id"] != omitted["obs_id"]]
            retained_cells = {r["analysis_cell"] for r in retained}
            if len(retained) < 2 or len(retained_cells) < 2:
                raise ValueError(f"dropping {mid}/{omitted['obs_id']} breaks frozen two-cell gate")
            updated = dict(values)
            updated[mid] = float(np.median([r["lightness"] for r in retained]))
            rows.append({
                "paper_japan_member_id": mid,
                "omitted_obs_id": omitted["obs_id"],
                "retained_observations": len(retained),
                "retained_analysis_cells": len(retained_cells),
                "recomputed_concept_lightness": updated[mid],
                "rho": rho(tree, raw_tip_by_mid, TARGET_IDS, updated),
            })
    rhos = [r["rho"] for r in rows]
    return {
        "predeclared_sparse_concepts": SPARSE_IDS,
        "definition": "All admitted concepts with 2-4 Japan-local strict-spatial observations at panel freeze; each deletion must retain >=2 observations and >=2 cells.",
        "cases": rows,
        "n_cases": len(rows),
        "min_rho": min(rhos),
        "max_rho": max(rhos),
        "all_negative": all(v < 0 for v in rhos),
        "all_positive": all(v > 0 for v in rhos),
    }


def pairwise_rows(tree, raw_tip_by_mid, values):
    pairs, distances = pairwise_patristic(tree, raw_tip_by_mid, TARGET_IDS)
    return [
        {
            "concept_a": a,
            "concept_b": b,
            "patristic_distance": float(d),
            "absolute_lightness_difference": abs(float(values[a]) - float(values[b])),
        }
        for (a, b), d in zip(pairs, distances)
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tree", type=Path, required=True)
    parser.add_argument("--concept-map", type=Path, required=True)
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--sparse-observations", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    panel = read_panel(args.panel)
    sparse = read_sparse(args.sparse_observations, panel)
    cmap = read_concept_map(args.concept_map)
    tree = Phylo.read(str(args.tree), "newick")
    validate_tree(tree, cmap)
    raw_tip_by_mid = {mid: cmap[mid][0] for mid in TARGET_IDS}
    values = {mid: panel[mid]["local_lightness"] for mid in TARGET_IDS}

    signal = exact_permutation(tree, raw_tip_by_mid, TARGET_IDS, values)
    concept_loo = concept_leave_one_out(tree, raw_tip_by_mid, values)
    sparse_loo = sparse_observation_leave_one_out(tree, raw_tip_by_mid, values, sparse)

    directional_pass = bool(
        signal["rho"] < 0
        and signal["negative_tail_p"] <= 0.05
        and concept_loo["all_negative"]
        and sparse_loo["all_negative"]
    )
    strict_pass = bool(directional_pass and signal["two_sided_abs_p"] <= 0.05)

    result = {
        "contract_version": "japan7_source_balanced_lightness_history_v1",
        "status_date": "2026-08-27",
        "question": "Does the previously observed directional anti-phylogenetic L* pattern replicate in seven identity-resolved Japan-local concepts when all phenotype evidence comes from the same frozen Azami strict-spatial detector/crop pipeline?",
        "concept_panel": TARGET_IDS,
        "n_concepts": 7,
        "lightness_values": values,
        "evidence_contract": {
            "source_class": "single frozen Azami strict-spatial detector/crop continuous-colour cohort",
            "source_run": 29306454759,
            "source_artifact": 8301295025,
            "source_rows": 46276,
            "admission_rule": ">=2 Japan-local colour-usable observations AND >=2 distinct analysis cells; exact concept identity",
            "source_balanced": True,
            "external_direct_images_used": False,
        },
        "tree_contract": {
            "source": "frozen Japan38 Comp1061 compatibility ML tree",
            "branch_length_semantics": "substitutions/site; not absolute time",
        },
        "primary_signal": signal,
        "concept_leave_one_out": concept_loo,
        "sparse_observation_leave_one_out": sparse_loo,
        "pairwise_values": pairwise_rows(tree, raw_tip_by_mid, values),
        "predeclared_gates": {
            "directional_replication_rule": "rho < 0 AND exact negative-tail p <= 0.05 AND all concept-LOO rho < 0 AND all sparse-observation-LOO rho < 0",
            "directional_replication_pass": directional_pass,
            "strict_two_sided_rule": "directional replication pass AND exact two-sided |rho| p <= 0.05",
            "strict_two_sided_replication_pass": strict_pass,
            "panel_or_threshold_changed_after_result": False,
        },
        "frozen_prior_results": {
            "japan5_baseline_rho": -0.10303030303030303,
            "harmonized5_rho": -0.01818181818181818,
            "expanded6_rho": 0.06071428571428571,
            "note": "These remain frozen prior analyses and are not replaced by Japan7."
        },
        "claim_boundary": "Continuous local L* phylogenetic-structure diagnostic only. A failed anti-phylogenetic gate blocks promotion of the global species-proxy lightness result to the Japanese radiation at this evidence stage. A positive rho is not post-hoc evidence of phylogenetic conservatism unless independently preregistered and tested. No W/C state, transition direction, ancestry, convergence, adaptation, adaptive radiation, evolutionary rate or molecular reactivation is inferred."
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
