#!/usr/bin/env python3
"""Combine the 294-tip baseline and post-empirical EA01-only augmentation bundle."""
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


def load(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"invalid manifest: {path}")
    return data


def validate_inputs(baseline: Path, augmentation: Path) -> tuple[dict[str, object], dict[str, object]]:
    bm = load(baseline / "execution_manifest.json")
    am = load(augmentation / "execution_manifest.json")
    if bm.get("bundle_version") != "japan_origin_global_hpc_bundle_v2":
        raise ValueError("baseline bundle version drift")
    if bm.get("biological_samples") != 294 or bm.get("public_runs") != 295:
        raise ValueError("baseline inventory drift")
    if am.get("bundle_version") != "ea01_public_augmentation_hpc_bundle_v2":
        raise ValueError("EA01 augmentation bundle version drift")
    if am.get("candidate_id") != "EA01" or am.get("candidate_tip_id") != "PUBEA001":
        raise ValueError("EA01 augmentation identity drift")
    if am.get("candidate_strict_loci_bwa") != 236 or am.get("ea02_enters_biological_tree_inputs") is not False:
        raise ValueError("post-empirical EA01 bundle contract drift")
    for name in (
        "00_prepare_inputs_slurm.sh", "01_fetch_trim_slurm.sh", "02_hybpiper_bwa_slurm.sh",
        "02b_hybpiper_blastx_slurm.sh", "03_retrieve_qc_slurm.sh", "04_prepare_tree_inputs_slurm.sh",
        "05_align_loci_slurm.sh", "06_gene_trees_slurm.sh", "07_concat_tree_slurm.sh",
        "08_astral_species_tree_slurm.sh", "09_accept_trees_slurm.sh",
    ):
        if not (baseline / name).is_file():
            raise ValueError(f"baseline bundle missing {name}")
    return bm, am


def common() -> str:
    return r'''set -euo pipefail
AUG_BUNDLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HANDOFF_DIR="$(cd "$AUG_BUNDLE_DIR/.." && pwd)"
REPO_ROOT="${REPO_ROOT:?Set REPO_ROOT to an EAzami checkout at the handoff code revision}"
BASELINE_RESULT_ROOT="${RESULT_ROOT:-$PWD/results/japan_origin_global_v2}"
AUGMENT_ROOT="${AUGMENT_ROOT:-$PWD/results/ea01_public_augmentation}"
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
    return '''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-ea01-cand-fetch
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=08:00:00
''' + common() + r'''CID=EA01; TIP=PUBEA001; RUNACC=SRR30887223
ROOT="$AUGMENT_ROOT/candidate_mapping/reads/$CID"
R1="$ROOT/trimmed/$TIP.R1.fastq.gz"; R2="$ROOT/trimmed/$TIP.R2.fastq.gz"
if [[ -s "$R1" && -s "$R2" ]]; then exit 0; fi
mkdir -p "$ROOT"/{sra,raw,trimmed,scratch}
"${RUN[@]}" prefetch "$RUNACC" --max-size u --output-directory "$ROOT/sra"
SRA=$(find "$ROOT/sra" -name "$RUNACC.sra" -print -quit); test -s "$SRA"
"${RUN[@]}" vdb-validate "$SRA"
"${RUN[@]}" fasterq-dump "$SRA" --split-files -e 4 -t "$ROOT/scratch" -O "$ROOT/raw"
test -s "$ROOT/raw/${RUNACC}_1.fastq"; test -s "$ROOT/raw/${RUNACC}_2.fastq"
"${RUN[@]}" fastp -i "$ROOT/raw/${RUNACC}_1.fastq" -I "$ROOT/raw/${RUNACC}_2.fastq" \
  -o "$R1" -O "$R2" --thread 4 --detect_adapter_for_pe \
  --json "$ROOT/trimmed/fastp.json" --html "$ROOT/trimmed/fastp.html"
