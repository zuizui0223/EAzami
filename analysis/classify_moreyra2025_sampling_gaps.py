#!/usr/bin/env python3
"""Translate the Moreyra 2025 evidence audit into sequencing decisions.

The score is a transparent project-priority index, not a biological parameter or
formal expected-information-gain estimate. Species placement and population
history are classified separately so that a taxon already present in a nuclear
backbone can still be a high-priority colour-morph sampling target.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Mapping, Sequence

DEFAULT_INPUT = Path(
    "data/evidence/moreyra2025_east_asia_focal_taxon_audit_2026-08-11.csv"
)
DEFAULT_OUTPUT = Path("sampling/SEQUENCING_PANEL_V0_3_MOREYRA_AUDIT.csv")

OUTPUT_FIELDS = (
    "accepted_taxon",
    "focal_region",
    "input_priority_class",
    "combined_evidence_state",
    "species_backbone_class",
    "population_history_class",
    "recommended_data",
    "mandatory_prerequisite",
    "decision_score",
    "decision_rationale",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return [
            {key: (value or "").strip() for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


def has_supplement(row: Mapping[str, str]) -> bool:
    return row.get("supplement_match_status") == "matched"


def has_ncbi(row: Mapping[str, str]) -> bool:
    return row.get("ncbi_match_status") == "matched"


def priority_base(value: str) -> float:
    if value.startswith("A_population_colour") or value.startswith("A_transition"):
        return 10.0
    if value.startswith("A2_population_bridge"):
        return 8.5
    if value.startswith("A2_white_form_screen") or value.startswith("A2_transition_gap"):
        return 8.0
    if value.startswith("A_screen"):
        return 7.0
    if value.startswith("B_coloured_control"):
        return 5.0
    if value.startswith("B_backbone") or value.startswith("B_nipponocirsium"):
        return 4.5
    if value.startswith("B_reticulation_reference"):
        return 4.0
    return 3.5


def classify(row: Mapping[str, str]) -> dict[str, object]:
    priority = row["priority_class"]
    supp = has_supplement(row)
    ncbi = has_ncbi(row)
    transition = any(token in priority for token in ("population_colour", "transition"))
    bridge = "population_bridge" in priority
    white_screen = "white_form_screen" in priority

    if supp and ncbi:
        species = "modern_nuclear_sample_and_public_reads_verified"
    elif supp:
        species = "published_nuclear_sample_verified_public_reads_unmatched"
    elif ncbi:
        species = "public_project_sample_verified_supplement_tip_unmatched"
    else:
        species = "modern_nuclear_placement_not_recovered_after_current_audit"

    if transition and (supp or ncbi):
        population = "species_backbone_covered_population_colour_history_missing"
        recommended = "RAD-seq_or_resequencing_plus_pigment_RNA_ploidy"
        prerequisite = "paired_morph_population_sampling_and_tip-level_colour_labels"
    elif bridge and (supp or ncbi):
        population = "species_backbone_partly_covered_transregional_population_history_missing"
        recommended = "RAD-seq_or_low-coverage_resequencing_across_bridge_populations"
        prerequisite = "taxonomy_ploidy_and_geographic_replication"
    elif white_screen:
        population = "historical_white_form_requires_extant_voucher_confirmation"
        recommended = (
            "verify_white_morph_then_Compositae1061_if_species_gap_else_population_resequencing"
        )
        prerequisite = "extant_natural_white_morph_or_voucher-backed_repeated_occurrence"
    elif not (supp or ncbi) and transition:
        population = "transition-critical_species_and_population_gap"
        recommended = "Compositae1061_target_capture_then_population_resequencing"
        prerequisite = "accepted-name_synonym_and_existing-dataset_exhaustion"
    elif not (supp or ncbi):
        population = "species_backbone_gap_low_or_medium_colour_information"
        recommended = "Compositae1061_only_if_transition-adjacent_or_backbone-critical"
        prerequisite = "confirm_true_nuclear_gap_and_transition_information_gain"
    else:
        population = "species_context_available_no_immediate_colour_population_target"
        recommended = "reuse_existing_backbone_as_control"
        prerequisite = "none_beyond_tip_and_colour_provenance"

    score = priority_base(priority)
    if transition:
        score += 2.0
    if bridge:
        score += 1.0
    if supp or ncbi:
        # Existing placement increases immediate population-analysis feasibility.
        score += 1.0
    if supp and ncbi:
        score += 0.5
    if white_screen and not (supp or ncbi):
        score -= 0.5

    if transition and (supp or ncbi):
        rationale = (
            "Species-level evidence is already recoverable, so the remaining information gain "
            "comes from morph-linked population ancestry and molecular mechanism rather than another placement-only sample."
        )
    elif not (supp or ncbi):
        rationale = (
            "No accepted/alias match was recovered from the current supplement/SRA audit; target capture "
            "is considered only after synonym, unsequenced-tip and alternative-dataset checks."
        )
    else:
        rationale = (
            "Existing nuclear context can be reused; sequencing is promoted only when population, "
            "bridge or replicated-mechanism information is needed."
        )

    return {
        "accepted_taxon": row["accepted_taxon"],
        "focal_region": row["focal_region"],
        "input_priority_class": priority,
        "combined_evidence_state": row["combined_evidence_state"],
        "species_backbone_class": species,
        "population_history_class": population,
        "recommended_data": recommended,
        "mandatory_prerequisite": prerequisite,
        "decision_score": f"{score:.1f}",
        "decision_rationale": rationale,
    }


def rank(rows: Sequence[Mapping[str, str]]) -> list[dict[str, object]]:
    output = [classify(row) for row in rows]
    return sorted(
        output,
        key=lambda row: (-float(row["decision_score"]), str(row["accepted_taxon"]).casefold()),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = read_csv(args.input)
    if not rows:
        raise SystemExit(f"No audit rows in {args.input}")
    ranked = rank(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(OUTPUT_FIELDS))
        writer.writeheader()
        writer.writerows(ranked)
    print(f"ranked_taxa={len(ranked)}")
    for row in ranked[:15]:
        print(
            f"{row['decision_score']} {row['accepted_taxon']} :: "
            f"{row['recommended_data']}"
        )
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
