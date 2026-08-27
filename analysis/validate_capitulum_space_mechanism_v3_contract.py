#!/usr/bin/env python3
"""Validate the preregistered EAzami capitulum-space mechanism-v3 contract.

The validator resolves the declared primary targets against the provenance-gated
Azami source tables already imported into EAzami.  It checks that the v3 score
will use statistically matched targets, that the >=2 scope remains a replication
check rather than a duplicate fit term, and that descriptive coefficient geometry
is not silently promoted to causal evidence.

This script does not simulate or rank model families.  Its purpose is to freeze a
machine-readable contract before v3 family outcomes are generated.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


EXPECTED_FAMILIES = {
    "environment_only",
    "pollinator_only",
    "antagonist_only",
    "full_tradeoff_common_lability",
    "full_tradeoff_modular_evolvability",
}
EXPECTED_MODULE_SIZES = {
    "orientation": 1,
    "colour": 3,
    "shape": 4,
    "involucre_architecture": 7,
    "armature": 2,
}
STRUCTURE_IDS = {
    "capitulum_within_module_integration_contrast",
    "capitulum_among_module_integration_contrast",
    "capitulum_cross_scale_association_matrix_similarity",
}
ALLOWED_SCALES = {"within_taxon", "among_taxon", "within_vs_among"}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--contract", type=Path, required=True)
    p.add_argument("--structure", type=Path, required=True)
    p.add_argument("--environment", type=Path, required=True)
    p.add_argument("--incremental", type=Path, required=True)
    p.add_argument("--handoff-report", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    return p.parse_args()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def as_float(value: Any, label: str) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be numeric: {value!r}") from exc
    if out != out or out in (float("inf"), float("-inf")):
        raise ValueError(f"{label} must be finite")
    return out


def as_bool(value: Any, label: str) -> bool:
    text = str(value).strip().lower()
    if text in {"true", "1", "yes"}:
        return True
    if text in {"false", "0", "no"}:
        return False
    raise ValueError(f"{label} must be boolean-like: {value!r}")


def unique_index(rows: list[dict[str, str]], label: str) -> dict[tuple[str, str, str], dict[str, str]]:
    index: dict[tuple[str, str, str], dict[str, str]] = {}
    for row in rows:
        key = (row.get("target_id", ""), row.get("scope", ""), row.get("scale", ""))
        if not all(key):
            raise ValueError(f"{label} contains an incomplete target key: {key}")
        if key in index:
            raise ValueError(f"{label} contains duplicate target key: {key}")
        index[key] = row
    return index


def validate_source_provenance(
    contract: dict[str, Any],
    report: dict[str, Any],
    structure_path: Path,
    environment_path: Path,
    incremental_path: Path,
) -> dict[str, str]:
    source = contract["source"]
    checks = {
        "run_id": str(report["source_run_id"]),
        "artifact_id": str(report["source_artifact_id"]),
        "artifact_digest": str(report["source_artifact_digest"]),
        "head_sha": str(report["source_head_sha"]),
    }
    for field, observed in checks.items():
        if str(source[field]) != observed:
            raise ValueError(f"Contract source {field} does not match handoff report")
    if not source["artifact_digest"].startswith("sha256:"):
        raise ValueError("Source artifact digest must use sha256: prefix")
    if len(source["head_sha"]) != 40:
        raise ValueError("Source head SHA must be a full commit SHA")

    table_hashes = {
        "structure": sha256(structure_path),
        "environment": sha256(environment_path),
        "incremental": sha256(incremental_path),
    }
    expected_hashes = {
        "structure": report["space_table_sha256"],
        "environment": report["environment_table_sha256"],
        "incremental": report["incremental_table_sha256"],
    }
    for label, observed in table_hashes.items():
        if observed != expected_hashes[label]:
            raise ValueError(f"{label} table SHA-256 does not match handoff report")
    return table_hashes


def validate_units(contract: dict[str, Any]) -> dict[str, int]:
    units = contract["inferential_units"]
    ids = [str(x["unit_id"]) for x in units]
    if len(ids) != 17 or len(set(ids)) != 17:
        raise ValueError("Contract must contain 17 unique inferential units")
    module_sizes = Counter(str(x["module"]) for x in units)
    if dict(module_sizes) != EXPECTED_MODULE_SIZES:
        raise ValueError(
            f"Unexpected registered-module sizes: {dict(module_sizes)}; "
            f"expected {EXPECTED_MODULE_SIZES}"
        )
    constraints = contract["generator_constraints"]
    if int(constraints["n_inferential_units"]) != 17:
        raise ValueError("generator_constraints n_inferential_units must equal 17")
    if constraints.get("endpoint_specific_parameter_tuning") is not False:
        raise ValueError("Endpoint-specific parameter tuning must be prohibited")
    if constraints.get("hue_is_one_joint_unit") is not True:
        raise ValueError("Circular hue must remain one joint unit")
    if constraints.get("within_and_among_outputs_must_be_generated_from_same_simulated_taxa") is not True:
        raise ValueError("Within and among outputs must use the same simulated taxa")
    return dict(module_sizes)


def validate_families(contract: dict[str, Any]) -> list[str]:
    families = contract["model_families"]
    ids = [str(x["family_id"]) for x in families]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate model family IDs")
    if set(ids) != EXPECTED_FAMILIES:
        raise ValueError(f"Unexpected model families: {ids}")
    by = {str(x["family_id"]): x for x in families}
    common = by["full_tradeoff_common_lability"]
    modular = by["full_tradeoff_modular_evolvability"]
    if common["lability_structure"] == modular["lability_structure"]:
        raise ValueError("Common-lability and modular families must differ structurally")
    for family in (common, modular):
        if not all(family.get(x) is True for x in ("environment", "pollinator", "antagonist")):
            raise ValueError("Both focal full-tradeoff families must include all three driver classes")
    return ids


def resolve_primary_targets(
    contract: dict[str, Any],
    structure_index: dict[tuple[str, str, str], dict[str, str]],
    incremental_index: dict[tuple[str, str, str], dict[str, str]],
) -> list[dict[str, Any]]:
    resolved: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for spec in contract["primary_fit_targets"]:
        key = (str(spec["target_id"]), str(spec["scope"]), str(spec["scale"]))
        if key in seen:
            raise ValueError(f"Primary target is double-counted: {key}")
        seen.add(key)
        if key[2] not in ALLOWED_SCALES:
            raise ValueError(f"Unsupported primary target scale: {key[2]}")
        if key[1].endswith("min2"):
            raise ValueError("min2 sensitivity rows must not enter primary fit distance")

        if key[0] in STRUCTURE_IDS:
            row = structure_index.get(key)
            if row is None:
                raise ValueError(f"Missing structure target: {key}")
            value = as_float(row["value"], f"{key} value")
            low = as_float(row["ci95_low"], f"{key} ci95_low")
            high = as_float(row["ci95_high"], f"{key} ci95_high")
            if not low <= value <= high:
                raise ValueError(f"Structure point estimate lies outside interval: {key}")
            if spec["distance"] != "bootstrap_standardized_huber":
                raise ValueError("Structure targets must use bootstrap-standardized Huber distance")
            resolved.append({
                **spec,
                "observed_value": value,
                "observed_ci95_low": low,
                "observed_ci95_high": high,
                "observed_support": True,
            })
            continue

        if not key[0].startswith("environment_incremental:"):
            raise ValueError(f"Unsupported primary target ID: {key[0]}")
        row = incremental_index.get(key)
        if row is None:
            raise ValueError(f"Missing incremental target: {key}")
        value = as_float(row["partial_r2"], f"{key} partial_r2")
        support = as_bool(row["supported_0_05"], f"{key} supported_0_05")
        expected = bool(spec["expected_support"])
        if support != expected:
            raise ValueError(f"Contract expected support does not match frozen observation: {key}")
        tolerance = as_float(spec["tolerance"], f"{key} tolerance")
        if tolerance <= 0 or tolerance > 1:
            raise ValueError(f"Incremental tolerance must be in (0,1]: {key}")
        if spec["distance"] != "bounded_numeric_plus_support_state":
            raise ValueError("Incremental targets must use bounded numeric plus support-state distance")
        resolved.append({
            **spec,
            "observed_value": value,
            "observed_delta_r2": as_float(row["delta_r2"], f"{key} delta_r2"),
            "observed_permutation_p": as_float(row["permutation_p"], f"{key} permutation_p"),
            "observed_q_bh_block_specific": (
                None if str(row.get("q_bh_block_specific", "")).strip() == ""
                else as_float(row["q_bh_block_specific"], f"{key} q")
            ),
            "observed_support": support,
        })

    expected_outputs = set(contract["required_model_outputs"])
    required_keys = {
        x["target_id"] if x["target_id"] in STRUCTURE_IDS
        else f"{x['target_id']}:{x['scale']}"
        for x in resolved
    }
    if required_keys != expected_outputs:
        raise ValueError(
            "required_model_outputs must match the seven primary fit estimands exactly; "
            f"resolved={sorted(required_keys)}, declared={sorted(expected_outputs)}"
        )
    return resolved


def validate_replication(
    contract: dict[str, Any],
    structure_index: dict[tuple[str, str, str], dict[str, str]],
    incremental_index: dict[tuple[str, str, str], dict[str, str]],
) -> dict[str, Any]:
    replication = contract["replication_targets"]
    if replication.get("must_not_be_double_counted_in_primary_distance") is not True:
        raise ValueError("Replication rows must be explicitly excluded from primary distance")

    structure_rows = [
        structure_index[(target_id, "complete18_min2", scale)]
        for target_id, scale in [
            ("capitulum_within_module_integration_contrast", "within_taxon"),
            ("capitulum_among_module_integration_contrast", "among_taxon"),
            ("capitulum_cross_scale_association_matrix_similarity", "within_vs_among"),
        ]
    ]
    if not all(as_float(row["value"], "replication structure value") > 0 for row in structure_rows):
        raise ValueError("All three min2 structure replication values must be positive")

    incremental_expectations = [
        ("environment_incremental:all_process_extension_beyond_core4", "within_taxon", False),
        ("environment_incremental:all_process_extension_beyond_core4", "among_taxon", True),
        ("environment_incremental:growing_season_water_input_beyond_core4", "among_taxon", True),
    ]
    resolved = []
    for target_id, scale, expected in incremental_expectations:
        key = (target_id, "complete18_env_min2", scale)
        row = incremental_index.get(key)
        if row is None:
            raise ValueError(f"Missing min2 replication row: {key}")
        support = as_bool(row["supported_0_05"], f"{key} support")
        if support != expected:
            raise ValueError(f"Unexpected min2 support state: {key}")
        resolved.append({"target_id": target_id, "scale": scale, "support": support})
    return {
        "structure_positive": True,
        "incremental_support_patterns": resolved,
        "role": replication["role"],
    }


def validate_context_and_comparison(contract: dict[str, Any]) -> None:
    context = contract["context_only_targets"]
    if context.get("environment_block_r2_and_coefficient_cosines") != "descriptive_not_scored_in_v3_primary_distance":
        raise ValueError("Environment-block R2/cosines must remain descriptive in v3 primary score")
    comparison = contract["family_comparison"]
    if int(comparison["draws_per_seed_per_family"]) < 100:
        raise ValueError("Too few prior draws per seed")
    if len(comparison["seeds"]) < 4 or len(set(comparison["seeds"])) != len(comparison["seeds"]):
        raise ValueError("At least four unique deterministic seeds are required")
    fraction = as_float(comparison["accept_fraction"], "accept_fraction")
    if not 0 < fraction <= 0.2:
        raise ValueError("accept_fraction must be in (0, 0.2]")
    forbidden = set(comparison["prohibited_statistics"])
    required_forbidden = {"Bayes_factor", "posterior_model_probability", "likelihood_ratio"}
    if not required_forbidden.issubset(forbidden):
        raise ValueError("Misleading probability/likelihood labels must remain prohibited")
    if contract["promotion_rule"]["causal_boundary"].strip() == "":
        raise ValueError("A causal claim boundary is required")


def write_primary_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "target_id", "scope", "scale", "metric", "distance", "weight",
        "expected_support", "tolerance", "observed_value", "observed_ci95_low",
        "observed_ci95_high", "observed_delta_r2", "observed_permutation_p",
        "observed_q_bh_block_specific", "observed_support",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fields})


def main() -> int:
    args = parse_args()
    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    report = json.loads(args.handoff_report.read_text(encoding="utf-8"))
    structure_rows = load_csv(args.structure)
    environment_rows = load_csv(args.environment)
    incremental_rows = load_csv(args.incremental)

    table_hashes = validate_source_provenance(
        contract, report, args.structure, args.environment, args.incremental
    )
    module_sizes = validate_units(contract)
    families = validate_families(contract)
    structure_index = unique_index(structure_rows, "structure table")
    environment_index = unique_index(environment_rows, "environment table")
    incremental_index = unique_index(incremental_rows, "incremental table")
    if len(environment_index) != 36:
        raise ValueError(f"Expected 36 environment-block rows, found {len(environment_index)}")
    resolved_primary = resolve_primary_targets(contract, structure_index, incremental_index)
    replication = validate_replication(contract, structure_index, incremental_index)
    validate_context_and_comparison(contract)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    primary_csv = args.out_dir / "capitulum_space_mechanism_v3_primary_targets.csv"
    write_primary_csv(primary_csv, resolved_primary)
    audit = {
        "status": "v3_contract_validated_before_model_family_outcomes",
        "contract_version": contract["contract_version"],
        "contract_sha256": sha256(args.contract),
        "source_table_sha256": table_hashes,
        "source_run_id": contract["source"]["run_id"],
        "source_artifact_id": contract["source"]["artifact_id"],
        "source_artifact_digest": contract["source"]["artifact_digest"],
        "n_inferential_units": 17,
        "module_sizes": module_sizes,
        "model_families": families,
        "n_primary_fit_targets": len(resolved_primary),
        "primary_target_keys": [
            [row["target_id"], row["scope"], row["scale"]]
            for row in resolved_primary
        ],
        "replication_validation": replication,
        "environment_rows_retained_as_context": len(environment_index),
        "scoring_status": "not_run",
        "causal_status": "structural_sufficiency_contract_only",
    }
    audit_path = args.out_dir / "capitulum_space_mechanism_v3_contract_audit.json"
    audit_path.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(audit, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
