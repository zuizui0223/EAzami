#!/usr/bin/env python3
"""Validate Chapter 2 temporal selection-pressure triangulation.

This validator intentionally checks a synthesis of frozen evidence. It does not
manufacture calendar event ages, cross-trait P values or causal/adaptive scores.
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "data" / "evidence"
DOC = ROOT / "docs" / "chapter2" / "TEMPORAL_SELECTION_PRESSURE_TRIANGULATION_V1.md"
CONTRACT = EVID / "chapter2_temporal_selection_pressure_contract_v1.json"
LEDGER = EVID / "chapter2_temporal_selection_pressure_concordance_v1.csv"
CLOSURE = EVID / "chapter2_space_time_public_data_closure_v1.csv"
RELATIVE = EVID / "japan38_relative_event_depth_v1.json"
ECOLOGY = EVID / "chapter2_ecological_explanatory_reach_v1.json"
TAIWAN = EVID / "fdt4_taiwan_multisource_orientation_sensitivity_v1.json"
CONTINUOUS = EVID / "chapter2_time_axis_compute" / "continuous_primary_phylogenetic_structure_v1.csv"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def close(actual: float, expected: float, tol: float = 1e-9) -> None:
    assert math.isclose(float(actual), float(expected), rel_tol=0.0, abs_tol=tol), (actual, expected)


def main() -> int:
    contract = read_json(CONTRACT)
    ledger_rows = read_csv(LEDGER)
    closure_rows = {r["trait_id"]: r for r in read_csv(CLOSURE)}
    rel = read_json(RELATIVE)
    eco = read_json(ECOLOGY)
    tw = read_json(TAIWAN)
    continuous = read_csv(CONTINUOUS)
    text = DOC.read_text(encoding="utf-8")

    assert contract["contract_version"] == "chapter2_temporal_selection_pressure_contract_v1"
    assert contract["absolute_time_gate"]["status"] == "not_evaluable"
    assert contract["historical_environment_gate"]["status"] == "not_evaluable"
    assert contract["current_decision"]["orientation"] == "space_time_selection_pressure_candidate"
    assert "single published radiation age" in contract["absolute_time_gate"]["prohibited_shortcut"]

    expected_traits = {
        "orientation",
        "phyllary_posture",
        "stickiness",
        "colour_continuous",
        "capitulum_outline_shape",
        "involucre_architecture_armature",
    }
    rows = {r["trait_id"]: r for r in ledger_rows}
    assert set(rows) == expected_traits

    # Discrete recurrence and relative-placement values must reproduce the
    # admitted exact minimum-history artifact rather than prose estimates.
    expected = {
        "orientation": (6, 4, 5, 6, 0.7952380952380952, 0.9942857142857143),
        "phyllary_posture": (3, 3, 3, 3, 0.6952380952380953, 1.0),
        "stickiness": (5, 5, 5, 5, 0.9371428571, 0.9542857143),
    }
    rel_key = {"orientation": "orientation", "phyllary_posture": "phyllary", "stickiness": "stickiness"}
    for trait, values in expected.items():
        row = rows[trait]
        ml, lo, med, hi, depth_lo, depth_hi = values
        assert int(row["ml_minimum_changes"]) == ml
        assert int(row["ufboot_minimum_changes"]) == lo
        assert int(row["ufboot_median_changes"]) == med
        assert int(row["ufboot_maximum_changes"]) == hi
        close(float(row["median_relative_depth_lower"]), depth_lo, 2e-9)
        close(float(row["median_relative_depth_upper"]), depth_hi, 2e-9)

        artifact = rel["ufboot1000_relative_event_depth"][rel_key[trait]]["metric_summaries"]
        assert int(artifact["minimum_steps"]["min"]) == lo
        assert int(artifact["minimum_steps"]["median"]) == med
        assert int(artifact["minimum_steps"]["max"]) == hi
        if trait != "stickiness":
            close(artifact["mean_relative_lineage_depth_lower_bound"]["median"], depth_lo)
            close(artifact["mean_relative_lineage_depth_upper_bound"]["median"], depth_hi)

    # The stable ecological direction and source-sensitive threshold class are
    # distinct claims and both must remain visible.
    orient = rows["orientation"]
    assert orient["ecological_domain_concordance"] == "hydric_cross_facet_concordance_with_scale_specific_thermal_signal"
    assert orient["explanatory_class"] == "strongest_public_data_space_time_selection_pressure_candidate"
    assert "annual precipitation amount" in orient["azami_spatial_gradient"]
    assert "precipitation seasonality" in orient["eazami_current_ecology"]
    assert eco["orientation"]["status"] == "unresolved"
    assert eco["orientation"]["chelsa_bio15"]["accepted_topology_sign_agreement"] == 1.0
    assert eco["orientation"]["chelsa_bio15"]["species_loo_evaluations"] == 54
    assert eco["orientation"]["chelsa_bio01"]["accepted_topology_sign_agreement"] == 1.0
    assert tw["native_tbn_tier"]["frozen_rule_status"] == "tendency_supported"
    assert tw["non_gbif_tbn_tier"]["frozen_rule_status"] == "unresolved"
    assert tw["decision"]["primary_status_change"] is False

    # Existing cross-repository closure must agree with the new causal-evidence
    # interpretation, but the new ledger must add temporal identifiability.
    assert closure_rows["orientation"]["cross_axis_class"] == "priority_space_time_ecology_bridge"
    assert closure_rows["colour_continuous"]["cross_axis_class"] == "space_only_radiation_sorting_candidate"
    assert closure_rows["phyllary_posture"]["cross_axis_class"] == "history_only_boundary"
    assert closure_rows["stickiness"]["cross_axis_class"] == "history_only_boundary"

    # All eight primary continuous units remain unpromoted after the frozen
    # corrected history family. Colour can therefore be spatially strong while
    # its Japanese temporal depth remains unresolved.
    primary_n2 = [r for r in continuous if r["scope"] == "nobs_ge_2"]
    assert len(primary_n2) == 8
    assert {r["history_support_class"] for r in primary_n2} == {"two_sided_not_supported"}
    assert rows["colour_continuous"]["explanatory_class"] == "strong_spatial_candidate_temporal_depth_unresolved"

    # No trait currently has admitted dated transition windows or historical
    # environmental correspondence. Missing ontology/coverage is unidentified,
    # not directional discordance.
    for row in ledger_rows:
        assert row["historical_environmental_alignment"].startswith("not_evaluable_")
    assert rows["phyllary_posture"]["ecological_domain_concordance"].startswith("unidentified_")
    assert rows["stickiness"]["ecological_domain_concordance"].startswith("unidentified_")

    required = [
        "repeated history (R)",
        "relative event placement (T)",
        "present spatial gradient (S)",
        "present state–ecology correspondence (C)",
        "dated historical environmental correspondence (P)",
        "trait-to-function-to-fitness evidence (F)",
        "hydric cross-facet concordance",
        "Current taxon niche centroids are not historical environments",
        "Do not infer calendar event ages from relative lineage-depth",
    ]
    for phrase in required:
        assert phrase in text, phrase

    forbidden = [
        "rain adaptation is demonstrated",
        "adaptive convergence is supported",
        "relative lineage-depth gives calendar time",
        "BIO12 and BIO15 reproduce the same coefficient",
        "stickiness is a demonstrated defence",
    ]
    lower = text.lower()
    for phrase in forbidden:
        assert phrase.lower() not in lower, phrase

    print("temporal selection-pressure triangulation: validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
