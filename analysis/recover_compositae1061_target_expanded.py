#!/usr/bin/env python3
"""Expanded metadata-aware recovery of Compositae1061 target FASTA candidates.

The first-pass target audit follows explicit URLs discovered in public pages and
APIs.  Some repositories, especially Mendeley Data and Dryad, store a file name,
file ID and download URL in separate JSON fields.  This module pairs those fields,
follows GitHub contents-API records, reconstructs public-file URLs where the API
provides only a stable file ID, and then delegates FASTA validation to
``recover_compositae1061_target.py``.

The output still refuses to freeze an exact Moreyra target solely from sequence
counts or locus-ID overlap; exact identity requires source/method confirmation.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, Sequence
from urllib.parse import quote, urljoin, urlparse

MODULE_PATH = Path(__file__).with_name("recover_compositae1061_target.py")
SPEC = importlib.util.spec_from_file_location("recover_compositae1061_target_base", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
base = importlib.util.module_from_spec(SPEC)
sys.modules["recover_compositae1061_target_base"] = base
SPEC.loader.exec_module(base)

DEFAULT_LOCI = base.DEFAULT_LOCI
DEFAULT_OUTDIR = Path("data/evidence/generated/compositae1061_target_audit_expanded")

DATASETS = {
    "bhvv6rmyt6": {
        "version": "1",
        "label": "Herrando-Moraira 2019 Cardueae Hyb-Seq",
        "landing": "https://data.mendeley.com/datasets/bhvv6rmyt6/1",
    },
    "hgpn6g27c6": {
        "version": "1",
        "label": "Herrando-Moraira processing-strategy dataset",
        "landing": "https://data.mendeley.com/datasets/hgpn6g27c6/1",
    },
}
DRYAD_DOI = "10.5061/dryad.gr93t"
GITHUB_QUERIES = base.GITHUB_QUERIES

NAME_KEYS = {
    "filename",
    "file_name",
    "fileName",
    "name",
    "title",
    "original_filename",
    "originalFilename",
    "path",
    "key",
}
URL_KEYS = {
    "download_url",
    "downloadUrl",
    "download",
    "content_url",
    "contentUrl",
    "url",
    "href",
    "link",
}
ID_KEYS = {"id", "file_id", "fileId", "uuid"}
SIZE_KEYS = {"size", "size_bytes", "sizeBytes", "filesize", "file_size"}

DISCOVERY_FIELDS = (
    "candidate_key",
    "source_key",
    "repository",
    "dataset_id",
    "dataset_version",
    "filename",
    "download_url",
    "file_id",
    "declared_size",
    "context",
    "discovery_method",
    "score",
    "type_hint",
)
DOWNLOAD_FIELDS = (
    "candidate_key",
    "source_key",
    "filename",
    "download_url",
    "status",
    "content_type",
    "content_length",
    "final_url",
    "sha256",
    "error",
)


@dataclass(frozen=True)
class Candidate:
    source_key: str
    repository: str
    dataset_id: str
    dataset_version: str
    filename: str
    download_url: str
    file_id: str = ""
    declared_size: str = ""
    context: str = ""
    discovery_method: str = ""

    @property
    def candidate_key(self) -> str:
        material = "|".join(
            (
                self.source_key,
                self.dataset_id,
                self.file_id,
                self.filename,
                self.download_url,
            )
        )
        import hashlib

        return "candidate_" + hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]


def clean(value: object) -> str:
    return str(value or "").strip()


def first_string(mapping: Mapping[str, Any], keys: Iterable[str]) -> str:
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
        if isinstance(value, (int, float)):
            return str(value)
    return ""


def direct_url_strings(mapping: Mapping[str, Any]) -> list[tuple[str, str]]:
    output: list[tuple[str, str]] = []
    for key, value in mapping.items():
        if isinstance(value, str) and (
            key in URL_KEYS
            or "download" in key.casefold()
            or "content" in key.casefold() and value.startswith(("http://", "https://"))
        ):
            output.append((value, key))
        elif isinstance(value, Mapping) and key.casefold() in {
            "links",
            "_links",
            "content_details",
            "contentdetails",
            "file",
        }:
            for child_key, child_value in value.items():
                if isinstance(child_value, str) and child_value.startswith(("http://", "https://", "/")):
                    output.append((child_value, f"{key}.{child_key}"))
                elif isinstance(child_value, Mapping):
                    href = first_string(child_value, ("href", "url", "download_url", "downloadUrl"))
                    if href:
                        output.append((href, f"{key}.{child_key}"))
    return output


def infer_filename_from_url(url: str) -> str:
    name = Path(urlparse(url).path).name
    if name.casefold() in {"download", "file_downloaded", "content", "files"}:
        return ""
    return base.safe_name(name, "") if name else ""


def likely_file_mapping(mapping: Mapping[str, Any]) -> bool:
    keys = {str(key).casefold() for key in mapping}
    return bool(
        keys
        & {
            "filename",
            "file_name",
            "filename",
            "original_filename",
            "download_url",
            "downloadurl",
            "content_details",
            "filesize",
            "file_size",
        }
    )


def mendeley_constructed_url(dataset_id: str, file_id: str) -> str:
    return (
        f"https://data.mendeley.com/public-files/datasets/{dataset_id}/"
        f"files/{file_id}/file_downloaded"
    )


def dryad_constructed_url(file_id: str) -> str:
    return f"https://datadryad.org/api/v2/files/{file_id}/download"


def walk_file_mappings(
    value: Any,
    *,
    source_key: str,
    repository: str,
    dataset_id: str = "",
    dataset_version: str = "",
    base_url: str = "",
    context: str = "root",
) -> Iterator[Candidate]:
    if isinstance(value, Mapping):
        name = first_string(value, NAME_KEYS)
        file_id = first_string(value, ID_KEYS)
        declared_size = first_string(value, SIZE_KEYS)
        urls = direct_url_strings(value)
        for raw_url, url_context in urls:
            resolved = urljoin(base_url, raw_url)
            if not resolved.startswith(("http://", "https://")):
                continue
            filename = name or infer_filename_from_url(resolved)
            if filename or base.file_like(resolved):
                yield Candidate(
                    source_key=source_key,
                    repository=repository,
                    dataset_id=dataset_id,
                    dataset_version=dataset_version,
                    filename=filename or base.safe_name(resolved),
                    download_url=resolved,
                    file_id=file_id,
                    declared_size=declared_size,
                    context=f"{context}.{url_context}",
                    discovery_method="json_field_pair",
                )
        if name and file_id and likely_file_mapping(value):
            if repository == "Mendeley_Data" and dataset_id:
                yield Candidate(
                    source_key=source_key,
                    repository=repository,
                    dataset_id=dataset_id,
                    dataset_version=dataset_version,
                    filename=name,
                    download_url=mendeley_constructed_url(dataset_id, file_id),
                    file_id=file_id,
                    declared_size=declared_size,
                    context=context,
                    discovery_method="constructed_from_public_file_id",
                )
            elif repository == "Dryad":
                yield Candidate(
                    source_key=source_key,
                    repository=repository,
                    dataset_id=dataset_id,
                    dataset_version=dataset_version,
                    filename=name,
                    download_url=dryad_constructed_url(file_id),
                    file_id=file_id,
                    declared_size=declared_size,
                    context=context,
                    discovery_method="constructed_from_public_file_id",
                )
        for key, child in value.items():
            yield from walk_file_mappings(
                child,
                source_key=source_key,
                repository=repository,
                dataset_id=dataset_id,
                dataset_version=dataset_version,
                base_url=base_url,
                context=f"{context}.{key}",
            )
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_file_mappings(
                child,
                source_key=source_key,
                repository=repository,
                dataset_id=dataset_id,
                dataset_version=dataset_version,
                base_url=base_url,
                context=f"{context}[{index}]",
            )


def extract_script_json(html_text: str) -> list[Any]:
    parsed: list[Any] = []
    for match in re.finditer(
        r"<script(?P<attrs>[^>]*)>(?P<body>.*?)</script>",
        html_text,
        flags=re.I | re.S,
    ):
        attrs = match.group("attrs")
        body = match.group("body").strip()
        if not body:
            continue
        if "application/json" not in attrs.casefold() and not body.startswith(("{", "[")):
            continue
        try:
            parsed.append(json.loads(body))
        except json.JSONDecodeError:
            continue
    return parsed


def candidates_from_response(
    response: Any,
    *,
    repository: str,
    dataset_id: str = "",
    dataset_version: str = "",
) -> list[Candidate]:
    if response.status != "ok" or not response.payload:
        return []
    values: list[Any] = []
    text = response.payload.decode("utf-8", errors="replace")
    try:
        values.append(json.loads(text))
    except json.JSONDecodeError:
        values.extend(extract_script_json(text))
    output: list[Candidate] = []
    for index, value in enumerate(values):
        output.extend(
            walk_file_mappings(
                value,
                source_key=response.source_key,
                repository=repository,
                dataset_id=dataset_id,
                dataset_version=dataset_version,
                base_url=response.final_url or response.requested_url,
                context=f"payload[{index}]",
            )
        )
    return dedupe_candidates(output)


def dedupe_candidates(values: Iterable[Candidate]) -> list[Candidate]:
    output: list[Candidate] = []
    seen: set[tuple[str, str, str]] = set()
    for value in values:
        key = (
            value.download_url,
            value.filename.casefold(),
            value.file_id.casefold(),
        )
        if key not in seen:
            seen.add(key)
            output.append(value)
    return output


def github_candidates(token: str) -> tuple[list[Any], list[Candidate]]:
    responses: list[Any] = []
    output: list[Candidate] = []
    for index, query in enumerate(GITHUB_QUERIES, start=1):
        url = "https://api.github.com/search/code?" + __import__("urllib.parse").parse.urlencode(
            {"q": query, "per_page": 100}
        )
        response = base.download(f"github_search_{index}", url, token)
        responses.append(response)
        if response.status != "ok":
            continue
        try:
            data = json.loads(response.payload)
        except json.JSONDecodeError:
            continue
        for item_index, item in enumerate(data.get("items", []), start=1):
            contents_url = clean(item.get("url"))
            path = clean(item.get("path"))
            repo = clean((item.get("repository") or {}).get("full_name"))
            if not contents_url:
                continue
            contents = base.download(
                f"github_contents_{index}_{item_index}", contents_url, token
            )
            responses.append(contents)
            if contents.status != "ok":
                continue
            try:
                metadata = json.loads(contents.payload)
            except json.JSONDecodeError:
                continue
            download_url = clean(metadata.get("download_url"))
            if not download_url:
                continue
            output.append(
                Candidate(
                    source_key=response.source_key,
                    repository="GitHub",
                    dataset_id=repo,
                    dataset_version=clean(metadata.get("sha")),
                    filename=path or clean(metadata.get("name")),
                    download_url=download_url,
                    file_id=clean(metadata.get("sha")),
                    declared_size=clean(metadata.get("size")),
                    context=f"github_code:{repo}:{path}",
                    discovery_method="github_contents_api",
                )
            )
    return responses, dedupe_candidates(output)


def candidate_score(candidate: Candidate) -> int:
    link = base.Link(
        candidate.source_key,
        candidate.download_url,
        candidate.filename,
        f"{candidate.context} {candidate.dataset_id} {candidate.repository}",
    )
    return base.score(link)


def candidate_hint(candidate: Candidate) -> str:
    link = base.Link(
        candidate.source_key,
        candidate.download_url,
        candidate.filename,
        f"{candidate.context} {candidate.dataset_id} {candidate.repository}",
    )
    return base.hint(link)


def write_csv(path: Path, rows: Iterable[Mapping[str, object]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--moreyra-loci", type=Path, default=DEFAULT_LOCI)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    parser.add_argument("--github-token", default=os.environ.get("GITHUB_TOKEN", ""))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    source_dir = args.outdir / "downloaded_candidates"
    source_dir.mkdir(parents=True, exist_ok=True)
    loci = base.read_loci(args.moreyra_loci)

    responses: list[Any] = []
    candidates: list[Candidate] = []

    for dataset_id, metadata in DATASETS.items():
        version = metadata["version"]
        endpoints = (
            (f"mendeley_{dataset_id}_landing", metadata["landing"]),
            (
                f"mendeley_{dataset_id}_api_version",
                f"https://api.mendeley.com/datasets/{dataset_id}/versions/{version}",
            ),
            (
                f"mendeley_{dataset_id}_api_files",
                f"https://api.mendeley.com/datasets/{dataset_id}/versions/{version}/files",
            ),
            (
                f"mendeley_{dataset_id}_data_version",
                f"https://data.mendeley.com/api/datasets/{dataset_id}/versions/{version}",
            ),
            (
                f"mendeley_{dataset_id}_data_files",
                f"https://data.mendeley.com/api/datasets/{dataset_id}/versions/{version}/files",
            ),
        )
        for source_key, url in endpoints:
            response = base.download(source_key, url, args.github_token)
            responses.append(response)
            candidates.extend(
                candidates_from_response(
                    response,
                    repository="Mendeley_Data",
                    dataset_id=dataset_id,
                    dataset_version=version,
                )
            )

    dryad_endpoints = (
        ("dryad_dataset", "https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.gr93t"),
        ("dryad_landing", "https://datadryad.org/dataset/doi:10.5061/dryad.gr93t"),
    )
    dryad_followups: list[tuple[str, str]] = []
    for source_key, url in dryad_endpoints:
        response = base.download(source_key, url, args.github_token)
        responses.append(response)
        candidates.extend(
            candidates_from_response(
                response,
                repository="Dryad",
                dataset_id=DRYAD_DOI,
                dataset_version="",
            )
        )
        dryad_followups.extend(base.followup_api_links(response))
    for index, (_, url) in enumerate(dryad_followups[:100], start=1):
        response = base.download(f"dryad_followup_{index}", url, args.github_token)
        responses.append(response)
        candidates.extend(
            candidates_from_response(
                response,
                repository="Dryad",
                dataset_id=DRYAD_DOI,
                dataset_version="",
            )
        )

    github_responses, github_found = github_candidates(args.github_token)
    responses.extend(github_responses)
    candidates.extend(github_found)
    candidates = dedupe_candidates(candidates)

    discovery_rows = [
        {
            "candidate_key": candidate.candidate_key,
            "source_key": candidate.source_key,
            "repository": candidate.repository,
            "dataset_id": candidate.dataset_id,
            "dataset_version": candidate.dataset_version,
            "filename": candidate.filename,
            "download_url": candidate.download_url,
            "file_id": candidate.file_id,
            "declared_size": candidate.declared_size,
            "context": candidate.context,
            "discovery_method": candidate.discovery_method,
            "score": candidate_score(candidate),
            "type_hint": candidate_hint(candidate),
        }
        for candidate in candidates
    ]
    discovery_rows.sort(
        key=lambda row: (-int(row["score"]), row["repository"], row["filename"])
    )

    fasta_rows: list[dict[str, object]] = []
    download_rows: list[dict[str, object]] = []
    attempted: set[str] = set()
    for candidate in sorted(
        candidates,
        key=lambda value: (-candidate_score(value), value.download_url),
    ):
        if candidate.download_url in attempted:
            continue
        attempted.add(candidate.download_url)
        score = candidate_score(candidate)
        hint = candidate_hint(candidate)
        if score < 1 and hint not in {
            "generic_fasta",
            "target_or_reference",
            "bait_or_probe",
        }:
            continue
        response = base.download(
            f"expanded_download_{len(download_rows)+1}",
            candidate.download_url,
            args.github_token,
        )
        download_rows.append(
            {
                "candidate_key": candidate.candidate_key,
                "source_key": candidate.source_key,
                "filename": candidate.filename,
                "download_url": candidate.download_url,
                "status": response.status,
                "content_type": response.content_type,
                "content_length": response.content_length,
                "final_url": response.final_url,
                "sha256": base.digest(response.payload) if response.payload else "",
                "error": response.error,
            }
        )
        if response.status != "ok" or not response.payload:
            continue
        container_name = candidate.filename or base.filename_from_response(
            response, candidate.download_url
        )
        (source_dir / f"{len(download_rows):04d}_{base.safe_name(container_name)}").write_bytes(
            response.payload
        )
        link = base.Link(
            candidate.source_key,
            candidate.download_url,
            container_name,
            f"{candidate.context} {candidate.dataset_id} {candidate.repository}",
        )
        for member, fasta in base.fasta_payloads(container_name, response.payload):
            if not fasta.lstrip().startswith(b">"):
                continue
            key = f"expanded_fasta_{len(fasta_rows)+1:04d}"
            try:
                row = base.audit_candidate(
                    key, link, container_name, member, fasta, loci
                )
            except ValueError:
                continue
            row["notes"] = (
                row["notes"]
                + f" Discovery method: {candidate.discovery_method}; "
                + f"dataset: {candidate.dataset_id} version {candidate.dataset_version or 'unresolved'}."
            )
            fasta_rows.append(row)
            (source_dir / f"{key}_{base.safe_name(member or container_name)}").write_bytes(
                fasta
            )

    fasta_rows.sort(
        key=lambda row: (
            -float(row["normalized_overlap_fraction"]),
            -int(row["record_count"]),
        )
    )
    high = [
        row
        for row in fasta_rows
        if row["candidate_status"]
        == "high_confidence_candidate_method_confirmation_required"
    ]
    compatible = [
        row
        for row in fasta_rows
        if row["candidate_status"] == "compatible_target_candidate"
    ]
    best = high[0] if high else compatible[0] if compatible else None
    status = (
        "high_confidence_candidate_recovered_method_confirmation_required"
        if high
        else "compatible_candidate_recovered_not_exact"
        if compatible
        else "exact_or_compatible_target_not_recovered"
    )
    request_rows = [
        {
            "source_key": response.source_key,
            "url": response.requested_url,
            "status": response.status,
            "content_type": response.content_type,
            "content_length": response.content_length,
            "final_url": response.final_url,
            "sha256": base.digest(response.payload) if response.payload else "",
            "error": response.error,
        }
        for response in responses
    ]
    summary = {
        "audit_status": status,
        "source_requests": len(responses),
        "successful_source_requests": sum(
            response.status == "ok" for response in responses
        ),
        "metadata_paired_file_candidates": len(discovery_rows),
        "download_attempts": len(download_rows),
        "successful_downloads": sum(row["status"] == "ok" for row in download_rows),
        "fasta_candidates": len(fasta_rows),
        "moreyra_locus_ids": len(loci),
        "high_confidence_candidates": len(high),
        "compatible_candidates": len(compatible),
        "best_candidate": best,
        "exact_target_frozen": False,
        "freeze_rule": (
            "The exact Moreyra target requires a source/method-linked file version; "
            "metadata pairing and sequence overlap alone are insufficient."
        ),
        "dataset_ids": list(DATASETS) + [DRYAD_DOI],
        "github_queries": list(GITHUB_QUERIES),
    }

    write_csv(args.outdir / "source_request_log.csv", request_rows, base.REQUEST_FIELDS)
    write_csv(args.outdir / "metadata_paired_files.csv", discovery_rows, DISCOVERY_FIELDS)
    write_csv(args.outdir / "download_log.csv", download_rows, DOWNLOAD_FIELDS)
    write_csv(args.outdir / "fasta_candidate_audit.csv", fasta_rows, base.FASTA_FIELDS)
    (args.outdir / "audit_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"audit_status={status}")
    print(f"source_requests={summary['source_requests']}")
    print(f"successful_source_requests={summary['successful_source_requests']}")
    print(f"metadata_paired_file_candidates={len(discovery_rows)}")
    print(f"download_attempts={len(download_rows)}")
    print(f"successful_downloads={summary['successful_downloads']}")
    print(f"fasta_candidates={len(fasta_rows)}")
    print(f"high_confidence_candidates={len(high)}")
    print(f"compatible_candidates={len(compatible)}")
    if best:
        print(
            f"best={best['container_filename']}::{best['archive_member']} "
            f"overlap={best['normalized_overlap_fraction']} sha256={best['sha256']}"
        )
    print(args.outdir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
