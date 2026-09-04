#!/usr/bin/env python3
"""Final combined stress test: geography residualization + internal-edge scoring."""
from __future__ import annotations

import argparse, json
from pathlib import Path
import pandas as pd

from run_chapter2_orientation_transition_regime_hypothesis_v1 import read_trees, panel_state_map, prepare_topology_assets
from run_chapter2_orientation_transition_regime_geography_residual_v1 import build_residual_environment
from run_chapter2_orientation_transition_regime_internal_edge_v1 import exact_test


def args():
    p=argparse.ArgumentParser()
    for name in ("contract","coverage-audit","orientation","japan-occurrences","taiwan-occurrences","au-trees","out-json","out-csv"):
        p.add_argument("--"+name,type=Path,required=True)
    return p.parse_args()

def load(p): return json.loads(p.read_text(encoding="utf-8"))

def main():
    a=args(); c=load(a.contract); cov=load(a.coverage_audit)
    if c["version"]!="chapter2_orientation_transition_regime_combined_stress_contract_v1": raise AssertionError("contract drift")
    cross=pd.read_csv(a.orientation)
    occ=pd.concat([pd.read_csv(a.japan_occurrences),pd.read_csv(a.taiwan_occurrences)],ignore_index=True)
    trees=read_trees(a.au_trees,6)
    taxa_by={str(k):list(v["taxa"]) for k,v in cov["threshold_summaries"].items()}
    results={}; frames=[]
    for name,key,spec_key in (("strict_n10_primary","10","primary_panel"),("n5_sensitivity","5","sensitivity_panel")):
        spec=c[spec_key]; taxa=taxa_by[key]
        ss=cross.set_index("accepted_taxon").loc[taxa,"analysis_state"]
        got=(len(taxa),int((ss=="U").sum()),int((ss=="D").sum()))
        exp=(spec["expected_n"],spec["expected_U"],spec["expected_D"])
        if got!=exp: raise AssertionError(("panel drift",name,got,exp))
        counts,env,diag=build_residual_environment(occ,taxa)
        if any(int(counts.get(t,0))<spec["threshold"] for t in taxa): raise AssertionError(("threshold drift",name))
        states=panel_state_map(cross,taxa)
        assets=prepare_topology_assets(trees,taxa,env)
        res,df=exact_test(name,taxa,states,assets,spec["exact_state_maps"])
        res["geography_residualization"]=diag
        results[name]=res; frames.append(df)
    p=results["strict_n10_primary"]; top=p["observed"]["topology_composite"]; f=p["exact_primary_rank"]["exact_fraction"]
    if all(x>0 for x in top) and f<=0.05: cls="transition_regime_concordance_survives_combined_geography_and_terminal_edge_stress"
    elif all(x>0 for x in top): cls="transition_regime_direction_survives_combined_stress_but_exceptionality_does_not"
    else: cls="transition_regime_direction_breaks_under_combined_stress"
    out={"version":"chapter2_orientation_transition_regime_combined_stress_result_v1","analysis_role":c["analysis_role"],"fixed_hypothesis":c["fixed_hypothesis"],"classification":cls,"panels":results,"stop_rule":c["stop_rule"],"claim_ceiling":c["claim_ceiling"]}
    a.out_json.parent.mkdir(parents=True,exist_ok=True); a.out_json.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    pd.concat(frames,ignore_index=True).to_csv(a.out_csv,index=False)
    print(json.dumps(out,indent=2)); return 0

if __name__=="__main__": raise SystemExit(main())
