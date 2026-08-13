#!/usr/bin/env python3
"""Recover versioned public phylogeny artifacts from a curated manifest.

The script downloads only unauthenticated direct URLs. It computes SHA256 hashes,
checks optional expected sizes, and extracts DOCX text/tables using the Python
standard library. Records requiring authentication or lacking a verified direct
URL remain explicit skipped rows rather than being guessed.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import os
import re
import shutil
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Iterable, Mapping, Sequence

DEFAULT_MANIFEST = Path(
    "data/evidence/published_phylogeny_artifact_manifest_2026-08-10.csv"
)
DEFAULT_OUTDIR = Path("data/evidence/generated/published_phylogeny_artifacts")
SUMMARY_FIELDS = (
    "artifact_key",
    "citation_key",
    "artifact_type",
    "host",
    "status",
    "download_url",
    "output_path",
    "sha256",
    "size_bytes",
    "expected_size_bytes",
    "size_check",
    "extracted_text_path",
    "extracted_table_count",
    "error",
)

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}


def safe_name(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    value = value.strip("._")
    if not value:
        raise ValueError("Artifact name becomes empty after sanitization")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_bool(value: str) -> bool:
    return value.strip().casefold() in {"1", "true", "yes", "y"}


def read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        required = {
            "artifact_key",
            "citation_key",
            "artifact_type",
            "host",
            "landing_url",
            "download_url",
            "requires_auth",
            "license",
            "expected_size_bytes",
            "expected_filename",
            "status",
            "extraction",
            "notes",
        }
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Manifest missing required fields: {sorted(missing)}")
        rows = [
            {key: (value or "").strip() for key, value in row.items()}
            for row in reader
            if row.get("artifact_key")
        ]

    seen: set[str] = set()
    for row in rows:
        key = row["artifact_key"]
        if key in seen:
            raise ValueError(f"Duplicate artifact_key: {key}")
        safe_name(key)
        seen.add(key)
    return rows


class Downloader:
    def __init__(self, timeout: int = 120, retries: int = 5) -> None:
        self.timeout = timeout
        self.retries = retries

    def download(self, url: str, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_suffix(path.suffix + ".part")
        headers = {
            "User-Agent": "EAzami-published-phylogeny-artifact-recovery/1.0",
            "Accept": "*/*",
        }
        for attempt in range(self.retries):
            request = urllib.request.Request(url, headers=headers)
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    with temp.open("wb") as handle:
                        shutil.copyfileobj(response, handle)
                temp.replace(path)
                return
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
                if temp.exists():
                    temp.unlink()
                if attempt + 1 == self.retries:
                    raise RuntimeError(f"Download failed after retries: {url}") from exc
                delay = 2**attempt
                if isinstance(exc, urllib.error.HTTPError):
                    retry_after = exc.headers.get("Retry-After")
                    if retry_after and retry_after.isdigit():
                        delay = max(delay, int(retry_after))
                time.sleep(delay)


def paragraph_text(element: ET.Element) -> str:
    texts = [node.text or "" for node in element.findall(".//w:t", NS)]
    return "".join(texts).strip()


def table_rows(table: ET.Element) -> list[list[str]]:
    output: list[list[str]] = []
    for row in table.findall("./w:tr", NS):
        values: list[str] = []
        for cell in row.findall("./w:tc", NS):
            parts = [paragraph_text(paragraph) for paragraph in cell.findall(".//w:p", NS)]
            values.append("\n".join(part for part in parts if part).strip())
        output.append(values)
    return output


def extract_docx(docx_path: Path, output_dir: Path) -> tuple[Path, list[Path]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(docx_path) as archive:
        try:
            xml_bytes = archive.read("word/document.xml")
        except KeyError as exc:
            raise ValueError(f"Not a valid DOCX document: {docx_path}") from exc

    root = ET.fromstring(xml_bytes)
    body = root.find(".//w:body", NS)
    if body is None:
        raise ValueError(f"DOCX has no document body: {docx_path}")

    lines: list[str] = []
    table_paths: list[Path] = []
    table_index = 0

    for child in list(body):
        if child.tag == f"{{{W_NS}}}p":
            text = paragraph_text(child)
            if text:
                lines.append(text)
        elif child.tag == f"{{{W_NS}}}tbl":
            table_index += 1
            rows = table_rows(child)
            table_path = output_dir / f"table_{table_index:03d}.csv"
            max_width = max((len(row) for row in rows), default=0)
            with table_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                for row in rows:
                    writer.writerow(row + [""] * (max_width - len(row)))
            table_paths.append(table_path)
            lines.append(f"[TABLE {table_index}: {table_path.name}]")

    text_path = output_dir / "document.txt"
    text_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return text_path, table_paths


def write_csv(path: Path, rows: Iterable[Mapping[str, object]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def recover_one(
    row: Mapping[str, str],
    outdir: Path,
    downloader: Downloader,
    force: bool = False,
) -> dict[str, object]:
    result: dict[str, object] = {
        "artifact_key": row["artifact_key"],
        "citation_key": row["citation_key"],
        "artifact_type": row["artifact_type"],
        "host": row["host"],
        "status": "",
        "download_url": row["download_url"],
        "output_path": "",
        "sha256": "",
        "size_bytes": "",
        "expected_size_bytes": row["expected_size_bytes"],
        "size_check": "not_applicable",
        "extracted_text_path": "",
        "extracted_table_count": 0,
        "error": "",
    }

    if parse_bool(row["requires_auth"]):
        result["status"] = "skipped_requires_auth"
        return result
    if not row["download_url"]:
        result["status"] = "skipped_no_verified_direct_url"
        return result

    artifact_dir = outdir / safe_name(row["artifact_key"])
    filename = safe_name(row["expected_filename"] or Path(row["download_url"]).name)
    output_path = artifact_dir / filename
    result["output_path"] = str(output_path)

    try:
        if force or not output_path.exists():
            downloader.download(row["download_url"], output_path)
        size = output_path.stat().st_size
        digest = sha256_file(output_path)
        result["size_bytes"] = size
        result["sha256"] = digest

        expected = row["expected_size_bytes"].strip()
        if expected:
            result["size_check"] = "match" if size == int(expected) else "mismatch"
        else:
            result["size_check"] = "not_provided"

        extraction = row["extraction"]
        if extraction == "docx_text_and_tables":
            text_path, table_paths = extract_docx(output_path, artifact_dir / "extracted")
            result["extracted_text_path"] = str(text_path)
            result["extracted_table_count"] = len(table_paths)
        elif extraction == "plain_text":
            # Preserve bytes as published. A UTF-8 preview is stored only when decoding works.
            try:
                text = output_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                text = ""
            if text:
                preview = artifact_dir / "published_text_preview.txt"
                preview.write_text(text, encoding="utf-8")
                result["extracted_text_path"] = str(preview)

        result["status"] = "downloaded"
    except Exception as exc:  # keep per-artifact failures explicit in the manifest output
        result["status"] = "failed"
        result["error"] = f"{type(exc).__name__}: {exc}"
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--fail-on-download-error",
        action="store_true",
        help="Exit nonzero when any direct unauthenticated artifact fails.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = read_manifest(args.manifest)
    args.outdir.mkdir(parents=True, exist_ok=True)
    downloader = Downloader()
    results = [recover_one(row, args.outdir, downloader, args.force) for row in rows]
    summary = args.outdir / "artifact_recovery_summary.csv"
    write_csv(summary, results, SUMMARY_FIELDS)

    for result in results:
        print(
            f"{result['artifact_key']}: {result['status']} "
            f"size={result['size_bytes']} sha256={result['sha256']}"
        )
    print(summary)

    failed = [row for row in results if row["status"] == "failed"]
    if failed and args.fail_on_download_error:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
