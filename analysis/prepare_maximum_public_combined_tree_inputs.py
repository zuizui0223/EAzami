#!/usr/bin/env python3
"""Prepare the post-admission common-locus 294–296 scenario panel.

This builder cannot run until the independent-gate summary says that EA01 and
CNIPG both passed. EA02 is explicitly excluded as a duplicate-readset control.
All four subset scenarios use one identical baseline∩EA01∩CNIPG locus set.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
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

EXPECTED_INDEPENDENT_SUMMARY = "maximum_public_nuclear_independent_gate_summary_v2"
MINIMUM_COMMON_LOCI = 100
CANDIDATES = {
    "EA01": {
        "tip_id": "PUBEA001",
        "taxon": "Cirsium nipponicum var. yoshinoi",
        "summary_name": "candidate_pack_summary.json",
        "summary_count_field": "strict_no_warning_recovered_loci",
        "expected_strict": 236,
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
    ("cnipg_295", ("CNIPG",)),
    ("ea01_cnipg_296", ("EA01", "CNIPG")),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_independent_gate_summary(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("contract_version") != EXPECTED_INDEPENDENT_SUMMARY:
        raise ValueError("unexpected independent-gate summary contract")
    if data.get("independent_candidate_gate_results") != {"EA01": True, "CNIPG": True}:
        raise ValueError("EA01 and CNIPG must both pass before combined-tree input construction")
    if data.get("both_independent_gates_passed") is not True:
        raise ValueError("both_independent_gates_passed must be true")
    excluded = data.get("excluded_duplicate_controls")
    if not isinstance(excluded, dict) or "EA02" not in excluded:
        raise ValueError("EA02 duplicate-control exclusion missing from independent summary")
    if data.get("combined_296_tree_accepted") is not False:
        raise ValueError("combined 296 tree must not already be accepted")
    if data.get("combined_common_paired_locus_tree_required") is not True:
        raise ValueError("combined common paired-locus tree must be required")
    if data.get("new_china_sampling_freeze_allowed") is not False:
        raise ValueError("new China sampling must remain unfrozen")
    return data


def validate_pack(candidate_id: str, pack: Path) -> list[str]:
    spec = CANDIDATES[candidate_id]
    summary = json.loads((pack / str(spec["summary_name"])).read_text(encoding="utf-8"))
    loci = read_loci(pack / "strict_recovered_loci.txt")
    expected = int(spec["expected_strict"])
    observed = int(summary.get(str(spec["summary_count_field"]), -1))
    if observed != expected or len(loci) != expected:
        raise ValueError(f"{candidate_id} strict-locus count drift")
    if clean(summary.get("tip_id")) != spec["tip_id"]:
        raise ValueError(f"{candidate_id} tip ID drift")
    if candidate_id == "EA01":
        if clean(summary.get("scientific_name")) != spec["taxon"]:
            raise ValueError("EA01 taxon drift")
        if summary.get("pilot_locus_pack_ready") is not True or summary.get("tree_tip_promotion_allowed") is not False:
            raise ValueError("EA01 pack is not at frozen pre-tree state")
    else:
        if summary.get("augmentation_locus_pack_ready") is not True or summary.get("tree_tip_promotion_allowed") is not False:
            raise ValueError("CNIPG pack is not at frozen pre-tree state")
    if len(list((pack / "loci").glob("*.fasta"))) != expected:
        raise ValueError(f"{candidate_id} locus FASTA count drift")
    return loci


def write_primary_runs(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["tip_id", "analysis_taxon_label"])
        writer.writeheader(); writer.writerows(rows)


def scenario_species_map(baseline_species: list[dict[str, str]], candidate_ids: tuple[str, ...]) -> list[dict[str, str]]:
    rows = [dict(row) for row in baseline_species]
    for cid in candidate_ids:
        tip = str(CANDIDATES[cid]["tip_id"]); taxon = str(CANDIDATES[cid]["taxon"])
        hits = [row for row in rows if row["analysis_taxon_label"] == taxon]
        if len(hits) != 1:
            raise ValueError(f"combined gate requires exactly one baseline species row for {cid}")
        hit = hits[0]; tips = [x for x in hit["tip_ids"].split("|") if x]
        if tip in tips: raise ValueError(f"candidate tip already present: {tip}")
        tips.append(tip); hit["tip_ids"] = "|".join(tips); hit["n_tips"] = str(len(tips))
    return rows


def prepare(
    *,
    primary_inputs: Path,
    baseline_manifest: Path,
    baseline_species_map: Path,
    ea01_pack: Path,
    cnipg_pack: Path,
    independent_gate_summary: Path,
    outdir: Path,
    minimum_common_loci: int = MINIMUM_COMMON_LOCI,
) -> dict[str, object]:
    if minimum_common_loci < MINIMUM_COMMON_LOCI:
        raise ValueError(f"minimum_common_loci cannot be relaxed below {MINIMUM_COMMON_LOCI}")
    load_independent_gate_summary(independent_gate_summary)
    baseline = read_baseline_manifest(baseline_manifest, 294)
    baseline_tips = {row["tip_id"] for row in baseline}; baseline_taxa = {row["analysis_taxon_label"] for row in baseline}
    species = read_species_map(baseline_species_map)
    species_tips = {tip for row in species for tip in row["tip_ids"].split("|") if tip}
    if species_tips != baseline_tips: raise ValueError("baseline species map and manifest disagree")
    for cid, spec in CANDIDATES.items():
        if str(spec["taxon"]) not in baseline_taxa: raise ValueError(f"missing baseline taxon label for {cid}")
        if str(spec["tip_id"]) in baseline_tips: raise ValueError(f"candidate tip already in baseline: {cid}")

    packs = {"EA01": ea01_pack, "CNIPG": cnipg_pack}
    locus_sets = {cid: set(validate_pack(cid, pack)) for cid, pack in packs.items()}
    primary_loci = read_loci(primary_inputs / "eligible_loci.txt")
    common = [locus for locus in primary_loci if all(locus in locus_sets[cid] for cid in CANDIDATES)]
    if len(common) < minimum_common_loci:
        raise ValueError(f"Only {len(common)} baseline-EA01-CNIPG common loci; require >= {minimum_common_loci}")

    baseline_run_rows = [{"tip_id": row["tip_id"], "analysis_taxon_label": row["analysis_taxon_label"]} for row in baseline]
    audit: list[dict[str, object]] = []
    for locus in common:
        base_records = read_fasta(primary_inputs / "loci_unaligned" / f"{locus}.fasta")
        names = {name for name, _ in base_records}
        candidate_records: dict[str, tuple[str, str]] = {}
        for cid, pack in packs.items():
            rows = read_fasta(pack / "loci" / f"{locus}.fasta"); tip = str(CANDIDATES[cid]["tip_id"])
            if len(rows) != 1 or rows[0][0] != tip or not rows[0][1]: raise ValueError(f"invalid {cid} FASTA at {locus}")
            if tip in names: raise ValueError(f"candidate tip already in baseline FASTA: {tip}")
            candidate_records[cid] = rows[0]
        for scenario_id, ids in SCENARIOS:
            records = list(base_records) + [candidate_records[cid] for cid in ids]
            write_fasta(outdir / scenario_id / "loci_unaligned" / f"{locus}.fasta", records)
            audit.append({"locus": locus, "scenario_id": scenario_id, "candidate_ids": "|".join(ids), "baseline_records": len(base_records), "scenario_records": len(records), "exact_same_baseline_records": True})

    outdir.mkdir(parents=True, exist_ok=True)
    for scenario_id, ids in SCENARIOS:
        scenario = outdir / scenario_id
        (scenario / "eligible_loci.txt").write_text("".join(f"{x}\n" for x in common), encoding="utf-8")
        run_rows = list(baseline_run_rows) + [{"tip_id": str(CANDIDATES[cid]["tip_id"]), "analysis_taxon_label": str(CANDIDATES[cid]["taxon"])} for cid in ids]
        write_primary_runs(scenario / "primary_runs.csv", run_rows)
        write_species_map(scenario, scenario_species_map(species, ids))

    with (outdir / "paired_locus_audit.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(audit[0])); writer.writeheader(); writer.writerows(audit)
    scenario_rows = [{"scenario_id": sid, "candidate_ids": "|".join(ids), "focal_tip_count": 294 + len(ids), "common_paired_loci": len(common)} for sid, ids in SCENARIOS]
    with (outdir / "scenario_manifest.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(scenario_rows[0])); writer.writeheader(); writer.writerows(scenario_rows)

    result: dict[str, object] = {
        "contract_version": "maximum_public_combined_tree_inputs_v2",
        "source_independent_gate_summary_sha256": sha256(independent_gate_summary),
        "independent_gate_prerequisite_passed": True,
        "baseline_focal_tips": 294,
        "primary_eligible_loci": len(primary_loci),
        "candidate_strict_loci": {cid: len(locus_sets[cid]) for cid in CANDIDATES},
        "baseline_ea01_cnipg_common_paired_loci": len(common),
        "minimum_common_loci": minimum_common_loci,
        "all_four_scenarios_use_identical_locus_set": True,
        "scenario_focal_tip_counts": {sid: 294 + len(ids) for sid, ids in SCENARIOS},
        "scenario_count": 4,
        "ea02_enters_combined_tree": False,
        "new_analysis_taxon_labels_added": 0,
        "combined_tree_acceptance_pre_authorized": False,
        "new_china_sampling_freeze_allowed": False,
        "next_gate": "Infer paired concatenated and source-label ASTRAL trees for baseline294, ea01_295, cnipg_295 and ea01_cnipg_296 separately under accepted BWA and BLASTx baseline modes before any 296-tip acceptance."
    }
    (outdir / "combined_input_summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2)); return result


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--primary-inputs", type=Path, required=True); parser.add_argument("--baseline-manifest", type=Path, required=True); parser.add_argument("--baseline-species-map", type=Path, required=True); parser.add_argument("--ea01-pack", type=Path, required=True); parser.add_argument("--cnipg-pack", type=Path, required=True); parser.add_argument("--independent-gate-summary", type=Path, required=True); parser.add_argument("--outdir", type=Path, required=True); parser.add_argument("--minimum-common-loci", type=int, default=MINIMUM_COMMON_LOCI)
    args = parser.parse_args(); prepare(primary_inputs=args.primary_inputs, baseline_manifest=args.baseline_manifest, baseline_species_map=args.baseline_species_map, ea01_pack=args.ea01_pack, cnipg_pack=args.cnipg_pack, independent_gate_summary=args.independent_gate_summary, outdir=args.outdir, minimum_common_loci=args.minimum_common_loci); return 0


if __name__ == "__main__": raise SystemExit(main())
