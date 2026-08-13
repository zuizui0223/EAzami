#!/usr/bin/env python3
"""Build the paired EA01/EA02 augmentation stage for the 294-tip public tree.

The bundle assumes the ordinary v2 data-recovery stage has already produced
accepted tree inputs for BWA and/or BLASTx.  It then recomputes four scenarios
on one joint paired locus set: 294 baseline, +EA01, +EA02, and +EA01+EA02.
"""
from __future__ import annotations
import argparse,csv,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCENARIOS=("baseline294","ea01_295","ea02_295","ea01_ea02_296")

def clean(x:object)->str:return str(x or '').strip()
def write(path:Path,text:str,mode:int=0o644)->None:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf-8');path.chmod(mode)

def validate_baseline(bundle:Path)->None:
    m=json.loads((bundle/'execution_manifest.json').read_text())
    if m.get('bundle_version')!='japan_origin_global_hpc_bundle_v2' or m.get('biological_samples')!=294 or m.get('public_runs')!=295: raise ValueError('baseline bundle is not frozen v2 294-tip/295-SRR bundle')
    with (bundle/'sample_manifest.csv').open(encoding='utf-8-sig',newline='') as h: rows=list(csv.DictReader(h))
    if len(rows)!=294 or len({r['tip_id'] for r in rows})!=294: raise ValueError('baseline sample manifest drift')
    if not (bundle/'astral_species_map.csv').is_file(): raise ValueError('baseline ASTRAL species map missing')

def validate_pack(pack:Path,cid:str)->dict:
    s=json.loads((pack/'candidate_pack_summary.json').read_text())
    if s.get('candidate_id')!=cid or not s.get('pilot_locus_pack_ready') or s.get('tree_tip_promotion_allowed'): raise ValueError(f'invalid {cid} candidate pack')
    if not (pack/'strict_recovered_loci.txt').is_file() or not (pack/'loci').is_dir(): raise ValueError(f'incomplete {cid} pack')
    return s

