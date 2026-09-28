from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis/build_functional_trait_function_effect_ledger_v1.py"

spec = importlib.util.spec_from_file_location("fdt1_effects", SCRIPT)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


def test_harmonized_ledger_preserves_metric_families_and_expected_rows():
    rows = mod.build_rows()
    summary = mod.summarize(rows)
    assert summary["row_count"] == 79
    assert summary["row_count_is_not_independent_study_count"] is True
    assert summary["module_row_counts"] == {
        "capitulum_or_flower_size_proxy": 8,
        "cross_module_antagonist_pressure": 9,
        "cross_module_selection_mosaic": 9,
        "demographic_gate": 6,
        "display_quantity": 19,
        "flower_colour_pigmentation": 9,
        "orientation": 7,
        "pollination_efficiency_reference": 4,
        "reproductive_assurance": 7,
        "stickiness_mucilage": 1,
    }
    assert summary["poolability_counts"] == {
        "article_cluster_poolable_within_metric_family": 33,
        "nonpoolable_metric_specific_anchor": 9,
        "nonpoolable_structured_anchor": 5,
        "single_study_direct_effect_not_meta_ready": 2,
        "structured_nonpoolable_context_prior": 21,
        "study_cluster_poolable_direct_effect": 9,
    }


def test_only_commensurable_groups_are_flagged_as_existing_meta_seeds():
    summary = mod.summarize(mod.build_rows())
    assert summary["independent_cluster_counts_by_poolable_group"] == {
        "antagonist_lnRR_seed_output": 4,
        "pollinator_delta_beta::capitulum_or_flower_size_proxy": 5,
        "pollinator_delta_beta::display_quantity": 5,
        "pollinator_delta_beta::flower_colour_pigmentation": 2,
        "pollinator_delta_beta::pollination_efficiency_reference": 3,
    }
    assert summary["existing_meta_ready_groups_k_ge_3"] == {
        "antagonist_lnRR_seed_output": 4,
        "pollinator_delta_beta::capitulum_or_flower_size_proxy": 5,
        "pollinator_delta_beta::display_quantity": 5,
        "pollinator_delta_beta::pollination_efficiency_reference": 3,
    }
    assert "pollinator_delta_beta::flower_colour_pigmentation" not in summary["existing_meta_ready_groups_k_ge_3"]


def test_direct_orientation_and_stickiness_evidence_stay_out_of_false_pooling():
    rows = mod.build_rows()
    orientation_direct = [r for r in rows if r["module"] == "orientation" and r["poolability"] == "single_study_direct_effect_not_meta_ready"]
    assert {r["source_row_id"] for r in orientation_direct} == {"OR_CREM_ACHENE", "OR_CREM_POLL_NULL"}
    sticky = [r for r in rows if r["module"] == "stickiness_mucilage"]
    assert len(sticky) == 1
    assert sticky[0]["source_row_id"] == "IQ13"
    assert sticky[0]["poolability"] == "nonpoolable_metric_specific_anchor"


def test_herbivory_prior_is_not_mislabeled_as_trait_adaptation():
    rows = mod.build_rows()
    herb = [r for r in rows if r["module"] == "cross_module_antagonist_pressure"]
    assert len(herb) == 9
    assert len({r["independence_cluster"] for r in herb}) == 4
    assert all("not the adaptive effect" in r["claim_boundary"] for r in herb)


def test_summary_forces_targeted_search_instead_of_one_cross_module_number():
    summary = mod.summarize(mod.build_rows())
    assert "no single cross-module scalar effect" in summary["decision"]
    gaps = " ".join(summary["existing_gap_priorities"])
    for term in ("orientation", "phyllary/spine", "stickiness/mucilage", "flower pigmentation", "display"):
        assert term in gaps
