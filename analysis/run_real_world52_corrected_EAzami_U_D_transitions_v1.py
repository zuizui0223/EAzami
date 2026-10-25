#!/usr/bin/env python3
"""EAzami U<->D transitions on CORRECTED true-52-tip ORIGINAL nuclear phylogenies.

51 unique source Cirsium BioSamples + an actual Carthamus outgroup.  The older
53-tip pilot duplicated SAMN44017865/SRR30887251 under two tip names and is
retracted for evolutionary inference. This analysis REFITS to three genuinely
newly inferred, independent-inference (NOT independent datasets) phylogenies:
176 original Compositae1061 nuclear loci, 75 all-12-external-covered loci,
and 73 loci after technical same-SRR pipeline-disagreement filtering.

Separate:
  (i) Fitch minimum changes, and geographically/study-blocked 27-taxon
      morphology-label permutation (not an unconditional evolutionary null).
 (ii) ER versus ARD two-state continuous-time Markov Mk likelihood,
      24 unscored heads marginalized, actual root posterior and fixed-q prior
      sensitivity, original North-American/Western-D taxon omission.
(iii) Exact conditional expected U->D / D->U history jumps using Van Loan
      Markov reward integrals. These include arbitrarily many hidden cycles,
      can become huge under q saturation, and NEVER count independent
      observed historical origins or actual dated evolution events.

Source botanical head states attach to taxon concepts, NOT the sequenced
S1 voucher. The Japan38 genetic PAPER category includes non-Japan-collected
samples and is only a sampling-study stratum, not a country-of-origin gate.
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import math
from collections import Counter,defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from Bio import Phylo

from fit_real_world45_multitopology_U_D_mk_v1 import fit_one
from run_real_world53_EAzami_transition_signal_Mk_reward_v1 import (
    concept,compiled_fitch,fitch,exact_markov_rewards,
    root_prior_sensitivity,permute_observed
)

OUTGROUP="OUTGROUP_saff"
NA_D="GLB_SRR30887231_Cirsium_vinaceum"
EU_D="GLB_SRR30887186_Cirsium_erisithales"
REMOVED_DUP="GLB2_SRR30887251_Cirsium_kamtschaticum"
REAL_J38_KAM="J38S038"
PINS={
    "full176":"ef4a93f8b39dfda19180903f5e39b57a8a34eda293060a57ab30fea46b377fb3",
    "high_occupancy75":"58296516b78f3b4200e015fa7503ef11035af7cd58940fe26e6be39c518b894b",
    "pipeline_qc73":"3830972a1b747684a69e90fa7bc1b1a22102e703b6db1f4d5411cee3260423b5",
    "source_traits":"1a4629347007b73b900db5b7c36fba345933281b9868d1c9555f4a1906100962",
}
PRIMARY_CASES={
    "primary_all_source_states":None,
    "west_D_cultivated_unresolved":EU_D,
    "north_america_D_unresolved":NA_D,
}
DEFAULT_SEED=2317
DEFAULT_PERMUTATIONS=20000


def digest(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_source_table(path:Path):
    if digest(path)!=PINS["source_traits"]:
        raise ValueError("molecular-source S1 and independent botanical source CSV SHA drift")
    with path.open(encoding="utf-8-sig",newline="") as h:
        raw=list(csv.DictReader(h))
    if len(raw)!=52 or len({r["tip_id"] for r in raw})!=52:
        raise ValueError("corrected tree must have 52 DISTINCT molecular tip labels")
    allrows={r["tip_id"]:r for r in raw}
    if OUTGROUP not in allrows or allrows[OUTGROUP]["head_orientation"] not in {"?",""}:
        raise ValueError("Carthamus must be a molecular-only outgroup without fabricated Cirsium phenotype")
    del allrows[OUTGROUP]
    if len(allrows)!=51 or len({r["source_biosample"] for r in allrows.values()})!=51:
        raise ValueError("unique original source BioSample identity violated")
    if REMOVED_DUP in allrows or REAL_J38_KAM not in allrows:
        raise ValueError("duplicate processing of SRR30887251 was not removed before trait analysis")
    if allrows[REAL_J38_KAM]["source_biosample"]!="SAMN44017865":
        raise ValueError("retained source C. kamtschaticum BioSample provenance changed")
    counts=Counter(r["head_orientation"] for r in allrows.values())
    if counts!=Counter({"U":19,"D":8,"?":24}):
        raise ValueError("original botanical head U/D/unknown source counts drift")
    if (allrows[NA_D]["head_orientation"]!="D" or
        allrows[EU_D]["head_orientation"]!="D"):
        raise ValueError("two original external D botanical authority source records drift")
    taxon_rows=defaultdict(list)
    strata=defaultdict(list)
    for row in allrows.values():
        state=row["head_orientation"]
        label=concept(row["source_taxon"])
        if state not in {"U","D","?"}:
            raise ValueError("unsupported/orphan head state")
        if state in {"U","D"}:
            if not row["head_source_url"]:
                raise ValueError("no original morphological source URL for an admitted head state")
            taxon_rows[label].append(row)
    if len(taxon_rows)!=27:
        raise ValueError("original source resolving U/D must yield 27 botanical taxon concepts")
    assignments={}
    for taxon,samples in taxon_rows.items():
        states={r["head_orientation"] for r in samples}
        if len(states)!=1:
            raise ValueError("source botanical taxon concept has conflicting head descriptions")
        assignments[taxon]=samples[0]["head_orientation"]
        # CRITICAL: name of this original stratum is a PAPER source cohort,
        # not a region where each historical voucher physically grew.
        strata[samples[0]["region"]].append(taxon)
    if set(strata)!={"Japan38_2025_moreyra","North_America","West_Palearctic"}:
        raise ValueError("original genetic study/sample geography strata have changed")
    expected={
        "Japan38_2025_moreyra":{"U":14,"D":5},
        "North_America":{"U":4,"D":2},
        "West_Palearctic":{"U":1,"D":1}
    }
    found={name:dict(Counter(assignments[x] for x in ss)) for name,ss in strata.items()}
    if found!=expected:raise ValueError("original taxon-block permutation stratum states changed")
    for varname in ("Cirsium nipponicum var. incomptum","Cirsium nipponicum var. yoshinoi"):
        original=[r for r in allrows.values() if concept(r["source_taxon"])==varname]
        if not original or any(r["head_orientation"]!="?" for r in original):
            raise ValueError("do not infer Cirsium nipponicum named variety states from species")
    return allrows, taxon_rows, assignments, strata


def load_tree(path:Path,name:str,original:dict):
    if digest(path)!=PINS[name]:
        raise ValueError("corrected unique original-BioSample real nucleotide phylogeny checksum drift")
    tree=Phylo.read(path,"newick")
    tips=[t.name for t in tree.get_terminals()]
    if len(tips)!=len(set(tips))!=52 or set(tips)!={OUTGROUP}|set(original):
        raise ValueError("new empirical nuclear tree not exactly 51 unique Cirsium plus outgroup")
    tree.root_with_outgroup({"name":OUTGROUP})
    tree.prune(OUTGROUP)
    while len(tree.root.clades)==1 and not tree.root.is_terminal():
        tree.root=tree.root.clades[0]
        tree.root.branch_length=None
    for x in tree.find_clades():
        if x is tree.root:continue
        if x.branch_length is None or not math.isfinite(float(x.branch_length)) or float(x.branch_length)<0:
            raise ValueError("original molecular tree has missing or negative substitution branch length")
    return tree


def model_ancestral(tree,original,case):
    state={k:dict(v) for k,v in original.items()}
    if case not in PRIMARY_CASES:
        raise ValueError("scientific source phenotype holdout not prespecified")
    if PRIMARY_CASES[case]:
        tip=PRIMARY_CASES[case]
        if state[tip]["head_orientation"]!="D":
            raise ValueError("source originally observed D morphological record was overwritten")
        state[tip]["head_orientation"]="?"
    return state


def execute(*,trees:dict[str,Path],traits:Path,outdir:Path,nperm:int,seed:int):
    original,groups,known,strata=validate_source_table(traits)
    parsed={name:load_tree(path,name,original) for name,path in trees.items()}
    null=permute_observed(parsed,original,groups,known,strata,nperm,seed)
    results=[]
    edge_rows=[]
    for name,tree in parsed.items():
        scorer=compiled_fitch(tree,original)
        for case in PRIMARY_CASES:
            state=model_ancestral(tree,original,case)
            n=Counter(r["head_orientation"] for r in state.values())
            assigned={concept(r["source_taxon"]):r["head_orientation"]
                      for r in state.values() if r["head_orientation"] in ("U","D")}
            score=fitch(scorer,assigned)
            n_unique=len(assigned)
            for model in ("ER","ARD"):
                fit=fit_one(tree,state,model)
                ud,du,edges=exact_markov_rewards(tree,fit)
                k=1 if model=="ER" else 2
                aic=2*k-2*fit["log_likelihood"]
                aicc=aic+2*k*(k+1)/(n_unique-k-1)
                rootprior=root_prior_sensitivity(fit)
                if not all(math.isfinite(x) for x in (ud,du,aicc)):
                    raise ValueError("Mk exact conditional transition expectation nonfinite")
                row={
                    "nuclear_tree":name,"source_head_panel":case,"Mk_model":model,
                    "source_real_unique_Cirsium_BioSamples":len(original),
                    "observed_source_tips_U":n["U"],"observed_source_tips_D":n["D"],
                    "missing_source_tips":n["?"],
                    "observed_unique_head_taxon_concepts":n_unique,
                    "Fitch_minimum_changes_not_origin_count":score,
                    "Mk_log_likelihood":fit["log_likelihood"],"AIC":aic,
                    "AICc_taxon_concept_n_approx":aicc,
                    "q_U_to_D_per_substitution":fit["q_UD_per_substitution"],
                    "q_D_to_U_per_substitution":fit["q_DU_per_substitution"],
                    "expected_all_U_to_D_jumps_Mk_conditional":ud,
                    "expected_all_D_to_U_jumps_Mk_conditional":du,
                    "root_PU_given_fixed_prior0p5":float(fit["post"]["node_posterior"][0][0]),
                    "root_PU_given_fixed_q_prior0p1":rootprior["0.1"],
                    "root_PU_given_fixed_q_prior0p9":rootprior["0.9"],
                    "rate_on_optimizer_bound":fit["near_parameter_bounds"],
                    "same_sequenced_molecular_voucher_phenotyped":False,
                    "conditional_jumps_not_real_independent_origins":True,
                }
                results.append(row)
                if case=="primary_all_source_states":
                    for edge in edges:
                        edge_rows.append({
                            "nuclear_tree":name,"Mk_model":model,**edge
                        })
    comparisons=[]
    for name in trees:
        for case in PRIMARY_CASES:
            records={r["Mk_model"]:r for r in results if
                     r["nuclear_tree"]==name and r["source_head_panel"]==case}
            a,b=records["ER"],records["ARD"]
            comparisons.append({
                "nuclear_tree":name,"source_head_panel":case,
                "Fitch_minimum_steps":a["Fitch_minimum_changes_not_origin_count"],
                "delta_AICc_ARD_minus_ER":b["AICc_taxon_concept_n_approx"]-
                     a["AICc_taxon_concept_n_approx"],
                "ER_q_U_to_D_per_substitution":a["q_U_to_D_per_substitution"],
                "ARD_q_U_to_D_per_substitution":b["q_U_to_D_per_substitution"],
                "ARD_q_D_to_U_per_substitution":b["q_D_to_U_per_substitution"],
                "ER_expected_U_to_D_hidden_jumps":a["expected_all_U_to_D_jumps_Mk_conditional"],
                "ARD_expected_U_to_D_hidden_jumps":b["expected_all_U_to_D_jumps_Mk_conditional"],
                "ER_root_prior0p5_posteriorU":a["root_PU_given_fixed_prior0p5"],
            })
    outdir.mkdir(parents=True,exist_ok=True)
    def writecsv(path,rows):
        with path.open("w",newline="",encoding="utf-8") as h:
            writer=csv.DictWriter(h,fieldnames=list(rows[0]))
            writer.writeheader();writer.writerows(rows)
    writecsv(outdir/"world52_directional_U_D_ER_ARD_source_Mk_fits.csv",results)
    writecsv(outdir/"world52_original_gene_source_event_expectation_vs_endpoint_probability.csv",edge_rows)
    writecsv(outdir/"world52_treemodel_climate_unmeasured_transition_sensitivity.csv",comparisons)
    summary={
        "version":"real_world52_unique_BioSample_nuclear_U_D_176_75_73_original_study_block_20261025_v1",
        "world_nuclear_registry_294_BioSamples_350_locus_final_tree_available":False,
        "full_source_molecular_tips":52,
        "unique_public_Cirsium_BioSamples":51,
        "technical_duplicate_BioSample_SRR30887251_removed_before_new_tree":True,
        "source_S1_U_D_missing":{"U":19,"D":8,"unknown":24},
        "source_unique_phenotyped_taxon_concepts":len(known),
        "source_botanical_trait_observed_on_same_sequenced_voucher":False,
        "newly_inferred_original_nuclear_ML_Newick_sha256":{k:digest(v) for k,v in trees.items()},
        "original_nuclear_locus_sets":[176,75,73],
        "external12_75_coverage_blind":True,
        "technical_disagreement_73_loci_not_certified_single_copy":True,
        "fixed_Mk_root_prior_U":0.5,
        "branch_length_units":"substitutions/site, not absolute time",
        "taxon_concept_blocked_permutation_null":{
            "n_permutations":nperm,"seed":seed,
            "source_strata":"Moreyra original Japan38 paper cohort (NOT necessarily Japan-collected), North America, West Palearctic",
            "morphology_unknown_taxa_never_permuted_as_observed":True,
            "study_stratum_source_labels_fixed":{k:dict(Counter(known[t] for t in names))
                                                 for k,names in strata.items()},
            "results":null,
            "inference_boundary":"conditional fixed-count morphology label reassignments on phylograms, not causal evolutionary or spatial process null",
        },
        "Mk_model_results":comparisons,
        "source_model_rate_and_root_uncertainty":[
            "Markov reward expected jump totals integrate hidden back-and-forth cycles and can be extremely high when q*branch lengths saturate; these are NOT counted independent or observed historical U->D origins.",
            "Mk q estimates are per neutral sequence substitution/site and NOT transitions per million years.",
            "An uninformative ancestral root posterior near 0.5 is sensitive to its assumed 0.5 prior; report fixed-rate prior0.1 and prior0.9 posteriors.",
            "ARD vs ER delta AICc is approximate (n=27 taxon concepts); no decisive directional mechanism can be claimed on sparse trait sampling.",
            "Three trees use the same source sequences with different original gene coverage filters, not independent biological replicates.",
            "Moreyra original Japan38 panel includes foreign-collected and cultivated material; source paper label cannot substitute for physical provenance/native range.",
            "Missing U/D states are explicitly marginalized. No original S1 phenotype for 24 source tips is inferred from near relatives.",
            "Original worldwide phylogenomic tree (294 BioSample, final 350 targets) and globally matched native range CHELSA BIO15/BIO1 have not been completed.",
        ],
    }
    summary["taxon_concept_blocked_permutation_null"]["results"]=null
    (outdir/"world52_original_source_Mk_hidden_events_and_null_audit.json").write_text(
        json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    fig,ax=plt.subplots(figsize=(9.4,4.4))
    names=list(null)
    yy=np.arange(len(names))
    means=np.array([null[k]["regional_null_mean_steps"] for k in names])
    low=np.array([null[k]["regional_null_95pct_steps"][0] for k in names])
    high=np.array([null[k]["regional_null_95pct_steps"][1] for k in names])
    obs=np.array([null[k]["observed_minimum_Fitch_steps"] for k in names])
    ax.errorbar(means,yy,xerr=np.vstack([means-low,high-means]),fmt="o",capsize=4,label="Source-block null (mean, 95% interval)")
    ax.scatter(obs,yy,marker="D",s=55,label="Observed minimum changes")
    ax.set_yticks(yy,names)
    ax.set_xlabel("Fitch minimum category changes, NOT observed historical events")
    ax.set_title("Corrected 51 unique BioSample Cirsium heads: paper-blocked U/D label test")
    ax.invert_yaxis();ax.legend(frameon=False);ax.grid(axis="x",alpha=.15)
    fig.tight_layout()
    fig.savefig(outdir/"world52_real_176_75_73_UD_study_block_null.png",dpi=180,bbox_inches="tight")
    plt.close(fig)
    print(json.dumps({
        "molecular_tips":52,"unique_Cirsium":51,"source_U_D_unscored":[19,8,24],
        "expected_jumps_by_tree_model":[{
            "tree":x["nuclear_tree"],"case":x["source_head_panel"],
            "Fitch":x["Fitch_minimum_steps"],"ARD_minus_ER":x["delta_AICc_ARD_minus_ER"],
            "ER_hidden_UD":round(x["ER_expected_U_to_D_hidden_jumps"],1),
            "ARD_hidden_UD":round(x["ARD_expected_U_to_D_hidden_jumps"],1)
        } for x in comparisons if x["source_head_panel"]=="primary_all_source_states"],
        "null_raw":null,
    },indent=2),flush=True)
    return summary


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--full176",required=True,type=Path)
    p.add_argument("--balanced75",required=True,type=Path)
    p.add_argument("--technical73",required=True,type=Path)
    p.add_argument("--traits",required=True,type=Path)
    p.add_argument("--outdir",required=True,type=Path)
    p.add_argument("--permutations",type=int,default=DEFAULT_PERMUTATIONS)
    p.add_argument("--seed",type=int,default=DEFAULT_SEED)
    a=p.parse_args()
    if not 999<=a.permutations<=50000:
        raise ValueError("source label permutation must use at least 999 and no more than 50000 iterations")
    execute(
        trees={"full176":a.full176,"high_occupancy75":a.balanced75,"pipeline_qc73":a.technical73},
        traits=a.traits,outdir=a.outdir,nperm=a.permutations,seed=a.seed
    )


if __name__=="__main__":
    main()
