#!/usr/bin/env python3
"""Prepare a real-read four-tip same-taxon placement pilot for EA01 and EA02.

The quartet contains two matched 294-baseline Moreyra tips and the two durable
public candidate packs. All four samples use one exact strict-locus intersection.
This is deliberately smaller than the full 294-tip gate and can never authorize
promotion by itself.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from build_public_sra_comp1061_candidate_pack import read_fasta, write_fasta

TIPS = {
    "MRY_YOSHINOI": "Cirsium nipponicum var. yoshinoi",
    "PUBEA001": "Cirsium nipponicum var. yoshinoi",
    "MRY_SAIRAMENSE": "Cirsium sairamense",
    "PUBEA002": "Cirsium sairamense",
}
PACK_KEYS = (
    ("MRY_YOSHINOI", "baseline_yoshinoi"),
    ("PUBEA001", "ea01"),
    ("MRY_SAIRAMENSE", "baseline_sairamense"),
    ("PUBEA002", "ea02"),
)


def loci(path: Path) -> list[str]:
    rows = [x.strip() for x in (path / "strict_recovered_loci.txt").read_text(encoding="utf-8").splitlines() if x.strip()]
    if not rows or len(rows) != len(set(rows)):
        raise ValueError(f"invalid strict locus list: {path}")
    return rows


def single_sequence(path: Path, expected_tip: str) -> tuple[str, str]:
    rows = read_fasta(path)
    if len(rows) != 1 or rows[0][0] != expected_tip or not rows[0][1]:
        raise ValueError(f"expected one {expected_tip} record in {path}")
    return rows[0]


def prepare(
    *,
    locus_universe: Path,
    baseline_yoshinoi: Path,
    ea01: Path,
    baseline_sairamense: Path,
    ea02: Path,
    outdir: Path,
    minimum_common_loci: int = 100,
) -> dict[str, object]:
    if minimum_common_loci < 100:
        raise ValueError("empirical quartet minimum cannot be relaxed below 100 loci")
    universe = [x.strip() for x in locus_universe.read_text(encoding="utf-8").splitlines() if x.strip()]
    if len(universe) != 241 or len(universe) != len(set(universe)):
        raise ValueError("expected the frozen 241-locus universe")
    packs = {
        "baseline_yoshinoi": baseline_yoshinoi,
        "ea01": ea01,
        "baseline_sairamense": baseline_sairamense,
        "ea02": ea02,
    }
    sets = {name: set(loci(path)) for name, path in packs.items()}
    common = [locus for locus in universe if all(locus in sets[name] for name in sets)]
    if len(common) < minimum_common_loci:
        raise ValueError(f"Only {len(common)} four-way strict loci; require >= {minimum_common_loci}")

    unaligned = outdir / "loci_unaligned"
    for locus in common:
        records = []
        for tip, key in PACK_KEYS:
            records.append(single_sequence(packs[key] / "loci" / f"{locus}.fasta", tip))
        write_fasta(unaligned / f"{locus}.fasta", records)

    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "four_way_common_strict_loci.txt").write_text(
        "".join(f"{locus}\n" for locus in common), encoding="utf-8"
    )
    with (outdir / "sample_manifest.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["tip_id", "analysis_taxon_label", "role"])
        writer.writeheader()
        for tip in TIPS:
            writer.writerow({
                "tip_id": tip,
                "analysis_taxon_label": TIPS[tip],
                "role": "baseline_294" if tip.startswith("MRY_") else "public_candidate",
            })
    summary: dict[str, object] = {
        "contract_version": "public_candidate_empirical_quartet_inputs_v1",
        "frozen_locus_universe": 241,
        "pack_strict_loci": {name: len(sets[name]) for name in sets},
        "four_way_common_strict_loci": len(common),
        "minimum_common_loci": minimum_common_loci,
        "tips": list(TIPS),
        "taxon_pairs": {
            "Cirsium nipponicum var. yoshinoi": ["MRY_YOSHINOI", "PUBEA001"],
            "Cirsium sairamense": ["MRY_SAIRAMENSE", "PUBEA002"],
        },
        "all_four_samples_same_locus_set": True,
        "full_294_tip_promotion_allowed_from_this_pilot": False,
        "new_china_sampling_freeze_allowed": False,
    }
    (outdir / "input_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return summary


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--locus-universe", type=Path, required=True)
    p.add_argument("--baseline-yoshinoi", type=Path, required=True)
    p.add_argument("--ea01", type=Path, required=True)
    p.add_argument("--baseline-sairamense", type=Path, required=True)
    p.add_argument("--ea02", type=Path, required=True)
    p.add_argument("--outdir", type=Path, required=True)
    p.add_argument("--minimum-common-loci", type=int, default=100)
    a = p.parse_args()
    prepare(
        locus_universe=a.locus_universe,
        baseline_yoshinoi=a.baseline_yoshinoi,
        ea01=a.ea01,
        baseline_sairamense=a.baseline_sairamense,
        ea02=a.ea02,
        outdir=a.outdir,
        minimum_common_loci=a.minimum_common_loci,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
