#!/usr/bin/env python3
"""Partial-calibrated two-state Mk sensitivity for Ryukyu Arenicola flower colour.

This analysis advances the Arenicola loss-versus-regain test beyond equal-cost
parsimony without pretending that the exact Chang et al. (2026) machine-readable
species tree has been recovered.

Source-backed median node ages used directly:

- Arenicola + Nipponocirsium split: 1.02 Mya;
- C. brevicaule + C. irumtiense MRCA: 0.93 Mya;
- C. morii versus the remaining sampled Nipponocirsium: 0.79 Mya.

Two younger Nipponocirsium node ages are not available as machine-readable
published values in the recovered material. They are therefore nuisance
parameters varied on a predeclared grid rather than fixed to invented values.

A single binary character cannot identify transition rates. Accordingly, this
script does *not* fit q(C->W) or q(W->C). It evaluates an explicit grid of total
transition rates and loss:regain rate ratios under both flat and stationary root
priors. For each scenario it exactly sums over all internal C/W assignments and
reports P(Arenicola MRCA=C | tip states, tree, rates, root prior).

The result is a conditional sensitivity surface, not a final posterior ancestral
state reconstruction. Its main purpose is to show which assumptions preserve,
erase, or reverse the one-step parsimony preference for a coloured Arenicola
ancestor.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from itertools import product
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import arenicola_colour_history_sensitivity as parsimony

C, W = "C", "W"
STATE_INDEX = {C: 0, W: 1}
DEFAULT_AGES = Path("data/evidence/arenicola_published_node_age_constraints_v1.csv")
DEFAULT_EVIDENCE = parsimony.DEFAULT_EVIDENCE
DEFAULT_OUTPUT = Path("analysis/arenicola_partial_calibrated_mk_sensitivity_v1.csv")
DEFAULT_SUMMARY = Path("analysis/arenicola_partial_calibrated_mk_sensitivity_v1.json")

TOPOLOGY_VARIANTS = (
    "published_pengii_basal",
    "alternative_kawakamii_basal",
    "alternative_tatakaense_basal",
)
DEFAULT_CORE_AGES = (0.15, 0.30, 0.45, 0.60)
DEFAULT_CROWN_FRACTIONS = (0.25, 0.50, 0.75)
DEFAULT_TOTAL_RATES = (0.10, 0.30, 1.00, 3.00)
DEFAULT_LOSS_REGAIN_RATIOS = (0.25, 0.50, 1.00, 2.00, 4.00)
DEFAULT_ROOT_PRIORS = ("flat", "equilibrium")

OUTPUT_FIELDS = (
    "topology_variant",
    "nipp_core_age_mya",
    "nipp_crown_fraction",
    "nipp_crown_age_mya",
    "total_rate_per_myr",
    "loss_to_regain_rate_ratio",
    "q_C_to_W_per_myr",
    "q_W_to_C_per_myr",
    "root_prior",
    "tip_data_likelihood",
    "p_arenicola_mrca_C",
    "p_arenicola_mrca_W",
    "log_odds_C_over_W",
    "preferred_arenicola_state",
)


def clean(value: object) -> str:
    return str(value or "").strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [
            {key: clean(value) for key, value in row.items()}
            for row in csv.DictReader(handle)
            if any(clean(value) for value in row.values())
        ]


def load_published_median_ages(path: Path) -> dict[str, float]:
    rows = read_csv(path)
    wanted = {"AREN_NIPP_ROOT", "AREN_MRCA", "NIPP_MRCA"}
    output: dict[str, float] = {}
    for row in rows:
        node = row.get("node", "")
        if node not in wanted:
            continue
        if row.get("use_status") != "median_primary":
            raise ValueError(f"{node}: expected use_status=median_primary")
        try:
            output[node] = float(row["median_age_mya"])
        except Exception as exc:
            raise ValueError(f"{node}: invalid median_age_mya") from exc
    if set(output) != wanted:
        raise ValueError(f"Missing published age constraints: {sorted(wanted - set(output))}")
    if not (output["AREN_NIPP_ROOT"] > output["AREN_MRCA"] > 0):
        raise ValueError("Published root/Arenicola medians are not time ordered")
    if not (output["AREN_NIPP_ROOT"] > output["NIPP_MRCA"] > 0):
        raise ValueError("Published root/Nipponocirsium medians are not time ordered")
    return output


def parse_float_list(text: str) -> tuple[float, ...]:
    values = tuple(float(item.strip()) for item in text.split(",") if item.strip())
    if not values or any(value <= 0 for value in values):
        raise ValueError("Grid values must be positive")
    return values


def topology_children(variant: str) -> dict[str, tuple[str, str]]:
    if variant == "published_pengii_basal":
        core = {
            "NIPP_CORE": ("pengii", "NIPP_CROWN"),
            "NIPP_CROWN": ("kawakamii", "tatakaense"),
        }
    elif variant == "alternative_kawakamii_basal":
        core = {
            "NIPP_CORE": ("kawakamii", "NIPP_CROWN"),
            "NIPP_CROWN": ("pengii", "tatakaense"),
        }
    elif variant == "alternative_tatakaense_basal":
        core = {
            "NIPP_CORE": ("tatakaense", "NIPP_CROWN"),
            "NIPP_CROWN": ("pengii", "kawakamii"),
        }
    else:
        raise ValueError(f"Unsupported topology variant: {variant}")
    return {
        "ROOT": ("AREN_MRCA", "NIPP_MRCA"),
        "AREN_MRCA": ("brevicaule", "irumtiense"),
        "NIPP_MRCA": ("morii", "NIPP_CORE"),
        **core,
    }


def branch_table(
    variant: str,
    published_ages: Mapping[str, float],
    *,
    core_age: float,
    crown_fraction: float,
) -> list[tuple[str, str, float]]:
    if not 0 < crown_fraction < 1:
        raise ValueError("nipp_crown_fraction must be between 0 and 1")
    if not 0 < core_age < published_ages["NIPP_MRCA"]:
        raise ValueError("NIPP_CORE age must lie between 0 and published NIPP_MRCA age")
    crown_age = core_age * crown_fraction
    ages = {
        "ROOT": published_ages["AREN_NIPP_ROOT"],
        "AREN_MRCA": published_ages["AREN_MRCA"],
        "NIPP_MRCA": published_ages["NIPP_MRCA"],
        "NIPP_CORE": core_age,
        "NIPP_CROWN": crown_age,
        "brevicaule": 0.0,
        "irumtiense": 0.0,
        "morii": 0.0,
        "pengii": 0.0,
        "kawakamii": 0.0,
        "tatakaense": 0.0,
    }
    output: list[tuple[str, str, float]] = []
    for parent, children in topology_children(variant).items():
        for child in children:
            length = ages[parent] - ages[child]
            if length <= 0:
                raise ValueError(f"Non-positive branch length {parent}->{child}: {length}")
            output.append((parent, child, length))
    return output


def transition_matrix(q_cw: float, q_wc: float, t: float) -> tuple[tuple[float, float], tuple[float, float]]:
    if min(q_cw, q_wc, t) <= 0:
        raise ValueError("Rates and branch lengths must be positive")
    total = q_cw + q_wc
    decay = math.exp(-total * t)
    pi_c = q_wc / total
    pi_w = q_cw / total
    return (
        (pi_c + pi_w * decay, pi_w * (1.0 - decay)),
        (pi_c * (1.0 - decay), pi_w + pi_c * decay),
    )


def root_prior(q_cw: float, q_wc: float, mode: str) -> tuple[float, float]:
    if mode == "flat":
        return (0.5, 0.5)
    if mode == "equilibrium":
        total = q_cw + q_wc
        return (q_wc / total, q_cw / total)
    raise ValueError(f"Unsupported root prior: {mode}")


def exact_internal_posterior(
    branch_rows: Sequence[tuple[str, str, float]],
    tip_states: Mapping[str, str],
    *,
    q_cw: float,
    q_wc: float,
    root_prior_mode: str,
) -> dict[str, float]:
    internals = ("ROOT", "AREN_MRCA", "NIPP_MRCA", "NIPP_CORE", "NIPP_CROWN")
    prior = root_prior(q_cw, q_wc, root_prior_mode)
    weighted = {C: 0.0, W: 0.0}
    likelihood = 0.0

    for values in product((C, W), repeat=len(internals)):
        assignment = dict(zip(internals, values))
        assignment.update(tip_states)
        probability = prior[STATE_INDEX[assignment["ROOT"]]]
        for parent, child, length in branch_rows:
            matrix = transition_matrix(q_cw, q_wc, length)
            probability *= matrix[STATE_INDEX[assignment[parent]]][STATE_INDEX[assignment[child]]]
        weighted[assignment["AREN_MRCA"]] += probability
        likelihood += probability

    if not likelihood > 0:
        raise RuntimeError("Tip-data likelihood underflowed to zero")
    p_c = weighted[C] / likelihood
    p_w = weighted[W] / likelihood
    if abs((p_c + p_w) - 1.0) > 1e-10:
        raise RuntimeError("Internal-state posterior failed to normalize")
    return {"likelihood": likelihood, "p_C": p_c, "p_W": p_w}


def rates_from_total_ratio(total_rate: float, loss_regain_ratio: float) -> tuple[float, float]:
    if total_rate <= 0 or loss_regain_ratio <= 0:
        raise ValueError("Rate grid values must be positive")
    q_wc = total_rate / (1.0 + loss_regain_ratio)
    q_cw = loss_regain_ratio * q_wc
    return q_cw, q_wc


def scenario_rows(
    tip_states: Mapping[str, str],
    published_ages: Mapping[str, float],
    *,
    core_ages: Sequence[float],
    crown_fractions: Sequence[float],
    total_rates: Sequence[float],
    loss_regain_ratios: Sequence[float],
    root_priors: Sequence[str],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for variant in TOPOLOGY_VARIANTS:
        for core_age in core_ages:
            for crown_fraction in crown_fractions:
                branches = branch_table(
                    variant,
                    published_ages,
                    core_age=core_age,
                    crown_fraction=crown_fraction,
                )
                crown_age = core_age * crown_fraction
                for total_rate in total_rates:
                    for ratio in loss_regain_ratios:
                        q_cw, q_wc = rates_from_total_ratio(total_rate, ratio)
                        for prior_mode in root_priors:
                            posterior = exact_internal_posterior(
                                branches,
                                tip_states,
                                q_cw=q_cw,
                                q_wc=q_wc,
                                root_prior_mode=prior_mode,
                            )
                            p_c = posterior["p_C"]
                            p_w = posterior["p_W"]
                            log_odds = math.log(max(p_c, 1e-300) / max(p_w, 1e-300))
                            if p_c > 0.5000000001:
                                preferred = C
                            elif p_w > 0.5000000001:
                                preferred = W
                            else:
                                preferred = "tie"
                            rows.append(
                                {
                                    "topology_variant": variant,
                                    "nipp_core_age_mya": f"{core_age:.6f}",
                                    "nipp_crown_fraction": f"{crown_fraction:.6f}",
                                    "nipp_crown_age_mya": f"{crown_age:.6f}",
                                    "total_rate_per_myr": f"{total_rate:.6f}",
                                    "loss_to_regain_rate_ratio": f"{ratio:.6f}",
                                    "q_C_to_W_per_myr": f"{q_cw:.9f}",
                                    "q_W_to_C_per_myr": f"{q_wc:.9f}",
                                    "root_prior": prior_mode,
                                    "tip_data_likelihood": f"{posterior['likelihood']:.12g}",
                                    "p_arenicola_mrca_C": f"{p_c:.12f}",
                                    "p_arenicola_mrca_W": f"{p_w:.12f}",
                                    "log_odds_C_over_W": f"{log_odds:.12f}",
                                    "preferred_arenicola_state": preferred,
                                }
                            )
    return rows


def write_csv(path: Path, rows: Iterable[Mapping[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(OUTPUT_FIELDS), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows: Sequence[Mapping[str, object]], published_ages: Mapping[str, float]) -> dict[str, object]:
    numeric = []
    for row in rows:
        numeric.append(
            {
                **row,
                "total": float(row["total_rate_per_myr"]),
                "ratio": float(row["loss_to_regain_rate_ratio"]),
                "p_c": float(row["p_arenicola_mrca_C"]),
            }
        )

    by_symmetric_rate: dict[str, dict[str, object]] = {}
    for total in DEFAULT_TOTAL_RATES:
        subset = [row for row in numeric if math.isclose(row["ratio"], 1.0) and math.isclose(row["total"], total)]
        if not subset:
            continue
        values = [row["p_c"] for row in subset]
        by_symmetric_rate[f"{total:g}"] = {
            "n_scenarios": len(values),
            "min_p_arenicola_C": min(values),
            "max_p_arenicola_C": max(values),
            "all_prefer_C": all(value > 0.5 for value in values),
        }

    all_values = [row["p_c"] for row in numeric]
    reversed_rows = [row for row in numeric if row["p_c"] < 0.5]
    near_tie = [row for row in numeric if 0.45 <= row["p_c"] <= 0.55]

    strongest_c = max(numeric, key=lambda row: row["p_c"])
    strongest_w = min(numeric, key=lambda row: row["p_c"])

    return {
        "analysis_version": "arenicola_partial_calibrated_mk_sensitivity_v1",
        "published_median_node_ages_mya": dict(published_ages),
        "grid": {
            "topology_variants": list(TOPOLOGY_VARIANTS),
            "nipp_core_age_mya": list(DEFAULT_CORE_AGES),
            "nipp_crown_fraction_of_core_age": list(DEFAULT_CROWN_FRACTIONS),
            "total_transition_rate_per_myr": list(DEFAULT_TOTAL_RATES),
            "q_C_to_W_over_q_W_to_C": list(DEFAULT_LOSS_REGAIN_RATIOS),
            "root_priors": list(DEFAULT_ROOT_PRIORS),
        },
        "scenario_count": len(numeric),
        "symmetric_rate_summary": by_symmetric_rate,
        "all_grid_summary": {
            "min_p_arenicola_C": min(all_values),
            "max_p_arenicola_C": max(all_values),
            "n_prefer_C": sum(value > 0.5 for value in all_values),
            "n_prefer_W": sum(value < 0.5 for value in all_values),
            "n_near_tie_0_45_to_0_55": len(near_tie),
            "direction_reversal_exists": bool(reversed_rows),
        },
        "strongest_C_scenario": {
            key: strongest_c[key]
            for key in (
                "topology_variant", "nipp_core_age_mya", "nipp_crown_fraction",
                "total_rate_per_myr", "loss_to_regain_rate_ratio", "root_prior",
                "p_arenicola_mrca_C",
            )
        },
        "strongest_W_scenario": {
            key: strongest_w[key]
            for key in (
                "topology_variant", "nipp_core_age_mya", "nipp_crown_fraction",
                "total_rate_per_myr", "loss_to_regain_rate_ratio", "root_prior",
                "p_arenicola_mrca_C",
            )
        },
        "working_inference": (
            "The one-step parsimony preference for a coloured Arenicola ancestor is the "
            "low-transition-rate limit of a broader Mk sensitivity surface. Under symmetric "
            "low-to-moderate transition rates the partial published calibration consistently "
            "favours Arenicola MRCA=C, but the signal approaches a tie as transitions become "
            "fast. Across asymmetric loss/regain rates and alternative root priors, scenarios "
            "exist that favour Arenicola MRCA=W. Therefore the direction cannot be promoted "
            "to a rate-model posterior conclusion until flower-colour transition rates are "
            "estimated from a broader East Asian/global Cirsium character dataset or exact "
            "published posterior trees and a justified rate prior become available."
        ),
        "claim_limit": (
            "This is not the published Chang et al. posterior. Three node medians are sourced "
            "from the paper, two younger Nipponocirsium ages are nuisance grids, and transition "
            "rates/root priors are explicit sensitivity assumptions. A single binary character "
            "cannot identify q(C->W) and q(W->C). Do not report p_arenicola_mrca_C from any one "
            "grid row as an empirical posterior probability."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--age-constraints", type=Path, default=DEFAULT_AGES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--core-ages", default=",".join(str(x) for x in DEFAULT_CORE_AGES))
    parser.add_argument("--crown-fractions", default=",".join(str(x) for x in DEFAULT_CROWN_FRACTIONS))
    parser.add_argument("--total-rates", default=",".join(str(x) for x in DEFAULT_TOTAL_RATES))
    parser.add_argument("--loss-regain-ratios", default=",".join(str(x) for x in DEFAULT_LOSS_REGAIN_RATIOS))
    parser.add_argument("--root-priors", default=",".join(DEFAULT_ROOT_PRIORS))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    tip_states = parsimony.load_tip_states(args.evidence)
    ages = load_published_median_ages(args.age_constraints)
    core_ages = parse_float_list(args.core_ages)
    crown_fractions = parse_float_list(args.crown_fractions)
    total_rates = parse_float_list(args.total_rates)
    ratios = parse_float_list(args.loss_regain_ratios)
    root_priors = tuple(item.strip() for item in args.root_priors.split(",") if item.strip())
    if not root_priors or any(item not in DEFAULT_ROOT_PRIORS for item in root_priors):
        raise SystemExit("--root-priors must contain only flat,equilibrium")

    rows = scenario_rows(
        tip_states,
        ages,
        core_ages=core_ages,
        crown_fractions=crown_fractions,
        total_rates=total_rates,
        loss_regain_ratios=ratios,
        root_priors=root_priors,
    )
    write_csv(args.output, rows)
    summary = summarize(rows, ages)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"scenario_count={summary['scenario_count']}")
    for rate, result in summary["symmetric_rate_summary"].items():
        print(
            "symmetric_total_rate=" + rate
            + f" pC_range={result['min_p_arenicola_C']:.6f}-{result['max_p_arenicola_C']:.6f}"
            + f" all_prefer_C={str(result['all_prefer_C']).lower()}"
        )
    print(f"direction_reversal_exists={str(summary['all_grid_summary']['direction_reversal_exists']).lower()}")
    print("working_inference=" + summary["working_inference"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
