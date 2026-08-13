#!/usr/bin/env python3
"""Audit the public Ulleung Cirsium nipponicum genome as a nuclear-tree augmentation.

The primary Japan-origin panel is deliberately built from unique public biological
samples in Moreyra 2025 and Chang 2025/2026. A separate high-quality genome exists
for an Ulleung Island C. nipponicum individual (PRJNA1127082; Figshare article
26927092). This audit asks only whether the public Figshare article exposes stable
assembly/annotation sequence files from which the frozen Compositae1061 locus set
can later be recovered. It does not silently append the genome to the primary tree.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

EXPECTED_ARTICLE_ID = 26927092
EXPECTED_BIOPROJECT = "PRJNA1127082"
EXPECTED_TAXON = "Cirsium nipponicum"

SEQUENCE_SUFFIXES = (
    ".fa", ".fasta", ".fna", ".ffn", ".faa", ".fas", ".fsa", ".cds",
    ".gff", ".gff3", ".gtf", ".gb", ".gbk", ".gbff", ".zip", ".gz",
)


def clean(value: object) -> str:
    return str(value or "").strip()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Figshare article response must be a JSON object")
    return data


def classify_file(name: str) -> tuple[bool, str]:
    n = name.casefold()
    sequence_like = n.endswith(SEQUENCE_SUFFIXES)
    if any(token in n for token in ("protein", "pep", "amino")):
        return sequence_like, "protein_or_peptide_candidate"
    if any(token in n for token in ("cds", "coding", "transcript", "rna")):
        return sequence_like, "cds_or_transcript_candidate"
    if any(token in n for token in ("gff", "gtf", "annotation")):
        return sequence_like, "annotation_candidate"
    if any(token in n for token in ("genome", "assembly", "purge", "contig", "scaffold")):
        return sequence_like, "genome_assembly_candidate"
    if sequence_like:
        return True, "generic_sequence_or_archive_candidate"
    return False, "non_sequence_support_file"


def audit(data: dict[str, Any]) -> tuple[list[dict[str, str]], dict[str, object]]:
    article_id = data.get("id")
    if article_id != EXPECTED_ARTICLE_ID:
        raise ValueError(f"unexpected Figshare article id {article_id!r}")
    title = clean(data.get("title"))
    if "Cirsium nipponicum" not in title:
        raise ValueError(f"unexpected Figshare article title: {title}")
    files = data.get("files")
    if not isinstance(files, list) or not files:
        raise ValueError("Figshare article has no public files")

    rows: list[dict[str, str]] = []
    for item in files:
        if not isinstance(item, dict):
            raise ValueError("Figshare file entry is not an object")
        name = clean(item.get("name"))
        if not name:
            raise ValueError("Figshare file is missing a name")
        candidate, role = classify_file(name)
        rows.append(
            {
                "file_id": clean(item.get("id")),
                "name": name,
                "size_bytes": clean(item.get("size")),
                "download_url": clean(item.get("download_url")),
                "supplied_md5": clean(item.get("supplied_md5")),
                "computed_md5": clean(item.get("computed_md5")),
                "is_link_only": clean(item.get("is_link_only")).lower(),
                "sequence_candidate": str(candidate).lower(),
                "candidate_role": role,
            }
        )

    candidates = [row for row in rows if row["sequence_candidate"] == "true"]
    direct_seq = [
        row for row in candidates
        if row["candidate_role"] in {
            "protein_or_peptide_candidate",
            "cds_or_transcript_candidate",
            "genome_assembly_candidate",
        }
    ]
    stable_downloads = [row for row in candidates if row["download_url"]]
    total_bytes = sum(int(row["size_bytes"] or 0) for row in rows)
    candidate_bytes = sum(int(row["size_bytes"] or 0) for row in candidates)

    summary: dict[str, object] = {
        "contract_version": "cirsium_nipponicum_public_genome_augmentation_v1",
        "taxon": EXPECTED_TAXON,
        "region": "Korea_Ulleung_Island",
        "bioproject": EXPECTED_BIOPROJECT,
        "figshare_article_id": EXPECTED_ARTICLE_ID,
        "figshare_title": title,
        "figshare_doi": clean(data.get("doi")),
        "article_metadata_sha256": "filled_by_cli",
        "file_count": len(rows),
        "total_public_file_bytes": total_bytes,
        "sequence_or_archive_candidate_count": len(candidates),
        "sequence_or_archive_candidate_bytes": candidate_bytes,
        "direct_sequence_candidate_count": len(direct_seq),
        "stable_candidate_download_count": len(stable_downloads),
        "augmentation_candidate": bool(candidates and stable_downloads),
        "primary_294_panel_changed": False,
        "tree_tip_promotion_allowed": False,
        "promotion_gate": (
            "Recover the frozen Compositae1061 loci from the public genome/annotation, "
            "verify orthology/copy state and occupancy against the 294-tip matrix, then "
            "add the Ulleung individual only as a separately labelled public-genome "
            "augmentation/sensitivity until cross-data-type placement is validated."
        ),
        "sampling_policy": "No new China sampling decision is made by this audit.",
    }
    return rows, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--figshare-json", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args()

    raw = args.figshare_json.read_bytes()
    rows, summary = audit(load_json(args.figshare_json))
    summary["article_metadata_sha256"] = hashlib.sha256(raw).hexdigest()

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
