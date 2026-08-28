#!/usr/bin/env python3
"""Fail-closed validation of the active Chapter 2 JEB submission package."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CH = ROOT / "docs" / "chapter2"
TIME = ROOT / "data" / "evidence" / "chapter2_time_axis_compute"
PROV = ROOT / "data" / "evidence" / "chapter2_provenance_sensitivity_compute"
FIG = CH / "figures"
SUPP_FIG = FIG / "supplementary"
SUBMISSION = CH / "submission_package"

REQUIRED = [
    ROOT / "README.md",
    ROOT / "PROJECT_STATUS.md",
    ROOT / "docs" / "RESEARCH_PLAN.md",
    CH / "README.md",
    CH / "CHAPTER2_CORE_RESULT_RECOVERY_V1.md",
    CH / "TIME_AXIS_MAINLINE_V3.md",
    CH / "MANUSCRIPT_JEB_V3.md",
    CH / "JEB_SUBMISSION_TARGET_V1.md",
    CH / "TARGET_JOURNAL_JEB_V1.md",
    CH / "JEB_QUESTION_RESULT_FIGURE_MAP_V1.md",
    CH / "JEB_FIGURE_CHART_CONTRACT_V1.md",
    CH / "JEB_SUPPORTING_INFORMATION_V1.md",
    CH / "JEB_TITLE_PAGE_TEMPLATE_V1.md",
    CH / "JEB_COVER_LETTER_TEMPLATE_V1.md",
    ROOT / "data" / "evidence" / "chapter2_jeb_reframe_contract_v1.json",
    ROOT / "data" / "evidence" / "chapter2_historical_integration_hypothesis_v1.json",
    ROOT / "data" / "evidence" / "chapter2_analysis_disposition_v1.csv",
    ROOT / "data" / "evidence" / "chapter2_claim_registry_v1.csv",
    ROOT / "data" / "evidence" / "chapter2_result_role_map_v2.csv",
    ROOT / "data" / "evidence" / "chapter2_jeb_main_result_table_v1.csv",
    ROOT / "data" / "evidence" / "chapter2_core_result_recovery_v1.csv",
    ROOT / "data" / "evidence" / "source" / "azami_capitulum_space_eazami_targets_run33035785120.csv",
    TIME / "continuous_primary_phylogenetic_structure_v1.csv",
    TIME / "japan38_branch_change_reconstruction_null_v1.json",
    TIME / "japan38_branch_change_reconstruction_null_distribution_v1.csv",
    TIME / "japan38_continuous_branch_change_topology_sensitivity_v1.json",
    TIME / "japan38_latest_module_transition_overlap_v2.json",
    TIME / "japan38_latest_module_overlap_topology_sensitivity_v2.json",
    PROV / "continuous_primary_phylogenetic_structure_v1.csv",
    PROV / "japan38_all_continuous_history_summary_v1.json",
    PROV / "japan38_branch_change_provenance_sensitivity_v1.json",
    PROV / "japan38_branch_change_provenance_sensitivity_null_distribution_v1.csv",
    PROV / "japan38_branch_change_provenance_sensitivity_provenance_v1.json",
    ROOT / "data" / "evidence" / "jpn24_stickiness_extension_parsimony_v1.json",
    FIG / "figure_manifest_v1.json",
    SUPP_FIG / "supplementary_figure_manifest_v1.json",
    SUBMISSION / "Chapter2_JEB_Anonymous_Manuscript_V3.docx",
    SUBMISSION / "Chapter2_JEB_Title_Page_TEMPLATE_V1.docx",
    SUBMISSION / "Chapter2_JEB_Supporting_Information_V1.docx",
    SUBMISSION / "Chapter2_JEB_Cover_Letter_TEMPLATE_V1.docx",
]


def require(text: str, needles: list[str], label: str) -> None:
    missing = [x for x in needles if x not in text]
    if missing:
        raise AssertionError(f"{label} missing required statements: {missing}")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def markdown_word_count(text: str) -> int:
    return len(re.findall(r"\b[\w][\w\-.]*\b", text, flags=re.UNICODE))


def check_manuscript() -> None:
    manuscript = (CH / "MANUSCRIPT_JEB_V3.md").read_text(encoding="utf-8")
    require(
        manuscript,
        [
            "Present-day phenotypic integration does not imply a shared evolutionary history",
            "0.1645",
            "0.0885",
            "0.3504",
            "0.1959",
            "0.1418",
            "75.4%",
            "not evaluable",
            "global species-level image proxies",
            "Generative AI assisted",
            "Moreyra, L. D., Susanna, A.",
            "figure1_present_integration.png",
            "figure4_discrete_overlap.png",
        ],
        "MANUSCRIPT_JEB_V3",
    )
    prohibited = [
        "coordinated evolutionary remodeling",
        "continuous trait states are weakly conserved",
        "large continuous changes were coordinated across every tested bootstrap topology",
        "branch permutation P = **0.00010**",
    ]
    found = [x for x in prohibited if x.lower() in manuscript.lower()]
    if found:
        raise AssertionError(f"active manuscript retains superseded claims: {found}")
    abstract_match = re.search(r"(?s)## Abstract\s+(.*?)\s+\*\*Keywords:", manuscript)
    main_match = re.search(r"(?s)# Introduction\s+(.*?)\s+# References", manuscript)
    if not abstract_match or not main_match:
        raise AssertionError("could not locate abstract or main-text boundaries")
    abstract_words = markdown_word_count(abstract_match.group(1))
    main_words = markdown_word_count(main_match.group(1))
    if abstract_words > 250:
        raise AssertionError(f"abstract exceeds JEB limit: {abstract_words}")
    if main_words > 7500:
        raise AssertionError(f"main text exceeds JEB limit: {main_words}")
    keyword_match = re.search(r"\*\*Keywords:\*\*\s*(.*)", manuscript)
    if not keyword_match:
        raise AssertionError("keywords line missing")
    keyword_count = len([x for x in keyword_match.group(1).split(";") if x.strip()])
    if not 4 <= keyword_count <= 10:
        raise AssertionError(f"JEB requires 4-10 keywords, found {keyword_count}")
    if manuscript.count("![Alternative text:") != 4:
        raise AssertionError("every one of four main figures must have embedded alternative text")
    print(f"abstract_words={abstract_words}")
    print(f"main_text_words={main_words}")
    print(f"keywords={keyword_count}")


def check_present_integration() -> None:
    target = rows(ROOT / "data" / "evidence" / "source" / "azami_capitulum_space_eazami_targets_run33035785120.csv")
    lookup = {(r["target_id"], r["scope"]): r for r in target}
    expected = {
        ("capitulum_within_module_integration_contrast", "complete18_min5"): 0.1645023304673242,
        ("capitulum_among_module_integration_contrast", "complete18_min5"): 0.08847536372583811,
        ("capitulum_within_module_integration_contrast", "complete18_min2"): 0.15768784945046527,
        ("capitulum_among_module_integration_contrast", "complete18_min2"): 0.08366242420240788,
        ("capitulum_cross_scale_association_matrix_similarity", "complete18_min5"): 0.36629931778064023,
    }
    for key, value in expected.items():
        if key not in lookup or abs(float(lookup[key]["value"]) - value) > 1e-12:
            raise AssertionError(f"present-integration target drift: {key}")


def check_continuous_state_structure() -> None:
    original = rows(TIME / "continuous_primary_phylogenetic_structure_v1.csv")
    for threshold in (2, 5):
        subset = [r for r in original if int(r["threshold"]) == threshold]
        if len(subset) != 8 or any(r["history_support_class"] != "two_sided_not_supported" for r in subset):
            raise AssertionError(f"original continuous family drift at threshold {threshold}")
    corrected = rows(PROV / "continuous_primary_phylogenetic_structure_v1.csv")
    n2 = [r for r in corrected if int(r["threshold"]) == 2]
    n5 = [r for r in corrected if int(r["threshold"]) == 5]
    if len(n2) != 8 or any(r["history_support_class"] != "two_sided_not_supported" for r in n2):
        raise AssertionError("JPN29-excluded nobs>=2 family drift")
    if n5:
        raise AssertionError("JPN29-excluded high-depth family must remain not_evaluable, not populated")
    summary = load_json(PROV / "japan38_all_continuous_history_summary_v1.json")
    if summary["excluded_concepts"] != ["JPN_29"] or summary["n5_history_classes"] != {}:
        raise AssertionError("JPN29 exclusion or high-depth not_evaluable state drift")


def check_reconstruction_nulls() -> None:
    original = load_json(TIME / "japan38_branch_change_reconstruction_null_v1.json")
    if original["decision"] != "FAIL" or abs(original["one_sided_reconstruction_null_p"] - 0.3504) > 1e-12:
        raise AssertionError("original reconstruction-aware FAIL drift")
    if original["common_concepts"] != 8 or original["branches"] != 14 or original["permutations"] != 9999:
        raise AssertionError("original reconstruction-null panel drift")
    sensitivity = load_json(PROV / "japan38_branch_change_provenance_sensitivity_v1.json")
    if sensitivity["decision"] != "FAIL" or abs(sensitivity["one_sided_reconstruction_null_p"] - 0.1959) > 1e-12:
        raise AssertionError("JPN29-excluded reconstruction-aware FAIL drift")
    if sensitivity["excluded_concepts"] != ["JPN_29"] or sensitivity["common_concepts"] != 7 or sensitivity["branches"] != 12:
        raise AssertionError("JPN29-excluded panel drift")
    if sensitivity["analysis_role"] != "provenance_sensitivity_not_confirmatory_rescue":
        raise AssertionError("provenance sensitivity role drift")
    for path in (
        TIME / "japan38_branch_change_reconstruction_null_distribution_v1.csv",
        PROV / "japan38_branch_change_provenance_sensitivity_null_distribution_v1.csv",
    ):
        if sum(1 for _ in path.open(encoding="utf-8")) != 10000:
            raise AssertionError(f"null distribution does not contain 9999 draws: {path.name}")


def check_topology_diagnostic_determinism() -> None:
    topology = load_json(TIME / "japan38_continuous_branch_change_topology_sensitivity_v1.json")
    tie_contract = topology.get("spearman_tie_contract", "")
    if not tie_contract.startswith("branch-change magnitudes rounded to 12 decimal places"):
        raise AssertionError("equal-branch topology diagnostic lacks its deterministic tie contract")
    summary = topology["global_mean_pairwise_rho_distribution"]
    if abs(summary["median"] - 0.1417859210142532) > 1e-12:
        raise AssertionError("deterministic topology median drift")
    if abs(summary["q05"] - 0.11896314374693295) > 1e-12:
        raise AssertionError("deterministic topology q05 drift")
    if summary["fraction_positive"] != 1.0:
        raise AssertionError("topology diagnostic sign distribution drift")


def check_discrete_history() -> None:
    sticky = load_json(ROOT / "data" / "evidence" / "jpn24_stickiness_extension_parsimony_v1.json")
    if sticky["stickiness"]["resolved_concepts_after"] != 13:
        raise AssertionError("stickiness coverage drift")
    if sticky["stickiness"]["ufboot1000_steps_min"] != 5 or sticky["stickiness"]["ufboot1000_steps_max"] != 5:
        raise AssertionError("stickiness minimum-change drift")
    dtop = load_json(TIME / "japan38_latest_module_overlap_topology_sensitivity_v2.json")
    if dtop["bootstrap_topology_sensitivity"]["bootstrap_trees_total"] != 1000:
        raise AssertionError("discrete topology ensemble incomplete")
    dist = dtop["bootstrap_topology_sensitivity"]["pairwise_spearman_distributions"]
    if dist["orientation__stickiness"]["fraction_positive"] >= 0.05:
        raise AssertionError("orientation-stickiness topology result drift")
    if all(v["q05"] > 0 and v["fraction_positive"] >= 0.95 for v in dist.values()):
        raise AssertionError("one shared discrete history was unexpectedly promoted")


def check_result_registries() -> None:
    main = {r["result_id"]: r for r in rows(ROOT / "data" / "evidence" / "chapter2_jeb_main_result_table_v1.csv")}
    needed = {"R0_present_primary", "R1_jpn29_excluded", "R4_original_null", "R4_jpn29_excluded", "R5_topology_diagnostic", "R6_os"}
    if not needed.issubset(main):
        raise AssertionError(f"headline result registry missing {sorted(needed - set(main))}")
    if main["R4_original_null"]["decision"] != "FAIL" or main["R4_jpn29_excluded"]["decision"] != "FAIL":
        raise AssertionError("result registry fails to preserve null decisions")
    if main["R5_topology_diagnostic"]["decision"] != "diagnostic_only":
        raise AssertionError("topology diagnostic was promoted")
    if "12-decimal tie contract" not in main["R5_topology_diagnostic"]["headline_value"]:
        raise AssertionError("result registry omits deterministic topology tie contract")
    claims = {r["claim_id"]: r for r in rows(ROOT / "data" / "evidence" / "chapter2_claim_registry_v1.csv")}
    if claims.get("C2_25", {}).get("status") != "synthesis":
        raise AssertionError("active JEB claim missing from claim registry")
    disposition = {r["analysis_id"]: r for r in rows(ROOT / "data" / "evidence" / "chapter2_analysis_disposition_v1.csv")}
    if disposition.get("D31", {}).get("current_status") != "canonical_negative":
        raise AssertionError("reconstruction-aware null disposition missing")
    if disposition.get("D32", {}).get("current_status") != "canonical_provenance_sensitivity":
        raise AssertionError("JPN29 sensitivity disposition missing")


def check_figures() -> None:
    manifest = load_json(FIG / "figure_manifest_v1.json")
    outputs = manifest["outputs"]
    if len(outputs) != 8:
        raise AssertionError("expected four PDF and four PNG figure outputs")
    for name, meta in outputs.items():
        path = FIG / name
        if not path.exists() or path.stat().st_size <= 10_000:
            raise AssertionError(f"missing or undersized figure: {name}")
        got = hashlib.sha256(path.read_bytes()).hexdigest()
        if got != meta["sha256"]:
            raise AssertionError(f"figure hash drift: {name}")
        if path.suffix == ".pdf" and not path.read_bytes().startswith(b"%PDF"):
            raise AssertionError(f"invalid PDF header: {name}")
        if path.suffix == ".png" and not path.read_bytes().startswith(b"\x89PNG"):
            raise AssertionError(f"invalid PNG header: {name}")


def check_supplementary_figures() -> None:
    manifest = load_json(SUPP_FIG / "supplementary_figure_manifest_v1.json")
    outputs = manifest["outputs"]
    if len(outputs) != 10:
        raise AssertionError("expected five PDF and five PNG supplementary figure outputs")
    for name, meta in outputs.items():
        path = SUPP_FIG / name
        if not path.exists() or path.stat().st_size <= 10_000:
            raise AssertionError(f"missing or undersized supplementary figure: {name}")
        got = hashlib.sha256(path.read_bytes()).hexdigest()
        if got != meta["sha256"]:
            raise AssertionError(f"supplementary figure hash drift: {name}")
        if path.suffix == ".pdf" and not path.read_bytes().startswith(b"%PDF"):
            raise AssertionError(f"invalid supplementary PDF header: {name}")
        if path.suffix == ".png" and not path.read_bytes().startswith(b"\x89PNG"):
            raise AssertionError(f"invalid supplementary PNG header: {name}")
    supporting = (CH / "JEB_SUPPORTING_INFORMATION_V1.md").read_text(encoding="utf-8")
    if supporting.count("![Alternative text:") != 5:
        raise AssertionError("every one of five supplementary figures must have embedded alternative text")
    for idx in range(1, 6):
        if f"figure_s{idx}_" not in supporting:
            raise AssertionError(f"Supporting Information omits Figure S{idx}")
    require(
        supporting,
        ["P=0.3504", "P=0.1959", "not_evaluable", "substitutions/site", "rounded to 12 decimal places", "4/4", "0/4"],
        "JEB_SUPPORTING_INFORMATION_V1",
    )


def check_docx_package() -> None:
    package = {
        "main": (SUBMISSION / "Chapter2_JEB_Anonymous_Manuscript_V3.docx", 4),
        "title": (SUBMISSION / "Chapter2_JEB_Title_Page_TEMPLATE_V1.docx", 0),
        "supporting": (SUBMISSION / "Chapter2_JEB_Supporting_Information_V1.docx", 5),
        "cover": (SUBMISSION / "Chapter2_JEB_Cover_Letter_TEMPLATE_V1.docx", 0),
    }
    ns = {
        "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
        "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
        "dc": "http://purl.org/dc/elements/1.1/",
        "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    }
    for role, (path, expected_images) in package.items():
        if not zipfile.is_zipfile(path):
            raise AssertionError(f"invalid DOCX archive: {path.name}")
        with zipfile.ZipFile(path) as archive:
            names = set(archive.namelist())
            for required in ("[Content_Types].xml", "word/document.xml", "docProps/core.xml"):
                if required not in names:
                    raise AssertionError(f"{path.name} omits {required}")
            raw = archive.read("word/document.xml")
            root = ET.fromstring(raw)
            doc_pr = root.findall(".//wp:docPr", ns)
            if len(doc_pr) != expected_images:
                raise AssertionError(f"{path.name} expected {expected_images} figures, found {len(doc_pr)}")
            if any(not node.attrib.get("descr", "").startswith("Alternative text:") for node in doc_pr):
                raise AssertionError(f"{path.name} has a figure without meaningful alternative text")
            if b"rsid" in raw:
                raise AssertionError(f"{path.name} retains Word revision-session identifiers")
            core = ET.fromstring(archive.read("docProps/core.xml"))
            for field in ("dc:creator", "cp:lastModifiedBy"):
                node = core.find(field, ns)
                if node is not None and (node.text or "").strip():
                    raise AssertionError(f"{path.name} retains identifying core property {field}")
            if role == "main":
                line_numbering = root.findall(".//w:lnNumType", ns)
                if not line_numbering or any(n.attrib.get(f"{{{ns['w']}}}restart") != "continuous" for n in line_numbering):
                    raise AssertionError("anonymous manuscript lacks continuous line numbering")
                if b"[INSERT" in raw.upper():
                    raise AssertionError("anonymous manuscript contains an author-only placeholder")


def check_entry_points() -> None:
    for path, needles in {
        ROOT / "README.md": [
            "COMPLETE_EXISTING_PUBLIC_HISTORY_CORE",
            "Capitulum configuration diversity, minimum change counts",
            "MANUSCRIPT_JEB_V3.md",
            "audit snapshots",
        ],
        ROOT / "PROJECT_STATUS.md": [
            "HOLD_JEB_PACKAGE_REBUILD_ONLY",
            "Active standalone title",
            "v4 is current submission text",
            "CHAPTER2_CORE_RESULT_RECOVERY_V1.md",
        ],
        ROOT / "docs" / "RESEARCH_PLAN.md": [
            "standalone",
            "configuration diversity plus multiple minimum changes",
            "Journal of Evolutionary Biology",
            "immutable audit snapshot",
        ],
        CH / "README.md": ["MANUSCRIPT_JEB_V4.md", "Frozen legacy submission package", "0.3504", "0.1959", "CHAPTER2_CORE_RESULT_RECOVERY_V1.md"],
        CH / "TIME_AXIS_MAINLINE_V3.md": ["frozen audit", "not_evaluable", "Diagnostic only"],
        CH / "JEB_SUBMISSION_TARGET_V1.md": ["7,500 words", "<=250 words", "double-anonymous", "generative-AI"],
    }.items():
        require(path.read_text(encoding="utf-8"), needles, path.name)


def main() -> int:
    for path in REQUIRED:
        if not path.exists() or path.stat().st_size == 0:
            raise AssertionError(f"missing/empty Chapter 2 file: {path.relative_to(ROOT)}")
    check_manuscript()
    check_present_integration()
    check_continuous_state_structure()
    check_reconstruction_nulls()
    check_topology_diagnostic_determinism()
    check_discrete_history()
    check_result_registries()
    check_figures()
    check_supplementary_figures()
    check_docx_package()
    check_entry_points()
    print("chapter2_jeb_v3_audit_package_valid=true")
    print("original_reconstruction_null=FAIL_P_0.3504")
    print("jpn29_excluded_sensitivity=FAIL_P_0.1959")
    print("main_figures=4_pdf_plus_png")
    print("supplementary_figures=5_pdf_plus_png")
    print("submission_docx=4_privacy_scrubbed_and_accessible")
    print("submission_target=Journal_of_Evolutionary_Biology")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
