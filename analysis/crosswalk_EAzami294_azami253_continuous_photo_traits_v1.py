#!/usr/bin/env python3
"""Bridge EAzami 294 nuclear public biological samples to actual azami photo traits.

Original image trait universe: 253 Cirsium taxon-level photo phenotype
morphospace modules colour and capitulum outline, and 127 taxa with
bract/involucre module PC scores. A morphospace PC is a derived continuous
module coordinate, NOT an original colour L*/C* or directly measured
phyllary length, spine defence effectiveness or anthocyanin concentration.
The image score for a taxon and genomic voucher are NOT the same specimen.

Source files SHA pinned to azami main commit b463dbc... (2026-10-25 audit);
NO taxon name synonyms/alias propagation; only exactly equal taxon strings.
Scores were computed on published/observed heterogenous citizen-science
photographs and carry image resolution/angle/ROI technical limitations.
"""
from __future__ import annotations

import argparse,csv,hashlib,io,json,math,urllib.request
from collections import Counter,defaultdict
from pathlib import Path

from audit_global_nuclear_294_orientation_join_v3 import rebuild_panel_and_join

SOURCE_REPO="zuizui0223/azami"
SOURCE_COMMIT="b463dbc938e454baa54b2e480f7f1d8badd7795d"
SRC_ROOT="analysis_outputs/v2_full27_environment_atlas_2026-08-27/secondary/pca"
SCORES_FILE=f"{SRC_ROOT}/geb_v2_taxon_morphospace_scores.csv"
LOADINGS_FILE=f"{SRC_ROOT}/geb_v2_taxon_morphospace_loadings.csv"
REPORT_FILE=f"{SRC_ROOT}/geb_v2_trait_geography_report.json"
PIN_SCORES="e5553182a15a9c401d4c3e47d5451b036ca62825"
PIN_LOADINGS="8ba8e6ef26472f86cc1a66717c074c93e77606fc"
PHOTO_SCOPES={
  "all_inferential_endpoints":127,
  "module:armature":127,
  "module:colour":253,
  "module:involucre_architecture":127,
  "module:shape":253
}
ENDPOINTS=("PC1","PC2","PC3")
MODULES=tuple(PHOTO_SCOPES)
FNA_MIXED_HEAD={"Cirsium eatonii","Cirsium joannae"}


def git_blob(data:bytes):
    return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()


def retrieve(path,expected=None):
    url=f"https://raw.githubusercontent.com/{SOURCE_REPO}/{SOURCE_COMMIT}/{path}"
    req=urllib.request.Request(url,headers={"User-Agent":"EAzami-actual-image-phenotype-source-citation/1.0"})
    with urllib.request.urlopen(req,timeout=60) as h:
        raw=h.read()
    if expected is not None and git_blob(raw)!=expected:
        raise ValueError(f"azami original full image morphospace source blob drift: {path}")
    return raw


def csvbytes(data):
    with io.StringIO(data.decode("utf-8-sig")) as f:
        return list(csv.DictReader(f))


def namescores():
    src=csvbytes(retrieve(SCORES_FILE,PIN_SCORES))
    load=csvbytes(retrieve(LOADINGS_FILE,PIN_LOADINGS))
    report=json.loads(retrieve(REPORT_FILE).decode("utf-8"))
    if not src or set(src[0])!={"scope","taxon_name","PC1","PC2","PC3"}:
        raise ValueError("original azami continuous species morphospace score columns drift")
    grouped=defaultdict(dict)
    for row in src:
        scope,name=row["scope"],row["taxon_name"]
        if scope not in PHOTO_SCOPES or not name.startswith("Cirsium "):
            raise ValueError("unexpected photographic trait source taxon/definition")
        if name in grouped[scope]:
            raise ValueError("duplicated original image taxon in morphospace scope")
        if any(not math.isfinite(float(row[x])) for x in ENDPOINTS):
            raise ValueError("invalid actual original continuous photo-derived PCA trait coordinate")
        grouped[scope][name]=row
    actual={k:len(v) for k,v in grouped.items()}
    if actual!=PHOTO_SCOPES:
        raise ValueError("actual image source trait geographic coverage unexpectedly changed: "+repr(actual))
    n_expected={r["scope"]:r["n_complete_taxa"] for r in report["pca_scopes"]}
    if n_expected!=actual:
        raise ValueError("original azami photo-derived independent morphospace report disagrees")
    loadby=defaultdict(list)
    for row in load:
        scope=row["scope"]
        if scope not in PHOTO_SCOPES:
            raise ValueError("unexpected actual phenotype loading scope")
        loadby[scope].append(row)
    return grouped,loadby,report


