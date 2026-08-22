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


def test_pair_randomizer_is_deterministic_and_balanced(tmp_path):
    source = tmp_path / "eligible.csv"
    source.write_text(
        "orientation_experiment_id,individual_id,population_id,capitulum_id,phenological_stage,natural_orientation_deg,eligible,exclusion_reason,notes\n"
        "E1,I1,P1,H1,anthesis,15,1,,\n"
        "E1,I1,P1,H2,anthesis,18,1,,\n"
        "E1,I1,P1,H3,anthesis,44,1,,\n"
        "E1,I1,P1,H4,anthesis,47,1,,\n"
        "E1,I2,P1,H5,anthesis,20,1,,\n"
        "E1,I2,P1,H6,anthesis,25,1,,\n",
        encoding="utf-8",
    )
    out1 = tmp_path / "assign1.csv"
    out2 = tmp_path / "assign2.csv"
    cmd = [
        sys.executable,
        str(ROOT / "analysis/randomize_aim2_orientation_pairs_v1.py"),
        str(source),
        str(out1),
        "--seed",
        "20260822",
    ]
    subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True, text=True)
    cmd[3] = str(out2)
    subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True, text=True)
    assert out1.read_text(encoding="utf-8") == out2.read_text(encoding="utf-8")

    with out1.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    by_block = {}
    for row in rows:
        by_block.setdefault(row["randomization_block"], []).append(row)
    assert len(rows) == 6
    assert len(by_block) == 3
    for block_rows in by_block.values():
        assert len(block_rows) == 2
        assert sorted(r["assignment"] for r in block_rows) == ["reoriented", "sham"]
        assert {r["randomization_seed"] for r in block_rows} == {"20260822"}
        assert block_rows[0]["matched_capitulum_id"] == block_rows[1]["capitulum_id"]
        assert block_rows[1]["matched_capitulum_id"] == block_rows[0]["capitulum_id"]
