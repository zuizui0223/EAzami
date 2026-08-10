#!/usr/bin/env python3
"""Recover and audit public files from ldmoreyra/A-thorny-tale.

The journal Data Availability Statement points only to PRJNA957074 and the
supplement, but the corresponding author's public GitHub repository also contains
HybPiper recovery statistics, the sequence-length matrix and a paralog report.
This script downloads those files, records their hashes, parses the two TSV files,
extracts XLSX sheets using only the Python standard library, and produces summary
statistics without pretending that the exact manually retained 350-locus list can
be reconstructed from summary files alone.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import shutil
import statistics
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from pathlib import Path
from typing import Iterable, Mapping, Sequence

REPOSITORY = "ldmoreyra/A-thorny-tale"
RAW_BASE = "https://raw.githubusercontent.com/ldmoreyra/A-thorny-tale/main"
FILES = {
    "hybpiper_stats": {
        "filename": "hybpiper_stats_exonerate.tsv",
        "url": f"{RAW_BASE}/hybpiper_stats_exonerate.tsv",
        "expected_github_blob_sha": "e3680fc9dc49dbbcc3219d38b97759f339f0e139",
    },
    "seq_lengths": {
        "filename": "seq_lengths_exonerate.tsv",
        "url": f"{RAW_BASE}/seq_lengths_exonerate.tsv",
        "expected_github_blob_sha": "9fba52328882d34cfde35f558b5ce3527bdf7411",
    },
    "paralog_report": {
        "filename": "paralog_report.xlsx",
        "url": f"{RAW_BASE}/paralog_report.xlsx",
        "expected_github_blob_sha": "bc8856784eabc0b81c5fdddab23f085c907a6f36",
    },
}

DEFAULT_OUTDIR = Path("data/evidence/generated/moreyra_author_repository")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def download(url: str, path: Path, timeout: int = 120, retries: int = 5) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".part")
    headers = {
        "User-Agent": "EAzami-Moreyra-author-repository-audit/1.0",
        "Accept": "*/*",
    }
    for attempt in range(retries):
        try:
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=timeout) as response:
                with temp.open("wb") as handle:
                    shutil.copyfileobj(response, handle)
            temp.replace(path)
            return
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            if temp.exists():
                temp.unlink()
            if attempt + 1 == retries:
                raise RuntimeError(f"Download failed after {retries} attempts: {url}") from exc
            delay = 2**attempt
            if isinstance(exc, urllib.error.HTTPError):
                retry_after = exc.headers.get("Retry-After")
                if retry_after and retry_after.isdigit():
                    delay = max(delay, int(retry_after))
            time.sleep(delay)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if not reader.fieldnames:
            raise ValueError(f"{path}: missing TSV header")
        return [
            {key: (value or "").strip() for key, value in row.items()}
            for row in reader
            if any((value or "").strip() for value in row.values())
        ]


def write_csv(path: Path, rows: Iterable[Mapping[str, object]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def as_float(value: object) -> float | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def median(values: Iterable[float]) -> float | None:
    usable = [value for value in values if math.isfinite(value)]
    return statistics.median(usable) if usable else None


def summarize_hybpiper_stats(rows: Sequence[Mapping[str, str]]) -> dict[str, object]:
    if not rows:
        raise ValueError("HybPiper stats table is empty")
    required = {
        "Name",
        "GenesMapped",
        "GenesWithSeqs",
        "GenesAt50pct",
        "GenesAt75pct",
        "ParalogWarningsLong",
        "ParalogWarningsDepth",
    }
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"HybPiper stats missing fields: {sorted(missing)}")

    def numeric(field: str) -> list[float]:
        return [value for row in rows if (value := as_float(row.get(field))) is not None]

    return {
        "sample_rows": len(rows),
        "unique_sample_names": len({row["Name"] for row in rows}),
        "genes_mapped_max": max(numeric("GenesMapped")),
        "genes_mapped_median": median(numeric("GenesMapped")),
        "genes_with_sequences_median": median(numeric("GenesWithSeqs")),
        "genes_at_50pct_median": median(numeric("GenesAt50pct")),
        "genes_at_75pct_median": median(numeric("GenesAt75pct")),
        "paralog_warnings_long_median": median(numeric("ParalogWarningsLong")),
        "paralog_warnings_depth_median": median(numeric("ParalogWarningsDepth")),
        "samples_with_any_chimera_warning": sum(
            1 for row in rows if (as_float(row.get("GenesWithChimeraWarning")) or 0) > 0
        ),
    }


def infer_seq_length_layout(rows: Sequence[Mapping[str, str]]) -> tuple[str, list[str]]:
    if not rows:
        raise ValueError("Sequence-length matrix is empty")
    fields = list(rows[0])
    first = fields[0]
    first_values = [row.get(first, "") for row in rows[:20]]
    sample_like = sum(
        bool(re.search(r"(?:Cirsium|Carduus|Afrocarduus|Notobasis|Picnomon|Silybum|Alfredia)", value))
        for value in first_values
    )
    if sample_like >= max(1, len(first_values) // 2):
        return first, fields[1:]
    raise ValueError(
        "Unexpected seq_lengths layout: first column does not look like sample names. "
        f"Header begins with {fields[:5]!r}"
    )


def summarize_seq_lengths(
    rows: Sequence[Mapping[str, str]],
) -> tuple[dict[str, object], list[dict[str, object]]]:
    sample_field, loci = infer_seq_length_layout(rows)
    sample_count = len(rows)
    locus_rows: list[dict[str, object]] = []
    for locus in loci:
        lengths = [
            value
            for row in rows
            if (value := as_float(row.get(locus))) is not None and value > 0
        ]
        recovered = len(lengths)
        locus_rows.append(
            {
                "locus": locus,
                "samples_with_sequence": recovered,
                "sample_count": sample_count,
                "occupancy": recovered / sample_count if sample_count else 0,
                "min_recovered_length": min(lengths) if lengths else "",
                "median_recovered_length": median(lengths) if lengths else "",
                "max_recovered_length": max(lengths) if lengths else "",
            }
        )

    occupancy_counts = {
        "ge_0_80": sum(row["occupancy"] >= 0.80 for row in locus_rows),
        "ge_0_90": sum(row["occupancy"] >= 0.90 for row in locus_rows),
        "ge_0_95": sum(row["occupancy"] >= 0.95 for row in locus_rows),
        "eq_1_00": sum(row["occupancy"] == 1.0 for row in locus_rows),
    }
    return (
        {
            "layout": "samples_by_loci",
            "sample_field": sample_field,
            "sample_rows": sample_count,
            "target_locus_columns": len(loci),
            "occupancy_threshold_counts": occupancy_counts,
        },
        locus_rows,
    )


XLSX_NS = {
    "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "rel": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "pkgrel": "http://schemas.openxmlformats.org/package/2006/relationships",
}


def column_index(cell_ref: str) -> int:
    letters = re.match(r"[A-Z]+", cell_ref)
    if not letters:
        raise ValueError(f"Malformed XLSX cell reference: {cell_ref}")
    value = 0
    for char in letters.group(0):
        value = value * 26 + (ord(char) - ord("A") + 1)
    return value - 1


def xlsx_shared_strings(archive: zipfile.ZipFile) -> list[str]:
    try:
        root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    except KeyError:
        return []
    values: list[str] = []
    for item in root.findall("main:si", XLSX_NS):
        values.append("".join(node.text or "" for node in item.findall(".//main:t", XLSX_NS)))
    return values


def xlsx_sheet_targets(archive: zipfile.ZipFile) -> list[tuple[str, str]]:
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    relationship_map = {
        rel.attrib["Id"]: rel.attrib["Target"]
        for rel in rels.findall("pkgrel:Relationship", XLSX_NS)
    }
    output: list[tuple[str, str]] = []
    for sheet in workbook.findall("main:sheets/main:sheet", XLSX_NS):
        name = sheet.attrib["name"]
        relation_id = sheet.attrib[f"{{{XLSX_NS['rel']}}}id"]
        target = relationship_map[relation_id]
        if target.startswith("/"):
            path = target.lstrip("/")
        else:
            path = str(Path("xl") / target)
        output.append((name, path.replace("\\", "/")))
    return output


def xlsx_cell_value(cell: ET.Element, shared: Sequence[str]) -> str:
    cell_type = cell.attrib.get("t", "")
    if cell_type == "inlineStr":
        return "".join(node.text or "" for node in cell.findall(".//main:t", XLSX_NS))
    value_node = cell.find("main:v", XLSX_NS)
    if value_node is None or value_node.text is None:
        return ""
    value = value_node.text
    if cell_type == "s":
        index = int(value)
        return shared[index] if 0 <= index < len(shared) else value
    if cell_type == "b":
        return "TRUE" if value == "1" else "FALSE"
    return value


def extract_xlsx(path: Path, outdir: Path) -> tuple[list[dict[str, object]], dict[str, list[list[str]]]]:
    outdir.mkdir(parents=True, exist_ok=True)
    metadata: list[dict[str, object]] = []
    matrices: dict[str, list[list[str]]] = {}
    with zipfile.ZipFile(path) as archive:
        shared = xlsx_shared_strings(archive)
        for sheet_index, (sheet_name, target) in enumerate(xlsx_sheet_targets(archive), start=1):
            root = ET.fromstring(archive.read(target))
            sparse_rows: dict[int, dict[int, str]] = {}
            max_col = -1
            for row in root.findall("main:sheetData/main:row", XLSX_NS):
                row_index = int(row.attrib.get("r", "1")) - 1
                values: dict[int, str] = {}
                for cell in row.findall("main:c", XLSX_NS):
                    ref = cell.attrib.get("r", "A1")
                    col_index = column_index(ref)
                    values[col_index] = xlsx_cell_value(cell, shared)
                    max_col = max(max_col, col_index)
                sparse_rows[row_index] = values
            max_row = max(sparse_rows, default=-1)
            matrix = [
                [sparse_rows.get(row, {}).get(col, "") for col in range(max_col + 1)]
                for row in range(max_row + 1)
            ]
            safe_sheet = re.sub(r"[^A-Za-z0-9._-]+", "_", sheet_name).strip("_") or f"sheet_{sheet_index}"
            output_path = outdir / f"sheet_{sheet_index:02d}_{safe_sheet}.csv"
            with output_path.open("w", encoding="utf-8", newline="") as handle:
                csv.writer(handle).writerows(matrix)
            nonempty = sum(bool(value) for row in matrix for value in row)
            metadata.append(
                {
                    "sheet_index": sheet_index,
                    "sheet_name": sheet_name,
                    "rows": len(matrix),
                    "columns": max_col + 1,
                    "nonempty_cells": nonempty,
                    "output_path": str(output_path),
                }
            )
            matrices[sheet_name] = matrix
    return metadata, matrices


def summarize_paralog_workbook(
    metadata: Sequence[Mapping[str, object]], matrices: Mapping[str, Sequence[Sequence[str]]]
) -> dict[str, object]:
    sheet_summaries: dict[str, object] = {}
    for sheet_name, matrix in matrices.items():
        header = list(matrix[0]) if matrix else []
        flattened = [value for row in matrix for value in row if str(value).strip()]
        numeric = [value for value in (as_float(item) for item in flattened) if value is not None]
        text_counter = Counter(str(value).strip().casefold() for value in flattened if as_float(value) is None)
        sheet_summaries[sheet_name] = {
            "rows": len(matrix),
            "columns": max((len(row) for row in matrix), default=0),
            "header_preview": header[:12],
            "numeric_cell_count": len(numeric),
            "numeric_min": min(numeric) if numeric else None,
            "numeric_max": max(numeric) if numeric else None,
            "most_common_text_values": text_counter.most_common(10),
        }
    return {
        "sheet_count": len(metadata),
        "sheets": sheet_summaries,
        "interpretation_limit": (
            "The workbook documents paralog warnings/copies, but the paper also used manual gene-tree "
            "inspection. Summary files alone do not identify the final 350 retained loci with certainty."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_dir = args.outdir / "source"
    extracted_dir = args.outdir / "extracted"
    source_dir.mkdir(parents=True, exist_ok=True)
    extracted_dir.mkdir(parents=True, exist_ok=True)

    provenance_rows: list[dict[str, object]] = []
    paths: dict[str, Path] = {}
    for key, metadata in FILES.items():
        path = source_dir / metadata["filename"]
        if args.force or not path.exists():
            download(metadata["url"], path)
        paths[key] = path
        provenance_rows.append(
            {
                "artifact_key": key,
                "repository": REPOSITORY,
                "filename": metadata["filename"],
                "url": metadata["url"],
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
                "github_blob_sha": metadata["expected_github_blob_sha"],
            }
        )

    stats_rows = read_tsv(paths["hybpiper_stats"])
    seq_rows = read_tsv(paths["seq_lengths"])
    stats_summary = summarize_hybpiper_stats(stats_rows)
    seq_summary, locus_rows = summarize_seq_lengths(seq_rows)
    xlsx_metadata, xlsx_matrices = extract_xlsx(paths["paralog_report"], extracted_dir / "paralog_report")
    paralog_summary = summarize_paralog_workbook(xlsx_metadata, xlsx_matrices)

    write_csv(
        args.outdir / "source_provenance.csv",
        provenance_rows,
        ("artifact_key", "repository", "filename", "url", "size_bytes", "sha256", "github_blob_sha"),
    )
    write_csv(
        args.outdir / "locus_occupancy.csv",
        locus_rows,
        (
            "locus",
            "samples_with_sequence",
            "sample_count",
            "occupancy",
            "min_recovered_length",
            "median_recovered_length",
            "max_recovered_length",
        ),
    )
    write_csv(
        args.outdir / "paralog_report_sheets.csv",
        xlsx_metadata,
        ("sheet_index", "sheet_name", "rows", "columns", "nonempty_cells", "output_path"),
    )

    summary = {
        "repository": REPOSITORY,
        "source_files": provenance_rows,
        "hybpiper_stats": stats_summary,
        "seq_lengths": seq_summary,
        "paralog_report": paralog_summary,
        "paper_filtering_context": {
            "mapped_target_loci_reported_in_paper": 1064,
            "retained_alignments_reported_in_paper": 350,
            "discard_rule": "discard genes with >10 HybPiper paralog warnings; manually inspect 1-10-warning gene trees; retain loci with <50% missing data and >=80% species presence",
            "exact_350_locus_list_recovered": False,
            "reason": "manual gene-tree orthology decisions and final alignment-level missingness are not encoded as an explicit retained-locus list in the public repository files",
        },
    }
    summary_path = args.outdir / "author_repository_audit_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"source_files={len(provenance_rows)}")
    print(f"hybpiper_sample_rows={stats_summary['sample_rows']}")
    print(f"target_locus_columns={seq_summary['target_locus_columns']}")
    print(f"loci_occupancy_ge_0_80={seq_summary['occupancy_threshold_counts']['ge_0_80']}")
    print(f"paralog_report_sheets={paralog_summary['sheet_count']}")
    print(summary_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
