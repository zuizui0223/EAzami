#!/usr/bin/env python3
"""Summarize per-sample QC for executed Chang 2026 transcriptome assemblies.

The QC gate is intentionally mechanical rather than biological: exact sample/run
identity, expected paired-read count at fastp input, non-empty assembly/protein
products, and stable protein-header prefixes must pass. Transcript N50, peptide
counts, Q30, GC and resource use are reported as diagnostics but no post-hoc
biological threshold is imposed on the six published colour morph samples.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import statistics
from pathlib import Path
from typing import Iterable, Mapping, Sequence

FIELDS = (
    "sample_id", "taxon", "morph", "run", "expected_paired_reads",
    "fastp_before_reads", "read_count_matches_expected",
    "fastp_after_reads", "fastp_retained_fraction", "fastp_after_q20_rate",
    "fastp_after_q30_rate", "fastp_after_gc_content",
    "transcript_count", "transcript_total_bases", "transcript_n50",
    "transcript_median_length", "transcript_max_length",
    "peptide_count", "peptide_total_aa", "peptide_n50_aa",
    "peptide_median_length", "peptide_max_length", "peptides_ge_100aa",
    "prefixed_header_count", "all_headers_have_sample_prefix",
    "raw_gib", "trimmed_gib", "trinity_fasta_gib", "peptide_fasta_gib",
    "trinity_peak_rss_gib", "trinity_elapsed_seconds",
    "mechanical_gate_pass", "gate_fail_reasons",
)


def clean(value: object) -> str:
    return str(value or "").strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [{key: clean(value) for key, value in row.items()} for row in csv.DictReader(handle) if any(clean(value) for value in row.values())]


def write_csv(path: Path, rows: Iterable[Mapping[str, object]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), extrasaction="ignore"); writer.writeheader(); writer.writerows(rows)


def fasta_lengths(path: Path) -> list[int]:
    if not path.is_file() or path.stat().st_size == 0: return []
    lengths: list[int] = []; current = 0
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if line.startswith(">"):
                if current: lengths.append(current)
                current = 0
            else: current += len("".join(line.split()))
    if current: lengths.append(current)
    return lengths


def n50(lengths: Sequence[int]) -> int:
    if not lengths: return 0
    target = sum(lengths) / 2; cumulative = 0
    for value in sorted(lengths, reverse=True):
        cumulative += value
        if cumulative >= target: return value
    return 0


def fasta_metrics(path: Path) -> dict[str, object]:
    lengths = fasta_lengths(path)
    if not lengths: return {"count": 0, "total": 0, "n50": 0, "median": 0.0, "max": 0}
    return {"count": len(lengths), "total": sum(lengths), "n50": n50(lengths), "median": statistics.median(lengths), "max": max(lengths)}


def prefix_metrics(path: Path, sample_id: str) -> tuple[int, bool]:
    if not path.is_file() or path.stat().st_size == 0: return 0, False
    with path.open(encoding="utf-8", errors="replace") as handle:
        headers = [line[1:].strip().split()[0] for line in handle if line.startswith(">")]
    return len(headers), bool(headers) and all(header.startswith(sample_id + "|") for header in headers)


def nested(mapping: Mapping[str, object], *keys: str, default: object = "") -> object:
    value: object = mapping
    for key in keys:
        if not isinstance(value, Mapping): return default
        value = value.get(key, default)
    return value


def read_fastp(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() and path.stat().st_size else {}


def file_gib(paths: Sequence[Path]) -> float:
    return sum(path.stat().st_size for path in paths if path.is_file()) / 1024**3


def parse_elapsed_seconds(value: str) -> float | None:
    parts = value.strip().split(":")
    try:
        if len(parts) == 3: return float(parts[0])*3600 + float(parts[1])*60 + float(parts[2])
        if len(parts) == 2: return float(parts[0])*60 + float(parts[1])
        return float(value)
    except ValueError: return None


def parse_gnu_time(path: Path) -> dict[str, float | None]:
    result: dict[str, float | None] = {"peak_rss_gib": None, "elapsed_seconds": None}
    if not path.is_file(): return result
    text = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"Maximum resident set size \(kbytes\):\s*(\d+)", text)
    if m: result["peak_rss_gib"] = int(m.group(1)) / 1024**2
    m = re.search(r"Elapsed \(wall clock\) time \(h:mm:ss or m:ss\):\s*([^\n]+)", text)
    if m: result["elapsed_seconds"] = parse_elapsed_seconds(m.group(1))
    return result


def expected_index(panel: Path, resource_plan: Path | None) -> dict[str, dict[str, object]]:
    panel_rows = read_csv(panel); resources = {row["sample_id"]: row for row in read_csv(resource_plan)} if resource_plan else {}; output = {}
    for row in panel_rows:
        sample_id = row["sample_id"]; resource = resources.get(sample_id, {}); spots_text = clean(resource.get("spots")) or clean(row.get("matched_spots")); spots = int(float(spots_text)) if spots_text else 0
        output[sample_id] = {"sample_id": sample_id, "taxon": row.get("taxon", ""), "morph": row.get("morph", ""), "run": row.get("matched_run", ""), "expected_paired_reads": int(clean(resource.get("paired_read_count")) or 2*spots)}
    return output


def summarize_sample(meta: Mapping[str, object], results_dir: Path) -> dict[str, object]:
    sample_id = str(meta["sample_id"]); run = str(meta["run"]); root = results_dir / "samples" / sample_id
    raw1 = root / "raw" / f"{run}_1.fastq.gz"; raw2 = root / "raw" / f"{run}_2.fastq.gz"; trim1 = root / "trimmed" / f"{sample_id}.R1.trim.fastq.gz"; trim2 = root / "trimmed" / f"{sample_id}.R2.trim.fastq.gz"; fastp_json = root / "trimmed" / f"{sample_id}.fastp.json"; trinity = root / "trinity" / "Trinity.fasta"; peptide = root / "transdecoder" / "Trinity.fasta.transdecoder.pep"; prefixed = results_dir / "prefixed_proteomes" / f"{sample_id}.faa"
    fastp = read_fastp(fastp_json); before = int(nested(fastp, "summary", "before_filtering", "total_reads", default=0) or 0); after = int(nested(fastp, "summary", "after_filtering", "total_reads", default=0) or 0); expected = int(meta["expected_paired_reads"]); retained = after / before if before else math.nan
    transcript = fasta_metrics(trinity); pep = fasta_metrics(peptide); header_count, headers_ok = prefix_metrics(prefixed, sample_id); timing = parse_gnu_time(root / "resources" / "trinity.time.txt")
    reasons = []
    if before != expected: reasons.append(f"fastp_before_reads_{before}_neq_expected_{expected}")
    if after <= 0: reasons.append("no_reads_after_fastp")
    if transcript["count"] <= 0: reasons.append("empty_trinity_transcriptome")
    if pep["count"] <= 0: reasons.append("empty_transdecoder_peptides")
    if header_count <= 0 or not headers_ok: reasons.append("invalid_prefixed_proteome_headers")
    return {**meta, "fastp_before_reads": before, "read_count_matches_expected": before == expected, "fastp_after_reads": after, "fastp_retained_fraction": retained, "fastp_after_q20_rate": nested(fastp, "summary", "after_filtering", "q20_rate", default=""), "fastp_after_q30_rate": nested(fastp, "summary", "after_filtering", "q30_rate", default=""), "fastp_after_gc_content": nested(fastp, "summary", "after_filtering", "gc_content", default=""), "transcript_count": transcript["count"], "transcript_total_bases": transcript["total"], "transcript_n50": transcript["n50"], "transcript_median_length": transcript["median"], "transcript_max_length": transcript["max"], "peptide_count": pep["count"], "peptide_total_aa": pep["total"], "peptide_n50_aa": pep["n50"], "peptide_median_length": pep["median"], "peptide_max_length": pep["max"], "peptides_ge_100aa": sum(value >= 100 for value in fasta_lengths(peptide)), "prefixed_header_count": header_count, "all_headers_have_sample_prefix": headers_ok, "raw_gib": file_gib((raw1, raw2)), "trimmed_gib": file_gib((trim1, trim2)), "trinity_fasta_gib": file_gib((trinity,)), "peptide_fasta_gib": file_gib((peptide,)), "trinity_peak_rss_gib": timing["peak_rss_gib"] if timing["peak_rss_gib"] is not None else "", "trinity_elapsed_seconds": timing["elapsed_seconds"] if timing["elapsed_seconds"] is not None else "", "mechanical_gate_pass": not reasons, "gate_fail_reasons": "|".join(reasons)}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(); p.add_argument("--panel", type=Path, required=True); p.add_argument("--results-dir", type=Path, required=True); p.add_argument("--resource-plan", type=Path); p.add_argument("--sample-id", action="append", default=[]); p.add_argument("--outdir", type=Path); return p.parse_args()


def main() -> int:
    args = parse_args(); index = expected_index(args.panel, args.resource_plan); selected = args.sample_id or sorted(index); missing = [sample for sample in selected if sample not in index]
    if missing: raise SystemExit("Unknown sample IDs: " + "|".join(missing))
    rows = [summarize_sample(index[sample], args.results_dir) for sample in selected]; outdir = args.outdir or args.results_dir / "qc"; write_csv(outdir / "transcriptome_qc_summary.csv", rows, FIELDS); passed = sum(bool(row["mechanical_gate_pass"]) for row in rows)
    summary = {"qc_version": "chang2026_transcriptome_qc_v1", "sample_count": len(rows), "mechanical_gate_pass_count": passed, "mechanical_gate_fail_count": len(rows)-passed, "sample_ids": selected, "gate_definition": ["fastp input read count equals expected 2 x official SRA spots", "at least one read remains after fastp", "Trinity FASTA is non-empty", "TransDecoder peptide FASTA is non-empty", "all prefixed protein headers begin with stable sample_id plus pipe"], "non_gate_diagnostics": ["Q20/Q30/GC and read retention", "transcript count/total bases/N50/median/max", "peptide count/length distribution", "GNU time peak RSS and elapsed time when available"], "claim_limit": "This QC gate establishes mechanical execution and identity consistency only; it does not establish biological transcriptome completeness or orthology."}
    outdir.mkdir(parents=True, exist_ok=True); (outdir / "transcriptome_qc_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8"); print(f"sample_count={len(rows)}"); print(f"mechanical_gate_pass_count={passed}"); print(f"mechanical_gate_fail_count={len(rows)-passed}"); return 0 if passed == len(rows) else 1


if __name__ == "__main__": raise SystemExit(main())
