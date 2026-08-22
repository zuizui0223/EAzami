import csv
import json
import math
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/evidence/experimental_pollinator_selection_gradients_v1.csv"
SUMMARY = ROOT / "data/evidence/experimental_pollinator_selection_leverage_meta_v1.json"


def test_gradient_registry_internal_arithmetic():
    with DATA.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 41
    assert len({r["study_id"] for r in rows}) == 41
    assert sum(int(r["included_primary"]) for r in rows) == 38
    for r in rows:
        if r["beta_open"] and r["beta_hand"]:
            observed = float(r["beta_open"]) - float(r["beta_hand"])
            # Published deltas are sometimes rounded to two decimals.
            assert math.isclose(observed, float(r["delta_beta"]), abs_tol=0.011)
        if r["se_delta_source"] == "computed_independent_groups":
            expected = math.sqrt(float(r["se_open"]) ** 2 + float(r["se_hand"]) ** 2)
            # Stored derived SEs are provenance only; analysis recomputes from the
            # published rounded treatment-specific SEs. Require discrepancies tiny.
            assert math.isclose(expected, float(r["se_delta"]), rel_tol=0, abs_tol=5e-5)


def test_selection_leverage_meta_recomputes_and_keeps_article_clustering():
    subprocess.run(
        [sys.executable, str(ROOT / "analysis/meta_analyze_experimental_pollinator_selection_leverage_v1.py")],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    s = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert s["primary_gradient_rows"] == 38
    assert s["independent_article_clusters"] == 6
    assert s["taxon_count"] == 6
    assert s["max_abs_stored_vs_recomputed_delta_se_difference"] < 5e-5
    assert s["functional_class_hierarchy_identified"] is False
    assert s["significant_paired_class_contrasts"] == []
    classes = s["functional_class_summary_all"]
    assert classes["plant_display"]["n_articles"] == 5
    assert classes["flower_sensory"]["n_articles"] == 6
    assert classes["phenology"]["n_articles"] == 4
    assert classes["pollination_efficiency"]["n_articles"] == 3


def test_lobelia_intensity_increase_is_not_uniform():
    s = json.loads(SUMMARY.read_text(encoding="utf-8"))
    l = s["lobelia_pollinator_decline_context_test"]
    assert math.isclose(l["mean_abs_selection_change"], 0.019833333333333335, abs_tol=1e-12)
    assert l["traits_stronger_under_reduced"] == 4
    assert l["traits_weaker_under_reduced"] == 2
    assert math.isclose(l["two_sided_exact_signflip_p_exploratory"], 0.25, abs_tol=1e-12)
    assert l["pollen_limitation_log_response_ratio"]["ambient"]["estimate"] == 0.062
    assert l["pollen_limitation_log_response_ratio"]["reduced"]["estimate"] == 0.259
