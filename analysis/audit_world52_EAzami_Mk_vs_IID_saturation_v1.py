#!/usr/bin/env python3
"""EAzami REAL corrected-world52 saturated-Mk vs independent-tip-frequency diagnostic.

Actual molecular sources: 51 unique Moreyra et al. 2025 S1 Cirsium BioSamples
and one Carthamus outgroup, newly inferred 176/75/73 Compositae1061-locus
nuclear trees. Phenotypes: 19 U, 8 D, 24 unknown at nuclear-tip level, matching
27 distinct original botanical taxon concepts, never voucher-level photographs.

The IID reference is the LIMIT of a fully mixed ARD CTMC (for positive
stationary qUD/(qUD+qDU)); it estimates ONE shared D prevalence parameter.
Evaluate identical observed 27 named concept labels under IID and the actual
previously fitted Mk models, and quantify tree-branch memory e^(-(qUD+qDU)t).
This is MODEL ADEQUACY / saturation diagnosis. Source taxon concepts are
phylogenetically related and initially U/D-ascertained: IID AICc is descriptive,
NOT formal proof of evolutionary independence or adaptive irrelevance.
"""
from __future__ import annotations

import argparse,csv,hashlib,json,math,re
from collections import Counter,defaultdict
from pathlib import Path

from Bio import Phylo

SOURCE_TRAIT_SHA="1a4629347007b73b900db5b7c36fba345933281b9868d1c9555f4a1906100962"
TREE_SHA={
 "full176":"ef4a93f8b39dfda19180903f5e39b57a8a34eda293060a57ab30fea46b377fb3",
 "high_occupancy75":"58296516b78f3b4200e015fa7503ef11035af7cd58940fe26e6be39c518b894b",
 "pipeline_qc73":"3830972a1b747684a69e90fa7bc1b1a22102e703b5",
}
OUTGROUP="OUTGROUP_saff"
PRIOR="0.5"
MODELS=("irreversible_UD","irreversible_DU","ER_reversible","ARD_reversible")
CASES=("all_source_states","omit_NA_selected_D","omit_West_cultivated_D")
ROOTPRIORS=("0.1","0.5","0.9")


