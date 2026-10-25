#!/usr/bin/env python3
"""Join genuine 53-tip, 176-locus molecular tree to S1 vouchers and original nine traits.

Strictly source-frozen:
- Original Moreyra J38 molecule/voucher metadata remain from the archived
  original 39-sample manifest; prior five Moreyra NA/EU original sources are
  frozen separately.
- Original independent botanical U/D and NA nine traits from world45 CSV.
- Further eight molecules were chosen BEFORE phenotype inspection and
  their nine-character source rows are archived post-freeze.
- The previously preselected Cirsium fargesii run was rejected at 63<70
  source-ortholog loci, not based on its head, flower colour or topology.
Biological conclusions remain taxon-level, NOT photos of the sequenced voucher.
"""
from __future__ import annotations
import argparse,copy,csv,hashlib,json,math,re
from collections import Counter,defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
from Bio import Phylo

from fit_real_world45_multitopology_U_D_mk_v1 import fit_one, fitch_minimum
from build_real_world54_176locus_traitblind_extension_v1 import registry as nine

OUTGROUP="OUTGROUP_saff"
SHA45="c405956db7c3d68f9b408b0a91cb588b0a2775f6eaff96456998a76b08deac07"
SHA9="f768c7097267d37507fb20b4167ea5613940bad5518ff9f8c5a02185a466f607"
SHAJ38="57127dc2fd55bd87b85a1002aa124472b684310ba4f853cc169a792614129bab"
FAILED_RUN="SRR30887183"
NINE=("CorollaThroat","CorollaColor","Duration","GlutinousRidge","Habit",
      "HeadPosition","InnerPhyllaryColor","OuterPhyllaryPosition","StyleBranchColor")
COLOUR={"0":"#B84E5E","1":"#9659A2","2":"#D3CBD9","3":"#D5B84C"}
HEAD={"U":"#367FA4","D":"#DB8E44","?":"#D5DADF"}
DEFAULT_PALETTE={"0":"#D9DFE4","1":"#6B899D","2":"#9A64AA","3":"#CFB365","":"#E7E9EA"}
REGION={"North_America":"#CC9870","West_Palearctic":"#71967C",
        "Continental_East_Central_Asia":"#AF79A3",
        "Japan38_2025_moreyra":"#7F96AC"}
COLUMNS=("head_orientation",)+NINE


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read_csv(p):
    with Path(p).open(encoding="utf-8-sig",newline="") as h:
        return list(csv.DictReader(h))


def source_binomial(name):
    match=re.match(r"^(Cirsium|Carduus)\s+([a-z][a-z-]+)",name)
    return (" ".join(match.groups())) if match else ""


