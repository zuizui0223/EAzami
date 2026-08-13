#!/usr/bin/env python3
"""Prepare paired baseline/augmentation locus sets for the Ulleung genome sensitivity.

The comparison is deliberately paired: both trees use exactly the same loci.  The
baseline retains the original 294-tip locus FASTAs; the augmentation adds only
AUG_ULLEUNG_CNIP2024.  This avoids confusing an extra-tip effect with a changed
locus set.
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
from pathlib import Path

AUG_TIP = "AUG_ULLEUNG_CNIP2024"


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


def prepare(primary_inputs: Path, augmentation_pack: Path, outdir: Path, minimum_overlap: int = 100) -> dict[str, object]:
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

    summary = {
        "contract_version": "cirsium_nipponicum_paired_augmentation_inputs_v1",
        "primary_eligible_loci": len(primary_loci),
        "ulleung_strict_loci": len(aug_loci),
        "paired_overlap_loci": len(overlap),
        "minimum_overlap_loci": minimum_overlap,
        "paired_tree_inputs_ready": True,
        "baseline_focal_tips": 294,
        "augmented_focal_tips": 295,
        "augmentation_tip": AUG_TIP,
        "same_locus_set_required": True,
        "primary_294_tree_superseded": False,
        "promotion_rule": (
            "Compare baseline294 and augmented295 on this exact paired locus set; promote the Ulleung tip "
            "to the maximum-public tree only if placement is stable across the predeclared concatenated/coalescent "
            "and mapping sensitivities."
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
    args = parser.parse_args()
    prepare(args.primary_inputs, args.augmentation_pack, args.outdir, args.minimum_overlap)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
