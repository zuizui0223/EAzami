#!/usr/bin/env python3
"""Fail-closed validation of the standalone Chapter 2 diversity-depth contract."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "data" / "evidence" / "chapter2_diversity_depth_contract_v1.json"
INVENTORY_PATH = ROOT / "data" / "evidence" / "chapter2_diversity_depth_inventory_v1.csv"
DESIGN_PATH = ROOT / "docs" / "chapter2" / "DIVERSITY_DEPTH_STANDALONE_V1.md"

ALLOWED_CLASSES = {"directly_usable", "reanalysis_needed", "design_only", "new_data_needed"}
EXPECTED_CLASSES = {
    "I01": "directly_usable",
    "I02": "reanalysis_needed",
    "I03": "directly_usable",
    "I04": "directly_usable",
    "I05": "directly_usable",
    "I06": "reanalysis_needed",
    "I07": "reanalysis_needed",
    "I08": "directly_usable",
    "I09": "directly_usable",
    "I10": "directly_usable",
    "I11": "reanalysis_needed",
    "I12": "directly_usable",
    "I13": "directly_usable",
    "I14": "design_only",
    "I15": "directly_usable",
    "I16": "design_only",
    "I17": "design_only",
}
REQUIRED_NATIVE_FIELDS = {
    "record_id",
    "paper_japan_member_id",
    "taxon_concept",
    "trait_id",
    "value",
    "unit",
    "source_type",
    "source_locator",
    "rights_status",
    "measurement_protocol",
    "admission_status",
    "exclusion_reason",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_inventory() -> list[dict[str, str]]:
    rows = read_rows(INVENTORY_PATH)
    ids = [row["item_id"] for row in rows]
    if ids != [f"I{i:02d}" for i in range(1, 18)]:
        raise AssertionError(f"inventory must contain ordered I01-I17 exactly, got {ids}")
    for row in rows:
        item_id = row["item_id"]
        classification = row["classification"]
        if classification not in ALLOWED_CLASSES:
            raise AssertionError(f"invalid classification for {item_id}: {classification}")
        if classification != EXPECTED_CLASSES[item_id]:
            raise AssertionError(f"classification drift for {item_id}: {classification}")
        for field in ("implementation_status", "evidence_paths", "next_gate", "claim_boundary"):
            if not row[field].strip():
                raise AssertionError(f"{item_id} has empty {field}")
        for raw_path in row["evidence_paths"].split(";"):
            path = ROOT / raw_path.strip()
            if not path.exists() or path.stat().st_size == 0:
                raise AssertionError(f"{item_id} evidence missing or empty: {raw_path.strip()}")
    return rows


def validate_native_input(contract: dict) -> str:
    native = contract["independent_continuous_input"]
    if set(native["required_fields"]) != REQUIRED_NATIVE_FIELDS:
        raise AssertionError("EAzami-native registry field contract drift")
    native_path = ROOT / native["required_path"]
    status = contract["current_submission_status"]
    if status == "STOP_STANDALONE_CONTINUOUS_INPUT_NOT_ADMITTED":
        if native["exists_at_freeze"] is not False:
            raise AssertionError("STOP contract must record exists_at_freeze=false")
        if native_path.exists():
            raise AssertionError(
                "native registry now exists; review provenance and deliberately advance or retain the STOP contract"
            )
        return "STOP_preserved"
    if status != "READY_STANDALONE_INPUTS_ADMITTED":
        raise AssertionError(f"unknown submission status: {status}")
    if not native_path.exists():
        raise AssertionError("READY status requires the EAzami-native continuous registry")
    rows = read_rows(native_path)
    if not rows or not REQUIRED_NATIVE_FIELDS.issubset(rows[0]):
        raise AssertionError("EAzami-native registry is empty or lacks required fields")
    forbidden = tuple(x.lower() for x in native["forbidden_provenance_for_primary_analysis"])
    for index, row in enumerate(rows, start=2):
        joined = " ".join(row.values()).lower()
        if any(token in joined for token in forbidden):
            raise AssertionError(f"forbidden primary provenance at native-registry row {index}")
    return "READY_admitted"


def validate_independence_boundary(contract: dict) -> None:
    legacy_bridge = (
        ROOT
        / "data"
        / "evidence"
        / "chapter2_time_axis_compute"
        / "source_japan38_continuous_trait_bridge_v1.csv"
    )
    if not legacy_bridge.exists():
        raise AssertionError("legacy continuous bridge must be retained for audit provenance")
    continuous_script = (ROOT / "analysis" / "run_japan38_all_continuous_history_v1.py").read_text(
        encoding="utf-8"
    )
    if "frozen Azami" not in continuous_script:
        raise AssertionError("continuous-history dependency is no longer explicit")
    if contract["legacy_pr126_package"]["status"] != "frozen_audit_snapshot_not_current_standalone_submission":
        raise AssertionError("legacy PR126 package was silently promoted")
    if "Azami observational handoff as Result 1" not in contract["legacy_pr126_package"]["remove_from_active_story"]:
        raise AssertionError("Azami handoff removal rule missing")


def validate_frozen_results() -> None:
    scaffold = load_json(ROOT / "data" / "evidence" / "japan38_comp1061_primary_tree_acceptance_v1.json")
    if scaffold["bootstrap_replicates"] != 1000 or scaffold["branch_length_semantics"] != "substitutions/site; not absolute time":
        raise AssertionError("Comp1061 scaffold or time boundary drift")

    sticky = load_json(ROOT / "data" / "evidence" / "jpn24_stickiness_extension_parsimony_v1.json")
    if sticky["stickiness"]["resolved_concepts_after"] != 13:
        raise AssertionError("stickiness coverage drift")
    if {sticky["stickiness"]["ufboot1000_steps_min"], sticky["stickiness"]["ufboot1000_steps_max"]} != {5}:
        raise AssertionError("stickiness recurrence drift")

    pgls = load_json(ROOT / "data" / "evidence" / "fdt4_eastasia_pgls_recovered_diagnostic_v1.json")
    primary = pgls["primary_min_n_10"]
    if primary["n_taxa"] != 9:
        raise AssertionError("East-Asia PGLS primary panel drift")
    bio15 = primary["axis_ranges_across_six_topologies"]["chelsa_bio15"]
    if bio15["p_min"] < 0.05 or bio15["p_max"] < 0.05:
        raise AssertionError("primary BIO15 screen was silently promoted")

    branchwise = load_json(ROOT / "data" / "evidence" / "fdt4_branchwise_niche_transition_concordance_v1.json")
    for axis in ("chelsa_bio15", "chelsa_bio01"):
        result = branchwise["results_across_six_topologies"][axis]
        if result["permutation_p_min"] < 0.05:
            raise AssertionError(f"unsupported branchwise result promoted for {axis}")


def validate_design_document(contract: dict) -> None:
    text = DESIGN_PATH.read_text(encoding="utf-8")
    required = [
        "diversity breadth -> diversity depth",
        "Central question",
        "Standalone EAzami analysis pipeline",
        "Repository-wide inventory",
        "Analyses runnable now",
        "Missing analyses for historical trait-environment recurrence",
        "PR #126 disposition",
        "Recurrence and localization are distinct dimensions",
        "submission authorization withheld",
    ]
    missing = [needle for needle in required if needle not in text]
    if missing:
        raise AssertionError(f"standalone design document missing: {missing}")
    if contract["claim_ceiling"] not in text:
        raise AssertionError("machine-readable and narrative claim ceilings differ")


def main() -> int:
    for path in (CONTRACT_PATH, INVENTORY_PATH, DESIGN_PATH):
        if not path.exists() or path.stat().st_size == 0:
            raise AssertionError(f"missing or empty standalone Chapter 2 file: {path.relative_to(ROOT)}")
    contract = load_json(CONTRACT_PATH)
    if contract["contract_version"] != "chapter2_diversity_depth_contract_v1":
        raise AssertionError("contract version drift")
    inventory = validate_inventory()
    gate = validate_native_input(contract)
    validate_independence_boundary(contract)
    validate_frozen_results()
    validate_design_document(contract)
    print("chapter2_diversity_depth_contract_valid=true")
    print(f"inventory_rows={len(inventory)}")
    print(f"standalone_continuous_gate={gate}")
    print(f"submission_status={contract['current_submission_status']}")
    print("legacy_pr126_package=frozen_audit_snapshot")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
