#!/usr/bin/env python3
"""Build the standalone EAzami continuous-trait registry from direct sources.

Only EAzami-curated direct literature, flora and taxonomic-authority seeds are
admitted. Source-reported ranges are preserved verbatim and remain context-only;
they are never converted to midpoints. No Azami phenotype value or result is read.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

REQUIRED_OUTPUT_FIELDS = (
    "record_id",
    "paper_japan_member_id",
    "taxon_concept",
    "trait_id",
    "value",
    "unit",
    "source_type",
    "source_locator",
    "rights_status",
    "measurement_protocol",
    "admission_status",
    "exclusion_reason",
)
OUTPUT_FIELDS = REQUIRED_OUTPUT_FIELDS + (
    "tip_id",
    "region",
    "source_name",
    "source_evidence_note",
    "claim_boundary",
)

DISPLAY_FIELDS = (
    "taxon",
    "region",
    "trait_component",
    "size_metric",
    "length_cm",
    "width_cm",
    "diameter_cm",
    "arrangement",
    "orientation",
    "source",
    "evidence_note",
    "claim_boundary",
)
PHYLLARY_FIELDS = (
    "taxon",
    "region",
    "phyllary_length_cm",
    "phyllary_protrusion_mm",
    "inner_outer_length_ratio",
    "phyllary_number",
    "involucre_shape",
    "source",
    "evidence_note",
    "claim_boundary",
)

STATIC_SOURCES = {
    "Chang et al. 2026 comparative morphology": (
        "primary_comparative_morphology",
        "https://doi.org/10.1186/s12870-026-08097-6",
        "open_access_article_numeric_fact_citation_required",
    ),
    "Tseng et al. 2025 comparative morphology": (
        "primary_comparative_morphology",
        "https://doi.org/10.1186/s40529-025-00454-2",
        "open_access_article_numeric_fact_citation_required",
    ),
    "Chang and Tseng 2019 taxon treatment": (
        "primary_taxonomic_treatment",
        "https://www.researchgate.net/publication/335202385_Cirsium_japonicum_DC_var_fukienense_Kitam_Compositae_a_newly_recorded_taxon_of_Taiwan_and_its_western_outlying_islands",
        "citation_only_no_media_ingested",
    ),
    "Flora of Taiwan 2nd ed.": (
        "digital_flora",
        "https://www.efloras.org/florataxon.aspx?flora_id=100&taxon_id=242313149",
        "public_web_flora_numeric_fact_citation_required",
    ),
}


def read_csv(path: Path, expected_fields: tuple[str, ...] | None = None) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        observed = tuple(reader.fieldnames or ())
        if expected_fields is not None and observed != expected_fields:
            raise ValueError(f"{path}: expected header {expected_fields}, observed {observed}")
        return [
            {key: (value or "").strip() for key, value in row.items()}
            for row in reader
            if any((value or "").strip() for value in row.values())
        ]


def is_scalar(value: str) -> bool:
    if not value or "-" in value:
        return False
    try:
        float(value)
    except ValueError:
        return False
    return True


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.casefold()).strip("_")


def membership_map(path: Path) -> dict[str, str]:
    rows = read_csv(path)
    mapping: dict[str, str] = {}
    for row in rows:
        for name in row["tree_codes"].split("|"):
            normalized = name.strip()
            if not normalized:
                continue
            previous = mapping.get(normalized)
            if previous and previous != row["paper_japan_member_id"]:
                raise ValueError(f"duplicate Japan38 taxon mapping for {normalized}")
            mapping[normalized] = row["paper_japan_member_id"]
    return mapping


def tip_and_locator_maps(orientation_path: Path, nmns_path: Path) -> tuple[dict[str, str], dict[str, str]]:
    orientation = read_csv(orientation_path)
    tips: dict[str, str] = {}
    locators: dict[str, str] = {}
    for row in orientation:
        taxon = row["accepted_taxon"]
        tips[taxon] = row["tip_id"]
        locator = row["source_url"]
        if locator.startswith("http"):
            locators[taxon] = locator
    for row in read_csv(nmns_path):
        locator = row["source_url"]
        if locator.startswith("http"):
            locators[row["nmns_taxon_concept"]] = locator
    return tips, locators


def source_contract(source: str, taxon: str, nmns_locators: dict[str, str]) -> tuple[str, str, str]:
    if source == "NMNS Japanese Cirsium database":
        locator = nmns_locators.get(taxon, "")
        if not locator:
            raise ValueError(f"no exact NMNS locator for {taxon}")
        return (
            "national_museum_taxonomic_authority",
            locator,
            "public_web_authority_numeric_fact_citation_required",
        )
    if source not in STATIC_SOURCES:
        raise ValueError(f"unregistered direct source: {source}")
    return STATIC_SOURCES[source]


def make_record(
    *,
    taxon: str,
    region: str,
    trait_id: str,
    value: str,
    unit: str,
    source: str,
    evidence_note: str,
    claim_boundary: str,
    japan_map: dict[str, str],
    tip_map: dict[str, str],
    locator_map: dict[str, str],
) -> dict[str, str]:
    source_type, source_locator, rights_status = source_contract(source, taxon, locator_map)
    scalar = is_scalar(value)
    return {
        "record_id": f"NATIVE_{slug(taxon)}__{trait_id}",
        "paper_japan_member_id": japan_map.get(taxon, ""),
        "taxon_concept": taxon,
        "trait_id": trait_id,
        "value": value,
        "unit": unit,
        "source_type": source_type,
        "source_locator": source_locator,
        "rights_status": rights_status,
        "measurement_protocol": (
            "source_reported_direct_point_estimate_no_remeasurement"
            if scalar
            else "source_reported_range_preserved_verbatim_no_midpoint"
        ),
        "admission_status": "admitted_comparable_scalar" if scalar else "context_only_range_not_scalar",
        "exclusion_reason": "" if scalar else "range_not_collapsed_to_midpoint",
        "tip_id": tip_map.get(taxon, ""),
        "region": region,
        "source_name": source,
        "source_evidence_note": evidence_note,
        "claim_boundary": claim_boundary,
    }


def build_records(
    display_rows: list[dict[str, str]],
    phyllary_rows: list[dict[str, str]],
    japan_map: dict[str, str],
    tip_map: dict[str, str],
    locator_map: dict[str, str],
) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in display_rows:
        if row["trait_component"] != "display_size":
            raise ValueError(f"unexpected display trait component: {row}")
        metric = row["size_metric"]
        if metric == "measured_capitulum_length_width":
            traits = (
                ("measured_capitulum_length_cm", row["length_cm"], "cm"),
                ("measured_capitulum_width_cm", row["width_cm"], "cm"),
            )
        elif metric == "involucre_length_width":
            traits = (
                ("involucre_length_cm", row["length_cm"], "cm"),
                ("involucre_width_cm", row["width_cm"], "cm"),
            )
        elif metric == "involucre_live_diameter":
            traits = (("involucre_live_diameter_cm", row["diameter_cm"], "cm"),)
        else:
            raise ValueError(f"unregistered display metric: {metric}")
        for trait_id, value, unit in traits:
            if not value:
                raise ValueError(f"empty display value for {row['taxon']} {trait_id}")
            records.append(
                make_record(
                    taxon=row["taxon"],
                    region=row["region"],
                    trait_id=trait_id,
                    value=value,
                    unit=unit,
                    source=row["source"],
                    evidence_note=row["evidence_note"],
                    claim_boundary=row["claim_boundary"],
                    japan_map=japan_map,
                    tip_map=tip_map,
                    locator_map=locator_map,
                )
            )

    phyllary_traits = (
        ("phyllary_length_cm", "cm"),
        ("phyllary_protrusion_mm", "mm"),
        ("inner_outer_length_ratio", "ratio"),
        ("phyllary_number", "count"),
    )
    for row in phyllary_rows:
        for trait_id, unit in phyllary_traits:
            value = row[trait_id]
            if not value:
                continue
            records.append(
                make_record(
                    taxon=row["taxon"],
                    region=row["region"],
                    trait_id=trait_id,
                    value=value,
                    unit=unit,
                    source=row["source"],
                    evidence_note=row["evidence_note"],
                    claim_boundary=row["claim_boundary"],
                    japan_map=japan_map,
                    tip_map=tip_map,
                    locator_map=locator_map,
                )
            )

    records.sort(key=lambda row: (row["taxon_concept"], row["trait_id"]))
    ids = [row["record_id"] for row in records]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate native registry record_id")
    return records


def summarize(records: list[dict[str, str]], registry_sha256: str) -> dict:
    admitted = [row for row in records if row["admission_status"] == "admitted_comparable_scalar"]
    context = [row for row in records if row["admission_status"] == "context_only_range_not_scalar"]
    panels: dict[str, set[str]] = defaultdict(set)
    for row in admitted:
        panels[row["trait_id"]].add(row["taxon_concept"])
    panel_counts = {trait: len(taxa) for trait, taxa in sorted(panels.items())}
    seven_taxon_traits = sorted(trait for trait, count in panel_counts.items() if count == 7)
    japan_admitted = [row for row in admitted if row["paper_japan_member_id"]]
    source_counts = Counter(row["source_name"] for row in records)
    return {
        "contract_version": "chapter2_eazami_native_continuous_trait_registry_v1",
        "registry_sha256": registry_sha256,
        "source_seed_rows": {"display": 15, "phyllary": 7},
        "registry_records": len(records),
        "unique_taxa": len({row["taxon_concept"] for row in records}),
        "source_record_counts": dict(sorted(source_counts.items())),
        "admitted_comparable_scalar_records": len(admitted),
        "context_only_range_records": len(context),
        "comparable_scalar_panel_taxa": panel_counts,
        "seven_taxon_direct_panel_traits": seven_taxon_traits,
        "japan38_mapped_taxa": len({row["paper_japan_member_id"] for row in records if row["paper_japan_member_id"]}),
        "japan38_admitted_scalar_records": len(japan_admitted),
        "japan38_admitted_scalar_taxa": len({row["paper_japan_member_id"] for row in japan_admitted}),
        "registry_gate": "ADMITTED_EAZAMI_NATIVE_VALUES",
        "japan38_history_gate": "NOT_EVALUABLE_ZERO_ADMITTED_SCALAR_JAPAN38_TIPS",
        "east_asia_direct_panel_gate": "DIAGNOSTIC_READY_N7_SOURCE_AND_LINEAGE_CLUSTERED",
        "analysis_route": "Eligible for a predeclared four-trait seven-taxon direct continuous-history diagnostic across the six frozen AU-nonrejected topologies; retain source and lineage clustering as a claim ceiling.",
        "claim_boundary": "The registry proves independent source admission, not adequate Japan38 coverage. Ranges are not midpoints. The seven-taxon point-estimate panels are lineage- and source-clustered diagnostics, not evidence of adaptation, convergence, absolute rates or a general East-Asian process.",
    }


def write_registry(path: Path, records: list[dict[str, str]]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--display", type=Path, required=True)
    parser.add_argument("--phyllary", type=Path, required=True)
    parser.add_argument("--membership", type=Path, required=True)
    parser.add_argument("--orientation-crosswalk", type=Path, required=True)
    parser.add_argument("--nmns-seed", type=Path, required=True)
    parser.add_argument("--registry-output", type=Path, required=True)
    parser.add_argument("--summary-output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    display = read_csv(args.display, DISPLAY_FIELDS)
    phyllary = read_csv(args.phyllary, PHYLLARY_FIELDS)
    if len(display) != 15 or len(phyllary) != 7:
        raise ValueError(f"direct seed row drift: display={len(display)} phyllary={len(phyllary)}")
    japan = membership_map(args.membership)
    tips, locators = tip_and_locator_maps(args.orientation_crosswalk, args.nmns_seed)
    records = build_records(display, phyllary, japan, tips, locators)
    digest = write_registry(args.registry_output, records)
    summary = summarize(records, digest)
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