test -s "$R1"; test -s "$R2"; rm -rf "$ROOT/raw" "$ROOT/sra" "$ROOT/scratch"
'''


def candidate_blastx() -> str:
    return '''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-ea01-cand-blastx
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=48:00:00
''' + common() + r'''TIP=PUBEA001
R1="$AUGMENT_ROOT/candidate_mapping/reads/EA01/trimmed/$TIP.R1.fastq.gz"
R2="$AUGMENT_ROOT/candidate_mapping/reads/EA01/trimmed/$TIP.R2.fastq.gz"
TARGET="$BASELINE_RESULT_ROOT/inputs/reference/comp1061_hybpiper_reference.fasta"
OUT="$AUGMENT_ROOT/candidate_mapping/blastx/hybpiper"
test -s "$R1"; test -s "$R2"; test -s "$TARGET"; mkdir -p "$OUT"
[[ -s "$OUT/$TIP.tar.gz" ]] && exit 0
cd "$OUT"
"${RUN[@]}" hybpiper assemble -t_dna "$TARGET" -r "$R1" "$R2" --prefix "$TIP" --cpu 16 --no_intronerate --compress_sample_folder
cd - >/dev/null; test -s "$OUT/$TIP.tar.gz"
'''


def candidate_pack() -> str:
    return '''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-ea01-cand-pack
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --time=08:00:00
''' + common() + r'''TIP=PUBEA001
TARGET="$BASELINE_RESULT_ROOT/inputs/reference/comp1061_hybpiper_reference.fasta"
LOCI="$BASELINE_RESULT_ROOT/inputs/locus_sets/moreyra_conservative_241_no_warning_loci.txt"
HYB="$AUGMENT_ROOT/candidate_mapping/blastx/hybpiper"
ROOT="$AUGMENT_ROOT/candidate_mapping/blastx/EA01"; RETR="$ROOT/retrieved"
PACK="$AUGMENT_ROOT/candidate_mapping/blastx/packs/EA01"; REPORT="$ROOT/paralog_report"
test -s "$TARGET"; test -s "$LOCI"; test -s "$HYB/$TIP.tar.gz"; mkdir -p "$ROOT" "$RETR" "$PACK"
printf '%s\n' "$TIP" > "$ROOT/sample_names.txt"
cd "$HYB"
"${RUN[@]}" hybpiper retrieve_sequences dna -t_dna "$TARGET" --sample_names "$ROOT/sample_names.txt" --hybpiper_dir . --fasta_dir "$RETR" --cpu 4
"${RUN[@]}" hybpiper paralog_retriever "$ROOT/sample_names.txt" -t_dna "$TARGET" --hybpiper_dir . \
  --fasta_dir_all "$ROOT/paralogs_all" --paralog_report_filename "$REPORT" \
  --paralogs_above_threshold_report_filename "$ROOT/paralog_loci_any" \
  --paralogs_list_threshold_percentage 0 --no_heatmap --cpu 4
cd - >/dev/null; test -s "$REPORT.tsv"
"${RUN[@]}" python "$AUG_BUNDLE_DIR/helpers/build_public_sra_comp1061_candidate_pack.py" \
  --candidate-manifest "$AUG_BUNDLE_DIR/candidate_manifest.csv" --candidate-id EA01 \
  --locus-list "$LOCI" --retrieved-dir "$RETR" --paralog-report "$REPORT.tsv" --outdir "$PACK"
