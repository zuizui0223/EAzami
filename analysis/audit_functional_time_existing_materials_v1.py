from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRAITS = ROOT / "data/evidence/japan38_nmns_capitulum_trait_seed_v1.csv"
JAPAN38 = ROOT / "data/evidence/moreyra2025_japan_38_membership_audit_2026-08-10.csv"
FDT_REGISTRY = ROOT / "data/evidence/functional_diversity_time_meta_registry_v1.csv"

KNOWN_ASSETS = {
    "antagonist_meta": ROOT / "data/evidence/cirsium_floral_herbivory_lnrr_meta_v2.json",
    "generic_meta_gate": ROOT / "data/evidence/doctoral_meta_resolution_gate_v1.json",
    "focal_niche_builder": ROOT / "analysis/build_focal_occurrence_niche_sample_information_v1.py",
    "focal_niche_config": ROOT / "data/evidence/focal_occurrence_niche_sampling_config_v1.json",
    "focal_niche_report": ROOT / "docs/FULL_OCCURRENCE_NICHE_SAMPLE_INFORMATION_2026-08-21.md",
    "focal_branch_length_tree": ROOT / "data/evidence/full20_comp1061_primary_tree_v1.nwk",
    "orientation_posttree": ROOT / "data/evidence/orientation_comp1061_posttree_ensemble_preflight_v1.json",
    "japan_origin_synthesis": ROOT / "docs/JAPAN_CIRSIUM_ORIGIN_META_ANALYSIS_2026-08-14.md",
    "field_manifest": ROOT / "sampling/doctoral_field_tranche1_population_manifest_v1.csv",
}

