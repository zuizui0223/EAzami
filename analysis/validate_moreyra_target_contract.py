#!/usr/bin/env python3
"""Validate the target/reference FASTA contract for the Moreyra reconstruction pilot.

Execution is blocked unless a candidate is explicitly approved, has a matching
SHA256, is a HybPiper target/reference FASTA rather than a bait/probe file, and
meets its declared overlap threshold against the public 1,061 Moreyra locus IDs.

An unresolved template may be checked with ``--allow-unapproved`` for CI/schema
purposes, but the resulting report always has ``execution_allowed = false``.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from statistics import median
from typing import Any, Mapping, Sequence

MODULE_PATH = Path(__file__).with_name("recover_compositae1061_target.py")
SPEC = importlib.util.spec_from_file_location("recover_compositae1061_target_contract_base", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
base = importlib.util.module_from_spec(SPEC)
sys.modules["recover_compositae1061_target_contract_base"] = base
SPEC.loader.exec_module(base)

DEFAULT_CONTRACT = Path("config/moreyra_target_contract.template.json")
DEFAULT_LOCI = Path(
    "data/evidence/generated/moreyra_author_repository/locus_sets/"
    "moreyra_public_1061_loci.txt"
)
DEFAULT_REPORT = Path(
    "data/evidence/generated/moreyra_target_contract_validation.json"
)

IDENTITY_STATUSES = {
    "unresolved",
    "compatible_compositae1061_target",
    "exact_moreyra_target",
}
TARGET_TYPES = {"hybpiper_reference_fasta", "bait_probe_fasta", "unresolved"}
SEQUENCE_TYPES = {"dna", "protein", "unresolved"}
MAPPING_MODES = {"bwa", "diamond", "blastx", "unresolved"}
BAIT_WORDS = ("bait", "probe", "oligo", "mybaits")


class ContractError(ValueError):
    """Raised when a target contract is internally inconsistent or unsafe."""


def clean(value: object) -> str:
    return str(value or "").strip()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ContractError(f"Contract not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ContractError(f"Invalid JSON contract {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError("Target contract must be a JSON object")
    return value


def nested_mapping(value: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    child = value.get(key)
    if not isinstance(child, Mapping):
        raise ContractError(f"Contract field {key!r} must be an object")
    return child


def optional_int(value: Any, field: str) -> int | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        raise ContractError(f"{field} must be an integer or null")
    try:
        result = int(value)
    except (TypeError, ValueError) as exc:
        raise ContractError(f"{field} must be an integer or null") from exc
    if result < 1:
        raise ContractError(f"{field} must be positive")
    return result


def required_float(value: Any, field: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ContractError(f"{field} must be numeric") from exc
    if not 0 <= result <= 1:
        raise ContractError(f"{field} must be between 0 and 1")
    return result


def resolve_target_path(contract_path: Path, local_path: str) -> Path:
    target = Path(local_path)
    if target.is_absolute():
        return target
    # Repository contracts use paths relative to the repository root.  Locate the
    # root from a config/ contract when possible; otherwise use the current cwd.
    if contract_path.parent.name == "config":
        root = contract_path.parent.parent
        return (root / target).resolve()
    return (Path.cwd() / target).resolve()


def parse_fasta(path: Path) -> list[tuple[str, str]]:
    try:
        payload = path.read_bytes()
    except FileNotFoundError as exc:
        raise ContractError(f"Target FASTA not found: {path}") from exc
    records = base.parse_fasta(payload)
    if not records:
        raise ContractError(f"No FASTA records found in {path}")
    return records


def sequence_alphabet(records: Sequence[tuple[str, str]]) -> str:
    observed = {char.upper() for _, sequence in records for char in sequence if char not in ".-*"}
    dna = set("ACGTURYSWKMBDHVN")
    protein = set("ABCDEFGHIKLMNPQRSTVWXYZOUJB")
    if observed and observed <= dna:
        return "dna"
    if observed and observed <= protein:
        return "protein"
    return "mixed_or_invalid"


def normalized_locus_matches(
    records: Sequence[tuple[str, str]], loci: Sequence[str]
) -> set[str]:
    normalized = {base.normalize(locus): locus for locus in loci}
    matched: set[str] = set()
    for header, _ in records:
        for value in base.variants(header):
            if value in normalized:
                matched.add(normalized[value])
    return matched


def validate_contract(
    contract: Mapping[str, Any],
    *,
    contract_path: Path,
    loci: Sequence[str],
    allow_unapproved: bool = False,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    version = clean(contract.get("contract_version"))
    if not version:
        errors.append("contract_version is required")

    identity = clean(contract.get("identity_status"))
    target_type = clean(contract.get("target_type"))
    sequence_type = clean(contract.get("target_sequence_type"))
    mapping_mode = clean(contract.get("mapping_mode"))
    if identity not in IDENTITY_STATUSES:
        errors.append(f"identity_status must be one of {sorted(IDENTITY_STATUSES)}")
    if target_type not in TARGET_TYPES:
        errors.append(f"target_type must be one of {sorted(TARGET_TYPES)}")
    if sequence_type not in SEQUENCE_TYPES:
        errors.append(f"target_sequence_type must be one of {sorted(SEQUENCE_TYPES)}")
    if mapping_mode not in MAPPING_MODES:
        errors.append(f"mapping_mode must be one of {sorted(MAPPING_MODES)}")

    source = nested_mapping(contract, "source")
    expected = nested_mapping(contract, "expected")
    approval = nested_mapping(contract, "approval")
    approved = bool(approval.get("approved_for_12_sample_pilot"))
    local_path = clean(contract.get("local_path"))
    candidate_label = clean(contract.get("candidate_label"))

    if not local_path:
        errors.append("local_path is required")
    target_path = resolve_target_path(contract_path, local_path) if local_path else Path("")

    declared_public_count = optional_int(
        expected.get("moreyra_public_locus_count"),
        "expected.moreyra_public_locus_count",
    )
    if declared_public_count is not None and declared_public_count != len(loci):
        errors.append(
            "expected.moreyra_public_locus_count does not match the supplied locus manifest"
        )
    threshold = required_float(
        expected.get("minimum_normalized_locus_overlap", 0.95),
        "expected.minimum_normalized_locus_overlap",
    )
    declared_record_count = optional_int(
        expected.get("record_count"), "expected.record_count"
    )
    declared_unique_tokens = optional_int(
        expected.get("unique_first_tokens"), "expected.unique_first_tokens"
    )
    declared_sha = clean(expected.get("sha256")).casefold()
    if declared_sha and not re.fullmatch(r"[0-9a-f]{64}", declared_sha):
        errors.append("expected.sha256 must be a lowercase or uppercase 64-character SHA256")

    unresolved = identity == "unresolved"
    if approved and unresolved:
        errors.append("An unresolved target cannot be approved for pilot execution")
    if approved and target_type != "hybpiper_reference_fasta":
        errors.append("Only a HybPiper reference/target FASTA may be approved")
    if approved and sequence_type not in {"dna", "protein"}:
        errors.append("Approved target_sequence_type must be dna or protein")
    if approved and mapping_mode == "unresolved":
        errors.append("Approved mapping_mode cannot be unresolved")
    if sequence_type == "dna" and mapping_mode != "bwa" and approved:
        errors.append("Approved DNA target currently requires mapping_mode=bwa")
    if sequence_type == "protein" and mapping_mode not in {"diamond", "blastx"} and approved:
        errors.append("Approved protein target requires diamond or blastx mapping mode")

    source_required = (
        "repository",
        "dataset_id",
        "dataset_version",
        "landing_url",
        "download_url",
    )
    if approved:
        for key in source_required:
            if not clean(source.get(key)):
                errors.append(f"source.{key} is required for an approved target")
        if not declared_sha:
            errors.append("expected.sha256 is required for an approved target")
        if not candidate_label:
            errors.append("candidate_label is required for an approved target")
        for key in ("approved_by", "approval_date", "basis"):
            if not clean(approval.get(key)):
                errors.append(f"approval.{key} is required for an approved target")
    if identity == "exact_moreyra_target" and not clean(source.get("method_confirmation")):
        errors.append(
            "source.method_confirmation is required for identity_status=exact_moreyra_target"
        )
    if identity == "compatible_compositae1061_target" and approved:
        basis = clean(approval.get("basis")).casefold()
        if "compatible" not in basis and "not exact" not in basis:
            warnings.append(
                "Approval basis should explicitly state that a compatible target is not exact"
            )

    file_metrics: dict[str, Any] | None = None
    if target_path and target_path.exists():
        records = parse_fasta(target_path)
        lengths = [len(sequence) for _, sequence in records]
        first_tokens = {
            header.split()[0] if header.split() else header for header, _ in records
        }
        alphabet = sequence_alphabet(records)
        matched = normalized_locus_matches(records, loci)
        overlap = len(matched) / len(loci)
        observed_sha = sha256_file(target_path)
        filename_text = target_path.name.casefold()
        file_metrics = {
            "resolved_path": str(target_path),
            "sha256": observed_sha,
            "record_count": len(records),
            "unique_first_tokens": len(first_tokens),
            "total_bp": sum(lengths),
            "minimum_length": min(lengths),
            "median_length": median(lengths),
            "maximum_length": max(lengths),
            "sequence_alphabet": alphabet,
            "matched_moreyra_loci": len(matched),
            "moreyra_public_loci": len(loci),
            "normalized_locus_overlap": overlap,
        }
        if any(word in filename_text for word in BAIT_WORDS):
            errors.append("Target filename appears to describe a bait/probe oligo file")
        if target_type == "bait_probe_fasta":
            errors.append("target_type=bait_probe_fasta is not executable")
        if alphabet == "mixed_or_invalid":
            errors.append("FASTA contains a mixed or invalid sequence alphabet")
        if sequence_type in {"dna", "protein"} and alphabet != sequence_type:
            errors.append(
                f"Declared target_sequence_type={sequence_type} but observed alphabet={alphabet}"
            )
        if declared_sha and observed_sha != declared_sha:
            errors.append("Observed target SHA256 does not match expected.sha256")
        if declared_record_count is not None and len(records) != declared_record_count:
            errors.append("Observed FASTA record count does not match expected.record_count")
        if declared_unique_tokens is not None and len(first_tokens) != declared_unique_tokens:
            errors.append(
                "Observed unique first-token count does not match expected.unique_first_tokens"
            )
        if overlap < threshold:
            errors.append(
                f"Normalized locus overlap {overlap:.6f} is below required threshold {threshold:.6f}"
            )
    elif approved:
        errors.append(f"Approved target FASTA does not exist: {target_path}")
    else:
        warnings.append(f"Unapproved target FASTA is absent: {target_path}")

    execution_allowed = approved and not errors and file_metrics is not None
    if not approved and not allow_unapproved:
        errors.append(
            "Target is not approved for the 12-sample pilot; use --allow-unapproved only to validate a template"
        )
    if unresolved and not allow_unapproved:
        errors.append("identity_status=unresolved blocks pilot execution")

    return {
        "contract_version": version,
        "identity_status": identity,
        "candidate_label": candidate_label,
        "target_type": target_type,
        "target_sequence_type": sequence_type,
        "mapping_mode": mapping_mode,
        "approved_for_12_sample_pilot": approved,
        "allow_unapproved_mode": allow_unapproved,
        "source": dict(source),
        "expected": dict(expected),
        "approval": dict(approval),
        "file_metrics": file_metrics,
        "errors": errors,
        "warnings": warnings,
        "contract_valid": not errors,
        "execution_allowed": execution_allowed,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--moreyra-loci", type=Path, default=DEFAULT_LOCI)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--allow-unapproved", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    contract = read_json(args.contract)
    loci = base.read_loci(args.moreyra_loci)
    try:
        report = validate_contract(
            contract,
            contract_path=args.contract,
            loci=loci,
            allow_unapproved=args.allow_unapproved,
        )
    except ContractError as exc:
        report = {
            "contract_valid": False,
            "execution_allowed": False,
            "errors": [str(exc)],
            "warnings": [],
        }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"contract_valid={report['contract_valid']}")
    print(f"execution_allowed={report['execution_allowed']}")
    for error in report.get("errors", []):
        print(f"ERROR: {error}")
    for warning in report.get("warnings", []):
        print(f"WARNING: {warning}")
    print(args.report)
    return 0 if report["contract_valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
