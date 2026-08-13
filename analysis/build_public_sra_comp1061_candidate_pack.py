#!/usr/bin/env python3
"""Build a strict frozen-241 Compositae1061 locus pack for one public SRA candidate.

This is a pre-admission screen for extending the 294-tip public nuclear tree.  A
candidate can pass this screen without being promoted into the maximum-public
tree: final promotion still requires overlap with the accepted 294-tip current
locus set and a paired baseline-vs-augmentation topology check.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Iterable


def clean(value: object) -> str:
    return str(value or "").strip()


def read_fasta(path: Path) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    name: str | None = None
    seq: list[str] = []
    with path.open(encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line:
                continue
            if line.startswith(">"):
                if name is not None:
                    rows.append((name, "".join(seq).upper()))
                name = line[1:].split()[0]
                seq = []
            else:
                seq.append(line)
    if name is not None:
        rows.append((name, "".join(seq).upper()))
    return rows


def write_fasta(path: Path, records: Iterable[tuple[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for name, seq in records:
            handle.write(f">{name}\n")
            for start in range(0, len(seq), 80):
                handle.write(seq[start:start + 80] + "\n")


def read_loci(path: Path) -> list[str]:
    loci = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(loci) != 241 or len(set(loci)) != 241:
        raise ValueError(f"expected exactly 241 unique frozen loci, found {len(loci)} / {len(set(loci))}")
    return loci


def read_candidate(path: Path, candidate_id: str) -> dict[str, str]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = [{key: clean(value) for key, value in row.items()} for row in csv.DictReader(handle)]
    hits = [row for row in rows if row.get("candidate_id") == candidate_id]
    if len(hits) != 1:
        raise ValueError(f"candidate {candidate_id!r} expected exactly once, found {len(hits)}")
    row = hits[0]
    if row.get("pilot_execute", "").casefold() != "true":
        raise ValueError(f"candidate {candidate_id} is not admitted to the bounded pilot")
    for field in ("tip_id", "scientific_name", "biosample", "run", "bioproject"):
        if not row.get(field):
            raise ValueError(f"candidate {candidate_id} missing {field}")
    return row


def read_paralog_counts(path: Path, tip_id: str) -> dict[str, int]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if not rows or "Species" not in rows[0]:
        raise ValueError("paralog report lacks Species column")
    hits = [row for row in rows if clean(row.get("Species")) == tip_id]
    if len(hits) != 1:
        raise ValueError(f"expected one paralog row for {tip_id}, found {len(hits)}")
    row = hits[0]
    out: dict[str, int] = {}
    for locus, value in row.items():
        if locus == "Species":
            continue
        text = clean(value)
        if not text:
            out[locus] = 0
            continue
        try:
            out[locus] = int(float(text))
        except ValueError as exc:
            raise ValueError(f"invalid paralog count {tip_id}/{locus}={text!r}") from exc
    return out


def recovered_sequences(root: Path, tip_id: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for path in sorted(root.iterdir()):
        if not path.is_file():
            continue
        suffix = path.suffix.casefold()
        if suffix not in {".fna", ".fa", ".fas", ".fasta"}:
            continue
        locus = path.stem
        matches: list[str] = []
        for name, seq in read_fasta(path):
            if name == tip_id or name.startswith(tip_id + "-") or name.startswith(tip_id + "_") or name.startswith(tip_id + "|"):
                if seq:
                    matches.append(seq)
        if len(matches) > 1:
            raise ValueError(f"multiple recovered sequences for {tip_id} at locus {locus}")
        if matches:
            out[locus] = matches[0]
    return out


def build(
    candidate_manifest: Path,
    candidate_id: str,
    locus_list: Path,
    retrieved_dir: Path,
    paralog_report: Path,
    outdir: Path,
    minimum_strict_loci: int = 100,
) -> dict[str, object]:
    candidate = read_candidate(candidate_manifest, candidate_id)
    tip_id = candidate["tip_id"]
    loci = read_loci(locus_list)
    counts = read_paralog_counts(paralog_report, tip_id)
    sequences = recovered_sequences(retrieved_dir, tip_id)

    rows: list[dict[str, object]] = []
    strict_loci: list[str] = []
    locus_out = outdir / "loci"
    for locus in loci:
        seq = sequences.get(locus, "")
        copies = counts.get(locus, 0)
        warning = copies > 1
        eligible = bool(seq) and not warning
        reason = "eligible" if eligible else ("paralog_warning" if warning else "not_recovered")
        if eligible:
            strict_loci.append(locus)
            write_fasta(locus_out / f"{locus}.fasta", [(tip_id, seq)])
        rows.append(
            {
                "locus": locus,
                "recovered": bool(seq),
                "sequence_length_nt": len(seq),
                "hybpiper_copy_count": copies,
                "paralog_warning": warning,
                "strict_eligible": eligible,
                "reason": reason,
            }
        )

    outdir.mkdir(parents=True, exist_ok=True)
    with (outdir / "locus_audit.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (outdir / "strict_recovered_loci.txt").write_text(
        "".join(f"{locus}\n" for locus in strict_loci), encoding="utf-8"
    )

    recovered = sum(bool(row["recovered"]) for row in rows)
    warned = sum(bool(row["paralog_warning"]) for row in rows)
    summary: dict[str, object] = {
        "contract_version": "public_sra_comp1061_candidate_pack_v1",
        "candidate_id": candidate_id,
        "tip_id": tip_id,
        "scientific_name": candidate["scientific_name"],
        "biosample": candidate["biosample"],
        "run": candidate["run"],
        "bioproject": candidate["bioproject"],
        "library_strategy": candidate.get("library_strategy", ""),
        "frozen_candidate_loci": len(loci),
        "recovered_frozen_loci": recovered,
        "recovered_fraction": recovered / len(loci),
        "paralog_warning_loci": warned,
        "strict_no_warning_recovered_loci": len(strict_loci),
        "strict_fraction": len(strict_loci) / len(loci),
        "minimum_strict_loci_for_pilot_pack": minimum_strict_loci,
        "pilot_locus_pack_ready": len(strict_loci) >= minimum_strict_loci,
        "primary_294_panel_changed": False,
        "tree_tip_promotion_allowed": False,
        "promotion_requires": [
            "intersect this pack with the accepted 294-tip current strict locus set",
            "retain at least 100 paired loci or use a separately versioned missing-data contract",
            "rerun the paired baseline-versus-augmentation tree on the identical locus set",
            "verify placement is not driven by assay type or a single conflicting public sample",
        ],
        "new_china_sampling_freeze_allowed": False,
    }
    (outdir / "candidate_pack_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-manifest", type=Path, required=True)
    parser.add_argument("--candidate-id", required=True)
    parser.add_argument("--locus-list", type=Path, required=True)
    parser.add_argument("--retrieved-dir", type=Path, required=True)
    parser.add_argument("--paralog-report", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--minimum-strict-loci", type=int, default=100)
    args = parser.parse_args()
    build(
        args.candidate_manifest,
        args.candidate_id,
        args.locus_list,
        args.retrieved_dir,
        args.paralog_report,
        args.outdir,
        args.minimum_strict_loci,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
