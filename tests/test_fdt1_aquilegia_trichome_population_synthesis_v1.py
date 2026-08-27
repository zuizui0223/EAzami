from __future__ import annotations

import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXTRACT = ROOT / "data" / "evidence" / "fdt1_aquilegia_trichome_population_extract_v1.csv"
SYNTHESIS = ROOT / "data" / "evidence" / "fdt1_aquilegia_trichome_population_synthesis_v1.json"
BROAD = ROOT / "data" / "evidence" / "fdt1_broad_functional_calibration_summary_v1.json"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def test_extract_preserves_one_study_cluster_and_frozen_design() -> None:
    rows = read_csv(EXTRACT)
    assert len(rows) == 8
    assert len({row["effect_id"] for row in rows}) == 8
    assert {row["study_cluster"] for row in rows} == {"Jaime2013"}
    assert sum(int(row["n_control"]) + int(row["n_removal"]) for row in rows) == 300
    assert {(row["population"], int(row["n_control"])) for row in rows if int(row["n_control"]) == 10} == {
        ("Cabañas", 10)
    }
    assert {row["source_doi"] for row in rows} == {"10.1007/s00442-012-2553-z"}
    assert {row["source_artifact_sha256"] for row in rows} == {
        "60e5d7ca872f703d039fe42bf0b5adda154296b2a727617a5fff49738c79b790"
    }


def test_effect_directions_are_context_dependent_not_eight_studies() -> None:
    result = json.loads(SYNTHESIS.read_text(encoding="utf-8"))
    assert result["coverage"]["population_effects"] == 8
    assert result["coverage"]["independent_study_clusters"] == 1
    vulgaris = result["direction_by_species"]["Aquilegia vulgaris"]
    pyrenaica = result["direction_by_species"]["Aquilegia pyrenaica"]
    assert vulgaris["fruit_lnRR_positive"] == vulgaris["damage_lnRR_positive"] == 4
    assert pyrenaica["fruit_lnRR_positive"] == 1
    assert pyrenaica["fruit_lnRR_zero"] == 1
    assert pyrenaica["fruit_lnRR_negative"] == 2
    assert pyrenaica["damage_lnRR_positive"] == pyrenaica["damage_lnRR_negative"] == 2
    assert result["published_hierarchical_model_tests"]["healthy_fruit_set"]["species_by_treatment_p"] == 0.016
    assert result["published_hierarchical_model_tests"]["herbivory_damage"]["species_by_treatment_p"] == 0.041
    assert "not eight independent studies" in result["claim_boundary"]


def test_population_effects_recompute_from_table_means() -> None:
    rows = {row["effect_id"]: row for row in read_csv(EXTRACT)}
    result = json.loads(SYNTHESIS.read_text(encoding="utf-8"))
    fruit = {effect["effect_id"]: effect for effect in result["healthy_fruit_set_effects"]}
    damage = {effect["effect_id"]: effect for effect in result["herbivory_damage_effects"]}
    for effect_id, row in rows.items():
        expected_fruit = math.log(
            float(row["control_healthy_fruit_set_mean"]) / float(row["removal_healthy_fruit_set_mean"])
        )
        expected_damage = math.log(
            float(row["removal_herbivory_damage_mean"]) / float(row["control_herbivory_damage_mean"])
        )
        assert math.isclose(fruit[effect_id]["lnRR"], expected_fruit, rel_tol=0.0, abs_tol=1e-15)
        assert math.isclose(damage[effect_id]["lnRR"], expected_damage, rel_tol=0.0, abs_tol=1e-15)


def test_broad_registry_keeps_aquilegia_cluster_separate_after_mechanism_replication() -> None:
    broad = json.loads(BROAD.read_text(encoding="utf-8"))
    module = broad["modules"]["stickiness_glandular_trichomes"]
    assert module["quantitative_ready_rows"] == 1
    assert module["effect_extraction_needed_rows"] == 0
    assert any(
        "fruit or seed output" in action
        for action in broad["next_meta_actions"]
    )
