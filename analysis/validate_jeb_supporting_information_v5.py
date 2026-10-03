#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]; E=R/"data"/"evidence"; CH=R/"docs"/"chapter2"
SI=CH/"JEB_SUPPORTING_INFORMATION_V5.md"
def load(p): return json.loads((E/p).read_text(encoding="utf-8"))
def need(t,x):
 if x not in t: raise AssertionError(f"missing {x}")
def main():
 t=SI.read_text(encoding="utf-8")
 for bad in ("The Azami image dataset","37,196 observations","BIO12 standardized beta = +0.304359","azami_orientation_crossscale"):
  if bad.casefold() in t.casefold(): raise AssertionError(f"separate-paper contamination: {bad}")
 hist=load("chapter2_historical_differentiation_final_summary_v1.json")
 cause=load("chapter2_trait_cause_falsification_v2.json")
 tr=load("chapter2_orientation_transition_regime_hypothesis_result_v1.json")
 h=load("chapter2_orientation_historical_regime_persistence_result_v1.json")
 meta=load("cirsium_floral_herbivory_lnrr_meta_v2.json")
 assert hist["recurrence_and_depth"]["shared_transition_localization"].startswith("0/3")
 assert cause["orientation"]["leading_domain"]=="abiotic_reproductive_exposure_plus_timing"
 assert cause["phyllary"]["leading_domain"]=="mechanical_antagonist_exclusion"
 assert cause["stickiness"]["leading_domain"]=="arthropod_community_filter_by_trait_cost"
 assert tr["n5_primary"]["exact_primary_rank"]["count_at_least_observed"]==16
 assert h["overall"]["h4_match_count"]==99 and h["overall"]["n_scenarios"]==376
 assert meta["random_effects"]["k"]==4
 for x in ("1000/1000","993/1000","905/1000","16/792 = 2.02%","19/1716 = 1.11%","4/126 = 3.17%",
           "99/376 = 26.3%","at least 75%","2.67364","62.6%","Adaptation inference ladder",
           "adaptation as a testable next step rather than a conclusion from recurrence"):
  need(t,x)
 print(json.dumps({"status":"ok","azami_image_dependency":"none","functional_interfaces":"matched","historical_origin":"matched","adaptation":"bounded"},indent=2))
if __name__=="__main__": main()
