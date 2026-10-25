#!/usr/bin/env python3
"""Worldwide Moreyra nuclear-source x independently documented U/D evidence gate.

Existing primary-source inventories only. Exact names, no synonym transfer.
Documented 'unknown' is not contradictory evidence; explicit ambiguity,
taxonomic conflict or within-species orientation polymorphism vetoes the
single-state Mk taxon-tip assumption.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOREYRA = ROOT / "data/evidence/moreyra2025_cirsium_reconciliation_v1"
CROSSWALK = ROOT / "data/evidence/orientation_comp1061_20tip_source_crosswalk_v1.csv"
NMNS = ROOT / "data/evidence/japan38_nmns_capitulum_trait_seed_v1.csv"
NMNS_EXT1 = ROOT / "data/evidence/japan38_nmns_capitulum_trait_seed_extension_v1.csv"
NMNS_EXT2 = ROOT / "data/evidence/japan38_nmns_capitulum_trait_seed_extension_v2.csv"
HELDOUT_FOC = ROOT / "data/evidence/heldout_east_asia_orientation_candidate_panel_v2.csv"
HELDOUT_AUDIT = ROOT / "data/evidence/heldout_east_asia_trait_state_audit_v1.csv"
FNA = ROOT / "data/evidence/global_fna_head_orientation_evidence_v1.csv"

NO_STATE = {"", "unknown", "not_codable"}
UNCERTAIN = {"?", "ambiguous", "source_conflict_index_downward_detail_erect"}

FIELDNAMES = (
    "tree_code", "biosamples", "source_region_classes", "source_locations",
    "source_row_count", "orientation_U_D_or_unresolved", "status",
    "source_lanes", "n_source_records", "evidence_states",
    "source_urls", "source_paths", "trait_evidence_notes",
    "is_east_asian_discovery_source", "same_molecular_voucher_phenotyped",
    "needs_taxon_name_authority_review", "claim_limit",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = [
            {k: (v or "").strip() for k, v in row.items()}
            for row in csv.DictReader(handle)
        ]
    if not rows:
        raise ValueError("empty input: " + str(path))
    return rows


def load_sources(root: Path = ROOT):
    parts = sorted((root / MOREYRA.relative_to(ROOT)).glob("part_*.csv"))
    if len(parts) != 8:
        raise ValueError("expected eight frozen Moreyra reconciliation parts")
    all_moreyra = [r for p in parts for r in read_csv(p)]
    molecular = [
        r for r in all_moreyra if r["tree_code"].startswith("Cirsium")
        and r["sra_link_status"] == "linked_runinfo"
        and r["scope_class"] != "source_conflict_target_vs_outside"
    ]
    if len(molecular) < 200:
        raise ValueError("Moreyra biological source roster unexpectedly incomplete")
    for row in molecular:
        if not row.get("biosample") or not row.get("tree_code"):
            raise ValueError("missing exact Moreyra source identifier")
    evidence = defaultdict(list)

    def append(name: str, raw_state: str, lane: str, url: str, note: str,
               source_path: Path, source_status: str = ""):
        if not name or not name.startswith("Cirsium "):
            raise ValueError("invalid exact Cirsium evidence taxon name")
        raw = raw_state.strip()
        if raw in ("U", "upward_or_erect", "upward_or_ascending"):
            state = "U"
        elif raw in ("D", "downward_or_nodding"):
            state = "D"
        elif raw in UNCERTAIN:
            state = "ambiguous"
        elif raw in NO_STATE:
            state = "unknown"
        else:
            raise ValueError(f"unrecognized evidence state {raw!r} for {name}")
        # A local opposite-orientation state negates a fixed species-tip label.
        # Do NOT misinterpret flower-colour polymorphism as orientation polymorphism.
        text = note.casefold()
        polymorphic = bool(
            re.search(r"local upright forms|locally erect heads|erect and nodding heads|"
                      r"nodding and erect heads|orientation polymorph|variable head orientation", text)
        )
        evidence[name].append({
            "state": state, "lane": lane, "source_url": url,
            "note": note, "source_path": str(source_path.relative_to(root)),
            "source_status": source_status,
            "orientation_polymorphism": polymorphic,
        })

    for row in read_csv(root / CROSSWALK.relative_to(ROOT)):
        append(row["accepted_taxon"], row["analysis_state"], "east_asia_discovery",
               row["source_url"], row["claim_boundary"], CROSSWALK,
               row.get("evidence_status", ""))
    for path in [NMNS, NMNS_EXT1, NMNS_EXT2]:
        for row in read_csv(root / path.relative_to(ROOT)):
            append(row["nmns_taxon_concept"], row["orientation_state"],
                   "japan38_botanical_authority", row["source_url"],
                   row["claim_boundary"], path, row.get("authority_match_status", ""))

    for row in read_csv(root / HELDOUT_FOC.relative_to(ROOT)):
        if row["eligible_for_occurrence_gate"] != "true":
            continue
        append(row["analysis_taxon"], row["orientation_state"],
               "independent_foc_heldout", row["source_url"],
               row["source_basis"], HELDOUT_FOC, row.get("source_sha256", ""))

    for row in read_csv(root / HELDOUT_AUDIT.relative_to(ROOT)):
        lane = ("independent_eastasia_trait_census" if
                row.get("discovery_overlap") == "no" else
                "eastasia_discovery_overlap_or_ambiguous")
        append(row["analysis_taxon"], row["orientation_state"], lane,
               row["source_url"], row["source_basis"] + " " + row["claim_boundary"],
               HELDOUT_AUDIT, row.get("orientation_pool_status", ""))
    # New geographic evidence is deliberately external to the East-Asian
    # hypothesis selection cohort. Mixed heads stay explicitly ambiguous.
    for row in read_csv(root / FNA.relative_to(ROOT)):
        if row["source_lane"] != "Flora_of_North_America" or row["source_scope"] != "North_America":
            raise ValueError("FNA source scope drift")
        if "Heads" not in row["source_basis"]:
            raise ValueError("FNA clause does not explicitly describe heads")
        append(row["analysis_taxon"], row["orientation_state"],
               "independent_fna_north_america", row["source_url"],
               row["source_basis"] + " " + row["admission_note"],
               FNA, row["source_authority"])
    return molecular, evidence


def classify(evs: list[dict]) -> tuple[str, str]:
    if not evs:
        return "unassessed_by_available_evidence", ""
    observed = {r["state"] for r in evs if r["state"] in {"U", "D"}}
    if any(r["orientation_polymorphism"] for r in evs):
        return "orientation_polymorphism_veto", ""
    if len(observed) > 1:
        return "conflicting_orientation_sources_veto", ""
    if any(r["state"] == "ambiguous" for r in evs):
        return "explicit_ambiguous_or_conflict_veto", ""
    if len(observed) == 0:
        return "no_resolved_orientation_in_available_evidence", ""
    return "exact_name_evidence_candidate", next(iter(observed))


def run(root: Path = ROOT):
    molecular, evidence = load_sources(root)
    grouped = defaultdict(list)
    for row in molecular:
        grouped[row["tree_code"]].append(row)

    out = []
    for name in sorted(grouped):
        mo = grouped[name]
        evs = evidence.get(name, [])
        status, state = classify(evs)
        out.append({
            "tree_code": name,
            "biosamples": "|".join(sorted({x["biosample"] for x in mo})),
            "source_region_classes": "|".join(sorted({x["region_class"] for x in mo})),
            "source_locations": "|".join(sorted({x["geographic_location"] for x in mo})),
            "source_row_count": len(mo),
            "orientation_U_D_or_unresolved": state,
            "status": status,
            "source_lanes": "|".join(sorted({x["lane"] for x in evs})),
            "n_source_records": len(evs),
            "evidence_states": "|".join(sorted({x["state"] for x in evs})),
            "source_urls": "|".join(sorted({x["source_url"] for x in evs if x["source_url"]})),
            "source_paths": "|".join(sorted({x["source_path"] for x in evs})),
            "trait_evidence_notes": " || ".join(dict.fromkeys(x["note"] for x in evs)),
            "is_east_asian_discovery_source": str(any(x["lane"] in {
                "east_asia_discovery", "japan38_botanical_authority",
                "eastasia_discovery_overlap_or_ambiguous",
            } for x in evs)).lower(),
            "same_molecular_voucher_phenotyped": "false",
            "needs_taxon_name_authority_review": "true",
            "claim_limit": (
                "candidate exact tree-code/trait-name match only; "
                "not accepted-name resolved, same-voucher coded, "
                "global nuclear phylogeny or historical climate inference"
            ),
        })

    counts = Counter(x["status"] for x in out)
    states = Counter(x["orientation_U_D_or_unresolved"] for x in out)
    candidates = [x for x in out if x["status"] == "exact_name_evidence_candidate"]
    outside = [x for x in candidates if x["source_region_classes"] == "Outside_target_region"]
    summary = {
        "version": "global_nuclear_orientation_multisource_overlap_v2",
        "classification": "REAL_SOURCE_JOIN_ONLY_NOT_GLOBAL_ECOLOGICAL_INFERENCE",
        "moreyra_linked_cirsium_source_rows": len(molecular),
        "moreyra_distinct_biosamples": len({r["biosample"] for r in molecular}),
        "moreyra_tree_code_labels": len(grouped),
        "source_tables": [str(x.relative_to(ROOT)) for x in
                          (CROSSWALK, NMNS, NMNS_EXT1, NMNS_EXT2, HELDOUT_FOC, HELDOUT_AUDIT, FNA)],
        "source_backed_exact_name_overlaps": sum(x["n_source_records"] > 0 for x in out),
        "candidate_resolved_orientation_labels": len(candidates),
        "candidate_U": states.get("U", 0),
        "candidate_D": states.get("D", 0),
        "status_counts": dict(sorted(counts.items())),
        "candidate_source_region_classes": dict(Counter(
            c for x in candidates for c in x["source_region_classes"].split("|")
        )),
        "outside_east_asia_source_region_candidate_names": [
            {"tree_code": x["tree_code"], "state": x["orientation_U_D_or_unresolved"],
             "source_location": x["source_locations"]} for x in outside
        ],
        "candidate_name_state_rows": [
            {"tree_code": x["tree_code"],
             "state": x["orientation_U_D_or_unresolved"],
             "source_lanes": x["source_lanes"],
             "region_classes": x["source_region_classes"]}
            for x in candidates
        ],
        "audit_gates": {
            "taxon_concept_authority_matching_complete": False,
            "molecular_specimen_to_phenotype_voucher_verified": False,
            "validated_full_global_nuclear_tree_ensemble_available": False,
            "independent_worldwide_U_D_by_nuclear_tip_available": False,
            "worldwide_present_BIO15_BIO1_join_complete": False,
            "global_transition_regime_model_executed": False,
        },
        "limits": [
            "Unassessed species in limited existing trait tables are not assumed to have unknown true head orientation.",
            "Unspecified orientation is neutral; explicitly mixed, conflicting or documented polymorphic orientation is excluded.",
            "Exact tree-code matches are not automatically accepted taxon or molecular voucher phenotype matches.",
            "East Asian discovery-authority states do not give an independent worldwide replication by themselves.",
            "If all confidently coded D tips concentrate in one region, a global branchwise result is not geographically generalizable.",
            "No real global topology or transition effect is estimated by this audit.",
        ],
    }
    return summary, out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    report, records = run()
    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    with (args.outdir / "moreyra_orientation_multisource_candidates.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(records)
    print(json.dumps({k: report[k] for k in (
        "source_backed_exact_name_overlaps", "candidate_resolved_orientation_labels",
        "candidate_U", "candidate_D", "status_counts",
        "candidate_source_region_classes")}, indent=2))


if __name__ == "__main__":
    main()
