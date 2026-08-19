#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${REPO_ROOT:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
OUTDIR="${1:-$PWD/maximum_public_nuclear_handoff}"
export REPO_ROOT

python "$REPO_ROOT/analysis/build_maximum_public_nuclear_hpc_handoff.py" --outdir "$OUTDIR"
while IFS= read -r -d '' script; do bash -n "$script"; done < <(find "$OUTDIR" -type f -name '*.sh' -print0)

python - "$OUTDIR/handoff_manifest.json" "$REPO_ROOT/data/evidence/east_asia_public_candidate_disposition_v2.json" <<'PY'
import json,sys
from pathlib import Path
m=json.loads(Path(sys.argv[1]).read_text())
d=json.loads(Path(sys.argv[2]).read_text())
assert m['handoff_version']=='maximum_public_nuclear_hpc_handoff_v2'
assert m['accepted_primary_before_empirical_candidate_gates']==294
assert m['baseline_public_runs']==295
assert m['analysis_taxon_labels']==270
assert set(m['independent_candidates'])=={'EA01','CNIPG'}
assert m['excluded_duplicate_controls']['EA02']['counts_as_independent_tip'] is False
assert m['sample_level_candidate_ceiling']==296
assert m['new_analysis_taxon_labels_at_candidate_ceiling']==0
assert m['combined_296_tree_built_by_this_handoff'] is False
assert m['new_china_sampling_freeze_allowed'] is False
assert d['independent_candidates_beyond_primary']==['EA01','CNIPG']
assert d['candidates']['EA02']['counts_toward_public_tip_ceiling'] is False
print('maximum_public_v2_preflight=passed')
PY

cat <<EOF
Prepared current post-empirical handoff: $OUTDIR
Accepted primary: 294 tips / 295 SRRs / 270 labels
Independent candidates: EA01 + CNIPG
EA02: duplicate-control only; never submitted as an independent biological tip
Maximum candidate ceiling if both gates pass: 296 tips / 0 new labels
Combined 296 acceptance remains blocked until a common paired-locus tree is built.
EOF

if [[ "${PREPARE_ONLY:-0}" == "1" ]]; then
  echo "PREPARE_ONLY=1: bundle generation complete; Slurm submission skipped"
  exit 0
fi

command -v sbatch >/dev/null 2>&1 || {
  echo "sbatch is required for heavy execution; rerun with PREPARE_ONLY=1 for bundle generation only" >&2
  exit 2
}

bash "$OUTDIR/submit_all_independent_public_gates.sh"
