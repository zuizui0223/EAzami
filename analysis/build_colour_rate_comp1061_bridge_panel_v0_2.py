#!/usr/bin/env python3
"""Corrected v0.2 driver for the 20-taxon Compositae1061 bridge.

v0.1 predeclared an expected publication-label split of Chang2025=6 and
Chang2026=7 before the official SRA/BioProject join was executed.  The first
full network-backed build demonstrated that the actual sequencing-project
partition is PRJNA1311153/Chang2026=10 and PRJNA1158676/Chang2025=3, with the
Moreyra target-capture contribution remaining 7.  This v0.2 driver records that
empirical correction while leaving the taxon set, colour states, primary sample
selection rule and run matching unchanged.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import build_colour_rate_comp1061_bridge_panel as impl

CORRECTED_EXPECTED_STUDIES = {
    "Chang2025": 3,
    "Chang2026": 10,
    "Moreyra2025": 7,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--atlas", type=Path, required=True)
    parser.add_argument("--reference-contract", type=Path, required=True)
    parser.add_argument("--chang-reconciliation", type=Path, required=True)
    parser.add_argument("--chang-accession-audit", type=Path, required=True)
    parser.add_argument("--chang2025-runinfo", type=Path, required=True)
    parser.add_argument("--moreyra-audit", type=Path, required=True)
    parser.add_argument("--moreyra-runinfo", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    return parser.parse_args()


def build(**kwargs):
    previous = impl.EXPECTED_STUDIES
    impl.EXPECTED_STUDIES = dict(CORRECTED_EXPECTED_STUDIES)
    try:
        primary, replicates, summary = impl.build(**kwargs)
    finally:
        impl.EXPECTED_STUDIES = previous
    summary["contract_version"] = "colour_rate_comp1061_bridge_panel_v0_2"
    summary["source_study_partition"] = dict(CORRECTED_EXPECTED_STUDIES)
    summary["v0_1_correction"] = (
        "The first full official-SRA build showed that ten eligible taxa are "
        "represented by PRJNA1311153 and three additional taxa by PRJNA1158676. "
        "The v0.1 7/6 Chang study-label expectation was a pre-data bookkeeping "
        "assumption; taxon/run matching and the maximum-Spots sample rule are unchanged."
    )
    return primary, replicates, summary


def main() -> int:
    args = parse_args()
    primary, replicates, summary = build(
        atlas_path=args.atlas,
        reference_contract_path=args.reference_contract,
        chang_reconciliation_path=args.chang_reconciliation,
        chang_accession_audit_path=args.chang_accession_audit,
        chang2025_runinfo_path=args.chang2025_runinfo,
        moreyra_audit_path=args.moreyra_audit,
        moreyra_runinfo_path=args.moreyra_runinfo,
    )
    args.outdir.mkdir(parents=True, exist_ok=True)
    impl.write_csv(args.outdir / "colour_rate_comp1061_primary_20tip_panel.csv", primary)
    impl.write_csv(
        args.outdir / "colour_rate_comp1061_replicate_sensitivity_manifest.csv",
        replicates,
    )
    (args.outdir / "colour_rate_comp1061_bridge_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print("contract_version=colour_rate_comp1061_bridge_panel_v0_2")
    print(f"primary_taxa={summary['primary']['taxon_count']}")
    print("state_counts=" + json.dumps(summary["primary"]["state_counts"], sort_keys=True))
    print("data_type_counts=" + json.dumps(summary["primary"]["data_type_counts"], sort_keys=True))
    print("study_counts=" + json.dumps(summary["primary"]["study_counts"], sort_keys=True))
    print(f"replicate_candidate_rows={summary['replicate_candidate_rows']}")
    print(f"comp1061_reference_sha256={summary['comp1061_reference_sha256']}")
    print("branch_length_tree_completed=false")
    print("rate_fit_execution_allowed=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
