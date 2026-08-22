#!/usr/bin/env python3
"""Structural and descriptive QC for the frozen Comp1061 tree alignments.

This gate deliberately avoids post-hoc filtering on phylogenetic signal. It
checks that every pre-admitted locus produced a valid alignment with the
pre-registered focal taxa plus the sole tree reference ``OUTGROUP_saff``.
Gap and variability diagnostics are recorded for later sensitivity work but do
not remove loci once upstream occupancy/paralog/root-reference gates have been
passed.
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
from pathlib import Path

ROOT_OUTGROUP = "OUTGROUP_saff"
REQUIRED_REFERENCES = (ROOT_OUTGROUP,)
DNA_ALLOWED = set("ACGTURYSWKMBDHVN?-X")
RESOLVED = set("ACGT")
MISSING = set("-?")


def clean(x: object) -> str:
    return str(x or "").strip()


def read_primary(path: Path) -> list[str]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    tips = [clean(r.get("tip_id")) for r in rows]
    if len(tips) != 20 or len(set(tips)) != 20 or any(not x for x in tips):
        raise ValueError("Expected exactly 20 unique non-empty primary tip IDs")
    return tips


def read_loci(path: Path) -> list[str]:
    loci = [x.strip() for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    if len(loci) < 100:
        raise ValueError("Alignment QC requires at least 100 pre-admitted loci")
    if len(loci) != len(set(loci)):
        raise ValueError("Eligible locus list contains duplicates")
    return loci


def read_aligned_fasta(path: Path) -> dict[str, str]:
    records: dict[str, str] = {}
    name: str | None = None
    seq: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith(">"):
            if name is not None:
                if name in records:
                    raise ValueError(f"duplicate header {name}")
                records[name] = "".join(seq).upper()
            name = line[1:].split()[0]
            if not name:
                raise ValueError("empty FASTA header")
            seq = []
        else:
            if name is None:
                raise ValueError("sequence encountered before FASTA header")
            seq.append(line)
    if name is not None:
        if name in records:
            raise ValueError(f"duplicate header {name}")
        records[name] = "".join(seq).upper()
    if not records:
        raise ValueError("empty alignment")
    return records


def site_stats(records: dict[str, str], length: int) -> tuple[int, int, int]:
    variable = 0
    informative = 0
    all_gap = 0
    seqs = list(records.values())
    for i in range(length):
        column = [s[i] for s in seqs]
        if all(c in MISSING for c in column):
            all_gap += 1
        counts = {base: column.count(base) for base in RESOLVED}
        observed = [n for n in counts.values() if n > 0]
        if len(observed) >= 2:
            variable += 1
        if sum(n >= 2 for n in observed) >= 2:
            informative += 1
    return variable, informative, all_gap


def inspect_locus(locus: str, path: Path, focal: set[str]) -> dict[str, object]:
    row: dict[str, object] = {
        "locus": locus,
        "passed": False,
        "reason": "",
        "aligned_length": 0,
        "sequence_records": 0,
        "focal_sequences": 0,
        "focal_fraction": 0.0,
        "gap_fraction": 1.0,
        "all_gap_columns": 0,
        "min_non_gap_bases": 0,
        "max_non_gap_bases": 0,
        "variable_sites_acgt": 0,
        "parsimony_informative_sites_acgt": 0,
        "invalid_characters": "",
    }
    if not path.is_file():
        row["reason"] = "alignment_missing"
        return row
    try:
        records = read_aligned_fasta(path)
    except ValueError as exc:
        row["reason"] = f"invalid_fasta:{exc}"
        return row

    row["sequence_records"] = len(records)
    unknown = sorted(set(records) - focal - set(REQUIRED_REFERENCES))
    if unknown:
        row["reason"] = "unexpected_taxa:" + ";".join(unknown)
        return row
    missing_refs = [x for x in REQUIRED_REFERENCES if x not in records]
    if missing_refs:
        row["reason"] = "missing_reference:" + ";".join(missing_refs)
        return row

    lengths = {len(s) for s in records.values()}
    if len(lengths) != 1:
        row["reason"] = "ragged_alignment"
        return row
    length = next(iter(lengths))
    row["aligned_length"] = length
    if length <= 0:
        row["reason"] = "zero_length_alignment"
        return row

    focal_n = sum(t in records for t in focal)
    row["focal_sequences"] = focal_n
    row["focal_fraction"] = focal_n / 20
    if focal_n < 16:
        row["reason"] = "focal_occupancy_below_0.80"
        return row

    invalid = sorted({c for s in records.values() for c in s if c not in DNA_ALLOWED})
    row["invalid_characters"] = "".join(invalid)
    if invalid:
        row["reason"] = "invalid_dna_characters"
        return row

    non_gap = [sum(c not in MISSING for c in s) for s in records.values()]
    row["min_non_gap_bases"] = min(non_gap)
    row["max_non_gap_bases"] = max(non_gap)
    if min(non_gap) <= 0:
        row["reason"] = "empty_present_sequence"
        return row

    total_chars = length * len(records)
    gaps = sum(s.count("-") for s in records.values())
    row["gap_fraction"] = gaps / total_chars
    variable, informative, all_gap = site_stats(records, length)
    row["variable_sites_acgt"] = variable
    row["parsimony_informative_sites_acgt"] = informative
    row["all_gap_columns"] = all_gap
    if all_gap:
        row["reason"] = "all_gap_alignment_columns"
        return row

    row["passed"] = True
    row["reason"] = "structural_qc_pass"
    return row


def summarize(eligible_loci: Path, alignment_dir: Path, primary_runs: Path, output_csv: Path, output_json: Path) -> dict[str, object]:
    loci = read_loci(eligible_loci)
    focal = set(read_primary(primary_runs))
    rows = [inspect_locus(locus, alignment_dir / f"{locus}.aln.fasta", focal) for locus in loci]

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0])
    with output_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)

    passed = [r for r in rows if r["passed"]]
    failed = [r for r in rows if not r["passed"]]
    lengths = [int(r["aligned_length"]) for r in passed]
    gaps = [float(r["gap_fraction"]) for r in passed]
    summary: dict[str, object] = {
        "contract_version": "colour_rate_comp1061_alignment_qc_v2_saff_only_root",
        "expected_loci": len(loci),
        "passed_loci": len(passed),
        "failed_loci": len(failed),
        "failed_reasons": {reason: sum(r["reason"] == reason for r in failed) for reason in sorted({str(r["reason"]) for r in failed})},
        "focal_taxa": 20,
        "minimum_focal_sequences": 16,
        "root_outgroup": ROOT_OUTGROUP,
        "required_reference_tips": list(REQUIRED_REFERENCES),
        "tree_tip_count_if_complete": 21,
        "alignment_length_min": min(lengths) if lengths else None,
        "alignment_length_median": statistics.median(lengths) if lengths else None,
        "alignment_length_max": max(lengths) if lengths else None,
        "gap_fraction_median": statistics.median(gaps) if gaps else None,
        "total_variable_sites_acgt": sum(int(r["variable_sites_acgt"]) for r in passed),
        "total_parsimony_informative_sites_acgt": sum(int(r["parsimony_informative_sites_acgt"]) for r in passed),
        "all_gap_columns_total": sum(int(r["all_gap_columns"]) for r in rows),
        "posthoc_signal_filtering_applied": False,
        "alignment_qc_passed": len(passed) == len(loci),
        "claim_limit": "This gate validates alignment structure, focal/reference membership, occupancy, alphabet, non-empty sequences and absence of all-gap columns. Gap fraction and phylogenetic-site counts are descriptive only and do not remove loci post hoc."
    }
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    if failed:
        raise ValueError(f"Structural alignment QC failed for {len(failed)}/{len(loci)} loci; see {output_csv}")
    return summary


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--eligible-loci", type=Path, required=True)
    p.add_argument("--alignment-dir", type=Path, required=True)
    p.add_argument("--primary-runs", type=Path, required=True)
    p.add_argument("--output-csv", type=Path, required=True)
    p.add_argument("--output-json", type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(summarize(a.eligible_loci, a.alignment_dir, a.primary_runs, a.output_csv, a.output_json), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
