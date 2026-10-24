#!/usr/bin/env python3
"""Join actual 45-tip 176-locus nuclear tree to source-specific capitulum traits.

Never turn Moreyra S1 voucher columns into morphology, or force missing
Siniscalchi 9-character codes onto Japanese taxa. Match actual frozen molecular
tip IDs to the independent Japan NMNS botanical ontology and five independent
North America/Europe species treatments, retaining provenance and conflicts.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,urllib.request
from collections import Counter
from pathlib import Path
from Bio import Phylo

ROOT=Path(__file__).resolve().parents[1]
EVID=ROOT/"data/evidence"
NA_COMMIT="c925d4af86160064448f794a9715f70b917a2786"
NA_BLOB_SHA1="fa127f0587b676e6e004ea121424d26069586bcb"
NA_URL=f"https://raw.githubusercontent.com/carol-siniscalchi/cirsium/{NA_COMMIT}/traits/traits.csv"
NINE=["CorollaThroat","CorollaColor","Duration","GlutinousRidge","Habit","HeadPosition",
      "InnerPhyllaryColor","OuterPhyllaryPosition","StyleBranchColor"]
HEAD_U={"upward_or_erect","upward_or_ascending","erect","U"}
HEAD_D={"downward_or_nodding","D"}
UNKNOWN={"","unknown","source_conflict_index_downward_detail_erect"}
SKIP_MODERN={"JPN_29":"phenotype_tip_identity_warning","JPN_31":"trait_asr_disallowed",
             "JPN_36":"documented_orientation_polymorphism"}

def rows(path):
    with Path(path).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))

def original_NA_codes():
    req=urllib.request.Request(NA_URL,headers={"User-Agent":"EAzami-world45-authenticated-source-9traits/1.0"})
    with urllib.request.urlopen(req,timeout=45) as f:raw=f.read()
    sha=hashlib.sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest()
    if sha!=NA_BLOB_SHA1:raise ValueError("source Siniscalchi original categorical nine traits changed")
    import io
    return {r["Species"]:r for r in csv.DictReader(io.StringIO(raw.decode()))}

def source_table(tree_path):
    tree=Phylo.read(tree_path,"newick")
    tips={t.name for t in tree.get_terminals()}
    if len(tips)!=45 or "OUTGROUP_saff" not in tips:
        raise ValueError("new real 176-locus 45tip tree not present")
    concepts=rows(EVID/"japan38_comp1061_concept_map_v1.csv")
    seed={}
    for f in ["japan38_nmns_capitulum_trait_seed_v1.csv",
              "japan38_nmns_capitulum_trait_seed_extension_v2.csv"]:
        for r in rows(EVID/f):
            k=r["paper_japan_member_id"]
            if k in seed:
                for field in ("orientation_state","phyllary_posture","stickiness_state"):
                    if r[field] not in UNKNOWN and seed[k][field] not in UNKNOWN and r[field]!=seed[k][field]:
                        raise ValueError("published Japanese source ontology contradiction for "+k)
                    if seed[k][field] in UNKNOWN and r[field] not in UNKNOWN:seed[k][field]=r[field]
            else:seed[k]=dict(r)
    colours={r["moreyra_japan_member_id"]:r for r in
             rows(EVID/"moreyra2025_japan_colour_text_evidence_v1.csv")}
    original_9=original_NA_codes()
    five={r["SRR"]:r for r in rows(EVID/"global_5taxa_comp1061_real_target_capture_bridge_v1.csv")}

    out=[]
    for concept in concepts:
        jpn=concept["paper_japan_member_id"]
        if concept["trait_asr_primary_allowed"] not in {"true","false"}:
            raise ValueError("trait provenance admission malformed")
        s=seed.get(jpn,{})
        h=s.get("orientation_state","")
        state= "U" if h in HEAD_U else "D" if h in HEAD_D else "?"
        exclude=SKIP_MODERN.get(jpn,"")
        if concept["trait_asr_primary_allowed"]=="false":
            state="?";exclude=exclude or "tip_phenotype_excluded"
        if exclude:state="?"
        cr=colours.get(jpn,{})
        for tip in concept["tip_ids"].split("|"):
            out.append({
                "tip_id":tip,"source_taxon":concept["paper_taxon_concept"],
                "geographic_panel":"Japan38_2025_moreyra",
                "source_genetic_study":"Moreyra2025_real_Comp1061_same_176_loci",
                "head_orientation":state,
                "head_orientation_verbatim":h or "unknown",
                "head_source_url":s.get("source_url",""),
                "head_reason_unresolved":exclude or ("no_explicit_accepted_source" if state=="?" else ""),
                "phyllary_source_category":s.get("phyllary_posture","unknown"),
                "glutinous_source_category":s.get("stickiness_state","unknown"),
                "flower_colour_source_category":cr.get("fine_colour_state","unknown"),
                "flower_colour_C_W_P_code":cr.get("binary_colour_code","?"),
                "colour_source_url":cr.get("colour_source_url",""),
                "strict_original_9trait_source_same_study":"false",
                **{k:"" for k in NINE}
            })
    for run,r in five.items():
        tip="GLB_"+run+"_"+r["source_taxon"].replace(" ","_")
        name=r["source_taxon"].replace(" ","_")
        original=original_9.get(name,{})
        # Source code HeadPosition is the author's independent taxon-level
        # observation for North America. Preserve even if other source states
        # disagree, but do not impute from unnamed genus.
        if original and original["HeadPosition"] not in {"0","1"}:
            raise ValueError("unrecognized original nine-trait head code")
        expected=r["head_state_source_only"]
        if original and ("U" if original["HeadPosition"]=="0" else "D")!=expected:
            raise ValueError("mismatch FNA and original source head state")
        color={
            "Cirsium vinaceum":"rose-purple",
            "Cirsium flodmanii":"purple_with_white_form",
            "Cirsium ownbeyi":"white_to_pink-purple",
            "Cirsium erisithales":"pale_yellow",
            "Cirsium oleraceum":"pale_yellow-green",
        }[r["source_taxon"]]
        out.append({
            "tip_id":tip,"source_taxon":r["source_taxon"],
            "geographic_panel":r["region"],
            "source_genetic_study":"Moreyra2025_real_Comp1061_same_176_loci",
            "head_orientation":expected,"head_orientation_verbatim":expected,
            "head_source_url":r["head_morphology_url"],
            "head_reason_unresolved":"",
            "phyllary_source_category":"unknown",
            "glutinous_source_category":"unknown",
            "flower_colour_source_category":color,
            "flower_colour_C_W_P_code":"?",
            "colour_source_url":r["head_morphology_url"],
            "strict_original_9trait_source_same_study":str(bool(original)).lower(),
            **{k:original.get(k,"") for k in NINE}
        })
    out.append({"tip_id":"OUTGROUP_saff","source_taxon":"Carthamus (outgroup)",
        "geographic_panel":"outgroup","source_genetic_study":"original_Comp1061_public_ref",
        "head_orientation":"?","head_orientation_verbatim":"unassessed",
        "head_source_url":"","head_reason_unresolved":"outgroup_not_phenotyped",
        "phyllary_source_category":"unknown","glutinous_source_category":"unknown",
        "flower_colour_source_category":"unknown","flower_colour_C_W_P_code":"?",
        "colour_source_url":"","strict_original_9trait_source_same_study":"false",
        **{k:"" for k in NINE}})
    if len(out)!=45 or len({r["tip_id"] for r in out})!=45 or {r["tip_id"] for r in out}!=tips:
        raise ValueError("exact 45-tip real molecular tree and phenotype inventory mismatch")
    return tree,out

def fit_fitch(root,labels):
    if root.is_terminal():
        state=labels.get(root.name)
        return {state} if state in {"U","D"} else {"U","D"},0
    items=[fit_fitch(c,labels) for c in root.clades]
    acc=set(items[0][0]);steps=sum(x[1] for x in items)
    for child,_ in items[1:]:
        inside=acc&child
        if inside:acc=inside
        else:acc|=child;steps+=1
    return acc,steps

def plot(tree,table,outdir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    look={x["tip_id"]:x for x in table}
    tips=tree.get_terminals()
    y={t:float(len(tips)-i-1) for i,t in enumerate(tips)}
    x={t:float(tree.distance(t)) for t in tree.find_clades()}
    def ypos(n):
        if n in y:return y[n]
        vals=[ypos(c) for c in n.clades]
        y[n]=sum(vals)/len(vals)
        return y[n]
    ypos(tree.root)
    mx=max(x.values())
    fig,ax=plt.subplots(figsize=(16.5,14))
    for n in tree.find_clades():
        if not n.clades:continue
        ys=[y[c] for c in n.clades]
        ax.plot([x[n]]*2,[min(ys),max(ys)],color="#9299A2",lw=.60)
        for c in n.clades:ax.plot([x[n],x[c]],[y[c]]*2,color="#9299A2",lw=.60)
    head={"U":"#318CB5","D":"#E48541","?":"#CBD1D6"}
    region={"Japan38_2025_moreyra":"#5977A8","North_America":"#76AB89",
            "West_Palearctic":"#B28CC4","outgroup":"#818B94"}
    for t in tips:
        r=look[t.name];yy=y[t]
        for col,palette in ((mx+.1,region.get(r["geographic_panel"],"#bbb")),
                            (mx+.3,head[r["head_orientation"]])):
            ax.add_patch(Rectangle((col,yy-.36),.14,.72,facecolor=palette,edgecolor="white",lw=.3))
        ax.text(mx+.53,yy,r["source_taxon"]+"   ["+t.name+"]",va="center",fontsize=7)
    ax.set_xlim(-.05,mx+3.7);ax.set_ylim(-1.2,len(tips)+2.0)
    ax.set_title("Empirical 45-tip 176-locus Compositae1061 nuclear pilot | U/D source annotation",loc="left",pad=14)
    ax.set_xlabel("IQ-TREE branch lengths, substitutions/site; NOT phylogenetic divergence times")
    ax.set_yticks([])
    for k in ax.spines:ax.spines[k].set_visible(False)
    ax.text(.65,.01,"Morphology from independent taxon-level floras; unknowns retained; regional pilot, not all-world phylogeny",
            fontsize=7,transform=ax.transAxes,color="#555")
    fig.tight_layout()
    fig.savefig(outdir/"real_nuclear45_U_D_source_map.png",dpi=170,bbox_inches="tight")
    fig.savefig(outdir/"real_nuclear45_U_D_source_map.svg",bbox_inches="tight")
    plt.close(fig)

def run(treepath,outdir):
    tree,table=source_table(treepath)
    labels={r["tip_id"]:r["head_orientation"] for r in table}
    states=Counter(r["head_orientation"] for r in table)
    regions=Counter(r["geographic_panel"] for r in table)
    root_states,minsteps=fit_fitch(tree.root,labels)
    output={
        "version":"real_global45_japan38_plus_northamerica_europe_nuclear_source_traits_v1",
        "source_phenotype_methods":"exact source botanical authority by Japan38 JPN concept and five new Moreyra specimen taxon labels; original nine Siniscalchi codes only when that source exact matches",
        "source_tip_count":len(table),
        "n_source_U":states["U"],"n_source_D":states["D"],"n_unknown":states["?"],
        "region_samples":dict(regions),
        "source_scope":"Japan38+five predeclared NA/West Paleartic molecular samples",
        "Fitch_minimum_U_D_changes_on_real_new_tree":minsteps,
        "possible_root_states":sorted(root_states),
        "source_original_9trait_all_9_available_tip_count":sum(r["strict_original_9trait_source_same_study"]=="true" for r in table),
        "source_colour_fixed_or_polymorphic":dict(Counter(r["flower_colour_C_W_P_code"] for r in table)),
        "statements_not_licensed":["multiple independent adaptive convergences","calendar ages","palaeoclimate cause","statistically calibrated between-region replication","all 294 global capture tip placements","same-voucher head phenotypes"],
    }
    outdir.mkdir(parents=True,exist_ok=True)
    with (outdir/"real_nuclear45_source_traits_v1.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(table[0]))
        w.writeheader();w.writerows(table)
    plot(tree,table,outdir)
    (outdir/"real_nuclear45_trait_audit.json").write_text(json.dumps(output,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(output,indent=2,ensure_ascii=False))
    return output

def main():
    p=argparse.ArgumentParser();p.add_argument("--tree",type=Path,required=True);p.add_argument("--outdir",type=Path,required=True)
    a=p.parse_args();run(a.tree,a.outdir)
if __name__=="__main__":main()
