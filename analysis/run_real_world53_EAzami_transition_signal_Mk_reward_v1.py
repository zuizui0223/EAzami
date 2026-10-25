#!/usr/bin/env python3
"""EAzami REAL worldwide-pilot U/D phylogenetic transition diagnostics.

Inputs are genuine 53-tip Moreyra-based Compositae1061 ML trees (176 loci,
74 whole high-occupancy loci, and independent FastTree fit), and the ORIGINAL
per-tip Moreyra S1 accession/voucher + independently published floral ontology.

Two separate questions:
(1) Are observed species/variety-level U/D states phylogenetically clustered
    beyond geography? Permute 20,000 taxon-concept BLOCKS, keeping source region,
    resolved/missing specimen positions and region-specific U/D counts fixed.
(2) Do fitted reversible ER and ARD Mk models actually identify a COUNT of
    directional U->D events? Calculate exact branch-conditional expectations
    via Van Loan 4x4 Markov reward integrals, including hidden reversals.
    Event expectations are CONDITIONAL on inferred q and branch lengths, NOT
    dated historical transitions or the number of independent adaptive origins.

Important anti-pseudoreplication: "Cirsium nipponicum var. yoshinoi" and
"var. incomptum" remain UNRESOLVED even if a different C. nipponicum
molecular sample has species-level U. The two separate C. kamtschaticum
source biological samples share ONE taxon-concept label when permuted.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from Bio import Phylo
from scipy.linalg import expm

from fit_real_world45_multitopology_U_D_mk_v1 import build_layout, fit_one

PINS = {
    "full176": "5828ccd9f4f0b083f804f87bfa7407a20ad5eb52647e92eb5a26e812bd6807a7",
    "balanced74": "57483eb8f1232631a8160e7dfe8e9427a1a85f20a8957e5d23ea65bca08e5e64",
    "FastTree176": "75f0b2087228c190d2d9ca928928eaf603cfe49cdd2a791ab1a72bcf82976cc5",
    "trait_source": "457059076a15d91be941d661a19b2590e25192a89399f22ed6f2299eeff5198a",
}
DEFAULT_SEED = 2317
DEFAULT_PERMUTATIONS = 20000
EXTERNAL_DUPLICATE = "GLB2_SRR30887251_Cirsium_kamtschaticum"
OUTGROUP = "OUTGROUP_saff"
NA_D = "GLB_SRR30887231_Cirsium_vinaceum"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def concept(source: str) -> str:
    """Taxon-concept label, preserving infraspecific status, not just binomial."""
    m = re.match(r"^(Cirsium [a-z][a-z-]+)(?:\s+var\.\s+([a-z][a-z-]+))?", source)
    if not m:
        raise ValueError("invalid source taxon concept: " + source)
    return m.group(1) + (f" var. {m.group(2)}" if m.group(2) else "")


def source_panel(path: Path):
    if sha(path) != PINS["trait_source"]:
        raise ValueError("S1-and-botanical source trait CSV was modified without a source audit")
    with path.open(encoding="utf-8-sig", newline="") as h:
        rows = list(csv.DictReader(h))
    if len(rows) != 53 or len({r["tip_id"] for r in rows}) != 53:
        raise ValueError("53 original molecular specimen IDs required")
    original = {r["tip_id"]: r for r in rows}
    if original[OUTGROUP]["head_orientation"] not in {"?", ""}:
        raise ValueError("Carthamus outgroup was wrongly given a Cirsium head state")
    del original[OUTGROUP]
    if Counter(x["head_orientation"] for x in original.values()) != Counter({"U":19, "D":9, "?":24}):
        raise ValueError("original S1 botanical U/D evidence changed")
    grouped = defaultdict(list)
    for row in original.values():
        if row["head_orientation"] in ("U", "D"):
            grouped[concept(row["source_taxon"])].append(row)
    if len(grouped) != 27:
        raise ValueError("27 source flower-taxon concepts expected (28 labelled nuclear tips)")
    for name, samples in grouped.items():
        if len({r["head_orientation"] for r in samples}) != 1:
            raise ValueError("same botanical concept has conflicting U/D original evidence: " + name)
    assigned = {name: samples[0]["head_orientation"] for name, samples in grouped.items()}
    reconstructed = Counter(assigned.get(concept(x["source_taxon"]), "?") for x in original.values())
    if reconstructed != Counter(x["head_orientation"] for x in original.values()):
        raise ValueError("illegal morphology propagation to unsampled species or named varieties")
    # The original Japan sample takes priority when a taxon has two geographic
    # molecular records; the state is still attached to BOTH specimens as one
    # taxon-concept block.
    bins = defaultdict(list)
    for name, samples in grouped.items():
        reg = next((x["region"] for x in samples if x["region"]=="Japan38_2025_moreyra"),
                   samples[0]["region"])
        bins[reg].append(name)
    if len(bins) != 3:
        raise ValueError("expected source-informed Japan/NorthAmerica/WestPalearctic state bins")
    if original[EXTERNAL_DUPLICATE]["head_orientation"]!="D":
        raise ValueError("C. kamtschaticum original replicates lost")
    for label in ("Cirsium nipponicum var. incomptum","Cirsium nipponicum var. yoshinoi"):
        matches = [r for r in original.values() if concept(r["source_taxon"])==label]
        if not matches or any(r["head_orientation"]!="?" for r in matches):
            raise ValueError("named C. nipponicum varieties must not inherit U from C. nipponicum")
    return original, grouped, assigned, bins


def ingest_tree(path: Path, tree_name: str, original: dict):
    if sha(path) != PINS[tree_name]:
        raise ValueError("real source ML phylogeny differs from frozen empirical Newick")
    tree = Phylo.read(path, "newick")
    if {n.name for n in tree.get_terminals()} != set(original)|{OUTGROUP}:
        raise ValueError("molecular 53 tip set differs from frozen original specimen ontology")
    tree.root_with_outgroup({"name":OUTGROUP})
    tree.prune(OUTGROUP)
    if len(tree.root.clades)==1:
        tree.root = tree.root.clades[0]
        tree.root.branch_length = None
    return tree


def compiled_fitch(tree, original):
    """Fast deterministic Fitch step scorer for 20k taxon-block permutations."""
    nodes, kids, _, _, post = build_layout(tree)
    terminal = {}
    for idx, nd in enumerate(nodes):
        if nd.is_terminal():
            terminal[idx] = concept(original[nd.name]["source_taxon"])
    if len(terminal) != len(tree.get_terminals()) or len(terminal) > len(original):
        raise ValueError("source terminal tip count changed")
    k = len(nodes)
    return {"post":post, "terminal":terminal,
            "children":[[ch for ch,_ in row] for row in kids],"k":k}


def fitch(compiled, assignment):
    # 1 = U, 2 = D, 3 = unknown or polymorphic (never impute unknown)
    state = [3]*compiled["k"]
    steps = [0]*compiled["k"]
    children = compiled["children"]
    for n in compiled["post"]:
        if not children[n]:
            s=assignment.get(compiled["terminal"][n], "?")
            state[n] = 1 if s=="U" else 2 if s=="D" else 3
            continue
        first = True
        changes = 0
        for child in children[n]:
            changes += steps[child]
            if first:
                curr = state[child]
                first = False
            else:
                intersect = curr & state[child]
                if intersect:
                    curr = intersect
                else:
                    curr |= state[child]
                    changes += 1
        state[n] = curr
        steps[n] = changes
    return steps[0]


def exact_markov_rewards(tree, fit):
    """Posterior mean U->D and D->U events via Q Markov bridge integrals.

    Edge endpoint posterior = P(S_parent=i,S_child=j | all tips,q).
    Per edge E[N_direction | tip data] = sum_ij J_ij [F_ij/P_ij].
    F is upper-right 2x2 of expm([[Q,R],[0,Q]]*t), Van Loan block.
    This integrates *hidden multiple switches* instead of equating endpoint
    discordance to a real single transition.
    """
    qUD,qDU=fit["q_UD_per_substitution"],fit["q_DU_per_substitution"]
    Q=np.array([[-qUD,qUD],[qDU,-qDU]],dtype=float)
    RUD=np.array([[0.,qUD],[0.,0.]])
    RDU=np.array([[0.,0.],[qDU,0.]])
    def numerator(R,time):
        block=np.zeros((4,4))
        block[:2,:2]=Q
        block[2:,2:]=Q
        block[:2,2:]=R
        return expm(block*time)[:2,2:]
    nodes, kids, _, _, _=build_layout(tree)
    endpoint = fit["post"]["edge_joint"]
    rows=[]
    totalUD=totalDU=0.
    for parent, children in enumerate(kids):
        for child,time in children:
            J=endpoint[child]
            P=expm(Q*time)
            if not np.allclose(P.sum(axis=1),1.,atol=1e-7):
                raise AssertionError("transition probability was not stochastic")
            EUD=float(np.sum(J*(numerator(RUD,time)/np.maximum(P,1e-300))))
            EDU=float(np.sum(J*(numerator(RDU,time)/np.maximum(P,1e-300))))
            if EUD < -1e-7 or EDU < -1e-7:
                raise AssertionError("negative conditional transition count")
            totalUD+=max(0.,EUD)
            totalDU+=max(0.,EDU)
            descendants=sorted(t.name for t in nodes[child].get_terminals())
            tip_label = nodes[child].name if nodes[child].is_terminal() else ""
            rows.append({
                "edge_descendant_key":str(len(descendants))+":"+
                    hashlib.sha256("|".join(descendants).encode()).hexdigest()[:12],
                "child_terminal_tip":tip_label,
                "edge_branch_length_substitutions_per_site":time,
                "P_parent_U_child_D_endpoints":float(J[0,1]),
                "expected_hidden_and_visible_U_to_D_given_fitted_model":EUD,
                "expected_hidden_and_visible_D_to_U_given_fitted_model":EDU,
                "exact_origin_count_identified":False,
            })
    return totalUD,totalDU,rows


def root_prior_sensitivity(fit,priors=(.1,.5,.9)):
    original=float(fit["post"]["node_posterior"][0][0])
    # Original Mk used P(root U)=0.5. Recover the conditional root U:D
    # likelihood ratio; vary ONLY the prior while holding fitted rates fixed.
    odds=original/max(1-original,1e-300)
    return {str(q):float((q*odds)/(q*odds+1-q)) for q in priors}


def permute_observed(trees, original, groups, assign, strata, n=DEFAULT_PERMUTATIONS,seed=DEFAULT_SEED):
    rng=np.random.default_rng(seed)
    c={name:compiled_fitch(tree,original) for name,tree in trees.items()}
    observed={name:fitch(f,assign) for name,f in c.items()}
    tally={name:{"regional":Counter(),"pooled":Counter()} for name in c}
    known=sorted(assign)
    pooled=[assign[x] for x in known]
    bins = {stratum:(sorted(names),[assign[x] for x in sorted(names)])
            for stratum,names in sorted(strata.items())}
    for _ in range(n):
        regional={}
        for names,obs in bins.values():
            regional.update(zip(names,rng.permutation(obs)))
        pool=dict(zip(known,rng.permutation(pooled)))
        for name,func in c.items():
            tally[name]["regional"][fitch(func,regional)]+=1
            tally[name]["pooled"][fitch(func,pool)]+=1
    summary={}
    for name in c:
        o=observed[name]
        out={"observed_minimum_Fitch_steps":o,"permutations":n}
        for mode in ("regional","pooled"):
            hist=tally[name][mode]
            v=np.repeat(np.asarray(list(hist)),list(hist.values()))
            out[mode+"_null_mean_steps"]=float(v.mean())
            out[mode+"_null_95pct_steps"]=[float(x) for x in np.quantile(v,[.025,.975])]
            out[mode+"_p_one_sided_clustered"]=float((1+sum(cnt for st,cnt in hist.items() if st<=o))/(n+1))
            out[mode+"_p_one_sided_overdispersed"]=float((1+sum(cnt for st,cnt in hist.items() if st>=o))/(n+1))
            out[mode+"_fitch_step_frequencies"]={str(k):int(v) for k,v in sorted(hist.items())}
        summary[name]=out
    return summary


def execute(trees: dict[str,Path],traits:Path,outdir:Path,nperm:int,seed:int):
    original,groups,known,strata=source_panel(traits)
    parsed={name:ingest_tree(p,name,original) for name,p in trees.items()}
    perm=permute_observed(parsed,original,groups,known,strata,nperm,seed)
    outcome=[]
    edge_stats=[]
    for name,tree in parsed.items():
        for panel in ("primary","omit_duplicate_kamtschaticum","mark_NA_vinaceum_unresolved"):
            import copy
            t=copy.deepcopy(tree)
            source={tip:dict(r) for tip,r in original.items()}
            if panel=="omit_duplicate_kamtschaticum":
                t.prune(EXTERNAL_DUPLICATE)
                del source[EXTERNAL_DUPLICATE]
            elif panel=="mark_NA_vinaceum_unresolved":
                source[NA_D]["head_orientation"]="?"
            states=Counter(x["head_orientation"] for x in source.values())
            observed_concepts={concept(x["source_taxon"]) for x in source.values()
                               if x["head_orientation"] in {"U","D"}}
            for Mk_model in ("ER","ARD"):
                fit=fit_one(t,source,Mk_model)
                expectedUD,expectedDU,edges=exact_markov_rewards(t,fit)
                params=1 if Mk_model=="ER" else 2
                nobs=len(observed_concepts)
                AIC=2*params-2*fit["log_likelihood"]
                AICc=AIC+2*params*(params+1)/(nobs-params-1)
                row={
                    "tree":name,"source_panel":panel,"Mk_model":Mk_model,
                    "ingroup_molecular_tips":len(source),
                    "U_tips":states["U"],"D_tips":states["D"],"unknown_tips":states["?"],
                    "n_resolved_taxon_concepts":nobs,
                    "observed_Fitch_minimum_steps":fitch(compiled_fitch(t,original),
                        {concept(x["source_taxon"]):x["head_orientation"] for x in source.values()
                         if x["head_orientation"] in ("U","D")}),
                    "log_likelihood":fit["log_likelihood"],"AIC":AIC,"approx_AICc":AICc,
                    "q_UD_per_substitution":fit["q_UD_per_substitution"],
                    "q_DU_per_substitution":fit["q_DU_per_substitution"],
                    "expected_Mk_U_to_D_events_conditional_not_origin_count":expectedUD,
                    "expected_Mk_D_to_U_events_conditional_not_origin_count":expectedDU,
                    "root_U_posterior_prior_U_0p5":float(fit["post"]["node_posterior"][0][0]),
                    "root_U_posterior_fixed_q_prior_U_0p1":root_prior_sensitivity(fit)["0.1"],
                    "root_U_posterior_fixed_q_prior_U_0p9":root_prior_sensitivity(fit)["0.9"],
                    "model_q_at_bound":fit["near_parameter_bounds"],
                    "same_sequenced_voucher_head_verified":False,
                    "count_is_independent_adaptive_U_to_D_origin":False,
                }
                outcome.append(row)
                if panel=="primary":
                    for record in edges:
                        edge_stats.append({"tree":name,"Mk_model":Mk_model,**record})
    outdir.mkdir(parents=True,exist_ok=True)
    with (outdir/"real_world53_U_D_Mk_transition_rate_and_event_sensitivity.csv").open("w",newline="",encoding="utf-8") as h:
        writer=csv.DictWriter(h,fieldnames=list(outcome[0]))
        writer.writeheader();writer.writerows(outcome)
    with (outdir/"real_world53_Mk_edge_endpoint_vs_true_reward_expected_events.csv").open("w",newline="",encoding="utf-8") as h:
        writer=csv.DictWriter(h,fieldnames=list(edge_stats[0]))
        writer.writeheader();writer.writerows(edge_stats)
    receipt={
        "contract":"EAzami_empirical_world53_176_vs_74_vs_FastTree_taxon_block_transition_v1",
        "molecular_source_S1_scope":{
            "original_phylogenetic_sample_tips":53,"Cirsium_ingroup_tips":52,
            "U":19,"D":9,"unknown":24,"resolved_unique_taxon_concepts":len(known),
            "independent_botanical_species_or_variety_states_not_same_sequenced_voucher":True,
            "trait_source_SHA256":PINS["trait_source"],
            "source_molecular_newick_SHA256":{name:sha(path) for name,path in trees.items()},
            "full_world_294_BioSample_and_350_gene_Moreyra_tree_completed":False
        },
        "taxon_block_original_state_n":Counter(known.values()),
        "morphology_blind_null":{
            "n_permutations":nperm,"seed":seed,
            "same_species_and_named_variety_frozen_across_repeated_molecular_tips":True,
            "unscored_original_taxon_concepts_remain_missing":True,
            "geographic_strata_original_source_names":{area:{
                "U":sum(known[x]=="U" for x in clades),"D":sum(known[x]=="D" for x in clades)}
                for area,clades in strata.items()
            },
            "p_values":perm
        },
        "Mk":outcome,
        "robustness_limitations":[
            "Stochastic CTMC Markov reward integrates arbitrarily many hidden U<->D reversals conditional on the fitted rates; large expected counts are a diagnostic of saturation/nonidentification, NOT number of independent adaptive origins.",
            "Short molecular phylogram lengths (substitutions per site), nonrepresentative sampled species and source phenotype uncertainty mean fitted rate q is not a calibrated evolutionary rate per year.",
            "Ancestral posterior near .5 under fixed equal root prior is primarily uninformative; holding fitted rates fixed while changing root priors shows data's limited leverage.",
            "Fitch phylogenetic label null conditions only on observed source species/variety codes and region; it does not reproduce true morphological evolutionary processes or correct uneven taxonomic sampling.",
            "Only 27 accepted source taxon concepts have original binary head descriptions among 52 Cirsium molecular individuals; full genome-scale worldwide tree is not built.",
            "The three trees share the same original real nucleotide records and are not independent biological replications.",
            "No historical CHELSA BIO1/BIO15 assigned to molecular branch ancestors; no pollinator causality or species-level fitness effect can be estimated."
        ]
    }
    (outdir/"EAzami_real_world53_transition_diagnostics_result.json").write_text(
        json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"
    )
    # One useful chart rather than placing different hypothesis tests on
    # superficially comparable numeric axes.
    names=list(perm)
    fig,ax=plt.subplots(figsize=(9.4,4.4))
    y=np.arange(len(names))
    lo=np.array([perm[x]["regional_null_95pct_steps"][0] for x in names])
    hi=np.array([perm[x]["regional_null_95pct_steps"][1] for x in names])
    mean=np.array([perm[x]["regional_null_mean_steps"] for x in names])
    observed=np.array([perm[x]["observed_minimum_Fitch_steps"] for x in names])
    ax.errorbar(mean,y,xerr=np.vstack([mean-lo,hi-mean]),fmt="o",
                capsize=4,label="Null mean and 95% permutation interval")
    ax.scatter(observed,y,marker="D",s=52,label="Actual observed state changes")
    ax.set_yticks(y,names)
    ax.invert_yaxis()
    ax.set_xlim(4,10)
    ax.set_xlabel("Minimum Fitch changes (not actual historical events)")
    ax.set_title("Cirsium: U/D clustering conditional on region and taxon concepts")
    ax.legend(frameon=False,fontsize=8,loc="lower left")
    ax.grid(axis="x",alpha=.17)
    fig.tight_layout()
    fig.savefig(outdir/"real_world53_source_head_UD_phylogenetic_signal.png",dpi=170)
    plt.close(fig)
    print(json.dumps({
        "n_molecular_Cirsium":len(original),"n_observed_source_concepts":len(known),
        "source_region_fixed_counts":receipt["morphology_blind_null"]["geographic_strata_original_source_names"],
        "permutation_actual_vs_null":{k:{
            "Fitch":v["observed_minimum_Fitch_steps"],
            "mean":v["regional_null_mean_steps"],
            "cluster_p":v["regional_p_one_sided_clustered"],
            "overdispersion_p":v["regional_p_one_sided_overdispersed"]}
            for k,v in perm.items()},
        "primary_models":[{"tree":r["tree"],"model":r["Mk_model"],
            "AICc":r["approx_AICc"],"conditional_U_to_D":r[
                "expected_Mk_U_to_D_events_conditional_not_origin_count"]}
            for r in outcome if r["source_panel"]=="primary"]
    },indent=2))
    return receipt


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--tree-full",type=Path,required=True)
    p.add_argument("--tree-74",type=Path,required=True)
    p.add_argument("--tree-fast",type=Path,required=True)
    p.add_argument("--traits",type=Path,required=True)
    p.add_argument("--permutations",type=int,default=DEFAULT_PERMUTATIONS)
    p.add_argument("--seed",type=int,default=DEFAULT_SEED)
    p.add_argument("--outdir",type=Path,required=True)
    args=p.parse_args()
    if not (999<=args.permutations<=50000):
        raise ValueError("at least 999 permutations required")
    execute({"full176":args.tree_full,"balanced74":args.tree_74,"FastTree176":args.tree_fast},
            args.traits,args.outdir,args.permutations,args.seed)


if __name__=="__main__":
    main()
