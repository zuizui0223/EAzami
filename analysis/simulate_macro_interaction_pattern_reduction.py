#!/usr/bin/env python3
"""Prior-predictive pattern-reduction simulation for the Azami -> EAzami bridge.

This is intentionally a *structural sufficiency* test, not a fitted evolutionary model.
Five mechanism families are given broad symmetric parameter priors. We ask whether they
can jointly reproduce a compact target set drawn from:

1) global Azami observational trait/environment patterns; and
2) quantitative/qualitative plant-interaction literature targets.

The simulation never changes the frozen Azami observations. It lives in EAzami because
its purpose is mechanistic reduction: can a small set of ecological processes generate the
observed pattern bundle without per-target hand tuning?
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
    "environment_only",
    "pollinator_only",
    "antagonist_only",
    "full_tradeoff_common_lability",
    "full_tradeoff_modular_evolvability",
]
MODULES = ["orientation", "colour", "display_shape", "involucre_defence"]


def mean(xs):
    return sum(xs) / len(xs)


def variance(xs):
    if len(xs) < 2:
        return 0.0
    m = mean(xs)
    return sum((x - m) ** 2 for x in xs) / (len(xs) - 1)


def stdev(xs):
    return math.sqrt(max(0.0, variance(xs)))


def corr(x, y):
    mx, my = mean(x), mean(y)
    sx, sy = stdev(x), stdev(y)
    if sx == 0 or sy == 0:
        return 0.0
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / ((len(x) - 1) * sx * sy)


def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    out = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i + 1
        while j < len(order) and xs[order[j]] == xs[order[i]]:
            j += 1
        r = (i + j - 1) / 2.0 + 1.0
        for k in range(i, j):
            out[order[k]] = r
        i = j
    return out


def spearman(x, y):
    return corr(ranks(x), ranks(y))


def sigmoid(x):
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def load_targets(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    by_id = {r["target_id"]: r for r in rows}
    required = {
        "AZ_VAR_RANGE", "AZ_ORIENT_BIO1", "AZ_CHROMA_BIO12", "AZ_SHAPE_BIO4",
        "AZ_SHAPE_BIO12", "AZ_INVOL_BIO4", "AZ_LABILITY_RHO", "AZ_ENV_MODULE_RANK",
        "INT_HERB_RR", "INT_PURP_VISIT_R2", "INT_PURP_PRED_NIKKO",
    }
    missing = required - set(by_id)
    if missing:
        raise ValueError(f"Missing simulation targets: {sorted(missing)}")
    return rows, by_id


def draw_signed(rng, magnitude=0.65):
    return rng.uniform(-magnitude, magnitude)


def simulate_once(family: str, seed: int, n_taxa: int = 60, populations_per_taxon: int = 6):
    rng = random.Random(seed)
    env_on = family in {"environment_only", "full_tradeoff_common_lability", "full_tradeoff_modular_evolvability"}
    poll_on = family in {"pollinator_only", "full_tradeoff_common_lability", "full_tradeoff_modular_evolvability"}
    ant_on = family in {"antagonist_only", "full_tradeoff_common_lability", "full_tradeoff_modular_evolvability"}
    modular = family == "full_tradeoff_modular_evolvability"

    # Symmetric priors: the target signs are not hard-coded into parameter draws.
    env_coef = {
        "oT": draw_signed(rng),
        "cP": draw_signed(rng),
        "dS": draw_signed(rng, 0.45),
        "dP": draw_signed(rng, 0.45),
        "hS": draw_signed(rng),
    } if env_on else {k: 0.0 for k in ["oT", "cP", "dS", "dP", "hS"]}

    poll_coef = {
        "orientation": draw_signed(rng, 1.4),
        "colour": draw_signed(rng, 1.6),
        "display": draw_signed(rng, 2.0),
        "defence_cost": draw_signed(rng, 0.8),
    } if poll_on else {"orientation": 0.0, "colour": 0.0, "display": 0.0, "defence_cost": 0.0}

    ant_coef = {
        "orientation": draw_signed(rng, 0.7),
        "display": draw_signed(rng, 2.0),
        "defence": draw_signed(rng, 1.8),
        "intercept": rng.uniform(0.15, 1.25),
        "fitness_cost": rng.uniform(0.68, 0.97),
    } if ant_on else {"orientation": 0.0, "display": 0.0, "defence": 0.0, "intercept": -0.5, "fitness_cost": 0.0}

    taxon_base = [[rng.gauss(0.0, 0.35) for _ in MODULES] for _ in range(n_taxa)]
    if modular:
        evolvability = [[math.exp(rng.gauss(-0.25, 0.55)) for _ in MODULES] for _ in range(n_taxa)]
        residual_sd = [[rng.uniform(0.55, 1.00) for _ in MODULES] for _ in range(n_taxa)]
    else:
        common_e = [math.exp(rng.gauss(-0.25, 0.45)) for _ in range(n_taxa)]
        evolvability = [[common_e[t]] * len(MODULES) for t in range(n_taxa)]
        # Coupled models intentionally share a taxon-level lability factor. This is the
        # structural alternative to modular evolvability, not a fitted parameter choice.
        residual_sd = [[0.45 + 0.42 * common_e[t]] * len(MODULES) for t in range(n_taxa)]

    taxon_ids, temps, precips, seasons = [], [], [], []
    traits = [[] for _ in MODULES]
    pollinator, antagonist, seed_ambient, seed_no_ant = [], [], [], []

    for t in range(n_taxa):
        for _ in range(populations_per_taxon):
            T = rng.gauss(0, 1)
            P = rng.gauss(0, 1)
            S = rng.gauss(0, 1)
            poll_pressure = rng.gauss(0, 1)
            ant_pressure = rng.gauss(0, 1)

            gradients = [
                env_coef["oT"] * T + poll_coef["orientation"] * poll_pressure - ant_coef["orientation"] * ant_pressure,
                env_coef["cP"] * P + poll_coef["colour"] * poll_pressure,
                env_coef["dS"] * S + env_coef["dP"] * P + poll_coef["display"] * poll_pressure - ant_coef["display"] * ant_pressure,
                env_coef["hS"] * S - poll_coef["defence_cost"] * poll_pressure + ant_coef["defence"] * ant_pressure,
            ]
            x = []
            for m in range(len(MODULES)):
                value = taxon_base[t][m] + evolvability[t][m] * gradients[m] + rng.gauss(0.0, residual_sd[t][m])
                x.append(value)
                traits[m].append(value)

            O, C, D, H = x
            if poll_on:
                v = sigmoid(-0.25 + poll_coef["orientation"] * O + poll_coef["colour"] * C + poll_coef["display"] * D - poll_coef["defence_cost"] * H)
            else:
                v = sigmoid(rng.gauss(-0.25, 0.18))
            if ant_on:
                a = sigmoid(ant_coef["intercept"] + ant_coef["orientation"] * O + ant_coef["display"] * D - ant_coef["defence"] * H)
            else:
                a = sigmoid(rng.gauss(-0.55, 0.15))

            # A deliberately simple abiotic survival term: it allows environmental
            # mechanisms to influence fitness without forcing any empirical sign.
            if env_on:
                abi = sigmoid(1.0 - 0.25 * max(P, 0.0) * O + 0.15 * H * S)
            else:
                abi = 0.75
            s0 = max(1e-6, v * abi)
            sa = max(1e-6, s0 * (1.0 - ant_coef["fitness_cost"] * a))

            taxon_ids.append(t)
            temps.append(T); precips.append(P); seasons.append(S)
            pollinator.append(v); antagonist.append(a)
            seed_no_ant.append(s0); seed_ambient.append(sa)

    # Within-taxon variance fraction for each simulated module.
    within_fractions = []
    for y in traits:
        total = variance(y)
        taxon_means = [mean([y[i] for i, tx in enumerate(taxon_ids) if tx == t]) for t in range(n_taxa)]
        among = variance(taxon_means)
        within_fractions.append(max(0.0, total - among) / total if total > 0 else 0.0)

    env_corr = {
        "oT": corr(traits[0], temps),
        "cP": corr(traits[1], precips),
        "dS": corr(traits[2], seasons),
        "dP": corr(traits[2], precips),
        "hS": corr(traits[3], seasons),
    }

    visible_variation, association_energy = [], []
    for t in range(n_taxa):
        idx = [i for i, tx in enumerate(taxon_ids) if tx == t]
        module_sds = [stdev([traits[m][i] for i in idx]) for m in range(len(MODULES))]
        visible_variation.append(mean(module_sds))
        local_e, vals = [temps[i] for i in idx], []
        for m in range(len(MODULES)):
            y = [traits[m][i] for i in idx]
            for ev in ([temps[i] for i in idx], [precips[i] for i in idx], [seasons[i] for i in idx]):
                vals.append(corr(y, ev) ** 2)
        association_energy.append(math.sqrt(mean(vals)))

    rr = mean(seed_no_ant) / mean(seed_ambient)
    env_oc = abs(env_corr["oT"]) + abs(env_corr["cP"])
    env_shape = abs(env_corr["dS"]) + abs(env_corr["dP"])

    return {
        "within_fraction_mean": mean(within_fractions),
        "within_fraction_min": min(within_fractions),
        "lability_association_rho": spearman(visible_variation, association_energy),
        "orientation_temperature_r": env_corr["oT"],
        "colour_precipitation_r": env_corr["cP"],
        "display_seasonality_r": env_corr["dS"],
        "display_precipitation_r": env_corr["dP"],
        "defence_seasonality_r": env_corr["hS"],
        "orientation_colour_vs_shape_env_signal_ratio": env_oc / (env_shape + 1e-9),
        "display_pollinator_r": corr(traits[2], pollinator),
        "display_pollinator_R2": corr(traits[2], pollinator) ** 2,
        "display_antagonist_r": corr(traits[2], antagonist),
        "display_antagonist_R2": corr(traits[2], antagonist) ** 2,
        "reduced_herbivory_seed_output_RR": rr,
    }


def evaluate(summary, targets):
    var_lo = float(targets["AZ_VAR_RANGE"]["lower_bound"])
    var_hi = float(targets["AZ_VAR_RANGE"]["upper_bound"])
    rho_lo = float(targets["AZ_LABILITY_RHO"]["lower_bound"])
    rho_hi = float(targets["AZ_LABILITY_RHO"]["upper_bound"])
    rr_lo = float(targets["INT_HERB_RR"]["lower_bound"])
    rr_hi = float(targets["INT_HERB_RR"]["upper_bound"])

    checks = {
        "high_below_taxon_variance": var_lo <= summary["within_fraction_mean"] <= var_hi,
        "orientation_temperature_positive": summary["orientation_temperature_r"] > 0,
        "colour_precipitation_positive": summary["colour_precipitation_r"] > 0,
        "display_seasonality_positive": summary["display_seasonality_r"] > 0,
        "display_precipitation_negative": summary["display_precipitation_r"] < 0,
        "defence_seasonality_positive": summary["defence_seasonality_r"] > 0,
        "cross_scale_decoupling": rho_lo <= summary["lability_association_rho"] <= rho_hi,
        "orientation_colour_env_stronger_than_shape": summary["orientation_colour_vs_shape_env_signal_ratio"] > 1.0,
        "display_increases_pollinator_response": summary["display_pollinator_r"] > 0.45,
        "display_increases_antagonist_response": summary["display_antagonist_r"] > 0.30,
        "herbivory_cost_matches_meta_range": rr_lo <= summary["reduced_herbivory_seed_output_RR"] <= rr_hi,
    }
    # A continuous distance is retained so models can be ranked even when no random draw
    # hits every target simultaneously.
    var_mid = (var_lo + var_hi) / 2
    rho_mid = float(targets["AZ_LABILITY_RHO"]["target_value"])
    rr_mid = float(targets["INT_HERB_RR"]["target_value"])
    poll_R2_target = float(targets["INT_PURP_VISIT_R2"]["target_value"])
    pred_R2_target = float(targets["INT_PURP_PRED_NIKKO"]["target_value"])
    distance_terms = [
        min(2.0, abs(summary["within_fraction_mean"] - var_mid) / 0.20),
        0.0 if summary["orientation_temperature_r"] > 0 else 1.0,
        0.0 if summary["colour_precipitation_r"] > 0 else 1.0,
        0.0 if summary["display_seasonality_r"] > 0 else 1.0,
        0.0 if summary["display_precipitation_r"] < 0 else 1.0,
        0.0 if summary["defence_seasonality_r"] > 0 else 1.0,
        min(2.0, abs(summary["lability_association_rho"] - rho_mid) / 0.25),
        0.0 if summary["orientation_colour_vs_shape_env_signal_ratio"] > 1.0 else 1.0,
        min(2.0, abs(summary["display_pollinator_R2"] - poll_R2_target) / 0.35),
        min(2.0, abs(summary["display_antagonist_R2"] - pred_R2_target) / 0.35),
        min(2.0, abs(math.log(summary["reduced_herbivory_seed_output_RR"] / rr_mid)) / math.log(1.35)),
    ]
    return checks, sum(checks.values()), mean(distance_terms)


def summarize_family(family, targets, draws, base_seed):
    runs = []
    for i in range(draws):
        s = simulate_once(family, base_seed + i)
        checks, nmatch, distance = evaluate(s, targets)
        runs.append((nmatch, distance, s, checks))
    runs.sort(key=lambda x: (-x[0], x[1]))
    best = runs[0]
    pass_rates = {}
    for key in best[3]:
        pass_rates[key] = sum(1 for r in runs if r[3][key]) / len(runs)
    matches = [r[0] for r in runs]
    return {
        "family": family,
        "draws": draws,
        "best_match_count": best[0],
        "n_targets": len(best[3]),
        "best_pattern_distance": round(best[1], 6),
        "median_match_count": statistics.median(matches),
        "full_match_rate": sum(1 for x in matches if x == len(best[3])) / len(matches),
        "target_pass_rates": {k: round(v, 4) for k, v in sorted(pass_rates.items())},
        "best_summary": {k: round(v, 6) for k, v in sorted(best[2].items())},
        "best_checks": best[3],
    }


def run(target_path: Path, draws: int, seed: int):
    rows, targets = load_targets(target_path)
    families = [summarize_family(f, targets, draws, seed + j * 100000) for j, f in enumerate(FAMILIES)]
    ranking = sorted(families, key=lambda x: (-x["best_match_count"], x["best_pattern_distance"], -x["full_match_rate"]))
    return {
        "contract_version": "macro_interaction_pattern_reduction_simulation_v1",
        "status_date": "2026-08-20",
        "purpose": "structural_sufficiency_not_parameter_inference",
        "target_registry": str(target_path),
        "target_rows_total": len(rows),
        "fit_target_rows": sum(1 for r in rows if r["simulation_role"] == "fit_target"),
        "simulation_targets_scored": 11,
        "draws_per_family": draws,
        "seed": seed,
        "families": families,
        "ranking": [x["family"] for x in ranking],
        "best_family_by_structural_pattern_score": ranking[0]["family"],
        "interpretation_boundary": (
            "A higher score means that a model family can generate more of the frozen pattern bundle under broad prior draws. "
            "It is not a likelihood, posterior probability, causal proof, or fitted estimate of evolutionary parameters."
        ),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--targets", type=Path, required=True)
    p.add_argument("--draws", type=int, default=180)
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
