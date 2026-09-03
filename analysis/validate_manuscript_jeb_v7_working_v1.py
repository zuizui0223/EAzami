#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "data" / "evidence"
MANUSCRIPT = ROOT / "docs" / "chapter2" / "MANUSCRIPT_JEB_V7_WORKING.md"
FIGMAP = ROOT / "docs" / "chapter2" / "JEB_V7_FIGURE_MAP.md"


def load_json(name: str) -> dict:
    return json.loads((EVID / name).read_text(encoding="utf-8"))


def require(text: str, token: str) -> None:
    if token not in text:
        raise AssertionError(f"required V7 manuscript token missing: {token!r}")


def forbid(text: str, token: str) -> None:
    if token.lower() in text.lower():
        raise AssertionError(f"forbidden V7 manuscript claim returned: {token!r}")


def main() -> None:
    text = MANUSCRIPT.read_text(encoding="utf-8")
    fig = FIGMAP.read_text(encoding="utf-8")
    hist = load_json("chapter2_historical_differentiation_final_summary_v1.json")
    eco = load_json("chapter2_orientation_environment_scale_partition_v1.json")
    rank = load_json("chapter2_orientation_origin_region_ranking_result_v1.json")

    # V7 identity / routing.
    require(text, "# Repeated mosaic assembly at unequal evolutionary depths in a young thistle radiation")
    require(text, "V7 WORKING SCIENTIFIC TEXT")
    require(fig, "positive assembly first")
    require(fig, "No three-trait `depth × ecological reach` correlation")

    # Positive historical core must agree with the frozen final summary.
    rec = hist["recurrence_and_depth"]
    assert rec["orientation"]["resolved_concepts"] == 20
    assert rec["orientation"]["minimum_changes_ml"] == 6
    assert rec["orientation"]["minimum_changes_ufboot_range"] == [4, 6]
    assert rec["orientation"]["minimum_changes_ufboot_median"] == 5
    assert rec["phyllary_posture"]["minimum_changes"] == 3
    assert rec["stickiness"]["minimum_changes"] == 5
    assert rec["shared_transition_localization"].startswith("0/3")
    assert rec["orientation"]["relative_depth_median_envelope"] == [0.795, 0.994]
    assert rec["phyllary_posture"]["relative_depth_median_envelope"] == [0.695, 1.0]
    assert rec["stickiness"]["relative_depth_median_envelope"] == [0.937, 0.954]

    for token in (
        "Thirty-six of 38",
        "four to six across 1,000 bootstrap topologies",
        "exactly three changes",
        "exactly five changes",
        "0.795–0.994",
        "0.695–1.000",
        "0.937–0.954",
        "Zero of three",
        "6/20 and 3/10",
        "5/13",
    ):
        require(text, token)

    # Equal-lability is specifically not identified.
    for bad in (
        "similarly labile",
        "same lability",
        "traits are equally labile",
        "modules are equally labile",
        "equal evolutionary rates",
    ):
        forbid(text, bad)
    require(text, "equal evolutionary changeability is not established")

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

    for token in (
        "0.30436",
        "0.00640",
        "0.00533",
        "0.874",
        "+1.320 to +1.330 SD",
        "54/54",
        "0.01715",
        "0.0349",
        "-0.975 to -0.967 SD",
    ):
        require(text, token)

    # Regional ranking remains a sensitivity-grid ordering, not ancestral probability.
    assert rank["classification"] == "relative_ordering_present_but_not_dominant"
    assert rank["n_chronology_scenarios"] == 94
    assert rank["n_region_by_chronology_rows"] == 376
    assert rank["region_rank_summary"]["southern_japan"]["rank1_count"] == 48
    assert rank["pairwise_win_fraction_matrix"]["southern_japan"]["taiwan"] == 61 / 94
    assert rank["pairwise_win_fraction_matrix"]["southern_japan"]["ryukyu_corridor"] == 61 / 94
    assert rank["pairwise_win_fraction_matrix"]["southern_japan"]["east_asia_core_corridor"] == 64 / 94
    for token in ("48/94", "61/94", "64/94", "75% dominance gate"):
        require(text, token)

    # Historical-cause ceiling.
    assert hist["orientation_historical_environment"]["chronology_pairs"] == 94
    assert hist["orientation_historical_environment"]["region_by_chronology_scenarios"] == 376
    assert hist["lineage_level_climate_context"]["tested_scenario_variable_combinations"] == 15472
    assert hist["lineage_level_climate_context"]["robust_event_level_classes"] == 0
    assert hist["global_sea_level_context"]["n_event_metric_classes"] == 21
    assert hist["global_sea_level_context"]["robust_event_metric_classes"] == 0
    for token in ("0.79–0.74 Ma", "15,472", "0/324", "0/21"):
        require(text, token)

    # #160 is intentionally not promoted before pinned-runtime validation.
    for provisional in ("1000/1000", "993/1000", "905/1000", "898/1000"):
        forbid(text, provisional)
    require(text, "inserted after the pinned-runtime workflow validates the result")

    # Claim-ceiling guards.
    for bad in (
        "environment was irrelevant",
        "environment is irrelevant",
        "ancestral-area probability is",
        "relative lineage depth is calendar time",
        "minimum changes are independent origins",
    ):
        forbid(text, bad)

    print(json.dumps({
        "status": "ok",
        "manuscript": str(MANUSCRIPT.relative_to(ROOT)),
        "figure_map": str(FIGMAP.relative_to(ROOT)),
        "historical_classification": hist["final_classification"],
        "ecological_classification": eco["classification"],
        "regional_ordering_classification": rank["classification"],
        "pr160_values_promoted": False,
    }, indent=2))


if __name__ == "__main__":
    main()
