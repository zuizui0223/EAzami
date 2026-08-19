#!/usr/bin/env python3
"""Build the paired 294-vs-295 Ulleung genome augmentation Slurm bundle."""
from __future__ import annotations

import argparse
import csv
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ("baseline294", "cnipg_295")
MANDATORY_GENOME_PACK_FILES = (
    "cirsium_nipponicum_comp1061_locus_pack_summary.json",
    "strict_recovered_loci.txt",
)
OPTIONAL_GENOME_PACK_DIAGNOSTICS = (
    "cirsium_nipponicum_comp1061_locus_audit.csv",
    "durable_materialization.json",
)


def write(path: Path, text: str, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    path.chmod(mode)


def validate_baseline(bundle: Path) -> None:
    manifest = json.loads((bundle / "execution_manifest.json").read_text(encoding="utf-8"))
    if manifest.get("bundle_version") != "japan_origin_global_hpc_bundle_v2":
        raise ValueError("baseline bundle is not Japan-origin global HPC v2")
    if manifest.get("biological_samples") != 294 or manifest.get("public_runs") != 295:
        raise ValueError("baseline bundle inventory drift")
    with (bundle / "sample_manifest.csv").open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 294 or len({row["tip_id"] for row in rows}) != 294:
        raise ValueError("baseline sample manifest drift")
    if not any(row["analysis_taxon_label"] == "Cirsium nipponicum" for row in rows):
        raise ValueError("baseline exact Cirsium nipponicum taxon representation is missing")
    if not (bundle / "astral_species_map.csv").is_file():
        raise ValueError("baseline ASTRAL species map missing")


def validate_genome_pack(pack: Path, gate: dict[str, object]) -> dict[str, object]:
    summary = json.loads((pack / "cirsium_nipponicum_comp1061_locus_pack_summary.json").read_text(encoding="utf-8"))
    candidate = gate["candidates"][0]  # type: ignore[index]
    expected = int(candidate["strict_no_warning_recovered_loci"])  # type: ignore[index]
    if summary.get("contract_version") != "cirsium_nipponicum_comp1061_locus_pack_v1":
        raise ValueError("unexpected genome locus-pack version")
    if summary.get("tip_id") != "AUG_ULLEUNG_CNIP2024":
        raise ValueError("unexpected genome augmentation tip")
    if int(summary.get("strict_recovered_loci", -1)) != expected:
        raise ValueError("genome strict-locus count differs from frozen gate")
    if not summary.get("augmentation_locus_pack_ready") or summary.get("tree_tip_promotion_allowed"):
        raise ValueError("genome locus pack did not stop at the correct pre-tree gate")
    loci = [x for x in (pack / "strict_recovered_loci.txt").read_text(encoding="utf-8").splitlines() if x]
    if len(loci) != expected or len(loci) != len(set(loci)):
        raise ValueError("genome strict-locus list drift")
    if len(list((pack / "loci").glob("*.fasta"))) != expected:
        raise ValueError("genome locus FASTA pack is incomplete")
    return summary


def common() -> str:
    return '''set -euo pipefail
BUNDLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${REPO_ROOT:-$(cd "$BUNDLE_DIR/../.." && pwd)}"
BASELINE_RESULT_ROOT="${BASELINE_RESULT_ROOT:-$PWD/results/japan_origin_global_v2}"
GENOME_AUGMENT_ROOT="${GENOME_AUGMENT_ROOT:-$PWD/results/cnipponicum_genome_augmentation}"
ENV_PREFIX="${ENV_PREFIX:-$REPO_ROOT/.conda/eazami-japan-origin-global}"
export BUNDLE_DIR REPO_ROOT BASELINE_RESULT_ROOT GENOME_AUGMENT_ROOT ENV_PREFIX
if command -v micromamba >/dev/null 2>&1; then
  if [[ ! -x "$ENV_PREFIX/bin/python" ]]; then micromamba create -y -p "$ENV_PREFIX" -f "$BUNDLE_DIR/env.yml"; fi
  RUN=(micromamba run -p "$ENV_PREFIX")
elif command -v mamba >/dev/null 2>&1; then
  if [[ ! -x "$ENV_PREFIX/bin/python" ]]; then mamba env create -y -p "$ENV_PREFIX" -f "$BUNDLE_DIR/env.yml"; fi
  RUN=(mamba run -p "$ENV_PREFIX")
else echo "micromamba or mamba required" >&2; exit 2; fi
mkdir -p "$GENOME_AUGMENT_ROOT"
'''


def prep() -> str:
    return '''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-cnipg-prep
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=02:00:00
''' + common() + '''MODE="${MODE:-bwa}"
[[ "$MODE" == "bwa" || "$MODE" == "blastx" ]]
PRIMARY="$BASELINE_RESULT_ROOT/tree_$MODE/inputs"
test -s "$PRIMARY/eligible_loci.txt"
"${RUN[@]}" python "$BUNDLE_DIR/helpers/prepare_cirsium_nipponicum_augmentation_tree_inputs.py" \
  --primary-inputs "$PRIMARY" \
  --augmentation-pack "$BUNDLE_DIR/genome_pack" \
  --baseline-manifest "$BUNDLE_DIR/baseline_sample_manifest.csv" \
  --baseline-species-map "$BUNDLE_DIR/baseline_astral_species_map.csv" \
  --minimum-overlap 100 \
  --outdir "$GENOME_AUGMENT_ROOT/$MODE/paired_inputs"
'''


def align() -> str:
    return '''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-cnipg-align
#SBATCH --array=0-481%24
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=04:00:00
''' + common() + '''MODE="${MODE:-bwa}"; TASK="${SLURM_ARRAY_TASK_ID:?}"; SIDX=$((TASK / 241)); LIDX=$((TASK % 241)); SCENARIOS=(baseline294 augmented295); [[ "$SIDX" -lt 2 ]] || exit 0; S="${SCENARIOS[$SIDX]}"; INPUT="$GENOME_AUGMENT_ROOT/$MODE/paired_inputs/$S"; LOCUS=$(sed -n "$((LIDX+1))p" "$INPUT/eligible_loci.txt" || true); [[ -n "$LOCUS" ]] || exit 0; IN="$INPUT/loci_unaligned/$LOCUS.fasta"; OUT="$GENOME_AUGMENT_ROOT/$MODE/$S/alignments/$LOCUS.aln.fasta"; mkdir -p "$(dirname "$OUT")"; [[ -s "$OUT" ]] && exit 0; test -s "$IN"; "${RUN[@]}" mafft --auto --thread 4 "$IN" > "$OUT"; test -s "$OUT"
'''


def gene() -> str:
    return '''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-cnipg-gene
#SBATCH --array=0-481%20
#SBATCH --cpus-per-task=4
#SBATCH --mem=12G
#SBATCH --time=08:00:00
''' + common() + '''MODE="${MODE:-bwa}"; TASK="${SLURM_ARRAY_TASK_ID:?}"; SIDX=$((TASK / 241)); LIDX=$((TASK % 241)); SCENARIOS=(baseline294 augmented295); [[ "$SIDX" -lt 2 ]] || exit 0; S="${SCENARIOS[$SIDX]}"; INPUT="$GENOME_AUGMENT_ROOT/$MODE/paired_inputs/$S"; LOCUS=$(sed -n "$((LIDX+1))p" "$INPUT/eligible_loci.txt" || true); [[ -n "$LOCUS" ]] || exit 0; ALN="$GENOME_AUGMENT_ROOT/$MODE/$S/alignments/$LOCUS.aln.fasta"; PREFIX="$GENOME_AUGMENT_ROOT/$MODE/$S/gene_trees/$LOCUS"; mkdir -p "$(dirname "$PREFIX")"; [[ -s "$PREFIX.treefile" ]] && exit 0; test -s "$ALN"; "${RUN[@]}" iqtree2 -s "$ALN" -m MFP -B 1000 --alrt 1000 -T 4 -o OUTGROUP_lett,OUTGROUP_sunf --prefix "$PREFIX"; test -s "$PREFIX.treefile"
'''


def concat() -> str:
    return '''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-cnipg-concat
#SBATCH --array=0-1
#SBATCH --cpus-per-task=32
#SBATCH --mem=128G
#SBATCH --time=48:00:00
''' + common() + '''MODE="${MODE:-bwa}"; SCENARIOS=(baseline294 augmented295); S="${SCENARIOS[${SLURM_ARRAY_TASK_ID:?}]}"; INPUT="$GENOME_AUGMENT_ROOT/$MODE/paired_inputs/$S"; TREE="$GENOME_AUGMENT_ROOT/$MODE/$S"; mkdir -p "$TREE/concat"; "${RUN[@]}" python "$BUNDLE_DIR/helpers/concatenate_colour_rate_comp1061_alignments.py" --eligible-loci "$INPUT/eligible_loci.txt" --alignment-dir "$TREE/alignments" --primary-runs "$INPUT/primary_runs.csv" --output "$TREE/concat/concat.fasta" --partitions "$TREE/concat/partitions.csv" --summary "$TREE/concat/concat_summary.json"; "${RUN[@]}" iqtree2 -s "$TREE/concat/concat.fasta" -m MFP -B 1000 --alrt 1000 -T AUTO -o OUTGROUP_lett,OUTGROUP_sunf --prefix "$TREE/concat/$S"; test -s "$TREE/concat/$S.treefile"
'''


def astral() -> str:
    return '''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-cnipg-astral
#SBATCH --array=0-1
#SBATCH --cpus-per-task=4
#SBATCH --mem=96G
#SBATCH --time=12:00:00
''' + common() + '''MODE="${MODE:-bwa}"; SCENARIOS=(baseline294 augmented295); S="${SCENARIOS[${SLURM_ARRAY_TASK_ID:?}]}"; INPUT="$GENOME_AUGMENT_ROOT/$MODE/paired_inputs/$S"; TREE="$GENOME_AUGMENT_ROOT/$MODE/$S"; OUT="$TREE/astral"; mkdir -p "$OUT"; GT="$OUT/gene_trees.tre"; : > "$GT"; while IFS= read -r LOCUS; do test -s "$TREE/gene_trees/$LOCUS.treefile"; cat "$TREE/gene_trees/$LOCUS.treefile" >> "$GT"; printf '\n' >> "$GT"; done < "$INPUT/eligible_loci.txt"; MAP="$OUT/astral_map_runtime.txt"; cp "$INPUT/astral_map.txt" "$MAP"; if grep -q 'OUTGROUP_saff' "$GT"; then echo 'OUTGROUP_saff:OUTGROUP_saff' >> "$MAP"; fi; "${RUN[@]}" astral -Xmx90G -i "$GT" -a "$MAP" -o "$OUT/$S.astral.tree" 2> "$OUT/astral.log"; test -s "$OUT/$S.astral.tree"
'''


def evaluate() -> str:
    return '''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-cnipg-eval
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=02:00:00
''' + common() + '''MODE="${MODE:-bwa}"; ROOT="$GENOME_AUGMENT_ROOT/$MODE"; BASE="$ROOT/baseline294/concat/baseline294.treefile"; AUG="$ROOT/augmented295/concat/augmented295.treefile"; test -s "$BASE"; test -s "$AUG"; mkdir -p "$ROOT/evaluation"; "${RUN[@]}" python "$BUNDLE_DIR/helpers/evaluate_east_asia_public_augmentation_tree_pair.py" --baseline-tree "$BASE" --augmented-tree "$AUG" --baseline-manifest "$BUNDLE_DIR/baseline_sample_manifest.csv" --contract "$BUNDLE_DIR/augmentation_gate.json" --candidate-id CNIPG --output "$ROOT/evaluation/cnipg_295_CNIPG_concat.json"; ABASE="$ROOT/baseline294/astral/baseline294.astral.tree"; AAUG="$ROOT/augmented295/astral/augmented295.astral.tree"; test -s "$ABASE"; test -s "$AAUG"; "${RUN[@]}" python "$BUNDLE_DIR/helpers/compare_east_asia_public_augmentation_astral_backbone.py" --baseline-tree "$ABASE" --augmented-tree "$AAUG" --baseline-species-map "$ROOT/paired_inputs/baseline294/astral_species_map.csv" --scenario-id cnipg_295 --output "$ROOT/evaluation/cnipg_295_astral_backbone.json"
'''


def summarize() -> str:
    return '''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-cnipg-summary
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=01:00:00
''' + common() + '''for MODE in bwa blastx; do test -s "$GENOME_AUGMENT_ROOT/$MODE/paired_inputs/paired_augmentation_summary.json"; test -s "$GENOME_AUGMENT_ROOT/$MODE/evaluation/cnipg_295_CNIPG_concat.json"; test -s "$GENOME_AUGMENT_ROOT/$MODE/evaluation/cnipg_295_astral_backbone.json"; done; "${RUN[@]}" python "$BUNDLE_DIR/helpers/summarize_cirsium_nipponicum_genome_augmentation_sensitivities.py" --root "$GENOME_AUGMENT_ROOT" --output "$GENOME_AUGMENT_ROOT/cross_data_type_sensitivity_summary.json"
'''


def submit_mode() -> str:
    return '''#!/usr/bin/env bash
set -euo pipefail
MODE="${MODE:-bwa}"
[[ "$MODE" == "bwa" || "$MODE" == "blastx" ]]
prep=$(sbatch --parsable --export=ALL,MODE="$MODE" 20_prepare_cnipg_paired_inputs_slurm.sh)
aln=$(sbatch --parsable --dependency=afterok:$prep --export=ALL,MODE="$MODE" 21_align_cnipg_paired_slurm.sh)
gene=$(sbatch --parsable --dependency=afterok:$aln --export=ALL,MODE="$MODE" 22_gene_trees_cnipg_paired_slurm.sh)
con=$(sbatch --parsable --dependency=afterok:$aln --export=ALL,MODE="$MODE" 23_concat_cnipg_paired_slurm.sh)
ast=$(sbatch --parsable --dependency=afterok:$gene --export=ALL,MODE="$MODE" 24_astral_cnipg_paired_slurm.sh)
ev=$(sbatch --parsable --dependency=afterok:$con:$ast --export=ALL,MODE="$MODE" 25_evaluate_cnipg_paired_slurm.sh)
printf 'mode=%s\nprepare=%s\nalign=%s\ngene=%s\nconcat=%s\nastral=%s\nevaluate=%s\n' "$MODE" "$prep" "$aln" "$gene" "$con" "$ast" "$ev"
'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-bundle", type=Path, required=True)
    parser.add_argument("--genome-pack", type=Path, required=True)
    parser.add_argument("--gate", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()

    validate_baseline(args.baseline_bundle)
    gate = json.loads(args.gate.read_text(encoding="utf-8"))
    if gate.get("contract_version") != "cirsium_nipponicum_public_genome_augmentation_v1":
        raise ValueError("unexpected Ulleung genome augmentation gate")
    pack = validate_genome_pack(args.genome_pack, gate)

    args.outdir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(args.baseline_bundle / "env.yml", args.outdir / "env.yml")
    shutil.copy2(args.baseline_bundle / "sample_manifest.csv", args.outdir / "baseline_sample_manifest.csv")
    shutil.copy2(args.baseline_bundle / "astral_species_map.csv", args.outdir / "baseline_astral_species_map.csv")
    shutil.copy2(args.gate, args.outdir / "augmentation_gate.json")
    dst = args.outdir / "genome_pack"
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    for name in MANDATORY_GENOME_PACK_FILES:
        src = args.genome_pack / name
        if not src.is_file():
            raise ValueError(f"mandatory genome-pack tree input is missing: {name}")
        shutil.copy2(src, dst / name)
    optional_present: list[str] = []
    optional_absent: list[str] = []
    for name in OPTIONAL_GENOME_PACK_DIAGNOSTICS:
        src = args.genome_pack / name
        if src.is_file():
            shutil.copy2(src, dst / name)
            optional_present.append(name)
        else:
            optional_absent.append(name)
    shutil.copytree(args.genome_pack / "loci", dst / "loci")

    helpers = (
        "prepare_cirsium_nipponicum_augmentation_tree_inputs.py",
        "evaluate_east_asia_public_augmentation_tree_pair.py",
        "compare_east_asia_public_augmentation_astral_backbone.py",
        "summarize_cirsium_nipponicum_genome_augmentation_sensitivities.py",
        "concatenate_colour_rate_comp1061_alignments.py",
    )
    (args.outdir / "helpers").mkdir(parents=True, exist_ok=True)
    for name in helpers:
        shutil.copy2(ROOT / "analysis" / name, args.outdir / "helpers" / name)

    scripts = {
        "20_prepare_cnipg_paired_inputs_slurm.sh": prep(),
        "21_align_cnipg_paired_slurm.sh": align(),
        "22_gene_trees_cnipg_paired_slurm.sh": gene(),
        "23_concat_cnipg_paired_slurm.sh": concat(),
        "24_astral_cnipg_paired_slurm.sh": astral(),
        "25_evaluate_cnipg_paired_slurm.sh": evaluate(),
        "26_summarize_cnipg_cross_data_type_slurm.sh": summarize(),
        "submit_cnipg_mode_chain.sh": submit_mode(),
    }
    for name, text in scripts.items():
        write(args.outdir / name, text, 0o755)

    manifest = {
        "bundle_version": "cirsium_nipponicum_genome_augmentation_hpc_bundle_v1",
        "baseline_bundle_version": "japan_origin_global_hpc_bundle_v2",
        "baseline_focal_tips": 294,
        "candidate_id": "CNIPG",
        "candidate_tip": pack["tip_id"],
        "candidate_taxon": "Cirsium nipponicum",
        "genome_strict_loci": pack["strict_recovered_loci"],
        "minimum_paired_loci": 100,
        "baseline_mapping_modes": ["bwa", "blastx"],
        "candidate_mapping_mode": "genome_annotation_derived_CDS_fixed_pack",
        "scenarios": list(SCENARIOS),
        "cross_data_type_sensitivity": True,
        "tree_tip_promotion_allowed": False,
        "new_analysis_taxon_labels_added": 0,
        "combined_current_public_candidate_tip_ceiling": 297,
        "combined_ceiling_is_accepted_tree": False,
        "genome_pack_tree_inputs_complete": True,
        "genome_pack_mandatory_files": list(MANDATORY_GENOME_PACK_FILES),
        "genome_pack_optional_diagnostics_present": optional_present,
        "genome_pack_optional_diagnostics_absent": optional_absent,
    }
    write(args.outdir / "execution_manifest.json", json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
