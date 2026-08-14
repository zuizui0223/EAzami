#!/usr/bin/env python3
"""Build a strict frozen-241 Compositae1061 pack for one matched 294-baseline SRA tip.

This is used by bounded empirical placement pilots.  It applies the same
recovered-sequence and HybPiper paralog-warning logic as the public candidate
pack builder but does not change the accepted 294-tip panel or authorize sample
promotion.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import build_public_sra_comp1061_candidate_pack as core


def build(
    *,
    tip_id: str,
    scientific_name: str,
    biosample: str,
    run: str,
    panel_id: str,
    locus_list: Path,
    retrieved_dir: Path,
    paralog_report: Path,
    outdir: Path,
    minimum_strict_loci: int = 100,
) -> dict[str, object]:
    if not tip_id or not scientific_name or not biosample or not run or not panel_id:
        raise ValueError("matched baseline metadata must be complete")
    loci = core.read_loci(locus_list)
    counts = core.read_paralog_counts(paralog_report, tip_id)
    sequences = core.recovered_sequences(retrieved_dir, tip_id)

    rows: list[dict[str, object]] = []
    strict: list[str] = []
    for locus in loci:
        seq = sequences.get(locus, "")
        copies = counts.get(locus, 0)
        warning = copies > 1
        eligible = bool(seq) and not warning
        if eligible:
            strict.append(locus)
            core.write_fasta(outdir / "loci" / f"{locus}.fasta", [(tip_id, seq)])
        rows.append({
            "locus": locus,
            "recovered": bool(seq),
            "sequence_length_nt": len(seq),
            "hybpiper_copy_count": copies,
            "paralog_warning": warning,
            "strict_eligible": eligible,
            "reason": "eligible" if eligible else ("paralog_warning" if warning else "not_recovered"),
        })

    outdir.mkdir(parents=True, exist_ok=True)
    with (outdir / "locus_audit.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    (outdir / "strict_recovered_loci.txt").write_text(
        "".join(f"{locus}\n" for locus in strict), encoding="utf-8"
    )
    recovered = sum(bool(row["recovered"]) for row in rows)
    warned = sum(bool(row["paralog_warning"]) for row in rows)
    summary: dict[str, object] = {
        "contract_version": "matched_294_baseline_comp1061_pack_v1",
        "tip_id": tip_id,
        "scientific_name": scientific_name,
        "panel_id": panel_id,
        "biosample": biosample,
        "run": run,
        "frozen_candidate_loci": len(loci),
        "recovered_frozen_loci": recovered,
        "paralog_warning_loci": warned,
        "strict_no_warning_recovered_loci": len(strict),
        "strict_fraction": len(strict) / len(loci),
        "minimum_strict_loci_for_empirical_pilot": minimum_strict_loci,
        "empirical_pilot_pack_ready": len(strict) >= minimum_strict_loci,
        "accepted_294_panel_changed": False,
        "tree_tip_promotion_allowed": False,
        "claim_boundary": "Matched-baseline sequence recovery supports a bounded placement sanity check only; it is not a full 294-tip promotion gate.",
    }
    (outdir / "matched_baseline_pack_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--tip-id", required=True)
    p.add_argument("--scientific-name", required=True)
    p.add_argument("--biosample", required=True)
    p.add_argument("--run", required=True)
    p.add_argument("--panel-id", required=True)
    p.add_argument("--locus-list", type=Path, required=True)
    p.add_argument("--retrieved-dir", type=Path, required=True)
    p.add_argument("--paralog-report", type=Path, required=True)
    p.add_argument("--outdir", type=Path, required=True)
    p.add_argument("--minimum-strict-loci", type=int, default=100)
    a = p.parse_args()
    build(
        tip_id=a.tip_id,
        scientific_name=a.scientific_name,
        biosample=a.biosample,
        run=a.run,
        panel_id=a.panel_id,
        locus_list=a.locus_list,
        retrieved_dir=a.retrieved_dir,
        paralog_report=a.paralog_report,
        outdir=a.outdir,
        minimum_strict_loci=a.minimum_strict_loci,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
