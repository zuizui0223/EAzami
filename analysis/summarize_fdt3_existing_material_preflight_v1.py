#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


REQUIRED_PREFLIGHT_COLUMNS = {
    "material_id",
    "source_artifact",
    "registered_units",
    "independence_unit",
    "current_role",
    "fdt3_event_ledger_rows",
    "allowed_use",
    "blocking_reason",
    "route",
    "claim_boundary",
}

REQUIRED_EVENT_COLUMNS = {
    "event_id",
    "source_id",
    "study_cluster_id",
    "lineage_id",
    "module",
    "raw_trait",
    "ancestor_functional_state",
    "derived_functional_state",
    "transition_direction_status",
    "phylogeny_scope",
    "topology_uncertainty",
    "branch_or_node_id",
    "age_median",
    "age_lower",
    "age_upper",
    "age_unit",
    "ancestor_ecological_regime",
    "derived_ecological_regime",
    "ecological_transition_axis",
    "ecological_transition_evidence",
    "independent_origin_group",
    "molecular_reuse_status",
    "fitness_validation_status",
    "event_independence_status",
    "allowed_term",
    "source_locator",
    "claim_boundary",
}

REQUIRED_PILOT_COLUMNS = {
    "candidate_id",
    "source_id",
    "taxon_scope",
    "orientation_ontology",
    "phylogenetic_result",
    "ecology_result",
    "topology_boundary",
    "event_rows_admitted",
    "disposition",
    "source_url",
    "claim_boundary",
}


def read_csv(path: Path, required: set[str]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"missing header: {path}")
        missing = required - set(reader.fieldnames)
        if missing:
            raise ValueError(f"missing columns in {path}: {sorted(missing)}")
        return [dict(row) for row in reader]


def validate(
    preflight: list[dict[str, str]],
    events: list[dict[str, str]],
    pilot: list[dict[str, str]],
) -> None:
    if [row["material_id"] for row in preflight] != [f"FDT3P{i:02d}" for i in range(1, 7)]:
        raise ValueError("unexpected preflight material order")
    if any(int(row["fdt3_event_ledger_rows"]) != 0 for row in preflight):
        raise ValueError("preflight must not claim unextracted event rows")
    if events:
        raise ValueError("FDT3 v1 event ledger must remain empty until primary event extraction")
    if [row["candidate_id"] for row in pilot] != [f"ORP{i:02d}" for i in range(1, 8)]:
        raise ValueError("unexpected orientation-pilot candidate order")
    if any(int(row["event_rows_admitted"]) != 0 for row in pilot):
        raise ValueError("orientation pilot has not licensed an event row")
    for row in preflight:
        if not row["blocking_reason"] or not row["claim_boundary"]:
            raise ValueError(f"missing boundary for {row['material_id']}")


def summarize(
    preflight: list[dict[str, str]],
    events: list[dict[str, str]],
    pilot: list[dict[str, str]],
) -> dict[str, object]:
    role_counts = Counter(row["current_role"] for row in preflight)
    disposition_counts = Counter(row["disposition"] for row in pilot)
    return {
        "contract_version": "fdt3_existing_material_preflight_v1",
        "material_classes_audited": len(preflight),
        "registered_input_units": sum(int(row["registered_units"]) for row in preflight),
        "current_role_counts": dict(sorted(role_counts.items())),
        "extracted_external_transition_events": len(events),
        "orientation_primary_pilot": {
            "primary_sources_audited": len(pilot),
            "event_rows_admitted": sum(int(row["event_rows_admitted"]) for row in pilot),
            "disposition_counts": dict(sorted(disposition_counts.items())),
            "priority_source": "10.1111/jse.12554",
            "decision": "NO_EVENT_ROWS_ADMITTED_SOURCE_FAMILY_IDENTIFIED_BRANCHWISE_EXTRACTION_PENDING",
        },
        "gate_decision": "NOT_READY_ZERO_PRIMARY_EVENT_LEDGER_ROWS_SOURCE_FAMILY_IDENTIFIED",
        "terminology_contract": {
            "repeated_or_homoplastic_state": "independent origin is reconstructed under declared topology uncertainty",
            "convergence_or_parallelism": "ancestral relationship plus trajectory or mechanism criterion is explicit",
            "parallel_or_convergent_adaptation": "ecological function and fitness validation are additionally present",
        },
        "reopen_requirements": [
            "primary-source branch or node with ancestral and derived functional states",
            "declared topology and transition-direction uncertainty",
            "ecological transition evidence coded separately from trait transition",
            "age and molecular/fitness validation retained as optional rather than imputed",
            "study-cluster and independent-origin rules fixed before event coupling analysis",
        ],
        "next_valid_action": (
            "Lawfully recover Lonicera Supporting Fig. S1 and Table S3; freeze the "
            "node-state probability and branch-independence rules before extracting "
            "all accepted, rejected and directionally unresolved branches."
        ),
        "claim_boundary": (
            "This preflight inventories current repository roles. It does not infer "
            "external repeated evolution, convergence, parallelism or adaptation."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", type=Path, required=True)
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--orientation-pilot", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    preflight = read_csv(args.preflight, REQUIRED_PREFLIGHT_COLUMNS)
    events = read_csv(args.events, REQUIRED_EVENT_COLUMNS)
    pilot = read_csv(args.orientation_pilot, REQUIRED_PILOT_COLUMNS)
    validate(preflight, events, pilot)
    result = summarize(preflight, events, pilot)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
