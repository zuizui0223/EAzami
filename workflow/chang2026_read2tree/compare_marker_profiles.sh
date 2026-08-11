#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

STATIC_ROOT="${STATIC_ROOT:?set STATIC_ROOT to the completed static400 result root}"
BROWSER_ROOT="${BROWSER_ROOT:?set BROWSER_ROOT to the completed Browser400 result root}"
OUTDIR="${OUTDIR:-$PWD/results/chang2026_read2tree_profile_comparison}"

STATIC_CONTRACT="${STATIC_CONTRACT:-$STATIC_ROOT/validated_marker_pack/marker_pack_contract.json}"
BROWSER_CONTRACT="${BROWSER_CONTRACT:-$BROWSER_ROOT/validated_marker_pack/marker_pack_contract.json}"
STATIC_DETAILS="${STATIC_DETAILS:-$STATIC_ROOT/read2tree_topology_scores.csv}"
BROWSER_DETAILS="${BROWSER_DETAILS:-$BROWSER_ROOT/read2tree_topology_scores.csv}"

for path in "$STATIC_CONTRACT" "$BROWSER_CONTRACT" "$STATIC_DETAILS" "$BROWSER_DETAILS"; do
  if [[ ! -f "$path" ]]; then
    echo "Required profile-comparison input is missing: $path" >&2
    exit 2
  fi
done
mkdir -p "$OUTDIR"

python "$REPO_ROOT/analysis/compare_read2tree_oma_marker_packs.py" \
  --profile-a-contract "$STATIC_CONTRACT" \
  --profile-b-contract "$BROWSER_CONTRACT" \
  --expected-marker-count 400 \
  --output "$OUTDIR/marker_group_overlap.csv" \
  --summary-json "$OUTDIR/marker_group_overlap_summary.json"

python "$REPO_ROOT/analysis/compare_chang2026_read2tree_profiles.py" \
  --profile-a-details "$STATIC_DETAILS" \
  --profile-b-details "$BROWSER_DETAILS" \
  --profile-a-name oma_static_broadconservation400_may2026_v1 \
  --profile-b-name oma_browser_export400_may2026_v1 \
  --output "$OUTDIR/topology_profile_comparison.csv" \
  --summary-json "$OUTDIR/topology_profile_comparison_summary.json"

cat <<EOF
Read2Tree marker-profile comparison complete.

Marker overlap:
  $OUTDIR/marker_group_overlap_summary.json
Topology decision comparison:
  $OUTDIR/topology_profile_comparison_summary.json

Interpretation rule:
- direct candidate-regain vs loss-only disagreement => marker-profile conflict;
- one decisive + one unresolved/not-scored => not concordance;
- same decisive direction with high-support unresolved branches => support-sensitive concordance;
- same decisive direction at all thresholds => strongest fast-screen marker-profile concordance.

Even the strongest concordance remains a topology sensitivity result, not proof of
species history or molecular anthocyanin reactivation.
EOF
