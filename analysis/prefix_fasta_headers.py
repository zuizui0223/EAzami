#!/usr/bin/env python3
"""Prefix FASTA identifiers with a stable sample ID.

OrthoFinder gene-tree leaves must be traceable to the 19-sample panel.  This
utility rewrites every record as ``sample_id|original_id`` while preserving the
sequence and rejecting duplicate original identifiers.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Iterator, TextIO


def fasta_records(handle: Iterable[str]) -> Iterator[tuple[str, str]]:
    header = ""
    sequence: list[str] = []
    for raw in handle:
        line = raw.strip()
        if not line:
            continue
        if line.startswith(">"):
            if header:
                yield header, "".join(sequence)
            header = line[1:].strip()
            sequence = []
        else:
            if not header:
                raise ValueError("FASTA sequence encountered before first header")
            sequence.append(line)
    if header:
        yield header, "".join(sequence)


def normalized_identifier(header: str) -> str:
    identifier = header.split()[0]
    if not identifier:
        raise ValueError(f"Empty FASTA identifier in header {header!r}")
    return identifier


def write_wrapped(handle: TextIO, sequence: str, width: int = 80) -> None:
    for start in range(0, len(sequence), width):
        handle.write(sequence[start : start + width] + "\n")


def prefix_fasta(
    input_path: Path,
    output_path: Path,
    sample_id: str,
) -> dict[str, object]:
    sample_id = sample_id.strip()
    if not sample_id or any(char.isspace() for char in sample_id) or "|" in sample_id:
        raise ValueError(
            "sample_id must be non-empty and contain neither whitespace nor '|'"
        )

    seen: set[str] = set()
    records: list[tuple[str, str]] = []
    with input_path.open(encoding="utf-8") as handle:
        for header, sequence in fasta_records(handle):
            identifier = normalized_identifier(header)
            if identifier in seen:
                raise ValueError(f"Duplicate FASTA identifier: {identifier}")
            if not sequence:
                raise ValueError(f"Empty sequence for {identifier}")
            seen.add(identifier)
            records.append((identifier, sequence))
    if not records:
        raise ValueError(f"No FASTA records in {input_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for identifier, sequence in records:
            handle.write(f">{sample_id}|{identifier}\n")
            write_wrapped(handle, sequence)

    return {
        "sample_id": sample_id,
        "record_count": len(records),
        "input_path": str(input_path),
        "output_path": str(output_path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sample-id", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = prefix_fasta(args.input, args.output, args.sample_id)
    print(f"sample_id={summary['sample_id']}")
    print(f"record_count={summary['record_count']}")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
