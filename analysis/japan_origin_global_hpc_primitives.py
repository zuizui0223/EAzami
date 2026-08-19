#!/usr/bin/env python3
"""Shared Slurm-script primitives for Japan-origin public nuclear-tree bundles.

This module contains only reusable shell-generation logic. Inventory sizes,
result namespaces and generated helper paths are supplied by the active bundle
builder so a historical sample count cannot silently leak into a current run.
"""
from __future__ import annotations

REF_SHA = "77d510ef101d08a7a23a4df391d077d3b7f75482c66f7f4bea6d32cf290ced2c"


def env_yml() -> str:
    return """name: eazami-japan-origin-global
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
"""


def common(result_namespace: str) -> str:
    return f'''set -euo pipefail
BUNDLE_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
REPO_ROOT="${{REPO_ROOT:-$(cd "$BUNDLE_DIR/../.." && pwd)}}"
RESULT_ROOT="${{RESULT_ROOT:-$PWD/results/{result_namespace}}}"
ENV_PREFIX="${{ENV_PREFIX:-$REPO_ROOT/.conda/eazami-japan-origin-global}}"
export BUNDLE_DIR REPO_ROOT RESULT_ROOT ENV_PREFIX
if command -v micromamba >/dev/null 2>&1; then
  if [[ ! -x "$ENV_PREFIX/bin/python" ]]; then micromamba create -y -p "$ENV_PREFIX" -f "$BUNDLE_DIR/env.yml"; fi
  RUN=(micromamba run -p "$ENV_PREFIX")
elif command -v mamba >/dev/null 2>&1; then
  if [[ ! -x "$ENV_PREFIX/bin/python" ]]; then mamba env create -y -p "$ENV_PREFIX" -f "$BUNDLE_DIR/env.yml"; fi
  RUN=(mamba run -p "$ENV_PREFIX")
else echo "micromamba or mamba required" >&2; exit 2; fi
mkdir -p "$RESULT_ROOT"
'''


def row_shell() -> str:
    return '''eval "$(python - "$BUNDLE_DIR/sample_manifest.tsv" "$IDX" <<'PY'
import csv,shlex,sys
p,idx=sys.argv[1],int(sys.argv[2])
with open(p,encoding='utf-8',newline='') as h:rows=list(csv.DictReader(h,delimiter='\t'))
r=rows[idx]
for k in ('tip_id','run_accessions','run_count','source_study','assay'):
 print(f'{k.upper()}={shlex.quote(r[k])}')
PY
)"
'''


def prep(result_namespace: str) -> str:
    return '#!/usr/bin/env bash\n' + common(result_namespace) + '''mkdir -p "$RESULT_ROOT/inputs/reference" "$RESULT_ROOT/inputs/locus_sets"
"${RUN[@]}" python "$REPO_ROOT/analysis/recover_comp1061_original_hybpiper_reference.py" --outdir "$RESULT_ROOT/inputs/reference"
python - <<'PY'
import json,os,pathlib
root=pathlib.Path(os.environ['RESULT_ROOT']);c=json.loads((root/'inputs/reference/comp1061_original_reference_contract.json').read_text())
assert c['sha256']==''' + repr(REF_SHA) + ''' and c['locus_count']==1061
PY
"${RUN[@]}" python "$REPO_ROOT/analysis/recover_moreyra_author_repository.py" --outdir "$RESULT_ROOT/inputs/moreyra_author_repo" --force
"${RUN[@]}" python "$REPO_ROOT/analysis/summarize_moreyra_locus_filter.py" --audit-dir "$RESULT_ROOT/inputs/moreyra_author_repo"
"${RUN[@]}" python "$REPO_ROOT/analysis/export_moreyra_locus_manifests.py" --input "$RESULT_ROOT/inputs/moreyra_author_repo/paralog_locus_filter_reconstruction.csv" --outdir "$RESULT_ROOT/inputs/locus_sets"
for x in moreyra_public_1061_loci.txt moreyra_reproducible_531_candidate_loci.txt moreyra_conservative_241_no_warning_loci.txt; do test -s "$RESULT_ROOT/inputs/locus_sets/$x"; done
echo global_inputs_checkpoint=complete
'''


