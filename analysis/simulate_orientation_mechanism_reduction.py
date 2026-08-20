#!/usr/bin/env python3
"""Reduced orientation-mechanism screen.

The model is deliberately small. It asks which functional pathways are needed to jointly
reproduce four otherwise awkward observations:
- Azami: orientation is environmentally structured;
- Cremanthodium: nodding strongly increases achene set without detected pollinator preference;
- Helianthus: orientation changes early-morning visitation/siring;
- Helianthus: the all-day landing effect can be weak/null.

This is a structural sufficiency screen, not a fitted model or claim that Cirsium uses the
same mechanisms as the comparison systems.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import statistics
from pathlib import Path

FAMILIES = [
    "static_pollinator_only",
    "abiotic_protection_only",
    "thermal_timing_only",
    "combined_static_pollinator_abiotic",
    "combined_time_abiotic",
]


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def logit(p: float) -> float:
    return math.log(p / (1.0 - p))


def mean(xs):
    return sum(xs) / len(xs)


def corr(x, y):
    mx, my = mean(x), mean(y)
    sx = math.sqrt(sum((v - mx) ** 2 for v in x))
    sy = math.sqrt(sum((v - my) ** 2 for v in y))
    if sx == 0 or sy == 0:
        return 0.0
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


def load_targets(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    by = {r["target_id"]: r for r in rows}
    required = {
        "OR_AZ_TEMP", "OR_CREM_ACHENE", "OR_CREM_POLL_NULL",
        "OR_HEL_EARLY", "OR_HEL_ALLDAY", "OR_HEL_SIRING", "OR_CREM_EXPOSURE",
    }
    missing = required - set(by)
    if missing:
        raise ValueError(f"missing orientation targets: {sorted(missing)}")
    return rows, by


def simulate_once(family: str, seed: int):
    rng = random.Random(seed)
    static_poll = family in {"static_pollinator_only", "combined_static_pollinator_abiotic"}
    abiotic = family in {"abiotic_protection_only", "combined_static_pollinator_abiotic", "combined_time_abiotic"}
    timing = family in {"thermal_timing_only", "combined_time_abiotic"}

    # Environment -> orientation is retained in every family because v2 already showed that
    # a full viable mechanism needs the environmental layer. Its sign is not hard-coded.
    env_beta = rng.uniform(-0.9, 0.9)
    temp = [rng.gauss(0, 1) for _ in range(120)]
    orient = [env_beta * t + rng.gauss(0, 0.85) for t in temp]
    orientation_temperature_r = corr(orient, temp)

    # Cremanthodium-style inclination comparison.
    base_visit = rng.uniform(0.30, 0.70)
    preference = rng.uniform(-1.5, 1.5) if static_poll else 0.0
    visit_nodding = sigmoid(logit(base_visit) + preference / 2.0)
    visit_erect = sigmoid(logit(base_visit) - preference / 2.0)
    pollinator_difference = visit_nodding - visit_erect

    nodding_viability = rng.uniform(0.72, 0.96)
    exposure_loss = rng.uniform(0.30, 0.82) if abiotic else 0.0
    erect_viability = nodding_viability * (1.0 - exposure_loss)
    protected_vs_exposed_viability_RR = nodding_viability / max(erect_viability, 1e-9)

    # Fitness depends on both viable pollen and visitation, but visitation has a non-zero floor
    # because the comparison system is not assumed to be completely pollinator limited.
    achene_nodding = nodding_viability * (0.35 + 0.65 * visit_nodding)
    achene_erect = erect_viability * (0.35 + 0.65 * visit_erect)
    nodding_vs_erect_achene_RR = achene_nodding / max(achene_erect, 1e-9)

    # Helianthus-style azimuth comparison. A static preference persists all day; a thermal
    # timing effect is large early but is compensated later, allowing an early effect plus
    # an all-day near-null.
    early_west = rng.uniform(0.18, 0.42)
    late_west = rng.uniform(0.45, 0.80)
    if timing:
        timing_strength = rng.uniform(0.12, 0.90)
        early_east = early_west * (1.0 + timing_strength)
        early_gain = early_east - early_west
        compensation = rng.uniform(0.78, 1.08)
        late_east = max(0.02, late_west - compensation * early_gain)
    elif static_poll:
        static_shift = rng.uniform(-1.2, 1.2)
        early_east = sigmoid(logit(min(0.95, early_west)) + static_shift)
        late_east = sigmoid(logit(min(0.95, late_west)) + static_shift)
    else:
        early_east = early_west
        late_east = late_west

    early_visit_RR = early_east / max(early_west, 1e-9)
    all_day_visit_RR = (early_east + late_east) / max(early_west + late_west, 1e-9)
    # Earlier pollen presentation is given extra male-fitness weight; this is a sign-level
    # analogue, not a fitted sunflower paternity model.
    siring_RR = 1.0 + 0.55 * max(0.0, early_visit_RR - 1.0)

    return {
        "orientation_temperature_r": orientation_temperature_r,
        "crem_pollinator_difference": pollinator_difference,
        "crem_protected_vs_exposed_viability_RR": protected_vs_exposed_viability_RR,
        "crem_nodding_vs_erect_achene_RR": nodding_vs_erect_achene_RR,
        "helianthus_early_visit_RR": early_visit_RR,
        "helianthus_all_day_visit_RR": all_day_visit_RR,
        "helianthus_siring_RR": siring_RR,
    }


def evaluate(summary, targets):
    ach_lo = float(targets["OR_CREM_ACHENE"]["lower_bound"])
    ach_hi = float(targets["OR_CREM_ACHENE"]["upper_bound"])
    poll_lo = float(targets["OR_CREM_POLL_NULL"]["lower_bound"])
    poll_hi = float(targets["OR_CREM_POLL_NULL"]["upper_bound"])
    early_lo = float(targets["OR_HEL_EARLY"]["lower_bound"])
    day_lo = float(targets["OR_HEL_ALLDAY"]["lower_bound"])
    day_hi = float(targets["OR_HEL_ALLDAY"]["upper_bound"])
    sir_lo = float(targets["OR_HEL_SIRING"]["lower_bound"])
    viability_lo = float(targets["OR_CREM_EXPOSURE"]["lower_bound"])

    core = {
        "azami_environment_orientation_positive": summary["orientation_temperature_r"] > 0,
        "crem_nodding_fitness_ratio": ach_lo <= summary["crem_nodding_vs_erect_achene_RR"] <= ach_hi,
        "crem_pollinator_preference_null": poll_lo <= summary["crem_pollinator_difference"] <= poll_hi,
        "helianthus_early_visit_positive": summary["helianthus_early_visit_RR"] >= early_lo,
        "helianthus_all_day_near_null": day_lo <= summary["helianthus_all_day_visit_RR"] <= day_hi,
    }
    heldout = {
        "helianthus_siring_positive": summary["helianthus_siring_RR"] >= sir_lo,
        "crem_exposure_reduces_pollen_viability": summary["crem_protected_vs_exposed_viability_RR"] >= viability_lo,
    }

    # Continuous distance to prevent ties among equally many binary matches.
    ach_mid = float(targets["OR_CREM_ACHENE"]["target_value"])
    day_mid = float(targets["OR_HEL_ALLDAY"]["target_value"])
    terms = [
        0.0 if summary["orientation_temperature_r"] > 0 else 1.0,
        min(2.0, abs(math.log(summary["crem_nodding_vs_erect_achene_RR"] / ach_mid)) / math.log(1.5)),
        min(2.0, abs(summary["crem_pollinator_difference"]) / 0.08),
        0.0 if summary["helianthus_early_visit_RR"] >= early_lo else min(2.0, (early_lo - summary["helianthus_early_visit_RR"]) / 0.20),
        min(2.0, abs(summary["helianthus_all_day_visit_RR"] - day_mid) / 0.10),
    ]
    return core, heldout, sum(core.values()), statistics.mean(terms)


def summarize_family(family, targets, draws, seed):
    runs = []
    for i in range(draws):
        summary = simulate_once(family, seed + i)
        core, held, nmatch, distance = evaluate(summary, targets)
        runs.append((nmatch, distance, summary, core, held))
    runs.sort(key=lambda x: (-x[0], x[1]))
    accepted = runs[:max(25, math.ceil(0.05 * len(runs)))]
    held_keys = sorted(accepted[0][4])
    held_rates = {k: sum(1 for r in accepted if r[4][k]) / len(accepted) for k in held_keys}
    return {
        "family": family,
        "draws": draws,
        "best_core_match": runs[0][0],
        "best_distance": round(runs[0][1], 6),
        "full_core_match_rate": round(sum(1 for r in runs if r[0] == 5) / len(runs), 6),
        "accepted_core_match_median": statistics.median(r[0] for r in accepted),
        "accepted_distance_median": round(statistics.median(r[1] for r in accepted), 6),
        "heldout_pass_rates": {k: round(v, 4) for k, v in held_rates.items()},
        "heldout_mean": round(statistics.mean(held_rates.values()), 4),
        "best_summary": {k: round(v, 6) for k, v in sorted(runs[0][2].items())},
    }


def run(target_path: Path, draws: int, seed: int):
    rows, targets = load_targets(target_path)
    families = [summarize_family(f, targets, draws, seed + j * 100000) for j, f in enumerate(FAMILIES)]
    ranking = sorted(
        families,
        key=lambda x: (-x["accepted_core_match_median"], x["accepted_distance_median"], -x["heldout_mean"], -x["full_core_match_rate"]),
    )
    return {
        "contract_version": "orientation_mechanism_reduction_v1",
        "status_date": "2026-08-20",
        "purpose": "minimal_pathway_sufficiency_for_orientation_scale_dependence",
        "target_rows": len(rows),
        "core_targets": 5,
        "heldout_targets": 2,
        "draws_per_family": draws,
        "seed": seed,
        "families": families,
        "ranking": [x["family"] for x in ranking],
        "best_family": ranking[0]["family"],
        "claim_boundary": (
            "The screen tests whether static pollinator preference, abiotic protection and/or time-window thermal timing are structurally sufficient for a cross-study orientation pattern. "
            "Cremanthodium nodding and Helianthus azimuth are not treated as homologous traits, and the model is not fitted to Cirsium fitness data."
        ),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--targets", type=Path, required=True)
    p.add_argument("--draws", type=int, default=1500)
    p.add_argument("--seed", type=int, default=20260820)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    result = run(args.targets, args.draws, args.seed)
    text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
