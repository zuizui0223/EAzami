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
assert m['bundle_version']=='maximum_public_combined_hpc_bundle_v1'
assert m['prerequisite_independent_gate_contract']=='maximum_public_nuclear_independent_gate_summary_v1'
assert m['independent_candidates_required_to_pass']==['EA01','EA02','CNIPG']
assert m['baseline_focal_tips']==294
assert m['scenario_count']==8
assert m['final_scenario']=='ea01_ea02_cnipg_297'
assert m['mapping_modes']==['bwa','blastx']
assert m['minimum_four_way_common_loci']==100
assert m['all_scenarios_same_locus_set_within_mode'] is True
assert m['combined_297_acceptance_pre_authorized'] is False
assert m['new_analysis_taxon_labels_added']==0
assert m['new_china_sampling_freeze_allowed'] is False
assert m['heavy_compute_executed_by_builder'] is False
print('combined_post_admission_bundle_preflight=passed')
PY

cat <<EOF
Prepared and validated: $COMBINED_BUNDLE
This bundle remains dormant until independent_gate_summary.json records EA01, EA02 and CNIPG all passing.
It will reconstruct 8 subset scenarios separately for BWA and BLASTx on one four-way common locus set per mode.
A 297-sample state can be accepted only if every subset scenario passes concatenated shared-294 and source-label ASTRAL invariance in both modes.
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
