from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))

import run_japan38_branch_change_provenance_sensitivity_v1 as target


def test_original_null_gate_requires_frozen_fail(tmp_path: Path):
    p = tmp_path / "null.json"
    p.write_text(
        json.dumps(
            {
                "contract_version": "japan38_branch_change_reconstruction_null_v1",
                "decision": "FAIL",
                "one_sided_reconstruction_null_p": 0.3504,
                "concept_ids": ["JPN_29", "JPN_30"],
            }
        ),
        encoding="utf-8",
    )
    assert target.validate_original_null(p)["decision"] == "FAIL"
    x = json.loads(p.read_text(encoding="utf-8"))
    x["decision"] = "PASS"
    p.write_text(json.dumps(x), encoding="utf-8")
    with pytest.raises(ValueError, match="frozen original FAIL"):
        target.validate_original_null(p)
