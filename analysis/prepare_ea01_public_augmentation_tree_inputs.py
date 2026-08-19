#!/usr/bin/env python3
"""Prepare identical-locus baseline294 vs EA01_295 tree inputs.

This is the post-empirical replacement for the former EA01/EA02 four-scenario
builder. EA02 is retained only as duplicate-readset evidence and never enters
these biological-tip tree inputs.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from prepare_east_asia_public_augmentation_tree_inputs import (
    clean,
    read_baseline_manifest,
    read_fasta,
    read_loci,
    read_species_map,
    write_fasta,
    write_species_map,
)

EXPECTED_CONTRACT = "ea01_public_tree_augmentation_v2"


def load_contract(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("contract_version") != EXPECTED_CONTRACT:
        raise ValueError(f"unexpected EA01 contract: {data.get('contract_version')!r}")
    candidate = data.get("candidate")
    if not isinstance(candidate, dict) or clean(candidate.get("candidate_id")) != "EA01":
        raise ValueError("EA01 contract must define exactly candidate EA01")
    disposition = data.get("ea02_disposition")
    if not isinstance(disposition, dict) or disposition.get("counts_as_independent_tip") is not False:
        raise ValueError("EA02 duplicate-control disposition is not frozen")
    return data


def validate_pack(pack: Path, candidate: dict[str, object]) -> tuple[dict[str, object], list[str]]:
    summary = json.loads((pack / "candidate_pack_summary.json").read_text(encoding="utf-8"))
    for field in ("candidate_id", "tip_id", "scientific_name", "biosample", "run"):
        if clean(summary.get(field)) != clean(candidate.get(field)):
            raise ValueError(f"EA01 {field} drift: {summary.get(field)!r} != {candidate.get(field)!r}")
    loci = read_loci(pack / "strict_recovered_loci.txt")
    expected = int(candidate["strict_no_warning_recovered_loci"])
    if len(loci) != expected or int(summary.get("strict_no_warning_recovered_loci", -1)) != expected:
        raise ValueError("EA01 strict-locus count drift")
    if summary.get("pilot_locus_pack_ready") is not True or summary.get("tree_tip_promotion_allowed") is not False:
        raise ValueError("EA01 pack is not at the frozen pre-tree state")
    if len(list((pack / "loci").glob("*.fasta"))) != expected:
        raise ValueError("EA01 locus FASTA count drift")
    return summary, loci


def write_primary_runs(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["tip_id", "analysis_taxon_label"])
        writer.writeheader()
        writer.writerows(rows)


def prepare(
    *,
    primary_inputs: Path,
    baseline_manifest: Path,
    baseline_species_map: Path,
    ea01_pack: Path,
    contract_path: Path,
    outdir: Path,
) -> dict[str, object]:
    contract = load_contract(contract_path)
    candidate = contract["candidate"]
    assert isinstance(candidate, dict)
    baseline_spec = contract["baseline"]
    assert isinstance(baseline_spec, dict)
    baseline_n = int(baseline_spec["biological_tips"])
    baseline_rows = read_baseline_manifest(baseline_manifest, baseline_n)
    baseline_tips = {row["tip_id"] for row in baseline_rows}
    baseline_taxa = {row["analysis_taxon_label"] for row in baseline_rows}
    species_rows = read_species_map(baseline_species_map)
    mapped = {tip for row in species_rows for tip in row["tip_ids"].split("|") if tip}
    if mapped != baseline_tips:
        raise ValueError("baseline species map and manifest disagree")

    summary, candidate_loci = validate_pack(ea01_pack, candidate)
    tip = clean(summary["tip_id"])
    taxon = clean(summary["scientific_name"])
    if tip in baseline_tips:
        raise ValueError("EA01 tip already occurs in baseline")
    if bool(candidate.get("baseline_exact_taxon_expected")) != (taxon in baseline_taxa):
        raise ValueError("EA01 exact-taxon baseline expectation failed")

    primary_loci = read_loci(primary_inputs / "eligible_loci.txt")
    if len(primary_loci) < int(baseline_spec["minimum_primary_loci_to_launch"]):
        raise ValueError("baseline accepted locus set is below launch threshold")
    candidate_set = set(candidate_loci)
    paired = [locus for locus in primary_loci if locus in candidate_set]
    minimum = int(contract["minimum_paired_loci"])
    if len(paired) < minimum:
        raise ValueError(f"Only {len(paired)} paired EA01 loci; require >= {minimum}")

    scenarios = (("baseline294", False), ("ea01_295", True))
    audit: list[dict[str, object]] = []
    for locus in paired:
        baseline_records = read_fasta(primary_inputs / "loci_unaligned" / f"{locus}.fasta")
        names = {name for name, _ in baseline_records}
        if tip in names:
            raise ValueError(f"EA01 tip already in baseline FASTA at {locus}")
        rows = read_fasta(ea01_pack / "loci" / f"{locus}.fasta")
        if len(rows) != 1 or rows[0][0] != tip:
            raise ValueError(f"invalid EA01 FASTA at {locus}")
        for scenario_id, add_candidate in scenarios:
            records = list(baseline_records) + ([rows[0]] if add_candidate else [])
            write_fasta(outdir / scenario_id / "loci_unaligned" / f"{locus}.fasta", records)
            audit.append({
                "locus": locus,
                "scenario_id": scenario_id,
                "baseline_records": len(baseline_records),
                "candidate_ids": "EA01" if add_candidate else "",
                "scenario_records": len(records),
                "exact_same_baseline_records": True,
            })

    baseline_run_rows = [
        {"tip_id": row["tip_id"], "analysis_taxon_label": row["analysis_taxon_label"]}
        for row in baseline_rows
    ]
    for scenario_id, add_candidate in scenarios:
        scenario = outdir / scenario_id
        (scenario / "eligible_loci.txt").write_text("".join(f"{x}\n" for x in paired), encoding="utf-8")
        run_rows = list(baseline_run_rows)
        species_out = [dict(row) for row in species_rows]
        if add_candidate:
            run_rows.append({"tip_id": tip, "analysis_taxon_label": taxon})
            hits = [row for row in species_out if row["analysis_taxon_label"] == taxon]
            if len(hits) != 1:
                raise ValueError(f"expected one baseline species-map row for {taxon}")
            hit = hits[0]
            tips = [x for x in hit["tip_ids"].split("|") if x]
            tips.append(tip)
            hit["tip_ids"] = "|".join(tips)
            hit["n_tips"] = str(len(tips))
        write_primary_runs(scenario / "primary_runs.csv", run_rows)
        write_species_map(scenario, species_out)

    outdir.mkdir(parents=True, exist_ok=True)
    with (outdir / "paired_locus_audit.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(audit[0]))
        writer.writeheader()
        writer.writerows(audit)
    with (outdir / "scenario_manifest.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["scenario_id", "candidate_ids", "focal_tip_count", "paired_loci"])
        writer.writeheader()
        writer.writerow({"scenario_id": "baseline294", "candidate_ids": "", "focal_tip_count": 294, "paired_loci": len(paired)})
        writer.writerow({"scenario_id": "ea01_295", "candidate_ids": "EA01", "focal_tip_count": 295, "paired_loci": len(paired)})

    result: dict[str, object] = {
        "contract_version": "ea01_public_paired_augmentation_inputs_v2",
        "source_contract_version": contract["contract_version"],
        "baseline_focal_tips": baseline_n,
        "baseline_eligible_loci": len(primary_loci),
        "ea01_strict_loci": len(candidate_loci),
        "paired_loci": len(paired),
        "minimum_paired_loci": minimum,
        "same_locus_set_across_both_scenarios": True,
        "scenario_focal_tip_counts": {"baseline294": 294, "ea01_295": 295},
        "paired_tree_inputs_ready": True,
        "ea01_tree_tip_promotion_allowed": False,
        "ea02_enters_biological_tree_inputs": False,
        "new_china_sampling_freeze_allowed": False,
    }
    (outdir / "paired_augmentation_summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--primary-inputs", type=Path, required=True)
    parser.add_argument("--baseline-manifest", type=Path, required=True)
    parser.add_argument("--baseline-species-map", type=Path, required=True)
    parser.add_argument("--ea01-pack", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    prepare(
        primary_inputs=args.primary_inputs,
        baseline_manifest=args.baseline_manifest,
        baseline_species_map=args.baseline_species_map,
        ea01_pack=args.ea01_pack,
        contract_path=args.contract,
        outdir=args.outdir,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
