import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "analysis"
if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))
SCRIPT = ANALYSIS / "validate_azami_v3_null_heldout_support.py"
spec = importlib.util.spec_from_file_location("heldout", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def contract():
    return json.loads((ROOT / "data/evidence/azami_capitulum_v3_null_heldout_support_contract_v1.json").read_text())


def test_observed_support_vector_matches_frozen_20_cells():
    observed = mod.validate_observed_vector(
        contract(),
        ROOT / "data/evidence/source/azami_capitulum_environment_incremental_eazami_targets_run33035785120.csv",
    )
    assert len(observed) == 20
    assert observed[("complete18_env_min5", "among_taxon", "all_process_extension_beyond_core4")] is True
    assert observed[("complete18_env_min2", "among_taxon", "growing_season_water_input_beyond_core4")] is True
    assert observed[("complete18_env_min5", "within_taxon", "all_process_extension_beyond_core4")] is False


def test_bh_adjust_matches_four_test_example():
    x = pd.Series([0.01, 0.02, 0.20, 0.80])
    q = mod.bh_adjust(x)
    assert q.tolist() == pytest.approx([0.04, 0.04, 0.26666666666666666, 0.8])


def test_exact_observed_vector_is_primary_and_full_match():
    c = contract()
    observed = mod.contract_support_vector(c)
    rows = []
    for (scope, scale, test_id), state in observed.items():
        rows.append({"seed": 1, "scope": scope, "scale": scale, "test_id": test_id, "supported_0_05": state})
    summary = mod.summarize_draws(pd.DataFrame(rows), observed, c)
    assert len(summary) == 1
    assert bool(summary.iloc[0]["primary_pattern_match"])
    assert bool(summary.iloc[0]["exact_20_cell_match"])
    assert int(summary.iloc[0]["matching_cells_out_of_20"]) == 20


@pytest.mark.parametrize(
    "matches,expected",
    [
        (0, "not_reproduced_or_exceptional"),
        (1, "not_reproduced_or_exceptional"),
        (2, "rare"),
        (6, "rare"),
        (7, "compatible_frequency"),
    ],
)
def test_predeclared_interpretation_bins(matches, expected):
    rows = []
    for i in range(64):
        rows.append({
            "primary_pattern_match": i < matches,
            "exact_20_cell_match": False,
            "matching_cells_out_of_20": 15,
        })
    decision = mod.final_decision(pd.DataFrame(rows), contract())
    assert decision["primary_pattern_matches"] == matches
    assert decision["primary_pattern_classification"] == expected
    assert decision["v1_winner_changed"] is False
