from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))

import run_japan38_continuous_branch_change_topology_sensitivity_v1 as target


def test_stable_spearman_collapses_lapack_scale_near_ties():
    base = pd.DataFrame(
        {
            "left": [0.0, 0.5, 0.5, 1.0, 1.5, 1.5, 2.0, 2.5],
            "right": [2.5, 2.0, 2.0, 1.5, 1.0, 1.0, 0.5, 0.0],
        }
    )
    jitter = base.copy()
    jitter["left"] += np.array([0, 4, -4, 0, -3, 3, 0, 0]) * 1e-14
    jitter["right"] += np.array([0, -3, 3, 0, 4, -4, 0, 0]) * 1e-14

    expected = target.stable_spearman(base, ["left", "right"])
    observed = target.stable_spearman(jitter, ["left", "right"])
    pd.testing.assert_frame_equal(observed, expected)


def test_tie_precision_is_frozen():
    assert target.SPEARMAN_TIE_DECIMALS == 12
