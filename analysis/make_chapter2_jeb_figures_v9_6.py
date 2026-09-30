#!/usr/bin/env python3
"""Generate the four active JEB V9.6 main figures from frozen evidence.

Figure 1: repeated change within the young radiation.
Figure 2: unequal evolutionary depth.
Figure 3: lack of robust shared transition localization.
Figure 4: ecological correspondence changes with scale/representation.

All displayed numerical claims are fail-closed against committed evidence.
Topology fractions and finite-map ranks are descriptive sensitivity/null ranks,
not biological replicate probabilities or conventional P values.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "data" / "evidence"
CH = ROOT / "docs" / "chapter2"
TIME = EVID / "chapter2_time_axis_compute"

DARK="#252525"; MID="#707070"; LIGHT="#D9DDE2"; PALE="#F4F5F6"
BLUE="#4C78A8"; ORANGE="#F2A541"; GREEN="#5A9367"; PURPLE="#8A6FB0"
RED="#B05A5A"; TEAL="#4C9C9C"

def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def load_csv(path: Path) -> list[dict[str,str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda:fh.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def setup_style():
    plt.rcParams.update({
        "font.family":"DejaVu Sans","font.size":8.0,"axes.titlesize":9.4,
        "axes.labelsize":8.0,"axes.edgecolor":DARK,"axes.linewidth":0.8,
        "xtick.color":DARK,"ytick.color":DARK,"text.color":DARK,
        "figure.facecolor":"white","axes.facecolor":"white","savefig.facecolor":"white",
        "pdf.fonttype":42,"ps.fonttype":42,
    })

def panel(ax, letter):
    ax.text(-0.10,1.04,letter,transform=ax.transAxes,fontsize=11,fontweight="bold",va="bottom")

def save(fig,out,stem,dpi=600):
    out.mkdir(parents=True,exist_ok=True)
    png=out/f"{stem}.png"; pdf=out/f"{stem}.pdf"
    fig.savefig(png,dpi=dpi,bbox_inches="tight",metadata={"Software":"EAzami"})
    fig.savefig(pdf,bbox_inches="tight",metadata={"Creator":"EAzami","Title":stem})
    plt.close(fig)
    if png.stat().st_size < 20000 or pdf.stat().st_size < 7000:
        raise RuntimeError(f"unexpectedly small output: {stem}")
    return {
        "png":{"path":str(png),"bytes":png.stat().st_size,"sha256":sha256(png)},
        "pdf":{"path":str(pdf),"bytes":pdf.stat().st_size,"sha256":sha256(pdf)},
    }

def known_orientation(x):
    return x not in {"unknown","source_conflict_index_downward_detail_erect"}

def known(x):
    return x!="unknown"

def ocode(x):
    if x=="downward_or_nodding": return "D",ORANGE
    if x in {"upward_or_erect","upward_or_ascending"}: return "U",BLUE
    if x.startswith("source_conflict_"): return "!",RED
    return "·",LIGHT

def pcode(x):
    if x=="appressed": return "App",GREEN
    if x in {"ascending","appressed_or_ascending"}: return "Asc",GREEN
    if x in {"spreading","spreading_or_recurved"}: return "Spr",PURPLE
    if x in {"recurved","ascending_or_recurved"}: return "Rec",PURPLE
    return "·",LIGHT

def scode(x):
    if x=="sticky": return "S",PURPLE
    if x=="nonsticky_or_nearly_nonsticky": return "N",GREEN
    return "·",LIGHT

def short(name):
    return name.replace("Cirsium ","C. ")

def parse_fraction(s):
    m=re.search(r"(\d+)\s*/\s*(\d+)",s)
    if not m: raise ValueError(s)
    a,b=map(int,m.groups())
    return a,b,100*a/b

def validate(hist,depth,cov,common,azami,tr,over,ml,held_contract,held_doc,seed,ext):
    rec=hist["recurrence_and_depth"]
    assert rec["orientation"]["minimum_changes_ml"]==6
    assert rec["orientation"]["minimum_changes_ufboot_range"]==[4,6]
    assert rec["phyllary_posture"]["minimum_changes"]==3
    assert rec["stickiness"]["minimum_changes"]==5
    assert rec["shared_transition_localization"].startswith("0/3")
    assert len(seed)==22 and len(ext)==2
    rows=seed+ext
    assert sum(known_orientation(r["orientation_state"]) for r in rows)==20
    assert sum(known(r["phyllary_posture"]) for r in rows)==10
    assert sum(known(r["stickiness_state"]) for r in rows)==13

    pair={(x["deeper_candidate"],x["shallower_candidate"]):x for x in depth["pairwise_results"]}
    assert pair[("phyllary","stickiness")]["fraction_prespecified_deeper_direction"]==1.0
    assert pair[("phyllary","orientation")]["fraction_prespecified_deeper_direction"]==0.993
    assert pair[("orientation","stickiness")]["fraction_prespecified_deeper_direction"]==0.905
    assert depth["complete_lower_bound_ordering"]["count"]==898
    assert cov["overall_classification"]=="unequal_depth_retained_against_matched_medians_but_strict_tail_overlap_remains"

    d=over["bootstrap_topology_sensitivity"]["pairwise_spearman_distributions"]
    assert over["bootstrap_topology_sensitivity"]["bootstrap_trees_total"]==1000
    assert d["orientation__stickiness"]["fraction_positive"]==0.009
    assert d["phyllary__stickiness"]["q05"]<0
    assert ml["pairwise_overlap"]["orientation__stickiness"]["spearman_transition_excess_over_branch_prior"]>0

    assert common["primary"]["orientation"]["n_taxa"]==17
    assert common["primary"]["phyllary"]["n_taxa"]==4
    assert common["primary"]["stickiness"]["n_taxa"]==12
    assert common["multiplicity"]["supported_rows_q_lt_0_05"]==0

    assert azami["decision"]=="NOT_ELIGIBLE_AS_PROSPECTIVE_P3"
    assert azami["azami_existing_within_taxon"]["BIO1"]["q_fdr"]<0.05
    assert azami["azami_existing_within_taxon"]["BIO15"]["q_fdr"]>0.05
    assert azami["azami_existing_among_taxon"]["BIO12"]["beta_std"]>0.3
    assert tr["n5_primary"]["exact_primary_rank"]["count_at_least_observed"]==16
    assert tr["n5_primary"]["exact_primary_rank"]["n_maps"]==792
    assert tr["n3_sensitivity"]["exact_primary_rank"]["count_at_least_observed"]==19
    assert held_contract["n_candidates"]==13
    assert held_contract["state_counts_before_occurrence"]=={"downward_or_nodding":3,"upward_or_erect":10}
    assert "downward/nodding: **0 taxa**" in held_doc
    assert "upward/erect: **1 taxon**" in held_doc
    assert "Cirsium vulgare" in held_doc and "16 deterministic 0.1-degree thinned records" in held_doc
    assert "BIO1 and BIO15 are **not extracted**" in held_doc

def figure1(out,hist,seed,ext):
    rows=sorted(seed+ext,key=lambda r:int(r["paper_japan_member_id"].split("_")[1]))
    rec=hist["recurrence_and_depth"]
    fig=plt.figure(figsize=(8.1,8.25))
    gs=fig.add_gridspec(2,2,height_ratios=[0.70,2.30],width_ratios=[1.05,1.35],
                        left=.22,right=.98,top=.94,bottom=.07,hspace=.32,wspace=.30)
    ax=fig.add_subplot(gs[0,0])
    ax.barh([0],[36],height=.5,color=BLUE)
    ax.barh([0],[2],left=[36],height=.5,color=LIGHT,edgecolor=MID)
    ax.text(18,0,"36",ha="center",va="center",color="white",fontsize=18,fontweight="bold")
    ax.text(37,0,"2",ha="center",va="center",fontsize=10,fontweight="bold")
    ax.set_xlim(0,38); ax.set_yticks([]); ax.set_xlabel("Japanese taxon concepts")
    ax.set_title("One dominant young radiation")
    ax.text(.5,-.32,"36/38 sampled concepts in dominant radiation",transform=ax.transAxes,ha="center",fontsize=7,color=MID)
    panel(ax,"a")

    ax=fig.add_subplot(gs[0,1])
    traits=["Orientation","Phyllary","Stickiness"]; y=np.arange(3)[::-1]
    vals=[(4,6,5,20),(3,3,3,10),(5,5,5,13)]
    cols=[BLUE,GREEN,PURPLE]
    for yy,(lo,hi,med,n),col in zip(y,vals,cols):
        ax.hlines(yy,lo,hi,color=col,lw=6)
        ax.plot(med,yy,"o",mfc="white",mec=col,mew=1.4,ms=6)
        ax.text(6.16,yy,f"n={n}",va="center",fontsize=7,color=MID)
    ax.set_yticks(y,traits); ax.set_xlim(2.6,6.8)
    ax.set_xlabel("Minimum state changes across topology ensemble")
    ax.set_title("Every component repeatedly changes")
    ax.grid(axis="x",color=LIGHT,lw=.6)
    panel(ax,"b")

    ax=fig.add_subplot(gs[1,:])
    ax.set_xlim(-.5,2.5); ax.set_ylim(len(rows)-.5,-.5)
    ax.set_xticks([0,1,2],["Orientation","Phyllary","Stickiness"]); ax.xaxis.tick_top()
    labels=[]
    for i,r in enumerate(rows):
        cells=[ocode(r["orientation_state"]),pcode(r["phyllary_posture"]),scode(r["stickiness_state"])]
        for j,(txt,col) in enumerate(cells):
            ax.add_patch(Rectangle((j-.46,i-.42),.92,.84,facecolor=col,alpha=.80,edgecolor="white",lw=.6))
            ax.text(j,i,txt,ha="center",va="center",fontsize=5.8,
                    color="white" if col not in {LIGHT,GREEN} else DARK,
                    fontweight="bold" if txt!="·" else "normal")
        labels.append(f"{r['paper_japan_member_id'].replace('JPN_','J')}: {short(r['paper_taxon_concept'])}")
    ax.set_yticks(np.arange(len(rows)),labels,fontsize=5.6)
    ax.set_xticks(np.arange(-.5,3,1),minor=True); ax.set_yticks(np.arange(-.5,len(rows),1),minor=True)
    ax.grid(which="minor",color="white",lw=.6); ax.tick_params(which="minor",bottom=False,left=False)
    ax.set_title("Authority-backed component states (missing/conflict retained)",pad=25)
    ax.text(0,-.045,"U/D = upward/downward; App/Asc/Spr/Rec = phyllary posture; S/N = sticky/nonsticky; · = unknown; ! = source conflict",
            transform=ax.transAxes,fontsize=6.2,color=MID)
    panel(ax,"c")
    fig.suptitle("Figure 1. Repeated component differentiation occurs within one young radiation",fontsize=11.5)
    return save(fig,out,"figure1_v9_6_repeated_components")

def figure2(out,hist,depth,cov):
    rec=hist["recurrence_and_depth"]
    fig,axs=plt.subplots(2,2,figsize=(8.0,6.7))
    fig.subplots_adjust(left=.12,right=.98,top=.90,bottom=.10,hspace=.48,wspace=.42)
    traits=["Orientation","Phyllary","Stickiness"]; cols=[BLUE,GREEN,PURPLE]; y=np.arange(3)[::-1]
    env=[rec["orientation"]["relative_depth_median_envelope"],
         rec["phyllary_posture"]["relative_depth_median_envelope"],
         rec["stickiness"]["relative_depth_median_envelope"]]
    ax=axs[0,0]
    for yy,(lo,hi),col in zip(y,env,cols):
        ax.hlines(yy,lo,hi,color=col,lw=6); ax.plot([lo,hi],[yy,yy],"|",color=DARK,ms=11)
        ax.text((lo+hi)/2,yy+.17,f"{lo:.3f}–{hi:.3f}",ha="center",fontsize=6.7)
    ax.set_yticks(y,traits); ax.set_xlim(.65,1.02); ax.set_ylim(-.35,2.4)
    ax.set_xlabel("Relative lineage depth (1 = terminal)")
    ax.set_title("Different admissible depth envelopes"); ax.grid(axis="x",color=LIGHT,lw=.6)
    panel(ax,"a")

    ax=axs[0,1]
    labels=["P < S","P < O","O < S","P < O < S"]
    vals=np.array([1.0,.993,.905,.898])*100
    bars=ax.bar(range(4),vals,color=[GREEN,GREEN,BLUE,DARK],width=.64)
    for b,v in zip(bars,vals): ax.text(b.get_x()+b.get_width()/2,v+1.2,f"{v:.1f}%",ha="center",fontsize=7)
    ax.set_xticks(range(4),labels); ax.set_ylim(0,106); ax.set_ylabel("Topology realizations (%)")
    ax.set_title("Paired ordering on the same 1,000 topologies")
    ax.text(.5,-.22,"P=phyllary, O=orientation, S=stickiness",transform=ax.transAxes,ha="center",fontsize=6.4,color=MID)
    panel(ax,"b")

    ax=axs[1,0]
    cm={x["comparison"]:x for x in cov["comparison_results"]}
    labs=["P<O","P<S (5/5)","P<S (6/4)"]
    med=[cm["phyllary_lt_orientation_median"]["fraction"]*100,
         cm["phyllary_lt_stickiness_5_5_median"]["fraction"]*100,
         cm["phyllary_lt_stickiness_6_4_median"]["fraction"]*100]
    tail=[cm["phyllary_lt_orientation_q05"]["fraction"]*100,
          cm["phyllary_lt_stickiness_5_5_q05"]["fraction"]*100,
          cm["phyllary_lt_stickiness_6_4_q05"]["fraction"]*100]
    yy=np.arange(3)[::-1]; h=.28
    ax.barh(yy+h/2,med,height=h,color=BLUE,label="matched median")
    ax.barh(yy-h/2,tail,height=h,color=MID,label="strict q05")
    ax.set_yticks(yy,labs); ax.set_xlim(0,105); ax.set_xlabel("Selected topology realizations (%)")
    ax.set_title("Coverage matching preserves the center, not tails"); ax.legend(frameon=False,fontsize=6.5)
    ax.grid(axis="x",color=LIGHT,lw=.6); panel(ax,"c")

    ax=axs[1,1]; ax.axis("off")
    ax.add_patch(FancyBboxPatch((.06,.16),.88,.70,boxstyle="round,pad=0.025",facecolor=PALE,edgecolor=DARK,lw=.9,transform=ax.transAxes))
    ax.text(.5,.67,"Unequal evolutionary depth",transform=ax.transAxes,ha="center",fontsize=12,fontweight="bold")
    ax.text(.5,.50,"is robust in central ordering",transform=ax.transAxes,ha="center",fontsize=10,color=BLUE)
    ax.text(.5,.34,"but strict tails overlap after coverage matching",transform=ax.transAxes,ha="center",fontsize=8,color=MID)
    ax.text(.5,.20,"Topology coordinate ≠ calendar time ≠ evolutionary rate",transform=ax.transAxes,ha="center",fontsize=6.7,color=RED)
    panel(ax,"d")
    fig.suptitle("Figure 2. Repeated histories occupy unequal evolutionary depths",fontsize=11.5)
    return save(fig,out,"figure2_v9_6_unequal_depth")

def figure3(out,over,ml):
    dist=over["bootstrap_topology_sensitivity"]["pairwise_spearman_distributions"]
    mlp=ml["pairwise_overlap"]
    keys=["orientation__phyllary","orientation__stickiness","phyllary__stickiness"]
    labels=["Orientation × phyllary","Orientation × stickiness","Phyllary × stickiness"]
    fig=plt.figure(figsize=(8.0,4.7))
    gs=fig.add_gridspec(1,2,width_ratios=[2.15,1.0],left=.13,right=.98,top=.86,bottom=.17,wspace=.30)
    ax=fig.add_subplot(gs[0,0]); yy=np.arange(3)[::-1]
    for y,k,col in zip(yy,keys,[BLUE,ORANGE,GREEN]):
        d=dist[k]; q=[d["q05"],d["median"],d["q95"]]
        ax.hlines(y,q[0],q[2],color=col,lw=5,alpha=.72)
        ax.plot(q[1],y,"o",mfc="white",mec=col,mew=1.5,ms=7,label=None)
        mlv=mlp[k]["spearman_transition_excess_over_branch_prior"]
        ax.plot(mlv,y,"D",color=DARK,ms=5)
        ax.text(q[2]+.02,y,f"{100*d['fraction_positive']:.1f}% >0",va="center",fontsize=6.7,color=MID)
    ax.axvline(0,color=DARK,lw=.8,ls="--")
    ax.set_yticks(yy,labels); ax.set_xlim(-.48,.48)
    ax.set_xlabel("Transition-localization association (Spearman ρ)")
    ax.set_title("Branch-length and topology-only diagnostics disagree")
    ax.text(.5,-.18,"line=q05–q95 equal-branch topology sensitivity; ○ median; ◆ ML excess-over-prior",transform=ax.transAxes,ha="center",fontsize=6.3,color=MID)
    panel(ax,"a")

    ax=fig.add_subplot(gs[0,1]); ax.axis("off")
    ax.add_patch(FancyBboxPatch((.08,.20),.84,.63,boxstyle="round,pad=0.03",facecolor=PALE,edgecolor=DARK,lw=1,transform=ax.transAxes))
    ax.text(.5,.64,"0 / 3",transform=ax.transAxes,ha="center",fontsize=28,fontweight="bold",color=RED)
    ax.text(.5,.48,"trait pairs pass the robust\nshared-localization rule",transform=ax.transAxes,ha="center",fontsize=9)
    ax.text(.5,.30,"No one synchronized\nwhole-capitulum history required",transform=ax.transAxes,ha="center",fontsize=7.5,color=MID)
    panel(ax,"b")
    fig.suptitle("Figure 3. Component changes do not repeatedly synchronize on the same branches",fontsize=11.5)
    return save(fig,out,"figure3_v9_6_shared_localization")

def figure4(out,common,azami,tr,held_contract,held_doc):
    fig,axs=plt.subplots(2,2,figsize=(8.4,7.0))
    fig.subplots_adjust(left=.11,right=.98,top=.91,bottom=.10,hspace=.50,wspace=.38)

    ax=axs[0,0]
    traits=["Orientation","Phyllary","Stickiness"]
    ranks=[parse_fraction(common["primary"]["orientation"]["omnibus_nine_environment_rank"])[2],
           parse_fraction(common["primary"]["phyllary"]["omnibus_nine_environment_rank"])[2],
           parse_fraction(common["primary"]["stickiness"]["omnibus_nine_environment_rank"])[2]]
    bars=ax.bar(range(3),ranks,color=[BLUE,LIGHT,PURPLE],edgecolor=[BLUE,MID,PURPLE],width=.62)
    ns=[17,4,12]; states=["5D/12U","1 App/3 Asc","6 sticky/6 non"]
    for b,v,n,st in zip(bars,ranks,ns,states):
        ax.text(b.get_x()+b.get_width()/2,v+3,f"{v:.1f}%\nn={n}; {st}",ha="center",fontsize=6.4)
    ax.set_xticks(range(3),traits); ax.set_ylim(0,112)
    ax.set_ylabel("Finite-map omnibus rank (%)")
    ax.set_title("Common9: no shared static abiotic syndrome")
    ax.text(.5,-.20,"Lower = more exceptional; phyllary is state-replication limited",transform=ax.transAxes,ha="center",fontsize=6.2,color=MID)
    panel(ax,"a")

    ax=axs[0,1]; ax.axis("off")
    ax.set_xlim(0,3); ax.set_ylim(0,3)
    cols=["BIO12","BIO1","BIO15"]; rows=["Among taxa\n(Azami image)","Within taxa\n(Azami image)","Transitions\n(EAzami states)"]
    for j,c in enumerate(cols): ax.text(j+.5,2.83,c,ha="center",fontweight="bold",fontsize=8)
    for i,r in enumerate(rows): ax.text(-.05,2.35-i,r,ha="right",va="center",fontsize=7)
    cells={
        (0,0):("+","β=+0.304","supported",BLUE),
        (0,1):("·","different predictor","n/a",LIGHT),
        (0,2):("·","different predictor","n/a",LIGHT),
        (1,0):("≈0","q=.823","unsupported",LIGHT),
        (1,1):("+","β=+0.017; q=.048","warmer → more down",BLUE),
        (1,2):("−","β=−0.0076; q=.183","not FDR-supported",ORANGE),
        (2,0):("·","not focal","n/a",LIGHT),
        (2,1):("−","D associated lower BIO1","opposite within-taxon",ORANGE),
        (2,2):("+","D associated higher BIO15","transition vector",BLUE),
    }
    for i in range(3):
        for j in range(3):
            sym,line1,line2,col=cells[(i,j)]
            ax.add_patch(Rectangle((j+.08,1.98-i),.84,.70,facecolor=col,alpha=.18 if col!=LIGHT else .55,edgecolor=col if col!=LIGHT else MID,lw=.8))
            ax.text(j+.5,2.49-i,sym,ha="center",va="center",fontsize=14,fontweight="bold",color=DARK)
            ax.text(j+.5,2.27-i,line1,ha="center",va="center",fontsize=5.8)
            ax.text(j+.5,2.10-i,line2,ha="center",va="center",fontsize=5.3,color=MID)
    ax.set_title("Orientation–environment mapping changes with scale",pad=9)
    panel(ax,"b")

    ax=axs[1,0]
    ranks2=[100*tr["n5_primary"]["exact_primary_rank"]["exact_fraction"],
            100*tr["n3_sensitivity"]["exact_primary_rank"]["exact_fraction"],
            100*(4/126)]
    labs=["n≥5\n12 taxa","n≥3\n13 taxa","n≥10\n9 taxa"]
    bars=ax.bar(range(3),ranks2,color=[BLUE,TEAL,PURPLE],width=.62)
    ax.axhline(5,color=RED,ls="--",lw=1)
    for b,v,raw in zip(bars,ranks2,["16/792","19/1716","4/126"]):
        ax.text(b.get_x()+b.get_width()/2,v+.25,f"{raw}\n{v:.2f}%",ha="center",fontsize=6.7)
    ax.set_xticks(range(3),labs); ax.set_ylim(0,6.3)
    ax.set_ylabel("Exact finite-map rank (%)")
    ax.set_title("Transition-level BIO15↑ + BIO1↓ is exceptional")
    ax.text(.02,.95,"5% frozen decision boundary",transform=ax.transAxes,color=RED,fontsize=6.3,va="top")
    panel(ax,"c")

    ax=axs[1,1]; ax.axis("off")
    ax.set_xlim(0,1); ax.set_ylim(0,1)
    ax.text(.05,.82,"External confirmation gate",fontsize=9.4,fontweight="bold")
    boxes=[(.05,.57,.25,.16,"13 taxa\n3 D / 10 U"),
           (.39,.57,.25,.16,"strict GBIF QC\n≤10 km; n≥3"),
           (.73,.57,.22,.16,"1 taxon\n0 D / 1 U")]
    for x,y,w,h,txt in boxes:
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.02",facecolor=PALE,edgecolor=DARK,lw=.8))
        ax.text(x+w/2,y+h/2,txt,ha="center",va="center",fontsize=6.7)
    ax.annotate("",xy=(.38,.65),xytext=(.31,.65),arrowprops=dict(arrowstyle="->",color=MID))
    ax.annotate("",xy=(.72,.65),xytext=(.65,.65),arrowprops=dict(arrowstyle="->",color=MID))
    ax.text(.84,.43,"C. vulgare\nU; 16 thinned",ha="center",fontsize=6.6,color=MID)
    ax.add_patch(FancyBboxPatch((.13,.12),.74,.19,boxstyle="round,pad=0.025",facecolor="#FFF6F2",edgecolor=RED,lw=1.0))
    ax.text(.50,.235,"NOT EVALUABLE",ha="center",fontsize=12,fontweight="bold",color=RED)
    ax.text(.50,.165,"BIO1 / BIO15 never opened",ha="center",fontsize=7.4)
    panel(ax,"d")
    fig.suptitle("Figure 4. Orientation ecology is scale- and representation-dependent",fontsize=11.5)
    return save(fig,out,"figure4_v9_6_scale_conditioned_ecology")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,default=CH/"figures_v9_6")
    a=ap.parse_args()
    setup_style()
    hist=load_json(EVID/"chapter2_historical_differentiation_final_summary_v1.json")
    depth=load_json(EVID/"chapter2_depth_ordering_robustness_result_v1.json")
    cov=load_json(EVID/"chapter2_depth_coverage_matched_sensitivity_result_v1.json")
    common=load_json(EVID/"chapter2_three_trait_common9_result_v1.json")
    azami=load_json(EVID/"azami_orientation_crossscale_validation_audit_v1.json")
    tr=load_json(EVID/"chapter2_orientation_transition_regime_hypothesis_result_v1.json")
    over=load_json(TIME/"japan38_latest_module_overlap_topology_sensitivity_v2.json")
    ml=load_json(TIME/"japan38_latest_module_transition_overlap_v2.json")
    held_contract=load_json(EVID/"heldout_orientation_occurrence_gate_v2_contract.json")
    held_doc=(CH/"HELDOUT_ORIENTATION_OCCURRENCE_GATE_V2_RESULT.md").read_text(encoding="utf-8")
    seed=load_csv(EVID/"japan38_nmns_capitulum_trait_seed_v1.csv")
    ext=load_csv(EVID/"japan38_nmns_capitulum_trait_seed_extension_v2.csv")
    validate(hist,depth,cov,common,azami,tr,over,ml,held_contract,held_doc,seed,ext)

    outputs={
        "figure1":figure1(a.out,hist,seed,ext),
        "figure2":figure2(a.out,hist,depth,cov),
        "figure3":figure3(a.out,over,ml),
        "figure4":figure4(a.out,common,azami,tr,held_contract,held_doc),
    }
    manifest={
        "version":"chapter2_jeb_v9_6_main_figures_manifest_v1",
        "status_date":"2026-09-30",
        "manuscript":"docs/chapter2/MANUSCRIPT_JEB_V9_6_SCALE_CONDITIONED_ECOLOGY.md",
        "outputs":outputs,
        "claim_boundaries":[
            "minimum changes are lower bounds, not independent origins",
            "relative lineage depth is not calendar time or rate",
            "topology fractions are sensitivity summaries, not probabilities",
            "finite-map fractions are exact conditional ranks, not biological-replicate P values",
            "Azami cross-scale evidence is not prospective P3",
            "held-out V2 external confirmation is not evaluable and environment remained unopened",
            "no figure establishes climatic causation, selection or adaptation",
        ]
    }
    (a.out/"v9_6_main_figure_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(manifest,indent=2))
if __name__=="__main__":
    main()
