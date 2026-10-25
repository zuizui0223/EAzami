#!/usr/bin/env python3
"""Independent inference-algorithm sensitivity of authentic 53-tip 176-nuclear-locus Cirsium.

Compare UNROOTED ML tree bipartitions, geographic clades and head U/D fit
from two different algorithms run on the IDENTICAL original sample alignments.
IQ-TREE ModelFinder-UFBoot support and FastTree local SH support are not
the same statistical metric. No synthetic taxon placements or inferred
morphology. Missing head data are integrated (not imputed).
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,copy
from collections import Counter
from pathlib import Path
from Bio import Phylo

from annotate_real_world53_original_S1_nine_traits_Mk_v1 import model_phylo,fitted_models

SHA_ML="5828ccd9f4f0b083f804f87bfa7407a20ad5eb52647e92eb5a26e812bd6807a7"
OUTGROUP="OUTGROUP_saff"
NA6=(
 "GLB_SRR30887153_Cirsium_ownbeyi",
 "GLB_SRR30887180_Cirsium_flodmanii",
 "GLB_SRR30887231_Cirsium_vinaceum",
 "GLB2_SRR25265683_Cirsium_mohavense",
 "GLB2_SRR25265699_Cirsium_hesperium",
 "GLB2_SRR25265707_Cirsium_fontinale_var._campylon"
)
EU5=(
 "GLB_SRR30887156_Cirsium_oleraceum",
 "GLB_SRR30887186_Cirsium_erisithales",
 "GLB2_SRR25265555_Cirsium_arvense",
 "GLB2_SRR30887218_Cirsium_brachycephalum",
 "GLB2_SRR30887242_Cirsium_leucocephalum"
)
KAM_REPS=("GLB2_SRR30887251_Cirsium_kamtschaticum","J38S038")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def splits(tree,names):
    result=set()
    for node in tree.find_clades():
        side=frozenset(t.name for t in node.get_terminals())
        other=frozenset(names-side)
        if min(len(side),len(other))<2:
            continue
        result.add(min((side,other),key=lambda x:(len(x),tuple(sorted(x)))))
    return result


def group(tree,refs):
    names=set(refs)
    all_tips={tip.name for tip in tree.get_terminals()}
    if not names<=all_tips:
        raise ValueError("regional biological source not in frozen source molecular panel")
    node=tree.common_ancestor(list(refs))
    descendants={tip.name for tip in node.get_terminals()}
    return {
        "source_specimens":len(refs),
        "MRCA_original_molecular_tips":len(descendants),
        "clade_exclusive":descendants==names,
        "original_tip_identity_grounded":True,
        "source_support_node_raw":node.name or node.confidence,
        "support_value_not_comparable_across_IQ_TREE_and_FastTree":True,
    }


def run(ml_tree,fast_tree,trait_source,outdir):
    if sha(ml_tree)!=SHA_ML:
        raise ValueError("53 original IQ-TREE source molecular Newick drift")
    ml=Phylo.read(ml_tree,"newick")
    fast=Phylo.read(fast_tree,"newick")
    base_ml={t.name for t in ml.get_terminals()}
    base_fast={t.name for t in fast.get_terminals()}
    if base_ml!=base_fast or len(base_ml)!=53 or OUTGROUP not in base_ml:
        raise ValueError("the two molecular algorithms did not infer exactly the same 53 original nuclear tips")
    with trait_source.open(encoding="utf-8-sig",newline="") as h:
        rows=list(csv.DictReader(h))
    if len(rows)!=53 or {r["tip_id"] for r in rows}!=base_ml:
        raise ValueError("fixed S1 original source trait join has missing/extraneous molecule")
    expected=Counter(r["head_orientation"] for r in rows if r["tip_id"]!=OUTGROUP)
    if expected!=Counter({"U":19,"D":9,"?":24}):
        raise ValueError("frozen U/D source evidence changed; independent source review required")
    source_splits=splits(ml,base_ml)
    alternate_splits=splits(fast,base_ml)
    max_binary_RF=2*(len(base_ml)-3)
    RF=len(source_splits.symmetric_difference(alternate_splits))
    analysis=[]
    for tree_name, tree in (("IQTREE_ModelFinder",ml),("FastTree_GTR_gamma",fast)):
        ingroup, indexed=model_phylo(tree,rows)
        fits=fitted_models(ingroup,indexed)
        # This fitting function carries 3 prespecified biological source
        # sensitivity panels, each ER + ARD, while preserving 24 unknowns.
        if len(fits)!=6:
            raise ValueError("unexpected count of source morphological fits")
        pairs={}
        for case in {x["case"] for x in fits}:
            rows_case={r["Mk_model"]:r for r in fits if r["case"]==case}
            pairs[case]={
                "n_source_U":rows_case["ER"]["U_source_tips"],
                "n_source_D":rows_case["ER"]["D_source_tips"],
                "n_missing":rows_case["ER"]["unresolved_source_tips"],
                "Fitch_minimum_steps":rows_case["ER"]["Fitch_minimum_states_on_fixed_tree"],
                "ER_AICc":rows_case["ER"]["AICc_approx_unique_binomial_n"],
                "ARD_AICc":rows_case["ARD"]["AICc_approx_unique_binomial_n"],
                "delta_AICc_ARD_minus_ER":rows_case["ARD"]["AICc_approx_unique_binomial_n"]-
                    rows_case["ER"]["AICc_approx_unique_binomial_n"],
                "source_root_P_U_ER":rows_case["ER"]["root_P_U"],
                "source_root_P_U_ARD":rows_case["ARD"]["root_P_U"],
            }
        analysis.append({
            "tree_name":tree_name,
            "source_tree_SHA256":sha(ml_tree if tree_name=="IQTREE_ModelFinder" else fast_tree),
            "regional_MRCA":{
                "North_America_six":group(tree,NA6),
                "West_Palearctic_five":group(tree,EU5),
                "kamtschaticum_repeated_species_molecular_tip_pair":group(tree,KAM_REPS),
            },
            "source_head_fits":pairs,
        })
    if not all(x["regional_MRCA"]["North_America_six"]["clade_exclusive"] for x in analysis):
        raise ValueError("observable North-American six-sample monophyly unexpectedly lost")
    report={
        "version":"actual_world53_ML_vs_FastTree_nuclear_topology_and_floral_history_sensitivity_v1",
        "source_real_nuclear_tips":53,
        "two_inference_algorithms_not_independent_evolutionary_replicates":True,
        "unaltered_molecular_source_alignment_176_Comp1061_loci":True,
        "source_molecular_tree_input_SHA256":{
            "IQTREE_ModelFinder":SHA_ML,
            "FastTree_GTR_gamma":sha(fast_tree),
        },
        "source_original_53tip_count":53,
        "source_trait_states_52_ingroup":{"U":19,"D":9,"?":24},
        "topology_RF_unrooted_53tips":RF,
        "topology_RF_max_two_fully_resolved":max_binary_RF,
        "topology_RF_fraction_max":RF/max_binary_RF,
        "split_count_IQTREE":len(source_splits),
        "split_count_FastTree":len(alternate_splits),
        "shared_unrooted_bipartitions":len(source_splits&alternate_splits),
        "per_tree":analysis,
        "fragility_cautions":[
            "Two trees are derived from the SAME real molecular alignment and hence not independent biological replicate phylogenies.",
            "FastTree local SH-like node support is not IQ-TREE SH-aLRT or ultrafast bootstrap, despite sometimes both being near 1.",
            "North American six source samples are a robust observed clade on these two trees, but this is far from global species sampling.",
            "West Palearctic five and Cirsium kamtschaticum two same-species source samples are not monophyletic in either tree; this may reflect sparse sampling, wrong source taxonomy, introgression or differential/missing-locus mapping, and is not evidence of evolutionary reversion.",
            "Moreyra 2025 S1 supplies genetic voucher records, not direct measured heads for each sequenced specimen.",
            "Fitch changes are minimum steps on fixed trees, not the number or direction of actual historical events.",
            "No world genomic 294-tip/350-locus species-tree, historical climate or pollinator fitness inference is licensed."
        ]
    }
    outdir.mkdir(parents=True,exist_ok=True)
    (outdir/"real_world53_two_nuclear_algorithms_U_D_topology_sensitivity.json").write_text(
        json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8"
    )
    print(json.dumps({
        "molecular_tips":53,"unrooted_RF":RF,
        "nuclear_splits_shared":len(source_splits&alternate_splits),
        "comparisons":[{
            "model":x["tree_name"],
            "head_min_steps":x["source_head_fits"]["all_source_vouchers"]["Fitch_minimum_steps"],
            "delta_AICc_ARD_minus_ER":x["source_head_fits"]["all_source_vouchers"]["delta_AICc_ARD_minus_ER"],
            "North_America_six_clade":x["regional_MRCA"]["North_America_six"]["clade_exclusive"],
            "West_Palearctic_five_clade":x["regional_MRCA"]["West_Palearctic_five"]["clade_exclusive"],
        } for x in analysis]
    },indent=2),flush=True)
    return report


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--ml-tree",type=Path,required=True)
    a.add_argument("--fasttree",type=Path,required=True)
    a.add_argument("--trait-table",type=Path,required=True)
    a.add_argument("--outdir",type=Path,required=True)
    p=a.parse_args()
    run(p.ml_tree,p.fasttree,p.trait_table,p.outdir)


if __name__=="__main__":
    main()