def sha(p:Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read_table(path:Path):
    with path.open(encoding="utf-8-sig",newline="") as h:
        return list(csv.DictReader(h))


def concept(name:str)->str:
    m=re.match(r"^(Cirsium [a-z][a-z-]+)(?:\s+var\.\s+([a-z][a-z-]+))?",name)
    if not m:
        raise ValueError("invalid original botanical taxon: "+name)
    return m.group(1)+(f" var. {m.group(2)}" if m.group(2) else "")


def source_traits(path:Path):
    if sha(path)!=SOURCE_TRAIT_SHA:
        raise ValueError("original corrected S1 molecular sample and botanical trait CSV SHA drift")
    rows=read_table(path)
    if len(rows)!=52 or len({r["tip_id"] for r in rows})!=52:
        raise ValueError("source 52 distinct molecular specimen tip labels required")
    if OUTGROUP not in {r["tip_id"] for r in rows}:
        raise ValueError("real source Carthamus outgroup missing")
    r=[x for x in rows if x["tip_id"]!=OUTGROUP]
    if len(r)!=51 or len({x["source_biosample"] for x in r})!=51:
        raise ValueError("not unique original Moreyra Cirsium BioSamples")
    if any("GLB2_SRR30887251_Cirsium_kamtschaticum"==x["tip_id"] for x in r):
        raise ValueError("retracted same-SRR copied Kamchatka tip reintroduced")
    if Counter(x["head_orientation"] for x in r)!=Counter({"U":19,"D":8,"?":24}):
        raise ValueError("original source states drift")
    by=defaultdict(list)
    for x in r:
        if x["head_orientation"] in {"U","D"}:
            if not x["head_source_url"]:
                raise ValueError("resolved botanical taxon without source URL")
            by[concept(x["source_taxon"])].append(x)
    if len(by)!=27 or any(len({y["head_orientation"] for y in vals})!=1 for vals in by.values()):
        raise ValueError("not exactly 27 unique consistent source botanical concepts")
    groups={k:vals[0]["head_orientation"] for k,vals in by.items()}
    regions=Counter(x["region"] for val in by.values() for x in val[:1])
    if regions!=Counter({"Japan38_2025_moreyra":19,"North_America":6,"West_Palearctic":2}):
        raise ValueError("original genetic study strata changed")
    for var in ("Cirsium nipponicum var. incomptum","Cirsium nipponicum var. yoshinoi"):
        if any(x["head_orientation"]!="?" for x in r if concept(x["source_taxon"])==var):
            raise ValueError("unscored variety illegally inherited species phenotype")
    return r,groups,by


def iid_fit(u:int,d:int):
    if min(u,d)<=0:raise ValueError("both original U and D source states required")
    n=u+d
    pD=d/n
    ll=u*math.log1p(-pD)+d*math.log(pD)
    aic=2-2*ll
    aicc=aic+4/(n-2)
    return {"U":u,"D":d,"n_named_taxon_concepts":n,"p_D_empirical":pD,
            "IID_loglik":ll,"IID_AICc_k1":aicc}


def phylo_memory(path:Path,qUD:float,qDU:float,required:set[str],want_sha:str):
    if sha(path)!=want_sha:
        raise ValueError("not original source nuclear phylogram "+str(path))
    tree=Phylo.read(path,"newick")
    if {x.name for x in tree.get_terminals()}!=required|{OUTGROUP}:
        raise ValueError("corrected original 51 BioSample tip universe or outgroup changed")
    tree.root_with_outgroup({"name":OUTGROUP})
    tree.prune(OUTGROUP)
    if len(tree.get_terminals())!=51:raise ValueError("source ingroup length changed")
    if qUD<=0 or qDU<=0:raise ValueError("ARD must have two positive fitted rates")
    qsum=qUD+qDU
    branches=[float(c.branch_length or 0.) for c in tree.find_clades() if c is not tree.root]
    if len(branches)!=100 or any(x<0 or not math.isfinite(x) for x in branches):
        raise ValueError("tree does not have 100 valid rooted 51-ingrouptip binary branches")
    memories=sorted(math.exp(-qsum*x) for x in branches)
    return {"source_ingroup_branches":len(branches),
        "qUD_per_substitution":qUD,"qDU_per_substitution":qDU,
        "q_total":qsum,"stationary_p_D":qUD/qsum,
        "Markov_memory_half_life_in_DNA_substitutions_per_site":math.log(2)/qsum,
        "proportion_edges_memory_below_0p1":sum(x<.1 for x in memories)/len(memories),
        "proportion_edges_memory_below_0p01":sum(x<.01 for x in memories)/len(memories),
        "median_original_phylogenetic_edge_memory":(memories[49]+memories[50])/2,
        "median_length_original_ingroup_edge":sorted(branches)[50],
        "meaning":"memory is exp(-(qUD+qDU)*branch_length), not an observed reversal/event count or estimate of calendar years"}


def run(traits:Path,fits_file:Path,trees:dict[str,Path],outdir:Path):
    rows,by_concept,blocks=source_traits(traits)
    fitted=read_table(fits_file)
    if len(fitted)!=60:raise ValueError("original 3 trees x 4 rate models x source holds/root stress should give 60 fits")
    keyed={(x["tree"],x["trait_case"],x["root_prior_U_fixed"],x["model"]):x for x in fitted}
    if len(keyed)!=60 or set(x["tree"] for x in fitted)!=set(trees):
        raise ValueError("duplicated rate fits or missing original tree panels")
    original_count=Counter(by_concept.values())
    if original_count!=Counter({"U":19,"D":8}):raise ValueError("source concept probabilities incorrectly counted")
    out=[]
    all_pop=source_traits(traits)[1]
    samples={x["tip_id"]:x for x in rows}
    keys_by_case={
        "all_source_states":None,
        "omit_NA_selected_D":"GLB_SRR30887231_Cirsium_vinaceum",
        "omit_West_cultivated_D":"GLB_SRR30887186_Cirsium_erisithales",
    }
    for tree_key,path in trees.items():
        for case,held_tip in keys_by_case.items():
            assigned=dict(all_pop)
            if held_tip:
                if samples[held_tip]["head_orientation"]!="D":
                    raise ValueError("source holdout D state lost")
                assigned.pop(concept(samples[held_tip]["source_taxon"]))
            tally=Counter(assigned.values())
            base=iid_fit(tally["U"],tally["D"])
            for prior in ROOTPRIORS if case=="all_source_states" else (PRIOR,):
                models={m:keyed[(tree_key,case,prior,m)] for m in MODELS}
                for name,fit in models.items():
                    if (int(fit["n_observed_U"]),int(fit["n_observed_D"]),int(fit["n_unknown"]),
                        int(fit["n_taxon_concepts"])) != (tally["U"],tally["D"],
                            24 if not held_tip else 25,tally["U"]+tally["D"]):
                        raise ValueError("original rate and fitted model sample counts inconsistent")
                ard=models["ARD_reversible"]
                qU,qD=float(ard["q_UD_per_substitution"]),float(ard["q_DU_per_substitution"])
                if min(qU,qD)<=0:raise ValueError("source ARD fit is not fully reversible")
                row={
                    "original_real_phylogeny":tree_key,
                    "source_trait_case":case,
                    "root_prior_U_for_phylogenetic_Mk":float(prior),
                    **base,
                    "ARD_Mk_loglik":float(ard["log_likelihood"]),
                    "ARD_AICc_k2":float(ard["AICc"]),
                    "ER_AICc_k1":float(models["ER_reversible"]["AICc"]),
                    "UDonly_AICc_k1":float(models["irreversible_UD"]["AICc"]),
                    "DUonly_AICc_k1":float(models["irreversible_DU"]["AICc"]),
                    "delta_ARDminusIID_AICc":float(ard["AICc"])-base["IID_AICc_k1"],
                    "ARD_over_IID_loglik_gain":float(ard["log_likelihood"])-base["IID_loglik"],
                    "ARD_stationary_pD":qU/(qU+qD),
                    "ARD_pD_minus_observed_iid":qU/(qU+qD)-base["p_D_empirical"],
                    "ARD_qsum_per_DNA_substitution":qU+qD,
                }
                if case=="all_source_states" and prior==PRIOR:
                    row.update(phylo_memory(path,qU,qD,set(samples),TREE_SHA[tree_key]))
                out.append(row)
    main=[x for x in out if x["source_trait_case"]=="all_source_states" and x["root_prior_U_for_phylogenetic_Mk"]==.5]
    if len(main)!=3 or any(x["delta_ARDminusIID_AICc"]<=0 for x in main):
        raise ValueError("AAD/IID comparison failed or original data unexpectedly show stronger tree signal")
    if any(abs(x["ARD_pD_minus_observed_iid"])>.025 for x in main):
        raise ValueError("fitted ARD model does not converge towards the actually observed D frequency")
    outdir.mkdir(parents=True,exist_ok=True)
    with (outdir/"corrected_world52_IID_vs_ER_ARD_irreversible_by_molecular_tree.csv").open(
            "w",encoding="utf-8",newline="") as h:
        columns=list(dict.fromkeys(k for x in out for k in x.keys()))
        w=csv.DictWriter(h,fieldnames=columns)
        w.writeheader();w.writerows(out)
    result={
        "version":"EAzami_world52_true_uniqueBioSamples_reversible_ARD_vs_IID_stationary_adequacy_v1",
        "molecular_source":"Moreyra 2025 original 51 distinct S1 Cirsium BioSamples, plus Carthamus outgroup; three actual reference-projected 176/75/73-locus trees",
        "original_molecular_source_trait_csv_sha256":SOURCE_TRAIT_SHA,
        "original_nuclear_tree_SHA256":TREE_SHA,
        "n_nuclear_ingroup_unique_BioSamples":51,
        "n_source_taxon_concepts_observed":27,
        "source_head_states":{"U":19,"D":8,"unknown":24},
        "IID_stationary_one_parameter_baseline":iid_fit(19,8),
        "source_AICc_model_comparison_and_branch_saturation":main,
        "sensitivity_all_root_priors_and_D_holdouts":out,
        "scientific_interpretation":[
           "The one-parameter source prevalence-only IID model has LOWER DESCRIPTIVE AICc than the two-rate reversible ARD Mk on all three gene panels.",
           "The fitted reversible ARD stationary D probability approximately equals 8/27 original botanically scored source taxon concepts.",
           "Most original molecular branches retain little original U/D state memory under huge per-substitution Mk q, indicating weak internal state signal and long-hidden-jump saturation.",
           "This does not mean true evolution is IID or U/D is independent of phylogeny: source phenotypes are related and non-randomly sampled.",
           "27 source botanical head concept labels have unknown voucher-level phenotype assignment and 24 unscored molecular tips, so all formal macroevolutionary directional claims remain open.",
           "These three gene-panel trees reuse one molecular source panel, not independent 294 BioSample 350 locus genome-scale data.",
           "Likelihood/AICc of an IID source-tip model are descriptive and cannot be treated as a phylogenetically calibrated selection-adaptation test.",
           "U/D flower-head functional selection, pollinators, historic precipitation BIO15/annual temperature BIO1 remain unmeasured in this analysis."
        ],
        "no_observed_U_to_D_or_D_to_U_event_count_inferred":True,
        "no_phylogenetic_IID_evolution_proven":True,
        "one_BioSample_per_source_molecular_tip_verified":True,
    }
    (outdir/"real_world52_Mk_phylogenetic_signal_saturation_vs_IID_result.json").write_text(
        json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"n_source_taxon_concepts":27,"IID_AICc":iid_fit(19,8)["IID_AICc_k1"],
        "per_tree":[{k:x[k] for k in ("original_real_phylogeny","ARD_AICc_k2",
                   "ARD_over_IID_loglik_gain","delta_ARDminusIID_AICc",
                   "ARD_stationary_pD","proportion_edges_memory_below_0p1")}
                   for x in main],"statistical_claim":"descriptive model adequacy, not adaptive selection"},indent=2))


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--traits",required=True,type=Path)
    p.add_argument("--fitted-Mk",required=True,type=Path)
    p.add_argument("--tree-full176",required=True,type=Path)
    p.add_argument("--tree-covered75",required=True,type=Path)
    p.add_argument("--tree-technical73",required=True,type=Path)
    p.add_argument("--outdir",required=True,type=Path)
    a=p.parse_args()
    run(a.traits,getattr(a,"fitted_Mk"),{
        "full176":a.tree_full176,
        "high_occupancy75":a.tree_covered75,
        "pipeline_qc73":a.tree_technical73,
    },a.outdir)

if __name__=="__main__":
    main()
