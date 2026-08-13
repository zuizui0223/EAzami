#!/usr/bin/env python3
"""Integrate the four accepted Japan-origin topology sensitivities.

The gate combines BWA/BLASTx mapping and concatenated/ASTRAL tree methods. It
classifies monophyly without converting it into a colonisation-direction claim,
and promotes only sister-neighbour candidates stable in every scenario.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Mapping, Sequence


EXPECTED_SCENARIOS = {
    "bwa_concat": ("bwa", "concat"),
    "bwa_astral": ("bwa", "astral"),
    "blastx_concat": ("blastx", "concat"),
    "blastx_astral": ("blastx", "astral"),
}
EXPECTED_FOCAL_GROUPS = {
    "main_japanese_radiation",
    "arenicola",
    "Cirsium dipsacolepis",
    "Cirsium lineare",
}
SCENARIO_FIELDS = (
    "scenario_id",
    "mapping_method",
    "tree_method",
    "interpretation_json",
    "candidate_table",
)
CANDIDATE_FIELDS = (
    "focal_group",
    "neighbourhood_kind",
    "candidate_taxon",
    "region",
    "source_study",
    "tip_count",
    "tip_ids",
    "name_review_required",
    "sampling_priority_if_public_data_remain_unresolved",
    "interpretation_limit",
)
STABLE_FIELDS = (
    "focal_group",
    "neighbourhood_kind",
    "candidate_taxon",
    "region",
    "source_study",
    "sampling_priority",
    "scenario_count",
    "scenario_tip_ids",
    "name_review_required",
    "name_review_status",
    "name_review_evidence_locator",
    "promotion_eligible",
    "interpretation_limit",
)


def clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path, expected: Sequence[str] | None = None) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        observed = tuple(reader.fieldnames or ())
        if expected is not None and observed != tuple(expected):
            raise ValueError(
                f"{path}: unexpected header. Expected {tuple(expected)}, observed {observed}"
            )
        rows = [
            {key: clean(value) for key, value in row.items()}
            for row in reader
            if any(clean(value) for value in row.values())
        ]
    return rows


def resolve_path(base: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else base / path


def monophyly_classification(values: Sequence[bool]) -> str:
    if all(values):
        return "supported_monophyletic"
    if not any(values):
        return "rejected_monophyly"
    return "unresolved_sensitivity_conflict"


def stable_classification(values: Sequence[str]) -> str:
    unique = {clean(value) for value in values}
    return next(iter(unique)) if len(unique) == 1 else "unresolved_sensitivity_conflict"


def candidate_key(row: Mapping[str, str]) -> tuple[str, ...]:
    return (
        row["focal_group"],
        row["neighbourhood_kind"],
        row["candidate_taxon"],
        row["region"],
    )


def load_name_review(path: Path | None) -> dict[tuple[str, str], dict[str, str]]:
    if path is None:
        return {}
    fields = ("candidate_taxon", "region", "review_status", "evidence_locator")
    rows = read_csv(path, fields)
    allowed = {"confirmed_source_label", "excluded_from_sampling", "unresolved"}
    out: dict[tuple[str, str], dict[str, str]] = {}
    for row_number, row in enumerate(rows, start=2):
        key = (row["candidate_taxon"], row["region"])
        if not all(key) or row["review_status"] not in allowed or not row["evidence_locator"]:
            raise ValueError(f"{path}:{row_number}: invalid name-review row")
        if key in out:
            raise ValueError(f"{path}:{row_number}: duplicate name-review key {key}")
        out[key] = row
    return out


def validate_interpretation(
    scenario_id: str,
    tree_method: str,
    result: Mapping[str, object],
) -> None:
    if result.get("contract_version") != "japan_origin_global_topology_interpretation_v2":
        raise ValueError(f"{scenario_id}: unexpected topology interpretation contract")
    if result.get("tree_artifact_acceptance_verified") is not True:
        raise ValueError(f"{scenario_id}: tree artifact acceptance was not verified")
    tree_hash = clean(result.get("tree_sha256"))
    if not re.fullmatch(r"[0-9a-f]{64}", tree_hash):
        raise ValueError(f"{scenario_id}: invalid tree SHA256")
    if result.get("focal_public_individual_count") != 294:
        raise ValueError(f"{scenario_id}: expected 294 deduplicated biological individuals")
    expected_unit = "individual_tip" if tree_method == "concat" else "source_label_tip"
    if result.get("analysis_unit") != expected_unit:
        raise ValueError(
            f"{scenario_id}: {tree_method} requires analysis_unit={expected_unit!r}"
        )
    for field in (
        "dispersal_direction_inferred",
        "direct_ancestry_inferred",
        "introgression_inferred",
        "new_china_sampling_freeze_allowed",
    ):
        if result.get(field) is not False:
            raise ValueError(f"{scenario_id}: upstream result must keep {field}=false")
    groups = result.get("group_statistics")
    required_groups = {
        "main_japanese_radiation",
        "all_public_japan_region_tips",
        "arenicola",
        "Cirsium brevicaule",
        "Cirsium irumtiense",
    }
    if not isinstance(groups, dict) or not required_groups <= set(groups):
        raise ValueError(f"{scenario_id}: group statistics are incomplete")
    for group in required_groups:
        if not isinstance(groups[group].get("monophyletic"), bool):
            raise ValueError(f"{scenario_id}: {group} monophyly is not boolean")
    exceptions = result.get("published_exception_relationships")
    if not isinstance(exceptions, dict) or not {
        "Cirsium dipsacolepis", "Cirsium lineare"
    } <= set(exceptions):
        raise ValueError(f"{scenario_id}: separate-invasion anchor states are incomplete")


def integrate(
    scenarios_path: Path,
    name_review_path: Path | None = None,
) -> tuple[dict[str, object], list[dict[str, str]]]:
    scenario_rows = read_csv(scenarios_path, SCENARIO_FIELDS)
    observed_ids = [row["scenario_id"] for row in scenario_rows]
    if len(observed_ids) != len(set(observed_ids)):
        raise ValueError("scenario_id values must be unique")
    if set(observed_ids) != set(EXPECTED_SCENARIOS):
        raise ValueError(
            f"four-scenario inventory mismatch: expected {sorted(EXPECTED_SCENARIOS)}, "
            f"observed {sorted(observed_ids)}"
        )

    base = scenarios_path.parent
    results: dict[str, dict[str, object]] = {}
    candidates: dict[str, dict[tuple[str, ...], dict[str, str]]] = {}
    provenance: dict[str, dict[str, str]] = {}
    for row in scenario_rows:
        scenario_id = row["scenario_id"]
        expected_mapping, expected_tree = EXPECTED_SCENARIOS[scenario_id]
        if (row["mapping_method"], row["tree_method"]) != (
            expected_mapping,
            expected_tree,
        ):
            raise ValueError(f"{scenario_id}: mapping/tree method mismatch")
        result_path = resolve_path(base, row["interpretation_json"])
        candidate_path = resolve_path(base, row["candidate_table"])
        result = json.loads(result_path.read_text(encoding="utf-8"))
        validate_interpretation(scenario_id, expected_tree, result)
        rows = read_csv(candidate_path, CANDIDATE_FIELDS)
        if len(rows) != result.get("candidate_row_count"):
            raise ValueError(f"{scenario_id}: candidate row count does not match JSON")
        by_key: dict[tuple[str, ...], dict[str, str]] = {}
        for candidate in rows:
            key = candidate_key(candidate)
            if key in by_key:
                raise ValueError(f"{scenario_id}: duplicate candidate key {key}")
            if candidate["name_review_required"] not in {"true", "false"}:
                raise ValueError(f"{scenario_id}: invalid name_review_required")
            by_key[key] = candidate
        results[scenario_id] = result
        candidates[scenario_id] = by_key
        provenance[scenario_id] = {
            "mapping_method": expected_mapping,
            "tree_method": expected_tree,
            "tree_sha256": clean(result["tree_sha256"]),
            "interpretation_sha256": sha256(result_path),
            "candidate_table_sha256": sha256(candidate_path),
        }

    scenario_order = list(EXPECTED_SCENARIOS)
    common_keys = set.intersection(*(set(candidates[item]) for item in scenario_order))
    common_keys = {
        key for key in common_keys if key[1] == "immediate_sibling_branch"
    }
    name_reviews = load_name_review(name_review_path)
    stable_rows: list[dict[str, str]] = []
    for key in sorted(common_keys):
        scenario_candidates = [candidates[item][key] for item in scenario_order]
        review_required = any(row["name_review_required"] == "true" for row in scenario_candidates)
        review = name_reviews.get((key[2], key[3]), {}) if review_required else {}
        review_status = clean(review.get("review_status")) if review_required else "not_required"
        evidence_locator = clean(review.get("evidence_locator"))
        priorities = {
            row["sampling_priority_if_public_data_remain_unresolved"]
            for row in scenario_candidates
        }
        if len(priorities) != 1:
            raise ValueError(f"stable candidate priority drift for {key}")
        eligible = not review_required or review_status == "confirmed_source_label"
        if review_status == "excluded_from_sampling":
            eligible = False
        stable_rows.append({
            "focal_group": key[0],
            "neighbourhood_kind": key[1],
            "candidate_taxon": key[2],
            "region": key[3],
            "source_study": "|".join(sorted({
                study
                for row in scenario_candidates
                for study in row["source_study"].split("|")
                if study
            })),
            "sampling_priority": next(iter(priorities)),
            "scenario_count": "4",
            "scenario_tip_ids": ";".join(
                f"{scenario_id}:{candidates[scenario_id][key]['tip_ids']}"
                for scenario_id in scenario_order
            ),
            "name_review_required": str(review_required).lower(),
            "name_review_status": review_status or "unresolved",
            "name_review_evidence_locator": evidence_locator,
            "promotion_eligible": str(eligible).lower(),
            "interpretation_limit": (
                "Stable topological sister neighbourhood across four sensitivities; "
                "not dispersal direction, direct ancestry or introgression."
            ),
        })

    def group_values(group: str) -> list[bool]:
        return [
            bool(results[item]["group_statistics"][group]["monophyletic"])
            for item in scenario_order
        ]

    main_class = monophyly_classification(group_values("main_japanese_radiation"))
    all_japan_class = monophyly_classification(group_values("all_public_japan_region_tips"))
    aren_class = monophyly_classification(group_values("arenicola"))
    brev_class = monophyly_classification(group_values("Cirsium brevicaule"))
    irum_class = monophyly_classification(group_values("Cirsium irumtiense"))
    aren_relation = stable_classification([
        clean(results[item]["arenicola_relative_to_main_radiation"])
        for item in scenario_order
    ])
    exception_consensus = {
        taxon: stable_classification([
            clean(results[item]["published_exception_relationships"][taxon])
            for item in scenario_order
        ])
        for taxon in ("Cirsium dipsacolepis", "Cirsium lineare")
    }
    stable_groups = sorted({row["focal_group"] for row in stable_rows})
    eligible_groups = sorted({
        row["focal_group"] for row in stable_rows if row["promotion_eligible"] == "true"
    })
    unresolved_reviews = sum(
        row["name_review_required"] == "true"
        and row["name_review_status"] not in {
            "confirmed_source_label", "excluded_from_sampling"
        }
        for row in stable_rows
    )
    decision_ready = (
        main_class != "unresolved_sensitivity_conflict"
        and all_japan_class != "unresolved_sensitivity_conflict"
        and aren_relation != "unresolved_sensitivity_conflict"
        and all(value != "unresolved_sensitivity_conflict" for value in exception_consensus.values())
        and EXPECTED_FOCAL_GROUPS <= set(eligible_groups)
        and unresolved_reviews == 0
    )

    blockers = []
    if main_class == "unresolved_sensitivity_conflict":
        blockers.append("main Japanese radiation monophyly differs among sensitivities")
    if all_japan_class == "unresolved_sensitivity_conflict":
        blockers.append("all sampled Japanese-lineage monophyly differs among sensitivities")
    if aren_relation == "unresolved_sensitivity_conflict":
        blockers.append("Arenicola placement differs among sensitivities")
    for taxon, value in exception_consensus.items():
        if value == "unresolved_sensitivity_conflict":
            blockers.append(f"{taxon} relationship to the main radiation is unstable")
    missing_groups = sorted(EXPECTED_FOCAL_GROUPS - set(eligible_groups))
    if missing_groups:
        blockers.append("no four-scenario stable sister neighbourhood for " + "|".join(missing_groups))
    if unresolved_reviews:
        blockers.append(f"{unresolved_reviews} stable candidate name reviews remain unresolved")

    summary = {
        "contract_version": "japan_origin_topology_sensitivity_acceptance_v1",
        "panel_contract_version": "japan_origin_global_public_panel_v2",
        "deduplicated_biological_individuals": 294,
        "public_runs": 295,
        "scenario_count": 4,
        "scenario_provenance": provenance,
        "main_japanese_radiation_monophyly": main_class,
        "all_sampled_japanese_lineages_monophyly": all_japan_class,
        "arenicola_monophyly": aren_class,
        "Cirsium_brevicaule_monophyly": brev_class,
        "Cirsium_irumtiense_monophyly": irum_class,
        "arenicola_relative_to_main_radiation": aren_relation,
        "published_exception_relationships": exception_consensus,
        "stable_sister_candidate_rows": len(stable_rows),
        "promotion_eligible_stable_candidate_rows": sum(
            row["promotion_eligible"] == "true" for row in stable_rows
        ),
        "stable_neighbourhood_focal_groups": stable_groups,
        "promotion_eligible_focal_groups": eligible_groups,
        "unresolved_stable_candidate_name_reviews": unresolved_reviews,
        "sensitivity_decision_ready": decision_ready,
        "stable_public_gap_conversion_allowed": decision_ready,
        "new_china_sampling_freeze_allowed": decision_ready,
        "sampling_freeze_blockers": blockers,
        "single_colonisation_inferred": False,
        "dispersal_direction_inferred": False,
        "direct_ancestry_inferred": False,
        "introgression_inferred": False,
        "claim_limit": (
            "Four-scenario monophyly and stable-neighbourhood agreement can prioritize "
            "sampling but cannot alone establish one colonisation, dispersal direction, "
            "direct ancestry or absence of introgression."
        ),
    }
    return summary, stable_rows


def write_csv(path: Path, rows: Sequence[Mapping[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(STABLE_FIELDS))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenarios", type=Path, required=True)
    parser.add_argument("--name-review", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--stable-candidates", type=Path, required=True)
    args = parser.parse_args()
    summary, rows = integrate(args.scenarios, args.name_review)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    write_csv(args.stable_candidates, rows)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
