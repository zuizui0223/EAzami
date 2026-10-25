#!/usr/bin/env python3
"""Make a frozen, source-led nuclear-phylogeny pilot intake from the 294 public BioSamples.

PURPOSE: real biological sample acquisition and rooting/coverage QA, NOT a
recovered global nuclear tree or U->D climate result.

All 294 JOG IDs remain anchored to the original full-panel ordering.
Prioritize 35 source-name-clean U/D taxon labels (46 biological samples),
then taxon-distinct geographic reference anchors chosen without trait/climate
information.  Do not turn pilot inference into a full-genus claim.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from audit_global_nuclear_294_orientation_join_v3 import rebuild_panel_and_join

SEED = "global-U2D-anchor-preclimate-v1"
AREAS = ("North_America", "East_NE_Asia", "West_Palearctic", "Other_or_unresolved")
FIELDS = (
    "full_jog_tip_id", "panel_id", "biosample", "run_accessions",
    "run_count", "assay", "source_studies", "analysis_taxon_label",
    "source_location", "source_region", "broad_area", "orientation_candidate",
    "name_review_required", "acquisition_tier", "group_size_at_source_taxon_label",
    "phenotype_same_voucher_confirmed", "climate_centroid_ready",
    "independent_phylogenetic_branch_confirmed",
)
TERMS_NORTH = ("usa", "united states", "canada", "mexico")
TERMS_EAST = ("japan", "taiwan", "china", "korea", "mongolia")
TERMS_WEST = (
    "spain", "france", "italy", "portugal", "germany", "greece",
    "turkey", "türkiye", "iran", "afghanistan", "morocco", "georgia",
    "bulgaria", "armenia", "azerbaijan", "serbia", "croatia",
    "switzerland", "austria", "ukraine", "lebanon", "romania",
)


def classify_area(location: str, region: str) -> str:
    """Only country text; no inferred provenance from taxon/trait."""
    combined = (location or "") + "|" + (region or "")
    lc = combined.casefold()
    for term in TERMS_NORTH:
        if re.search(r"(?<![a-z])" + re.escape(term) + r"(?![a-z])", lc):
            return "North_America"
    for term in TERMS_EAST:
        if re.search(r"(?<![a-z])" + re.escape(term) + r"(?![a-z])", lc):
            return "East_NE_Asia"
    for term in TERMS_WEST:
        if re.search(r"(?<![a-z])" + re.escape(term) + r"(?![a-z])", lc):
            return "West_Palearctic"
    return "Other_or_unresolved"


def rank(row: dict) -> str:
    return hashlib.sha256((SEED + "|" + row["biosample"]).encode("utf-8")).hexdigest()


def build(anchor_per_area: int = 12):
    if anchor_per_area < 1:
        raise ValueError("anchor_per_area must be positive")
    source, samples, taxa = rebuild_panel_and_join()
    if source["n_biosamples"] != 294 or source["n_source_taxon_labels"] != 270:
        raise ValueError("frozen global sample manifest drift")
    strict_taxa = {
        x["analysis_taxon_label"] for x in taxa
        if x["orientation_state_candidate"] in {"U", "D"}
        and x["source_label_taxonomic_review_hold"] == "false"
    }
    assert len(strict_taxa) == 35, "unexpected taxon metadata change: manual review needed"
    # Crucially JOG numbers are defined across ALL 294 original samples first,
    # never renumbered after selecting the pilot acquisition wave.
    sample_rows = []
    for index, r in enumerate(samples, start=1):
        name = r["analysis_taxon_label"]
        is_focal = name in strict_taxa
        area = classify_area(r["location"], r["region"])
        sample_rows.append({
            "full_jog_tip_id": f"JOG{index:04d}",
            "panel_id": r["panel_id"],
            "biosample": r["biosample"],
            "run_accessions": r["run_accessions"],
            "run_count": str(len(r["run_accessions"].split("|"))),
            "assay": r["assay"],
            "source_studies": r["source_studies"],
            "analysis_taxon_label": name,
            "source_location": r["location"],
            "source_region": r["region"],
            "broad_area": area,
            "orientation_candidate": r["orientation_state_candidate"] if is_focal else "",
            "name_review_required": r["name_review_required"],
            "acquisition_tier": "priority_U_D_source" if is_focal else "background_unselected",
            "group_size_at_source_taxon_label": r["n_biosamples_with_same_source_taxon_label"],
            "phenotype_same_voucher_confirmed": "false",
            "climate_centroid_ready": "false",
            "independent_phylogenetic_branch_confirmed": "false",
        })
    priority = [x for x in sample_rows if x["acquisition_tier"] == "priority_U_D_source"]
    if len(priority) != 46 or len({x["analysis_taxon_label"] for x in priority}) != 35:
        raise ValueError("expected 46 samples from 35 source-name-clean U/D taxon labels")

    # Background is selected WITHOUT observing a climate axis or inventing U/D.
    # One sample per source taxon label; candidate labels are excluded.
    backgrounds: dict[str, list[dict]] = defaultdict(list)
    for x in sample_rows:
        if x["analysis_taxon_label"] not in strict_taxa and x["name_review_required"] == "false":
            backgrounds[x["broad_area"]].append(x)
    selected = []
    for area in AREAS:
        seen = set()
        for r in sorted(backgrounds[area], key=rank):
            taxon = r["analysis_taxon_label"]
            if taxon in seen:
                continue
            seen.add(taxon)
            selected.append(r)
            if sum(y["broad_area"] == area for y in selected) >= anchor_per_area:
                break
    for row in selected:
        row["acquisition_tier"] = "trait_blind_geographic_anchor"

    wave = [r for r in sample_rows if r["acquisition_tier"] != "background_unselected"]
    if len({r["biosample"] for r in wave}) != len(wave):
        raise ValueError("duplicate biological sample in acquisition pilot")
    if len({r["full_jog_tip_id"] for r in wave}) != len(wave):
        raise ValueError("duplicate molecular-tip identifier")
    full_runs = [acc for r in sample_rows for acc in r["run_accessions"].split("|")]
    pilot_runs = [acc for r in wave for acc in r["run_accessions"].split("|")]
    if len(set(full_runs)) != 295 or len(set(pilot_runs)) != len(pilot_runs):
        raise ValueError("SRR duplicate / sample run collision")

    # Use this only as a prioritized input-acquisition list; tree must be
    # inferred de novo with proper outgroups, aligned loci and QC.
    missing_climate = sorted({r["analysis_taxon_label"] for r in priority})
    frozen_name_state_lines = sorted({
        r["analysis_taxon_label"] + "\t" + r["orientation_candidate"]
        for r in priority
    })
    if len(frozen_name_state_lines) != 35:
        raise ValueError("unexpected cohort identity after name-state fingerprint")
    cohort_sha = hashlib.sha256(
        ("\n".join(frozen_name_state_lines) + "\n").encode("utf-8")
    ).hexdigest()
    summary = {
        "contract_version": "global_orientation_nuclear_priority_intake_v1",
        "primary_full_nuclear_biosamples": 294,
        "primary_unique_SRRs": 295,
        "source_labels_in_full_nuclear": 270,
        "priority_source_taxon_labels": len(strict_taxa),
        "priority_U": sum(x["orientation_state_candidate"] == "U" for x in taxa
                          if x["analysis_taxon_label"] in strict_taxa),
        "priority_D": sum(x["orientation_state_candidate"] == "D" for x in taxa
                          if x["analysis_taxon_label"] in strict_taxa),
        "priority_biosamples": len(priority),
        "frozen_priority_name_state_sha256": cohort_sha,
        "background_trait_blind_biosamples": len(selected),
        "background_area_counts": dict(sorted(Counter(x["broad_area"] for x in selected).items())),
        "pilot_total_biosamples": len(wave),
        "pilot_unique_SRRs": len(pilot_runs),
        "priority_area_counts_by_taxon": dict(sorted(Counter(
            classify_area(next(r["source_location"] for r in priority if
                               r["analysis_taxon_label"] == taxon),
                          next(r["source_region"] for r in priority if
                               r["analysis_taxon_label"] == taxon))
            for taxon in strict_taxa
        ).items())),
        "sample_tip_mapping": "JOG0001..JOG0294 frozen full-panel ordering; subset never renumbered",
        "anchor_selection": "deterministic SHA256 biosample selection without trait or climate from remaining source-name-clean taxa",
        "nuclear_tree_inferred": False,
        "present_climate_ready": False,
        "dated_tree_ready": False,
        "source_coverage_ready_for_read_acquisition_only": True,
        "status": "REAL_294_SOURCE_PRIORITIZED_FETCH_MANIFEST_NOT_NUCLEAR_TREE",
        "not_licensed": [
            "source specimen head orientation verified",
            "tree inference using 46 tips without global sampling context",
            "U->D transition probabilities",
            "global climate effect",
            "climate change at historical transition times",
        ],
        "tip_climate_join_pending": missing_climate,
    }
    # A full panel with explicitly unresolved rows allows later joined
    # metadata to be matched to future full nuclear JOG IDs without guessing.
    future_tip_join = []
    for row in sample_rows:
        future_tip_join.append({
            "tip_id": row["full_jog_tip_id"],
            "accepted_taxon": "",  # must be authority-resolved, never source guessed
            "source_taxon_label": row["analysis_taxon_label"],
            "biosample": row["biosample"],
            "orientation_state_provisional": row["orientation_candidate"],
            "orientation_state_for_model": "unresolved",
            "bio15": "",
            "bio1": "",
            "biogeographic_region": "",
            "orientation_source": "",
            "climate_source": "",
            "exclusion_reason": "taxonomy_and_climate_and_nuclear_tree_not_jointly_verified",
        })
    return summary, sample_rows, wave, future_tip_join


def write_csv(path, rows, delimiter=","):
    if not rows:
        raise ValueError("cannot write empty manifest")
    with path.open("w", encoding="utf-8", newline="") as h:
        writer = csv.DictWriter(h, fieldnames=list(rows[0]), delimiter=delimiter)
        writer.writeheader()
        writer.writerows(rows)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--outdir", type=Path, required=True)
    p.add_argument("--anchors-per-area", type=int, default=12)
    a = p.parse_args()
    summary, roster, wave, future = build(a.anchors_per_area)
    a.outdir.mkdir(parents=True, exist_ok=True)
    write_csv(a.outdir / "full_294_jog_sample_lookup.csv", roster)
    write_csv(a.outdir / "priority_wave_source_manifest.tsv", wave, delimiter="\t")
    write_csv(a.outdir / "future_tree_tip_climate_join_UNRESOLVED.csv", future)
    (a.outdir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps({k: summary[k] for k in (
        "priority_source_taxon_labels", "priority_biosamples", "frozen_priority_name_state_sha256", "background_trait_blind_biosamples",
        "pilot_total_biosamples", "priority_U", "priority_D", "priority_area_counts_by_taxon",
        "nuclear_tree_inferred")}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
