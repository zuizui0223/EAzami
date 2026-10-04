#!/usr/bin/env python3
"""Generate the new V10 Figures 3–5 from frozen EAzami evidence only."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT=Path(__file__).resolve().parents[1]; E=ROOT/"data"/"evidence"; CH=ROOT/"docs"/"chapter2"
DARK="#252525"; MID="#707070"; PALE="#F4F5F6"; BLUE="#4C78A8"; ORANGE="#F2A541"; GREEN="#5A9367"; PURPLE="#8A6FB0"; RED="#B05A5A"; TEAL="#4C9C9C"

def load(n): return json.loads((E/n).read_text(encoding="utf-8"))
def panel(ax,l): ax.text(-.12,1.05,l,transform=ax.transAxes,fontsize=11,fontweight="bold")
def sha(p):
 h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()
def save(fig,out,stem):
 out.mkdir(parents=True,exist_ok=True); png=out/f"{stem}.png"; pdf=out/f"{stem}.pdf"
 fig.savefig(png,dpi=600,bbox_inches="tight"); fig.savefig(pdf,bbox_inches="tight"); plt.close(fig)
 return {"png":{"path":str(png),"sha256":sha(png)},"pdf":{"path":str(pdf),"sha256":sha(pdf)}}

def fig3(out,meta):
 fig=plt.figure(figsize=(8.5,6.2)); gs=fig.add_gridspec(2,3,height_ratios=[1.65,.85],left=.06,right=.98,top=.90,bottom=.08,hspace=.30,wspace=.20)
 traits=[
 ("Orientation","Abiotic reproductive\nexposure / timing",BLUE,"Cremanthodium angle manipulation","56.3% nodding vs 15.7% erect\nachene set; RR ≈ 3.59","water + UV-B reduce pollen viability\nno angle preference by pollinators"),
 ("Phyllary posture","Mechanical antagonist\naccess",GREEN,"Centaurea spine removal","filled seeds −22%","illegitimate Lepidoptera deterrence lost\nlegitimate visit frequency not increased"),
 ("Stickiness","Arthropod-community filter\nunder trait cost",PURPLE,"Direct Cirsium experiments","benefit + null contexts","pollinators avoid traps; some enemies bypass\nants/aphids deterred; predators may use heads")]
 for i,(name,domain,col,study,effect,detail) in enumerate(traits):
  ax=fig.add_subplot(gs[0,i]); ax.axis("off")
  ax.add_patch(FancyBboxPatch((.04,.05),.92,.88,boxstyle="round,pad=0.025",facecolor=PALE,edgecolor=col,lw=1.4,transform=ax.transAxes))
  ax.text(.5,.84,name,transform=ax.transAxes,ha="center",fontsize=11,fontweight="bold",color=col)
  ax.text(.5,.68,domain,transform=ax.transAxes,ha="center",fontsize=8.2,fontweight="bold")
  ax.text(.5,.51,study,transform=ax.transAxes,ha="center",fontsize=7.1,color=MID)
  ax.text(.5,.37,effect,transform=ax.transAxes,ha="center",fontsize=8.4,fontweight="bold")
  ax.text(.5,.20,detail,transform=ax.transAxes,ha="center",fontsize=6.2,color=MID); panel(ax,chr(97+i))
 ax=fig.add_subplot(gs[1,:]); ax.axis("off"); re=meta["random_effects"]; lo,hi=re["ci95_response_ratio"]
 ax.add_patch(FancyBboxPatch((.04,.15),.92,.68,boxstyle="round,pad=0.025",facecolor="#F7F7F7",edgecolor=DARK,lw=1,transform=ax.transAxes))
 ax.text(.18,.57,"Cirsium reproductive\nherbivory",transform=ax.transAxes,ha="center",fontsize=9,fontweight="bold")
 ax.text(.48,.59,f'RR = {re["response_ratio"]:.3f}',transform=ax.transAxes,ha="center",fontsize=18,fontweight="bold",color=RED)
 ax.text(.48,.39,f"95% CI {lo:.3f}–{hi:.3f}",transform=ax.transAxes,ha="center",fontsize=7)
 ax.text(.75,.59,f'{100*re["ambient_seed_output_reduction_fraction"]:.1f}%',transform=ax.transAxes,ha="center",fontsize=18,fontweight="bold",color=RED)
 ax.text(.75,.39,"potential seed output lost\nunder ambient herbivory",transform=ax.transAxes,ha="center",fontsize=7)
 ax.text(.5,.20,"Fitness-pressure context only — not a pooled adaptive effect of the three focal traits",transform=ax.transAxes,ha="center",fontsize=6.5,color=MID); panel(ax,"d")
 fig.suptitle("Figure 3. Repeated capitulum components map to distinct candidate functional interfaces",fontsize=11.5)
 return save(fig,out,"figure3_v10_functional_interfaces")

def fig4(out,tr):
 fig,axs=plt.subplots(1,3,figsize=(8.5,3.9)); fig.subplots_adjust(left=.09,right=.98,top=.82,bottom=.20,wspace=.36)
 ax=axs[0]; ax.axis("off")
 ax.add_patch(FancyBboxPatch((.08,.12),.84,.76,boxstyle="round,pad=0.025",facecolor=PALE,edgecolor=DARK,lw=1,transform=ax.transAxes))
 ax.text(.5,.70,"Fixed U→D vector",transform=ax.transAxes,ha="center",fontsize=9,fontweight="bold")
 ax.text(.5,.50,"BIO15 ↑\nBIO1 ↓",transform=ax.transAxes,ha="center",fontsize=18,fontweight="bold",color=BLUE)
 ax.text(.5,.25,"post-result focused hypothesis",transform=ax.transAxes,ha="center",fontsize=6.5,color=MID); panel(ax,"a")
 ax=axs[1]; vals=[100*tr["n5_primary"]["exact_primary_rank"]["exact_fraction"],100*tr["n3_sensitivity"]["exact_primary_rank"]["exact_fraction"],100*(4/126)]
 labs=["n≥5\n16/792","n≥3\n19/1716","n≥10\n4/126"]; bars=ax.bar(range(3),vals,color=[BLUE,TEAL,PURPLE],width=.62); ax.axhline(5,color=RED,ls="--",lw=1)
 for b,v in zip(bars,vals): ax.text(b.get_x()+b.get_width()/2,v+.2,f"{v:.2f}%",ha="center",fontsize=6.5)
 ax.set_xticks(range(3),labs); ax.set_ylim(0,6.2); ax.set_ylabel("Exact finite-map rank (%)"); ax.set_title("Transition concordance"); panel(ax,"b")
 ax=axs[2]; ax.axis("off"); ax.add_patch(FancyBboxPatch((.07,.10),.86,.78,boxstyle="round,pad=0.025",facecolor=PALE,edgecolor=DARK,lw=1,transform=ax.transAxes))
 ax.text(.5,.72,"Bidirectional floor",transform=ax.transAxes,ha="center",fontsize=9,fontweight="bold")
 ax.text(.5,.57,"3/126 = 2.38%",transform=ax.transAxes,ha="center",fontsize=14,fontweight="bold",color=BLUE)
 ax.text(.5,.40,"direction survives\n9/9 taxon deletions",transform=ax.transAxes,ha="center",fontsize=8)
 ax.text(.5,.22,"also survives geography +\ninternal-edge stresses",transform=ax.transAxes,ha="center",fontsize=6.5,color=MID); panel(ax,"c")
 fig.suptitle("Figure 4. Orientation transitions track a present two-axis ecological regime",fontsize=11.5)
 return save(fig,out,"figure4_v10_orientation_transition_regime")

def fig5(out,h):
 fig,axs=plt.subplots(2,2,figsize=(8.4,6.4)); fig.subplots_adjust(left=.10,right=.98,top=.90,bottom=.10,hspace=.48,wspace=.35)
 ax=axs[0,0]; keys=["taiwan","ryukyu_corridor","southern_japan","east_asia_core_corridor"]; labs=["Taiwan","Ryukyu","S. Japan","E-Asia core"]; vals=[100*h["per_region"][k]["h4_match_fraction"] for k in keys]
 bars=ax.bar(range(4),vals,color=[MID,GREEN,BLUE,PURPLE],width=.65); ax.axhline(75,color=RED,ls="--",lw=1)
 for b,k,v in zip(bars,keys,vals): ax.text(b.get_x()+b.get_width()/2,v+2,f'{h["per_region"][k]["h4_match_count"]}/94',ha="center",fontsize=6.5)
 ax.set_xticks(range(4),labs,rotation=18,ha="right"); ax.set_ylim(0,83); ax.set_ylabel("Scenarios matching present regime (%)"); ax.set_title("No region approaches 75% persistence"); panel(ax,"a")
 ax=axs[0,1]; ax.axis("off"); ax.add_patch(FancyBboxPatch((.06,.08),.88,.82,boxstyle="round,pad=0.025",facecolor=PALE,edgecolor=DARK,lw=1,transform=ax.transAxes))
 ax.text(.5,.72,"Overall historical match",transform=ax.transAxes,ha="center",fontsize=9); ax.text(.5,.56,"99 / 376",transform=ax.transAxes,ha="center",fontsize=25,fontweight="bold",color=RED)
 ax.text(.5,.42,"26.3%",transform=ax.transAxes,ha="center",fontsize=10); ax.text(.5,.25,"only 6 / 94 chronologies\nmatch in all four regions",transform=ax.transAxes,ha="center",fontsize=7,color=MID); panel(ax,"b")
 ax=axs[1,0]; ax.axis("off"); ax.text(.5,.88,"Central 0.79–0.74 Ma",transform=ax.transAxes,ha="center",fontsize=9,fontweight="bold")
 ax.text(.26,.62,"Present U→D",transform=ax.transAxes,ha="center",fontsize=8); ax.text(.26,.43,"BIO15 ↑\nBIO1 ↓",transform=ax.transAxes,ha="center",fontsize=15,fontweight="bold",color=BLUE)
 ax.text(.74,.62,"Historical 4/4",transform=ax.transAxes,ha="center",fontsize=8); ax.text(.74,.43,"BIO15 ↓\nBIO1 ↓",transform=ax.transAxes,ha="center",fontsize=15,fontweight="bold",color=ORANGE)
 ax.text(.5,.16,"BIO15 is opposite in every region",transform=ax.transAxes,ha="center",fontsize=8,color=RED); panel(ax,"c")
 ax=axs[1,1]; ax.axis("off"); ax.add_patch(FancyBboxPatch((.04,.10),.92,.78,boxstyle="round,pad=0.025",facecolor="#F7F7F7",edgecolor=DARK,lw=1,transform=ax.transAxes))
 ax.text(.30,.62,"0 / 324",transform=ax.transAxes,ha="center",fontsize=20,fontweight="bold",color=RED); ax.text(.30,.43,"robust climate classes\n17 BIOCLIM × 6 contexts",transform=ax.transAxes,ha="center",fontsize=6.8)
 ax.text(.72,.62,"0 / 21",transform=ax.transAxes,ha="center",fontsize=20,fontweight="bold",color=RED); ax.text(.72,.43,"robust sea-level classes\n3 clades × 7 metrics",transform=ax.transAxes,ha="center",fontsize=6.8)
 ax.text(.5,.20,"No recurring coarse tested historical trigger",transform=ax.transAxes,ha="center",fontsize=7.5,fontweight="bold"); panel(ax,"d")
 fig.suptitle("Figure 5. Present ecological association does not identify the historical origin regime",fontsize=11.5)
 return save(fig,out,"figure5_v10_origin_trigger_falsification")

def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--out",type=Path,required=True); a=ap.parse_args()
 plt.rcParams.update({"font.family":"DejaVu Sans","font.size":8,"pdf.fonttype":42,"ps.fonttype":42})
 meta=load("cirsium_floral_herbivory_lnrr_meta_v2.json"); tr=load("chapter2_orientation_transition_regime_hypothesis_result_v1.json"); h=load("chapter2_orientation_historical_regime_persistence_result_v1.json")
 assert abs(meta["random_effects"]["response_ratio"]-2.673636515996)<1e-9
 assert tr["n5_primary"]["exact_primary_rank"]["count_at_least_observed"]==16 and tr["n3_sensitivity"]["exact_primary_rank"]["count_at_least_observed"]==19
 assert h["overall"]["h4_match_count"]==99 and h["overall"]["n_scenarios"]==376 and h["n_chronologies_4_of_4_regions"]==6
 outputs={"figure3":fig3(a.out,meta),"figure4":fig4(a.out,tr),"figure5":fig5(a.out,h)}
 (a.out/"v10_new_figures_manifest.json").write_text(json.dumps(outputs,indent=2)+"\n",encoding="utf-8"); print(json.dumps(outputs,indent=2))
if __name__=="__main__": main()
