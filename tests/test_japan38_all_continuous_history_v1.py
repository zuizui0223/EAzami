from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "analysis"
if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))

MODULE_PATH = ANALYSIS / "run_japan38_all_continuous_history_v1.py"
spec = importlib.util.spec_from_file_location("all_history", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


def test_primary_unit_contract_is_eight_units():
    assert len(mod.PRIMARY_UNITS) == 8
    assert mod.PRIMARY_UNITS[0] == "orientation_image_vertical_angle"
    assert mod.HUE_UNIT in mod.PRIMARY_UNITS
    assert sum(mod.UNIT_MODULE[u] == "shape" for u in mod.PRIMARY_UNITS) == 4
    assert sum(mod.UNIT_MODULE[u] == "colour" for u in mod.PRIMARY_UNITS) == 3


def test_bh_is_monotone_on_sorted_p_values():
    p = [0.001, 0.01, 0.04, 0.2]
    q = mod.bh(p)
    assert all(0 <= x <= 1 for x in q)
    assert q[0] <= q[1] <= q[2] <= q[3]
    np.testing.assert_allclose(q, [0.004, 0.02, 0.05333333333333334, 0.2])


def test_zscore_has_zero_mean_and_unit_sample_sd():
    z = mod.zscore({"a": 1.0, "b": 2.0, "c": 4.0, "d": 7.0})
    arr = np.array(list(z.values()), float)
    assert abs(arr.mean()) < 1e-12
    assert abs(arr.std(ddof=1) - 1.0) < 1e-12


def test_candidate_endpoints_are_not_in_primary_units():
    assert "bract_projection_maximum" not in mod.PRIMARY_UNITS
    assert "involucre_length_width_ratio" not in mod.PRIMARY_UNITS


def test_concept_exclusion_is_explicit_and_fail_closed():
    bridge = pd.DataFrame(
        {
            "paper_japan_member_id": ["JPN_01", "JPN_29", "JPN_30"],
            "endpoint_id": ["x", "x", "x"],
        }
    )
    got = mod.apply_concept_exclusions(bridge, ["JPN_29", "JPN_29"])
    assert got["paper_japan_member_id"].tolist() == ["JPN_01", "JPN_30"]
    with pytest.raises(ValueError, match="absent from bridge"):
        mod.apply_concept_exclusions(bridge, ["JPN_99"])
