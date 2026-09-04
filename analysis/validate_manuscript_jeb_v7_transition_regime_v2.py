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

    assert h1["classification"] == "repeated_u_to_d_transition_regime_concordance_supported"
    assert h1["panels"]["n5_primary"]["exact_primary_rank"]["count_at_least_observed"] == 16
    assert h1["panels"]["n5_primary"]["exact_primary_rank"]["n_maps"] == 792
    assert h1["panels"]["n3_sensitivity"]["exact_primary_rank"]["count_at_least_observed"] == 19
    assert h1["panels"]["n3_sensitivity"]["exact_primary_rank"]["n_maps"] == 1716

    assert region["classification"] == "transition_regime_concordance_strict_coverage_robust_but_region_sensitive"
    assert region["tests"]["strict_n10"]["exact_primary_rank"]["count_at_least_observed"] == 4
    assert region["tests"]["strict_n10"]["exact_primary_rank"]["n_maps"] == 126
    assert region["tests"]["japan_n5"]["exact_primary_rank"]["count_at_least_observed"] == 10
    assert region["tests"]["japan_n5"]["exact_primary_rank"]["n_maps"] == 56

    assert deletion["classification"] == "transition_regime_direction_not_single_taxon_dependent_but_exceptionality_sensitive"
    assert deletion["all_deletions_direction_pass"] is True
    assert deletion["n_deletions"] == 9
    assert deletion["n_exact_exceptionality_pass"] == 2

    assert geo["classification"] == "transition_regime_concordance_persists_after_linear_geography_residualization"
    assert geo["panels"]["strict_n10_primary"]["exact_primary_rank"]["count_at_least_observed"] == 5
    assert geo["panels"]["strict_n10_primary"]["exact_primary_rank"]["n_maps"] == 126

    assert internal["classification"] == "transition_regime_concordance_supported_on_internal_edges"
    assert internal["panels"]["strict_n10_primary"]["exact_primary_rank"]["count_at_least_observed"] == 3
    assert internal["panels"]["strict_n10_primary"]["exact_primary_rank"]["n_maps"] == 126
    assert internal["panels"]["n5_sensitivity"]["exact_primary_rank"]["count_at_least_observed"] == 29
    assert internal["panels"]["n5_sensitivity"]["exact_primary_rank"]["n_maps"] == 792

    assert combined["classification"] == "transition_regime_concordance_survives_combined_geography_and_terminal_edge_stress"
    assert combined["panels"]["strict_n10_primary"]["exact_primary_rank"]["count_at_least_observed"] == 3
    assert combined["panels"]["strict_n10_primary"]["exact_primary_rank"]["n_maps"] == 126
    assert combined["panels"]["n5_sensitivity"]["exact_primary_rank"]["count_at_least_observed"] == 29
    assert combined["panels"]["n5_sensitivity"]["exact_primary_rank"]["n_maps"] == 792

    h2 = current["orientation_transition_regime"]["h2"]
    assert h2["classification"] == "bidirectional_reversible_regime_supported"
    assert h2["both_positive_topologies"] == "6/6"
    assert h2["exact_bidirectional_floor_rank"] == "3/126 = 2.38%"
    hist = current["historical_persistence"]["h4"]
    assert hist["classification"] == "historical_regime_persistence_not_supported"
    assert hist["overall_match"] == "99/376 = 26.3%"

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
        "observed ancestral climate",
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
