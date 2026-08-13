#!/usr/bin/env python3
"""Build a restartable Slurm/local execution bundle for the Chang 2026
six-sample static400 Read2Tree topology screen.

The bundle intentionally separates three checkpointed jobs:

1. fetch/validate/trim the six paired SRA libraries without Trinity;
2. validate an already-built static400 marker pack and run Read2Tree + IQ-TREE;
3. score the resulting tree against the frozen eight topology hypotheses.

The static400 pack is an input artifact, not rebuilt on the HPC node. This keeps
the heavy execution independent of OMA API availability and avoids transferring
the ~98-MB archived OMA group file when the validated execution pack is only a
few MiB.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

EXPECTED_HYPOTHESIS_SHA256 = "b3cf6ab230fba4e21dd06690580c49c0bfd759be2c1e30ac2fa576ff8e2b7082"


def clean(value: object) -> str:
    return str(value or "").strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [
            {key: clean(value) for key, value in row.items()}
            for row in csv.DictReader(handle)
            if any(clean(value) for value in row.values())
        ]


def validate_panel(panel: Path) -> list[dict[str, str]]:
    rows = read_csv(panel)
    if len(rows) != 6:
        raise ValueError(f"Expected six focal samples, observed {len(rows)}")
    if sorted(row.get("morph", "").upper() for row in rows) != ["BP", "BP", "BP", "W", "W", "W"]:
        raise ValueError("Panel must contain exactly 3 BP and 3 W samples")
    if any(row.get("library_layout", "").upper() != "PAIRED" for row in rows):
        raise ValueError("All six Read2Tree samples must be official paired libraries")
    if len({row.get("sample_id") for row in rows}) != 6:
        raise ValueError("sample_id values must be unique")
    if len({row.get("matched_run") for row in rows}) != 6:
        raise ValueError("SRA run values must be unique")
    return rows


def common_header(*, slurm: bool, job_name: str, cpus: int, mem_gb: int, hours: int) -> str:
    directives = ""
    if slurm:
        directives = (
            f"#SBATCH --job-name={job_name}\n"
            f"#SBATCH --cpus-per-task={cpus}\n"
            f"#SBATCH --mem={mem_gb}G\n"
            f"#SBATCH --time={hours}:00:00\n"
            f"#SBATCH --output={job_name}_%j.out\n"
            f"#SBATCH --error={job_name}_%j.err\n"
        )
    return f"#!/usr/bin/env bash\n{directives}set -euo pipefail\n"


def path_preamble() -> str:
    return '''SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -z "${REPO_ROOT:-}" ]]; then
  REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || true)"
fi
if [[ -z "$REPO_ROOT" || ! -f "$REPO_ROOT/analysis/build_chang2026_read2tree_pilot.py" ]]; then
  echo "Unable to resolve EAzami repository root. Set REPO_ROOT explicitly." >&2
  exit 2
fi
'''


def trim_script(*, slurm: bool, panel_name: str, evidence_name: str) -> str:
    header = common_header(slurm=slurm, job_name="EAzami-r2t-trim", cpus=16, mem_gb=32, hours=24)
    return header + path_preamble() + f'''PANEL="${{PANEL:-$SCRIPT_DIR/{panel_name}}}"
EVIDENCE="${{EVIDENCE:-$SCRIPT_DIR/{evidence_name}}}"
READS_ROOT="${{READS_ROOT:-$REPO_ROOT/results/chang2026_takaoense_pilot}}"
JOBS="${{JOBS:-1}}"
FASTERQ_THREADS="${{FASTERQ_THREADS:-8}}"
FASTP_THREADS="${{FASTP_THREADS:-8}}"
MIN_FREE_DISK_GIB="${{MIN_FREE_DISK_GIB:-150}}"
export PANEL EVIDENCE READS_ROOT JOBS FASTERQ_THREADS FASTP_THREADS MIN_FREE_DISK_GIB
bash "$REPO_ROOT/workflow/chang2026_read2tree/prepare_six_trimmed_reads.sh"
python - <<'PY'
import csv, os
from pathlib import Path
panel = list(csv.DictReader(Path(os.environ["PANEL"]).open()))
root = Path(os.environ["READS_ROOT"])
missing=[]
for row in panel:
    sid=row["sample_id"]
    for mate in ("R1","R2"):
        p=root/"samples"/sid/"trimmed"/f"{{sid}}.{{mate}}.trim.fastq.gz"
        if not p.is_file() or p.stat().st_size == 0:
            missing.append(str(p))
if missing:
    raise SystemExit("trim stage incomplete:\n"+"\n".join(missing))
print("trim_checkpoint=complete")
PY
'''


def read2tree_script(*, slurm: bool, panel_name: str, evidence_name: str, refs_name: str) -> str:
    header = common_header(slurm=slurm, job_name="EAzami-r2t-static", cpus=16, mem_gb=64, hours=48)
    return header + path_preamble() + f'''# Requires the lightweight validated static400 execution pack to be unpacked.
: "${{MARKER_CONTRACT:?Set MARKER_CONTRACT to marker_pack_contract.json inside the validated static400 execution pack}}"
MARKER_CONTRACT="$(cd "$(dirname "$MARKER_CONTRACT")" && pwd)/$(basename "$MARKER_CONTRACT")"
PANEL="${{PANEL:-$SCRIPT_DIR/{panel_name}}}"
EVIDENCE="${{EVIDENCE:-$SCRIPT_DIR/{evidence_name}}}"
REFS="${{REFS:-$SCRIPT_DIR/{refs_name}}}"
READS_ROOT="${{READS_ROOT:-$REPO_ROOT/results/chang2026_takaoense_pilot}}"
RESULT_ROOT="${{RESULT_ROOT:-$REPO_ROOT/results/chang2026_read2tree_static400}}"
THREADS="${{THREADS:-16}}"
CHECK_INPUTS=1
ENV_PREFIX="${{READ2TREE_ENV_PREFIX:-$REPO_ROOT/.conda/eazami-chang2026-read2tree}}"
ENV_YML="$REPO_ROOT/workflow/chang2026_read2tree/envs/read2tree.yml"
if command -v micromamba >/dev/null 2>&1; then
  if [[ ! -x "$ENV_PREFIX/bin/python" ]]; then
    micromamba create -y -p "$ENV_PREFIX" -f "$ENV_YML"
  fi
  RUN=(micromamba run -p "$ENV_PREFIX")
elif command -v mamba >/dev/null 2>&1; then
  if [[ ! -x "$ENV_PREFIX/bin/python" ]]; then
    mamba env create -y -p "$ENV_PREFIX" -f "$ENV_YML"
  fi
  RUN=(mamba run -p "$ENV_PREFIX")
else
  echo "micromamba or mamba is required for the pinned Read2Tree environment" >&2
  exit 2
fi
export MARKER_CONTRACT PANEL EVIDENCE REFS READS_ROOT RESULT_ROOT THREADS CHECK_INPUTS
"${{RUN[@]}}" bash "$REPO_ROOT/workflow/chang2026_read2tree/prepare_from_validated_marker_pack.sh"
PLAN="$RESULT_ROOT/read2tree_plan/run_read2tree_fast_screen.sh"
if [[ ! -s "$PLAN" ]]; then
  echo "Read2Tree plan missing: $PLAN" >&2
  exit 2
fi
"${{RUN[@]}}" bash "$PLAN"
TREE="$RESULT_ROOT/read2tree_output/takaoense6_read2tree_dna.treefile"
if [[ ! -s "$TREE" ]]; then
  echo "IQ-TREE output missing: $TREE" >&2
  exit 2
fi
printf 'read2tree_checkpoint=complete\ntree=%s\n' "$TREE"
'''


def scoring_script(*, slurm: bool, panel_name: str, refs_name: str) -> str:
    header = common_header(slurm=slurm, job_name="EAzami-r2t-score", cpus=2, mem_gb=8, hours=2)
    return header + path_preamble() + f'''PANEL="${{PANEL:-$SCRIPT_DIR/{panel_name}}}"
REFS="${{REFS:-$SCRIPT_DIR/{refs_name}}}"
RESULT_ROOT="${{RESULT_ROOT:-$REPO_ROOT/results/chang2026_read2tree_static400}}"
TREE="$RESULT_ROOT/read2tree_output/takaoense6_read2tree_dna.treefile"
python "$REPO_ROOT/analysis/run_chang2026_read2tree_scoring_contract.py" \
  --tree "$TREE" \
  --panel "$PANEL" \
  --reference-manifest "$REFS" \
  --frozen-hypotheses "$REPO_ROOT/analysis/chang2026_takaoense_gene_tree_hypotheses_v1.csv" \
  --expected-hypothesis-sha256 {EXPECTED_HYPOTHESIS_SHA256} \
  --nearest "$REPO_ROOT/analysis/chang2026_takaoense_nearest_no_regain_topologies.csv" \
  --robustness-summary "$REPO_ROOT/analysis/chang2026_takaoense_topology_robustness_summary.json" \
  --scorer "$REPO_ROOT/analysis/score_chang2026_read2tree_topology.py" \
  --thresholds 0,50,70,90 \
  --output "$RESULT_ROOT/read2tree_topology_scores.csv" \
  --hypothesis-output "$RESULT_ROOT/read2tree_per_hypothesis_scores.csv" \
  --summary-json "$RESULT_ROOT/read2tree_topology_summary.json"
test -s "$RESULT_ROOT/read2tree_topology_summary.json"
echo "scoring_checkpoint=complete"
'''


def submit_script() -> str:
    return '''#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${MARKER_CONTRACT:?Set MARKER_CONTRACT before submission so the static400 execution-pack location is explicit}"
MARKER_CONTRACT="$(cd "$(dirname "$MARKER_CONTRACT")" && pwd)/$(basename "$MARKER_CONTRACT")"
trim_job=$(sbatch --parsable --chdir="$SCRIPT_DIR" "$SCRIPT_DIR/run_01_trim_slurm.sh")
r2t_job=$(sbatch --parsable --chdir="$SCRIPT_DIR" --dependency=afterok:"$trim_job" --export=ALL,MARKER_CONTRACT="$MARKER_CONTRACT" "$SCRIPT_DIR/run_02_read2tree_slurm.sh")
score_job=$(sbatch --parsable --chdir="$SCRIPT_DIR" --dependency=afterok:"$r2t_job" "$SCRIPT_DIR/run_03_score_slurm.sh")
printf 'trim_job=%s\nread2tree_job=%s\nscore_job=%s\n' "$trim_job" "$r2t_job" "$score_job"
'''


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--references", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    panel_rows = validate_panel(args.panel)
    if not args.evidence.is_file() or not args.references.is_file():
        raise SystemExit("Evidence/reference inputs must exist")
    args.outdir.mkdir(parents=True, exist_ok=True)

    copies = {}
    for source in (args.panel, args.evidence, args.references):
        target = args.outdir / source.name
        target.write_bytes(source.read_bytes())
        copies[source.name] = sha256(target)

    scripts = {
        "run_01_trim_local.sh": trim_script(slurm=False, panel_name=args.panel.name, evidence_name=args.evidence.name),
        "run_01_trim_slurm.sh": trim_script(slurm=True, panel_name=args.panel.name, evidence_name=args.evidence.name),
        "run_02_read2tree_local.sh": read2tree_script(slurm=False, panel_name=args.panel.name, evidence_name=args.evidence.name, refs_name=args.references.name),
        "run_02_read2tree_slurm.sh": read2tree_script(slurm=True, panel_name=args.panel.name, evidence_name=args.evidence.name, refs_name=args.references.name),
        "run_03_score_local.sh": scoring_script(slurm=False, panel_name=args.panel.name, refs_name=args.references.name),
        "run_03_score_slurm.sh": scoring_script(slurm=True, panel_name=args.panel.name, refs_name=args.references.name),
        "submit_slurm_chain.sh": submit_script(),
    }
    for name, text in scripts.items():
        path = args.outdir / name
        path.write_text(text, encoding="utf-8")
        path.chmod(0o755)

    manifest = {
        "bundle_version": "chang2026_read2tree_static400_hpc_bundle_v1",
        "sample_count": len(panel_rows),
        "morph_counts": {
            "BP": sum(row["morph"].upper() == "BP" for row in panel_rows),
            "W": sum(row["morph"].upper() == "W" for row in panel_rows),
        },
        "input_sha256": copies,
        "stage_resources": {
            "trim": {"cpus": 16, "memory_gb": 32, "wall_hours": 24, "minimum_free_disk_gib": 150},
            "read2tree_iqtree": {"cpus": 16, "memory_gb": 64, "wall_hours": 48},
            "score": {"cpus": 2, "memory_gb": 8, "wall_hours": 2},
        },
        "required_external_input": {
            "type": "validated_static400_execution_pack",
            "environment_variable": "MARKER_CONTRACT",
            "expected_marker_count": 400,
            "expected_oma_release": "May2026",
            "note": "Use the lightweight eazami-read2tree-oma-static400-exec artifact; the archived oma-groups.txt.gz is not needed for execution.",
        },
        "environment_contracts": {
            "read_prep": "workflow/chang2026_read2tree/envs/read_prep.yml",
            "read2tree": "workflow/chang2026_read2tree/envs/read2tree.yml",
            "read2tree_source_commit": "e19ad8f32a438ff7a38d9ee1d41832e1fc326a3c",
        },
        "frozen_hypothesis_sha256": EXPECTED_HYPOTHESIS_SHA256,
        "execution_order": ["trim", "read2tree_iqtree", "score"],
        "restart_policy": (
            "Each numbered stage has an explicit output checkpoint. Re-run a failed stage without deleting prior successful SRA/FASTQ/Read2Tree outputs; downstream Slurm jobs use afterok dependencies."
        ),
        "claim_limit": (
            "This bundle executes an ancestry/topology sensitivity screen from young-leaf RNA-seq. "
            "It does not test floral anthocyanin expression or molecular reactivation."
        ),
    }
    (args.outdir / "execution_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (args.outdir / "README.md").write_text(
        "# Chang 2026 static400 Read2Tree HPC bundle\n\n"
        "Keep this directory inside an EAzami checkout (or set `REPO_ROOT`). Unpack the lightweight validated static400 "
        "execution artifact, set `MARKER_CONTRACT` to its `marker_pack_contract.json`, then run `submit_slurm_chain.sh` "
        "on Slurm or the three local scripts in numeric order.\n\n"
        "The trim stage intentionally stops before Trinity. The topology stage creates/uses the pinned Read2Tree conda "
        "environment, validates the marker pack, runs Read2Tree and IQ-TREE, and checks the tree exists. The scoring stage "
        "applies the frozen 8-hypothesis/support-collapse contract.\n\n"
        "Default planning resources: trim 16 CPU/32 GiB/24 h with >=150 GiB free disk; Read2Tree+IQ-TREE "
        "16 CPU/64 GiB/48 h; scoring 2 CPU/8 GiB/2 h. These are planning envelopes, not measured requirements.\n",
        encoding="utf-8",
    )
    print("bundle_version=chang2026_read2tree_static400_hpc_bundle_v1")
    print("sample_count=6")
    print("stages=trim|read2tree_iqtree|score")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
