#!/usr/bin/env python3
"""Assemble the 19-sample Chang 2026 transcriptome panel from official SRA runs.

The public assembly audit recovered no BioSample-linked TSA or Assembly records,
so every current panel sample uses its reconciled official SRA run.  This runner
creates a restartable per-sample plan:

1. fasterq-dump paired reads;
2. pigz compression;
3. fastp trimming and QC;
4. Trinity de novo transcriptome assembly;
5. TransDecoder coding-sequence/protein prediction;
6. deterministic ``sample_id|transcript`` protein headers for OrthoFinder.

The runner supports ``--dry-run`` and never downloads data in CI.  It is not a
substitute for assembly-quality review; downstream analyses must retain read,
assembly, BUSCO/orthology, and copy-number diagnostics.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import shlex
import subprocess
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Iterable, Mapping, Sequence

DEFAULT_OUTDIR = Path("results/chang2026_transcriptomes")

RUN_FIELDS = (
    "sample_id",
    "taxon",
    "morph",
    "run",
    "status",
    "raw_read_1",
    "raw_read_2",
    "trimmed_read_1",
    "trimmed_read_2",
    "trinity_fasta",
    "transdecoder_peptide_fasta",
    "prefixed_proteome_fasta",
    "fasterq_command",
    "pigz_command",
    "fastp_command",
    "trinity_command",
    "transdecoder_longorfs_command",
    "transdecoder_predict_command",
    "prefix_headers_command",
    "started_at_unix",
    "finished_at_unix",
    "elapsed_seconds",
    "error",
)

SUMMARY_FIELDS = ("metric", "value")


def clean(value: object) -> str:
    return str(value or "").strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [
            {key: clean(value) for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


def write_csv(
    path: Path,
    rows: Iterable[Mapping[str, object]],
    fields: Sequence[str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(fields), extrasaction="ignore"
        )
        writer.writeheader()
        writer.writerows(rows)


def validate_panel(path: Path) -> list[dict[str, str]]:
    rows = read_csv(path)
    if not rows:
        raise ValueError(f"No panel rows in {path}")
    if len(rows) != 19:
        raise ValueError(f"Expected 19 panel samples, observed {len(rows)}")

    sample_ids = [clean(row.get("sample_id")) for row in rows]
    runs = [clean(row.get("matched_run")) for row in rows]
    if any(not value for value in sample_ids + runs):
        raise ValueError("One or more panel rows lack sample_id or matched_run")
    if len(sample_ids) != len(set(sample_ids)):
        raise ValueError("Panel sample_id values are not unique")
    if len(runs) != len(set(runs)):
        raise ValueError("Official SRA run values are not unique")

    unresolved = [
        row
        for row in rows
        if clean(row.get("run_match_confidence")) not in {"verified", "probable"}
    ]
    if unresolved:
        raise ValueError(
            "Panel contains unresolved run mappings: "
            + "|".join(clean(row.get("sample_id")) for row in unresolved)
        )
    wrong_source = [
        row
        for row in rows
        if clean(row.get("de_novo_required")) != "true"
        or clean(row.get("preferred_sequence_source"))
        != clean(row.get("matched_run"))
    ]
    if wrong_source:
        raise ValueError(
            "Current workflow expects official-SRA de novo input for every sample: "
            + "|".join(clean(row.get("sample_id")) for row in wrong_source)
        )
    nonpaired = [
        row
        for row in rows
        if "paired" not in clean(row.get("read_count_relation")).casefold()
    ]
    if nonpaired:
        raise ValueError(
            "Current assembly runner is paired-end only; unresolved rows: "
            + "|".join(clean(row.get("sample_id")) for row in nonpaired)
        )
    return sorted(rows, key=lambda row: row["sample_id"])


def command_plan(
    row: Mapping[str, str],
    *,
    outdir: Path,
    fasterq_threads: int,
    fastp_threads: int,
    trinity_threads: int,
    trinity_memory_gb: int,
    fasterq_executable: str,
    pigz_executable: str,
    fastp_executable: str,
    trinity_executable: str,
    transdecoder_longorfs_executable: str,
    transdecoder_predict_executable: str,
    python_executable: str,
    prefix_script: Path,
) -> dict[str, object]:
    sample_id = clean(row.get("sample_id"))
    run = clean(row.get("matched_run"))
    sample_root = outdir / "samples" / sample_id
    raw_dir = sample_root / "raw"
    trimmed_dir = sample_root / "trimmed"
    trinity_dir = sample_root / "trinity"
    transdecoder_dir = sample_root / "transdecoder"

    raw_1_uncompressed = raw_dir / f"{run}_1.fastq"
    raw_2_uncompressed = raw_dir / f"{run}_2.fastq"
    raw_1 = Path(str(raw_1_uncompressed) + ".gz")
    raw_2 = Path(str(raw_2_uncompressed) + ".gz")
    trimmed_1 = trimmed_dir / f"{sample_id}.R1.trim.fastq.gz"
    trimmed_2 = trimmed_dir / f"{sample_id}.R2.trim.fastq.gz"
    trinity_fasta = trinity_dir / "Trinity.fasta"
    copied_trinity = transdecoder_dir / "Trinity.fasta"
    peptide = transdecoder_dir / "Trinity.fasta.transdecoder.pep"
    prefixed = outdir / "prefixed_proteomes" / f"{sample_id}.faa"

    fasterq = [
        fasterq_executable,
        run,
        "--split-files",
        "--skip-technical",
        "--threads",
        str(fasterq_threads),
        "--outdir",
        str(raw_dir),
    ]
    pigz = [
        pigz_executable,
        "-p",
        str(fasterq_threads),
        "-f",
        str(raw_1_uncompressed),
        str(raw_2_uncompressed),
    ]
    fastp = [
        fastp_executable,
        "-i",
        str(raw_1),
        "-I",
        str(raw_2),
        "-o",
        str(trimmed_1),
        "-O",
        str(trimmed_2),
        "--thread",
        str(fastp_threads),
        "--detect_adapter_for_pe",
        "--json",
        str(trimmed_dir / f"{sample_id}.fastp.json"),
        "--html",
        str(trimmed_dir / f"{sample_id}.fastp.html"),
    ]
    trinity = [
        trinity_executable,
        "--seqType",
        "fq",
        "--left",
        str(trimmed_1),
        "--right",
        str(trimmed_2),
        "--CPU",
        str(trinity_threads),
        "--max_memory",
        f"{trinity_memory_gb}G",
        "--output",
        str(trinity_dir),
        "--full_cleanup",
    ]
    longorfs = [
        transdecoder_longorfs_executable,
        "-t",
        str(copied_trinity),
    ]
    predict = [
        transdecoder_predict_executable,
        "-t",
        str(copied_trinity),
        "--single_best_only",
    ]
    prefix = [
        python_executable,
        str(prefix_script),
        "--input",
        str(peptide),
        "--output",
        str(prefixed),
        "--sample-id",
        sample_id,
    ]

    return {
        "sample_id": sample_id,
        "taxon": clean(row.get("taxon")),
        "morph": clean(row.get("morph")),
        "run": run,
        "sample_root": str(sample_root),
        "raw_read_1": str(raw_1),
        "raw_read_2": str(raw_2),
        "trimmed_read_1": str(trimmed_1),
        "trimmed_read_2": str(trimmed_2),
        "trinity_fasta": str(trinity_fasta),
        "copied_trinity_fasta": str(copied_trinity),
        "transdecoder_peptide_fasta": str(peptide),
        "prefixed_proteome_fasta": str(prefixed),
        "fasterq": fasterq,
        "pigz": pigz,
        "fastp": fastp,
        "trinity": trinity,
        "longorfs": longorfs,
        "predict": predict,
        "prefix": prefix,
        "fasterq_command": shlex.join(fasterq),
        "pigz_command": shlex.join(pigz),
        "fastp_command": shlex.join(fastp),
        "trinity_command": shlex.join(trinity),
        "transdecoder_longorfs_command": shlex.join(longorfs),
        "transdecoder_predict_command": shlex.join(predict),
        "prefix_headers_command": shlex.join(prefix),
    }


def run_logged(
    command: Sequence[str],
    log_path: Path,
    *,
    cwd: Path | None = None,
) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as log:
        log.write("\n$ " + shlex.join(command) + "\n")
        log.flush()
        subprocess.run(
            list(command),
            cwd=str(cwd) if cwd is not None else None,
            check=True,
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True,
        )


def ensure_nonempty(path: Path, label: str) -> None:
    if not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError(f"{label} was not created or is empty: {path}")


def run_one(
    plan: Mapping[str, object],
    *,
    outdir: Path,
    dry_run: bool,
    force: bool,
    keep_raw_reads: bool,
) -> dict[str, object]:
    started = time.time()
    prefixed = Path(str(plan["prefixed_proteome_fasta"]))
    base = {
        "sample_id": plan["sample_id"],
        "taxon": plan["taxon"],
        "morph": plan["morph"],
        "run": plan["run"],
        "raw_read_1": plan["raw_read_1"],
        "raw_read_2": plan["raw_read_2"],
        "trimmed_read_1": plan["trimmed_read_1"],
        "trimmed_read_2": plan["trimmed_read_2"],
        "trinity_fasta": plan["trinity_fasta"],
        "transdecoder_peptide_fasta": plan["transdecoder_peptide_fasta"],
        "prefixed_proteome_fasta": plan["prefixed_proteome_fasta"],
        "fasterq_command": plan["fasterq_command"],
        "pigz_command": plan["pigz_command"],
        "fastp_command": plan["fastp_command"],
        "trinity_command": plan["trinity_command"],
        "transdecoder_longorfs_command": plan[
            "transdecoder_longorfs_command"
        ],
        "transdecoder_predict_command": plan[
            "transdecoder_predict_command"
        ],
        "prefix_headers_command": plan["prefix_headers_command"],
        "started_at_unix": f"{started:.6f}",
    }
    if dry_run:
        finished = time.time()
        return {
            **base,
            "status": "planned_dry_run",
            "finished_at_unix": f"{finished:.6f}",
            "elapsed_seconds": f"{finished - started:.6f}",
            "error": "",
        }
    if prefixed.is_file() and prefixed.stat().st_size > 0 and not force:
        finished = time.time()
        return {
            **base,
            "status": "skipped_existing_prefixed_proteome",
            "finished_at_unix": f"{finished:.6f}",
            "elapsed_seconds": f"{finished - started:.6f}",
            "error": "",
        }

    sample_id = str(plan["sample_id"])
    log = outdir / "logs" / f"{sample_id}.assembly.log"
    try:
        raw_1 = Path(str(plan["raw_read_1"]))
        raw_2 = Path(str(plan["raw_read_2"]))
        raw_1.parent.mkdir(parents=True, exist_ok=True)
        if force or not (raw_1.is_file() and raw_2.is_file()):
            run_logged(plan["fasterq"], log)
            uncompressed_1 = Path(str(raw_1).removesuffix(".gz"))
            uncompressed_2 = Path(str(raw_2).removesuffix(".gz"))
            ensure_nonempty(uncompressed_1, "fasterq R1")
            ensure_nonempty(uncompressed_2, "fasterq R2")
            run_logged(plan["pigz"], log)
        ensure_nonempty(raw_1, "compressed raw R1")
        ensure_nonempty(raw_2, "compressed raw R2")

        trimmed_1 = Path(str(plan["trimmed_read_1"]))
        trimmed_2 = Path(str(plan["trimmed_read_2"]))
        trimmed_1.parent.mkdir(parents=True, exist_ok=True)
        if force or not (trimmed_1.is_file() and trimmed_2.is_file()):
            run_logged(plan["fastp"], log)
        ensure_nonempty(trimmed_1, "trimmed R1")
        ensure_nonempty(trimmed_2, "trimmed R2")

        trinity_fasta = Path(str(plan["trinity_fasta"]))
        if force or not trinity_fasta.is_file():
            run_logged(plan["trinity"], log)
        ensure_nonempty(trinity_fasta, "Trinity transcriptome")

        copied_trinity = Path(str(plan["copied_trinity_fasta"]))
        copied_trinity.parent.mkdir(parents=True, exist_ok=True)
        if force or not copied_trinity.is_file():
            copied_trinity.write_bytes(trinity_fasta.read_bytes())

        peptide = Path(str(plan["transdecoder_peptide_fasta"]))
        if force or not peptide.is_file():
            run_logged(plan["longorfs"], log, cwd=copied_trinity.parent)
            run_logged(plan["predict"], log, cwd=copied_trinity.parent)
        ensure_nonempty(peptide, "TransDecoder peptide FASTA")

        prefixed.parent.mkdir(parents=True, exist_ok=True)
        if force or not prefixed.is_file():
            run_logged(plan["prefix"], log)
        ensure_nonempty(prefixed, "prefixed proteome FASTA")

        if not keep_raw_reads:
            for path in (raw_1, raw_2):
                if path.exists():
                    path.unlink()
        status = "completed"
        error = ""
    except Exception as exc:
        status = "failed"
        error = f"{type(exc).__name__}: {exc}"

    finished = time.time()
    return {
        **base,
        "status": status,
        "finished_at_unix": f"{finished:.6f}",
        "elapsed_seconds": f"{finished - started:.6f}",
        "error": error,
    }


def execute(
    plans: Sequence[Mapping[str, object]],
    *,
    outdir: Path,
    jobs: int,
    dry_run: bool,
    force: bool,
    keep_raw_reads: bool,
) -> list[dict[str, object]]:
    if jobs < 1:
        raise ValueError("jobs must be >= 1")
    if dry_run or jobs == 1:
        return [
            run_one(
                plan,
                outdir=outdir,
                dry_run=dry_run,
                force=force,
                keep_raw_reads=keep_raw_reads,
            )
            for plan in plans
        ]
    output: list[dict[str, object]] = []
    with ThreadPoolExecutor(max_workers=jobs) as executor:
        futures = {
            executor.submit(
                run_one,
                plan,
                outdir=outdir,
                dry_run=False,
                force=force,
                keep_raw_reads=keep_raw_reads,
            ): str(plan["sample_id"])
            for plan in plans
        }
        for future in as_completed(futures):
            output.append(future.result())
    return sorted(output, key=lambda row: str(row["sample_id"]))


def build_summary(
    rows: Sequence[Mapping[str, object]],
    *,
    dry_run: bool,
    keep_raw_reads: bool,
) -> dict[str, object]:
    statuses = Counter(str(row["status"]) for row in rows)
    return {
        "sample_count": len(rows),
        "status_counts": dict(sorted(statuses.items())),
        "completed_or_existing_proteome_count": statuses.get("completed", 0)
        + statuses.get("skipped_existing_prefixed_proteome", 0),
        "failed_count": statuses.get("failed", 0),
        "dry_run": dry_run,
        "keep_raw_reads": keep_raw_reads,
        "assembly_sequence": [
            "fasterq-dump paired official SRA run",
            "pigz raw reads",
            "fastp paired-end QC and trimming",
            "Trinity de novo transcriptome assembly",
            "TransDecoder LongOrfs and Predict --single_best_only",
            "prefix protein identifiers with stable panel sample_id",
        ],
        "claim_limit": (
            "Successful command completion does not establish assembly completeness or orthology. Read QC, transcriptome metrics, BUSCO/reference recovery, one-to-one orthogroup validation, and multi-copy sensitivity remain required."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--fasterq-threads", type=int, default=8)
    parser.add_argument("--fastp-threads", type=int, default=8)
    parser.add_argument("--trinity-threads", type=int, default=16)
    parser.add_argument("--trinity-memory-gb", type=int, default=96)
    parser.add_argument("--fasterq", default="fasterq-dump")
    parser.add_argument("--pigz", default="pigz")
    parser.add_argument("--fastp", default="fastp")
    parser.add_argument("--trinity", default="Trinity")
    parser.add_argument("--transdecoder-longorfs", default="TransDecoder.LongOrfs")
    parser.add_argument("--transdecoder-predict", default="TransDecoder.Predict")
    parser.add_argument("--python", default=os.environ.get("PYTHON", "python"))
    parser.add_argument(
        "--prefix-script",
        type=Path,
        default=Path(__file__).with_name("prefix_fasta_headers.py"),
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--keep-raw-reads", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    for name in (
        "fasterq_threads",
        "fastp_threads",
        "trinity_threads",
        "trinity_memory_gb",
    ):
        if getattr(args, name) < 1:
            raise SystemExit(f"--{name.replace('_', '-')} must be >= 1")

    panel = validate_panel(args.panel)
    plans = [
        command_plan(
            row,
            outdir=args.outdir,
            fasterq_threads=args.fasterq_threads,
            fastp_threads=args.fastp_threads,
            trinity_threads=args.trinity_threads,
            trinity_memory_gb=args.trinity_memory_gb,
            fasterq_executable=args.fasterq,
            pigz_executable=args.pigz,
            fastp_executable=args.fastp,
            trinity_executable=args.trinity,
            transdecoder_longorfs_executable=args.transdecoder_longorfs,
            transdecoder_predict_executable=args.transdecoder_predict,
            python_executable=args.python,
            prefix_script=args.prefix_script,
        )
        for row in panel
    ]
    results = execute(
        plans,
        outdir=args.outdir,
        jobs=args.jobs,
        dry_run=args.dry_run,
        force=args.force,
        keep_raw_reads=args.keep_raw_reads,
    )
    summary = build_summary(
        results,
        dry_run=args.dry_run,
        keep_raw_reads=args.keep_raw_reads,
    )

    args.outdir.mkdir(parents=True, exist_ok=True)
    write_csv(args.outdir / "transcriptome_assembly_run_manifest.csv", results, RUN_FIELDS)
    write_csv(
        args.outdir / "transcriptome_assembly_command_plan.csv",
        (
            {
                **plan,
                "status": "planned",
                "started_at_unix": "",
                "finished_at_unix": "",
                "elapsed_seconds": "",
                "error": "",
            }
            for plan in plans
        ),
        RUN_FIELDS,
    )
    (args.outdir / "transcriptome_assembly_run_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_csv(
        args.outdir / "transcriptome_assembly_run_summary.csv",
        (
            {
                "metric": key,
                "value": json.dumps(value, ensure_ascii=False)
                if isinstance(value, (dict, list))
                else value,
            }
            for key, value in summary.items()
        ),
        SUMMARY_FIELDS,
    )

    print(f"sample_count={summary['sample_count']}")
    print("status_counts=" + json.dumps(summary["status_counts"], sort_keys=True))
    print(f"failed_count={summary['failed_count']}")
    print(args.outdir / "transcriptome_assembly_run_manifest.csv")
    if not args.dry_run and summary["failed_count"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
