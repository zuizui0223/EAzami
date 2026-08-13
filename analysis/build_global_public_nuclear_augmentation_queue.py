#!/usr/bin/env python3
"""Collapse the global public Cirsium SRA audit into biological augmentation candidates.

The SRA audit is run-level.  Phylogenetic tips are biological-sample-level, so
this queue builder prevents a second form of pseudoreplication: an extra run for
an already admitted BioSample must be merged into that tip rather than counted
as a new tip.  New BioSamples are separated into exact-taxon additions versus
independent replicates of taxa already represented in the frozen 294-tip core.

Priority tiers are execution order only. They never auto-admit a sample into the
maximum-public tree and they never define a new mainland sampling list.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping, Sequence

DIRECT = "direct_common_locus_candidate"


def clean(value: object) -> str:
    return str(value or "").strip()


def label(value: object) -> str:
    return " ".join(clean(value).casefold().split())


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [
            {key: clean(value) for key, value in row.items()}
            for row in csv.DictReader(handle)
            if any(clean(value) for value in row.values())
        ]


def number(value: object) -> float | None:
    text = clean(value)
    if not text:
        return None
    try:
        out = float(text)
    except ValueError:
        return None
    return out if math.isfinite(out) else None


def stable_tip_id(biosample: str, run: str) -> str:
    token = biosample or run
    token = re.sub(r"[^A-Za-z0-9]+", "_", token).strip("_")
    if not token:
        raise ValueError("cannot construct stable augmentation tip id")
    return f"AUGSRA_{token}"


def aggregate_runs(
    audit_rows: Sequence[Mapping[str, str]],
    primary_rows: Sequence[Mapping[str, str]],
) -> tuple[list[dict[str, object]], dict[str, object]]:
    if not audit_rows:
        raise ValueError("SRA audit is empty")
    if not primary_rows:
        raise ValueError("primary panel is empty")
    if "common_locus_compatibility_class" not in audit_rows[0]:
        raise ValueError("SRA audit lacks compatibility classification")
    if "biosample" not in primary_rows[0]:
        raise ValueError("primary panel lacks biosample")

    primary_biosamples = {clean(row.get("biosample")) for row in primary_rows if clean(row.get("biosample"))}
    source_labels = {label(row.get("source_taxon_label")) for row in primary_rows if clean(row.get("source_taxon_label"))}
    analysis_labels = {label(row.get("analysis_taxon_label")) for row in primary_rows if clean(row.get("analysis_taxon_label"))}
    primary_labels = source_labels | analysis_labels

    direct = [
        dict(row)
        for row in audit_rows
        if clean(row.get("known_primary_295_srr")).casefold() == "false"
        and clean(row.get("common_locus_compatibility_class")) == DIRECT
    ]
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in direct:
        biosample = clean(row.get("BioSample"))
        run = clean(row.get("Run"))
        if not run:
            continue
        key = f"BS:{biosample}" if biosample else f"RUN:{run}"
        groups[key].append(row)

    queue: list[dict[str, object]] = []
    for _, rows in sorted(groups.items()):
        runs = sorted({clean(row.get("Run")) for row in rows if clean(row.get("Run"))})
        biosamples = sorted({clean(row.get("BioSample")) for row in rows if clean(row.get("BioSample"))})
        biosample = biosamples[0] if len(biosamples) == 1 else ""
        taxa = sorted({clean(row.get("ScientificName")) for row in rows if clean(row.get("ScientificName"))})
        projects = sorted({clean(row.get("BioProject")) for row in rows if clean(row.get("BioProject"))})
        strategies = sorted({clean(row.get("LibraryStrategy")) for row in rows if clean(row.get("LibraryStrategy"))})
        sources = sorted({clean(row.get("LibrarySource")) for row in rows if clean(row.get("LibrarySource"))})
        selections = sorted({clean(row.get("LibrarySelection")) for row in rows if clean(row.get("LibrarySelection"))})
        layouts = sorted({clean(row.get("LibraryLayout")) for row in rows if clean(row.get("LibraryLayout"))})
        platforms = sorted({clean(row.get("Platform")) for row in rows if clean(row.get("Platform"))})

        sizes = [number(row.get("size_MB")) for row in rows]
        sizes_present = [value for value in sizes if value is not None]
        total_size = sum(sizes_present) if sizes_present else 0.0
        positive_size_complete = len(sizes_present) == len(rows) and all(value > 0 for value in sizes_present)
        bases = [number(row.get("bases")) for row in rows]
        total_bases = sum(value for value in bases if value is not None)

        taxon = taxa[0] if len(taxa) == 1 else "|".join(taxa)
        taxon_conflict = len(taxa) != 1
        biosample_missing = not biosample
        biosample_in_primary = bool(biosample and biosample in primary_biosamples)
        exact_taxon_in_primary = bool(len(taxa) == 1 and label(taxa[0]) in primary_labels)
        paired_only = bool(layouts) and set(layouts) == {"PAIRED"}
        bounded = positive_size_complete and total_size <= 2000 and paired_only
        medium = positive_size_complete and total_size <= 5000 and paired_only

        if biosample_in_primary:
            candidate_type = "existing_primary_biosample_extra_run"
            tier = "MERGE_ONLY"
        elif biosample_missing or taxon_conflict:
            candidate_type = "metadata_unresolved"
            tier = "MANUAL_METADATA"
        elif not positive_size_complete:
            candidate_type = "new_biological_sample"
            tier = "MANUAL_SIZE"
        elif bounded and not exact_taxon_in_primary:
            candidate_type = "new_biological_sample_new_exact_taxon"
            tier = "A_NEW_EXACT_TAXON_BOUNDED"
        elif bounded:
            candidate_type = "new_biological_sample_existing_exact_taxon"
            tier = "B_REPLICATE_BOUNDED"
        elif medium and not exact_taxon_in_primary:
            candidate_type = "new_biological_sample_new_exact_taxon"
            tier = "C_NEW_EXACT_TAXON_MEDIUM"
        elif medium:
            candidate_type = "new_biological_sample_existing_exact_taxon"
            tier = "D_REPLICATE_MEDIUM"
        elif not exact_taxon_in_primary:
            candidate_type = "new_biological_sample_new_exact_taxon"
            tier = "E_NEW_EXACT_TAXON_LARGE_OR_NONPAIRED"
        else:
            candidate_type = "new_biological_sample_existing_exact_taxon"
            tier = "F_REPLICATE_LARGE_OR_NONPAIRED"

        queue.append(
            {
                "candidate_id": stable_tip_id(biosample, runs[0]),
                "tip_id_if_admitted": stable_tip_id(biosample, runs[0]),
                "scientific_name": taxon,
                "taxon_conflict": taxon_conflict,
                "biosample": biosample,
                "biosample_missing": biosample_missing,
                "biosample_in_primary_294": biosample_in_primary,
                "exact_taxon_label_in_primary_294": exact_taxon_in_primary,
                "candidate_type": candidate_type,
                "priority_tier": tier,
                "bioprojects": "|".join(projects),
                "run_accessions": "|".join(runs),
                "run_count": len(runs),
                "library_strategies": "|".join(strategies),
                "library_sources": "|".join(sources),
                "library_selections": "|".join(selections),
                "library_layouts": "|".join(layouts),
                "platforms": "|".join(platforms),
                "total_size_mb": round(total_size, 3),
                "positive_size_metadata_complete": positive_size_complete,
                "total_bases": int(total_bases),
                "bounded_ci_pilot_shape": bounded,
                "automatic_tip_admission_allowed": False,
                "new_china_sampling_freeze_allowed": False,
            }
        )

    tier_order = {
        "A_NEW_EXACT_TAXON_BOUNDED": 0,
        "B_REPLICATE_BOUNDED": 1,
        "C_NEW_EXACT_TAXON_MEDIUM": 2,
        "D_REPLICATE_MEDIUM": 3,
        "E_NEW_EXACT_TAXON_LARGE_OR_NONPAIRED": 4,
        "F_REPLICATE_LARGE_OR_NONPAIRED": 5,
        "MANUAL_SIZE": 6,
        "MANUAL_METADATA": 7,
        "MERGE_ONLY": 8,
    }
    queue.sort(
        key=lambda row: (
            tier_order.get(str(row["priority_tier"]), 99),
            str(row["scientific_name"]).casefold(),
            str(row["biosample"]),
            str(row["run_accessions"]),
        )
    )

    new_samples = [row for row in queue if not bool(row["biosample_in_primary_294"]) and not bool(row["biosample_missing"])]
    new_exact = [row for row in new_samples if not bool(row["exact_taxon_label_in_primary_294"]) and not bool(row["taxon_conflict"])]
    replicate = [row for row in new_samples if bool(row["exact_taxon_label_in_primary_294"]) and not bool(row["taxon_conflict"])]
    summary: dict[str, object] = {
        "contract_version": "global_public_nuclear_augmentation_queue_v1",
        "primary_core_biological_tips": len(primary_rows),
        "direct_extra_sra_runs": len(direct),
        "run_groups_after_biosample_collapse": len(queue),
        "new_biological_sample_candidates": len(new_samples),
        "new_exact_taxon_candidates": len(new_exact),
        "existing_exact_taxon_independent_replicates": len(replicate),
        "existing_primary_biosample_extra_run_groups": sum(bool(row["biosample_in_primary_294"]) for row in queue),
        "bounded_paired_positive_size_candidates_le_2000mb": sum(bool(row["bounded_ci_pilot_shape"]) for row in queue),
        "priority_tier_counts": dict(sorted(Counter(str(row["priority_tier"]) for row in queue).items())),
        "new_exact_taxa": sorted({str(row["scientific_name"]) for row in new_exact}),
        "automatic_tip_admission_allowed": False,
        "primary_294_panel_changed": False,
        "new_china_sampling_freeze_allowed": False,
        "admission_rule": (
            "A queue row becomes a phylogenetic tip only after same-Compositae1061 recovery, copy-state/orthology QC, "
            "intersection with the accepted primary locus set, and paired topology sensitivity. MERGE_ONLY rows never become extra tips."
        ),
    }
    return queue, summary


def write_csv(path: Path, rows: Iterable[Mapping[str, object]]) -> None:
    rows = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sra-audit", type=Path, required=True)
    parser.add_argument("--primary-panel", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()

    queue, summary = aggregate_runs(read_csv(args.sra_audit), read_csv(args.primary_panel))
    args.outdir.mkdir(parents=True, exist_ok=True)
    write_csv(args.outdir / "global_public_nuclear_augmentation_queue.csv", queue)
    (args.outdir / "global_public_nuclear_augmentation_queue_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
