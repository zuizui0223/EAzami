#!/usr/bin/env python3
"""Validate the bounded public-data recovery audit for fixed-white candidates.

Discovery metadata, lawful copy routes, exact-name absences, morphology-only
papers, herbarium specimens and image localities are deliberately kept separate
from reusable nuclear tips. Promotion requires exact sequence/sample provenance
and the independent fixed-white promotion contract.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

REQUIRED_COLUMNS = {
    "candidate_id","taxon","search_route","query_or_identifier","result_status",
    "evidence_source","evidence_locator","implication","next_action","claim_limit",
}
A1_EXPECTED = {"WREC01":"Cirsium boninense","WREC02":"Cirsium wulongense"}
NON_TIP_STATUSES = {
    "existing_genetic_study_identified",
    "study_metadata_independently_corrobated",
    "proceedings_copy_route_identified",
    "ndl_remote_copy_route_confirmed",
    "iriomote_indexing_clue_identified",
    "paftol_current_release_exact_taxon_absent",
    "paftol_current_deleted_exact_taxon_absent",
    "no_exact_indexed_plant_asset_recovered",
    "no_followup_publication_or_thesis_recovered",
    "voucher_anchor_recovered",
    "additional_voucher_anchor_recovered",
    "published_taxonomic_study_morphology_only_no_molecular_data",
    "no_public_digitized_voucher_record_recovered",
    "secondary_locality_image_evidence_identified",
    "no_exact_indexed_asset_recovered",
}
FORBIDDEN_READY_TOKENS = ("rate_fit_ready","nuclear_tip_ready","placement_ready","execution_allowed")


def clean(x: object) -> str: return str(x or "").strip()

def read_rows(path: Path) -> tuple[list[str], list[dict[str,str]]]:
    with path.open(encoding="utf-8-sig", newline="") as h:
        r=csv.DictReader(h)
        if not r.fieldnames: raise ValueError("audit table has no header")
        rows=[{k:clean(v) for k,v in row.items()} for row in r if any(clean(v) for v in row.values())]
        return list(r.fieldnames),rows


def validate(path: Path) -> dict[str,object]:
    fields,rows=read_rows(path)
    missing=sorted(REQUIRED_COLUMNS-set(fields))
    if missing: raise ValueError(f"audit missing required columns: {missing}")
    if not rows: raise ValueError("audit contains no evidence rows")

    by_candidate: dict[str,list[dict[str,str]]]=defaultdict(list); statuses=Counter()
    for i,row in enumerate(rows,start=2):
        cid=row["candidate_id"]
        if cid not in A1_EXPECTED: raise ValueError(f"line {i}: unexpected candidate_id {cid!r} in A1 bounded audit")
        if row["taxon"]!=A1_EXPECTED[cid]: raise ValueError(f"line {i}: candidate/taxon mismatch {cid}/{row['taxon']}")
        status=row["result_status"]
        if status not in NON_TIP_STATUSES: raise ValueError(f"line {i}: unsupported result_status {status!r}")
        joined=" ".join(row.values()).lower()
        for token in FORBIDDEN_READY_TOKENS:
            if token in joined: raise ValueError(f"line {i}: audit discovery row contains forbidden readiness token {token!r}")
        for col in ("evidence_source","evidence_locator","implication","next_action","claim_limit"):
            if not row[col]: raise ValueError(f"line {i}: missing {col}")
        by_candidate[cid].append(row); statuses[status]+=1

    if set(by_candidate)!=set(A1_EXPECTED): raise ValueError("both A1 fixed-white candidates must remain represented")

    bon={r["result_status"] for r in by_candidate["WREC01"]}
    required_bon={
        "existing_genetic_study_identified","study_metadata_independently_corrobated",
        "proceedings_copy_route_identified","ndl_remote_copy_route_confirmed",
        "iriomote_indexing_clue_identified","paftol_current_release_exact_taxon_absent",
        "paftol_current_deleted_exact_taxon_absent","no_exact_indexed_plant_asset_recovered",
        "no_followup_publication_or_thesis_recovered",
    }
    if not required_bon<=bon: raise ValueError(f"C. boninense audit lost required recovery states: {sorted(required_bon-bon)}")

    wul={r["result_status"] for r in by_candidate["WREC02"]}
    required_wul={
        "voucher_anchor_recovered","additional_voucher_anchor_recovered",
        "published_taxonomic_study_morphology_only_no_molecular_data",
        "no_public_digitized_voucher_record_recovered","secondary_locality_image_evidence_identified",
        "no_exact_indexed_asset_recovered",
    }
    if not required_wul<=wul: raise ValueError(f"C. wulongense audit lost required public-recovery states: {sorted(required_wul-wul)}")

    return {
        "contract_version":"fixed_white_public_nuclear_recovery_audit_v4",
        "evidence_rows":len(rows),
        "candidates":A1_EXPECTED,
        "result_status_counts":dict(sorted(statuses.items())),
        "boninense_paftol_current_release_exact_taxon_present":False,
        "boninense_existing_2025_genetic_study_data_recovered":False,
        "boninense_ndl_p69_remote_copy_route_confirmed":True,
        "boninense_ndl_copy_order_placed":False,
        "wulongense_published_study_contains_molecular_analysis":False,
        "wulongense_public_digitized_exact_voucher_recovered":False,
        "usable_nuclear_tip_recovered":False,
        "rate_fit_tip_promotion_allowed":False,
        "next_actions":{
            "Cirsium boninense":"request/read exactly p.69 of NDL item 034039888 / RA241-R8 through an eligible user/library remote-copy route; extract method/samples/accessions; author contact deferred",
            "Cirsium wulongense":"published paper is morphology-only; continue public specimen/data mirrors for XLS21-095/XLS21-093 and retain Guizhou PPBC locality as a sampling lead; then new >=2-individual nuclear sampling if no reusable public asset emerges; author contact deferred",
        },
        "claim_limit":"A lawful NDL route to the exact C. boninense abstract page is confirmed but no copy has been ordered by this workflow. Public retrieval has not produced a reusable nuclear tip for either A1 species, so rate-fit promotion remains blocked.",
    }


def main() -> int:
    p=argparse.ArgumentParser();p.add_argument("audit",type=Path);p.add_argument("--output",type=Path);a=p.parse_args()
    out=validate(a.audit);text=json.dumps(out,indent=2,ensure_ascii=False)+"\n"
    if a.output: a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(text,encoding="utf-8")
    print(text,end="");return 0

if __name__=="__main__": raise SystemExit(main())
