#!/usr/bin/env python3
"""Summarize the frozen Ulleung C. nipponicum genome augmentation gate."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

MODES = ("bwa", "blastx")


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate_mode(root: Path, mode: str) -> dict[str, object]:
    paired = load(root / mode / "paired_inputs" / "paired_augmentation_summary.json")
    concat = load(root / mode / "evaluation" / "cnipg_295_CNIPG_concat.json")
    astral = load(root / mode / "evaluation" / "cnipg_295_astral_backbone.json")
    loci = int(paired["paired_overlap_loci"])
    checks = {
        "minimum_paired_loci": loci >= int(paired["minimum_overlap_loci"]),
        "shared_294_concat_rf_zero": bool(concat["exact_shared_tip_backbone_invariance"]),
        "same_taxon_nearest": bool(concat["same_taxon_among_nearest_baseline_tips"]),
        "shared_species_astral_rf_zero": bool(astral["exact_shared_species_backbone_invariance"]),
    }
    return {
        "mapping_mode": mode,
        "paired_loci": loci,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "concat_shared_294_rf": int(concat["unrooted_rf_distance_on_shared_baseline_tips"]),
        "astral_shared_species_rf": int(astral["unrooted_rf_distance_on_shared_species"]),
        "nearest_baseline_tip_ids": concat["candidate_nearest_baseline_tip_ids"],
        "baseline_exact_taxon_tip_ids": concat["baseline_exact_taxon_tip_ids"],
    }


def summarize(root: Path, output: Path) -> dict[str, object]:
    by_mode = {mode: evaluate_mode(root, mode) for mode in MODES}
    promote = all(bool(by_mode[mode]["all_checks_pass"]) for mode in MODES)
    out: dict[str, object] = {
        "contract_version": "cirsium_nipponicum_public_genome_cross_data_type_summary_v1",
        "candidate_id": "CNIPG",
        "candidate_tip": "AUG_ULLEUNG_CNIP2024",
        "candidate_taxon": "Cirsium nipponicum",
        "baseline_focal_tips": 294,
        "baseline_mapping_modes": list(MODES),
        "mapping_results": by_mode,
        "automatic_sample_tip_promotion_allowed": promote,
        "manual_review_required": not promote,
        "resulting_sample_level_tip_count_if_promoted_alone": 295 if promote else 294,
        "new_analysis_taxon_labels_added_if_promoted": 0,
        "combined_current_public_candidate_tip_ceiling_if_all_independent_gates_pass": 297,
        "combined_ceiling_is_an_accepted_tree": False,
        "new_china_sampling_freeze_allowed": False,
        "claim_boundary": (
            "Passing this summary admits the natural Ulleung genome-derived sample as a same-taxon public replicate. "
            "It does not by itself admit EA01/EA02, create an accepted combined 297-tip tree, or change any flower-colour history claim."
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    summarize(args.root, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
