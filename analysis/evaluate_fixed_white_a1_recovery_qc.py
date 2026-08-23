#!/usr/bin/env python3
"""Evaluate individual fixed-white A1 recovery against the frozen 153-locus gate.

Input rows are compact outputs from the existing HybPiper recovery lane. This
stage evaluates only per-individual homologous recovery. It does not establish
species-level placement concordance or permit rate fitting.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

EXPECTED_TAXA = ("Cirsium boninense", "Cirsium wulongense")
FROZEN_LOCI = 153
MIN_CLEAN = 123
REQUIRED = {
    "immutable_sample_id", "taxon", "frozen_loci", "recovered_frozen_loci",
    "paralog_warning_frozen_loci", "clean_recovered_frozen_loci", "non_gap_aligned_bp",
}


def clean(x: object) -> str:
    return str(x or "").strip()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("recovery QC table has no header")
        missing = REQUIRED - set(reader.fieldnames)
        if missing:
            raise ValueError(f"missing recovery QC columns: {sorted(missing)}")
        return [{k: clean(v) for k, v in r.items()} for r in reader if any(clean(v) for v in r.values())]


def evaluate_rows(rows: list[dict[str, str]]) -> dict[str, object]:
    seen: set[str] = set()
    by_taxon: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        sid = row["immutable_sample_id"]
        taxon = row["taxon"]
        if not sid:
            raise ValueError("recovery row lacks immutable_sample_id")
        if sid in seen:
            raise ValueError(f"duplicate recovery sample id: {sid}")
        seen.add(sid)
        if taxon not in EXPECTED_TAXA:
            raise ValueError(f"unexpected recovery taxon: {taxon}")
        frozen = int(row["frozen_loci"])
        recovered = int(row["recovered_frozen_loci"])
        paralog = int(row["paralog_warning_frozen_loci"])
        clean_n = int(row["clean_recovered_frozen_loci"])
        nongap = int(row["non_gap_aligned_bp"])
        if frozen != FROZEN_LOCI:
            raise ValueError(f"{sid}: frozen locus universe must remain {FROZEN_LOCI}")
        if min(recovered, paralog, clean_n, nongap) < 0:
            raise ValueError(f"{sid}: negative QC metric")
        if recovered > frozen or paralog > frozen or clean_n > frozen:
            raise ValueError(f"{sid}: locus count exceeds frozen universe")
        if clean_n > recovered:
            raise ValueError(f"{sid}: clean recovery cannot exceed recovered loci")
        # Clean means recovered and not paralog-warning for this individual; paralog
        # loci are masked for that individual instead of deleting the locus globally.
        if clean_n > recovered - min(paralog, recovered):
            raise ValueError(f"{sid}: clean/paralog counts are internally inconsistent")
        passed = clean_n >= MIN_CLEAN
        by_taxon[taxon].append({
            "immutable_sample_id": sid,
            "clean_recovered_frozen_loci": clean_n,
            "recovered_frozen_loci": recovered,
            "paralog_warning_frozen_loci": paralog,
            "non_gap_aligned_bp": nongap,
            "individual_recovery_passed": passed,
        })

    taxa_summary = {}
    for taxon in EXPECTED_TAXA:
        samples = sorted(by_taxon[taxon], key=lambda x: str(x["immutable_sample_id"]))
        passing = [x for x in samples if x["individual_recovery_passed"]]
        taxa_summary[taxon] = {
            "observed_samples": len(samples),
            "passing_samples": len(passing),
            "minimum_two_passing_individuals": len(passing) >= 2,
            "samples": samples,
        }

    both = all(taxa_summary[t]["minimum_two_passing_individuals"] for t in EXPECTED_TAXA)
    return {
        "contract_version": "fixed_white_a1_individual_recovery_qc_v0_1",
        "frozen_loci": FROZEN_LOCI,
        "minimum_clean_recovered_loci": MIN_CLEAN,
        "minimum_clean_recovered_fraction": MIN_CLEAN / FROZEN_LOCI,
        "taxa": taxa_summary,
        "individual_recovery_gate_passed_for_both_taxa": both,
        "replicate_placement_qc_allowed": both,
        "rate_fit_tip_promotion_allowed": False,
        "next_gate": "replicate-expanded placement concordance across retained topology sensitivities" if both else "obtain or improve at least two passing individuals per A1 taxon",
    }


def evaluate(path: Path) -> dict[str, object]:
    return evaluate_rows(read_rows(path))


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("qc", type=Path)
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    out = evaluate(a.qc)
    text = json.dumps(out, indent=2, ensure_ascii=False) + "\n"
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
