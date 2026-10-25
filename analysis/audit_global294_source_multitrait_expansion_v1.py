#!/usr/bin/env python3
"""Actual worldwide 294 nuclear BioSample × nine independent floristic trait census.

Original Moreyra/Chang sampling ledger: 294 biological individuals / 295 SRA
runs / 270 source names; those are NOT an inferred 294-tip global phylogeny.
Join published Siniscalchi 2023 original nine categorical source species by
EXACT original botanical concept text only, and existing separately sourced
strict U/D evidence. Keep all unjoined source names and voucher/locality/runs.

Never treat NA botanical categorical morphology on a sequenced voucher as
measured; trait code 2 means white+pink+purple MIXED, not fixed white.
No climate extracted outside original NA author source; Moreyra S1 alone
does not supply images of biological phenotypes or global BIO18 niches.
"""
from __future__ import annotations

import argparse,csv,json,re
from collections import Counter,defaultdict
from pathlib import Path

from audit_global_nuclear_294_orientation_join_v3 import rebuild_panel_and_join
from run_siniscalchi_2023_real_nuclear_traits_v1 import acquire
from select_real_world45_traitblind_moreyra_next9_v1 import region

NINE=("CorollaThroat","CorollaColor","Duration","GlutinousRidge",
      "Habit","HeadPosition","InnerPhyllaryColor","OuterPhyllaryPosition",
      "StyleBranchColor")


def source_region(row):
    location=" ".join((row["location"],row["region"])).casefold()
    if any(x in location for x in ("japan","okinawa","ryukyu")):
        return "Japan_Ryukyu"
    known=region(location)
    return known or "Other_or_unresolved"


def source_exact_original_label(source):
    # One-to-one original published botanical *taxon name* equality only:
    # "Cirsium fontinale var. campylon" is NOT automatically synonymized to
    # "Cirsium_fontinale_campylon" or another species concept.
    return str(source).strip().replace(" ","_")


