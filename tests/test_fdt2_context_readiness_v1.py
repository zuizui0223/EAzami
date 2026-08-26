from __future__ import annotations

import csv
import importlib.util
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTEXT = ROOT / "data/evidence/fdt2_source_context_registry_v1.csv"
FDT1 = ROOT / "data/evidence/fdt1_broad_functional_calibration_seed_v1.csv"
SUMMARY = ROOT / "data/evidence/fdt2_context_readiness_summary_v1.json"
SCRIPT = ROOT / "analysis/summarize_fdt2_context_readiness_v1.py"


def read_rows(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_script():
    spec = importlib.util.spec_from_file_location("fdt2_context", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_registry_collapses_fdt1_responses_to_unique_source_clusters():
    contexts = read_rows(CONTEXT)
    fdt1 = read_rows(FDT1)
    assert len(contexts) == 23
    assert len({row["source_id"] for row in contexts}) == 23
    assert {row["source_id"] for row in contexts} == {
        row["source_id"] for row in fdt1
    }
    expected = Counter(row["source_id"] for row in fdt1)
    assert {
        row["source_id"]: int(row["fdt1_seed_rows"]) for row in contexts
    } == expected


def test_missing_geography_stays_missing_and_forbidden_proxies_are_absent():
    contexts = read_rows(CONTEXT)
    assert not any(
        row["geography_basis"] in {"author_affiliation", "species_range_inference"}
        for row in contexts
    )
    for row in contexts:
        assert bool(row["latitude"]) == bool(row["longitude"])
        if row["geography_readiness"] in {
            "unresolved",
            "laboratory_or_greenhouse_without_field_origin",
        }:
            assert not row["latitude"]
            assert not row["longitude"]


def test_current_registry_does_not_license_geographic_meta_regression():
    contexts = read_rows(CONTEXT)
    assert not any(
        row["fdt2_use"] == "geographic_meta_regression" for row in contexts
    )
    assert any(
        row["fdt2_use"] == "directional_exposure_calibration_only"
        for row in contexts
    )
    assert all(row["claim_boundary"] for row in contexts)


def test_checked_in_summary_matches_validated_registry():
    module = load_script()
    contexts = module.read_csv(CONTEXT)
    fdt1 = read_rows(FDT1)
    module.validate_contexts(contexts, fdt1)
    expected = module.summarize(contexts)
    observed = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert observed == expected
    assert (
        observed["gate_decision"]["geographic_meta_regression"]
        == "NOT_READY_NO_HOMOLOGOUS_GEOREFERENCED_EFFECT_FAMILY"
    )
    assert (
        observed["gate_decision"]["experimental_exposure_synthesis"]
        == "DIRECTIONAL_CALIBRATION_ONLY"
    )
