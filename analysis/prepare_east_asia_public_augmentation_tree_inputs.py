#!/usr/bin/env python3
"""Prepare one frozen paired locus set for EA01/EA02 public-tree augmentation.

All scenarios are derived from the *same* intersection of the accepted 294-tip
baseline loci and both candidate strict packs. Thus any topology difference is
caused by adding tips, not by changing the locus set.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Iterable, Mapping

EXPECTED_CONTRACT = "east_asia_public_tree_augmentation_v1"


def clean(value: object) -> str:
    return str(value or "").strip()


def read_fasta(path: Path) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    name: str | None = None
    seq: list[str] = []
    with path.open(encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line:
                continue
            if line.startswith(">"):
                if name is not None:
                    rows.append((name, "".join(seq).upper()))
                name = line[1:].split()[0]
                seq = []
            else:
                seq.append(line)
    if name is not None:
        rows.append((name, "".join(seq).upper()))
    if not rows:
        raise ValueError(f"empty FASTA: {path}")
    if len({name for name, _ in rows}) != len(rows):
        raise ValueError(f"duplicate FASTA names: {path}")
    if any(not seq for _, seq in rows):
        raise ValueError(f"empty FASTA sequence: {path}")
    return rows


def write_fasta(path: Path, rows: Iterable[tuple[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for name, seq in rows:
            handle.write(f">{name}\n")
            for start in range(0, len(seq), 80):
                handle.write(seq[start:start + 80] + "\n")


def read_loci(path: Path) -> list[str]:
    rows = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows or len(rows) != len(set(rows)):
        raise ValueError(f"locus list empty or duplicated: {path}")
    return rows


def load_contract(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("contract_version") != EXPECTED_CONTRACT:
        raise ValueError(f"unexpected augmentation contract: {data.get('contract_version')!r}")
    candidates = data.get("candidates")
    if not isinstance(candidates, list) or {clean(x.get("candidate_id")) for x in candidates if isinstance(x, dict)} != {"EA01", "EA02"}:
        raise ValueError("augmentation contract must define exactly EA01 and EA02")
    return data


def candidate_contract(contract: Mapping[str, object], candidate_id: str) -> dict[str, object]:
    for row in contract["candidates"]:  # type: ignore[index]
        if isinstance(row, dict) and clean(row.get("candidate_id")) == candidate_id:
            return row
    raise ValueError(f"candidate missing from contract: {candidate_id}")


def validate_pack(pack: Path, expected: Mapping[str, object]) -> tuple[dict[str, object], list[str]]:
    summary_path = pack / "candidate_pack_summary.json"
    locus_path = pack / "strict_recovered_loci.txt"
    if not summary_path.is_file() or not locus_path.is_file():
        raise ValueError(f"candidate pack incomplete: {pack}")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    for field in ("candidate_id", "tip_id", "scientific_name", "biosample", "run"):
        if clean(summary.get(field)) != clean(expected.get(field)):
            raise ValueError(
                f"candidate pack {field} mismatch: {summary.get(field)!r} != {expected.get(field)!r}"
            )
    loci = read_loci(locus_path)
    if int(summary.get("strict_no_warning_recovered_loci", -1)) != len(loci):
        raise ValueError("strict locus count differs from candidate summary")
    if len(loci) != int(expected.get("strict_no_warning_recovered_loci", -1)):
        raise ValueError("strict locus count differs from frozen augmentation contract")
    if not summary.get("pilot_locus_pack_ready"):
        raise ValueError("candidate pack did not pass the public SRA pilot gate")
    if summary.get("tree_tip_promotion_allowed"):
        raise ValueError("candidate pack improperly pre-authorizes tree-tip promotion")
    return summary, loci


def read_baseline_manifest(path: Path, expected_n: int) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = [{key: clean(value) for key, value in row.items()} for row in csv.DictReader(handle)]
    required = {"tip_id", "analysis_taxon_label"}
    if not rows or not required <= set(rows[0]):
        raise ValueError(f"baseline manifest missing {sorted(required - set(rows[0]) if rows else required)}")
    if len(rows) != expected_n or len({row["tip_id"] for row in rows}) != expected_n:
        raise ValueError(f"expected {expected_n} unique baseline focal tips")
    return rows


def read_species_map(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = [{key: clean(value) for key, value in row.items()} for row in csv.DictReader(handle)]
    required = {"species_id", "analysis_taxon_label", "tip_ids", "n_tips"}
    if not rows or not required <= set(rows[0]):
        raise ValueError(f"species map missing {sorted(required - set(rows[0]) if rows else required)}")
    if len({row["species_id"] for row in rows}) != len(rows):
        raise ValueError("duplicate species_id in baseline map")
    seen: set[str] = set()
    for row in rows:
        tips = [x for x in row["tip_ids"].split("|") if x]
        if len(tips) != int(row["n_tips"]) or len(tips) != len(set(tips)):
            raise ValueError(f"species map count mismatch for {row['species_id']}")
        if seen & set(tips):
            raise ValueError("tip appears in multiple baseline species-map rows")
        seen.update(tips)
    return rows


def write_species_map(outdir: Path, rows: list[dict[str, str]]) -> None:
    with (outdir / "astral_species_map.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["species_id", "analysis_taxon_label", "tip_ids", "n_tips"])
        writer.writeheader()
        writer.writerows(rows)
    lines = [f"{row['species_id']}:{','.join(row['tip_ids'].split('|'))}" for row in rows]
    lines.extend(["OUTGROUP_lett:OUTGROUP_lett", "OUTGROUP_sunf:OUTGROUP_sunf"])
    (outdir / "astral_map.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def scenario_rows(contract: Mapping[str, object]) -> list[dict[str, object]]:
    scenarios = contract.get("scenarios")
    if not isinstance(scenarios, list) or len(scenarios) != 4:
        raise ValueError("contract must define four paired scenarios")
    out: list[dict[str, object]] = []
    names: set[str] = set()
    for row in scenarios:
        if not isinstance(row, dict):
            raise ValueError("invalid scenario row")
        name = clean(row.get("scenario_id"))
        candidates = row.get("candidate_ids")
        if not name or name in names or not isinstance(candidates, list):
            raise ValueError("invalid/duplicate scenario")
        ids = [clean(x) for x in candidates]
        if any(x not in {"EA01", "EA02"} for x in ids) or len(ids) != len(set(ids)):
            raise ValueError(f"invalid candidate IDs in {name}")
        names.add(name)
        out.append({"scenario_id": name, "candidate_ids": ids})
    expected = {(), ("EA01",), ("EA02",), ("EA01", "EA02")}
    got = {tuple(row["candidate_ids"]) for row in out}
    if got != expected:
        raise ValueError(f"scenario candidate sets drift: {got}")
    return out


def prepare(
    primary_inputs: Path,
    baseline_manifest: Path,
    baseline_species_map: Path,
    ea01_pack: Path,
    ea02_pack: Path,
    contract_path: Path,
    outdir: Path,
) -> dict[str, object]:
    contract = load_contract(contract_path)
    minimum = int(contract["minimum_joint_paired_loci"])
    baseline_expected = int(contract["baseline"]["biological_tips"])  # type: ignore[index]
    baseline_rows = read_baseline_manifest(baseline_manifest, baseline_expected)
    baseline_taxa = {row["analysis_taxon_label"] for row in baseline_rows}
    baseline_species_rows = read_species_map(baseline_species_map)
    mapped_baseline_tips = {tip for row in baseline_species_rows for tip in row["tip_ids"].split("|") if tip}
    if mapped_baseline_tips != {row["tip_id"] for row in baseline_rows}:
        raise ValueError("baseline species map and baseline manifest contain different focal tips")
    primary_loci = read_loci(primary_inputs / "eligible_loci.txt")
    if len(primary_loci) < int(contract["baseline"]["minimum_primary_loci_to_launch"]):  # type: ignore[index]
        raise ValueError("baseline accepted locus set is below its frozen launch threshold")

    pack_by_id = {"EA01": ea01_pack, "EA02": ea02_pack}
    meta: dict[str, dict[str, object]] = {}
    locus_sets: dict[str, set[str]] = {}
    for cid, pack in pack_by_id.items():
        summary, loci = validate_pack(pack, candidate_contract(contract, cid))
        meta[cid] = summary
        locus_sets[cid] = set(loci)
        expected = candidate_contract(contract, cid)
        taxon = clean(summary["scientific_name"])
        exact_present = taxon in baseline_taxa
        if bool(expected.get("baseline_exact_taxon_expected")) != exact_present:
            raise ValueError(f"{cid} baseline exact-taxon expectation failed for {taxon}")

    joint = [
        locus for locus in primary_loci
        if locus in locus_sets["EA01"] and locus in locus_sets["EA02"]
    ]
    if len(joint) < minimum:
        raise ValueError(f"Only {len(joint)} joint paired loci; require >= {minimum}")

    scenarios = scenario_rows(contract)
    audit_rows: list[dict[str, object]] = []
    for locus in joint:
        primary_path = primary_inputs / "loci_unaligned" / f"{locus}.fasta"
        primary = read_fasta(primary_path)
        primary_names = {name for name, _ in primary}
        if any(clean(meta[cid]["tip_id"]) in primary_names for cid in ("EA01", "EA02")):
            raise ValueError(f"augmentation tip already occurs in baseline at {locus}")

        aug_records: dict[str, tuple[str, str]] = {}
        for cid in ("EA01", "EA02"):
            rows = read_fasta(pack_by_id[cid] / "loci" / f"{locus}.fasta")
            tip = clean(meta[cid]["tip_id"])
            if len(rows) != 1 or rows[0][0] != tip:
                raise ValueError(f"invalid {cid} candidate FASTA at {locus}")
            aug_records[cid] = rows[0]

        for scenario in scenarios:
            sid = clean(scenario["scenario_id"])
            ids = scenario["candidate_ids"]  # type: ignore[assignment]
            rows = list(primary) + [aug_records[cid] for cid in ids]  # type: ignore[index]
            write_fasta(outdir / sid / "loci_unaligned" / f"{locus}.fasta", rows)
            audit_rows.append({
                "locus": locus,
                "scenario_id": sid,
                "baseline_records": len(primary),
                "candidate_ids": "|".join(ids),  # type: ignore[arg-type]
                "scenario_records": len(rows),
                "exact_same_baseline_records": True,
                "ea01_nt": len(aug_records["EA01"][1]) if "EA01" in ids else 0,
                "ea02_nt": len(aug_records["EA02"][1]) if "EA02" in ids else 0,
            })

    outdir.mkdir(parents=True, exist_ok=True)
    for scenario in scenarios:
        sid = clean(scenario["scenario_id"])
        (outdir / sid / "eligible_loci.txt").write_text(
            "".join(f"{locus}\n" for locus in joint), encoding="utf-8"
        )

    with (outdir / "paired_locus_audit.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(audit_rows[0]))
        writer.writeheader()
        writer.writerows(audit_rows)

    scenario_out: list[dict[str, object]] = []
    for scenario in scenarios:
        ids = scenario["candidate_ids"]  # type: ignore[assignment]
        sid = clean(scenario["scenario_id"])
        run_rows = [{"tip_id": row["tip_id"], "analysis_taxon_label": row["analysis_taxon_label"]} for row in baseline_rows]
        for cid in ids:  # type: ignore[assignment]
            run_rows.append({
                "tip_id": clean(meta[cid]["tip_id"]),
                "analysis_taxon_label": clean(meta[cid]["scientific_name"]),
            })
        with (outdir / sid / "primary_runs.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["tip_id", "analysis_taxon_label"])
            writer.writeheader()
            writer.writerows(run_rows)

        species_rows = [dict(row) for row in baseline_species_rows]
        for cid in ids:  # type: ignore[assignment]
            tip = clean(meta[cid]["tip_id"])
            taxon = clean(meta[cid]["scientific_name"])
            hits = [row for row in species_rows if row["analysis_taxon_label"] == taxon]
            if hits:
                if len(hits) != 1:
                    raise ValueError(f"multiple baseline species-map rows for {taxon}")
                hit = hits[0]
                tips = [x for x in hit["tip_ids"].split("|") if x] + [tip]
                hit["tip_ids"] = "|".join(tips)
                hit["n_tips"] = str(len(tips))
            else:
                species_rows.append({
                    "species_id": f"AUG_{cid}",
                    "analysis_taxon_label": taxon,
                    "tip_ids": tip,
                    "n_tips": "1",
                })
        write_species_map(outdir / sid, species_rows)
        scenario_out.append({
            "scenario_id": scenario["scenario_id"],
            "candidate_ids": "|".join(ids),  # type: ignore[arg-type]
            "focal_tip_count": baseline_expected + len(ids),  # type: ignore[arg-type]
            "paired_loci": len(joint),
        })
    with (outdir / "scenario_manifest.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(scenario_out[0]))
        writer.writeheader()
        writer.writerows(scenario_out)

    summary: dict[str, object] = {
        "contract_version": "east_asia_public_paired_augmentation_inputs_v1",
        "source_contract_version": contract["contract_version"],
        "baseline_focal_tips": baseline_expected,
        "baseline_eligible_loci": len(primary_loci),
        "ea01_strict_loci": len(locus_sets["EA01"]),
        "ea02_strict_loci": len(locus_sets["EA02"]),
        "ea01_is_subset_of_ea02_strict_loci": locus_sets["EA01"] <= locus_sets["EA02"],
        "joint_paired_loci": len(joint),
        "minimum_joint_paired_loci": minimum,
        "same_locus_set_across_all_scenarios": True,
        "scenario_focal_tip_counts": {
            clean(row["scenario_id"]): baseline_expected + len(row["candidate_ids"])  # type: ignore[arg-type]
            for row in scenarios
        },
        "paired_tree_inputs_ready": True,
        "primary_294_tree_superseded": False,
        "ea01_tree_tip_promotion_allowed": False,
        "ea02_tree_tip_promotion_allowed": False,
        "promotion_requires": contract["promotion_requires"],
        "new_china_sampling_freeze_allowed": False,
    }
    (outdir / "paired_augmentation_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--primary-inputs", type=Path, required=True)
    parser.add_argument("--baseline-manifest", type=Path, required=True)
    parser.add_argument("--baseline-species-map", type=Path, required=True)
    parser.add_argument("--ea01-pack", type=Path, required=True)
    parser.add_argument("--ea02-pack", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.primary_inputs, args.baseline_manifest, args.baseline_species_map, args.ea01_pack, args.ea02_pack, args.contract, args.outdir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
