#!/usr/bin/env python3
"""Run the matched capitulum-space v3 screen with preregistered adequacy gates.

The first simulator implementation ranked families by relative distance but the
contract was amended, before any model-family outcome was inspected, to require
absolute fit adequacy, a minimum focal-family separation, and an absolute
replication threshold.  This wrapper is the only interpretable v3.1 entry point:
it validates those gates, runs the shared generator, applies them to the focal
common-lability versus modular-evolvability comparison, and writes the final
artifact.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import simulate_capitulum_space_mechanism_v3 as sim  # noqa: E402


EXPECTED_CONTRACT_VERSION = "capitulum_space_mechanism_v3_1_2026-08-27"
REQUIRED_PROMOTION_RULES = {
    "same_estimand_for_all_seven_primary_targets",
    "winning_accepted_primary_distance_median_at_or_below_1_0",
    "at_least_10_percent_relative_median_distance_improvement",
    "primary_distance_separation_across_all_declared_seeds",
    "winning_replication_pattern_rate_at_or_above_0_75",
    "replication_pattern_rate_not_worse_for_winning_family",
    "existing_independent_literature_heldout_rate_not_worse_for_winning_family",
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--contract", type=Path, required=True)
    p.add_argument("--structure", type=Path, required=True)
    p.add_argument("--incremental", type=Path, required=True)
    p.add_argument("--v2-heldout", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--draws-per-seed", type=int)
    p.add_argument("--seeds")
    p.add_argument("--accept-fraction", type=float)
    p.add_argument("--main-taxa", type=int, default=60)
    p.add_argument("--main-populations", type=int, default=6)
    p.add_argument("--replication-taxa", type=int, default=75)
    p.add_argument("--replication-populations", type=int, default=5)
    return p.parse_args()


def finite_number(value: Any, label: str) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be numeric") from exc
    if not math.isfinite(out):
        raise ValueError(f"{label} must be finite")
    return out


def validate_v3_1_contract(contract: dict[str, Any]) -> dict[str, float]:
    if contract.get("contract_version") != EXPECTED_CONTRACT_VERSION:
        raise ValueError(
            f"Only {EXPECTED_CONTRACT_VERSION} is interpretable; "
            f"found {contract.get('contract_version')!r}"
        )
    if contract.get("status") != "amended_before_v3_model_family_outcome_inspection":
        raise ValueError("v3.1 contract must record the pre-outcome amendment status")
    note = str(contract.get("amendment_note", ""))
    required_note_terms = ("No v3 result", "supersedes", "uninspected")
    if not all(term in note for term in required_note_terms):
        raise ValueError("Amendment note must preserve the uninspected-run boundary")

    comparison = contract["family_comparison"]
    max_distance = finite_number(
        comparison["maximum_accepted_primary_distance_median_for_adequacy"],
        "maximum accepted primary distance median",
    )
    min_improvement = finite_number(
        comparison["minimum_relative_median_distance_improvement_for_focal_promotion"],
        "minimum relative median distance improvement",
    )
    min_replication = finite_number(
        comparison["minimum_replication_pattern_rate_for_adequacy"],
        "minimum replication pattern rate",
    )
    if not 0 < max_distance <= 3:
        raise ValueError("Absolute distance adequacy threshold must be in (0, 3]")
    if not 0 < min_improvement < 1:
        raise ValueError("Minimum relative improvement must be in (0, 1)")
    if not 0 < min_replication <= 1:
        raise ValueError("Minimum replication rate must be in (0, 1]")

    promotion = set(contract["promotion_rule"]["common_vs_modular_decision_requires"])
    missing = REQUIRED_PROMOTION_RULES.difference(promotion)
    if missing:
        raise ValueError(f"Missing v3.1 promotion requirements: {sorted(missing)}")
    tie_rule = str(contract["promotion_rule"].get("tie_rule", ""))
    if not all(term in tie_rule for term in ("absolute adequacy", "minimum separation", "unresolved")):
        raise ValueError("Tie rule must retain unresolved under failed adequacy/separation")
    return {
        "maximum_primary_distance_median": max_distance,
        "minimum_relative_improvement": min_improvement,
        "minimum_replication_rate": min_replication,
    }


def apply_v3_1_gate(
    result: dict[str, Any], contract: dict[str, Any]
) -> dict[str, Any]:
    thresholds = validate_v3_1_contract(contract)
    by_family = {row["family"]: row for row in result["families"]}
    focal_names = [
        "full_tradeoff_common_lability",
        "full_tradeoff_modular_evolvability",
    ]
    focal_sorted = sorted(
        focal_names, key=lambda name: float(by_family[name]["primary_distance_median"])
    )
    winner, other = focal_sorted
    winner_row = by_family[winner]
    other_row = by_family[other]

    winner_distance = finite_number(
        winner_row["primary_distance_median"], "winning focal median distance"
    )
    other_distance = finite_number(
        other_row["primary_distance_median"], "other focal median distance"
    )
    relative_improvement = (
        (other_distance - winner_distance) / max(abs(other_distance), 1e-12)
    )
    absolute_adequacy = (
        winner_distance <= thresholds["maximum_primary_distance_median"]
    )
    minimum_separation = (
        relative_improvement >= thresholds["minimum_relative_improvement"]
    )
    replication_rate = finite_number(
        winner_row["replication_pattern_rate_mean"],
        "winning focal replication pattern rate",
    )
    replication_adequacy = (
        replication_rate >= thresholds["minimum_replication_rate"]
    )

    old_focal = result["focal_common_vs_modular"]
    seedwise_stable = bool(old_focal["seedwise_distance_winner_stable"])
    replication_not_worse = bool(old_focal["replication_not_worse"])
    heldout_not_worse = bool(old_focal["independent_v2_heldout_not_worse"])
    all_gates = {
        "absolute_primary_adequacy": absolute_adequacy,
        "minimum_relative_distance_improvement_met": minimum_separation,
        "seedwise_distance_winner_stable": seedwise_stable,
        "replication_absolute_adequacy": replication_adequacy,
        "replication_not_worse": replication_not_worse,
        "independent_v2_heldout_not_worse": heldout_not_worse,
    }
    registered_decision = winner if all(all_gates.values()) else "unresolved"

    adequate_families = [
        row["family"]
        for row in result["families"]
        if float(row["primary_distance_median"])
        <= thresholds["maximum_primary_distance_median"]
        and float(row["replication_pattern_rate_mean"])
        >= thresholds["minimum_replication_rate"]
    ]

    result["contract_version"] = contract["contract_version"]
    result["screen_version"] = "capitulum_space_mechanism_v3_1_screen_1"
    result["status"] = (
        "completed_prior_predictive_structural_sufficiency_screen_"
        "with_absolute_adequacy_gate"
    )
    result["superseded_uninspected_run_boundary"] = contract["amendment_note"]
    result["absolute_adequacy_thresholds"] = thresholds
    result["adequate_families"] = adequate_families
    result["focal_common_vs_modular"] = {
        "distance_winner": winner,
        "other": other,
        "winner_primary_distance_median": winner_distance,
        "other_primary_distance_median": other_distance,
        "relative_median_distance_improvement": relative_improvement,
        "winner_replication_pattern_rate": replication_rate,
        **all_gates,
        "registered_decision": registered_decision,
        "decision_reason": (
            "winner_promoted_under_all_preregistered_v3_1_gates"
            if registered_decision != "unresolved"
            else "one_or_more_absolute_adequacy_separation_replication_or_heldout_gates_failed"
        ),
    }
    return result


def main() -> int:
    args = parse_args()
    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    comparison = contract["family_comparison"]
    validate_v3_1_contract(contract)
    draws = args.draws_per_seed or int(comparison["draws_per_seed_per_family"])
    seeds = (
        [int(x) for x in args.seeds.split(",") if x.strip()]
        if args.seeds
        else [int(x) for x in comparison["seeds"]]
    )
    accept_fraction = args.accept_fraction or float(comparison["accept_fraction"])
    if draws <= 0 or not seeds or not 0 < accept_fraction <= 0.2:
        raise ValueError("Invalid screen parameters")

    targets = sim.load_observed(contract, args.structure, args.incremental)
    heldout = sim.load_v2_heldout(args.v2_heldout)
    result = sim.run_screen(
        contract,
        targets,
        heldout,
        draws,
        seeds,
        accept_fraction,
        args.main_taxa,
        args.main_populations,
        args.replication_taxa,
        args.replication_populations,
    )
    apply_v3_1_gate(result, contract)
    sim.write_outputs(args.out_dir, result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