def construct_key(scope,pc):
    return scope.replace(":","_").replace("all_inferential_endpoints","all18") + "__" + pc


def to_photo_record(taxon,grouped):
    data={}
    for scope in MODULES:
        present=taxon in grouped[scope]
        data[scope.replace(":","_")+"_source_photo_available"]=str(present).lower()
        for pc in ENDPOINTS:
            data[construct_key(scope,pc)]=(grouped[scope][taxon][pc] if present else "")
    return data


def summarize(grouped,rows):
    byscope={}
    for scope in MODULES:
        selected={r["source_taxon_label"] for r in rows if r[scope.replace(":","_")+"_source_photo_available"]=="true"}
        byscope[scope]={
            "n_unique_original_nuclear_taxon_concepts_with_exact_photo_module":len(selected),
            "n_nuclear_BioSamples_receiving_taxon_level_module_PC":sum(
                r[scope.replace(":","_")+"_source_photo_available"]=="true" for r in rows),
        }
    return byscope


def run(outdir:Path,world53_traits:Path|None=None):
    _receipt,nuclear,phylo_taxa=rebuild_panel_and_join()
    if len(nuclear)!=294 or len(phylo_taxa)!=270:
        raise ValueError("original 294/270 genomic source input unexpectedly changed")
    photo,loadings,report=namescores()
    joined=[]
    for r in nuclear:
        taxon=r["analysis_taxon_label"]
        z={
            "source_biosample":r["biosample"],
            "source_run_accessions":r["run_accessions"],
            "source_taxon_label":taxon,
            "source_taxon_name_review_required":r["name_review_required"],
            "source_sample_geographic_text":r["location"],
            "source_studies":r["source_studies"],
            "original_source_U_D_candidate":r["orientation_state_candidate"],
            "source_head_U_D_strict_only":(
                r["orientation_state_candidate"] if (
                    r["inference_gate"]=="exact_name_U_D_candidate_not_same_voucher"
                    and taxon not in FNA_MIXED_HEAD) else ""
            ),
            "source_original_photo_genetic_voucher_same_individual":"false",
            "photo_source_nativenessor_local_population_match":"UNVERIFIED",
            **to_photo_record(taxon,photo)
        }
        joined.append(z)
    if len(joined)!=294 or len({x["source_biosample"] for x in joined})!=294:
        raise ValueError("lost/repeated Moreyra/Chang source molecule")
    taxon_groups=defaultdict(list)
    for row in joined:taxon_groups[row["source_taxon_label"]].append(row)
    taxon_rows=[]
    for taxon,group in sorted(taxon_groups.items()):
        row={
            "source_taxon_label":taxon,
            "n_distinct_genetic_biosamples":len(group),
            "source_region_sample_text":"|".join(sorted({x["source_sample_geographic_text"] for x in group})),
            "source_photo_genetic_same_voucher":"false",
            "photo_geographic_NA_EU_EAsia_provenance_unresolved":"true",
            "original_source_name_review_required":str(any(x["source_taxon_name_review_required"]=="true" for x in group)).lower(),
            **to_photo_record(taxon,photo)
        }
        taxon_rows.append(row)
    if len(taxon_rows)!=270:
        raise ValueError("global actual taxon roster drift")
    world53=[]
    if world53_traits is not None:
        source53=[]
        with world53_traits.open(encoding="utf-8-sig",newline="") as h:
            source53=list(csv.DictReader(h))
        if len(source53)!=53 or len({x["tip_id"] for x in source53})!=53:
            raise ValueError("accepted original actual 53-tip nuclear tree source shape coverage drift")
        for row in source53:
            taxon=row["source_taxon"]
            z={
                "source53_nuclear_tip_id":row["tip_id"],
                "source_taxon_label":taxon,
                "original_source_U_D":row["head_orientation"],
                "source_molecular_BioSample":row["source_biosample"],
                "source_molecular_run":row["source_run"],
                "source_image_trait_same_sequenced_voucher":"false",
                **to_photo_record(taxon,photo),
            }
            world53.append(z)
    outdir.mkdir(parents=True,exist_ok=True)
    def write(name,rows):
        if not rows:return
        with (outdir/name).open("w",encoding="utf-8",newline="") as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]))
            w.writeheader();w.writerows(rows)
    write("actual_global294_nuclear_biosample_azami_continuous_photo_PC_5modules.csv",joined)
    write("actual_global270_taxon_azami_continuous_photo_PC_5modules.csv",taxon_rows)
    if world53:write("actual_world53_nuclear_tip_azami_continuous_photo_PC_5modules.csv",world53)
    info={
        "contract":"EAzami_x_azami_2026_worldwide_nuclear294_vs_photo253_5module_continuous_exact_taxon_bridge_v1",
        "original_azami_repo_commit_SHA256":SOURCE_COMMIT,
        "original_azami_photo_species_PCA_scores_git_blob":PIN_SCORES,
        "original_azami_photo_PC_loadings_git_blob":PIN_LOADINGS,
        "original_azami_image_trait_module_taxon_counts":PHOTO_SCOPES,
        "photo_source_derivation":"real photograph repeated measurements reduced to among-taxon module PCA coordinates; PCA axes are NOT measured floral colour or bract organ lengths directly",
        "n_Moreyra_Chang_public_genetic_individuals":294,
        "n_independent_original_genetic_taxon_labels":270,
        "n_public_phylogenetic_individuals_on_176locus_pilot_including_outgroup":53,
        "n_world53_source_tips_in_crosswalk":len(world53),
        "global_taxon_and_biosample_image_trait_exact_coverage_by_module":summarize(photo,joined),
        "world53_tip_photo_module_coverage":{
            scope:sum(row[scope.replace(":","_")+"_source_photo_available"]=="true" for row in world53)
            for scope in MODULES
        },
        "original_azami_photo_PCA_loadings_top3_per_PC":{
            scope:{
                pc:sorted([
                   {"endpoint_id":r["endpoint_id"],"loading":float(r[pc+"_loading"])}
                   for r in loadings[scope] if r[pc+"_loading"]
                ],key=lambda r:-abs(r["loading"]))[:3] for pc in ENDPOINTS
            } for scope in MODULES
        },
        "original_photo_measurement_technical_warnings":{
            "orientation":"photograph-referenced vertical angle cannot directly establish gravitational head nodding; image bbox shift sensitive",
            "colour":"CIELAB lightness/chroma from heterogeneous photos not standardized spectrophotometer or true anthocyanin quantity",
            "shape":"2D outline traits sensitive to image scale and projected view, not direct 3D shape",
            "phyllary_armature":"image bract projections not automatically physical spine length, resin gland density or mechanical defence",
        },
        "exact_taxon_spelling_no_synonym_transfer":True,
        "not_same_genetic_voucher_as_photographic_measurement":True,
        "n_original_global_nuclear_genetic_tips_with_fully_joint_photo_PCA_not_necessarily_53":True,
        "source_native_range_image_population_gate_passed":False,
        "all_global_photo_taxa_have_176locus_sequence":False,
        "global_294tip_350gene_species_phylogeny_not_inferred":True,
        "research_action":"Now join independently measured continuous capitulum/colour/involucre image axis diversity and real source nuclear phylogenies at taxon level, then compare regional environmental responses with spatial and evolutionary structure."
    }
    (outdir/"EAzami_azami_source_photo_nuclear_continuous_trait_bridge.json").write_text(
        json.dumps(info,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "genetic_source_BioSamples":294,"genetic_source_taxon_labels":270,
        "azami_photo_module_source_taxa":PHOTO_SCOPES,
        "world294_module_exact_coverage":info["global_taxon_and_biosample_image_trait_exact_coverage_by_module"],
        "world53_nuclear_tip_source_image_overlap":info["world53_tip_photo_module_coverage"],
        "photographic_gravity_reference_verified":False,
        "full_worldwide_294_tip_molecular_phylogeny_complete":False,
    },indent=2))
    return info


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--outdir",type=Path,required=True)
    p.add_argument("--world53-traits",type=Path)
    a=p.parse_args()
    run(a.outdir,a.world53_traits)


if __name__=="__main__":
    main()
