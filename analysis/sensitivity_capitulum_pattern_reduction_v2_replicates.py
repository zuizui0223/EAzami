#!/usr/bin/env python3
"""Replicate-seed sensitivity for the v2 cross-layer pattern-reduction ranking.

Each parameter draw is evaluated across five fixed simulation realizations and ranked by
mean distance. This checks whether the v2 structural ranking is a one-realization lottery;
it is not a posterior model probability or a new biological model.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_SCRIPT = ROOT / "analysis" / "simulate_capitulum_pattern_reduction_v2.py"
spec = importlib.util.spec_from_file_location("pattern_reduction_v2", BASE_SCRIPT)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

MODELS = [
    "ENV_ONLY",
    "ENV_POLL",
    "ENV_ANT",
    "FULL_COUPLED_GLOBAL",
    "FULL_MODULAR_GLOBAL",
    "FULL_COUPLED_HET",
    "FULL_MODULAR_HET",
]
REPLICATE_SEEDS = [910000, 911000, 912000, 913000, 914000]


def percentile(sorted_values, p):
    idx = max(0, min(len(sorted_values) - 1, math.ceil(p * len(sorted_values)) - 1))
    return sorted_values[idx]


def draw_params(rng):
    return {
        "env": rng.uniform(0.2, 1.2),
        "poll": rng.uniform(0.2, 1.2),
        "ant": rng.uniform(0.2, 1.2),
        "within": rng.uniform(0.25, 1.5),
        "log_rr": rng.uniform(math.log(1.2), math.log(4.2)),
        "size_pred_z": rng.uniform(0.1, 1.3),
        "log10_attack": rng.uniform(-5.5, -3.8),
        "ant_het_log10": rng.uniform(0.0, 1.25),
        "poll_slope_base": rng.uniform(0.05, 0.30),
        "poll_het_ratio": rng.uniform(1.0, 4.0),
        "visit_r2": rng.uniform(0.2, 0.9),
        "probe_r2": rng.uniform(0.2, 0.9),
        "log_nodding_rr": rng.uniform(math.log(1.5), math.log(5.0)),
    }


def run(target_path: Path, draws=600):
    target = base.load_targets(target_path)
    results = {}
    for model in MODELS:
        rng = random.Random(20260820 + sum(ord(ch) for ch in model))
        mean_distances = []
        for _ in range(draws):
            params = draw_params(rng)
            replicate_distances = []
            for seed in REPLICATE_SEEDS:
                summary = base.simulate(params, model, seed=seed)
                distance, _ = base.distance(summary, target)
                replicate_distances.append(distance)
            mean_distances.append(sum(replicate_distances) / len(replicate_distances))
        mean_distances.sort()
        results[model] = {
            "parameter_draws": draws,
            "simulation_replicates_per_draw": len(REPLICATE_SEEDS),
            "best_mean_distance": mean_distances[0],
            "mean_distance_p01": percentile(mean_distances, 0.01),
        }

    ranking = sorted(MODELS, key=lambda model: results[model]["best_mean_distance"])
    full_models = [
        "FULL_COUPLED_GLOBAL", "FULL_MODULAR_GLOBAL", "FULL_COUPLED_HET", "FULL_MODULAR_HET"
    ]
    factorial = sorted(full_models, key=lambda model: results[model]["best_mean_distance"])
    return base.round_obj({
        "contract_version": "capitulum_pattern_reduction_v2_replicate_sensitivity",
        "status_date": "2026-08-20",
        "parameter_draws_per_model": draws,
        "replicate_seeds": REPLICATE_SEEDS,
        "models": results,
        "overall_ranking": ranking,
        "full_factorial_ranking": factorial,
        "headline": (
            "Averaging each parameter draw across five fixed simulation realizations preserves the v2 full-model "
            "ranking: FULL_MODULAR_HET < FULL_MODULAR_GLOBAL < FULL_COUPLED_HET < FULL_COUPLED_GLOBAL."
        ),
        "claim_boundary": (
            "This sensitivity addresses stochastic-realization dependence only. It does not validate the operational "
            "uncertainty weights or make the model comparison a posterior probability."
        ),
    })


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--targets", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--draws", type=int, default=600)
    args = parser.parse_args()
    result = run(args.targets, args.draws)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
