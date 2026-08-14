#!/usr/bin/env python3
"""Canonical corrected 20-taxon Compositae1061 flower-colour bridge builder.

The first full official-SRA reconciliation corrected the pre-data publication
bookkeeping used by the original prototype.  The current project partition is
Chang2025=3, Chang2026=10 and Moreyra2025=7.  Taxon membership, colour states,
run matching and the maximum-Spots primary-sample rule are unchanged.

Shared parsing/reconciliation helpers live in
``colour_rate_comp1061_bridge_primitives.py``.  This file is the only supported
bridge entry point and freezes the corrected v0.2 scientific contract.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Mapping, Sequence

import colour_rate_comp1061_bridge_primitives as core

EXPECTED_TAXA = core.EXPECTED_TAXA
EXPECTED_STATES = core.EXPECTED_STATES
EXPECTED_DATA_TYPES = core.EXPECTED_DATA_TYPES
EXPECTED_STUDIES = {"Chang2025": 3, "Chang2026": 10, "Moreyra2025": 7}
EXPECTED_REFERENCE_SHA256 = core.EXPECTED_REFERENCE_SHA256
EXPECTED_REFERENCE_LOCI = core.EXPECTED_REFERENCE_LOCI
CHANG_RECON_TAXA = core.CHANG_RECON_TAXA
CHANG2025_DIRECT_TAXA = core.CHANG2025_DIRECT_TAXA
MOREYRA_TAXA = core.MOREYRA_TAXA
CHANG2025_SRA_ALIASES = core.CHANG2025_SRA_ALIASES
FIELDS = core.FIELDS

# Public helper surface retained for tests/downstream callers.
clean = core.clean
read_csv = core.read_csv
canonical_taxon = core.canonical_taxon
safe_tip_id = core.safe_tip_id
integer_field = core.integer_field
value_field = core.value_field
atlas_eligible = core.atlas_eligible
frozen_reference_contract = core.frozen_reference_contract
atlas_index = core.atlas_index
accession_audit_by_voucher = core.accession_audit_by_voucher
make_row = core.make_row
chang_reconciliation_candidates = core.chang_reconciliation_candidates
chang2025_direct_candidates = core.chang2025_direct_candidates
runinfo_by_run = core.runinfo_by_run
moreyra_candidates = core.moreyra_candidates
choose_primary = core.choose_primary
write_csv = core.write_csv


def validate_primary(primary: Sequence[Mapping[str, str]]) -> dict[str, object]:
    if len(primary) != EXPECTED_TAXA:
        raise ValueError(f"Primary bridge must contain {EXPECTED_TAXA} tips")
    if len({row["tip_id"] for row in primary}) != EXPECTED_TAXA:
        raise ValueError("Primary tip IDs are not unique")
    if len({row["run"] for row in primary}) != EXPECTED_TAXA:
        raise ValueError("Primary bridge runs are not unique")
    states = Counter(row["binary_colour_code"] for row in primary)
    if dict(sorted(states.items())) != EXPECTED_STATES:
        raise ValueError(f"Primary state counts drifted: {dict(states)}")
    data_types = Counter(row["data_type"] for row in primary)
    if dict(sorted(data_types.items())) != EXPECTED_DATA_TYPES:
        raise ValueError(f"Primary data-type counts drifted: {dict(data_types)}")
    studies = Counter(row["source_study"] for row in primary)
    if dict(sorted(studies.items())) != EXPECTED_STUDIES:
        raise ValueError(f"Primary source-study counts drifted: {dict(studies)}")
    if any(row["primary_tip"] != "yes" for row in primary):
        raise ValueError("Primary manifest contains non-primary row")
    if any(row["accepted_taxon"].casefold().endswith("takaoense") for row in primary):
        raise ValueError("Polymorphic var. takaoense leaked into fixed-state primary bridge")
    return {
        "taxon_count": len(primary),
        "state_counts": dict(sorted(states.items())),
        "data_type_counts": dict(sorted(data_types.items())),
        "study_counts": dict(sorted(studies.items())),
        "paired_runs": sum(row["library_layout"] == "PAIRED" for row in primary),
        "single_runs": sum(row["library_layout"] == "SINGLE" for row in primary),
        "total_spots": sum(int(row["spots"] or 0) for row in primary),
        "total_bases": sum(int(row["bases"] or 0) for row in primary),
    }


def build(
    *,
    atlas_path: Path,
    reference_contract_path: Path,
    chang_reconciliation_path: Path,
    chang_accession_audit_path: Path,
    chang2025_runinfo_path: Path,
    moreyra_audit_path: Path,
    moreyra_runinfo_path: Path,
) -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, object]]:
    atlas_rows = atlas_eligible(atlas_path)
    reference = frozen_reference_contract(reference_contract_path)
    candidates = (
        chang_reconciliation_candidates(
            atlas_rows, chang_reconciliation_path, chang_accession_audit_path
        )
        + chang2025_direct_candidates(atlas_rows, chang2025_runinfo_path)
        + moreyra_candidates(atlas_rows, moreyra_audit_path, moreyra_runinfo_path)
    )
    primary, replicates = choose_primary(candidates)
    observed = validate_primary(primary)
    summary: dict[str, object] = {
        "contract_version": "colour_rate_comp1061_bridge_panel_v0_2",
        "reference_contract": str(reference_contract_path),
        "comp1061_reference_sha256": reference["sha256"],
        "comp1061_locus_count": reference["locus_count"],
        "source_study_partition": dict(EXPECTED_STUDIES),
        "v0_1_correction": (
            "The first full official-SRA build showed ten eligible taxa represented "
            "by PRJNA1311153/Chang2026 and three additional taxa by "
            "PRJNA1158676/Chang2025. The old 7/6 Chang split was pre-data "
            "bookkeeping; taxon/run matching and the maximum-Spots rule are unchanged."
        ),
        "primary_sample_rule": (
            "maximum official Spots within each source-backed taxon; ties "
            "voucher/sample-code/run lexical; flower colour and topology excluded"
        ),
        "primary": observed,
        "replicate_candidate_rows": len(replicates),
        "taxa_with_multiple_candidate_runs": sorted(
            taxon
            for taxon, count in Counter(row["accepted_taxon"] for row in replicates).items()
            if count > 1
        ),
        "execution_ready_for_read_recovery": True,
        "branch_length_tree_completed": False,
        "rate_fit_execution_allowed": False,
        "required_tree_sensitivities": [
            "1061_all_public_reference_loci",
            "531_reproducible_warning_occupancy_candidates_when_mappable",
            "241_conservative_no_warning_high_occupancy_loci_when_mappable",
            "replicate_inclusive_or_per_taxon_alternative_sample_sensitivity",
            "target_capture_vs_leaf_rnaseq_occupancy_and_missingness_audit",
            "paralog_copy_conflict_audit",
        ],
        "claim_limit": (
            "The bridge panel only freezes taxon/run selection in a shared "
            "Compositae1061 coordinate system. It does not imply equivalent locus "
            "recovery between target-capture and leaf RNA-seq, does not create a "
            "branch-length tree, and does not permit empirical flower-colour "n            "transition-rate inference."
        ),
    }
    return primary, replicates, summary


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
    write_csv(args.outdir / "colour_rate_comp1061_primary_20tip_panel.csv", primary)
    write_csv(
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
