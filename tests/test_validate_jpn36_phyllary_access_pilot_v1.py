import csv
import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data/evidence/jpn36_phyllary_access_pilot_contract_v1.json"
VALIDATION = ROOT / "data/evidence/jpn36_phyllary_access_pilot_validation_v1.json"
ELIGIBLE_TEMPLATE = ROOT / "sampling/jpn36_phyllary_access_eligible_heads_v1.csv"
ASSIGNMENT = ROOT / "sampling/jpn36_phyllary_access_assignment_v1.csv"
RANDOMIZER = ROOT / "analysis/randomize_jpn36_phyllary_access_pairs_v1.py"


def make_authorization(**overrides):
    record = {
        "protocol_version": "jpn36_phyllary_access_pilot_v1",
        "authorization_record_id": "AUTH-DEID-001",
        "site_id": "SITE-DEID-01",
        "population_id": "POP-DEID-01",
        "execution_authorized": True,
        "land_manager_authorization_status": "approved",
        "manipulation_authorization_status": "approved",
        "conservation_review_status": "approved",
        "terminal_collection_authorization_status": "approved",
        "viability_assay_authorization_status": "approved",
        "population_census_complete": True,
        "counted_flowering_individuals": 1200,
        "authorized_manipulation_head_quota": 24,
        "authorized_terminal_collection_head_quota": 24,
        "device_qualification_status": "passed",
        "device_qualification_record_id": "DEVQUAL-DEID-001",
        "device_id": "DEVICE-V1",
        "material_lot": "LOT-DEID-001",
        "frozen_target_access_gap_mm": 1.5,
    }
    record.update(overrides)
    return record


def make_eligible(path: Path):
    with ELIGIBLE_TEMPLATE.open(newline="", encoding="utf-8") as handle:
        fieldnames = next(csv.reader(handle))
    rows = []
    for pair_number in range(1, 13):
        for member in ("A", "B"):
            individual = f"I{pair_number:02d}{member}"
            row = {field: "" for field in fieldnames}
            row.update(
                {
                    "pilot_id": "PILOT-DEID-01",
                    "site_id": "SITE-DEID-01",
                    "population_id": "POP-DEID-01",
                    "observation_date_local": "2026-09-15",
                    "pair_id": f"PAIR-{pair_number:02d}",
                    "individual_id": individual,
                    "capitulum_id": f"H-{individual}",
                    "phenological_stage": "early_anthesis",
                    "capitulum_diameter_mm": "18.0",
                    "capitulum_diameter_bin": "16-20",
                    "baseline_damage_fraction": "0.00",
                    "baseline_damage_bin": "0",
                    "phyllary_posture_class": "appressed",
                    "natural_stickiness_state": "nonsticky_or_nearly_nonsticky",
                    "minimum_access_gap_mm": "0.5",
                    "outer_phyllary_angle_deg": "5.0",
                    "natural_head_orientation_deg": "120.0",
                    "taxon_identity_confirmed": "yes",
                    "live_state_confirmed": "yes",
                    "permit_record_id": "AUTH-DEID-001",
                    "land_manager_authorization_record_id": "AUTH-DEID-001",
                    "conservation_review_record_id": "AUTH-DEID-001",
                    "terminal_collection_authorization_record_id": "AUTH-DEID-001",
                    "viability_authorization_record_id": "AUTH-DEID-001",
                    "device_qualification_record_id": "DEVQUAL-DEID-001",
                    "eligible": "yes",
                }
            )
            rows.append(row)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run_randomizer(tmp_path: Path, authorization: dict, suffix: str):
    eligible = tmp_path / f"eligible-{suffix}.csv"
    auth = tmp_path / f"authorization-{suffix}.json"
    output = tmp_path / f"assignment-{suffix}.csv"
    make_eligible(eligible)
    auth.write_text(json.dumps(authorization), encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, str(RANDOMIZER), str(eligible), str(auth), str(output)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return completed, output


def test_protocol_recomputes_but_field_execution_remains_unauthorized():
    subprocess.run(
        [sys.executable, str(ROOT / "analysis/validate_jpn36_phyllary_access_pilot_v1.py")],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    summary = json.loads(VALIDATION.read_text(encoding="utf-8"))
    assert summary["protocol_schema_ready"] is True
    assert summary["authorization_schema_ready"] is True
    assert summary["field_execution_authorized"] is False
    assert summary["empirical_result_available"] is False
    assert summary["fdt8_alignment"]["ufboot_terminal_forced_fraction"] == 0.754
    assert summary["sample_allocation"]["pairs"] == 12
    assert summary["sample_allocation"]["individuals"] == 24


def test_current_assignment_ledger_is_empty_until_authorized():
    with ASSIGNMENT.open(newline="", encoding="utf-8") as handle:
        assert list(csv.DictReader(handle)) == []


def test_randomizer_is_deterministic_balanced_and_one_head_per_plant(tmp_path):
    completed1, output1 = run_randomizer(tmp_path, make_authorization(), "one")
    completed2, output2 = run_randomizer(tmp_path, make_authorization(), "two")
    assert completed1.returncode == 0, completed1.stderr
    assert completed2.returncode == 0, completed2.stderr
    assert output1.read_text(encoding="utf-8") == output2.read_text(encoding="utf-8")
    with output1.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 24
    assert len({row["individual_id"] for row in rows}) == 24
    assert {row["randomization_seed"] for row in rows} == {
        "JPN36-PHYLLARY-ACCESS-V1-20260827"
    }
    by_pair = {}
    for row in rows:
        by_pair.setdefault(row["pair_id"], []).append(row)
    assert len(by_pair) == 12
    assert all(sorted(row["assignment"] for row in pair) == ["access_proxy", "sham"] for pair in by_pair.values())


@pytest.mark.parametrize(
    "overrides,expected",
    [
        ({"execution_authorized": False}, "execution_authorized"),
        ({"conservation_review_status": "pending"}, "conservation_review_status"),
        ({"terminal_collection_authorization_status": "not_approved"}, "terminal_collection_authorization_status"),
        ({"counted_flowering_individuals": 1199}, "2 percent population cap"),
        ({"device_qualification_status": "failed"}, "device_qualification_status"),
    ],
)
def test_randomizer_fails_closed_on_rights_conservation_or_device_gate(tmp_path, overrides, expected):
    completed, output = run_randomizer(tmp_path, make_authorization(**overrides), expected.replace(" ", "-"))
    assert completed.returncode != 0
    assert expected in completed.stderr
    assert not output.exists()


def test_validator_rejects_claim_boundary_or_sample_drift():
    sys.path.insert(0, str(ROOT))
    from analysis.validate_jpn36_phyllary_access_pilot_v1 import validate_contract

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    sample_drift = copy.deepcopy(contract)
    sample_drift["field_design"]["target_pair_count"] = 10
    with pytest.raises(RuntimeError, match="sample allocation"):
        validate_contract(sample_drift)

    claim_drift = copy.deepcopy(contract)
    claim_drift["claim_boundary"] = "The pilot proves adaptation."
    with pytest.raises(RuntimeError, match="claim boundary"):
        validate_contract(claim_drift)
