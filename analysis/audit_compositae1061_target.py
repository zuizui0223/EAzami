#!/usr/bin/env python3
"""Discover, validate and compare public Compositae1061 FASTA candidates.

The script audits official/public dataset pages and APIs rather than relying on a
single remembered file name.  It distinguishes target/reference FASTA files from
bait/probe oligos and derived alignments, records checksums and compares candidate
header/locus identifiers with the 1,061 public Moreyra locus IDs.

A candidate is never called the exact Moreyra target from sequence counts alone.
Exact status additionally requires source metadata linking the file to the panel
or analysis.  When no exact target is recovered, the output is an explicit,
versioned unresolved decision rather than an invented target choice.
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
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from statistics import median
from typing import Any, Iterable, Iterator, Mapping, Sequence

DEFAULT_OUTDIR = Path("data/evidence/generated/compositae1061_target_audit")
DEFAULT_MOREYRA_LOCI = Path(
    "data/evidence/generated/moreyra_author_repository/locus_sets/"
    "moreyra_public_1061_loci.txt"
)
MAX_DOWNLOAD_BYTES = 300 * 1024 * 1024
USER_AGENT = "EAzami-Compositae1061-target-audit/1.0"

FASTA_EXTENSIONS = (
    ".fa",
    ".fasta",
    ".fas",
    ".fna",
    ".faa",
    ".fa.gz",
    ".fasta.gz",
    ".fas.gz",
)
ARCHIVE_EXTENSIONS = (".zip", ".tar", ".tar.gz", ".tgz", ".gz")
FILE_EXTENSIONS = FASTA_EXTENSIONS + ARCHIVE_EXTENSIONS + (
    ".txt",
    ".tsv",
    ".csv",
    ".json",
    ".xlsx",
    ".docx",
)

SOURCE_ENDPOINTS = (
    # Herrando-Moraira Cardueae datasets.
    ("mendeley_cardueae_landing", "https://data.mendeley.com/datasets/bhvv6rmyt6/1"),
    ("mendeley_processing_landing", "https://data.mendeley.com/datasets/hgpn6g27c6/1"),
    ("mendeley_cardueae_api_v1", "https://api.mendeley.com/datasets/bhvv6rmyt6/versions/1"),
    ("mendeley_cardueae_api_files", "https://api.mendeley.com/datasets/bhvv6rmyt6/versions/1/files"),
    ("mendeley_processing_api_v1", "https://api.mendeley.com/datasets/hgpn6g27c6/versions/1"),
    ("mendeley_processing_api_files", "https://api.mendeley.com/datasets/hgpn6g27c6/versions/1/files"),
    ("mendeley_cardueae_data_api", "https://data.mendeley.com/api/datasets/bhvv6rmyt6/versions/1"),
    ("mendeley_cardueae_data_api_files", "https://data.mendeley.com/api/datasets/bhvv6rmyt6/versions/1/files"),
    ("mendeley_processing_data_api", "https://data.mendeley.com/api/datasets/hgpn6g27c6/versions/1"),
    ("mendeley_processing_data_api_files", "https://data.mendeley.com/api/datasets/hgpn6g27c6/versions/1/files"),
    # Foundational Compositae Dryad dataset.
    (
        "dryad_mandel_landing",
        "https://datadryad.org/dataset/doi:10.5061/dryad.gr93t",
    ),
    (
        "dryad_mandel_api",
        "https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.gr93t",
    ),
    # DataCite discovery for related deposits.
    (
        "datacite_compositae1061",
        "https://api.datacite.org/dois?query=Compositae1061&page[size]=100",
    ),
    (
        "datacite_cardueae_hybseq",
        "https://api.datacite.org/dois?query=Cardueae%20Hyb-Seq&page[size]=100",
    ),
)

GITHUB_CODE_QUERIES = (
    '"Compositae1061" in:file',
    'Compositae1061 extension:fasta',
    'Compositae1061 extension:fa',
    'Compositae1061 target HybPiper',
    '"1061" "HybPiper" extension:fasta',
)
GITHUB_REPOSITORY_QUERIES = (
    "Compositae1061",
    '"Compositae 1061" target',
    "Cardueae Hyb-Seq",
)

TARGET_KEYWORDS = (
    "compositae1061",
    "compositae_1061",
    "compositae-1061",
    "1061target",
    "1061_target",
    "target1061",
    "target_file",
    "targetfile",
    "hybpiper",
    "targets",
    "target",
    "reference",
    "cos",
)
BAIT_KEYWORDS = ("bait", "probe", "oligo", "mybaits", "capture_probe")
DERIVED_KEYWORDS = (
    "alignment",
    "aligned",
    "concat",
    "supermatrix",
    "gene_tree",
    "genetree",
    "species_tree",
    "newick",
)

REQUEST_FIELDS = (
    "source_key",
    "url",
    "status",
    "content_type",
    "content_length",
    "final_url",
    "response_sha256",
    "discovered_url_count",
    "error",
)
DISCOVERED_FIELDS = (
    "source_key",
    "discovered_url",
    "suggested_filename",
    "discovery_context",
    "keyword_score",
    "candidate_type_hint",
)
FASTA_FIELDS = (
    "candidate_key",
    "source_key",
    "source_url",
    "download_url",
    "container_filename",
    "archive_member",
    "file_size_bytes",
    "sha256",
    "record_count",
    "unique_first_tokens",
    "sequence_total_bp",
    "min_length",
    "median_length",
    "max_length",
    "invalid_sequence_characters",
    "filename_keyword_score",
    "classification",
    "moreyra_exact_token_matches",
    "moreyra_normalized_matches",
    "moreyra_total_loci",
    "exact_overlap_fraction",
    "normalized_overlap_fraction",
    "provenance_strength",
    "selection_status",
    "notes",
)


@dataclass
class RequestResult:
    source_key: str
    url: str
    status: str
    content_type: str = ""
    content_length: str = ""
    final_url: str = ""
    payload: bytes = b""
    error: str = ""
    headers: dict[str, str] = field(default_factory=dict)


@dataclass
class DiscoveredURL:
    source_key: str
    url: str
    filename: str
    context: str


@dataclass
class FastaRecord:
    header: str
    sequence: str


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._text: list[str] = []
        self._current_attrs: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        for key in ("href", "src", "data-url", "data-download-url"):
            if values.get(key):
                self.links.append((values[key], f"html:{tag}:{key}"))
        self._current_attrs = values

    def handle_data(self, data: str) -> None:
        if data.strip():
            self._text.append(data.strip())


def clean(value: object) -> str:
    return str(value or "").strip()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_filename(value: str, fallback: str = "download") -> str:
    value = urllib.parse.unquote(value)
    value = Path(value).name
    value = re.sub(r"[^A-Za-z0-9._+-]+", "_", value).strip("._")
    return value or fallback


def filename_from_headers(url: str, headers: Mapping[str, str]) -> str:
    disposition = headers.get("content-disposition", "")
    match = re.search(r"filename\*?=(?:UTF-8''|\")?([^\";]+)", disposition, re.I)
    if match:
        return safe_filename(match.group(1))
    path = urllib.parse.urlparse(url).path
    return safe_filename(path, "download")


def request_bytes(
    source_key: str,
    url: str,
    *,
    token: str = "",
    timeout: int = 60,
    retries: int = 4,
    max_bytes: int = MAX_DOWNLOAD_BYTES,
) -> RequestResult:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json,text/html,application/octet-stream,*/*;q=0.8",
    }
    if token and "api.github.com" in url:
        headers["Authorization"] = f"Bearer {token}"
        headers["X-GitHub-Api-Version"] = "2022-11-28"
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                response_headers = {
                    key.casefold(): value for key, value in response.headers.items()
                }
                declared = response_headers.get("content-length", "")
                if declared.isdigit() and int(declared) > max_bytes:
                    return RequestResult(
                        source_key,
                        url,
                        "skipped_too_large",
                        response_headers.get("content-type", ""),
                        declared,
                        response.geturl(),
                        headers=response_headers,
                    )
                payload = response.read(max_bytes + 1)
                if len(payload) > max_bytes:
                    return RequestResult(
                        source_key,
                        url,
                        "skipped_too_large",
                        response_headers.get("content-type", ""),
                        str(len(payload)),
                        response.geturl(),
                        headers=response_headers,
                    )
                return RequestResult(
                    source_key=source_key,
                    url=url,
                    status="ok",
                    content_type=response_headers.get("content-type", ""),
                    content_length=declared or str(len(payload)),
                    final_url=response.geturl(),
                    payload=payload,
                    headers=response_headers,
                )
        except urllib.error.HTTPError as exc:
            if exc.code in {401, 403, 404, 410}:
                return RequestResult(
                    source_key,
                    url,
                    f"http_{exc.code}",
                    error=f"HTTPError: {exc}",
                )
            if attempt + 1 == retries:
                return RequestResult(
                    source_key,
                    url,
                    f"http_{exc.code}",
                    error=f"HTTPError: {exc}",
                )
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            if attempt + 1 == retries:
                return RequestResult(
                    source_key,
                    url,
                    "request_error",
                    error=f"{type(exc).__name__}: {exc}",
                )
        time.sleep(2**attempt)
    return RequestResult(source_key, url, "request_error", error="unreachable")


def iter_json_strings(value: Any, context: str = "json") -> Iterator[tuple[str, str]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            yield from iter_json_strings(child, f"{context}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_json_strings(child, f"{context}[{index}]")
    elif isinstance(value, str):
        yield value, context


def looks_file_like(value: str) -> bool:
    lowered = value.casefold().split("?", 1)[0]
    return any(lowered.endswith(ext) for ext in FILE_EXTENSIONS) or any(
        keyword in lowered for keyword in ("download", "file_stream", "public-files")
    )


def resolve_url(value: str, base_url: str) -> str | None:
    value = html.unescape(clean(value)).replace("\\/", "/")
    if not value or value.startswith(("mailto:", "javascript:", "data:")):
        return None
    if value.startswith("//"):
        value = "https:" + value
    resolved = urllib.parse.urljoin(base_url, value)
    parsed = urllib.parse.urlparse(resolved)
    if parsed.scheme not in {"http", "https"}:
        return None
    return resolved


def discover_from_payload(result: RequestResult) -> list[DiscoveredURL]:
    if result.status != "ok" or not result.payload:
        return []
    text = result.payload.decode("utf-8", errors="replace")
    candidates: list[DiscoveredURL] = []
    content_type = result.content_type.casefold()
    parsed_json: Any | None = None
    if "json" in content_type or text.lstrip().startswith(("{", "[")):
        try:
            parsed_json = json.loads(text)
        except json.JSONDecodeError:
            parsed_json = None
    if parsed_json is not None:
        for value, context in iter_json_strings(parsed_json):
            resolved = resolve_url(value, result.final_url or result.url)
            if resolved and looks_file_like(resolved):
                candidates.append(
                    DiscoveredURL(
                        result.source_key,
                        resolved,
                        safe_filename(urllib.parse.urlparse(resolved).path),
                        context,
                    )
                )
            elif looks_file_like(value):
                # Preserve a file name next to a separately discovered URL in the audit.
                candidates.append(
                    DiscoveredURL(result.source_key, "", safe_filename(value), context)
                )
    if "html" in content_type or "<html" in text[:2000].casefold():
        parser = LinkParser()
        try:
            parser.feed(text)
        except Exception:
            pass
        for value, context in parser.links:
            resolved = resolve_url(value, result.final_url or result.url)
            if resolved and looks_file_like(resolved):
                candidates.append(
                    DiscoveredURL(
                        result.source_key,
                        resolved,
                        safe_filename(urllib.parse.urlparse(resolved).path),
                        context,
                    )
                )
        # Modern dataset pages often embed escaped download URLs in script JSON.
        for match in re.finditer(
            r"https?(?:\\/|/)[^\"'<>\s]+", text, flags=re.I
        ):
            resolved = resolve_url(match.group(0), result.final_url or result.url)
            if resolved and looks_file_like(resolved):
                candidates.append(
                    DiscoveredURL(
                        result.source_key,
                        resolved,
                        safe_filename(urllib.parse.urlparse(resolved).path),
                        "html_embedded_url",
                    )
                )
    return dedupe_discovered(candidates)


def dedupe_discovered(values: Iterable[DiscoveredURL]) -> list[DiscoveredURL]:
    output: list[DiscoveredURL] = []
    seen: set[tuple[str, str, str]] = set()
    for value in values:
        key = (value.source_key, value.url, value.filename.casefold())
        if key not in seen:
            seen.add(key)
            output.append(value)
    return output


def keyword_score(filename: str, context: str = "") -> int:
    text = f"{filename} {context}".casefold()
    score = 0
    for keyword in TARGET_KEYWORDS:
        if keyword in text:
            score += 3 if "1061" in keyword else 1
    for keyword in BAIT_KEYWORDS:
        if keyword in text:
            score += 1
    if any(text.split("?", 1)[0].endswith(ext) for ext in FASTA_EXTENSIONS):
        score += 3
    if any(text.split("?", 1)[0].endswith(ext) for ext in ARCHIVE_EXTENSIONS):
        score += 1
    return score


def candidate_hint(filename: str, context: str = "") -> str:
    text = f"{filename} {context}".casefold()
    if any(keyword in text for keyword in BAIT_KEYWORDS):
        return "bait_or_probe_candidate"
    if any(keyword in text for keyword in DERIVED_KEYWORDS):
        return "derived_alignment_or_tree_candidate"
    if any(keyword in text for keyword in TARGET_KEYWORDS):
        return "target_or_reference_candidate"
    if any(text.split("?", 1)[0].endswith(ext) for ext in FASTA_EXTENSIONS):
        return "generic_fasta_candidate"
    return "other_file_candidate"


def github_discovery(token: str) -> tuple[list[RequestResult], list[DiscoveredURL]]:
    requests: list[RequestResult] = []
    discovered: list[DiscoveredURL] = []
    for index, query in enumerate(GITHUB_CODE_QUERIES, start=1):
        url = "https://api.github.com/search/code?" + urllib.parse.urlencode(
            {"q": query, "per_page": 100}
        )
        result = request_bytes(f"github_code_{index}", url, token=token)
        requests.append(result)
        if result.status != "ok":
            continue
        try:
            data = json.loads(result.payload)
        except json.JSONDecodeError:
            continue
        for item in data.get("items", []):
            download_url = clean(item.get("download_url"))
            html_url = clean(item.get("html_url"))
            path = clean(item.get("path"))
            repository = clean((item.get("repository") or {}).get("full_name"))
            if download_url:
                discovered.append(
                    DiscoveredURL(
                        result.source_key,
                        download_url,
                        safe_filename(path),
                        f"github:{repository}:{path}",
                    )
                )
            elif html_url and looks_file_like(path):
                discovered.append(
                    DiscoveredURL(
                        result.source_key,
                        html_url,
                        safe_filename(path),
                        f"github_html:{repository}:{path}",
                    )
                )
    for index, query in enumerate(GITHUB_REPOSITORY_QUERIES, start=1):
        url = "https://api.github.com/search/repositories?" + urllib.parse.urlencode(
            {"q": query, "per_page": 50}
        )
        result = request_bytes(f"github_repo_{index}", url, token=token)
        requests.append(result)
        if result.status != "ok":
            continue
        try:
            data = json.loads(result.payload)
        except json.JSONDecodeError:
            continue
        for repo in data.get("items", []):
            full_name = clean(repo.get("full_name"))
            default_branch = clean(repo.get("default_branch")) or "main"
            if not full_name:
                continue
            tree_url = (
                f"https://api.github.com/repos/{full_name}/git/trees/"
                f"{urllib.parse.quote(default_branch)}?recursive=1"
            )
            tree_result = request_bytes(
                f"github_tree_{full_name.replace('/', '_')}", tree_url, token=token
            )
            requests.append(tree_result)
            if tree_result.status != "ok":
                continue
            try:
                tree = json.loads(tree_result.payload)
            except json.JSONDecodeError:
                continue
            for entry in tree.get("tree", []):
                path = clean(entry.get("path"))
                if entry.get("type") != "blob" or not looks_file_like(path):
                    continue
                raw_url = (
                    f"https://raw.githubusercontent.com/{full_name}/"
                    f"{urllib.parse.quote(default_branch)}/{urllib.parse.quote(path)}"
                )
                discovered.append(
                    DiscoveredURL(
                        tree_result.source_key,
                        raw_url,
                        safe_filename(path),
                        f"github_tree:{full_name}:{path}",
                    )
                )
    return requests, dedupe_discovered(discovered)


def additional_api_links(result: RequestResult) -> list[tuple[str, str]]:
    """Find follow-up API URLs such as Dryad version/file endpoints."""
    if result.status != "ok":
        return []
    try:
        data = json.loads(result.payload)
    except json.JSONDecodeError:
        return []
    output: list[tuple[str, str]] = []
    for value, context in iter_json_strings(data):
        resolved = resolve_url(value, result.final_url or result.url)
        if not resolved:
            continue
        lowered = resolved.casefold()
        if any(token in lowered for token in ("/versions/", "/files", "download")):
            output.append((f"followup_{result.source_key}_{len(output)+1}", resolved))
    return list(dict.fromkeys(output))


def read_moreyra_loci(path: Path) -> list[str]:
    loci = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    if not loci:
        raise ValueError(f"{path}: no Moreyra locus IDs")
    if len(loci) != len(set(loci)):
        raise ValueError(f"{path}: duplicate Moreyra locus IDs")
    return loci


def normalize_identifier(value: str) -> str:
    value = html.unescape(clean(value)).casefold()
    value = value.split()[0] if value.split() else value
    value = re.sub(r"\.(fa|fasta|fas|fna|faa)$", "", value)
    value = re.sub(r"[^a-z0-9]+", "", value)
    return value


def header_identifier_variants(header: str) -> set[str]:
    raw = clean(header).lstrip(">")
    first = raw.split()[0] if raw.split() else raw
    pieces = {raw, first}
    for delimiter in ("|", ":", ";", ","):
        for piece in list(pieces):
            pieces.update(part for part in piece.split(delimiter) if part)
    for piece in list(pieces):
        pieces.update(part for part in re.split(r"[_-]+", piece) if part)
    variants = {normalize_identifier(piece) for piece in pieces}
    # Include obvious numeric/gene-ID components but avoid one- and two-digit noise.
    for match in re.finditer(r"[A-Za-z]*\d{3,}[A-Za-z0-9]*", raw):
        variants.add(normalize_identifier(match.group(0)))
    return {value for value in variants if value}


def parse_fasta(payload: bytes) -> list[FastaRecord]:
    text = payload.decode("utf-8", errors="replace")
    records: list[FastaRecord] = []
    header = ""
    sequence: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            if header:
                records.append(FastaRecord(header, "".join(sequence)))
            header = line[1:].strip()
            sequence = []
        elif header:
            sequence.append(re.sub(r"\s+", "", line))
    if header:
        records.append(FastaRecord(header, "".join(sequence)))
    return records


def is_fasta_payload(payload: bytes) -> bool:
    head = payload[:8192].lstrip()
    return head.startswith(b">") and b"\n" in head


def decompress_candidates(
    filename: str, payload: bytes
) -> Iterator[tuple[str, bytes]]:
    lower = filename.casefold()
    if is_fasta_payload(payload):
        yield "", payload
        return
    if lower.endswith(".gz") and not lower.endswith((".tar.gz", ".tgz")):
        try:
            decompressed = gzip.decompress(payload)
        except OSError:
            return
        member_name = filename[:-3]
        if is_fasta_payload(decompressed) or any(
            member_name.casefold().endswith(ext) for ext in FASTA_EXTENSIONS
        ):
            yield member_name, decompressed
        return
    if payload.startswith(b"PK\x03\x04"):
        try:
            with zipfile.ZipFile(io.BytesIO(payload)) as archive:
                for info in archive.infolist():
                    if info.is_dir() or info.file_size > MAX_DOWNLOAD_BYTES:
                        continue
                    name = info.filename
                    if any(name.casefold().endswith(ext) for ext in FASTA_EXTENSIONS):
                        yield name, archive.read(info)
        except (zipfile.BadZipFile, RuntimeError):
            return
        return
    if tarfile.is_tarfile(fileobj := io.BytesIO(payload)):
        fileobj.seek(0)
        try:
            with tarfile.open(fileobj=fileobj, mode="r:*") as archive:
                for member in archive.getmembers():
                    if not member.isfile() or member.size > MAX_DOWNLOAD_BYTES:
                        continue
                    if any(member.name.casefold().endswith(ext) for ext in FASTA_EXTENSIONS):
                        extracted = archive.extractfile(member)
                        if extracted:
                            yield member.name, extracted.read()
        except tarfile.TarError:
            return


def invalid_sequence_characters(records: Sequence[FastaRecord]) -> str:
    allowed = set("ACGTURYSWKMBDHVN.-*XEFILPQZJO")
    invalid = sorted(
        {
            char.upper()
            for record in records
            for char in record.sequence
            if char.upper() not in allowed
        }
    )
    return "".join(invalid)


def classify_fasta(
    filename: str,
    archive_member: str,
    records: Sequence[FastaRecord],
    normalized_overlap_fraction: float,
) -> str:
    text = f"{filename} {archive_member}".casefold()
    lengths = [len(record.sequence) for record in records if record.sequence]
    med = median(lengths) if lengths else 0
    if any(keyword in text for keyword in BAIT_KEYWORDS) and med <= 250:
        return "bait_probe_fasta"
    if any(keyword in text for keyword in DERIVED_KEYWORDS):
        return "derived_alignment_or_other_fasta"
    if (
        any(keyword in text for keyword in TARGET_KEYWORDS)
        and 800 <= len(records) <= 10000
        and med >= 150
    ):
        return "target_reference_fasta_candidate"
    if normalized_overlap_fraction >= 0.80 and med >= 150:
        return "target_reference_fasta_candidate"
    if len(records) >= 800 and med >= 150:
        return "large_reference_or_alignment_fasta"
    return "generic_or_unrelated_fasta"


def provenance_strength(source_key: str, context: str, filename: str) -> str:
    text = f"{source_key} {context} {filename}".casefold()
    if "mendeley" in text and any(
        token in text for token in ("bhvv6rmyt6", "cardueae", "processing")
    ):
        return "strong_dataset_provenance"
    if "dryad" in text and "gr93t" in text:
        return "foundational_dataset_provenance"
    if "github" in text:
        return "public_repository_provenance_needs_paper_link"
    if "datacite" in text:
        return "repository_metadata_provenance"
    return "weak_or_unresolved_provenance"


def selection_status(
    classification: str,
    provenance: str,
    normalized_overlap: float,
    record_count: int,
) -> str:
    if (
        classification == "target_reference_fasta_candidate"
        and provenance == "strong_dataset_provenance"
        and normalized_overlap >= 0.95
        and 900 <= record_count <= 10000
    ):
        return "high_confidence_panel_target_candidate_requires_method_confirmation"
    if classification == "target_reference_fasta_candidate" and normalized_overlap >= 0.70:
        return "compatible_target_candidate"
    if classification == "bait_probe_fasta":
        return "not_hybpiper_target_bait_or_probe"
    return "not_selected_or_unresolved"


def audit_fasta_candidate(
    candidate_key: str,
    discovered: DiscoveredURL,
    download_result: RequestResult,
    filename: str,
    archive_member: str,
    payload: bytes,
    moreyra_loci: Sequence[str],
) -> dict[str, object]:
    records = parse_fasta(payload)
    if not records:
        raise ValueError("No FASTA records")
    lengths = [len(record.sequence) for record in records]
    first_tokens = {
        record.header.split()[0] if record.header.split() else record.header
        for record in records
    }
    exact_tokens = {token for token in first_tokens if token in set(moreyra_loci)}
    normalized_moreyra = {
        normalize_identifier(locus): locus for locus in moreyra_loci
    }
    matched_normalized: set[str] = set()
    for record in records:
        variants = header_identifier_variants(record.header)
        matched_normalized.update(
            normalized_moreyra[value]
            for value in variants
            if value in normalized_moreyra
        )
    exact_fraction = len(exact_tokens) / len(moreyra_loci)
    normalized_fraction = len(matched_normalized) / len(moreyra_loci)
    classification = classify_fasta(
        filename, archive_member, records, normalized_fraction
    )
    provenance = provenance_strength(
        discovered.source_key, discovered.context, filename
    )
    status = selection_status(
        classification, provenance, normalized_fraction, len(records)
    )
    return {
        "candidate_key": candidate_key,
        "source_key": discovered.source_key,
        "source_url": discovered.url,
        "download_url": download_result.final_url or discovered.url,
        "container_filename": filename,
        "archive_member": archive_member,
        "file_size_bytes": len(payload),
        "sha256": sha256_bytes(payload),
        "record_count": len(records),
        "unique_first_tokens": len(first_tokens),
        "sequence_total_bp": sum(lengths),
        "min_length": min(lengths),
        "median_length": median(lengths),
        "max_length": max(lengths),
        "invalid_sequence_characters": invalid_sequence_characters(records),
        "filename_keyword_score": keyword_score(filename, discovered.context),
        "classification": classification,
        "moreyra_exact_token_matches": len(exact_tokens),
        "moreyra_normalized_matches": len(matched_normalized),
        "moreyra_total_loci": len(moreyra_loci),
        "exact_overlap_fraction": f"{exact_fraction:.6f}",
        "normalized_overlap_fraction": f"{normalized_fraction:.6f}",
        "provenance_strength": provenance,
        "selection_status": status,
        "notes": (
            "Sequence structure alone cannot prove exact Moreyra target identity; "
            "methods/source metadata are required."
        ),
    }


def write_csv(path: Path, rows: Iterable[Mapping[str, object]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def save_payload(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--moreyra-loci", type=Path, default=DEFAULT_MOREYRA_LOCI)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    parser.add_argument("--github-token", default=os.environ.get("GITHUB_TOKEN", ""))
    parser.add_argument("--max-download-bytes", type=int, default=MAX_DOWNLOAD_BYTES)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    source_dir = args.outdir / "source_candidates"
    source_dir.mkdir(parents=True, exist_ok=True)
    moreyra_loci = read_moreyra_loci(args.moreyra_loci)

    request_results: list[RequestResult] = []
    discovered: list[DiscoveredURL] = []
    pending = list(SOURCE_ENDPOINTS)
    visited: set[str] = set()
    while pending:
        source_key, url = pending.pop(0)
        if url in visited:
            continue
        visited.add(url)
        result = request_bytes(
            source_key,
            url,
            token=args.github_token,
            max_bytes=args.max_download_bytes,
        )
        request_results.append(result)
        discovered.extend(discover_from_payload(result))
        for follow_key, follow_url in additional_api_links(result):
            if follow_url not in visited and len(pending) < 200:
                pending.append((follow_key, follow_url))

    github_requests, github_discovered = github_discovery(args.github_token)
    request_results.extend(github_requests)
    discovered.extend(github_discovered)
    discovered = dedupe_discovered(discovered)

    # Retain file-name-only discoveries in the audit, but only URLs can be downloaded.
    discovered_rows = []
    for item in discovered:
        discovered_rows.append(
            {
                "source_key": item.source_key,
                "discovered_url": item.url,
                "suggested_filename": item.filename,
                "discovery_context": item.context,
                "keyword_score": keyword_score(item.filename, item.context),
                "candidate_type_hint": candidate_hint(item.filename, item.context),
            }
        )
    discovered_rows.sort(
        key=lambda row: (-int(row["keyword_score"]), row["source_key"], row["suggested_filename"])
    )

    fasta_rows: list[dict[str, object]] = []
    download_results: list[RequestResult] = []
    downloaded_urls: set[str] = set()
    for item in sorted(
        (value for value in discovered if value.url),
        key=lambda value: (-keyword_score(value.filename, value.context), value.url),
    ):
        score = keyword_score(item.filename, item.context)
        hint = candidate_hint(item.filename, item.context)
        if score < 2 and hint not in {
            "generic_fasta_candidate",
            "target_or_reference_candidate",
            "bait_or_probe_candidate",
        }:
            continue
        if item.url in downloaded_urls:
            continue
        downloaded_urls.add(item.url)
        result = request_bytes(
            f"download_{item.source_key}_{len(download_results)+1}",
            item.url,
            token=args.github_token,
            max_bytes=args.max_download_bytes,
        )
        download_results.append(result)
        if result.status != "ok" or not result.payload:
            continue
        filename = filename_from_headers(
            result.final_url or item.url, result.headers
        )
        save_payload(
            source_dir / f"{len(download_results):04d}_{safe_filename(filename)}",
            result.payload,
        )
        for member_index, (member_name, fasta_payload) in enumerate(
            decompress_candidates(filename, result.payload), start=1
        ):
            if not is_fasta_payload(fasta_payload):
                continue
            candidate_key = f"fasta_{len(fasta_rows)+1:04d}"
            try:
                row = audit_fasta_candidate(
                    candidate_key,
                    item,
                    result,
                    filename,
                    member_name,
                    fasta_payload,
                    moreyra_loci,
                )
            except ValueError:
                continue
            fasta_rows.append(row)
            save_payload(
                source_dir
                / "extracted_fasta"
                / f"{candidate_key}_{safe_filename(member_name or filename)}",
                fasta_payload,
            )

    all_requests = request_results + download_results
    request_rows = []
    discovery_counts = Counter(item.source_key for item in discovered)
    for result in all_requests:
        request_rows.append(
            {
                "source_key": result.source_key,
                "url": result.url,
                "status": result.status,
                "content_type": result.content_type,
                "content_length": result.content_length,
                "final_url": result.final_url,
                "response_sha256": sha256_bytes(result.payload) if result.payload else "",
                "discovered_url_count": discovery_counts.get(result.source_key, 0),
                "error": result.error,
            }
        )

    fasta_rows.sort(
        key=lambda row: (
            -float(row["normalized_overlap_fraction"]),
            -int(row["filename_keyword_score"]),
            -int(row["record_count"]),
        )
    )
    selected = [
        row
        for row in fasta_rows
        if row["selection_status"]
        == "high_confidence_panel_target_candidate_requires_method_confirmation"
    ]
    compatible = [
        row
        for row in fasta_rows
        if row["selection_status"] == "compatible_target_candidate"
    ]
    if selected:
        overall_status = "high_confidence_candidate_recovered_method_confirmation_required"
        best = selected[0]
    elif compatible:
        overall_status = "compatible_target_candidate_recovered_not_exact"
        best = compatible[0]
    else:
        overall_status = "exact_or_compatible_target_not_recovered"
        best = None

    summary = {
        "audit_status": overall_status,
        "source_endpoints_requested": len(request_results),
        "successful_source_requests": sum(
            result.status == "ok" for result in request_results
        ),
        "discovered_file_candidates": len(discovered_rows),
        "download_attempts": len(download_results),
        "fasta_candidates_audited": len(fasta_rows),
        "moreyra_locus_ids": len(moreyra_loci),
        "high_confidence_candidates": len(selected),
        "compatible_candidates": len(compatible),
        "best_candidate": best,
        "exact_moreyra_target_frozen": False,
        "exact_freeze_rule": (
            "A sequence/overlap match is insufficient; source metadata or methods must "
            "confirm the exact target/reference file and version."
        ),
        "sources_audited": [key for key, _ in SOURCE_ENDPOINTS]
        + [f"github_code:{query}" for query in GITHUB_CODE_QUERIES]
        + [f"github_repository:{query}" for query in GITHUB_REPOSITORY_QUERIES],
    }

    write_csv(args.outdir / "source_request_log.csv", request_rows, REQUEST_FIELDS)
    write_csv(args.outdir / "discovered_files.csv", discovered_rows, DISCOVERED_FIELDS)
    write_csv(args.outdir / "fasta_candidate_audit.csv", fasta_rows, FASTA_FIELDS)
    (args.outdir / "audit_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(f"audit_status={overall_status}")
    print(f"source_endpoints_requested={summary['source_endpoints_requested']}")
    print(f"successful_source_requests={summary['successful_source_requests']}")
    print(f"discovered_file_candidates={len(discovered_rows)}")
    print(f"download_attempts={len(download_results)}")
    print(f"fasta_candidates_audited={len(fasta_rows)}")
    print(f"high_confidence_candidates={len(selected)}")
    print(f"compatible_candidates={len(compatible)}")
    if best:
        print(
            "best_candidate="
            + str(best["container_filename"])
            + "::"
            + str(best["archive_member"])
            + " overlap="
            + str(best["normalized_overlap_fraction"])
        )
    print(args.outdir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
