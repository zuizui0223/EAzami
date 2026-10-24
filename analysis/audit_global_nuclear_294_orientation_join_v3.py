#!/usr/bin/env python3
"""Join the fully deduplicated 294-BioSample nuclear panel to exact U/D sources.

Source level only, without joining clinical/occurrence climate or claiming
specimen-specific phenotypes. Reuses the original 294-sample panel builder and
validator so Chang 2025/2026 reused BioSamples are NEVER duplicate tips.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from audit_global_nuclear_orientation_multisource_v2 import (
    ROOT, MOREYRA, load_sources, classify,
)
from build_japan_origin_global_public_panel_v2 import (
    FIELDS as PANEL_FIELDS,
    build_moreyra, build_chang, validate, japan38_index, load_contract, read_csv,
)

CH25 = ROOT / "data/evidence/chang2025_public_run_manifest_v1.csv"
CH26 = ROOT / "data/evidence/chang2026_public_run_manifest_v1.csv"
J38 = ROOT / "data/evidence/moreyra2025_japan_38_membership_audit_2026-08-10.csv"
CONTRACT = ROOT / "data/evidence/japan_origin_global_public_panel_contract_v2.json"

FIELDS = (
    "panel_id", "biosample", "assay", "source_studies", "analysis_taxon_label",
    "voucher", "region", "location", "run_accessions", "name_review_required",
    "n_biosamples_with_same_source_taxon_label", "has_exact_source_orientation_evidence",
    "orientation_state_candidate", "orientation_source_decision", "inference_gate",
    "orientation_evidence_source_urls", "orientation_evidence_lanes",
    "same_voucher_orientation_confirmed", "repeated_biosample_is_independent_trait_origin",
)


def rebuild_panel_and_join(root: Path = ROOT):
    paths = sorted((root / MOREYRA.relative_to(ROOT)).glob("part_*.csv"))
    if len(paths) != 8:
        raise ValueError("incomplete Moreyra source parts")
    all_source = [row for p in paths for row in read_csv(p)]
    j38 = read_csv(root / J38.relative_to(ROOT))
    moreyra, excluded = build_moreyra(all_source, japan38_index(j38))
    chang, shared = build_chang(
        read_csv(root / CH25.relative_to(ROOT)),
        read_csv(root / CH26.relative_to(ROOT))
    )
    panel = moreyra + chang
    builder_receipt = validate(panel, excluded, shared,
                               load_contract(root / CONTRACT.relative_to(ROOT)), j38)
    if not len(panel) == 294 or len({p["biosample"] for p in panel}) != 294:
        raise ValueError("real frozen 294-panel roster drift")

    _, evidence = load_sources(root)
    multiplicity = Counter(x["analysis_taxon_label"] for x in panel)
    sample_rows = []
    taxon_ledger = defaultdict(list)

    for r in panel:
        name = r["analysis_taxon_label"]
        evs = evidence.get(name, [])
        decision, state = classify(evs)
        review = r["name_review_required"] == "true"
        if state and review:
            gate = "hold_source_taxon_name_conflict"
        elif state:
            gate = "exact_name_U_D_candidate_not_same_voucher"
        elif evs:
            gate = "no_binary_state_or_ambiguous_or_polymorphic"
        else:
            gate = "no_explicit_source_orientation_evidence"
        row = {
            "panel_id": r["panel_id"],
            "biosample": r["biosample"],
            "assay": r["assay"],
            "source_studies": r["source_studies"],
            "analysis_taxon_label": name,
            "voucher": r["voucher"],
            "region": r["region"],
            "location": r["location"],
            "run_accessions": r["run_accessions"],
            "name_review_required": r["name_review_required"],
            "n_biosamples_with_same_source_taxon_label": multiplicity[name],
            "has_exact_source_orientation_evidence": str(bool(evs)).lower(),
            "orientation_state_candidate": state,
            "orientation_source_decision": decision,
            "inference_gate": gate,
            "orientation_evidence_source_urls": "|".join(sorted({
                e["source_url"] for e in evs if e["source_url"]
            })),
            "orientation_evidence_lanes": "|".join(sorted({e["lane"] for e in evs})),
            "same_voucher_orientation_confirmed": "false",
            "repeated_biosample_is_independent_trait_origin": "false",
        }
        sample_rows.append(row)
        taxon_ledger[name].append(row)

    taxon_rows = []
    for name, group in sorted(taxon_ledger.items()):
        possible = {x["orientation_state_candidate"] for x in group}
        if len(possible) > 1:
            raise ValueError("same source label acquired different U/D evidence")
        review = any(x["name_review_required"] == "true" for x in group)
        state = next(iter(possible))
        taxon_rows.append({
            "analysis_taxon_label": name,
            "n_biosamples": len(group),
            "sample_panel_ids": "|".join(sorted(x["panel_id"] for x in group)),
            "source_studies": "|".join(sorted({x["source_studies"] for x in group})),
            "source_regions": "|".join(sorted({x["region"] for x in group})),
            "orientation_state_candidate": state,
            "source_label_taxonomic_review_hold": str(review).lower(),
            "n_source_evidence_lanes": len(set(
                y for x in group for y in x["orientation_evidence_lanes"].split("|") if y
            )),
            "needs_population_aware_or_one_representative_design": str(len(group) > 1).lower(),
            "admission_limit": (
                "taxon-level botanical evidence; no nuclear specimen-phenotype linkage; "
                "multiple individual samples cannot count as independent state origins"
            ),
        })

    sample_state = Counter(x["orientation_state_candidate"] for x in sample_rows)
    taxon_state = Counter(x["orientation_state_candidate"] for x in taxon_rows)
    inference = Counter(x["inference_gate"] for x in sample_rows)
    summary = {
        "version": "global_nuclear_294_orientation_source_join_v3",
        "status": "VALIDATED_NUCLEAR_SAMPLE_SOURCE_JOIN_ONLY",
        "builder_contract": builder_receipt,
        "n_biosamples": len(sample_rows),
        "n_public_run_accessions": len({
            x for r in sample_rows for x in r["run_accessions"].split("|") if x
        }),
        "n_source_taxon_labels": len(taxon_rows),
        "n_duplicated_taxon_labels": sum(x["n_biosamples"] > 1 for x in taxon_rows),
        "candidate_sample_states": {"U": sample_state.get("U", 0), "D": sample_state.get("D", 0)},
        "candidate_distinct_taxon_states": {"U": taxon_state.get("U", 0), "D": taxon_state.get("D", 0)},
        "candidate_sample_inference_gates": dict(sorted(inference.items())),
        "name_review_required_candidate_samples": sum(
            x["orientation_state_candidate"] in {"U", "D"}
            and x["name_review_required"] == "true" for x in sample_rows
        ),
        "source_region_by_candidate_taxon": dict(Counter(
            x["source_regions"] for x in taxon_rows if x["orientation_state_candidate"]
        )),
        "public_source_inference_ready": False,
        "global_nuclear_tree_executed": False,
        "branchwise_climate_shift_estimable": False,
        "all_294_biosamples_same_voucher_head_state_verified": False,
        "claim_limit": (
            "Exact botanical taxon name to source nuclear sample join, NOT "
            "specimen-verified head orientation, geographic representativeness, "
            "independent transitions, world nuclear tree, or palaeoclimate."
        )
    }
    return summary, sample_rows, taxon_rows


def write_csv(path: Path, rows: list[dict], fields=None):
    if not rows:
        raise ValueError("empty generated source join")
    with path.open("w", newline="", encoding="utf-8") as h:
        w = csv.DictWriter(h, fieldnames=list(fields or rows[0]))
        w.writeheader()
        w.writerows(rows)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--outdir",type=Path,required=True)
    a=p.parse_args()
    summary,samples,taxa=rebuild_panel_and_join()
    a.outdir.mkdir(parents=True,exist_ok=True)
    (a.outdir/"report.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    write_csv(a.outdir/"all_294_nuclear_biosample_orientation_source_join.csv",samples,FIELDS)
    write_csv(a.outdir/"taxon_label_orientation_source_join.csv",taxa)
    print(json.dumps({
        "n_biosamples":summary["n_biosamples"],
        "n_source_taxon_labels":summary["n_source_taxon_labels"],
        "candidate_sample_states":summary["candidate_sample_states"],
        "candidate_distinct_taxon_states":summary["candidate_distinct_taxon_states"],
        "candidate_sample_inference_gates":summary["candidate_sample_inference_gates"],
        "global_nuclear_tree_executed":summary["global_nuclear_tree_executed"],
    },indent=2))


if __name__=="__main__":
    main()
