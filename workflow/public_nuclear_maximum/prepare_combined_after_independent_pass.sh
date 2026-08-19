#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${REPO_ROOT:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
MAXIMUM_HANDOFF="${1:?Usage: prepare_combined_after_independent_pass.sh MAXIMUM_HANDOFF [COMBINED_BUNDLE]}"
COMBINED_BUNDLE="${2:-$MAXIMUM_HANDOFF/combined_post_admission_bundle}"
export REPO_ROOT

python "$REPO_ROOT/analysis/build_maximum_public_combined_hpc_bundle.py" \
  --maximum-handoff "$MAXIMUM_HANDOFF" \
  --outdir "$COMBINED_BUNDLE"

while IFS= read -r -d '' script; do
  bash -n "$script"
done < <(find "$COMBINED_BUNDLE" -type f -name '*.sh' -print0)

python - "$COMBINED_BUNDLE/execution_manifest.json" <<'PY'
import json,sys
m=json.load(open(sys.argv[1]))
assert m['bundle_version']=='maximum_public_combined_hpc_bundle_v2'
assert m['source_maximum_handoff_version']=='maximum_public_nuclear_hpc_handoff_v2'
assert m['prerequisite_independent_gate_contract']=='maximum_public_nuclear_independent_gate_summary_v2'
assert m['independent_candidates_required_to_pass']==['EA01','CNIPG']
assert m['excluded_duplicate_controls']==['EA02']
assert m['baseline_focal_tips']==294
assert m['scenario_count']==4
assert m['final_scenario']=='ea01_cnipg_296'
assert m['mapping_modes']==['bwa','blastx']
assert m['minimum_common_loci']==100
assert m['all_scenarios_same_locus_set_within_mode'] is True
assert m['ea02_enters_biological_tree_inputs'] is False
assert m['combined_296_acceptance_pre_authorized'] is False
assert m['new_analysis_taxon_labels_added']==0
assert m['new_china_sampling_freeze_allowed'] is False
assert m['heavy_compute_executed_by_builder'] is False
print('combined_post_admission_bundle_v2_preflight=passed')
PY

cat <<EOF
Prepared and validated: $COMBINED_BUNDLE
This bundle remains dormant until independent_gate_summary.json records EA01 and CNIPG both passing.
EA02 remains excluded as a duplicate-readset control and never enters biological tree inputs.
It will reconstruct 4 scenarios separately for BWA and BLASTx on one baseline∩EA01∩CNIPG common-locus set per mode.
A 296-sample state can be accepted only if every subset scenario passes concatenated shared-294 and source-label ASTRAL invariance in both modes.
EOF

if [[ "${PREPARE_ONLY:-0}" == "1" ]]; then
  echo "PREPARE_ONLY=1: combined Slurm submission skipped"
  exit 0
fi

command -v sbatch >/dev/null 2>&1 || {
  echo "sbatch is required for heavy combined-tree execution; use PREPARE_ONLY=1 to build only" >&2
  exit 2
}

bash "$COMBINED_BUNDLE/submit_combined_after_independent_pass.sh"
