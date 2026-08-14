#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${REPO_ROOT:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
OUTDIR="${1:-$PWD/maximum_public_nuclear_handoff}"
export REPO_ROOT

# The v1 bundle is still generated in PREPARE_ONLY mode as a reproducibility
# check of the pre-empirical planning state. Real-read analysis on 2026-08-14
# showed that EA02 is a duplicate-readset pseudoreplicate of the accepted
# baseline C. sairamense sample, so this v1 297-tip submission graph is no
# longer an allowed heavy-execution entry point.
python "$REPO_ROOT/analysis/build_maximum_public_nuclear_hpc_handoff.py" \
  --outdir "$OUTDIR"

while IFS= read -r -d '' script; do
  bash -n "$script"
done < <(find "$OUTDIR" -type f -name '*.sh' -print0)

python - "$OUTDIR/handoff_manifest.json" "$REPO_ROOT/data/evidence/east_asia_public_candidate_disposition_v2.json" <<'PY'
import json,sys
from pathlib import Path
legacy=json.loads(Path(sys.argv[1]).read_text())
current=json.loads(Path(sys.argv[2]).read_text())
assert legacy['handoff_version']=='maximum_public_nuclear_hpc_handoff_v1'
assert legacy['accepted_primary_before_empirical_candidate_gates']==294
assert legacy['baseline_public_runs']==295
assert legacy['analysis_taxon_labels']==270
assert legacy['sample_level_candidate_ceiling']==297  # historical v1 arithmetic only
assert current['contract_version']=='east_asia_public_candidate_disposition_v2'
assert current['independent_candidates_beyond_primary']==['EA01','CNIPG']
assert current['candidates']['EA02']['independent_biological_tip_candidate'] is False
assert current['candidates']['EA02']['counts_toward_public_tip_ceiling'] is False
assert current['revised_sample_level_candidate_ceiling']==296
assert current['new_analysis_taxon_labels_at_ceiling']==0
assert current['combined_296_is_accepted_tree'] is False
print('legacy_v1_bundle_reproducibility_preflight=passed')
print('current_candidate_disposition=EA01+CNIPG_only')
PY

cat <<EOF
Prepared legacy v1 bundle for reproducibility only: $OUTDIR
Accepted primary: 294 tips / 295 SRRs / 270 labels
Current independent candidates after real-read audit: EA01 + CNIPG
EA02: excluded as duplicate-readset pseudoreplicate pending explicit contrary provenance
Revised public sample-level ceiling: 296 tips / 0 new labels
Accepted primary remains 294.
EOF

if [[ "${PREPARE_ONLY:-0}" == "1" ]]; then
  echo "PREPARE_ONLY=1: legacy bundle generation complete; Slurm submission skipped"
  exit 0
fi

cat >&2 <<'EOF'
Heavy submission BLOCKED: this v1 orchestrator still contains the superseded
EA02-independent-tip assumption. Real-read evidence freezes EA02 as a duplicate
control, not a biological augmentation tip. Build/use the post-empirical
EA01+CNIPG v2 handoff before launching the maximum-public heavy analysis.
EOF
exit 3
