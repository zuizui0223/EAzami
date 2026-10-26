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
FDT1_SEED = ROOT / "data/evidence/functional_effect_existing_seed_registry_v1.csv"
PHYLLARY_CONTRACT = ROOT / "data/evidence/phyllary_posture_harmonization_contract_v1.json"
EVENT_WINDOWS = ROOT / "data/evidence/cirsium_ecological_event_windows_v1.csv"
PUBLIC_NUCLEAR_README = ROOT / "workflow/public_nuclear_maximum/README.md"
CURRENT_STATE = ROOT / "docs/CURRENT_STATE_2026-08-14.md"
JAPAN_WIDE_MACHINE_TREE = ROOT / "data/evidence/japan_origin_global_primary_tree_v1.nwk"

KNOWN_ASSETS = {
    "antagonist_meta": ROOT / "data/evidence/cirsium_floral_herbivory_lnrr_meta_v2.json",
    "generic_meta_gate": ROOT / "data/evidence/doctoral_meta_resolution_gate_v1.json",
    "multiagent_registry": ROOT / "data/evidence/multiagent_floral_selection_mosaic_registry_v1.csv",
    "pollinator_gradient_registry": ROOT / "data/evidence/experimental_pollinator_selection_gradients_v1.csv",
    "pollinator_assurance_registry": ROOT / "data/evidence/cirsium_pollinator_assurance_meta_v1.csv",
    "demographic_transmission_registry": ROOT / "data/evidence/cirsium_demographic_transmission_meta_v1.csv",
    "orientation_mechanism_targets": ROOT / "data/evidence/orientation_mechanism_reduction_targets_v1.csv",
    "interaction_pattern_ledger": ROOT / "data/evidence/interaction_quantitative_pattern_ledger_v1.csv",
    "fdt1_existing_seed_registry": FDT1_SEED,
    "phyllary_harmonization_contract": PHYLLARY_CONTRACT,
    "event_window_registry": EVENT_WINDOWS,
    "focal_niche_builder": ROOT / "analysis/build_focal_occurrence_niche_sample_information_v1.py",
    "focal_niche_config": ROOT / "data/evidence/focal_occurrence_niche_sampling_config_v1.json",
    "focal_niche_report": ROOT / "docs/FULL_OCCURRENCE_NICHE_SAMPLE_INFORMATION_2026-08-21.md",
    "focal_branch_length_tree": ROOT / "data/evidence/full20_comp1061_primary_tree_v1.nwk",
    "orientation_posttree": ROOT / "data/evidence/orientation_comp1061_posttree_ensemble_preflight_v1.json",
    "japan294_execution_bundle": ROOT / "analysis/build_japan_origin_global_hpc_bundle_v2.py",
    "japan294_execution_readme": PUBLIC_NUCLEAR_README,
    "japan_origin_synthesis": ROOT / "docs/JAPAN_CIRSIUM_ORIGIN_META_ANALYSIS_2026-08-14.md",
    "field_manifest": ROOT / "sampling/doctoral_field_tranche1_population_manifest_v1.csv",
}

MISSING_PROGRAM_ASSETS = {
    "cross_module_trait_function_matrix": ROOT / "data/evidence/trait_function_effect_matrix_v1.csv",
    "georeferenced_cross_module_effect_ledger": ROOT / "data/evidence/functional_effect_geography_v1.csv",
    "japan_wide_machine_readable_tree": JAPAN_WIDE_MACHINE_TREE,
    "exact_tip_dated_tree": ROOT / "data/evidence/cirsium_functional_dated_tree_v1.nwk",
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
            "decision": "state_data_ready_but_japan_wide_tree_execution_gate_blocks_transition_count",
            "claim_boundary": "generic reproductive-defence function is weakened; historical recurrence would not rescue an adaptive claim",
        },
        "phyllary_posture": {
            "resolved": n_phyllary,
            "coverage_percent_of_japan38": pct(n_phyllary, n_japan),
            "coverage_percent_within_nmns_seed": pct(n_phyllary, n_seed),
            "raw_state_counts": dict(sorted(phyllary_counts.items())),
            "raw_state_classes": len(phyllary_counts),
            "decision": "harmonization_frozen_but_current_binary_compatible_coverage_is_exploratory_only",
            "claim_boundary": "do not collapse posture categories post hoc to maximize transition signal",
        },
    }


