#!/usr/bin/env python3
"""Prepare paired baseline/augmentation locus sets for the Ulleung genome sensitivity.

The comparison is deliberately paired: both trees use exactly the same loci.
The baseline retains the original 294-tip locus FASTAs; the augmentation adds
only AUG_ULLEUNG_CNIP2024. Optional baseline manifest/species-map inputs also
produce complete concatenated-tree and source-label ASTRAL metadata for both
scenarios.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

AUG_TIP = "AUG_ULLEUNG_CNIP2024"
AUG_TAXON = "Cirsium nipponicum"


def clean(value: object) -> str:
    return str(value or "").strip()


def read_fasta(path: Path) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    name = None
    seq: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
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
        raise ValueError(f"duplicate FASTA name: {path}")
    return rows


def write_fasta(path: Path, rows: list[tuple[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for name, seq in rows:
            handle.write(f">{name}\n")
            for i in range(0, len(seq), 80):
                handle.write(seq[i:i+80] + "\n")


def locus_set(path: Path) -> list[str]:
    rows = [x.strip() for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    if not rows or len(rows) != len(set(rows)):
        raise ValueError(f"locus list empty or duplicated: {path}")
    return rows


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [{key: clean(value) for key, value in row.items()} for row in csv.DictReader(handle)]


def write_primary_runs(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["tip_id", "analysis_taxon_label"])
        writer.writeheader()
        writer.writerows(rows)


def write_species_map(outdir: Path, rows: list[dict[str, str]]) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    fields = ["species_id", "analysis_taxon_label", "tip_ids", "n_tips"]
    with (outdir / "astral_species_map.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    lines = [f"{row['species_id']}:{','.join(row['tip_ids'].split('|'))}" for row in rows]
    lines.extend(["OUTGROUP_lett:OUTGROUP_lett", "OUTGROUP_sunf:OUTGROUP_sunf"])
    (outdir / "astral_map.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def prepare_metadata(
    outdir: Path,
    baseline_manifest: Path,
    baseline_species_map: Path,
    expected_baseline_tips: int = 294,
) -> dict[str, object]:
    manifest = read_csv(baseline_manifest)
    required_manifest = {"tip_id", "analysis_taxon_label"}
    if not manifest or not required_manifest <= set(manifest[0]):
        raise ValueError("baseline manifest missing tip/taxon columns")
    if len(manifest) != expected_baseline_tips or len({row["tip_id"] for row in manifest}) != expected_baseline_tips:
        raise ValueError(f"expected {expected_baseline_tips} unique baseline tips")
    same_taxon = [row for row in manifest if row["analysis_taxon_label"] == AUG_TAXON]
    if not same_taxon:
        raise ValueError(f"baseline lacks exact same-taxon representation for {AUG_TAXON}")

    run_rows = [
        {"tip_id": row["tip_id"], "analysis_taxon_label": row["analysis_taxon_label"]}
        for row in manifest
    ]
    write_primary_runs(outdir / "baseline294" / "primary_runs.csv", run_rows)
    write_primary_runs(
        outdir / "augmented295" / "primary_runs.csv",
        run_rows + [{"tip_id": AUG_TIP, "analysis_taxon_label": AUG_TAXON}],
    )

    species = read_csv(baseline_species_map)
    required_species = {"species_id", "analysis_taxon_label", "tip_ids", "n_tips"}
    if not species or not required_species <= set(species[0]):
        raise ValueError("baseline species map missing required columns")
    seen_tips: set[str] = set()
    for row in species:
        tips = [x for x in row["tip_ids"].split("|") if x]
        if len(tips) != int(row["n_tips"]) or seen_tips & set(tips):
            raise ValueError("invalid baseline species map")
        seen_tips.update(tips)
    if seen_tips != {row["tip_id"] for row in manifest}:
        raise ValueError("baseline species map and sample manifest disagree")

    baseline_species = [dict(row) for row in species]
    augmented_species = [dict(row) for row in species]
    hits = [row for row in augmented_species if row["analysis_taxon_label"] == AUG_TAXON]
    if len(hits) != 1:
        raise ValueError(f"expected one baseline species-map row for {AUG_TAXON}")
    hit = hits[0]
    tips = [x for x in hit["tip_ids"].split("|") if x]
    if AUG_TIP in tips:
        raise ValueError("augmentation tip already occurs in baseline species map")
    tips.append(AUG_TIP)
    hit["tip_ids"] = "|".join(tips)
    hit["n_tips"] = str(len(tips))
    write_species_map(outdir / "baseline294", baseline_species)
    write_species_map(outdir / "augmented295", augmented_species)
    return {
        "baseline_same_taxon_tip_ids": sorted(row["tip_id"] for row in same_taxon),
        "baseline_source_label_species": len(baseline_species),
        "augmented_source_label_species": len(augmented_species),
        "new_analysis_taxon_labels_added": 0,
    }


def prepare(
    primary_inputs: Path,
    augmentation_pack: Path,
    outdir: Path,
    minimum_overlap: int = 100,
    baseline_manifest: Path | None = None,
    baseline_species_map: Path | None = None,
) -> dict[str, object]:
    primary_loci = locus_set(primary_inputs / "eligible_loci.txt")
    aug_loci = set(locus_set(augmentation_pack / "strict_recovered_loci.txt"))
    overlap = [locus for locus in primary_loci if locus in aug_loci]
    if len(overlap) < minimum_overlap:
        raise ValueError(f"Only {len(overlap)} paired loci; require >= {minimum_overlap}")

    baseline_dir = outdir / "baseline294" / "loci_unaligned"
    augmented_dir = outdir / "augmented295" / "loci_unaligned"
    manifest: list[dict[str, object]] = []
    for locus in overlap:
        primary_path = primary_inputs / "loci_unaligned" / f"{locus}.fasta"
        aug_path = augmentation_pack / "loci" / f"{locus}.fasta"
        primary = read_fasta(primary_path)
        aug = read_fasta(aug_path)
        names = [name for name, _ in primary]
        if AUG_TIP in names:
            raise ValueError(f"augmentation tip already present in primary {locus}")
        if len(aug) != 1 or aug[0][0] != AUG_TIP or not aug[0][1]:
            raise ValueError(f"invalid augmentation FASTA for {locus}")
        if len(names) != len(set(names)):
            raise ValueError(f"duplicate primary tip in {locus}")
        write_fasta(baseline_dir / f"{locus}.fasta", primary)
        write_fasta(augmented_dir / f"{locus}.fasta", primary + aug)
        manifest.append({
            "locus": locus,
            "baseline_sequences": len(primary),
            "augmented_sequences": len(primary) + 1,
            "augmentation_nt": len(aug[0][1]),
            "exact_same_primary_records": True,
        })

    outdir.mkdir(parents=True, exist_ok=True)
    for label in ("baseline294", "augmented295"):
        (outdir / label / "eligible_loci.txt").write_text("".join(x + "\n" for x in overlap), encoding="utf-8")
    with (outdir / "paired_locus_manifest.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(manifest[0]))
        writer.writeheader()
        writer.writerows(manifest)

    metadata: dict[str, object] = {}
    if (baseline_manifest is None) != (baseline_species_map is None):
        raise ValueError("baseline manifest and species map must be supplied together")
    if baseline_manifest is not None and baseline_species_map is not None:
        metadata = prepare_metadata(outdir, baseline_manifest, baseline_species_map)

    summary = {
        "contract_version": "cirsium_nipponicum_paired_augmentation_inputs_v2",
        "primary_eligible_loci": len(primary_loci),
        "ulleung_strict_loci": len(aug_loci),
        "paired_overlap_loci": len(overlap),
        "minimum_overlap_loci": minimum_overlap,
        "paired_tree_inputs_ready": True,
        "baseline_focal_tips": 294,
        "augmented_focal_tips": 295,
        "augmentation_tip": AUG_TIP,
        "augmentation_taxon": AUG_TAXON,
        "same_locus_set_required": True,
        "primary_294_tree_superseded": False,
        "astral_metadata_ready": bool(metadata),
        **metadata,
        "promotion_rule": (
            "Compare baseline294 and augmented295 on this exact paired locus set separately against the accepted "
            "BWA and BLASTx baseline inputs; promote the Ulleung tip only if shared-backbone, same-taxon-neighbour "
            "and source-label ASTRAL gates all pass in both baseline mapping modes."
        ),
    }
    (outdir / "paired_augmentation_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--primary-inputs", type=Path, required=True)
    parser.add_argument("--augmentation-pack", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--minimum-overlap", type=int, default=100)
    parser.add_argument("--baseline-manifest", type=Path)
    parser.add_argument("--baseline-species-map", type=Path)
    args = parser.parse_args()
    prepare(
        args.primary_inputs,
        args.augmentation_pack,
        args.outdir,
        args.minimum_overlap,
        args.baseline_manifest,
        args.baseline_species_map,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
