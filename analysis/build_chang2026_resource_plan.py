#!/usr/bin/env python3
"""Build an evidence-backed compute and storage plan for the Chang 2026 panel.

The frozen 19-sample panel records run identities and official library layout,
while the complete NCBI runinfo table additionally records spots, bases,
average spot length and deposited SRA size.  This planner joins those files by
exact SRR accession and reports:

* exact public SRA download size;
* exact total spots, paired reads and sequenced bases;
* a transparent uncompressed FASTQ staging range;
* a conservative working-disk planning value; and
* separate six-takaoense-pilot and full-19-sample totals.

FASTQ and working-disk values are planning heuristics, not observed output sizes.
All multipliers are written into the summary so an HPC run can revise them
without changing the underlying public metadata.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Iterable, Mapping, Sequence

DEFAULT_OUTDIR = Path(
    "data/evidence/generated/chang2026_gene_tree_panel/resource_plan"
)

RESOURCE_FIELDS = (
    "sample_id",
    "taxon",
    "morph",
    "panel_role",
    "run",
    "library_layout",
    "spots",
    "paired_read_count",
    "bases",
    "gigabases",
    "average_spot_length",
    "derived_average_read_length",
    "sra_size_mb",
    "sra_size_gib",
    "estimated_uncompressed_fastq_min_gib",
    "estimated_uncompressed_fastq_max_gib",
    "estimated_working_disk_gib",
    "execution_group",
)


def clean(value: object) -> str:
    return str(value or "").strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [
            {key: clean(value) for key, value in row.items()}
            for row in csv.DictReader(handle)
            if any(clean(value) for value in row.values())
        ]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def positive_int(value: object, label: str) -> int:
    text = clean(value)
    try:
        parsed = int(float(text))
    except ValueError as exc:
        raise ValueError(f"Invalid integer for {label}: {text!r}") from exc
    if parsed <= 0:
        raise ValueError(f"Expected positive integer for {label}: {parsed}")
    return parsed


def positive_float(value: object, label: str) -> float:
    text = clean(value)
    try:
        parsed = float(text)
    except ValueError as exc:
        raise ValueError(f"Invalid number for {label}: {text!r}") from exc
    if not math.isfinite(parsed) or parsed <= 0:
        raise ValueError(f"Expected positive finite value for {label}: {parsed}")
    return parsed


def runinfo_index(rows: Sequence[Mapping[str, str]]) -> dict[str, Mapping[str, str]]:
    output: dict[str, Mapping[str, str]] = {}
    for row in rows:
        run = clean(row.get("Run"))
        if not run:
            continue
        if run in output:
            raise ValueError(f"Duplicate runinfo accession: {run}")
        output[run] = row
    return output


def build_plan(
    panel_rows: Sequence[Mapping[str, str]],
    runinfo_rows: Sequence[Mapping[str, str]],
    *,
    fastq_bytes_per_base_min: float,
    fastq_bytes_per_base_max: float,
    working_disk_multiplier: float,
) -> list[dict[str, object]]:
    if len(panel_rows) != 19:
        raise ValueError(f"Expected 19 panel samples, observed {len(panel_rows)}")
    if not (0 < fastq_bytes_per_base_min <= fastq_bytes_per_base_max):
        raise ValueError("FASTQ byte-per-base bounds are invalid")
    if working_disk_multiplier < 1:
        raise ValueError("working_disk_multiplier must be >= 1")

    index = runinfo_index(runinfo_rows)
    sample_ids: set[str] = set()
    runs: set[str] = set()
    output: list[dict[str, object]] = []
    gib = 1024**3

    for panel in panel_rows:
        sample_id = clean(panel.get("sample_id"))
        run = clean(panel.get("matched_run"))
        if not sample_id or not run:
            raise ValueError("Panel row lacks sample_id or matched_run")
        if sample_id in sample_ids:
            raise ValueError(f"Duplicate panel sample_id: {sample_id}")
        if run in runs:
            raise ValueError(f"Duplicate panel run: {run}")
        sample_ids.add(sample_id)
        runs.add(run)

        info = index.get(run)
        if info is None:
            raise ValueError(f"Run is absent from complete runinfo: {run}")
        panel_layout = clean(panel.get("library_layout")).upper()
        official_layout = clean(info.get("LibraryLayout")).upper()
        if panel_layout != official_layout:
            raise ValueError(
                f"LibraryLayout mismatch for {run}: panel={panel_layout}, "
                f"runinfo={official_layout}"
            )
        if official_layout != "PAIRED":
            raise ValueError(f"Current Chang resource contract requires PAIRED: {run}")

        spots = positive_int(info.get("spots"), f"{run}.spots")
        panel_spots = positive_int(panel.get("matched_spots"), f"{run}.matched_spots")
        if spots != panel_spots:
            raise ValueError(
                f"Spot-count mismatch for {run}: panel={panel_spots}, runinfo={spots}"
            )
        spots_with_mates = positive_int(
            info.get("spots_with_mates"), f"{run}.spots_with_mates"
        )
        if spots_with_mates != spots:
            raise ValueError(
                f"Not every official spot has mates for {run}: "
                f"{spots_with_mates}/{spots}"
            )

        bases = positive_int(info.get("bases"), f"{run}.bases")
        average_spot_length = positive_float(
            info.get("avgLength"), f"{run}.avgLength"
        )
        size_mb = positive_float(info.get("size_MB"), f"{run}.size_MB")
        fastq_min = bases * fastq_bytes_per_base_min / gib
        fastq_max = bases * fastq_bytes_per_base_max / gib
        working = fastq_max * working_disk_multiplier
        role = clean(panel.get("panel_role"))
        group = (
            "takaoense6_pilot"
            if role == "focal_colour_morph"
            else "full19_extension"
        )

        output.append(
            {
                "sample_id": sample_id,
                "taxon": clean(panel.get("taxon")),
                "morph": clean(panel.get("morph")),
                "panel_role": role,
                "run": run,
                "library_layout": official_layout,
                "spots": spots,
                "paired_read_count": 2 * spots,
                "bases": bases,
                "gigabases": f"{bases / 1e9:.6f}",
                "average_spot_length": f"{average_spot_length:.3f}",
                "derived_average_read_length": f"{average_spot_length / 2:.3f}",
                "sra_size_mb": f"{size_mb:.3f}",
                "sra_size_gib": f"{size_mb / 1024:.6f}",
                "estimated_uncompressed_fastq_min_gib": f"{fastq_min:.6f}",
                "estimated_uncompressed_fastq_max_gib": f"{fastq_max:.6f}",
                "estimated_working_disk_gib": f"{working:.6f}",
                "execution_group": group,
            }
        )

    focal = [row for row in output if row["execution_group"] == "takaoense6_pilot"]
    if len(focal) != 6:
        raise ValueError(f"Expected six focal takaoense samples, observed {len(focal)}")
    return sorted(
        output,
        key=lambda row: (
            row["execution_group"] != "takaoense6_pilot",
            str(row["sample_id"]),
        ),
    )


def group_summary(rows: Sequence[Mapping[str, object]]) -> dict[str, object]:
    if not rows:
        raise ValueError("Cannot summarize an empty resource group")
    total_spots = sum(int(row["spots"]) for row in rows)
    total_reads = sum(int(row["paired_read_count"]) for row in rows)
    total_bases = sum(int(row["bases"]) for row in rows)
    total_sra_gib = sum(float(row["sra_size_gib"]) for row in rows)
    fastq_min = sum(
        float(row["estimated_uncompressed_fastq_min_gib"]) for row in rows
    )
    fastq_max = sum(
        float(row["estimated_uncompressed_fastq_max_gib"]) for row in rows
    )
    working = sum(float(row["estimated_working_disk_gib"]) for row in rows)
    return {
        "sample_count": len(rows),
        "sample_ids": [str(row["sample_id"]) for row in rows],
        "total_spots": total_spots,
        "total_paired_reads": total_reads,
        "total_bases": total_bases,
        "total_gigabases": total_bases / 1e9,
        "total_sra_size_gib": total_sra_gib,
        "estimated_uncompressed_fastq_min_gib": fastq_min,
        "estimated_uncompressed_fastq_max_gib": fastq_max,
        "estimated_working_disk_gib": working,
        "recommended_free_disk_gib_rounded_up": int(math.ceil(working / 25) * 25),
        "largest_sample_gigabases": max(float(row["gigabases"]) for row in rows),
        "largest_sample_working_disk_gib": max(
            float(row["estimated_working_disk_gib"]) for row in rows
        ),
    }


def build_summary(
    rows: Sequence[Mapping[str, object]],
    *,
    panel: Path,
    runinfo: Path,
    fastq_bytes_per_base_min: float,
    fastq_bytes_per_base_max: float,
    working_disk_multiplier: float,
) -> dict[str, object]:
    pilot = [row for row in rows if row["execution_group"] == "takaoense6_pilot"]
    return {
        "resource_plan_version": "chang2026_resource_plan_v1",
        "panel_sha256": sha256_file(panel),
        "complete_runinfo_sha256": sha256_file(runinfo),
        "official_library_layout_counts": {"PAIRED": len(rows)},
        "fastq_bytes_per_base_min": fastq_bytes_per_base_min,
        "fastq_bytes_per_base_max": fastq_bytes_per_base_max,
        "working_disk_multiplier_over_fastq_max": working_disk_multiplier,
        "fastq_estimate_definition": (
            "Total NCBI bases multiplied by configurable bytes/base bounds; "
            "includes sequence and quality text plus approximate FASTQ overhead."
        ),
        "working_disk_definition": (
            "Estimated maximum uncompressed FASTQ multiplied for simultaneous "
            "raw, trimmed, temporary and assembly staging. This is a planning "
            "heuristic, not measured disk use."
        ),
        "takaoense6_pilot": group_summary(pilot),
        "full19_panel": group_summary(rows),
        "workflow_resource_request": {
            "initial_parallel_sample_jobs": 1,
            "trinity_threads_per_sample": 16,
            "trinity_memory_gb_per_sample": 96,
            "reason": (
                "Start one focal sample at a time, record peak RSS/disk and "
                "assembly QC, then revise concurrency before the remaining panel."
            ),
        },
        "execution_sequence": [
            "download and assemble the six morph-labelled takaoense samples sequentially",
            "record exact fasterq/fastp/Trinity peak storage, runtime and memory per sample",
            "run transcriptome and protein QC before OrthoFinder",
            "expand to the 13 controls only after the pilot resource/QC gate passes",
        ],
        "claim_limit": (
            "SRA sizes, spots and bases are official metadata. FASTQ and working-disk "
            "values are transparent planning estimates and must be replaced by measured "
            "usage after the first completed sample."
        ),
    }


def write_csv(
    path: Path,
    rows: Iterable[Mapping[str, object]],
    fields: Sequence[str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--runinfo", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    parser.add_argument("--fastq-bytes-per-base-min", type=float, default=2.2)
    parser.add_argument("--fastq-bytes-per-base-max", type=float, default=3.0)
    parser.add_argument("--working-disk-multiplier", type=float, default=2.5)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    panel_rows = read_csv(args.panel)
    runinfo_rows = read_csv(args.runinfo)
    plan = build_plan(
        panel_rows,
        runinfo_rows,
        fastq_bytes_per_base_min=args.fastq_bytes_per_base_min,
        fastq_bytes_per_base_max=args.fastq_bytes_per_base_max,
        working_disk_multiplier=args.working_disk_multiplier,
    )
    summary = build_summary(
        plan,
        panel=args.panel,
        runinfo=args.runinfo,
        fastq_bytes_per_base_min=args.fastq_bytes_per_base_min,
        fastq_bytes_per_base_max=args.fastq_bytes_per_base_max,
        working_disk_multiplier=args.working_disk_multiplier,
    )

    args.outdir.mkdir(parents=True, exist_ok=True)
    write_csv(
        args.outdir / "chang2026_sample_resource_plan.csv",
        plan,
        RESOURCE_FIELDS,
    )
    (args.outdir / "chang2026_resource_plan_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    pilot = summary["takaoense6_pilot"]
    full = summary["full19_panel"]
    print(f"pilot_samples={pilot['sample_count']}")
    print(f"pilot_gigabases={pilot['total_gigabases']:.6f}")
    print(f"pilot_sra_size_gib={pilot['total_sra_size_gib']:.6f}")
    print(
        "pilot_recommended_free_disk_gib="
        f"{pilot['recommended_free_disk_gib_rounded_up']}"
    )
    print(f"full_samples={full['sample_count']}")
    print(f"full_gigabases={full['total_gigabases']:.6f}")
    print(f"full_sra_size_gib={full['total_sra_size_gib']:.6f}")
    print(
        "full_recommended_free_disk_gib="
        f"{full['recommended_free_disk_gib_rounded_up']}"
    )
    print(args.outdir / "chang2026_resource_plan_summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
