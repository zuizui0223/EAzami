#!/usr/bin/env python3
"""Analyze actual corrected 52-tip Cirsium nuclear ML trees (51 unique ingroup BioSamples).

The full-176 and 12-distinct-external-source high-occupancy-75 gene trees
are newly refitted to TRUE unique nuclear readsets. No sequenced biological
voucher is repeated as a second phylogenetic tip. The previously reported
53-tip Mk and extra C. kamtschaticum population are INVALID as independent
evolutionary evidence, and retained only in the historical audit.
"""
from __future__ import annotations

import argparse,copy,csv,hashlib,json,math,re
from collections import Counter
from pathlib import Path
from Bio import Phylo
import numpy as np
from scipy.optimize import minimize
from fit_real_world45_multitopology_U_D_mk_v1 import fit_one, fitch_minimum

OUTGROUP="OUTGROUP_saff"
REMOVE_TIP="GLB2_SRR30887251_Cirsium_kamtschaticum"
KAM_REAL="J38S038"
NA_D="GLB_SRR30887231_Cirsium_vinaceum"
WEST_D="GLB_SRR30887186_Cirsium_erisithales"
NA6=(
"GLB_SRR30887153_Cirsium_ownbeyi",
"GLB_SRR30887180_Cirsium_flodmanii",
"GLB_SRR30887231_Cirsium_vinaceum",
"GLB2_SRR25265683_Cirsium_mohavense",
"GLB2_SRR25265699_Cirsium_hesperium",
"GLB2_SRR25265707_Cirsium_fontinale_var._campylon")
EU5=(
"GLB_SRR30887156_Cirsium_oleraceum",
"GLB_SRR30887186_Cirsium_erisithales",
"GLB2_SRR25265555_Cirsium_arvense",
"GLB2_SRR30887218_Cirsium_brachycephalum",
"GLB2_SRR30887242_Cirsium_leucocephalum")
NINE=("CorollaThroat","CorollaColor","Duration","GlutinousRidge","Habit",
      "HeadPosition","InnerPhyllaryColor","OuterPhyllaryPosition","StyleBranchColor")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load_table(p):
    with Path(p).open(encoding="utf-8-sig",newline="") as handle:
        return list(csv.DictReader(handle))


def source_ingroup(tree, row_by_tip):
    t=copy.deepcopy(tree)
    t.root_with_outgroup({"name":OUTGROUP})
    t.prune(OUTGROUP)
    while len(t.root.clades)==1:
        t.root=t.root.clades[0]
        t.root.branch_length=None
    if len(t.get_terminals())!=51:
        raise ValueError("source ingroup is not exactly 51 original public BioSamples")
    for child in t.find_clades():
        if child is not t.root and (child.branch_length is None or
            not math.isfinite(float(child.branch_length)) or float(child.branch_length)<0):
            raise ValueError("original nuclear tree has unphysical/missing branch length")
    return t, {k:v for k,v in row_by_tip.items() if k!=OUTGROUP}


def unrooted_splits(tree, universe):
    out=set()
    for n in tree.find_clades():
        side=frozenset(t.name for t in n.get_terminals())
        other=frozenset(universe-side)
        if min(len(side),len(other))<2:continue
        out.add(min((side,other),key=lambda x:(len(x),tuple(sorted(x)))))
    return out


def source_clade(tree, ids):
    required=set(ids)
    if not required<={t.name for t in tree.get_terminals()}:
        raise ValueError("geographic source voucher not present in real nuclear tree")
    a=tree.common_ancestor(list(ids))
    observed={t.name for t in a.get_terminals()}
    return {"n_source_individuals":len(required),"n_MRCA_descendant_tips":len(observed),
            "monophyletic_on_original_source_tree":observed==required,
            "MRCA_original_source_support_node":str(a.name or a.confidence or ""),
            "not_global_clade_of_all_accepted_species":True}


