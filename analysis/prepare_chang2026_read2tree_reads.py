#!/usr/bin/env python3
"""Prepare the six Chang 2026 focal RNA-seq libraries through fastp only.

This is the light-weight, restartable read-preparation stage shared by the
Read2Tree fast screen and the later Trinity/TransDecoder workflow.  It reuses
the frozen sample/run contract and path layout from
run_chang2026_restartable_transcriptome_assembly.py, but deliberately stops
before Trinity so the assembly-free topology screen can run first.
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import run_chang2026_restartable_transcriptome_assembly as heavy

READ_STAGES = ("prefetch", "vdb_validate", "fasterq", "pigz", "fastp")
RUN_FIELDS = (
    "sample_id", "taxon", "morph", "run", "library_layout", "status",
    "completed_stage", "sra_dir", "raw_read_1", "raw_read_2",
    "trimmed_read_1", "trimmed_read_2", "fastp_json",
    "started_at_unix", "finished_at_unix", "elapsed_seconds", "error",
)


def write_csv(path: Path, rows: Iterable[Mapping[str, object]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def command_plan_for_row(
    row: Mapping[str, str], *, outdir: Path, fasterq_threads: int,
    fastp_threads: int, prefetch_executable: str = "prefetch",
    vdb_validate_executable: str = "vdb-validate",
    fasterq_executable: str = "fasterq-dump", pigz_executable: str = "pigz",
    fastp_executable: str = "fastp",
) -> dict[str, object]:
    # Keep exactly the same sample directory and FASTQ naming convention used by
    # the heavy runner so Trinity can resume later without copying the reads.
    return heavy.command_plan(
        row,
        outdir=outdir,
        fasterq_threads=fasterq_threads,
        fastp_threads=fastp_threads,
        trinity_threads=1,
        trinity_memory_gb=1,
        prefetch_executable=prefetch_executable,
        vdb_validate_executable=vdb_validate_executable,
        fasterq_executable=fasterq_executable,
        pigz_executable=pigz_executable,
        fastp_executable=fastp_executable,
        trinity_executable="Trinity",
        transdecoder_longorfs_executable="TransDecoder.LongOrfs",
        transdecoder_predict_executable="TransDecoder.Predict",
        python_executable=sys.executable,
    )


def prepare_one(plan: Mapping[str, object], *, dry_run: bool) -> dict[str, object]:
    start = time.time()
    completed = "none"
    base = {
        key: plan[key]
        for key in (
            "sample_id", "taxon", "morph", "run", "library_layout", "sra_dir",
            "raw_read_1", "raw_read_2", "trimmed_read_1", "trimmed_read_2", "fastp_json",
        )
    }
    if dry_run:
        end = time.time()
        return {
            **base,
            "status": "planned_dry_run",
            "completed_stage": completed,
            "started_at_unix": f"{start:.6f}",
            "finished_at_unix": f"{end:.6f}",
            "elapsed_seconds": f"{end-start:.6f}",
            "error": "",
        }

    try:
        root = Path(str(plan["sample_root"]))
        root.mkdir(parents=True, exist_ok=True)
        sra_dir = Path(str(plan["sra_dir"]))
        raw1u = Path(str(plan["raw_read_1_uncompressed"]))
        raw2u = Path(str(plan["raw_read_2_uncompressed"]))
        raw1 = Path(str(plan["raw_read_1"]))
        raw2 = Path(str(plan["raw_read_2"]))
        trim1 = Path(str(plan["trimmed_read_1"]))
        trim2 = Path(str(plan["trimmed_read_2"]))
        fastp_json = Path(str(plan["fastp_json"]))

        trimmed_state = (heavy.nonempty(trim1), heavy.nonempty(trim2), heavy.nonempty(fastp_json))
        if all(trimmed_state):
            status = "skipped_existing_trimmed_reads"
            completed = "fastp"
        else:
            if any(trimmed_state):
                raise RuntimeError("Partial trimmed-read/fastp state detected; inspect before restart")

            gz_state = (heavy.nonempty(raw1), heavy.nonempty(raw2))
            u_state = (heavy.nonempty(raw1u), heavy.nonempty(raw2u))
            if gz_state in {(True, False), (False, True)} or u_state in {(True, False), (False, True)}:
                raise RuntimeError("Partial paired FASTQ state detected; inspect before restart")

            if not all(gz_state):
                if any(u_state):
                    raise RuntimeError("Uncompressed FASTQ pair exists without completed compression; inspect before restart")
                # Only touch the network/SRA stages when no complete raw pair is
                # already present. A stale completion marker without its SRA
                # directory is repaired by repeating prefetch.
                if not sra_dir.is_dir() or not heavy.marker(plan, "prefetch").exists():
                    heavy.run_stage(plan, "prefetch")
                    completed = "prefetch"
                if not sra_dir.is_dir():
                    raise RuntimeError(f"prefetch accession directory missing: {sra_dir}")
                if not heavy.marker(plan, "vdb_validate").exists():
                    heavy.run_stage(plan, "vdb_validate")
                    completed = "vdb_validate"
                raw1.parent.mkdir(parents=True, exist_ok=True)
                Path(str(plan["sample_root"])).joinpath("scratch", "fasterq").mkdir(parents=True, exist_ok=True)
                heavy.run_stage(plan, "fasterq")
                completed = "fasterq"
                heavy.require_nonempty(raw1u, "fasterq R1")
                heavy.require_nonempty(raw2u, "fasterq R2")
                heavy.run_stage(plan, "pigz")
                completed = "pigz"

            heavy.require_nonempty(raw1, "raw R1.gz")
            heavy.require_nonempty(raw2, "raw R2.gz")
            trim1.parent.mkdir(parents=True, exist_ok=True)
            heavy.run_stage(plan, "fastp")
            completed = "fastp"
            heavy.require_nonempty(trim1, "trimmed R1")
            heavy.require_nonempty(trim2, "trimmed R2")
            heavy.require_nonempty(fastp_json, "fastp JSON")
            status = "trimmed_ready"
        error = ""
    except Exception as exc:
        status = "failed"
        error = f"{type(exc).__name__}: {exc}"

    end = time.time()
    return {
        **base,
        "status": status,
        "completed_stage": completed,
        "started_at_unix": f"{start:.6f}",
        "finished_at_unix": f"{end:.6f}",
        "elapsed_seconds": f"{end-start:.6f}",
        "error": error,
    }


def executable_preflight(plans: Sequence[Mapping[str, object]]) -> list[str]:
    if not plans:
        return []
    commands = plans[0]["commands"]
    missing: list[str] = []
    for stage in READ_STAGES:
        executable = str(commands[stage][0])
        if shutil.which(executable) is None and not Path(executable).is_file():
            missing.append(executable)
    return sorted(set(missing))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--panel", type=Path, required=True)
    p.add_argument("--expected-panel-samples", type=int, default=6)
    p.add_argument("--sample-id", action="append", default=[])
    p.add_argument("--outdir", type=Path, required=True)
    p.add_argument("--jobs", type=int, default=1)
    p.add_argument("--fasterq-threads", type=int, default=8)
    p.add_argument("--fastp-threads", type=int, default=8)
    p.add_argument("--min-free-disk-gib", type=float, default=0)
    p.add_argument("--prefetch", default="prefetch")
    p.add_argument("--vdb-validate", default="vdb-validate")
    p.add_argument("--fasterq", default="fasterq-dump")
    p.add_argument("--pigz", default="pigz")
    p.add_argument("--fastp", default="fastp")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--preflight-only", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if args.jobs < 1:
        raise SystemExit("--jobs must be >= 1")
    validated = heavy.validate_panel(args.panel, expected_samples=args.expected_panel_samples)
    rows = heavy.select_rows(validated, args.sample_id)
    plans = [
        command_plan_for_row(
            row,
            outdir=args.outdir,
            fasterq_threads=args.fasterq_threads,
            fastp_threads=args.fastp_threads,
            prefetch_executable=args.prefetch,
            vdb_validate_executable=args.vdb_validate,
            fasterq_executable=args.fasterq,
            pigz_executable=args.pigz,
            fastp_executable=args.fastp,
        )
        for row in rows
    ]

    disk = heavy.disk_preflight(args.outdir, args.min_free_disk_gib)
    (args.outdir / "read2tree_read_preflight_disk.json").write_text(
        json.dumps(disk, indent=2) + "\n", encoding="utf-8"
    )
    cmd_rows = [
        {
            "sample_id": plan["sample_id"],
            "run": plan["run"],
            "morph": plan["morph"],
            **{f"{stage}_command": plan["command_strings"][stage] for stage in READ_STAGES},
        }
        for plan in plans
    ]
    write_csv(
        args.outdir / "read2tree_read_command_plan.csv",
        cmd_rows,
        ("sample_id", "run", "morph") + tuple(f"{stage}_command" for stage in READ_STAGES),
    )

    missing = [] if args.dry_run else executable_preflight(plans)
    if args.preflight_only:
        print(f"selected_samples={len(plans)}")
        print(f"disk_free_gib={disk['free_gib']:.3f}")
        print("missing_executables=" + "|".join(missing))
        return 1 if missing else 0

    if args.dry_run or args.jobs == 1:
        results = [prepare_one(plan, dry_run=args.dry_run) for plan in plans]
    else:
        results = []
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            futures = [pool.submit(prepare_one, plan, dry_run=False) for plan in plans]
            for future in as_completed(futures):
                results.append(future.result())
        results.sort(key=lambda row: str(row["sample_id"]))

    write_csv(args.outdir / "read2tree_read_manifest.csv", results, RUN_FIELDS)
    statuses = Counter(str(row["status"]) for row in results)
    summary = {
        "contract_version": "chang2026_read2tree_trimmed_reads_v1",
        "input_panel_sample_count": len(validated),
        "selected_sample_count": len(rows),
        "selected_sample_ids": [row["sample_id"] for row in rows],
        "status_counts": dict(sorted(statuses.items())),
        "failed_count": statuses.get("failed", 0),
        "dry_run": args.dry_run,
        "reads_root": str(args.outdir),
        "read2tree_path_contract": "samples/<sample_id>/trimmed/<sample_id>.R[12].trim.fastq.gz",
        "last_allowed_stage": "fastp",
        "trinity_executed": False,
        "claim_limit": "This stage prepares validated paired reads for the assembly-free Read2Tree topology screen. It does not assemble transcriptomes or test the colour-history hypotheses by itself.",
        "disk_preflight": disk,
    }
    (args.outdir / "read2tree_read_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(f"selected_sample_count={len(rows)}")
    print("selected_sample_ids=" + "|".join(row["sample_id"] for row in rows))
    print("status_counts=" + json.dumps(summary["status_counts"], sort_keys=True))
    return 1 if summary["failed_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
