from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data" / "evidence" / "fdt1_ipomopsis_display_source_recovery_v1.csv"
MOD = ROOT / "analysis" / "validate_fdt1_ipomopsis_display_source_recovery_v1.py"
SPEC = importlib.util.spec_from_file_location("fdt1_ipomopsis_recovery", MOD)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_bounded_recovery_retains_direction_but_blocks_effect_promotion() -> None:
    result = MODULE.validate(AUDIT)
    assert result["routes_checked"] == 6
    assert result["primary_abstract_verified"] is True
    assert result["verified_numeric_fulltext_recovered"] is False
    assert result["group_means_dispersions_sample_sizes_recovered"] is False
    assert result["content_mismatch_artifact_rejected"] is True
    assert result["display_effect_size_ready"] is False
    assert result["cross_study_display_meta_analysis_ready"] is False
    assert "joint display benefit/enemy-cost direction" in result["claim_limit"]
    assert "Do not ingest" in result["do_not_repeat"]


def test_rejected_pdf_is_hash_and_identity_anchored() -> None:
    _, rows = MODULE.read_rows(AUDIT)
    rejected = next(row for row in rows if row["result_status"] == "rejected_content_mismatch")
    assert "0a30b448cb695bc9e96cf7a29e2cc2467c86af9731650936ea0b6065bfcaf3a3" in rejected["observed_content"]
    assert "Lesquerella fendleri" in rejected["observed_content"]
    assert "not Brody and Mitchell" in rejected["observed_content"]
