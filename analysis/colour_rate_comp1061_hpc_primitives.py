#!/usr/bin/env python3
"""Pure helpers for the canonical 20-tip colour-rate Compositae1061 HPC bundle.

This module has no CLI or supported entry point. It validates the frozen bridge
and locus contracts and generates reusable read-recovery/HybPiper/QC shell
stages. The canonical builder owns stage-0 input preparation, argument parsing,
manifest emission and the supported public interface.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

BRIDGE_VERSION = "colour_rate_comp1061_bridge_artifact_contract_v1"
LOCUS_VERSION = "moreyra_public_locus_sets_v1"
REF_SHA = "77d510ef101d08a7a23a4df391d077d3b7f75482c66f7f4bea6d32cf290ced2c"
ASTRAL_COMMIT = "068a4b2497f61c866c4727bfbfd78b4361ba27c8"
ASTRAL_ZIP_BLOB_SHA1 = "3150e813e223dbc47dbf3d64829be048ef059e5d"


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(bridge: dict[str, object], locus: dict[str, object]) -> list[dict[str, object]]:
    if bridge.get("contract_version") != BRIDGE_VERSION:
        raise ValueError("bridge contract version drift")
    counts = bridge.get("primary_counts", {})
    if not isinstance(counts, dict):
        raise ValueError("bridge primary counts missing")
    if counts.get("taxon_count") != 20 or counts.get("state_counts") != {"C": 17, "W": 3}:
        raise ValueError("bridge counts drift")
    if counts.get("data_type_counts") != {"leaf_rnaseq": 13, "target_capture": 7}:
        raise ValueError("bridge data-type counts drift")
    tips = bridge.get("primary_tips", [])
    if not isinstance(tips, list):
        raise ValueError("bridge primary tips missing")
    if len(tips) != 20 or len({x["tip_id"] for x in tips}) != 20 or len({x["run"] for x in tips}) != 20:
        raise ValueError("bridge tips/runs not unique")
    if any(x.get("library_layout") != "PAIRED" for x in tips):
        raise ValueError("all primary runs must remain paired")
    if bridge.get("comp1061_reference_sha256") != REF_SHA:
        raise ValueError("reference hash drift")
    if locus.get("contract_version") != LOCUS_VERSION:
        raise ValueError("locus manifest version drift")
    locus_sets = locus.get("locus_sets", {})
    if not isinstance(locus_sets, dict):
        raise ValueError("locus sets missing")
    expected = {
        "public_1061": 1061,
        "reproducible_531": 531,
        "conservative_241": 241,
        "manual_review_290": 290,
    }
    for name, n in expected.items():
        entry = locus_sets.get(name, {})
        if not isinstance(entry, dict) or entry.get("count") != n:
            raise ValueError(f"{name} count drift")
    return tips


def write(path: Path, text: str, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    path.chmod(mode)


def runs_csv(path: Path, tips: list[dict[str, object]]) -> None:
    fields = [
        "index",
        "tip_id",
        "accepted_taxon",
        "binary_colour_code",
        "source_study",
        "source_bioproject",
        "data_type",
        "run",
        "biosample",
        "voucher",
        "spots",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for i, row in enumerate(tips):
            writer.writerow({key: (i if key == "index" else row.get(key, "")) for key in fields})


def env_yml() -> str:
    return """name: eazami-colour-rate-comp1061
channels:
  - conda-forge
  - bioconda
dependencies:
  - python=3.11
  - hybpiper=2.3.4
  - sra-tools
  - fastp
  - pigz
  - bwa
  - samtools
  - blast
  - spades
  - exonerate
  - mafft
  - iqtree
  - biopython
  - openjdk=17
"""


def common() -> str:
    return """set -euo pipefail
BUNDLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${REPO_ROOT:-$(cd "$BUNDLE_DIR/../.." && pwd)}"
RESULT_ROOT="${RESULT_ROOT:-$PWD/results/colour_rate_comp1061}"
ENV_PREFIX="${ENV_PREFIX:-$REPO_ROOT/.conda/eazami-colour-rate-comp1061}"
export REPO_ROOT RESULT_ROOT ENV_PREFIX
if command -v micromamba >/dev/null 2>&1; then
  if [[ ! -x "$ENV_PREFIX/bin/python" ]]; then micromamba create -y -p "$ENV_PREFIX" -f "$BUNDLE_DIR/env.yml"; fi
  RUN=(micromamba run -p "$ENV_PREFIX")
elif command -v mamba >/dev/null 2>&1; then
  if [[ ! -x "$ENV_PREFIX/bin/python" ]]; then mamba env create -y -p "$ENV_PREFIX" -f "$BUNDLE_DIR/env.yml"; fi
  RUN=(mamba run -p "$ENV_PREFIX")
else
  echo "micromamba or mamba required" >&2; exit 2
fi
mkdir -p "$RESULT_ROOT"
"""


def fetch_script() -> str:
    return """#!/usr/bin/env bash
#SBATCH --job-name=EAzami-cr-fetch
#SBATCH --array=0-19
#SBATCH --cpus-per-task=8
#SBATCH --mem=24G
#SBATCH --time=24:00:00
#SBATCH --output=cr_fetch_%A_%a.out
#SBATCH --error=cr_fetch_%A_%a.err
""" + common() + """
IDX="${SLURM_ARRAY_TASK_ID:?}"
ROW=$(awk -F, -v n=$((IDX+2)) 'NR==n{print}' "$BUNDLE_DIR/primary_runs.csv")
TIP=$(printf '%s' "$ROW" | cut -d, -f2); RUNACC=$(printf '%s' "$ROW" | cut -d, -f8)
OUT="$RESULT_ROOT/reads/$TIP"; mkdir -p "$OUT/raw" "$OUT/trimmed" "$OUT/scratch"
if [[ -s "$OUT/trimmed/$TIP.R1.trim.fastq.gz" && -s "$OUT/trimmed/$TIP.R2.trim.fastq.gz" ]]; then echo already_complete; exit 0; fi
"${RUN[@]}" prefetch "$RUNACC" --output-directory "$OUT/sra"
SRA=$(find "$OUT/sra" -name "$RUNACC.sra" -print -quit); test -s "$SRA"
"${RUN[@]}" vdb-validate "$SRA"
"${RUN[@]}" fasterq-dump "$SRA" --split-files --threads 8 --temp "$OUT/scratch" --outdir "$OUT/raw"
"${RUN[@]}" pigz -p 8 "$OUT/raw/${RUNACC}_1.fastq" "$OUT/raw/${RUNACC}_2.fastq"
"${RUN[@]}" fastp -i "$OUT/raw/${RUNACC}_1.fastq.gz" -I "$OUT/raw/${RUNACC}_2.fastq.gz" \
  -o "$OUT/trimmed/$TIP.R1.trim.fastq.gz" -O "$OUT/trimmed/$TIP.R2.trim.fastq.gz" \
  --thread 8 --json "$OUT/trimmed/$TIP.fastp.json" --html "$OUT/trimmed/$TIP.fastp.html"
test -s "$OUT/trimmed/$TIP.R1.trim.fastq.gz"; test -s "$OUT/trimmed/$TIP.R2.trim.fastq.gz"
touch "$OUT/trimmed/.complete"
"""


def hybpiper_script(mode: str) -> str:
    if mode not in {"bwa", "blastx"}:
        raise ValueError(f"unsupported mapping mode: {mode}")
    bwa = " --bwa" if mode == "bwa" else ""
    return f"""#!/usr/bin/env bash
