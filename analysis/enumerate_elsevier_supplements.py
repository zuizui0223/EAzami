#!/usr/bin/env python3
"""Enumerate Elsevier `mmc` supplementary artifacts for a PII.

This is an artifact-discovery tool, not a content-validation shortcut. It tests a
bounded set of common supplementary extensions, records HTTP metadata and checks
file magic for successful responses. Candidate files still require source and
content review before entering the curated artifact manifest.
"""

from __future__ import annotations

import argparse
import csv
import urllib.error
import urllib.request
from pathlib import Path
from typing import Iterable, Mapping, Sequence

DEFAULT_PII = "S1055790325000028"
DEFAULT_OUTPUT = Path(
    "data/evidence/generated/moreyra2025_elsevier_supplement_enumeration.csv"
)
DEFAULT_EXTENSIONS = (
    "docx",
    "xlsx",
    "zip",
    "txt",
    "csv",
    "tsv",
    "pdf",
    "nex",
    "nexus",
    "nwk",
    "newick",
    "tre",
    "tree",
    "tar.gz",
)
FIELDS = (
    "index",
    "extension",
    "url",
    "status",
    "content_type",
    "content_length",
    "final_url",
    "magic_hex",
    "magic_class",
    "validation",
    "error",
)


def candidate_url(pii: str, index: int, extension: str) -> str:
    return (
        "https://ars.els-cdn.com/content/image/"
        f"1-s2.0-{pii}-mmc{index}.{extension}"
    )


def magic_class(payload: bytes) -> str:
    if payload.startswith(b"PK\x03\x04"):
        return "zip_container"
    if payload.startswith(b"%PDF"):
        return "pdf"
    if payload.startswith(b"#NEXUS") or payload.lstrip().startswith(b"#NEXUS"):
        return "nexus_text"
    if payload.lstrip().startswith(b"("):
        return "possible_newick_text"
    if payload.startswith((b"<!DOCTYPE html", b"<html", b"<!doctype html")):
        return "html"
    if payload:
        return "other_or_plain_text"
    return "empty"


def inspect_candidate(
    url: str,
    timeout: int = 30,
) -> dict[str, object] | None:
    headers = {"User-Agent": "EAzami-Elsevier-artifact-enumerator/1.0"}
    request = urllib.request.Request(url, method="HEAD", headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = getattr(response, "status", 200)
            content_type = response.headers.get("Content-Type", "")
            content_length = response.headers.get("Content-Length", "")
            final_url = response.geturl()
        if status != 200:
            return None

        range_request = urllib.request.Request(
            url,
            headers={**headers, "Range": "bytes=0-63"},
        )
        with urllib.request.urlopen(range_request, timeout=timeout) as response:
            payload = response.read(64)
        kind = magic_class(payload)
        return {
            "status": status,
            "content_type": content_type,
            "content_length": content_length,
            "final_url": final_url,
            "magic_hex": payload.hex(),
            "magic_class": kind,
            "validation": "candidate_exists" if kind != "html" else "html_not_artifact",
            "error": "",
        }
    except urllib.error.HTTPError as exc:
        if exc.code in {403, 404}:
            return None
        return {
            "status": exc.code,
            "content_type": exc.headers.get("Content-Type", ""),
            "content_length": exc.headers.get("Content-Length", ""),
            "final_url": "",
            "magic_hex": "",
            "magic_class": "",
            "validation": "http_error",
            "error": f"HTTPError: {exc}",
        }
    except Exception as exc:
        return {
            "status": "error",
            "content_type": "",
            "content_length": "",
            "final_url": "",
            "magic_hex": "",
            "magic_class": "",
            "validation": "request_error",
            "error": f"{type(exc).__name__}: {exc}",
        }


def enumerate_candidates(
    pii: str,
    max_index: int,
    extensions: Sequence[str] = DEFAULT_EXTENSIONS,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for index in range(1, max_index + 1):
        for extension in extensions:
            url = candidate_url(pii, index, extension)
            result = inspect_candidate(url)
            if result is None:
                continue
            rows.append(
                {
                    "index": index,
                    "extension": extension,
                    "url": url,
                    **result,
                }
            )
    return rows


def write_csv(path: Path, rows: Iterable[Mapping[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(FIELDS), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pii", default=DEFAULT_PII)
    parser.add_argument("--max-index", type=int, default=20)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.pii.startswith("S"):
        raise SystemExit(f"Unexpected Elsevier PII: {args.pii}")
    rows = enumerate_candidates(args.pii, args.max_index)
    write_csv(args.output, rows)
    valid = [row for row in rows if row["validation"] == "candidate_exists"]
    print(f"recorded_responses={len(rows)}")
    print(f"valid_artifact_candidates={len(valid)}")
    for row in valid:
        print(
            f"mmc{row['index']}.{row['extension']} "
            f"size={row['content_length']} magic={row['magic_class']}"
        )
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
