import importlib.util
import json
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis" / "run_azami_capitulum_v3_one_shot_scoring.py"
spec = importlib.util.spec_from_file_location("v3score", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def observed():
    return mod.load_observed(
        ROOT / "data/evidence/source/azami_capitulum_space_eazami_targets_run33035785120.csv",
        ROOT / "data/evidence/source/azami_capitulum_environment_eazami_targets_run33035785120.csv",
        ROOT / "data/evidence/source/azami_capitulum_environment_incremental_eazami_targets_run33035785120.csv",
    )


def scoring():
    return json.loads((ROOT / "data/evidence/azami_capitulum_v3_scoring_contract_v1.json").read_text())


def test_observed_registry_is_exact_62_and_split_31_31():
    x = observed()
    assert len(x) == 62
    assert not x.duplicated(["target_id", "scope", "scale"]).any()
    for channel in scoring()["score_channels"].values():
        assert int(mod.channel_scope_mask(x, channel).sum()) == 31


def test_identity_model_has_zero_primary_and_sensitivity_distance():
    x = observed()
    model = x[["target_id", "scope", "scale", "value"]].copy()
    for channel in scoring()["score_channels"]:
        result = mod.score_estimands(model, x, scoring(), channel)
        assert result["total"] == pytest.approx(0.0, abs=1e-15)
        for klass in mod.TARGET_CLASSES:
            assert result[f"loss_{klass}"] == pytest.approx(0.0, abs=1e-15)


def test_class_balancing_prevents_row_count_weighting():
    x = observed()
    model = x[["target_id", "scope", "scale", "value"]].copy()
    mask = x["target_class"].eq("environment_geometry")
    model.loc[mask, "value"] = model.loc[mask, "value"] + 0.25
    result = mod.score_estimands(model, x, scoring(), "primary")
    assert result["loss_environment_geometry"] == pytest.approx(1.0, rel=1e-12)
    assert result["loss_structure"] == pytest.approx(0.0, abs=1e-15)
    assert result["loss_environment_block_r2"] == pytest.approx(0.0, abs=1e-15)
    assert result["loss_environment_incremental"] == pytest.approx(0.0, abs=1e-15)
    assert result["total"] == pytest.approx(0.25, rel=1e-12)


def test_structure_discrepancy_floor_is_frozen_at_point_zero_five():
    cfg = scoring()
    loss = mod.row_loss("structure", model=0.15, observed=0.10, low=0.09, high=0.11, scoring=cfg)
    assert loss == pytest.approx(1.0, rel=1e-12)


def test_factor_contrast_pair_counts_are_predeclared():
    families = sorted(mod.FAMILY_AXES)
    rows = []
    for channel in ["primary", "replication_sensitivity"]:
        for seed in scoring()["one_shot_draws"]["seeds"]:
            for rank, family in enumerate(families):
                rows.append({"channel": channel, "seed": seed, "family": family, "total": float(rank + 1)})
    factors = mod.factor_contrasts(pd.DataFrame(rows), scoring())
    primary = factors[factors["channel"].eq("primary")].set_index("contrast")
    assert int(primary.loc["residual_architecture", "n_paired_contrasts"]) == 7 * 16
    assert int(primary.loc["scale_coefficient_architecture", "n_paired_contrasts"]) == 6 * 16
    assert int(primary.loc["process_both_vs_core4", "n_paired_contrasts"]) == 4 * 16
    assert int(primary.loc["process_among_only_vs_core4", "n_paired_contrasts"]) == 4 * 16
    assert int(primary.loc["process_among_only_vs_process_both", "n_paired_contrasts"]) == 4 * 16
