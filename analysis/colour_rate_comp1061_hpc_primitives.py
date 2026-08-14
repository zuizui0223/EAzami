#!/usr/bin/env python3
"""Build a restartable HPC bundle for the 20-tip colour-rate Compositae1061 tree.

The bundle freezes the successful official-SRA bridge selection and emits two
parallel mapping modes:

* BWA primary, matching the original Compositae1061 analysis style;
* HybPiper default BLASTx as a mapping sensitivity.

GitHub CI only validates the generated contract/scripts. SRA download,
HybPiper, MAFFT, IQ-TREE and ASTRAL are external/HPC execution steps.
"""
from __future__ import annotations

import argparse, csv, hashlib, json, textwrap
from pathlib import Path

BRIDGE_VERSION="colour_rate_comp1061_bridge_artifact_contract_v1"
LOCUS_VERSION="moreyra_public_locus_sets_v1"
REF_SHA="77d510ef101d08a7a23a4df391d077d3b7f75482c66f7f4bea6d32cf290ced2c"
ASTRAL_COMMIT="068a4b2497f61c866c4727bfbfd78b4361ba27c8"
ASTRAL_ZIP_BLOB_SHA1="3150e813e223dbc47dbf3d64829be048ef059e5d"


def load(path:Path): return json.loads(path.read_text(encoding="utf-8"))
def sha256(path:Path): return hashlib.sha256(path.read_bytes()).hexdigest()

def validate(bridge,locus):
    if bridge.get("contract_version")!=BRIDGE_VERSION: raise ValueError("bridge contract version drift")
    counts=bridge.get("primary_counts",{})
    if counts.get("taxon_count")!=20 or counts.get("state_counts")!={"C":17,"W":3}: raise ValueError("bridge counts drift")
    if counts.get("data_type_counts")!={"leaf_rnaseq":13,"target_capture":7}: raise ValueError("bridge data-type counts drift")
    tips=bridge.get("primary_tips",[])
    if len(tips)!=20 or len({x["tip_id"] for x in tips})!=20 or len({x["run"] for x in tips})!=20: raise ValueError("bridge tips/runs not unique")
    if any(x.get("library_layout")!="PAIRED" for x in tips): raise ValueError("all primary runs must remain paired")
    if bridge.get("comp1061_reference_sha256")!=REF_SHA: raise ValueError("reference hash drift")
    if locus.get("contract_version")!=LOCUS_VERSION: raise ValueError("locus manifest version drift")
    expected={"public_1061":1061,"reproducible_531":531,"conservative_241":241,"manual_review_290":290}
    for name,n in expected.items():
        if locus.get("locus_sets",{}).get(name,{}).get("count")!=n: raise ValueError(f"{name} count drift")
    return tips

def write(path,text,mode=0o644):
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(text,encoding="utf-8"); path.chmod(mode)

def runs_csv(path,tips):
    fields=["index","tip_id","accepted_taxon","binary_colour_code","source_study","source_bioproject","data_type","run","biosample","voucher","spots"]
    with path.open("w",encoding="utf-8",newline="") as h:
        w=csv.DictWriter(h,fieldnames=fields); w.writeheader()
        for i,x in enumerate(tips): w.writerow({k:(i if k=="index" else x.get(k,"")) for k in fields})

def env_yml():
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

def common():
    return """set -euo pipefail
BUNDLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${REPO_ROOT:-$(cd "$BUNDLE_DIR/../.." && pwd)}"
RESULT_ROOT="${RESULT_ROOT:-$PWD/results/colour_rate_comp1061}"
ENV_PREFIX="${ENV_PREFIX:-$REPO_ROOT/.conda/eazami-colour-rate-comp1061}"
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

def prepare_script():
    return "#!/usr/bin/env bash\n"+common()+"""
mkdir -p "$RESULT_ROOT/inputs/reference" "$RESULT_ROOT/inputs/locus_sets"
"${RUN[@]}" python "$REPO_ROOT/analysis/recover_comp1061_original_hybpiper_reference.py" --outdir "$RESULT_ROOT/inputs/reference"
python - <<'PY'
import hashlib,json,os,pathlib
root=pathlib.Path(os.environ.get('RESULT_ROOT','results/colour_rate_comp1061'))
c=json.loads((root/'inputs/reference/comp1061_original_reference_contract.json').read_text())
assert c['sha256']=='"""+REF_SHA+"""' and c['locus_count']==1061
PY
# Recreate the 1061/531/241 named sets from the pinned public Moreyra stats/paralog source.
"${RUN[@]}" python "$REPO_ROOT/analysis/recover_moreyra_author_repository.py" --outdir "$RESULT_ROOT/inputs/moreyra_author_repo"
"${RUN[@]}" python "$REPO_ROOT/analysis/export_moreyra_locus_manifests.py" \
  --locus-filter "$RESULT_ROOT/inputs/moreyra_author_repo/paralog_locus_filter_reconstruction.csv" \
  --outdir "$RESULT_ROOT/inputs/locus_sets"
