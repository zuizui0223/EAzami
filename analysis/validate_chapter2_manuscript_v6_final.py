#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "data" / "evidence"
CH = ROOT / "docs" / "chapter2"
MANUSCRIPT = CH / "MANUSCRIPT_JEB_V6_FINAL.md"
FIGMAP = CH / "JEB_QUESTION_RESULT_FIGURE_MAP_V6.md"
SI = CH / "JEB_SUPPORTING_INFORMATION_V4.md"
TITLE = CH / "JEB_TITLE_PAGE_TEMPLATE_V3.md"
COVER = CH / "JEB_COVER_LETTER_TEMPLATE_V3.md"
FIGSCRIPT = ROOT / "analysis" / "make_chapter2_jeb_figures_v6.py"
BUILDER = ROOT / "analysis" / "build_chapter2_jeb_docx_v4.py"


def load(name: str) -> dict:
    return json.loads((EVID / name).read_text(encoding="utf-8"))


def words(text: str) -> int:
    return len(re.findall(r"\b[\w'’–-]+\b", text))


def main() -> None:
    final = load("chapter2_historical_differentiation_final_summary_v1.json")
    orient = load("chapter2_orientation_differentiation_environment_v2_summary.json")
    atlas = load("chapter2_lineage_differentiation_environment_atlas_v1_summary.json")
    sea = load("chapter2_lineage_differentiation_sealevel_v1.json")

    assert final["status"] == "public_data_ceiling_reached_for_current_differentiation_trigger_programme"
    assert final["final_classification"] == "repeated_differentiation_resolved_but_recurring_tested_environmental_trigger_not_identified_under_public_data"

    rec = final["recurrence_and_depth"]
    assert rec["orientation"]["minimum_changes_ufboot_range"] == [4, 6]
    assert rec["orientation"]["minimum_changes_ml"] == 6
    assert rec["phyllary_posture"]["minimum_changes"] == 3
    assert rec["stickiness"]["minimum_changes"] == 5
    assert rec["orientation"]["relative_depth_median_envelope"] == [0.795, 0.994]
    assert rec["phyllary_posture"]["relative_depth_median_envelope"] == [0.695, 1.0]
    assert rec["stickiness"]["relative_depth_median_envelope"] == [0.937, 0.954]
    assert rec["shared_transition_localization"].startswith("0/3")

    cal = final["calendar_identifiability"]
    assert cal["trait_transitions_with_calendar_paleolocation_environment_gate"] == 1
    assert cal["additional_machine_readable_dated_tree_recovered"] is False

    oe = final["orientation_historical_environment"]
    assert oe["chronology_pairs"] == 94
    assert oe["paleolocation_regions"] == 4
    assert oe["region_by_chronology_scenarios"] == 376
    assert oe["robust_extreme_level_variables"] == 0
    assert oe["robust_absolute_change_variables"] == 0
    assert oe["robust_variability_variables"] == 0
    assert orient["cross_variable_summary"]["variables_with_robust_signed_direction"] == []

    lc = final["lineage_level_climate_context"]
    assert lc["n_bioclim_variables"] == 17
    assert lc["n_dated_lineage_contexts"] == 6
    assert lc["tested_scenario_variable_combinations"] == 15472
    assert lc["robust_event_level_classes"] == 0
    assert lc["recurring_context_candidates"] == []
    assert atlas["formal_result"]["n_event_level_classes"] == 324
    assert atlas["formal_result"]["n_event_level_robust_classes"] == 0

    sl = final["global_sea_level_context"]
    assert sl["n_event_metric_classes"] == 21
    assert sl["robust_event_metric_classes"] == 0
    assert sl["recurring_context_candidates"] == []
    assert sea["decision"] == "no_recurring_global_sea_level_context_survives_age_background_window_gates"

    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    required = (
        "Repeated capitulum differentiation at unequal evolutionary depths without a recurring coarse historical trigger",
        "0/324",
        "0/21",
        "94 admissible age pairs × four regions",
        "repeated trait differentiation is well resolved; repeated historical cause is not",
        final["final_classification"],
        "No Chapter 3, field, RAD-seq, mechanism or reproductive-fitness result is a submission gate",
    )
    for phrase in required:
        assert phrase in manuscript, phrase

    for i in range(1, 6):
        assert f"(Fig. {i}" in manuscript, f"missing main-text Figure {i} call"

    prohibited_mainline = (
        "pair-level concordance = 1/2",
        "partial coordinated remodelling inside",
        "current RSDS contrasts",
        "orientation × hydric exposure is the first experimental priority",
    )
    for phrase in prohibited_mainline:
        assert phrase not in manuscript, phrase

    abstract = manuscript.split("## Abstract", 1)[1].split("**Keywords:**", 1)[0]
    assert words(abstract) <= 250, words(abstract)

    main_before_refs = manuscript.split("# References", 1)[0]
    assert words(main_before_refs) <= 7500, words(main_before_refs)

    figmap = FIGMAP.read_text(encoding="utf-8")
    for phrase in ("0/324", "0/21", "Main-text exclusion rule", "Figure 5"):
        assert phrase in figmap, phrase

    si = SI.read_text(encoding="utf-8")
    for phrase in ("0/324", "0/21", "Calendar identifiability funnel", "V5 evidence retained outside the V6 main spine"):
        assert phrase in si, phrase

    title = TITLE.read_text(encoding="utf-8")
    cover = COVER.read_text(encoding="utf-8")
    active_title = "Repeated capitulum differentiation at unequal evolutionary depths without a recurring coarse historical trigger in a young thistle radiation"
    assert active_title in title
    assert active_title in cover
    assert "0/324" in cover and "0/21" in cover

    assert FIGSCRIPT.exists()
    assert BUILDER.exists()
    builder = BUILDER.read_text(encoding="utf-8")
    for source in (
        "MANUSCRIPT_JEB_V6_FINAL.md",
        "JEB_SUPPORTING_INFORMATION_V4.md",
        "JEB_TITLE_PAGE_TEMPLATE_V3.md",
        "JEB_COVER_LETTER_TEMPLATE_V3.md",
        "figures_v6",
        "submission_package_v6",
    ):
        assert source in builder, source
    for stale in (
        "MANUSCRIPT_JEB_V5.md",
        "JEB_SUPPORTING_INFORMATION_V3.md",
        "figures_v5",
        "submission_package_v5",
    ):
        assert stale not in builder, stale

    print("chapter2_manuscript_v6_final: PASS")
    print(f"abstract_words={words(abstract)}")
    print(f"main_before_refs_words={words(main_before_refs)}")


if __name__ == "__main__":
    main()