def build_rows(old_path,new_path,manifest_path,tree):
    for p,want in ((old_path,SHA45),(new_path,SHA9),(manifest_path,SHAJ38)):
        if sha(p)!=want:
            raise ValueError("S1 source phenotype or voucher source SHA256 changed: "+str(p))
    old=read_csv(old_path)
    new=read_csv(new_path)
    j38=read_csv(manifest_path)
    if len(old)!=45 or len(new)!=9 or len(j38)!=39:
        raise ValueError("source phenotype and S1 molecular-voucher cohort no longer frozen")
    jap={r["tip_id"]:r for r in j38}
    if len(jap)!=39:
        raise ValueError("duplicate original molecular Japanese accession")
    oldkeys={r["tip_id"] for r in old}
    if len(oldkeys)!=45 or OUTGROUP not in oldkeys:
        raise ValueError("source 45-tip phylogeny character table drift")
    if len({r["SRR"] for r in new})!=9:
        raise ValueError("nine source-selected SRR cohort has duplicates")
    selected=nine()
    if {r["SRR"] for r in new}!=set(selected):
        raise ValueError("postselection morphology no longer matches blind source registration")
    pending=[]
    for r in old:
        d={
            "tip_id":r["tip_id"],"source_taxon":r["source_taxon"],
            "region":r["geographic_panel"],
            "head_orientation":r["head_orientation"],
            "head_source_url":r["head_source_url"],
            "head_reason_unresolved":r["head_reason_unresolved"],
            "Japanese_taxon_colour_code":r["flower_colour_C_W_P_code"],
            "same_sequenced_voucher_phenotyped":"false",
            "head_selection_did_not_use_phenotype":"false",
            "molecule_study":"Moreyra_2025_Comp1061_target_capture",
            "source_biosample":"","source_run":"","source_voucher":"",
            **{x:r[x] for x in NINE}
        }
        tip=r["tip_id"]
        if tip in jap:
            d["source_biosample"]=jap[tip]["biosample"]
            d["source_run"]=jap[tip]["run_accessions"]
            d["source_voucher"]=jap[tip]["voucher"]
        elif tip.startswith("GLB_"):
            # Original five exact source identities should be looked up from
            # the frozen named taxon+SRR given in the tip itself. The 45-tip
            # source data do not pretend to have raw voucher metadata.
            d["source_run"]=tip.split("_")[1]
        else:
            if tip!=OUTGROUP:
                raise ValueError("neither Japan38 nor public NA/EU source tip "+tip)
        pending.append(d)
    for r in new:
        if r["SRR"]==FAILED_RUN:
            continue
        row=selected[r["SRR"]]
        if r["biosample"]!=row["biosample"] or r["taxon_source_label"]!=row["taxon_source_label"]:
            raise ValueError("original blind molecular S1 sample vs phenotype row mismatch")
        d={
            "tip_id":r["source_tree_tip_provisional"],
            "source_taxon":r["taxon_source_label"],
            "region":r["source_region"],
            "head_orientation":r["head_orientation_from_exact_botanical_source_after_freeze"],
            "head_source_url":r["head_source_botanical_URLS"] or
                 ("https://github.com/carol-siniscalchi/cirsium/blob/c925d4af86160064448f794a9715f70b917a2786/traits/traits.csv"
                  if r["head_source_original_Siniscalchi_state"] else ""),
            "head_reason_unresolved":r["head_state_admission_reason"],
            "Japanese_taxon_colour_code":"?",
            "same_sequenced_voucher_phenotyped":"false",
            "head_selection_did_not_use_phenotype":"true",
            "molecule_study":"Moreyra_2025_Comp1061_target_capture",
            "source_biosample":r["biosample"],
            "source_run":r["SRR"],
            "source_voucher":r["source_location"],
            **{x:r[x] for x in NINE},
        }
        pending.append(d)
    expected={x.name for x in tree.get_terminals()}
    observed=[r["tip_id"] for r in pending]
    if len(observed)!=len(expected) or len(set(observed))!=len(observed) or set(observed)!=expected:
        raise ValueError("53 actual nuclear tips and original source S1/phenotype tip IDs are not identical")
    for r in pending:
        if r["head_orientation"] not in {"U","D","?"}:
            raise ValueError("source phenotype not explicit U/D/unresolved")
        if r["head_orientation"] in {"U","D"} and not r["head_source_url"]:
            raise ValueError("source observed head phenotype lacks botanical original URL")
        if r["tip_id"].startswith("GLB2_") and r["head_selection_did_not_use_phenotype"]!="true":
            raise ValueError("one of the eight new source specimens was chosen by trait")
    return pending


def model_phylo(tree,panel):
    x=copy.deepcopy(tree)
    x.root_with_outgroup({"name":OUTGROUP})
    x.prune(OUTGROUP)
    if len(x.root.clades)==1:
        x.root=x.root.clades[0]
        x.root.branch_length=None
    rows={r["tip_id"]:r for r in panel if r["tip_id"]!=OUTGROUP}
    if len(rows)!=len(x.get_terminals()):
        raise ValueError("partial ingroup under model")
    return x,rows


def fitted_models(tree,rows):
    tally=Counter(r["head_orientation"] for r in rows.values())
    if tally!=Counter({"U":19,"D":9,"?":24}):
        raise ValueError("original shape/U/D counts no longer match the frozen source claims")
    out=[]
    for case in ("all_source_vouchers","omit_extra_kamtschaticum_population","omit_single_NA_vinaceum_D"):
        t=copy.deepcopy(tree)
        states=copy.deepcopy(rows)
        if case=="omit_extra_kamtschaticum_population":
            alt="GLB2_SRR30887251_Cirsium_kamtschaticum"
            if alt not in states or states[alt]["head_orientation"]!="D":
                raise ValueError("missing independently source-vouchered same-taxon D replicate")
            t.prune(alt)
            del states[alt]
        elif case=="omit_single_NA_vinaceum_D":
            alt="GLB_SRR30887231_Cirsium_vinaceum"
            if alt not in states or states[alt]["head_orientation"]!="D":
                raise ValueError("missing originally selected North American D")
            states[alt]["head_orientation"]="?"
        count=Counter(r["head_orientation"] for r in states.values())
        if min(count["U"],count["D"])<2:
            raise ValueError("non-identifiable source state panel")
        q=[fit_one(t,states,"ER"),fit_one(t,states,"ARD")]
        fitch=fitch_minimum(t,states)
        n_species=len({source_binomial(r["source_taxon"]) for r in states.values()
                       if r["head_orientation"] in {"U","D"}})
        for result in q:
            k=result["n_params"]
            AIC=2*k-2*result["log_likelihood"]
            AICc=AIC+(2*k*(k+1)/(n_species-k-1)) if n_species>k+1 else float("nan")
            out.append({
                "case":case,"Mk_model":result["model"],"n_tip":len(states),
                "U_source_tips":count["U"],"D_source_tips":count["D"],
                "unresolved_source_tips":count["?"],"n_unique_source_binomials_approx":n_species,
                "Fitch_minimum_states_on_fixed_tree":fitch,
                "Mk_nuclear_branch_unit":"substitutions_per_site",
                "log_likelihood":result["log_likelihood"],"AIC":AIC,
                "AICc_approx_unique_binomial_n":AICc,
                "q_UD_per_substitution":result["q_UD_per_substitution"],
                "q_DU_per_substitution":result["q_DU_per_substitution"],
                "root_P_U":float(result["post"]["node_posterior"][0][0]),
                "root_P_D":float(result["post"]["node_posterior"][0][1]),
                "rate_optimizer_at_bound":result["near_parameter_bounds"],
                "root_prior_PU":0.5,
            })
    return out


