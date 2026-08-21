#!/usr/bin/env python3
"""Diagnose flower-colour ASR identifiability on a published-age East Asian scaffold.

The purpose is not to manufacture a final phylogeny. We ask a narrower question:
if the source-backed topology fragments are given approximate published node ages, does
a symmetric binary Mk model identify the Arenicola MRCA state without a transition-rate
assumption?

Only standard-library code is used. The five internal node states are enumerated exactly.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path

W, C = 0, 1
INTERNAL = [
    "root",
    "arenicola_mrca",
    "nipponocirsium_crown",
    "taiwan_trio_crown",
    "terminal_pair_mrca",
]
TIP_KEY = {
    "Cirsium brevicaule": "brevicaule",
    "Cirsium irumtiense": "irumtiense",
    "Cirsium morii": "morii",
    "Cirsium pengii": "pengii",
    "Cirsium kawakamii": "kawakamii",
    "Cirsium tatakaense": "tatakaense",
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--scaffold", type=Path, required=True)
    p.add_argument("--output", type=Path)
    return p.parse_args()


def transition_probability(parent: int, child: int, q: float, branch_myr: float) -> float:
    if q < 0 or branch_myr < 0:
        raise ValueError("q and branch length must be nonnegative")
    decay = math.exp(-2.0 * q * branch_myr)
    same = 0.5 + 0.5 * decay
    return same if parent == child else 1.0 - same


def build_tree(scaffold: dict, basal_taxon: str) -> dict[str, tuple[float, list[str]]]:
    ages = scaffold["central_node_ages_mya"]
    basal = TIP_KEY[basal_taxon]
    trio = ["pengii", "kawakamii", "tatakaense"]
    pair = [x for x in trio if x != basal]
    return {
        "root": (float(ages["arenicola_nipponocirsium_root"]), ["arenicola_mrca", "nipponocirsium_crown"]),
        "arenicola_mrca": (float(ages["arenicola_mrca"]), ["brevicaule", "irumtiense"]),
        "nipponocirsium_crown": (float(ages["nipponocirsium_crown_morii_split"]), ["morii", "taiwan_trio_crown"]),
        "taiwan_trio_crown": (float(ages["taiwan_trio_crown"]), [basal, "terminal_pair_mrca"]),
        "terminal_pair_mrca": (float(ages["terminal_pair_mrca"]), pair),
        "brevicaule": (0.0, []),
        "irumtiense": (0.0, []),
        "morii": (0.0, []),
        "pengii": (0.0, []),
        "kawakamii": (0.0, []),
        "tatakaense": (0.0, []),
    }


def tip_states(scaffold: dict) -> dict[str, int]:
    convert = {"W": W, "C": C}
    return {TIP_KEY[name]: convert[state] for name, state in scaffold["tip_states"].items()}


def exact_likelihood_and_marginals(
    tree: dict[str, tuple[float, list[str]]], states: dict[str, int], q: float, root_prior=(0.5, 0.5)
) -> tuple[float, dict[str, list[float]]]:
    total = 0.0
    marg = {node: [0.0, 0.0] for node in INTERNAL}
    for values in itertools.product((W, C), repeat=len(INTERNAL)):
        assignment = dict(zip(INTERNAL, values))
        assignment.update(states)
        weight = float(root_prior[assignment["root"]])
        for parent, (parent_age, children) in tree.items():
            for child in children:
                child_age = tree[child][0]
                weight *= transition_probability(
                    assignment[parent], assignment[child], q, parent_age - child_age
                )
        total += weight
        for node in INTERNAL:
            marg[node][assignment[node]] += weight
    if total <= 0:
        raise RuntimeError("likelihood underflowed to zero")
    for node in INTERNAL:
        marg[node] = [x / total for x in marg[node]]
    return total, marg


def logspace(log10_min: float, log10_max: float, points: int) -> list[float]:
    if points < 2:
        raise ValueError("rate grid needs at least two points")
    step = (log10_max - log10_min) / (points - 1)
    return [10 ** (log10_min + i * step) for i in range(points)]


def first_q_below(rows: list[dict], key: str, threshold: float):
    for row in rows:
        if row[key] < threshold:
            return row["q_per_myr"]
    return None


def profile_one(scaffold: dict, variant: dict) -> dict:
    tree = build_tree(scaffold, variant["taiwan_trio_basal"])
    states = tip_states(scaffold)
    prior = scaffold["root_prior"]
    root_prior = (float(prior["W"]), float(prior["C"]))
    grid_cfg = scaffold["rate_grid_per_myr"]
    q_grid = logspace(
        float(grid_cfg["log10_min"]), float(grid_cfg["log10_max"]), int(grid_cfg["points"])
    )
    rows = []
    for q in q_grid:
        likelihood, marg = exact_likelihood_and_marginals(tree, states, q, root_prior)
        rows.append({
            "q_per_myr": q,
            "log_likelihood": math.log(likelihood),
            "P_C_root": marg["root"][C],
            "P_C_arenicola_mrca": marg["arenicola_mrca"][C],
            "P_C_nipponocirsium_crown": marg["nipponocirsium_crown"][C],
        })
    best_i = max(range(len(rows)), key=lambda i: rows[i]["log_likelihood"])
    max_ll = rows[best_i]["log_likelihood"]
    lr95 = [r for r in rows if 2.0 * (max_ll - r["log_likelihood"]) <= 3.841458820694124]
    ref = []
    for q in scaffold["reference_rates_per_myr"]:
        likelihood, marg = exact_likelihood_and_marginals(tree, states, float(q), root_prior)
        ref.append({
            "q_per_myr": float(q),
            "log_likelihood": round(math.log(likelihood), 8),
            "P_C_root": round(marg["root"][C], 8),
            "P_C_arenicola_mrca": round(marg["arenicola_mrca"][C], 8),
        })
    p_range = [min(r["P_C_arenicola_mrca"] for r in lr95), max(r["P_C_arenicola_mrca"] for r in lr95)]
    return {
        "topology_variant": variant["id"],
        "taiwan_trio_basal": variant["taiwan_trio_basal"],
        "profile_best_q_per_myr": round(rows[best_i]["q_per_myr"], 8),
        "profile_best_log_likelihood": round(max_ll, 8),
        "best_at_lower_grid_boundary": best_i == 0,
        "best_at_upper_grid_boundary": best_i == len(rows) - 1,
        "profile_LR95_q_lower": round(lr95[0]["q_per_myr"], 8),
        "profile_LR95_q_upper": round(lr95[-1]["q_per_myr"], 8),
        "profile_LR95_hits_upper_grid_boundary": lr95[-1] is rows[-1],
        "profile_LR95_P_C_arenicola_range": [round(p_range[0], 8), round(p_range[1], 8)],
        "q_where_P_C_arenicola_first_below_0_75": (
            None if first_q_below(rows, "P_C_arenicola_mrca", 0.75) is None
            else round(first_q_below(rows, "P_C_arenicola_mrca", 0.75), 8)
        ),
        "reference_rate_sensitivity": ref,
    }


def run(scaffold_path: Path) -> dict:
    scaffold = json.loads(scaffold_path.read_text(encoding="utf-8"))
    profiles = [profile_one(scaffold, x) for x in scaffold["topology_variants"]]
    primary = profiles[0]
    primary_ref = {x["q_per_myr"]: x for x in primary["reference_rate_sensitivity"]}
    all_low_q_coloured = all(
        next(x for x in p["reference_rate_sensitivity"] if x["q_per_myr"] == 0.2)["P_C_arenicola_mrca"] > 0.85
        for p in profiles
    )
    all_profile_include_uninformative = all(
        p["profile_LR95_P_C_arenicola_range"][0] <= 0.51 and p["profile_LR95_P_C_arenicola_range"][1] >= 0.85
        for p in profiles
    )
    return {
        "contract_version": "arenicola_dated_asr_rate_identifiability_v1",
        "status_date": scaffold["status_date"],
        "model": "binary_symmetric_Mk_ER_with_equal_root_prior",
        "profiles": profiles,
        "primary_topology_key_results": {
            "P_C_arenicola_at_q_0_2": primary_ref[0.2]["P_C_arenicola_mrca"],
            "P_C_arenicola_at_q_0_5": primary_ref[0.5]["P_C_arenicola_mrca"],
            "P_C_arenicola_at_q_1": primary_ref[1.0]["P_C_arenicola_mrca"],
            "profile_best_at_upper_rate_boundary": primary["best_at_upper_grid_boundary"],
            "profile_LR95_hits_upper_rate_boundary": primary["profile_LR95_hits_upper_grid_boundary"],
        },
        "diagnostics": {
            "all_topology_variants_support_coloured_MRCA_if_q_0_2": all_low_q_coloured,
            "all_topology_variants_profile_support_spans_coloured_to_uninformative": all_profile_include_uninformative,
            "rate_is_identified_from_six_tip_colour_pattern": False,
            "ancestral_state_is_identified_without_rate_constraint": False,
        },
        "interpretation": (
            "Published time information does not by itself resolve Arenicola flower-colour polarity. "
            "At low symmetric transition rates the coloured MRCA receives high conditional support, consistent with the parsimony result. "
            "However the likelihood profile permits high transition rates, under which the Arenicola MRCA approaches 0.5/0.5. "
            "Therefore the current coloured-ancestor preference is conditional on a low-change regime rather than identified by the six-tip colour data alone."
        ),
        "sampling_implication": {
            "immediate_new_focal_populations": 0,
            "higher_value_information": [
                "machine-readable branch-length topology ensemble",
                "broader source-backed sister/root flower-colour states",
                "transition-rate information from a broader phylogenetically matched colour dataset"
            ],
            "population_sampling_role": "P001-P008 remain necessary for standing variation versus introgression/gene-flow inference, not for solving deep ASR polarity by sample count alone."
        },
        "claim_boundary": scaffold["claim_boundary"],
    }


def main() -> None:
    args = parse_args()
    result = run(args.scaffold)
    text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