def common()->str:return '''set -euo pipefail
BUNDLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${REPO_ROOT:-$(cd "$BUNDLE_DIR/../.." && pwd)}"
BASELINE_RESULT_ROOT="${BASELINE_RESULT_ROOT:-$PWD/results/japan_origin_global_v2}"
AUGMENT_ROOT="${AUGMENT_ROOT:-$PWD/results/east_asia_public_augmentation}"
ENV_PREFIX="${ENV_PREFIX:-$REPO_ROOT/.conda/eazami-japan-origin-global}"
export BUNDLE_DIR REPO_ROOT BASELINE_RESULT_ROOT AUGMENT_ROOT ENV_PREFIX
if command -v micromamba >/dev/null 2>&1; then
  if [[ ! -x "$ENV_PREFIX/bin/python" ]]; then micromamba create -y -p "$ENV_PREFIX" -f "$BUNDLE_DIR/env.yml"; fi
  RUN=(micromamba run -p "$ENV_PREFIX")
elif command -v mamba >/dev/null 2>&1; then
  if [[ ! -x "$ENV_PREFIX/bin/python" ]]; then mamba env create -y -p "$ENV_PREFIX" -f "$BUNDLE_DIR/env.yml"; fi
  RUN=(mamba run -p "$ENV_PREFIX")
else echo "micromamba or mamba required" >&2; exit 2; fi
mkdir -p "$AUGMENT_ROOT"
'''
def prep()->str:return '''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-eaaug-prep
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=02:00:00
'''+common()+'''MODE="${MODE:-bwa}"
PRIMARY="$BASELINE_RESULT_ROOT/tree_$MODE/inputs"
test -s "$PRIMARY/eligible_loci.txt"
"${RUN[@]}" python "$BUNDLE_DIR/helpers/prepare_east_asia_public_augmentation_tree_inputs.py" \
  --primary-inputs "$PRIMARY" \
  --baseline-manifest "$BUNDLE_DIR/baseline_sample_manifest.csv" \
  --baseline-species-map "$BUNDLE_DIR/baseline_astral_species_map.csv" \
  --ea01-pack "$BUNDLE_DIR/candidate_packs/EA01" \
  --ea02-pack "$BUNDLE_DIR/candidate_packs/EA02" \
  --contract "$BUNDLE_DIR/augmentation_contract.json" \
  --outdir "$AUGMENT_ROOT/$MODE/paired_inputs"
'''
def align()->str:return '''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-eaaug-align
#SBATCH --array=0-963%24
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=04:00:00
'''+common()+'''MODE="${MODE:-bwa}"; TASK="${SLURM_ARRAY_TASK_ID:?}"; SIDX=$((TASK / 241)); LIDX=$((TASK % 241)); SCENARIOS=(baseline294 ea01_295 ea02_295 ea01_ea02_296); [[ "$SIDX" -lt 4 ]] || exit 0; S="${SCENARIOS[$SIDX]}"; INPUT="$AUGMENT_ROOT/$MODE/paired_inputs/$S"; LOCUS=$(sed -n "$((LIDX+1))p" "$INPUT/eligible_loci.txt" || true); [[ -n "$LOCUS" ]] || exit 0; IN="$INPUT/loci_unaligned/$LOCUS.fasta"; OUT="$AUGMENT_ROOT/$MODE/$S/alignments/$LOCUS.aln.fasta"; mkdir -p "$(dirname "$OUT")"; [[ -s "$OUT" ]] && exit 0; test -s "$IN"; "${RUN[@]}" mafft --auto --thread 4 "$IN" > "$OUT"; test -s "$OUT"
'''
def gene()->str:return '''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-eaaug-gene
#SBATCH --array=0-963%20
#SBATCH --cpus-per-task=4
#SBATCH --mem=12G
#SBATCH --time=08:00:00
'''+common()+'''MODE="${MODE:-bwa}"; TASK="${SLURM_ARRAY_TASK_ID:?}"; SIDX=$((TASK / 241)); LIDX=$((TASK % 241)); SCENARIOS=(baseline294 ea01_295 ea02_295 ea01_ea02_296); [[ "$SIDX" -lt 4 ]] || exit 0; S="${SCENARIOS[$SIDX]}"; INPUT="$AUGMENT_ROOT/$MODE/paired_inputs/$S"; LOCUS=$(sed -n "$((LIDX+1))p" "$INPUT/eligible_loci.txt" || true); [[ -n "$LOCUS" ]] || exit 0; ALN="$AUGMENT_ROOT/$MODE/$S/alignments/$LOCUS.aln.fasta"; PREFIX="$AUGMENT_ROOT/$MODE/$S/gene_trees/$LOCUS"; mkdir -p "$(dirname "$PREFIX")"; [[ -s "$PREFIX.treefile" ]] && exit 0; test -s "$ALN"; "${RUN[@]}" iqtree2 -s "$ALN" -m MFP -B 1000 --alrt 1000 -T 4 -o OUTGROUP_lett,OUTGROUP_sunf --prefix "$PREFIX"; test -s "$PREFIX.treefile"
'''
def concat()->str:return '''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-eaaug-concat
#SBATCH --array=0-3
#SBATCH --cpus-per-task=32
#SBATCH --mem=128G
#SBATCH --time=48:00:00
'''+common()+'''MODE="${MODE:-bwa}"; SCENARIOS=(baseline294 ea01_295 ea02_295 ea01_ea02_296); S="${SCENARIOS[${SLURM_ARRAY_TASK_ID:?}]}"; INPUT="$AUGMENT_ROOT/$MODE/paired_inputs/$S"; TREE="$AUGMENT_ROOT/$MODE/$S"; mkdir -p "$TREE/concat"; "${RUN[@]}" python "$BUNDLE_DIR/helpers/concatenate_colour_rate_comp1061_alignments.py" --eligible-loci "$INPUT/eligible_loci.txt" --alignment-dir "$TREE/alignments" --primary-runs "$INPUT/primary_runs.csv" --output "$TREE/concat/concat.fasta" --partitions "$TREE/concat/partitions.csv" --summary "$TREE/concat/concat_summary.json"; "${RUN[@]}" iqtree2 -s "$TREE/concat/concat.fasta" -m MFP -B 1000 --alrt 1000 -T AUTO -o OUTGROUP_lett,OUTGROUP_sunf --prefix "$TREE/concat/$S"; test -s "$TREE/concat/$S.treefile"
'''
def astral()->str:return '''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-eaaug-astral
#SBATCH --array=0-3
#SBATCH --cpus-per-task=4
#SBATCH --mem=96G
#SBATCH --time=12:00:00
'''+common()+'''MODE="${MODE:-bwa}"; SCENARIOS=(baseline294 ea01_295 ea02_295 ea01_ea02_296); S="${SCENARIOS[${SLURM_ARRAY_TASK_ID:?}]}"; INPUT="$AUGMENT_ROOT/$MODE/paired_inputs/$S"; TREE="$AUGMENT_ROOT/$MODE/$S"; OUT="$TREE/astral"; mkdir -p "$OUT"; GT="$OUT/gene_trees.tre"; : > "$GT"; while IFS= read -r LOCUS; do test -s "$TREE/gene_trees/$LOCUS.treefile"; cat "$TREE/gene_trees/$LOCUS.treefile" >> "$GT"; printf '\n' >> "$GT"; done < "$INPUT/eligible_loci.txt"; MAP="$OUT/astral_map_runtime.txt"; cp "$INPUT/astral_map.txt" "$MAP"; if grep -q 'OUTGROUP_saff' "$GT"; then echo 'OUTGROUP_saff:OUTGROUP_saff' >> "$MAP"; fi; "${RUN[@]}" astral -Xmx90G -i "$GT" -a "$MAP" -o "$OUT/$S.astral.tree" 2> "$OUT/astral.log"; test -s "$OUT/$S.astral.tree"
'''
def evaluate()->str:return '''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-eaaug-eval
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=02:00:00
'''+common()+'''MODE="${MODE:-bwa}"; ROOT="$AUGMENT_ROOT/$MODE"; BASE="$ROOT/baseline294/concat/baseline294.treefile"; test -s "$BASE"; mkdir -p "$ROOT/evaluation"; for SPEC in 'ea01_295 EA01' 'ea02_295 EA02' 'ea01_ea02_296 EA01' 'ea01_ea02_296 EA02'; do set -- $SPEC; S="$1"; C="$2"; "${RUN[@]}" python "$BUNDLE_DIR/helpers/evaluate_east_asia_public_augmentation_tree_pair.py" --baseline-tree "$BASE" --augmented-tree "$ROOT/$S/concat/$S.treefile" --baseline-manifest "$BUNDLE_DIR/baseline_sample_manifest.csv" --contract "$BUNDLE_DIR/augmentation_contract.json" --candidate-id "$C" --output "$ROOT/evaluation/${S}_${C}_concat.json"; done; ABASE="$ROOT/baseline294/astral/baseline294.astral.tree"; test -s "$ABASE"; for S in ea01_295 ea02_295 ea01_ea02_296; do "${RUN[@]}" python "$BUNDLE_DIR/helpers/compare_east_asia_public_augmentation_astral_backbone.py" --baseline-tree "$ABASE" --augmented-tree "$ROOT/$S/astral/$S.astral.tree" --baseline-species-map "$ROOT/paired_inputs/baseline294/astral_species_map.csv" --scenario-id "$S" --output "$ROOT/evaluation/${S}_astral_backbone.json"; done
'''
def submit()->str:return '''#!/usr/bin/env bash
set -euo pipefail
MODE="${MODE:-bwa}"; prep=$(sbatch --parsable --export=ALL,MODE="$MODE" 10_prepare_paired_inputs_slurm.sh); aln=$(sbatch --parsable --dependency=afterok:$prep --export=ALL,MODE="$MODE" 11_align_paired_scenarios_slurm.sh); gene=$(sbatch --parsable --dependency=afterok:$aln --export=ALL,MODE="$MODE" 12_gene_trees_paired_scenarios_slurm.sh); con=$(sbatch --parsable --dependency=afterok:$aln --export=ALL,MODE="$MODE" 13_concat_paired_scenarios_slurm.sh); ast=$(sbatch --parsable --dependency=afterok:$gene --export=ALL,MODE="$MODE" 14_astral_paired_scenarios_slurm.sh); ev=$(sbatch --parsable --dependency=afterok:$con:$ast --export=ALL,MODE="$MODE" 15_evaluate_paired_scenarios_slurm.sh); printf 'prepare=%s\nalign=%s\ngene=%s\nconcat=%s\nastral=%s\nevaluate=%s\n' "$prep" "$aln" "$gene" "$con" "$ast" "$ev"
'''
def main()->int:
    p=argparse.ArgumentParser();p.add_argument('--baseline-bundle',type=Path,required=True);p.add_argument('--ea01-pack',type=Path,required=True);p.add_argument('--ea02-pack',type=Path,required=True);p.add_argument('--contract',type=Path,required=True);p.add_argument('--outdir',type=Path,required=True);a=p.parse_args();validate_baseline(a.baseline_bundle); e1=validate_pack(a.ea01_pack,'EA01'); e2=validate_pack(a.ea02_pack,'EA02'); contract=json.loads(a.contract.read_text());
    if contract.get('contract_version')!='east_asia_public_tree_augmentation_v1': raise ValueError('wrong augmentation contract')
    a.outdir.mkdir(parents=True,exist_ok=True); shutil.copy2(a.baseline_bundle/'env.yml',a.outdir/'env.yml'); shutil.copy2(a.baseline_bundle/'sample_manifest.csv',a.outdir/'baseline_sample_manifest.csv'); shutil.copy2(a.baseline_bundle/'astral_species_map.csv',a.outdir/'baseline_astral_species_map.csv'); shutil.copy2(a.contract,a.outdir/'augmentation_contract.json')
    for cid,src in [('EA01',a.ea01_pack),('EA02',a.ea02_pack)]:
        dst=a.outdir/'candidate_packs'/cid
        if dst.exists(): shutil.rmtree(dst)
        dst.mkdir(parents=True)
        for name in ('candidate_pack_summary.json','strict_recovered_loci.txt'): shutil.copy2(src/name,dst/name)
        shutil.copytree(src/'loci',dst/'loci')
    (a.outdir/'helpers').mkdir(parents=True,exist_ok=True)
    helpers=('prepare_east_asia_public_augmentation_tree_inputs.py','evaluate_east_asia_public_augmentation_tree_pair.py','compare_east_asia_public_augmentation_astral_backbone.py','concatenate_colour_rate_comp1061_alignments.py')
    for name in helpers: shutil.copy2(ROOT/'analysis'/name,a.outdir/'helpers'/name)
    scripts={'10_prepare_paired_inputs_slurm.sh':prep(),'11_align_paired_scenarios_slurm.sh':align(),'12_gene_trees_paired_scenarios_slurm.sh':gene(),'13_concat_paired_scenarios_slurm.sh':concat(),'14_astral_paired_scenarios_slurm.sh':astral(),'15_evaluate_paired_scenarios_slurm.sh':evaluate(),'submit_paired_augmentation_chain.sh':submit()}
    for name,text in scripts.items(): write(a.outdir/name,text,0o755)
    m={'bundle_version':'east_asia_public_augmentation_hpc_bundle_v1','baseline_bundle_version':'japan_origin_global_hpc_bundle_v2','baseline_focal_tips':294,'candidate_tip_ids':[e1['tip_id'],e2['tip_id']],'candidate_strict_loci':{'EA01':e1['strict_no_warning_recovered_loci'],'EA02':e2['strict_no_warning_recovered_loci']},'candidate_analysis_taxon_labels_already_in_baseline':['EA01','EA02'],'new_analysis_taxon_labels_added':0,'scenarios':list(SCENARIOS),'same_joint_locus_set_required':True,'minimum_joint_paired_loci':contract['minimum_joint_paired_loci'],'mapping_modes':['bwa','blastx'],'tree_products':['paired concatenated IQ-TREE trees','paired per-locus IQ-TREE gene trees','paired source-label ASTRAL trees','shared-backbone RF diagnostics'],'tree_tip_promotion_allowed':False,'primary_294_tree_superseded':False,'new_china_sampling_freeze_allowed':False}
    write(a.outdir/'execution_manifest.json',json.dumps(m,indent=2)+'\n'); print(json.dumps(m,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
