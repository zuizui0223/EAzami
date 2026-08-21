#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/evidence/cirsium_demographic_transmission_meta_v1.csv"
OUTPUT = ROOT / "data/evidence/cirsium_demographic_transmission_meta_v1.json"


def truthy(value: str) -> bool:
    return value.strip() in {"1", "true", "True", "yes", "YES"}


def main() -> None:
    with INPUT.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    study_ids = [row["study_id"] for row in rows]
    if len(study_ids) != len(set(study_ids)):
        raise SystemExit("study_id values must be unique")

    taxa = sorted({row["taxon"] for row in rows})
    transmission = Counter(row["population_transmission"] for row in rows)
    fecundity_support = sum(truthy(row["fecundity_cost_supported"]) for row in rows)
    abiotic_tested = [row for row in rows if truthy(row["broad_abiotic_context_tested"])]
    abiotic_general_support = sum(
        truthy(row["broad_abiotic_general_moderator_support"]) for row in abiotic_tested
    )
    gate_tested = [row for row in rows if truthy(row["demographic_gate_tested"])]
    gate_supported = sum(truthy(row["demographic_gate_supported"]) for row in gate_tested)

    result = {
        "version": "v1",
        "study_count": len(rows),
        "taxon_count": len(taxa),
        "taxa": taxa,
        "fecundity_cost_supported_studies": fecundity_support,
        "population_transmission": {
            "consistent": transmission.get("consistent", 0),
            "context_dependent": transmission.get("context_dependent", 0),
            "blocked": transmission.get("blocked", 0),
        },
        "broad_abiotic_context_tested_studies": len(abiotic_tested),
        "broad_abiotic_general_moderator_support_studies": abiotic_general_support,
        "demographic_gate_tested_studies": len(gate_tested),
        "demographic_gate_supported_studies": gate_supported,
        "headline": (
            "Reproductive insect herbivory has a repeatable fecundity cost, but whether that cost "
            "propagates to recruitment or population growth is gated more consistently by demographic "
            "opportunity (safe sites, disturbance and density dependence) than by broad abiotic gradients "
            "such as productivity, fertility or elevation."
        ),
        "pooling_status": (
            "Structured quantitative meta-synthesis only. Population-level response metrics include raw "
            "recruitment ratios, intrinsic growth rates and IPM/Bayesian lambda outputs, so a single pooled "
            "population-growth effect size is not authorized."
        ),
    }

    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
