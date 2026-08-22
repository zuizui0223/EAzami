import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "data/evidence/doctoral_meta_resolution_gate_v1.json"


def test_meta_resolution_gate_recomputes():
    subprocess.run(
        [sys.executable, str(ROOT / "analysis/summarize_doctoral_meta_resolution_gate_v1.py")],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    s = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert s["hypothesis_count"] == 6
    assert s["meta_ceiling_reached_count"] == 6
    by = {r["hypothesis_id"]: r for r in s["hypotheses"]}
    assert by["HGA0"]["meta_general_status"] == "weakened"
    assert by["HGA1"]["meta_general_status"] == "working_support"
    assert by["HGA2"]["meta_general_status"] == "working_support"
    assert by["HGA3"]["meta_general_status"] == "working_meta_support_general"
    assert by["HGA4"]["meta_general_status"] == "mechanistic_candidate"
    assert by["HGA5"]["meta_general_status"] == "unresolved"


def test_focal_cirsium_is_not_overclaimed():
    s = json.loads(SUMMARY.read_text(encoding="utf-8"))
    by = {r["hypothesis_id"]: r for r in s["hypotheses"]}
    assert by["HGA3"]["focal_cirsium_status"] == "unidentified_agent_dominance_in_cirsium"
    assert by["HGA4"]["focal_cirsium_status"] == "unidentified_in_cirsium"
    assert by["HGA5"]["focal_cirsium_status"] == "unresolved"
    assert "does not mean" in s["claim_boundary"]


def test_every_ceiling_has_reopening_trigger_and_decisive_next_data():
    s = json.loads(SUMMARY.read_text(encoding="utf-8"))
    for row in s["hypotheses"]:
        assert row["meta_ceiling_reached"] == 1
        assert row["new_literature_reopens_gate_if"].strip()
        assert row["decisive_next_data"].strip()
