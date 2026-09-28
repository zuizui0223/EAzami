from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis/summarize_fdt1_tierA_effect_extraction_seed_v1.py"

spec = importlib.util.spec_from_file_location("tierA", SCRIPT)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


def test_tierA_seed_has_expected_studies_and_exact_quantitative_anchors():
    out = mod.build()
    assert out["effect_rows"] == 10
    assert out["independence_clusters"] == 8
    assert out["module_counts"] == {
        "display_quantity": 1,
        "orientation": 3,
        "phyllary_spine_defence": 5,
        "stickiness_mucilage": 1,
    }
    assert out["primary_fitness_rows"] == 8
    assert out["primary_fitness_rows_with_reported_mean_se"] == 2

    key = out["key_quantitative_seed"]
    assert key["Polygonatum_seed_number_lnRR_downward_over_upward"] == 0.251314
    assert key["Polygonatum_seed_number_delta_SE"] == 0.087706
    assert key["Thunia_fruit_set_lnRR_intact_over_removed_bracts"] == 1.255553
    assert key["Thunia_fruit_set_delta_SE"] == 0.42071
    assert key["Bejaria_fruit_set_lnRR_sticky_over_washed_from_reported_32_5pct_drop"] == 0.393043


def test_secondary_endpoints_do_not_inflate_independent_study_count():
    out = mod.build()
    effects = {r["effect_id"]: r for r in out["candidate_effects"]}
    assert effects["TA_ORI_POLY_SEEDSET"]["independence_cluster"] == effects["TA_ORI_POLY_SEEDNUM"]["independence_cluster"]
    assert effects["TA_DEF_THUNIA_DEP"]["independence_cluster"] == effects["TA_DEF_THUNIA_FRUIT"]["independence_cluster"]
    assert effects["TA_ORI_POLY_SEEDSET"]["primary_or_mediator"] == "secondary_fitness"
    assert effects["TA_DEF_THUNIA_DEP"]["primary_or_mediator"] == "mediator"


def test_provisional_delta_se_is_not_promoted_to_final_variance():
    out = mod.build()
    assert "provisional arithmetic transforms" in out["claim_boundary"]
    assert "one preregistered primary endpoint" in out["claim_boundary"]
    assert len(out["next_extraction_order"]) == 5
