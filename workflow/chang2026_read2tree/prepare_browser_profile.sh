#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

: "${OMA_BROWSER_ARCHIVE:?Set OMA_BROWSER_ARCHIVE to the downloaded OMA Browser 3-species/400-marker tarball}"
: "${OMA_BROWSER_EXPORT_DATE:?Set OMA_BROWSER_EXPORT_DATE to the YYYY-MM-DD date on which the Browser export was downloaded}"

RESULT_ROOT="${RESULT_ROOT:-$PWD/results/chang2026_read2tree_browser400}"
READS_ROOT="${READS_ROOT:-$PWD/results/chang2026_takaoense_pilot}"
PANEL="${PANEL:-$REPO_ROOT/sampling/chang2026_takaoense6_read2tree_panel_v1.csv}"
EVIDENCE="${EVIDENCE:-$REPO_ROOT/data/evidence/chang2026_takaoense_morph_linked_public_samples_v1.csv}"
REFS="${REFS:-$REPO_ROOT/sampling/read2tree_oma_reference_set_v0_2.csv}"
THREADS="${THREADS:-16}"
CHECK_INPUTS="${CHECK_INPUTS:-1}"
OMA_BROWSER_EXPORT_URL="${OMA_BROWSER_EXPORT_URL:-oma-browser-marker-export:oma_browser_export400_may2026_v1}"

ARCHIVE="$(cd "$(dirname "$OMA_BROWSER_ARCHIVE")" && pwd)/$(basename "$OMA_BROWSER_ARCHIVE")"
if [[ ! -s "$ARCHIVE" ]]; then
  echo "OMA Browser archive missing or empty: $ARCHIVE" >&2
  exit 2
fi
if [[ ! "$OMA_BROWSER_EXPORT_DATE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
  echo "OMA_BROWSER_EXPORT_DATE must be YYYY-MM-DD" >&2
  exit 2
fi

VALIDATED_DIR="$RESULT_ROOT/validated_marker_pack"
PLAN_DIR="$RESULT_ROOT/read2tree_plan"
R2T_OUTPUT="$RESULT_ROOT/read2tree_output"
mkdir -p "$RESULT_ROOT/provenance"

# Revalidate the scientific input before accepting an external Browser archive.
python "$REPO_ROOT/analysis/validate_chang2026_takaoense6_read2tree_panel.py" \
  --panel "$PANEL" \
  --evidence "$EVIDENCE"

sha256sum "$ARCHIVE" "$PANEL" "$EVIDENCE" "$REFS" \
  > "$RESULT_ROOT/provenance/browser400_input_sha256.txt"

# The archive is not trusted by filename or UI description. The validator must
# observe exactly 400 paired AA/DNA markers and exactly one CYNCS, HELAN and
# DAUCS sequence in every marker before execution is allowed.
python "$REPO_ROOT/analysis/validate_read2tree_oma_marker_pack.py" \
  --archive "$ARCHIVE" \
  --reference-manifest "$REFS" \
  --outdir "$VALIDATED_DIR" \
  --oma-release May2026 \
  --export-date "$OMA_BROWSER_EXPORT_DATE" \
  --export-url "$OMA_BROWSER_EXPORT_URL" \
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
Validated OMA Browser400 profile and generated the Read2Tree plan.

External archive:
  $ARCHIVE
Validated marker contract:
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
    --expected-hypothesis-sha256 5dbd081b5c360f73d824221f2dbc09892666f23ecc74a706620943f4c881692f \
    --nearest $REPO_ROOT/analysis/chang2026_takaoense_nearest_no_regain_topologies.csv \
    --robustness-summary $REPO_ROOT/analysis/chang2026_takaoense_topology_robustness_summary.json \
    --scorer $REPO_ROOT/analysis/score_chang2026_read2tree_topology.py \
    --thresholds 0,50,70,90 \
    --output $RESULT_ROOT/read2tree_topology_scores.csv \
    --hypothesis-output $RESULT_ROOT/read2tree_per_hypothesis_scores.csv \
    --summary-json $RESULT_ROOT/read2tree_topology_summary.json
EOF