def draw(tree,traits,output):
    nodes=list(tree.find_clades())
    tips=tree.get_terminals()
    source={r["tip_id"]:r for r in traits}
    xpos={x:float(tree.distance(x)) for x in nodes}
    ypos={tip:len(tips)-i-1 for i,tip in enumerate(tips)}
    def y(node):
        if node in ypos:return ypos[node]
        l=[y(c) for c in node.clades]
        ypos[node]=sum(l)/len(l)
        return ypos[node]
    y(tree.root)
    maxlen=max(xpos[x] for x in tips)
    step=max(maxlen*0.065,.011)
    x0=maxlen+step
    tracks=["head_orientation","Japanese_taxon_colour_code"]+list(NINE)
    xx=[x0+i*step*.75 for i in range(len(tracks))]
    fig,ax=plt.subplots(figsize=(19,16.3))
    fig.patch.set_facecolor("white")
    for nd in nodes:
        if nd.is_terminal():continue
        ys=[ypos[ch] for ch in nd.clades]
        ax.plot([xpos[nd],xpos[nd]],[min(ys),max(ys)],color="#8A969E",lw=.52)
        for ch in nd.clades:
            ax.plot([xpos[nd],xpos[ch]],[ypos[ch],ypos[ch]],color="#8A969E",lw=.52)
    for tip in tips:
        r=source[tip.name];yy=ypos[tip]
        for i,key in enumerate(tracks):
            value=r[key]
            if key=="head_orientation":col=HEAD[value]
            elif key=="CorollaColor":col=COLOUR.get(value,"#E7E9EA")
            elif key=="Japanese_taxon_colour_code":
                col={"C":"#9561A0","W":"#E6E6E6","P":"#BDA1C9"}.get(value,"#E7E9EA")
            else:col=DEFAULT_PALETTE.get(value,"#E7E9EA")
            ax.add_patch(Rectangle((xx[i],yy-.32),step*.52,.64,
                                   facecolor=col,edgecolor="white",linewidth=.25))
        color=REGION.get(r["region"],"#404A56")
        ax.text(xx[-1]+step*.9,yy,r["source_taxon"],
                fontsize=5.9,color=color,va="center",ha="left")
    labels=["U / D", "JPN colour"]+[{"CorollaThroat":"Throat","CorollaColor":"Corolla colour",
        "GlutinousRidge":"Sticky","InnerPhyllaryColor":"Inner bracts",
        "OuterPhyllaryPosition":"Outer bracts","StyleBranchColor":"Style colour",
        "HeadPosition":"Author head"}.get(x,x) for x in NINE]
    for i,(key,label) in enumerate(zip(tracks,labels)):
        ax.text(xx[i]+step*.2,len(tips)+.7,label,fontsize=7,rotation=60,
                ha="left",va="bottom",color="#41505E")
    ax.set_yticks([])
    ax.set_xlim(-.03,xx[-1]+maxlen*.65+step)
    ax.set_ylim(-1.1,len(tips)+5)
    ax.set_xlabel("Source-preserving real nuclear ML branch length (substitutions/site; NOT time)",fontsize=9)
    ax.set_title("EAzami: empirical crosscontinental 53-tip / 176-locus nuclear tree + S1 / original flower traits",
                 fontsize=12,weight="semibold",loc="left",pad=26)
    ax.text(.003,1.004,
      "8 new source DNA specimens passed frozen 70-locus QC; C. fargesii (63 loci) excluded. Grey = unphenotyped, not erect.",
      transform=ax.transAxes,fontsize=8,color="#65717B",ha="left")
    for spine in ax.spines.values():spine.set_visible(False)
    ax.grid(axis="x",alpha=.15)
    fig.tight_layout()
    fig.savefig(output/"world53_real_176locus_nuclear_S1_9traits.png",dpi=175,bbox_inches="tight")
    fig.savefig(output/"world53_real_176locus_nuclear_S1_9traits.svg",bbox_inches="tight")
    plt.close(fig)


