#!/usr/bin/env python3
"""Build the maximal currently curated public panel for Japanese Cirsium origins.

This builder combines three already-audited public evidence layers without
silently harmonising taxon names or claiming that different sequencing assays
have already been merged phylogenetically:

1. Moreyra et al. 2025 PRJNA957074 Compositae1061 target-capture samples from
   Japan, China, the Russian Far East, Inner Northeast Asia and Mongolia;
2. Chang et al. 2025 PRJNA1158676 leaf-transcriptome samples; and
3. Chang et al. 2026 PRJNA1311153 leaf-transcriptome samples, including the
   Ryukyu Arenicola samples absent from the Moreyra Japan-38 analysis.

The output is a source/provenance manifest and an accession-resolution queue.
It is *not* a tree and cannot by itself establish monophyly, dispersal direction
or the number of invasions. Moreyra source rows are grouped by BioSample so a
single biological sample with multiple runs is not double-counted. The known
Japan-voucher/Ukraine-SRA geography conflict is excluded from automatic use but
retained in an exclusion ledger.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping, Sequence

DEFAULT_MOREYRA = Path("data/evidence/moreyra2025_east_ne_asia_sample_audit_2026-08-10.csv")
DEFAULT_CHANG2025 = Path("data/evidence/chang2025_nipponocirsium_accession_audit_2026-08-10.csv")
DEFAULT_CHANG2026 = Path("data/evidence/chang2026_east_asia_accession_audit_2026-08-10.csv")
DEFAULT_OUTDIR = Path("data/evidence/generated/japan_origin_max_public_panel")

OUTPUT_FIELDS = (
    "panel_id", "source_study", "bioproject", "assay", "source_taxon_label",
    "analysis_taxon_label", "voucher", "herbarium", "biosample",
    "public_identifiers", "run_accessions", "run_resolution_state", "region",
    "location", "origin_test_role", "name_or_geography_review_required",
    "automatic_use", "exclusion_reason", "common_locus_space",
    "claim_boundary",
)


def clean(x: object) -> str:
    return str(x or "").strip()


def slug(x: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", clean(x)).strip("_") or "sample"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as h:
        rows=[{k:clean(v) for k,v in row.items()} for row in csv.DictReader(h)
              if any(clean(v) for v in row.values())]
    if not rows:
        raise ValueError(f"{path}: no rows")
    return rows


def unique_join(values: Iterable[str]) -> str:
    return "|".join(sorted({clean(v) for v in values if clean(v)}))


def normalize_chang_taxon(label: str) -> str:
    label=clean(label)
    if label.startswith("C. "):
        return "Cirsium " + label[3:]
    return label


def moreyra_role(region: str, taxon: str) -> str:
    if taxon == "Cirsium dipsacolepis":
        return "published_separate_japan_invasion_anchor"
    if taxon == "Cirsium lineare":
        return "published_separate_japan_invasion_cross_assay_anchor"
    if region == "Japan":
        return "main_japanese_radiation_or_japan38_test"
    if region == "China":
        return "continental_source_or_sister_candidate"
    if region in {"Russian_Far_East","Russian_Inner_NE_Asia","Mongolia"}:
        return "northeast_asia_bridge"
    return "east_asia_backbone"


def chang_role(taxon: str, location: str, year: int) -> str:
    low=taxon.casefold()
    if taxon in {"Cirsium brevicaule","Cirsium irumtiense"}:
        return "ryukyu_origin_test"
    if taxon == "Cirsium lineare":
        return "published_separate_japan_invasion_cross_assay_anchor"
    if taxon == "Cirsium morii":
        return "arenicola_sister_context"
    if "japan" in location.casefold():
        return "japanese_cross_assay_bridge"
    if year == 2025 and any(k in low for k in ("kawakamii","tatakaense","pengii")):
        return "taiwan_nipponocirsium_bridge"
    return "taiwan_or_continental_east_asia_bridge"


def build_moreyra(rows: Sequence[Mapping[str,str]]) -> tuple[list[dict[str,str]], list[dict[str,str]]]:
    required={"tree_code","biosample","run","region_class","scope_class","sra_link_status",
              "geographic_evidence_relation","name_reconciliation_priority","published_species",
              "voucher_and_herbarium","sra_scientific_name","geographic_location"}
    missing=required-set(rows[0])
    if missing: raise ValueError(f"Moreyra input missing {sorted(missing)}")
    by_bio: dict[str,list[Mapping[str,str]]]=defaultdict(list)
    admitted_scopes={"core_east_asia","northeast_asia_bridge","source_conflict_target_vs_outside"}
    for row in rows:
        if row["scope_class"] not in admitted_scopes:
            continue
        if row["sra_link_status"] != "linked_runinfo":
            continue
        if not row["biosample"]:
            raise ValueError("Moreyra admitted row lacks BioSample")
        by_bio[row["biosample"]].append(row)

    panel=[]; exclusions=[]
    for biosample in sorted(by_bio):
        group=by_bio[biosample]
        conflict=any(
            r["scope_class"]=="source_conflict_target_vs_outside"
            or r["geographic_evidence_relation"]=="source_conflict_target_vs_outside"
            for r in group
        )
        runs=unique_join(r["run"] for r in group)
        taxon=unique_join(r["tree_code"] for r in group)
        region=unique_join(r["region_class"] for r in group)
        high=any(r["name_reconciliation_priority"]=="high" for r in group)
        relation=unique_join(r["tree_code_vs_sra_name"] for r in group)
        review=high or relation!="exact"
        row={
            "panel_id":f"MRY_{slug(biosample)}",
            "source_study":"Moreyra2025",
            "bioproject":"PRJNA957074",
            "assay":"Compositae1061_target_capture",
            "source_taxon_label":taxon,
            "analysis_taxon_label":taxon,
            "voucher":unique_join(r["voucher_and_herbarium"] for r in group),
            "herbarium":"embedded_in_voucher_field",
            "biosample":biosample,
            "public_identifiers":unique_join([biosample,*(r["experiment"] for r in group),*(r["run"] for r in group)]),
            "run_accessions":runs,
            "run_resolution_state":"resolved_public_runs",
            "region":region,
            "location":unique_join(r["geographic_location"] for r in group),
            "origin_test_role":moreyra_role(region,taxon),
            "name_or_geography_review_required":str(review or conflict).lower(),
            "automatic_use":str(not conflict).lower(),
            "exclusion_reason":"source_conflict_target_vs_outside" if conflict else "",
            "common_locus_space":"Compositae1061_direct",
            "claim_boundary":"Source labels are preserved; inclusion is not evidence of Japanese monophyly or direct continental ancestry.",
        }
        if conflict: exclusions.append(row)
        else: panel.append(row)
    return panel,exclusions


def build_chang2025(rows: Sequence[Mapping[str,str]]) -> list[dict[str,str]]:
    required={"taxon","sample_index","collecting_location","voucher","bioproject"}
    missing=required-set(rows[0])
    if missing: raise ValueError(f"Chang2025 input missing {sorted(missing)}")
    out=[]
    for row in rows:
        taxon=normalize_chang_taxon(row["taxon"])
        ident=f"{taxon}|{row['voucher']}|{row['sample_index']}"
        out.append({
            "panel_id":f"CH25_{slug(row['voucher'] or ident)}",
            "source_study":"Chang2025",
            "bioproject":row["bioproject"],
            "assay":"leaf_RNAseq_transcriptome",
            "source_taxon_label":row["taxon"],
            "analysis_taxon_label":taxon,
            "voucher":row["voucher"],
            "herbarium":"",
            "biosample":"",
            "public_identifiers":row["bioproject"],
            "run_accessions":"",
            "run_resolution_state":"bioproject_public_run_join_required",
            "region":"Japan" if "JAPAN" in row["collecting_location"].upper() else "Taiwan",
            "location":row["collecting_location"],
            "origin_test_role":chang_role(taxon,row["collecting_location"],2025),
            "name_or_geography_review_required":"false",
            "automatic_use":"true",
            "exclusion_reason":"",
            "common_locus_space":"Compositae1061_homolog_projection_required",
            "claim_boundary":"Transcriptome metadata are public; common-locus recovery and exact SRA run join are still required before joint tree inference.",
        })
    return out


def build_chang2026(rows: Sequence[Mapping[str,str]]) -> list[dict[str,str]]:
    required={"taxon","sample_number_within_taxon","location","voucher","herbarium","embedded_public_accession","bioproject"}
    missing=required-set(rows[0])
    if missing: raise ValueError(f"Chang2026 input missing {sorted(missing)}")
    out=[]
    for row in rows:
        taxon=normalize_chang_taxon(row["taxon"])
        embedded=clean(row["embedded_public_accession"]).upper()
        state="embedded_public_identifier_present" if embedded else "bioproject_public_run_join_required"
        out.append({
            "panel_id":f"CH26_{slug(row['voucher'] or taxon+'_'+row['sample_number_within_taxon'])}",
            "source_study":"Chang2026",
            "bioproject":row["bioproject"],
            "assay":"leaf_RNAseq_transcriptome",
            "source_taxon_label":row["taxon"],
            "analysis_taxon_label":taxon,
            "voucher":row["voucher"],
            "herbarium":row["herbarium"],
            "biosample":"",
            "public_identifiers":unique_join([row["bioproject"],embedded]),
            "run_accessions":embedded if embedded.startswith("SRR") else "",
            "run_resolution_state":state,
            "region":"Japan" if "JAPAN" in row["location"].upper() else "Taiwan",
            "location":row["location"],
            "origin_test_role":chang_role(taxon,row["location"],2026),
            "name_or_geography_review_required":"false",
            "automatic_use":"true",
            "exclusion_reason":"",
            "common_locus_space":"Compositae1061_homolog_projection_required",
            "claim_boundary":"Raw reads are public under the cited BioProject, but exact run reconciliation and homolog recovery must pass before joint inference.",
        })
    return out


def validate_panel(panel: Sequence[Mapping[str,str]], exclusions: Sequence[Mapping[str,str]]) -> dict[str,object]:
    ids=[r["panel_id"] for r in panel]
    if len(ids)!=len(set(ids)): raise ValueError("duplicate panel_id")
    taxa={r["analysis_taxon_label"] for r in panel}
    for required in ("Cirsium dipsacolepis","Cirsium lineare","Cirsium brevicaule","Cirsium irumtiense"):
        if required not in taxa: raise ValueError(f"missing origin-critical taxon {required}")
    for taxon in ("Cirsium brevicaule","Cirsium irumtiense"):
        n=sum(r["analysis_taxon_label"]==taxon for r in panel)
        if n < 3: raise ValueError(f"{taxon} needs all three public Chang2026 samples; found {n}")
    if not any(r["source_study"]=="Moreyra2025" and r["region"]=="China" for r in panel):
        raise ValueError("no Chinese Moreyra public samples")
    if not any(r["origin_test_role"]=="northeast_asia_bridge" for r in panel):
        raise ValueError("no Northeast Asian public bridge")
    if not exclusions or not any(r["exclusion_reason"]=="source_conflict_target_vs_outside" for r in exclusions):
        raise ValueError("known Japan-vs-outside geography conflict was not retained in exclusions")
    if any(r["automatic_use"]!="true" for r in panel):
        raise ValueError("admitted panel contains automatic_use=false")

    study_counts=Counter(r["source_study"] for r in panel)
    assay_counts=Counter(r["assay"] for r in panel)
    region_counts=Counter(r["region"] for r in panel)
    role_counts=Counter(r["origin_test_role"] for r in panel)
    run_state_counts=Counter(r["run_resolution_state"] for r in panel)
    return {
        "contract_version":"japan_origin_max_public_panel_v1",
        "panel_rows":len(panel),
        "unique_panel_ids":len(set(ids)),
        "unique_analysis_taxa":len(taxa),
        "study_counts":dict(sorted(study_counts.items())),
        "assay_counts":dict(sorted(assay_counts.items())),
        "region_counts":dict(sorted(region_counts.items())),
        "origin_test_role_counts":dict(sorted(role_counts.items())),
        "run_resolution_state_counts":dict(sorted(run_state_counts.items())),
        "excluded_rows":len(exclusions),
        "ryukyu_public_replicates":{
            t:sum(r["analysis_taxon_label"]==t for r in panel)
            for t in ("Cirsium brevicaule","Cirsium irumtiense")
        },
        "japan_all_taxa_monophyly_claim_allowed":False,
        "main_japanese_radiation_36_of_38_is_published_prior":True,
        "joint_common_locus_tree_executed":False,
        "new_china_sampling_freeze_allowed":False,
        "next_gate":"resolve Chang SRA runs, recover common Compositae1061 homologs, infer public-only joint tree, then rank new Chinese sampling by sister-branch information gain",
    }


def write_csv(path: Path, rows: Sequence[Mapping[str,str]]) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as h:
        w=csv.DictWriter(h,fieldnames=list(OUTPUT_FIELDS));w.writeheader();w.writerows(rows)


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--moreyra",type=Path,default=DEFAULT_MOREYRA)
    p.add_argument("--chang2025",type=Path,default=DEFAULT_CHANG2025)
    p.add_argument("--chang2026",type=Path,default=DEFAULT_CHANG2026)
    p.add_argument("--outdir",type=Path,default=DEFAULT_OUTDIR)
    a=p.parse_args()
    more,excl=build_moreyra(read_csv(a.moreyra))
    ch25=build_chang2025(read_csv(a.chang2025))
    ch26=build_chang2026(read_csv(a.chang2026))
    panel=more+ch25+ch26
    summary=validate_panel(panel,excl)
    write_csv(a.outdir/"japan_origin_max_public_panel_v1.csv",panel)
    write_csv(a.outdir/"japan_origin_max_public_exclusions_v1.csv",excl)
    queue=[r for r in panel if r["run_resolution_state"]!="resolved_public_runs"]
    write_csv(a.outdir/"japan_origin_public_run_resolution_queue_v1.csv",queue)
    (a.outdir/"japan_origin_max_public_panel_summary_v1.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
