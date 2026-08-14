#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
OUTDIR="${1:-$PWD/colour_rate_comp1061_hpc_bundle}"

python "$REPO_ROOT/analysis/build_colour_rate_comp1061_hpc_bundle.py" \
  --bridge-contract "$REPO_ROOT/data/evidence/colour_rate_comp1061_bridge_artifact_contract_v1.json" \
  --locus-manifest "$REPO_ROOT/data/evidence/moreyra_public_locus_set_manifest_v1.json" \
  --outdir "$OUTDIR"

python "$REPO_ROOT/analysis/augment_colour_rate_comp1061_tree_stages.py" \
  --bundle-dir "$OUTDIR"

for script in "$OUTDIR"/*.sh; do
  bash -n "$script"
done

python - "$OUTDIR" <<'PY'
import csv, json, pathlib, sys
root=pathlib.Path(sys.argv[1])
rows=list(csv.DictReader((root/'primary_runs.csv').open()))
manifest=json.loads((root/'execution_manifest.json').read_text())
assert len(rows)==20 and len({r['tip_id'] for r in rows})==20
assert sum(r['binary_colour_code']=='W' for r in rows)==3
assert manifest['bundle_version']=='colour_rate_comp1061_hpc_bundle_v0_3_tree_stage'
assert manifest['current_stage_end']=='tree_acceptance_scripts_prepared'
assert manifest['tree_stage']['frozen_locus_universe']==241
assert manifest['tree_stage']['current_occupancy_gate']==0.8
assert 'paralog' in manifest['tree_stage']['current_paralog_gate']
assert manifest['tree_stage']['minimum_eligible_loci_to_launch']==100
assert manifest['branch_length_tree_completed'] is False
assert manifest['rate_fit_execution_allowed'] is False
required={
 '00_prepare_inputs_slurm.sh','01_fetch_trim_slurm.sh','02_hybpiper_bwa_slurm.sh',
 '02b_hybpiper_blastx_slurm.sh','03_retrieve_qc_slurm.sh','04_prepare_tree_inputs_slurm.sh',
 '05_align_loci_slurm.sh','06_gene_trees_slurm.sh','07_concat_tree_slurm.sh',
 '08_accept_tree_slurm.sh','submit_bwa_chain.sh','submit_blastx_chain.sh','submit_tree_chain.sh'
}
missing=sorted(required-{p.name for p in root.glob('*.sh')})
assert not missing, missing
print('bundle_validation=passed')
print('taxa=20 states=C17_W3')
print('tree_stage=current_paralog_plus_occupancy_gate')
print('branch_length_tree_completed=false')
PY

cat <<EOF
Prepared: $OUTDIR

Execution order on Slurm/HPC:
  cd "$OUTDIR"
  bash submit_bwa_chain.sh

After the BWA HybPiper/QC jobs have completed successfully, inspect:
  results/colour_rate_comp1061/qc_bwa/
Then submit the predeclared tree chain:
  MODE=bwa bash submit_tree_chain.sh

Optional mapping sensitivity after/alongside the primary run:
  bash submit_blastx_chain.sh
  MODE=blastx bash submit_tree_chain.sh

Important: an IQ-TREE result is not automatically a rate result. 08_accept_tree_slurm.sh
checks branch lengths, exact atlas tip joins, declared OUTGROUP_lett/OUTGROUP_sunf,
focal monophyly relative to those references, provenance and the tree byte hash.
The current C17/W3 atlas still blocks empirical ER/ARD fitting until the fixed-white
promotion gate yields a rebuilt 22-species-tip C17/W5 tree.
EOF
