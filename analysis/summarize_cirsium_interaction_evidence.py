#!/usr/bin/env python3
"""Summarize the bounded Cirsium interaction evidence seed."""
from __future__ import annotations
import argparse,csv,json
from collections import Counter
from pathlib import Path
from typing import Iterable

REQUIRED_COLUMNS=["evidence_id","study_id","year","taxon","region","interaction_domain","partner_guild","capitulum_module","design","trait_or_treatment","response_chain","fitness_endpoint","direction","quantitative_extraction_status","direct_capitulum_relevance","doctoral_use","doi","primary_source_title","claim_boundary"]
ALLOWED_INTERACTION_DOMAINS={"pollination","pollination_florivory_tradeoff","pre_dispersal_seed_predation","foliar_herbivory_context"}
ALLOWED_RELEVANCE={"direct","contextual"}
AIM2_TARGET_MODULES={
 "head_orientation":{"head_orientation"},
 "flower_colour":{"flower_colour"},
 "involucre_spine":{"involucre","phyllary","spine","involucre_spine"},
 "stickiness":{"stickiness"},
 "display_size":{"display_size"},
 "floral_scent":{"floral_scent"},
 "capitulum_size_position":{"capitulum_size","capitulum_position_and_size"},
}

def read_rows(path:Path)->list[dict[str,str]]:
    with path.open(encoding="utf-8",newline="") as h:
        r=csv.DictReader(h)
        if r.fieldnames!=REQUIRED_COLUMNS: raise ValueError("Unexpected columns")
        rows=list(r)
    if not rows: raise ValueError("Evidence seed is empty")
    return rows

def validate(rows:Iterable[dict[str,str]])->list[dict[str,str]]:
    rows=list(rows); ids=[r["evidence_id"] for r in rows]
    if len(ids)!=len(set(ids)): raise ValueError("evidence_id must be unique")
    for r in rows:
        if any(not r[k].strip() for k in REQUIRED_COLUMNS): raise ValueError(f"empty field: {r['evidence_id']}")
        if r["interaction_domain"] not in ALLOWED_INTERACTION_DOMAINS: raise ValueError("bad domain")
        if r["direct_capitulum_relevance"] not in ALLOWED_RELEVANCE: raise ValueError("bad relevance")
        if not 1900<=int(r["year"])<=2100: raise ValueError("bad year")
        if not r["taxon"].startswith("Cirsium "): raise ValueError("bad taxon")
        if not r["doi"].startswith("10."): raise ValueError("bad DOI")
    return rows

def summarize(rows:list[dict[str,str]])->dict:
    direct=[r for r in rows if r["direct_capitulum_relevance"]=="direct"]
    taxa=sorted({r["taxon"] for r in rows}); studies={r["study_id"] for r in rows}
    domains=Counter(r["interaction_domain"] for r in rows)
    domain_studies={d:len({r["study_id"] for r in rows if r["interaction_domain"]==d}) for d in sorted(domains)}
    modules=Counter(r["capitulum_module"] for r in direct)
    chains=Counter(r["response_chain"] for r in rows)
    fitness=[r for r in rows if r["fitness_endpoint"]!="none"]
    full=[r for r in direct if r["response_chain"]=="trait_to_interaction_and_fitness"]
    gate={}
    for target,aliases in AIM2_TARGET_MODULES.items():
        m=[r for r in direct if r["capitulum_module"] in aliases]
        gate[target]={"direct_rows":len(m),"independent_studies":len({r['study_id'] for r in m}),"fitness_rows":sum(r["fitness_endpoint"]!="none" for r in m),"manipulative_rows":sum("manipulation" in r["design"] for r in m)}
    return {
      "contract_version":"cirsium_interaction_evidence_summary_v1",
      "status_date":"2026-08-19",
      "scope":"bounded_primary_literature_seed_for_EAzami_Aim2_not_exhaustive_meta_analysis",
      "coverage":{"evidence_rows":len(rows),"independent_studies":len(studies),"taxa":len(taxa),"taxon_names":taxa,"direct_capitulum_rows":len(direct),"contextual_herbivory_rows":len(rows)-len(direct)},
      "interaction_domain_rows":dict(sorted(domains.items())),
      "interaction_domain_independent_studies":domain_studies,
      "direct_module_rows":dict(sorted(modules.items())),
      "response_chain_rows":dict(sorted(chains.items())),
      "fitness_coverage":{"rows_with_reproductive_or_demographic_fitness":len(fitness),"direct_trait_interaction_fitness_rows":len(full),"direct_trait_interaction_fitness_studies":len({r['study_id'] for r in full})},
      "aim2_module_gate":gate,
      "current_inference":[
        "Cirsium evidence supports capitulum display effects on pollinator behaviour and shows that floral signals can attract both mutualists and florivores.",
        "Cirsium palustre provides direct natural colour-morph pollination evidence, but replicated ancestry-controlled colour-to-effective-pollination-to-reproductive-fitness evidence remains absent from the bounded seed.",
        "Predispersal seed predators can strongly reduce achene or seed output; Japanese Cirsium purpuratum also shows that greater seasonal flower production can increase predation and counteract reproductive gains, supporting a mutualist-attraction versus antagonist-cost trade-off framing.",
        "The only recovered direct stickiness manipulation was null, so visible defensive-looking structures cannot be assigned a defence function without manipulation.",
        "No direct Cirsium head-orientation or phyllary/spine manipulation linked through interaction to reproductive fitness was recovered in the bounded targeted search."
      ],
      "field_experiment_priorities":[
        {"rank":1,"module":"head_orientation","reason":"No direct Cirsium orientation study was recovered in the bounded targeted search; it remains the cleanest primary Azami-trait functional gap."},
        {"rank":2,"module":"flower_colour","reason":"Cirsium palustre provides direct natural colour-morph pollination evidence, but ancestry-controlled colour-to-effective-pollination-to-fitness evidence remains unresolved; this also bridges Aim 3."},
        {"rank":3,"module":"involucre_spine","reason":"No direct phyllary/spine manipulation was recovered; test only after focal botanical validation and repeatable variation."},
        {"rank":4,"module":"stickiness","reason":"One direct manipulation was recovered and was null, so stickiness remains opportunistic/lower priority."}
      ],
      "effect_size_meta_analysis_gate":{"status":"not_yet_authorized","minimum_independent_studies_per_harmonized_outcome":5,"minimum_taxa_per_harmonized_outcome":3,"requirements":["same biological contrast and response scale","original-study deduplication","separate visitor abundance from effective pollination","separate florivory from pre-dispersal seed predation and foliar herbivory","retain null results and study-level sampling variance"],"current_use":"systematic evidence map and field-design prioritization; six seed-predation studies do not automatically authorize pooling because their traits, contrasts and outcomes remain heterogeneous."},
      "claim_boundary":"This bounded, source-backed seed identifies doctoral field gaps and trade-off priors. It is not an exhaustive literature census and does not estimate pooled effect sizes."
    }

def main():
    p=argparse.ArgumentParser(); p.add_argument("--input",type=Path,required=True); p.add_argument("--output",type=Path,required=True); a=p.parse_args()
    d=summarize(validate(read_rows(a.input))); a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
if __name__=="__main__": main()