def fetch(result_namespace: str, sample_last_index: int, max_parallel: int = 20) -> str:
    return f'''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-jog-fetch
#SBATCH --array=0-{sample_last_index}%{max_parallel}
#SBATCH --cpus-per-task=8
#SBATCH --mem=24G
#SBATCH --time=24:00:00
#SBATCH --output=jog_fetch_%A_%a.out
#SBATCH --error=jog_fetch_%A_%a.err
''' + common(result_namespace) + '''IDX="${SLURM_ARRAY_TASK_ID:?}"
''' + row_shell() + '''OUT="$RESULT_ROOT/reads/$TIP_ID"; mkdir -p "$OUT/sra" "$OUT/raw" "$OUT/combined" "$OUT/trimmed" "$OUT/scratch"
if [[ -s "$OUT/trimmed/$TIP_ID.R1.trim.fastq.gz" && -s "$OUT/trimmed/$TIP_ID.R2.trim.fastq.gz" ]]; then echo already_complete; exit 0; fi
IFS='|' read -r -a ACCS <<< "$RUN_ACCESSIONS"
if [[ "${#ACCS[@]}" -ne "$RUN_COUNT" ]]; then echo "run-count mismatch $TIP_ID" >&2; exit 3; fi
R1S=(); R2S=()
for ACC in "${ACCS[@]}"; do
  "${RUN[@]}" prefetch "$ACC" --output-directory "$OUT/sra"
  SRA=$(find "$OUT/sra" -name "$ACC.sra" -print -quit); test -s "$SRA"
  "${RUN[@]}" vdb-validate "$SRA"
  if [[ ! -s "$OUT/raw/${ACC}_1.fastq.gz" || ! -s "$OUT/raw/${ACC}_2.fastq.gz" ]]; then
    "${RUN[@]}" fasterq-dump "$SRA" --split-files --threads 8 --temp "$OUT/scratch" --outdir "$OUT/raw"
    test -s "$OUT/raw/${ACC}_1.fastq"; test -s "$OUT/raw/${ACC}_2.fastq"
    "${RUN[@]}" pigz -p 8 "$OUT/raw/${ACC}_1.fastq" "$OUT/raw/${ACC}_2.fastq"
  fi
  R1S+=("$OUT/raw/${ACC}_1.fastq.gz"); R2S+=("$OUT/raw/${ACC}_2.fastq.gz")
done
cat "${R1S[@]}" > "$OUT/combined/$TIP_ID.R1.fastq.gz"; cat "${R2S[@]}" > "$OUT/combined/$TIP_ID.R2.fastq.gz"
test -s "$OUT/combined/$TIP_ID.R1.fastq.gz"; test -s "$OUT/combined/$TIP_ID.R2.fastq.gz"
"${RUN[@]}" fastp -i "$OUT/combined/$TIP_ID.R1.fastq.gz" -I "$OUT/combined/$TIP_ID.R2.fastq.gz" -o "$OUT/trimmed/$TIP_ID.R1.trim.fastq.gz" -O "$OUT/trimmed/$TIP_ID.R2.trim.fastq.gz" --thread 8 --json "$OUT/trimmed/$TIP_ID.fastp.json" --html "$OUT/trimmed/$TIP_ID.fastp.html"
test -s "$OUT/trimmed/$TIP_ID.R1.trim.fastq.gz"; test -s "$OUT/trimmed/$TIP_ID.R2.trim.fastq.gz"; touch "$OUT/trimmed/.complete"
'''