MISSING_PROGRAM_ASSETS = {
    "cross_module_trait_function_matrix": ROOT / "data/evidence/trait_function_effect_matrix_v1.csv",
    "georeferenced_cross_module_effect_ledger": ROOT / "data/evidence/functional_effect_geography_v1.csv",
    "exact_tip_dated_tree": ROOT / "data/evidence/cirsium_functional_dated_tree_v1.nwk",
    "event_window_registry": ROOT / "data/evidence/cirsium_ecological_event_windows_v1.csv",
    "simulation_engine": ROOT / "analysis/simulate_functional_evolution_v1.py",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def pct(n: int, d: int) -> float:
    return round(100.0 * n / d, 3) if d else 0.0


def summarize_traits(traits: list[dict[str, str]], japan38: list[dict[str, str]]) -> dict:
    japan_ids = {r["paper_japan_member_id"] for r in japan38}
    trait_ids = [r["paper_japan_member_id"] for r in traits]
    if len(trait_ids) != len(set(trait_ids)):
        raise ValueError("duplicate paper_japan_member_id in NMNS trait seed")
    if not set(trait_ids) <= japan_ids:
        raise ValueError("NMNS trait seed contains taxa outside the audited Japan38 panel")

    authority_exact = sum(r["authority_match_status"] == "exact_authority_concept_match" for r in traits)

    orientation_counts: Counter[str] = Counter()
    orientation_unknown = 0
    orientation_conflict = 0
    for row in traits:
        state = row["orientation_state"]
        if state in {"upward_or_erect", "upward_or_ascending"}:
            orientation_counts["upward_or_erect"] += 1
        elif state == "downward_or_nodding":
            orientation_counts["downward_or_nodding"] += 1
        elif state == "unknown":
            orientation_unknown += 1
        else:
            orientation_conflict += 1

    sticky_counts = Counter(
        r["stickiness_state"]
        for r in traits
        if r["stickiness_state"] in {"sticky", "nonsticky_or_nearly_nonsticky"}
    )
    phyllary_counts = Counter(r["phyllary_posture"] for r in traits if r["phyllary_posture"] != "unknown")

    n_japan = len(japan38)
    n_seed = len(traits)
    n_orientation = sum(orientation_counts.values())
    n_sticky = sum(sticky_counts.values())
    n_phyllary = sum(phyllary_counts.values())

    stickiness_balance = 0.0
    if len(sticky_counts) == 2 and max(sticky_counts.values()) > 0:
        stickiness_balance = round(min(sticky_counts.values()) / max(sticky_counts.values()), 3)

    return {
        "japan38_taxon_concepts": n_japan,
        "nmns_exact_trait_rows": n_seed,
        "nmns_trait_coverage_percent_of_japan38": pct(n_seed, n_japan),
        "authority_exact_rows": authority_exact,
        "orientation": {
            "primary_resolved": n_orientation,
            "coverage_percent_of_japan38": pct(n_orientation, n_japan),
            "coverage_percent_within_nmns_seed": pct(n_orientation, n_seed),
            "state_counts": dict(sorted(orientation_counts.items())),
            "unknown": orientation_unknown,
            "source_conflict_or_nonbinary": orientation_conflict,
            "decision": "ready_existing_history; already has an independent topology-robust focal analysis",
        },
        "stickiness": {
            "resolved": n_sticky,
            "coverage_percent_of_japan38": pct(n_sticky, n_japan),
            "coverage_percent_within_nmns_seed": pct(n_sticky, n_seed),
            "state_counts": dict(sorted(sticky_counts.items())),
            "minor_to_major_state_balance": stickiness_balance,
            "decision": "ready_for_discrete_repeated-state preflight as a functional negative-control module",
            "claim_boundary": "generic reproductive-defence function is weakened; historical recurrence does not rescue an adaptive claim",
        },
        "phyllary_posture": {
            "resolved": n_phyllary,
            "coverage_percent_of_japan38": pct(n_phyllary, n_japan),
            "coverage_percent_within_nmns_seed": pct(n_phyllary, n_seed),
            "raw_state_counts": dict(sorted(phyllary_counts.items())),
            "raw_state_classes": len(phyllary_counts),
            "decision": "partial_ready; freeze a botanical state-harmonization rule before transition mapping",
            "claim_boundary": "do not collapse posture categories post hoc to maximize transition signal",
        },
    }


def layer_readiness() -> list[dict[str, str]]:
    have = {name: path.exists() for name, path in KNOWN_ASSETS.items()}
    missing = {name: path.exists() for name, path in MISSING_PROGRAM_ASSETS.items()}
    return [
        {
            "analysis_id": "FDT1",
            "status": "partial_ready",
            "usable_now": "antagonist seed-output meta; generic mechanism gate; module-specific literature extracts",
            "next_gate": "build harmonized cross-module trait->function effect ledger/matrix",
        },
        {
            "analysis_id": "FDT2",
            "status": "not_yet_executable_as_cross_module_meta_regression",
            "usable_now": "focal Cirsium occurrence+CHELSA niche pipeline is ready as a separate environmental layer",
            "next_gate": "georeference FDT1 effect rows; current niche audit is not a substitute for study-level effect geography",
        },
        {
            "analysis_id": "FDT3",
            "status": "partial_ready",
            "usable_now": "orientation repeated-state result; Japan38 NMNS stickiness/phyllary seed",
            "next_gate": "run stickiness historical preflight; harmonize phyllary states; build cross-plant event ledger",
        },
        {
            "analysis_id": "FDT4",
            "status": "partial_ready",
            "usable_now": "focal occurrence niche pipeline; published temporal anchors; empirical branch-length tree; trait seeds",
            "next_gate": "obtain/freeze an exact-tip dated tree and expand voucher-linked trait coverage before branch-wise trait-niche timing",
        },
        {
            "analysis_id": "FDT5",
            "status": "blocked",
            "usable_now": "branch-length phylogeny and provisional module definitions only",
            "next_gate": "requires both meta-derived functional loadings and a dated/ultrametric trait-compatible tree",
        },
        {
            "analysis_id": "FDT6",
            "status": "partial_ready",
            "usable_now": "published Japan colonization/secondary-entry age intervals and lineage-split anchors",
            "next_gate": "freeze event-window registry with uncertainty before testing transition clustering",
        },
        {
            "analysis_id": "FDT7",
            "status": "design_ready_not_parameterized",
            "usable_now": "M0-M5 model definitions and some empirical summary targets",
            "next_gate": "parameterize after FDT1/FDT4; no simulation engine should invent missing functional priors",
        },
        {
            "analysis_id": "FDT8",
            "status": "partial_ready",
            "usable_now": "core190, Japan-wide breadth panel and focal niche sampling-information analysis",
            "next_gate": "rank experiments only after transition confidence + functional effect strength + ecological contrast are joined",
        },
    ]


def build_summary() -> dict:
    traits = read_csv(TRAITS)
    japan38 = read_csv(JAPAN38)
    registry = read_csv(FDT_REGISTRY)
    registry_ids = [r["analysis_id"] for r in registry]
    if registry_ids != [f"FDT{i}" for i in range(1, 9)]:
        raise ValueError("functional-diversity registry must contain ordered FDT1-FDT8")

    return {
        "contract_version": "functional_time_existing_material_preflight_v1",
        "source_commit_expectation": "run against current repository checkout; no external data required",
        "known_assets": {name: path.relative_to(ROOT).as_posix() for name, path in KNOWN_ASSETS.items() if path.exists()},
        "program_assets_not_yet_present": {
            name: path.relative_to(ROOT).as_posix() for name, path in MISSING_PROGRAM_ASSETS.items() if not path.exists()
        },
        "japan38_multitrait": summarize_traits(traits, japan38),
        "fdt_layer_readiness": layer_readiness(),
        "next_execution_order": [
            "FDT3a: freeze and run Japan38 stickiness repeated-state/history preflight using existing authority states; treat as negative-control module",
            "FDT3b: predeclare phyllary-posture harmonization, then evaluate whether coverage supports history mapping",
            "FDT1a: convert already-extracted module literature into a study/effect ledger before any new broad search",
            "FDT2a: add coordinates/environment to homologous FDT1 effects; keep focal Cirsium niche pipeline separate",
            "FDT4a: secure a dated exact-tip Cirsium scaffold; do not run disparity-through-time on substitution branch lengths",
            "FDT5-FDT7: only after functional loadings + dated tree + branch-wise niche summaries exist",
        ],
        "claim_boundary": "This audit identifies reusable evidence and executable next analyses. It does not infer adaptation from authority states, current niches, or file availability.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    summary = build_summary()
    text = json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