def run(assets:Path,outdir:Path):
    receipt,source_rows,taxa=rebuild_panel_and_join()
    if len(source_rows)!=294 or len(taxa)!=270 or receipt["n_public_run_accessions"]!=295:
        raise ValueError("EAzami actual global molecular sampling source roster changed")
    assets_=acquire(assets)
    with assets_["traits/traits.csv"].open(encoding="utf-8-sig",newline="") as h:
        orig=list(csv.DictReader(h))
    index={r["Species"]:r for r in orig}
    if len(index)!=len(orig) or len(index)!=63:
        raise ValueError("original 63 nuclear-tip Siniscalchi morphological table unexpected")
    if len(NINE)!=9 or any(any(c not in r for c in NINE) for r in orig):
        raise ValueError("original nine-category published author morphology missing")
    taxon_counts=Counter(r["analysis_taxon_label"] for r in source_rows)
    result=[]
    bytaxon=defaultdict(list)
    for r in source_rows:
        original_label=r["analysis_taxon_label"]
        tid=source_exact_original_label(original_label)
        matched=index.get(tid)
        if matched is not None and matched["Species"]!=tid:
            raise ValueError("non-exact botanical name unexpectedly admitted")
        ext_head={"0":"U","1":"D"}.get(matched["HeadPosition"],"") if matched else ""
        earlier_head=r["orientation_state_candidate"] if r["orientation_state_candidate"] in {"U","D"} else ""
        mismatch=bool(ext_head and earlier_head and ext_head!=earlier_head)
        name_review=r["name_review_required"]!="false"
        admitted=""
        if name_review or mismatch:
            gate="hold_original_nuclear_taxon_name_or_morphological_conflict"
        elif ext_head:
            admitted=ext_head
            gate="published_original_NorthAmerican_nine_trait_source_taxon_only"
        elif earlier_head:
            admitted=earlier_head
            gate="published_other_botanical_U_D_source_taxon_only"
        else:
            gate="no_independent_source_trait"
        out={
            "panel_id":r["panel_id"],
            "biosample":r["biosample"],
            "study":r["source_studies"],
            "assay":r["assay"],
            "run_accessions":r["run_accessions"],
            "source_taxon_label":original_label,
            "source_locality_text":r["location"],
            "source_geographic_bucket":source_region(r),
            "voucher_original":r["voucher"],
            "original_nuclear_name_review_hold":str(name_review).lower(),
            "published_Siniscalchi_exact_nine_character_match":str(bool(matched)).lower(),
            "original_independent_9trait_author_reference_Git_commit":"c925d4af86160064448f794a9715f70b917a2786" if matched else "",
            "original_botanical_nine_trait_taxon_code":tid if matched else "",
            "existing_strict_U_D_evidence_candidate":earlier_head,
            "new_author_head_U_D":ext_head,
            "conflicting_original_botanical_head_source":str(mismatch).lower(),
            "admitted_U_D_source_taxon_level":admitted,
            "head_source_status":gate,
            "colour_code_2_means_white_pink_purple_not_fixed_white":str(bool(matched and matched["CorollaColor"]=="2")).lower(),
            "same_sequenced_voucher_head_or_colour_measured":"false",
            "source_BIO18_climate_for_this_molecular_biosample":"NOT_EXTRACTED",
            "n_same_taxon_biosamples":taxon_counts[original_label],
            **{trait:(matched[trait] if matched else "") for trait in NINE},
        }
        result.append(out)
        bytaxon[original_label].append(out)
    if len(result)!=294 or len({r["biosample"] for r in result})!=294:
        raise ValueError("molecular BioSamples repeated in worldwide proposed expansion")
    taxa_rows=[]
    for name,rows in sorted(bytaxon.items()):
        unique_states=set(r["admitted_U_D_source_taxon_level"] for r in rows)
        if len(unique_states)>1:
            raise ValueError("duplicated source molecular concept got inconsistent categorical trait evidence")
        original_match=any(r["published_Siniscalchi_exact_nine_character_match"]=="true" for r in rows)
        taxa_rows.append({
            "source_taxon_label":name,
            "n_genetically_sampled_biosamples":len(rows),
            "n_original_public_run_accessions":len({run for r in rows for run in r["run_accessions"].split("|") if run}),
            "geographic_buckets":"|".join(sorted({r["source_geographic_bucket"] for r in rows})),
            "n_nuclear_assays":len({r["assay"] for r in rows}),
            "nine_original_Siniscalchi_morphological_variables_present":str(original_match).lower(),
            "admitted_source_U_D_taxon_only":next(iter(unique_states)),
            "any_taxonomic_or_morphology_review_hold":str(any(r["head_source_status"].startswith("hold_") for r in rows)).lower(),
            "source_sequences_have_genomewide_tree_inferred":"false",
            "same_sequenced_voucher_phenotype_measurement_verified":"false",
            "multiple_source_biosamples_equal_independent_trait_origins":"false",
        })
    if len(taxa_rows)!=270:
        raise ValueError("source taxonomic concept ledger was not preserved")
    def count_match(col):
        return sum(x["published_Siniscalchi_exact_nine_character_match"]=="true" for x in result) if col=="bio" else None
    tally=Counter(x["source_geographic_bucket"] for x in result)
    state=Counter(x["admitted_U_D_source_taxon_level"] or "?" for x in result)
    states_taxa=Counter(x["admitted_source_U_D_taxon_only"] or "?" for x in taxa_rows)
    matched_nine=sum(x["nine_original_Siniscalchi_morphological_variables_present"]=="true" for x in taxa_rows)
    count_all9=sum(x["published_Siniscalchi_exact_nine_character_match"]=="true" for x in result)
    source_taxa=[x for x in taxa_rows if x["nine_original_Siniscalchi_morphological_variables_present"]=="true"]
    matched_genomes=[
        x["source_taxon_label"] for x in source_taxa
        if x["admitted_source_U_D_taxon_only"] in {"U","D"}
    ]
    if count_all9==0:
        raise ValueError("unexpected no exact original NA source 9-trait taxa across worldwide genetic roster")
    report={
        "version":"worldwide_294_270taxon_head_colour_phyllary_glutinous_source_exact_9trait_coverage_v1",
        "molecular_S1_current_source_BioSamples":294,
        "molecular_S1_current_source_SRRs":295,
        "molecular_S1_source_taxon_labels":270,
        "source_region_counts":dict(sorted(tally.items())),
        "molecular_biosamples_with_all_9_original_Siniscalchi_categories":count_all9,
        "unique_294source_taxon_labels_with_all_9_original_Siniscalchi_categories":matched_nine,
        "taxon_names_nine_trait_matched_sorted":sorted(x["source_taxon_label"] for x in source_taxa),
        "matched_original_nine_and_independent_U_D_taxa":len(matched_genomes),
        "strict_taxon_botanical_head_state_counts":dict(sorted(states_taxa.items())),
        "individual_nuclear_biosample_botanical_head_source_counts":dict(sorted(state.items())),
        "original_source_morphology_codebook":"Source Siniscalchi 2023 exact same name-only, original categories 0-3, including pooled white/pink/purple code 2",
        "original_Japan38_176gene_world53_real_tree_done":True,
        "prior_real_world53_nuclear_individuals_including_Carthamus_outgroup":53,
        "all_294_nuclear_tree_real_inferred":False,
        "global_climate_BIO18_extracted_and_native_filtered_for_all":False,
        "is_sufficient_for_global_multivariate_phylogenetic_analysis":False,
        "n_taxon_morphology_gaps_to_fill":270-matched_nine,
        "n_taxon_orientation_gaps_to_fill":states_taxa.get("?",0),
        "study_target":"Now have exact real worldwide DNA-source roster for selecting independent phenotype extraction across 270 source taxon concepts and 294 distinct molecular individuals, not a false global 294-tip species tree",
        "phenotype_collection_rule":"All nine original published source character categories, plus new continuous photograph-measured traits (chroma, capitulum angle, phyllary curvature, gland density/adhesion) require reviewed taxon/voucher source and observed photos; never fill by genus or from same-genus relatives",
        "regional_native_range_gate":"Not validated in all regions, original source location text is a genetic voucher provenance and does not prove native occurrence of morphological reference data",
    }
    outdir.mkdir(parents=True,exist_ok=True)
    with (outdir/"all_294_real_nuclear_source_biosample_exact_9trait_expansion.csv").open("w",encoding="utf-8",newline="") as h:
        w=csv.DictWriter(h,fieldnames=list(result[0]))
        w.writeheader();w.writerows(result)
    with (outdir/"all_270_source_taxon_label_nine_trait_and_UD_coverage.csv").open("w",encoding="utf-8",newline="") as h:
        w=csv.DictWriter(h,fieldnames=list(taxa_rows[0]))
        w.writeheader();w.writerows(taxa_rows)
    (outdir/"worldwide_294_nuclear_multitrait_coverage_receipt.json").write_text(
        json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,ensure_ascii=False))
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--asset-dir",type=Path,required=True)
    p.add_argument("--outdir",type=Path,required=True)
    a=p.parse_args()
    run(a.asset_dir,a.outdir)


if __name__=="__main__":
    main()