def mk_model_set(tree, phenotype):
    result=[]
    for panel in ("all_unique_original_molecules",
                  "hold_North_America_C_vinaceum_D_as_unknown",
                  "hold_West_Palearctic_cultivated_C_erisithales_D_as_unknown"):
        states=copy.deepcopy(phenotype)
        if panel.startswith("hold_North"):
            if states[NA_D]["head_orientation"]!="D":raise ValueError("NA source botanical D vanished")
            states[NA_D]["head_orientation"]="?"
        elif panel.startswith("hold_West"):
            if states[WEST_D]["head_orientation"]!="D":raise ValueError("cultivated west source D vanished")
            states[WEST_D]["head_orientation"]="?"
        count=Counter(x["head_orientation"] for x in states.values())
        if sum(count.values())!=51 or count["U"]!=19 or count["D"]<7:
            raise ValueError("botanical source panel drift")
        phylo_trait_taxa={
          " ".join(re.match(r"^(Cirsium) ([a-z][a-z-]+)",x["source_taxon"]).groups())
          for x in states.values() if x["head_orientation"] in {"U","D"}
        }
        fitch=fitch_minimum(tree,states)
        n=len(phylo_trait_taxa)
        for model in ("ER","ARD"):
            fit=fit_one(tree,states,model)
            k=fit["n_params"]
            AIC=2*k-2*fit["log_likelihood"]
            AICc=AIC+2*k*(k+1)/(n-k-1)
            result.append({
              "panel":panel,"model":model,"n_real_ingroup_BioSamples":51,
              "U_tip_states":count["U"],"D_tip_states":count["D"],"missing":count["?"],
              "n_distinct_phenotyped_source_species_binomials":n,
              "source_Fitch_minimum_character_changes":fitch,
              "log_likelihood":fit["log_likelihood"],"AIC":AIC,"AICc":AICc,
              "q_U_to_D_per_sequence_substitution":fit["q_UD_per_substitution"],
              "q_D_to_U_per_sequence_substitution":fit["q_DU_per_substitution"],
              "root_P_U":float(fit["post"]["node_posterior"][0][0]),
              "root_P_D":float(fit["post"]["node_posterior"][0][1]),
              "ARD_rate_optimizer_boundary_warning":fit["near_parameter_bounds"],
            })
    return result


