#!/usr/bin/env python3
"""Reproduce Siniscalchi 2023 published nuclear tree mapped onto ALL NINE original traits.

The morphology key is copied literally from the author's R legend and numeric
CSV levels; no attempt to split white/pink/purple or invent actual events.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from Bio import Phylo

# Each state dict is in author's numeric factor order, verified against their
# original R legends at the immutable source commit.
TRAITS = {
    "CorollaThroat": (
        "Throat ratio",
        {"0": "lobes <2x throat", "1": "lobes 2x throat"},
        {"0": "#E1E7EB", "1": "#4C92B3"},
    ),
    "CorollaColor": (
        "Corolla colour",
        {"0": "red", "1": "reddish-purple",
         "2": "white/pink/purple (COMBINED)", "3": "yellow"},
        {"0": "#DC586A", "1": "#96519B", "2": "#D3C9D8", "3": "#D9C451"},
    ),
    "Duration": (
        "Life history",
        {"0": "perennial", "1": "biennial"},
        {"0": "#D6E5DC", "1": "#5E9A80"},
    ),
    "GlutinousRidge": (
        "Glutinous ridge",
        {"0": "absent", "1": "present"},
        {"0": "#DFE5E9", "1": "#608D75"},
    ),
    "Habit": (
        "Plant habit",
        {"0": "caulescent", "1": "acaulescent"},
        {"0": "#D5DBDF", "1": "#8A6CB1"},
    ),
    "HeadPosition": (
        "Head U/D",
        {"0": "U erect", "1": "D pendent"},
        {"0": "#328EB8", "1": "#EA8B36"},
    ),
    "InnerPhyllaryColor": (
        "Inner bracts",
        {"0": "green", "1": "purple", "2": "red", "3": "pink"},
        {"0": "#75A084", "1": "#7555A3", "2": "#D65C63", "3": "#DC94BC"},
    ),
    "OuterPhyllaryPosition": (
        "Outer bracts",
        {"0": "ascending", "1": "spreading", "2": "reflexed"},
        {"0": "#DBE1E5", "1": "#7F9BAF", "2": "#62618F"},
    ),
    "StyleBranchColor": (
        "Style branches",
        {"0": "red", "1": "reddish-purple",
         "2": "white/pink/purple (COMBINED)", "3": "yellow"},
        {"0": "#DB6069", "1": "#945AA5", "2": "#D6CCD8", "3": "#E5C451"},
    ),
}


def read_table(path: Path):
    with path.open(encoding="utf-8-sig",newline="") as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=63 or len({x["source_tip"] for x in rows})!=63:
        raise ValueError("source phenotypes are not 63 unique nuclear tips")
    return {x["source_tip"]:x for x in rows}


def fitch(node, data, char):
    if node.is_terminal():
        return {data[node.name][char]},0
    cur=None
    steps=0
    for child in node.clades:
        vals,n=fitch(child,data,char)
        steps+=n
        if cur is None:
            cur=vals
        else:
            common=cur&vals
            if common:
                cur=common
            else:
                cur=cur|vals
                steps+=1
    return cur,steps


def render(root: Path, out: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    data=read_table(root/"original_published_trait_states.csv")
    tree=Phylo.read(root/"siniscalchi_2023_north_american_nuclear_tree.nwk","newick")
    tips=tree.get_terminals()
    if len(tips)!=63 or {x.name for x in tips}!=set(data):
        raise ValueError("tree and nine-trait source correspondence failed")
    trait_summary=[]
    for char,(display,codes,palette) in TRAITS.items():
        values=[data[n.name][char] for n in tips]
        if any(v not in codes for v in values):
            raise ValueError("unknown published morphological state: "+char)
        states,steps=fitch(tree.root,data,char)
        trait_summary.append({
            "character":char,
            "name":display,
            "minimum_fitch_changes":steps,
            "state_counts":dict(sorted(Counter(values).items())),
            "original_author_legend":codes,
        })

    count=len(tips)
    y={tip:float(count-1-i) for i,tip in enumerate(tips)}
    x={n:float(tree.distance(n)) for n in tree.find_clades()}
    def Y(n):
        if n in y:return y[n]
        ys=[Y(c) for c in n.clades]
        y[n]=sum(ys)/len(ys)
        return y[n]
    Y(tree.root)
    x_max=max(x[z] for z in tips)
    base=x_max+.22
    step=.26
    squares=[base+i*step for i in range(len(TRAITS))]
    label_x=squares[-1]+.42

    fig,ax=plt.subplots(figsize=(19,18.2))
    fig.patch.set_facecolor("white")
    for n in tree.find_clades():
        if not n.clades:continue
        a=[y[c] for c in n.clades]
        ax.plot([x[n],x[n]],[min(a),max(a)],color="#96A0AA",lw=.57)
        for c in n.clades:
            ax.plot([x[n],x[c]],[y[c],y[c]],color="#96A0AA",lw=.57)
    for tip in tips:
        yy=y[tip]
        for j,(char,(_,codes,palette)) in enumerate(TRAITS.items()):
            v=data[tip.name][char]
            ax.add_patch(Rectangle((squares[j],yy-.32),.19,.64,facecolor=palette[v],
                                   edgecolor="white",linewidth=.25))
        ax.text(label_x,yy,tip.name.replace("_"," "),fontsize=6.8,color="#39434C",va="center")
    for j,(char,(name,codes,palette)) in enumerate(TRAITS.items()):
        ax.text(squares[j]+.08,count+.4,name,fontsize=7.3,color="#344152",rotation=64,va="bottom",ha="left")
    # Map category choices in a textual legend below the plotted phylogeny.
    desc=[]
    for t in trait_summary:
        shorthand=" | ".join(f"{k}: {val}" for k,val in t["original_author_legend"].items())
        desc.append(f"{t['name']}  [{t['minimum_fitch_changes']} min. steps]:  {shorthand}")
    ax.set_yticks([])
    ax.set_xlim(-.05,label_x+5.3)
    ax.set_ylim(-1.3,count+5.1)
    ax.set_xlabel("Published time-calibrated nuclear tree: root-to-tip branch lengths (source scale, Ma)",fontsize=9)
    ax.set_title("North American Cirsium | Nine floral, architectural and life-history traits on a real nuclear tree",
                 loc="left",fontsize=13,pad=24,weight="bold")
    ax.text(.003,1.006,"Siniscalchi et al. (2023), Compositae1061 • 63 actual source tips • categorical authors' trait codes; no invented global graft",
            fontsize=8,color="#64717D",transform=ax.transAxes,ha="left")
    ax.grid(axis="x",alpha=.13)
    for side in ax.spines:ax.spines[side].set_visible(False)
    fig.subplots_adjust(left=.04,right=.97,top=.94,bottom=.09)
    out.mkdir(parents=True,exist_ok=True)
    fig.savefig(out/"north_america_nuclear_ALL_NINE_traits.png",dpi=190,bbox_inches="tight")
    fig.savefig(out/"north_america_nuclear_ALL_NINE_traits.svg",bbox_inches="tight")
    plt.close(fig)

    text=[
        "# Siniscalchi et al. (2023) — original numerical morphology categories",
        "",
        "Tree: published dated North American Compositae1061 nuclear phylogeny (63 terminal labels).",
        "Each Fitch count is a minimum number of state changes on the fixed tree;",
        "not a fitted number of historical events or adaptive origins.",
        "",
    ]
    for t in trait_summary:
        text.append(
            f"- {t['name']} ({t['character']}): **{t['minimum_fitch_changes']} minimum changes**; "
            + "; ".join(f"{s} = {v} (n={t['state_counts'].get(s,0)})"
                        for s,v in t["original_author_legend"].items())
        )
    text.extend([
        "",
        "**CorollaColor code 2 contains white, pink and purple together**: do not infer",
        "the presence of white flowers or anthocyanin regain from that code.",
        "The molecular tree is independent North America, not the unavailable",
        "Moreyra et al. (2025) full-world 350-locus phylogeny.",
    ])
    (out/"nine_trait_original_legend_and_parsimony.md").write_text("\n".join(text)+"\n",encoding="utf-8")
    report={
        "version":"published_north_america_nuclear_nine_trait_parsimony_v1",
        "n_source_nuclear_tips":63,
        "source":"Siniscalchi et al. 2023 DOI 10.1086/724310",
        "n_original_morphological_characters":len(TRAITS),
        "characters":trait_summary,
        "nuclear_tree_scope":"independent North America",
        "inferred_world_nuclear_tree":False,
        "all_trait_category_transitions_are_historical_event_estimates":False,
    }
    (out/"nine_trait_phylogeny_parsimony_report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"n_tips":len(tips),"n_traits":len(TRAITS),
                      "min_changes":{r["character"]:r["minimum_fitch_changes"] for r in trait_summary}},
                      indent=2))
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-dir",type=Path,required=True)
    p.add_argument("--outdir",type=Path,required=True)
    args=p.parse_args()
    render(args.source_dir,args.outdir)


if __name__=="__main__":
    main()
