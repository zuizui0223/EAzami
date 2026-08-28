from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))

import make_chapter2_jeb_figures_v1 as target


def test_all_figures_render_from_frozen_sources(tmp_path: Path):
    target.style()
    outputs = []
    outputs += target.figure1(tmp_path)
    outputs += target.figure2(tmp_path)
    outputs += target.figure3(tmp_path)
    outputs += target.figure4(tmp_path)
    assert len(outputs) == 8
    assert all(path.exists() and path.stat().st_size > 10_000 for path in outputs)


def test_frozen_reconstruction_decisions_are_fail():
    original = target.read_json(target.TIME / "japan38_branch_change_reconstruction_null_v1.json")
    sensitivity = target.read_json(target.PROV / "japan38_branch_change_provenance_sensitivity_v1.json")
    assert original["decision"] == "FAIL"
    assert original["one_sided_reconstruction_null_p"] == 0.3504
    assert sensitivity["decision"] == "FAIL"
    assert sensitivity["one_sided_reconstruction_null_p"] == 0.1959
