#!/usr/bin/env python3
"""Fail-closed validation of the standalone Chapter 2 diversity-depth contract."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "data" / "evidence" / "chapter2_diversity_depth_contract_v1.json"
INVENTORY_PATH = ROOT / "data" / "evidence" / "chapter2_diversity_depth_inventory_v1.csv"
DESIGN_PATH = ROOT / "docs" / "chapter2" / "DIVERSITY_DEPTH_STANDALONE_V1.md"
SUMMARY_PATH = (
    ROOT / "data" / "evidence" / "chapter2_eazami_native_continuous_trait_registry_summary_v1.json"
)
NATIVE_HISTORY_DESIGN_PATH = (
    ROOT / "data" / "evidence" / "chapter2_eazami_native_continuous_history_design_v1.json"
)
NATIVE_HISTORY_RESULT_PATH = (
    ROOT / "data" / "evidence" / "chapter2_eazami_native_continuous_history_diagnostic_v1.json"
)
NATIVE_HISTORY_CSV_PATH = (
    ROOT
    / "data"
    / "evidence"
    / "chapter2_eazami_native_continuous_history_diagnostic_by_topology_v1.csv"
)
RADSEQ_BRIDGE_PATH = (
    ROOT / "data" / "evidence" / "chapter2_to_chapter3_radseq_bridge_v1.json"
)
RADSEQ_PRIORITY_PATH = (
    ROOT / "data" / "evidence" / "chapter2_to_chapter3_sampling_priorities_v1.csv"
)
MANUSCRIPT_PATH = ROOT / "docs" / "chapter2" / "MANUSCRIPT_JEB_V4.md"
CORE_RECOVERY_PATH = ROOT / "data" / "evidence" / "chapter2_core_result_recovery_v1.csv"
CORE_POSITION_PATH = ROOT / "docs" / "chapter2" / "CHAPTER2_CORE_RESULT_RECOVERY_V1.md"
RESOLUTION_CLASS_PATH = (
    ROOT / "data" / "evidence" / "chapter2_resolution_classification_v1.csv"
)
META_SIM_AUDIT_PATH = (
    ROOT / "data" / "evidence" / "meta_simulation_resolution_audit_v1.csv"
)
RESOLUTION_SPLIT_PATH = (
    ROOT / "docs" / "chapter2" / "CHAPTER2_RESOLUTION_AWARE_EVIDENCE_SPLIT_V1.md"
)
META_SIM_DISPOSITION_PATH = (
    ROOT / "docs" / "chapter2" / "META_SIM_DISPOSITION_V1.md"
)
ANALYSIS_DISPOSITION_PATH = (
    ROOT / "data" / "evidence" / "chapter2_analysis_disposition_v1.csv"
)
RELATIVE_DEPTH_PATH = (
    ROOT / "data" / "evidence" / "japan38_relative_event_depth_v1.json"
)

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
EXPECTED_CORE_RESULT_IDS = [
    "M01", "M02", "M03", "M04", "M05",
    "S01", "S02", "S03", "S04",
    "X01", "X02", "X03", "X04",
]
EXPECTED_MAIN_ROLES = {
    "M01": "MAIN_CONTEXT",
    "M02": "MAIN_BIOLOGICAL_RESULT",
    "M03": "MAIN_BIOLOGICAL_RESULT",
    "M04": "MAIN_INFERENCE_RESULT",
    "M05": "MAIN_BOUNDARY",
}
EXPECTED_RESOLUTION_IDS = [f"D{i:02d}" for i in range(1, 35)]
EXPECTED_META_SIM_IDS = [f"M{i:02d}" for i in range(1, 13)] + [
    f"S{i:02d}" for i in range(1, 11)
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_text_sha256(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()


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
    if status not in {
        "STOP_STANDALONE_CONTINUOUS_COVERAGE_INSUFFICIENT",
        "READY_STANDALONE_INPUTS_ADMITTED",
        "HOLD_JEB_PACKAGE_REBUILD_ONLY",
    }:
        raise AssertionError(f"unknown submission status: {status}")
    if native["exists_at_freeze"] is not True:
        raise AssertionError("admitted native registry must record exists_at_freeze=true")
    if not native_path.exists():
        raise AssertionError("admitted status requires the EAzami-native continuous registry")
    rows = read_rows(native_path)
    if not rows or not REQUIRED_NATIVE_FIELDS.issubset(rows[0]):
        raise AssertionError("EAzami-native registry is empty or lacks required fields")
    record_ids = [row["record_id"] for row in rows]
    if len(record_ids) != len(set(record_ids)):
        raise AssertionError("EAzami-native registry contains duplicate record_id values")
    forbidden = tuple(x.lower() for x in native["forbidden_provenance_for_primary_analysis"])
    for index, row in enumerate(rows, start=2):
        joined = " ".join(row.values()).lower()
        if any(token in joined for token in forbidden):
            raise AssertionError(f"forbidden primary provenance at native-registry row {index}")
        if row["admission_status"] == "admitted_comparable_scalar":
            try:
                float(row["value"])
            except ValueError as exc:
                raise AssertionError(f"non-scalar value admitted at native-registry row {index}") from exc
        elif row["admission_status"] == "context_only_range_not_scalar":
            if row["exclusion_reason"] != "range_not_collapsed_to_midpoint":
                raise AssertionError(f"range exclusion contract drift at native-registry row {index}")
        else:
            raise AssertionError(f"unknown admission_status at native-registry row {index}")

    if not SUMMARY_PATH.exists():
        raise AssertionError("admitted native registry requires its frozen summary")
    summary = load_json(SUMMARY_PATH)
    if contract.get("frozen_text_hash_semantics") != (
        "SHA-256 of UTF-8 text after CRLF-to-LF normalization; "
        "binary artifacts retain exact-byte SHA-256"
    ):
        raise AssertionError("frozen text hash semantics are not explicit")
    digest = canonical_text_sha256(native_path)
    if summary["registry_sha256"] != digest or native.get("registry_sha256") != digest:
        raise AssertionError("native registry hash differs from summary or contract")
    expected = {
        "registry_records": 45,
        "admitted_comparable_scalar_records": 35,
        "context_only_range_records": 10,
        "japan38_admitted_scalar_records": 0,
        "japan38_admitted_scalar_taxa": 0,
    }
    for field, value in expected.items():
        if summary[field] != value:
            raise AssertionError(f"native registry summary drift for {field}: {summary[field]}")
    if summary["seven_taxon_direct_panel_traits"] != [
        "measured_capitulum_length_cm",
        "measured_capitulum_width_cm",
        "phyllary_length_cm",
        "phyllary_protrusion_mm",
    ]:
        raise AssertionError("seven-taxon direct-panel trait set drift")

    if status == "STOP_STANDALONE_CONTINUOUS_COVERAGE_INSUFFICIENT":
        if summary["registry_gate"] != "ADMITTED_EAZAMI_NATIVE_VALUES":
            raise AssertionError("coverage STOP requires an admitted native registry")
        if summary["japan38_history_gate"] != "NOT_EVALUABLE_ZERO_ADMITTED_SCALAR_JAPAN38_TIPS":
            raise AssertionError("coverage STOP requires zero admitted Japan38 scalar tips")
        return "ADMITTED_coverage_insufficient"
    if status == "HOLD_JEB_PACKAGE_REBUILD_ONLY":
        if contract.get("chapter2_scientific_status") != "COMPLETE_EXISTING_PUBLIC_HISTORY_CORE":
            raise AssertionError("submission-package hold must not demote the scientific core")
        if native.get("chapter2_role") != (
            "bounded independent coverage and small-panel retention diagnostic; not a completion gate"
        ):
            raise AssertionError("native continuous panel was silently restored as a completion gate")
        if summary["japan38_history_gate"] != "NOT_EVALUABLE_ZERO_ADMITTED_SCALAR_JAPAN38_TIPS":
            raise AssertionError("bounded native panel must retain the zero-Japan38 coverage result")
        return "ADMITTED_bounded_not_completion_gate"
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


def validate_native_history_diagnostic() -> None:
    for path in (NATIVE_HISTORY_DESIGN_PATH, NATIVE_HISTORY_RESULT_PATH, NATIVE_HISTORY_CSV_PATH):
        if not path.exists() or path.stat().st_size == 0:
            raise AssertionError(f"missing native continuous-history artifact: {path.relative_to(ROOT)}")
    design = load_json(NATIVE_HISTORY_DESIGN_PATH)
    result = load_json(NATIVE_HISTORY_RESULT_PATH)
    if len(design["fixed_taxa"]) != 7 or len(design["fixed_traits"]) != 4:
        raise AssertionError("native history frozen panel drift")
    if design["null"]["exact_permutations"] != 5040:
        raise AssertionError("native history exact-null drift")
    if result["design_sha256"] != canonical_text_sha256(NATIVE_HISTORY_DESIGN_PATH):
        raise AssertionError("native history design hash drift")
    if result["topology_count"] != 6 or result["exact_permutations_per_trait_topology"] != 5040:
        raise AssertionError("native history topology or permutation count drift")
    if result["supported_traits"] or result["panel_decision"] != "not_supported_no_topology_robust_retention_detected":
        raise AssertionError("unsupported native continuous history was promoted")
    protrusion = result["by_trait"]["phyllary_protrusion_mm"]
    if protrusion["rho_min"] <= 0 or protrusion["positive_tail_bh_q_min"] < 0.05:
        raise AssertionError("phyllary-protrusion bounded diagnostic drift")
    if result["japan38_transfer"] != "PROHIBITED_ZERO_ADMITTED_SCALAR_JAPAN38_TIPS":
        raise AssertionError("native diagnostic was transferred to Japan38")
    rows = read_rows(NATIVE_HISTORY_CSV_PATH)
    if len(rows) != 24:
        raise AssertionError("native history result table must contain 4 traits x 6 topologies")


def validate_chapter2_to_chapter3_bridge(contract: dict) -> list[dict[str, str]]:
    if not RADSEQ_BRIDGE_PATH.exists() or not RADSEQ_PRIORITY_PATH.exists():
        raise AssertionError("Chapter 2 to Chapter 3 RAD-seq bridge is incomplete")
    bridge = load_json(RADSEQ_BRIDGE_PATH)
    if bridge.get("contract_version") != "chapter2_to_chapter3_radseq_bridge_v1":
        raise AssertionError("RAD-seq bridge version drift")
    if bridge.get("chapter2_status") != "COMPLETE_EXISTING_PUBLIC_HISTORY_CORE":
        raise AssertionError("RAD-seq bridge made Chapter 2 scientifically incomplete")
    if bridge.get("dependency_direction") != (
        "chapter2_uncertainty_informs_chapter3_sampling; "
        "chapter3_is_not_required_to_make_chapter2_valid"
    ):
        raise AssertionError("Chapter 2/3 dependency direction drift")
    product = bridge["chapter3_sampling_product"]
    if "sensitivity phylogeny" not in product["name"]:
        raise AssertionError("Japan-wide RAD-seq product was promoted to an unconditional species tree")
    if not product["status_if_quality_gates_fail"].startswith("population-ancestry"):
        raise AssertionError("RAD-seq quality-gate failure is not fail closed")
    rights = bridge["rights_and_conservation_gate"]
    if rights.get("status") != "FAIL_CLOSED_NOT_AUTHORIZED_BY_THIS_CONTRACT":
        raise AssertionError("sampling bridge was mistaken for field authorization")
    if contract["chapter2_to_chapter3_bridge"]["own_radseq_required_for_chapter2"] is not False:
        raise AssertionError("own RAD-seq was made a Chapter 2 completion dependency")
    if contract["chapter2_to_chapter3_bridge"]["contract_path"] != str(
        RADSEQ_BRIDGE_PATH.relative_to(ROOT)
    ).replace("\\", "/"):
        raise AssertionError("contract points to the wrong RAD-seq bridge")

    rows = read_rows(RADSEQ_PRIORITY_PATH)
    if [row["priority_id"] for row in rows] != ["P01", "P02", "P03", "P04", "P05"]:
        raise AssertionError("sampling priorities must contain ordered P01-P05")
    required = {
        "priority_id", "rank", "trait_module", "focal_concepts", "chapter2_result",
        "remaining_history_discrimination", "chapter3_radseq_requirement",
        "linked_own_measurement", "predeclared_falsifier", "rights_conservation_gate",
        "chapter2_claim_boundary", "chapter3_claim_boundary", "evidence_paths",
    }
    if not rows or not required.issubset(rows[0]):
        raise AssertionError("sampling-priority schema drift")
    for expected_rank, row in enumerate(rows, start=1):
        if int(row["rank"]) != expected_rank:
            raise AssertionError(f"sampling rank drift for {row['priority_id']}")
        for field in required - {"priority_id", "rank"}:
            if not row[field].strip():
                raise AssertionError(f"{row['priority_id']} has empty {field}")
        for raw_path in row["evidence_paths"].split(";"):
            path = ROOT / raw_path.strip()
            if not path.exists() or path.stat().st_size == 0:
                raise AssertionError(
                    f"{row['priority_id']} evidence missing or empty: {raw_path.strip()}"
                )
    if (
        "JPN_06" not in rows[0]["focal_concepts"]
        or "JPN_15" not in rows[0]["focal_concepts"]
        or "0.995" not in rows[0]["chapter2_result"]
    ):
        raise AssertionError("JPN06/JPN15 stickiness discrimination is not priority 1")
    if "JPN_36" not in rows[1]["focal_concepts"] or "0.728" not in rows[1]["chapter2_result"]:
        raise AssertionError("JPN36 phyllary discrimination is not priority 2")
    return rows


def validate_frozen_results() -> None:
    scaffold = load_json(ROOT / "data" / "evidence" / "japan38_comp1061_primary_tree_acceptance_v1.json")
    if scaffold["bootstrap_replicates"] != 1000 or scaffold["branch_length_semantics"] != "substitutions/site; not absolute time":
        raise AssertionError("Comp1061 scaffold or time boundary drift")

    sticky = load_json(ROOT / "data" / "evidence" / "jpn24_stickiness_extension_parsimony_v1.json")
    if sticky["stickiness"]["resolved_concepts_after"] != 13:
        raise AssertionError("stickiness coverage drift")
    if {sticky["stickiness"]["ufboot1000_steps_min"], sticky["stickiness"]["ufboot1000_steps_max"]} != {5}:
        raise AssertionError("stickiness minimum-change drift")

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


def validate_core_result_recovery() -> list[dict[str, str]]:
    rows = read_rows(CORE_RECOVERY_PATH)
    ids = [row["result_id"] for row in rows]
    if ids != EXPECTED_CORE_RESULT_IDS:
        raise AssertionError(f"core-result ledger order or membership drift: {ids}")
    lookup = {row["result_id"]: row for row in rows}
    main = {rid: row["paper_role"] for rid, row in lookup.items() if rid.startswith("M")}
    if main != EXPECTED_MAIN_ROLES:
        raise AssertionError(f"active main-result selection drift: {main}")
    for row in rows:
        if not row["evidence_status"].startswith("COMPLETE_"):
            raise AssertionError(f"unfinished result entered recovery ledger: {row['result_id']}")
        for field in ("question", "headline_result", "allowed_interpretation", "claim_ceiling"):
            if not row[field].strip():
                raise AssertionError(f"{row['result_id']} has empty {field}")
        for raw_path in row["source_paths"].split(";"):
            path = ROOT / raw_path.strip()
            if not path.exists() or path.stat().st_size == 0:
                raise AssertionError(
                    f"{row['result_id']} source missing or empty: {raw_path.strip()}"
                )

    origin = load_json(ROOT / "data" / "evidence" / "japan_cirsium_origin_meta_analysis_v1.json")
    dominant = origin["dominant_main_radiation"]
    if dominant["japanese_species_sampled"] != 38 or dominant["species_in_main_radiation"] != 36:
        raise AssertionError("M01 dominant-radiation context drift")

    combos = load_json(ROOT / "data" / "evidence" / "japan38_authority_module_combinations_v1.json")
    if combos["n_dominant_seed_concepts"] != 20:
        raise AssertionError("M02 authority-covered dominant subset drift")
    if combos["n_dominant_orientation_stickiness_combinations"] != 4:
        raise AssertionError("M02 observed configuration count drift")
    allowed_orientation_labels = {
        "downward_or_nodding", "upward_or_ascending", "upward_or_erect",
    }
    allowed_stickiness_labels = {
        "nonsticky_or_nearly_nonsticky", "sticky",
    }
    harmonized = set()
    for item in combos["dominant_orientation_stickiness_combinations"]:
        orientation_label, stickiness_label = item.split(" + ", 1)
        if orientation_label not in allowed_orientation_labels:
            raise AssertionError(f"M02 unknown orientation label: {orientation_label}")
        if stickiness_label not in allowed_stickiness_labels:
            raise AssertionError(f"M02 unknown stickiness label: {stickiness_label}")
        orientation_state = "D" if orientation_label == "downward_or_nodding" else "U"
        stickiness_state = (
            "nonsticky" if stickiness_label == "nonsticky_or_nearly_nonsticky" else "sticky"
        )
        harmonized.add((orientation_state, stickiness_state))
    if harmonized != {("D", "nonsticky"), ("U", "nonsticky"), ("U", "sticky")}:
        raise AssertionError(f"M02 harmonized configuration set drift: {harmonized}")

    orientation = load_json(ROOT / "data" / "evidence" / "jpn34_orientation_extension_parsimony_v1.json")
    history = load_json(RELATIVE_DEPTH_PATH)
    sticky = load_json(ROOT / "data" / "evidence" / "jpn24_stickiness_extension_parsimony_v1.json")
    if orientation["orientation"]["resolved_concepts_after"] != 20:
        raise AssertionError("M03 orientation coverage drift")
    if orientation["orientation"]["ufboot1000_steps_min"] != 4 or orientation["orientation"]["ufboot1000_steps_max"] != 6:
        raise AssertionError("M03 orientation minimum-change drift")
    posture = history["ufboot1000_relative_event_depth"]["phyllary"][
        "metric_summaries"
    ]["minimum_steps"]
    if {posture["min"], posture["max"]} != {3.0}:
        raise AssertionError("M03 phyllary minimum-change drift")
    if {sticky["stickiness"]["ufboot1000_steps_min"], sticky["stickiness"]["ufboot1000_steps_max"]} != {5}:
        raise AssertionError("M03 stickiness minimum-change drift")

    ml = history["ml_relative_event_depth"]
    boot = history["ufboot1000_relative_event_depth"]
    if ml["orientation"]["forced_change_edges"]:
        raise AssertionError("M04 orientation forced-edge drift")
    def forced_fraction(trait: str, edge: str) -> float:
        values = {
            row["edge_id"]: row["fraction"]
            for row in boot[trait]["forced_change_edge_frequencies"]
        }
        return values[edge]
    if abs(forced_fraction("orientation", "JPN_36") - 0.227) > 1e-12:
        raise AssertionError("M04 orientation terminal fraction drift")
    if abs(forced_fraction("phyllary", "JPN_36") - 0.728) > 1e-12:
        raise AssertionError("M04 phyllary terminal fraction drift")
    if abs(forced_fraction("stickiness", "JPN_06") - 0.995) > 1e-12:
        raise AssertionError("M04 stickiness terminal fraction drift")
    stick_depth = ml["stickiness"]["mean_relative_lineage_depth_interval"]
    if any(abs(a - b) > 1e-12 for a, b in zip(stick_depth, [0.9428571428571428, 0.9542857142857143])):
        raise AssertionError("M04 stickiness relative lineage-depth drift")

    branch_overlap = load_json(
        ROOT / "data" / "evidence" / "chapter2_time_axis_compute"
        / "japan38_latest_module_transition_overlap_v2.json"
    )
    overlap = load_json(
        ROOT / "data" / "evidence" / "chapter2_time_axis_compute"
        / "japan38_latest_module_overlap_topology_sensitivity_v2.json"
    )
    dist = overlap["bootstrap_topology_sensitivity"]["pairwise_spearman_distributions"]
    expected_branch_rho = {
        "orientation__phyllary": 0.3622994652406417,
        "orientation__stickiness": 0.20188204398730714,
        "phyllary__stickiness": 0.08387096774193549,
    }
    expected_medians = {
        "orientation__phyllary": -0.059394365771196084,
        "orientation__stickiness": -0.387012001175683,
        "phyllary__stickiness": 0.18399015228406285,
    }
    expected_q05 = {
        "orientation__phyllary": -0.20588270079151355,
        "orientation__stickiness": -0.39198786339609276,
        "phyllary__stickiness": -0.07345437846675106,
    }
    for pair, expected in expected_medians.items():
        branch_rho = branch_overlap["pairwise_overlap"][pair][
            "spearman_transition_excess_over_branch_prior"
        ]
        if abs(branch_rho - expected_branch_rho[pair]) > 1e-12:
            raise AssertionError(f"M05 branch-aware overlap drift for {pair}")
        if abs(dist[pair]["median"] - expected) > 1e-12:
            raise AssertionError(f"M05 equal-branch overlap drift for {pair}")
        if abs(dist[pair]["q05"] - expected_q05[pair]) > 1e-12:
            raise AssertionError(f"M05 equal-branch fifth-percentile drift for {pair}")
        if not branch_rho > 0 or not dist[pair]["q05"] < 0:
            raise AssertionError(f"M05 cross-treatment robustness classification drift for {pair}")

    hmm2 = load_json(ROOT / "data" / "evidence" / "hmm2_population_aware_transition_test_v1.json")
    if hmm2["stage_A_state_compression"]["systems_exposing_W_C_multiplicity_hidden_by_one_P_tip"] != 4:
        raise AssertionError("S01 species-tip compression drift")
    stage_b = hmm2["stage_B_minimum_transition_count"]
    if stage_b["systems_with_morph_linked_nuclear_genealogy"] != 1:
        raise AssertionError("S01 morph-linked system count drift")
    if (stage_b["takaoense_species_tip_minimum"], stage_b["takaoense_population_sample_minimum"]) != (1, 2):
        raise AssertionError("S01 population-aware minimum-count drift")

    native = load_json(NATIVE_HISTORY_RESULT_PATH)
    if native["supported_traits"] or native["topology_count"] != 6:
        raise AssertionError("S02 direct continuous boundary drift")

    pgls = load_json(ROOT / "data" / "evidence" / "fdt4_eastasia_pgls_recovered_diagnostic_v1.json")
    bio15 = pgls["primary_min_n_10"]["axis_ranges_across_six_topologies"]["chelsa_bio15"]
    if bio15["p_min"] < 0.05 or bio15["p_max"] < 0.05:
        raise AssertionError("S03 primary ecological lead was promoted")

    cytotype = load_json(ROOT / "data" / "evidence" / "japan38_cytotype_trait_overlap_v1.json")
    if cytotype["n_source_backed_cytotype_concepts"] != 9:
        raise AssertionError("S04 cytotype coverage drift")

    position = CORE_POSITION_PATH.read_text(encoding="utf-8")
    required = [
        "COMPLETE_CONFIGURATION_DIVERSITY_AND_MINIMUM_CHANGE_CORE",
        "How many state changes are minimally required in the traits",
        "36 of 38 sampled Japanese concepts",
        "minimum-count stability",
        "relative lineage-depth",
        "event resolution",
        "five result groups only",
        "Capitulum configuration diversity, minimum change counts",
    ]
    missing = [needle for needle in required if needle not in position]
    if missing:
        raise AssertionError(f"core-result positioning document missing: {missing}")
    return rows


def validate_resolution_and_meta_sim_audit() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    disposition_ids = [row["analysis_id"] for row in read_rows(ANALYSIS_DISPOSITION_PATH)]
    resolution = read_rows(RESOLUTION_CLASS_PATH)
    resolution_ids = [row["analysis_id"] for row in resolution]
    if disposition_ids != EXPECTED_RESOLUTION_IDS or resolution_ids != disposition_ids:
        raise AssertionError(
            "resolution classification must match ordered D01-D34 disposition membership exactly"
        )
    required_resolution_fields = {
        "analysis_id", "epistemic_class", "negative_status", "chapter_destination",
        "chapter3_migration", "reason",
    }
    allowed_negative_status = {
        "NOT_NEGATIVE", "NOT_A_BIOLOGICAL_NEGATIVE", "NEGATIVE_ONLY_FOR_PREDECLARED_DIRECTION",
        "NO_RESULT", "NOT_A_GENERAL_BIOLOGICAL_NEGATIVE", "RESTRICTED_TRUE_NEGATIVE",
        "TRUE_NEGATIVE_FOR_DECLARED_MODEL_SET", "NOT_A_BIOLOGICAL_RESULT",
        "TRUE_NEGATIVE_FOR_FROZEN_GENERATOR", "TRUE_NEGATIVE_FOR_DECLARED_DIAGNOSTIC_SET",
        "NO_CANONICAL_RESULT", "NO_SCIENTIFIC_RESULT",
    }
    for row in resolution:
        if set(row) != required_resolution_fields:
            raise AssertionError("resolution-classification schema drift")
        if row["negative_status"] not in allowed_negative_status:
            raise AssertionError(
                f"unknown negative status for {row['analysis_id']}: {row['negative_status']}"
            )
        for field in required_resolution_fields - {"analysis_id"}:
            if not row[field].strip():
                raise AssertionError(f"{row['analysis_id']} has empty {field}")
    classified = {row["analysis_id"]: row for row in resolution}
    for analysis_id in ("D04", "D05", "D06"):
        if classified[analysis_id]["epistemic_class"] != "CERTAIN_TOPOLOGY_CONDITIONAL_MINIMUM":
            raise AssertionError(f"{analysis_id} minimum-change certainty class drift")
        if classified[analysis_id]["negative_status"] != "NOT_NEGATIVE":
            raise AssertionError(f"{analysis_id} was mislabeled as a negative result")
    if classified["D34"]["epistemic_class"] != "CERTAIN_TOPOLOGY_CONDITIONAL_DEPTH_ENVELOPE":
        raise AssertionError("D34 relative lineage-depth class drift")
    if classified["D34"]["negative_status"] != "NOT_NEGATIVE":
        raise AssertionError("D34 was mislabeled as a negative result")
    for analysis_id in ("D07", "D31", "D32", "D33"):
        if classified[analysis_id]["negative_status"] != "NOT_A_BIOLOGICAL_NEGATIVE":
            raise AssertionError(f"{analysis_id} was promoted to a biological negative")
    if classified["D15"]["negative_status"] != "RESTRICTED_TRUE_NEGATIVE":
        raise AssertionError("universal-agent model falsification class drift")
    expected_model_negatives = {
        "D19": "TRUE_NEGATIVE_FOR_DECLARED_MODEL_SET",
        "D21": "TRUE_NEGATIVE_FOR_FROZEN_GENERATOR",
        "D22": "TRUE_NEGATIVE_FOR_DECLARED_DIAGNOSTIC_SET",
    }
    for analysis_id, expected in expected_model_negatives.items():
        if classified[analysis_id]["negative_status"] != expected:
            raise AssertionError(f"{analysis_id} model-negative boundary drift")

    audit = read_rows(META_SIM_AUDIT_PATH)
    audit_ids = [row["audit_id"] for row in audit]
    if audit_ids != EXPECTED_META_SIM_IDS:
        raise AssertionError(f"meta/simulation audit membership drift: {audit_ids}")
    required_audit_fields = {
        "audit_id", "programme", "kind", "status", "exact_result", "resolution_class",
        "chapter_destination", "chapter3_use", "source_paths", "claim_ceiling",
    }
    for row in audit:
        if set(row) != required_audit_fields:
            raise AssertionError("meta/simulation audit schema drift")
        for field in required_audit_fields - {"audit_id"}:
            if not row[field].strip():
                raise AssertionError(f"{row['audit_id']} has empty {field}")
        for raw_path in row["source_paths"].split(";"):
            source = ROOT / raw_path.strip()
            if not source.exists() or source.stat().st_size == 0:
                raise AssertionError(
                    f"{row['audit_id']} source missing or empty: {raw_path.strip()}"
                )
    audited = {row["audit_id"]: row for row in audit}

    herbivory = load_json(ROOT / "data" / "evidence" / "cirsium_floral_herbivory_lnrr_meta_v2.json")
    pooled = herbivory["random_effects"]
    if pooled["k"] != 4 or abs(pooled["response_ratio"] - 2.673636515996) > 1e-12:
        raise AssertionError("M02 herbivory pooled effect drift")
    if pooled["ci95_response_ratio"] != [2.388333567719, 2.993020872917]:
        raise AssertionError("M02 herbivory confidence interval drift")

    mosaic = load_json(ROOT / "data" / "evidence" / "multiagent_floral_selection_mosaic_summary_v1.json")
    if mosaic["strict_factorial_program_count"] != 5:
        raise AssertionError("M03 strict programme count drift")
    if mosaic["strict_dominance_counts"] != {"antagonist": 2, "mixed": 2, "pollinator": 1}:
        raise AssertionError("M03 dominance-count drift")
    if mosaic["leave_one_program_out_minimum_dominance_categories"] != 2:
        raise AssertionError("M03 leave-one-program-out result drift")

    leverage = load_json(ROOT / "data" / "evidence" / "experimental_pollinator_selection_leverage_meta_v1.json")
    if leverage["primary_gradient_rows"] != 38 or leverage["independent_article_clusters"] != 6:
        raise AssertionError("M04 selection-leverage coverage drift")
    paired_ps = [row["two_sided_exact_signflip_p"] for row in leverage["paired_article_contrasts"]]
    if leverage["significant_paired_class_contrasts"] or min(paired_ps) != 0.5 or max(paired_ps) != 1.0:
        raise AssertionError("M04 paired functional-class decision drift")

    demographic = load_json(ROOT / "data" / "evidence" / "cirsium_demographic_transmission_meta_v1.json")
    if demographic["population_transmission"] != {"consistent": 4, "context_dependent": 1, "blocked": 1}:
        raise AssertionError("M05 transmission counts drift")
    if (demographic["demographic_gate_supported_studies"], demographic["demographic_gate_tested_studies"]) != (3, 4):
        raise AssertionError("M05 demographic-gate result drift")
    if (demographic["broad_abiotic_general_moderator_support_studies"], demographic["broad_abiotic_context_tested_studies"]) != (0, 5):
        raise AssertionError("M05 broad-abiotic result drift")

    pollinator = load_json(ROOT / "data" / "evidence" / "cirsium_pollinator_assurance_meta_v1.json")
    if (pollinator["independent_study_count"], pollinator["high_pollinator_dependence_studies"], pollinator["exact_numeric_studies"]) != (6, 5, 1):
        raise AssertionError("M06 pollinator-assurance coverage drift")

    orientation = load_json(ROOT / "data" / "evidence" / "fdt1_orientation_net_fitness_two_study_meta_v1.json")
    if orientation["k"] != 2 or abs(orientation["heterogeneity"]["I2_percent"] - 93.5714188738) > 1e-10:
        raise AssertionError("M07 orientation diagnostic drift")

    calibration = load_json(ROOT / "data" / "evidence" / "fdt1_broad_functional_calibration_summary_v1.json")
    if calibration["rows"] != 26:
        raise AssertionError("M08 calibration-row count drift")
    module_counts = calibration["modules"]
    if (
        module_counts["orientation"]["rows"],
        module_counts["stickiness"]["rows"] + module_counts["stickiness_glandular_trichomes"]["rows"],
        module_counts["display"]["rows"],
        module_counts["bract_defence"]["rows"],
        module_counts["colour_pigmentation"]["rows"],
    ) != (11, 5, 3, 3, 4):
        raise AssertionError("M08 calibration module counts drift")

    ceiling = load_json(ROOT / "data" / "evidence" / "doctoral_meta_resolution_gate_v1.json")
    if ceiling["hypothesis_count"] != 6 or ceiling["meta_ceiling_reached_count"] != 6:
        raise AssertionError("M09 meta-ceiling count drift")
    cross_scale = load_json(ROOT / "data" / "evidence" / "cross_scale_identifiability_meta_v1.json")
    linkage = cross_scale["hmm2_linkage_ceiling"]
    current = linkage["currently_testable_system_result"]
    if (
        linkage["reviewed_polymorphic_systems"],
        linkage["systems_with_state_resolution_compression"],
        linkage["systems_with_direct_morph_linked_public_nuclear_samples"],
        current["species_level_minimum_transitions"],
        current["sample_aware_minimum_transitions"],
    ) != (4, 4, 1, 1, 2):
        raise AssertionError("M10 cross-scale identifiability drift")
    cytotype = load_json(ROOT / "data" / "evidence" / "japan38_cytotype_trait_overlap_v1.json")
    if (
        cytotype["n_source_backed_cytotype_concepts"],
        cytotype["dominant_radiation_ploidy_levels"],
        cytotype["upward_or_ascending_observed_ploidy_levels"],
        cytotype["diploid_observed_orientation_states"],
    ) != (
        9,
        [2, 4, 6],
        [2, 4, 6],
        ["downward_or_nodding", "upward_or_erect"],
    ):
        raise AssertionError("M11 cytotype-trait context drift")
    fdt_registry = read_rows(
        ROOT / "data" / "evidence" / "functional_diversity_time_meta_registry_v1.csv"
    )
    if [row["analysis_id"] for row in fdt_registry] != [f"FDT{i}" for i in range(1, 9)]:
        raise AssertionError("M12 FDT programme registry drift")

    v31 = load_json(ROOT / "data" / "evidence" / "capitulum_space_mechanism_v3_1_result_summary.json")
    if len(v31["families"]) != 5 or len(v31["seeds"]) != 4 or v31["draws_per_seed_per_family"] != 500 or v31["adequate_families"]:
        raise AssertionError("S03 frozen model-family result drift")
    scalar = load_json(ROOT / "data" / "evidence" / "azami_capitulum_v3_one_shot_decision_v1.json")
    if scalar["robust_leader"] != "NULL_COUPLED" or scalar["paired_draw_count"] != 16 or scalar["model_family_count"] != 14:
        raise AssertionError("S04 scalar-screen result drift")
    heldout = load_json(ROOT / "data" / "evidence" / "azami_capitulum_v3_null_heldout_support_decision_v1.json")
    if (heldout["primary_pattern_matches"], heldout["exact_20_cell_matches"], heldout["validation_draws"]) != (0, 0, 64):
        raise AssertionError("S05 heldout-falsification result drift")
    among_only = load_json(ROOT / "data" / "evidence" / "azami_capitulum_v3_support_geometry_diagnostic_decision_v1.json")
    if among_only["diagnostically_adequate_families"] or among_only["best_median_primary_cells_matched_out_of_8"] != 6.0 or among_only["paired_draw_count"] != 24:
        raise AssertionError("S06 post-heldout diagnostic drift")
    v41 = load_json(ROOT / "data" / "contracts" / "scale_specific_covariance_v4_contract.json")
    if v41["status"] != "frozen_before_v4_family_outcomes":
        raise AssertionError("S07 provisional-contract boundary drift")
    fdt7 = load_json(ROOT / "data" / "evidence" / "fdt7_legacy_simulation_bridge_v2.json")
    if (
        fdt7["model_aliases"]["M0"]["status"] != "time-axis implementation required"
        or fdt7["model_aliases"]["M4"]["status"]
        != "preferred structural starting family, not yet time-axis winner"
        or fdt7["model_aliases"]["M5"]["status"]
        != "blocked_until_dated_tree_and_event_inputs"
    ):
        raise AssertionError("S08 planned FDT7 model was promoted to a result")
    orientation_sim = load_json(
        ROOT / "data" / "evidence" / "orientation_mechanism_reduction_result_v1.json"
    )
    orientation_best = next(
        family for family in orientation_sim["families"]
        if family["family"] == "combined_time_abiotic"
    )
    if (
        len(orientation_sim["families"]),
        orientation_sim["draws_per_family"],
        orientation_sim["best_family"],
        orientation_best["full_core_match_rate"],
        orientation_best["heldout_mean"],
    ) != (5, 1500, "combined_time_abiotic", 0.183333, 1.0):
        raise AssertionError("S09 orientation mechanism diagnostic drift")
    macro_v1 = load_json(
        ROOT / "data" / "evidence" / "macro_interaction_pattern_reduction_result_v1.json"
    )
    macro_v2 = load_json(
        ROOT / "data" / "evidence" / "macro_interaction_pattern_reduction_result_v2.json"
    )
    if (
        macro_v1["families"][0]["family"],
        macro_v1["families"][0]["best_match_count"],
        macro_v1["families"][0]["full_match_rate"],
        macro_v2["best_family_by_robust_pattern_score"],
        macro_v2["draws_per_seed_per_family"],
        len(macro_v2["seeds"]),
    ) != (
        "full_tradeoff_modular_evolvability",
        11,
        1 / 180,
        "full_tradeoff_modular_evolvability",
        180,
        4,
    ):
        raise AssertionError("S10 historical macro-interaction screen drift")

    split = RESOLUTION_SPLIT_PATH.read_text(encoding="utf-8")
    required_split = [
        "at least four state changes", "at least three", "at least five",
        "not identifiable at current resolution", "0/64", "RR=2.674",
        "field_execution_authorized=false",
    ]
    missing = [needle for needle in required_split if needle not in split]
    if missing:
        raise AssertionError(f"resolution-aware split missing: {missing}")
    disposition = META_SIM_DISPOSITION_PATH.read_text(encoding="utf-8")
    required_disposition = [
        "pooled RR=2.674", "6/6 current HGA hypotheses", "five families x four seeds x 500 draws",
        "0/64", "22/24", "5 x 1,500", "11/11", "Present-state simulations",
        "Evolutionary simulations",
    ]
    missing = [needle for needle in required_disposition if needle not in disposition]
    if missing:
        raise AssertionError(f"meta/simulation disposition missing: {missing}")
    if audited["S03"]["chapter_destination"] != "Chapter_1":
        raise AssertionError("present-state simulation was routed into Chapter 2")
    if audited["M02"]["chapter_destination"] != "Chapter_3_function":
        raise AssertionError("functional meta-analysis was routed into Chapter 2")
    return resolution, audit


def validate_design_document(contract: dict) -> None:
    text = DESIGN_PATH.read_text(encoding="utf-8")
    required = [
        "diversity breadth -> diversity depth",
        "Central question",
        "Standalone EAzami analysis pipeline",
        "Repository-wide inventory",
        "Analyses runnable now",
        "final Chapter 2 result",
        "PR #126 and legacy V3 disposition",
        "minimum-count stability, relative lineage-depth and named-edge localization are separate properties",
        "configuration diversity with multiple minimum changes within a dominant radiation",
        "scientifically complete with existing public evidence",
        "Chapter 3 is not a completion gate",
    ]
    missing = [needle for needle in required if needle not in text]
    if missing:
        raise AssertionError(f"standalone design document missing: {missing}")
    if contract["claim_ceiling"] not in text:
        raise AssertionError("machine-readable and narrative claim ceilings differ")


def validate_active_manuscript() -> None:
    text = MANUSCRIPT_PATH.read_text(encoding="utf-8")
    required = [
        "# Capitulum configuration diversity, minimum change counts",
        "## Abstract",
        "# Introduction",
        "# Materials and methods",
        "# Results",
        "# Discussion",
        "# Conclusion",
        "# References",
        "four to six unordered changes",
        "phyllary posture exactly three",
        "stickiness exactly five",
        "relative lineage-depth",
        "0.227",
        "0.728",
        "0.995",
        "0.707",
        "36 of 38 sampled Japanese concepts",
        "at least three harmonized orientation × stickiness configurations",
        "All four audited colour-polymorphic systems",
        "Zero of three trait pairs",
        "No new RAD-seq, phenotype, dated-tree or field result is a submission gate",
    ]
    missing = [needle for needle in required if needle not in text]
    if missing:
        raise AssertionError(f"active JEB v4 manuscript missing: {missing}")
    abstract = text.split("## Abstract", 1)[1].split("**Keywords:**", 1)[0]
    abstract_words = len(abstract.replace("\n", " ").split())
    if abstract_words > 250:
        raise AssertionError(f"JEB v4 abstract exceeds 250 words: {abstract_words}")
    prohibited = [
        "46,276 unique strict-spatial image observations",
        "Present-day capitulum integration is scale dependent",
        "P=0.3504",
        "P=0.1959",
        "Robust recurrence but uncertain localization",
        "Recurrent assembly of capitulum trait configurations",
        "recurrent trait change",
        "recurrence lower bound",
        "minimum steps equal independent origins",
        "field execution authorized",
    ]
    found = [needle for needle in prohibited if needle in text]
    if found:
        raise AssertionError(f"active JEB v4 manuscript crosses its claim boundary: {found}")


def main() -> int:
    for path in (
        CONTRACT_PATH, INVENTORY_PATH, DESIGN_PATH, MANUSCRIPT_PATH,
        CORE_RECOVERY_PATH, CORE_POSITION_PATH, RESOLUTION_CLASS_PATH,
        META_SIM_AUDIT_PATH, RESOLUTION_SPLIT_PATH, META_SIM_DISPOSITION_PATH,
        ANALYSIS_DISPOSITION_PATH, RELATIVE_DEPTH_PATH,
    ):
        if not path.exists() or path.stat().st_size == 0:
            raise AssertionError(f"missing or empty standalone Chapter 2 file: {path.relative_to(ROOT)}")
    contract = load_json(CONTRACT_PATH)
    if contract["contract_version"] != "chapter2_diversity_depth_contract_v1":
        raise AssertionError("contract version drift")
    inventory = validate_inventory()
    gate = validate_native_input(contract)
    validate_independence_boundary(contract)
    validate_native_history_diagnostic()
    priorities = validate_chapter2_to_chapter3_bridge(contract)
    validate_frozen_results()
    recovered = validate_core_result_recovery()
    resolution, meta_sim = validate_resolution_and_meta_sim_audit()
    validate_design_document(contract)
    validate_active_manuscript()
    print("chapter2_diversity_depth_contract_valid=true")
    print(f"inventory_rows={len(inventory)}")
    print(f"standalone_continuous_gate={gate}")
    print(f"submission_status={contract['current_submission_status']}")
    print(f"radseq_sampling_priorities={len(priorities)}")
    print(f"core_result_rows={len(recovered)}")
    print(f"resolution_classification_rows={len(resolution)}")
    print(f"meta_simulation_audit_rows={len(meta_sim)}")
    print("main_result_groups=5")
    print("legacy_pr126_package=frozen_audit_snapshot")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
