#!/usr/bin/env python3
"""Expand the frozen v0.1 Cirsium flower-colour atlas with source-backed
Moreyra-2025 Japanese nuclear tips.

The v0.2 expansion joins two independent evidence layers:

* flower-colour text from the National Museum of Nature and Science Japan
  Cirsium database; and
* verified sample/tip membership in the Moreyra et al. 2025 nuclear dataset.

Fixed C/W taxa can therefore become rate-fit candidates. Taxa with documented
white/coloured polymorphism remain P even when a nuclear tip exists, because the
sequenced individual is not morph-linked.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Iterable, Mapping

import validate_colour_atlas as validator

DEFAULT_BASE = Path("data/evidence/cirsium_flower_colour_atlas_v0_1.csv")
DEFAULT_MOREYRA = Path("data/evidence/moreyra2025_japan_colour_text_evidence_v1.csv")
DEFAULT_OUTPUT = Path("data/evidence/cirsium_flower_colour_atlas_v0_2.csv")
DEFAULT_SUMMARY = Path("analysis/cirsium_flower_colour_atlas_v0_2_readiness.json")


def clean(value: object) -> str:
    return str(value or "").strip()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"Missing header: {path}")
        rows = [
            {key: clean(value) for key, value in row.items()}
            for row in reader
            if any(clean(value) for value in row.values())
        ]
        return list(reader.fieldnames), rows


def blank_row(fieldnames: Iterable[str]) -> dict[str, str]:
    return {field: "" for field in fieldnames}


def build_moreyra_rows(
    fieldnames: list[str], evidence_rows: list[Mapping[str, str]]
) -> list[dict[str, str]]:
    if len(evidence_rows) != 8:
        raise ValueError(
            f"Expected eight reviewed Moreyra-Japan colour records, observed {len(evidence_rows)}"
        )
    ids = [clean(row.get("record_id")) for row in evidence_rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Moreyra-Japan colour evidence record IDs are not unique")

    output: list[dict[str, str]] = []
    for index, item in enumerate(evidence_rows, start=1):
        taxon = clean(item.get("accepted_taxon"))
        binary = clean(item.get("binary_colour_code")).upper()
        fine = clean(item.get("fine_colour_state"))
        declared_eligible = clean(item.get("rate_fit_eligible")).lower()
        if binary not in {"C", "P"}:
            raise ValueError(f"Unexpected v0.2 Moreyra-Japan binary code for {taxon}: {binary}")
        if validator.EXPECTED_BINARY.get(fine) != binary:
            raise ValueError(f"Fine/binary mismatch for {taxon}: {fine}/{binary}")
        if declared_eligible not in {"yes", "no"}:
            raise ValueError(f"Invalid rate_fit_eligible for {taxon}: {declared_eligible}")
        if binary == "P" and declared_eligible != "no":
            raise ValueError(f"Polymorphic taxon cannot be rate-fit eligible: {taxon}")
        if binary == "C" and declared_eligible != "yes":
            raise ValueError(f"Fixed coloured mapped tip should be declared eligible: {taxon}")
        if clean(item.get("nuclear_tip_status")) != "moreyra_sample_membership_verified":
            raise ValueError(f"Unverified Moreyra tip mapping for {taxon}")

        row = blank_row(fieldnames)
        row.update(
            {
                "record_id": f"ATL-MJ{index:02d}",
                "accepted_taxon": taxon,
                "source_taxon_name": taxon,
                "country": "Japan",
                "observation_unit": "taxon",
                "observation_id": taxon,
                "evidence_type": "official_species_database_plus_nuclear_tip_mapping",
                "evidence_source": "National Museum of Nature and Science Japan Cirsium database + Moreyra et al. 2025",
                "evidence_id": "|".join(
                    part
                    for part in (
                        clean(item.get("record_id")),
                        clean(item.get("moreyra_japan_member_id")),
                        clean(item.get("biosample")),
                        clean(item.get("run")),
                    )
                    if part
                ),
                "source_url": clean(item.get("colour_source_url")),
                "source_locator": clean(item.get("colour_source_locator")),
                "life_stage": "flower",
                "assessable": "yes",
                "colour_state": fine,
                "binary_colour_code": binary,
                "binary_collapse_rule": (
                    "official text reddish/pale-reddish purple->C; explicitly documented white/coloured form polymorphism->P"
                ),
                "anthocyanin_visible": "yes" if binary == "C" else "unknown",
                "polymorphic_context": (
                    clean(item.get("notes")) if binary == "P" else ""
                ),
                "phylogeny_context": "Moreyra2025_Japan38",
                "phylogeny_tip_candidate": "yes",
                "rate_fit_eligible": declared_eligible,
                "rate_fit_exclusion_reason": (
                    "documented white/coloured polymorphism but Moreyra nuclear tip is not morph-linked; retain P"
                    if binary == "P"
                    else ""
                ),
                "evidence_status": "official_database_text_direct",
                "notes": (
                    f"Moreyra mapping: {clean(item.get('moreyra_japan_member_id'))}; "
                    f"tree={clean(item.get('moreyra_tree_code'))}; "
                    f"BioSample={clean(item.get('biosample'))}; run={clean(item.get('run'))}. "
                    f"{clean(item.get('notes'))}"
                ).strip(),
                "review_status": "reviewed",
            }
        )
        output.append(row)
    return output


def build(
    base_path: Path, moreyra_path: Path
) -> tuple[list[str], list[dict[str, str]], dict[str, object]]:
    fieldnames, base_rows = read_csv(base_path)
    validator.validate_rows(fieldnames, base_rows)
    _, evidence_rows = read_csv(moreyra_path)
    new_rows = build_moreyra_rows(fieldnames, evidence_rows)

    superseded_taxa = {
        row["accepted_taxon"]
        for row in new_rows
        if any(
            old.get("accepted_taxon") == row["accepted_taxon"]
            and old.get("evidence_status") == "official_database_seed_pending_exact_provenance"
            for old in base_rows
        )
    }
    retained = [
        row
        for row in base_rows
        if not (
            row.get("accepted_taxon") in superseded_taxa
            and row.get("evidence_status") == "official_database_seed_pending_exact_provenance"
        )
    ]
    rows = retained + new_rows
    validator.validate_rows(fieldnames, rows)
    summary = validator.readiness_summary(rows)
    summary["contract_version"] = "cirsium_flower_colour_atlas_v0_2"
    summary["base_atlas"] = str(base_path)
    summary["expansion_evidence"] = str(moreyra_path)
    summary["superseded_pending_taxa"] = sorted(superseded_taxa)
    summary["claim_limit"] = (
        "v0.2 expands directly source-backed, nuclear-tip-mapped records but remains below the project gate for "
        "transition-rate fitting. Polymorphic Japanese taxa are retained as P and are not converted into fixed W/C tips."
    )
    return fieldnames, rows, summary


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[Mapping[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--moreyra-japan", type=Path, default=DEFAULT_MOREYRA)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    fieldnames, rows, summary = build(args.base, args.moreyra_japan)
    write_csv(args.output, fieldnames, rows)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"atlas_records={summary['record_count']}")
    print(f"reviewed_records={summary['reviewed_record_count']}")
    print(f"rate_fit_eligible_taxa={summary['rate_fit_eligible_unique_taxa']}")
    print(f"eligible_state_counts={summary['rate_fit_eligible_state_counts']}")
    print(f"blockers={'|'.join(summary['readiness_blockers'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
