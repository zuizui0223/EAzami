#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EVID=ROOT/"data"/"evidence"
CH=ROOT/"docs"/"chapter2"
SI=CH/"JEB_SUPPORTING_INFORMATION_V4.md"
MAN=CH/"MANUSCRIPT_JEB_V9_6_SCALE_CONDITIONED_ECOLOGY.md"

def load(name):
    return json.loads((EVID/name).read_text(encoding="utf-8"))

def need(text, token):
    if token not in text:
        raise AssertionError(f"missing SI token: {token}")

def main():
    si=SI.read_text(encoding="utf-8")
    man=MAN.read_text(encoding="utf-8")
    hist=load("chapter2_historical_differentiation_final_summary_v1.json")
    dep=load("chapter2_depth_ordering_robustness_result_v1.json")
    cov=load("chapter2_depth_coverage_matched_sensitivity_result_v1.json")
    common=load("chapter2_three_trait_common9_result_v1.json")
    tr=load("chapter2_orientation_transition_regime_hypothesis_result_v1.json")
    direction=load("chapter2_orientation_transition_directionality_result_v1.json")
    deletion=load("chapter2_orientation_transition_regime_single_deletion_result_v1.json")
    bidir_deletion=load("chapter2_orientation_transition_directionality_single_deletion_result_v1.json")
    geo=load("chapter2_orientation_transition_regime_geography_residual_result_v1.json")
    internal=load("chapter2_orientation_transition_regime_internal_edge_result_v1.json")
    combined=load("chapter2_orientation_transition_regime_combined_stress_result_v1.json")
    az=load("azami_orientation_crossscale_validation_audit_v1.json")
    held=(CH/"HELDOUT_ORIENTATION_OCCURRENCE_GATE_V2_RESULT.md").read_text(encoding="utf-8")
    meta=load("cirsium_floral_herbivory_lnrr_meta_v2.json")

    title=man.splitlines()[0].lstrip("# ").strip()
    need(si, f"**{title}**")

    rec=hist["recurrence_and_depth"]
    assert rec["orientation"]["minimum_changes_ufboot_range"]==[4,6]
    assert rec["phyllary_posture"]["minimum_changes"]==3
    assert rec["stickiness"]["minimum_changes"]==5
    assert rec["shared_transition_localization"].startswith("0/3")
    for t in ("4–6","1000/1000","993/1000","905/1000","898/1000","**Zero of three**"):
        need(si,t)

    p={(x["deeper_candidate"],x["shallower_candidate"]):x for x in dep["pairwise_results"]}
    assert p[("phyllary","stickiness")]["fraction_prespecified_deeper_direction"]==1
    assert p[("phyllary","orientation")]["fraction_prespecified_deeper_direction"]==.993
    assert p[("orientation","stickiness")]["fraction_prespecified_deeper_direction"]==.905
    assert cov["comparison_results"][0]["fraction"]==.975
    for t in ("195/200 = 97.5%","193/200 = 96.5%","21/200 = 10.5%","31/200 = 15.5%"):
        need(si,t)

    assert common["primary"]["orientation"]["n_taxa"]==17
    assert common["primary"]["phyllary"]["n_taxa"]==4
    assert common["primary"]["stickiness"]["n_taxa"]==12
    assert common["multiplicity"]["supported_rows_q_lt_0_05"]==0
    for t in ("2138/6188 = 34.55%","4/4 = 100%","116/924 = 12.55%","+1.3110","0.3214"):
        need(si,t)

    assert tr["n5_primary"]["exact_primary_rank"]["count_at_least_observed"]==16
    assert tr["n3_sensitivity"]["exact_primary_rank"]["count_at_least_observed"]==19
    assert direction["exact_floor_rank"]["count_at_least_observed"]==3
    assert deletion["n_exact_exceptionality_pass"]==2
    assert bidir_deletion["n_exact_exceptionality_pass"]==3
    assert geo["strict_n10_primary"]["exact_primary_rank"]["count_at_least_observed"]==5
    assert internal["strict_n10_primary"]["exact_primary_rank"]["count_at_least_observed"]==3
    assert combined["strict_n10_primary"]["exact_primary_rank"]["count_at_least_observed"]==3
    for t in ("16/792 = 2.02%","19/1716 = 1.11%","4/126 = 3.17%","3/126 = 2.38%","9/9","2/9","3/9","5/126 = 3.97%","29/792 = 3.66%"):
        need(si,t)

    assert az["decision"]=="NOT_ELIGIBLE_AS_PROSPECTIVE_P3"
    assert az["azami_existing_within_taxon"]["BIO1"]["q_fdr"]<.05
    assert az["azami_existing_among_taxon"]["BIO12"]["beta_std"]>.3
    for t in ("37,196","199 taxa","+0.304359","+0.0171503","+0.0265374","−0.0076180","not eligible as prospective held-out P3"):
        need(si,t)

    for t in ("downward/nodding: **0 taxa**","upward/erect: **1 taxon**","16 deterministic 0.1-degree thinned records"):
        need(held,t)
    for t in ("3 downward/nodding","10 upward/erect","*Cirsium vulgare*","BIO1 and BIO15 were not extracted"):
        need(si,t)

    re=meta["random_effects"]
    assert re["k"]==4
    assert 2.67 < re["response_ratio"] < 2.68
    assert re["I2_percent"] < 2
    for t in ("2.67364","2.38833–2.99302","62.6%","1.02%"):
        need(si,t)

    for bad in (
        "Public-image cohort and colour assay validation",
        "Focal current colour–RSDS concordance",
        "Arenicola: C. brevicaule",
        "Taiwan: C. kawakamii",
    ):
        if bad in si:
            raise AssertionError(f"stale V5 colour SI retained: {bad}")

    for t in (
        "scale- and representation-dependent",
        "external-taxon orientation confirmation is not evaluable",
        "public-data rescue is stopped after V2",
        "prospective aza3 field manipulation",
    ):
        need(si,t)

    print(json.dumps({
        "status":"ok",
        "si":"JEB_SUPPORTING_INFORMATION_V4.md",
        "history":"matched",
        "common9":"matched",
        "orientation_transition_robustness":"matched",
        "azami_crossscale":"matched_not_p3",
        "heldout_external":"not_evaluable_environment_unopened",
        "functional_meta":"matched"
    },indent=2))

if __name__=="__main__":
    main()
