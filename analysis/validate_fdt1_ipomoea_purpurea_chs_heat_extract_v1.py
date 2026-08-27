from __future__ import annotations

import argparse
import csv
import itertools
import json
from pathlib import Path


FACTORS = (
    "maternal_genotype",
    "paternal_genotype",
    "maternal_light",
    "paternal_light",
    "maternal_temperature",
    "paternal_temperature",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    with args.input.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    if len(rows) != 64 or len({row["cell_id"] for row in rows}) != 64:
        raise ValueError("expected 64 unique Table 1 cells")

    levels = {factor: sorted({row[factor] for row in rows}) for factor in FACTORS}
    expected = set(itertools.product(*(levels[factor] for factor in FACTORS)))
    observed = {tuple(row[factor] for factor in FACTORS) for row in rows}
    if observed != expected:
        raise ValueError("Table 1 is not a complete 2^6 factorial cell extract")

    total_n = sum(int(row["n_plant_day_pollination_pairs"]) for row in rows)
    if total_n != 1342:
        raise ValueError(f"expected the reported total n=1342, found {total_n}")
    if any(not 0 <= float(row["mean_fertilization_success"]) <= 1 for row in rows):
        raise ValueError("fertilization-success means must be proportions")
    if any(float(row["se_reported"]) <= 0 for row in rows):
        raise ValueError("reported SE must be positive")

    summary = {
        "contract_version": "fdt1_ipomoea_purpurea_chs_heat_extract_v1",
        "source_id": "10.1046/j.1365-294X.2003.01786.x",
        "source_location": "Table_1",
        "rows": len(rows),
        "total_plant_day_pollination_pairs": total_n,
        "factor_levels": levels,
        "complete_two_level_factorial": True,
        "observation_unit": "one_or_two_flowers_pooled_on_one_maternal_plant_on_one_day",
        "reported_interactions": {
            "maternal_genotype_x_maternal_temperature": {"F": 7.32, "p": 0.0069},
            "paternal_genotype_x_maternal_temperature": {"F": 4.85, "p": 0.0278},
        },
        "author_reported_relative_differences": {
            "mutant_recipient_deficit_at_high_maternal_temperature_percent": 26,
            "mutant_pollen_deficit_on_high_temperature_recipients_percent": 24,
        },
        "readiness": "bounded_effect_extraction_ready_not_pool_ready",
        "blocking_design_features": [
            "one_chamber_per_temperature",
            "one_light_subchamber_per_light_level_within_temperature",
            "two_constructed_lines_pooled_in_the_published_cell_table",
            "maternal_plants_generally_used_once_and_rarely_twice_per_treatment_combination",
            "published_cell_SEs_do_not_supply_cross_cell_or_repeated_plant_covariance",
        ],
        "claim_boundary": (
            "This is a CHS-D whole-flavonoid-pathway genotype-by-environment calibration, "
            "not an anthocyanin-only visible-petal effect. Temperature is chamber-confounded; "
            "do not treat the 64 cells as independent study effects or inverse-variance pool them."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
