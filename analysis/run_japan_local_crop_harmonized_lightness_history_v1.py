#!/usr/bin/env python3
"""Run frozen crop-harmonized Japan-local continuous-lightness panels.

Two panels are evaluated from one predeclared contract:
1. ``harmonized5`` changes only the JPN30 measurement source relative to the
   frozen five-concept baseline and is a source-harmonization sensitivity.
2. ``expanded6`` adds independently admitted JPN05 and is the first coverage
   expansion beyond five concepts.

For each panel, all label permutations are enumerated exactly. The directional
anti-phylogenetic gate is unchanged from the frozen Japan5 analysis:
    rho < 0 AND negative-tail p <= 0.05 AND every leave-one-out rho < 0.
A stricter flag also requires two-sided |rho| p <= 0.05.

No result is a discrete W/C transition, convergence, adaptation, dating or rate
analysis.
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


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_concept_map(path: Path):
    rows = read_csv(path)
    if len(rows) != 38:
        raise ValueError(f"expected 38 concepts, found {len(rows)}")
    cmap = {r["paper_japan_member_id"]: [x for x in r["tip_ids"].split("|") if x] for r in rows}
    return cmap


def validate_tree(tree, cmap):
    names = {t.name for t in tree.get_terminals()}
    expected = {tip for tips in cmap.values() for tip in tips} | {"OUTGROUP_saff"}
    if names != expected:
        raise ValueError(f"tree mismatch missing={sorted(expected-names)} extra={sorted(names-expected)}")
    for clade in tree.find_clades():
        if clade is not tree.root and clade.branch_length is None:
            raise ValueError("substitution-length tree contains missing branch length")


def pair_vectors(tree, raw_tip_by_mid, mids, values):
    tips = {t.name: t for t in tree.get_terminals()}
    patristic, trait, rows = [], [], []
    for i, a in enumerate(mids):
        for j in range(i):
            b = mids[j]
            d = float(tree.distance(tips[raw_tip_by_mid[a]], tips[raw_tip_by_mid[b]]))
            td = abs(float(values[a]) - float(values[b]))
            patristic.append(d); trait.append(td)
            rows.append({"concept_a": b, "concept_b": a, "patristic_distance": d, "absolute_lightness_difference": td})
    return np.asarray(patristic), np.asarray(trait), rows


def rho(tree, raw_tip_by_mid, mids, values):
    p, t, _ = pair_vectors(tree, raw_tip_by_mid, mids, values)
    if len(p) < 3 or np.allclose(p, p[0]) or np.allclose(t, t[0]):
        return math.nan
    return float(spearmanr(p, t).statistic)


def exact_signal(tree, raw_tip_by_mid, mids, values):
    observed = rho(tree, raw_tip_by_mid, mids, values)
    ordered = [values[mid] for mid in mids]
    null = []
    for perm in itertools.permutations(ordered):
        assigned = {mid: float(v) for mid, v in zip(mids, perm)}
        value = rho(tree, raw_tip_by_mid, mids, assigned)
        if math.isfinite(value):
            null.append(value)
    expected = math.factorial(len(mids))
    if len(null) != expected:
        raise ValueError(f"expected {expected} exact permutations, got {len(null)}")
    return {
        "rho": observed,
        "exact_permutations": len(null),
        "negative_tail_p": sum(v <= observed for v in null) / len(null),
        "positive_tail_p": sum(v >= observed for v in null) / len(null),
        "two_sided_abs_p": sum(abs(v) >= abs(observed) for v in null) / len(null),
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


def analyze_panel(tree, cmap, panel_name, panel, common_gate):
    mids = panel["concept_order"]
    values = {mid: float(panel["lightness"][mid]) for mid in mids}
    raw_tip_by_mid = {}
    for mid in mids:
        tips = cmap.get(mid, [])
        if len(tips) != 1:
            raise ValueError(f"{panel_name}:{mid} requires exactly one nuclear tip, got {tips}")
        raw_tip_by_mid[mid] = tips[0]
    signal = exact_signal(tree, raw_tip_by_mid, mids, values)
    if signal["exact_permutations"] != int(panel["expected_exact_permutations"]):
        raise ValueError(f"{panel_name} permutation total changed")
    loo = leave_one_out(tree, raw_tip_by_mid, mids, values)
    _, _, pairs = pair_vectors(tree, raw_tip_by_mid, mids, values)
    directional = bool(signal["rho"] < 0 and signal["negative_tail_p"] <= 0.05 and loo["all_negative"])
    strict = bool(directional and signal["two_sided_abs_p"] <= 0.05)
    return {
        "analysis_role": panel["analysis_role"],
        "concept_panel": mids,
        "n_concepts": len(mids),
        "lightness_values": values,
        "source_class": panel["source_class"],
        "raw_tree_tips": raw_tip_by_mid,
        "primary_signal": signal,
        "leave_one_out": loo,
        "pairwise_values": pairs,
        "predeclared_gates": {
            "directional_rule": common_gate["directional_rule"],
            "directional_pass": directional,
            "strict_two_sided_rule": common_gate["strict_two_sided_rule"],
            "strict_two_sided_pass": strict,
            "thresholds_or_panel_changed_after_result": False,
        },
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--tree", type=Path, required=True)
    p.add_argument("--concept-map", type=Path, required=True)
    p.add_argument("--contract", type=Path, required=True)
    p.add_argument("--baseline", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()

    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    if contract["contract_version"] != "japan_local_crop_harmonized_lightness_analysis_contract_v1":
        raise ValueError("unexpected analysis contract")
    if contract["frozen_before_execution"] is not True:
        raise ValueError("analysis contract was not frozen before execution")
    if set(contract["panels"]) != {"harmonized5", "expanded6"}:
        raise ValueError("panel set changed")
    cmap = read_concept_map(args.concept_map)
    tree = Phylo.read(str(args.tree), "newick")
    validate_tree(tree, cmap)
    baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
    if baseline["contract_version"] != "japan5_population_matched_lightness_history_v1":
        raise ValueError("wrong frozen baseline")

    results = {
        name: analyze_panel(tree, cmap, name, panel, contract["common_gate"])
        for name, panel in contract["panels"].items()
    }
    h5 = results["harmonized5"]
    e6 = results["expanded6"]
    result = {
        "contract_version": "japan_local_crop_harmonized_lightness_history_v1",
        "status_date": "2026-08-27",
        "frozen_contract": str(args.contract),
        "frozen_baseline": str(args.baseline),
        "tree_contract": contract["tree_contract"],
        "panels": results,
        "baseline_comparison": {
            "baseline_rho": baseline["primary_signal"]["rho"],
            "baseline_negative_tail_p": baseline["primary_signal"]["negative_tail_p"],
            "baseline_directional_pass": baseline["predeclared_gates"]["directional_replication_pass"],
            "harmonized5_rho": h5["primary_signal"]["rho"],
            "harmonized5_negative_tail_p": h5["primary_signal"]["negative_tail_p"],
            "harmonized5_directional_pass": h5["predeclared_gates"]["directional_pass"],
            "jpn30_lightness_shift_crop_minus_full_image": float(contract["panels"]["harmonized5"]["harmonized_jpn30_lightness"] - contract["panels"]["harmonized5"]["baseline_jpn30_lightness"]),
        },
        "coverage_expansion": {
            "baseline_n_concepts": 5,
            "expanded_n_concepts": e6["n_concepts"],
            "added_concept": "JPN_05",
            "expanded6_directional_pass": e6["predeclared_gates"]["directional_pass"],
            "expanded6_strict_two_sided_pass": e6["predeclared_gates"]["strict_two_sided_pass"],
        },
        "claim_boundary": contract["claim_boundary"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
