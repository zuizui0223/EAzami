#!/usr/bin/env python3
"""Real NA62 nuclear U/D endpoint-direction x BIO18, BIO15 and BIO1 contrasts.

Faithful EAzami transition-regime structure: ER 2-state Mk CTMC on the real
Siniscalchi 2023 dated nuclear tree, exact parent/child endpoint posterior,
Brownian ancestral *modern niche-centroid* reconstruction, signed
association of U->D minus D->U endpoint changes and reconstructed climate.

A sample-state permutation *holding source counts fixed* provides an
illustrative rank/label null, NOT a spatial/phylogenetic-evolutionary process
calibrated causal p value. This is an exploratory out-of-sample North
American comparison of the East-Asian original +BIO15/-BIO1 direction;
BIO18 direction (higher warmest-quarter rainfall) was selected by user
before looking at the new empirical scores. Predeclare three directions
and Holm correction; independently flag Mixed forest after its separate
PGLS screen as a post-hoc exploratory replication target. No events dated.
"""
from __future__ import annotations

import argparse
import copy
import csv
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np

from run_siniscalchi2023_NA_nuclear_BIO18_full9trait_envscreen_v1 import (
    source, AMBIGUOUS_HEAD,
)
from run_chapter2_orientation_transition_regime_hypothesis_v1 import (
    brownian_internal_values,
    fit_symmetric_q,
    ctmc_likelihood_and_edge_joint,
    tree_structure,
)

PREDEFINED={"BIO18":1,"BIO15":1,"BIO1":-1}
EXPLORATORY={"Mixed":1}
AXES=tuple(PREDEFINED)+tuple(EXPLORATORY)
SEED=20261025
N_NULL=999


def freeze(tree,original_traits,environment,exclude):
    tr=copy.deepcopy(tree)
    for name in exclude:tr.prune(name)
    tips=sorted(t.name for t in tr.get_terminals())
    states={name:(0 if original_traits[name]["HeadPosition"]=="0" else 1)
            for name in tips}
    if Counter(states.values())!=Counter({0:len(tips)-5,1:5}):
        raise ValueError("original 5 D source coding drift after FNA mixed head review")
    edge_delta={}
    for axis in AXES:
        values=np.asarray([float(environment[t][axis]) for t in tips],dtype=float)
        z=(values-float(values.mean()))/float(values.std(ddof=1))
        _,edge_delta[axis]=brownian_internal_values(tr,dict(zip(tips,z)))
    _,_,parents,_,_,_,_=tree_structure(tr)
    if set(edge_delta["BIO18"])!=set(parents):
        raise ValueError("original real nuclear tips and reconstructed branch set differ")
    return tr,tips,states,parents,edge_delta


def scores(tree,states,parents,edge_delta,full_detail=False):
    rate=fit_symmetric_q(tree,states)
    like,joint=ctmc_likelihood_and_edge_joint(tree,states,rate,need_joint=True)
    if joint is None or not math.isfinite(like) or like<=0:
        raise ValueError("real fitted phylogenetic endpoint posterior failed")
    keys=sorted(joint)
    signed=np.asarray([float(joint[k][0,1]-joint[k][1,0]) for k in keys])
    discord=np.asarray([float(joint[k][0,1]+joint[k][1,0]) for k in keys])
    denom=float(sum(discord))
    if denom<=0 or any(float(joint[k].sum()-1.0).__abs__()>1e-5 for k in keys):
        raise ValueError("invalid normalized fitted ancestral-state edge joint")
    score={axis:float(np.dot(signed,np.array([edge_delta[axis][k] for k in keys]))/denom)
           for axis in AXES}
    result={
        "q_ER_per_published_calibrated_source_tree_length":rate,
        "exact_joint_endpoint_likelihood":like,
        "total_endpoint_discordance_mass_NOT_number_of_true_events":denom,
        "signed_transition_niche_axis_scores":score,
        "predeclared_composite_plusBIO15_minusBIO1":
            (score["BIO15"]-score["BIO1"])/math.sqrt(2),
    }
    if not full_detail:return result,[]
    nodes=tree_structure(tree)[0]
    edges=[]
    for k in keys:
        J=joint[k];n=nodes[k]
        descendants=[x.name for x in n.get_terminals()]
        edges.append({
            "observed_daughter_tip_if_terminal":descendants[0] if len(descendants)==1 else "",
            "n_descendant_molecular_source_tips":len(descendants),
            "parent_U_child_D_endpoint_joint":float(J[0,1]),
            "parent_D_child_U_endpoint_joint":float(J[1,0]),
            "p_endpoint_discordant":float(J[0,1]+J[1,0]),
            "reconstructed_modern_BIO18_delta_z":edge_delta["BIO18"][k],
            "reconstructed_modern_BIO15_delta_z":edge_delta["BIO15"][k],
            "reconstructed_modern_BIO1_delta_z":edge_delta["BIO1"][k],
            "endpoint_BIO18_signed_contribution":
                float(J[0,1]-J[1,0])*edge_delta["BIO18"][k],
            "claim_boundary":"joint endpoints not actual number/location/time of evolutionary U->D events"
        })
    return result,edges


def directional_value(axis,score):
    return PREDEFINED.get(axis,EXPLORATORY.get(axis))*score


def holm(p):
    order=sorted(p,key=p.get)
    n=len(order)
    raw={}
    previous=0.0
    for rank,axis in enumerate(order):
        previous=max(previous,min(1.,p[axis]*(n-rank)))
        raw[axis]=previous
    return raw


