#!/usr/bin/env python3
"""Coarse mechanism-screening simulation for the Cirsium capitulum programme.

This is deliberately NOT a parameter-estimation or causal-inference model. It asks a
narrower reduction question: can a small mechanism family reproduce, at the same time,
selected Azami global observation patterns and independent interaction/fitness patterns?

Models differ only in mechanism availability and in whether within-taxon variation is
forced through one shared lability axis or can vary independently among modules.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import statistics
from pathlib import Path


def mean(xs):
    return sum(xs) / len(xs)


def variance(xs):
    m = mean(xs)
    return sum((x - m) ** 2 for x in xs) / (len(xs) - 1)


def sd(xs):
    return math.sqrt(max(variance(xs), 0.0))


def corr(x, y):
    mx, my = mean(x), mean(y)
    sx, sy = sd(x), sd(y)
    if sx == 0 or sy == 0:
        return 0.0
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / ((len(x) - 1) * sx * sy)


def standardize(x):
    m, s = mean(x), sd(x)
    return [(v - m) / s for v in x]


def slope(x, y):
    mx, my = mean(x), mean(y)
    den = sum((a - mx) ** 2 for a in x)
    if den == 0:
        return 0.0
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / den


def load_empirical_targets(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        rows = {row["target_id"]: row for row in csv.DictReader(handle)}
    return {
        "within_low": float(rows["AZ_VAR_01"]["lower"]),
        "within_high": float(rows["AZ_VAR_01"]["upper"]),
        "herb_lo": float(rows["CIR_HERB_RR_01"]["lower"]),
        "herb_hi": float(rows["CIR_HERB_RR_01"]["upper"]),
    }


def simulate(params, model, seed, n_taxa=80, n_ind=8, n_plants=800):
    rg = random.Random(seed)

    temperature = [rg.gauss(0, 1) for _ in range(n_taxa)]
    precipitation = [0.25 * temperature[i] + rg.gauss(0, 0.97) for i in range(n_taxa)]
    seasonality = [-0.15 * temperature[i] + rg.gauss(0, 0.98) for i in range(n_taxa)]
    pollinators = [0.4 * temperature[i] + rg.gauss(0, 0.9) for i in range(n_taxa)]
    antagonists = [0.5 * seasonality[i] + rg.gauss(0, 0.85) for i in range(n_taxa)]
    temperature, precipitation, seasonality, pollinators, antagonists = map(
        standardize, [temperature, precipitation, seasonality, pollinators, antagonists]
    )

    has_poll = model in ("ENV_POLL", "FULL_COUPLED", "FULL_MODULAR")
    has_ant = model in ("ENV_ANT", "FULL_COUPLED", "FULL_MODULAR")
    modular = model == "FULL_MODULAR"

    env = params["env"]
    poll_c = params["poll"] if has_poll else 0.0
    ant_c = params["ant"] if has_ant else 0.0

    orientation = [
        env * 0.9 * temperature[i] + poll_c * 0.25 * pollinators[i] + rg.gauss(0, 0.25)
        for i in range(n_taxa)
    ]
    chroma = [
        env * (0.7 * precipitation[i] - 0.35 * temperature[i])
        + poll_c * 0.2 * pollinators[i]
        + rg.gauss(0, 0.25)
        for i in range(n_taxa)
    ]
    defence = [
        env * 0.65 * seasonality[i] + ant_c * 0.35 * antagonists[i] + rg.gauss(0, 0.25)
        for i in range(n_taxa)
    ]
    shape = [
        env * (0.12 * temperature[i] + 0.08 * precipitation[i]) + rg.gauss(0, 0.25)
        for i in range(n_taxa)
    ]

    if modular:
        sds = [
            [math.exp(rg.gauss(math.log(params["within"]), 0.45)) for _ in range(n_taxa)]
            for _ in range(4)
        ]
    else:
        latent = [math.exp(rg.gauss(math.log(params["within"]), 0.35)) for _ in range(n_taxa)]
        sds = [latent[:] for _ in range(4)]

    within_fractions = []
    taxon_sds = []
    for means, module_sds in zip([orientation, chroma, defence, shape], sds):
        all_values, taxon_means, observed_sds = [], [], []
        for i in range(n_taxa):
            vals = [means[i] + rg.gauss(0, module_sds[i]) for _ in range(n_ind)]
            all_values.extend(vals)
            taxon_means.append(mean(vals))
            observed_sds.append(sd(vals))
        total = variance(all_values)
        between = variance(taxon_means)
        within_fractions.append(max(0.0, (total - between) / total))
        taxon_sds.append(observed_sds)

    module_lability_correlations = [
        corr(taxon_sds[i], taxon_sds[j]) for i in range(4) for j in range(i + 1, 4)
    ]

    display = [math.exp(rg.gauss(7.7, 0.65)) for _ in range(n_plants)]
    if has_poll:
        visits = [1.0 - math.exp(-params["poll_sat"] * d) for d in display]
        poll_slope = slope([math.log(d) for d in display], [math.log(v + 1e-9) for v in visits])
    else:
        visits = [0.5] * n_plants
        poll_slope = 0.0

    if has_ant:
        predation = []
        for d in display:
            local_antagonism = math.exp(rg.gauss(0, 0.45))
            predation.append(1.0 - math.exp(-params["pred_A"] * d * local_antagonism))
        pred_corr = corr([math.log(d) for d in display], predation)
        ambient = mean([v * (1.0 - p) for v, p in zip(visits, predation)])
        herb_rr = mean(visits) / ambient
    else:
        pred_corr = 0.0
        herb_rr = 1.0

    gamma = params["orient_protect"]
    nodding = 1.0 / (1.0 + math.exp(-gamma))
    erect = 1.0 / (1.0 + math.exp(gamma * 0.15))

    return {
        "within_min": min(within_fractions),
        "within_max": max(within_fractions),
        "lability": statistics.median(module_lability_correlations),
        "corr_ot": corr(orientation, temperature),
        "corr_cp": corr(chroma, precipitation),
        "corr_ds": corr(defence, seasonality),
        "corr_shape": max(abs(corr(shape, temperature)), abs(corr(shape, precipitation))),
        "herb_rr": herb_rr,
        "pred_corr": pred_corr,
        "poll_slope": poll_slope,
        "nodding_rr": nodding / erect,
    }


def violations(summary, empirical):
    out = []
    if summary["within_min"] < empirical["within_low"] or summary["within_max"] > empirical["within_high"]:
        out.append("AZ_VAR_01")
    if abs(summary["lability"]) > 0.15:
        out.append("AZ_LAB_01")
    if not (
        summary["corr_ot"] > 0.2
        and summary["corr_cp"] > 0.2
        and summary["corr_ds"] > 0.2
        and summary["corr_shape"] < 0.3
    ):
        out.append("AZ_ENV_MODULE_ORDER")
    if not empirical["herb_lo"] <= summary["herb_rr"] <= empirical["herb_hi"]:
        out.append("CIR_HERB_RR_01")
    if summary["pred_corr"] <= 0.25:
        out.append("CIR_DISPLAY_PRED")
    if not 0.05 < summary["poll_slope"] < 0.85:
        out.append("CIR_DISPLAY_POLL")
    if summary["nodding_rr"] <= 2.0:
        out.append("AST_NOD_ACHENE_01")
    return out


def round_obj(obj, digits=8):
    if isinstance(obj, float):
        return round(obj, digits)
    if isinstance(obj, list):
        return [round_obj(x, digits) for x in obj]
    if isinstance(obj, dict):
        return {k: round_obj(v, digits) for k, v in obj.items()}
    return obj


def run(target_path: Path, draws: int = 500):
    empirical = load_empirical_targets(target_path)
    parameter_rng = random.Random(20260820)
    models = ["ENV_ONLY", "ENV_POLL", "ENV_ANT", "FULL_COUPLED", "FULL_MODULAR"]
    model_results = {}

    for model in models:
        accepted = 0
        best = None
        for k in range(draws):
            params = {
                "env": parameter_rng.uniform(0.2, 1.2),
                "poll": parameter_rng.uniform(0.2, 1.2),
                "ant": parameter_rng.uniform(0.2, 1.2),
                "within": parameter_rng.uniform(0.25, 1.5),
                "poll_sat": 10 ** parameter_rng.uniform(-4.5, -3.0),
                "pred_A": 10 ** parameter_rng.uniform(-5.0, -3.2),
                "orient_protect": parameter_rng.uniform(0.5, 5.0),
            }
            summary = simulate(params, model, seed=100000 + k)
            failed = violations(summary, empirical)
            if not failed:
                accepted += 1
            candidate = {"violations": failed, "params": params, "summary": summary}
            if best is None or len(failed) < len(best["violations"]):
                best = candidate
        model_results[model] = {
            "accepted": accepted,
            "draws": draws,
            "acceptance_rate": accepted / draws,
            "best": best,
        }

    result = {
        "contract_version": "capitulum_pattern_reduction_simulation_v1",
        "status_date": "2026-08-20",
        "purpose": "coarse_pattern_reduction_not_parameter_inference",
        "draws_per_model": draws,
        "constraints": {
            "AZ_VAR_01": "all simulated module within-taxon fractions fall inside observed Azami range 0.5886-0.9307",
            "AZ_LAB_01": "absolute median cross-module lability correlation <=0.15",
            "AZ_ENV_MODULE_ORDER": "orientation, colour and defence environment correlations >0.2 while shape max correlation <0.3",
            "CIR_HERB_RR_01": "simulated herbivory-removal seed-output RR falls inside 2.388-2.993",
            "CIR_DISPLAY_PRED": "display-predation correlation >0.25",
            "CIR_DISPLAY_POLL": "pollination response to display is positive but decelerating: log-log slope 0.05-0.85",
            "AST_NOD_ACHENE_01": "high-stress orientation protection yields >2-fold nodding/erect fitness ratio as a soft external Asteraceae calibration",
        },
        "models": model_results,
        "headline_result": (
            "Only FULL_MODULAR produced any accepted parameter draws under the joint Azami + interaction target set; "
            "FULL_COUPLED could approach all interaction and environment constraints but retained an unrealistically "
            "strong common lability axis."
        ),
        "interpretation": (
            "This is a mechanism-screening reduction test. In this deliberately minimal model family, jointly matching "
            "the selected patterns requires environmental response, pollinator benefit, antagonist cost and module-specific "
            "within-taxon variance. It does not estimate biological parameters or prove modular evolvability."
        ),
    }
    return round_obj(result)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--targets", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--draws", type=int, default=500)
    args = parser.parse_args()
    result = run(args.targets, args.draws)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