def hyb(mode: str, result_namespace: str, sample_last_index: int, max_parallel: int = 16) -> str:
    if mode not in {"bwa", "blastx"}:
        raise ValueError(f"unsupported mapping mode: {mode}")
    bwa = ' --bwa' if mode == 'bwa' else ''
    return f'''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-jog-{mode}
#SBATCH --array=0-{sample_last_index}%{max_parallel}
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=48:00:00
#SBATCH --output=jog_{mode}_%A_%a.out
#SBATCH --error=jog_{mode}_%A_%a.err
''' + common(result_namespace) + '''IDX="${SLURM_ARRAY_TASK_ID:?}"
''' + row_shell() + f'''R1="$RESULT_ROOT/reads/$TIP_ID/trimmed/$TIP_ID.R1.trim.fastq.gz"; R2="$RESULT_ROOT/reads/$TIP_ID/trimmed/$TIP_ID.R2.trim.fastq.gz"; TARGET="$RESULT_ROOT/inputs/reference/comp1061_hybpiper_reference.fasta"; OUT="$RESULT_ROOT/hybpiper_{mode}"
test -s "$R1"; test -s "$R2"; test -s "$TARGET"; mkdir -p "$OUT"; [[ -s "$OUT/$TIP_ID.tar.gz" ]] && exit 0
cd "$OUT"; "${{RUN[@]}}" hybpiper assemble -t_dna "$TARGET" -r "$R1" "$R2" --prefix "$TIP_ID" --cpu 16{bwa} --no_intronerate --compress_sample_folder; cd - >/dev/null; test -s "$OUT/$TIP_ID.tar.gz"
'''


def qc(result_namespace: str) -> str:
    return '''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-jog-qc
#SBATCH --cpus-per-task=32
#SBATCH --mem=96G
#SBATCH --time=24:00:00
''' + common(result_namespace) + '''MODE="${MODE:-bwa}"; [[ "$MODE" == bwa || "$MODE" == blastx ]]; HYB="$RESULT_ROOT/hybpiper_$MODE"; TARGET="$RESULT_ROOT/inputs/reference/comp1061_hybpiper_reference.fasta"; QC="$RESULT_ROOT/qc_$MODE"; mkdir -p "$QC"
cut -f2 "$BUNDLE_DIR/sample_manifest.tsv" | tail -n +2 > "$QC/sample_names.txt"
cd "$QC"
"${RUN[@]}" hybpiper stats -t_dna "$TARGET" gene "$QC/sample_names.txt" --hybpiper_dir "$HYB" --cpu 32 --no_heatmap --seq_lengths_filename seq_lengths --stats_filename hybpiper_stats
"${RUN[@]}" hybpiper retrieve_sequences dna -t_dna "$TARGET" --sample_names "$QC/sample_names.txt" --hybpiper_dir "$HYB" --fasta_dir "$QC/retrieved_dna" --cpu 32
"${RUN[@]}" hybpiper paralog_retriever "$QC/sample_names.txt" -t_dna "$TARGET" --hybpiper_dir "$HYB" --fasta_dir_all "$QC/paralogs_all" --paralog_report_filename "$QC/paralog_report" --paralogs_above_threshold_report_filename "$QC/paralog_loci_any" --paralogs_list_threshold_percentage 0 --no_heatmap --cpu 32
cd - >/dev/null; test -s "$QC/hybpiper_stats.tsv"; test -d "$QC/retrieved_dna"; test -s "$QC/paralog_report"
'''


def treeprep(result_namespace: str, summarize_helper: str, prepare_helper: str) -> str:
    return '''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-jog-treeprep
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=08:00:00
''' + common(result_namespace) + f'''MODE="${{MODE:-bwa}}"; QC="$RESULT_ROOT/qc_$MODE"; TREE="$RESULT_ROOT/tree_$MODE"; mkdir -p "$TREE/current_qc" "$TREE/inputs"
"${{RUN[@]}}" python "{summarize_helper}" --manifest "$BUNDLE_DIR/sample_manifest.csv" --retrieved-dir "$QC/retrieved_dna" --paralog-report "$QC/paralog_report" --locus-dir "$RESULT_ROOT/inputs/locus_sets" --outdir "$TREE/current_qc"
CURRENT="$TREE/current_qc/current_strict_conservative_241_loci.txt"; test -s "$CURRENT"
"${{RUN[@]}}" python "{prepare_helper}" --manifest "$BUNDLE_DIR/sample_manifest.csv" --locus-list "$CURRENT" --retrieved-dir "$QC/retrieved_dna" --target "$RESULT_ROOT/inputs/reference/comp1061_hybpiper_reference.fasta" --outdir "$TREE/inputs"
'''


