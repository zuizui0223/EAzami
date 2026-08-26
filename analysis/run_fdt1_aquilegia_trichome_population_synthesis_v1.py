#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path


MEAN_FIELDS = (
    "control_herbivory_damage_mean",
    "removal_herbivory_damage_mean",
    "control_healthy_fruit_set_mean",
    "removal_healthy_fruit_set_mean",
)
SE_FIELDS = (
    "control_herbivory_damage_se",
    "removal_herbivory_damage_se",
    "control_healthy_fruit_set_se",
    "removal_healthy_fruit_set_se",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def validate(rows: list[dict[str, str]]) -> None:
    if len(rows) != 8:
        raise ValueError("the frozen Aquilegia extraction must contain eight populations")
    ids = [row["effect_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate effect_id")
    if {row["study_cluster"] for row in rows} != {"Jaime2013"}:
        raise ValueError("all populations must remain in one study cluster")
    if {row["source_doi"] for row in rows} != {"10.1007/s00442-012-2553-z"}:
        raise ValueError("source DOI drift")
    source_hashes = {row["source_artifact_sha256"] for row in rows}
    if len(source_hashes) != 1 or len(next(iter(source_hashes))) != 64:
        raise ValueError("source artifact hash drift")
    for row in rows:
        if min(int(row["n_control"]), int(row["n_removal"])) <= 0:
            raise ValueError("sample sizes must be positive")
        values = {field: float(row[field]) for field in MEAN_FIELDS + SE_FIELDS}
        if any(values[field] <= 0 for field in MEAN_FIELDS):
            raise ValueError("delta-method lnRR requires positive means")
        if any(values[field] < 0 for field in SE_FIELDS):
            raise ValueError("standard errors must be non-negative")
        for field in (
            "control_healthy_fruit_set_mean",
            "removal_healthy_fruit_set_mean",
        ):
            if not 0 < values[field] <= 1:
                raise ValueError("healthy fruit set must be in (0, 1]")
        for field in ("source_url", "source_locator", "extraction_method", "claim_boundary"):
            if not row[field].strip():
                raise ValueError(f"missing provenance field: {field}")


def lnrr(
    numerator_mean: float,
    numerator_se: float,
    denominator_mean: float,
    denominator_se: float,
) -> tuple[float, float]:
    estimate = math.log(numerator_mean / denominator_mean)
    se = math.sqrt((numerator_se / numerator_mean) ** 2 + (denominator_se / denominator_mean) ** 2)
    return estimate, se


def random_effects_dl(effects: list[dict[str, float]]) -> dict[str, float | list[float]]:
    estimates = [effect["lnRR"] for effect in effects]
    variances = [effect["se_lnRR"] ** 2 for effect in effects]
    weights = [1.0 / variance for variance in variances]
    sum_weights = sum(weights)
    fixed = sum(weight * estimate for weight, estimate in zip(weights, estimates)) / sum_weights
    q = sum(weight * (estimate - fixed) ** 2 for weight, estimate in zip(weights, estimates))
    df = len(effects) - 1
    c_value = sum_weights - sum(weight**2 for weight in weights) / sum_weights
    tau2 = max(0.0, (q - df) / c_value) if c_value > 0 else 0.0
    random_weights = [1.0 / (variance + tau2) for variance in variances]
    random_sum = sum(random_weights)
    pooled = sum(weight * estimate for weight, estimate in zip(random_weights, estimates)) / random_sum
    pooled_se = math.sqrt(1.0 / random_sum)
    i2 = max(0.0, (q - df) / q) * 100.0 if q > 0 else 0.0
    return {
        "k_populations": len(effects),
        "pooled_lnRR": pooled,
        "se_lnRR": pooled_se,
        "pooled_RR": math.exp(pooled),
        "ci95_RR_normal": [math.exp(pooled - 1.96 * pooled_se), math.exp(pooled + 1.96 * pooled_se)],
        "tau2_lnRR": tau2,
        "Q": q,
        "Q_df": df,
        "I2_percent": i2,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    rows = read_rows(args.input)
    validate(rows)
    fruit_effects: list[dict[str, float | str | int | list[float]]] = []
    damage_effects: list[dict[str, float | str | int | list[float]]] = []
    by_species: dict[str, dict[str, list[float]]] = defaultdict(lambda: {"fruit": [], "damage": []})

    for row in rows:
        fruit_y, fruit_se = lnrr(
            float(row["control_healthy_fruit_set_mean"]),
            float(row["control_healthy_fruit_set_se"]),
            float(row["removal_healthy_fruit_set_mean"]),
            float(row["removal_healthy_fruit_set_se"]),
        )
        damage_y, damage_se = lnrr(
            float(row["removal_herbivory_damage_mean"]),
            float(row["removal_herbivory_damage_se"]),
            float(row["control_herbivory_damage_mean"]),
            float(row["control_herbivory_damage_se"]),
        )
        common = {
            "effect_id": row["effect_id"],
            "taxon": row["taxon"],
            "population": row["population"],
            "n_control": int(row["n_control"]),
            "n_removal": int(row["n_removal"]),
        }
        fruit_effects.append(
            common
            | {
                "lnRR": fruit_y,
                "se_lnRR": fruit_se,
                "RR": math.exp(fruit_y),
                "ci95_RR": [math.exp(fruit_y - 1.96 * fruit_se), math.exp(fruit_y + 1.96 * fruit_se)],
            }
        )
        damage_effects.append(
            common
            | {
                "lnRR": damage_y,
                "se_lnRR": damage_se,
                "RR": math.exp(damage_y),
                "ci95_RR": [math.exp(damage_y - 1.96 * damage_se), math.exp(damage_y + 1.96 * damage_se)],
            }
        )
        species = row["taxon"].split(" subsp.")[0]
        by_species[species]["fruit"].append(fruit_y)
        by_species[species]["damage"].append(damage_y)

    species_direction = {
        species: {
            "population_count": len(endpoints["fruit"]),
            "fruit_lnRR_positive": sum(value > 0 for value in endpoints["fruit"]),
            "fruit_lnRR_zero": sum(value == 0 for value in endpoints["fruit"]),
            "fruit_lnRR_negative": sum(value < 0 for value in endpoints["fruit"]),
            "damage_lnRR_positive": sum(value > 0 for value in endpoints["damage"]),
            "damage_lnRR_zero": sum(value == 0 for value in endpoints["damage"]),
            "damage_lnRR_negative": sum(value < 0 for value in endpoints["damage"]),
        }
        for species, endpoints in sorted(by_species.items())
    }

    output = {
        "contract_version": "fdt1_aquilegia_trichome_population_synthesis_v1",
        "status_date": "2026-08-26",
        "coverage": {
            "population_effects": len(rows),
            "independent_study_clusters": 1,
            "taxa": sorted({row["taxon"] for row in rows}),
            "design_total_n": sum(int(row["n_control"]) + int(row["n_removal"]) for row in rows),
        },
        "estimands": {
            "healthy_fruit_set": "ln(mean healthy fruit set, intact control / trichome removal)",
            "herbivory_damage": "ln(mean herbivory damage, trichome removal / intact control)",
        },
        "healthy_fruit_set_effects": fruit_effects,
        "herbivory_damage_effects": damage_effects,
        "population_level_random_effects_descriptive": {
            "healthy_fruit_set": random_effects_dl(fruit_effects),
            "herbivory_damage": random_effects_dl(damage_effects),
        },
        "direction_by_species": species_direction,
        "published_hierarchical_model_tests": {
            "healthy_fruit_set": {"treatment_F": 40.71, "treatment_p": 0.001, "species_by_treatment_F": 8.86, "species_by_treatment_p": 0.016},
            "herbivory_damage": {"treatment_F": 22.5, "treatment_p": 0.007, "species_by_treatment_F": 8.12, "species_by_treatment_p": 0.041},
            "source_locator": "Table 10; PDF page 127; printed page 115",
        },
        "interpretation": "Removing glandular-trichome protection increased herbivory damage and reduced healthy fruit set overall, but population directions and the published species-by-treatment interactions show strong context dependence. Aquilegia can now calibrate a direct trichome-to-enemy-to-fitness pathway, not a universal sticky-defence effect.",
        "claim_boundary": "The eight population effects come from one article and one coordinated experiment, so they are not eight independent studies. The DL summaries describe among-population effects only and are not an across-study meta-analysis. Delta-method lnRR uses the published raw population means and SEs; the published F tests come from the authors' hierarchical models, with variables log-transformed when necessary. Do not transport the magnitude to Cirsium or equate Aquilegia glandular trichomes with capitulum stickiness without focal tests.",
        "inputs": {"extract": args.input.as_posix(), "extract_sha256": sha256(args.input)},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
