from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data" / "evidence" / "fdt1_lilium_orientation_source_recovery_v1.csv"
MOD = ROOT / "analysis" / "validate_fdt1_lilium_orientation_source_recovery_v1.py"
SPEC = importlib.util.spec_from_file_location("fdt1_lilium_recovery", MOD)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_bounded_recovery_preserves_interaction_but_blocks_generic_effect() -> None:
    result = MODULE.validate(AUDIT)
    assert result["routes_checked"] == 6
    assert result["primary_abstract_verified"] is True
    assert result["verified_numeric_fulltext_recovered"] is False
    assert result["orientation_by_slope_coefficient_and_covariance_recovered"] is False
    assert result["generic_orientation_response_ratio_identified"] is False
    assert result["effect_size_ready"] is False
    assert result["cross_study_orientation_meta_analysis_addition_ready"] is False
    assert result["retained_estimand"] == "direction of the orientation-by-slope interaction"
    assert "preserving slope as a continuous moderator" in result["reopen_condition"]


def test_audit_records_publisher_redirect_and_unresolved_oa_badge() -> None:
    _, rows = MODULE.read_rows(AUDIT)
    statuses = {row["result_status"] for row in rows}
    assert "publisher_redirects_to_abstract" in statuses
    assert "open_access_label_unresolved" in statuses
    assert "author_request_only" in statuses
