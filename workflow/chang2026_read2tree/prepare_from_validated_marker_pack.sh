#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

: "${MARKER_CONTRACT:?Set MARKER_CONTRACT to a validated marker_pack_contract.json and keep its sibling marker_genes/ and dna_ref.fa files together}"

RESULT_ROOT="${RESULT_ROOT:-$PWD/results/chang2026_read2tree_validated_pack}"
READS_ROOT="${READS_ROOT:-$PWD/results/chang2026_takaoense_pilot}"
PANEL="${PANEL:-$REPO_ROOT/sampling/chang2026_takaoense6_read2tree_panel_v1.csv}"
EVIDENCE="${EVIDENCE:-$REPO_ROOT/data/evidence/chang2026_takaoense_morph_linked_public_samples_v1.csv}"
REFS="${REFS:-$REPO_ROOT/sampling/read2tree_oma_reference_set_v0_2.csv}"
THREADS="${THREADS:-16}"
CHECK_INPUTS="${CHECK_INPUTS:-1}"

CONTRACT="$(cd "$(dirname "$MARKER_CONTRACT")" && pwd)/$(basename "$MARKER_CONTRACT")"
if [[ ! -s "$CONTRACT" ]]; then
  echo "Validated marker contract missing or empty: $CONTRACT" >&2
  exit 2
fi

PLAN_DIR="$RESULT_ROOT/read2tree_plan"
R2T_OUTPUT="$RESULT_ROOT/read2tree_output"
mkdir -p "$RESULT_ROOT/provenance"

python "$REPO_ROOT/analysis/validate_chang2026_takaoense6_read2tree_panel.py" \
  --panel "$PANEL" \
  --evidence "$EVIDENCE"

sha256sum "$CONTRACT" "$PANEL" "$EVIDENCE" "$REFS" \
  > "$RESULT_ROOT/provenance/validated_pack_input_sha256.txt"

plan=(
  python "$REPO_ROOT/analysis/build_chang2026_read2tree_pilot.py"
  --panel "$PANEL"
  --reference-manifest "$REFS"
  --marker-contract "$CONTRACT"
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
Prepared Read2Tree from an already validated marker pack.

Marker contract:
  $CONTRACT
Read2Tree plan:
  $PLAN_DIR/run_read2tree_fast_screen.sh

Next explicit heavy step:
  bash $PLAN_DIR/run_read2tree_fast_screen.sh

After IQ-TREE completes, score with the frozen hypothesis gate:
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
