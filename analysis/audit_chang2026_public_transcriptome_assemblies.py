#!/usr/bin/env python3
"""Audit public TSA and Assembly records for Chang et al. 2026 samples.

The supplement-to-SRA reconciliation identifies the official BioSample and run
for each transcriptome.  Before planning a costly six-sample de novo assembly,
this script asks whether NCBI already exposes a reusable Transcriptome Shotgun
Assembly (TSA) or Assembly record for each BioSample.

Queries use official NCBI E-utilities only.  Absence of a hit is reported as
``not_recovered_by_current_ncbi_query`` rather than proof that no author-held or
unlinked assembly exists.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Callable, Iterable, Mapping, Sequence

DEFAULT_MANIFEST = Path(
    "data/evidence/generated/chang2026_ncbi_reconciliation/"
    "chang2026_sample_run_reconciliation.csv"
)
DEFAULT_OUTDIR = Path(
    "data/evidence/generated/chang2026_public_transcriptome_assemblies"
)

OUTPUT_FIELDS = (
    "taxon",
    "code",
    "voucher",
    "published_figure_label",
    "flower_colour_state",
    "matched_run",
    "matched_biosample",
    "match_confidence",
    "biosample_tsa_query",
    "voucher_tsa_query",
    "assembly_query",
    "tsa_biosample_hit_count",
    "tsa_voucher_fallback_hit_count",
    "tsa_total_unique_hit_count",
    "tsa_uids",
    "tsa_accessions",
    "tsa_titles",
    "tsa_assembly_accessions",
    "assembly_hit_count",
    "assembly_uids",
    "assembly_accessions",
    "assembly_names",
    "assembly_statuses",
    "public_transcriptome_status",
    "preferred_public_source",
    "query_error",
    "interpretation",
)

SUMMARY_FIELDS = ("metric", "value")
EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def clean(value: object) -> str:
    return str(value or "").strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return [
            {key: clean(value) for key, value in row.items()}
            for row in reader
            if any(clean(value) for value in row.values())
        ]


def write_csv(
    path: Path,
    rows: Iterable[Mapping[str, object]],
    fields: Sequence[str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(fields), extrasaction="ignore"
        )
        writer.writeheader()
        writer.writerows(rows)


def unique_join(values: Iterable[object]) -> str:
    return "|".join(sorted({clean(value) for value in values if clean(value)}))


def eutils_json(
    endpoint: str,
    params: Mapping[str, object],
    *,
    email: str = "",
    api_key: str = "",
    timeout: int = 60,
    retries: int = 5,
) -> dict[str, object]:
    payload = {key: value for key, value in params.items() if value not in {None, ""}}
    payload["retmode"] = "json"
    if email:
        payload["email"] = email
    if api_key:
        payload["api_key"] = api_key
    url = f"{EUTILS_BASE}/{endpoint}?{urllib.parse.urlencode(payload)}"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "EAzami-Chang2026-TSA-audit/1.0"},
    )
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            if attempt + 1 == retries:
                raise RuntimeError(f"NCBI request failed: {url}") from exc
            delay = 2**attempt
            if isinstance(exc, urllib.error.HTTPError):
                retry_after = exc.headers.get("Retry-After")
                if retry_after and retry_after.isdigit():
                    delay = max(delay, int(retry_after))
            time.sleep(delay)
    raise AssertionError("unreachable")


def esearch(
    db: str,
    term: str,
    *,
    email: str = "",
    api_key: str = "",
    retmax: int = 100,
) -> list[str]:
    payload = eutils_json(
        "esearch.fcgi",
        {"db": db, "term": term, "retmax": retmax},
        email=email,
        api_key=api_key,
    )
    result = payload.get("esearchresult", {})
    return [clean(value) for value in result.get("idlist", []) if clean(value)]


def esummary(
    db: str,
    ids: Sequence[str],
    *,
    email: str = "",
    api_key: str = "",
) -> list[dict[str, object]]:
    if not ids:
        return []
    payload = eutils_json(
        "esummary.fcgi",
        {"db": db, "id": ",".join(ids)},
        email=email,
        api_key=api_key,
    )
    result = payload.get("result", {})
    output: list[dict[str, object]] = []
    for uid in result.get("uids", []):
        record = result.get(str(uid), {})
        if isinstance(record, dict):
            output.append({"uid": str(uid), **record})
    return output


def value_from(record: Mapping[str, object], *names: str) -> str:
    index = {
        re.sub(r"[^a-z0-9]+", "", str(key).casefold()): clean(value)
        for key, value in record.items()
    }
    for name in names:
        value = index.get(re.sub(r"[^a-z0-9]+", "", name.casefold()), "")
        if value:
            return value
    return ""


def parse_nuccore_summaries(records: Sequence[Mapping[str, object]]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for record in records:
        output.append(
            {
                "uid": clean(record.get("uid")),
                "accession": value_from(record, "caption", "accessionversion", "accession"),
                "title": value_from(record, "title"),
                "assembly_accession": value_from(record, "assemblyacc", "assemblyaccession"),
                "extra": value_from(record, "extra"),
            }
        )
    return output


def parse_assembly_summaries(records: Sequence[Mapping[str, object]]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for record in records:
        output.append(
            {
                "uid": clean(record.get("uid")),
                "accession": value_from(record, "assemblyaccession", "synonym"),
                "name": value_from(record, "assemblyname"),
                "status": value_from(record, "assemblystatus", "assembly_status"),
                "description": value_from(record, "assemblydescription"),
            }
        )
    return output


def tsa_query_for_biosample(biosample: str) -> str:
    return f'"{biosample}"[BioSample] AND tsa[filter]'


def tsa_query_for_voucher(voucher: str) -> str:
    return f'"{voucher}"[All Fields] AND tsa[filter]'


def assembly_query_for_biosample(biosample: str) -> str:
    return f'"{biosample}"[BioSample]'


def audit_row(
    row: Mapping[str, str],
    *,
    search_fn: Callable[[str, str], Sequence[str]],
    summary_fn: Callable[[str, Sequence[str]], Sequence[Mapping[str, object]]],
) -> dict[str, object]:
    biosample = clean(row.get("matched_biosample"))
    voucher = clean(row.get("voucher"))
    confidence = clean(row.get("match_confidence"))

    biosample_tsa_query = tsa_query_for_biosample(biosample) if biosample else ""
    voucher_tsa_query = tsa_query_for_voucher(voucher) if voucher else ""
    assembly_query = assembly_query_for_biosample(biosample) if biosample else ""

    errors: list[str] = []
    biosample_tsa_ids: list[str] = []
    voucher_tsa_ids: list[str] = []
    assembly_ids: list[str] = []

    if confidence not in {"verified", "probable"} or not biosample:
        status = "run_or_biosample_not_verified"
        interpretation = (
            "Public assembly audit was not attempted because the official run/BioSample reconciliation is unresolved."
        )
        tsa_records: list[dict[str, str]] = []
        assembly_records: list[dict[str, str]] = []
    else:
        try:
            biosample_tsa_ids = list(search_fn("nuccore", biosample_tsa_query))
        except Exception as exc:  # keep all other samples auditable
            errors.append(f"biosample_tsa:{type(exc).__name__}:{exc}")
        if not biosample_tsa_ids and voucher:
            try:
                voucher_tsa_ids = list(search_fn("nuccore", voucher_tsa_query))
            except Exception as exc:
                errors.append(f"voucher_tsa:{type(exc).__name__}:{exc}")
        try:
            assembly_ids = list(search_fn("assembly", assembly_query))
        except Exception as exc:
            errors.append(f"assembly:{type(exc).__name__}:{exc}")

        tsa_ids = sorted(set(biosample_tsa_ids) | set(voucher_tsa_ids))
        try:
            tsa_records = parse_nuccore_summaries(
                summary_fn("nuccore", tsa_ids)
            )
        except Exception as exc:
            errors.append(f"nuccore_summary:{type(exc).__name__}:{exc}")
            tsa_records = []
        try:
            assembly_records = parse_assembly_summaries(
                summary_fn("assembly", assembly_ids)
            )
        except Exception as exc:
            errors.append(f"assembly_summary:{type(exc).__name__}:{exc}")
            assembly_records = []

        if tsa_records:
            status = "public_tsa_recovered"
            interpretation = (
                "A public TSA record was recovered and should be evaluated before de novo assembly from SRA reads."
            )
        elif assembly_records:
            status = "public_assembly_record_recovered_no_tsa_hit"
            interpretation = (
                "An Assembly record was recovered, but the current TSA query returned no nucleotide TSA hit."
            )
        elif errors:
            status = "query_incomplete_due_to_ncbi_error"
            interpretation = (
                "No reusable assembly can be concluded because one or more NCBI queries failed."
            )
        else:
            status = "not_recovered_by_current_ncbi_query"
            interpretation = (
                "No BioSample- or voucher-linked TSA/Assembly record was recovered; de novo assembly from official SRA reads is the reproducible fallback."
            )

    if tsa_records:
        preferred = "NCBI_TSA"
    elif assembly_records:
        preferred = "NCBI_Assembly"
    elif confidence in {"verified", "probable"}:
        preferred = "de_novo_from_official_SRA"
    else:
        preferred = "resolve_run_first"

    all_tsa_ids = sorted(set(biosample_tsa_ids) | set(voucher_tsa_ids))
    return {
        "taxon": clean(row.get("taxon")),
        "code": clean(row.get("code")),
        "voucher": voucher,
        "published_figure_label": clean(row.get("published_figure_label")),
        "flower_colour_state": clean(row.get("flower_colour_state")),
        "matched_run": clean(row.get("matched_run")),
        "matched_biosample": biosample,
        "match_confidence": confidence,
        "biosample_tsa_query": biosample_tsa_query,
        "voucher_tsa_query": voucher_tsa_query,
        "assembly_query": assembly_query,
        "tsa_biosample_hit_count": len(biosample_tsa_ids),
        "tsa_voucher_fallback_hit_count": len(voucher_tsa_ids),
        "tsa_total_unique_hit_count": len(all_tsa_ids),
        "tsa_uids": unique_join(record.get("uid") for record in tsa_records),
        "tsa_accessions": unique_join(record.get("accession") for record in tsa_records),
        "tsa_titles": unique_join(record.get("title") for record in tsa_records),
        "tsa_assembly_accessions": unique_join(
            record.get("assembly_accession") for record in tsa_records
        ),
        "assembly_hit_count": len(assembly_ids),
        "assembly_uids": unique_join(record.get("uid") for record in assembly_records),
        "assembly_accessions": unique_join(
            record.get("accession") for record in assembly_records
        ),
        "assembly_names": unique_join(record.get("name") for record in assembly_records),
        "assembly_statuses": unique_join(record.get("status") for record in assembly_records),
        "public_transcriptome_status": status,
        "preferred_public_source": preferred,
        "query_error": "; ".join(errors),
        "interpretation": interpretation,
    }


def build_summary(rows: Sequence[Mapping[str, object]]) -> dict[str, object]:
    status_counts = Counter(str(row["public_transcriptome_status"]) for row in rows)
    source_counts = Counter(str(row["preferred_public_source"]) for row in rows)
    takaoense = [
        row for row in rows if "takaoense" in str(row["taxon"]).casefold()
    ]
    return {
        "sample_rows": len(rows),
        "status_counts": dict(sorted(status_counts.items())),
        "preferred_public_source_counts": dict(sorted(source_counts.items())),
        "samples_with_public_tsa": sum(
            row["public_transcriptome_status"] == "public_tsa_recovered"
            for row in rows
        ),
        "samples_with_public_assembly_without_tsa": sum(
            row["public_transcriptome_status"]
            == "public_assembly_record_recovered_no_tsa_hit"
            for row in rows
        ),
        "samples_requiring_de_novo_sra_fallback": sum(
            row["preferred_public_source"] == "de_novo_from_official_SRA"
            for row in rows
        ),
        "takaoense_rows": len(takaoense),
        "takaoense_public_tsa_rows": sum(
            row["public_transcriptome_status"] == "public_tsa_recovered"
            for row in takaoense
        ),
        "takaoense_de_novo_sra_fallback_rows": sum(
            row["preferred_public_source"] == "de_novo_from_official_SRA"
            for row in takaoense
        ),
        "takaoense_records": [
            {
                "code": row["code"],
                "voucher": row["voucher"],
                "morph": row["published_figure_label"],
                "run": row["matched_run"],
                "biosample": row["matched_biosample"],
                "status": row["public_transcriptome_status"],
                "tsa_accessions": row["tsa_accessions"],
                "assembly_accessions": row["assembly_accessions"],
                "preferred_public_source": row["preferred_public_source"],
            }
            for row in takaoense
        ],
        "interpretation_limit": (
            "No NCBI hit means only that the current BioSample/voucher-linked official query did not recover one. It does not exclude an unlinked repository or author-held assembly."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    parser.add_argument("--email", default=os.getenv("NCBI_EMAIL", ""))
    parser.add_argument("--api-key", default=os.getenv("NCBI_API_KEY", ""))
    parser.add_argument("--delay", type=float, default=0.11)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = read_csv(args.manifest)
    if not manifest:
        raise SystemExit(f"No reconciliation rows in {args.manifest}")

    def search_fn(db: str, term: str) -> Sequence[str]:
        ids = esearch(
            db,
            term,
            email=args.email,
            api_key=args.api_key,
        )
        time.sleep(args.delay)
        return ids

    def summary_fn(
        db: str, ids: Sequence[str]
    ) -> Sequence[Mapping[str, object]]:
        records = esummary(
            db,
            ids,
            email=args.email,
            api_key=args.api_key,
        )
        time.sleep(args.delay)
        return records

    rows = [
        audit_row(row, search_fn=search_fn, summary_fn=summary_fn)
        for row in manifest
    ]
    summary = build_summary(rows)

    args.outdir.mkdir(parents=True, exist_ok=True)
    write_csv(args.outdir / "chang2026_public_transcriptome_assembly_audit.csv", rows, OUTPUT_FIELDS)
    takaoense = [
        row for row in rows if "takaoense" in str(row["taxon"]).casefold()
    ]
    write_csv(args.outdir / "chang2026_takaoense_public_assembly_audit.csv", takaoense, OUTPUT_FIELDS)
    (args.outdir / "chang2026_public_assembly_audit_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_csv(
        args.outdir / "chang2026_public_assembly_audit_summary.csv",
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

    print(f"sample_rows={summary['sample_rows']}")
    print(f"samples_with_public_tsa={summary['samples_with_public_tsa']}")
    print(
        "samples_requiring_de_novo_sra_fallback="
        f"{summary['samples_requiring_de_novo_sra_fallback']}"
    )
    print(f"takaoense_rows={summary['takaoense_rows']}")
    print(f"takaoense_public_tsa_rows={summary['takaoense_public_tsa_rows']}")
    print(
        "takaoense_de_novo_sra_fallback_rows="
        f"{summary['takaoense_de_novo_sra_fallback_rows']}"
    )
    print(args.outdir / "chang2026_takaoense_public_assembly_audit.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