"${RUN[@]}" python - "$PACK/candidate_pack_summary.json" <<'PY'
import json,sys
s=json.load(open(sys.argv[1]))
print(json.dumps({'candidate_id':s['candidate_id'],'strict_no_warning_recovered_loci':s['strict_no_warning_recovered_loci'],'pilot_locus_pack_ready':s['pilot_locus_pack_ready']},indent=2))
if not s['pilot_locus_pack_ready']: raise SystemExit('EA01 BLASTx pack failed >=100 strict-locus gate')
if s['tree_tip_promotion_allowed'] or s['primary_294_panel_changed']: raise SystemExit('candidate pack illegally pre-authorized promotion')
PY
'''


def dynamic_prepare() -> str:
    return '''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-ea01-prep-map
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=02:00:00
''' + common() + r'''MODE="${MODE:-bwa}"; PRIMARY="$BASELINE_RESULT_ROOT/tree_$MODE/inputs"; test -s "$PRIMARY/eligible_loci.txt"
if [[ "$MODE" == "bwa" ]]; then EA01="$AUG_BUNDLE_DIR/candidate_packs/EA01";
elif [[ "$MODE" == "blastx" ]]; then EA01="$AUGMENT_ROOT/candidate_mapping/blastx/packs/EA01";
else echo "unsupported MODE=$MODE" >&2; exit 2; fi
"${RUN[@]}" python "$AUG_BUNDLE_DIR/helpers/prepare_ea01_public_augmentation_tree_inputs.py" \
  --primary-inputs "$PRIMARY" --baseline-manifest "$AUG_BUNDLE_DIR/baseline_sample_manifest.csv" \
  --baseline-species-map "$AUG_BUNDLE_DIR/baseline_astral_species_map.csv" --ea01-pack "$EA01" \
  --contract "$AUG_BUNDLE_DIR/ea01_contract.json" --outdir "$AUGMENT_ROOT/$MODE/paired_inputs"
'''


def orchestrator() -> str:
    return r'''#!/usr/bin/env bash