def compare(*,full_tree,subset_tree,source_traits,collision_receipt,source_inputs,outdir):
    qc=json.loads(collision_receipt.read_text(encoding="utf-8"))
    if qc["unique_individual_BioSamples_after_de_dup"]!=51 or qc["source_52tip_S1_original_nine_trait_csv_SHA256"]!=sha(source_traits):
        raise ValueError("original S1 duplicate-proof molecular audit and trait source disagree")
    if qc["source_52tip_176locus_alignment_SHA256"]!=sha(source_inputs/"world52_original176_uniqueBioSamples.fasta"):
        raise ValueError("original molecular source alignment changed unexpectedly")
    if qc["source_52tip_75locus_alignment_SHA256"]!=sha(source_inputs/"world52_75loci_all12_external_uniqueBioSamples.fasta"):
        raise ValueError("original 12-unique-external gene subset changed unexpectedly")
    traits=load_table(source_traits)
    if len(traits)!=52 or len({r["source_biosample"] for r in traits if r["tip_id"]!=OUTGROUP})!=51:
        raise ValueError("S1 voucher has uncorrected individual duplicate")
    row_by_tip={r["tip_id"]:r for r in traits}
    if REMOVE_TIP in row_by_tip or KAM_REAL not in row_by_tip:
        raise ValueError("wrong same-SRR source individual retained")
    if Counter(row_by_tip[k]["head_orientation"] for k in row_by_tip if k!=OUTGROUP)!=Counter({"U":19,"D":8,"?":24}):
        raise ValueError("source corrected original taxon concepts/missing morphology drift")
    base=set(row_by_tip)
    trees={}
    results=[]
    for label,path in (("all_176_nuclear_genes",full_tree),
                       ("matched_75_all12_unique_externals_ge40pct",subset_tree)):
        original=Phylo.read(path,"newick")
        ids={x.name for x in original.get_terminals()}
        if ids!=base or len(original.get_terminals())!=52:
            raise ValueError("genuine molecular tree has not 52 UNIQUE source tips")
        ingroup,panel=source_ingroup(original,row_by_tip)
        fits=mk_model_set(ingroup,panel)
        originals={x["model"]:x for x in fits if x["panel"]=="all_unique_original_molecules"}
        result={
          "tree":label,"newick_sha256":sha(path),
          "n_source_individuals":52,"n_Cirsium_unique_BioSamples":51,
          "n_total_source_flower_head_assignments":{"U":19,"D":8,"unknown":24},
          "original_source_Mk_models":originals,
          "ARD_minus_ER_AICc":originals["ARD"]["AICc"]-originals["ER"]["AICc"],
          "Fitch_minimum_U_D_steps":originals["ER"]["source_Fitch_minimum_character_changes"],
          "North_American_six_original_Moreyra_source_samples":source_clade(original,NA6),
          "West_Palearctic_five_original_Moreyra_source_samples":source_clade(original,EU5),
          "other_molecular_tip_counts":{
              "original_Moreyra_39_taxonomic_paper_members":39,
              "other_region_external_individuals":12,
              "source_long_outgroup":1,
          },
          "model_sensitivities":fits,
        }
        results.append(result)
        trees[label]=original
    a,b=trees.values()
    A,B=unrooted_splits(a,base),unrooted_splits(b,base)
    rf=len(A.symmetric_difference(B))
    if len(A)!=49 or len(B)!=49:
        raise ValueError("some source molecular tree is unresolved or unexpected split count")
    source_only_j38_vouchers={
       k:v["source_voucher"] for k,v in row_by_tip.items()
       if k.startswith("J38S") and not any(x in v["source_voucher"].lower()
                   for x in ("japan","honshu","shikoku","kyushu","hokkaido"))
    }
    report={
      "version":"world52_true_S1_unique_source_176vs75_gene_Mk_and_topology_v1",
      "QC_before_any_topology":"Original 53-tip source tree contained same C. kamtschaticum BioSample/SRR twice. Replaced by an actually de-duplicated 52-tip phylogeny, with only ONE true C. kamtschaticum genomic sample.",
      "shared_source_alignment_and_original_study_molecular_tip_hashes_verified":True,
      "all_source_Cirsium_individuals_unique_BioSample":True,
      "n_Cirsium_unique_BioSamples":51,"n_total_molecular_tips":52,
      "same_SRR_duplicated":False,"original_duplication":qc,
      "phylogram_branch_units":"substitutions/site, not time",
      "new_gene_subset_criterion":"all 12 externally added actual distinct BioSamples >=40% ACGT per entire original gene, morphology-blind",
      "original_nuclear_loci":176,"gene_subset_high_occupancy_loci":75,
      "all52tip_unrooted_Robinson_Foulds":rf,
      "max_possible_RF_for_two_bifurcating52tip_trees":2*(52-3),
      "shared_unrooted_bipartitions":len(A.intersection(B)),
      "model_analyses":results,
      "source_original_Moreyra_J38_is_paper_taxonomy_not_exclusive_Japanese_collection_area":True,
      "original_J38_voucher_fields_without_literally_Japan_or_Honshu_or_Hokkaido":source_only_j38_vouchers,
      "population_evolutionary_claims_excluded":[
        "the original two kamtschaticum molecular tips represent distinct geographic populations",
        "same-SRR independent evolutionary state change count or phylogenetic allele divergence",
        "identified ancestral head U or D from equal-prior Mk root ~0.5",
        "reliably directed number of U-to-D transitions from fixed-tree Fitch steps",
        "robust complete 294-BioSample/350-low-copy-locus worldwide Cirsium species tree",
        "selection/fitness/palaeoclimate event cause or date",
        "all 39 original Japan38 members sampled physically in Japan",
        "sequenced-voucher head colour directly measured in S1"
      ]
    }
    outdir.mkdir(parents=True,exist_ok=True)
    (outdir/"world52_unique_BioSample_176_vs75_nuclear_S1_phylogenetic_audit.json").write_text(
       json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    with (outdir/"corrected_world52_mk_ancestral_U_D_ER_ARD.csv").open("w",encoding="utf-8",newline="") as h:
        fitrows=[{"tree":x["tree"],**v} for x in results for v in x["model_sensitivities"]]
        w=csv.DictWriter(h,fieldnames=list(fitrows[0]))
        w.writeheader();w.writerows(fitrows)
    print(json.dumps({
      "actual_nuclear_tips":52,"actual_Cirsium_BioSamples":51,
      "same_BioSample_duplication_removed":True,
      "source_original_U_D_missing":[19,8,24],
      "RF_176_vs75":rf,
      "comparisons":[{
        "real_nuclear_loci":176 if x["tree"]=="all_176_nuclear_genes" else 75,
        "source_Fitch_UD_minimum":x["Fitch_minimum_U_D_steps"],
        "ARD_minus_ER_AICc":x["ARD_minus_ER_AICc"],
        "North_America_six_exclusive":x["North_American_six_original_Moreyra_source_samples"]["monophyletic_on_original_source_tree"],
        "West_Palearctic_five_exclusive":x["West_Palearctic_five_original_Moreyra_source_samples"]["monophyletic_on_original_source_tree"]
      } for x in results]
    },indent=2),flush=True)
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--full176-tree",type=Path,required=True)
    p.add_argument("--balanced75-tree",type=Path,required=True)
    p.add_argument("--traits",type=Path,required=True)
    p.add_argument("--collision-receipt",type=Path,required=True)
    p.add_argument("--source-input-dir",type=Path,required=True)
    p.add_argument("--outdir",type=Path,required=True)
    a=p.parse_args()
    compare(full_tree=a.full176_tree,subset_tree=a.balanced75_tree,
            source_traits=a.traits,collision_receipt=a.collision_receipt,
            source_inputs=a.source_input_dir,outdir=a.outdir)


if __name__=="__main__":
    main()