def run_panel(tree,original,env,exclusions,permutations,seed):
    tr,tips,states,parents,deltas=freeze(tree,original,env,exclusions)
    observed,edges=scores(tr,states,parents,deltas,full_detail=True)
    rand=np.random.default_rng(seed)
    sample=np.array(list(tips))
    d_count=sum(v==1 for v in states.values())
    directions=AXES
    observed_dir={ax:directional_value(ax,observed["signed_transition_niche_axis_scores"][ax]) for ax in directions}
    ranks={axis:0 for axis in directions}
    null_means={axis:0.0 for axis in directions}
    for i in range(permutations):
        ds=set(rand.choice(sample,size=d_count,replace=False).tolist())
        shuffled={x:(1 if x in ds else 0) for x in tips}
        s,_=scores(tr,shuffled,parents,deltas,full_detail=False)
        for axis in directions:
            test=directional_value(axis,s["signed_transition_niche_axis_scores"][axis])
            if test>=observed_dir[axis]-1e-12:
                ranks[axis]+=1
            null_means[axis]+=test/permutations
    original_p={ax:(ranks[ax]+1)/(permutations+1) for ax in PREDEFINED}
    root_check=sum(x==1 for x in states.values())
    return {
        "n_ingroup_molecular_source_taxa":len(tips),
        "n_original_source_U":len(tips)-root_check,
        "n_original_source_D":root_check,
        "botanical_mixed_head_excluded":sorted(exclusions),
        "signed_axis_scores":observed["signed_transition_niche_axis_scores"],
        "source_ER_rate_and_endpoint_diagnostic":{
            k:v for k,v in observed.items() if k!="signed_transition_niche_axis_scores"
        },
        "permutation_null":{
            "method":"source_tip_state_count_preserving_random_assignments; not evolutionary/phylogenetic/spatial process",
            "seed":seed,"draws":permutations,
            "direction_axis":{a:("positive" if PREDEFINED.get(a,EXPLORATORY.get(a))==1 else "negative") for a in directions},
            "observed_signed_score_reoriented_to_hypothesis":observed_dir,
            "count_null_at_least_observed":ranks,
            "one_sided_rank_fraction_plus_one":{a:(ranks[a]+1)/(permutations+1) for a in directions},
            "three_user_hypotheses_Holm_adjusted_rank_fraction":holm(original_p),
            "null_mean_reoriented":null_means,
        },
    },edges


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--asset-dir",type=Path,required=True)
    p.add_argument("--outdir",type=Path,required=True)
    p.add_argument("--permutations",type=int,default=N_NULL)
    a=p.parse_args()
    if a.permutations!=N_NULL:
        raise ValueError("cannot silently change preregistered 999 molecular tip-label null draws")
    tree,names,original,env=source(a.asset_dir)
    full,edges=run_panel(tree,original,env,[],N_NULL,SEED)
    strict,_=run_panel(tree,original,env,AMBIGUOUS_HEAD,N_NULL,SEED)
    out={
        "version":"Siniscalchi2023_NA_nuclear_BIO18_BIO15_BIO1_U_D_ancestral_endpoint_niche_v1",
        "source":"Siniscalchi et al. 2023 independently published NA Cirsium nuclear chronogram, fully authenticated original flower U/D categories and species modern environment means",
        "preselected_before_this_fit":["higher BIO18 warmest-quarter precipitation after U->D","higher BIO15 seasonality after U->D","lower BIO1 annual temperature after U->D"],
        "exploratory_PostHoc_from_same_data":"Mixed (mixed forest cover), selected by earlier morphology/environment screen; its permutation rank is NOT independent validation",
        "model":"symmetric two-state Mk CTMC with equal 0.5 source ingroup root prior; Brownian reconstruction of CONTEMPORARY taxon environment means; signed P(parent U,child D) minus P(parent D,child U) endpoint mass weighted by branch's reconstructed contemporary-niche difference",
        "original_author_62_taxon_panel":full,
        "fna_60_taxon_mixed_head_veto_sensitivity":strict,
        "source_branchwise_endpoint_detail_file":"NA62_original_nuclear_BIO18_signed_endpoint_diagnostics.csv",
        "chronogram_time_scale":"published NA molecular chronogram units; no measured historical environmental field",
        "neither_model_is_historical_climate_at_actual_event":True,
        "no_transition_event_count_identified":True,
        "few_D_source_species_original":5,
        "null_not_phylogenetic_stochastic_process_calibrated":True,
        "causality_and_pollinator_selection_not_inferred":True,
        "full_world_294tip_350gene_tree_available":False,
    }
    a.outdir.mkdir(parents=True,exist_ok=True)
    (a.outdir/"NA62_BIO18_u2d_nuclear_EAzami_style_concordance.json").write_text(
        json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    with (a.outdir/"NA62_original_nuclear_BIO18_signed_endpoint_diagnostics.csv").open(
        "w",encoding="utf-8",newline="") as h:
        writer=csv.DictWriter(h,fieldnames=list(edges[0]))
        writer.writeheader();writer.writerows(edges)
    print(json.dumps({
        "n_real_nuclear_source_taxa":full["n_ingroup_molecular_source_taxa"],
        "D_source_taxa":full["n_original_source_D"],
        "full_signed_axis_scores":full["signed_axis_scores"],
        "full_directional_label_null":full["permutation_null"]["one_sided_rank_fraction_plus_one"],
        "full_Holm_three_axes":full["permutation_null"]["three_user_hypotheses_Holm_adjusted_rank_fraction"],
        "FNA_exclusion_signed_axis_scores":strict["signed_axis_scores"],
        "FNA_exclusion_directional_label_null":strict["permutation_null"]["one_sided_rank_fraction_plus_one"],
        "not_historical_event_causation":True,
    },indent=2))


if __name__=="__main__":
    main()
