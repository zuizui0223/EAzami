#!/usr/bin/env python3
"""Recover the complete public RNA-seq run universe used by Chang et al. 2026.

The paper's 33 transcriptome samples are split across two provenance layers:

1. runs deposited directly under PRJNA1311153; and
2. exact public identifiers printed in the supplement and reused from earlier
   data.

The supplement's accession column is heterogeneous: it can contain an SRA run
(``SRR``), experiment (``SRX``), or BioSample (``SAMN``) accession.  A
BioProject-only query therefore returns an incomplete set.  This script
recovers every identifier according to its accession type, records provenance
for each run, enriches runinfo with explicit BioSample attributes needed for
voucher reconciliation, and never infers sample identity from geography.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from recover_ncbi_project_runs import (
    ClientConfig,
    ESEARCH_URL,
    NCBIClient,
    biosample_attributes,
    esearch_sra_uids,
    fetch_runinfo,
    summarize_taxa,
    write_csv,
)

DEFAULT_PROJECT = "PRJNA1311153"
DEFAULT_SUPPLEMENT = Path(
    "data/evidence/chang2026_east_asia_accession_audit_2026-08-10.csv"
)
DEFAULT_OUTDIR = Path("data/evidence/generated/chang2026_published_runinfo")
RUN_PATTERN = re.compile(r"SRR\d+", flags=re.IGNORECASE)
EXPERIMENT_PATTERN = re.compile(r"SRX\d+", flags=re.IGNORECASE)
BIOSAMPLE_PATTERN = re.compile(r"SAM[A-Z]+\d+", flags=re.IGNORECASE)
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


def identifier_kind(value: object) -> str:
    accession = clean(value).upper()
    if RUN_PATTERN.fullmatch(accession):
        return "run"
    if EXPERIMENT_PATTERN.fullmatch(accession):
        return "experiment"
    if BIOSAMPLE_PATTERN.fullmatch(accession):
        return "biosample"
    return ""


def embedded_accessions(
    rows: Sequence[Mapping[str, str]],
    field: str = "embedded_public_accession",
) -> list[str]:
    """Extract unique supported identifiers explicitly printed in the supplement."""
    output: set[str] = set()
    for row in rows:
        value = clean(row.get(field)).upper()
        if not value:
            continue
        if not identifier_kind(value):
            raise ValueError(f"Invalid embedded public accession: {value!r}")
        output.add(value)
    return sorted(output)


def identifier_query(identifier: str) -> tuple[str, str]:
    kind = identifier_kind(identifier)
    if kind in {"run", "experiment"}:
        return kind, f"{identifier}[Accession]"
    if kind == "biosample":
        return kind, f"{identifier}[BioSample]"
    raise ValueError(f"Unsupported embedded identifier: {identifier!r}")


def row_matches_identifier(row: Mapping[str, str], identifier: str) -> bool:
    kind = identifier_kind(identifier)
    field = {
        "run": "Run",
        "experiment": "Experiment",
        "biosample": "BioSample",
    }.get(kind)
    return bool(field and clean(row.get(field)).upper() == identifier.upper())


def fetch_exact_identifier_rows(
    client: NCBIClient, identifier: str
) -> list[dict[str, str]]:
    """Fetch every runinfo row carrying the exact run/experiment/BioSample ID."""
    identifier = clean(identifier).upper()
    kind, term = identifier_query(identifier)
    payload = client.get(
        ESEARCH_URL,
        {
            "db": "sra",
            "term": term,
            "retmax": 100,
            "retmode": "json",
        },
    )
    result = json.loads(payload.decode("utf-8"))
    ids = [str(item) for item in result.get("esearchresult", {}).get("idlist", [])]
    if not ids:
        # Some NCBI index configurations do not expose every field alias in the
        # same way.  A literal fallback remains exact because returned rows are
        # still filtered against the requested accession below.
        payload = client.get(
            ESEARCH_URL,
            {
                "db": "sra",
                "term": identifier,
                "retmax": 100,
                "retmode": "json",
            },
        )
        result = json.loads(payload.decode("utf-8"))
        ids = [
            str(item)
            for item in result.get("esearchresult", {}).get("idlist", [])
        ]
    if not ids:
        raise RuntimeError(
            f"No SRA record found for embedded {kind} identifier {identifier}"
        )
    rows = fetch_runinfo(client, ids)
    exact = [
        {key: clean(value) for key, value in row.items()}
        for row in rows
        if row_matches_identifier(row, identifier)
    ]
    if not exact:
        returned = sorted(
            {
                clean(row.get("Run"))
                + "/"
                + clean(row.get("Experiment"))
                + "/"
                + clean(row.get("BioSample"))
                for row in rows
            }
        )
        raise RuntimeError(
            f"No exact runinfo row for {identifier}; returned={returned}"
        )
    by_run = {clean(row.get("Run")): row for row in exact if row.get("Run")}
    if len(by_run) != len(exact):
        raise RuntimeError(f"Duplicate runinfo rows returned for {identifier}")
    return [by_run[run] for run in sorted(by_run)]


def merge_layers(
    project_rows: Sequence[Mapping[str, str]],
    reused_rows: Sequence[Mapping[str, str]],
) -> list[dict[str, str]]:
    """Merge by exact SRR while preserving every provenance layer."""
    by_run: dict[str, dict[str, str]] = {}
    scopes: dict[str, set[str]] = {}
    for scope, rows in (
        ("primary_bioproject", project_rows),
        ("supplement_embedded_reused_run", reused_rows),
    ):
        for source in rows:
            row = {key: clean(value) for key, value in source.items()}
            run = clean(row.get("Run")).upper()
            if not RUN_PATTERN.fullmatch(run):
                raise ValueError(f"Runinfo row lacks a valid SRR accession: {run!r}")
            if run in by_run:
                existing = by_run[run]
                for key in set(existing) & set(row):
                    if existing[key] and row[key] and existing[key] != row[key]:
                        raise ValueError(
                            f"Conflicting values for {run} field {key}: "
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


def enrich_with_biosample(
    rows: Sequence[Mapping[str, str]],
    attributes: Mapping[str, Mapping[str, str]],
) -> list[dict[str, str]]:
    """Attach only explicit BioSample fields; no geographic sample matching occurs."""
    output: list[dict[str, str]] = []
    for source in rows:
        row = {key: clean(value) for key, value in source.items()}
        record = attributes.get(clean(row.get("BioSample")), {})
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
    embedded: Sequence[str],
    identifier_rows: Mapping[str, Sequence[Mapping[str, str]]],
    complete_rows: Sequence[Mapping[str, str]],
) -> dict[str, object]:
    runs = {clean(row.get("Run")).upper() for row in complete_rows if row.get("Run")}
    project_runs = {
        clean(row.get("Run")).upper() for row in project_rows if row.get("Run")
    }
    missing = sorted(identifier for identifier in embedded if not identifier_rows.get(identifier))
    type_counts = Counter(identifier_kind(identifier) for identifier in embedded)
    scope_counts = Counter(clean(row.get("recovery_scope")) for row in complete_rows)
    return {
        "supplement_sample_rows": len(supplement_rows),
        "primary_bioproject_run_count": len(project_runs),
        "supplement_embedded_identifier_count": len(embedded),
        "embedded_identifier_type_counts": dict(sorted(type_counts.items())),
        "embedded_identifier_run_counts": {
            identifier: len(identifier_rows.get(identifier, []))
            for identifier in embedded
        },
        "complete_unique_run_count": len(runs),
        "unique_biosample_count": len(
            {
                clean(row.get("BioSample"))
                for row in complete_rows
                if row.get("BioSample")
            }
        ),
        "runs_with_numeric_biosample_isolate": sum(
            bool(re.fullmatch(r"\d+", clean(row.get("biosample_isolate"))))
            for row in complete_rows
        ),
        "recovery_scope_counts": dict(sorted(scope_counts.items())),
        "embedded_identifiers": list(embedded),
        "missing_embedded_identifiers": missing,
        "interpretation": (
            "The published run universe is the union of the primary "
            "PRJNA1311153 deposit and exact run, experiment, or BioSample "
            "identifiers explicitly reused in the supplement."
        ),
    }


def write_summary_csv(path: Path, summary: Mapping[str, object]) -> None:
    write_csv(
        path,
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
        raise SystemExit(f"No supplement rows found in {args.supplement}")
    embedded = embedded_accessions(supplement)

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

    identifier_rows: dict[str, list[dict[str, str]]] = {}
    reused_rows: list[dict[str, str]] = []
    for identifier in embedded:
        rows = fetch_exact_identifier_rows(client, identifier)
        identifier_rows[identifier] = rows
        reused_rows.extend(rows)

    complete = merge_layers(project_rows, reused_rows)
    attributes = biosample_attributes(
        client, [clean(row.get("BioSample")) for row in complete]
    )
    complete = enrich_with_biosample(complete, attributes)
    summary = build_summary(
        supplement,
        project_rows,
        embedded,
        identifier_rows,
        complete,
    )

    if summary["missing_embedded_identifiers"]:
        raise SystemExit(
            "Embedded identifiers not recovered: "
            + "|".join(summary["missing_embedded_identifiers"])
        )
    if summary["complete_unique_run_count"] < len(supplement):
        raise SystemExit(
            "Complete run universe is smaller than the supplement: "
            f"{summary['complete_unique_run_count']} < {len(supplement)}"
        )

    args.outdir.mkdir(parents=True, exist_ok=True)
    run_path = args.outdir / f"{project}_published_complete_runinfo.csv"
    write_csv(run_path, complete, ordered_fields(complete))
    summary_path = args.outdir / f"{project}_published_complete_runinfo_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_summary_csv(
        args.outdir / f"{project}_published_complete_runinfo_summary.csv",
        summary,
    )
    write_csv(
        args.outdir / f"{project}_published_complete_taxon_summary.csv",
        summarize_taxa(complete),
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
        "supplement_embedded_identifier_count="
        f"{summary['supplement_embedded_identifier_count']}"
    )
    print(
        "embedded_identifier_type_counts="
        + json.dumps(summary["embedded_identifier_type_counts"], sort_keys=True)
    )
    print(f"complete_unique_run_count={summary['complete_unique_run_count']}")
    print(f"unique_biosample_count={summary['unique_biosample_count']}")
    print(
        "runs_with_numeric_biosample_isolate="
        f"{summary['runs_with_numeric_biosample_isolate']}"
    )
    print(run_path)
    print(summary_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
