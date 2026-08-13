#!/usr/bin/env python3
"""Integrate modern nuclear coverage for the EAzami focal taxon table.

The builder joins the hypothesis-driven regional master table to three independently
curated evidence layers:

* Moreyra et al. 2025 Supplementary Table S1 + PRJNA957074 reconciliation;
* Chang et al. 2025 Nipponocirsium transcriptome/voucher audit;
* Chang et al. 2026 Sinocirsium/Arenicola transcriptome/voucher audit.

It deliberately distinguishes species-level placement from population/morph history.
A species with a verified nuclear tip can still be a high-priority RAD/resequencing
target when the white/coloured populations were not represented.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping, Sequence

DEFAULT_MASTER = Path("data/regional_master_taxa_seed.csv")
DEFAULT_MOREYRA = Path("data/evidence/prjna957074_focal_tip_recovery_2026-08-10.csv")
DEFAULT_CHANG_2025 = Path(
    "data/evidence/chang2025_nipponocirsium_accession_audit_2026-08-10.csv"
)
DEFAULT_CHANG_2026 = Path(
    "data/evidence/chang2026_east_asia_accession_audit_2026-08-10.csv"
)
DEFAULT_OUTPUT = Path("data/evidence/generated/east_asia_nuclear_coverage_current.csv")
DEFAULT_SUMMARY = Path("data/evidence/generated/east_asia_nuclear_coverage_summary.json")

OUTPUT_FIELDS = (
    "accepted_taxon",
    "region",
    "subsection_or_group",
    "flower_colour_state",
    "ploidy_or_chromosome",
    "transition_role",
    "radseq_priority",
    "moreyra_tip_status",
    "moreyra_tree_codes",
    "moreyra_biosamples",
    "moreyra_runs",
    "chang2025_sample_count",
    "chang2025_bioprojects",
    "chang2026_sample_count",
    "chang2026_bioprojects",
    "chang2026_morph_resolution",
    "modern_nuclear_evidence_sources",
    "best_species_level_nuclear_status",
    "species_backbone_gap_class",
    "population_or_morph_gap_class",
    "recommended_next_data",
    "evidence_note",
)

MOREYRA_EXACT = "exact_sra_project_tip_verified"


def clean(value: object) -> str:
    return str(value or "").strip()


def canonical_taxon(value: str) -> str:
    value = re.sub(r"\s+", " ", clean(value).replace("_", " ")).strip()
    if value.startswith("C. "):
        value = "Cirsium " + value[3:]
    return value.casefold()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return [
            {key: clean(value) for key, value in row.items()}
            for row in reader
            if any(clean(value) for value in row.values())
        ]


def require_fields(rows: Sequence[Mapping[str, str]], fields: Sequence[str], path: Path) -> None:
    if not rows:
        raise ValueError(f"{path}: no data rows")
    missing = set(fields) - set(rows[0])
    if missing:
        raise ValueError(f"{path}: missing required columns {sorted(missing)}")


def unique_join(values: Iterable[str]) -> str:
    return "|".join(sorted({clean(value) for value in values if clean(value)}))


def index_single(rows: Sequence[Mapping[str, str]], field: str, source: Path) -> dict[str, Mapping[str, str]]:
    output: dict[str, Mapping[str, str]] = {}
    for row in rows:
        key = canonical_taxon(row.get(field, ""))
        if not key:
            continue
        if key in output:
            raise ValueError(f"{source}: duplicate taxon key {row.get(field)!r}")
        output[key] = row
    return output


def index_many(rows: Sequence[Mapping[str, str]], field: str) -> dict[str, list[Mapping[str, str]]]:
    output: dict[str, list[Mapping[str, str]]] = defaultdict(list)
    for row in rows:
        key = canonical_taxon(row.get(field, ""))
        if key:
            output[key].append(row)
    return dict(output)


def population_target(master: Mapping[str, str]) -> bool:
    priority = clean(master.get("radseq_priority")).upper()
    role = clean(master.get("transition_role")).casefold()
    role_tokens = (
        "white",
        "polymorphism",
        "coloured_sister",
        "bridge",
        "core_",
        "transition",
    )
    return priority == "A" or any(token in role for token in role_tokens)


def classify_row(
    master: Mapping[str, str],
    moreyra: Mapping[str, str] | None,
    chang2025: Sequence[Mapping[str, str]],
    chang2026: Sequence[Mapping[str, str]],
) -> dict[str, str]:
    moreyra = moreyra or {}
    moreyra_status = clean(moreyra.get("project_tip_status"))
    moreyra_exact = moreyra_status == MOREYRA_EXACT
    c25_count = len(chang2025)
    c26_count = len(chang2026)

    sources: list[str] = []
    if moreyra_exact:
        sources.append("Moreyra2025_PRJNA957074")
    if c25_count:
        sources.append("Chang2025_PRJNA1158676")
    if c26_count:
        sources.append("Chang2026_PRJNA1311153")

    if len(sources) >= 2:
        best_status = "multiple_modern_nuclear_sources"
    elif c25_count or c26_count:
        best_status = "phylotranscriptomic_local_backbone"
    elif moreyra_exact:
        best_status = "global_target_capture_tip_verified"
    else:
        master_status = clean(master.get("nuclear_phylogeny_status"))
        if any(token in master_status for token in ("resolved", "represented", "target_capture")):
            best_status = "published_nuclear_claim_not_accession_reconciled_here"
        else:
            best_status = "no_modern_nuclear_tip_in_integrated_sources"

    if sources:
        gap_class = "species_placement_resolved_in_modern_nuclear_data"
    elif best_status == "published_nuclear_claim_not_accession_reconciled_here":
        gap_class = "file_or_accession_recovery_pending"
    else:
        gap_class = "candidate_species_gap_pending_synonym_and_other_dataset_audit"

    is_population_target = population_target(master)
    if is_population_target:
        population_gap = "population_or_morph_history_missing"
    else:
        population_gap = "not_primary_population_target"

    morph_values = unique_join(row.get("sample_morph_resolution", "") for row in chang2026)
    morph_unresolved = "not identified" in morph_values.casefold()

    if sources and is_population_target and morph_unresolved:
        next_data = "recover_published_morph_identity_then_population_RAD_or_resequencing"
    elif sources and is_population_target:
        next_data = "population_RAD_or_resequencing_plus_ploidy"
    elif not sources and is_population_target:
        next_data = "verify_synonyms_then_Compositae1061_target_capture_then_population_genomics"
    elif sources:
        next_data = "reuse_existing_species_backbone_and_complete_trait_evidence"
    else:
        next_data = "verify_synonyms_and_transition_value_before_target_capture"

    notes: list[str] = []
    if moreyra_exact:
        notes.append("Moreyra Supplement S1 tip is linked to an exact PRJNA957074 scientific-name match")
    elif moreyra_status:
        notes.append(f"Moreyra audit: {moreyra_status}")
    if c25_count:
        notes.append(f"Chang 2025 has {c25_count} transcriptome sample(s)")
    if c26_count:
        notes.append(f"Chang 2026 has {c26_count} transcriptome sample(s)")
    if morph_unresolved:
        notes.append("published Chang 2026 samples are not assigned to white versus coloured morph")
    if not sources:
        notes.append("absence from these three sources is not proof of absence from all nuclear datasets")

    return {
        "accepted_taxon": clean(master.get("accepted_taxon")),
        "region": clean(master.get("region")),
        "subsection_or_group": clean(master.get("subsection_or_group")),
        "flower_colour_state": clean(master.get("flower_colour_state")),
        "ploidy_or_chromosome": clean(master.get("ploidy_or_chromosome")),
        "transition_role": clean(master.get("transition_role")),
        "radseq_priority": clean(master.get("radseq_priority")),
        "moreyra_tip_status": moreyra_status or "not_in_focal_moreyra_audit",
        "moreyra_tree_codes": clean(moreyra.get("supplement_tree_codes")),
        "moreyra_biosamples": clean(moreyra.get("biosamples")),
        "moreyra_runs": clean(moreyra.get("runs")),
        "chang2025_sample_count": str(c25_count),
        "chang2025_bioprojects": unique_join(row.get("bioproject", "") for row in chang2025),
        "chang2026_sample_count": str(c26_count),
        "chang2026_bioprojects": unique_join(row.get("bioproject", "") for row in chang2026),
        "chang2026_morph_resolution": morph_values,
        "modern_nuclear_evidence_sources": "|".join(sources),
        "best_species_level_nuclear_status": best_status,
        "species_backbone_gap_class": gap_class,
        "population_or_morph_gap_class": population_gap,
        "recommended_next_data": next_data,
        "evidence_note": "; ".join(notes),
    }


def build(
    master_rows: Sequence[Mapping[str, str]],
    moreyra_rows: Sequence[Mapping[str, str]],
    chang2025_rows: Sequence[Mapping[str, str]],
    chang2026_rows: Sequence[Mapping[str, str]],
) -> list[dict[str, str]]:
    master_index = index_single(master_rows, "accepted_taxon", DEFAULT_MASTER)
    moreyra_index = index_single(moreyra_rows, "query_taxon", DEFAULT_MOREYRA)
    c25_index = index_many(chang2025_rows, "taxon")
    c26_index = index_many(chang2026_rows, "taxon")

    output = []
    for key, master in master_index.items():
        output.append(
            classify_row(
                master,
                moreyra_index.get(key),
                c25_index.get(key, []),
                c26_index.get(key, []),
            )
        )
    return sorted(output, key=lambda row: (row["radseq_priority"], row["accepted_taxon"]))


def write_csv(path: Path, rows: Iterable[Mapping[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(OUTPUT_FIELDS), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def summary(rows: Sequence[Mapping[str, str]]) -> dict[str, object]:
    return {
        "taxa": len(rows),
        "best_species_level_nuclear_status": dict(
            Counter(row["best_species_level_nuclear_status"] for row in rows)
        ),
        "species_backbone_gap_class": dict(
            Counter(row["species_backbone_gap_class"] for row in rows)
        ),
        "recommended_next_data": dict(
            Counter(row["recommended_next_data"] for row in rows)
        ),
        "priority_A_taxa": [
            row["accepted_taxon"] for row in rows if row["radseq_priority"] == "A"
        ],
        "priority_A_species_gap_candidates": [
            row["accepted_taxon"]
            for row in rows
            if row["radseq_priority"] == "A"
            and row["species_backbone_gap_class"]
            == "candidate_species_gap_pending_synonym_and_other_dataset_audit"
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--master", type=Path, default=DEFAULT_MASTER)
    parser.add_argument("--moreyra", type=Path, default=DEFAULT_MOREYRA)
    parser.add_argument("--chang-2025", type=Path, default=DEFAULT_CHANG_2025)
    parser.add_argument("--chang-2026", type=Path, default=DEFAULT_CHANG_2026)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    master = read_csv(args.master)
    moreyra = read_csv(args.moreyra)
    c25 = read_csv(args.chang_2025)
    c26 = read_csv(args.chang_2026)
    require_fields(master, ("accepted_taxon", "radseq_priority"), args.master)
    require_fields(moreyra, ("query_taxon", "project_tip_status"), args.moreyra)
    require_fields(c25, ("taxon", "bioproject"), args.chang_2025)
    require_fields(c26, ("taxon", "bioproject", "sample_morph_resolution"), args.chang_2026)

    rows = build(master, moreyra, c25, c26)
    write_csv(args.output, rows)
    payload = summary(rows)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"taxa={payload['taxa']}")
    for key, value in sorted(payload["species_backbone_gap_class"].items()):
        print(f"gap_{key}={value}")
    print(f"priority_A_species_gap_candidates={len(payload['priority_A_species_gap_candidates'])}")
    print(args.output)
    print(args.summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
