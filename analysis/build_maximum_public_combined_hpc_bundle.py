#!/usr/bin/env python3
"""Build the dormant post-admission 294–297 common-locus HPC bundle.

The bundle is prepared before heavy execution so the acceptance rule is frozen
in advance, but it cannot be submitted successfully until
``independent_gate_summary.json`` records EA01, EA02 and CNIPG all passing.

BWA and BLASTx are treated as separate baseline mapping modes. Within each mode
all eight subset scenarios are reconstructed on one identical four-way common
locus set. The final sensitivity summary accepts a 297-sample state only when
every candidate/subset/backbone check passes in both modes.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = (
    "baseline294",
    "ea01_295",
    "ea02_295",
    "cnipg_295",
    "ea01_ea02_296",
    "ea01_cnipg_296",
    "ea02_cnipg_296",
    "ea01_ea02_cnipg_297",
)
SCENARIO_CANDIDATES = {
    "ea01_295": ("EA01",),
    "ea02_295": ("EA02",),
    "cnipg_295": ("CNIPG",),
    "ea01_ea02_296": ("EA01", "EA02"),
    "ea01_cnipg_296": ("EA01", "CNIPG"),
    "ea02_cnipg_296": ("EA02", "CNIPG"),
    "ea01_ea02_cnipg_297": ("EA01", "EA02", "CNIPG"),
}


def write(path: Path, text: str, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    path.chmod(mode)


def validate_handoff(handoff: Path) -> tuple[Path, Path, Path]:
    top = json.loads((handoff / "handoff_manifest.json").read_text(encoding="utf-8"))
    if top.get("handoff_version") != "maximum_public_nuclear_hpc_handoff_v1":
        raise ValueError("unexpected maximum-public handoff version")
    if top.get("accepted_primary_before_empirical_candidate_gates") != 294:
        raise ValueError("maximum-public handoff baseline drift")
    if top.get("sample_level_candidate_ceiling") != 297:
        raise ValueError("maximum-public candidate ceiling drift")
    if top.get("combined_296_or_297_tree_built_by_this_handoff") is not False:
        raise ValueError("source handoff unexpectedly claims a combined tree")
    ea = handoff / "ea01_ea02_handoff"
    cn = handoff / "cnipg_bundle"
    base = ea / "baseline_bundle"
    for path in (ea, cn, base):
        if not path.is_dir():
            raise ValueError(f"required component missing: {path}")
    return ea, cn, base


def common() -> str:
    return '''set -euo pipefail
BUNDLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${REPO_ROOT:?Set REPO_ROOT to the EAzami checkout used for the maximum-public run}"
RESULT_ROOT="${RESULT_ROOT:-$PWD/results/japan_origin_global_v2}"
AUGMENT_ROOT="${AUGMENT_ROOT:-$PWD/results/east_asia_public_augmentation}"
MAXIMUM_PUBLIC_ROOT="${MAXIMUM_PUBLIC_ROOT:-$PWD/results/maximum_public_nuclear}"
COMBINED_ROOT="${COMBINED_ROOT:-$MAXIMUM_PUBLIC_ROOT/combined}"
ENV_PREFIX="${ENV_PREFIX:-$REPO_ROOT/.conda/eazami-japan-origin-global}"
export BUNDLE_DIR REPO_ROOT RESULT_ROOT AUGMENT_ROOT MAXIMUM_PUBLIC_ROOT COMBINED_ROOT ENV_PREFIX
if command -v micromamba >/dev/null 2>&1; then
  RUN=(micromamba run -p "$ENV_PREFIX")
elif command -v mamba >/dev/null 2>&1; then
  RUN=(mamba run -p "$ENV_PREFIX")
else
  echo "micromamba or mamba required" >&2; exit 2
fi
mkdir -p "$COMBINED_ROOT"
'''


def prepare_script() -> str:
    return '''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-max-combined-prep
#SBATCH --array=0-1
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --time=04:00:00
''' + common() + '''MODES=(bwa blastx); MODE="${MODES[${SLURM_ARRAY_TASK_ID:?}]}"
PRIMARY="$RESULT_ROOT/tree_$MODE/inputs"
if [[ "$MODE" == "bwa" ]]; then
  EA01="$BUNDLE_DIR/candidate_packs/EA01"
  EA02="$BUNDLE_DIR/candidate_packs/EA02"
else
  EA01="$AUGMENT_ROOT/candidate_mapping/blastx/packs/EA01"
  EA02="$AUGMENT_ROOT/candidate_mapping/blastx/packs/EA02"
fi
CNIPG="$BUNDLE_DIR/candidate_packs/CNIPG"
for p in "$PRIMARY/eligible_loci.txt" "$EA01/strict_recovered_loci.txt" "$EA02/strict_recovered_loci.txt" "$CNIPG/strict_recovered_loci.txt" "$MAXIMUM_PUBLIC_ROOT/independent_gate_summary.json"; do test -s "$p"; done
"${RUN[@]}" python "$BUNDLE_DIR/helpers/prepare_maximum_public_combined_tree_inputs.py" \
  --primary-inputs "$PRIMARY" \
  --baseline-manifest "$BUNDLE_DIR/baseline_sample_manifest.csv" \
  --baseline-species-map "$BUNDLE_DIR/baseline_astral_species_map.csv" \
  --ea01-pack "$EA01" \
  --ea02-pack "$EA02" \
  --cnipg-pack "$CNIPG" \
  --independent-gate-summary "$MAXIMUM_PUBLIC_ROOT/independent_gate_summary.json" \
  --outdir "$COMBINED_ROOT/$MODE/paired_inputs" \
  --minimum-common-loci 100
'''


def align_script() -> str:
    return '''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-max-combined-align
#SBATCH --array=0-1927%32
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=04:00:00
''' + common() + '''MODE="${MODE:?set MODE=bwa or blastx}"; [[ "$MODE" == bwa || "$MODE" == blastx ]]
SCENARIOS=(baseline294 ea01_295 ea02_295 cnipg_295 ea01_ea02_296 ea01_cnipg_296 ea02_cnipg_296 ea01_ea02_cnipg_297)
TASK="${SLURM_ARRAY_TASK_ID:?}"; SIDX=$((TASK / 241)); LIDX=$((TASK % 241)); [[ "$SIDX" -lt 8 ]] || exit 0
S="${SCENARIOS[$SIDX]}"; INPUT="$COMBINED_ROOT/$MODE/paired_inputs/$S"
LOCUS=$(sed -n "$((LIDX+1))p" "$INPUT/eligible_loci.txt" || true); [[ -n "$LOCUS" ]] || exit 0
IN="$INPUT/loci_unaligned/$LOCUS.fasta"; OUT="$COMBINED_ROOT/$MODE/$S/alignments/$LOCUS.aln.fasta"
mkdir -p "$(dirname "$OUT")"; [[ -s "$OUT" ]] && exit 0; test -s "$IN"
"${RUN[@]}" mafft --auto --thread 4 "$IN" > "$OUT"; test -s "$OUT"
'''


def gene_script() -> str:
    return '''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-max-combined-gene
#SBATCH --array=0-1927%24
#SBATCH --cpus-per-task=4
#SBATCH --mem=12G
#SBATCH --time=08:00:00
''' + common() + '''MODE="${MODE:?set MODE=bwa or blastx}"; [[ "$MODE" == bwa || "$MODE" == blastx ]]
SCENARIOS=(baseline294 ea01_295 ea02_295 cnipg_295 ea01_ea02_296 ea01_cnipg_296 ea02_cnipg_296 ea01_ea02_cnipg_297)
TASK="${SLURM_ARRAY_TASK_ID:?}"; SIDX=$((TASK / 241)); LIDX=$((TASK % 241)); [[ "$SIDX" -lt 8 ]] || exit 0
S="${SCENARIOS[$SIDX]}"; INPUT="$COMBINED_ROOT/$MODE/paired_inputs/$S"
LOCUS=$(sed -n "$((LIDX+1))p" "$INPUT/eligible_loci.txt" || true); [[ -n "$LOCUS" ]] || exit 0
ALN="$COMBINED_ROOT/$MODE/$S/alignments/$LOCUS.aln.fasta"; PREFIX="$COMBINED_ROOT/$MODE/$S/gene_trees/$LOCUS"
mkdir -p "$(dirname "$PREFIX")"; [[ -s "$PREFIX.treefile" ]] && exit 0; test -s "$ALN"
"${RUN[@]}" iqtree2 -s "$ALN" -m MFP -B 1000 --alrt 1000 -T 4 -o OUTGROUP_lett,OUTGROUP_sunf --prefix "$PREFIX"; test -s "$PREFIX.treefile"
'''


def concat_script() -> str:
    return '''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-max-combined-concat
#SBATCH --array=0-7
#SBATCH --cpus-per-task=32
#SBATCH --mem=128G
#SBATCH --time=48:00:00
''' + common() + '''MODE="${MODE:?set MODE=bwa or blastx}"; [[ "$MODE" == bwa || "$MODE" == blastx ]]
SCENARIOS=(baseline294 ea01_295 ea02_295 cnipg_295 ea01_ea02_296 ea01_cnipg_296 ea02_cnipg_296 ea01_ea02_cnipg_297)
S="${SCENARIOS[${SLURM_ARRAY_TASK_ID:?}]}"; INPUT="$COMBINED_ROOT/$MODE/paired_inputs/$S"; TREE="$COMBINED_ROOT/$MODE/$S"
mkdir -p "$TREE/concat"
"${RUN[@]}" python "$BUNDLE_DIR/helpers/concatenate_colour_rate_comp1061_alignments.py" \
  --eligible-loci "$INPUT/eligible_loci.txt" --alignment-dir "$TREE/alignments" \
  --primary-runs "$INPUT/primary_runs.csv" --output "$TREE/concat/concat.fasta" \
  --partitions "$TREE/concat/partitions.csv" --summary "$TREE/concat/concat_summary.json"
"${RUN[@]}" iqtree2 -s "$TREE/concat/concat.fasta" -m MFP -B 1000 --alrt 1000 -T AUTO \
  -o OUTGROUP_lett,OUTGROUP_sunf --prefix "$TREE/concat/$S"
test -s "$TREE/concat/$S.treefile"
'''


def astral_script() -> str:
    return '''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-max-combined-astral
#SBATCH --array=0-7
#SBATCH --cpus-per-task=4
#SBATCH --mem=96G
#SBATCH --time=12:00:00
''' + common() + '''MODE="${MODE:?set MODE=bwa or blastx}"; [[ "$MODE" == bwa || "$MODE" == blastx ]]
SCENARIOS=(baseline294 ea01_295 ea02_295 cnipg_295 ea01_ea02_296 ea01_cnipg_296 ea02_cnipg_296 ea01_ea02_cnipg_297)
S="${SCENARIOS[${SLURM_ARRAY_TASK_ID:?}]}"; INPUT="$COMBINED_ROOT/$MODE/paired_inputs/$S"; TREE="$COMBINED_ROOT/$MODE/$S"; OUT="$TREE/astral"
mkdir -p "$OUT"; GT="$OUT/gene_trees.tre"; : > "$GT"
while IFS= read -r LOCUS; do test -s "$TREE/gene_trees/$LOCUS.treefile"; cat "$TREE/gene_trees/$LOCUS.treefile" >> "$GT"; printf '\n' >> "$GT"; done < "$INPUT/eligible_loci.txt"
MAP="$OUT/astral_map_runtime.txt"; cp "$INPUT/astral_map.txt" "$MAP"; if grep -q 'OUTGROUP_saff' "$GT"; then echo 'OUTGROUP_saff:OUTGROUP_saff' >> "$MAP"; fi
"${RUN[@]}" astral -Xmx90G -i "$GT" -a "$MAP" -o "$OUT/$S.astral.tree" 2> "$OUT/astral.log"; test -s "$OUT/$S.astral.tree"
'''


def evaluate_script() -> str:
    lines = [
        "#!/usr/bin/env bash",
        "#SBATCH --job-name=EAzami-max-combined-eval",
        "#SBATCH --cpus-per-task=2",
        "#SBATCH --mem=8G",
        "#SBATCH --time=04:00:00",
        common().rstrip(),
        'MODE="${MODE:?set MODE=bwa or blastx}"; [[ "$MODE" == bwa || "$MODE" == blastx ]]',
        'ROOT="$COMBINED_ROOT/$MODE"; BASE="$ROOT/baseline294/concat/baseline294.treefile"; ABASE="$ROOT/baseline294/astral/baseline294.astral.tree"',
        'test -s "$BASE"; test -s "$ABASE"; mkdir -p "$ROOT/evaluation"',
    ]
    for scenario, candidates in SCENARIO_CANDIDATES.items():
        lines += [
            f'AUG="$ROOT/{scenario}/concat/{scenario}.treefile"',
            f'AAUG="$ROOT/{scenario}/astral/{scenario}.astral.tree"',
            'test -s "$AUG"; test -s "$AAUG"',
        ]
        for cid in candidates:
            contract = "$BUNDLE_DIR/cnipg_gate.json" if cid == "CNIPG" else "$BUNDLE_DIR/ea_gate.json"
            lines.append(
                f'"${{RUN[@]}}" python "$BUNDLE_DIR/helpers/evaluate_east_asia_public_augmentation_tree_pair.py" '
                f'--baseline-tree "$BASE" --augmented-tree "$AUG" --baseline-manifest "$BUNDLE_DIR/baseline_sample_manifest.csv" '
                f'--contract "{contract}" --candidate-id {cid} --output "$ROOT/evaluation/{scenario}_{cid}_concat.json"'
            )
        lines.append(
            f'"${{RUN[@]}}" python "$BUNDLE_DIR/helpers/compare_east_asia_public_augmentation_astral_backbone.py" '
            f'--baseline-tree "$ABASE" --augmented-tree "$AAUG" '
            f'--baseline-species-map "$ROOT/paired_inputs/baseline294/astral_species_map.csv" '
            f'--scenario-id {scenario} --output "$ROOT/evaluation/{scenario}_astral_backbone.json"'
        )
    return "\n".join(lines) + "\n"


def summarize_script() -> str:
    return '''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-max-combined-summary
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=01:00:00
''' + common() + '''for MODE in bwa blastx; do
  test -s "$COMBINED_ROOT/$MODE/paired_inputs/combined_input_summary.json"
  test -s "$COMBINED_ROOT/$MODE/evaluation/ea01_ea02_cnipg_297_astral_backbone.json"
done
"${RUN[@]}" python "$BUNDLE_DIR/helpers/summarize_maximum_public_combined_sensitivities.py" \
  --root "$COMBINED_ROOT" \
  --output "$MAXIMUM_PUBLIC_ROOT/combined_297_sensitivity_summary.json"
'''


def submit_script() -> str:
    return '''#!/usr/bin/env bash
set -euo pipefail
BUNDLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAXIMUM_PUBLIC_ROOT="${MAXIMUM_PUBLIC_ROOT:-$PWD/results/maximum_public_nuclear}"
SUMMARY="$MAXIMUM_PUBLIC_ROOT/independent_gate_summary.json"
test -s "$SUMMARY"
python - "$SUMMARY" <<'PY'
import json,sys
x=json.load(open(sys.argv[1]))
assert x['contract_version']=='maximum_public_nuclear_independent_gate_summary_v1'
assert x['independent_candidate_gate_results']=={'EA01':True,'EA02':True,'CNIPG':True}
assert x['all_three_independent_gates_passed'] is True
assert x['combined_296_or_297_tree_accepted'] is False
assert x['combined_common_paired_locus_tree_required'] is True
assert x['new_china_sampling_freeze_allowed'] is False
PY
submit_mode() {
  local mode="$1" prep aln gene con ast ev
  prep=$(sbatch --parsable --export=ALL,MODE="$mode" "$BUNDLE_DIR/40_prepare_combined_inputs_slurm.sh")
  aln=$(sbatch --parsable --dependency=afterok:"$prep" --export=ALL,MODE="$mode" "$BUNDLE_DIR/41_align_combined_slurm.sh")
  gene=$(sbatch --parsable --dependency=afterok:"$aln" --export=ALL,MODE="$mode" "$BUNDLE_DIR/42_gene_trees_combined_slurm.sh")
  con=$(sbatch --parsable --dependency=afterok:"$aln" --export=ALL,MODE="$mode" "$BUNDLE_DIR/43_concat_combined_slurm.sh")
  ast=$(sbatch --parsable --dependency=afterok:"$gene" --export=ALL,MODE="$mode" "$BUNDLE_DIR/44_astral_combined_slurm.sh")
  ev=$(sbatch --parsable --dependency=afterok:"$con":"$ast" --export=ALL,MODE="$mode" "$BUNDLE_DIR/45_evaluate_combined_slurm.sh")
  printf '%s\n' "$ev"
}
bwa_eval=$(submit_mode bwa)
blastx_eval=$(submit_mode blastx)
final=$(sbatch --parsable --dependency=afterok:"$bwa_eval":"$blastx_eval" --export=ALL "$BUNDLE_DIR/46_summarize_combined_slurm.sh")
printf 'combined_bwa_evaluate=%s\ncombined_blastx_evaluate=%s\ncombined_cross_mapping_summary=%s\n' "$bwa_eval" "$blastx_eval" "$final"
'''


def build(maximum_handoff: Path, outdir: Path) -> dict[str, object]:
    ea, cn, base = validate_handoff(maximum_handoff)
    if outdir.exists():
        shutil.rmtree(outdir)
    outdir.mkdir(parents=True)

    shutil.copy2(base / "env.yml", outdir / "env.yml")
    shutil.copy2(base / "sample_manifest.csv", outdir / "baseline_sample_manifest.csv")
    shutil.copy2(base / "astral_species_map.csv", outdir / "baseline_astral_species_map.csv")
    shutil.copy2(ROOT / "data/evidence/east_asia_public_tree_augmentation_contract_v1.json", outdir / "ea_gate.json")
    shutil.copy2(ROOT / "data/evidence/cirsium_nipponicum_public_genome_augmentation_gate_v1.json", outdir / "cnipg_gate.json")

    packs = outdir / "candidate_packs"
    shutil.copytree(ea / "augmentation_bundle/candidate_packs/EA01", packs / "EA01")
    shutil.copytree(ea / "augmentation_bundle/candidate_packs/EA02", packs / "EA02")
    shutil.copytree(cn / "genome_pack", packs / "CNIPG")

    helpers = (
        "prepare_maximum_public_combined_tree_inputs.py",
        "prepare_east_asia_public_augmentation_tree_inputs.py",
        "evaluate_east_asia_public_augmentation_tree_pair.py",
        "compare_east_asia_public_augmentation_astral_backbone.py",
        "concatenate_colour_rate_comp1061_alignments.py",
        "summarize_maximum_public_combined_sensitivities.py",
    )
    (outdir / "helpers").mkdir()
    for name in helpers:
        shutil.copy2(ROOT / "analysis" / name, outdir / "helpers" / name)

    scripts = {
        "40_prepare_combined_inputs_slurm.sh": prepare_script(),
        "41_align_combined_slurm.sh": align_script(),
        "42_gene_trees_combined_slurm.sh": gene_script(),
        "43_concat_combined_slurm.sh": concat_script(),
        "44_astral_combined_slurm.sh": astral_script(),
        "45_evaluate_combined_slurm.sh": evaluate_script(),
        "46_summarize_combined_slurm.sh": summarize_script(),
        "submit_combined_after_independent_pass.sh": submit_script(),
    }
    for name, text in scripts.items():
        write(outdir / name, text, 0o755)

    manifest: dict[str, object] = {
        "bundle_version": "maximum_public_combined_hpc_bundle_v1",
        "prerequisite_independent_gate_contract": "maximum_public_nuclear_independent_gate_summary_v1",
        "independent_candidates_required_to_pass": ["EA01", "EA02", "CNIPG"],
        "baseline_focal_tips": 294,
        "scenario_count": 8,
        "scenarios": list(SCENARIOS),
        "final_scenario": "ea01_ea02_cnipg_297",
        "mapping_modes": ["bwa", "blastx"],
        "minimum_four_way_common_loci": 100,
        "all_scenarios_same_locus_set_within_mode": True,
        "bwa_candidate_packs_frozen_in_bundle": True,
        "blastx_ea01_ea02_packs_from_independent_heavy_run": True,
        "cnipg_pack_fixed_across_mapping_modes": True,
        "combined_297_acceptance_pre_authorized": False,
        "final_acceptance_contract": "maximum_public_combined_sensitivity_summary_v1",
        "new_analysis_taxon_labels_added": 0,
        "new_china_sampling_freeze_allowed": False,
        "heavy_compute_executed_by_builder": False,
    }
    write(outdir / "execution_manifest.json", json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--maximum-handoff", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    build(args.maximum_handoff, args.outdir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
