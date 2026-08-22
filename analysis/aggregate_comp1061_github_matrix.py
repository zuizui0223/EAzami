#!/usr/bin/env python3
"""Aggregate compact per-sample HybPiper GitHub Actions artifacts for current QC.

Each sample artifact must contain:
  sample_metadata.json
  retrieved_dna/*.FNA
  paralog_report.tsv

The aggregator reconstructs the multi-sample retrieved FASTA directory and the
single 20-row HybPiper-style paralog report consumed by the existing QC script.
It deliberately does not infer occupancy or promote a tree itself.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


def read_runs(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    tips = [r["tip_id"].strip() for r in rows]
    if not rows or len(tips) != len(set(tips)):
        raise ValueError("primary-runs table must contain unique tips")
    return rows


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = list(reader)
        return list(reader.fieldnames or []), rows


def aggregate(artifact_root: Path, runs_path: Path, outdir: Path) -> dict:
    runs = read_runs(runs_path)
    expected = {r["tip_id"] for r in runs}
    records = {}
    for meta_path in sorted(artifact_root.rglob("sample_metadata.json")):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        tip = str(meta.get("tip_id", "")).strip()
        if not tip:
            raise ValueError(f"missing tip_id in {meta_path}")
        if tip in records:
            raise ValueError(f"duplicate compact artifact for {tip}")
        records[tip] = (meta_path.parent, meta)
    observed = set(records)
    if observed != expected:
        raise ValueError(f"compact sample mismatch missing={sorted(expected-observed)} extra={sorted(observed-expected)}")

    retrieved_out = outdir / "retrieved_dna"
    retrieved_out.mkdir(parents=True, exist_ok=True)
    fasta_chunks: dict[str, list[str]] = defaultdict(list)
    paralog_rows = []
    all_gene_columns = set()
    sample_recovered_counts = {}

    for tip in sorted(expected):
        sample_dir, meta = records[tip]
        retrieved = sample_dir / "retrieved_dna"
        if not retrieved.is_dir():
            raise ValueError(f"missing retrieved_dna for {tip}")
        loci = 0
        for fasta in sorted(retrieved.glob("*.FNA")):
            text = fasta.read_text(encoding="utf-8").strip()
            if not text:
                continue
            fasta_chunks[fasta.name].append(text + "\n")
            loci += 1
        if loci == 0:
            raise ValueError(f"no recovered FASTA loci for {tip}")
        sample_recovered_counts[tip] = loci

        paralog_path = sample_dir / "paralog_report.tsv"
        if not paralog_path.is_file():
            raise ValueError(f"missing paralog report for {tip}")
        fields, rows = read_tsv(paralog_path)
        if "Species" not in fields or len(rows) != 1:
            raise ValueError(f"expected one Species row in {paralog_path}")
        row = rows[0]
        if row.get("Species", "").strip() != tip:
            raise ValueError(f"paralog Species mismatch for {tip}: {row.get('Species')!r}")
        genes = [x for x in fields if x != "Species"]
        all_gene_columns.update(genes)
        paralog_rows.append((tip, row))

    for name, chunks in sorted(fasta_chunks.items()):
        (retrieved_out / name).write_text("".join(chunks), encoding="utf-8")

    genes = sorted(all_gene_columns)
    paralog_out = outdir / "paralog_report.tsv"
    with paralog_out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["Species", *genes], delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for tip, row in sorted(paralog_rows):
            writer.writerow({"Species": tip, **{gene: (row.get(gene, "") or "0") for gene in genes}})

    summary = {
        "contract_version": "comp1061_github_matrix_aggregate_v1",
        "expected_samples": len(expected),
        "aggregated_samples": len(observed),
        "aggregated_locus_files": len(fasta_chunks),
        "sample_recovered_locus_counts": sample_recovered_counts,
        "paralog_gene_columns": len(genes),
        "full_panel_qc_not_yet_inferred": True,
        "claim_boundary": "This artifact aggregation only reconstructs the multi-sample FASTA/paralog inputs. Occupancy/no-paralog eligibility and tree acceptance remain downstream gates."
    }
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "aggregate_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--artifact-root", type=Path, required=True)
    p.add_argument("--runs", type=Path, required=True)
    p.add_argument("--outdir", type=Path, required=True)
    a = p.parse_args()
    result = aggregate(a.artifact_root, a.runs, a.outdir)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
