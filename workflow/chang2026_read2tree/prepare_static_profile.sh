#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

RESULT_ROOT="${RESULT_ROOT:-$PWD/results/chang2026_read2tree_static400}"
READS_ROOT="${READS_ROOT:-$PWD/results/chang2026_takaoense_pilot}"
PANEL="${PANEL:-$REPO_ROOT/sampling/chang2026_takaoense6_read2tree_panel_v1.csv}"
EVIDENCE="${EVIDENCE:-$REPO_ROOT/data/evidence/chang2026_takaoense_morph_linked_public_samples_v1.csv}"
REFS="${REFS:-$REPO_ROOT/sampling/read2tree_oma_reference_set_v0_2.csv}"
THREADS="${THREADS:-16}"
CHECK_INPUTS="${CHECK_INPUTS:-1}"
OMA_GROUP_FILE="${OMA_GROUP_FILE:-}"

SOURCE_DIR="$RESULT_ROOT/static_source"
VALIDATED_DIR="$RESULT_ROOT/validated_marker_pack"
PLAN_DIR="$RESULT_ROOT/read2tree_plan"
R2T_OUTPUT="$RESULT_ROOT/read2tree_output"
mkdir -p "$RESULT_ROOT"

# Scientific-input gate: exact run/voucher/BioSample/morph assignments must still
# match the direct Figure-1 + NCBI evidence before any marker data are fetched.
python "$REPO_ROOT/analysis/validate_chang2026_takaoense6_read2tree_panel.py" \
  --panel "$PANEL" \
  --evidence "$EVIDENCE"

builder=(
  python "$REPO_ROOT/analysis/build_read2tree_oma_static_marker_pack.py"
  --reference-manifest "$REFS"
  --outdir "$SOURCE_DIR"
)
if [[ -n "$OMA_GROUP_FILE" ]]; then
  builder+=(--group-file "$OMA_GROUP_FILE")
fi
"${builder[@]}"

python "$REPO_ROOT/analysis/validate_read2tree_oma_marker_pack.py" \
  --archive "$SOURCE_DIR/oma_static_broadconservation_marker_export.tar.gz" \
  --reference-manifest "$REFS" \
  --outdir "$VALIDATED_DIR" \
  --oma-release May2026 \
  --export-date "$(date +%F)" \
  --export-url "static-profile:oma_may2026_static_broadconservation400_v1" \
  --minimum-species-coverage 1.0 \
  --maximum-markers 400 \
  --expected-marker-count 400

plan=(
  python "$REPO_ROOT/analysis/build_chang2026_read2tree_pilot.py"
  --panel "$PANEL"
  --reference-manifest "$REFS"
  --marker-contract "$VALIDATED_DIR/marker_pack_contract.json"
  --reads-root "$READS_ROOT"
  --reads-stage trimmed
  --output-dir "$R2T_OUTPUT"
  --plan-outdir "$PLAN_DIR"
  --threads "$THREADS"
)
if [[ "$CHECK_INPUTS" == "1" ]]; then
  plan+=(--check-inputs)
elif [[ "$CHECK_INPUTS" != "0" ]]; then
  echo "CHECK_INPUTS must be 0 or 1" >&2
  exit 2
fi
"${plan[@]}"

cat <<EOF
Prepared deterministic Read2Tree static profile.

Source contract:
  $SOURCE_DIR/static_marker_source_contract.json
Normalized marker contract:
  $VALIDATED_DIR/marker_pack_contract.json
Read2Tree plan:
  $PLAN_DIR/run_read2tree_fast_screen.sh

Next explicit heavy step:
  bash $PLAN_DIR/run_read2tree_fast_screen.sh

After IQ-TREE completes, score the tree with:
  python $REPO_ROOT/analysis/run_chang2026_read2tree_scoring_contract.py \
    --tree $R2T_OUTPUT/takaoense6_read2tree_dna.treefile \
    --panel $PANEL \
    --reference-manifest $REFS \
    --frozen-hypotheses $REPO_ROOT/analysis/chang2026_takaoense_gene_tree_hypotheses_v1.csv \
    --expected-hypothesis-sha256 5cf8aed00a71df8d18868b7b7d108344dcc22ec79541e53a941ce43df295e7ef \
    --nearest $REPO_ROOT/analysis/chang2026_takaoense_nearest_no_regain_topologies.csv \
    --robustness-summary $REPO_ROOT/analysis/chang2026_takaoense_topology_robustness_summary.json \
    --scorer $REPO_ROOT/analysis/score_chang2026_read2tree_topology.py \
    --thresholds 0,50,70,90 \
    --output $RESULT_ROOT/read2tree_topology_scores.csv \
    --hypothesis-output $RESULT_ROOT/read2tree_per_hypothesis_scores.csv \
    --summary-json $RESULT_ROOT/read2tree_topology_summary.json
EOF
