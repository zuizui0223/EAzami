from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXTRACT = ROOT / "data/evidence/fdt1_ipomoea_purpurea_chs_heat_cell_extract_v1.csv"
SUMMARY = ROOT / "data/evidence/fdt1_ipomoea_purpurea_chs_heat_extract_summary_v1.json"
SCRIPT = ROOT / "analysis/validate_fdt1_ipomoea_purpurea_chs_heat_extract_v1.py"
MARGINS = ROOT / "data/evidence/fdt1_ipomoea_purpurea_chs_heat_descriptive_margins_v1.json"
MARGIN_SCRIPT = ROOT / "analysis/summarize_fdt1_ipomoea_purpurea_chs_heat_descriptive_margins_v1.py"


def read_rows():
    with EXTRACT.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_primary_table_extract_is_complete_and_preserves_design_debt():
    rows = read_rows()
    assert len(rows) == 64
    assert len({row["cell_id"] for row in rows}) == 64
    assert sum(int(row["n_plant_day_pollination_pairs"]) for row in rows) == 1342
    by_id = {row["cell_id"]: row for row in rows}
    assert by_id["IPUR_CELL_001"]["mean_fertilization_success"] == "0.237"
    assert by_id["IPUR_CELL_064"]["mean_fertilization_success"] == "0.563"
    assert {row["environment_replication"] for row in rows} == {
        "one_chamber_per_temperature_and_one_light_subchamber_per_temperature"
    }


def test_recomputed_summary_matches_frozen_summary(tmp_path):
    output = tmp_path / "summary.json"
    subprocess.run(
        [sys.executable, str(SCRIPT), str(EXTRACT), "--output", str(output)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(output.read_text(encoding="utf-8")) == json.loads(
        SUMMARY.read_text(encoding="utf-8")
    )


def test_summary_does_not_call_visible_anthocyanin_or_independent_environment():
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert summary["complete_two_level_factorial"] is True
    assert summary["readiness"] == "bounded_effect_extraction_ready_not_pool_ready"
    assert "one_chamber_per_temperature" in summary["blocking_design_features"]
    assert "not an anthocyanin-only visible-petal effect" in summary["claim_boundary"]
    assert "do not treat the 64 cells as independent study effects" in summary["claim_boundary"]


def test_descriptive_margins_reproduce_direction_without_inventing_uncertainty(tmp_path):
    output = tmp_path / "margins.json"
    subprocess.run(
        [sys.executable, str(MARGIN_SCRIPT), str(EXTRACT), "--output", str(output)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    observed = json.loads(output.read_text(encoding="utf-8"))
    frozen = json.loads(MARGINS.read_text(encoding="utf-8"))
    assert observed == frozen
    assert frozen["direction_check"] == {
        "mutant_deficit_at_high_maternal_temperature_both_weightings": True,
        "mutant_deficit_at_low_maternal_temperature_both_weightings": False,
        "matches_author_reported_genotype_by_maternal_temperature_direction": True,
    }
    maternal = frozen["unweighted_equal_cell_margins"][
        "maternal_genotype_x_maternal_temperature"
    ]
    paternal = frozen["n_weighted_descriptive_margins"][
        "paternal_genotype_x_maternal_temperature"
    ]
    assert maternal["by_maternal_temperature"]["high"]["aa_over_AA"] < 1
    assert maternal["by_maternal_temperature"]["low"]["aa_over_AA"] > 1
    assert paternal["by_maternal_temperature"]["high"]["aa_over_AA"] < 1
    assert frozen["inference_status"] == "descriptive_reconstruction_only"
    assert "No confidence interval" in frozen["claim_boundary"]
