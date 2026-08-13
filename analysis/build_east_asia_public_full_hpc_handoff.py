#!/usr/bin/env python3
"""Combine the validated 294-tip baseline and EA01/EA02 augmentation bundles.

The handoff adds the missing candidate-side BLASTx recovery sensitivity and one
Slurm orchestrator that shares the 295-SRR baseline download across BWA and
BLASTx before running the paired augmentation gate.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def write(path: Path, text: str, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    path.chmod(mode)


def manifest(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"invalid manifest: {path}")
    return data


def validate_inputs(baseline: Path, augmentation: Path) -> tuple[dict[str, object], dict[str, object]]:
    bm = manifest(baseline / "execution_manifest.json")
    am = manifest(augmentation / "execution_manifest.json")
    if bm.get("bundle_version") != "japan_origin_global_hpc_bundle_v2":
        raise ValueError("baseline bundle version drift")
    if int(bm.get("biological_samples", 0)) != 294 or int(bm.get("public_runs", 0)) != 295:
        raise ValueError("baseline bundle is not 294-tip / 295-SRR v2")
    if am.get("bundle_version") != "east_asia_public_augmentation_hpc_bundle_v1":
        raise ValueError("augmentation bundle version drift")
    if int(am.get("baseline_focal_tips", 0)) != 294:
        raise ValueError("augmentation baseline count drift")
    if am.get("candidate_tip_ids") != ["PUBEA001", "PUBEA002"]:
        raise ValueError("augmentation candidate tip drift")
    if am.get("candidate_strict_loci") != {"EA01": 236, "EA02": 239}:
        raise ValueError("augmentation BWA candidate-locus drift")
    for name in (
        "00_prepare_inputs_slurm.sh",
        "01_fetch_trim_slurm.sh",
        "02_hybpiper_bwa_slurm.sh",
        "02b_hybpiper_blastx_slurm.sh",
        "03_retrieve_qc_slurm.sh",
        "04_prepare_tree_inputs_slurm.sh",
        "05_align_loci_slurm.sh",
        "06_gene_trees_slurm.sh",
        "07_concat_tree_slurm.sh",
        "08_astral_species_tree_slurm.sh",
        "09_accept_trees_slurm.sh",
    ):
        if not (baseline / name).is_file():
            raise ValueError(f"baseline bundle missing {name}")
    for name in (
        "11_align_paired_scenarios_slurm.sh",
        "12_gene_trees_paired_scenarios_slurm.sh",
        "13_concat_paired_scenarios_slurm.sh",
        "14_astral_paired_scenarios_slurm.sh",
        "15_evaluate_paired_scenarios_slurm.sh",
        "16_summarize_cross_mapping_sensitivities_slurm.sh",
    ):
        if not (augmentation / name).is_file():
            raise ValueError(f"augmentation bundle missing {name}")
    return bm, am


def common() -> str:
    return r'''set -euo pipefail
AUG_BUNDLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HANDOFF_DIR="$(cd "$AUG_BUNDLE_DIR/.." && pwd)"
REPO_ROOT="${REPO_ROOT:?Set REPO_ROOT to an EAzami checkout at the handoff code revision}"
BASELINE_RESULT_ROOT="${RESULT_ROOT:-$PWD/results/japan_origin_global_v2}"
AUGMENT_ROOT="${AUGMENT_ROOT:-$PWD/results/east_asia_public_augmentation}"
ENV_PREFIX="${ENV_PREFIX:-$REPO_ROOT/.conda/eazami-japan-origin-global}"
export REPO_ROOT RESULT_ROOT="$BASELINE_RESULT_ROOT" BASELINE_RESULT_ROOT AUGMENT_ROOT ENV_PREFIX
if command -v micromamba >/dev/null 2>&1; then
  if [[ ! -x "$ENV_PREFIX/bin/python" ]]; then micromamba create -y -p "$ENV_PREFIX" -f "$AUG_BUNDLE_DIR/env.yml"; fi
  RUN=(micromamba run -p "$ENV_PREFIX")
elif command -v mamba >/dev/null 2>&1; then
  if [[ ! -x "$ENV_PREFIX/bin/python" ]]; then mamba env create -y -p "$ENV_PREFIX" -f "$AUG_BUNDLE_DIR/env.yml"; fi
  RUN=(mamba run -p "$ENV_PREFIX")
else
  echo "micromamba or mamba required" >&2
  exit 2
fi
mkdir -p "$AUGMENT_ROOT/candidate_mapping"
'''


def candidate_fetch() -> str:
    return r'''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-eaaug-cand-fetch
#SBATCH --array=0-1%2
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=08:00:00
#SBATCH --output=eaaug_cand_fetch_%A_%a.out
#SBATCH --error=eaaug_cand_fetch_%A_%a.err
''' + common() + r'''
CIDS=(EA01 EA02)
TIPS=(PUBEA001 PUBEA002)
RUNS=(SRR30887223 SRR9119112)
IDX="${SLURM_ARRAY_TASK_ID:?}"
CID="${CIDS[$IDX]}"; TIP="${TIPS[$IDX]}"; RUNACC="${RUNS[$IDX]}"
ROOT="$AUGMENT_ROOT/candidate_mapping/reads/$CID"
R1="$ROOT/trimmed/$TIP.R1.fastq.gz"; R2="$ROOT/trimmed/$TIP.R2.fastq.gz"
if [[ -s "$R1" && -s "$R2" ]]; then exit 0; fi
mkdir -p "$ROOT"/{sra,raw,trimmed,scratch}
"${RUN[@]}" prefetch "$RUNACC" --output-directory "$ROOT/sra"
SRA=$(find "$ROOT/sra" -name "$RUNACC.sra" -print -quit)
test -s "$SRA"
"${RUN[@]}" vdb-validate "$SRA"
"${RUN[@]}" fasterq-dump "$SRA" --split-files --threads 4 --temp "$ROOT/scratch" --outdir "$ROOT/raw"
test -s "$ROOT/raw/${RUNACC}_1.fastq"; test -s "$ROOT/raw/${RUNACC}_2.fastq"
"${RUN[@]}" fastp -i "$ROOT/raw/${RUNACC}_1.fastq" -I "$ROOT/raw/${RUNACC}_2.fastq" -o "$R1" -O "$R2" --thread 4 --json "$ROOT/trimmed/fastp.json" --html "$ROOT/trimmed/fastp.html"
test -s "$R1"; test -s "$R2"
rm -rf "$ROOT/raw" "$ROOT/sra" "$ROOT/scratch"
'''


def candidate_blastx() -> str:
    return r'''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-eaaug-cand-blastx
#SBATCH --array=0-1%2
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=48:00:00
#SBATCH --output=eaaug_cand_blastx_%A_%a.out
#SBATCH --error=eaaug_cand_blastx_%A_%a.err
''' + common() + r'''
CIDS=(EA01 EA02)
TIPS=(PUBEA001 PUBEA002)
IDX="${SLURM_ARRAY_TASK_ID:?}"
CID="${CIDS[$IDX]}"; TIP="${TIPS[$IDX]}"
READROOT="$AUGMENT_ROOT/candidate_mapping/reads/$CID/trimmed"
R1="$READROOT/$TIP.R1.fastq.gz"; R2="$READROOT/$TIP.R2.fastq.gz"
TARGET="$BASELINE_RESULT_ROOT/inputs/reference/comp1061_hybpiper_reference.fasta"
OUT="$AUGMENT_ROOT/candidate_mapping/blastx/hybpiper"
test -s "$R1"; test -s "$R2"; test -s "$TARGET"; mkdir -p "$OUT"
[[ -s "$OUT/$TIP.tar.gz" ]] && exit 0
cd "$OUT"
"${RUN[@]}" hybpiper assemble -t_dna "$TARGET" -r "$R1" "$R2" --prefix "$TIP" --cpu 16 --no_intronerate --compress_sample_folder
cd - >/dev/null
test -s "$OUT/$TIP.tar.gz"
'''


def candidate_pack() -> str:
    return r'''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-eaaug-cand-pack
#SBATCH --array=0-1%2
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --time=08:00:00
#SBATCH --output=eaaug_cand_pack_%A_%a.out
#SBATCH --error=eaaug_cand_pack_%A_%a.err
''' + common() + r'''
CIDS=(EA01 EA02)
TIPS=(PUBEA001 PUBEA002)
IDX="${SLURM_ARRAY_TASK_ID:?}"
CID="${CIDS[$IDX]}"; TIP="${TIPS[$IDX]}"
TARGET="$BASELINE_RESULT_ROOT/inputs/reference/comp1061_hybpiper_reference.fasta"
LOCI="$BASELINE_RESULT_ROOT/inputs/locus_sets/moreyra_conservative_241_no_warning_loci.txt"
HYB="$AUGMENT_ROOT/candidate_mapping/blastx/hybpiper"
ROOT="$AUGMENT_ROOT/candidate_mapping/blastx/$CID"
RETR="$ROOT/retrieved"; PACK="$AUGMENT_ROOT/candidate_mapping/blastx/packs/$CID"
REPORT="$ROOT/paralog_report"
test -s "$TARGET"; test -s "$LOCI"; test -s "$HYB/$TIP.tar.gz"
mkdir -p "$ROOT" "$RETR" "$PACK"
printf '%s\n' "$TIP" > "$ROOT/sample_names.txt"
cd "$HYB"
"${RUN[@]}" hybpiper retrieve_sequences dna -t_dna "$TARGET" --sample_names "$ROOT/sample_names.txt" --hybpiper_dir . --fasta_dir "$RETR" --cpu 4
"${RUN[@]}" hybpiper paralog_retriever "$ROOT/sample_names.txt" -t_dna "$TARGET" --hybpiper_dir . --fasta_dir_all "$ROOT/paralogs_all" --paralog_report_filename "$REPORT" --paralogs_above_threshold_report_filename "$ROOT/paralog_loci_any" --paralogs_list_threshold_percentage 0 --no_heatmap --cpu 4
cd - >/dev/null
test -s "$REPORT.tsv"
"${RUN[@]}" python "$AUG_BUNDLE_DIR/helpers/build_public_sra_comp1061_candidate_pack.py" --candidate-manifest "$AUG_BUNDLE_DIR/candidate_manifest.csv" --candidate-id "$CID" --locus-list "$LOCI" --retrieved-dir "$RETR" --paralog-report "$REPORT.tsv" --outdir "$PACK"
"${RUN[@]}" python - "$PACK/candidate_pack_summary.json" <<'PY'
import json,sys
p=sys.argv[1]; s=json.load(open(p))
print(json.dumps({'candidate_id':s['candidate_id'],'strict_no_warning_recovered_loci':s['strict_no_warning_recovered_loci'],'pilot_locus_pack_ready':s['pilot_locus_pack_ready']},indent=2))
if not s['pilot_locus_pack_ready']:
    raise SystemExit('BLASTx candidate pack failed >=100 strict-locus admission gate')
if s['tree_tip_promotion_allowed'] or s['primary_294_panel_changed']:
    raise SystemExit('candidate pack illegally pre-authorized tree promotion')
PY
'''


def dynamic_prepare() -> str:
    return r'''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-eaaug-prep-map
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=02:00:00
''' + common() + r'''
MODE="${MODE:-bwa}"
PRIMARY="$BASELINE_RESULT_ROOT/tree_$MODE/inputs"
test -s "$PRIMARY/eligible_loci.txt"
if [[ "$MODE" == "bwa" ]]; then
  EA01="$AUG_BUNDLE_DIR/candidate_packs/EA01"
  EA02="$AUG_BUNDLE_DIR/candidate_packs/EA02"
elif [[ "$MODE" == "blastx" ]]; then
  EA01="$AUGMENT_ROOT/candidate_mapping/blastx/packs/EA01"
  EA02="$AUGMENT_ROOT/candidate_mapping/blastx/packs/EA02"
else
  echo "unsupported MODE=$MODE" >&2; exit 2
fi
"${RUN[@]}" python "$AUG_BUNDLE_DIR/helpers/prepare_east_asia_public_augmentation_tree_inputs.py" --primary-inputs "$PRIMARY" --baseline-manifest "$AUG_BUNDLE_DIR/baseline_sample_manifest.csv" --baseline-species-map "$AUG_BUNDLE_DIR/baseline_astral_species_map.csv" --ea01-pack "$EA01" --ea02-pack "$EA02" --contract "$AUG_BUNDLE_DIR/augmentation_contract.json" --outdir "$AUGMENT_ROOT/$MODE/paired_inputs"
'''


def orchestrator() -> str:
    return r'''#!/usr/bin/env bash
set -euo pipefail
HANDOFF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE="$HANDOFF_DIR/baseline_bundle"
AUG="$HANDOFF_DIR/augmentation_bundle"
REPO_ROOT="${REPO_ROOT:?Set REPO_ROOT to the EAzami checkout used with this handoff}"
RESULT_ROOT="${RESULT_ROOT:-$PWD/results/japan_origin_global_v2}"
BASELINE_RESULT_ROOT="$RESULT_ROOT"
AUGMENT_ROOT="${AUGMENT_ROOT:-$PWD/results/east_asia_public_augmentation}"
ENV_PREFIX="${ENV_PREFIX:-$REPO_ROOT/.conda/eazami-japan-origin-global}"
export REPO_ROOT RESULT_ROOT BASELINE_RESULT_ROOT AUGMENT_ROOT ENV_PREFIX
for f in "$BASE/00_prepare_inputs_slurm.sh" "$BASE/01_fetch_trim_slurm.sh" "$BASE/02_hybpiper_bwa_slurm.sh" "$BASE/02b_hybpiper_blastx_slurm.sh" "$AUG/00_fetch_candidate_reads_slurm.sh" "$AUG/01_hybpiper_candidate_blastx_slurm.sh" "$AUG/02_build_candidate_blastx_packs_slurm.sh" "$AUG/10_prepare_paired_inputs_with_candidate_mapping_slurm.sh" "$AUG/16_summarize_cross_mapping_sensitivities_slurm.sh"; do test -s "$f"; done

prep=$(sbatch --parsable --export=ALL "$BASE/00_prepare_inputs_slurm.sh")
fetch=$(sbatch --parsable --dependency=afterok:$prep --export=ALL "$BASE/01_fetch_trim_slurm.sh")
cfetch=$(sbatch --parsable --dependency=afterok:$prep --export=ALL "$AUG/00_fetch_candidate_reads_slurm.sh")
bhyb=$(sbatch --parsable --dependency=afterok:$fetch --export=ALL "$BASE/02_hybpiper_bwa_slurm.sh")
xhyb=$(sbatch --parsable --dependency=afterok:$fetch --export=ALL "$BASE/02b_hybpiper_blastx_slurm.sh")
cxhyb=$(sbatch --parsable --dependency=afterok:$cfetch:$prep --export=ALL "$AUG/01_hybpiper_candidate_blastx_slurm.sh")
bqc=$(sbatch --parsable --dependency=afterok:$bhyb --export=ALL,MODE=bwa "$BASE/03_retrieve_qc_slurm.sh")
xqc=$(sbatch --parsable --dependency=afterok:$xhyb --export=ALL,MODE=blastx "$BASE/03_retrieve_qc_slurm.sh")
cxpack=$(sbatch --parsable --dependency=afterok:$cxhyb --export=ALL "$AUG/02_build_candidate_blastx_packs_slurm.sh")

btprep=$(sbatch --parsable --dependency=afterok:$bqc --export=ALL,MODE=bwa "$BASE/04_prepare_tree_inputs_slurm.sh")
xtprep=$(sbatch --parsable --dependency=afterok:$xqc --export=ALL,MODE=blastx "$BASE/04_prepare_tree_inputs_slurm.sh")
baln=$(sbatch --parsable --dependency=afterok:$btprep --export=ALL,MODE=bwa "$BASE/05_align_loci_slurm.sh")
xaln=$(sbatch --parsable --dependency=afterok:$xtprep --export=ALL,MODE=blastx "$BASE/05_align_loci_slurm.sh")
bgene=$(sbatch --parsable --dependency=afterok:$baln --export=ALL,MODE=bwa "$BASE/06_gene_trees_slurm.sh")
xgene=$(sbatch --parsable --dependency=afterok:$xaln --export=ALL,MODE=blastx "$BASE/06_gene_trees_slurm.sh")
bcon=$(sbatch --parsable --dependency=afterok:$baln --export=ALL,MODE=bwa "$BASE/07_concat_tree_slurm.sh")
xcon=$(sbatch --parsable --dependency=afterok:$xaln --export=ALL,MODE=blastx "$BASE/07_concat_tree_slurm.sh")
bast=$(sbatch --parsable --dependency=afterok:$bgene --export=ALL,MODE=bwa "$BASE/08_astral_species_tree_slurm.sh")
xast=$(sbatch --parsable --dependency=afterok:$xgene --export=ALL,MODE=blastx "$BASE/08_astral_species_tree_slurm.sh")
bacc=$(sbatch --parsable --dependency=afterok:$bcon:$bast --export=ALL,MODE=bwa "$BASE/09_accept_trees_slurm.sh")
xacc=$(sbatch --parsable --dependency=afterok:$xcon:$xast --export=ALL,MODE=blastx "$BASE/09_accept_trees_slurm.sh")

baprep=$(sbatch --parsable --dependency=afterok:$bacc --export=ALL,MODE=bwa "$AUG/10_prepare_paired_inputs_with_candidate_mapping_slurm.sh")
xaprep=$(sbatch --parsable --dependency=afterok:$xacc:$cxpack --export=ALL,MODE=blastx "$AUG/10_prepare_paired_inputs_with_candidate_mapping_slurm.sh")
baaln=$(sbatch --parsable --dependency=afterok:$baprep --export=ALL,MODE=bwa "$AUG/11_align_paired_scenarios_slurm.sh")
xaaln=$(sbatch --parsable --dependency=afterok:$xaprep --export=ALL,MODE=blastx "$AUG/11_align_paired_scenarios_slurm.sh")
bagene=$(sbatch --parsable --dependency=afterok:$baaln --export=ALL,MODE=bwa "$AUG/12_gene_trees_paired_scenarios_slurm.sh")
xagene=$(sbatch --parsable --dependency=afterok:$xaaln --export=ALL,MODE=blastx "$AUG/12_gene_trees_paired_scenarios_slurm.sh")
bacon=$(sbatch --parsable --dependency=afterok:$baaln --export=ALL,MODE=bwa "$AUG/13_concat_paired_scenarios_slurm.sh")
xacon=$(sbatch --parsable --dependency=afterok:$xaaln --export=ALL,MODE=blastx "$AUG/13_concat_paired_scenarios_slurm.sh")
baast=$(sbatch --parsable --dependency=afterok:$bagene --export=ALL,MODE=bwa "$AUG/14_astral_paired_scenarios_slurm.sh")
xaast=$(sbatch --parsable --dependency=afterok:$xagene --export=ALL,MODE=blastx "$AUG/14_astral_paired_scenarios_slurm.sh")
baeval=$(sbatch --parsable --dependency=afterok:$bacon:$baast --export=ALL,MODE=bwa "$AUG/15_evaluate_paired_scenarios_slurm.sh")
xaeval=$(sbatch --parsable --dependency=afterok:$xacon:$xaast --export=ALL,MODE=blastx "$AUG/15_evaluate_paired_scenarios_slurm.sh")
summary=$(sbatch --parsable --dependency=afterok:$baeval:$xaeval --export=ALL "$AUG/16_summarize_cross_mapping_sensitivities_slurm.sh")

cat <<EOF
baseline_prepare=$prep
baseline_fetch_295_srr=$fetch
candidate_fetch_2_srr=$cfetch
baseline_bwa_hybpiper=$bhyb
baseline_blastx_hybpiper=$xhyb
candidate_blastx_hybpiper=$cxhyb
baseline_bwa_qc=$bqc
baseline_blastx_qc=$xqc
candidate_blastx_pack=$cxpack
baseline_bwa_accept=$bacc
baseline_blastx_accept=$xacc
augmentation_bwa_evaluate=$baeval
augmentation_blastx_evaluate=$xaeval
cross_mapping_summary=$summary
EOF
'''


def readme() -> str:
    return """# EAzami public nuclear phylogeny full HPC handoff\n\nThis handoff joins the validated 294-tip/295-SRR baseline bundle and the EA01/EA02 paired augmentation bundle.\n\n## Required external state\n\n1. A checkout of the EAzami repository at the PR #19 code revision (or a descendant containing these scripts).\n2. Slurm, micromamba or mamba, network access to public SRA, and the resources requested by the generated jobs.\n3. Set `REPO_ROOT=/path/to/EAzami`.\n\n## One-command submission\n\nFrom a work directory with sufficient storage:\n\n```bash\nexport REPO_ROOT=/path/to/EAzami\nbash /path/to/full_handoff/submit_full_public_tree_and_augmentation.sh\n```\n\nOptional output roots:\n\n```bash\nexport RESULT_ROOT=/scratch/.../japan_origin_global_v2\nexport AUGMENT_ROOT=/scratch/.../east_asia_public_augmentation\n```\n\nThe orchestrator downloads the 295 baseline SRRs once, then launches BWA and BLASTx baseline recovery in parallel. EA01/EA02 BLASTx recovery is run separately from the frozen BWA pilot packs, so candidate-side mapping sensitivity is real rather than inherited from the BWA pilot. Baseline tree acceptance precedes paired augmentation for each mapping mode. The final job writes `cross_mapping_sensitivity_summary.json`.\n\nNo China sampling list is frozen by this handoff.\n"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-bundle", type=Path, required=True)
    parser.add_argument("--augmentation-bundle", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    bm, am = validate_inputs(args.baseline_bundle, args.augmentation_bundle)
    if args.outdir.exists():
        shutil.rmtree(args.outdir)
    args.outdir.mkdir(parents=True)
    base_out = args.outdir / "baseline_bundle"
    aug_out = args.outdir / "augmentation_bundle"
    shutil.copytree(args.baseline_bundle, base_out)
    shutil.copytree(args.augmentation_bundle, aug_out)

    candidate_manifest = ROOT / "data/evidence/east_asia_public_sra_augmentation_candidates_v1.csv"
    pack_builder = ROOT / "analysis/build_public_sra_comp1061_candidate_pack.py"
    if not candidate_manifest.is_file() or not pack_builder.is_file():
        raise ValueError("repository candidate recovery dependencies missing")
    shutil.copy2(candidate_manifest, aug_out / "candidate_manifest.csv")
    shutil.copy2(pack_builder, aug_out / "helpers/build_public_sra_comp1061_candidate_pack.py")

    write(aug_out / "00_fetch_candidate_reads_slurm.sh", candidate_fetch(), 0o755)
    write(aug_out / "01_hybpiper_candidate_blastx_slurm.sh", candidate_blastx(), 0o755)
    write(aug_out / "02_build_candidate_blastx_packs_slurm.sh", candidate_pack(), 0o755)
    write(aug_out / "10_prepare_paired_inputs_with_candidate_mapping_slurm.sh", dynamic_prepare(), 0o755)
    write(args.outdir / "submit_full_public_tree_and_augmentation.sh", orchestrator(), 0o755)
    write(args.outdir / "README.md", readme())

    out = {
        "handoff_version": "east_asia_public_full_hpc_handoff_v1",
        "baseline_bundle_version": bm["bundle_version"],
        "augmentation_bundle_version": am["bundle_version"],
        "baseline_biological_tips": 294,
        "baseline_public_runs": 295,
        "baseline_sra_download_shared_between_mapping_modes": True,
        "candidate_ids": ["EA01", "EA02"],
        "candidate_bwa_source": "frozen successful public-SRA pilot packs from workflow run 31684233834",
        "candidate_blastx_source": "fresh HPC recovery from the original EA01/EA02 public SRRs using HybPiper 2.3.4 BLASTx mapping",
        "candidate_mapping_sensitivity_is_symmetric": True,
        "mapping_modes": ["bwa", "blastx"],
        "paired_scenarios": ["baseline294", "ea01_295", "ea02_295", "ea01_ea02_296"],
        "final_product": "cross_mapping_sensitivity_summary.json",
        "heavy_compute_location": "HPC_or_large_memory_local_only",
        "github_actions_role": "artifact_contract_bundle_and_decision_logic_validation_only",
        "new_analysis_taxon_labels_added_by_candidates": 0,
        "new_china_sampling_freeze_allowed": False,
    }
    write(args.outdir / "handoff_manifest.json", json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
