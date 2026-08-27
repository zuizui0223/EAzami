from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = ROOT / "data/evidence/fdt3_existing_material_preflight_v1.csv"
EVENTS = ROOT / "data/evidence/fdt3_repeated_evolution_event_ledger_v1.csv"
PILOT = ROOT / "data/evidence/fdt3_orientation_primary_pilot_v1.csv"
SUMMARY = ROOT / "data/evidence/fdt3_existing_material_preflight_v1.json"
SCRIPT = ROOT / "analysis/summarize_fdt3_existing_material_preflight_v1.py"
AUDIT = ROOT / "docs/FDT3_ORIENTATION_REPEATED_EVOLUTION_PRIMARY_PILOT_2026-08-26.md"


def rows(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_script():
    spec = importlib.util.spec_from_file_location("fdt3_preflight", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_existing_materials_keep_their_inferential_roles():
    data = rows(PREFLIGHT)
    assert len(data) == 6
    assert {row["route"] for row in data} == {
        "FDT1_FDT2",
        "FDT4",
        "FDT3_design",
        "FDT3",
    }
    assert all(int(row["fdt3_event_ledger_rows"]) == 0 for row in data)
    assert all(row["blocking_reason"] and row["claim_boundary"] for row in data)


def test_registered_input_counts_match_current_repository_materials():
    by_id = {row["material_id"]: row for row in rows(PREFLIGHT)}
    fdt2_sources = {
        row["source_id"]
        for row in rows(ROOT / "data/evidence/fdt2_source_context_registry_v1.csv")
    }
    assert int(by_id["FDT3P01"]["registered_units"]) == len(fdt2_sources) == 23

    phylogeny_pairs = set()
    for path in sorted(
        (ROOT / "data/evidence").glob("cirsium_phylogeny_literature_registry*.csv")
    ):
        for row in rows(path):
            phylogeny_pairs.add((row["citation_key"], row["doi"]))
    assert int(by_id["FDT3P02"]["registered_units"]) == len(phylogeny_pairs) == 54

    module_rows = rows(ROOT / "data/evidence/capitulum_adaptive_module_registry_v1.csv")
    functional_modules = [row for row in module_rows if row["module_id"].startswith("M")]
    assert int(by_id["FDT3P04"]["registered_units"]) == len(functional_modules) == 6

    pilot_rows = rows(PILOT)
    assert int(by_id["FDT3P06"]["registered_units"]) == len(pilot_rows) == 7
    assert all(int(row["event_rows_admitted"]) == 0 for row in pilot_rows)
    assert pilot_rows[0]["source_id"] == "10.1111/jse.12554"


def test_event_ledger_is_schema_complete_and_intentionally_empty():
    with EVENTS.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames is not None
        assert set(reader.fieldnames) == load_script().REQUIRED_EVENT_COLUMNS
        assert list(reader) == []


def test_primary_pilot_preserves_zero_event_decision_and_reopening_source():
    text = AUDIT.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    assert "NO_EVENT_ROWS_ADMITTED / SOURCE_FAMILY_IDENTIFIED / BRANCHWISE_EXTRACTION_PENDING" in text
    assert "10.1111/jse.12554" in text
    assert "Supporting Fig. S1 and Table S3" in text
    assert "0_EVENT_ROWS" in text
    assert "not evidence that repeated orientation evolution is absent" in normalized


def test_fdt3_summary_freezes_terminology_and_stop():
    module = load_script()
    preflight = module.read_csv(PREFLIGHT, module.REQUIRED_PREFLIGHT_COLUMNS)
    events = module.read_csv(EVENTS, module.REQUIRED_EVENT_COLUMNS)
    pilot = module.read_csv(PILOT, module.REQUIRED_PILOT_COLUMNS)
    module.validate(preflight, events, pilot)
    expected = module.summarize(preflight, events, pilot)
    observed = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert observed == expected
    assert observed["extracted_external_transition_events"] == 0
    assert observed["gate_decision"] == "NOT_READY_ZERO_PRIMARY_EVENT_LEDGER_ROWS_SOURCE_FAMILY_IDENTIFIED"
    assert observed["orientation_primary_pilot"]["primary_sources_audited"] == 7
    assert observed["orientation_primary_pilot"]["event_rows_admitted"] == 0
    assert "fitness validation" in observed["terminology_contract"]["parallel_or_convergent_adaptation"]
