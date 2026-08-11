#!/usr/bin/env python3
"""Recover the complete Chang et al. 2026 RNA-seq run set.

The Chang 2026 supplement contains 33 transcriptome samples, but the samples do
not all originate from one newly deposited BioProject batch.  The reproducible
public set is the union of:

* runs returned directly by PRJNA1311153; and
* supplement-embedded SRR accessions reused from earlier public datasets.

A BioProject-only query therefore undercounts the published sample set.  This
script recovers both provenance layers, preserves their origin, enriches every
run with official BioSample identity fields, and writes one complete runinfo
file for downstream voucher reconciliation.

No sample is linked from geography.  External runs enter only through an exact
SRR accession printed in the supplement.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from recover_ncbi_project_runs import (
    ClientConfig,
    ESEARCH_URL,
    EFETCH_URL,
    NCBIClient,
    chunks,
    esearch_sra_uids,
    fetch_runinfo,
    summarize_taxa,
    write_csv,
)

DEFAULT_PROJECT = "PRJNA1311153"
DEFAULT_SUPPLEMENT = Path(
    "data/evidence/chang2026_east_asia_accession_audit_2026-08-10.csv"
)
DEFAULT_OUTDIR = Path("data/evidence/generated/chang2026_complete_runinfo")
RUN_PATTERN = re.compile(r"SRR\d+", re.IGNORECASE)

SUMMARY_FIELDS = ("metric", "value")


def clean(value: object) -> str:
    return str(value or "").strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [
            {key: clean(value) for key, value in row.items()}
            for row in csv.DictReader(handle)
            if any(clean(value) for value in row.values())
        ]


def supplement_embedded_runs(
    rows: Sequence[Mapping[str, str]],
    column: str = "embedded_public_accession",
) -> list[str]:
    """Return unique exact SRR accessions printed in the supplement."""
    accessions: set[str] = set()
    for row in rows:
        value = clean(row.get(column)).upper()
        if not value:
            continue
        if not RUN_PATTERN.fullmatch(value):
            raise ValueError(
                f"Unexpected embedded run accession {value!r} in column {column!r}"
            )
        accessions.add(value)
    return sorted(accessions)


def esearch_exact_run_uid(client: NCBIClient, accession: str) -> str:
    payload = client.get(
        ESEARCH_URL,
        {
            "db": "sra",
            "term": f"{accession}[Accession]",
            "retmax": 10,
            "retmode": "json",
        },
    )
    result = json.loads(payload.decode("utf-8"))
    ids = [str(item) for item in result.get("esearchresult", {}).get("idlist", [])]
    if not ids:
        raise RuntimeError(f"No SRA UID recovered for embedded run {accession}")
    rows = fetch_runinfo(client, ids)
    exact = [row for row in rows if clean(row.get("Run")).upper() == accession]
    if len(exact) != 1:
        returned = sorted(clean(row.get("Run")) for row in rows)
        raise RuntimeError(
            f"Expected one exact runinfo row for {accession}; returned={returned}"
        )
    # The caller fetches the row again only if necessary.  Return the UID whose
    # result set has already been proven to contain the exact accession.
    return ids[0]


def fetch_exact_embedded_rows(
    client: NCBIClient, accessions: Sequence[str]
) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for accession in sorted(set(accessions)):
        uid = esearch_exact_run_uid(client, accession)
        rows = fetch_runinfo(client, [uid])
        exact = [row for row in rows if clean(row.get("Run")).upper() == accession]
        if len(exact) != 1:
            raise RuntimeError(f"Exact embedded run disappeared on refetch: {accession}")
        output.append(dict(exact[0]))
    return output


def merge_runinfo_layers(
    project_rows: Sequence[Mapping[str, str]],
    embedded_rows: Sequence[Mapping[str, str]],
) -> list[dict[str, str]]:
    """Merge provenance layers by exact run accession without silent conflicts."""
    by_run: dict[str, dict[str, str]] = {}
    scopes: dict[str, set[str]] = {}

    for scope, rows in (
        ("primary_bioproject", project_rows),
        ("supplement_embedded_reused_run", embedded_rows),
    ):
        for source in rows:
            row = {key: clean(value) for key, value in source.items()}
            run = clean(row.get("Run")).upper()
            if not RUN_PATTERN.fullmatch(run):
                raise ValueError(f"Invalid or missing run accession: {run!r}")
            if run in by_run:
                existing = by_run[run]
                for key in set(existing) & set(row):
                    if existing[key] and row[key] and existing[key] != row[key]:
                        raise ValueError(
                            f"Conflicting runinfo values for {run} field {key}: "
                            f"{existing[key]!r} != {row[key]!r}"
                        )
                for key, value in row.items():
                    if value and not existing.get(key):
                        existing[key] = value
            else:
                by_run[run] = row
            scopes.setdefault(run, set()).add(scope)

    output: list[dict[str, str]] = []
    for run in sorted(by_run):
        row = dict(by_run[run])
        row["recovery_scope"] = "|".join(sorted(scopes[run]))
        output.append(row)
    return output


def _normalized_label(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.casefold()).strip("_")


def fetch_biosample_identity(
    client: NCBIClient,
    accessions: Sequence[str],
    chunk_size: int = 100,
) -> dict[str, dict[str, str]]:
    """Recover BioSample title, sample-name IDs and all named attributes."""
    output: dict[str, dict[str, str]] = {}
    for batch in chunks(sorted(set(filter(None, accessions))), chunk_size):
        term = " OR ".join(f"{accession}[Accession]" for accession in batch)
        search_payload = client.get(
            ESEARCH_URL,
            {
                "db": "biosample",
                "term": term,
                "retmax": max(10, len(batch) * 2),
                "retmode": "json",
            },
        )
        search = json.loads(search_payload.decode("utf-8"))
        ids = [str(item) for item in search.get("esearchresult", {}).get("idlist", [])]
        if not ids:
            continue
        xml_payload = client.get(
            EFETCH_URL,
            {
                "db": "biosample",
                "id": ",".join(ids),
                "retmode": "xml",
            },
        )
        root = ET.fromstring(xml_payload)
        for sample in root.findall(".//BioSample"):
            accession = clean(sample.attrib.get("accession"))
            if not accession:
                continue
            record: dict[str, str] = {}
            title = sample.findtext("./Description/Title")
            if title:
                record["biosample_title"] = clean(title)
            organism = sample.find("./Description/Organism")
            if organism is not None:
                record["biosample_organism"] = clean(
                    organism.attrib.get("taxonomy_name")
                )
            for identifier in sample.findall("./Ids/Id"):
                value = clean(identifier.text)
                label = clean(
                    identifier.attrib.get("db_label")
                    or identifier.attrib.get("db")
                )
                if not value or not label:
                    continue
                key = "biosample_id_" + _normalized_label(label)
                record[key] = value
                if _normalized_label(label) in {"sample_name", "sample"}:
                    record["biosample_sample_name"] = value
            for attribute in sample.findall(".//Attribute"):
                name = clean(
                    attribute.attrib.get("harmonized_name")
                    or attribute.attrib.get("attribute_name")
                )
                if name:
                    record[name] = clean(attribute.text)
            output[accession] = record
    return output


def enrich_runinfo_rows(
    rows: Sequence[Mapping[str, str]],
    metadata: Mapping[str, Mapping[str, str]],
) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for source in rows:
        row = {key: clean(value) for key, value in source.items()}
        record = metadata.get(clean(row.get("BioSample")), {})
        row["biosample_title"] = clean(record.get("biosample_title"))
        row["biosample_sample_name"] = clean(
            record.get("biosample_sample_name")
            or record.get("sample name")
            or record.get("sample_name")
        )
        row["biosample_isolate"] = clean(record.get("isolate"))
        row["biosample_organism"] = clean(record.get("biosample_organism"))
        row["geographic_location"] = clean(
            record.get("geo_loc_name")
            or record.get("geographic location")
            or record.get("geographic_location")
        )
        row["collection_date"] = clean(record.get("collection_date"))
        row["latitude_longitude"] = clean(
            record.get("lat_lon")
            or record.get("latitude and longitude")
            or record.get("latitude_longitude")
        )
        output.append(row)
    return output


def ordered_fields(rows: Sequence[Mapping[str, str]]) -> list[str]:
    preferred = [
        "Run",
        "Experiment",
        "SRAStudy",
        "BioProject",
        "Sample",
        "BioSample",
        "ScientificName",
        "LibraryName",
        "SampleName",
        "recovery_scope",
        "biosample_title",
        "biosample_sample_name",
        "biosample_isolate",
        "biosample_organism",
        "geographic_location",
        "collection_date",
        "latitude_longitude",
    ]
    observed = {key for row in rows for key in row}
    return [field for field in preferred if field in observed] + sorted(
        observed - set(preferred)
    )


def build_summary(
    supplement_rows: Sequence[Mapping[str, str]],
    project_rows: Sequence[Mapping[str, str]],
    embedded_accessions: Sequence[str],
    complete_rows: Sequence[Mapping[str, str]],
) -> dict[str, object]:
    scope_counts = Counter(clean(row.get("recovery_scope")) for row in complete_rows)
    complete_runs = {clean(row.get("Run")) for row in complete_rows}
    missing_embedded = sorted(set(embedded_accessions) - complete_runs)
    return {
        "supplement_sample_rows": len(supplement_rows),
        "primary_bioproject_run_count": len(project_rows),
        "supplement_embedded_accession_count": len(embedded_accessions),
        "complete_unique_run_count": len(complete_runs),
        "unique_biosample_count": len(
            {clean(row.get("BioSample")) for row in complete_rows if row.get("BioSample")}
        ),
        "recovery_scope_counts": dict(sorted(scope_counts.items())),
        "embedded_accessions": list(embedded_accessions),
        "missing_embedded_accessions": missing_embedded,
        "interpretation": (
            "The complete published run universe is the union of the primary "
            "PRJNA1311153 deposition and exact SRR accessions explicitly reused "
            "in the Chang 2026 supplement."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bioproject", default=DEFAULT_PROJECT)
    parser.add_argument("--supplement", type=Path, default=DEFAULT_SUPPLEMENT)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    parser.add_argument("--email", default=os.getenv("NCBI_EMAIL", ""))
    parser.add_argument("--api-key", default=os.getenv("NCBI_API_KEY"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project = clean(args.bioproject)
    if not re.fullmatch(r"PRJ[A-Z]{2}\d+", project):
        raise SystemExit(f"Unexpected BioProject accession: {project!r}")
    supplement = read_csv(args.supplement)
    if not supplement:
        raise SystemExit(f"No supplement rows recovered from {args.supplement}")
    embedded = supplement_embedded_runs(supplement)

    if not args.email:
        print(
            "WARNING: --email/NCBI_EMAIL was not provided; requests remain rate-limited.",
            file=sys.stderr,
        )
    client = NCBIClient(ClientConfig(args.email, args.api_key))

    project_uids = esearch_sra_uids(client, project)
    project_rows = [
        row
        for row in fetch_runinfo(client, project_uids)
        if clean(row.get("BioProject")) == project
    ]
    project_runs = {clean(row.get("Run")).upper() for row in project_rows}
    missing_from_project = [run for run in embedded if run not in project_runs]
    embedded_rows = fetch_exact_embedded_rows(client, missing_from_project)

    complete = merge_runinfo_layers(project_rows, embedded_rows)
    metadata = fetch_biosample_identity(
        client, [clean(row.get("BioSample")) for row in complete]
    )
    complete = enrich_runinfo_rows(complete, metadata)
    summary = build_summary(supplement, project_rows, embedded, complete)

    if summary["missing_embedded_accessions"]:
        raise SystemExit(
            "Embedded accessions were not recovered: "
            + "|".join(summary["missing_embedded_accessions"])
        )
    if summary["complete_unique_run_count"] < len(supplement):
        raise SystemExit(
            "Complete public run set is smaller than the published supplement: "
            f"{summary['complete_unique_run_count']} < {len(supplement)}"
        )

    args.outdir.mkdir(parents=True, exist_ok=True)
    run_path = args.outdir / f"{project}_complete_runinfo.csv"
    write_csv(run_path, complete, ordered_fields(complete))
    summary_path = args.outdir / f"{project}_complete_runinfo_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_csv(
        args.outdir / f"{project}_complete_runinfo_summary.csv",
        (
            {
                "metric": key,
                "value": json.dumps(value, ensure_ascii=False)
                if isinstance(value, (dict, list))
                else value,
            }
            for key, value in summary.items()
        ),
        SUMMARY_FIELDS,
    )
    taxon_summary = summarize_taxa(complete)
    write_csv(
        args.outdir / f"{project}_complete_taxon_summary.csv",
        taxon_summary,
        (
            "scientific_name",
            "n_biosamples",
            "n_experiments",
            "n_runs",
            "biosamples",
            "experiments",
            "runs",
            "libraries",
        ),
    )

    print(f"supplement_sample_rows={summary['supplement_sample_rows']}")
    print(f"primary_bioproject_run_count={summary['primary_bioproject_run_count']}")
    print(
        "supplement_embedded_accession_count="
        f"{summary['supplement_embedded_accession_count']}"
    )
    print(f"complete_unique_run_count={summary['complete_unique_run_count']}")
    print(f"unique_biosample_count={summary['unique_biosample_count']}")
    print(run_path)
    print(summary_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
