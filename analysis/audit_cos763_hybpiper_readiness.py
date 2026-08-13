#!/usr/bin/env python3
"""Audit the recovered Mandel et al. COS763 alignments for target-file use.

The Dryad record ``10.5061/dryad.gr93t`` contains 763 per-locus nucleotide
alignments from the foundational Compositae target-enrichment dataset.  They are
source-backed and useful, but they are not automatically equivalent to the
unrecovered Moreyra Compositae1061 HybPiper target.  This script therefore:

* locates ``COS_alignment_files_NEW.zip`` in a downloaded Dryad archive;
* removes alignment gaps without changing sequence order;
* records length, ambiguity and frame-0 internal-stop diagnostics;
* writes an explicitly *unframed* multi-source mapping reference;
* writes only directly frame-compatible sequences to a separate candidate file;
* refuses to call the complete 763-locus set a CDS-ready HybPiper target unless
  every locus has at least one directly compatible source sequence.

The output is a readiness audit, not a claim that the alignments are the exact
Compositae1061 target or that their reading frames have been experimentally
validated.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import statistics
import zipfile
from collections import Counter
from pathlib import Path
from typing import Iterable, Iterator, Mapping, Sequence

DEFAULT_OUTDIR = Path("data/evidence/generated/cos763_hybpiper_readiness")
ALIGNMENT_ARCHIVE_NAME = "COS_alignment_files_NEW.zip"
DNA_ALPHABET = set("ACGTNRYKMSWBDHV")
STOP_CODONS = {"TAA", "TAG", "TGA"}

SEQUENCE_FIELDS = (
    "locus",
    "source_taxon",
    "original_header",
    "alignment_length",
    "ungapped_length",
    "gap_fraction",
    "ambiguous_count",
    "ambiguous_fraction",
    "length_mod_3",
    "internal_stop_count_frame0",
    "terminal_stop_frame0",
    "invalid_characters",
    "mapping_reference_included",
    "direct_cds_candidate",
    "mapping_header",
)

LOCUS_FIELDS = (
    "locus",
    "source_sequence_count",
    "source_taxon_count",
    "source_taxa",
    "min_ungapped_length",
    "median_ungapped_length",
    "max_ungapped_length",
    "mapping_reference_count",
    "direct_cds_candidate_count",
    "any_source_direct_cds_candidate",
    "all_sources_direct_cds_candidate",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def clean(value: object) -> str:
    return str(value or "").strip()


def safe_token(value: str) -> str:
    token = re.sub(r"[^A-Za-z0-9_.]+", "_", clean(value)).strip("_")
    return token or "unknown"


def parse_fasta(data: bytes) -> list[tuple[str, str]]:
    records: list[tuple[str, str]] = []
    header = ""
    sequence: list[str] = []
    for raw in data.decode("utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith(">"):
            if header:
                records.append((header, "".join(sequence)))
            header = line[1:].strip()
            sequence = []
        else:
            if not header:
                raise ValueError("FASTA sequence encountered before first header")
            sequence.append(line)
    if header:
        records.append((header, "".join(sequence)))
    if not records:
        raise ValueError("No FASTA records recovered")
    return records


def ungap(sequence: str) -> str:
    return re.sub(r"[-.\s]", "", sequence.upper())


def internal_stop_count(sequence: str) -> tuple[int, bool]:
    codons = [sequence[index : index + 3] for index in range(0, len(sequence), 3)]
    complete = [codon for codon in codons if len(codon) == 3]
    if not complete:
        return 0, False
    terminal_stop = complete[-1] in STOP_CODONS
    internal = sum(codon in STOP_CODONS for codon in complete[:-1])
    return internal, terminal_stop


def alignment_member_names(archive: zipfile.ZipFile) -> list[str]:
    return sorted(
        name
        for name in archive.namelist()
        if not name.endswith("/")
        and re.search(r"(?:^|/)COS_[0-9]+\.fasta$", name, flags=re.I)
    )


def locate_alignment_archive(
    *,
    archive: Path | None,
    archive_dir: Path | None,
) -> tuple[Path, str, bytes]:
    candidates: list[Path]
    if archive is not None:
        candidates = [archive]
    elif archive_dir is not None:
        candidates = sorted(path for path in archive_dir.iterdir() if path.is_file())
    else:
        raise ValueError("One of archive or archive_dir is required")

    matches: list[tuple[Path, str, bytes]] = []
    for path in candidates:
        if not zipfile.is_zipfile(path):
            continue
        with zipfile.ZipFile(path) as outer:
            direct = alignment_member_names(outer)
            if direct:
                matches.append((path, "", path.read_bytes()))
                continue
            nested = [
                name
                for name in outer.namelist()
                if Path(name).name == ALIGNMENT_ARCHIVE_NAME
            ]
            for member in nested:
                payload = outer.read(member)
                if not zipfile.is_zipfile(io.BytesIO(payload)):
                    raise ValueError(f"Nested alignment member is not ZIP: {member}")
                matches.append((path, member, payload))
    if len(matches) != 1:
        raise ValueError(
            f"Expected exactly one COS763 alignment archive, observed {len(matches)}"
        )
    return matches[0]


def analyze(
    alignment_zip: bytes,
    *,
    min_length: int,
    max_ambiguous_fraction: float,
) -> tuple[
    list[dict[str, object]],
    list[dict[str, object]],
    list[tuple[str, str]],
    list[tuple[str, str]],
]:
    if min_length < 1:
        raise ValueError("min_length must be >= 1")
    if not 0 <= max_ambiguous_fraction <= 1:
        raise ValueError("max_ambiguous_fraction must be between 0 and 1")

    sequence_rows: list[dict[str, object]] = []
    mapping_records: list[tuple[str, str]] = []
    direct_records: list[tuple[str, str]] = []
    headers_seen: set[str] = set()

    with zipfile.ZipFile(io.BytesIO(alignment_zip)) as alignments:
        members = alignment_member_names(alignments)
        if len(members) != 763:
            raise ValueError(f"Expected 763 COS alignment files, observed {len(members)}")
        for member in members:
            locus = Path(member).stem
            for original_header, aligned in parse_fasta(alignments.read(member)):
                source_taxon = original_header.split()[0]
                sequence = ungap(aligned)
                invalid = "".join(sorted(set(sequence) - DNA_ALPHABET))
                ambiguous_count = sum(base not in {"A", "C", "G", "T"} for base in sequence)
                ambiguous_fraction = (
                    ambiguous_count / len(sequence) if sequence else 1.0
                )
                internal_stops, terminal_stop = internal_stop_count(sequence)
                mapping_header = f"{safe_token(source_taxon)}-{safe_token(locus)}"
                if mapping_header in headers_seen:
                    raise ValueError(f"Duplicate normalized target header: {mapping_header}")
                headers_seen.add(mapping_header)

                mapping_ok = (
                    len(sequence) >= min_length
                    and not invalid
                    and ambiguous_fraction <= max_ambiguous_fraction
                )
                direct_ok = (
                    mapping_ok
                    and len(sequence) % 3 == 0
                    and internal_stops == 0
                )
                if mapping_ok:
                    mapping_records.append((mapping_header, sequence))
                if direct_ok:
                    direct_records.append((mapping_header, sequence))

                sequence_rows.append(
                    {
                        "locus": locus,
                        "source_taxon": source_taxon,
                        "original_header": original_header,
                        "alignment_length": len(aligned),
                        "ungapped_length": len(sequence),
                        "gap_fraction": (
                            f"{(len(aligned) - len(sequence)) / len(aligned):.6f}"
                            if aligned
                            else "1.000000"
                        ),
                        "ambiguous_count": ambiguous_count,
                        "ambiguous_fraction": f"{ambiguous_fraction:.6f}",
                        "length_mod_3": len(sequence) % 3,
                        "internal_stop_count_frame0": internal_stops,
                        "terminal_stop_frame0": str(terminal_stop).lower(),
                        "invalid_characters": invalid,
                        "mapping_reference_included": str(mapping_ok).lower(),
                        "direct_cds_candidate": str(direct_ok).lower(),
                        "mapping_header": mapping_header,
                    }
                )

    by_locus: dict[str, list[dict[str, object]]] = {}
    for row in sequence_rows:
        by_locus.setdefault(str(row["locus"]), []).append(row)
    locus_rows: list[dict[str, object]] = []
    for locus, rows in sorted(by_locus.items()):
        lengths = [int(row["ungapped_length"]) for row in rows]
        taxa = sorted({str(row["source_taxon"]) for row in rows})
        mapping_count = sum(row["mapping_reference_included"] == "true" for row in rows)
        direct_count = sum(row["direct_cds_candidate"] == "true" for row in rows)
        locus_rows.append(
            {
                "locus": locus,
                "source_sequence_count": len(rows),
                "source_taxon_count": len(taxa),
                "source_taxa": "|".join(taxa),
                "min_ungapped_length": min(lengths),
                "median_ungapped_length": f"{statistics.median(lengths):.1f}",
                "max_ungapped_length": max(lengths),
                "mapping_reference_count": mapping_count,
                "direct_cds_candidate_count": direct_count,
                "any_source_direct_cds_candidate": str(direct_count > 0).lower(),
                "all_sources_direct_cds_candidate": str(direct_count == len(rows)).lower(),
            }
        )
    return sequence_rows, locus_rows, mapping_records, direct_records


def write_csv(
    path: Path,
    rows: Iterable[Mapping[str, object]],
    fields: Sequence[str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_fasta(path: Path, records: Iterable[tuple[str, str]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as handle:
        for header, sequence in records:
            handle.write(f">{header}\n")
            for start in range(0, len(sequence), 80):
                handle.write(sequence[start : start + 80] + "\n")
            count += 1
    return count


def build_summary(
    *,
    source_archive: Path,
    nested_member: str,
    source_bytes: bytes,
    alignment_zip: bytes,
    sequence_rows: Sequence[Mapping[str, object]],
    locus_rows: Sequence[Mapping[str, object]],
    mapping_count: int,
    direct_count: int,
    min_length: int,
    max_ambiguous_fraction: float,
) -> dict[str, object]:
    taxa = sorted({str(row["source_taxon"]) for row in sequence_rows})
    lengths = [int(row["ungapped_length"]) for row in sequence_rows]
    any_direct = sum(
        row["any_source_direct_cds_candidate"] == "true" for row in locus_rows
    )
    all_direct = sum(
        row["all_sources_direct_cds_candidate"] == "true" for row in locus_rows
    )
    ready = any_direct == len(locus_rows)
    direct_mod3 = sum(int(row["length_mod_3"]) == 0 for row in sequence_rows)
    no_internal_stops = sum(
        int(row["internal_stop_count_frame0"]) == 0 for row in sequence_rows
    )
    return {
        "audit_name": "Mandel 2014 COS763 HybPiper-readiness audit",
        "source_dataset": "Dryad 10.5061/dryad.gr93t version 1",
        "source_license": "CC0-1.0",
        "source_archive": str(source_archive),
        "source_archive_sha256": sha256_bytes(source_bytes),
        "nested_alignment_member": nested_member,
        "alignment_zip_sha256": sha256_bytes(alignment_zip),
        "locus_count": len(locus_rows),
        "sequence_count": len(sequence_rows),
        "source_taxon_count": len(taxa),
        "source_taxa": taxa,
        "median_sources_per_locus": statistics.median(
            int(row["source_sequence_count"]) for row in locus_rows
        ),
        "min_sources_per_locus": min(
            int(row["source_sequence_count"]) for row in locus_rows
        ),
        "max_sources_per_locus": max(
            int(row["source_sequence_count"]) for row in locus_rows
        ),
        "median_ungapped_length": statistics.median(lengths),
        "min_ungapped_length": min(lengths),
        "max_ungapped_length": max(lengths),
        "length_multiple_of_three_count": direct_mod3,
        "length_multiple_of_three_fraction": direct_mod3 / len(sequence_rows),
        "frame0_no_internal_stop_count": no_internal_stops,
        "frame0_no_internal_stop_fraction": no_internal_stops / len(sequence_rows),
        "mapping_reference_sequence_count": mapping_count,
        "direct_cds_candidate_sequence_count": direct_count,
        "loci_with_at_least_one_direct_cds_candidate": any_direct,
        "loci_with_all_sources_direct_cds_candidate": all_direct,
        "ready_as_complete_direct_hybpiper_nucleotide_target": ready,
        "minimum_sequence_length": min_length,
        "maximum_ambiguous_fraction": max_ambiguous_fraction,
        "recommended_role": (
            "mapping_reference_or_frame-correction_input_only"
            if not ready
            else "direct_hybpiper_nucleotide_target_candidate"
        ),
        "primary_chang2026_path": (
            "Retain de novo transcriptome assembly plus orthology inference as the primary route."
        ),
        "claim_limit": (
            "COS763 is a source-backed foundational Compositae alignment set, not the exact Moreyra Compositae1061 target. The unframed mapping reference must not be used as validated CDS input without reading-frame and orthology correction."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--archive", type=Path)
    group.add_argument("--archive-dir", type=Path)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    parser.add_argument("--min-length", type=int, default=90)
    parser.add_argument("--max-ambiguous-fraction", type=float, default=0.01)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_path, nested_member, alignment_zip = locate_alignment_archive(
        archive=args.archive,
        archive_dir=args.archive_dir,
    )
    source_bytes = source_path.read_bytes()
    sequence_rows, locus_rows, mapping_records, direct_records = analyze(
        alignment_zip,
        min_length=args.min_length,
        max_ambiguous_fraction=args.max_ambiguous_fraction,
    )

    args.outdir.mkdir(parents=True, exist_ok=True)
    write_csv(args.outdir / "cos763_sequence_readiness.csv", sequence_rows, SEQUENCE_FIELDS)
    write_csv(args.outdir / "cos763_locus_readiness.csv", locus_rows, LOCUS_FIELDS)
    mapping_count = write_fasta(
        args.outdir / "cos763_unframed_multisource_mapping_reference.fasta",
        mapping_records,
    )
    direct_count = write_fasta(
        args.outdir / "cos763_direct_cds_candidate_subset.fasta",
        direct_records,
    )
    summary = build_summary(
        source_archive=source_path,
        nested_member=nested_member,
        source_bytes=source_bytes,
        alignment_zip=alignment_zip,
        sequence_rows=sequence_rows,
        locus_rows=locus_rows,
        mapping_count=mapping_count,
        direct_count=direct_count,
        min_length=args.min_length,
        max_ambiguous_fraction=args.max_ambiguous_fraction,
    )
    (args.outdir / "cos763_hybpiper_readiness_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"locus_count={summary['locus_count']}")
    print(f"sequence_count={summary['sequence_count']}")
    print(f"source_taxon_count={summary['source_taxon_count']}")
    print(
        "length_multiple_of_three_fraction="
        f"{summary['length_multiple_of_three_fraction']:.6f}"
    )
    print(
        "loci_with_at_least_one_direct_cds_candidate="
        f"{summary['loci_with_at_least_one_direct_cds_candidate']}"
    )
    print(
        "ready_as_complete_direct_hybpiper_nucleotide_target="
        f"{summary['ready_as_complete_direct_hybpiper_nucleotide_target']}"
    )
    print(args.outdir / "cos763_hybpiper_readiness_summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
