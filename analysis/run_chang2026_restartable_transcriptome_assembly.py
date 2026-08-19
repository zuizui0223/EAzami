#!/usr/bin/env python3
"""Canonical restartable local/HPC runner for the Chang 2026 transcriptome panel.

This is the execution path for the public RNA-seq data. It validates the frozen
panel directly from reconciled official SRA metadata, requires official
``LibraryLayout=PAIRED``, uses restartable ``prefetch`` plus ``vdb-validate``,
converts local accessions with an explicit fasterq scratch directory, and keeps
Trinity's working directory so restart state and ``Trinity.fasta`` survive.

The six-takaoense pilot additionally remains frozen at BP=3 / W=3. Heavy
execution is external/HPC; PR CI exercises dry-run and restart contracts only.
"""

from __future__ import annotations

import argparse
import csv
import json
import platform
import shlex
import shutil
import subprocess
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Iterable, Mapping, Sequence

DEFAULT_OUTDIR = Path("results/chang2026_transcriptomes_restartable")
STAGES = (
    "prefetch", "vdb_validate", "fasterq", "pigz", "fastp", "trinity",
    "transdecoder_longorfs", "transdecoder_predict", "prefix_headers",
)
RUN_FIELDS = (
    "sample_id", "taxon", "morph", "run", "library_layout", "status",
    "completed_stage", "sra_dir", "raw_read_1", "raw_read_2",
    "trimmed_read_1", "trimmed_read_2", "fastp_json", "trinity_fasta",
    "transdecoder_peptide_fasta", "prefixed_proteome_fasta",
    "started_at_unix", "finished_at_unix", "elapsed_seconds", "error",
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


def write_csv(path: Path, rows: Iterable[Mapping[str, object]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def validate_panel(path: Path, *, expected_samples: int) -> list[dict[str, str]]:
    """Validate the frozen panel using reconciled official SRA metadata."""
    if expected_samples < 1:
        raise ValueError("expected_samples must be >= 1")
    rows = read_csv(path)
    if not rows:
        raise ValueError(f"No panel rows in {path}")
    if len(rows) != expected_samples:
        raise ValueError(f"Expected {expected_samples} panel samples, observed {len(rows)}")

    sample_ids = [clean(row.get("sample_id")) for row in rows]
    runs = [clean(row.get("matched_run")) for row in rows]
    if any(not value for value in sample_ids + runs):
        raise ValueError("One or more panel rows lack sample_id or matched_run")
    if len(sample_ids) != len(set(sample_ids)):
        raise ValueError("Panel sample_id values are not unique")
    if len(runs) != len(set(runs)):
        raise ValueError("Official SRA run values are not unique")

    unresolved = [
        row for row in rows
        if clean(row.get("run_match_confidence")) not in {"verified", "probable"}
    ]
    if unresolved:
        raise ValueError(
            "Panel contains unresolved run mappings: "
            + "|".join(clean(row.get("sample_id")) for row in unresolved)
        )

    wrong_source = [
        row for row in rows
        if clean(row.get("de_novo_required")) != "true"
        or clean(row.get("preferred_sequence_source")) != clean(row.get("matched_run"))
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
            "Panel rows lack official SRA LibraryLayout: " + "|".join(missing_layout)
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


def select_rows(
    rows: Sequence[Mapping[str, str]], sample_ids: Sequence[str] | None
) -> list[dict[str, str]]:
    """Select stable sample IDs only after the complete input panel is validated."""
    requested = [clean(value) for value in (sample_ids or []) if clean(value)]
    if not requested:
        return [dict(row) for row in rows]
    if len(requested) != len(set(requested)):
        raise ValueError("--sample-id values must be unique")
    index = {clean(row.get("sample_id")): dict(row) for row in rows}
    missing = [sample_id for sample_id in requested if sample_id not in index]
    if missing:
        raise ValueError(
            "Requested sample IDs are absent from the validated panel: " + "|".join(missing)
        )
    return [index[sample_id] for sample_id in requested]


def command_plan(
    row: Mapping[str, str], *, outdir: Path, fasterq_threads: int,
    fastp_threads: int, trinity_threads: int, trinity_memory_gb: int,
    prefetch_executable: str = "prefetch", vdb_validate_executable: str = "vdb-validate",
    fasterq_executable: str = "fasterq-dump", pigz_executable: str = "pigz",
    fastp_executable: str = "fastp", trinity_executable: str = "Trinity",
    transdecoder_longorfs_executable: str = "TransDecoder.LongOrfs",
    transdecoder_predict_executable: str = "TransDecoder.Predict",
    python_executable: str = sys.executable, prefix_script: Path | None = None,
) -> dict[str, object]:
    if min(fasterq_threads, fastp_threads, trinity_threads, trinity_memory_gb) < 1:
        raise ValueError("All resource values must be >= 1")
    if clean(row.get("library_layout")).upper() != "PAIRED":
        raise ValueError("Restartable runner currently supports PAIRED runs only")
    prefix_script = prefix_script or Path(__file__).with_name("prefix_fasta_headers.py")
    sample_id = clean(row.get("sample_id")); run = clean(row.get("matched_run"))
    root = outdir / "samples" / sample_id
    sra_dir = root / "sra" / run
    raw = root / "raw"; scratch = root / "scratch" / "fasterq"
    trimmed = root / "trimmed"; trinity_dir = root / "trinity"
    transdecoder = root / "transdecoder"; state = root / "state"; resources = root / "resources"
    raw1u = raw / f"{run}_1.fastq"; raw2u = raw / f"{run}_2.fastq"
    raw1 = Path(str(raw1u) + ".gz"); raw2 = Path(str(raw2u) + ".gz")
    trim1 = trimmed / f"{sample_id}.R1.trim.fastq.gz"; trim2 = trimmed / f"{sample_id}.R2.trim.fastq.gz"
    fastp_json = trimmed / f"{sample_id}.fastp.json"; fastp_html = trimmed / f"{sample_id}.fastp.html"
    trinity_fasta = trinity_dir / "Trinity.fasta"
    copied = transdecoder / "Trinity.fasta"; peptide = transdecoder / "Trinity.fasta.transdecoder.pep"
    prefixed = outdir / "prefixed_proteomes" / f"{sample_id}.faa"
    commands = {
        "prefetch": [prefetch_executable, run, "--max-size", "u", "-O", str(sra_dir)],
        "vdb_validate": [vdb_validate_executable, str(sra_dir)],
        "fasterq": [fasterq_executable, str(sra_dir), "--split-files", "-e", str(fasterq_threads), "-O", str(raw), "-t", str(scratch)],
        "pigz": [pigz_executable, "-p", str(fasterq_threads), "-f", str(raw1u), str(raw2u)],
        "fastp": [fastp_executable, "-i", str(raw1), "-I", str(raw2), "-o", str(trim1), "-O", str(trim2), "--thread", str(fastp_threads), "--detect_adapter_for_pe", "--json", str(fastp_json), "--html", str(fastp_html)],
        "trinity": [trinity_executable, "--seqType", "fq", "--left", str(trim1), "--right", str(trim2), "--CPU", str(trinity_threads), "--max_memory", f"{trinity_memory_gb}G", "--output", str(trinity_dir)],
        "transdecoder_longorfs": [transdecoder_longorfs_executable, "-t", str(copied)],
        "transdecoder_predict": [transdecoder_predict_executable, "-t", str(copied), "--single_best_only"],
        "prefix_headers": [python_executable, str(prefix_script), "--input", str(peptide), "--output", str(prefixed), "--sample-id", sample_id],
    }
    return {
        "sample_id": sample_id, "taxon": clean(row.get("taxon")), "morph": clean(row.get("morph")),
        "run": run, "library_layout": "PAIRED", "sample_root": str(root), "sra_dir": str(sra_dir),
        "raw_read_1_uncompressed": str(raw1u), "raw_read_2_uncompressed": str(raw2u),
        "raw_read_1": str(raw1), "raw_read_2": str(raw2), "trimmed_read_1": str(trim1),
        "trimmed_read_2": str(trim2), "fastp_json": str(fastp_json), "trinity_fasta": str(trinity_fasta),
        "copied_trinity_fasta": str(copied), "transdecoder_peptide_fasta": str(peptide),
        "prefixed_proteome_fasta": str(prefixed), "state_dir": str(state), "resource_dir": str(resources),
        "commands": commands, "command_strings": {name: shlex.join(cmd) for name, cmd in commands.items()},
    }


def nonempty(path: Path) -> bool:
    return path.is_file() and path.stat().st_size > 0


def require_nonempty(path: Path, label: str) -> None:
    if not nonempty(path):
        raise RuntimeError(f"{label} missing or empty: {path}")


def marker(plan: Mapping[str, object], stage: str) -> Path:
    return Path(str(plan["state_dir"])) / f"{stage}.done.json"


def mark_done(plan: Mapping[str, object], stage: str) -> None:
    path = marker(plan, stage); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"stage": stage, "completed_at_unix": time.time()}, indent=2) + "\n", encoding="utf-8")


def run_logged(command: Sequence[str], log: Path, resource_file: Path, *, cwd: Path | None = None) -> None:
    log.parent.mkdir(parents=True, exist_ok=True); resource_file.parent.mkdir(parents=True, exist_ok=True)
    time_exe = shutil.which("/usr/bin/time") or shutil.which("time")
    actual = [time_exe, "-v", "-o", str(resource_file)] + list(command) if time_exe else list(command)
    with log.open("a", encoding="utf-8") as handle:
        handle.write("\n$ " + shlex.join(actual) + "\n"); handle.flush()
        subprocess.run(actual, cwd=str(cwd) if cwd else None, check=True, stdout=handle, stderr=subprocess.STDOUT, text=True)


def run_stage(plan: Mapping[str, object], stage: str, *, cwd: Path | None = None) -> None:
    log = Path(str(plan["sample_root"])) / "assembly.log"
    resource = Path(str(plan["resource_dir"])) / f"{stage}.time.txt"
    run_logged(plan["commands"][stage], log, resource, cwd=cwd)
    mark_done(plan, stage)


def _remove(paths: Sequence[Path]) -> None:
    for path in paths:
        if path.is_file() or path.is_symlink(): path.unlink()
        elif path.is_dir(): shutil.rmtree(path)


def execute_one(
    plan: Mapping[str, object], *, dry_run: bool, force: bool,
    delete_raw_after_success: bool, delete_sra_after_success: bool,
) -> dict[str, object]:
    start = time.time(); completed = "none"
    base = {key: plan[key] for key in ("sample_id", "taxon", "morph", "run", "library_layout", "sra_dir", "raw_read_1", "raw_read_2", "trimmed_read_1", "trimmed_read_2", "fastp_json", "trinity_fasta", "transdecoder_peptide_fasta", "prefixed_proteome_fasta")}
    if dry_run:
        end = time.time(); return {**base, "status": "planned_dry_run", "completed_stage": completed, "started_at_unix": f"{start:.6f}", "finished_at_unix": f"{end:.6f}", "elapsed_seconds": f"{end-start:.6f}", "error": ""}
    if nonempty(Path(str(plan["prefixed_proteome_fasta"]))) and not force:
        end = time.time(); return {**base, "status": "skipped_existing_prefixed_proteome", "completed_stage": "prefix_headers", "started_at_unix": f"{start:.6f}", "finished_at_unix": f"{end:.6f}", "elapsed_seconds": f"{end-start:.6f}", "error": ""}
    try:
        root = Path(str(plan["sample_root"])); sra_dir = Path(str(plan["sra_dir"])); root.mkdir(parents=True, exist_ok=True)
        raw1u = Path(str(plan["raw_read_1_uncompressed"])); raw2u = Path(str(plan["raw_read_2_uncompressed"])); raw1 = Path(str(plan["raw_read_1"])); raw2 = Path(str(plan["raw_read_2"]))
        trim1 = Path(str(plan["trimmed_read_1"])); trim2 = Path(str(plan["trimmed_read_2"])); fastp_json = Path(str(plan["fastp_json"])); trinity = Path(str(plan["trinity_fasta"])); copied = Path(str(plan["copied_trinity_fasta"])); peptide = Path(str(plan["transdecoder_peptide_fasta"])); prefixed = Path(str(plan["prefixed_proteome_fasta"]))
        if force: _remove([Path(str(plan["state_dir"])), prefixed])
        if force or not marker(plan, "prefetch").exists(): run_stage(plan, "prefetch"); completed = "prefetch"
        if not sra_dir.is_dir(): raise RuntimeError(f"prefetch accession directory missing: {sra_dir}")
        if force or not marker(plan, "vdb_validate").exists(): run_stage(plan, "vdb_validate"); completed = "vdb_validate"
        gz_state = (nonempty(raw1), nonempty(raw2)); u_state = (nonempty(raw1u), nonempty(raw2u))
        if gz_state in {(True, False), (False, True)} or u_state in {(True, False), (False, True)}:
            raise RuntimeError("Partial paired FASTQ state detected; inspect before restart")
        if not all(gz_state):
            if any(u_state): raise RuntimeError("Uncompressed FASTQ pair exists without completed compression; inspect before restart")
            raw1.parent.mkdir(parents=True, exist_ok=True); Path(str(plan["sample_root"])).joinpath("scratch", "fasterq").mkdir(parents=True, exist_ok=True)
            run_stage(plan, "fasterq"); completed = "fasterq"; require_nonempty(raw1u, "fasterq R1"); require_nonempty(raw2u, "fasterq R2")
            run_stage(plan, "pigz"); completed = "pigz"
        require_nonempty(raw1, "raw R1.gz"); require_nonempty(raw2, "raw R2.gz")
        if not (nonempty(trim1) and nonempty(trim2) and nonempty(fastp_json)):
            _remove([trim1, trim2, fastp_json]); trim1.parent.mkdir(parents=True, exist_ok=True); run_stage(plan, "fastp"); completed = "fastp"
        require_nonempty(trim1, "trimmed R1"); require_nonempty(trim2, "trimmed R2"); require_nonempty(fastp_json, "fastp JSON")
        if not nonempty(trinity):
            trinity.parent.mkdir(parents=True, exist_ok=True); run_stage(plan, "trinity"); completed = "trinity"
        require_nonempty(trinity, "Trinity.fasta")
        copied.parent.mkdir(parents=True, exist_ok=True)
        if not nonempty(copied): shutil.copy2(trinity, copied)
        if force or not marker(plan, "transdecoder_longorfs").exists(): run_stage(plan, "transdecoder_longorfs", cwd=copied.parent); completed = "transdecoder_longorfs"
        if not nonempty(peptide): run_stage(plan, "transdecoder_predict", cwd=copied.parent); completed = "transdecoder_predict"
        require_nonempty(peptide, "TransDecoder peptide FASTA")
        if not nonempty(prefixed): prefixed.parent.mkdir(parents=True, exist_ok=True); run_stage(plan, "prefix_headers"); completed = "prefix_headers"
        require_nonempty(prefixed, "prefixed proteome")
        if delete_raw_after_success: _remove([raw1, raw2])
        if delete_sra_after_success: _remove([sra_dir])
        status = "completed"; error = ""
    except Exception as exc:
        status = "failed"; error = f"{type(exc).__name__}: {exc}"
    end = time.time()
    return {**base, "status": status, "completed_stage": completed, "started_at_unix": f"{start:.6f}", "finished_at_unix": f"{end:.6f}", "elapsed_seconds": f"{end-start:.6f}", "error": error}


def capture_versions(plan: Mapping[str, object], outdir: Path) -> dict[str, object]:
    version_args = {
        "prefetch": [plan["commands"]["prefetch"][0], "--version"], "vdb_validate": [plan["commands"]["vdb_validate"][0], "--version"],
        "fasterq": [plan["commands"]["fasterq"][0], "--version"], "pigz": [plan["commands"]["pigz"][0], "--version"],
        "fastp": [plan["commands"]["fastp"][0], "--version"], "trinity": [plan["commands"]["trinity"][0], "--version"],
        "transdecoder_longorfs": [plan["commands"]["transdecoder_longorfs"][0], "--version"], "transdecoder_predict": [plan["commands"]["transdecoder_predict"][0], "--version"],
    }
    payload: dict[str, object] = {"python": sys.version, "platform": platform.platform(), "tools": {}}
    for name, command in version_args.items():
        exe = str(command[0]); found = shutil.which(exe) is not None or Path(exe).is_file()
        item = {"command": shlex.join(command), "executable_found": found, "returncode": None, "output": "executable_not_found"}
        if found:
            try:
                process = subprocess.run(command, capture_output=True, text=True, timeout=30, check=False)
                item.update(returncode=process.returncode, output=(process.stdout + "\n" + process.stderr).strip()[:4000])
            except Exception as exc:
                item["output"] = f"{type(exc).__name__}: {exc}"
        payload["tools"][name] = item
    outdir.mkdir(parents=True, exist_ok=True); (outdir / "software_versions.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def disk_preflight(path: Path, required_gib: float) -> dict[str, float]:
    path.mkdir(parents=True, exist_ok=True); disk = shutil.disk_usage(path); free = disk.free / 1024**3
    if required_gib > 0 and free < required_gib:
        raise RuntimeError(f"Insufficient free disk: {free:.1f} GiB available; {required_gib:.1f} GiB required")
    return {"total_gib": disk.total/1024**3, "used_gib": disk.used/1024**3, "free_gib": free, "required_gib": required_gib}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(); parser.add_argument("--panel", type=Path, required=True); parser.add_argument("--expected-panel-samples", type=int, default=19); parser.add_argument("--sample-id", action="append", default=[]); parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR); parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--fasterq-threads", type=int, default=8); parser.add_argument("--fastp-threads", type=int, default=8); parser.add_argument("--trinity-threads", type=int, default=16); parser.add_argument("--trinity-memory-gb", type=int, default=96); parser.add_argument("--min-free-disk-gib", type=float, default=0)
    parser.add_argument("--prefetch", default="prefetch"); parser.add_argument("--vdb-validate", default="vdb-validate"); parser.add_argument("--fasterq", default="fasterq-dump"); parser.add_argument("--pigz", default="pigz"); parser.add_argument("--fastp", default="fastp"); parser.add_argument("--trinity", default="Trinity"); parser.add_argument("--transdecoder-longorfs", default="TransDecoder.LongOrfs"); parser.add_argument("--transdecoder-predict", default="TransDecoder.Predict"); parser.add_argument("--python", default=sys.executable); parser.add_argument("--prefix-script", type=Path, default=Path(__file__).with_name("prefix_fasta_headers.py"))
    parser.add_argument("--dry-run", action="store_true"); parser.add_argument("--preflight-only", action="store_true"); parser.add_argument("--force", action="store_true"); parser.add_argument("--delete-raw-after-success", action="store_true"); parser.add_argument("--delete-sra-after-success", action="store_true"); return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.jobs < 1: raise SystemExit("--jobs must be >= 1")
    validated = validate_panel(args.panel, expected_samples=args.expected_panel_samples); rows = select_rows(validated, args.sample_id)
    plans = [command_plan(row, outdir=args.outdir, fasterq_threads=args.fasterq_threads, fastp_threads=args.fastp_threads, trinity_threads=args.trinity_threads, trinity_memory_gb=args.trinity_memory_gb, prefetch_executable=args.prefetch, vdb_validate_executable=args.vdb_validate, fasterq_executable=args.fasterq, pigz_executable=args.pigz, fastp_executable=args.fastp, trinity_executable=args.trinity, transdecoder_longorfs_executable=args.transdecoder_longorfs, transdecoder_predict_executable=args.transdecoder_predict, python_executable=args.python, prefix_script=args.prefix_script) for row in rows]
    disk = disk_preflight(args.outdir, args.min_free_disk_gib); (args.outdir / "preflight_disk.json").write_text(json.dumps(disk, indent=2) + "\n", encoding="utf-8")
    versions = {} if args.dry_run else capture_versions(plans[0], args.outdir)
    cmd_rows = [{"sample_id": plan["sample_id"], "run": plan["run"], "morph": plan["morph"], "library_layout": plan["library_layout"], **{f"{stage}_command": plan["command_strings"][stage] for stage in STAGES}} for plan in plans]
    write_csv(args.outdir / "restartable_command_plan.csv", cmd_rows, ("sample_id", "run", "morph", "library_layout") + tuple(f"{stage}_command" for stage in STAGES))
    if args.preflight_only:
        missing = [name for name, item in versions.get("tools", {}).items() if not item.get("executable_found", False)]; print(f"selected_samples={len(plans)}"); print(f"disk_free_gib={disk['free_gib']:.3f}"); print("missing_executables=" + "|".join(missing)); return 1 if missing else 0
    if args.dry_run or args.jobs == 1:
        results = [execute_one(plan, dry_run=args.dry_run, force=args.force, delete_raw_after_success=args.delete_raw_after_success, delete_sra_after_success=args.delete_sra_after_success) for plan in plans]
    else:
        results = []
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            futures = [pool.submit(execute_one, plan, dry_run=False, force=args.force, delete_raw_after_success=args.delete_raw_after_success, delete_sra_after_success=args.delete_sra_after_success) for plan in plans]
            for future in as_completed(futures): results.append(future.result())
        results.sort(key=lambda row: str(row["sample_id"]))
    write_csv(args.outdir / "restartable_run_manifest.csv", results, RUN_FIELDS)
    statuses = Counter(str(row["status"]) for row in results)
    summary = {
        "runner_version": "chang2026_restartable_heavy_runner_v2_self_contained",
        "input_panel_sample_count": len(validated),
        "selected_sample_count": len(rows),
        "selected_sample_ids": [row["sample_id"] for row in rows],
        "status_counts": dict(sorted(statuses.items())),
        "failed_count": statuses.get("failed", 0),
        "dry_run": args.dry_run,
        "delete_raw_after_success": args.delete_raw_after_success,
        "delete_sra_after_success": args.delete_sra_after_success,
        "disk_preflight": disk,
        "library_layout_source": "official NCBI SRA LibraryLayout",
        "sra_execution_contract": "prefetch -> vdb-validate -> fasterq-dump local accession directory with explicit scratch",
        "trinity_cleanup": "disabled_to_preserve_Trinity.fasta_and_restart_state",
        "claim_limit": "Completion establishes execution of the public RNA-seq assembly pipeline only; it does not establish transcriptome completeness, orthology, introgression, or anthocyanin-pathway reactivation.",
    }
    (args.outdir / "restartable_run_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"selected_sample_count={len(rows)}"); print("selected_sample_ids=" + "|".join(row["sample_id"] for row in rows)); print("status_counts=" + json.dumps(summary["status_counts"], sort_keys=True)); return 1 if summary["failed_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
