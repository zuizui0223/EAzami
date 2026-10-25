#!/usr/bin/env python3
"""EAzami true-world52 source nuclear U/D: irreversible vs reversible Mk models.

Fit four explicit biologically distinct *statistical* processes on three REAL
source-verified and de-duplicated Moreyra 2025 52-tip nuclear trees:

  irreversible_UD: q(U->D)>0, q(D->U)=0
  irreversible_DU: q(U->D)=0, q(D->U)>0
  ER_reversible:    q(U->D)=q(D->U)>0
  ARD_reversible:   both rates>0 and independently fitted.

These are homogeneous taxon-level source state models, NOT proofs of molecular
gain/regain or experimentally measured selected evolutionary directions.
Unknown head states integrate as [1,1]. The original Carthamus molecular
outgroup roots each DNA tree, but receives NO Cirsium morphological state.
Both irreversible models are compared under EXACTLY THE SAME fixed ingroup
root U prior as the reversible models; 0.1 and 0.9 sensitivity is explicit.
Original 294-BioSample/350-locus global nuclear phylogeny remains unbuilt.

The published original Moreyra S1 contains molecular voucher/BioSample IDs, not
the nine Siniscalchi botanical phenotypes. Character states are independent
source-taxon botanical observations, not measured on the sequenced individuals.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from Bio import Phylo
from scipy.optimize import minimize, minimize_scalar

PINS={
    "full176":"ef4a93f8b39dfda19180903f5e39b57a8a34eda293060a57ab30fea46b377fb3",
    "high_occupancy75":"58296516b78f3b4200e015fa7503ef11035af7cd58940fe26e6be39c518b894b",
    "pipeline_qc73":"3830972a1b747684a69e90fa7bc1b1a22102e703b6db1f4d5411cee3260423b5",
}
PHENOTYPE_SHA="1a4629347007b73b900db5b7c36fba345933281b9868d1c9555f4a1906100962"
OUTGROUP="OUTGROUP_saff"
NA_D="GLB_SRR30887231_Cirsium_vinaceum"
EU_D="GLB_SRR30887186_Cirsium_erisithales"
MODELS=("irreversible_UD","irreversible_DU","ER_reversible","ARD_reversible")
ROOT_PRIORS=(0.1,0.5,0.9)
LOG_BOUNDS=(-12.,17.)


def digest(path:Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_traits(path:Path):
    if digest(path)!=PHENOTYPE_SHA:
        raise ValueError("corresponding real original corrected-world52 Moreyra source phenotype SHA changed")
    with path.open("r",encoding="utf-8-sig",newline="") as handle:
        rows=list(csv.DictReader(handle))
    if len(rows)!=52 or len({r["tip_id"] for r in rows})!=52:
        raise ValueError("not 52 exactly unique S1 source molecular tips")
    orig={r["tip_id"]:r for r in rows}
    if orig[OUTGROUP]["head_orientation"] not in {"?",""}:
        raise ValueError("Carthamus molecular outgroup cannot receive a Cirsium U/D head")
    ingroup={k:r for k,r in orig.items() if k!=OUTGROUP}
    assert len(ingroup)==51
    if len({r["source_biosample"] for r in ingroup.values()})!=51:
        raise ValueError("the original repeated J38S038 / GLB2 SRR source was not de-duplicated")
    tally=Counter(r["head_orientation"] for r in ingroup.values())
    if tally!=Counter({"U":19,"D":8,"?":24}):
        raise ValueError("the original 51 unique BioSample head evidence changed")
    for name in (NA_D,EU_D):
        if ingroup[name]["head_orientation"]!="D":
            raise ValueError("source name-specific D holdout no longer corresponds to original DNA panel")
    for r in ingroup.values():
        if r["head_orientation"] in {"U","D"} and not r["head_source_url"]:
            raise ValueError("original phenotype admitted without a botanical source link")
    return ingroup


def taxon_concept(name:str):
    m=re.match(r"^(Cirsium)\s+([a-z][a-z-]+)(?:\s+var\.\s+([a-z][a-z-]+))?",name)
    if not m:
        raise ValueError("cannot preserve original taxonomic varietal concept: "+name)
    genus, species, variety = m.groups()
    return f"{genus} {species}" + (f" var. {variety}" if variety else "")


def compile_real_tree(path:Path,expected:str,source:dict):
    if digest(path)!=expected:
        raise ValueError("real re-inferred world52 source phylogram Newick fingerprint drift")
    tr=Phylo.read(path,"newick")
    original={x.name for x in tr.get_terminals()}
    if len(original)!=52 or original!=set(source)|{OUTGROUP}:
        raise ValueError("52-tip DNA tree does not correspond to 51 original BioSamples plus Carthamus")
    tr.root_with_outgroup({"name":OUTGROUP})
    tr.prune(OUTGROUP)
    if len(tr.root.clades)==1:
        tr.root=tr.root.clades[0]
        tr.root.branch_length=None
    nodes=list(tr.find_clades(order="preorder"))
    index={id(n):i for i,n in enumerate(nodes)}
    children=[[(index[id(c)],max(float(c.branch_length or 0),1e-10))
               for c in n.clades] for n in nodes]
    postorder=[index[id(n)] for n in tr.find_clades(order="postorder")]
    tip_positions={n.name:index[id(n)] for n in tr.get_terminals()}
    if len(tip_positions)!=51 or set(tip_positions)!=set(source):
        raise ValueError("Cirsium-only rooted 51-BioSample tree lost original molecular tip")
    return {"children":children,"postorder":postorder,"tips":tip_positions,
            "n_nodes":len(nodes),"name_sha256":expected}


def transition(a:float,b:float,t:float):
    """Exact two-state CTMC edge matrix, including zero-rate directional models."""
    total=a+b
    if total<=0 or t<0 or not math.isfinite(total+t):
        raise ValueError("finite model rate and branch length required")
    switched=-math.expm1(-total*t)
    return np.array([[1-a/total*switched,a/total*switched],
                     [b/total*switched,1-b/total*switched]],dtype=float)


def likelihood(layout,phenotype,rate_u_d,rate_d_u,root_prior_U):
    if not 0<root_prior_U<1:
        raise ValueError("nondegenerate fixed root prior required")
    inside=np.ones((layout["n_nodes"],2),dtype=float)
    for tip,i in layout["tips"].items():
        if tip not in phenotype:
            raise ValueError("wrong source taxon ID in Mk fit")
        state=phenotype[tip]
        if state=="U":
            inside[i]=[1.,0.]
        elif state=="D":
            inside[i]=[0.,1.]
        elif state=="?":
            inside[i]=[1.,1.]  # Integrate actual missing botanically unscored tip
        else:
            raise ValueError("illegal morphology state")
    for i in layout["postorder"]:
        for child,length in layout["children"][i]:
            inside[i]*=transition(rate_u_d,rate_d_u,length) @ inside[child]
    Z=float(np.dot([root_prior_U,1-root_prior_U],inside[0]))
    if Z<=0 or not math.isfinite(Z):
        return -math.inf
    return math.log(Z)


def fit(layout,phenotype,model,rootprior):
    def evaluate(z):
        if model=="ARD_reversible":
            a,b=math.exp(float(z[0])),math.exp(float(z[1]))
        else:
            q=math.exp(float(z[0]))
            a,b=({"irreversible_UD":(q,0.),
                  "irreversible_DU":(0.,q),
                  "ER_reversible":(q,q)}[model])
        return -likelihood(layout,phenotype,a,b,rootprior)
    if model=="ARD_reversible":
        starts=[[3.,3.],[6.,6.],[8.,6.],[6.,8.]]
        fitlist=[minimize(evaluate,np.array(s),method="L-BFGS-B",
                          bounds=[LOG_BOUNDS,LOG_BOUNDS],
                          options={"maxiter":350,"ftol":1.e-12}) for s in starts]
        successful=[r for r in fitlist if np.isfinite(r.fun)]
        if not successful:
            raise RuntimeError("ARD profile returned no finite likelihood")
        winner=min(successful,key=lambda s:s.fun)
        logs=[float(k) for k in winner.x]
    else:
        opt=minimize_scalar(lambda v:evaluate([v]),method="bounded",
                            bounds=LOG_BOUNDS,options={"xatol":1.e-8})
        if not opt.success or not math.isfinite(opt.fun):
            raise RuntimeError("Mk 1D optimization failed")
        logs=[float(opt.x)]
    loglik=-evaluate(logs)
    rates=[math.exp(x) for x in logs]
    qa,qb=(rates if model=="ARD_reversible" else
           (rates[0],0.) if model=="irreversible_UD" else
           (0.,rates[0]) if model=="irreversible_DU" else
           (rates[0],rates[0]))
    if not math.isfinite(loglik):
        raise RuntimeError("nonfinite fitted Mk likelihood")
    return {"logL":loglik,"qUD":qa,"qDU":qb,
            "at_rate_boundary":any(abs(x-LOG_BOUNDS[0])<0.01 or
                                   abs(x-LOG_BOUNDS[1])<0.01 for x in logs),
            "nparams":2 if model=="ARD_reversible" else 1}


def fit_case(layout,source,case,prior):
    states={k:r["head_orientation"] for k,r in source.items()}
    if case=="omit_NA_selected_D":
        states[NA_D]="?"
    elif case=="omit_West_cultivated_D":
        states[EU_D]="?"
    elif case!="all_source_states":
        raise ValueError("unknown prior-to-analysis morphological sensitivity")
    counts=Counter(states.values())
    if counts["U"]<2 or counts["D"]<2 or counts["?"]<20:
        raise ValueError("insufficient independently observed source head states")
    groups={taxon_concept(source[k]["source_taxon"]) for k,s in states.items() if s!="?"}
    n=len(groups)
    fits={}
    for model in MODELS:
        values=fit(layout,states,model,prior)
        par=values["nparams"]
        values["AICc"]=2*par-2*values["logL"]+2*par*(par+1)/(n-par-1)
        fits[model]=values
    return fits,{"n_observed_U":counts["U"],"n_observed_D":counts["D"],
                 "n_unknown":counts["?"],"n_taxon_concepts":n}


def run(paths,trait_path,reference_csv,outdir):
    source=source_traits(trait_path)
    with reference_csv.open("r",encoding="utf-8",newline="") as handle:
        prior_rows=list(csv.DictReader(handle))
    reference={(r["nuclear_tree"],r["source_head_panel"],r["Mk_model"]):r
               for r in prior_rows}
    if len(reference)!=18:
        raise ValueError("independent previously fitted original ER/ARD corrected real-data reference has drifted")
    panels=("all_source_states","omit_NA_selected_D","omit_West_cultivated_D")
    name_map={"all_source_states":"primary_all_source_states",
              "omit_NA_selected_D":"north_america_D_unresolved",
              "omit_West_cultivated_D":"west_D_cultivated_unresolved"}
    fits=[]
    comparisons=[]
    for name,path in paths.items():
        if name not in PINS:
            raise ValueError("unexpected nuclear tree model panel")
        layout=compile_real_tree(path,PINS[name],source)
        for panel in panels:
            priors=ROOT_PRIORS if panel=="all_source_states" else (0.5,)
            for prior in priors:
                models,counts=fit_case(layout,source,panel,prior)
                reversible=min(models["ER_reversible"]["AICc"],models["ARD_reversible"]["AICc"])
                one_way=min(models["irreversible_UD"]["AICc"],models["irreversible_DU"]["AICc"])
                for model,val in models.items():
                    row={"tree":name,"trait_case":panel,"root_prior_U_fixed":prior,
                         "model":model,**counts,
                         "log_likelihood":val["logL"],"AICc":val["AICc"],
                         "q_UD_per_substitution":val["qUD"],
                         "q_DU_per_substitution":val["qDU"],
                         "optimizer_boundary":val["at_rate_boundary"],
                         "delta_AICc_vs_best_model":val["AICc"]-min(x["AICc"] for x in models.values())}
                    fits.append(row)
                    if prior==0.5 and model in {"ER_reversible","ARD_reversible"}:
                        old_model="ER" if model=="ER_reversible" else "ARD"
                        orig=reference[(name,name_map[panel],old_model)]
                        if abs(float(orig["Mk_log_likelihood"])-val["logL"])>0.015:
                            raise ValueError("reversible Mk refit deviates from previously executed independent source fit")
                        if abs(float(orig["AICc_taxon_concept_n_approx"])-val["AICc"])>0.015:
                            raise ValueError("AICc source taxon panel inconsistency")
                comparisons.append({"tree":name,"trait_case":panel,"root_prior_U_fixed":prior,
                    "AICc_U_to_D_only":models["irreversible_UD"]["AICc"],
                    "AICc_D_to_U_only":models["irreversible_DU"]["AICc"],
                    "AICc_ER":models["ER_reversible"]["AICc"],
                    "AICc_ARD":models["ARD_reversible"]["AICc"],
                    "delta_best_irreversible_minus_best_reversible":one_way-reversible,
                    "delta_UD_only_minus_ARD":models["irreversible_UD"]["AICc"]-models["ARD_reversible"]["AICc"],
                    "delta_DU_only_minus_ARD":models["irreversible_DU"]["AICc"]-models["ARD_reversible"]["AICc"],
                    **counts})
    if len(fits)!=60 or len(comparisons)!=15:
        raise AssertionError("expected 60 actual source likelihood fits over 15 fixed scenarios")
    selected=[r for r in comparisons if r["trait_case"]=="all_source_states" and r["root_prior_U_fixed"]==0.5]
    if len(selected)!=3:
        raise ValueError("missing primary across-three-source-tree test")
    output={
      "version":"real_unique52_176_75_73_Moreyra_nuclear_four_directional_Mk_AICc_v1",
      "original_unique_biosample_source":51,
      "molecular_tree_tips_with_original_outgroup":52,
      "original_source_morphology":{"U":19,"D":8,"unknown":24},
      "n_observed_unique_source_taxa":27,
      "source_S1_molecular_voucher_not_direct_botanical_phenotype":True,
      "compared_processes":{
        "irreversible_UD":"U→D transitions allowed, D→U exactly zero",
        "irreversible_DU":"D→U transitions allowed, U→D exactly zero",
        "ER_reversible":"equal positive U→D and D→U rates",
        "ARD_reversible":"separately fitted positive U→D and D→U rates"},
      "source_root_prior_stress":[0.1,0.5,0.9],
      "root_prior_same_for_all_four_processes_per_comparison":True,
      "three_real_nuclear_tree_SHA256":PINS,
      "original_unchanged_botanical_tip_table_SHA256":PHENOTYPE_SHA,
      "reversible_likelihood_AICc_crosschecked_against_original_Mk_run":True,
      "main_PU0p5_all_source_model_results":selected,
      "source_case_holds":["omit_NA_selected_D","omit_West_cultivated_D"],
      "source_main_delta_UDonly_minus_best_reversible_range":[
        min(r["delta_best_irreversible_minus_best_reversible"] for r in selected),
        max(r["delta_best_irreversible_minus_best_reversible"] for r in selected)],
      "scientific_boundaries":[
        "AICc is approximate with 27 observed original taxon concepts; state counts are not independent species-level phenotyping of sequenced vouchers.",
        "If reversible is favored over an irreversible homogeneous CTMC, that is evidence AGAINST the restrictive one-way homogeneous model on these trees. It does not demonstrate an actual observed D→U reversal or an ancestral U state.",
        "One-way models constrain the ancestral root state by allowing only one direction whenever both states occur. Prior stress is therefore essential.",
        "Previously fitted ER and ARD process rates are large relative to molecular branch lengths, and conditional jump counts include arbitrarily many hidden reversals; no directly observed independent evolutionary origin count follows.",
        "Trait-informed initial external source sampling, missing 24 source phenotype states and globally sparse 51 unique specimens limit broad evolutionary interpretation.",
        "The 3 genetic source trees are alternative alignments of the SAME biological samples, NOT replicated global evolutionary events.",
        "Moreyra accepted 294 BioSample / final 350 single-copy target gene world phylogeny remains unavailable; the present analysis uses 176/75/73 original nuclear loci."
      ]
    }
    outdir.mkdir(parents=True,exist_ok=True)
    def write(path,rows):
        with path.open("w",encoding="utf-8",newline="") as handle:
            w=csv.DictWriter(handle,fieldnames=list(rows[0]))
            w.writeheader();w.writerows(rows)
    write(outdir/"world52_four_directional_CTMC_real_model_fits.csv",fits)
    write(outdir/"world52_irreversibility_vs_reversible_real_AICc_sensitivity.csv",comparisons)
    (outdir/"world52_directional_irreversibility_real_nuclear_S1_contract.json").write_text(
        json.dumps(output,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    plot(outdir,comparisons)
    print(json.dumps({"real_unique_Cirsium_BioSamples":51,
        "n_real_model_fits":len(fits),
        "main_model_results":selected,
        "no_true_historical_reversal_claim":True},indent=2))
    return output


def plot(outdir,comparisons):
    fig,axes=plt.subplots(1,2,figsize=(12,4.6))
    main=[x for x in comparisons if x["root_prior_U_fixed"]==0.5]
    cases=["all_source_states","omit_NA_selected_D","omit_West_cultivated_D"]
    models=list(PINS)
    colors=plt.rcParams["axes.prop_cycle"].by_key()["color"]
    for i,t in enumerate(models):
        y=[next(r for r in main if r["tree"]==t and r["trait_case"]==case)[
           "delta_best_irreversible_minus_best_reversible"] for case in cases]
        axes[0].plot(range(3),y,"o-",label=t,color=colors[i])
    axes[0].axhline(0,color="#555555",lw=1,ls="--")
    axes[0].set_xticks(range(3),["All source states","NA D omitted","EU D omitted"],rotation=18)
    axes[0].set_ylabel("ΔAICc: best irreversible − best reversible")
    axes[0].set_title("One-way model penalty by source taxa")
    axes[0].legend(frameon=False,fontsize=8)
    for i,t in enumerate(models):
        x=[r for r in comparisons if r["tree"]==t and r["trait_case"]=="all_source_states"]
        x=sorted(x,key=lambda r:r["root_prior_U_fixed"])
        axes[1].plot([r["root_prior_U_fixed"] for r in x],
                     [r["delta_best_irreversible_minus_best_reversible"] for r in x],
                     "o-",label=t,color=colors[i])
    axes[1].axhline(0,color="#555555",lw=1,ls="--")
    axes[1].set_xlabel("Fixed source ingroup root P(U)")
    axes[1].set_title("Ancestral-root assumption sensitivity")
    axes[1].set_xticks(ROOT_PRIORS)
    fig.suptitle("World52 nuclear DNA: directional Mk constraints on real S1 taxon states\n"
                 "51 unique Cirsium BioSamples, 19 U / 8 D / 24 unknown; AICc is descriptive",fontsize=10)
    fig.tight_layout()
    fig.savefig(outdir/"world52_irreversible_vs_reversible_nuclear_Mk_AICc.png",
                dpi=200,bbox_inches="tight")
    fig.savefig(outdir/"world52_irreversible_vs_reversible_nuclear_Mk_AICc.svg",
                bbox_inches="tight")
    plt.close(fig)


def main():
    ap=argparse.ArgumentParser()
    for name in ("full176","high-occupancy75","pipeline-qc73",
                 "traits","original-corrected-Mk-reference","outdir"):
        ap.add_argument("--"+name,type=Path,required=True)
    args=ap.parse_args()
    run({"full176":args.full176,
         "high_occupancy75":args.high_occupancy75,
         "pipeline_qc73":args.pipeline_qc73},
         args.traits,args.original_corrected_Mk_reference,args.outdir)


if __name__=="__main__":
    main()
