#!/usr/bin/env python3
"""Robustness of ecological candidates from 333 nuclear-phylogenetic trait×environment tests.

All hypotheses tested below are POST HOC picked from the same 62 NA species;
none is an independent replication. Original environmental variable (modern
species taxon mean) remains the response, original 9-trait morphological
category is the factor. Uses same original source molecular tree BM covariance.
Leave-one-taxon-out refits are diagnostics for influential species.
"""
from __future__ import annotations

import argparse,copy,csv,json,math
from collections import Counter
from pathlib import Path

import numpy as np

from run_siniscalchi2023_NA_nuclear_BIO18_full9trait_envscreen_v1 import (
    source,covariance,cleanvec,gls_test,AMBIGUOUS_HEAD,
)

TARGETS=(
    ("HeadPosition","Mixed"),
    ("GlutinousRidge","BIO5"),
    ("GlutinousRidge","Slope"),
    ("OuterPhyllaryPosition","BIO3"),
    ("InnerPhyllaryColor","Mixed"),
    ("InnerPhyllaryColor","Clay"),
)
FULL_PQL=[
  (0.0007020367286384914,0.044341),
  (0.0007989445258221749,0.044341),
  (0.0005422715617074714,0.044341),
  (0.0005430610277807337,0.044341),
  (0.000030553428711389946,0.010174),
  (0.00012639014236396427,0.021044),
]


def fit(tr,names,traits,env,char,axis,other=()):
    cs=[traits[t][char] for t in names]
    yy=cleanvec([float(env[t][axis]) for t in names])
    chol,jitter=covariance(tr,names)
    extra=None
    if other:
        extra=np.column_stack([cleanvec([float(env[t][ax]) for t in names]) for ax in other])
    result=gls_test(yy,cs,chol,extra_covariates=extra)
    if result is None:raise ValueError("source trait PGLS not estimable")
    return result


