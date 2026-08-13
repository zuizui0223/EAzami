#!/usr/bin/env python3
"""Recover BioSample provenance for public nuclear augmentation candidates.

Run-level SRA taxonomy is not sufficient for phylogenetic admission. This step
checks each queued biological sample against its public BioSample record and
freezes taxonomic/provenance attributes before any candidate can be promoted.
Non-exact Cirsium names are retained for manual review rather than silently
synonymised or collapsed.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
from collections import Counter
from pathlib import Path
from typing import Mapping, Sequence

import recover_ncbi_project_runs as ncbi


def clean(value: object) -> str:
    return str(value or "").strip()


def canon(value: object) -> str:
    return " ".join(clean(value).casefold().replace("_", " ").split())


def keynorm(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "_", clean(value).casefold()).strip("_")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [
            {key: clean(value) for key, value in row.items()}
            for row in csv.DictReader(handle)
            if any(clean(value) for value in row.values())
        ]


def normalized_record(record: Mapping[str, str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for key, value in record.items():
        norm = keynorm(key)
        text = clean(value)
        if norm and text and norm not in out:
            out[norm] = text
    return out


def first(record: Mapping[str, str], *keys: str) -> str:
    normalized = normalized_record(record)
    for key in keys:
        value = normalized.get(keynorm(key), "")
        if value:
            return value
    return ""


def provenance_rows(
    queue: Sequence[Mapping[str, str]],
    attributes: Mapping[str, Mapping[str, str]],
) -> tuple[list[dict[str, object]], dict[str, object]]:
    rows: list[dict[str, object]] = []
    for candidate in queue:
        biosample = clean(candidate.get("biosample"))
        queued_taxon = clean(candidate.get("scientific_name"))
        record = dict(attributes.get(biosample, {})) if biosample else {}
        organism = clean(record.get("biosample_organism")) or first(record, "organism", "scientific_name")
        exact = bool(organism and queued_taxon and canon(organism) == canon(queued_taxon))
        genus = bool(organism and canon(organism).startswith("cirsium ")) or canon(organism) == "cirsium"

        if not biosample:
            status = "missing_biosample_accession"
        elif not record:
            status = "biosample_record_not_recovered"
        elif not genus:
            status = "biosample_organism_conflict"
        elif exact:
            status = "exact_taxon_metadata_concordant"
        else:
            status = "cirsium_taxon_name_manual_review"

        specimen_voucher = first(
            record,
            "specimen_voucher",
            "voucher",
            "voucher_id",
            "specimen_id",
            "herbarium_voucher",
        )
        geo = first(record, "geo_loc_name", "geographic_location", "country", "location")
        lat_lon = first(record, "lat_lon", "latitude_and_longitude")
        collection_date = first(record, "collection_date", "date_collected")
        isolate = first(record, "isolate", "isolate_name", "sample_name")
        cultivar = first(record, "cultivar", "cultivar_name")
        tissue = first(record, "tissue", "tissue_type", "sample_material")
        collected_by = first(record, "collected_by", "collector")
        identified_by = first(record, "identified_by", "identifier")

        rows.append(
            {
                "candidate_id": clean(candidate.get("candidate_id")),
                "tip_id_if_admitted": clean(candidate.get("tip_id_if_admitted")),
                "biosample": biosample,
                "queue_scientific_name": queued_taxon,
                "biosample_organism": organism,
                "organism_exact_match": exact,
                "organism_cirsium_genus_concordant": genus,
                "specimen_voucher": specimen_voucher,
                "geo_loc_name": geo,
                "lat_lon": lat_lon,
                "collection_date": collection_date,
                "isolate_or_sample_name": isolate,
                "cultivar": cultivar,
                "tissue": tissue,
                "collected_by": collected_by,
                "identified_by": identified_by,
                "provenance_review_status": status,
                "biosample_attribute_count": len(record),
                "all_biosample_attributes_json": json.dumps(record, ensure_ascii=False, sort_keys=True),
                "automatic_tree_tip_promotion_allowed": False,
                "new_china_sampling_freeze_allowed": False,
            }
        )

    counts = Counter(str(row["provenance_review_status"]) for row in rows)
    summary: dict[str, object] = {
        "contract_version": "global_public_nuclear_candidate_biosample_provenance_v1",
        "queued_candidate_groups": len(queue),
        "biosample_records_recovered": sum(bool(attributes.get(clean(row.get("biosample")), {})) for row in queue),
        "provenance_review_status_counts": dict(sorted(counts.items())),
        "exact_taxon_metadata_concordant": counts.get("exact_taxon_metadata_concordant", 0),
        "cirsium_taxon_name_manual_review": counts.get("cirsium_taxon_name_manual_review", 0),
        "biosample_organism_conflicts": counts.get("biosample_organism_conflict", 0),
        "biosample_records_not_recovered": counts.get("biosample_record_not_recovered", 0),
        "automatic_tree_tip_promotion_allowed": False,
        "primary_294_panel_changed": False,
        "new_china_sampling_freeze_allowed": False,
        "promotion_rule": (
            "Locus recovery alone is insufficient. A candidate with BioSample organism conflict or unrecovered BioSample provenance cannot be promoted; "
            "Cirsium genus-concordant but non-exact names require explicit taxonomic review without silent synonym resolution."
        ),
    }
    return rows, summary


def write_csv(path: Path, rows: Sequence[Mapping[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--email", default=os.getenv("NCBI_EMAIL", ""))
    parser.add_argument("--api-key", default=os.getenv("NCBI_API_KEY"))
    args = parser.parse_args()

    queue = read_csv(args.queue)
    biosamples = [clean(row.get("biosample")) for row in queue if clean(row.get("biosample"))]
    client = ncbi.NCBIClient(ncbi.ClientConfig(email=args.email, api_key=args.api_key))
    attributes = ncbi.biosample_attributes(client, biosamples)
    rows, summary = provenance_rows(queue, attributes)

    args.outdir.mkdir(parents=True, exist_ok=True)
    write_csv(args.outdir / "global_public_nuclear_candidate_biosample_provenance.csv", rows)
    (args.outdir / "global_public_nuclear_candidate_biosample_provenance_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
