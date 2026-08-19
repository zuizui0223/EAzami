#!/usr/bin/env python3
"""Summarize the bounded Cirsium interaction evidence seed.

This lightweight offline step validates the source-backed extraction table,
summarizes evidence by interaction class and capitulum module, and keeps the
EAzami Aim 2 field priorities synchronized with the current evidence ceiling.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Iterable

REQUIRED_COLUMNS = [
    "evidence_id", "study_id", "year", "taxon", "region",
    "interaction_domain", "partner_guild", "capitulum_module", "design",
    "trait_or_treatment", "response_chain", "fitness_endpoint", "direction",
    "quantitative_extraction_status", "direct_capitulum_relevance",
    "doctoral_use", "doi", "primary_source_title", "claim_boundary",
]

ALLOWED_INTERACTION_DOMAINS = {
    "pollination",
    "pollination_florivory_tradeoff",
    "pre_dispersal_seed_predation",
    "foliar_herbivory_context",
}
ALLOWED_RELEVANCE = {"direct", "contextual"}

AIM2_TARGET_MODULES = {
    "head_orientation": {"head_orientation"},
    "flower_colour": {"flower_colour"},
    "involucre_spine": {"involucre", "phyllary", "spine", "involucre_spine"},
    "stickiness": {"stickiness"},
    "display_size": {"display_size"},
    "floral_scent": {"floral_scent"},
    "capitulum_size_position": {"capitulum_size", "capitulum_position_and_size"},
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != REQUIRED_COLUMNS:
            raise ValueError(
                f"Unexpected columns. Expected {REQUIRED_COLUMNS}; observed {reader.fieldnames}"
            )
        rows = list(reader)
    if not rows:
        raise ValueError("Evidence seed is empty.")
    return rows


def validate(rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    rows = list(rows)
    ids = [r["evidence_id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("evidence_id must be unique.")

    for row in rows:
        missing = [name for name in REQUIRED_COLUMNS if not row[name].strip()]
        if missing:
            raise ValueError(f"{row['evidence_id']} has empty fields: {missing}")
        if row["interaction_domain"] not in ALLOWED_INTERACTION_DOMAINS:
            raise ValueError(f"{row['evidence_id']} invalid interaction_domain")
        if row["direct_capitulum_relevance"] not in ALLOWED_RELEVANCE:
            raise ValueError(f"{row['evidence_id']} invalid relevance")
        year = int(row["year"])
        if not 1900 <= year <= 2100:
            raise ValueError(f"{row['evidence_id']} year outside expected range")
        if not row["taxon"].startswith("Cirsium "):
            raise ValueError(f"{row['evidence_id']} is not a Cirsium taxon")
        if not row["doi"].startswith("10."):
            raise ValueError(f"{row['evidence_id']} DOI is not normalized")
    return rows


def summarize(rows: list[dict[str, str]]) -> dict:
    direct = [r for r in rows if r["direct_capitulum_relevance"] == "direct"]
    studies = sorted({r["study_id"] for r in rows})
    taxa = sorted({r["taxon"] for r in rows})

    domain_rows = Counter(r["interaction_domain"] for r in rows)
    domain_studies = {
        d: len({r["study_id"] for r in rows if r["interaction_domain"] == d})
        for d in sorted(domain_rows)
    }
    module_rows = Counter(r["capitulum_module"] for r in direct)
    response_chains = Counter(r["response_chain"] for r in rows)
    fitness_rows = [r for r in rows if r["fitness_endpoint"] != "none"]
    full_chain_rows = [
        r for r in direct if r["response_chain"] == "trait_to_interaction_and_fitness"
    ]

    module_gate = {}
    for target, aliases in AIM2_TARGET_MODULES.items():
        matched = [r for r in direct if r["capitulum_module"] in aliases]
        module_gate[target] = {
            "direct_rows": len(matched),
            "independent_studies": len({r["study_id"] for r in matched}),
            "fitness_rows": sum(r["fitness_endpoint"] != "none" for r in matched),
            "manipulative_rows": sum("manipulation" in r["design"] for r in matched),
        }

    return {
        "contract_version": "cirsium_interaction_evidence_summary_v1",
        "status_date": "2026-08-19",
        "scope": "bounded_primary_literature_seed_for_EAzami_Aim2_not_exhaustive_meta_analysis",
        "coverage": {
            "evidence_rows": len(rows),
            "independent_studies": len(studies),
            "taxa": len(taxa),
            "taxon_names": taxa,
            "direct_capitulum_rows": len(direct),
            "contextual_herbivory_rows": len(rows) - len(direct),
        },
        "interaction_domain_rows": dict(sorted(domain_rows.items())),
        "interaction_domain_independent_studies": domain_studies,
        "direct_module_rows": dict(sorted(module_rows.items())),
        "response_chain_rows": dict(sorted(response_chains.items())),
        "fitness_coverage": {
            "rows_with_reproductive_or_demographic_fitness": len(fitness_rows),
            "direct_trait_interaction_fitness_rows": len(full_chain_rows),
            "direct_trait_interaction_fitness_studies": len(
                {r["study_id"] for r in full_chain_rows}
            ),
        },
        "aim2_module_gate": module_gate,
        "current_inference": [
            "Cirsium evidence supports capitulum display effects on pollinator behaviour and shows that floral signals can attract both mutualists and florivores.",
            "A classic Cirsium palustre natural colour-polymorphism study reports preferential pollination of white flowers, so flower colour is not an interaction-evidence blank; the bounded evidence still lacks a replicated ancestry-controlled colour-to-effective-pollination-to-reproductive-fitness chain.",
            "Predispersal seed predators can strongly reduce achene or seed output; the expanded seed also confirms fitness costs in Cirsium palustre and Cirsium vulgare, while trait-specific defensive mechanisms remain unresolved.",
            "The only recovered direct stickiness manipulation was null, so visible defensive-looking structures cannot be assigned a defence function without manipulation.",
            "No direct Cirsium head-orientation or phyllary/spine manipulation linked through interaction to reproductive fitness was recovered in the bounded targeted search.",
        ],
        "field_experiment_priorities": [
            {
                "rank": 1,
                "module": "head_orientation",
                "reason": "No direct Cirsium orientation study was recovered in the bounded targeted search; it is a primary Azami trait and requires a pollination/rain/fitness manipulation in ancestry-resolved focal populations.",
            },
            {
                "rank": 2,
                "module": "flower_colour",
                "reason": "Cirsium palustre provides direct natural colour-morph pollination evidence, but the bounded seed still lacks replicated ancestry-controlled colour-to-effective-pollination-to-reproductive-fitness evidence. Repeated W/coloured systems make this both an Aim 2 function test and an Aim 3 mechanism bridge.",
            },
            {
                "rank": 3,
                "module": "involucre_spine",
                "reason": "No direct phyllary/spine manipulation was recovered. Test only after focal populations show repeatable, measurable variation; record both antagonist exclusion and pollinator-access costs.",
            },
            {
                "rank": 4,
                "module": "stickiness",
                "reason": "One direct manipulation was recovered and was null, so stickiness is not assumed to be defensive and is lower priority unless the Ryukyu focal taxa provide strong natural replication.",
            },
        ],
        "effect_size_meta_analysis_gate": {
            "status": "not_yet_authorized",
            "minimum_independent_studies_per_harmonized_outcome": 5,
            "minimum_taxa_per_harmonized_outcome": 3,
            "requirements": [
                "same biological contrast and response scale",
                "original-study deduplication",
                "separate visitor abundance from effective pollination",
                "separate florivory from pre-dispersal seed predation and foliar herbivory",
                "retain null results and study-level sampling variance",
            ],
            "current_use": "systematic evidence map and field-design prioritization; do not pool heterogeneous visitor, damage and fitness outcomes.",
        },
        "claim_boundary": "This bounded, source-backed seed demonstrates feasibility and identifies doctoral field gaps. It is not an exhaustive literature census, does not estimate pooled effect sizes, and absence from the seed is not evidence that an interaction or study does not exist.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = summarize(validate(read_rows(args.input)))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
