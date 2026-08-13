#!/usr/bin/env python3
"""Recover and validate the public original Compositae1061 HybPiper reference.

This is a compatibility input, not the Moreyra et al. (2025) augmented
reference. Moreyra added Cirsium tioganum recovered exons to the original
Compositae1061 target/reference. The public reference recovered here is useful
for an explicitly labelled compatibility reanalysis and for new same-assay
samples, but it must never be represented as the missing augmented file.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

SOURCE_REPOSITORY = "carol-siniscalchi/Comp1061-Angio353"
SOURCE_COMMIT = "c340244907c39579dca42060769678bf8759fa1d"
SOURCE_FILENAME = "comp1061_hybpiper_reference.fasta"
SOURCE_URL = (
    "https://raw.githubusercontent.com/"
    f"{SOURCE_REPOSITORY}/{SOURCE_COMMIT}/{SOURCE_FILENAME}"
)
EXPECTED_GITHUB_BLOB_SHA1 = "4f89e234007f367ffa8aa5e2be536bc44f31f445"
EXPECTED_SIZE_BYTES = 1_162_856
EXPECTED_LOCUS_COUNT = 1_061
EXPECTED_REFERENCE_PREFIXES = {"lett", "saff", "sunf"}
DNA_ALPHABET = set("ACGTRYSWKMBDHVN")
HEADER_RE = re.compile(r"^(?P<reference>[^\s-]+)-(?P<locus>\S+)$")


def git_blob_sha1(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def download(url: str, *, retries: int = 5, timeout: int = 120) -> bytes:
    headers = {
        "User-Agent": "EAzami-Compositae1061-reference-recovery/1.0",
        "Accept": "text/plain,application/octet-stream,*/*",
    }
    for attempt in range(retries):
        try:
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            if attempt + 1 >= retries:
                raise RuntimeError(f"download failed after {retries} attempts: {url}") from exc
            delay = 2**attempt
            if isinstance(exc, urllib.error.HTTPError) and exc.headers:
                retry_after = exc.headers.get("Retry-After")
                if retry_after and retry_after.isdigit():
                    delay = max(delay, int(retry_after))
            time.sleep(delay)
    raise AssertionError("unreachable")


def parse_fasta(payload: bytes) -> list[tuple[str, str]]:
    try:
        text = payload.decode("ascii")
    except UnicodeDecodeError as exc:
        raise ValueError("reference FASTA is not ASCII") from exc

    records: list[tuple[str, str]] = []
    header: str | None = None
    sequence: list[str] = []
    seen_headers: set[str] = set()

    def flush() -> None:
        nonlocal header, sequence
        if header is None:
            return
        seq = "".join(sequence).replace(" ", "").upper()
        if not seq:
            raise ValueError(f"empty FASTA sequence for {header}")
        invalid = sorted(set(seq) - DNA_ALPHABET)
        if invalid:
            raise ValueError(f"invalid DNA characters for {header}: {invalid}")
        if header in seen_headers:
            raise ValueError(f"duplicate FASTA header: {header}")
        seen_headers.add(header)
        records.append((header, seq))
        header = None
        sequence = []

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith(">"):
            flush()
            header = line[1:].strip()
            if not header:
                raise ValueError("empty FASTA header")
        else:
            if header is None:
                raise ValueError("sequence line observed before first FASTA header")
            sequence.append(line)
    flush()
    if not records:
        raise ValueError("reference FASTA contains no records")
    return records


def validate_payload(payload: bytes) -> dict[str, object]:
    observed_blob = git_blob_sha1(payload)
    if observed_blob != EXPECTED_GITHUB_BLOB_SHA1:
        raise ValueError(
            f"Git blob SHA mismatch: {observed_blob} != {EXPECTED_GITHUB_BLOB_SHA1}"
        )
    if len(payload) != EXPECTED_SIZE_BYTES:
        raise ValueError(
            f"reference size changed: {len(payload)} != {EXPECTED_SIZE_BYTES}"
        )

    records = parse_fasta(payload)
    locus_to_refs: dict[str, set[str]] = defaultdict(set)
    reference_counts: Counter[str] = Counter()
    duplicate_ref_locus: set[tuple[str, str]] = set()
    seen_ref_locus: set[tuple[str, str]] = set()

    for header, _sequence in records:
        match = HEADER_RE.fullmatch(header)
        if not match:
            raise ValueError(f"unexpected HybPiper reference header: {header}")
        reference = match.group("reference")
        locus = match.group("locus")
        key = (reference, locus)
        if key in seen_ref_locus:
            duplicate_ref_locus.add(key)
        seen_ref_locus.add(key)
        reference_counts[reference] += 1
        locus_to_refs[locus].add(reference)

    if duplicate_ref_locus:
        raise ValueError(f"duplicate reference/locus pairs: {sorted(duplicate_ref_locus)[:5]}")
    if set(reference_counts) != EXPECTED_REFERENCE_PREFIXES:
        raise ValueError(
            f"unexpected reference prefixes: {sorted(reference_counts)} != "
            f"{sorted(EXPECTED_REFERENCE_PREFIXES)}"
        )
    if len(locus_to_refs) != EXPECTED_LOCUS_COUNT:
        raise ValueError(
            f"unexpected locus count: {len(locus_to_refs)} != {EXPECTED_LOCUS_COUNT}"
        )
    if any(not refs or len(refs) > len(EXPECTED_REFERENCE_PREFIXES) for refs in locus_to_refs.values()):
        raise ValueError("invalid per-locus reference multiplicity")
    if any(not refs <= EXPECTED_REFERENCE_PREFIXES for refs in locus_to_refs.values()):
        raise ValueError("unexpected reference prefix assigned to a locus")

    multiplicity = Counter(len(refs) for refs in locus_to_refs.values())
    return {
        "contract_version": "comp1061_original_hybpiper_reference_v1",
        "source_repository": SOURCE_REPOSITORY,
        "source_commit": SOURCE_COMMIT,
        "source_filename": SOURCE_FILENAME,
        "source_url": SOURCE_URL,
        "github_blob_sha1": observed_blob,
        "sha256": sha256_bytes(payload),
        "size_bytes": len(payload),
        "sequence_record_count": len(records),
        "locus_count": len(locus_to_refs),
        "reference_prefixes": sorted(reference_counts),
        "records_by_reference": dict(sorted(reference_counts.items())),
        "locus_reference_multiplicity": {
            str(key): value for key, value in sorted(multiplicity.items())
        },
        "hybpiper_reference_structure_valid": True,
        "compatibility_reanalysis_usable": True,
        "moreyra_augmented_reference_recovered": False,
        "moreyra_augmentation_missing": "Cirsium tioganum recovered exons added by Moreyra et al. 2025",
        "claim_limit": (
            "This validates the original public Compositae1061 HybPiper reference used in a primary "
            "Asteraceae comparison study. Moreyra et al. 2025 augmented the original reference with "
            "Cirsium tioganum recovered exons; that augmented file remains unrecovered. Analyses using "
            "this file are compatibility reanalyses, not exact reproductions of Moreyra preprocessing."
        ),
    }


def recover(outdir: Path, payload: bytes | None = None) -> dict[str, object]:
    if payload is None:
        payload = download(SOURCE_URL)
    contract = validate_payload(payload)
    outdir.mkdir(parents=True, exist_ok=True)
    reference_path = outdir / SOURCE_FILENAME
    reference_path.write_bytes(payload)
    contract_path = outdir / "comp1061_original_reference_contract.json"
    contract_path.write_text(
        json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return contract


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    contract = recover(args.outdir)
    for key in (
        "github_blob_sha1",
        "sha256",
        "size_bytes",
        "sequence_record_count",
        "locus_count",
        "reference_prefixes",
        "locus_reference_multiplicity",
        "compatibility_reanalysis_usable",
        "moreyra_augmented_reference_recovered",
    ):
        print(f"{key}={contract[key]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
