#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

READS_ROOT="${READS_ROOT:-$PWD/results/chang2026_takaoense_pilot}"
PANEL="${PANEL:-$REPO_ROOT/sampling/chang2026_takaoense6_read2tree_panel_v1.csv}"
EVIDENCE="${EVIDENCE:-$REPO_ROOT/data/evidence/chang2026_takaoense_morph_linked_public_samples_v1.csv}"
ENV_PREFIX="${ENV_PREFIX:-$REPO_ROOT/.conda/eazami-chang2026-assembly}"
JOBS="${JOBS:-1}"
FASTERQ_THREADS="${FASTERQ_THREADS:-8}"
FASTP_THREADS="${FASTP_THREADS:-8}"
# Provisional read-only safety gate. Six libraries have a source-backed maximum
# uncompressed-FASTQ estimate of ~108 GiB; this adds room for deposited SRA,
# fasterq scratch and intermediate files. Replace with measured peak use after
# the first real execution rather than lowering it silently.
MIN_FREE_DISK_GIB="${MIN_FREE_DISK_GIB:-150}"

if command -v micromamba >/dev/null 2>&1; then
  if [[ ! -x "$ENV_PREFIX/bin/python" ]]; then
    micromamba create -y -p "$ENV_PREFIX" -f "$REPO_ROOT/workflow/chang2026_gene_trees/envs/assembly.yml"
  fi
  RUN=(micromamba run -p "$ENV_PREFIX")
elif command -v mamba >/dev/null 2>&1; then
  if [[ ! -x "$ENV_PREFIX/bin/python" ]]; then
    mamba env create -y -p "$ENV_PREFIX" -f "$REPO_ROOT/workflow/chang2026_gene_trees/envs/assembly.yml"
  fi
  RUN=(mamba run -p "$ENV_PREFIX")
else
  echo "micromamba or mamba is required" >&2
  exit 2
fi

mkdir -p "$READS_ROOT/provenance"
{
  date -u +"utc_started=%Y-%m-%dT%H:%M:%SZ"
  hostname
  git -C "$REPO_ROOT" rev-parse HEAD || true
  sha256sum "$PANEL" "$EVIDENCE" "$REPO_ROOT/workflow/chang2026_gene_trees/envs/assembly.yml"
} > "$READS_ROOT/provenance/read2tree_trimmed_reads.run_provenance.txt"

"${RUN[@]}" python "$REPO_ROOT/analysis/prepare_chang2026_read2tree_reads.py" \
  --panel "$PANEL" \
  --evidence "$EVIDENCE" \
  --outdir "$READS_ROOT" \
  --jobs "$JOBS" \
  --fasterq-threads "$FASTERQ_THREADS" \
  --fastp-threads "$FASTP_THREADS" \
  --min-free-disk-gib "$MIN_FREE_DISK_GIB" \
  --preflight-only

"${RUN[@]}" python "$REPO_ROOT/analysis/prepare_chang2026_read2tree_reads.py" \
  --panel "$PANEL" \
  --evidence "$EVIDENCE" \
  --outdir "$READS_ROOT" \
  --jobs "$JOBS" \
  --fasterq-threads "$FASTERQ_THREADS" \
  --fastp-threads "$FASTP_THREADS" \
  --min-free-disk-gib "$MIN_FREE_DISK_GIB"

{
  date -u +"utc_finished=%Y-%m-%dT%H:%M:%SZ"
  du -sh "$READS_ROOT" || true
  df -h "$READS_ROOT" || true
} >> "$READS_ROOT/provenance/read2tree_trimmed_reads.run_provenance.txt"

cat <<EOF
Six-sample trimmed-read stage completed without Trinity.

Reads root:
  $READS_ROOT

Read2Tree expects:
  $READS_ROOT/samples/<sample_id>/trimmed/<sample_id>.R1.trim.fastq.gz
  $READS_ROOT/samples/<sample_id>/trimmed/<sample_id>.R2.trim.fastq.gz

Next static400 preparation:
  READS_ROOT="$READS_ROOT" bash "$REPO_ROOT/workflow/chang2026_read2tree/prepare_static_profile.sh"
EOF
