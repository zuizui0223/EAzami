#!/usr/bin/env python3
"""Run MAFFT, ClipKIT and rooted IQ-TREE for validated orthogroups.

This runner consumes the conservative manifest produced by
``prepare_chang2026_single_copy_orthogroups.py``.  It is restartable, records the
exact command for every orthogroup, and supports a dry-run mode used in CI.

Trees are rooted in IQ-TREE with the two panel samples whose role is ``outgroup``
(Cirsium lineare).  The output is suitable for
``score_chang2026_gene_tree_hypotheses.py``.  The runner does not claim locus
independence or infer introgression; it only creates auditable gene-tree inputs.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import shlex
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Iterable, Mapping, Sequence

DEFAULT_OUTDIR = Path("results/chang2026_gene_trees")

RUN_FIELDS = (
    "orthogroup_id",
    "normalized_fasta",
    "alignment_fasta",
    "trimmed_alignment_fasta",
    "tree_prefix",
    "tree_file",
    "status",
    "mafft_command",
    "clipkit_command",
    "iqtree_command",
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


def read_outgroups(panel_path: Path) -> list[str]:
    rows = read_csv(panel_path)
    outgroups = [
        clean(row.get("sample_id"))
        for row in rows
        if clean(row.get("panel_role")) == "outgroup"
    ]
    if len(outgroups) != 2 or len(set(outgroups)) != 2:
        raise ValueError(
            f"Expected exactly two unique outgroup samples, observed {outgroups}"
        )
    return sorted(outgroups)


def complete_manifest_rows(path: Path) -> list[dict[str, str]]:
    rows = [
        row
        for row in read_csv(path)
        if clean(row.get("status")) == "complete_single_copy"
    ]
    if not rows:
        raise ValueError(f"No complete_single_copy rows in {path}")
    ids = [clean(row.get("orthogroup_id")) for row in rows]
    if any(not value for value in ids) or len(ids) != len(set(ids)):
        raise ValueError("Missing or duplicate orthogroup IDs in manifest")
    for row in rows:
        fasta = Path(clean(row.get("normalized_fasta")))
        if not fasta.is_file() or fasta.stat().st_size == 0:
            raise FileNotFoundError(
                f"Normalized FASTA is missing or empty for {row['orthogroup_id']}: {fasta}"
            )
    return sorted(rows, key=lambda row: row["orthogroup_id"])


def command_plan(
    row: Mapping[str, str],
    *,
    outdir: Path,
    outgroups: Sequence[str],
    threads_per_gene: int,
    bootstrap_replicates: int,
    alrt_replicates: int,
    mafft_executable: str,
    clipkit_executable: str,
    iqtree_executable: str,
) -> dict[str, object]:
    orthogroup_id = clean(row.get("orthogroup_id"))
    normalized = Path(clean(row.get("normalized_fasta")))
    alignment = outdir / "alignments" / f"{orthogroup_id}.mafft.fa"
    trimmed = outdir / "trimmed" / f"{orthogroup_id}.clipkit.fa"
    prefix = outdir / "trees" / orthogroup_id
    tree_file = Path(str(prefix) + ".treefile")

    mafft = [
        mafft_executable,
        "--auto",
        "--thread",
        str(threads_per_gene),
        str(normalized),
    ]
    clipkit = [
        clipkit_executable,
        str(alignment),
        "-o",
        str(trimmed),
        "-m",
        "smart-gap",
    ]
    iqtree = [
        iqtree_executable,
        "-s",
        str(trimmed),
        "-m",
        "MFP",
        "-B",
        str(bootstrap_replicates),
        "--alrt",
        str(alrt_replicates),
        "-T",
        str(threads_per_gene),
        "-o",
        ",".join(outgroups),
        "--prefix",
        str(prefix),
        "--redo",
    ]
    return {
        "orthogroup_id": orthogroup_id,
        "normalized_fasta": str(normalized),
        "alignment_fasta": str(alignment),
        "trimmed_alignment_fasta": str(trimmed),
        "tree_prefix": str(prefix),
        "tree_file": str(tree_file),
        "mafft": mafft,
        "clipkit": clipkit,
        "iqtree": iqtree,
        "mafft_command": shlex.join(mafft) + f" > {shlex.quote(str(alignment))}",
        "clipkit_command": shlex.join(clipkit),
        "iqtree_command": shlex.join(iqtree),
    }


def run_command(
    command: Sequence[str],
    *,
    stdout_path: Path | None,
    log_path: Path,
) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if stdout_path is not None:
        stdout_path.parent.mkdir(parents=True, exist_ok=True)
        with stdout_path.open("w", encoding="utf-8") as stdout, log_path.open(
            "w", encoding="utf-8"
        ) as log:
            subprocess.run(
                list(command),
                check=True,
                stdout=stdout,
                stderr=log,
                text=True,
            )
    else:
        with log_path.open("w", encoding="utf-8") as log:
            subprocess.run(
                list(command),
                check=True,
                stdout=log,
                stderr=subprocess.STDOUT,
                text=True,
            )


def run_one(
    plan: Mapping[str, object],
    *,
    outdir: Path,
    dry_run: bool,
    force: bool,
) -> dict[str, object]:
    started = time.time()
    tree_file = Path(str(plan["tree_file"]))
    base = {
        "orthogroup_id": plan["orthogroup_id"],
        "normalized_fasta": plan["normalized_fasta"],
        "alignment_fasta": plan["alignment_fasta"],
        "trimmed_alignment_fasta": plan["trimmed_alignment_fasta"],
        "tree_prefix": plan["tree_prefix"],
        "tree_file": plan["tree_file"],
        "mafft_command": plan["mafft_command"],
        "clipkit_command": plan["clipkit_command"],
        "iqtree_command": plan["iqtree_command"],
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
    if tree_file.is_file() and tree_file.stat().st_size > 0 and not force:
        finished = time.time()
        return {
            **base,
            "status": "skipped_existing_tree",
            "finished_at_unix": f"{finished:.6f}",
            "elapsed_seconds": f"{finished - started:.6f}",
            "error": "",
        }

    alignment = Path(str(plan["alignment_fasta"]))
    trimmed = Path(str(plan["trimmed_alignment_fasta"]))
    orthogroup = str(plan["orthogroup_id"])
    try:
        if force or not alignment.is_file() or alignment.stat().st_size == 0:
            run_command(
                plan["mafft"],
                stdout_path=alignment,
                log_path=outdir / "logs" / f"{orthogroup}.mafft.log",
            )
        if force or not trimmed.is_file() or trimmed.stat().st_size == 0:
            run_command(
                plan["clipkit"],
                stdout_path=None,
                log_path=outdir / "logs" / f"{orthogroup}.clipkit.log",
            )
        Path(str(plan["tree_prefix"])).parent.mkdir(parents=True, exist_ok=True)
        run_command(
            plan["iqtree"],
            stdout_path=None,
            log_path=outdir / "logs" / f"{orthogroup}.iqtree.log",
        )
        if not tree_file.is_file() or tree_file.stat().st_size == 0:
            raise RuntimeError(f"IQ-TREE did not create {tree_file}")
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
) -> list[dict[str, object]]:
    if jobs < 1:
        raise ValueError("jobs must be >= 1")
    if dry_run or jobs == 1:
        return [
            run_one(plan, outdir=outdir, dry_run=dry_run, force=force)
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
            ): str(plan["orthogroup_id"])
            for plan in plans
        }
        for future in as_completed(futures):
            output.append(future.result())
    return sorted(output, key=lambda row: str(row["orthogroup_id"]))


def build_summary(
    rows: Sequence[Mapping[str, object]],
    *,
    outgroups: Sequence[str],
    dry_run: bool,
) -> dict[str, object]:
    statuses = Counter(str(row["status"]) for row in rows)
    return {
        "orthogroup_count": len(rows),
        "status_counts": dict(sorted(statuses.items())),
        "completed_or_existing_tree_count": statuses.get("completed", 0)
        + statuses.get("skipped_existing_tree", 0),
        "failed_count": statuses.get("failed", 0),
        "dry_run": dry_run,
        "outgroup_samples": list(outgroups),
        "rooting_policy": "IQ-TREE -o with both Cirsium lineare panel samples",
        "support_policy": "SH-aLRT and ultrafast bootstrap are written to internal labels; downstream scoring uses the last numeric label component as UFBoot.",
        "claim_limit": (
            "Generated gene trees are locus-level inputs. Concordance counts require orthology, alignment-quality, linkage, and multi-copy sensitivity checks before biological interpretation."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--threads-per-gene", type=int, default=1)
    parser.add_argument("--bootstrap-replicates", type=int, default=1000)
    parser.add_argument("--alrt-replicates", type=int, default=1000)
    parser.add_argument("--mafft", default="mafft")
    parser.add_argument("--clipkit", default="clipkit")
    parser.add_argument("--iqtree", default="iqtree2")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.threads_per_gene < 1:
        raise SystemExit("--threads-per-gene must be >= 1")
    outgroups = read_outgroups(args.panel)
    manifest_rows = complete_manifest_rows(args.manifest)
    plans = [
        command_plan(
            row,
            outdir=args.outdir,
            outgroups=outgroups,
            threads_per_gene=args.threads_per_gene,
            bootstrap_replicates=args.bootstrap_replicates,
            alrt_replicates=args.alrt_replicates,
            mafft_executable=args.mafft,
            clipkit_executable=args.clipkit,
            iqtree_executable=args.iqtree,
        )
        for row in manifest_rows
    ]
    results = execute(
        plans,
        outdir=args.outdir,
        jobs=args.jobs,
        dry_run=args.dry_run,
        force=args.force,
    )
    summary = build_summary(
        results,
        outgroups=outgroups,
        dry_run=args.dry_run,
    )

    args.outdir.mkdir(parents=True, exist_ok=True)
    write_csv(args.outdir / "gene_tree_run_manifest.csv", results, RUN_FIELDS)
    write_csv(
        args.outdir / "gene_tree_command_plan.csv",
        (
            {
                **row,
                "status": "planned",
                "started_at_unix": "",
                "finished_at_unix": "",
                "elapsed_seconds": "",
                "error": "",
            }
            for row in plans
        ),
        RUN_FIELDS,
    )
    (args.outdir / "gene_tree_run_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_csv(
        args.outdir / "gene_tree_run_summary.csv",
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

    print(f"orthogroup_count={summary['orthogroup_count']}")
    print("status_counts=" + json.dumps(summary["status_counts"], sort_keys=True))
    print(f"failed_count={summary['failed_count']}")
    print(args.outdir / "gene_tree_run_manifest.csv")
    if not args.dry_run and summary["failed_count"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
