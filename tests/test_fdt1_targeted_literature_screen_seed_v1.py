from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "data/evidence/fdt1_targeted_literature_screen_seed_v1.csv"
PROTOCOL = ROOT / "docs/FDT1_TARGETED_SYSTEMATIC_REVIEW_PROTOCOL_2026-08-24.md"


def rows():
    with SEED.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_verified_seed_has_unique_candidates_and_required_module_gaps():
    data = rows()
    ids = [r["candidate_id"] for r in data]
    assert len(ids) == len(set(ids))
    modules = {r["module"] for r in data}
    assert {"orientation", "stickiness_mucilage", "phyllary_spine_defence", "flower_colour_pigmentation"} <= modules
    assert len([r for r in data if r["module"] == "orientation" and r["existing_repo_overlap"] == "no"]) >= 4
    assert len([r for r in data if r["module"] == "stickiness_mucilage" and r["existing_repo_overlap"] == "no"]) >= 2


def test_direct_causal_candidates_are_high_priority_but_analogs_are_labeled():
    by_id = {r["candidate_id"]: r for r in rows()}
    for cid in ("ORI_EXT01", "ORI_EXT03", "ORI_EXT04", "STK_EXT01", "COL_EXT01", "COL_EXT02"):
        assert by_id[cid]["priority"] in {"P0", "P1"}
    assert "analog" in by_id["STK_EXT02"]["claim_boundary"].lower()
    assert by_id["DEF_EXT01"]["priority"] == "P2"


def test_protocol_forbids_cross_metric_false_pooling_and_requires_independence():
    text = PROTOCOL.read_text(encoding="utf-8")
    assert "Do **not** transform all evidence into one number." in text
    assert "Retain standardized `delta_beta` and its SE as a separate family." in text
    assert "Do not pool R2, slopes and response ratios." in text
    assert "repeated years, sites, traits and endpoints" in text
    assert "Do not lower inclusion criteria simply to reach `k >= 5`." in text


def test_existing_repo_anchors_are_not_counted_as_new_candidates():
    data = rows()
    base = [r for r in data if r["priority"] == "BASE"]
    assert {r["candidate_id"] for r in base} == {"ORI_BASE01", "STK_BASE01"}
    assert all(r["existing_repo_overlap"] == "yes" for r in base)