def summarize_phyllary_harmonization(traits: list[dict[str, str]]) -> dict:
    contract = json.loads(PHYLLARY_CONTRACT.read_text(encoding="utf-8"))
    mapping = contract["coarse_mapping"]
    counts: Counter[str] = Counter()
    for row in traits:
        raw = row["phyllary_posture"]
        if raw == "unknown":
            continue
        if raw not in mapping:
            raise ValueError(f"unmapped phyllary state: {raw}")
        counts[mapping[raw]] += 1
    expected = contract["coarse_state_counts_expected"]
    if dict(counts) != expected:
        raise ValueError(f"phyllary coarse counts drifted: {dict(counts)} != {expected}")
    return {
        "contract": PHYLLARY_CONTRACT.relative_to(ROOT).as_posix(),
        "coarse_state_counts": dict(counts),
        "binary_compatible_resolved": counts["closed_to_ascending"] + counts["spreading_to_recurved"],
        "minor_state_count": min(counts["closed_to_ascending"], counts["spreading_to_recurved"]),
        "decision": contract["current_decision"],
        "reason": contract["reason"],
    }


def japan_wide_tree_gate() -> dict:
    public_readme = PUBLIC_NUCLEAR_README.read_text(encoding="utf-8")
    current_state = CURRENT_STATE.read_text(encoding="utf-8")
    accepted_sample_composition = "**294 biological tips**" in public_readme
    heavy_execution_remaining = "actual heavy execution" in current_state and "obtain accepted baseline BWA and BLASTx trees" in current_state
    tree_present = JAPAN_WIDE_MACHINE_TREE.exists()
    return {
        "accepted_294_sample_composition": accepted_sample_composition,
        "execution_bundle_present": KNOWN_ASSETS["japan294_execution_bundle"].exists(),
        "machine_readable_japan_wide_tree_present": tree_present,
        "heavy_tree_execution_remaining_in_current_state": heavy_execution_remaining,
        "decision": "tree_ready_for_japan38_trait_history" if tree_present else "sample_composition_and_execution_graph_ready_but_machine_tree_missing; do_not_infer_Japan38_transition_counts",
        "claim_boundary": "The accepted 294 biological-tip composition and validated execution graph are not themselves a machine-readable accepted topology. Published Moreyra final/dated trees were also not publicly recovered.",
    }


