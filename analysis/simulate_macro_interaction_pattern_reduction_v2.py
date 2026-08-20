#!/usr/bin/env python3
"""Robust pattern-reduction screen for the Azami -> EAzami bridge.

v2 addresses two weaknesses of v1:
1) it does not rank families from one lucky best draw; it summarizes the top 5% core-fitting
   draws across multiple deterministic seeds;
2) it evaluates independent/held-out interaction patterns that were not used to define the
   compact core distance, while explicitly marking mechanisms that the current toy generator
   cannot represent.

This remains an ABC-like structural sufficiency screen, not fitted parameter inference.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import simulate_macro_interaction_pattern_reduction as v1  # noqa: E402


def q(values, p):
    vals = sorted(values)
    if not vals:
        return None
    if len(vals) == 1:
        return vals[0]
    x = (len(vals) - 1) * p
    lo = int(math.floor(x)); hi = int(math.ceil(x))
    if lo == hi:
        return vals[lo]
    return vals[lo] * (hi - x) + vals[hi] * (x - lo)


def load_v2_targets(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    by = {r["target_id"]: r for r in rows}
    required = {
        "INT_PITCHERI_WEEVIL_RR",
        "INT_PURP_PROBE_R2",
        "INT_PURP_PRED_KAWAMATA",
        "INT_CAPSIZE_INFEST_20SP",
        "INT_DECU_CAPSIZE_ATTACK",
        "INT_SCENT_DUAL_GUILDS",
        "INT_CREM_NODDING_ACHENE_RR",
        "INT_CREM_POLLINATOR_NULL",
        "INT_STICKINESS_NULL",
        "INT_HELIANTHUS_ALLDAY_NULL",
    }
    missing = required - set(by)
    if missing:
        raise ValueError(f"missing v2 targets: {sorted(missing)}")
    return rows, by


def heldout_checks(summary, targets):
    """Checks only patterns represented by the current v1 generator.

    Different-trait analogues are labelled explicitly and never treated as direct mechanistic
    reproduction. Unrepresented targets are carried separately as structural gaps.
    """
    pitcheri = float(targets["INT_PITCHERI_WEEVIL_RR"]["target_value"])
    probe = float(targets["INT_PURP_PROBE_R2"]["target_value"])
    pred_k = float(targets["INT_PURP_PRED_KAWAMATA"]["target_value"])
    rr = summary["reduced_herbivory_seed_output_RR"]
    poll_r2 = summary["display_pollinator_R2"]
    ant_r2 = summary["display_antagonist_R2"]
    return {
        # Independent taxon, same fitness-cost axis. Broad 1.5-fold tolerance because the
        # pitcheri contrast is observational infestation, not experimental exclusion.
        "pitcheri_seed_cost_external": abs(math.log(rr / pitcheri)) <= math.log(1.5),
        # Same species but held out from core distance; checks numerical stability across two
        # pollinator response definitions and two antagonist populations.
        "purpuratum_heads_probed_R2": abs(poll_r2 - probe) <= 0.20,
        "purpuratum_kawamata_predation_R2": abs(ant_r2 - pred_k) <= 0.20,
        # Cross-study/cross-taxon sign replication for large display -> greater enemy exposure.
        "capitulum_size_attack_sign_generalizes": summary["display_antagonist_r"] > 0,
        # Cross-trait analogue only: the generator has one generic advertisement axis, while
        # the empirical held-out study is floral scent. This checks the shared-signal principle.
        "shared_signal_can_attract_both_guilds_analogue": (
            summary["display_pollinator_r"] > 0 and summary["display_antagonist_r"] > 0
        ),
    }


STRUCTURAL_GAPS = {
    "flower_colour_pollinator_preference": "Generator lacks a morph-specific colour-choice experiment layer.",
    "stickiness_null": "Generic defence axis cannot be identified with C. discolor stickiness.",
    "nodding_abiotic_achene_RR": "Generator lacks a paired orientation intervention under rain/UV; empirical RR is 56.3/15.7 = 3.586.",
    "nodding_pollinator_null": "Generator does not separate abiotic orientation benefit from pollinator orientation response.",
    "orientation_time_window": "Generator has no within-day state, so early-morning Helianthus effect plus all-day null is not representable.",
    "year_dependent_tolerance": "Generator has no multi-year compensatory state for C. undulatum.",
}


def summarize_family(family, core_targets, v2_targets, seeds, draws_per_seed, accept_fraction):
    runs = []
    for seed in seeds:
        for i in range(draws_per_seed):
            summary = v1.simulate_once(family, seed + i)
            checks, nmatch, distance = v1.evaluate(summary, core_targets)
            held = heldout_checks(summary, v2_targets)
            runs.append({
                "seed": seed + i,
                "summary": summary,
                "core_checks": checks,
                "core_match_count": nmatch,
                "core_distance": distance,
                "heldout_checks": held,
            })
    # ABC-like acceptance: prioritize maximum discrete core match, then continuous distance.
    runs.sort(key=lambda r: (-r["core_match_count"], r["core_distance"]))
    n_accept = max(20, int(math.ceil(len(runs) * accept_fraction)))
    accepted = runs[:n_accept]
    held_keys = sorted(accepted[0]["heldout_checks"])
    held_rates = {
        k: sum(1 for r in accepted if r["heldout_checks"][k]) / len(accepted)
        for k in held_keys
    }
    full_core = sum(1 for r in runs if all(r["core_checks"].values())) / len(runs)
    distances = [r["core_distance"] for r in accepted]
    matches = [r["core_match_count"] for r in accepted]
    held_mean = statistics.mean(held_rates.values())
    best = accepted[0]
    return {
        "family": family,
        "total_draws": len(runs),
        "accepted_draws": len(accepted),
        "accept_fraction": accept_fraction,
        "best_core_match_count": best["core_match_count"],
        "best_core_distance": round(best["core_distance"], 6),
        "full_core_match_rate_all_draws": round(full_core, 6),
        "accepted_core_match_median": statistics.median(matches),
        "accepted_core_distance_median": round(statistics.median(distances), 6),
        "accepted_core_distance_q10_q90": [round(q(distances, 0.10), 6), round(q(distances, 0.90), 6)],
        "heldout_reproduction_rates": {k: round(v, 4) for k, v in held_rates.items()},
        "heldout_mean_reproduction_rate": round(held_mean, 4),
        "best_summary": {k: round(v, 6) for k, v in sorted(best["summary"].items())},
    }


def run(target_path: Path, draws_per_seed: int, seeds: list[int], accept_fraction: float):
    rows, targets = load_v2_targets(target_path)
    # v1 evaluator expects the same named core targets; v2 registry is a superset.
    families = [
        summarize_family(f, targets, targets, seeds, draws_per_seed, accept_fraction)
        for f in v1.FAMILIES
    ]
    ranking = sorted(
        families,
        key=lambda x: (
            -x["accepted_core_match_median"],
            x["accepted_core_distance_median"],
            -x["heldout_mean_reproduction_rate"],
            -x["full_core_match_rate_all_draws"],
        ),
    )
    roles = {}
    for r in rows:
        roles[r["simulation_role"]] = roles.get(r["simulation_role"], 0) + 1
    return {
        "contract_version": "macro_interaction_pattern_reduction_simulation_v2",
        "status_date": "2026-08-20",
        "purpose": "multi_seed_abc_like_structural_sufficiency_with_heldout_literature_validation",
        "target_registry": str(target_path),
        "target_rows_total": len(rows),
        "target_roles": roles,
        "core_targets_scored": 11,
        "heldout_checks_represented": 5,
        "structural_gaps": STRUCTURAL_GAPS,
        "draws_per_seed_per_family": draws_per_seed,
        "seeds": seeds,
        "accept_fraction": accept_fraction,
        "families": families,
        "ranking": [x["family"] for x in ranking],
        "best_family_by_robust_pattern_score": ranking[0]["family"],
        "interpretation_boundary": (
            "v2 asks whether a model family repeatedly generates the core Azami+interaction bundle and then generalizes to held-out patterns. "
            "Acceptance is ABC-like ranking under declared priors, not a likelihood, posterior model probability, Bayes factor, or causal proof. "
            "Held-out checks labelled as analogues test a structural principle, not trait-specific mechanistic identity."
        ),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--targets", type=Path, required=True)
    p.add_argument("--draws-per-seed", type=int, default=180)
    p.add_argument("--seeds", default="20260820,20261820,20262820,20263820")
    p.add_argument("--accept-fraction", type=float, default=0.05)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    seeds = [int(x) for x in args.seeds.split(",") if x.strip()]
    result = run(args.targets, args.draws_per_seed, seeds, args.accept_fraction)
    text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
