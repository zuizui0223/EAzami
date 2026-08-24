from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/evidence/capitulum_adaptive_module_registry_v1.csv"
README = ROOT / "README.md"


def rows():
    with REGISTRY.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_all_core_capitulum_modules_are_present():
    by_id = {r["module_id"]: r for r in rows()}
    assert {"M1", "M2", "M3", "M4", "M5", "M6", "H1", "H2", "H3"} <= set(by_id)
    assert by_id["M1"]["module"] == "display_quantity"
    assert by_id["M2"]["module"] == "orientation"
    assert by_id["M3"]["module"] == "phyllary_spine_defence"
    assert by_id["M4"]["module"] == "stickiness_mucilage"
    assert by_id["M5"]["module"] == "flower_colour_pigmentation"


def test_every_trait_module_has_selection_mechanism_history_and_fitness_contract():
    for row in rows():
        if not row["module_id"].startswith("M"):
            continue
        assert row["phenotypes"]
        assert row["selection_pressures"]
        assert row["ecological_mechanisms"]
        assert row["evolutionary_test"]
        assert row["fitness_endpoint"]
        assert row["claim_boundary"]


def test_orientation_is_not_the_only_or_central_trait_contract():
    text = README.read_text(encoding="utf-8")
    lower = text.lower()
    assert "orientation" in lower
    assert "not the central doctoral trait" in lower
    assert "display quantity | orientation | phyllary/spine defence | stickiness/mucilage | flower colour/pigmentation" in text
    assert "multiple functional modules" in lower or "different functional modules" in lower


def test_cold_dark_colour_is_not_promoted_to_conclusion():
    by_id = {r["module_id"]: r for r in rows()}
    boundary = by_id["M5"]["claim_boundary"].lower()
    assert "testable hypothesis" in boundary
    assert "not a current cirsium conclusion" in boundary


def test_stickiness_remains_separate_from_spines():
    by_id = {r["module_id"]: r for r in rows()}
    assert by_id["M3"]["current_status"] != by_id["M4"]["current_status"]
    assert "do not merge" in by_id["M4"]["claim_boundary"].lower()
