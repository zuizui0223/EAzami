#!/usr/bin/env python3
"""Fail-closed consistency checks for the current Chapter 2 time-axis mainline."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CH = ROOT / "docs" / "chapter2"
TIME = ROOT / "data" / "evidence" / "chapter2_time_axis_compute"

REQUIRED = [
    ROOT / "PROJECT_STATUS.md",
    ROOT / "docs" / "RESEARCH_PLAN.md",
    CH / "TIME_AXIS_MAINLINE_V3.md",
    CH / "MANUSCRIPT_JEB_V2.md",
    CH / "JEB_SUBMISSION_TARGET_V1.md",
    CH / "JEB_QUESTION_RESULT_FIGURE_MAP_V1.md",
    CH / "META_SIM_DISPOSITION_V1.md",
    ROOT / "data" / "evidence" / "chapter2_analysis_disposition_v1.csv",
    ROOT / "data" / "evidence" / "chapter2_jeb_main_result_table_v1.csv",
    TIME / "continuous_primary_phylogenetic_structure_v1.csv",
    TIME / "continuous_primary_branch_change_summary_v1.json",
    TIME / "japan38_continuous_branch_change_topology_sensitivity_v1.json",
    TIME / "japan38_latest_module_transition_overlap_v2.json",
    TIME / "japan38_latest_module_overlap_topology_sensitivity_v2.json",
    ROOT / "data" / "evidence" / "jpn24_stickiness_extension_parsimony_v1.json",
]


def require(text: str, needles: list[str], label: str) -> None:
    missing = [x for x in needles if x not in text]
    if missing:
        raise AssertionError(f"{label} missing required statements: {missing}")


def main() -> int:
    for path in REQUIRED:
        if not path.exists() or path.stat().st_size == 0:
            raise AssertionError(f"missing/empty Chapter 2 file: {path.relative_to(ROOT)}")

    status = (ROOT / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    require(
        status,
        [
            "Chapter 1 — phenotype × present-day space/environment",
            "Chapter 2 — phenotype × evolutionary time/history",
            "Chapter 3 — phenotype × function/fitness",
            "0/8",
            "0.408006",
            "0.141287",
            "1000/1000",
            "nuclear population genomics",
            "plastid haplotype",
            "cytotype",
            "Journal of Evolutionary Biology",
        ],
        "PROJECT_STATUS",
    )
    if "EAzami-I\nphenotype → candidate function" in status:
        raise AssertionError("PROJECT_STATUS reverted to function-first Chapter 2 ordering")

    plan = (ROOT / "docs" / "RESEARCH_PLAN.md").read_text(encoding="utf-8")
    require(
        plan,
        [
            "Chapter 1 — phenotype × present-day space/environment",
            "Chapter 2 — phenotype × evolutionary time/history",
            "Chapter 3 — phenotype × function/fitness",
            "State conservation",
            "recurrence",
            "change localization",
            "0/8",
            "0.408006",
            "0.141287",
            "Journal of Evolutionary Biology",
            "What happens to existing meta-analysis",
            "What happens to existing simulation",
        ],
        "RESEARCH_PLAN",
    )

    mainline = (CH / "TIME_AXIS_MAINLINE_V3.md").read_text(encoding="utf-8")
    require(
        mainline,
        [
            "phenotype × evolutionary time/history",
            "state conservation",
            "recurrence",
            "change localization",
            "function",
            "not",
        ],
        "TIME_AXIS_MAINLINE_V3",
    )

    manuscript = (CH / "MANUSCRIPT_JEB_V2.md").read_text(encoding="utf-8")
    require(
        manuscript,
        [
            "Journal of Evolutionary Biology",
            "0.408006",
            "0.00010",
            "0.141287",
            "0.118995",
            "94.6%",
            "coordinated evolutionary remodeling",
            "not absolute time",
        ],
        "MANUSCRIPT_JEB_V2",
    )

    target = (CH / "JEB_SUBMISSION_TARGET_V1.md").read_text(encoding="utf-8")
    require(
        target,
        [
            "Journal of Evolutionary Biology",
            "7,500 words",
            "<=250 words",
            "4–10",
            "adaptive convergence",
        ],
        "JEB submission target",
    )

    figure_map = (CH / "JEB_QUESTION_RESULT_FIGURE_MAP_V1.md").read_text(encoding="utf-8")
    require(
        figure_map,
        [
            "Q1.", "Q2.", "Q3.", "Q4.", "Q5.",
            "1000/1000",
            "q05=.118995",
            "q05=-.095160",
            "Figure 5",
        ],
        "JEB figure map",
    )

    # Quantitative result contracts: check source tables, not only manuscript prose.
    units = list(csv.DictReader((TIME / "continuous_primary_phylogenetic_structure_v1.csv").open(encoding="utf-8", newline="")))
    for threshold in (2, 5):
        rows = [r for r in units if int(r["threshold"]) == threshold]
        if len(rows) != 8:
            raise AssertionError(f"expected 8 primary continuous units at threshold {threshold}, found {len(rows)}")
        if any(r["history_support_class"] != "two_sided_not_supported" for r in rows):
            raise AssertionError(f"unexpected promoted continuous history at threshold {threshold}")
        scalar = [r for r in rows if r["unit_type"] == "scalar"]
        if len(scalar) != 7 or any(abs(float(r["lambda_mle"])) > 1e-12 for r in scalar):
            raise AssertionError(f"scalar Pagel lambda result drift at threshold {threshold}")

    ml = json.loads((TIME / "continuous_primary_branch_change_summary_v1.json").read_text(encoding="utf-8"))
    if abs(ml["global_mean_pairwise_branch_change_rho"] - 0.40800627943485085) > 1e-12:
        raise AssertionError("ML continuous branch-change headline drifted")
    if abs(ml["global_shared_lability_permutation_p_positive"] - 9.999000099990002e-05) > 1e-12:
        raise AssertionError("ML continuous branch-change P drifted")
    if ml["module_label_exact_permutation_p_positive"] <= 0.05:
        raise AssertionError("module-specific coordination was unexpectedly promoted")

    topo = json.loads((TIME / "japan38_continuous_branch_change_topology_sensitivity_v1.json").read_text(encoding="utf-8"))
    g = topo["global_mean_pairwise_rho_distribution"]
    if topo["bootstrap_trees_total"] != 1000 or topo["bootstrap_trees_usable"] != 1000:
        raise AssertionError("continuous topology ensemble incomplete")
    if not (g["q05"] > 0 and g["fraction_positive"] >= 0.95):
        raise AssertionError("global continuous coordinated-change topology gate failed")
    m = topo["within_minus_between_distribution"]
    if m["q05"] > 0 and m["fraction_positive"] >= 0.95:
        raise AssertionError("module-specific coordination must not be promoted")

    discrete = json.loads((TIME / "japan38_latest_module_transition_overlap_v2.json").read_text(encoding="utf-8"))
    if discrete["traits"]["orientation"]["resolved_tips"] != 20:
        raise AssertionError("orientation coverage drift")
    if discrete["traits"]["phyllary"]["resolved_tips"] != 10:
        raise AssertionError("phyllary coverage drift")
    if discrete["traits"]["stickiness"]["resolved_tips"] != 13:
        raise AssertionError("stickiness coverage drift")

    dtop = json.loads((TIME / "japan38_latest_module_overlap_topology_sensitivity_v2.json").read_text(encoding="utf-8"))
    if dtop["bootstrap_topology_sensitivity"]["bootstrap_trees_total"] != 1000:
        raise AssertionError("discrete topology ensemble incomplete")
    dist = dtop["bootstrap_topology_sensitivity"]["pairwise_spearman_distributions"]
    if dist["orientation__stickiness"]["fraction_positive"] >= 0.05:
        raise AssertionError("orientation-stickiness topology sensitivity drifted")
    if all(v["q05"] > 0 and v["fraction_positive"] >= 0.95 for v in dist.values()):
        raise AssertionError("discrete one-shared-transition-history was unexpectedly promoted")

    sticky = json.loads((ROOT / "data" / "evidence" / "jpn24_stickiness_extension_parsimony_v1.json").read_text(encoding="utf-8"))
    if sticky["stickiness"]["resolved_concepts_after"] != 13:
        raise AssertionError("JPN24 canonical stickiness coverage drift")
    if sticky["stickiness"]["ufboot1000_steps_min"] != 5 or sticky["stickiness"]["ufboot1000_steps_max"] != 5:
        raise AssertionError("JPN24 canonical stickiness recurrence drift")

    disposition = list(csv.DictReader((ROOT / "data" / "evidence" / "chapter2_analysis_disposition_v1.csv").open(encoding="utf-8", newline="")))
    if len(disposition) < 20:
        raise AssertionError("analysis disposition registry unexpectedly small")
    text = (CH / "META_SIM_DISPOSITION_V1.md").read_text(encoding="utf-8")
    require(text, ["Chapter 1", "Chapter 2", "function", "simulation"], "meta/simulation disposition")

    print("chapter2_time_axis_mainline_valid=true")
    print("continuous_units_n2=8")
    print("continuous_units_n5=8")
    print("continuous_topologies=1000")
    print("discrete_topologies=1000")
    print("submission_target=Journal_of_Evolutionary_Biology")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