set -euo pipefail
HANDOFF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; BASE="$HANDOFF_DIR/baseline_bundle"; AUG="$HANDOFF_DIR/augmentation_bundle"
REPO_ROOT="${REPO_ROOT:?Set REPO_ROOT to the EAzami checkout used with this handoff}"
RESULT_ROOT="${RESULT_ROOT:-$PWD/results/japan_origin_global_v2}"; BASELINE_RESULT_ROOT="$RESULT_ROOT"
AUGMENT_ROOT="${AUGMENT_ROOT:-$PWD/results/ea01_public_augmentation}"; ENV_PREFIX="${ENV_PREFIX:-$REPO_ROOT/.conda/eazami-japan-origin-global}"
export REPO_ROOT RESULT_ROOT BASELINE_RESULT_ROOT AUGMENT_ROOT ENV_PREFIX
for f in "$BASE/00_prepare_inputs_slurm.sh" "$BASE/01_fetch_trim_slurm.sh" "$BASE/02_hybpiper_bwa_slurm.sh" "$BASE/02b_hybpiper_blastx_slurm.sh" "$AUG/00_fetch_candidate_reads_slurm.sh" "$AUG/01_hybpiper_candidate_blastx_slurm.sh" "$AUG/02_build_candidate_blastx_pack_slurm.sh" "$AUG/10_prepare_paired_inputs_with_candidate_mapping_slurm.sh" "$AUG/16_summarize_cross_mapping_sensitivities_slurm.sh"; do test -s "$f"; done
prep=$(sbatch --parsable --export=ALL "$BASE/00_prepare_inputs_slurm.sh")
fetch=$(sbatch --parsable --dependency=afterok:$prep --export=ALL "$BASE/01_fetch_trim_slurm.sh")
cfetch=$(sbatch --parsable --dependency=afterok:$prep --export=ALL "$AUG/00_fetch_candidate_reads_slurm.sh")
bhyb=$(sbatch --parsable --dependency=afterok:$fetch --export=ALL "$BASE/02_hybpiper_bwa_slurm.sh")
xhyb=$(sbatch --parsable --dependency=afterok:$fetch --export=ALL "$BASE/02b_hybpiper_blastx_slurm.sh")
cxhyb=$(sbatch --parsable --dependency=afterok:$cfetch:$prep --export=ALL "$AUG/01_hybpiper_candidate_blastx_slurm.sh")
bqc=$(sbatch --parsable --dependency=afterok:$bhyb --export=ALL,MODE=bwa "$BASE/03_retrieve_qc_slurm.sh")
xqc=$(sbatch --parsable --dependency=afterok:$xhyb --export=ALL,MODE=blastx "$BASE/03_retrieve_qc_slurm.sh")
cxpack=$(sbatch --parsable --dependency=afterok:$cxhyb --export=ALL "$AUG/02_build_candidate_blastx_pack_slurm.sh")
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
candidate_fetch_ea01=$cfetch
baseline_bwa_accept=$bacc
baseline_blastx_accept=$xacc
ea01_bwa_evaluate=$baeval
ea01_blastx_evaluate=$xaeval
ea01_cross_mapping_summary=$summary
EOF
'''


def readme() -> str:
    return """# EA01-only public nuclear HPC handoff\n\nThis is the post-empirical same-assay handoff. It runs the accepted 294-tip baseline under BWA and BLASTx and compares only `baseline294` versus `ea01_295` on identical paired loci within each mode. EA02 is not downloaded and never enters biological tree inputs.\n\nSet `REPO_ROOT`, optionally `RESULT_ROOT` and `AUGMENT_ROOT`, then run `submit_full_ea01_public_tree_augmentation.sh`. The final EA01 product is `cross_mapping_sensitivity_summary.json`.\n"""


def build(*, baseline_bundle: Path, augmentation_bundle: Path, outdir: Path) -> dict[str, object]:
    bm, am = validate_inputs(baseline_bundle, augmentation_bundle)
    if outdir.exists(): shutil.rmtree(outdir)
    outdir.mkdir(parents=True)
    base_out = outdir / "baseline_bundle"; aug_out = outdir / "augmentation_bundle"
    shutil.copytree(baseline_bundle, base_out); shutil.copytree(augmentation_bundle, aug_out)
    candidate_manifest = ROOT / "data/evidence/east_asia_public_sra_augmentation_candidates_v1.csv"
    pack_builder = ROOT / "analysis/build_public_sra_comp1061_candidate_pack.py"
    if not candidate_manifest.is_file() or not pack_builder.is_file(): raise ValueError("EA01 recovery dependencies missing")
    shutil.copy2(candidate_manifest, aug_out / "candidate_manifest.csv")
    shutil.copy2(pack_builder, aug_out / "helpers/build_public_sra_comp1061_candidate_pack.py")
    write(aug_out / "00_fetch_candidate_reads_slurm.sh", candidate_fetch(), 0o755)
    write(aug_out / "01_hybpiper_candidate_blastx_slurm.sh", candidate_blastx(), 0o755)
    write(aug_out / "02_build_candidate_blastx_pack_slurm.sh", candidate_pack(), 0o755)
    write(aug_out / "10_prepare_paired_inputs_with_candidate_mapping_slurm.sh", dynamic_prepare(), 0o755)
    write(outdir / "submit_full_ea01_public_tree_augmentation.sh", orchestrator(), 0o755)
    write(outdir / "README.md", readme())
    result: dict[str, object] = {
        "handoff_version": "ea01_public_full_hpc_handoff_v2",
        "baseline_bundle_version": bm["bundle_version"],
        "augmentation_bundle_version": am["bundle_version"],
        "baseline_biological_tips": 294,
        "baseline_public_runs": 295,
        "baseline_sra_download_shared_between_mapping_modes": True,
        "candidate_ids": ["EA01"],
        "candidate_bwa_source": "frozen successful public-SRA pilot pack",
        "candidate_blastx_source": "fresh HPC recovery from SRR30887223 using HybPiper BLASTx mapping",
        "candidate_mapping_sensitivity_is_symmetric": True,
        "mapping_modes": ["bwa", "blastx"],
        "paired_scenarios": ["baseline294", "ea01_295"],
        "ea02_enters_biological_tree_inputs": False,
        "ea02_public_read_downloaded": False,
        "final_product": "cross_mapping_sensitivity_summary.json",
        "heavy_compute_location": "HPC_or_large_memory_local_only",
        "new_analysis_taxon_labels_added_by_candidate": 0,
        "new_china_sampling_freeze_allowed": False,
    }
    write(outdir / "handoff_manifest.json", json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2)); return result


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--baseline-bundle", type=Path, required=True); parser.add_argument("--augmentation-bundle", type=Path, required=True); parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args(); build(baseline_bundle=args.baseline_bundle, augmentation_bundle=args.augmentation_bundle, outdir=args.outdir); return 0


if __name__ == "__main__": raise SystemExit(main())
