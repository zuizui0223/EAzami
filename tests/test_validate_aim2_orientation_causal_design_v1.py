import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "data/evidence/aim2_orientation_causal_design_v1.json"
REGISTRY = ROOT / "data/evidence/aim2_orientation_causal_hypothesis_registry_v1.csv"
ASSIGN = ROOT / "sampling/aim2_orientation_treatment_assignment_v1.csv"


def test_orientation_design_recomputes_and_is_empirically_unresolved():
    subprocess.run(
        [sys.executable, str(ROOT / "analysis/validate_aim2_orientation_causal_design_v1.py")],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    s = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert s["hypothesis_count"] == 6
    assert s["hypotheses"] == ["ORI0", "ORI1", "ORI2", "ORI3", "ORI4", "ORI5"]
    assert s["all_preregistered_process_pathways_schema_ready"] is True
    assert s["field_execution_ready"] is True
    assert s["empirical_result_available"] is False
    assert s["pathway_readiness"]["ORI0_null_compatible"]["supportable_now"] is False


def test_registry_has_falsifiers_and_claim_boundaries():
    with REGISTRY.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 6
    assert all(r["decision_rule"].strip() for r in rows)
    assert all(r["falsifier"].strip() for r in rows)
    assert all(r["claim_boundary"].strip() for r in rows)
    assert any(r["hypothesis_id"] == "ORI5" for r in rows)


def test_assignment_ledger_is_one_row_per_capitulum_when_populated():
    with ASSIGN.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    capitula = [r["capitulum_id"] for r in rows if r["capitulum_id"]]
    assert len(capitula) == len(set(capitula))
