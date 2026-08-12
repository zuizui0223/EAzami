#!/usr/bin/env python3
"""Add alignment/tree/acceptance stages to a validated colour-rate HPC bundle."""
from __future__ import annotations
import argparse,json
from pathlib import Path


def common():
    return '''set -euo pipefail
BUNDLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${REPO_ROOT:-$(cd "$BUNDLE_DIR/../.." && pwd)}"
RESULT_ROOT="${RESULT_ROOT:-$PWD/results/colour_rate_comp1061}"
ENV_PREFIX="${ENV_PREFIX:-$REPO_ROOT/.conda/eazami-colour-rate-comp1061}"
MODE="${MODE:-bwa}"
[[ "$MODE" == "bwa" || "$MODE" == "blastx" ]]
if command -v micromamba >/dev/null 2>&1; then RUN=(micromamba run -p "$ENV_PREFIX"); elif command -v mamba >/dev/null 2>&1; then RUN=(mamba run -p "$ENV_PREFIX"); else echo "micromamba or mamba required" >&2; exit 2; fi
'''

def prep():
    return '#!/usr/bin/env bash\n#SBATCH --job-name=EAzami-cr-treeprep\n#SBATCH --cpus-per-task=4\n#SBATCH --mem=16G\n#SBATCH --time=04:00:00\n'+common()+'''TREE="$RESULT_ROOT/tree_$MODE"
mkdir -p "$TREE"
"${RUN[@]}" python "$REPO_ROOT/analysis/prepare_colour_rate_comp1061_tree_inputs.py" \
 --primary-runs "$BUNDLE_DIR/primary_runs.csv" \
 --locus-list "$RESULT_ROOT/inputs/locus_sets/moreyra_conservative_241_no_warning_loci.txt" \
 --retrieved-dir "$RESULT_ROOT/qc_$MODE/retrieved_dna" \
 --target "$RESULT_ROOT/inputs/reference/comp1061_hybpiper_reference.fasta" \
 --outdir "$TREE/inputs" --min-fraction 0.8
test -s "$TREE/inputs/eligible_loci.txt"
echo tree_input_checkpoint=complete mode=$MODE
'''
def align():
    return '#!/usr/bin/env bash\n#SBATCH --job-name=EAzami-cr-align\n#SBATCH --array=0-240\n#SBATCH --cpus-per-task=4\n#SBATCH --mem=8G\n#SBATCH --time=02:00:00\n'+common()+'''TREE="$RESULT_ROOT/tree_$MODE"; IDX="${SLURM_ARRAY_TASK_ID:?}"
LOCUS=$(sed -n "$((IDX+1))p" "$TREE/inputs/eligible_loci.txt" || true)
[[ -n "$LOCUS" ]] || exit 0
IN="$TREE/inputs/loci_unaligned/$LOCUS.fasta"; OUT="$TREE/alignments/$LOCUS.aln.fasta"; mkdir -p "$TREE/alignments"
[[ -s "$OUT" ]] && exit 0
test -s "$IN"; "${RUN[@]}" mafft --auto --thread 4 "$IN" > "$OUT"; test -s "$OUT"
'''
def gene():
    return '#!/usr/bin/env bash\n#SBATCH --job-name=EAzami-cr-genetree\n#SBATCH --array=0-240\n#SBATCH --cpus-per-task=4\n#SBATCH --mem=8G\n#SBATCH --time=04:00:00\n'+common()+'''TREE="$RESULT_ROOT/tree_$MODE"; IDX="${SLURM_ARRAY_TASK_ID:?}"
LOCUS=$(sed -n "$((IDX+1))p" "$TREE/inputs/eligible_loci.txt" || true); [[ -n "$LOCUS" ]] || exit 0
ALN="$TREE/alignments/$LOCUS.aln.fasta"; PREFIX="$TREE/gene_trees/$LOCUS"; mkdir -p "$TREE/gene_trees"
[[ -s "$PREFIX.treefile" ]] && exit 0
test -s "$ALN"; "${RUN[@]}" iqtree2 -s "$ALN" -m MFP -B 1000 --alrt 1000 -T 4 -o OUTGROUP_lett,OUTGROUP_sunf --prefix "$PREFIX"; test -s "$PREFIX.treefile"
'''
def concat():
    return '#!/usr/bin/env bash\n#SBATCH --job-name=EAzami-cr-concat\n#SBATCH --cpus-per-task=16\n#SBATCH --mem=32G\n#SBATCH --time=24:00:00\n'+common()+'''TREE="$RESULT_ROOT/tree_$MODE"; mkdir -p "$TREE/concat"
"${RUN[@]}" python "$REPO_ROOT/analysis/concatenate_colour_rate_comp1061_alignments.py" \
 --eligible-loci "$TREE/inputs/eligible_loci.txt" --alignment-dir "$TREE/alignments" \
 --primary-runs "$BUNDLE_DIR/primary_runs.csv" --output "$TREE/concat/concat.fasta" \
 --partitions "$TREE/concat/partitions.csv" --summary "$TREE/concat/concat_summary.json"
"${RUN[@]}" iqtree2 -s "$TREE/concat/concat.fasta" -m MFP -B 1000 --alrt 1000 -T AUTO \
 -o OUTGROUP_lett,OUTGROUP_sunf --prefix "$TREE/concat/colour_rate_comp1061_concat"
test -s "$TREE/concat/colour_rate_comp1061_concat.treefile"
echo concat_tree_checkpoint=complete mode=$MODE
'''
def accept():
    return '#!/usr/bin/env bash\n#SBATCH --job-name=EAzami-cr-accept\n#SBATCH --cpus-per-task=2\n#SBATCH --mem=4G\n#SBATCH --time=01:00:00\n'+common()+'''TREE="$RESULT_ROOT/tree_$MODE"; TREEFILE="$TREE/concat/colour_rate_comp1061_concat.treefile"; test -s "$TREEFILE"
python - <<'PY'
import csv,hashlib,json,os,pathlib
bundle=pathlib.Path(os.environ['BUNDLE_DIR']); root=pathlib.Path(os.environ['RESULT_ROOT']); mode=os.environ['MODE']; tr=root/f'tree_{mode}'; tree=tr/'concat/colour_rate_comp1061_concat.treefile'
rows=list(csv.DictReader((bundle/'primary_runs.csv').open()))
with (tr/'tip_map.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['tree_tip','accepted_taxon','mapping_status']);w.writeheader();w.writerows({'tree_tip':r['tip_id'],'accepted_taxon':r['accepted_taxon'],'mapping_status':'exact'} for r in rows)
sha=hashlib.sha256(tree.read_bytes()).hexdigest()
prov={'tree_route':'compatibility_reanalysis','tree_sha256':sha,'analysis_name':f'EAzami 20-tip Compositae1061 {mode} concatenated ML tree','branch_length_interpretation':'IQ-TREE maximum-likelihood substitutions per site on concatenated recovered coding-sequence alignment','rooting_definition':'IQ-TREE rooted using OUTGROUP_lett and OUTGROUP_sunf reference sequences appended from the pinned original Compositae1061 target','support_metric_definition':'IQ-TREE ultrafast bootstrap 1000 plus SH-aLRT 1000; per-locus ML gene trees retained as topology sensitivity','source_or_pipeline_provenance':'20 frozen colour-atlas taxa; pinned original Compositae1061 reference SHA256 77d510ef101d08a7a23a4df391d077d3b7f75482c66f7f4bea6d32cf290ced2c; frozen Moreyra conservative 241-locus universe; current 20-tip occupancy >=0.80; HybPiper 2.3.4; MAFFT; IQ-TREE','topology_uncertainty_status':'bootstrap_or_gene_tree_sensitivity'}
(tr/'tree_provenance.json').write_text(json.dumps(prov,indent=2)+'\n')
PY
export BUNDLE_DIR RESULT_ROOT MODE
"${RUN[@]}" python "$REPO_ROOT/analysis/validate_colour_atlas_branch_length_tree.py" \
 --tree "$TREEFILE" --atlas "$REPO_ROOT/data/evidence/cirsium_flower_colour_atlas_v0_3.csv" \
 --tip-map "$TREE/tip_map.csv" --provenance "$TREE/tree_provenance.json" --output "$TREE/tree_acceptance.json"
test -s "$TREE/tree_acceptance.json"; echo tree_acceptance_checkpoint=complete mode=$MODE
'''
def submit():
    return '''#!/usr/bin/env bash
set -euo pipefail
MODE="${MODE:-bwa}"
prep=$(sbatch --parsable --export=ALL,MODE="$MODE" 04_prepare_tree_inputs_slurm.sh)
align=$(sbatch --parsable --dependency=afterok:$prep --export=ALL,MODE="$MODE" 05_align_loci_slurm.sh)
gene=$(sbatch --parsable --dependency=afterok:$align --export=ALL,MODE="$MODE" 06_gene_trees_slurm.sh)
concat=$(sbatch --parsable --dependency=afterok:$align --export=ALL,MODE="$MODE" 07_concat_tree_slurm.sh)
accept=$(sbatch --parsable --dependency=afterok:$gene:$concat --export=ALL,MODE="$MODE" 08_accept_tree_slurm.sh)
printf 'prep=%s\nalign=%s\ngene=%s\nconcat=%s\naccept=%s\n' "$prep" "$align" "$gene" "$concat" "$accept"
'''
def main():
    p=argparse.ArgumentParser();p.add_argument('--bundle-dir',type=Path,required=True);a=p.parse_args(); b=a.bundle_dir
    m=json.loads((b/'execution_manifest.json').read_text())
    if m.get('current_stage_end')!='retrieve_stats_paralog_qc': raise ValueError('Expected v0.2 QC-stage bundle')
    files={'04_prepare_tree_inputs_slurm.sh':prep(),'05_align_loci_slurm.sh':align(),'06_gene_trees_slurm.sh':gene(),'07_concat_tree_slurm.sh':concat(),'08_accept_tree_slurm.sh':accept(),'submit_tree_chain.sh':submit()}
    for n,t in files.items(): q=b/n;q.write_text(t);q.chmod(0o755)
    m['bundle_version']='colour_rate_comp1061_hpc_bundle_v0_3_tree_stage';m['current_stage_end']='tree_acceptance_scripts_prepared';m['tree_stage']={'frozen_locus_universe':241,'current_occupancy_gate':0.8,'minimum_eligible_loci_to_launch':100,'primary_branch_length_tree':'concatenated IQ-TREE ML substitutions/site','topology_sensitivity':'per-locus IQ-TREE gene trees','required_outgroups':['OUTGROUP_lett','OUTGROUP_sunf'],'acceptance_validator':'analysis/validate_colour_atlas_branch_length_tree.py'};m['branch_length_tree_completed']=False;m['rate_fit_execution_allowed']=False
    (b/'execution_manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(m,indent=2))
if __name__=='__main__': main()
