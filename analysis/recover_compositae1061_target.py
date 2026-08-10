#!/usr/bin/env python3
"""Recover and audit public Compositae1061 target/reference FASTA candidates.

This active audit searches official dataset pages/APIs plus public GitHub code,
extracts FASTA files from direct downloads and archives, and compares header IDs
with the 1,061 public Moreyra locus names.  It distinguishes target/reference
sequences from bait/probe oligos and derived alignments.

A high sequence-ID overlap is necessary but not sufficient for calling a file the
*exact* Moreyra target: source metadata or methods must also identify the exact
file/version used.  Therefore this script never freezes an exact target solely
from record counts or overlap.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import html
import io
import json
import os
import re
import shutil
import tarfile
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from statistics import median
from typing import Any, Iterable, Iterator, Mapping, Sequence

USER_AGENT = "EAzami-Compositae1061-recovery/1.0"
MAX_BYTES = 300 * 1024 * 1024
DEFAULT_LOCI = Path(
    "data/evidence/generated/moreyra_author_repository/locus_sets/"
    "moreyra_public_1061_loci.txt"
)
DEFAULT_OUTDIR = Path("data/evidence/generated/compositae1061_target_audit")

STATIC_SOURCES = (
    ("mendeley_cardueae_landing", "https://data.mendeley.com/datasets/bhvv6rmyt6/1"),
    ("mendeley_processing_landing", "https://data.mendeley.com/datasets/hgpn6g27c6/1"),
    ("mendeley_cardueae_api", "https://api.mendeley.com/datasets/bhvv6rmyt6/versions/1"),
    ("mendeley_cardueae_files", "https://api.mendeley.com/datasets/bhvv6rmyt6/versions/1/files"),
    ("mendeley_processing_api", "https://api.mendeley.com/datasets/hgpn6g27c6/versions/1"),
    ("mendeley_processing_files", "https://api.mendeley.com/datasets/hgpn6g27c6/versions/1/files"),
    ("mendeley_cardueae_data_api", "https://data.mendeley.com/api/datasets/bhvv6rmyt6/versions/1"),
    ("mendeley_cardueae_data_files", "https://data.mendeley.com/api/datasets/bhvv6rmyt6/versions/1/files"),
    ("mendeley_processing_data_api", "https://data.mendeley.com/api/datasets/hgpn6g27c6/versions/1"),
    ("mendeley_processing_data_files", "https://data.mendeley.com/api/datasets/hgpn6g27c6/versions/1/files"),
    ("dryad_mandel_landing", "https://datadryad.org/dataset/doi:10.5061/dryad.gr93t"),
    ("dryad_mandel_api", "https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.gr93t"),
    ("datacite_compositae1061", "https://api.datacite.org/dois?query=Compositae1061&page[size]=100"),
    ("datacite_cardueae_hybseq", "https://api.datacite.org/dois?query=Cardueae%20Hyb-Seq&page[size]=100"),
)
GITHUB_QUERIES = (
    '"Compositae1061" in:file',
    'Compositae1061 extension:fasta',
    'Compositae1061 extension:fa',
    '"Compositae 1061" HybPiper target',
    '"1061" "HybPiper" extension:fasta',
)

FASTA_SUFFIXES = (".fa", ".fasta", ".fas", ".fna", ".faa", ".fa.gz", ".fasta.gz")
ARCHIVE_SUFFIXES = (".zip", ".tar", ".tar.gz", ".tgz", ".gz")
DISCOVERY_SUFFIXES = FASTA_SUFFIXES + ARCHIVE_SUFFIXES + (
    ".txt", ".tsv", ".csv", ".json", ".xlsx", ".docx"
)
TARGET_WORDS = ("compositae1061", "compositae_1061", "1061", "hybpiper", "target", "reference", "cos")
BAIT_WORDS = ("bait", "probe", "oligo", "mybaits")
DERIVED_WORDS = ("align", "concat", "supermatrix", "gene_tree", "genetree", "species_tree")

REQUEST_FIELDS = (
    "source_key", "url", "status", "content_type", "content_length",
    "final_url", "sha256", "error"
)
DISCOVERED_FIELDS = (
    "source_key", "url", "filename", "context", "score", "type_hint"
)
FASTA_FIELDS = (
    "candidate_key", "source_key", "source_url", "container_filename",
    "archive_member", "size_bytes", "sha256", "record_count",
    "unique_first_tokens", "total_bp", "min_length", "median_length",
    "max_length", "invalid_characters", "classification",
    "moreyra_exact_matches", "moreyra_normalized_matches",
    "moreyra_total_loci", "exact_overlap_fraction",
    "normalized_overlap_fraction", "provenance_class", "candidate_status",
    "notes"
)


@dataclass(frozen=True)
class Link:
    source_key: str
    url: str
    filename: str
    context: str


@dataclass
class Response:
    source_key: str
    requested_url: str
    status: str
    payload: bytes = b""
    content_type: str = ""
    content_length: str = ""
    final_url: str = ""
    headers: dict[str, str] | None = None
    error: str = ""


class HTMLLinks(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.values: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        for key in ("href", "src", "data-url", "data-download-url"):
            if values.get(key):
                self.values.append((values[key], f"html:{tag}:{key}"))


def clean(value: object) -> str:
    return str(value or "").strip()


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def safe_name(value: str, fallback: str = "download") -> str:
    value = urllib.parse.unquote(Path(urllib.parse.urlparse(value).path).name or value)
    value = re.sub(r"[^A-Za-z0-9._+-]+", "_", value).strip("._")
    return value or fallback


def download(
    key: str,
    url: str,
    token: str = "",
    timeout: int = 60,
    retries: int = 4,
    max_bytes: int = MAX_BYTES,
) -> Response:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json,text/html,application/octet-stream,*/*;q=0.8",
    }
    if token and "api.github.com" in url:
        headers["Authorization"] = f"Bearer {token}"
        headers["X-GitHub-Api-Version"] = "2022-11-28"
    for attempt in range(retries):
        try:
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=timeout) as handle:
                response_headers = {
                    name.casefold(): value for name, value in handle.headers.items()
                }
                declared = response_headers.get("content-length", "")
                if declared.isdigit() and int(declared) > max_bytes:
                    return Response(
                        key, url, "skipped_too_large", content_length=declared,
                        content_type=response_headers.get("content-type", ""),
                        final_url=handle.geturl(), headers=response_headers
                    )
                payload = handle.read(max_bytes + 1)
                if len(payload) > max_bytes:
                    return Response(
                        key, url, "skipped_too_large", content_length=str(len(payload)),
                        content_type=response_headers.get("content-type", ""),
                        final_url=handle.geturl(), headers=response_headers
                    )
                return Response(
                    key, url, "ok", payload,
                    response_headers.get("content-type", ""),
                    declared or str(len(payload)), handle.geturl(), response_headers
                )
        except urllib.error.HTTPError as exc:
            if exc.code in {401, 403, 404, 410} or attempt + 1 == retries:
                return Response(key, url, f"http_{exc.code}", error=str(exc))
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            if attempt + 1 == retries:
                return Response(key, url, "request_error", error=f"{type(exc).__name__}: {exc}")
        time.sleep(2**attempt)
    return Response(key, url, "request_error", error="unreachable")


def resolve(value: str, base: str) -> str | None:
    value = html.unescape(clean(value)).replace("\\/", "/")
    if not value or value.startswith(("mailto:", "javascript:", "data:")):
        return None
    if value.startswith("//"):
        value = "https:" + value
    url = urllib.parse.urljoin(base, value)
    return url if urllib.parse.urlparse(url).scheme in {"http", "https"} else None


def file_like(value: str) -> bool:
    path = urllib.parse.urlparse(value).path.casefold()
    return path.endswith(DISCOVERY_SUFFIXES) or any(
        token in value.casefold() for token in ("download", "file_stream", "public-files")
    )


def json_strings(value: Any, context: str = "json") -> Iterator[tuple[str, str]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            yield from json_strings(child, f"{context}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from json_strings(child, f"{context}[{index}]")
    elif isinstance(value, str):
        yield value, context


def dedupe_links(values: Iterable[Link]) -> list[Link]:
    output: list[Link] = []
    seen: set[tuple[str, str, str]] = set()
    for value in values:
        key = (value.source_key, value.url, value.filename.casefold())
        if key not in seen:
            seen.add(key)
            output.append(value)
    return output


def extract_links(response: Response) -> list[Link]:
    if response.status != "ok" or not response.payload:
        return []
    base = response.final_url or response.requested_url
    text = response.payload.decode("utf-8", errors="replace")
    links: list[Link] = []
    parsed: Any | None = None
    if "json" in response.content_type.casefold() or text.lstrip().startswith(("{", "[")):
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            parsed = None
    if parsed is not None:
        for value, context in json_strings(parsed):
            url = resolve(value, base)
            if url and file_like(url):
                links.append(Link(response.source_key, url, safe_name(url), context))
    if "html" in response.content_type.casefold() or "<html" in text[:2000].casefold():
        parser = HTMLLinks()
        try:
            parser.feed(text)
        except Exception:
            pass
        for value, context in parser.values:
            url = resolve(value, base)
            if url and file_like(url):
                links.append(Link(response.source_key, url, safe_name(url), context))
        for match in re.finditer(r"https?(?:\\/|/)[^\"'<>\s]+", text, re.I):
            url = resolve(match.group(0), base)
            if url and file_like(url):
                links.append(Link(response.source_key, url, safe_name(url), "embedded_url"))
    return dedupe_links(links)


def followup_api_links(response: Response) -> list[tuple[str, str]]:
    if response.status != "ok":
        return []
    try:
        parsed = json.loads(response.payload)
    except json.JSONDecodeError:
        return []
    output: list[tuple[str, str]] = []
    for value, _ in json_strings(parsed):
        url = resolve(value, response.final_url or response.requested_url)
        if url and any(token in url.casefold() for token in ("/versions/", "/files", "download")):
            output.append((f"followup_{response.source_key}_{len(output)+1}", url))
    return list(dict.fromkeys(output))[:100]


def github_links(token: str) -> tuple[list[Response], list[Link]]:
    responses: list[Response] = []
    links: list[Link] = []
    for index, query in enumerate(GITHUB_QUERIES, start=1):
        url = "https://api.github.com/search/code?" + urllib.parse.urlencode(
            {"q": query, "per_page": 100}
        )
        response = download(f"github_code_{index}", url, token)
        responses.append(response)
        if response.status != "ok":
            continue
        try:
            data = json.loads(response.payload)
        except json.JSONDecodeError:
            continue
        for item in data.get("items", []):
            path = clean(item.get("path"))
            repo = clean((item.get("repository") or {}).get("full_name"))
            direct = clean(item.get("download_url"))
            if direct:
                links.append(Link(response.source_key, direct, safe_name(path), f"github:{repo}:{path}"))
    return responses, dedupe_links(links)


def score(link: Link) -> int:
    text = f"{link.filename} {link.context}".casefold()
    value = 3 if text.endswith(FASTA_SUFFIXES) else 0
    value += sum(3 if word == "1061" else 1 for word in TARGET_WORDS if word in text)
    value += sum(1 for word in BAIT_WORDS if word in text)
    return value


def hint(link: Link) -> str:
    text = f"{link.filename} {link.context}".casefold()
    if any(word in text for word in BAIT_WORDS):
        return "bait_or_probe"
    if any(word in text for word in DERIVED_WORDS):
        return "derived_alignment_or_tree"
    if any(word in text for word in TARGET_WORDS):
        return "target_or_reference"
    if text.endswith(FASTA_SUFFIXES):
        return "generic_fasta"
    return "other"


def filename_from_response(response: Response, fallback_url: str) -> str:
    headers = response.headers or {}
    disposition = headers.get("content-disposition", "")
    match = re.search(r"filename\*?=(?:UTF-8''|\")?([^\";]+)", disposition, re.I)
    return safe_name(match.group(1)) if match else safe_name(response.final_url or fallback_url)


def fasta_payloads(filename: str, payload: bytes) -> Iterator[tuple[str, bytes]]:
    lower = filename.casefold()
    if payload.lstrip().startswith(b">"):
        yield "", payload
        return
    if lower.endswith(".gz") and not lower.endswith((".tar.gz", ".tgz")):
        try:
            unpacked = gzip.decompress(payload)
        except OSError:
            return
        if unpacked.lstrip().startswith(b">"):
            yield filename[:-3], unpacked
        return
    if payload.startswith(b"PK\x03\x04"):
        try:
            with zipfile.ZipFile(io.BytesIO(payload)) as archive:
                for member in archive.infolist():
                    if member.is_dir() or member.file_size > MAX_BYTES:
                        continue
                    if member.filename.casefold().endswith(FASTA_SUFFIXES):
                        yield member.filename, archive.read(member)
        except (zipfile.BadZipFile, RuntimeError):
            return
        return
    try:
        with tarfile.open(fileobj=io.BytesIO(payload), mode="r:*") as archive:
            for member in archive.getmembers():
                if not member.isfile() or member.size > MAX_BYTES:
                    continue
                if member.name.casefold().endswith(FASTA_SUFFIXES):
                    handle = archive.extractfile(member)
                    if handle:
                        yield member.name, handle.read()
    except (tarfile.TarError, OSError):
        return


def parse_fasta(payload: bytes) -> list[tuple[str, str]]:
    text = payload.decode("utf-8", errors="replace")
    records: list[tuple[str, str]] = []
    header = ""
    sequence: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith(">"):
            if header:
                records.append((header, "".join(sequence)))
            header, sequence = line[1:].strip(), []
        elif header:
            sequence.append(re.sub(r"\s+", "", line))
    if header:
        records.append((header, "".join(sequence)))
    return records


def normalize(value: str) -> str:
    value = html.unescape(clean(value)).casefold()
    value = value.split()[0] if value.split() else value
    value = re.sub(r"\.(?:fa|fasta|fas|fna|faa)$", "", value)
    return re.sub(r"[^a-z0-9]+", "", value)


def variants(header: str) -> set[str]:
    raw = clean(header).lstrip(">")
    pieces = {raw, raw.split()[0] if raw.split() else raw}
    for delimiter in ("|", ":", ";", ",", "_", "-"):
        pieces.update(part for piece in list(pieces) for part in piece.split(delimiter) if part)
    for match in re.finditer(r"[A-Za-z]*\d{3,}[A-Za-z0-9]*", raw):
        pieces.add(match.group(0))
    return {normalize(piece) for piece in pieces if normalize(piece)}


def provenance(link: Link) -> str:
    text = f"{link.source_key} {link.context} {link.filename}".casefold()
    if "mendeley" in text and any(value in text for value in ("bhvv6rmyt6", "hgpn6g27c6", "cardueae", "processing")):
        return "strong_cardueae_dataset"
    if "dryad" in text and "gr93t" in text:
        return "foundational_compositae_dataset"
    if "github" in text:
        return "public_github_needs_paper_link"
    if "datacite" in text:
        return "repository_metadata"
    return "unresolved"


def classify(filename: str, member: str, records: Sequence[tuple[str, str]], overlap: float) -> str:
    text = f"{filename} {member}".casefold()
    lengths = [len(sequence) for _, sequence in records]
    med = median(lengths) if lengths else 0
    if any(word in text for word in BAIT_WORDS) and med <= 250:
        return "bait_probe_fasta"
    if any(word in text for word in DERIVED_WORDS):
        return "derived_alignment_or_other_fasta"
    if any(word in text for word in TARGET_WORDS) and len(records) >= 800 and med >= 150:
        return "target_reference_candidate"
    if overlap >= 0.80 and med >= 150:
        return "target_reference_candidate"
    return "generic_or_unrelated_fasta"


def audit_candidate(
    key: str,
    link: Link,
    filename: str,
    member: str,
    payload: bytes,
    loci: Sequence[str],
) -> dict[str, object]:
    records = parse_fasta(payload)
    if not records:
        raise ValueError("not FASTA")
    lengths = [len(sequence) for _, sequence in records]
    first_tokens = {header.split()[0] if header.split() else header for header, _ in records}
    locus_set = set(loci)
    exact = first_tokens & locus_set
    normalized_loci = {normalize(locus): locus for locus in loci}
    matched: set[str] = set()
    for header, _ in records:
        for value in variants(header):
            if value in normalized_loci:
                matched.add(normalized_loci[value])
    exact_fraction = len(exact) / len(loci)
    normalized_fraction = len(matched) / len(loci)
    classification = classify(filename, member, records, normalized_fraction)
    source_class = provenance(link)
    if (
        classification == "target_reference_candidate"
        and source_class == "strong_cardueae_dataset"
        and normalized_fraction >= 0.95
    ):
        status = "high_confidence_candidate_method_confirmation_required"
    elif classification == "target_reference_candidate" and normalized_fraction >= 0.70:
        status = "compatible_target_candidate"
    elif classification == "bait_probe_fasta":
        status = "not_target_bait_or_probe"
    else:
        status = "not_selected_or_unresolved"
    allowed = set("ACGTURYSWKMBDHVN.-*XEFILPQZJO")
    invalid = "".join(sorted({char.upper() for _, seq in records for char in seq if char.upper() not in allowed}))
    return {
        "candidate_key": key,
        "source_key": link.source_key,
        "source_url": link.url,
        "container_filename": filename,
        "archive_member": member,
        "size_bytes": len(payload),
        "sha256": digest(payload),
        "record_count": len(records),
        "unique_first_tokens": len(first_tokens),
        "total_bp": sum(lengths),
        "min_length": min(lengths),
        "median_length": median(lengths),
        "max_length": max(lengths),
        "invalid_characters": invalid,
        "classification": classification,
        "moreyra_exact_matches": len(exact),
        "moreyra_normalized_matches": len(matched),
        "moreyra_total_loci": len(loci),
        "exact_overlap_fraction": f"{exact_fraction:.6f}",
        "normalized_overlap_fraction": f"{normalized_fraction:.6f}",
        "provenance_class": source_class,
        "candidate_status": status,
        "notes": "Sequence overlap alone does not prove exact Moreyra target identity.",
    }


def read_loci(path: Path) -> list[str]:
    values = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]
    if len(values) != len(set(values)) or not values:
        raise ValueError(f"Invalid locus list: {path}")
    return values


def write_csv(path: Path, rows: Iterable[Mapping[str, object]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--moreyra-loci", type=Path, default=DEFAULT_LOCI)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    parser.add_argument("--github-token", default=os.environ.get("GITHUB_TOKEN", ""))
    args = parser.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    source_dir = args.outdir / "downloaded_candidates"
    source_dir.mkdir(parents=True, exist_ok=True)
    loci = read_loci(args.moreyra_loci)

    responses: list[Response] = []
    links: list[Link] = []
    queue = list(STATIC_SOURCES)
    visited: set[str] = set()
    while queue:
        key, url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)
        response = download(key, url, args.github_token)
        responses.append(response)
        links.extend(extract_links(response))
        if len(visited) < 200:
            queue.extend((key2, url2) for key2, url2 in followup_api_links(response) if url2 not in visited)

    github_responses, github_found = github_links(args.github_token)
    responses.extend(github_responses)
    links.extend(github_found)
    links = dedupe_links(links)

    discovered_rows = [
        {
            "source_key": link.source_key,
            "url": link.url,
            "filename": link.filename,
            "context": link.context,
            "score": score(link),
            "type_hint": hint(link),
        }
        for link in links
    ]
    discovered_rows.sort(key=lambda row: (-int(row["score"]), row["source_key"], row["filename"]))

    fasta_rows: list[dict[str, object]] = []
    attempted: set[str] = set()
    download_responses: list[Response] = []
    for link in sorted(links, key=lambda item: (-score(item), item.url)):
        if link.url in attempted:
            continue
        attempted.add(link.url)
        if score(link) < 2 and hint(link) not in {"generic_fasta", "target_or_reference", "bait_or_probe"}:
            continue
        response = download(f"candidate_{len(download_responses)+1}", link.url, args.github_token)
        download_responses.append(response)
        if response.status != "ok" or not response.payload:
            continue
        filename = filename_from_response(response, link.url)
        (source_dir / f"{len(download_responses):04d}_{safe_name(filename)}").write_bytes(response.payload)
        for member, fasta in fasta_payloads(filename, response.payload):
            if not fasta.lstrip().startswith(b">"):
                continue
            key = f"fasta_{len(fasta_rows)+1:04d}"
            try:
                row = audit_candidate(key, link, filename, member, fasta, loci)
            except ValueError:
                continue
            fasta_rows.append(row)
            (source_dir / f"{key}_{safe_name(member or filename)}").write_bytes(fasta)

    request_rows = [
        {
            "source_key": response.source_key,
            "url": response.requested_url,
            "status": response.status,
            "content_type": response.content_type,
            "content_length": response.content_length,
            "final_url": response.final_url,
            "sha256": digest(response.payload) if response.payload else "",
            "error": response.error,
        }
        for response in responses + download_responses
    ]
    fasta_rows.sort(key=lambda row: (-float(row["normalized_overlap_fraction"]), -int(row["record_count"])))
    high = [row for row in fasta_rows if row["candidate_status"] == "high_confidence_candidate_method_confirmation_required"]
    compatible = [row for row in fasta_rows if row["candidate_status"] == "compatible_target_candidate"]
    best = high[0] if high else compatible[0] if compatible else None
    status = (
        "high_confidence_candidate_recovered_method_confirmation_required" if high
        else "compatible_candidate_recovered_not_exact" if compatible
        else "exact_or_compatible_target_not_recovered"
    )
    summary = {
        "audit_status": status,
        "source_requests": len(responses),
        "successful_source_requests": sum(response.status == "ok" for response in responses),
        "discovered_files": len(discovered_rows),
        "download_attempts": len(download_responses),
        "fasta_candidates": len(fasta_rows),
        "moreyra_locus_ids": len(loci),
        "high_confidence_candidates": len(high),
        "compatible_candidates": len(compatible),
        "best_candidate": best,
        "exact_target_frozen": False,
        "freeze_rule": "Source/method confirmation is required in addition to FASTA overlap.",
        "sources": [key for key, _ in STATIC_SOURCES] + [f"github:{query}" for query in GITHUB_QUERIES],
    }
    write_csv(args.outdir / "source_request_log.csv", request_rows, REQUEST_FIELDS)
    write_csv(args.outdir / "discovered_files.csv", discovered_rows, DISCOVERED_FIELDS)
    write_csv(args.outdir / "fasta_candidate_audit.csv", fasta_rows, FASTA_FIELDS)
    (args.outdir / "audit_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"audit_status={status}")
    print(f"source_requests={summary['source_requests']}")
    print(f"successful_source_requests={summary['successful_source_requests']}")
    print(f"discovered_files={summary['discovered_files']}")
    print(f"download_attempts={summary['download_attempts']}")
    print(f"fasta_candidates={summary['fasta_candidates']}")
    print(f"high_confidence_candidates={len(high)}")
    print(f"compatible_candidates={len(compatible)}")
    if best:
        print(f"best_candidate={best['container_filename']}::{best['archive_member']} overlap={best['normalized_overlap_fraction']}")
    print(args.outdir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
