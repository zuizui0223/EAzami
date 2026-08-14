#!/usr/bin/env python3
"""Prepare the post-admission common-locus 294–297 scenario panel.

This builder is intentionally fail-closed. It cannot run until the frozen
independent-gate summary says that EA01, EA02 and CNIPG each passed their own
predeclared gates. It then intersects the accepted baseline loci with all three
candidate packs and writes every subset scenario on one identical locus set.

The output is tree *input* only. It does not pre-authorize a 296/297 tree. Final
combined acceptance still requires concatenated and source-label ASTRAL
backbone checks in both BWA and BLASTx baseline mapping modes.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Mapping

from prepare_east_asia_public_augmentation_tree_inputs import (
    clean,
    read_baseline_manifest,
    read_fasta,
    read_loci,
    read_species_map,
    write_fasta,
    write_species_map,
)

EXPECTED_INDEPENDENT_SUMMARY = "maximum_public_nuclear_independent_gate_summary_v1"
MINIMUM_COMMON_LOCI = 100
CANDIDATES = {
    "EA01": {
        "tip_id": "PUBEA001",
        "taxon": "Cirsium nipponicum var. yoshinoi",
        "summary_name": "candidate_pack_summary.json",
        "summary_count_field": "strict_no_warning_recovered_loci",
        "expected_strict": 236,
    },
    "EA02": {
        "tip_id": "PUBEA002",
        "taxon": "Cirsium sairamense",
        "summary_name": "candidate_pack_summary.json",
        "summary_count_field": "strict_no_warning_recovered_loci",
        "expected_strict": 239,
    },
    "CNIPG": {
        "tip_id": "AUG_ULLEUNG_CNIP2024",
        "taxon": "Cirsium nipponicum",
        "summary_name": "cirsium_nipponicum_comp1061_locus_pack_summary.json",
        "summary_count_field": "strict_recovered_loci",
        "expected_strict": 180,
    },
}
SCENARIOS = (
    ("baseline294", ()),
    ("ea01_295", ("EA01",)),
    ("ea02_295", ("EA02",)),
    ("cnipg_295", ("CNIPG",)),
    ("ea01_ea02_296", ("EA01", "EA02")),
    ("ea01_cnipg_296", ("EA01", "CNIPG")),
    ("ea02_cnipg_296", ("EA02", "CNIPG")),
    ("ea01_ea02_cnipg_297", ("EA01", "EA02", "CNIPG")),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_independent_gate_summary(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("contract_version") != EXPECTED_INDEPENDENT_SUMMARY:
        raise ValueError("unexpected independent-gate summary contract")
    expected = {"EA01": True, "EA02": True, "CNIPG": True}
    if data.get("independent_candidate_gate_results") != expected:
        raise ValueError("all three independent candidate gates must pass before combined-tree input construction")
    if data.get("all_three_independent_gates_passed") is not True:
        raise ValueError("all_three_independent_gates_passed must be true")
    if data.get("combined_296_or_297_tree_accepted") is not False:
        raise ValueError("combined tree must not already be marked accepted")
    if data.get("combined_common_paired_locus_tree_required") is not True:
        raise ValueError("combined common paired-locus tree must be explicitly required")
    if data.get("new_china_sampling_freeze_allowed") is not False:
        raise ValueError("new China sampling must remain unfrozen at this gate")
    return data


def validate_pack(candidate_id: str, pack: Path) -> tuple[list[str], tuple[str, str]]:
    spec = CANDIDATES[candidate_id]
    summary = json.loads((pack / str(spec["summary_name"])).read_text(encoding="utf-8"))
    loci = read_loci(pack / "strict_recovered_loci.txt")
    expected = int(spec["expected_strict"])
    observed = int(summary.get(str(spec["summary_count_field"]), -1))
    if observed != expected or len(loci) != expected:
        raise ValueError(f"{candidate_id} strict-locus count drift: summary={observed}, list={len(loci)}, expected={expected}")
    if clean(summary.get("tip_id")) != spec["tip_id"]:
        raise ValueError(f"{candidate_id} tip ID drift")
    if candidate_id in {"EA01", "EA02"}:
        if clean(summary.get("scientific_name")) != spec["taxon"]:
            raise ValueError(f"{candidate_id} taxon drift")
        if summary.get("pilot_locus_pack_ready") is not True or summary.get("tree_tip_promotion_allowed") is not False:
            raise ValueError(f"{candidate_id} pack is not at the frozen pre-tree state")
    else:
        if summary.get("augmentation_locus_pack_ready") is not True or summary.get("tree_tip_promotion_allowed") is not False:
            raise ValueError("CNIPG pack is not at the frozen pre-tree state")
    if len(list((pack / "loci").glob("*.fasta"))) != expected:
        raise ValueError(f"{candidate_id} locus FASTA count drift")
    return loci, (str(spec["tip_id"]), str(spec["taxon"]))


def write_primary_runs(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["tip_id", "analysis_taxon_label"])
        writer.writeheader()
        writer.writerows(rows)


def scenario_species_map(
    baseline_species: list[dict[str, str]],
    candidate_ids: tuple[str, ...],
) -> list[dict[str, str]]:
    rows = [dict(row) for row in baseline_species]
    for cid in candidate_ids:
        tip = str(CANDIDATES[cid]["tip_id"])
        taxon = str(CANDIDATES[cid]["taxon"])
        hits = [row for row in rows if row["analysis_taxon_label"] == taxon]
        if len(hits) != 1:
            raise ValueError(f"combined gate requires exactly one existing source-label row for {cid} taxon {taxon!r}")
        hit = hits[0]
        tips = [x for x in hit["tip_ids"].split("|") if x]
        if tip in tips:
            raise ValueError(f"candidate tip already present in baseline species map: {tip}")
        tips.append(tip)
        hit["tip_ids"] = "|".join(tips)
        hit["n_tips"] = str(len(tips))
    return rows


def prepare(
    *,
    primary_inputs: Path,
    baseline_manifest: Path,
    baseline_species_map: Path,
    ea01_pack: Path,
    ea02_pack: Path,
    cnipg_pack: Path,
    independent_gate_summary: Path,
    outdir: Path,
    minimum_common_loci: int = MINIMUM_COMMON_LOCI,
) -> dict[str, object]:
    if minimum_common_loci < MINIMUM_COMMON_LOCI:
        raise ValueError(f"minimum_common_loci cannot be relaxed below {MINIMUM_COMMON_LOCI}")
    gate = load_independent_gate_summary(independent_gate_summary)
    baseline = read_baseline_manifest(baseline_manifest, 294)
    baseline_tips = {row["tip_id"] for row in baseline}
    baseline_taxa = {row["analysis_taxon_label"] for row in baseline}
    species = read_species_map(baseline_species_map)
    species_tips = {tip for row in species for tip in row["tip_ids"].split("|") if tip}
    if species_tips != baseline_tips:
        raise ValueError("baseline species map and manifest disagree")
    for cid, spec in CANDIDATES.items():
        if str(spec["taxon"]) not in baseline_taxa:
            raise ValueError(f"combined gate expects an existing baseline taxon label for {cid}: {spec['taxon']}")
        if str(spec["tip_id"]) in baseline_tips:
            raise ValueError(f"candidate tip already present in 294-tip baseline: {spec['tip_id']}")

    packs = {"EA01": ea01_pack, "EA02": ea02_pack, "CNIPG": cnipg_pack}
    locus_sets: dict[str, set[str]] = {}
    for cid, pack in packs.items():
        loci, _ = validate_pack(cid, pack)
        locus_sets[cid] = set(loci)

    primary_loci = read_loci(primary_inputs / "eligible_loci.txt")
    common = [
        locus for locus in primary_loci
        if all(locus in locus_sets[cid] for cid in CANDIDATES)
    ]
    if len(common) < minimum_common_loci:
        raise ValueError(f"Only {len(common)} four-way common paired loci; require >= {minimum_common_loci}")

    baseline_run_rows = [
        {"tip_id": row["tip_id"], "analysis_taxon_label": row["analysis_taxon_label"]}
        for row in baseline
    ]
    audit: list[dict[str, object]] = []
    for locus in common:
        baseline_records = read_fasta(primary_inputs / "loci_unaligned" / f"{locus}.fasta")
        names = {name for name, _ in baseline_records}
        if len(names) != len(baseline_records):
            raise ValueError(f"duplicate baseline record at {locus}")
        candidate_records: dict[str, tuple[str, str]] = {}
        for cid, pack in packs.items():
            rows = read_fasta(pack / "loci" / f"{locus}.fasta")
            tip = str(CANDIDATES[cid]["tip_id"])
            if len(rows) != 1 or rows[0][0] != tip or not rows[0][1]:
                raise ValueError(f"invalid {cid} FASTA at {locus}")
            if tip in names:
                raise ValueError(f"candidate tip already in baseline FASTA at {locus}: {tip}")
            candidate_records[cid] = rows[0]

        for scenario_id, ids in SCENARIOS:
            records = list(baseline_records) + [candidate_records[cid] for cid in ids]
            write_fasta(outdir / scenario_id / "loci_unaligned" / f"{locus}.fasta", records)
            audit.append({
                "locus": locus,
                "scenario_id": scenario_id,
                "candidate_ids": "|".join(ids),
                "baseline_records": len(baseline_records),
                "scenario_records": len(records),
                "exact_same_baseline_records": True,
            })

    outdir.mkdir(parents=True, exist_ok=True)
    for scenario_id, ids in SCENARIOS:
        scenario = outdir / scenario_id
        (scenario / "eligible_loci.txt").write_text("".join(f"{locus}\n" for locus in common), encoding="utf-8")
        run_rows = list(baseline_run_rows) + [
            {
                "tip_id": str(CANDIDATES[cid]["tip_id"]),
                "analysis_taxon_label": str(CANDIDATES[cid]["taxon"]),
            }
            for cid in ids
        ]
        write_primary_runs(scenario / "primary_runs.csv", run_rows)
        write_species_map(scenario, scenario_species_map(species, ids))

    with (outdir / "paired_locus_audit.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(audit[0]))
        writer.writeheader()
        writer.writerows(audit)

    scenario_rows = [
        {
            "scenario_id": scenario_id,
            "candidate_ids": "|".join(ids),
            "focal_tip_count": 294 + len(ids),
            "common_paired_loci": len(common),
        }
        for scenario_id, ids in SCENARIOS
    ]
    with (outdir / "scenario_manifest.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(scenario_rows[0]))
        writer.writeheader()
        writer.writerows(scenario_rows)

    summary: dict[str, object] = {
        "contract_version": "maximum_public_combined_tree_inputs_v1",
        "source_independent_gate_summary_sha256": sha256(independent_gate_summary),
        "independent_gate_prerequisite_passed": True,
        "baseline_focal_tips": 294,
        "primary_eligible_loci": len(primary_loci),
        "candidate_strict_loci": {cid: len(locus_sets[cid]) for cid in CANDIDATES},
        "four_way_common_paired_loci": len(common),
        "minimum_four_way_common_loci": minimum_common_loci,
        "all_eight_scenarios_use_identical_locus_set": True,
        "scenario_focal_tip_counts": {scenario_id: 294 + len(ids) for scenario_id, ids in SCENARIOS},
        "scenario_count": len(SCENARIOS),
        "new_analysis_taxon_labels_added": 0,
        "combined_tree_acceptance_pre_authorized": False,
        "new_china_sampling_freeze_allowed": False,
        "next_gate": (
            "Infer concatenated and source-label ASTRAL trees for all eight scenarios on this identical locus set "
            "separately for BWA and BLASTx baseline mapping modes; require shared-294 backbone invariance and "
            "the predeclared same-taxon candidate placement safeguards before any combined 296/297 acceptance."
        ),
    }
    (outdir / "combined_input_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--primary-inputs", type=Path, required=True)
    parser.add_argument("--baseline-manifest", type=Path, required=True)
    parser.add_argument("--baseline-species-map", type=Path, required=True)
    parser.add_argument("--ea01-pack", type=Path, required=True)
    parser.add_argument("--ea02-pack", type=Path, required=True)
    parser.add_argument("--cnipg-pack", type=Path, required=True)
    parser.add_argument("--independent-gate-summary", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--minimum-common-loci", type=int, default=MINIMUM_COMMON_LOCI)
    args = parser.parse_args()
    prepare(
        primary_inputs=args.primary_inputs,
        baseline_manifest=args.baseline_manifest,
        baseline_species_map=args.baseline_species_map,
        ea01_pack=args.ea01_pack,
        ea02_pack=args.ea02_pack,
        cnipg_pack=args.cnipg_pack,
        independent_gate_summary=args.independent_gate_summary,
        outdir=args.outdir,
        minimum_common_loci=args.minimum_common_loci,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
