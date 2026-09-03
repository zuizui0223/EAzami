#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "data" / "evidence"
RESULT = EVID / "chapter2_discrete_trait_occurrence_gate_sensitivity_v1.json"
FROZEN = EVID / "chapter2_ecological_explanatory_reach_v1.json"


def main() -> None:
    x = json.loads(RESULT.read_text(encoding="utf-8"))
    frozen = json.loads(FROZEN.read_text(encoding="utf-8"))

    assert x["contract_version"] == "chapter2_discrete_trait_occurrence_gate_sensitivity_v1"
    assert x["scope"].startswith("resolution audit")

    # The audit must preserve the original n>=10 zero-yield state exactly.
    assert frozen["phyllary_posture"]["status"] == "not_evaluable"
    assert frozen["stickiness"]["status"] == "not_evaluable"
    assert frozen["phyllary_posture"]["climate_panel_resolved_taxa_n_ge_10"] == 2
    assert frozen["stickiness"]["climate_panel_resolved_taxa_n_ge_10"] == 2
    assert x["thresholds"]["10"]["phyllary"]["state_counts"] == {"ascending": 2}
    assert x["thresholds"]["10"]["stickiness"]["state_counts"] == {"nonsticky": 2}

    # Lowering the same frozen occurrence gate has asymmetric consequences.
    assert x["thresholds"]["5"]["phyllary"]["state_counts"] == {"ascending": 3}
    assert x["thresholds"]["3"]["phyllary"]["state_counts"] == {"ascending": 3}
    assert x["thresholds"]["5"]["phyllary"]["state_diverse"] is False
    assert x["thresholds"]["5"]["stickiness"]["state_counts"] == {"nonsticky": 2, "sticky": 1}
    assert x["thresholds"]["3"]["stickiness"]["state_counts"] == {"nonsticky": 2, "sticky": 1}
    assert x["thresholds"]["5"]["stickiness"]["state_diverse"] is True

    # State diversity alone is not replicated trait identification.
    contrast = x["stickiness_n_ge_5_descriptive_single_lineage_contrast"]
    assert contrast["sticky_taxon"] == "Cirsium gyojanum"
    assert len(contrast["nonsticky_taxa"]) == 2
    assert 1.69 < contrast["sticky_minus_nonsticky_mean_panel_sd"]["BIO12"] < 1.71
    assert 1.71 < contrast["sticky_minus_nonsticky_mean_panel_sd"]["BIO15"] < 1.73
    assert "lineage-confounded" in contrast["warning"]

    # A separate environment-free occurrence harvest demonstrates that the
    # targeted niche artifact, not public occurrence absence, is part of the bottleneck.
    spatial = x["broader_environment_free_spatial_support"]
    assert spatial["phyllary"]["state_counts"] == {"ascending": 3, "appressed": 1}
    assert spatial["stickiness"]["state_counts"] == {"nonsticky": 6, "sticky": 6}
    assert x["classification"]["overall"] == "coverage_threshold_and_targeted_panel_composition_jointly_limit_ecological_evaluability"

    # The proposed depth x ecological-reach tradeoff cannot be converted into a
    # three-trait quantitative result when two trait-specific ecological reaches
    # are not identified.
    testability = x["depth_ecological_reach_hypothesis_testability"]
    assert testability["trait_status"]["orientation"]["usable_for_cross_trait_tradeoff"] is True
    assert testability["trait_status"]["phyllary"]["usable_for_cross_trait_tradeoff"] is False
    assert testability["trait_status"]["stickiness"]["usable_for_cross_trait_tradeoff"] is False
    assert testability["classification"] == "three_trait_depth_vs_ecological_reach_tradeoff_not_identifiable_from_current_public_panel"
    assert "do not plot" in testability["figure_rule"].lower()

    # This is an auxiliary resolution audit, not a reopening of V7 environmental fishing.
    boundary = " ".join(x["claim_boundary"]).lower()
    for forbidden in ("adaptation", "selection", "historical causation", "trait effect"):
        assert forbidden in boundary
    assert "not identified" in boundary

    print(json.dumps({
        "status": "ok",
        "phyllary": x["classification"]["phyllary"],
        "stickiness": x["classification"]["stickiness"],
        "overall": x["classification"]["overall"],
        "depth_ecological_reach": testability["classification"],
    }, indent=2))


if __name__ == "__main__":
    main()
