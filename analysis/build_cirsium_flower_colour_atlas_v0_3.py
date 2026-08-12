#!/usr/bin/env python3
"""Expand the frozen flower-colour atlas v0.2 with additional nuclear-mapped,
source-backed East Asian Cirsium taxa.

v0.3 has one specific engineering goal: satisfy the breadth/coloured/context
parts of the transition-rate readiness gate without manufacturing white tips.
After this expansion, the only intended blocker is the number of independent
fixed-white, nuclear-mapped taxa.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Iterable, Mapping

import validate_colour_atlas as validator

DEFAULT_BASE = Path("data/evidence/cirsium_flower_colour_atlas_v0_2.csv")
DEFAULT_EXPANSION = Path("data/evidence/cirsium_flower_colour_atlas_v0_3_expansion_evidence.csv")
DEFAULT_OUTPUT = Path("data/evidence/cirsium_flower_colour_atlas_v0_3.csv")
DEFAULT_SUMMARY = Path("analysis/cirsium_flower_colour_atlas_v0_3_readiness.json")

CONTEXTS = {
    "Cirsium suffultum": "Nipponocirsium",
    "Cirsium nipponicum var. incomptum": "Nipponocirsium",
    "Cirsium kujuense": "Nipponocirsium",
    "Cirsium japonicum var. japonicum": "Sinocirsium",
    "Cirsium fanjingshanense": "Moreyra2025_China",
    "Cirsium kamtschaticum": "Moreyra2025_NEAsia",
    "Cirsium amplexifolium": "Moreyra2025_Japan38",
}


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


def build_expansion_rows(
    fieldnames: list[str], evidence_rows: list[Mapping[str, str]]
) -> list[dict[str, str]]:
    if len(evidence_rows) != 7:
        raise ValueError(f"Expected seven v0.3 expansion records, observed {len(evidence_rows)}")
    observed_taxa = {clean(row.get("accepted_taxon")) for row in evidence_rows}
    if observed_taxa != set(CONTEXTS):
        raise ValueError(f"Unexpected v0.3 taxon set: {sorted(observed_taxa)}")

    output: list[dict[str, str]] = []
    for index, item in enumerate(evidence_rows, start=1):
        taxon = clean(item.get("accepted_taxon"))
        binary = clean(item.get("binary_colour_code")).upper()
        fine = clean(item.get("fine_colour_state"))
        declared = clean(item.get("rate_fit_eligible")).lower()
        if binary not in {"C", "P"}:
            raise ValueError(f"v0.3 expansion permits only C or P, got {binary} for {taxon}")
        if validator.EXPECTED_BINARY.get(fine) != binary:
            raise ValueError(f"Fine/binary mismatch for {taxon}: {fine}/{binary}")
        if binary == "C" and declared != "yes":
            raise ValueError(f"Fixed coloured nuclear-mapped taxon must be eligible: {taxon}")
        if binary == "P" and declared != "no":
            raise ValueError(f"Polymorphic taxon cannot be eligible: {taxon}")
        if not clean(item.get("colour_source_url")) or not clean(item.get("colour_source_locator")):
            raise ValueError(f"Missing direct colour provenance for {taxon}")
        if not clean(item.get("nuclear_tip_status")):
            raise ValueError(f"Missing nuclear-tip status for {taxon}")

        source_name = clean(item.get("colour_evidence_source"))
        evidence_status = (
            "official_database_text_direct"
            if "National Museum of Nature and Science" in source_name
            else "direct_taxon_text"
        )

        row = blank_row(fieldnames)
        row.update(
            {
                "record_id": f"ATL-V03-{index:02d}",
                "accepted_taxon": taxon,
                "source_taxon_name": taxon,
                "country": (
                    "Japan" if taxon in {"Cirsium suffultum", "Cirsium nipponicum var. incomptum", "Cirsium kujuense", "Cirsium japonicum var. japonicum", "Cirsium amplexifolium"}
                    else "China" if taxon == "Cirsium fanjingshanense"
                    else "Russia/Japan"
                ),
                "observation_unit": "taxon",
                "observation_id": taxon,
                "evidence_type": "source_backed_colour_plus_nuclear_tip_mapping",
                "evidence_source": source_name,
                "evidence_id": "|".join(
                    value
                    for value in (
                        clean(item.get("record_id")),
                        clean(item.get("nuclear_tip_identifier")),
                        clean(item.get("biosample")),
                        clean(item.get("run")),
                    )
                    if value
                ),
                "source_url": clean(item.get("colour_source_url")),
                "source_locator": clean(item.get("colour_source_locator")),
                "life_stage": "flower",
                "assessable": "yes",
                "colour_state": fine,
                "binary_colour_code": binary,
                "binary_collapse_rule": (
                    "source text purple/pale-purple/bluish-purple->C; documented white-flowered infraspecific form->P"
                ),
                "anthocyanin_visible": "yes" if binary == "C" else "unknown",
                "polymorphic_context": clean(item.get("notes")) if binary == "P" else "",
                "phylogeny_context": CONTEXTS[taxon],
                "phylogeny_tip_candidate": "yes",
                "rate_fit_eligible": declared,
                "rate_fit_exclusion_reason": (
                    "documented white-flowered infraspecific form; existing nuclear tip is not morph-linked, so taxon remains P"
                    if binary == "P"
                    else ""
                ),
                "evidence_status": evidence_status,
                "notes": (
                    f"Nuclear evidence: {clean(item.get('nuclear_evidence_source'))}; "
                    f"tip={clean(item.get('nuclear_tip_identifier'))}; "
                    f"BioSample={clean(item.get('biosample'))}; run={clean(item.get('run'))}. "
                    f"{clean(item.get('notes'))}"
                ).strip(),
                "review_status": "reviewed",
            }
        )
        output.append(row)
    return output


def build(
    base_path: Path, expansion_path: Path
) -> tuple[list[str], list[dict[str, str]], dict[str, object]]:
    fieldnames, base_rows = read_csv(base_path)
    validator.validate_rows(fieldnames, base_rows)
    _, evidence_rows = read_csv(expansion_path)
    new_rows = build_expansion_rows(fieldnames, evidence_rows)

    base_taxa = {row["accepted_taxon"] for row in base_rows if row["observation_unit"] == "taxon"}
    overlap = base_taxa & {row["accepted_taxon"] for row in new_rows}
    if overlap:
        raise ValueError(f"v0.3 would duplicate taxon-level rows: {sorted(overlap)}")

    rows = base_rows + new_rows
    validator.validate_rows(fieldnames, rows)
    summary = validator.readiness_summary(rows)
    summary["contract_version"] = "cirsium_flower_colour_atlas_v0_3"
    summary["base_atlas"] = str(base_path)
    summary["expansion_evidence"] = str(expansion_path)
    summary["intended_gate_state"] = "all conservative engineering conditions except minimum_white_tips"
    summary["claim_limit"] = (
        "v0.3 deliberately broadens nuclear-mapped coloured coverage and preserves polymorphic taxa. "
        "It must not trigger asymmetric transition-rate fitting while fixed-white coverage remains below the predeclared gate."
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
    parser.add_argument("--expansion", type=Path, default=DEFAULT_EXPANSION)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    fieldnames, rows, summary = build(args.base, args.expansion)
    write_csv(args.output, fieldnames, rows)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"atlas_records={summary['record_count']}")
    print(f"eligible_taxa={summary['rate_fit_eligible_unique_taxa']}")
    print(f"eligible_states={summary['rate_fit_eligible_state_counts']}")
    print(f"blockers={'|'.join(summary['readiness_blockers'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