def run(*,tree_path,old_traits,new_trait_sources,j38_manifest,world53_receipt,outdir):
    receipt=json.loads(world53_receipt.read_text(encoding="utf-8"))
    if receipt.get("source_ML_newick_SHA256")!=sha(tree_path) or not receipt.get("nuclear_tree_estimated"):
        raise ValueError("53 source molecular tree not accepted from original 8 QC-passing DNA specimens")
    tree=Phylo.read(tree_path,"newick")
    table=build_rows(old_traits,new_trait_sources,j38_manifest,tree)
    ingroup,rows=model_phylo(tree,table)
    stats=fitted_models(ingroup,rows)
    outdir.mkdir(parents=True,exist_ok=True)
    with (outdir/"world53_original_S1_vouchers_head_nine_trait_rows.csv").open("w",newline="",encoding="utf-8") as h:
        writer=csv.DictWriter(h,fieldnames=list(table[0]))
        writer.writeheader();writer.writerows(table)
    with (outdir/"world53_Mk_U_D_fits.csv").open("w",newline="",encoding="utf-8") as h:
        writer=csv.DictWriter(h,fieldnames=list(stats[0]))
        writer.writeheader();writer.writerows(stats)
    draw(tree,table,outdir)
    result={
        "version":"empirical_real53_original_Moreyra_S1_9source_traits_ER_ARD_mk_v1",
        "n_molecular_tips":53,"n_ingroup_molecular_tips":52,
        "n_Japan38_source_sample_tips":39,
        "n_first_external_source_molecular_tips":5,
        "n_added_traitblind_QC_pass_source_tips":8,
        "n_source_excluded_QC_fail":1,
        "excluded_source_SRR":"SRR30887183",
        "phenotype_source_counts":dict(Counter(r["head_orientation"] for r in rows.values())),
        "n_orig_NA_source_9trait_molecular_tips":sum(any(r[k] for k in NINE) for r in table),
        "n_unique_taxon_binomials_in_phenotyped_panel":len({
             source_binomial(r["source_taxon"]) for r in rows.values()
             if r["head_orientation"] in {"U","D"}
        }),
        "has_same_species_molecular_replication_Cirsium_kamtschaticum":True,
        "model_null_traits_marginalized":True,
        "models_fitted":[
            {key:v for key,v in x.items() if key!="root_prior_PU"} for x in stats
        ],
        "n_original_molecular_gene_alignments":176,
        "published_world_294tip_350locus_tree_not_finished":True,
        "trait_conclusions_are_taxon_source_not_exact_sequenced_voucher":True,
        "single_tree_not_assumed_global_phylogenetic_certainty":True,
        "orientation_rate_CTG_Mk_not_adaptive_causation":True,
        "flower_colour_source_category_2_not_binary_white":"Siniscalchi original CorollaColor code 2 combines white/pink/purple",
        "inputs_SHA256":{
            "tree":sha(tree_path),"old_trait_table":SHA45,
            "new_postfreeze_trait_table":SHA9,"original_J38_S1":SHAJ38,
        },
    }
    (outdir/"world53_actual_nuclear_ancestral_trait_result.json").write_text(
        json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"real_tip_count":53,
        "head_source_U_D_unknown":result["phenotype_source_counts"],
        "mk_cases":[{"case":s["case"],"model":s["Mk_model"],
                "Fitch":s["Fitch_minimum_states_on_fixed_tree"],
                "AIC":round(s["AIC"],3),"root_P_U":round(s["root_P_U"],3)}
            for s in stats],"worldwide_tree_294_finished":False},indent=2),flush=True)
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--tree",type=Path,required=True)
    p.add_argument("--old-traits",type=Path,required=True)
    p.add_argument("--new-postfreeze-traits",type=Path,required=True)
    p.add_argument("--j38-manifest",type=Path,required=True)
    p.add_argument("--world53-receipt",type=Path,required=True)
    p.add_argument("--outdir",type=Path,required=True)
    a=p.parse_args()
    run(tree_path=a.tree,old_traits=a.old_traits,new_trait_sources=a.new_postfreeze_traits,
        j38_manifest=a.j38_manifest,world53_receipt=a.world53_receipt,outdir=a.outdir)

if __name__=="__main__":main()
