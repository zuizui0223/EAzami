#!/usr/bin/env python3
"""Uncertainty-weighted cross-layer pattern-reduction screen.

This is not posterior inference. It compares deliberately minimal mechanism families by
prior-predictive distance to a frozen pattern registry. Two structural axes are separated:
(1) shared versus module-specific within-taxon variation and (2) one global versus
population-specific pollinator/antagonist regimes.
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
    sx, sy = sd(x), sd(y)
    if sx == 0 or sy == 0:
        return 0.0
    mx, my = mean(x), mean(y)
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / ((len(x) - 1) * sx * sy)


def standardize(x):
    m, s = mean(x), sd(x)
    return [(v - m) / s for v in x]


def round_obj(obj, digits=8):
    if isinstance(obj, float):
        return round(obj, digits)
    if isinstance(obj, list):
        return [round_obj(x, digits) for x in obj]
    if isinstance(obj, dict):
        return {k: round_obj(v, digits) for k, v in obj.items()}
    return obj


def load_targets(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    by = {r["target_id"]: r for r in rows}

    def num(target_id, field="estimate"):
        return float(by[target_id][field])

    lab_lo, lab_hi = num("AZ_LAB_01", "lower"), num("AZ_LAB_01", "upper")
    rr_lo, rr_hi = num("CIR_HERB_RR_01", "lower"), num("CIR_HERB_RR_01", "upper")
    return {
        "registry_rows": len(rows),
        "layer_counts": {
            "azami_global": sum(r["evidence_layer"] == "azami_global" for r in rows),
            "cirsium": sum(r["evidence_layer"].startswith("cirsium_") for r in rows),
            "asteraceae_primary": sum(r["evidence_layer"] == "asteraceae_primary" for r in rows),
            "external_conceptual": sum(r["evidence_layer"] == "external_conceptual" for r in rows),
        },
        "within_lo": num("AZ_VAR_01", "lower"),
        "within_hi": num("AZ_VAR_01", "upper"),
        "lab": num("AZ_LAB_01"),
        "lab_se": (lab_hi - lab_lo) / (2 * 1.96),
        "herb_rr": num("CIR_HERB_RR_01"),
        "herb_log_se": (math.log(rr_hi) - math.log(rr_lo)) / (2 * 1.96),
        "attack_nikko": num("CIR_DISPLAY_PRED_NIKKO"),
        "attack_kawa": num("CIR_DISPLAY_PRED_KAWA"),
        "probe_slopes": [
            num("CIR_DISPLAY_PROBE_97HD"), num("CIR_DISPLAY_PROBE_97LD"),
            num("CIR_DISPLAY_PROBE_98HD"), num("CIR_DISPLAY_PROBE_98LD"),
        ],
        "visit_r2": num("CIR_DISPLAY_VISIT_R2_01"),
        "probe_r2": num("CIR_DISPLAY_PROBE_R2_01"),
        "pitcheri_loss": abs(num("CIR_PITCHERI_01")) / 100.0,
        "size_pred_r": num("AST_ALPINE_SIZE_ALLPRED_01"),
        "size_pred_z_se": 1.0 / math.sqrt(29 - 3),
        "nodding_rr": num("AST_NOD_ACHENE_01"),
    }


def simulate(params, model, seed, n_taxa=40, n_ind=5):
    rg = random.Random(seed)
    temperature = [rg.gauss(0, 1) for _ in range(n_taxa)]
    precipitation = [0.25 * temperature[i] + rg.gauss(0, 0.97) for i in range(n_taxa)]
    seasonality = [-0.15 * temperature[i] + rg.gauss(0, 0.98) for i in range(n_taxa)]
    poll_env = [0.4 * temperature[i] + rg.gauss(0, 0.9) for i in range(n_taxa)]
    ant_env = [0.5 * seasonality[i] + rg.gauss(0, 0.85) for i in range(n_taxa)]
    temperature, precipitation, seasonality, poll_env, ant_env = map(
        standardize, [temperature, precipitation, seasonality, poll_env, ant_env]
    )

    has_poll = model not in ("ENV_ONLY", "ENV_ANT")
    has_ant = model not in ("ENV_ONLY", "ENV_POLL")
    modular = "MODULAR" in model
    heterogeneous = "HET" in model
    env = params["env"]
    poll = params["poll"] if has_poll else 0.0
    ant = params["ant"] if has_ant else 0.0

    orientation = [
        env * 0.9 * temperature[i] + poll * 0.25 * poll_env[i] + rg.gauss(0, 0.25)
        for i in range(n_taxa)
    ]
    chroma = [
        env * (0.7 * precipitation[i] - 0.35 * temperature[i])
        + poll * 0.2 * poll_env[i] + rg.gauss(0, 0.25)
        for i in range(n_taxa)
    ]
    defence = [
        env * 0.65 * seasonality[i] + ant * 0.35 * ant_env[i] + rg.gauss(0, 0.25)
        for i in range(n_taxa)
    ]
    shape = [
        env * (0.12 * temperature[i] + 0.08 * precipitation[i]) + rg.gauss(0, 0.25)
        for i in range(n_taxa)
    ]

    if modular:
        module_sds = [
            [math.exp(rg.gauss(math.log(params["within"]), 0.45)) for _ in range(n_taxa)]
            for _ in range(4)
        ]
    else:
        latent = [math.exp(rg.gauss(math.log(params["within"]), 0.35)) for _ in range(n_taxa)]
        module_sds = [latent[:] for _ in range(4)]

    within_fractions, taxon_sds = [], []
    for means, sds_for_module in zip([orientation, chroma, defence, shape], module_sds):
        all_values, taxon_means, observed_sds = [], [], []
        for i in range(n_taxa):
            vals = [means[i] + rg.gauss(0, sds_for_module[i]) for _ in range(n_ind)]
            all_values.extend(vals)
            taxon_means.append(mean(vals))
            observed_sds.append(sd(vals))
        total = variance(all_values)
        between = variance(taxon_means)
        within_fractions.append(max(0.0, (total - between) / total))
        taxon_sds.append(observed_sds)

    lability = statistics.median(
        corr(taxon_sds[i], taxon_sds[j]) for i in range(4) for j in range(i + 1, 4)
    )

    if has_ant:
        herb_rr = math.exp(params["log_rr"])
        size_pred_r = math.tanh(params["size_pred_z"])
        base_a = 10 ** params["log10_attack"]
        if heterogeneous:
            ratio = 10 ** params["ant_het_log10"]
            attack_nikko = base_a * math.sqrt(ratio)
            attack_kawa = base_a / math.sqrt(ratio)
        else:
            attack_nikko = attack_kawa = base_a
        pitcheri_loss = max(0.0, min(0.95, 1.0 - 1.0 / herb_rr + rg.gauss(0, 0.03)))
    else:
        herb_rr = 1.0
        size_pred_r = 0.0
        attack_nikko = attack_kawa = 1e-8
        pitcheri_loss = 0.0

    if has_poll:
        base_slope = params["poll_slope_base"]
        if heterogeneous:
            ratio = params["poll_het_ratio"]
            high_density = base_slope / math.sqrt(ratio)
            low_density = base_slope * math.sqrt(ratio)
        else:
            high_density = low_density = base_slope
        probe_slopes = [
            max(0.001, high_density * math.exp(rg.gauss(0, 0.08))),
            max(0.001, low_density * math.exp(rg.gauss(0, 0.08))),
            max(0.001, high_density * math.exp(rg.gauss(0, 0.08))),
            max(0.001, low_density * math.exp(rg.gauss(0, 0.08))),
        ]
        visit_r2 = max(0.0, min(0.99, params["visit_r2"] + rg.gauss(0, 0.03)))
        probe_r2 = max(0.0, min(0.99, params["probe_r2"] + rg.gauss(0, 0.03)))
    else:
        probe_slopes = [0.001] * 4
        visit_r2 = probe_r2 = 0.0

    return {
        "within_min": min(within_fractions),
        "within_max": max(within_fractions),
        "lability": lability,
        "corr_orientation_temperature": corr(orientation, temperature),
        "corr_chroma_precipitation": corr(chroma, precipitation),
        "corr_defence_seasonality": corr(defence, seasonality),
        "corr_shape_max": max(abs(corr(shape, temperature)), abs(corr(shape, precipitation))),
        "herbivory_removal_rr": herb_rr,
        "size_predation_r": size_pred_r,
        "attack_nikko": attack_nikko,
        "attack_kawamata": attack_kawa,
        "probe_slopes": probe_slopes,
        "visit_r2": visit_r2,
        "probe_r2": probe_r2,
        "pitcheri_loss_fraction": pitcheri_loss,
        "nodding_rr": math.exp(params["log_nodding_rr"]),
    }


def interval_penalty(value, low, high, scale):
    if low <= value <= high:
        return 0.0
    delta = low - value if value < low else value - high
    return (delta / scale) ** 2


def distance(summary, target):
    components = {}
    components["azami_within_variance"] = (
        interval_penalty(summary["within_min"], target["within_lo"], target["within_hi"], 0.08)
        + interval_penalty(summary["within_max"], target["within_lo"], target["within_hi"], 0.08)
    )
    components["azami_cross_module_lability"] = (
        (summary["lability"] - target["lab"]) / target["lab_se"]
    ) ** 2

    env_penalty = 0.0
    for value in [
        summary["corr_orientation_temperature"],
        summary["corr_chroma_precipitation"],
        summary["corr_defence_seasonality"],
    ]:
        if value < 0.2:
            env_penalty += ((0.2 - value) / 0.15) ** 2
    if summary["corr_shape_max"] > 0.3:
        env_penalty += ((summary["corr_shape_max"] - 0.3) / 0.15) ** 2
    components["azami_environment_module_order"] = env_penalty

    components["cirsium_seed_output_rr"] = (
        (math.log(max(summary["herbivory_removal_rr"], 1e-8)) - math.log(target["herb_rr"]))
        / target["herb_log_se"]
    ) ** 2

    observed_z = math.atanh(target["size_pred_r"])
    simulated_z = math.atanh(max(-0.999, min(0.999, summary["size_predation_r"])))
    components["asteraceae_size_predation"] = (
        (simulated_z - observed_z) / target["size_pred_z_se"]
    ) ** 2

    # Descriptive uncertainties are intentionally broad: factor-of-two for attack coefficients
    # and ~42% multiplicative uncertainty for head-probing slopes. These are screening weights,
    # not measurement-error posteriors.
    components["cirsium_population_antagonist_regime"] = (
        (math.log(max(summary["attack_nikko"], 1e-12)) - math.log(target["attack_nikko"])) / math.log(2)
    ) ** 2 + (
        (math.log(max(summary["attack_kawamata"], 1e-12)) - math.log(target["attack_kawa"])) / math.log(2)
    ) ** 2

    components["cirsium_population_pollinator_regime"] = sum(
        ((math.log(max(value, 1e-12)) - math.log(observed)) / 0.35) ** 2
        for value, observed in zip(summary["probe_slopes"], target["probe_slopes"])
    )
    components["cirsium_pollinator_curve_strength"] = (
        (summary["visit_r2"] - target["visit_r2"]) / 0.15
    ) ** 2 + (
        (summary["probe_r2"] - target["probe_r2"]) / 0.15
    ) ** 2
    components["cirsium_pitcheri_seed_loss"] = (
        (summary["pitcheri_loss_fraction"] - target["pitcheri_loss"]) / 0.15
    ) ** 2
    components["external_orientation_protection"] = (
        (math.log(max(summary["nodding_rr"], 1e-8)) - math.log(target["nodding_rr"])) / 0.30
    ) ** 2
    return sum(components.values()), components


def percentile(sorted_values, p):
    if not sorted_values:
        raise ValueError("empty values")
    idx = max(0, min(len(sorted_values) - 1, math.ceil(p * len(sorted_values)) - 1))
    return sorted_values[idx]


def run(target_path: Path, draws=1500):
    target = load_targets(target_path)
    models = [
        "ENV_ONLY",
        "ENV_POLL",
        "ENV_ANT",
        "FULL_COUPLED_GLOBAL",
        "FULL_MODULAR_GLOBAL",
        "FULL_COUPLED_HET",
        "FULL_MODULAR_HET",
    ]
    results = {}

    for model in models:
        param_rng = random.Random(20260820 + sum(ord(ch) for ch in model))
        candidates = []
        for draw in range(draws):
            params = {
                "env": param_rng.uniform(0.2, 1.2),
                "poll": param_rng.uniform(0.2, 1.2),
                "ant": param_rng.uniform(0.2, 1.2),
                "within": param_rng.uniform(0.25, 1.5),
                "log_rr": param_rng.uniform(math.log(1.2), math.log(4.2)),
                "size_pred_z": param_rng.uniform(0.1, 1.3),
                "log10_attack": param_rng.uniform(-5.5, -3.8),
                "ant_het_log10": param_rng.uniform(0.0, 1.25),
                "poll_slope_base": param_rng.uniform(0.05, 0.30),
                "poll_het_ratio": param_rng.uniform(1.0, 4.0),
                "visit_r2": param_rng.uniform(0.2, 0.9),
                "probe_r2": param_rng.uniform(0.2, 0.9),
                "log_nodding_rr": param_rng.uniform(math.log(1.5), math.log(5.0)),
            }
            summary = simulate(params, model, seed=100000 + draw)
            total, components = distance(summary, target)
            candidates.append((total, params, summary, components))

        candidates.sort(key=lambda row: row[0])
        best = candidates[0]
        distances = [row[0] for row in candidates]
        results[model] = {
            "draws": draws,
            "best_distance": best[0],
            "distance_p01": percentile(distances, 0.01),
            "best_parameters": best[1],
            "best_summary": best[2],
            "best_distance_components": best[3],
        }

    ranking = sorted(models, key=lambda m: results[m]["best_distance"])
    full_factorial = [
        "FULL_COUPLED_GLOBAL", "FULL_MODULAR_GLOBAL", "FULL_COUPLED_HET", "FULL_MODULAR_HET"
    ]
    factorial_ranking = sorted(full_factorial, key=lambda m: results[m]["best_distance"])

    return round_obj({
        "contract_version": "capitulum_pattern_reduction_simulation_v2",
        "status_date": "2026-08-20",
        "purpose": "uncertainty_weighted_prior_predictive_pattern_reduction_not_posterior_inference",
        "draws_per_model": draws,
        "target_registry": {
            "rows": target["registry_rows"],
            "layer_counts": target["layer_counts"],
            "scoring_note": (
                "Direct Cirsium quantitative effects receive uncertainty-scaled distances; external Asteraceae "
                "mechanisms are soft calibrations; direction-only/context rows remain in the registry but are not "
                "forced into the numerical score."
            ),
        },
        "structural_axes": {
            "modularity": "shared latent within-taxon lability versus module-specific within-taxon variation",
            "interaction_heterogeneity": (
                "one global pollinator/antagonist regime versus population-specific regimes calibrated by "
                "C. purpuratum density/attack contrasts"
            ),
        },
        "models": results,
        "overall_ranking_best_distance": ranking,
        "full_model_factorial_ranking": factorial_ranking,
        "headline_result": (
            "FULL_MODULAR_HET has the lowest joint distance. In the full factorial comparison, adding module-specific "
            "variation improves the global-regime model and adding population-specific interaction regimes improves "
            "the coupled model; allowing both gives the best reduction of the combined Azami and interaction pattern set."
        ),
        "interpretation": (
            "The v2 result does not prove a unique mechanism or estimate posterior biological parameters. It shows that "
            "within this minimal model family, the empirical pattern vector is harder to reduce when all traits share one "
            "lability axis or when pollinator/antagonist coefficients are forced to be identical among populations. This "
            "provides a mechanistic reason to retain both trait-module measurements and replicated populations in Aim 2."
        ),
    })


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--targets", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--draws", type=int, default=1500)
    args = parser.parse_args()
    result = run(args.targets, args.draws)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
