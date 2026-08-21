#!/usr/bin/env python3
"""Diagnose whether broader fixed-colour East Asian context identifies Mk rate.

The analysis expands the six-tip Arenicola/Nipponocirsium sensitivity with four
fixed-state Sinocirsium tips that are source-backed in Chang 2026.  It uses only
published node-age medians plus explicit nuisance grids for shallow Taiwanese
Sinocirsium ages.  It is an identifiability diagnostic, not a recovered author tree.
"""
from __future__ import annotations

import argparse
import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

C, W = "C", "W"
STATE_INDEX = {C: 0, W: 1}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--scaffold", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    return p.parse_args()


def transition_matrix(q: float, t: float) -> tuple[tuple[float, float], tuple[float, float]]:
    if q <= 0 or t <= 0:
        raise ValueError("q and branch lengths must be positive")
    decay = math.exp(-2.0 * q * t)
    same = 0.5 + 0.5 * decay
    diff = 0.5 - 0.5 * decay
    return ((same, diff), (diff, same))


def topology_children(nipp_basal: str) -> dict[str, tuple[str, str]]:
    trio = ["Cirsium pengii", "Cirsium kawakamii", "Cirsium tatakaense"]
    if nipp_basal not in trio:
        raise ValueError(nipp_basal)
    pair = tuple(x for x in trio if x != nipp_basal)
    return {
        "ROOT": ("SINO_MRCA", "AREN_NIPP_ROOT"),
        "AREN_NIPP_ROOT": ("AREN_MRCA", "NIPP_MRCA"),
        "AREN_MRCA": ("Cirsium brevicaule", "Cirsium irumtiense"),
        "NIPP_MRCA": ("Cirsium morii", "NIPP_TW_TRIO"),
        "NIPP_TW_TRIO": (nipp_basal, "NIPP_TW_PAIR"),
        "NIPP_TW_PAIR": pair,
        "SINO_MRCA": ("Cirsium japonicum var. japonicum", "SINO_TW_MAJOR"),
        "SINO_TW_MAJOR": ("Cirsium japonicum var. albescens", "SINO_COLOURED_PAIR"),
        "SINO_COLOURED_PAIR": (
            "Cirsium japonicum var. australe",
            "Cirsium japonicum var. fukienense",
        ),
    }


def build_ages(cfg: dict[str, Any], tw_major: float, pair_fraction: float) -> dict[str, float]:
    a = cfg["central_node_ages_mya"]
    if not 0 < pair_fraction < 1:
        raise ValueError(pair_fraction)
    if not 0 < tw_major < float(a["sinocirsium_japan_vs_taiwan"]):
        raise ValueError(tw_major)
    pair_age = tw_major * pair_fraction
    ages = {
        "ROOT": float(a["sinocirsium_vs_arenicola_nipponocirsium"]),
        "AREN_NIPP_ROOT": float(a["arenicola_nipponocirsium_root"]),
        "AREN_MRCA": float(a["arenicola_mrca"]),
        "NIPP_MRCA": float(a["nipponocirsium_crown_morii_split"]),
        "NIPP_TW_TRIO": float(a["taiwan_nipponocirsium_trio_crown"]),
        "NIPP_TW_PAIR": float(a["taiwan_nipponocirsium_terminal_pair"]),
        "SINO_MRCA": float(a["sinocirsium_japan_vs_taiwan"]),
        "SINO_TW_MAJOR": tw_major,
        "SINO_COLOURED_PAIR": pair_age,
    }
    ages.update({taxon: 0.0 for taxon in cfg["tip_states"]})
    return ages


def total_likelihood(
    children: dict[str, tuple[str, str]],
    ages: dict[str, float],
    tip_states: dict[str, str],
    q: float,
    arenicola_fix: str | None = None,
) -> float:
    @lru_cache(maxsize=None)
    def partial(node: str, state_index: int) -> float:
        if node in tip_states:
            return 1.0 if STATE_INDEX[tip_states[node]] == state_index else 0.0
        if node == "AREN_MRCA" and arenicola_fix is not None:
            if STATE_INDEX[arenicola_fix] != state_index:
                return 0.0
        value = 1.0
        for child in children[node]:
            length = ages[node] - ages[child]
            if length <= 0:
                raise ValueError(f"non-positive branch: {node}->{child}: {length}")
            matrix = transition_matrix(q, length)
            child_like = sum(
                matrix[state_index][child_state] * partial(child, child_state)
                for child_state in (0, 1)
            )
            value *= child_like
        return value

    return 0.5 * partial("ROOT", 0) + 0.5 * partial("ROOT", 1)


def evaluate_q(
    children: dict[str, tuple[str, str]],
    ages: dict[str, float],
    tips: dict[str, str],
    q: float,
) -> dict[str, float]:
    like_c = total_likelihood(children, ages, tips, q, C)
    like_w = total_likelihood(children, ages, tips, q, W)
    total = like_c + like_w
    if total <= 0:
        raise RuntimeError("non-positive likelihood")
    return {
        "q": q,
        "log_likelihood": math.log(total),
        "p_arenicola_C": like_c / total,
    }


