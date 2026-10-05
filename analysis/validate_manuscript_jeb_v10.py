#!/usr/bin/env python3
from __future__ import annotations
import json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
E=ROOT/"data"/"evidence"
M=ROOT/"docs"/"chapter2"/"MANUSCRIPT_JEB_V10_FUNCTIONAL_ASSEMBLY_ORIGIN_DECOUPLING.md"

def load(p): return json.loads((E/p).read_text(encoding="utf-8"))
def need(t,x):
    if x not in t: raise AssertionError(f"missing: {x}")
def forbid(t,x):
    if x.casefold() in t.casefold(): raise AssertionError(f"forbidden: {x}")
def words(x): return len(re.findall(r"\b[\w'’*-]+\b",x))

def main():
    t=M.read_text(encoding="utf-8")
    hist=load("chapter2_historical_differentiation_final_summary_v1.json")
    depth=load("chapter2_depth_ordering_robustness_result_v1.json")
    cause=load("chapter2_trait_cause_falsification_v2.json")
    filt=load("chapter2_trait_specific_filter_synthesis_v1.json")
    tr=load("chapter2_orientation_transition_regime_hypothesis_result_v1.json")
    hreg=load("chapter2_orientation_historical_regime_persistence_result_v1.json")
    meta=load("cirsium_floral_herbivory_lnrr_meta_v2.json")

    # Complete separation from the independent Azami image paper.
    for bad in ("Azami image","azami_orientation","within-taxon image","among-taxon image",
                "scale- and representation-dependent","Orientation ecology is not scale invariant"):
        forbid(t,bad)

    rec=hist["recurrence_and_depth"]
    assert rec["orientation"]["minimum_changes_ufboot_range"]==[4,6]
    assert rec["phyllary_posture"]["minimum_changes"]==3
    assert rec["stickiness"]["minimum_changes"]==5
    assert rec["shared_transition_localization"].startswith("0/3")
    pair={(x["deeper_candidate"],x["shallower_candidate"]):x for x in depth["pairwise_results"]}
    assert pair[("phyllary","stickiness")]["fraction_prespecified_deeper_direction"]==1
    assert pair[("phyllary","orientation")]["fraction_prespecified_deeper_direction"]==.993
    assert pair[("orientation","stickiness")]["fraction_prespecified_deeper_direction"]==.905
    assert depth["complete_lower_bound_ordering"]["count"]==898
    for x in ("four to six","exactly three","exactly five","1,000/1,000","993/1,000","905/1,000","898/1,000","Zero of three"):
        need(t,x)
    need(t,"A young Cirsium radiation repeatedly rebuilt its reproductive head from functionally distinct components")
    need(t,"recurrent functional assembly")
    need(t,"recurrent functional rebuilding of the** *Cirsium* **capitulum")\n    need(t,"For this orientation event, the present ecological association and the tested coarse environment of its reconstructed origin are empirically separable.")

    orient_cal=load("chapter2_orientation_causal_triangulation_v3.json")
    assert orient_cal["external_mechanism_prior"]["achene_set_percent"]["nodding"]==56.3
    assert orient_cal["external_mechanism_prior"]["achene_set_percent"]["artificial_erect"]==15.7
    need(t,"56.3% achene set versus 15.7%")
    need(t,"response ratio ≈3.59")

    assert cause["whole_capitulum"]["trait_specific_filter_model"]=="best_current_integrative_model"
    assert cause["orientation"]["leading_domain"]=="abiotic_reproductive_exposure_plus_timing"
    assert cause["phyllary"]["leading_domain"]=="mechanical_antagonist_exclusion"
    assert cause["stickiness"]["leading_domain"]=="arthropod_community_filter_by_trait_cost"
    for x in ("abiotic reproductive exposure","mechanical antagonist","arthropod-community filtering"):
        need(t,x)

    reff=meta["random_effects"]
    assert reff["k"]==4
    assert abs(reff["response_ratio"]-2.673636515996)<1e-9
    assert abs(reff["ambient_seed_output_reduction_fraction"]-.625977579968)<1e-9
    for x in ("2.674-fold","2.388–2.993","62.6%","I² = 1.02%"):
        need(t,x)

    assert tr["n5_primary"]["exact_primary_rank"]["count_at_least_observed"]==16
    assert tr["n5_primary"]["exact_primary_rank"]["n_maps"]==792
    assert tr["n3_sensitivity"]["exact_primary_rank"]["count_at_least_observed"]==19
    for x in ("16/792","19/1,716","4/126","3/126"):
        need(t,x)

    assert hreg["classification"]=="historical_regime_persistence_not_supported"
    assert hreg["overall"]["n_scenarios"]==376
    assert hreg["overall"]["h4_match_count"]==99
    assert hreg["n_chronologies_4_of_4_regions"]==6
    assert all(x["BIO15_delta"]<0 and x["BIO1_delta"]<0 for x in hreg["central_0_79_to_0_74_ma"])
    need(t,"at least 75% of chronology scenarios")
    need(t,"threshold was frozen before the historical result was opened")
    need(t,"deterministic sensitivity-grid fractions, not posterior probabilities")
    for x in ("99/376","26.3%","21.3%","9.6%","43.6%","30.9%","6/94","0/324","0/21"):
        need(t,x)

    # Adaptation ceiling.
    for bad in ("repeated evolution proves adaptation",
                "we demonstrate that orientation is an adaptation",
                "we demonstrate that phyllary posture is an adaptation",
                "we demonstrate that stickiness is an adaptation",
                "climate caused the transition"):
        forbid(t,bad)
    for x in ("Repeated change alone does not prove adaptation","They do not by themselves establish independent origins, convergence or adaptation",
              "This does not prove selection","historical selective cause"):
        need(t,x)

    abstract=t.split("## Abstract\n\n",1)[1].split("\n\n**Keywords:**",1)[0]
    body=t.split("# References",1)[0]
    if words(abstract)>250: raise AssertionError(words(abstract))
    if words(body)>7500: raise AssertionError(words(body))
    if len([x for x in t.split("**Keywords:**",1)[1].split("\n",1)[0].split(";") if x.strip()]) not in range(4,11):
        raise AssertionError("keyword count")

    print(json.dumps({
      "status":"ok","abstract_words":words(abstract),"main_words":words(body),
      "azami_image_dependency":"none","historical_claim":"mosaic_reassembly",
      "functional_claim":"plausible_trait_specific_interfaces",
      "orientation_ecology":"transition_regime_supported",
      "historical_trigger":"present_regime_not_persistent",
      "adaptation":"not_demonstrated"
    },indent=2))

if __name__=="__main__": main()
