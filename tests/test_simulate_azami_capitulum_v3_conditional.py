from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


gen = load_module("v3gen", ROOT / "analysis/simulate_azami_capitulum_v3_conditional.py")
calc = load_module("v3calc", ROOT / "analysis/compute_azami_capitulum_v3_estimands.py")
audit = load_module("v3audit", ROOT / "analysis/audit_azami_capitulum_v3_scoreability_v1.py")
GEN_CONTRACT = json.loads((ROOT / "data/evidence/azami_capitulum_v3_generator_contract_v1.json").read_text())
EST_CONTRACT = json.loads((ROOT / "data/evidence/azami_capitulum_v3_estimand_contract_v1.json").read_text())


def synthetic_design(n_taxa: int = 14, n_obs: int = 6) -> pd.DataFrame:
    rows = []
    for t in range(n_taxa):
        for j in range(n_obs):
            z = 0.31 * t + 0.53 * j
            rows.append({
                "design_row_id": f"D{t:02d}_{j:02d}",
                "taxon_name": f"Taxon_{t:02d}",
                "chelsa_bio01": 0.70 * t + 0.20 * j + np.sin(z),
                "chelsa_bio04": -0.25 * t + 0.60 * j + np.cos(0.7 * z),
                "chelsa_bio12": 0.40 * t - 0.55 * j + np.sin(1.2 * z),
                "chelsa_bio15": -0.15 * t + 0.75 * j + np.cos(1.4 * z),
                "chelsa_rsds_mean": 0.55 * t + 0.15 * j + np.sin(0.4 + z),
                "chelsa_vpd_mean": 0.35 * t - 0.28 * j + np.cos(0.8 + z),
                "chelsa_sfcwind_mean": -0.08 * t + 0.45 * j + np.sin(1.8 * z),
                "chelsa_gsp": 0.30 * t + 0.72 * j + np.cos(2.0 * z),
                "chelsa_npp": 0.82 * t - 0.18 * j + np.sin(2.2 * z),
            })
    return pd.DataFrame(rows)


def test_contract_has_exact_14_families():
    assert set(GEN_CONTRACT["model_families"]) == set(gen.FAMILY_AXES)
    assert len(gen.FAMILY_AXES) == 14


def test_every_family_emits_exact_schema_and_62_estimands():
    design = synthetic_design()
    expected_cols = ["obs_id", "taxon_name", *gen.ENVIRONMENT, *gen.ENDPOINTS]
    for family in GEN_CONTRACT["model_families"]:
        rows = gen.generate(design, family, 20260827, GEN_CONTRACT)
        assert list(rows.columns) == expected_cols
        assert len(rows) == len(design)
        assert rows["obs_id"].is_unique
        assert np.isfinite(rows[[*gen.ENVIRONMENT, *gen.ENDPOINTS]].to_numpy(float)).all()
        targets = calc.compute(rows, EST_CONTRACT)
        assert len(targets) == 62
        assert not targets.duplicated(["target_id", "scope", "scale"]).any()


def test_generation_is_deterministic_and_seed_sensitive():
    design = synthetic_design()
    family = "PROCESS_AMONG_ONLY_INDEPENDENT_MODULAR"
    a = gen.generate(design, family, 71, GEN_CONTRACT)
    b = gen.generate(design, family, 71, GEN_CONTRACT)
    c = gen.generate(design, family, 72, GEN_CONTRACT)
    pd.testing.assert_frame_equal(a, b)
    assert not np.allclose(a[gen.ENDPOINTS].to_numpy(float), c[gen.ENDPOINTS].to_numpy(float))


def test_process_among_only_has_zero_process_coefficients_within():
    for architecture in ["SHARED", "INDEPENDENT"]:
        for module in gen.MODULES:
            within = gen.coefficient_vector(
                module, "within", "PROCESS_AMONG_ONLY", architecture, 20260827, GEN_CONTRACT
            )
            among = gen.coefficient_vector(
                module, "among", "PROCESS_AMONG_ONLY", architecture, 20260827, GEN_CONTRACT
            )
            assert all(within[p] == 0.0 for p in gen.PROCESS5)
            assert any(abs(among[p]) > 0 for p in gen.PROCESS5)


def test_shared_core_coefficients_are_identical_across_scales():
    for module in gen.MODULES:
        within = gen.coefficient_vector(module, "within", "PROCESS_AMONG_ONLY", "SHARED", 99, GEN_CONTRACT)
        among = gen.coefficient_vector(module, "among", "PROCESS_AMONG_ONLY", "SHARED", 99, GEN_CONTRACT)
        assert [within[p] for p in gen.CORE4] == [among[p] for p in gen.CORE4]


def test_independent_core_coefficients_are_not_forced_equal():
    differences = []
    for module in gen.MODULES:
        within = gen.coefficient_vector(module, "within", "CORE4", "INDEPENDENT", 99, GEN_CONTRACT)
        among = gen.coefficient_vector(module, "among", "CORE4", "INDEPENDENT", 99, GEN_CONTRACT)
        differences.extend(abs(within[p] - among[p]) for p in gen.CORE4)
    assert any(x > 1e-12 for x in differences)


def test_new_generator_is_exact_schema_scoreable_62_of_62():
    targets = audit.load_targets(
        ROOT / "data/evidence/source/azami_capitulum_space_eazami_targets_run33035785120.csv",
        ROOT / "data/evidence/source/azami_capitulum_environment_eazami_targets_run33035785120.csv",
        ROOT / "data/evidence/source/azami_capitulum_environment_incremental_eazami_targets_run33035785120.csv",
    )
    text = (ROOT / "analysis/simulate_azami_capitulum_v3_conditional.py").read_text()
    ledger, summary = audit.audit(EST_CONTRACT, targets, text)
    assert summary["generator_schema_marker_present"] is True
    assert summary["exact_endpoint_names_present_in_generator"] == 18
    assert summary["exact_environment_names_present_in_generator"] == 9
    assert summary["current_v2_exact_scoreable_targets"] == 62
    assert ledger["scoreable_now"].all()
