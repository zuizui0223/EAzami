from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis/meta_analyze_existing_capitulum_module_pollinator_analogs_v1.py"

spec = importlib.util.spec_from_file_location("module_analogs", SCRIPT)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


def test_existing_pollinator_gradients_reproduce_module_analog_seeds():
    out = mod.build()
    by = {x["module"]: x for x in out["modules"]}

    display = by["display_quantity_analog"]
    assert display["effect_rows"] == 14
    assert display["article_count"] == 5
    assert display["article_balanced_mean_abs_delta_beta"] == 0.09515
    assert display["leave_one_article_out_range"] == [0.057688, 0.107188]

    pigment = by["pigmentation_sensory_analog"]
    assert pigment["effect_rows"] == 8
    assert pigment["article_count"] == 2
    assert pigment["article_balanced_mean_abs_delta_beta"] == 0.21675
    assert pigment["leave_one_article_out_range"] == [0.0835, 0.35]
    assert pigment["interpretation_status"] == "seed_only_k_lt_3"

    size = by["flower_size_display_proxy"]
    assert size["effect_rows"] == 7
    assert size["article_count"] == 5
    assert size["article_balanced_mean_abs_delta_beta"] == 0.0695

    efficiency = by["pollination_efficiency_reference"]
    assert efficiency["effect_rows"] == 4
    assert efficiency["article_count"] == 3
    assert efficiency["article_balanced_mean_abs_delta_beta"] == 0.143667


def test_pilot_refuses_cross_module_ranking_and_keeps_missing_modules_explicit():
    out = mod.build()
    assert "no EAzami module ranking is authorized" in out["decision"]
    assert "orientation, spine/phyllary and stickiness" in out["decision"]
    assert "not the final FDT1" in out["claim_boundary"]
