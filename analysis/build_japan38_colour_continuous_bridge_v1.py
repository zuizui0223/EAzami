#!/usr/bin/env python3
"""Build an exact-concept Japan38 continuous colour bridge from Azami observations.

Only exact paper concepts are promoted. A broad species phenotype may be retained as
binomial-level sensitivity for an infraspecific Japan38 concept, but it is never
silently assigned to that variety/subspecies. Continuous image-derived colour
metrics remain continuous; this builder does not create C/W states.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import statistics
from collections import defaultdict
from pathlib import Path

METRICS = (
    "corolla_lab_lightness_median",
    "corolla_lab_chroma_median",
    "corolla_hue_sin_median",
    "corolla_hue_cos_median",
)


def concept_key(text: str) -> str:
    clean = " ".join((text or "").replace("×", "x").split())
    m = re.match(r"^([A-Z][A-Za-z-]+)\s+([a-z][A-Za-z-]+)", clean)
    if not m:
        raise ValueError(f"cannot parse taxon concept: {text!r}")
    genus, species = m.group(1), m.group(2)
    for rank in ("subsp.", "ssp.", "var.", "f."):
        rm = re.search(rf"(?:^|\s){re.escape(rank)}\s+([a-z][A-Za-z-]+)", clean)
        if rm:
            normalized_rank = "subsp." if rank == "ssp." else rank
            return f"{genus} {species} {normalized_rank} {rm.group(1)}"
    return f"{genus} {species}"


def species_key(text: str) -> str:
    clean = " ".join((text or "").split())
    m = re.match(r"^([A-Z][A-Za-z-]+)\s+([a-z][A-Za-z-]+)", clean)
    if not m:
        raise ValueError(f"cannot parse species binomial: {text!r}")
    return f"{m.group(1)} {m.group(2)}"


def read_members(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as h:
        rows = list(csv.DictReader(h))
    if len(rows) != 38:
        raise ValueError(f"expected 38 Japan38 concepts, found {len(rows)}")
    return rows


def number(value: str):
    try:
        x = float(value)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def mad(values):
    if not values:
        return None
    med = statistics.median(values)
    return statistics.median(abs(x - med) for x in values)


def evidence_depth(n: int) -> str:
    if n >= 10:
        return "moderate_or_better_10plus"
    if n >= 5:
        return "sparse_5_9"
    return "very_sparse_1_4"


def build(members, observation_rows):
    exact_by_taxon = {}
    infraspecific_by_species = defaultdict(list)
    for row in members:
        ckey = concept_key(row["paper_taxon_concept"])
        skey = species_key(row["paper_taxon_concept"])
        if ckey == skey:
            if skey in exact_by_taxon:
                raise ValueError(f"duplicate exact species concept: {skey}")
            exact_by_taxon[skey] = row
        else:
            infraspecific_by_species[skey].append(row)

    all_counts = defaultdict(int)
    usable_counts = defaultdict(int)
    values = {taxon: {m: [] for m in METRICS} for taxon in exact_by_taxon}
    source_taxa = set()

    for row in observation_rows:
        taxon = species_key(row.get("taxon_name", ""))
        source_taxa.add(taxon)
        if taxon not in exact_by_taxon:
            continue
        all_counts[taxon] += 1
        n_usable = number(row.get("corolla_lab_chroma_n_usable_heads", "")) or 0.0
        if n_usable <= 0:
            continue
        usable_counts[taxon] += 1
        for metric in METRICS:
            x = number(row.get(metric, ""))
            if x is not None:
                values[taxon][metric].append(x)

    out = []
    for taxon, member in exact_by_taxon.items():
        n_colour = usable_counts[taxon]
        if n_colour <= 0:
            continue
        item = {
            "paper_japan_member_id": member["paper_japan_member_id"],
            "paper_taxon_concept": concept_key(member["paper_taxon_concept"]),
            "taxon_name": taxon,
            "n_strict_spatial_observations": all_counts[taxon],
            "n_colour_usable_observations": n_colour,
        }
        for metric in METRICS:
            xs = values[taxon][metric]
            base = metric.removesuffix("_median")
            item[f"{base}_species_median"] = statistics.median(xs) if xs else None
            item[f"{base}_species_mad"] = mad(xs)
        hs = item["corolla_hue_sin_species_median"]
        hc = item["corolla_hue_cos_species_median"]
        item["corolla_hue_degrees_species_circular"] = (
            (math.degrees(math.atan2(hs, hc)) + 360.0) % 360.0
            if hs is not None and hc is not None
            else None
        )
        item["evidence_depth"] = evidence_depth(n_colour)
        out.append(item)
    out.sort(key=lambda x: x["paper_japan_member_id"])

    sensitivity = []
    for taxon, rows in infraspecific_by_species.items():
        if taxon not in source_taxa:
            continue
        sensitivity.extend(row["paper_japan_member_id"] for row in rows)
    sensitivity.sort()
    return out, sensitivity


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--membership-audit", type=Path, required=True)
    p.add_argument("--strict-cohort", type=Path, required=True)
    p.add_argument("--output-csv", type=Path, required=True)
    p.add_argument("--output-summary", type=Path, required=True)
    p.add_argument("--source-workflow-run", type=int, required=True)
    p.add_argument("--source-artifact-id", type=int, required=True)
    p.add_argument("--source-artifact-name", required=True)
    p.add_argument("--source-artifact-digest", required=True)
    a = p.parse_args()

    members = read_members(a.membership_audit)
    with a.strict_cohort.open(encoding="utf-8-sig", newline="") as h:
        rows, sensitivity = build(members, csv.DictReader(h))

    fields = [
        "paper_japan_member_id", "paper_taxon_concept", "taxon_name",
        "n_strict_spatial_observations", "n_colour_usable_observations",
        "corolla_lab_lightness_species_median", "corolla_lab_lightness_species_mad",
        "corolla_lab_chroma_species_median", "corolla_lab_chroma_species_mad",
        "corolla_hue_sin_species_median", "corolla_hue_sin_species_mad",
        "corolla_hue_cos_species_median", "corolla_hue_cos_species_mad",
        "corolla_hue_degrees_species_circular", "evidence_depth",
    ]
    a.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with a.output_csv.open("w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    summary = {
        "contract_version": "japan38_colour_continuous_bridge_v1",
        "source": {
            "repo": "zuizui0223/azami",
            "workflow_run": a.source_workflow_run,
            "artifact_id": a.source_artifact_id,
            "artifact_name": a.source_artifact_name,
            "artifact_digest": a.source_artifact_digest,
            "cohort": "strict_spatial_thinned_observations",
        },
        "coverage": {
            "japan38_paper_concepts": 38,
            "exact_japan38_concepts": len(rows),
            "exact_fraction": len(rows) / 38,
            "binomial_level_sensitivity_only_concepts": sensitivity,
            "paper_concepts_represented_at_binomial_level": len(rows) + len(sensitivity),
            "exact_concepts_with_n_colour_usable_ge_10": sum(
                r["n_colour_usable_observations"] >= 10 for r in rows
            ),
            "exact_concepts_with_n_colour_usable_ge_10_ids": [
                r["paper_japan_member_id"] for r in rows
                if r["n_colour_usable_observations"] >= 10
            ],
            "exact_concepts_with_any_colour": [r["paper_japan_member_id"] for r in rows],
        },
        "state_definition": {
            "type": "continuous_image_derived",
            "aggregation": "median across strict-spatial observation-level automated head measurements; MAD retained",
            "discrete_colour_state_frozen": False,
        },
        "claim_boundary": (
            "Exact Japan38 concept-level continuous image-trait bridge only. Broad species phenotypes "
            "are not assigned to infraspecific paper concepts. Image-derived medians do not establish "
            "fixed population colour, ancestral colour, transition direction, or adaptation."
        ),
    }
    a.output_summary.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
