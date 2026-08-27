#!/usr/bin/env python3
"""Fail-closed allocation for the JPN36 phyllary-access pilot v1."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


PROTOCOL_VERSION = "jpn36_phyllary_access_pilot_v1"
FROZEN_SEED = "JPN36-PHYLLARY-ACCESS-V1-20260827"
TARGET_PAIRS = 12
MAX_POPULATION_FRACTION = 0.02

ELIGIBLE_REQUIRED = {
    "pilot_id",
    "site_id",
    "population_id",
    "observation_date_local",
    "pair_id",
    "individual_id",
    "capitulum_id",
    "phenological_stage",
    "capitulum_diameter_bin",
    "baseline_damage_bin",
    "phyllary_posture_class",
    "natural_stickiness_state",
    "taxon_identity_confirmed",
    "live_state_confirmed",
    "permit_record_id",
    "land_manager_authorization_record_id",
    "conservation_review_record_id",
    "terminal_collection_authorization_record_id",
    "viability_authorization_record_id",
    "device_qualification_record_id",
    "eligible",
}

OUTPUT_FIELDS = [
    "pilot_id",
    "site_id",
    "population_id",
    "pair_id",
    "individual_id",
    "capitulum_id",
    "matched_individual_id",
    "matched_capitulum_id",
    "assignment",
    "randomization_seed",
    "randomization_method",
    "assignment_hash",
    "authorization_record_id",
    "device_qualification_record_id",
    "device_id",
    "material_lot",
    "target_access_gap_mm",
    "assignment_datetime_local",
    "treatment_attempted",
    "handling_duration_seconds",
    "achieved_access_gap_mm",
    "pre_head_orientation_deg",
    "post_head_orientation_deg",
    "device_retained",
    "floret_or_reproductive_contact",
    "tissue_injury",
    "treatment_integrity",
    "attrition_reason",
    "notes",
]


def _is_true(value: object) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y", "pass", "confirmed"}


def read_eligible(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = sorted(ELIGIBLE_REQUIRED - set(reader.fieldnames or []))
        if missing:
            raise RuntimeError(f"Eligible-head ledger is missing required columns: {missing}")
        rows = list(reader)
    kept = [row for row in rows if _is_true(row["eligible"])]
    if len(kept) != TARGET_PAIRS * 2:
        raise RuntimeError(
            f"Pilot v1 requires exactly {TARGET_PAIRS * 2} eligible heads; found {len(kept)}"
        )
    return kept


def validate_authorization(record: dict) -> None:
    exact = {
        "protocol_version": PROTOCOL_VERSION,
        "execution_authorized": True,
        "land_manager_authorization_status": "approved",
        "manipulation_authorization_status": "approved",
        "conservation_review_status": "approved",
        "terminal_collection_authorization_status": "approved",
        "viability_assay_authorization_status": "approved",
        "population_census_complete": True,
        "device_qualification_status": "passed",
    }
    for key, expected in exact.items():
        if record.get(key) != expected:
            raise RuntimeError(f"Authorization gate failed: {key} must equal {expected!r}")
    required_text = [
        "authorization_record_id",
        "site_id",
        "population_id",
        "device_qualification_record_id",
        "device_id",
        "material_lot",
    ]
    for key in required_text:
        if not str(record.get(key, "")).strip():
            raise RuntimeError(f"Authorization gate failed: {key} is required")
    counted = int(record.get("counted_flowering_individuals", 0))
    manipulation_quota = int(record.get("authorized_manipulation_head_quota", 0))
    collection_quota = int(record.get("authorized_terminal_collection_head_quota", 0))
    if TARGET_PAIRS * 2 > counted * MAX_POPULATION_FRACTION:
        raise RuntimeError(
            "Authorization gate failed: 24 experimental individuals exceed the frozen "
            "2 percent population cap"
        )
    if manipulation_quota < TARGET_PAIRS * 2 or collection_quota < TARGET_PAIRS * 2:
        raise RuntimeError("Authorization gate failed: manipulation/collection quota is below 24 heads")
    if float(record.get("frozen_target_access_gap_mm", 0)) <= 0:
        raise RuntimeError("Authorization gate failed: frozen_target_access_gap_mm must be positive")


def validate_rows(rows: list[dict[str, str]], authorization: dict) -> dict[str, list[dict[str, str]]]:
    by_pair: dict[str, list[dict[str, str]]] = defaultdict(list)
    seen_individuals: set[str] = set()
    seen_heads: set[str] = set()
    expected_records = {
        "permit_record_id": authorization["authorization_record_id"],
        "land_manager_authorization_record_id": authorization["authorization_record_id"],
        "conservation_review_record_id": authorization["authorization_record_id"],
        "terminal_collection_authorization_record_id": authorization["authorization_record_id"],
        "viability_authorization_record_id": authorization["authorization_record_id"],
        "device_qualification_record_id": authorization["device_qualification_record_id"],
    }
    for row in rows:
        if row["site_id"] != authorization["site_id"] or row["population_id"] != authorization["population_id"]:
            raise RuntimeError("Eligible head does not match the authorized site/population")
        if row["individual_id"] in seen_individuals:
            raise RuntimeError(f"More than one experimental head for individual {row['individual_id']}")
        if row["capitulum_id"] in seen_heads:
            raise RuntimeError(f"Duplicate capitulum_id {row['capitulum_id']}")
        seen_individuals.add(row["individual_id"])
        seen_heads.add(row["capitulum_id"])
        if not _is_true(row["taxon_identity_confirmed"]):
            raise RuntimeError(f"Taxon identity is not confirmed for {row['capitulum_id']}")
        if not _is_true(row["live_state_confirmed"]):
            raise RuntimeError(f"Live state is not confirmed for {row['capitulum_id']}")
        if row["phyllary_posture_class"] != "appressed":
            raise RuntimeError(f"Non-appressed head is ineligible: {row['capitulum_id']}")
        if row["natural_stickiness_state"] != "nonsticky_or_nearly_nonsticky":
            raise RuntimeError(f"Natural stickiness state mismatch: {row['capitulum_id']}")
        for key, expected in expected_records.items():
            if row[key] != expected:
                raise RuntimeError(f"{row['capitulum_id']}: {key} does not match authorization")
        by_pair[row["pair_id"]].append(row)

    if len(by_pair) != TARGET_PAIRS:
        raise RuntimeError(f"Pilot v1 requires exactly {TARGET_PAIRS} pairs; found {len(by_pair)}")
    match_fields = [
        "pilot_id",
        "site_id",
        "population_id",
        "observation_date_local",
        "phenological_stage",
        "capitulum_diameter_bin",
        "baseline_damage_bin",
    ]
    for pair_id, pair in by_pair.items():
        if len(pair) != 2:
            raise RuntimeError(f"Pair {pair_id} must contain exactly two heads")
        for field in match_fields:
            if len({row[field] for row in pair}) != 1:
                raise RuntimeError(f"Pair {pair_id} is not matched on {field}")
    return dict(by_pair)


def allocate(rows: list[dict[str, str]], authorization: dict) -> tuple[list[dict[str, str]], dict]:
    validate_authorization(authorization)
    by_pair = validate_rows(rows, authorization)
    assigned: list[dict[str, str]] = []
    for pair_id in sorted(by_pair):
        pair = sorted(by_pair[pair_id], key=lambda row: row["capitulum_id"])
        digest = hashlib.sha256(f"{FROZEN_SEED}|{pair_id}".encode("utf-8")).hexdigest()
        active_index = int(digest, 16) % 2
        for index, row in enumerate(pair):
            mate = pair[1 - index]
            assignment = "access_proxy" if index == active_index else "sham"
            assigned.append(
                {
                    "pilot_id": row["pilot_id"],
                    "site_id": row["site_id"],
                    "population_id": row["population_id"],
                    "pair_id": pair_id,
                    "individual_id": row["individual_id"],
                    "capitulum_id": row["capitulum_id"],
                    "matched_individual_id": mate["individual_id"],
                    "matched_capitulum_id": mate["capitulum_id"],
                    "assignment": assignment,
                    "randomization_seed": FROZEN_SEED,
                    "randomization_method": "sha256_seed_pair_id_within_predeclared_two_individual_pair",
                    "assignment_hash": digest,
                    "authorization_record_id": authorization["authorization_record_id"],
                    "device_qualification_record_id": authorization["device_qualification_record_id"],
                    "device_id": authorization["device_id"],
                    "material_lot": authorization["material_lot"],
                    "target_access_gap_mm": str(authorization["frozen_target_access_gap_mm"]),
                    "assignment_datetime_local": "",
                    "treatment_attempted": "",
                    "handling_duration_seconds": "",
                    "achieved_access_gap_mm": "",
                    "pre_head_orientation_deg": row.get("natural_head_orientation_deg", ""),
                    "post_head_orientation_deg": "",
                    "device_retained": "",
                    "floret_or_reproductive_contact": "",
                    "tissue_injury": "",
                    "treatment_integrity": "",
                    "attrition_reason": "",
                    "notes": "generated after all v1 authorization and eligibility gates passed",
                }
            )
    summary = {
        "protocol_version": PROTOCOL_VERSION,
        "randomization_seed": FROZEN_SEED,
        "authorization_record_id": authorization["authorization_record_id"],
        "pair_count": len(by_pair),
        "assigned_head_count": len(assigned),
        "arm_counts": {
            arm: sum(row["assignment"] == arm for row in assigned)
            for arm in ["access_proxy", "sham"]
        },
        "one_head_per_individual": len({row["individual_id"] for row in assigned}) == len(assigned),
        "claim_boundary": "Allocation only. Passing authorization and balance checks does not establish safe manipulation, biological efficacy or adaptation.",
    }
    return assigned, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("eligible", type=Path)
    parser.add_argument("authorization", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    rows = read_eligible(args.eligible)
    authorization = json.loads(args.authorization.read_text(encoding="utf-8"))
    assigned, summary = allocate(rows, authorization)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(assigned)
    args.output.with_suffix(args.output.suffix + ".summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
