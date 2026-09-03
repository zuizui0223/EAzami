#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "data" / "evidence"
MANUSCRIPT = ROOT / "docs" / "chapter2" / "MANUSCRIPT_JEB_V7_WORKING.md"
FIGMAP = ROOT / "docs" / "chapter2" / "JEB_V7_FIGURE_MAP.md"


def load_json(name: str) -> dict:
    return json.loads((EVID / name).read_text(encoding="utf-8"))


def require(text: str, token: str) -> None:
    if token not in text:
        raise AssertionError(f"required V7 token missing: {token!r}")


def forbid(text: str, token: str) -> None:
    if token.lower() in text.lower():
        raise AssertionError(f"forbidden V7 claim returned: {token!r}")


def words(text: str) -> int:
    return len(re.findall(r"\b[\w'’*-]+\b", text))


def main() -> None:
    text = MANUSCRIPT.read_text(encoding="utf-8")
    fig = FIGMAP.read_text(encoding="utf-8")
    hist = load_json("chapter2_historical_differentiation_final_summary_v1.json")
    eco = load_json("chapter2_orientation_environment_scale_partition_v1.json")
    rank = load_json("chapter2_orientation_origin_region_ranking_result_v1.json")
    depth = load_json("chapter2_depth_ordering_robustness_result_v1.json")
    coverage = load_json("chapter2_depth_coverage_matched_sensitivity_result_v1.json")

    # V7 identity and JEB size gates.
    require(text, "# Repeated mosaic assembly at unequal evolutionary depths in a young thistle radiation")
    require(text, "V7 VALIDATED SCIENTIFIC TEXT")
    abstract = text.split("## Abstract\n\n", 1)[1].split("\n\n**Keywords:**", 1)[0]
    keywords = text.split("**Keywords:**", 1)[1].split("\n", 1)[0]
    keyword_n = len([x for x in keywords.split(";") if x.strip()])
    if words(abstract) > 250:
        raise AssertionError(f"abstract exceeds JEB 250-word limit: {words(abstract)}")
    if not 4 <= keyword_n <= 10:
        raise AssertionError(f"keyword count outside 4-10: {keyword_n}")
    body_before_refs = text.split("# References", 1)[0]
    if words(body_before_refs) > 7500:
        raise AssertionError(f"main text exceeds JEB 7500-word limit: {words(body_before_refs)}")

    # Positive historical core.
    rec = hist["recurrence_and_depth"]
    assert rec["orientation"]["minimum_changes_ml"] == 6
    assert rec["orientation"]["minimum_changes_ufboot_range"] == [4, 6]
    assert rec["phyllary_posture"]["minimum_changes"] == 3
    assert rec["stickiness"]["minimum_changes"] == 5
    assert rec["orientation"]["relative_depth_median_envelope"] == [0.795, 0.994]
    assert rec["phyllary_posture"]["relative_depth_median_envelope"] == [0.695, 1.0]
    assert rec["stickiness"]["relative_depth_median_envelope"] == [0.937, 0.954]
    assert rec["shared_transition_localization"].startswith("0/3")
    for token in (
        "Thirty-six of 38",
        "four to six across 1,000 bootstrap topologies",
        "0.795–0.994",
        "0.695–1.000",
        "0.937–0.954",
        "Zero of three",
        "6/20 and 3/10",
        "5/13",
    ):
        require(text, token)

    # Validated paired topology ordering (#160).
    assert depth["classification"] == "paired_topology_depth_ordering_reproduced_under_frozen_runtime"
    pair = {(r["deeper_candidate"], r["shallower_candidate"]): r for r in depth["pairwise_results"]}
    assert pair[("phyllary", "stickiness")]["fraction_prespecified_deeper_direction"] == 1.0
    assert pair[("phyllary", "orientation")]["fraction_prespecified_deeper_direction"] == 0.993
    assert pair[("orientation", "stickiness")]["fraction_prespecified_deeper_direction"] == 0.905
    assert depth["complete_lower_bound_ordering"]["count"] == 898
    for token in ("1000/1000", "993/1000", "905/1000", "898/1000", "-0.24762", "-0.11905", "-0.10857"):
        require(text, token)

    # Coverage-matched sensitivity (#164): central ordering survives, strict tails overlap.
    assert coverage["overall_classification"] == "unequal_depth_retained_against_matched_medians_but_strict_tail_overlap_remains"
    comp = {r["comparison"]: r for r in coverage["comparison_results"]}
    assert comp["phyllary_lt_orientation_median"]["count"] == 195
    assert comp["phyllary_lt_stickiness_5_5_median"]["count"] == 193
    assert comp["phyllary_lt_orientation_q05"]["fraction"] == 0.105
    assert comp["phyllary_lt_stickiness_5_5_q05"]["fraction"] == 0.11
    assert comp["phyllary_lt_stickiness_6_4_q05"]["fraction"] == 0.155
    for token in ("195/200 (97.5%)", "193/200 (96.5%)", "10.5%", "11.0–15.5%", "not a coverage-independent separation"):
        require(text, token)

    # Equal-lability / coverage overclaim guards.
    for bad in (
        "similarly labile",
        "same lability",
        "traits are equally labile",
        "modules are equally labile",
        "coverage-independent result",
        "fully insensitive to missing states",
    ):
        forbid(text, bad)
    require(text, "Equal evolutionary changeability remains unestablished")

    # Cross-scale orientation ecology.
    assert eco["classification"] == "orientation_environment_association_is_scale_partitioned"
    b12 = eco["orientation_scale_partition"]["BIO12_annual_precipitation"]
    b15 = eco["orientation_scale_partition"]["BIO15_precipitation_seasonality"]
    b1 = eco["orientation_scale_partition"]["BIO1_annual_mean_temperature"]
    assert b12["cross_scale_class"] == "among_only"
    assert b12["azami_among"]["q"] < 0.01 and b12["azami_within"]["q"] > 0.8
    assert b1["azami_within"]["q"] < 0.05 and b1["azami_among"]["q"] > 0.8
    assert b15["eazami_downward_minus_upward"]["accepted_topology_sign_consistency"] == "6/6"
    assert b15["eazami_downward_minus_upward"]["topology_x_species_loo_sign_consistency"] == "54/54"
    for token in ("0.30436", "0.00640", "0.00533", "0.874", "+1.320 to +1.330 SD", "54/54", "0.01715", "0.0349", "-0.975 to -0.967 SD"):
        require(text, token)

    # Regional ranking and historical-cause ceiling.
    assert rank["classification"] == "relative_ordering_present_but_not_dominant"
    assert rank["region_rank_summary"]["southern_japan"]["rank1_count"] == 48
    assert rank["pairwise_win_fraction_matrix"]["southern_japan"]["taiwan"] == 61 / 94
    assert rank["pairwise_win_fraction_matrix"]["southern_japan"]["east_asia_core_corridor"] == 64 / 94
    for token in ("48/94", "61/94", "64/94", "75% dominance gate", "0.79–0.74 Ma", "15,472", "0/324", "0/21"):
        require(text, token)

    # Figure map must route the validated layers correctly.
    for token in (
        "Figure 2",
        "1000/1000",
        "993/1000",
        "905/1000",
        "coverage-matched",
        "strict tail",
        "No three-trait",
    ):
        require(fig, token)

    # Anonymous review main-file boundary.
    for bad in ("# Data and code availability", "# Generative-AI disclosure"):
        forbid(text, bad)

    # General claim ceiling.
    for bad in (
        "environment was irrelevant",
        "environment is irrelevant",
        "minimum changes are independent origins",
        "relative lineage depth is calendar time",
        "posterior probability of ancestral area",
    ):
        forbid(text, bad)

    print(json.dumps({
        "status": "ok",
        "abstract_words": words(abstract),
        "main_text_words_before_references": words(body_before_refs),
        "keyword_count": keyword_n,
        "paired_depth_promoted": True,
        "coverage_sensitivity_promoted": True,
        "historical_classification": hist["final_classification"],
        "ecological_classification": eco["classification"],
        "regional_ordering_classification": rank["classification"],
    }, indent=2))


if __name__ == "__main__":
    main()