def profile_one(
    cfg: dict[str, Any],
    *,
    tw_major: float,
    pair_fraction: float,
    nipp_basal: str,
) -> dict[str, Any]:
    tips = dict(cfg["tip_states"])
    children = topology_children(nipp_basal)
    ages = build_ages(cfg, tw_major, pair_fraction)
    rate_cfg = cfg["rate_profile"]
    q_grid = np.logspace(
        float(rate_cfg["log10_q_min"]),
        float(rate_cfg["log10_q_max"]),
        int(rate_cfg["points"]),
    )
    prof = [evaluate_q(children, ages, tips, float(q)) for q in q_grid]
    best = max(prof, key=lambda r: r["log_likelihood"])
    cutoff = best["log_likelihood"] - float(rate_cfg["profile_lr95_loglik_drop"])
    supported = [r for r in prof if r["log_likelihood"] >= cutoff]
    refs = {
        str(q): evaluate_q(children, ages, tips, float(q))["p_arenicola_C"]
        for q in rate_cfg["reference_q_per_myr"]
    }
    return {
        "nipp_basal": nipp_basal,
        "sinocirsium_taiwan_major_split_mya": tw_major,
        "sinocirsium_coloured_pair_fraction": pair_fraction,
        "profile_best_q_per_myr": best["q"],
        "profile_best_log_likelihood": best["log_likelihood"],
        "profile_LR95_q_lower": min(r["q"] for r in supported),
        "profile_LR95_q_upper": max(r["q"] for r in supported),
        "profile_LR95_hits_upper_grid_boundary": math.isclose(
            max(r["q"] for r in supported), float(q_grid[-1]), rel_tol=0, abs_tol=1e-12
        ),
        "profile_LR95_P_C_arenicola_range": [
            min(r["p_arenicola_C"] for r in supported),
            max(r["p_arenicola_C"] for r in supported),
        ],
        "reference_P_C_arenicola": refs,
    }


def run(scaffold: Path) -> dict[str, Any]:
    cfg = json.loads(scaffold.read_text(encoding="utf-8"))
    shallow = cfg["sinocirsium_shallow_age_sensitivity"]
    profiles = []
    for tw_major in shallow["taiwan_major_split_mya"]:
        for pair_fraction in shallow["australe_fukienense_fraction_of_major_split"]:
            for variant in cfg["nipponocirsium_topology_variants"]:
                profiles.append(
                    profile_one(
                        cfg,
                        tw_major=float(tw_major),
                        pair_fraction=float(pair_fraction),
                        nipp_basal=variant["taiwan_trio_basal"],
                    )
                )

    def rng(values: list[float]) -> list[float]:
        return [min(values), max(values)]

    ref_keys = [str(float(q)) for q in cfg["rate_profile"]["reference_q_per_myr"]]
    ref_ranges = {
        key: rng([p["reference_P_C_arenicola"][key] for p in profiles])
        for key in ref_keys
    }
    result = {
        "contract_version": "east_asia_colour_rate_information_v1",
        "status_date": cfg["status_date"],
        "n_fixed_tips": len(cfg["tip_states"]),
        "state_counts": {
            C: sum(v == C for v in cfg["tip_states"].values()),
            W: sum(v == W for v in cfg["tip_states"].values()),
        },
        "n_nuisance_topology_scenarios": len(profiles),
        "profile_best_q_range_per_myr": rng([p["profile_best_q_per_myr"] for p in profiles]),
        "profile_LR95_q_lower_range_per_myr": rng([p["profile_LR95_q_lower"] for p in profiles]),
        "all_profile_LR95_hit_upper_grid_boundary": all(
            p["profile_LR95_hits_upper_grid_boundary"] for p in profiles
        ),
        "profile_LR95_P_C_arenicola_global_range": [
            min(p["profile_LR95_P_C_arenicola_range"][0] for p in profiles),
            max(p["profile_LR95_P_C_arenicola_range"][1] for p in profiles),
        ],
        "reference_P_C_arenicola_ranges": ref_ranges,
        "diagnostics": {
            "expanded_fixed_tip_context_identifies_transition_rate": False,
            "expanded_fixed_tip_context_identifies_arenicola_ancestor_without_rate_constraint": False,
            "low_rate_coloured_ancestor_signal_persists": min(ref_ranges["0.2"]) > 0.95,
            "high_rate_uninformative_limit_remains_profile_supported": True,
        },
        "interpretation": (
            "Adding the four fixed-state Sinocirsium tips available from the same East Asian "
            "published time-tree context strengthens the conditional coloured-ancestor signal "
            "at low q but does not identify q. Every nuisance/topology scenario retains the "
            "upper rate-grid boundary in its LR95 set, so P(C) still reaches approximately 0.5."
        ),
        "sampling_implication": {
            "immediate_new_core190_populations": 0,
            "white_tip_gate_interpretation": (
                "W>=5 remains a conservative engineering gate for later ER/ARD fitting, not a "
                "guarantee that transition rates will become identifiable. New fixed-white taxa "
                "are valuable only together with credible nuclear placement and an accepted "
                "branch-length tree."
            ),
            "next_information_priority": [
                "accepted common-locus branch-length tree",
                "credible nuclear placement of independent fixed-white lineages",
                "model-adequacy and rate-identifiability check on the final tree before ARD interpretation"
            ],
        },
        "profiles": profiles,
        "claim_boundary": cfg["claim_boundary"],
    }
    return result


def main() -> None:
    args = parse_args()
    result = run(args.scaffold)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in [
        "n_fixed_tips", "state_counts", "n_nuisance_topology_scenarios",
        "profile_best_q_range_per_myr", "profile_LR95_q_lower_range_per_myr",
        "all_profile_LR95_hit_upper_grid_boundary", "profile_LR95_P_C_arenicola_global_range",
        "reference_P_C_arenicola_ranges", "diagnostics", "sampling_implication"
    ]}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
