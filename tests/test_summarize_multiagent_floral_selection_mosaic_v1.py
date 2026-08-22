import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/evidence/multiagent_floral_selection_mosaic_registry_v1.csv"
SUMMARY = ROOT / "data/evidence/multiagent_floral_selection_mosaic_summary_v1.json"


def test_registry_has_five_strict_dual_manipulation_programmes():
    with REGISTRY.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 9
    strict = [r for r in rows if r["strict_primary"] == "1"]
    assert len(strict) == 5
    assert len({r["program_cluster"] for r in strict}) == 5
    assert len({r["taxon"] for r in strict}) == 5
    assert all(r["pollination_manipulated"] == "1" for r in strict)
    assert all(r["antagonist_manipulated"] == "1" for r in strict)


def test_mosaic_summary_recomputes_and_rejects_fixed_agent_dominance():
    subprocess.run(
        [sys.executable, str(ROOT / "analysis/summarize_multiagent_floral_selection_mosaic_v1.py")],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    s = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert s["strict_factorial_program_count"] == 5
    assert s["strict_taxon_count"] == 5
    assert s["strict_dominance_counts"] == {"antagonist": 2, "mixed": 2, "pollinator": 1}
    assert s["leave_one_program_out_minimum_dominance_categories"] >= 2
    assert s["fixed_pollinator_dominance_falsified"] is True
    assert s["fixed_antagonist_dominance_falsified"] is True
    assert s["selection_mosaic_working_support"] is True


def test_context_dependence_is_common_but_not_universal():
    s = json.loads(SUMMARY.read_text(encoding="utf-8"))
    c = s["strict_context_dependence_or_nonadditivity"]
    assert c["supported_programs"] == 3
    assert c["total_programs"] == 5
    assert c["fraction"] == 0.6
    assert s["universal_nonadditivity_falsified"] is True
    assert s["universal_additivity_falsified"] is True
