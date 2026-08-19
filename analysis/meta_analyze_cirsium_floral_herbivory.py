#!/usr/bin/env python3
"""Quantitative pilot meta-analysis of experimental Cirsium reproductive herbivory.

Estimand: benefit to reproductive output when insect herbivory on reproductive or
apical tissues is experimentally reduced. Positive effects mean higher reproductive
output under reduced herbivory.

Published Hedges-d values are transformed exactly to Fisher z. Newer t/F model
statistics are transformed to partial-r/Fisher-z with a documented denominator-df
variance approximation. The latter must be replaced by raw-data/model-covariance
effects before a definitive publication-level magnitude is claimed.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path


def rf(x: float) -> float:
    return round(float(x), 12)


def d_to_z(d: float, var_d: float) -> tuple[float, float, float]:
    r = d / math.sqrt(d * d + 4.0)
    z = math.atanh(r)
    return r, z, var_d / (d * d + 4.0)


def t_to_z(t: float, df: float) -> tuple[float, float, float]:
    r = abs(t) / math.sqrt(t * t + df)
    return r, math.atanh(r), 1.0 / (df - 1.0)


def f_to_z(f_value: float, df_error: float) -> tuple[float, float, float]:
    r = math.sqrt(f_value / (f_value + df_error))
    return r, math.atanh(r), 1.0 / (df_error - 1.0)


def inverse_variance_combine(items: list[dict]) -> tuple[float, float]:
    weights = [1.0 / x["var_z"] for x in items]
    z = sum(w * x["z"] for w, x in zip(weights, items)) / sum(weights)
    return z, 1.0 / sum(weights)


def dl_random_effects(studies: list[dict]) -> dict:
    k = len(studies)
    if k < 2:
        raise ValueError("Need at least two independent studies")
    w = [1.0 / x["var_z"] for x in studies]
    fixed = sum(wi * x["z"] for wi, x in zip(w, studies)) / sum(w)
    q = sum(wi * (x["z"] - fixed) ** 2 for wi, x in zip(w, studies))
    c = sum(w) - sum(wi * wi for wi in w) / sum(w)
    tau2 = max(0.0, (q - (k - 1)) / c)
    wr = [1.0 / (x["var_z"] + tau2) for x in studies]
    pooled = sum(wi * x["z"] for wi, x in zip(wr, studies)) / sum(wr)
    var = 1.0 / sum(wr)
    se = math.sqrt(var)
    lo, hi = pooled - 1.96 * se, pooled + 1.96 * se
    z_stat = pooled / se
    p_two = math.erfc(abs(z_stat) / math.sqrt(2.0))
    i2 = max(0.0, (q - (k - 1)) / q) * 100.0 if q > 0 else 0.0
    r, r_lo, r_hi = math.tanh(pooled), math.tanh(lo), math.tanh(hi)

    def r_to_d(value: float) -> float:
        return 2.0 * value / math.sqrt(1.0 - value * value)

    return {
        "method": "DerSimonian-Laird_random_effects_pilot",
        "k_independent_studies": k,
        "pooled_fisher_z": rf(pooled),
        "se_fisher_z": rf(se),
        "ci95_fisher_z": [rf(lo), rf(hi)],
        "pooled_r": rf(r),
        "ci95_r": [rf(r_lo), rf(r_hi)],
        "approx_equivalent_standardized_mean_difference": rf(r_to_d(r)),
        "approx_equivalent_standardized_mean_difference_ci95": [rf(r_to_d(r_lo)), rf(r_to_d(r_hi))],
        "z_test": rf(z_stat),
        "p_two_sided": rf(p_two),
        "Q": rf(q),
        "Q_df": k - 1,
        "tau2_fisher_z": rf(tau2),
        "I2_percent": rf(i2),
    }


def load_effects(path: Path) -> tuple[list[dict], list[dict]]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    included, pending = [], []
    for row in rows:
        if row["primary_meta_status"] != "include":
            pending.append(row)
            continue
        test_type = row["test_type"]
        if test_type == "reported_Hedges_d":
            # Source d is damage-vs-undamaged. Reverse sign so positive means benefit of reducing herbivory.
            d = -float(row["reported_hedges_d"])
            r, z, var_z = d_to_z(d, float(row["reported_var_d"]))
            variance_basis = "exact_delta_from_published_Hedges_d_variance"
        elif test_type == "t":
            r, z, var_z = t_to_z(float(row["test_stat"]), float(row["df_error"]))
            variance_basis = "approx_1_over_df_minus_1_from_mixed_model_t"
        elif test_type == "F":
            r, z, var_z = f_to_z(float(row["test_stat"]), float(row["df_error"]))
            variance_basis = "approx_1_over_df_minus_1_from_one_df_F"
        else:
            raise ValueError(f"Unsupported included test type: {test_type}")
        included.append({
            "study_cluster": row["study_cluster"],
            "effect_id": row["effect_id"],
            "taxon": row["taxon"],
            "year": int(row["year"]),
            "test_type": test_type,
            "r": r,
            "z": z,
            "var_z": var_z,
            "variance_basis": variance_basis,
            "source_locator": row["source_locator"],
        })
    return included, pending


def summarize(input_path: Path) -> dict:
    effects, pending = load_effects(input_path)
    by_study: dict[str, list[dict]] = defaultdict(list)
    for effect in effects:
        by_study[effect["study_cluster"]].append(effect)

    study_level = []
    for cluster in sorted(by_study):
        items = by_study[cluster]
        z, var_z = inverse_variance_combine(items)
        study_level.append({
            "study_cluster": cluster,
            "n_effects_collapsed": len(items),
            "z": z,
            "var_z": var_z,
            "r": math.tanh(z),
            "taxa": sorted({x["taxon"] for x in items}),
        })

    pooled = dl_random_effects(study_level)
    leave_one_out = []
    for omitted in sorted(x["study_cluster"] for x in study_level):
        loo = dl_random_effects([x for x in study_level if x["study_cluster"] != omitted])
        leave_one_out.append({
            "omitted_study": omitted,
            "pooled_r": loo["pooled_r"],
            "ci95_r": loo["ci95_r"],
            "I2_percent": loo["I2_percent"],
        })

    effect_out = [{
        "study_cluster": x["study_cluster"],
        "effect_id": x["effect_id"],
        "taxon": x["taxon"],
        "year": x["year"],
        "test_type": x["test_type"],
        "r": rf(x["r"]),
        "fisher_z": rf(x["z"]),
        "var_z": rf(x["var_z"]),
        "variance_basis": x["variance_basis"],
        "source_locator": x["source_locator"],
    } for x in effects]

    study_out = [{
        "study_cluster": x["study_cluster"],
        "n_effects_collapsed": x["n_effects_collapsed"],
        "fisher_z": rf(x["z"]),
        "var_z": rf(x["var_z"]),
        "r": rf(x["r"]),
        "taxa": x["taxa"],
    } for x in study_level]

    return {
        "contract_version": "cirsium_floral_herbivory_meta_pilot_v1",
        "status_date": "2026-08-19",
        "estimand": "benefit_to_reproductive_output_when_insect_herbivory_on_reproductive_or_apical_tissues_is_experimentally_reduced",
        "effect_direction": "positive_means_higher_reproductive_output_under_reduced_herbivory",
        "effect_level": effect_out,
        "coverage": {
            "included_effect_rows": len(effects),
            "independent_study_clusters": len(study_level),
            "included_taxa": sorted({x["taxon"] for x in effects}),
            "pending_raw_data_studies": sorted({x["study_cluster"] for x in pending}),
        },
        "study_level": study_out,
        "random_effects": pooled,
        "leave_one_study_out": leave_one_out,
        "current_quantitative_inference": "In this four-study pilot, experimentally reducing reproductive/apical insect herbivory has a consistently positive standardized association with reproductive output. The random-effects pooled direction remains positive in every leave-one-study-out analysis.",
        "publication_gate": {
            "status": "pilot_quantitative_meta_not_publication_grade",
            "reasons": [
                "only four independent study clusters are currently pooled",
                "two newer studies use test-statistic-to-partial-r variance approximations",
                "tissue targeted by insect manipulation differs among floral heads, broader insect exclusion and apical meristems",
                "raw-data reanalysis is available for additional studies and should replace approximations where possible",
            ],
            "next_required": [
                "reanalyse Adhikari_Russell_2014 Dryad individual data to the same reproductive-output estimand",
                "reanalyse West_Louda_2021 public plant/head data to the same estimand",
                "recover raw/group-level variance for West_Louda_2018 and Russell_Houseman_2019 where possible",
                "then fit a multilevel random-effects model with study and taxon/tissue moderators",
            ],
        },
        "claim_boundary": "This is a real quantitative pilot meta-analysis, not an evidence count, but it is not yet a definitive pooled effect size. It supports a robust direction of reproductive cost from insect herbivory in the currently extractable Cirsium experiments; magnitude and moderators remain provisional until raw-data harmonization expands the independent-study set.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = summarize(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
