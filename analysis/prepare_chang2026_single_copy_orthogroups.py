#!/usr/bin/env python3
"""Validate OrthoFinder single-copy orthogroups for the Chang 2026 panel.

OrthoFinder's single-copy list is treated as a candidate set rather than a final
analysis matrix.  Every orthogroup is re-read and must contain exactly one
sequence for every panel sample.  Headers produced by ``prefix_fasta_headers.py``
are normalized from ``sample_id|transcript`` to ``sample_id`` before alignment.

Orthogroups with missing, duplicate, or unmapped sequences are retained in an
audit table but excluded from the primary one-to-one gene-tree matrix.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping, Sequence

try:
    from .prefix_fasta_headers import fasta_records, write_wrapped
except ImportError:
    from prefix_fasta_headers import fasta_records, write_wrapped

DEFAULT_OUTDIR = Path(
    "data/evidence/generated/chang2026_single_copy_orthogroups"
)

MANIFEST_FIELDS = (
    "orthogroup_id",
    "source_fasta",
    "normalized_fasta",
    "status",
    "expected_sample_count",
    "observed_sequence_count",
    "unique_mapped_sample_count",
    "missing_samples",
    "duplicate_samples",
    "unmapped_headers",
    "empty_sequence_headers",
    "interpretation",
)

SUMMARY_FIELDS = ("metric", "value")


def clean(value: object) -> str:
    return str(value or "").strip()


def read_panel_samples(path: Path) -> list[str]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    sample_ids = [clean(row.get("sample_id")) for row in rows]
    if not rows or any(not sample_id for sample_id in sample_ids):
        raise ValueError(f"Panel {path} is empty or has missing sample_id values")
    duplicates = sorted(
        sample_id
        for sample_id, count in Counter(sample_ids).items()
        if count > 1
    )
    if duplicates:
        raise ValueError(f"Duplicate panel sample IDs: {duplicates}")
    return sample_ids


def find_single_copy_file(root: Path) -> Path:
    matches = sorted(root.rglob("Orthogroups_SingleCopyOrthologues.txt"))
    if not matches:
        raise FileNotFoundError(
            f"No Orthogroups_SingleCopyOrthologues.txt below {root}"
        )
    if len(matches) > 1:
        raise ValueError(
            "Multiple OrthoFinder result sets found; supply one result directory: "
            + "|".join(str(path) for path in matches)
        )
    return matches[0]


def read_orthogroup_ids(path: Path) -> list[str]:
    ids = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    duplicates = sorted(
        value for value, count in Counter(ids).items() if count > 1
    )
    if duplicates:
        raise ValueError(f"Duplicate single-copy orthogroup IDs: {duplicates}")
    return ids


def sequence_directory(single_copy_file: Path) -> Path:
    result_root = single_copy_file.parent.parent
    directory = result_root / "Orthogroup_Sequences"
    if not directory.is_dir():
        raise FileNotFoundError(
            f"OrthoFinder Orthogroup_Sequences directory is missing: {directory}"
        )
    return directory


def source_fasta_for(directory: Path, orthogroup_id: str) -> Path | None:
    candidates = [
        directory / f"{orthogroup_id}.fa",
        directory / f"{orthogroup_id}.fasta",
        directory / f"{orthogroup_id}.faa",
    ]
    matches = [path for path in candidates if path.exists()]
    if len(matches) > 1:
        raise ValueError(
            f"Multiple sequence files for {orthogroup_id}: {matches}"
        )
    return matches[0] if matches else None


def sample_from_header(header: str, sample_ids: Sequence[str]) -> str | None:
    identifier = header.split()[0]
    if identifier in sample_ids:
        return identifier
    matches = [
        sample_id
        for sample_id in sample_ids
        if identifier.startswith(sample_id + "|")
        or identifier.startswith(sample_id + "__")
    ]
    return matches[0] if len(matches) == 1 else None


def inspect_orthogroup(
    orthogroup_id: str,
    source_fasta: Path | None,
    sample_ids: Sequence[str],
    normalized_fasta: Path,
) -> dict[str, object]:
    if source_fasta is None:
        return {
            "orthogroup_id": orthogroup_id,
            "source_fasta": "",
            "normalized_fasta": "",
            "status": "source_fasta_missing",
            "expected_sample_count": len(sample_ids),
            "observed_sequence_count": 0,
            "unique_mapped_sample_count": 0,
            "missing_samples": "|".join(sample_ids),
            "duplicate_samples": "",
            "unmapped_headers": "",
            "empty_sequence_headers": "",
            "interpretation": "The orthogroup is listed as single-copy but its sequence FASTA was not found.",
        }

    by_sample: dict[str, list[tuple[str, str]]] = defaultdict(list)
    unmapped: list[str] = []
    empty: list[str] = []
    observed = 0
    with source_fasta.open(encoding="utf-8") as handle:
        for header, sequence in fasta_records(handle):
            observed += 1
            if not sequence:
                empty.append(header)
            sample = sample_from_header(header, sample_ids)
            if sample is None:
                unmapped.append(header)
            else:
                by_sample[sample].append((header, sequence))

    missing = [sample for sample in sample_ids if not by_sample.get(sample)]
    duplicates = [
        sample for sample in sample_ids if len(by_sample.get(sample, [])) > 1
    ]

    if empty:
        status = "empty_sequences"
        interpretation = "One or more mapped or unmapped FASTA records have empty sequences."
    elif unmapped:
        status = "unmapped_headers"
        interpretation = "One or more sequence headers cannot be assigned uniquely to a panel sample."
    elif duplicates:
        status = "duplicate_sample_sequences"
        interpretation = "At least one panel sample has more than one sequence in the orthogroup."
    elif missing:
        status = "missing_panel_samples"
        interpretation = "The orthogroup lacks one or more of the 19 panel samples."
    elif observed != len(sample_ids):
        status = "sequence_count_mismatch"
        interpretation = "Observed sequence count differs from the expected one-per-sample count."
    else:
        status = "complete_single_copy"
        interpretation = "Exactly one non-empty sequence is present for every panel sample."
        normalized_fasta.parent.mkdir(parents=True, exist_ok=True)
        with normalized_fasta.open("w", encoding="utf-8") as handle:
            for sample in sample_ids:
                _, sequence = by_sample[sample][0]
                handle.write(f">{sample}\n")
                write_wrapped(handle, sequence)

    return {
        "orthogroup_id": orthogroup_id,
        "source_fasta": str(source_fasta),
        "normalized_fasta": str(normalized_fasta)
        if status == "complete_single_copy"
        else "",
        "status": status,
        "expected_sample_count": len(sample_ids),
        "observed_sequence_count": observed,
        "unique_mapped_sample_count": len(by_sample),
        "missing_samples": "|".join(missing),
        "duplicate_samples": "|".join(duplicates),
        "unmapped_headers": "|".join(unmapped),
        "empty_sequence_headers": "|".join(empty),
        "interpretation": interpretation,
    }


def prepare(
    orthofinder_root: Path,
    panel_path: Path,
    outdir: Path,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    sample_ids = read_panel_samples(panel_path)
    single_copy_file = find_single_copy_file(orthofinder_root)
    sequence_dir = sequence_directory(single_copy_file)
    orthogroup_ids = read_orthogroup_ids(single_copy_file)

    manifest: list[dict[str, object]] = []
    for orthogroup_id in orthogroup_ids:
        manifest.append(
            inspect_orthogroup(
                orthogroup_id,
                source_fasta_for(sequence_dir, orthogroup_id),
                sample_ids,
                outdir / "fastas" / f"{orthogroup_id}.fa",
            )
        )

    statuses = Counter(str(row["status"]) for row in manifest)
    summary = {
        "panel_sample_count": len(sample_ids),
        "orthofinder_single_copy_candidate_count": len(orthogroup_ids),
        "complete_single_copy_count": statuses.get("complete_single_copy", 0),
        "excluded_candidate_count": len(orthogroup_ids)
        - statuses.get("complete_single_copy", 0),
        "status_counts": dict(sorted(statuses.items())),
        "single_copy_list": str(single_copy_file),
        "orthogroup_sequence_directory": str(sequence_dir),
        "primary_matrix_rule": (
            "Exactly one non-empty sequence for every panel sample after deterministic header mapping."
        ),
        "claim_limit": (
            "One-to-one sequence presence is a conservative primary matrix rule; multi-copy orthogroups must be retained separately for homeolog and reticulation sensitivity analyses."
        ),
    }
    return manifest, summary


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--orthofinder-root", type=Path, required=True)
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest, summary = prepare(
        args.orthofinder_root,
        args.panel,
        args.outdir,
    )
    args.outdir.mkdir(parents=True, exist_ok=True)
    write_csv(
        args.outdir / "single_copy_orthogroup_manifest.csv",
        manifest,
        MANIFEST_FIELDS,
    )
    (args.outdir / "single_copy_orthogroup_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_csv(
        args.outdir / "single_copy_orthogroup_summary.csv",
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
    print(
        "orthofinder_single_copy_candidate_count="
        f"{summary['orthofinder_single_copy_candidate_count']}"
    )
    print(f"complete_single_copy_count={summary['complete_single_copy_count']}")
    print(f"excluded_candidate_count={summary['excluded_candidate_count']}")
    print(args.outdir / "single_copy_orthogroup_manifest.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
