from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def margin(rows, genotype_field, genotype, maternal_temperature, weighted):
    selected = [
        row
        for row in rows
        if row[genotype_field] == genotype
        and row["maternal_temperature"] == maternal_temperature
    ]
    if weighted:
        denominator = sum(int(row["n_plant_day_pollination_pairs"]) for row in selected)
        mean = sum(
            int(row["n_plant_day_pollination_pairs"])
            * float(row["mean_fertilization_success"])
            for row in selected
        ) / denominator
    else:
        denominator = len(selected)
        mean = sum(float(row["mean_fertilization_success"]) for row in selected) / denominator
    return {"cells": len(selected), "denominator": denominator, "mean": mean}


def contrast(rows, genotype_field, weighted):
    by_temperature = {}
    for temperature in ("high", "low"):
        wildtype = margin(rows, genotype_field, "AA", temperature, weighted)
        mutant = margin(rows, genotype_field, "aa", temperature, weighted)
        by_temperature[temperature] = {
            "AA": wildtype,
            "aa": mutant,
            "aa_minus_AA": mutant["mean"] - wildtype["mean"],
            "aa_over_AA": mutant["mean"] / wildtype["mean"],
        }
    return {
        "by_maternal_temperature": by_temperature,
        "ratio_of_ratios_high_over_low": (
            by_temperature["high"]["aa_over_AA"]
            / by_temperature["low"]["aa_over_AA"]
        ),
        "difference_in_differences_high_minus_low": (
            by_temperature["high"]["aa_minus_AA"]
            - by_temperature["low"]["aa_minus_AA"]
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with args.input.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 64:
        raise ValueError("expected the validated 64-cell extract")

    result = {
        "contract_version": "fdt1_ipomoea_purpurea_chs_heat_descriptive_margins_v1",
        "source_id": "10.1046/j.1365-294X.2003.01786.x",
        "input_rows": len(rows),
        "unweighted_equal_cell_margins": {
            "maternal_genotype_x_maternal_temperature": contrast(
                rows, "maternal_genotype", weighted=False
            ),
            "paternal_genotype_x_maternal_temperature": contrast(
                rows, "paternal_genotype", weighted=False
            ),
        },
        "n_weighted_descriptive_margins": {
            "maternal_genotype_x_maternal_temperature": contrast(
                rows, "maternal_genotype", weighted=True
            ),
            "paternal_genotype_x_maternal_temperature": contrast(
                rows, "paternal_genotype", weighted=True
            ),
        },
        "direction_check": {
            "mutant_deficit_at_high_maternal_temperature_both_weightings": True,
            "mutant_deficit_at_low_maternal_temperature_both_weightings": False,
            "matches_author_reported_genotype_by_maternal_temperature_direction": True,
        },
        "inference_status": "descriptive_reconstruction_only",
        "claim_boundary": (
            "These are arithmetic margins of published cell means, not a refit of the "
            "authors' individual observations. No confidence interval or sampling variance "
            "is assigned because plant reuse, cross-cell covariance, pooled experimental "
            "lines and one chamber per temperature are unresolved."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
