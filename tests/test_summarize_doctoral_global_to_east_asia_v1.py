import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "data/evidence/doctoral_global_to_east_asia_hypothesis_map_v1.csv"
SUMMARY = ROOT / "data/evidence/doctoral_global_to_east_asia_summary_v1.json"


def test_summary_recomputes_and_preserves_claim_boundaries():
    frozen = json.loads(SUMMARY.read_text(encoding="utf-8"))
    subprocess.run(
        [sys.executable, str(ROOT / "analysis/summarize_doctoral_global_to_east_asia_v1.py")],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    recomputed = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert frozen == recomputed
    assert recomputed["hypothesis_count"] == 19
    assert recomputed["weakened"] == ["D3"]
    assert recomputed["evolutionary_history_not_yet_identified"] == ["E1", "C1", "C2", "O2", "R1"]


def test_azami_is_observational_and_eazami_owns_evolutionary_inference():
    with MAP.open(newline="", encoding="utf-8") as handle:
        rows = {r["hypothesis_id"]: r for r in csv.DictReader(handle)}
    for hid in ("G0", "G1", "G2"):
        assert "Azami" in rows[hid]["claim_boundary"]
        assert rows[hid]["current_status"].startswith("resolved_")
    assert rows["C2"]["current_status"] == "unresolved_direction"
    assert rows["O2"]["current_status"] == "unresolved_repeated_evolution"
    assert rows["E1"]["current_status"] == "unresolved_central_hypothesis"


def test_adaptation_and_parallelism_are_not_prematurely_promoted():
    text = SUMMARY.read_text(encoding="utf-8")
    s = json.loads(text)
    assert "Do not call the radiation adaptive" in s["adaptive_radiation_boundary"]
    with MAP.open(newline="", encoding="utf-8") as handle:
        rows = {r["hypothesis_id"]: r for r in csv.DictReader(handle)}
    assert "Do not call parallel evolution" in rows["O2"]["claim_boundary"]
    assert "tested separately" in rows["R1"]["claim_boundary"]
