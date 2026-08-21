import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_interaction_gate_hypothesis_audit_is_reproducible():
    subprocess.run(
        [sys.executable, str(ROOT / "analysis/summarize_interaction_gate_hypotheses_v1.py")],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    summary = json.loads((ROOT / "data/evidence/interaction_gate_hypothesis_summary_v1.json").read_text(encoding="utf-8"))
    by_id = {row["hypothesis_id"]: row for row in summary["hypotheses"]}
    assert summary["hypothesis_count"] == 6
    assert by_id["HGA0"]["status"] == "weakened"
    assert by_id["HGA0"]["direct_contradict"] >= 3
    assert by_id["HGA1"]["status"] == "working_support"
    assert by_id["HGA1"]["direct_support"] >= 3
    assert by_id["HGA2"]["status"] == "working_support"
    assert by_id["HGA3"]["status"] == "candidate_supported_not_identified"
    assert by_id["HGA4"]["status"] == "mechanistic_candidate"
    assert by_id["HGA5"]["status"] == "unresolved"
    assert by_id["HGA5"]["unique_support_groups"] >= 1
    assert by_id["HGA5"]["unique_contradict_groups"] >= 1


def test_no_duplicate_evidence_row_within_hypothesis_and_group():
    path = ROOT / "data/evidence/interaction_gate_hypothesis_evidence_v1.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    keys = [(r["hypothesis_id"], r["prediction_id"], r["evidence_id"]) for r in rows]
    assert len(keys) == len(set(keys))


def test_every_hypothesis_has_a_decisive_missing_test():
    path = ROOT / "data/evidence/interaction_gate_hypothesis_registry_v1.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 6
    assert all(r["decisive_missing_test"].strip() for r in rows)
