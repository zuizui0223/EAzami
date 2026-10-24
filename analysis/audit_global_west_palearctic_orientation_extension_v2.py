#!/usr/bin/env python3
"""Prospective Western Palearctic U/D source expansion, separate from frozen 35.

Cross-check three independently sourced botanical diagnoses against 294 public
molecular samples.  A source-taxonomy review hold is not silently waived.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from audit_global_nuclear_294_orientation_join_v3 import ROOT, rebuild_panel_and_join

EXT = ROOT / "data/evidence/global_west_palearctic_head_orientation_external_v2.csv"


def audit(root: Path = ROOT):
    _, samples, taxa = rebuild_panel_and_join(root)
    known = {x["analysis_taxon_label"]: x for x in taxa}
    with (root / EXT.relative_to(ROOT)).open(encoding="utf-8", newline="") as f:
        evidence = list(csv.DictReader(f))
    if len(evidence) != 3 or len({x["accepted_taxon"] for x in evidence}) != 3:
        raise ValueError("Western source-evidence cohort changed; freeze new version")
    out = []
    for e in evidence:
        name = e["accepted_taxon"]
        if e["source_orientation_state"] not in {"U", "D"} or not e["source_url"]:
            raise ValueError("invalid source-backed orientation record")
        if e["prior_35_taxon_cohort_membership"] != "not_in_frozen_35":
            raise ValueError("prospective evidence must remain disjoint from 35 cohort")
        t = known.get(name)
        if t is None:
            raise ValueError("source botanical state has no exact molecular taxon label: " + name)
        source_rows = [r for r in samples if r["analysis_taxon_label"] == name]
        if not source_rows or len(source_rows) != int(t["n_biosamples"]):
            raise ValueError("molecular source sample mapping drift")
        if t["orientation_state_candidate"]:
            raise ValueError("prospective state was already in the frozen taxon-level join")
        review = t["source_label_taxonomic_review_hold"] == "true"
        out.append({
            "molecular_source_taxon_label": name,
            "source_U_D_state": e["source_orientation_state"],
            "molecular_biosamples": "|".join(sorted(r["biosample"] for r in source_rows)),
            "molecular_source_loci": "|".join(sorted({r["assay"] for r in source_rows})),
            "n_biosamples": len(source_rows),
            "moreyra_source_name_review_required": str(review).lower(),
            "prospective_admission": "source_name_review_hold" if review else "exact_source_candidate",
            "evidence_url": e["source_url"],
            "botanical_evidence_authority": e["source_authority"],
            "source_clause": e["brief_source_clause"],
            "geographic_scope": e["evidence_geographic_scope"],
            "population_and_voucher_caveat": e["taxon_population_caveat"],
            "frozen_35_unchanged": "true",
            "same_voucher_head_phenotype_verified": "false",
            "BIO15_BIO1_opened": "false",
            "historic_transition_probability_computed": "false",
        })
    counts = Counter(x["prospective_admission"] for x in out)
    clean = [x for x in out if x["prospective_admission"] == "exact_source_candidate"]
    return {
        "version": "global_west_palearctic_prospective_orientation_source_extension_v2",
        "baseline_frozen_35_membership_unchanged": True,
        "n_botanical_evidence_taxa": len(out),
        "n_molecular_exact_label_matches": len(out),
        "name_review_holds": counts.get("source_name_review_hold", 0),
        "exact_source_candidate_taxa": len(clean),
        "clean_U": sum(r["source_U_D_state"] == "U" for r in clean),
        "clean_D": sum(r["source_U_D_state"] == "D" for r in clean),
        "molecular_biosamples_in_extension": sum(x["n_biosamples"] for x in out),
        "additional_climate_freeze_status": "not_opened",
        "native_origin_verified": False,
        "nuclear_tree_ready": False,
        "branchwise_transition_executed": False,
        "claim_limit": (
            "Prospective Western source-only extension. Source name agreement does not "
            "establish specimen-level flower-head phenotype; high-review names remain "
            "held, garden-grown sources and subspecific differences require explicit review."
        ),
    }, out


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--outdir",type=Path,required=True)
    a=p.parse_args()
    r,rows=audit()
    a.outdir.mkdir(parents=True,exist_ok=True)
    (a.outdir/"summary.json").write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    with (a.outdir/"western_nuclear_botanical_evidence_v2.csv").open("w",encoding="utf-8",newline="") as h:
        writer=csv.DictWriter(h,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps(r,indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
