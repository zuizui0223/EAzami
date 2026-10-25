#!/usr/bin/env python3
"""Overlay explicit Moreyra S1 sample/voucher and independently sourced floral traits
on a newly inferred REAL 45-tip Compositae1061 global-bridge nuclear tree.

The Japan38 specimen IDs, BioSamples and vouchers come from the ORIGINAL
published/frozen 40-tip Japan38 alignment artifact; orientation, phyllary and
stickiness are authority-coded NMNS *taxon concept* evidence, not per-voucher
observations. Source-specific NA nine-category characters are NOT silently
equated to Japanese sticky and phyllary traits. Missing evidence is always "?".

Never treat tip-level duplicates as independent origins, or call a
40-tip Japan38 + five-continent pilot an accepted world 294-tip tree.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from collections import Counter
from pathlib import Path
from Bio import Phylo

ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/"data/evidence"
WORLD=EVIDENCE/"global_5taxa_comp1061_real_target_capture_bridge_v1.csv"
NMNS=[EVIDENCE/"japan38_nmns_capitulum_trait_seed_v1.csv",
      EVIDENCE/"japan38_nmns_capitulum_trait_seed_extension_v2.csv"]
COLOUR=EVIDENCE/"moreyra2025_japan_colour_text_evidence_v1.csv"
SINISCALCHI_COMMIT="c925d4af86160064448f794a9715f70b917a2786"
SINISCALCHI="https://raw.githubusercontent.com/carol-siniscalchi/cirsium/"+SINISCALCHI_COMMIT+"/traits/traits.csv"
SINISCALCHI_GIT_BLOB="fa127f0587b676e6e004ea121424d26069586bcb"
EXCLUDED_POLYMORPHISM={"JPN_36"} # C. sieboldii detail also describes local upright forms.
HEADER=[
    "tip_id","source_group","paper_japan_member_id",
    "source_taxon_label","source_voucher","biosample","run_accessions",
    "head_state","head_source","head_status",
    "corolla_colour_authority","corolla_colour_source","corolla_colour_status",
    "NMNS_phyllary_posture","NMNS_stickiness","NMNS_source",
    "Siniscalchi_corolla_throat","Siniscalchi_corolla_colour",
    "Siniscalchi_duration","Siniscalchi_glutinous_ridge",
    "Siniscalchi_habit","Siniscalchi_head_position",
    "Siniscalchi_inner_phyllary_colour",
    "Siniscalchi_outer_phyllary_position",
    "Siniscalchi_style_branch_colour",
    "trait_same_sequenced_voucher_confirmed",
]


def rows(path:Path):
    with Path(path).open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))


def source_nine_trait_table(path:Path):
    # The original 63-tip author matrix is downloaded in a separate pinned
    # workflow and checked against its original git blob SHA.
    from Bio import SeqIO
    if path is None:return {}
    if hashlib.sha1(b"blob "+str(path.stat().st_size).encode()+b"\0"+path.read_bytes()).hexdigest()!=SINISCALCHI_GIT_BLOB:
        raise ValueError("source Siniscalchi morphological CSV Git blob fingerprint drift")
    table={r["Species"]:r for r in rows(path)}
    if len(table)!=63:
        raise ValueError("Siniscalchi original nine character table changed")
    return table


def nmns_ontology():
    lookup={}
    for filepath in NMNS:
        for row in rows(filepath):
            key=row["paper_japan_member_id"]
            if key in lookup:
                a,b=lookup[key],row
                for trait in ("orientation_state","phyllary_posture","stickiness_state"):
                    if a[trait] not in ("", "unknown") and b[trait] not in ("","unknown") and a[trait]!=b[trait]:
                        raise ValueError("cross-source NMNS trait contradicts: "+key+"/"+trait)
                a.update({t:b[t] for t in ("orientation_state","phyllary_posture","stickiness_state")
                          if b[t] not in ("","unknown")})
            else:
                lookup[key]=dict(row)
    return lookup


def head_code(member, nmns):
    row=nmns.get(member)
    if not row:return "?", "", "NMNS_no_state_record"
    raw=row["orientation_state"]
    if member in EXCLUDED_POLYMORPHISM:
        return "?",row["source_url"],"within_taxon_orientation_polymorphism_veto"
    if raw in {"upward_or_erect","upward_or_ascending"}:
        return "U",row["source_url"],"NMNS_taxon_concept_only"
    if raw=="downward_or_nodding":
        return "D",row["source_url"],"NMNS_taxon_concept_only"
    return "?",row["source_url"],"unknown_or_conflicting_source_state"


def overlay(source_dir:Path, result_dir:Path, na_nine_trait:Path|None):
    jp=rows(source_dir/"japan38_bundle/sample_manifest.csv")
    if len(jp)!=39 or len({r["tip_id"] for r in jp})!=39:
        raise ValueError("not original Japan38 39 individual source samples")
    world=rows(WORLD)
    if len(world)!=5 or len({r["SRR"] for r in world})!=5:
        raise ValueError("not five independent outside-Japan specimen runs")
    nmns=nmns_ontology()
    colour={r["moreyra_japan_member_id"]:r for r in rows(COLOUR)}
    author_traits=source_nine_trait_table(na_nine_trait)
    out=[]
    for r in jp:
        tip=r["tip_id"]
        member=r["paper_japan_member_id"]
        state,source,status=head_code(member,nmns)
        m=nmns.get(member,{})
        col=colour.get(member,{})
        cr=col.get("binary_colour_code","?")
        out.append({
            "tip_id":tip,"source_group":"Japan38_original_nuclear_sampling_not_individual_origin",
            "paper_japan_member_id":member,"source_taxon_label":r["analysis_taxon_label"],
            "source_voucher":r["voucher"],"biosample":r["biosample"],
            "run_accessions":r["run_accessions"],
            "head_state":state,"head_source":source,"head_status":status,
            "corolla_colour_authority":cr,"corolla_colour_source":col.get("colour_source_url",""),
            "corolla_colour_status":"polymorphic" if cr=="P" else (
                "taxon_source_coloured" if cr=="C" else "unknown"
            ),
            "NMNS_phyllary_posture":m.get("phyllary_posture","unknown"),
            "NMNS_stickiness":m.get("stickiness_state","unknown"),
            "NMNS_source":m.get("source_url",""),
            "trait_same_sequenced_voucher_confirmed":"false",
        })
    na_columns={
        "CorollaThroat":"Siniscalchi_corolla_throat",
        "CorollaColor":"Siniscalchi_corolla_colour",
        "Duration":"Siniscalchi_duration",
        "GlutinousRidge":"Siniscalchi_glutinous_ridge",
        "Habit":"Siniscalchi_habit",
        "HeadPosition":"Siniscalchi_head_position",
        "InnerPhyllaryColor":"Siniscalchi_inner_phyllary_colour",
        "OuterPhyllaryPosition":"Siniscalchi_outer_phyllary_position",
        "StyleBranchColor":"Siniscalchi_style_branch_colour",
    }
    for r in world:
        name=r["source_taxon"]
        tip="GLB_"+r["SRR"]+"_"+name.replace(" ","_")
        t=author_traits.get(name.replace(" ","_"),{})
        newrow={
            "tip_id":tip,"source_group":r["region"],
            "paper_japan_member_id":"","source_taxon_label":name,
            "source_voucher":r["source_locality"],
            "biosample":r["biosample"],"run_accessions":r["SRR"],
            "head_state":r["head_state_source_only"],
            "head_source":r["head_morphology_url"],"head_status":"independent_species_treatment_taxon_concept_only",
            "corolla_colour_authority":"?",
            "corolla_colour_source":"",
            "corolla_colour_status":"no_mutually_comparable_Japan38_colour",
            "NMNS_phyllary_posture":"unknown",
            "NMNS_stickiness":"unknown",
            "NMNS_source":"",
            "trait_same_sequenced_voucher_confirmed":"false",
        }
        newrow.update({column:t.get(field,"") for field,column in na_columns.items()})
        out.append(newrow)
    if len(out)!=44 or len({r["tip_id"] for r in out})!=44:
        raise ValueError("expected 39 Japan and five independent global nuclear in-group specimens")
    return out


def fitch(node, states):
    if node.is_terminal():
        state=states.get(node.name,"?")
        return ({"U","D"} if state=="?" else {state}), 0
    subsets=[fitch(c,states) for c in node.clades]
    current=set(subsets[0][0]);steps=sum(x[1] for x in subsets)
    for allowed,_ in subsets[1:]:
        overlap=current & allowed
        if overlap:current=overlap
        else:
            current|=allowed
            steps+=1
    return current,steps


def run(args):
    out=overlay(args.original, args.tree_dir, args.na_traits)
    treefile=args.tree_dir/"world45_176loci_ML.treefile"
    if not treefile.exists():
        raise FileNotFoundError("genuine ML Newick tree has not been inferred")
    tree=Phylo.read(treefile,"newick")
    names=[x.name for x in tree.get_terminals()]
    if len(names)!=45 or len(set(names))!=45 or (set(names)-{"OUTGROUP_saff"})!={x["tip_id"] for x in out}:
        raise ValueError("molecular tree and independently frozen S1 plus extra sample metadata disagree")
    # Use outgroup only to set topology for plotting; no admixture events are inferred.
    tree.root_with_outgroup({"name":"OUTGROUP_saff"})
    states={r["tip_id"]:r["head_state"] for r in out}
    known=Counter(states.values())
    if known["D"]<5 or known["U"]<10:
        raise ValueError("frozen molecular U/D sources are no longer adequate for simple diagnostics")
    parsimony=fitch(tree.root,states)[1]
    outdir=args.outdir
    outdir.mkdir(parents=True,exist_ok=True)
    with (outdir/"world45_molecular_tip_MoreyraS1_nmns_colour_nine_trait_join.csv").open(
            "w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=HEADER)
        w.writeheader()
        w.writerows(out)

    # Distinguish within-taxon-unknown from a species-level true negative.
    report={
        "version":"world45_real_Comp1061_tree_independent_morphology_and_S1_voucher_join_v1",
        "molecular_tree_file":treefile.name,
        "molecular_tree_SHA256":hashlib.sha256(treefile.read_bytes()).hexdigest(),
        "total_tree_tips":45,"source_Japan38_specimens":39,
        "outside_Japan_source_tips":5,"outgroup_Carthamus":1,
        "molecular_tip_name_exact_join_passed":True,
        "Moreyra_S1_variables_anchored":["paper_japan_member_id","source_taxon_label","source_voucher","biosample","run_accessions"],
        "head_orientation_n_tip_counts":dict(sorted(known.items())),
        "source_taxon_concept_Fitch_minimum_U_D_changes":parsimony,
        "NMNS_and_FNA_species_head_state_not_same_voucher":True,
        "Siniscalchi_nine_traits_attached":sum(bool(r.get("Siniscalchi_head_position")) for r in out),
        "Moreyra_colour_authority_class":dict(sorted(Counter(r["corolla_colour_authority"] for r in out).items())),
        "resolved_nonadaptive_change_count_is_true_evolutionary_event_count":False,
        "same_specimen_morphology_assayed":False,
        "the_350gene_294BioSample_world_tree_inferred":False,
        "caveat":"17+ taxon-level head states not individual-voucher measured; unknown and polymorphic taxa remain unresolved; markers are a BWA reference-projected strict pilot and do not prove global complete phylogeny."
    }
    (outdir/"world45_S1_head_flower_9traits_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

    if not args.no_fig:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle
        tips=[x for x in tree.get_terminals() if x.name!="OUTGROUP_saff"]
        metadata={r["tip_id"]:r for r in out}
        ys={t:float(len(tips)-1-i) for i,t in enumerate(tips)}
        y={**ys}
        def find_y(node):
            if node in y:return y[node]
            a=[find_y(c) for c in node.clades]
            y[node]=sum(a)/len(a)
            return y[node]
        y[tree.find_any(name="OUTGROUP_saff")]=-1
        find_y(tree.root)
        for metric in ("cladogram","branch_lengths"):
            xs={}
            def find_x(node,last=0):
                v=last+(1.0 if metric=="cladogram" else float(node.branch_length or 0))
                xs[node]=v
                for child in node.clades:find_x(child,v)
            find_x(tree.root)
            mx=max(xs[t] for t in tips)
            fig,ax=plt.subplots(figsize=(16,15))
            for n in tree.find_clades():
                if not n.clades:continue
                x=xs[n]
                vals=[y[c] for c in n.clades]
                ax.vlines(x,min(vals),max(vals),color="#8E9AA5",lw=.65)
                for c in n.clades:
                    ax.hlines(y[c],x,xs[c],color="#8E9AA5",lw=.65)
            step=.15*max(mx,1.0) if metric=="cladogram" else .035*max(mx,1.0)
            bars=[mx+i*step for i in range(1,5)]
            palette_head={"U":"#2788AF","D":"#E08B37","?":"#E4E7EB"}
            palette_colour={"C":"#B56B9E","P":"#D0AFD8","W":"#D8D8D8","?":"#EBEEF1"}
            palette_source={"North_America":"#4282B0","West_Palearctic":"#B88655","Japan38_original_nuclear_sampling_not_individual_origin":"#78A991"}
            for t in tips:
                r=metadata[t.name];yi=y[t]
                attributes=[
                    palette_source.get(r["source_group"],"#CCCCCC"),
                    palette_head.get(r["head_state"],"#DDDDDD"),
                    palette_colour.get(r["corolla_colour_authority"],"#DDDDDD"),
                    "#A0B6A8" if r["NMNS_stickiness"]=="sticky" else ("#CFC6DA" if r["NMNS_stickiness"]=="nonsticky_or_nearly_nonsticky" else "#EBEEF1"),
                ]
                for bx,col in zip(bars,attributes):
                    ax.add_patch(Rectangle((bx,yi-.30),step*.65,.6,facecolor=col,edgecolor="white",lw=.3))
                label=f"{r['paper_japan_member_id'] or r['run_accessions']} {r['source_taxon_label']}"
                ax.text(bars[-1]+step*.95,yi,label,va="center",fontsize=6)
            for bx,label in zip(bars,("Source sample lane","Head U/D","Colour C/P","NMNS sticky")):
                ax.text(bx,len(tips)+.9,label,rotation=40,fontsize=7,ha="left",va="bottom")
            ax.set_yticks([])
            ax.set_ylim(-2,len(tips)+5)
            ax.set_xlim(-step,bars[-1]+(14 if metric=="cladogram" else 38)*step)
            ax.set_title("REAL 45-tip Cirsium nuclear Compositae1061 | Moreyra S1 sample IDs × source head traits",loc="left",fontsize=11)
            ax.set_xlabel("Topology only — equal branch display" if metric=="cladogram" else "IQ-TREE branch lengths — substitutions per site")
            for spine in ax.spines.values():spine.set_visible(False)
            fig.text(.08,.04,"39 original Japan38 molecular samples + 5 independently acquired NA/Europe Moreyra nuclear reads + saff outgroup. Colour C=coloured/P=polymorphic; ? unknown. Traits are source taxon concepts, not sequenced-voucher measurements.",fontsize=7)
            fig.subplots_adjust(bottom=.08)
            fig.savefig(outdir/f"world45_real_nuclear_{metric}_source_traits.png",dpi=160,bbox_inches="tight")
            fig.savefig(outdir/f"world45_real_nuclear_{metric}_source_traits.svg",bbox_inches="tight")
            plt.close(fig)
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--tree-dir",type=Path,required=True)
    p.add_argument("--na-traits",type=Path,default=None)
    p.add_argument("--outdir",type=Path,required=True)
    p.add_argument("--no-fig",action="store_true")
    run(p.parse_args())

if __name__=="__main__":main()
