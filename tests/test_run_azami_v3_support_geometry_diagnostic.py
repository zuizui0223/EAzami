import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "analysis"
if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))
SCRIPT = ANALYSIS / "run_azami_v3_support_geometry_diagnostic.py"
spec = importlib.util.spec_from_file_location("supportdiag", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def contract():
    return json.loads((ROOT / "data/evidence/azami_capitulum_v3_support_geometry_diagnostic_contract_v1.json").read_text())


def test_candidate_set_and_draw_count_are_frozen():
    c = contract()
    assert c["post_heldout_outcome_design"] is True
    assert c["frozen_v1_winner"] == "NULL_COUPLED"
    assert len(c["candidate_families"]) == 5
    assert len(c["paired_draws"]["seeds"]) == 24
    assert len(set(c["paired_draws"]["seeds"])) == 24


def test_adequacy_rule_selects_minimal_predeclared_family():
    c = contract()
    rows = []
    for family in c["candidate_families"]:
        for seed in c["paired_draws"]["seeds"]:
            if family == "NULL_COUPLED":
                match, full = 5, False
            elif family == "PROCESS_AMONG_ONLY_SHARED_COUPLED":
                match, full = 8, seed < c["paired_draws"]["seeds"][8]
            elif family == "PROCESS_AMONG_ONLY_INDEPENDENT_COUPLED":
                match, full = 8, seed < c["paired_draws"]["seeds"][12]
            else:
                match, full = 6, False
            rows.append({
                "family": family,
                "seed": seed,
                "primary_cells_matched_out_of_8": match,
                "full_8_cell_pattern_match": full,
                "matching_cells_out_of_20": 16,
                "exact_20_cell_match": False,
                "among_gsp_supported_both_thresholds": full,
                "among_omnibus_supported_both_thresholds": full,
                "within_omnibus_and_gsp_unsupported_both_thresholds": True,
            })
    summary = mod.family_summary(pd.DataFrame(rows), c)
    result = mod.decision(summary, c)
    assert "PROCESS_AMONG_ONLY_SHARED_COUPLED" in result["diagnostically_adequate_families"]
    assert result["minimal_diagnostically_adequate_family"] == "PROCESS_AMONG_ONLY_SHARED_COUPLED"
    assert result["frozen_v1_winner_unchanged"] == "NULL_COUPLED"


def test_no_adequate_family_is_valid_endpoint():
    c = contract()
    rows = []
    for family in c["candidate_families"]:
        for seed in c["paired_draws"]["seeds"]:
            rows.append({
                "family": family,
                "seed": seed,
                "primary_cells_matched_out_of_8": 5,
                "full_8_cell_pattern_match": False,
                "matching_cells_out_of_20": 14,
                "exact_20_cell_match": False,
                "among_gsp_supported_both_thresholds": False,
                "among_omnibus_supported_both_thresholds": False,
                "within_omnibus_and_gsp_unsupported_both_thresholds": True,
            })
    summary = mod.family_summary(pd.DataFrame(rows), c)
    result = mod.decision(summary, c)
    assert result["status"] == "no_diagnostically_adequate_addition"
    assert result["minimal_diagnostically_adequate_family"] is None