cp "$BUNDLE_DIR/bridge_contract.json" "$RESULT_ROOT/inputs/"
cp "$BUNDLE_DIR/locus_set_manifest.json" "$RESULT_ROOT/inputs/"
echo inputs_checkpoint=complete
"""

def fetch_script():
    return """#!/usr/bin/env bash
#SBATCH --job-name=EAzami-cr-fetch
#SBATCH --array=0-19
#SBATCH --cpus-per-task=8
#SBATCH --mem=24G
#SBATCH --time=24:00:00
#SBATCH --output=cr_fetch_%A_%a.out
#SBATCH --error=cr_fetch_%A_%a.err
"""+common()+"""
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

def hybpiper_script(mode):
    bwa=" --bwa" if mode=="bwa" else ""
    return f"""#!/usr/bin/env bash
#SBATCH --job-name=EAzami-cr-{mode}
#SBATCH --array=0-19
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=48:00:00
#SBATCH --output=cr_{mode}_%A_%a.out
#SBATCH --error=cr_{mode}_%A_%a.err
"""+common()+f"""
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

def qc_script():
    return """#!/usr/bin/env bash
#SBATCH --job-name=EAzami-cr-qc
#SBATCH --cpus-per-task=16
#SBATCH --mem=48G
#SBATCH --time=12:00:00
"""+common()+"""
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

def submit_script(mode):
    hyb="02_hybpiper_bwa_slurm.sh" if mode=="bwa" else "02b_hybpiper_blastx_slurm.sh"
    return f"""#!/usr/bin/env bash
set -euo pipefail
prep=$(sbatch --parsable 00_prepare_inputs_slurm.sh)
fetch=$(sbatch --parsable --dependency=afterok:$prep 01_fetch_trim_slurm.sh)
hyb=$(sbatch --parsable --dependency=afterok:$fetch {hyb})
qc=$(sbatch --parsable --dependency=afterok:$hyb --export=ALL,MODE={mode} 03_retrieve_qc_slurm.sh)
printf 'prepare=%s\nfetch=%s\nhybpiper=%s\nqc=%s\n' "$prep" "$fetch" "$hyb" "$qc"
"""

def main():
    p=argparse.ArgumentParser(); p.add_argument('--bridge-contract',type=Path,required=True); p.add_argument('--locus-manifest',type=Path,required=True); p.add_argument('--outdir',type=Path,required=True); a=p.parse_args()
    bridge,locus=load(a.bridge_contract),load(a.locus_manifest); tips=validate(bridge,locus); a.outdir.mkdir(parents=True,exist_ok=True)
    runs_csv(a.outdir/'primary_runs.csv',tips); write(a.outdir/'env.yml',env_yml());
    (a.outdir/'bridge_contract.json').write_bytes(a.bridge_contract.read_bytes()); (a.outdir/'locus_set_manifest.json').write_bytes(a.locus_manifest.read_bytes())
    for name,text in [('00_prepare_inputs_slurm.sh',prepare_script()),('01_fetch_trim_slurm.sh',fetch_script()),('02_hybpiper_bwa_slurm.sh',hybpiper_script('bwa')),('02b_hybpiper_blastx_slurm.sh',hybpiper_script('blastx')),('03_retrieve_qc_slurm.sh',qc_script()),('submit_bwa_chain.sh',submit_script('bwa')),('submit_blastx_chain.sh',submit_script('blastx'))]: write(a.outdir/name,text,0o755)
    manifest={"bundle_version":"colour_rate_comp1061_hpc_bundle_v1","taxa":20,"states":{"C":17,"W":3},"primary_mapping":"bwa","mapping_sensitivity":"blastx","target_reference_sha256":REF_SHA,"hybpiper_version":"2.3.4","astral_source":{"commit":ASTRAL_COMMIT,"zip_git_blob_sha1":ASTRAL_ZIP_BLOB_SHA1},"current_stage_end":"retrieve_stats_paralog_qc","next_tree_stage":"apply current occupancy/paralog gates to frozen 241/531/1061 locus sets, add reference outgroups, align, infer IQ-TREE gene/concat trees and ASTRAL sensitivity","branch_length_tree_completed":False,"rate_fit_execution_allowed":False,"claim_limit":"Bundle execution through QC does not itself create an accepted branch-length rate tree. Library-type occupancy, current paralogs, outgroup/Cirsium-monophyly and matrix sensitivities must pass before tree promotion."}
    write(a.outdir/'execution_manifest.json',json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2))
if __name__=='__main__': main()
