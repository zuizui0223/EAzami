#!/usr/bin/env python3
"""Aggregate the post-empirical EA01-only BWA/BLASTx promotion gate."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

MODES = ("bwa", "blastx")


def load(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise ValueError(f"missing EA01 evaluation artifact: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"invalid JSON object: {path}")
    return data


def require_bool(data: dict[str, object], key: str, path: Path) -> bool:
    value = data.get(key)
    if not isinstance(value, bool):
        raise ValueError(f"{path}: {key} is not boolean")
    return value


def summarize(
    *,
    bwa_paired_summary: Path,
    blastx_paired_summary: Path,
    bwa_evaluation: Path,
    blastx_evaluation: Path,
    output: Path,
) -> dict[str, object]:
    summaries = {
        "bwa": load(bwa_paired_summary),
        "blastx": load(blastx_paired_summary),
    }
    eval_dirs = {"bwa": bwa_evaluation, "blastx": blastx_evaluation}
    paired_by_mode: dict[str, int] = {}
    minimum_by_mode: dict[str, int] = {}
    checks: dict[str, bool] = {}
    rf: dict[str, int] = {}

    for mode in MODES:
        summary = summaries[mode]
        if summary.get("contract_version") != "ea01_public_paired_augmentation_inputs_v2":
            raise ValueError(f"{mode}: wrong paired-input summary contract")
        paired = int(summary.get("paired_loci", 0))
        minimum = int(summary.get("minimum_paired_loci", 100))
        if paired < minimum:
            raise ValueError(f"{mode} EA01 paired locus gate failed: {paired} < {minimum}")
        if summary.get("ea02_enters_biological_tree_inputs") is not False:
            raise ValueError(f"{mode}: EA02 unexpectedly entered biological tree inputs")
        paired_by_mode[mode] = paired
        minimum_by_mode[mode] = minimum

        concat_path = eval_dirs[mode] / "ea01_295_EA01_concat.json"
        concat = load(concat_path)
        if concat.get("candidate_id") != "EA01" or int(concat.get("shared_baseline_focal_tips", 0)) != 294:
            raise ValueError(f"{concat_path}: EA01/shared-tip drift")
        checks[f"{mode}_concat_exact_backbone"] = require_bool(concat, "exact_shared_tip_backbone_invariance", concat_path)
        checks[f"{mode}_same_taxon_nearest"] = require_bool(concat, "same_taxon_among_nearest_baseline_tips", concat_path)
        rf[f"{mode}_concat_rf"] = int(concat.get("unrooted_rf_distance_on_shared_baseline_tips", -1))

        astral_path = eval_dirs[mode] / "ea01_295_astral_backbone.json"
        astral = load(astral_path)
        if astral.get("scenario_id") != "ea01_295":
            raise ValueError(f"{astral_path}: scenario drift")
        checks[f"{mode}_astral_exact_backbone"] = require_bool(astral, "exact_shared_species_backbone_invariance", astral_path)
        rf[f"{mode}_astral_rf"] = int(astral.get("unrooted_rf_distance_on_shared_species", -1))

    passed = all(checks.values())
    result: dict[str, object] = {
        "contract_version": "ea01_public_augmentation_sensitivity_summary_v2",
        "candidate_id": "EA01",
        "mapping_modes": list(MODES),
        "paired_loci_by_mapping": paired_by_mode,
        "minimum_paired_loci_by_mapping": minimum_by_mode,
        "checks": checks,
        "rf_diagnostics": rf,
        "strict_automatic_sample_tip_promotion_gate_passed": passed,
        "sample_tip_promotion_allowed": passed,
        "manual_review_required": not passed,
        "resulting_sample_level_tip_count_if_promoted": 295 if passed else None,
        "new_analysis_taxon_label_added": False,
        "ea02_counts_as_independent_tip": False,
        "accepted_primary_before_gate": 294,
        "primary_294_tree_superseded_by_this_summary": passed,
        "new_china_sampling_freeze_allowed": False,
        "automatic_gate_policy": (
            "EA01 must retain >=100 paired loci independently in BWA and BLASTx; in both modes the shared-294 "
            "concatenated RF must be zero, the existing same-taxon baseline tip must be among nearest baseline "
            "neighbours, and the shared-species ASTRAL RF must be zero. Any failure requires manual review."
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bwa-paired-summary", type=Path, required=True)
    parser.add_argument("--blastx-paired-summary", type=Path, required=True)
    parser.add_argument("--bwa-evaluation", type=Path, required=True)
    parser.add_argument("--blastx-evaluation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    summarize(
        bwa_paired_summary=args.bwa_paired_summary,
        blastx_paired_summary=args.blastx_paired_summary,
        bwa_evaluation=args.bwa_evaluation,
        blastx_evaluation=args.blastx_evaluation,
        output=args.output,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
