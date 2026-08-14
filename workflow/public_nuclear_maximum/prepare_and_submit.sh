#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${REPO_ROOT:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
OUTDIR="${1:-$PWD/maximum_public_nuclear_handoff}"
export REPO_ROOT

python "$REPO_ROOT/analysis/build_maximum_public_nuclear_hpc_handoff.py" \
  --outdir "$OUTDIR"

while IFS= read -r -d '' script; do
  bash -n "$script"
done < <(find "$OUTDIR" -type f -name '*.sh' -print0)

python - "$OUTDIR/handoff_manifest.json" <<'PY'
import json,sys
from pathlib import Path
m=json.loads(Path(sys.argv[1]).read_text())
assert m['handoff_version']=='maximum_public_nuclear_hpc_handoff_v1'
assert m['accepted_primary_before_empirical_candidate_gates']==294
assert m['baseline_public_runs']==295
assert m['analysis_taxon_labels']==270
assert m['candidates']['EA01']['strict_loci']==236
assert m['candidates']['EA02']['strict_loci']==239
assert m['candidates']['CNIPG']['strict_loci']==180
assert m['sample_level_candidate_ceiling']==297
assert m['new_analysis_taxon_labels_at_candidate_ceiling']==0
assert m['baseline_download_shared_across_all_independent_gates'] is True
assert m['all_inputs_materialized_from_repository_evidence'] is True
assert m['github_actions_artifact_runtime_dependency'] is False
assert m['heavy_compute_executed_by_builder'] is False
assert m['combined_296_or_297_tree_built_by_this_handoff'] is False
assert m['combined_tree_requires_explicit_common_paired_locus_contract_after_independent_admission'] is True
assert m['new_china_sampling_freeze_allowed'] is False
print('maximum_public_handoff_preflight=passed')
PY

cat <<EOF
Prepared and validated: $OUTDIR
Accepted primary before empirical candidate gates: 294 tips / 295 SRRs / 270 labels
Independent candidates: EA01=236 loci, EA02=239 loci, CNIPG=180 loci
Candidate ceiling if all independent gates pass: 297 tips / 0 new labels
Combined 296/297 acceptance remains blocked pending a common paired-locus tree.
EOF

if [[ "${PREPARE_ONLY:-0}" == "1" ]]; then
  echo "PREPARE_ONLY=1: Slurm submission skipped"
  exit 0
fi

command -v sbatch >/dev/null 2>&1 || {
  echo "sbatch is required for heavy execution; rerun with PREPARE_ONLY=1 for bundle generation only" >&2
  exit 2
}

bash "$OUTDIR/submit_all_independent_public_gates.sh"
