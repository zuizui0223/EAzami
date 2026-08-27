from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


calc = load_module("v3calc", ROOT / "analysis/compute_azami_capitulum_v3_estimands.py")
audit_mod = load_module("v3audit", ROOT / "analysis/audit_azami_capitulum_v3_scoreability_v1.py")
CONTRACT = json.loads((ROOT / "data/evidence/azami_capitulum_v3_estimand_contract_v1.json").read_text())


def synthetic_observations() -> pd.DataFrame:
    endpoints = CONTRACT["observation_schema"]["response_endpoints"]
    env_names = CONTRACT["observation_schema"]["environment_predictors"]
    rows = []
    for t in range(14):
        for j in range(6):
            z = t / 4.0 + (j - 2.5) / 3.0
            env = {
                "chelsa_bio01": 0.8 * t + 0.4 * j + np.sin(z),
                "chelsa_bio04": -0.3 * t + 0.7 * j + np.cos(0.7 * z),
                "chelsa_bio12": 0.5 * t - 0.6 * j + np.sin(1.3 * z),
                "chelsa_bio15": -0.2 * t + 0.9 * j + np.cos(1.1 * z),
                "chelsa_rsds_mean": 0.6 * t + 0.2 * j + np.sin(0.4 + z),
                "chelsa_vpd_mean": 0.4 * t - 0.3 * j + np.cos(0.8 + z),
                "chelsa_sfcwind_mean": -0.1 * t + 0.5 * j + np.sin(1.7 * z),
                "chelsa_gsp": 0.3 * t + 0.8 * j + np.cos(1.9 * z),
                "chelsa_npp": 0.9 * t - 0.2 * j + np.sin(2.1 * z),
            }
            e = list(env.values())
            trait = {}
            for k, endpoint in enumerate(endpoints):
                # Deterministic but non-degenerate 18D phenotype. The purpose is
                # interface/formula validation, not biological calibration.
                trait[endpoint] = (
                    (0.12 + 0.015 * (k % 5)) * e[k % len(e)]
                    + (0.06 + 0.01 * (k % 3)) * e[(k + 3) % len(e)]
                    + 0.025 * np.sin((k + 1) * (t + 1) * 0.17 + j * 0.41)
                    + 0.01 * (k + 1) * j
                )
            theta = 0.2 * t + 0.35 * j + 0.1 * np.sin(z)
            trait["corolla_hue_sin"] = np.sin(theta)
            trait["corolla_hue_cos"] = np.cos(theta)
            rows.append({
                "obs_id": f"T{t:02d}_O{j:02d}",
                "taxon_name": f"Taxon_{t:02d}",
                **env,
                **trait,
            })
    df = pd.DataFrame(rows)
    assert set(env_names).issubset(df.columns)
    return df


def test_exact_adapter_emits_all_62_unique_targets():
    out = calc.compute(synthetic_observations(), CONTRACT)
    assert len(out) == 62
    assert not out.duplicated(["target_id", "scope", "scale"]).any()
    assert (out["target_class"] == "structure").sum() == 6
    assert (out["target_class"] == "environment_block_r2").sum() == 24
    assert (out["target_class"] == "environment_geometry").sum() == 12
    assert (out["target_class"] == "environment_incremental").sum() == 20
    assert np.isfinite(out["value"]).all()


def test_exact_adapter_fails_closed_when_one_endpoint_missing():
    df = synthetic_observations().drop(columns=["bract_projection_peak_density"])
    with pytest.raises(ValueError, match="missing exact v3 columns"):
        calc.compute(df, CONTRACT)


def test_current_v2_is_zero_of_62_exact_scoreable():
    targets = audit_mod.load_targets(
        ROOT / "data/evidence/source/azami_capitulum_space_eazami_targets_run33035785120.csv",
        ROOT / "data/evidence/source/azami_capitulum_environment_eazami_targets_run33035785120.csv",
        ROOT / "data/evidence/source/azami_capitulum_environment_incremental_eazami_targets_run33035785120.csv",
    )
    ledger, summary = audit_mod.audit(
        CONTRACT,
        targets,
        (ROOT / "analysis/simulate_capitulum_pattern_reduction_v2.py").read_text(),
    )
    assert len(ledger) == 62
    assert summary["statistics_adapter_ready_targets"] == 62
    assert summary["current_v2_exact_scoreable_targets"] == 0
    assert summary["current_v2_exact_unscoreable_targets"] == 62
    assert not summary["generator_schema_marker_present"]
    assert not ledger["scoreable_now"].any()
