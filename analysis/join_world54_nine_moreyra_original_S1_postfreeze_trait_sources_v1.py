#!/usr/bin/env python3
"""Post-freeze phenotype crosswalk for the nine BLIND world54 S1 nuclear samples.

Original Moreyra nuclear sample/voucher accession is not flower morphology.
Only after the region-stratified molecular sample choices have been frozen
do we join exact Siniscalchi-2023 original nine author trait codes and the
existing Japan/NMNS head authority sources.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import urllib.request
from collections import Counter
from pathlib import Path

from select_real_world45_traitblind_moreyra_next9_v1 import build
from audit_global_nuclear_294_orientation_join_v3 import rebuild_panel_and_join

ORIGIN="c925d4af86160064448f794a9715f70b917a2786"
ORIGIN_SHA1="fa127f0587b676e6e004ea121424d26069586bcb"
URL=f"https://raw.githubusercontent.com/carol-siniscalchi/cirsium/{ORIGIN}/traits/traits.csv"
NINE=("CorollaThroat","CorollaColor","Duration","GlutinousRidge","Habit",
      "HeadPosition","InnerPhyllaryColor","OuterPhyllaryPosition","StyleBranchColor")


def original_nine_source():
    req=urllib.request.Request(URL,headers={"User-Agent":"EAzami-after-source-freeze-original-NA-nine-traits/1.0"})
    with urllib.request.urlopen(req,timeout=45) as h:
        raw=h.read()
    digest=hashlib.sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest()
    if digest!=ORIGIN_SHA1:
        raise ValueError("published source original nine-trait CSV changed")
    rows=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    return {r["Species"]:r for r in rows}


def run(outdir:Path):
    source,panel=build(3)
    if source["selection_used_head_colour_morphology_information"] is not False:
        raise ValueError("source molecular roster not morphology-blind")
    _,biosamples,_=rebuild_panel_and_join()
    sourceby={r["biosample"]:r for r in biosamples}
    author=original_nine_source()
    rows=[]
    for original in panel:
        rec=sourceby[original["biosample"]]
        if rec["analysis_taxon_label"]!=original["taxon_source_label"]:
            raise ValueError("trait join to different S1 nuclear sample")
        name=original["taxon_source_label"]
        siniscalchi=name.replace(" var. ","_").replace(" ","_")
        na=author.get(siniscalchi,{})
        stateNA={"0":"U","1":"D"}.get(na.get("HeadPosition",""),"")
        stateNM=rec["orientation_state_candidate"] if rec["orientation_state_candidate"] in {"U","D"} else ""
        if stateNA and stateNM and stateNA!=stateNM:
            chosen="?";reason="SOURCE_AUTHORITIES_DISAGREE"
        elif stateNA or stateNM:
            chosen=stateNA or stateNM
            reason="species_level_authority_only_NOT_same_sequenced_voucher"
        else:
            chosen="?";reason="no_explicit_original_species_source_U_D"
        rows.append({
            **original,
            "head_orientation_from_exact_botanical_source_after_freeze":chosen,
            "head_source_original_Siniscalchi_state":stateNA or "",
            "head_source_other_authority_state":stateNM or "",
            "head_state_admission_reason":reason,
            "head_source_botanical_URLS":rec.get("orientation_evidence_source_urls",""),
            "same_sequenced_individual_phenotyped":False,
            "independent_evolutionary_origin_counted":False,
            "has_all_nine_original_Siniscalchi_source_traits":bool(na),
            **{name:na.get(name,"") for name in NINE},
            "corolla_code_2_is_white_pink_purple_combined":na.get("CorollaColor","")=="2",
        })
    a=Counter(r["head_orientation_from_exact_botanical_source_after_freeze"] for r in rows)
    receipt={
        "version":"real_world54_traitblind_nine_original_S1_biosample_to_flower_head_crosswalk_v1",
        "source_selection_before_original_author_morphology":True,
        "original_traitblind_genetic_roster_seed":source["seed"],
        "n_new_public_nuclear_biosamples":len(rows),
        "source_author_Siniscalchi2023_Git_blob":ORIGIN_SHA1,
        "source_author_original_nine_traits_in_new_specimens":sum(x["has_all_nine_original_Siniscalchi_source_traits"] for x in rows),
        "n_original_nine_fields":len(NINE),
        "head_state_after_freeze":dict(a),
        "source_original_na_author_codes_head":{"0":"U","1":"D"},
        "same_actual_sequenced_voucher_morphology_measured":False,
        "new_molecular_tree_inferred_by_this_stage":False,
        "missing_head_states_imputed":False,
        "n_taxa_climatic_trait_model_ready":0,
        "scientific_caveat":"Do not infer independent origins, ancestral ages, white-flower losses, climate causes, or global representativeness from source-taxonomy categories. Cirsium kamtschaticum has another sequenced population in Japan38."
    }
    outdir.mkdir(parents=True,exist_ok=True)
    with (outdir/"nine_blind_Moreyra_S1_postfreeze_head_nine_traits.csv").open("w",encoding="utf-8",newline="") as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)
    (outdir/"postfreeze_botanical_source_audit.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(receipt,ensure_ascii=False,indent=2))
    return receipt

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--outdir",type=Path,required=True)
    a=p.parse_args()
    run(a.outdir)
if __name__=="__main__":
    main()
