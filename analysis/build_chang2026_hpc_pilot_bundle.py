#!/usr/bin/env python3
"""Build an executable one-sample/HPC bundle for the Chang 2026 pilot.

The first sample is chosen mechanically from the six morph-labelled samples as
the one with the smallest precomputed working-disk requirement. Generated scripts
preserve SRA and raw FASTQ so the first run can replace planning estimates with
measured storage, memory and runtime before the remaining five samples are run.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Mapping, Sequence


def clean(value: object) -> str:
    return str(value or "").strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [{key: clean(value) for key, value in row.items()} for row in csv.DictReader(handle) if any(clean(value) for value in row.values())]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024*1024), b""): digest.update(block)
    return digest.hexdigest()


def choose_pilot(panel_rows: Sequence[Mapping[str, str]], resource_rows: Sequence[Mapping[str, str]]) -> dict[str, object]:
    panel = {row["sample_id"]: row for row in panel_rows}; focal = [row for row in resource_rows if row.get("execution_group") == "takaoense6_pilot" and row.get("sample_id") in panel]
    if len(focal) != 6: raise ValueError(f"Expected six resource-linked focal samples, observed {len(focal)}")
    if {panel[row["sample_id"]].get("morph") for row in focal} != {"BP", "W"}: raise ValueError("Focal panel must contain both BP and W")
    selected = min(focal, key=lambda row: float(row["estimated_working_disk_gib"])); source = panel[selected["sample_id"]]; working = float(selected["estimated_working_disk_gib"])
    return {"sample_id": selected["sample_id"], "run": selected["run"], "morph": source["morph"], "taxon": source["taxon"], "official_library_layout": selected["library_layout"], "spots": int(selected["spots"]), "paired_read_count": int(selected["paired_read_count"]), "bases": int(selected["bases"]), "gigabases": float(selected["gigabases"]), "sra_size_gib": float(selected["sra_size_gib"]), "estimated_uncompressed_fastq_max_gib": float(selected["estimated_uncompressed_fastq_max_gib"]), "estimated_working_disk_gib": working, "minimum_free_disk_gib_for_first_run": int(math.ceil(working/25.0)*25)}


def bash_script(sample: Mapping[str, object], panel_name: str, resource_name: str, *, slurm: bool) -> str:
    sid = sample["sample_id"]; min_disk = sample["minimum_free_disk_gib_for_first_run"]
    directives = "" if not slurm else "#SBATCH --job-name=EAzami-NH-pilot\n#SBATCH --cpus-per-task=16\n#SBATCH --mem=120G\n#SBATCH --output=chang2026_NH_%j.out\n#SBATCH --error=chang2026_NH_%j.err\n"
    return f'''#!/usr/bin/env bash
{directives}set -euo pipefail
# Run from the EAzami repository root.
PANEL="${{PANEL:-{panel_name}}}"
RESOURCE_PLAN="${{RESOURCE_PLAN:-{resource_name}}}"
RESULTS_DIR="${{RESULTS_DIR:-results/chang2026_takaoense_pilot}}"
ENV_PREFIX="${{ENV_PREFIX:-.conda/eazami-chang2026-assembly}}"
RUNNER="analysis/run_chang2026_restartable_transcriptome_assembly.py"
QC="analysis/summarize_chang2026_transcriptome_qc.py"
SAMPLE_ID="{sid}"
mkdir -p "$RESULTS_DIR/provenance"
{{ date -u +"utc_started=%Y-%m-%dT%H:%M:%SZ"; hostname; git rev-parse HEAD || true; sha256sum "$PANEL" "$RESOURCE_PLAN" workflow/chang2026_gene_trees/envs/assembly.yml; }} > "$RESULTS_DIR/provenance/${{SAMPLE_ID}}.run_provenance.txt"
if command -v micromamba >/dev/null 2>&1; then
  if [[ ! -x "$ENV_PREFIX/bin/python" ]]; then micromamba create -y -p "$ENV_PREFIX" -f workflow/chang2026_gene_trees/envs/assembly.yml; fi
  RUN=(micromamba run -p "$ENV_PREFIX")
elif command -v mamba >/dev/null 2>&1; then
  if [[ ! -x "$ENV_PREFIX/bin/python" ]]; then mamba env create -y -p "$ENV_PREFIX" -f workflow/chang2026_gene_trees/envs/assembly.yml; fi
  RUN=(mamba run -p "$ENV_PREFIX")
else
  echo "micromamba or mamba is required" >&2; exit 2
fi
"${{RUN[@]}}" python "$RUNNER" --panel "$PANEL" --expected-panel-samples 6 --sample-id "$SAMPLE_ID" --outdir "$RESULTS_DIR" --jobs 1 --fasterq-threads 8 --fastp-threads 8 --trinity-threads 16 --trinity-memory-gb 96 --min-free-disk-gib {min_disk} --preflight-only
"${{RUN[@]}}" python "$RUNNER" --panel "$PANEL" --expected-panel-samples 6 --sample-id "$SAMPLE_ID" --outdir "$RESULTS_DIR" --jobs 1 --fasterq-threads 8 --fastp-threads 8 --trinity-threads 16 --trinity-memory-gb 96 --min-free-disk-gib {min_disk}
"${{RUN[@]}}" python "$QC" --panel "$PANEL" --resource-plan "$RESOURCE_PLAN" --results-dir "$RESULTS_DIR" --sample-id "$SAMPLE_ID"
{{ date -u +"utc_finished=%Y-%m-%dT%H:%M:%SZ"; du -sh "$RESULTS_DIR" || true; df -h "$RESULTS_DIR" || true; }} >> "$RESULTS_DIR/provenance/${{SAMPLE_ID}}.run_provenance.txt"
'''


def dry_run_script(panel_name: str, sample_id: str) -> str:
    return f'''#!/usr/bin/env bash
set -euo pipefail
python analysis/run_chang2026_restartable_transcriptome_assembly.py --panel "${{PANEL:-{panel_name}}}" --expected-panel-samples 6 --sample-id {sample_id} --outdir /tmp/eazami_chang2026_restartable_dry_run --jobs 1 --dry-run
cat /tmp/eazami_chang2026_restartable_dry_run/restartable_command_plan.csv
'''


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(); parser.add_argument("--pilot-panel", type=Path, required=True); parser.add_argument("--resource-plan", type=Path, required=True); parser.add_argument("--outdir", type=Path, required=True); return parser.parse_args()


def main() -> int:
    args = parse_args(); panel_rows = read_csv(args.pilot_panel); resources = read_csv(args.resource_plan)
    if len(panel_rows) != 6: raise SystemExit(f"Expected six pilot rows, observed {len(panel_rows)}")
    selected = choose_pilot(panel_rows, resources); args.outdir.mkdir(parents=True, exist_ok=True); panel_copy = args.outdir / args.pilot_panel.name; resource_copy = args.outdir / args.resource_plan.name; panel_copy.write_bytes(args.pilot_panel.read_bytes()); resource_copy.write_bytes(args.resource_plan.read_bytes())
    manifest = {"bundle_version": "chang2026_hpc_pilot_bundle_v1", "selection_rule": "minimum estimated_working_disk_gib among the six source-backed W/BP samples", "selected_sample": selected, "pilot_panel_sha256": sha256(panel_copy), "resource_plan_sha256": sha256(resource_copy), "execution_policy": {"jobs": 1, "trinity_threads": 16, "trinity_memory_gb": 96, "preserve_prefetched_sra_after_success": True, "preserve_raw_fastq_after_success": True, "run_mechanical_qc_immediately_after_assembly": True}, "claim_limit": "The selected sample is a resource/QC pilot; its assembly alone is not a test of the candidate-regain topology."}; (args.outdir / "pilot_execution_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    for name, text in (("run_first_sample_local.sh", bash_script(selected, panel_copy.name, resource_copy.name, slurm=False)), ("run_first_sample_slurm.sh", bash_script(selected, panel_copy.name, resource_copy.name, slurm=True)), ("dry_run_first_sample.sh", dry_run_script(panel_copy.name, str(selected["sample_id"])))):
        path = args.outdir / name; path.write_text(text, encoding="utf-8"); path.chmod(0o755)
    readme = f"""# Chang 2026 first-sample transcriptome pilot\n\nSelected sample: `{selected['sample_id']}` ({selected['morph']}; `{selected['run']}`).\n\nSelection is mechanical: smallest estimated working-disk requirement among the six published W/BP `takaoense` transcriptomes.\n\n- sequenced bases: {selected['gigabases']:.3f} Gb\n- deposited SRA: {selected['sra_size_gib']:.3f} GiB\n- estimated max uncompressed FASTQ: {selected['estimated_uncompressed_fastq_max_gib']:.1f} GiB\n- planning working disk: {selected['estimated_working_disk_gib']:.1f} GiB\n- preflight minimum free disk: {selected['minimum_free_disk_gib_for_first_run']} GiB\n\nThe run scripts preserve the prefetched SRA and raw FASTQ after success. Compare measured disk/RSS/runtime with this envelope before changing cleanup or concurrency. They create/use the repository assembly environment, run tool/disk preflight, execute the restartable runner, and then run mechanical QC.\n"""; (args.outdir / "README.md").write_text(readme, encoding="utf-8")
    print(f"selected_sample_id={selected['sample_id']}"); print(f"selected_run={selected['run']}"); print(f"minimum_free_disk_gib={selected['minimum_free_disk_gib_for_first_run']}"); return 0


if __name__ == "__main__": raise SystemExit(main())
