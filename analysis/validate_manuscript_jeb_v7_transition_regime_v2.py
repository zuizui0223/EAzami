#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "data" / "evidence"
MANUSCRIPT = ROOT / "docs" / "chapter2" / "MANUSCRIPT_JEB_V7_WORKING.md"
FIGMAP = ROOT / "docs" / "chapter2" / "JEB_V7_FIGURE_MAP.md"


def load(name: str) -> dict:
    return json.loads((EVID / name).read_text(encoding="utf-8"))


def require(text: str, token: str) -> None:
    if token not in text:
        raise AssertionError(f"required transition-regime token missing: {token!r}")


def forbid(text: str, token: str) -> None:
    if token.lower() in text.lower():
        raise AssertionError(f"forbidden transition-regime claim present: {token!r}")


def words(text: str) -> int:
    return len(re.findall(r"\b[\w'’*-]+\b", text))


def rank_eq(block: dict, count: int, n: int) -> None:
    rank = block["exact_primary_rank"]
    assert rank["count_at_least_observed"] == count
    assert rank["n_maps"] == n


def main() -> None:
    text = MANUSCRIPT.read_text(encoding="utf-8")
    fig = FIGMAP.read_text(encoding="utf-8")

    current = load("chapter2_current_claims_h1_h4_v1.json")
    h1 = load("chapter2_orientation_transition_regime_hypothesis_result_v1.json")
    region = load("chapter2_orientation_transition_regime_robustness_result_v1.json")
    deletion = load("chapter2_orientation_transition_regime_single_deletion_result_v1.json")
    geo = load("chapter2_orientation_transition_regime_geography_residual_result_v1.json")
    internal = load("chapter2_orientation_transition_regime_internal_edge_result_v1.json")
    combined = load("chapter2_orientation_transition_regime_combined_stress_result_v1.json")

    # H1 frozen compact result.
    assert h1["version"] == "chapter2_orientation_transition_regime_hypothesis_result_v1"
    assert h1["classification"] == "repeated_u_to_d_transition_regime_concordance_supported"
    rank_eq(h1["n5_primary"], 16, 792)
    rank_eq(h1["n3_sensitivity"], 19, 1716)
    assert h1["n5_primary"]["bio15_only_rank"]["count_at_least_observed"] == 123
    assert h1["n5_primary"]["lower_bio1_rank"]["count_at_least_observed"] == 15

    # R1: strict coverage / region boundary.
    assert region["version"] == "chapter2_orientation_transition_regime_robustness_result_v1"
    assert region["classification"] == "transition_regime_concordance_strict_coverage_robust_but_region_sensitive"
    rank_eq(region["strict_n10"], 4, 126)
    rank_eq(region["japan_n5"], 10, 56)
    assert region["strict_n10"]["bio15_only_rank"]["count_at_least_observed"] == 7
    assert region["strict_n10"]["lower_bio1_rank"]["count_at_least_observed"] == 8

    # R1b: one-taxon deletion.
    assert deletion["classification"] == "transition_regime_direction_not_single_taxon_dependent_but_exceptionality_sensitive"
    assert deletion["all_deletions_direction_pass"] is True
    assert deletion["n_deletions"] == 9
    assert deletion["n_exact_exceptionality_pass"] == 2

    # R2: linear geography residualization.
    assert geo["version"] == "chapter2_orientation_transition_regime_geography_residual_result_v1"
    assert geo["classification"] == "transition_regime_concordance_persists_after_linear_geography_residualization"
    rank_eq(geo["strict_n10_primary"], 5, 126)
    rank_eq(geo["n5_sensitivity"], 41, 792)
    assert geo["strict_n10_primary"]["composite_positive_topologies"] == "6/6"

    # R3: internal-edge-only.
    assert internal["version"] == "chapter2_orientation_transition_regime_internal_edge_result_v1"
    assert internal["classification"] == "transition_regime_concordance_supported_on_internal_edges"
    rank_eq(internal["strict_n10_primary"], 3, 126)
    rank_eq(internal["n5_sensitivity"], 29, 792)
    assert internal["strict_n10_primary"]["internal_edges_scored_per_topology"] == 7
    assert internal["n5_sensitivity"]["internal_edges_scored_per_topology"] == 10

    # R4: combined geography + internal-edge stress.
    assert combined["version"] == "chapter2_orientation_transition_regime_combined_stress_result_v1"
    assert combined["classification"] == "transition_regime_concordance_survives_combined_geography_and_terminal_edge_stress"
    rank_eq(combined["strict_n10_primary"], 3, 126)
    rank_eq(combined["n5_sensitivity"], 29, 792)
    assert combined["strict_n10_primary"]["composite_positive_topologies"] == "6/6"
    assert "No further coarse environmental predictors" in combined["stop_rule"]

    # Existing biological H2 and H4 are sourced from the authoritative compact synthesis.
    h2 = current["orientation_transition_regime"]["h2"]
    assert h2["classification"] == "bidirectional_reversible_regime_supported"
    assert h2["both_positive_topologies"] == "6/6"
    assert h2["exact_bidirectional_floor_rank"] == "3/126 = 2.38%"
    hist = current["historical_persistence"]["h4"]
    assert hist["classification"] == "historical_regime_persistence_not_supported"
    assert hist["overall_match"] == "99/376 = 26.3%"
    assert hist["chronologies_match_4_of_4_regions"] == "6/94"

    for token in (
        "## Fixed transition-regime concordance and falsification tests",
        "## Orientation transitions track a fixed East-Asian present-niche regime",
        "16/792 (2.02%)",
        "19/1716 = 1.11%",
        "4/126 = 3.17%",
        "7/126 = 5.56%",
        "8/126 = 6.35%",
        "3/126 (2.38%)",
        "10/56 = 17.86%",
        "5/126 (3.97%)",
        "29/792 (3.66%)",
        "## The present transition regime is not supported as the bounded origin regime",
        "99/376 (26.3%)",
        "20/94 (21.3%)",
        "9/94 (9.6%)",
        "41/94 (43.6%)",
        "29/94 (30.9%)",
        "origin-versus-current-regime decoupling",
        "scale- and history-dependent",
    ):
        require(text, token)

    for token in (
        "Panel 3B — fixed transition-regime test",
        "16/792 = 2.02%",
        "4/126 = 3.17%",
        "Panel 3C — falsification ladder for U->D tracking",
        "10/56 = 17.86%",
        "5/126 = 3.97%",
        "3/126 = 2.38%",
        "29/792 = 3.66%",
        "Panel 3D — history-conditioned tip-contrast calibration",
        "99/376 = 26.3%",
    ):
        require(fig, token)

    for bad in (
        "BIO15 causes orientation",
        "BIO1 causes orientation",
        "precipitation seasonality caused orientation",
        "temperature caused orientation",
        "transition-regime test proves adaptation",
        "transition-regime test proves selection",
        "internal environmental values are observed ancestral climates",
        "universal Japan-only rule is supported",
    ):
        forbid(text, bad)

    abstract = text.split("## Abstract\n\n", 1)[1].split("\n\n**Keywords:**", 1)[0]
    body = text.split("# References", 1)[0]
    if words(abstract) > 250:
        raise AssertionError(f"abstract exceeds 250 words: {words(abstract)}")
    if words(body) > 7500:
        raise AssertionError(f"main text exceeds 7500 words: {words(body)}")

    print(json.dumps({
        "status": "ok",
        "abstract_words": words(abstract),
        "main_text_words_before_references": words(body),
        "h1_classification": h1["classification"],
        "regional_boundary_classification": region["classification"],
        "single_deletion_classification": deletion["classification"],
        "geography_residual_classification": geo["classification"],
        "internal_edge_classification": internal["classification"],
        "combined_stress_classification": combined["classification"],
        "bidirectional_classification": h2["classification"],
        "historical_persistence_classification": hist["classification"],
        "coarse_public_data_stop_rule_reached": True,
    }, indent=2))


if __name__ == "__main__":
    main()
