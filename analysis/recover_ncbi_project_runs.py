#!/usr/bin/env python3
"""Recover all SRA run metadata for an NCBI BioProject and audit focal taxa.

This script is designed for projects such as PRJNA957074 where the article
and supplementary tables are not sufficient/easy to retrieve, but public SRA
metadata can reconstruct the actual sample set.

It uses only Python's standard library and official NCBI services:
1. Entrez ESearch to retrieve SRA UIDs linked to a BioProject.
2. SRA Database Backend ``runinfo`` in UID chunks.
3. Optional BioSample EFetch enrichment for collection locality/date.

Outputs:
- complete run-level CSV;
- one row per unique scientific name;
- focal-taxon recovery audit that distinguishes verified absence from
  "not recovered by the current query".

NCBI usage:
- supply an email with --email or NCBI_EMAIL;
- optionally supply an API key with --api-key or NCBI_API_KEY;
- requests are rate-limited and retried.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Mapping, Sequence

ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
RUNINFO_URL = "https://trace.ncbi.nlm.nih.gov/Traces/sra-db-be/runinfo"
DEFAULT_PROJECT = "PRJNA957074"
DEFAULT_FOCAL = Path("data/evidence/focal_taxa_prjna957074.txt")
DEFAULT_OUTDIR = Path("data/evidence/generated")
REQUIRED_RUNINFO_COLUMNS = {
    "Run",
    "Experiment",
    "SRAStudy",
    "BioProject",
    "Sample",
    "BioSample",
    "ScientificName",
    "LibraryName",
}


@dataclass(frozen=True)
class ClientConfig:
    email: str
    api_key: str | None
    timeout: int = 60
    retries: int = 5

    @property
    def delay(self) -> float:
        # NCBI recommends no more than 3 requests/s without an API key and
        # no more than 10 requests/s with a key.
        return 0.11 if self.api_key else 0.36


class NCBIClient:
    def __init__(self, config: ClientConfig) -> None:
        self.config = config
        self._last_request = 0.0

    def _throttle(self) -> None:
        elapsed = time.monotonic() - self._last_request
        wait = self.config.delay - elapsed
        if wait > 0:
            time.sleep(wait)

    def get(self, url: str, params: Mapping[str, object]) -> bytes:
        query = dict(params)
        if self.config.email:
            query.setdefault("email", self.config.email)
        if self.config.api_key:
            query.setdefault("api_key", self.config.api_key)
        full_url = f"{url}?{urllib.parse.urlencode(query, doseq=True)}"

        for attempt in range(self.config.retries):
            self._throttle()
            request = urllib.request.Request(
                full_url,
                headers={
                    "User-Agent": (
                        "EAzami-NCBI-metadata-recovery/1.0 "
                        f"({self.config.email or 'email-not-provided'})"
                    )
                },
            )
            try:
                with urllib.request.urlopen(
                    request, timeout=self.config.timeout
                ) as response:
                    payload = response.read()
                self._last_request = time.monotonic()
                return payload
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
                self._last_request = time.monotonic()
                if attempt + 1 >= self.config.retries:
                    raise RuntimeError(f"NCBI request failed: {full_url}") from exc
                retry_after = 2**attempt
                if isinstance(exc, urllib.error.HTTPError):
                    value = exc.headers.get("Retry-After")
                    if value and value.isdigit():
                        retry_after = max(retry_after, int(value))
                time.sleep(retry_after)

        raise AssertionError("unreachable")


def chunks(values: Sequence[str], size: int) -> Iterator[list[str]]:
    for start in range(0, len(values), size):
        yield list(values[start : start + size])


def canonical_taxon(value: str) -> str:
    """Conservative normalization for exact matching, not synonym resolution."""
    value = value.strip().replace("_", " ")
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"\s+\([^)]*\)$", "", value)
    return value.casefold()


def parse_csv_payload(payload: bytes) -> list[dict[str, str]]:
    text = payload.decode("utf-8-sig", errors="replace").strip()
    if not text:
        return []
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None:
        return []
    return [
        {key: (value or "").strip() for key, value in row.items()}
        for row in reader
        if row.get("Run")
    ]


def esearch_sra_uids(
    client: NCBIClient, bioproject: str, retmax: int = 100_000
) -> list[str]:
    payload = client.get(
        ESEARCH_URL,
        {
            "db": "sra",
            "term": f"{bioproject}[BioProject]",
            "retmax": retmax,
            "retmode": "json",
        },
    )
    result = json.loads(payload.decode("utf-8"))
    search = result.get("esearchresult", {})
    count = int(search.get("count", 0))
    ids = [str(item) for item in search.get("idlist", [])]
    if count > retmax:
        raise RuntimeError(
            f"Project has {count} SRA records, larger than retmax={retmax}."
        )
    if count != len(ids):
        raise RuntimeError(
            f"ESearch reported {count} records but returned {len(ids)} UIDs."
        )
    return ids


def fetch_runinfo(
    client: NCBIClient, uids: Sequence[str], chunk_size: int = 200
) -> list[dict[str, str]]:
    rows_by_run: dict[str, dict[str, str]] = {}
    for batch in chunks(list(uids), chunk_size):
        payload = client.get(RUNINFO_URL, {"uid": ",".join(batch)})
        for row in parse_csv_payload(payload):
            run = row.get("Run", "")
            if run:
                rows_by_run[run] = row

    rows = sorted(rows_by_run.values(), key=lambda row: row["Run"])
    if not rows:
        return rows

    missing = REQUIRED_RUNINFO_COLUMNS - set(rows[0])
    if missing:
        raise RuntimeError(f"runinfo is missing expected columns: {sorted(missing)}")
    return rows


def biosample_attributes(
    client: NCBIClient, accessions: Sequence[str], chunk_size: int = 100
) -> dict[str, dict[str, str]]:
    """Retrieve a small set of BioSample fields using accession queries.

    This is deliberately optional because runinfo is sufficient for tip
    recovery and BioSample XML can be slower for a large project.
    """
    output: dict[str, dict[str, str]] = {}
    for batch in chunks(sorted(set(filter(None, accessions))), chunk_size):
        term = " OR ".join(f"{acc}[Accession]" for acc in batch)
        search_payload = client.get(
            ESEARCH_URL,
            {
                "db": "biosample",
                "term": term,
                "retmax": len(batch) * 2,
                "retmode": "json",
            },
        )
        search_result = json.loads(search_payload.decode("utf-8"))
        ids = search_result.get("esearchresult", {}).get("idlist", [])
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
            accession = sample.attrib.get("accession", "")
            if not accession:
                continue
            record: dict[str, str] = {}
            description = sample.find("./Description")
            if description is not None:
                organism = description.find("./Organism")
                if organism is not None:
                    record["biosample_organism"] = organism.attrib.get(
                        "taxonomy_name", ""
                    )
            for attribute in sample.findall(".//Attribute"):
                name = (
                    attribute.attrib.get("harmonized_name")
                    or attribute.attrib.get("attribute_name")
                    or ""
                ).strip()
                if name:
                    record[name] = (attribute.text or "").strip()
            output[accession] = record
    return output


def read_focal_taxa(path: Path) -> list[str]:
    if not path.exists():
        return []
    taxa: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            taxa.append(line)
    return taxa


def write_csv(path: Path, rows: Iterable[Mapping[str, object]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def summarize_taxa(
    rows: Sequence[Mapping[str, str]],
) -> list[dict[str, object]]:
    grouped: dict[str, list[Mapping[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row.get("ScientificName", "")].append(row)

    summary: list[dict[str, object]] = []
    for taxon, records in grouped.items():
        biosamples = sorted({r.get("BioSample", "") for r in records if r.get("BioSample")})
        experiments = sorted(
            {r.get("Experiment", "") for r in records if r.get("Experiment")}
        )
        runs = sorted({r.get("Run", "") for r in records if r.get("Run")})
        libraries = sorted(
            {r.get("LibraryName", "") for r in records if r.get("LibraryName")}
        )
        summary.append(
            {
                "scientific_name": taxon,
                "n_biosamples": len(biosamples),
                "n_experiments": len(experiments),
                "n_runs": len(runs),
                "biosamples": "|".join(biosamples),
                "experiments": "|".join(experiments),
                "runs": "|".join(runs),
                "libraries": "|".join(libraries),
            }
        )
    return sorted(summary, key=lambda row: str(row["scientific_name"]).casefold())


def focal_audit(
    focal_taxa: Sequence[str],
    rows: Sequence[Mapping[str, str]],
) -> list[dict[str, object]]:
    by_canonical: dict[str, list[Mapping[str, str]]] = defaultdict(list)
    for row in rows:
        by_canonical[canonical_taxon(row.get("ScientificName", ""))].append(row)

    audit: list[dict[str, object]] = []
    for taxon in focal_taxa:
        matched = by_canonical.get(canonical_taxon(taxon), [])
        biosamples = sorted(
            {row.get("BioSample", "") for row in matched if row.get("BioSample")}
        )
        experiments = sorted(
            {row.get("Experiment", "") for row in matched if row.get("Experiment")}
        )
        runs = sorted({row.get("Run", "") for row in matched if row.get("Run")})
        audit.append(
            {
                "query_taxon": taxon,
                "project_tip_status": (
                    "exact_sra_project_tip_verified"
                    if matched
                    else "not_recovered_in_project_runinfo"
                ),
                "n_runs": len(runs),
                "scientific_names_returned": "|".join(
                    sorted({row.get("ScientificName", "") for row in matched})
                ),
                "biosamples": "|".join(biosamples),
                "experiments": "|".join(experiments),
                "runs": "|".join(runs),
                "interpretation": (
                    "Taxon is directly verified in public SRA metadata for this project."
                    if matched
                    else (
                        "No exact accepted-name match in project runinfo. This is not "
                        "proof of biological absence: check synonyms, historical names, "
                        "unsequenced samples, and supplementary-tree tips."
                    )
                ),
            }
        )
    return audit


def enrich_rows_with_biosample(
    rows: list[dict[str, str]],
    attributes: Mapping[str, Mapping[str, str]],
) -> None:
    for row in rows:
        record = attributes.get(row.get("BioSample", ""), {})
        row["geographic_location"] = (
            record.get("geo_loc_name")
            or record.get("geographic location")
            or record.get("geographic_location")
            or ""
        )
        row["collection_date"] = record.get("collection_date", "")
        row["latitude_longitude"] = (
            record.get("lat_lon")
            or record.get("latitude and longitude")
            or record.get("latitude_longitude")
            or ""
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bioproject", default=DEFAULT_PROJECT)
    parser.add_argument(
        "--email",
        default=os.getenv("NCBI_EMAIL", ""),
        help="Email required/recommended by NCBI; or set NCBI_EMAIL.",
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("NCBI_API_KEY"),
        help="Optional NCBI API key; or set NCBI_API_KEY.",
    )
    parser.add_argument("--focal-taxa", type=Path, default=DEFAULT_FOCAL)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    parser.add_argument(
        "--enrich-biosample",
        action="store_true",
        help="Also fetch collection locality/date from BioSample XML.",
    )
    parser.add_argument(
        "--offline-runinfo",
        type=Path,
        help="Skip network and summarize an existing runinfo CSV.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project = args.bioproject.strip()
    if not re.fullmatch(r"PRJ[A-Z]{2}\d+", project):
        raise SystemExit(f"Unexpected BioProject accession: {project!r}")

    if args.offline_runinfo:
        with args.offline_runinfo.open(newline="", encoding="utf-8-sig") as handle:
            rows = [
                {key: (value or "").strip() for key, value in row.items()}
                for row in csv.DictReader(handle)
                if row.get("Run")
            ]
    else:
        if not args.email:
            print(
                "WARNING: --email/NCBI_EMAIL was not provided; NCBI requests "
                "will still be rate-limited.",
                file=sys.stderr,
            )
        client = NCBIClient(ClientConfig(args.email, args.api_key))
        uids = esearch_sra_uids(client, project)
        if not uids:
            raise SystemExit(f"No public SRA records found for {project}.")
        rows = fetch_runinfo(client, uids)
        rows = [row for row in rows if row.get("BioProject") == project]
        if args.enrich_biosample:
            attributes = biosample_attributes(
                client, [row.get("BioSample", "") for row in rows]
            )
            enrich_rows_with_biosample(rows, attributes)

    if not rows:
        raise SystemExit("No run rows remained after project filtering.")

    args.outdir.mkdir(parents=True, exist_ok=True)
    run_fields = list(rows[0])
    for optional in ("geographic_location", "collection_date", "latitude_longitude"):
        if optional in rows[0] and optional not in run_fields:
            run_fields.append(optional)
    run_path = args.outdir / f"{project}_runinfo.csv"
    write_csv(run_path, rows, run_fields)

    summary = summarize_taxa(rows)
    summary_path = args.outdir / f"{project}_taxon_summary.csv"
    write_csv(
        summary_path,
        summary,
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

    focal_taxa = read_focal_taxa(args.focal_taxa)
    focal_path = args.outdir / f"{project}_focal_taxon_audit.csv"
    audit = focal_audit(focal_taxa, rows)
    write_csv(
        focal_path,
        audit,
        (
            "query_taxon",
            "project_tip_status",
            "n_runs",
            "scientific_names_returned",
            "biosamples",
            "experiments",
            "runs",
            "interpretation",
        ),
    )

    print(f"Recovered {len(rows)} runs and {len(summary)} unique scientific names.")
    print(run_path)
    print(summary_path)
    print(focal_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
