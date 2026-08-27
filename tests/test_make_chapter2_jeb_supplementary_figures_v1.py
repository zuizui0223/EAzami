from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))

import make_chapter2_jeb_supplementary_figures_v1 as target


def test_all_supplementary_figures_render_from_frozen_sources(tmp_path: Path):
    target.style()
    outputs = []
    outputs += target.figure_s1(tmp_path)
    outputs += target.figure_s2(tmp_path)
    outputs += target.figure_s3(tmp_path)
    outputs += target.figure_s4(tmp_path)
    outputs += target.figure_s5(tmp_path)
    assert len(outputs) == 10
    assert all(path.exists() and path.stat().st_size > 10_000 for path in outputs)


def test_supplementary_negative_and_resolution_boundaries_are_frozen():
    lightness = target.read_json(target.EVID / "japan7_source_balanced_lightness_history_v1.json")
    compression = target.read_json(target.EVID / "hmm2_population_aware_transition_test_v1.json")
    assert lightness["predeclared_gates"]["directional_replication_pass"] is False
    assert lightness["primary_signal"]["negative_tail_p"] == 0.7579365079365079
    assert compression["stage_B_minimum_transition_count"]["takaoense_species_tip_minimum"] == 1
    assert compression["stage_B_minimum_transition_count"]["takaoense_population_sample_minimum"] == 2
    assert compression["stage_C_transition_rate"]["status"] == "blocked"
