#!/usr/bin/env python3
"""Validate the preregistered scale-specific covariance v4 contract.

The validator resolves the v4 gap diagnosis against the immutable Azami handoff,
checks that the seven v3.1 fit estimands are reused without change, verifies the
nested structural-family design and complexity ordering, and audits all
adequacy/replication/context gates before any v4 family outcome is generated.

No simulator is run here.  The output is a machine-readable frozen contract audit.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any


EXPECTED_VERSION = "scale_specific_covariance_v4_2026-08-27"
EXPECTED_FAMILIES = [
    "shared_scale_baseline",
    "within_only_module_factor",
    "among_unit_mosaic_loadings",
    "combined_scale_decoupling",
    "combined_scale_decoupling_with_rotation",
]
EXPECTED_COMPLEXITY = {
    "shared_scale_baseline": 0,
    "within_only_module_factor": 1,
    "among_unit_mosaic_loadings": 1,
    "combined_scale_decoupling": 2,
    "combined_scale_decoupling_with_rotation": 3,
}
EXPECTED_PARENTS = {
    "shared_scale_baseline": None,
    "within_only_module_factor": "shared_scale_baseline",
    "among_unit_mosaic_loadings": "shared_scale_baseline",
    "combined_scale_decoupling": "shared_scale_baseline",
    "combined_scale_decoupling_with_rotation": "combined_scale_decoupling",
}
EXPECTED_FEATURES = {
    "shared_scale_baseline": (False, False, False),
    "within_only_module_factor": (True, False, False),
    "among_unit_mosaic_loadings": (False, True, False),
    "combined_scale_decoupling": (True, True, False),
    "combined_scale_decoupling_with_rotation": (True, True, True),
}
EXPECTED_MODULES = {
    "orientation": 1,
    "colour": 3,
    "shape": 4,
    "involucre_architecture": 7,
    "armature": 2,
}
EXPECTED_PRIMARY_IDS = [
    "capitulum_within_module_integration_contrast:within_taxon",
    "capitulum_among_module_integration_contrast:among_taxon",
    "capitulum_cross_scale_association_matrix_similarity:within_vs_among",
    "environment_incremental:all_process_extension_beyond_core4:within_taxon",
    "environment_incremental:all_process_extension_beyond_core4:among_taxon",
    "environment_incremental:growing_season_water_input_beyond_core4:within_taxon",
    "environment_incremental:growing_season_water_input_beyond_core4:among_taxon",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--contract", type=Path, required=True)
    p.add_argument("--v3-contract", type=Path, required=True)
    p.add_argument("--structure", type=Path, required=True)
    p.add_argument("--environment", type=Path, required=True)
    p.add_argument("--incremental", type=Path, required=True)
    p.add_argument("--handoff-report", type=Path, required=True)
    p.add_argument("--v3-result", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    return p.parse_args()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def finite(value: Any, label: str) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be numeric") from exc
    if not math.isfinite(out):
        raise ValueError(f"{label} must be finite")
    return out


def close(left: Any, right: Any, label: str, tol: float = 1e-12) -> None:
    lval = finite(left, f"{label}:left")
    rval = finite(right, f"{label}:right")
    if not math.isclose(lval, rval, rel_tol=0.0, abs_tol=tol):
        raise ValueError(f"{label} mismatch: {lval} != {rval}")


def index_rows(rows: list[dict[str, str]], label: str) -> dict[tuple[str, str, str], dict[str, str]]:
    out: dict[tuple[str, str, str], dict[str, str]] = {}
    for row in rows:
        key = (row.get("target_id", ""), row.get("scope", ""), row.get("scale", ""))
        if not all(key):
            raise ValueError(f"{label} contains incomplete key: {key}")
        if key in out:
            raise ValueError(f"{label} contains duplicate key: {key}")
        out[key] = row
    return out


def validate_source(
    contract: dict[str, Any],
    handoff: dict[str, Any],
    v3_result: dict[str, Any],
    structure_path: Path,
    environment_path: Path,
    incremental_path: Path,
) -> dict[str, str]:
    source = contract["source"]
    required_pairs = {
        "azami_run_id": str(handoff["source_run_id"]),
        "azami_artifact_id": str(handoff["source_artifact_id"]),
        "azami_artifact_digest": str(handoff["source_artifact_digest"]),
        "azami_head_sha": str(handoff["source_head_sha"]),
        "v3_1_result_run_id": str(v3_result["workflow_run_id"]),
        "v3_1_result_artifact_id": str(v3_result["artifact_id"]),
        "v3_1_result_artifact_digest": str(v3_result["artifact_digest"]),
    }
    for field, expected in required_pairs.items():
        if str(source[field]) != expected:
            raise ValueError(f"Source {field} does not match frozen provenance")
    if not source["azami_artifact_digest"].startswith("sha256:"):
        raise ValueError("Azami artifact digest must use sha256: prefix")
    if not source["v3_1_result_artifact_digest"].startswith("sha256:"):
        raise ValueError("v3.1 artifact digest must use sha256: prefix")
    if len(source["azami_head_sha"]) != 40:
        raise ValueError("Azami source head must be a full SHA")

    hashes = {
        "structure": sha256(structure_path),
        "environment": sha256(environment_path),
        "incremental": sha256(incremental_path),
    }
    expected_hashes = {
        "structure": handoff["space_table_sha256"],
        "environment": handoff["environment_table_sha256"],
        "incremental": handoff["incremental_table_sha256"],
    }
    for label, digest in hashes.items():
        if digest != expected_hashes[label]:
            raise ValueError(f"{label} table hash mismatch")
    return hashes


def resolve_observed(
    structure_idx: dict[tuple[str, str, str], dict[str, str]],
    incremental_idx: dict[tuple[str, str, str], dict[str, str]],
) -> dict[str, float]:
    return {
        "observed_within_module_contrast": finite(
            structure_idx[(
                "capitulum_within_module_integration_contrast",
                "complete18_min5",
                "within_taxon",
            )]["value"],
            "within module contrast",
        ),
        "observed_among_module_contrast": finite(
            structure_idx[(
                "capitulum_among_module_integration_contrast",
                "complete18_min5",
                "among_taxon",
            )]["value"],
            "among module contrast",
        ),
        "observed_cross_scale_matrix_spearman": finite(
            structure_idx[(
                "capitulum_cross_scale_association_matrix_similarity",
                "complete18_min5",
                "within_vs_among",
            )]["value"],
            "cross-scale matrix similarity",
        ),
        "observed_within_process_partial_r2": finite(
            incremental_idx[(
                "environment_incremental:all_process_extension_beyond_core4",
                "complete18_env_min5",
                "within_taxon",
            )]["partial_r2"],
            "within process partial R2",
        ),
        "observed_among_process_partial_r2": finite(
            incremental_idx[(
                "environment_incremental:all_process_extension_beyond_core4",
                "complete18_env_min5",
                "among_taxon",
            )]["partial_r2"],
            "among process partial R2",
        ),
        "observed_within_gsp_partial_r2": finite(
            incremental_idx[(
                "environment_incremental:growing_season_water_input_beyond_core4",
                "complete18_env_min5",
                "within_taxon",
            )]["partial_r2"],
            "within GSP partial R2",
        ),
        "observed_among_gsp_partial_r2": finite(
            incremental_idx[(
                "environment_incremental:growing_season_water_input_beyond_core4",
                "complete18_env_min5",
                "among_taxon",
            )]["partial_r2"],
            "among GSP partial R2",
        ),
    }


def validate_gap(contract: dict[str, Any], observed: dict[str, float], v3_result: dict[str, Any]) -> dict[str, float]:
    gap = contract["frozen_gap_diagnosis"]
    for key, value in observed.items():
        close(gap[key], value, key)
    ratio = observed["observed_among_module_contrast"] / observed["observed_within_module_contrast"]
    close(gap["observed_among_to_within_module_contrast_ratio"], ratio, "among/within contrast ratio")
    if v3_result["adequate_families"] != []:
        raise ValueError("v4 gap contract requires the frozen v3.1 no-adequate-family result")
    if v3_result["focal_common_vs_modular"]["registered_decision"] != "unresolved":
        raise ValueError("v4 source requires unresolved common-versus-modular result")
    if "overproduced among-taxon" not in gap["v3_1_shared_failure"]:
        raise ValueError("Gap diagnosis must retain the among-taxon overintegration result")
    if "Scale-specific covariance" not in gap["required_new_structure"]:
        raise ValueError("Required new structure must be scale-specific covariance formation")
    return {**observed, "observed_among_to_within_module_contrast_ratio": ratio}


def validate_shared_generator(contract: dict[str, Any]) -> None:
    shared = contract["shared_generator_requirements"]
    if shared["driver_classes"] != ["environment", "pollinator", "antagonist"]:
        raise ValueError("Every v4 family must share the full three-driver layer")
    if shared["interaction_layer"] != "inherit_full_tradeoff_common_lability_v2_interaction_generator_without_change":
        raise ValueError("v4 must not reopen the independent interaction generator")
    if int(shared["n_inferential_units"]) != 17 or int(shared["n_response_endpoints"]) != 18:
        raise ValueError("v4 must retain the 17-unit / 18-endpoint estimand")
    if shared["registered_modules"] != EXPECTED_MODULES:
        raise ValueError("Registered module sizes changed")
    required_true = [
        "hue_is_one_joint_unit",
        "within_and_among_outputs_from_same_simulated_taxa",
        "signed_endpoint_values_retained_before_strength_matrices",
        "shared_parameters_have_identical_priors_across_families",
    ]
    if not all(shared.get(key) is True for key in required_true):
        raise ValueError("One or more shared generator constraints are not fixed true")
    required_false = ["endpoint_specific_parameter_tuning", "outcome_conditioned_prior_truncation"]
    if not all(shared.get(key) is False for key in required_false):
        raise ValueError("Endpoint tuning and outcome-conditioned priors must remain false")


def validate_families(contract: dict[str, Any]) -> list[dict[str, Any]]:
    families = contract["model_families"]
    ids = [row["family_id"] for row in families]
    if ids != EXPECTED_FAMILIES:
        raise ValueError(f"Unexpected family order/IDs: {ids}")
    by = {row["family_id"]: row for row in families}
    for family_id in EXPECTED_FAMILIES:
        row = by[family_id]
        if int(row["complexity_level"]) != EXPECTED_COMPLEXITY[family_id]:
            raise ValueError(f"Unexpected complexity level for {family_id}")
        if row["parent_family"] != EXPECTED_PARENTS[family_id]:
            raise ValueError(f"Unexpected parent family for {family_id}")
        features = (
            bool(row["within_only_module_factor"]),
            bool(row["among_unit_mosaic_loadings"]),
            bool(row["historical_rotation"]),
        )
        if features != EXPECTED_FEATURES[family_id]:
            raise ValueError(f"Unexpected structural features for {family_id}: {features}")
    if "cannot distinguish" not in by["within_only_module_factor"]["identifiability_boundary"]:
        raise ValueError("Within-only factor must retain biological-versus-observation non-identifiability")
    if int(by["combined_scale_decoupling_with_rotation"]["maximum_rotation_rank"]) != 3:
        raise ValueError("Historical rotation rank must be capped at three")
    return families


def validate_structural_constraints(contract: dict[str, Any]) -> None:
    constraints = contract["structural_constraints"]
    within = constraints["within_only_module_factor"]
    if finite(within["exact_taxon_mean"], "within factor taxon mean") != 0.0:
        raise ValueError("Within-only factor must have exact taxon mean zero")
    if not all(within.get(key) is True for key in [
        "independent_of_taxon_level_environment",
        "same_prior_scale_for_all_registered_modules",
        "cannot_enter_taxon_median_directly",
    ]):
        raise ValueError("Within-only factor constraints are incomplete")
    mosaic = constraints["among_unit_mosaic_loadings"]
    if not all(mosaic.get(key) is True for key in [
        "drawn_exchangeably_before_outcomes",
        "centred_to_zero_mean_within_registered_module",
        "shared_prior_scale_across_units",
        "no_unit_selected_by_observed_loading_or_residual",
    ]):
        raise ValueError("Among-unit mosaic constraints are incomplete")
    rotation = constraints["historical_rotation"]
    if not all(rotation.get(key) is True for key in [
        "independent_of_environment",
        "independent_of_registered_module_labels",
        "orthonormal_loading_columns",
        "not_labelled_phylogeny_without_a_tree",
    ]):
        raise ValueError("Historical rotation constraints are incomplete")
    if rotation["rank_drawn_from"] != [1, 2, 3]:
        raise ValueError("Historical rotation rank prior changed")


def v3_primary_ids(v3_contract: dict[str, Any]) -> list[str]:
    ids = []
    for row in v3_contract["primary_fit_targets"]:
        target_id = row["target_id"]
        ids.append(f"{target_id}:{row['scale']}")
    return ids


def validate_targets(contract: dict[str, Any], v3_contract: dict[str, Any]) -> None:
    primary = contract["primary_fit_targets"]
    if int(primary["n_targets"]) != 7:
        raise ValueError("v4 must retain exactly seven primary targets")
    if primary["scope"] != "main_min5_only":
        raise ValueError("v4 primary layer must remain main min5 only")
    if primary["target_ids"] != EXPECTED_PRIMARY_IDS:
        raise ValueError("v4 primary target list changed")
    if v3_primary_ids(v3_contract) != EXPECTED_PRIMARY_IDS:
        raise ValueError("The referenced v3.1 contract does not contain the expected seven targets")
    if primary["distance_definition"] != "reuse_v3_1_seven_target_distance_without_change":
        raise ValueError("v4 must reuse the frozen v3.1 distance")
    if primary["prohibit_min2_double_counting"] is not True:
        raise ValueError("min2 double counting must remain prohibited")


def validate_context(
    contract: dict[str, Any],
    environment_idx: dict[tuple[str, str, str], dict[str, str]],
) -> int:
    validation = contract["replication_and_context_validation"]
    patterns = validation["min2_replication_patterns"]
    if len(patterns) != 6 or len(set(patterns)) != 6:
        raise ValueError("Exactly six unique min2 replication patterns are required")
    context = validation["main_environment_block_r2_context"]
    rows = [
        row for (target_id, scope, scale), row in environment_idx.items()
        if target_id.startswith("environment_block_r2:")
        and scope == context["scope"]
        and scale in set(context["scales"])
    ]
    if len(rows) != int(context["n_r2_targets"]) or len(rows) != 12:
        raise ValueError(f"Expected 12 main environment-block R2 context rows, found {len(rows)}")
    if context["cross_scale_cosines_excluded"] is not True:
        raise ValueError("Uncertain cross-scale coefficient cosines must stay excluded")
    if context["metric"] != "root_mean_squared_error":
        raise ValueError("Context metric must remain RMSE")
    inherited = validation["existing_literature_heldout_rate"]
    if inherited["inherited_family"] != "full_tradeoff_common_lability":
        raise ValueError("v4 interaction heldout must inherit the unchanged common-lability interaction layer")
    if inherited["same_value_for_all_v4_families"] is not True:
        raise ValueError("Independent heldout must remain nondiscriminating across v4 covariance families")
    return len(rows)


def validate_screen(contract: dict[str, Any]) -> dict[str, float]:
    screen = contract["screen_design"]
    if int(screen["draws_per_seed_per_family"]) < 500:
        raise ValueError("v4 requires at least 500 draws per seed per family")
    if len(screen["seeds"]) != 4 or len(set(screen["seeds"])) != 4:
        raise ValueError("v4 requires four unique deterministic seeds")
    accept = finite(screen["accept_fraction"], "accept fraction")
    if not 0 < accept <= 0.1:
        raise ValueError("accept fraction must lie in (0, 0.1]")
    if int(screen["minimum_accepted_draws"]) < 100:
        raise ValueError("v4 requires at least 100 accepted draws")
    gates = {
        "absolute_primary_adequacy_threshold": finite(screen["absolute_primary_adequacy_threshold"], "absolute adequacy"),
        "minimum_replication_pattern_rate": finite(screen["minimum_replication_pattern_rate"], "replication rate"),
        "minimum_relative_primary_distance_improvement_over_parent": finite(screen["minimum_relative_primary_distance_improvement_over_parent"], "relative improvement"),
        "maximum_context_r2_rmse_increase_relative_to_parent": finite(screen["maximum_context_r2_rmse_increase_relative_to_parent"], "context RMSE increase"),
    }
    if gates != {
        "absolute_primary_adequacy_threshold": 1.0,
        "minimum_replication_pattern_rate": 0.75,
        "minimum_relative_primary_distance_improvement_over_parent": 0.15,
        "maximum_context_r2_rmse_increase_relative_to_parent": 0.05,
    }:
        raise ValueError(f"v4 gates changed: {gates}")
    if "lowest declared complexity" not in screen["complexity_selection_rule"]:
        raise ValueError("Complexity rule must prefer the simplest near-best adequate family")
    required_prohibited = {"Bayes_factor", "posterior_model_probability", "likelihood_ratio", "causal_model_selection"}
    if not required_prohibited.issubset(set(screen["prohibited_labels"])):
        raise ValueError("Misleading probability/causal labels must remain prohibited")
    return gates


def validate_promotion(contract: dict[str, Any]) -> None:
    promotion = contract["promotion_rule"]
    requirements = promotion["family_eligible_only_if"]
    if len(requirements) != 5 or len(set(requirements)) != 5:
        raise ValueError("v4 family eligibility must contain five unique gates")
    if "failure reference" not in promotion["baseline_rule"]:
        raise ValueError("Baseline must remain a failure reference")
    if "structural non-identifiability" not in promotion["multiple_family_rule"]:
        raise ValueError("Near-tied nonnested adequate families must retain non-identifiability")
    boundary = promotion["claim_boundary"]
    for phrase in [
        "sufficient covariance architecture",
        "not whether the within-only factor is biological versus photographic",
        "not phylogenetic history",
        "not a unique ecological or evolutionary mechanism",
    ]:
        if phrase not in boundary:
            raise ValueError(f"Claim boundary missing phrase: {phrase}")


def main() -> int:
    args = parse_args()
    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    v3_contract = json.loads(args.v3_contract.read_text(encoding="utf-8"))
    handoff = json.loads(args.handoff_report.read_text(encoding="utf-8"))
    v3_result = json.loads(args.v3_result.read_text(encoding="utf-8"))
    if contract.get("contract_version") != EXPECTED_VERSION:
        raise ValueError(f"Expected contract version {EXPECTED_VERSION}")
    if contract.get("status") != "frozen_before_v4_family_outcomes":
        raise ValueError("v4 status must remain frozen before outcomes")

    structure_rows = load_csv(args.structure)
    environment_rows = load_csv(args.environment)
    incremental_rows = load_csv(args.incremental)
    structure_idx = index_rows(structure_rows, "structure")
    environment_idx = index_rows(environment_rows, "environment")
    incremental_idx = index_rows(incremental_rows, "incremental")

    hashes = validate_source(
        contract,
        handoff,
        v3_result,
        args.structure,
        args.environment,
        args.incremental,
    )
    observed = resolve_observed(structure_idx, incremental_idx)
    gap = validate_gap(contract, observed, v3_result)
    validate_shared_generator(contract)
    families = validate_families(contract)
    validate_structural_constraints(contract)
    validate_targets(contract, v3_contract)
    context_rows = validate_context(contract, environment_idx)
    gates = validate_screen(contract)
    validate_promotion(contract)

    audit = {
        "status": "scale_specific_covariance_v4_contract_validated_before_family_outcomes",
        "contract_version": contract["contract_version"],
        "contract_sha256": sha256(args.contract),
        "source_table_sha256": hashes,
        "v3_1_result_summary_sha256": sha256(args.v3_result),
        "n_model_families": len(families),
        "model_families": [row["family_id"] for row in families],
        "complexity_levels": {row["family_id"]: row["complexity_level"] for row in families},
        "n_primary_fit_targets": 7,
        "n_min2_replication_patterns": 6,
        "n_main_environment_r2_context_targets": context_rows,
        "observed_gap": gap,
        "screen_gates": gates,
        "outcomes_inspected": False,
        "scoring_status": "not_run",
        "claim_status": "structural_covariance_architecture_contract_only",
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "scale_specific_covariance_v4_contract_audit.json").write_text(
        json.dumps(audit, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(audit, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
