#!/usr/bin/env python3
"""Reconcile Moreyra et al. (2025) Supplementary Table S1 with PRJNA957074.

The script joins the published tree code/species/voucher table to official NCBI
runinfo by BioSample accession. It intentionally preserves competing names rather
than silently choosing a synonym. Geographic scope is derived conservatively and
is used only to create an East/Northeast Asian audit subset.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping, Sequence

SUPPLEMENT_FIELDS = (
    "Tree code names",
    "Species",
    "Accession number",
    "Voucher and herbarium code",
)
RUNINFO_REQUIRED = (
    "Run",
    "Experiment",
    "BioProject",
    "BioSample",
    "ScientificName",
    "LibraryName",
)
OUTPUT_FIELDS = (
    "supplement_row_number",
    "tree_code",
    "published_species",
    "biosample",
    "voucher_and_herbarium",
    "sra_scientific_name",
    "library_name",
    "experiment",
    "run",
    "geographic_location",
    "collection_date",
    "latitude_longitude",
    "supplement_region_class",
    "sra_region_class",
    "region_class",
    "scope_class",
    "geographic_evidence_relation",
    "sra_link_status",
    "tree_code_vs_sra_name",
    "name_reconciliation_priority",
)
FOCAL_FIELDS = (
    "query_taxon",
    "project_tip_status",
    "n_supplement_rows",
    "n_sra_runs",
    "supplement_tree_codes",
    "published_species_names",
    "sra_scientific_names",
    "biosamples",
    "experiments",
    "runs",
    "interpretation",
)

FAR_EAST_TOKENS = (
    "primors", "sikhote", "sakhalin", "kamchat", "chukot", "khabarov",
    "amur", "vladivostok", "ussuri", "kuril", "magadan",
)
INNER_NE_ASIA_TOKENS = (
    "trans-baikal", "transbaikal", "zabaykal", "buryat", "tuva",
)
OUTSIDE_REGION_TOKENS = (
    "ukraine", "turkey", "united states", "u.s.a", "usa", "canada",
    "mexico", "spain", "france", "italy", "germany", "austria",
    "romania", "bulgaria", "georgia", "iran", "iraq", "pakistan",
    "afghanistan", "morocco", "ethiopia", "kenya", "tanzania",
)


def clean(value: object) -> str:
    return str(value or "").strip()


def compact(value: str) -> str:
    return re.sub(r"\s+", " ", clean(value).replace("_", " "))


def strip_tree_sample_suffix(value: str) -> str:
    value = compact(value)
    return re.sub(r"\s+\d+$", "", value)


def canonical_taxon(value: str) -> str:
    """Conservative name normalization; this does not resolve synonyms."""
    value = strip_tree_sample_suffix(value).casefold()
    value = re.sub(r"\s+\([^)]*\)$", "", value)
    value = re.sub(r"\s+sp\.\s+nova$", "", value)
    return re.sub(r"\s+", " ", value).strip()


def epithet_signature(value: str) -> str:
    parts = canonical_taxon(value).split()
    if len(parts) < 2:
        return ""
    retained = [parts[1]]
    for marker in ("subsp.", "var.", "f."):
        if marker in parts:
            index = parts.index(marker)
            if index + 1 < len(parts):
                retained.extend((marker, parts[index + 1]))
    return " ".join(retained)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return [
            {key: clean(value) for key, value in row.items()}
            for row in reader
            if any(clean(value) for value in row.values())
        ]


def validate_columns(rows: Sequence[Mapping[str, str]], required: Sequence[str], source: Path) -> None:
    if not rows:
        raise ValueError(f"{source}: no data rows")
    missing = set(required) - set(rows[0])
    if missing:
        raise ValueError(f"{source}: missing required columns {sorted(missing)}")


def classify_region_text(value: str) -> tuple[str, str]:
    text = value.casefold()
    if "japan" in text:
        return "Japan", "core_east_asia"
    if "china" in text:
        return "China", "core_east_asia"
    if "korea" in text:
        return "Korea", "core_east_asia"
    if "taiwan" in text:
        return "Taiwan", "core_east_asia"
    if "mongolia" in text:
        return "Mongolia", "northeast_asia_bridge"
    if any(token in text for token in FAR_EAST_TOKENS):
        return "Russian_Far_East", "northeast_asia_bridge"
    if any(token in text for token in INNER_NE_ASIA_TOKENS):
        return "Russian_Inner_NE_Asia", "northeast_asia_bridge"
    if "russia" in text or "caucasus" in text or "crimea" in text:
        return "Russia_other", "outside_scope"
    if any(token in text for token in OUTSIDE_REGION_TOKENS):
        return "Outside_target_region", "outside_scope"
    return "Other_or_unresolved", "outside_scope"


def combine_regions(geographic_location: str, voucher: str) -> tuple[str, str, str, str, str]:
    supplement_region, supplement_scope = classify_region_text(voucher)
    sra_region, sra_scope = classify_region_text(geographic_location)
    supplement_resolved = supplement_region != "Other_or_unresolved"
    sra_resolved = sra_region != "Other_or_unresolved"
    if supplement_resolved and sra_resolved and supplement_region == sra_region:
        return supplement_region, sra_region, supplement_region, supplement_scope, "concordant"
    if (
        supplement_region in {"Russian_Far_East", "Russian_Inner_NE_Asia"}
        and sra_region == "Russia_other"
    ):
        return (
            supplement_region,
            sra_region,
            supplement_region,
            supplement_scope,
            "supplement_refines_sra_russia",
        )
    if supplement_resolved and sra_resolved:
        if supplement_scope != "outside_scope" and sra_scope == "outside_scope":
            scope = "source_conflict_target_vs_outside"
        elif sra_scope != "outside_scope" and supplement_scope == "outside_scope":
            scope = "source_conflict_target_vs_outside"
        else:
            scope = supplement_scope if supplement_scope != "outside_scope" else sra_scope
        return (
            supplement_region,
            sra_region,
            f"{supplement_region}|{sra_region}",
            scope,
            "conflicting_resolved_regions",
        )
    if supplement_resolved:
        relation = (
            "supplement_only"
            if not geographic_location.strip()
            else "supplement_target_sra_other_or_unresolved"
        )
        return supplement_region, sra_region, supplement_region, supplement_scope, relation
    if sra_resolved:
        return supplement_region, sra_region, sra_region, sra_scope, "sra_only"
    return supplement_region, sra_region, "Other_or_unresolved", "outside_scope", "unresolved"


def name_relation(tree_code: str, sra_name: str) -> tuple[str, str]:
    if not sra_name:
        return "not_comparable_no_sra_name", "review_missing_accession_or_run"
    tree = canonical_taxon(tree_code)
    sra = canonical_taxon(sra_name)
    if tree == sra:
        return "exact", "low"
    if epithet_signature(tree_code) and epithet_signature(tree_code) == epithet_signature(sra_name):
        return "generic_reassignment_only", "medium"
    return "different_submitted_or_published_name", "high"


def reconcile_samples(
    supplement_rows: Sequence[Mapping[str, str]],
    runinfo_rows: Sequence[Mapping[str, str]],
) -> list[dict[str, str]]:
    by_biosample: dict[str, list[Mapping[str, str]]] = defaultdict(list)
    for row in runinfo_rows:
        biosample = clean(row.get("BioSample"))
        if biosample:
            by_biosample[biosample].append(row)

    output: list[dict[str, str]] = []
    for index, source in enumerate(supplement_rows, start=2):
        biosample = clean(source.get("Accession number"))
        matches = by_biosample.get(biosample, []) if biosample else []
        if not matches:
            matches = [{}]
        for run in matches:
            tree_code = clean(source.get("Tree code names"))
            sra_name = clean(run.get("ScientificName"))
            relation, priority = name_relation(tree_code, sra_name)
            supplement_region, sra_region, region, scope, geo_relation = combine_regions(
                clean(run.get("geographic_location")),
                clean(source.get("Voucher and herbarium code")),
            )
            if run:
                link_status = "linked_runinfo"
            elif biosample:
                link_status = "biosample_not_recovered_in_runinfo"
            else:
                link_status = "supplement_no_biosample"
            output.append(
                {
                    "supplement_row_number": str(index),
                    "tree_code": tree_code,
                    "published_species": clean(source.get("Species")),
                    "biosample": biosample,
                    "voucher_and_herbarium": compact(source.get("Voucher and herbarium code", "")),
                    "sra_scientific_name": sra_name,
                    "library_name": clean(run.get("LibraryName")),
                    "experiment": clean(run.get("Experiment")),
                    "run": clean(run.get("Run")),
                    "geographic_location": clean(run.get("geographic_location")),
                    "collection_date": clean(run.get("collection_date")),
                    "latitude_longitude": clean(run.get("latitude_longitude")),
                    "supplement_region_class": supplement_region,
                    "sra_region_class": sra_region,
                    "region_class": region,
                    "scope_class": scope,
                    "geographic_evidence_relation": geo_relation,
                    "sra_link_status": link_status,
                    "tree_code_vs_sra_name": relation,
                    "name_reconciliation_priority": priority,
                }
            )
    return output


def read_focal_taxa(path: Path | None) -> list[str]:
    if path is None or not path.exists():
        return []
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def focal_audit(
    focal_taxa: Sequence[str], reconciled: Sequence[Mapping[str, str]]
) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for query in focal_taxa:
        q = canonical_taxon(query)
        supplement_hits = [
            row
            for row in reconciled
            if canonical_taxon(row.get("tree_code", "")) == q
            or canonical_taxon(row.get("published_species", "")).startswith(q)
        ]
        sra_hits = [
            row
            for row in reconciled
            if canonical_taxon(row.get("sra_scientific_name", "")) == q
        ]
        runs = sorted({row.get("run", "") for row in sra_hits if row.get("run")})
        if runs:
            status = "exact_sra_project_tip_verified"
            interpretation = (
                "Exact scientific-name match is directly verified in PRJNA957074 "
                "runinfo and linked to Supplementary Table S1."
            )
        elif supplement_hits:
            linked = any(
                row.get("sra_link_status") == "linked_runinfo"
                for row in supplement_hits
            )
            if linked:
                status = "supplement_tree_tip_verified_runinfo_name_mismatch"
                interpretation = (
                    "The focal name is present in Supplementary Table S1, but NCBI "
                    "uses a different submitted scientific name; synonym/tree-code "
                    "reconciliation is required."
                )
            else:
                status = "supplement_tree_tip_verified_no_public_run"
                interpretation = (
                    "The focal name occurs in Supplementary Table S1 but no linked "
                    "public SRA run was recovered."
                )
        else:
            status = "not_recovered_in_supplement_or_exact_runinfo"
            interpretation = (
                "No exact accepted-name match was recovered from the supplement tree "
                "codes/published names or project runinfo; this is not proof of absence "
                "from all nuclear datasets."
            )
        source_rows = supplement_hits + [
            row for row in sra_hits if row not in supplement_hits
        ]
        output.append(
            {
                "query_taxon": query,
                "project_tip_status": status,
                "n_supplement_rows": str(
                    len({row.get("supplement_row_number") for row in supplement_hits})
                ),
                "n_sra_runs": str(len(runs)),
                "supplement_tree_codes": "|".join(
                    sorted(
                        {
                            row.get("tree_code", "")
                            for row in source_rows
                            if row.get("tree_code")
                        }
                    )
                ),
                "published_species_names": "|".join(
                    sorted(
                        {
                            row.get("published_species", "")
                            for row in source_rows
                            if row.get("published_species")
                        }
                    )
                ),
                "sra_scientific_names": "|".join(
                    sorted(
                        {
                            row.get("sra_scientific_name", "")
                            for row in source_rows
                            if row.get("sra_scientific_name")
                        }
                    )
                ),
                "biosamples": "|".join(
                    sorted(
                        {
                            row.get("biosample", "")
                            for row in source_rows
                            if row.get("biosample")
                        }
                    )
                ),
                "experiments": "|".join(
                    sorted(
                        {
                            row.get("experiment", "")
                            for row in source_rows
                            if row.get("experiment")
                        }
                    )
                ),
                "runs": "|".join(runs),
                "interpretation": interpretation,
            }
        )
    return output


def write_csv(
    path: Path, rows: Iterable[Mapping[str, str]], fields: Sequence[str]
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(fields), extrasaction="ignore"
        )
        writer.writeheader()
        writer.writerows(rows)


def build_summary(
    supplement_rows: Sequence[Mapping[str, str]],
    runinfo_rows: Sequence[Mapping[str, str]],
    reconciled: Sequence[Mapping[str, str]],
    focal_rows: Sequence[Mapping[str, str]],
) -> dict[str, object]:
    supplement_sample_ids = {row["supplement_row_number"] for row in reconciled}
    linked_sample_ids = {
        row["supplement_row_number"]
        for row in reconciled
        if row["sra_link_status"] == "linked_runinfo"
    }
    exact_focal = [
        row
        for row in focal_rows
        if row["project_tip_status"] == "exact_sra_project_tip_verified"
    ]
    return {
        "supplement_sample_rows": len(supplement_rows),
        "supplement_cirsium_rows": sum(
            clean(row.get("Tree code names")).startswith("Cirsium")
            for row in supplement_rows
        ),
        "project_runinfo_rows": len(runinfo_rows),
        "project_unique_scientific_names": len(
            {
                clean(row.get("ScientificName"))
                for row in runinfo_rows
                if clean(row.get("ScientificName"))
            }
        ),
        "joined_output_rows": len(reconciled),
        "supplement_samples_with_runinfo": len(linked_sample_ids),
        "supplement_samples_without_runinfo": len(
            supplement_sample_ids - linked_sample_ids
        ),
        "core_east_asia_sample_rows": len(
            {
                row["supplement_row_number"]
                for row in reconciled
                if row["scope_class"] == "core_east_asia"
            }
        ),
        "northeast_asia_bridge_sample_rows": len(
            {
                row["supplement_row_number"]
                for row in reconciled
                if row["scope_class"] == "northeast_asia_bridge"
            }
        ),
        "region_counts_by_joined_row": dict(
            sorted(Counter(row["region_class"] for row in reconciled).items())
        ),
        "name_relation_counts_by_joined_row": dict(
            sorted(
                Counter(
                    row["tree_code_vs_sra_name"] for row in reconciled
                ).items()
            )
        ),
        "focal_taxa": len(focal_rows),
        "exact_focal_matches": len(exact_focal),
        "exact_focal_taxa": [row["query_taxon"] for row in exact_focal],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--supplement-table", type=Path, required=True)
    parser.add_argument("--runinfo", type=Path, required=True)
    parser.add_argument("--focal-taxa", type=Path)
    parser.add_argument("--outdir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    supplement = read_csv(args.supplement_table)
    runinfo = read_csv(args.runinfo)
    validate_columns(supplement, SUPPLEMENT_FIELDS, args.supplement_table)
    validate_columns(runinfo, RUNINFO_REQUIRED, args.runinfo)

    reconciled = reconcile_samples(supplement, runinfo)
    east_ne_asia = [
        row for row in reconciled if row["scope_class"] != "outside_scope"
    ]
    discrepancies = [
        row
        for row in reconciled
        if row["tree_code_vs_sra_name"]
        not in {"exact", "not_comparable_no_sra_name"}
    ]
    unlinked = [
        row for row in reconciled if row["sra_link_status"] != "linked_runinfo"
    ]
    focal = focal_audit(read_focal_taxa(args.focal_taxa), reconciled)
    summary = build_summary(supplement, runinfo, reconciled, focal)

    args.outdir.mkdir(parents=True, exist_ok=True)
    write_csv(
        args.outdir / "moreyra2025_all_sample_reconciliation.csv",
        reconciled,
        OUTPUT_FIELDS,
    )
    write_csv(
        args.outdir / "moreyra2025_east_ne_asia_sample_audit.csv",
        east_ne_asia,
        OUTPUT_FIELDS,
    )
    write_csv(
        args.outdir / "moreyra2025_name_reconciliation_audit.csv",
        discrepancies,
        OUTPUT_FIELDS,
    )
    write_csv(
        args.outdir / "moreyra2025_unlinked_supplement_samples.csv",
        unlinked,
        OUTPUT_FIELDS,
    )
    write_csv(
        args.outdir / "moreyra2025_focal_taxon_audit.csv",
        focal,
        FOCAL_FIELDS,
    )
    (args.outdir / "moreyra2025_sample_audit_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