def summarize_fdt1_seed() -> dict:
    rows = read_csv(FDT1_SEED)
    ids = [r["source_id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate source_id in FDT1 existing seed registry")
    missing_paths = [r["path"] for r in rows if not (ROOT / r["path"]).exists()]
    if missing_paths:
        raise ValueError(f"FDT1 seed registry points to missing assets: {missing_paths}")
    return {
        "registered_existing_evidence_families": len(rows),
        "source_ids": ids,
        "all_paths_present": True,
        "decision": "reuse_existing_ledgers_first_before_new_systematic_search",
        "next_gate": "normalize only homologous estimands into trait->function effect rows; preserve nonpoolable evidence as structured priors",
    }


def summarize_event_windows() -> dict:
    rows = read_csv(EVENT_WINDOWS)
    eligible = [r for r in rows if r["eligible_transition_clustering"] == "yes"]
    anchors = [r for r in rows if r["event_class"] == "lineage_split_anchor"]
    for row in eligible:
        if not row["young_bound_ma"] or not row["old_bound_ma"]:
            raise ValueError(f"eligible event lacks uncertainty interval: {row['event_id']}")
    return {
        "event_rows": len(rows),
        "eligible_biogeographic_opportunity_windows": len(eligible),
        "eligible_event_ids": [r["event_id"] for r in eligible],
        "lineage_split_anchors": len(anchors),
        "decision": "event_windows_frozen_but_transition_clustering_waits_for_dated_trait_tree",
        "claim_boundary": "Only source-backed biogeographic intervals are eligible. Point-estimate lineage splits remain chronology anchors, not ecological-event windows.",
    }


def layer_readiness(tree_gate: dict) -> list[dict[str, str]]:
    return [
        {"analysis_id": "FDT1", "status": "seed_registry_ready_effect_harmonization_next", "usable_now": "seven existing evidence families registered, including exact gradients, direct lnRR, structured gates and module-specific targets", "next_gate": "derive harmonized trait->function rows only where estimands are commensurable; do not force heterogeneous metrics into one pool"},
        {"analysis_id": "FDT2", "status": "not_yet_executable_as_cross_module_meta_regression", "usable_now": "focal Cirsium occurrence+CHELSA niche pipeline is ready as a separate environmental layer", "next_gate": "georeference homologous FDT1 effect rows; current niche audit is not a substitute for study-level effect geography"},
        {"analysis_id": "FDT3", "status": "partial_ready_tree_gated", "usable_now": "orientation repeated-state result; balanced Japan38 stickiness states; frozen exploratory phyllary harmonization", "next_gate": "run Japan38 stickiness transition preflight" if tree_gate["machine_readable_japan_wide_tree_present"] else "execute/freeze the Japan-wide machine-readable nuclear tree before stickiness transition counts; meanwhile continue FDT1"},
        {"analysis_id": "FDT4", "status": "partial_ready", "usable_now": "focal occurrence niche pipeline; published temporal anchors; empirical focal branch-length tree; trait seeds", "next_gate": "obtain/freeze an exact-tip dated tree and expand voucher-linked trait coverage before branch-wise trait-niche timing"},
        {"analysis_id": "FDT5", "status": "blocked", "usable_now": "branch-length phylogeny and provisional module definitions only", "next_gate": "requires both meta-derived functional loadings and a dated/ultrametric trait-compatible tree"},
        {"analysis_id": "FDT6", "status": "event_windows_frozen_dated_transition_tree_missing", "usable_now": "three source-interval biogeographic opportunity windows plus four lineage-split chronology anchors", "next_gate": "join dated trait transitions with uncertainty to the frozen windows; do not use point estimates as event matches"},
        {"analysis_id": "FDT7", "status": "design_ready_not_parameterized", "usable_now": "M0-M5 model definitions and some empirical summary targets", "next_gate": "parameterize after FDT1/FDT4; no simulation engine should invent missing functional priors"},
        {"analysis_id": "FDT8", "status": "partial_ready", "usable_now": "core190, Japan-wide breadth panel and focal niche sampling-information analysis", "next_gate": "rank experiments only after transition confidence + functional effect strength + ecological contrast are joined"},
    ]


def build_summary() -> dict:
    traits = read_csv(TRAITS)
    japan38 = read_csv(JAPAN38)
    registry = read_csv(FDT_REGISTRY)
    registry_ids = [r["analysis_id"] for r in registry]
    if registry_ids != [f"FDT{i}" for i in range(1, 9)]:
        raise ValueError("functional-diversity registry must contain ordered FDT1-FDT8")

    tree_gate = japan_wide_tree_gate()
    return {
        "contract_version": "functional_time_existing_material_preflight_v1",
        "source_commit_expectation": "run against current repository checkout; no external data required",
        "known_assets": {name: path.relative_to(ROOT).as_posix() for name, path in KNOWN_ASSETS.items() if path.exists()},
        "program_assets_not_yet_present": {name: path.relative_to(ROOT).as_posix() for name, path in MISSING_PROGRAM_ASSETS.items() if not path.exists()},
        "japan38_multitrait": summarize_traits(traits, japan38),
        "phyllary_harmonization": summarize_phyllary_harmonization(traits),
        "japan_wide_tree_gate": tree_gate,
        "fdt1_existing_seed": summarize_fdt1_seed(),
        "ecological_event_windows": summarize_event_windows(),
        "fdt_layer_readiness": layer_readiness(tree_gate),
        "next_execution_order": [
            "FDT1a ACTIVE: normalize the seven registered existing evidence families into homologous trait->function effect rows before new literature search",
            "FDT2a NEXT: add coordinates/environment only to homologous FDT1 rows; keep focal Cirsium niche pipeline separate",
            "FDT3a GATED: balanced stickiness states are ready, but Japan38 transition counts wait for a frozen machine-readable Japan-wide tree",
            "FDT3b DONE-PREFLIGHT: conservative phyllary harmonization yields 7 closed/ascending vs 2 spreading/recurved plus 1 unresolved, so remain exploratory until broader direct measurements",
            "FDT6a DONE-PREFLIGHT: three biogeographic opportunity windows are frozen with uncertainty; transition clustering waits for a dated trait tree",
            "FDT4a: secure a dated exact-tip Cirsium scaffold; do not run disparity-through-time on substitution branch lengths",
            "FDT5-FDT7: only after functional loadings + dated tree + branch-wise niche summaries exist"
        ],
        "claim_boundary": "This audit identifies reusable evidence and executable next analyses. It does not infer adaptation from authority states, current niches, event-window overlap, or file availability."
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