def align(result_namespace: str, locus_last_index: int = 240, max_parallel: int = 24) -> str:
    return f'''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-jog-align
#SBATCH --array=0-{locus_last_index}%{max_parallel}
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=04:00:00
''' + common(result_namespace) + '''MODE="${MODE:-bwa}"; TREE="$RESULT_ROOT/tree_$MODE"; IDX="${SLURM_ARRAY_TASK_ID:?}"; LOCUS=$(sed -n "$((IDX+1))p" "$TREE/inputs/eligible_loci.txt" || true); [[ -n "$LOCUS" ]] || exit 0; IN="$TREE/inputs/loci_unaligned/$LOCUS.fasta"; OUT="$TREE/alignments/$LOCUS.aln.fasta"; mkdir -p "$TREE/alignments"; [[ -s "$OUT" ]] && exit 0; test -s "$IN"; "${RUN[@]}" mafft --auto --thread 4 "$IN" > "$OUT"; test -s "$OUT"
'''


def gene(result_namespace: str, locus_last_index: int = 240, max_parallel: int = 20) -> str:
    return f'''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-jog-genetree
#SBATCH --array=0-{locus_last_index}%{max_parallel}
#SBATCH --cpus-per-task=4
#SBATCH --mem=12G
#SBATCH --time=08:00:00
''' + common(result_namespace) + '''MODE="${MODE:-bwa}"; TREE="$RESULT_ROOT/tree_$MODE"; IDX="${SLURM_ARRAY_TASK_ID:?}"; LOCUS=$(sed -n "$((IDX+1))p" "$TREE/inputs/eligible_loci.txt" || true); [[ -n "$LOCUS" ]] || exit 0; ALN="$TREE/alignments/$LOCUS.aln.fasta"; PREFIX="$TREE/gene_trees/$LOCUS"; mkdir -p "$TREE/gene_trees"; [[ -s "$PREFIX.treefile" ]] && exit 0; test -s "$ALN"; "${RUN[@]}" iqtree2 -s "$ALN" -m MFP -B 1000 --alrt 1000 -T 4 -o OUTGROUP_lett,OUTGROUP_sunf --prefix "$PREFIX"; test -s "$PREFIX.treefile"
'''


def concat(result_namespace: str) -> str:
    return '''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-jog-concat
#SBATCH --cpus-per-task=32
#SBATCH --mem=128G
#SBATCH --time=48:00:00
''' + common(result_namespace) + '''MODE="${MODE:-bwa}"; TREE="$RESULT_ROOT/tree_$MODE"; mkdir -p "$TREE/concat"
"${RUN[@]}" python "$REPO_ROOT/analysis/concatenate_colour_rate_comp1061_alignments.py" --eligible-loci "$TREE/inputs/eligible_loci.txt" --alignment-dir "$TREE/alignments" --primary-runs "$BUNDLE_DIR/sample_manifest.csv" --output "$TREE/concat/concat.fasta" --partitions "$TREE/concat/partitions.csv" --summary "$TREE/concat/concat_summary.json"
"${RUN[@]}" iqtree2 -s "$TREE/concat/concat.fasta" -m MFP -B 1000 --alrt 1000 -T AUTO -o OUTGROUP_lett,OUTGROUP_sunf --prefix "$TREE/concat/japan_origin_global_concat"; test -s "$TREE/concat/japan_origin_global_concat.treefile"
'''


def submit_data(mode: str) -> str:
    if mode not in {"bwa", "blastx"}:
        raise ValueError(f"unsupported mapping mode: {mode}")
    hyb_script = '02_hybpiper_bwa_slurm.sh' if mode == 'bwa' else '02b_hybpiper_blastx_slurm.sh'
    return f'''#!/usr/bin/env bash
set -euo pipefail
prep=$(sbatch --parsable 00_prepare_inputs_slurm.sh); fetch=$(sbatch --parsable --dependency=afterok:$prep 01_fetch_trim_slurm.sh); hyb=$(sbatch --parsable --dependency=afterok:$fetch {hyb_script}); qc=$(sbatch --parsable --dependency=afterok:$hyb --export=ALL,MODE={mode} 03_retrieve_qc_slurm.sh); printf 'prepare=%s\nfetch=%s\nhybpiper=%s\nqc=%s\n' "$prep" "$fetch" "$hyb" "$qc"
'''
