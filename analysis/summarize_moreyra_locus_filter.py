#!/usr/bin/env python3
"""Reconstruct the reproducible portion of Moreyra et al. 2025 locus filtering.

Inputs are the public files recovered from ldmoreyra/A-thorny-tale by
``recover_moreyra_author_repository.py``.  The paper discarded loci with more
than ten HybPiper paralog warnings, manually inspected loci with one to ten
warnings, and then retained alignments with <50% missing data and >=80% species
presence.  This script reproduces the warning-count and raw occupancy portions,
but explicitly does not invent the manual gene-tree decisions or the final
alignment-level 350-locus list.

When a non-default ``--audit-dir`` is supplied and the output paths are not
explicitly overridden, outputs follow that audit directory.  This keeps
restartable HPC/CI workspaces self-contained instead of silently writing the
reconstruction CSV back into the repository-relative default directory.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Iterable, Mapping, Sequence

DEFAULT_AUDIT_DIR = Path("data/evidence/generated/moreyra_author_repository")
DEFAULT_OUTPUT = DEFAULT_AUDIT_DIR / "paralog_locus_filter_reconstruction.csv"
DEFAULT_SUMMARY = DEFAULT_AUDIT_DIR / "locus_filter_reconstruction_summary.json"
DEFAULT_SAMPLE_DIFF = DEFAULT_AUDIT_DIR / "sample_matrix_membership_difference.csv"

OUTPUT_FIELDS = (
    "locus",
    "paralog_report_sample_rows",
    "samples_with_zero_copies",
    "samples_with_one_copy",
    "samples_with_gt_one_copy",
    "samples_false_or_unparsed",
    "max_copy_count",
    "paralog_warning_class",
    "seq_length_sample_rows",
    "samples_with_sequence",
    "raw_sequence_occupancy",
    "occupancy_ge_0_80",
    "passes_reproducible_warning_and_occupancy_screen",
    "final_350_membership",
)


def clean(value: object) -> str:
    return str(value or "").strip()


def as_number(value: object) -> float | None:
    text = clean(value)
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def read_delimited(path: Path, delimiter: str = ",") -> tuple[list[str], list[list[str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle, delimiter=delimiter)
        rows = list(reader)
    if not rows:
        raise ValueError(f"{path}: empty table")
    return rows[0], rows[1:]


def write_csv(path: Path, rows: Iterable[Mapping[str, object]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def named_locus_positions(header: Sequence[str]) -> list[tuple[int, str]]:
    output: list[tuple[int, str]] = []
    seen: set[str] = set()
    for index, value in enumerate(header[1:], start=1):
        locus = clean(value)
        if not locus:
            continue
        if locus in seen:
            raise ValueError(f"Duplicate named locus in header: {locus}")
        seen.add(locus)
        output.append((index, locus))
    return output


def parse_paralog_matrix(path: Path) -> tuple[dict[str, dict[str, object]], dict[str, object]]:
    header, rows = read_delimited(path)
    if clean(header[0]) != "Species":
        raise ValueError(f"{path}: first paralog-report column must be Species")
    positions = named_locus_positions(header)
    output: dict[str, dict[str, object]] = {}
    for index, locus in positions:
        zero = one = gt_one = false_or_unparsed = 0
        maximum = 0.0
        for row in rows:
            value = row[index] if index < len(row) else ""
            numeric = as_number(value)
            if numeric is None:
                if clean(value):
                    false_or_unparsed += 1
                continue
            maximum = max(maximum, numeric)
            if numeric == 0:
                zero += 1
            elif numeric == 1:
                one += 1
            elif numeric > 1:
                gt_one += 1
        if gt_one > 10:
            warning_class = "discard_gt10_paralog_warnings"
        elif gt_one >= 1:
            warning_class = "manual_gene_tree_review_1_to_10_warnings"
        else:
            warning_class = "no_paralog_warning"
        output[locus] = {
            "paralog_report_sample_rows": len(rows),
            "samples_with_zero_copies": zero,
            "samples_with_one_copy": one,
            "samples_with_gt_one_copy": gt_one,
            "samples_false_or_unparsed": false_or_unparsed,
            "max_copy_count": maximum,
            "paralog_warning_class": warning_class,
        }
    metadata = {
        "raw_columns_including_species": len(header),
        "named_locus_columns": len(positions),
        "trailing_or_blank_columns": len(header) - 1 - len(positions),
        "sample_rows": len(rows),
    }
    return output, metadata


def parse_seq_lengths(path: Path) -> tuple[dict[str, dict[str, object]], dict[str, object], list[str]]:
    header, rows = read_delimited(path, delimiter="\t")
    if clean(header[0]) != "Species":
        raise ValueError(f"{path}: first sequence-length column must be Species")
    positions = named_locus_positions(header)
    reference_rows = [row for row in rows if clean(row[0]).casefold() == "meanlength"]
    biological_rows = [row for row in rows if clean(row[0]).casefold() != "meanlength"]
    output: dict[str, dict[str, object]] = {}
    for index, locus in positions:
        recovered = 0
        for row in biological_rows:
            value = as_number(row[index] if index < len(row) else "")
            if value is not None and value > 0:
                recovered += 1
        occupancy = recovered / len(biological_rows) if biological_rows else 0.0
        output[locus] = {
            "seq_length_sample_rows": len(biological_rows),
            "samples_with_sequence": recovered,
            "raw_sequence_occupancy": occupancy,
            "occupancy_ge_0_80": occupancy >= 0.80,
        }
    metadata = {
        "raw_rows": len(rows),
        "reference_meanlength_rows": len(reference_rows),
        "biological_sample_rows": len(biological_rows),
        "named_locus_columns": len(positions),
    }
    return output, metadata, [clean(row[0]) for row in biological_rows]


def read_hybpiper_sample_names(path: Path) -> list[str]:
    header, rows = read_delimited(path, delimiter="\t")
    if "Name" not in header:
        raise ValueError(f"{path}: missing Name column")
    index = header.index("Name")
    return [clean(row[index]) for row in rows if index < len(row) and clean(row[index])]


def reconstruct(
    paralog: Mapping[str, Mapping[str, object]],
    seq_lengths: Mapping[str, Mapping[str, object]],
) -> list[dict[str, object]]:
    if set(paralog) != set(seq_lengths):
        missing_in_paralog = sorted(set(seq_lengths) - set(paralog))
        missing_in_lengths = sorted(set(paralog) - set(seq_lengths))
        raise ValueError(
            "Named locus sets disagree: "
            f"missing_in_paralog={missing_in_paralog[:10]}, "
            f"missing_in_lengths={missing_in_lengths[:10]}"
        )
    rows: list[dict[str, object]] = []
    for locus in sorted(paralog):
        row = {"locus": locus, **paralog[locus], **seq_lengths[locus]}
        passes = (
            row["paralog_warning_class"] != "discard_gt10_paralog_warnings"
            and bool(row["occupancy_ge_0_80"])
        )
        row["passes_reproducible_warning_and_occupancy_screen"] = passes
        row["final_350_membership"] = "unresolved_manual_tree_and_alignment_filter"
        rows.append(row)
    return rows


def build_summary(
    rows: Sequence[Mapping[str, object]],
    paralog_metadata: Mapping[str, object],
    seq_metadata: Mapping[str, object],
    stats_names: Sequence[str],
    seq_names: Sequence[str],
) -> dict[str, object]:
    class_counts: dict[str, int] = {}
    for row in rows:
        key = str(row["paralog_warning_class"])
        class_counts[key] = class_counts.get(key, 0) + 1

    stats_set = set(stats_names)
    seq_set = set(seq_names)
    return {
        "public_author_repository": "ldmoreyra/A-thorny-tale",
        "paper_reported_mapped_loci": 1064,
        "public_named_loci": len(rows),
        "paper_vs_public_named_locus_difference": 1064 - len(rows),
        "paralog_matrix": dict(paralog_metadata),
        "sequence_length_matrix": dict(seq_metadata),
        "hybpiper_stats_sample_rows": len(stats_names),
        "seq_length_samples_not_in_hybpiper_stats": sorted(seq_set - stats_set),
        "hybpiper_stats_samples_not_in_seq_lengths": sorted(stats_set - seq_set),
        "paralog_warning_class_counts": class_counts,
        "loci_raw_occupancy_ge_0_80": sum(bool(row["occupancy_ge_0_80"]) for row in rows),
        "loci_warning_le_10_and_occupancy_ge_0_80": sum(
            bool(row["passes_reproducible_warning_and_occupancy_screen"]) for row in rows
        ),
        "no_warning_and_occupancy_ge_0_80": sum(
            row["paralog_warning_class"] == "no_paralog_warning"
            and bool(row["occupancy_ge_0_80"])
            for row in rows
        ),
        "manual_review_class_and_occupancy_ge_0_80": sum(
            row["paralog_warning_class"] == "manual_gene_tree_review_1_to_10_warnings"
            and bool(row["occupancy_ge_0_80"])
            for row in rows
        ),
        "paper_reported_final_alignments": 350,
        "exact_final_350_locus_names_recovered": False,
        "why_exact_350_remains_unresolved": (
            "The public summary matrices reproduce raw occupancy and the >10-warning screen, "
            "but the paper additionally used visual gene-tree orthology decisions and final "
            "alignment-level missingness. No explicit final retained-locus list or 350 gene-tree "
            "archive is present in the author repository."
        ),
    }


def sample_difference_rows(stats_names: Sequence[str], seq_names: Sequence[str]) -> list[dict[str, str]]:
    stats = set(stats_names)
    seq = set(seq_names)
    rows = [
        {"sample_name": name, "membership": "seq_lengths_only"}
        for name in sorted(seq - stats)
    ]
    rows.extend(
        {"sample_name": name, "membership": "hybpiper_stats_only"}
        for name in sorted(stats - seq)
    )
    return rows


def resolve_output_paths(
    audit_dir: Path,
    output: Path,
    summary: Path,
    sample_difference: Path,
) -> tuple[Path, Path, Path]:
    """Make implicit outputs follow an explicitly relocated audit workspace."""
    if audit_dir != DEFAULT_AUDIT_DIR:
        if output == DEFAULT_OUTPUT:
            output = audit_dir / "paralog_locus_filter_reconstruction.csv"
        if summary == DEFAULT_SUMMARY:
            summary = audit_dir / "locus_filter_reconstruction_summary.json"
        if sample_difference == DEFAULT_SAMPLE_DIFF:
            sample_difference = audit_dir / "sample_matrix_membership_difference.csv"
    return output, summary, sample_difference


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit-dir", type=Path, default=DEFAULT_AUDIT_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--sample-difference", type=Path, default=DEFAULT_SAMPLE_DIFF)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.output, args.summary, args.sample_difference = resolve_output_paths(
        args.audit_dir, args.output, args.summary, args.sample_difference
    )
    paralog_path = args.audit_dir / "extracted/paralog_report/sheet_01_paralog_report_1.csv"
    seq_path = args.audit_dir / "source/seq_lengths_exonerate.tsv"
    stats_path = args.audit_dir / "source/hybpiper_stats_exonerate.tsv"

    paralog, paralog_metadata = parse_paralog_matrix(paralog_path)
    seq_lengths, seq_metadata, seq_names = parse_seq_lengths(seq_path)
    stats_names = read_hybpiper_sample_names(stats_path)
    rows = reconstruct(paralog, seq_lengths)
    summary = build_summary(rows, paralog_metadata, seq_metadata, stats_names, seq_names)

    write_csv(args.output, rows, OUTPUT_FIELDS)
    write_csv(
        args.sample_difference,
        sample_difference_rows(stats_names, seq_names),
        ("sample_name", "membership"),
    )
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"public_named_loci={summary['public_named_loci']}")
    print(f"discard_gt10={summary['paralog_warning_class_counts']['discard_gt10_paralog_warnings']}")
    print(
        "manual_1_to_10="
        + str(summary['paralog_warning_class_counts']['manual_gene_tree_review_1_to_10_warnings'])
    )
    print(f"no_warning={summary['paralog_warning_class_counts']['no_paralog_warning']}")
    print(f"occupancy_ge_0_80={summary['loci_raw_occupancy_ge_0_80']}")
    print(
        "warning_le_10_and_occupancy_ge_0_80="
        + str(summary['loci_warning_le_10_and_occupancy_ge_0_80'])
    )
    print(f"paper_final_alignments={summary['paper_reported_final_alignments']}")
    print(args.summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