#SBATCH --job-name=EAzami-cr-{mode}
#SBATCH --array=0-19
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=48:00:00
#SBATCH --output=cr_{mode}_%A_%a.out
#SBATCH --error=cr_{mode}_%A_%a.err
""" + common() + f"""
IDX="${{SLURM_ARRAY_TASK_ID:?}}"
ROW=$(awk -F, -v n=$((IDX+2)) 'NR==n{{print}}' "$BUNDLE_DIR/primary_runs.csv")
TIP=$(printf '%s' "$ROW" | cut -d, -f2)
R1="$RESULT_ROOT/reads/$TIP/trimmed/$TIP.R1.trim.fastq.gz"; R2="$RESULT_ROOT/reads/$TIP/trimmed/$TIP.R2.trim.fastq.gz"
TARGET="$RESULT_ROOT/inputs/reference/comp1061_hybpiper_reference.fasta"; OUT="$RESULT_ROOT/hybpiper_{mode}"
test -s "$R1"; test -s "$R2"; test -s "$TARGET"; mkdir -p "$OUT"
if [[ -s "$OUT/$TIP.tar.gz" ]]; then echo already_complete; exit 0; fi
cd "$OUT"
"${{RUN[@]}}" hybpiper assemble -t_dna "$TARGET" -r "$R1" "$R2" --prefix "$TIP" --cpu 16{bwa} --no_intronerate --compress_sample_folder
cd - >/dev/null
test -s "$OUT/$TIP.tar.gz"
"""


def qc_script() -> str:
    return """#!/usr/bin/env bash
#SBATCH --job-name=EAzami-cr-qc
#SBATCH --cpus-per-task=16
#SBATCH --mem=48G
#SBATCH --time=12:00:00
""" + common() + """
MODE="${MODE:?set MODE=bwa or blastx}"; [[ "$MODE" == bwa || "$MODE" == blastx ]]
HYB="$RESULT_ROOT/hybpiper_$MODE"; TARGET="$RESULT_ROOT/inputs/reference/comp1061_hybpiper_reference.fasta"; QC="$RESULT_ROOT/qc_$MODE"; mkdir -p "$QC"
cut -d, -f2 "$BUNDLE_DIR/primary_runs.csv" | tail -n +2 > "$QC/sample_names.txt"
cd "$QC"
"${RUN[@]}" hybpiper stats -t_dna "$TARGET" gene "$QC/sample_names.txt" --hybpiper_dir "$HYB" --cpu 16 --no_heatmap --seq_lengths_filename seq_lengths --stats_filename hybpiper_stats
"${RUN[@]}" hybpiper retrieve_sequences dna -t_dna "$TARGET" --sample_names "$QC/sample_names.txt" --hybpiper_dir "$HYB" --fasta_dir "$QC/retrieved_dna" --cpu 16
"${RUN[@]}" hybpiper paralog_retriever "$QC/sample_names.txt" -t_dna "$TARGET" --hybpiper_dir "$HYB" --fasta_dir_all "$QC/paralogs_all" --paralog_report_filename "$QC/paralog_report" --paralogs_above_threshold_report_filename "$QC/paralog_loci_any" --paralogs_list_threshold_percentage 0 --no_heatmap --cpu 16
cd - >/dev/null
test -s "$QC/hybpiper_stats.tsv"; test -d "$QC/retrieved_dna"
echo qc_checkpoint=complete mode=$MODE
"""


def submit_script(mode: str) -> str:
    if mode not in {"bwa", "blastx"}:
        raise ValueError(f"unsupported mapping mode: {mode}")
    hyb = "02_hybpiper_bwa_slurm.sh" if mode == "bwa" else "02b_hybpiper_blastx_slurm.sh"
    return f"""#!/usr/bin/env bash
set -euo pipefail
prep=$(sbatch --parsable 00_prepare_inputs_slurm.sh)
fetch=$(sbatch --parsable --dependency=afterok:$prep 01_fetch_trim_slurm.sh)
hyb=$(sbatch --parsable --dependency=afterok:$fetch {hyb})
qc=$(sbatch --parsable --dependency=afterok:$hyb --export=ALL,MODE={mode} 03_retrieve_qc_slurm.sh)
printf 'prepare=%s\nfetch=%s\nhybpiper=%s\nqc=%s\n' "$prep" "$fetch" "$hyb" "$qc"
"""