def run(assets,outdir):
    tree,names,traits,env=source(assets)
    out=[]
    source_states={x:dict(Counter(traits[t][x] for t in names)) for x in {x for x,_ in TARGETS}}
    for char,axis in TARGETS:
        observed=fit(tree,names,traits,env,char,axis)
        counts=Counter(traits[t][char] for t in names)
        least=min(counts.values())
        minors=[cat for cat,n in counts.items() if n==least]
        leave_one=[]
        for tip in names:
            tr=copy.deepcopy(tree);tr.prune(tip)
            kept=[x for x in names if x!=tip]
            value=fit(tr,kept,traits,env,char,axis)
            leave_one.append({
                "omitted_source_taxon":tip,
                "source_removed_original_category":traits[tip][char],
                "original_category_is_rarest":traits[tip][char] in minors,
                "refit_n":len(kept),
                "refit_p":value["p"],
                "refit_standardized_difference_1_vs_0":
                    value.get("standardized_difference_level_1_minus_0"),
                "original_full_min_category_n":least
            })
        rare=[x for x in leave_one if x["original_category_is_rarest"]]
        report={
            "morphological_character":char,
            "source_environment_variable":axis,
            "source_original_levels":dict(sorted(counts.items())),
            "sparse_category_with_one_or_two_taxa":least<3,
            "original_real_nuclear_PGLS_F":observed["Fstat"],
            "original_real_nuclear_PGLS_p":observed["p"],
            "full62_original_effect_sd":observed.get("standardized_difference_level_1_minus_0"),
            "all_source_62_omissions":[x["refit_p"] for x in leave_one],
            "leave_one_full_range_p":[min(x["refit_p"] for x in leave_one),
                                       max(x["refit_p"] for x in leave_one)],
            "n_individually_dropped_source_taxa":len(leave_one),
            "fraction_leave_one_p_under_0_05":sum(x["refit_p"]<.05 for x in leave_one)/len(leave_one),
            "rarest_source_category_n":least,
            "rarest_category_leave_one_p_range":[min(x["refit_p"] for x in rare),
                                                  max(x["refit_p"] for x in rare)],
            "not_new_independent_p_values":True,
        }
        if char=="HeadPosition" and axis=="Mixed":
            # Source ambiguous erect/nodding taxon descriptions remain
            # uncertain regardless of original forced binary author coding.
            tr=copy.deepcopy(tree)
            for t in AMBIGUOUS_HEAD:tr.prune(t)
            kept=[t for t in names if t not in AMBIGUOUS_HEAD]
            report["FNA_60tip_mixed_head_excluded"]=fit(tr,kept,traits,env,char,axis)
            report["Mixed_forest_given_BIO18_BIO15_BIO1"]=fit(
                tree,names,traits,env,char,axis,("BIO18","BIO15","BIO1"))
        elif char=="GlutinousRidge" and axis=="BIO5":
            report["BIO5_given_Slope_and_Elevation"]=fit(
                tree,names,traits,env,char,axis,("Slope","Elevation"))
        elif char=="GlutinousRidge" and axis=="Slope":
            report["Slope_given_BIO5_and_Elevation"]=fit(
                tree,names,traits,env,char,axis,("BIO5","Elevation"))
        elif char=="OuterPhyllaryPosition" and axis=="BIO3":
            report["BIO3_given_Elevation"]=fit(
                tree,names,traits,env,char,axis,("Elevation",))
        out.append((report,leave_one))
    outdir.mkdir(parents=True,exist_ok=True)
    with (outdir/"NA62_original_nuclear_selected_morphology_env_leave1taxon.csv").open("w",encoding="utf-8",newline="") as h:
        fields=["morphology","environment","omitted_source_taxon","source_removed_original_category",
           "original_category_is_rarest","refit_n","refit_p","refit_standardized_difference_1_vs_0",
           "original_full_min_category_n"]
        w=csv.DictWriter(h,fieldnames=fields);w.writeheader()
        for d,rows in out:
            for row in rows:
                w.writerow({"morphology":d["morphological_character"],
                            "environment":d["source_environment_variable"],**row})
    report={
        "version":"NA62_original_nuclear_6_source_candidates_loo_phylogenetic_robustness_v1",
        "selection":"Six already discovered associations from same original nine-trait×37 environment PGLS screen; post-hoc sensitivity only",
        "n_original_nuclear_ingroup_species":62,
        "original_source_trait_taxon_voucher_not_same_individual":True,
        "three_mechanistic_nonexclusive_alternatives":"photosynthetic/warmth-water balance, mechanical defence/sticky insect contact, seasonal pollinator community; each is a hypothesis not causal inference",
        "source_gene_tree":"Siniscalchi et al. 2023 original Compositae1061 nuclear dated molecular tree; source immutable c925d4af86160064448f794a9715f70b917a2786",
        "original_authoritative_fna_mixed_head_names":sorted(AMBIGUOUS_HEAD),
        "environment_is_current_taxon_species_mean_not_historical_paleoclimate":True,
        "associations":[x[0] for x in out],
        "no_independent_validation":"All six chosen after looking at the same PGLS p/q values; regression and leave-one analysis evaluate sensitivity but are NOT validation in a separate phylogenetic dataset.",
        "no_global_Moreyra_294tip_nuclear_tree":True
    }
    (outdir/"NA62_nuclear_6candidate_morphology_environment_leaveone_report.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"n_original_real_nuclear_taxa":62,
        "six_actual_morphology_environment_candidate_associations":[{
            "morphology":x["morphological_character"],"environment":x["source_environment_variable"],
            "n_min_original_category":x["rarest_source_category_n"],
            "PGLS_p":x["original_real_nuclear_PGLS_p"],
            "leave_one_range_p":x["leave_one_full_range_p"],
            "n_loo_p_under05":round(x["fraction_leave_one_p_under_0_05"],3),
            "conditional_p_values":{k:v["p"] for k,v in x.items() if isinstance(v,dict) and "p" in v}
        } for x,_ in out]},indent=2),flush=True)
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--assets",type=Path,required=True)
    p.add_argument("--outdir",type=Path,required=True)
    a=p.parse_args()
    run(a.assets,a.outdir)


if __name__=="__main__":
    main()
