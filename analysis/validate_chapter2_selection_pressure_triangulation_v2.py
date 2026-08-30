#!/usr/bin/env python3
"""Validate the explanatory-ranking extension after the canonical v1 contract.

The canonical v1 validator owns the scientific source-of-truth checks for history,
ecology, occurrence-source sensitivity, function priors and the temporal gate.  This
v2 validator intentionally adds only the new ranking-document and exact matrix-scope
checks so it cannot drift by re-encoding internal summary structures.
"""
from __future__ import annotations

import csv
from pathlib import Path

import validate_chapter2_selection_pressure_triangulation_v1 as base

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "data" / "evidence"
MATRIX = EVID / "chapter2_selection_pressure_triangulation_v1.csv"
DOC = ROOT / "docs" / "chapter2" / "SELECTION_PRESSURE_EXPLANATORY_RANKING_V1.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    # Reuse the already validated canonical scientific contract rather than
    # duplicating its JSON-shape assumptions here.
    base.main()

    rows = read_csv(MATRIX)
    keyed = {(r["trait_id"], r["factor_domain"]): r for r in rows}
    expected_keys = {
        ("orientation", "hydric_regime"),
        ("orientation", "thermal_regime"),
        ("orientation", "radiation_pollinator_presentation"),
        ("colour_continuous", "radiative_environment"),
        ("phyllary_posture", "enemy_access_wetting"),
        ("stickiness", "enemy_community_and_cost"),
        ("capitulum_outline_shape", "multivariate_environment"),
        ("involucre_architecture_armature", "hydric_radiative_mechanical_enemy"),
        ("display_quantity", "pollinator_enemy_resource"),
        ("whole_capitulum", "common_lability_or_single_syndrome"),
    }
    assert len(rows) == len(keyed) == 10
    assert set(keyed) == expected_keys

    hydric = keyed[("orientation", "hydric_regime")]
    assert hydric["eazami_repeat_count"] == "4-6"
    assert hydric["concordance_class"] == "multi_axis_concordant_event_alignment_missing"
    assert hydric["explanatory_tier"] == "T2_cross_axis_selection_pressure_candidate"
    assert hydric["eazami_event_window_status"] == "blocked_exact_dated_tree_crosswalk"
    assert "BIO12" in hydric["azami_spatial_evidence"]
    assert "BIO15" in hydric["eazami_present_ecology"]
    assert "no ancestry-matched focal Japanese orientation-to-filled-achene path" in hydric["fitness_evidence"]

    thermal = keyed[("orientation", "thermal_regime")]
    assert thermal["concordance_class"] == "scale_dependent_or_confounded"
    assert thermal["explanatory_tier"].startswith("T1_")

    colour = keyed[("colour_continuous", "radiative_environment")]
    assert colour["eazami_repeat_count"] == "not_identified"
    assert colour["concordance_class"] == "spatial_candidate_temporal_history_unidentified"
    assert colour["explanatory_tier"].startswith("T1_")

    phyllary = keyed[("phyllary_posture", "enemy_access_wetting")]
    assert phyllary["eazami_repeat_count"] == "3"
    assert phyllary["concordance_class"] == "history_recurrence_driver_unidentified"

    sticky = keyed[("stickiness", "enemy_community_and_cost")]
    assert sticky["eazami_repeat_count"] == "5"
    assert sticky["concordance_class"] == "history_recurrence_generic_defence_weakened"
    assert "neutralization result weakens" in sticky["mechanism_prior"]

    whole = keyed[("whole_capitulum", "common_lability_or_single_syndrome")]
    assert whole["concordance_class"] == "universal_synchronized_syndrome_not_supported"
    assert whole["eazami_event_window_status"] == "not_applicable"

    # No row may be promoted past the current observational tiers. P and F remain
    # unresolved/blocked/not-applicable rather than being inferred from R/T/S/C/L.
    for row in rows:
        assert row["eazami_event_window_status"].startswith(
            ("blocked_", "not_evaluable", "not_applicable")
        ), row
        assert not row["explanatory_tier"].startswith(("T3", "T4", "T5")), row
        assert row["forbidden_upgrade"].strip(), row
        assert row["next_decisive_test"].strip(), row

    text = DOC.read_text(encoding="utf-8")
    required_phrases = [
        "independent evidence dimensions converge",
        "Why no numerical score is used",
        "Orientation × hydric exposure",
        "hydric-domain convergence across independent facets",
        "Orientation × thermal regime is informative because it does not align simply",
        "repeated history does not rescue the generic mechanism",
        "Historical pollinator/enemy turnover needs its own data series",
        "Multi-axis concordance strengthens a candidate selective-pressure explanation",
        "No current trait reaches P or F.",
        "This is a ranking of **current explanatory closure**, not biological importance.",
    ]
    for phrase in required_phrases:
        assert phrase in text, phrase

    forbidden_affirmations = [
        "hydric exposure demonstrates adaptation",
        "BIO12 and BIO15 are the same variable",
        "stickiness is an adaptive defence",
        "relative lineage-depth gives event age",
        "visitor abundance proves pollination",
    ]
    low = text.casefold()
    for phrase in forbidden_affirmations:
        assert phrase.casefold() not in low, phrase

    print("Chapter 2 selection-pressure explanatory ranking v2: VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
