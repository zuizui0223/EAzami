#!/usr/bin/env python3
"""Run Chang 2026 transcriptome assembly using official SRA LibraryLayout.

The original assembly runner is retained as the implementation of the paired-end
fasterq/fastp/Trinity/TransDecoder pipeline. This adapter replaces and extends
the input contract:

* library layout is read from the official SRA ``LibraryLayout`` field carried
  through the reconciled panel;
* the supplement raw-read versus SRA-spot relation remains a provenance and
  reconciliation diagnostic, not a sequencing-layout classifier;
* the current heavy pipeline is allowed only when every selected run is
  officially ``PAIRED``;
* the frozen 19-sample panel and the six-takaoense pilot are both accepted when
  their expected panel size is declared explicitly; and
* one or more stable sample IDs can be selected for restartable resource pilots.

All current Chang gene-tree-panel runs are officially paired-end. A future
single-end run fails explicitly until a separately tested command path is added;
it is never coerced into the paired workflow.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Mapping, Sequence

import run_chang2026_transcriptome_assembly as paired

DEFAULT_OUTDIR = paired.DEFAULT_OUTDIR
SUMMARY_FIELDS = paired.SUMMARY_FIELDS
RUN_FIELDS = (
    "sample_id",
    "taxon",
    "morph",
    "run",
    "library_layout",
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

clean = paired.clean
read_csv = paired.read_csv
write_csv = paired.write_csv


def validate_panel(
    path: Path,
    *,
    expected_samples: int = 19,
) -> list[dict[str, str]]:
    """Validate a declared frozen panel using official SRA metadata."""
    if expected_samples < 1:
        raise ValueError("expected_samples must be >= 1")
    rows = read_csv(path)
    if not rows:
        raise ValueError(f"No panel rows in {path}")
    if len(rows) != expected_samples:
        raise ValueError(
            f"Expected {expected_samples} panel samples, observed {len(rows)}"
        )

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

    missing_layout = [
        clean(row.get("sample_id"))
        for row in rows
        if not clean(row.get("library_layout"))
    ]
    if missing_layout:
        raise ValueError(
            "Panel rows lack official SRA LibraryLayout: "
            + "|".join(missing_layout)
        )

    unsupported = [
        f"{clean(row.get('sample_id'))}:{clean(row.get('library_layout')).upper()}"
        for row in rows
        if clean(row.get("library_layout")).upper() != "PAIRED"
    ]
    if unsupported:
        raise ValueError(
            "Current assembly implementation is paired-end only; official SRA "
            "LibraryLayout is not PAIRED for: " + "|".join(unsupported)
        )

    if expected_samples == 6:
        roles = Counter(clean(row.get("panel_role")) for row in rows)
        morphs = Counter(clean(row.get("morph")).upper() for row in rows)
        if roles != {"focal_colour_morph": 6}:
            raise ValueError(
                "Six-sample pilot must contain only focal_colour_morph rows: "
                f"{dict(roles)}"
            )
        if morphs != {"BP": 3, "W": 3}:
            raise ValueError(
                "Six-sample pilot must contain three BP and three W samples: "
                f"{dict(morphs)}"
            )

    return sorted(rows, key=lambda row: row["sample_id"])


def select_panel_rows(
    rows: Sequence[Mapping[str, str]],
    sample_ids: Sequence[str] | None,
) -> list[dict[str, str]]:
    """Select stable sample IDs without changing the validated input panel."""
    requested = [clean(value) for value in (sample_ids or []) if clean(value)]
    if not requested:
        return [dict(row) for row in rows]
    if len(requested) != len(set(requested)):
        raise ValueError("--sample-id values must be unique")
    index = {clean(row.get("sample_id")): dict(row) for row in rows}
    missing = [sample_id for sample_id in requested if sample_id not in index]
    if missing:
        raise ValueError(
            "Requested sample IDs are absent from the validated panel: "
            + "|".join(missing)
        )
    return [index[sample_id] for sample_id in requested]


def command_plan(
    row: Mapping[str, str],
    **kwargs: object,
) -> dict[str, object]:
    """Build the existing paired-end plan after validating official layout."""
    layout = clean(row.get("library_layout")).upper()
    if layout != "PAIRED":
        raise ValueError(
            f"Sample {clean(row.get('sample_id'))} has unsupported layout {layout!r}"
        )
    plan = paired.command_plan(row, **kwargs)
    plan["library_layout"] = layout
    return plan


def run_one(
    plan: Mapping[str, object],
    *,
    outdir: Path,
    dry_run: bool,
    force: bool,
    keep_raw_reads: bool,
) -> dict[str, object]:
    """Execute the paired implementation and retain layout provenance."""
    result = paired.run_one(
        plan,
        outdir=outdir,
        dry_run=dry_run,
        force=force,
        keep_raw_reads=keep_raw_reads,
    )
    result["library_layout"] = clean(plan.get("library_layout")).upper()
    return result


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
    input_panel_sample_count: int | None = None,
    selected_sample_ids: Sequence[str] | None = None,
) -> dict[str, object]:
    summary = paired.build_summary(
        rows,
        dry_run=dry_run,
        keep_raw_reads=keep_raw_reads,
    )
    layouts = Counter(clean(row.get("library_layout")).upper() for row in rows)
    selected = [clean(value) for value in (selected_sample_ids or [])]
    input_count = input_panel_sample_count if input_panel_sample_count is not None else len(rows)
    summary["official_library_layout_counts"] = dict(sorted(layouts.items()))
    summary["library_layout_source"] = "official NCBI SRA LibraryLayout"
    summary["read_count_relation_role"] = (
        "Reconciliation diagnostic only; not used to infer sequencing layout."
    )
    summary["input_panel_sample_count"] = input_count
    summary["selected_sample_count"] = len(rows)
    summary["selected_sample_ids"] = selected or [
        clean(row.get("sample_id")) for row in rows
    ]
    summary["subset_execution"] = len(rows) != input_count
    summary["assembly_sequence"] = [
        "fasterq-dump --split-files on officially PAIRED SRA run",
        "pigz raw read mates",
        "fastp paired-end QC and trimming",
        "Trinity de novo transcriptome assembly",
        "TransDecoder LongOrfs and Predict --single_best_only",
        "prefix protein identifiers with stable panel sample_id",
    ]
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--expected-panel-samples", type=int, default=19)
    parser.add_argument(
        "--sample-id",
        action="append",
        default=[],
        help=(
            "Stable sample_id to execute; repeat for multiple samples. The full "
            "input panel is validated before selection."
        ),
    )
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
        "expected_panel_samples",
        "fasterq_threads",
        "fastp_threads",
        "trinity_threads",
        "trinity_memory_gb",
    ):
        if getattr(args, name) < 1:
            raise SystemExit(f"--{name.replace('_', '-')} must be >= 1")

    validated_panel = validate_panel(
        args.panel,
        expected_samples=args.expected_panel_samples,
    )
    panel_rows = select_panel_rows(validated_panel, args.sample_id)
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
        for row in panel_rows
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
        input_panel_sample_count=len(validated_panel),
        selected_sample_ids=[clean(row.get("sample_id")) for row in panel_rows],
    )

    args.outdir.mkdir(parents=True, exist_ok=True)
    write_csv(
        args.outdir / "transcriptome_assembly_run_manifest.csv",
        results,
        RUN_FIELDS,
    )
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

    print(f"input_panel_sample_count={summary['input_panel_sample_count']}")
    print(f"selected_sample_count={summary['selected_sample_count']}")
    print("selected_sample_ids=" + "|".join(summary["selected_sample_ids"]))
    print("status_counts=" + json.dumps(summary["status_counts"], sort_keys=True))
    print(
        "official_library_layout_counts="
        + json.dumps(summary["official_library_layout_counts"], sort_keys=True)
    )
    print(f"failed_count={summary['failed_count']}")
    print(args.outdir / "transcriptome_assembly_run_manifest.csv")
    if not args.dry_run and summary["failed_count"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
