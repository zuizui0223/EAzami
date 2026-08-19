#!/usr/bin/env python3
"""Build the post-empirical EA01-only paired-tree augmentation bundle."""
from __future__ import annotations

import argparse
import csv
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ("baseline294", "ea01_295")


def write(path: Path, text: str, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    path.chmod(mode)


def validate_baseline(bundle: Path) -> dict[str, object]:
    manifest = json.loads((bundle / "execution_manifest.json").read_text(encoding="utf-8"))
    if manifest.get("bundle_version") != "japan_origin_global_hpc_bundle_v2":
        raise ValueError("baseline bundle version drift")
    if manifest.get("biological_samples") != 294 or manifest.get("public_runs") != 295:
        raise ValueError("baseline bundle is not frozen 294-tip/295-SRR v2")
    with (bundle / "sample_manifest.csv").open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 294 or len({row["tip_id"] for row in rows}) != 294:
        raise ValueError("baseline sample manifest drift")
    if not (bundle / "astral_species_map.csv").is_file():
        raise ValueError("baseline ASTRAL species map missing")
    return manifest


def validate_pack(pack: Path) -> dict[str, object]:
    summary = json.loads((pack / "candidate_pack_summary.json").read_text(encoding="utf-8"))
    if summary.get("candidate_id") != "EA01" or summary.get("tip_id") != "PUBEA001":
        raise ValueError("EA01 pack identity drift")
    if summary.get("strict_no_warning_recovered_loci") != 236:
        raise ValueError("EA01 strict-locus count drift")
    if summary.get("pilot_locus_pack_ready") is not True or summary.get("tree_tip_promotion_allowed") is not False:
        raise ValueError("EA01 pack is not at the frozen pre-tree state")
    if len(list((pack / "loci").glob("*.fasta"))) != 236:
        raise ValueError("EA01 FASTA count drift")
    return summary


def common() -> str:
    return r'''set -euo pipefail
BUNDLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${REPO_ROOT:-$(cd "$BUNDLE_DIR/../.." && pwd)}"
BASELINE_RESULT_ROOT="${BASELINE_RESULT_ROOT:-$PWD/results/japan_origin_global_v2}"
AUGMENT_ROOT="${AUGMENT_ROOT:-$PWD/results/ea01_public_augmentation}"
ENV_PREFIX="${ENV_PREFIX:-$REPO_ROOT/.conda/eazami-japan-origin-global}"
export BUNDLE_DIR REPO_ROOT BASELINE_RESULT_ROOT AUGMENT_ROOT ENV_PREFIX
if command -v micromamba >/dev/null 2>&1; then
  if [[ ! -x "$ENV_PREFIX/bin/python" ]]; then micromamba create -y -p "$ENV_PREFIX" -f "$BUNDLE_DIR/env.yml"; fi
  RUN=(micromamba run -p "$ENV_PREFIX")
elif command -v mamba >/dev/null 2>&1; then
  if [[ ! -x "$ENV_PREFIX/bin/python" ]]; then mamba env create -y -p "$ENV_PREFIX" -f "$BUNDLE_DIR/env.yml"; fi
  RUN=(mamba run -p "$ENV_PREFIX")
else
  echo "micromamba or mamba required" >&2
  exit 2
fi
mkdir -p "$AUGMENT_ROOT"
'''


def prepare_script() -> str:
    return '''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-ea01-prep
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=02:00:00
''' + common() + r'''MODE="${MODE:-bwa}"
PRIMARY="$BASELINE_RESULT_ROOT/tree_$MODE/inputs"
test -s "$PRIMARY/eligible_loci.txt"
"${RUN[@]}" python "$BUNDLE_DIR/helpers/prepare_ea01_public_augmentation_tree_inputs.py" \
  --primary-inputs "$PRIMARY" \
  --baseline-manifest "$BUNDLE_DIR/baseline_sample_manifest.csv" \
  --baseline-species-map "$BUNDLE_DIR/baseline_astral_species_map.csv" \
  --ea01-pack "$BUNDLE_DIR/candidate_packs/EA01" \
  --contract "$BUNDLE_DIR/ea01_contract.json" \
  --outdir "$AUGMENT_ROOT/$MODE/paired_inputs"
'''


def align_script() -> str:
    return '''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-ea01-align
#SBATCH --array=0-481%24
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=04:00:00
''' + common() + r'''MODE="${MODE:-bwa}"
TASK="${SLURM_ARRAY_TASK_ID:?}"
SIDX=$((TASK / 241)); LIDX=$((TASK % 241)); SCENARIOS=(baseline294 ea01_295)
[[ "$SIDX" -lt 2 ]] || exit 0
S="${SCENARIOS[$SIDX]}"; INPUT="$AUGMENT_ROOT/$MODE/paired_inputs/$S"
LOCUS=$(sed -n "$((LIDX+1))p" "$INPUT/eligible_loci.txt" || true); [[ -n "$LOCUS" ]] || exit 0
IN="$INPUT/loci_unaligned/$LOCUS.fasta"; OUT="$AUGMENT_ROOT/$MODE/$S/alignments/$LOCUS.aln.fasta"
mkdir -p "$(dirname "$OUT")"; [[ -s "$OUT" ]] && exit 0; test -s "$IN"
"${RUN[@]}" mafft --auto --thread 4 "$IN" > "$OUT"; test -s "$OUT"
'''


def gene_script() -> str:
    return '''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-ea01-gene
#SBATCH --array=0-481%20
#SBATCH --cpus-per-task=4
#SBATCH --mem=12G
#SBATCH --time=08:00:00
''' + common() + r'''MODE="${MODE:-bwa}"
TASK="${SLURM_ARRAY_TASK_ID:?}"; SIDX=$((TASK / 241)); LIDX=$((TASK % 241)); SCENARIOS=(baseline294 ea01_295)
[[ "$SIDX" -lt 2 ]] || exit 0; S="${SCENARIOS[$SIDX]}"; INPUT="$AUGMENT_ROOT/$MODE/paired_inputs/$S"
LOCUS=$(sed -n "$((LIDX+1))p" "$INPUT/eligible_loci.txt" || true); [[ -n "$LOCUS" ]] || exit 0
ALN="$AUGMENT_ROOT/$MODE/$S/alignments/$LOCUS.aln.fasta"; PREFIX="$AUGMENT_ROOT/$MODE/$S/gene_trees/$LOCUS"
mkdir -p "$(dirname "$PREFIX")"; [[ -s "$PREFIX.treefile" ]] && exit 0; test -s "$ALN"
IQTREE=$("${RUN[@]}" bash -lc 'command -v iqtree2 || command -v iqtree || command -v iqtree3')
"${RUN[@]}" "$IQTREE" -s "$ALN" -m MFP -B 1000 --alrt 1000 -T 4 -o OUTGROUP_lett,OUTGROUP_sunf --prefix "$PREFIX"
test -s "$PREFIX.treefile"
'''


def concat_script() -> str:
    return '''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-ea01-concat
#SBATCH --array=0-1
#SBATCH --cpus-per-task=32
#SBATCH --mem=128G
#SBATCH --time=48:00:00
''' + common() + r'''MODE="${MODE:-bwa}"; SCENARIOS=(baseline294 ea01_295); S="${SCENARIOS[${SLURM_ARRAY_TASK_ID:?}]}"
INPUT="$AUGMENT_ROOT/$MODE/paired_inputs/$S"; TREE="$AUGMENT_ROOT/$MODE/$S"; mkdir -p "$TREE/concat"
"${RUN[@]}" python "$BUNDLE_DIR/helpers/concatenate_colour_rate_comp1061_alignments.py" \
  --eligible-loci "$INPUT/eligible_loci.txt" --alignment-dir "$TREE/alignments" \
  --primary-runs "$INPUT/primary_runs.csv" --output "$TREE/concat/concat.fasta" \
  --partitions "$TREE/concat/partitions.csv" --summary "$TREE/concat/concat_summary.json"
IQTREE=$("${RUN[@]}" bash -lc 'command -v iqtree2 || command -v iqtree || command -v iqtree3')
"${RUN[@]}" "$IQTREE" -s "$TREE/concat/concat.fasta" -m MFP -B 1000 --alrt 1000 -T AUTO \
  -o OUTGROUP_lett,OUTGROUP_sunf --prefix "$TREE/concat/$S"
test -s "$TREE/concat/$S.treefile"
'''


def astral_script() -> str:
    return '''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-ea01-astral
#SBATCH --array=0-1
#SBATCH --cpus-per-task=4
#SBATCH --mem=96G
#SBATCH --time=12:00:00
''' + common() + r'''MODE="${MODE:-bwa}"; SCENARIOS=(baseline294 ea01_295); S="${SCENARIOS[${SLURM_ARRAY_TASK_ID:?}]}"
INPUT="$AUGMENT_ROOT/$MODE/paired_inputs/$S"; TREE="$AUGMENT_ROOT/$MODE/$S"; OUT="$TREE/astral"; mkdir -p "$OUT"
GT="$OUT/gene_trees.tre"; : > "$GT"
while IFS= read -r LOCUS; do test -s "$TREE/gene_trees/$LOCUS.treefile"; cat "$TREE/gene_trees/$LOCUS.treefile" >> "$GT"; printf '\n' >> "$GT"; done < "$INPUT/eligible_loci.txt"
MAP="$OUT/astral_map_runtime.txt"; cp "$INPUT/astral_map.txt" "$MAP"
if grep -q 'OUTGROUP_saff' "$GT"; then echo 'OUTGROUP_saff:OUTGROUP_saff' >> "$MAP"; fi
"${RUN[@]}" astral -Xmx90G -i "$GT" -a "$MAP" -o "$OUT/$S.astral.tree" 2> "$OUT/astral.log"
test -s "$OUT/$S.astral.tree"
'''


def evaluate_script() -> str:
    return '''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-ea01-eval
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=02:00:00
''' + common() + r'''MODE="${MODE:-bwa}"; ROOT="$AUGMENT_ROOT/$MODE"; mkdir -p "$ROOT/evaluation"
BASE="$ROOT/baseline294/concat/baseline294.treefile"; AUG="$ROOT/ea01_295/concat/ea01_295.treefile"; test -s "$BASE"; test -s "$AUG"
"${RUN[@]}" python "$BUNDLE_DIR/helpers/evaluate_east_asia_public_augmentation_tree_pair.py" \
  --baseline-tree "$BASE" --augmented-tree "$AUG" \
  --baseline-manifest "$BUNDLE_DIR/baseline_sample_manifest.csv" \
  --contract "$BUNDLE_DIR/pair_evaluator_contract.json" --candidate-id EA01 \
  --output "$ROOT/evaluation/ea01_295_EA01_concat.json"
ABASE="$ROOT/baseline294/astral/baseline294.astral.tree"; AAUG="$ROOT/ea01_295/astral/ea01_295.astral.tree"; test -s "$ABASE"; test -s "$AAUG"
"${RUN[@]}" python "$BUNDLE_DIR/helpers/compare_east_asia_public_augmentation_astral_backbone.py" \
  --baseline-tree "$ABASE" --augmented-tree "$AAUG" \
  --baseline-species-map "$ROOT/paired_inputs/baseline294/astral_species_map.csv" \
  --scenario-id ea01_295 --output "$ROOT/evaluation/ea01_295_astral_backbone.json"
'''


def summarize_script() -> str:
    return '''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-ea01-summary
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=01:00:00
''' + common() + r'''for MODE in bwa blastx; do test -s "$AUGMENT_ROOT/$MODE/paired_inputs/paired_augmentation_summary.json"; test -d "$AUGMENT_ROOT/$MODE/evaluation"; done
"${RUN[@]}" python "$BUNDLE_DIR/helpers/summarize_ea01_public_augmentation_sensitivities.py" \
  --bwa-paired-summary "$AUGMENT_ROOT/bwa/paired_inputs/paired_augmentation_summary.json" \
  --blastx-paired-summary "$AUGMENT_ROOT/blastx/paired_inputs/paired_augmentation_summary.json" \
  --bwa-evaluation "$AUGMENT_ROOT/bwa/evaluation" --blastx-evaluation "$AUGMENT_ROOT/blastx/evaluation" \
  --output "$AUGMENT_ROOT/cross_mapping_sensitivity_summary.json"
'''


def submit_script() -> str:
    return r'''#!/usr/bin/env bash
set -euo pipefail
MODE="${MODE:-bwa}"
prep=$(sbatch --parsable --export=ALL,MODE="$MODE" 10_prepare_paired_inputs_slurm.sh)
aln=$(sbatch --parsable --dependency=afterok:$prep --export=ALL,MODE="$MODE" 11_align_paired_scenarios_slurm.sh)
gene=$(sbatch --parsable --dependency=afterok:$aln --export=ALL,MODE="$MODE" 12_gene_trees_paired_scenarios_slurm.sh)
con=$(sbatch --parsable --dependency=afterok:$aln --export=ALL,MODE="$MODE" 13_concat_paired_scenarios_slurm.sh)
ast=$(sbatch --parsable --dependency=afterok:$gene --export=ALL,MODE="$MODE" 14_astral_paired_scenarios_slurm.sh)
ev=$(sbatch --parsable --dependency=afterok:$con:$ast --export=ALL,MODE="$MODE" 15_evaluate_paired_scenarios_slurm.sh)
printf 'prepare=%s\nalign=%s\ngene=%s\nconcat=%s\nastral=%s\nevaluate=%s\n' "$prep" "$aln" "$gene" "$con" "$ast" "$ev"
'''


def build(*, baseline_bundle: Path, ea01_pack: Path, contract: Path, evaluator_contract: Path, outdir: Path) -> dict[str, object]:
    baseline = validate_baseline(baseline_bundle)
    candidate = validate_pack(ea01_pack)
    c = json.loads(contract.read_text(encoding="utf-8"))
    if c.get("contract_version") != "ea01_public_tree_augmentation_v2":
        raise ValueError("wrong EA01 post-empirical contract")
    old = json.loads(evaluator_contract.read_text(encoding="utf-8"))
    if old.get("contract_version") != "east_asia_public_tree_augmentation_v1":
        raise ValueError("wrong pair evaluator contract")

    if outdir.exists():
        shutil.rmtree(outdir)
    outdir.mkdir(parents=True)
    shutil.copy2(baseline_bundle / "env.yml", outdir / "env.yml")
    shutil.copy2(baseline_bundle / "sample_manifest.csv", outdir / "baseline_sample_manifest.csv")
    shutil.copy2(baseline_bundle / "astral_species_map.csv", outdir / "baseline_astral_species_map.csv")
    shutil.copy2(contract, outdir / "ea01_contract.json")
    shutil.copy2(evaluator_contract, outdir / "pair_evaluator_contract.json")

    dst = outdir / "candidate_packs/EA01"
    dst.mkdir(parents=True)
    for name in ("candidate_pack_summary.json", "strict_recovered_loci.txt"):
        shutil.copy2(ea01_pack / name, dst / name)
    shutil.copytree(ea01_pack / "loci", dst / "loci")

    helpers = (
        "prepare_ea01_public_augmentation_tree_inputs.py",
        "evaluate_east_asia_public_augmentation_tree_pair.py",
        "compare_east_asia_public_augmentation_astral_backbone.py",
        "summarize_ea01_public_augmentation_sensitivities.py",
        "concatenate_colour_rate_comp1061_alignments.py",
    )
    (outdir / "helpers").mkdir()
    for name in helpers:
        shutil.copy2(ROOT / "analysis" / name, outdir / "helpers" / name)

    scripts = {
        "10_prepare_paired_inputs_slurm.sh": prepare_script(),
        "11_align_paired_scenarios_slurm.sh": align_script(),
        "12_gene_trees_paired_scenarios_slurm.sh": gene_script(),
        "13_concat_paired_scenarios_slurm.sh": concat_script(),
        "14_astral_paired_scenarios_slurm.sh": astral_script(),
        "15_evaluate_paired_scenarios_slurm.sh": evaluate_script(),
        "16_summarize_cross_mapping_sensitivities_slurm.sh": summarize_script(),
        "submit_paired_augmentation_chain.sh": submit_script(),
    }
    for name, text in scripts.items():
        write(outdir / name, text, 0o755)

    manifest: dict[str, object] = {
        "bundle_version": "ea01_public_augmentation_hpc_bundle_v2",
        "baseline_bundle_version": baseline["bundle_version"],
        "baseline_focal_tips": 294,
        "candidate_id": "EA01",
        "candidate_tip_id": candidate["tip_id"],
        "candidate_strict_loci_bwa": 236,
        "scenarios": list(SCENARIOS),
        "scenario_focal_tip_counts": {"baseline294": 294, "ea01_295": 295},
        "mapping_modes": ["bwa", "blastx"],
        "same_locus_set_within_mapping_mode": True,
        "ea02_enters_biological_tree_inputs": False,
        "tree_tip_promotion_allowed": False,
        "new_analysis_taxon_labels_added": 0,
        "new_china_sampling_freeze_allowed": False,
    }
    write(outdir / "execution_manifest.json", json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-bundle", type=Path, required=True)
    parser.add_argument("--ea01-pack", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--evaluator-contract", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    build(
        baseline_bundle=args.baseline_bundle,
        ea01_pack=args.ea01_pack,
        contract=args.contract,
        evaluator_contract=args.evaluator_contract,
        outdir=args.outdir,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
