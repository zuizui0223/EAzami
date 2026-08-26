from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data/evidence/fdt1_trait_function_loading_contract_v1.csv"


def rows():
    with CONTRACT.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_loading_contract_has_unique_module_function_rows_and_no_fixed_tip_weights():
    data = rows()
    assert len(data) == 15
    assert len({row["loading_id"] for row in data}) == 15
    assert len({(row["trait_module"], row["function_axis"]) for row in data}) == 15
    assert {row["trait_module"] for row in data} == {
        "display",
        "orientation",
        "defensive_envelope",
        "stickiness",
        "colour",
    }
    assert not any("fixed_tip" in row["allowed_chapter2_use"] for row in data)
    assert not any(row["cirsium_loading_status"] == "ready_fixed_numeric_loading" for row in data)


def test_loading_contract_preserves_new_defence_and_colour_boundaries():
    by_id = {row["loading_id"]: row for row in rows()}
    assert by_id["L07"]["evidence_state"] == "MECHANISM_REPLICATED_NOT_POOL_READY"
    assert "Rheum" in by_id["L07"]["counterevidence"]
    assert "Nonhomologous envelopes" in by_id["L07"]["claim_boundary"]
    assert by_id["L08"]["evidence_state"] == "FITNESS_REPLICATED_NOT_POOL_READY"
    assert by_id["L13"]["evidence_state"] == "CONDITIONAL_READY_FLAVONOL_REPRODUCTIVE_TISSUE"
    assert "not visible-petal anthocyanin" in by_id["L13"]["claim_boundary"]
    assert by_id["L14"]["cirsium_loading_status"] == "not_loadable"
    assert "Azami lightness cannot inherit" in by_id["L14"]["claim_boundary"]
    assert by_id["L15"]["evidence_state"] == "READY_FOR_BOUNDED_EFFECT_EXTRACTION"
    assert "64 cells are not independent studies" in by_id["L15"]["claim_boundary"]


def test_every_loading_has_an_explicit_uncertainty_and_claim_ceiling():
    for row in rows():
        assert row["uncertainty_rule"]
        assert row["claim_boundary"]
        assert row["allowed_chapter2_use"]
        assert row["cirsium_loading_status"]
