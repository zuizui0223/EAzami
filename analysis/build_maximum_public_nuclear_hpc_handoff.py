#!/usr/bin/env python3
"""Build one artifact-free handoff for all current maximum-public nuclear gates.

This is a lightweight bundle builder only. It reconstructs the frozen 294-tip
baseline inputs and all three durable candidate packs from repository evidence,
then composes the already validated EA01/EA02 and CNIPG HPC bundles under one
submission entry point. The generated Slurm orchestrator shares the 295-SRR
baseline recovery across all independent candidate gates.

It deliberately does not construct or authorize a combined 296/297 tree. Even
if all three independent gates pass, the final collector records that an
explicit common paired-locus combined tree is still required.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable

MOREYRA_SHA256 = "cf3af71a1a77eee5bd177cef9cf8106b749b949eaacc0ad82bbb331978084505"
CANDIDATE_COUNTS = {"EA01": 236, "EA02": 239, "CNIPG": 180}
CANDIDATE_TIPS = {
    "EA01": "PUBEA001",
    "EA02": "PUBEA002",
    "CNIPG": "AUG_ULLEUNG_CNIP2024",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, text: str, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    path.chmod(mode)


def run_script(script: str, *args: object) -> None:
    command = [PYTHON, str(ROOT / "analysis" / script), *(str(x) for x in args)]
    subprocess.run(command, cwd=ROOT, check=True)


def validate_component_manifests(ea_handoff: Path, cnipg_bundle: Path) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    hm = json.loads((ea_handoff / "handoff_manifest.json").read_text(encoding="utf-8"))
    bm = json.loads((ea_handoff / "baseline_bundle" / "execution_manifest.json").read_text(encoding="utf-8"))
    cm = json.loads((cnipg_bundle / "execution_manifest.json").read_text(encoding="utf-8"))
    if hm.get("handoff_version") != "east_asia_public_full_hpc_handoff_v1":
        raise ValueError("EA01/EA02 full handoff version drift")
    if bm.get("bundle_version") != "japan_origin_global_hpc_bundle_v2":
        raise ValueError("baseline bundle version drift")
    if bm.get("biological_samples") != 294 or bm.get("public_runs") != 295:
        raise ValueError("baseline inventory drift")
    if cm.get("bundle_version") != "cirsium_nipponicum_genome_augmentation_hpc_bundle_v1":
        raise ValueError("CNIPG bundle version drift")
    if cm.get("genome_strict_loci") != 180 or cm.get("baseline_focal_tips") != 294:
        raise ValueError("CNIPG bundle inventory drift")
    return hm, bm, cm


def collector_script() -> str:
    return r'''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-max-public-summary
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=01:00:00
set -euo pipefail
HANDOFF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUGMENT_ROOT="${AUGMENT_ROOT:-$PWD/results/east_asia_public_augmentation}"
GENOME_AUGMENT_ROOT="${GENOME_AUGMENT_ROOT:-$PWD/results/cnipponicum_genome_augmentation}"
MAXIMUM_PUBLIC_ROOT="${MAXIMUM_PUBLIC_ROOT:-$PWD/results/maximum_public_nuclear}"
mkdir -p "$MAXIMUM_PUBLIC_ROOT"
EA="$AUGMENT_ROOT/cross_mapping_sensitivity_summary.json"
CN="$GENOME_AUGMENT_ROOT/cross_data_type_sensitivity_summary.json"
test -s "$EA"; test -s "$CN"
python - "$EA" "$CN" "$MAXIMUM_PUBLIC_ROOT/independent_gate_summary.json" <<'PY'
import json,sys
from pathlib import Path
ea=json.loads(Path(sys.argv[1]).read_text())
cn=json.loads(Path(sys.argv[2]).read_text())
out_path=Path(sys.argv[3])
ea01=bool(ea['candidates']['EA01']['sample_tip_promotion_allowed'])
ea02=bool(ea['candidates']['EA02']['sample_tip_promotion_allowed'])
cnipg=bool(cn['automatic_sample_tip_promotion_allowed'])
all_three=ea01 and ea02 and cnipg
out={
  'contract_version':'maximum_public_nuclear_independent_gate_summary_v1',
  'accepted_primary_before_combined_tree':294,
  'independent_candidate_gate_results':{'EA01':ea01,'EA02':ea02,'CNIPG':cnipg},
  'independent_manual_review_required':{
    'EA01':bool(ea['candidates']['EA01']['manual_review_required']),
    'EA02':bool(ea['candidates']['EA02']['manual_review_required']),
    'CNIPG':bool(cn['manual_review_required']),
  },
  'all_three_independent_gates_passed':all_three,
  'sample_level_candidate_ceiling_if_all_three_pass':297,
  'new_analysis_taxon_labels_if_all_three_pass':0,
  'combined_296_or_297_tree_accepted':False,
  'combined_common_paired_locus_tree_required':all_three,
  'new_china_sampling_freeze_allowed':False,
  'next_action':(
    'build_explicit_common_paired_locus_combined_tree_before_any_296_or_297_acceptance'
    if all_three else
    'retain_294_primary_and_review_failed_or_unresolved_independent_candidate_gates'
  ),
  'claim_boundary':'Independent candidate gates do not by arithmetic create an accepted combined 296/297 tree and do not alter flower-colour history claims.'
}
out_path.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
PY
'''


def orchestrator_script() -> str:
    return r'''#!/usr/bin/env bash
set -euo pipefail
HANDOFF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EA="$HANDOFF_DIR/ea01_ea02_handoff"
CN="$HANDOFF_DIR/cnipg_bundle"
REPO_ROOT="${REPO_ROOT:?Set REPO_ROOT to the EAzami checkout used to build this handoff}"
RESULT_ROOT="${RESULT_ROOT:-$PWD/results/japan_origin_global_v2}"
BASELINE_RESULT_ROOT="$RESULT_ROOT"
AUGMENT_ROOT="${AUGMENT_ROOT:-$PWD/results/east_asia_public_augmentation}"
GENOME_AUGMENT_ROOT="${GENOME_AUGMENT_ROOT:-$PWD/results/cnipponicum_genome_augmentation}"
MAXIMUM_PUBLIC_ROOT="${MAXIMUM_PUBLIC_ROOT:-$PWD/results/maximum_public_nuclear}"
ENV_PREFIX="${ENV_PREFIX:-$REPO_ROOT/.conda/eazami-japan-origin-global}"
export REPO_ROOT RESULT_ROOT BASELINE_RESULT_ROOT AUGMENT_ROOT GENOME_AUGMENT_ROOT MAXIMUM_PUBLIC_ROOT ENV_PREFIX

for f in \
  "$EA/submit_full_public_tree_and_augmentation.sh" \
  "$CN/20_prepare_cnipg_paired_inputs_slurm.sh" \
  "$CN/21_align_cnipg_paired_slurm.sh" \
  "$CN/22_gene_trees_cnipg_paired_slurm.sh" \
  "$CN/23_concat_cnipg_paired_slurm.sh" \
  "$CN/24_astral_cnipg_paired_slurm.sh" \
  "$CN/25_evaluate_cnipg_paired_slurm.sh" \
  "$CN/26_summarize_cnipg_cross_data_type_slurm.sh" \
  "$HANDOFF_DIR/90_collect_independent_gate_summaries_slurm.sh"; do
  test -s "$f"
done

# Submit the complete EA01/EA02 chain. This schedules the shared 295-SRR baseline
# once and prints the accepted-baseline job IDs needed by the independent CNIPG gate.
ea_out=$(bash "$EA/submit_full_public_tree_and_augmentation.sh")
printf '%s\n' "$ea_out"
bacc=$(printf '%s\n' "$ea_out" | awk -F= '$1=="baseline_bwa_accept"{print $2}')
xacc=$(printf '%s\n' "$ea_out" | awk -F= '$1=="baseline_blastx_accept"{print $2}')
ea_summary=$(printf '%s\n' "$ea_out" | awk -F= '$1=="cross_mapping_summary"{print $2}')
for value in "$bacc" "$xacc" "$ea_summary"; do
  [[ "$value" =~ ^[0-9]+([_;].*)?$ ]] || { echo "failed to parse EA handoff job id: $value" >&2; exit 2; }
done

submit_cnipg_mode() {
  local mode="$1" baseline_accept="$2"
  local prep aln gene con ast ev
  prep=$(sbatch --parsable --dependency=afterok:"$baseline_accept" --export=ALL,MODE="$mode" "$CN/20_prepare_cnipg_paired_inputs_slurm.sh")
  aln=$(sbatch --parsable --dependency=afterok:"$prep" --export=ALL,MODE="$mode" "$CN/21_align_cnipg_paired_slurm.sh")
  gene=$(sbatch --parsable --dependency=afterok:"$aln" --export=ALL,MODE="$mode" "$CN/22_gene_trees_cnipg_paired_slurm.sh")
  con=$(sbatch --parsable --dependency=afterok:"$aln" --export=ALL,MODE="$mode" "$CN/23_concat_cnipg_paired_slurm.sh")
  ast=$(sbatch --parsable --dependency=afterok:"$gene" --export=ALL,MODE="$mode" "$CN/24_astral_cnipg_paired_slurm.sh")
  ev=$(sbatch --parsable --dependency=afterok:"$con":"$ast" --export=ALL,MODE="$mode" "$CN/25_evaluate_cnipg_paired_slurm.sh")
  printf '%s\n' "$ev"
}

cn_bwa_eval=$(submit_cnipg_mode bwa "$bacc")
cn_blastx_eval=$(submit_cnipg_mode blastx "$xacc")
cn_summary=$(sbatch --parsable --dependency=afterok:"$cn_bwa_eval":"$cn_blastx_eval" --export=ALL "$CN/26_summarize_cnipg_cross_data_type_slurm.sh")
final=$(sbatch --parsable --dependency=afterok:"$ea_summary":"$cn_summary" --export=ALL "$HANDOFF_DIR/90_collect_independent_gate_summaries_slurm.sh")

cat <<EOF
baseline_bwa_accept=$bacc
baseline_blastx_accept=$xacc
ea01_ea02_cross_mapping_summary=$ea_summary
cnipg_bwa_evaluate=$cn_bwa_eval
cnipg_blastx_evaluate=$cn_blastx_eval
cnipg_cross_data_type_summary=$cn_summary
maximum_public_independent_gate_summary=$final
EOF
'''


def execute_readme() -> str:
    return """# Maximum public nuclear tree — HPC execution handoff

This directory is the top-level execution handoff for issue #18. It contains the
same validated 294-tip baseline plus all three currently ready public candidates:
EA01, EA02 and CNIPG.

## What this handoff does

- reconstructs all input bundles from durable repository evidence;
- downloads the 295 baseline SRRs only once;
- runs baseline BWA and BLASTx recovery in parallel;
- runs EA01/EA02 same-assay BWA/BLASTx paired-tree sensitivities;
- starts CNIPG BWA- and BLASTx-baseline comparisons only after the corresponding
  baseline tree has passed its acceptance stage;
- writes one final **independent-gate** summary.

It does **not** build or authorize a combined 296/297 tree. If all three
independent gates pass, the final summary says that an explicit common
paired-locus combined tree is required before any 296/297 state can be accepted.

## External requirements

- Slurm;
- micromamba or mamba;
- network access to public SRA;
- scratch/storage sufficient for the 295 baseline SRRs and generated HybPiper,
  alignment and tree products;
- an EAzami checkout containing the code revision used to generate this handoff.

## One-command submission

```bash
export REPO_ROOT=/path/to/EAzami
bash /path/to/maximum_public_nuclear_handoff/submit_all_independent_public_gates.sh
```

Optional result roots:

```bash
export RESULT_ROOT=/scratch/.../japan_origin_global_v2
export AUGMENT_ROOT=/scratch/.../east_asia_public_augmentation
export GENOME_AUGMENT_ROOT=/scratch/.../cnipponicum_genome_augmentation
export MAXIMUM_PUBLIC_ROOT=/scratch/.../maximum_public_nuclear
```

Final independent-gate output:

```text
$MAXIMUM_PUBLIC_ROOT/independent_gate_summary.json
```

The only permitted outcomes at that stage are candidate-specific automatic
admission/manual review plus a decision about whether a **new combined tree must
be built**. A numerical 297-tip ceiling is never converted into an accepted
297-tip tree without that additional common-locus analysis.

New broad China sampling remains outside this handoff.
"""


def build(outdir: Path) -> dict[str, object]:
    if outdir.exists():
        shutil.rmtree(outdir)
    outdir.mkdir(parents=True)

    with tempfile.TemporaryDirectory(prefix="eazami-max-public-") as td:
        stage = Path(td)
        reconciliation = stage / "moreyra2025_all_sample_reconciliation.csv"
        panel_dir = stage / "panel"
        baseline = stage / "baseline_bundle"
        packs = stage / "candidate_packs"
        augmentation = stage / "ea01_ea02_augmentation_bundle"

        run_script("materialize_frozen_moreyra_reconciliation.py", "--output", reconciliation)
        if sha256(reconciliation) != MOREYRA_SHA256:
            raise ValueError("materialized Moreyra reconciliation checksum drift")
        run_script(
            "build_japan_origin_global_public_panel_v2.py",
            "--moreyra-reconciliation", reconciliation,
            "--outdir", panel_dir,
        )
        run_script(
            "build_japan_origin_global_hpc_bundle_v2.py",
            "--panel", panel_dir / "japan_origin_global_public_panel_v2.csv",
            "--outdir", baseline,
        )

        for cid in ("EA01", "EA02", "CNIPG"):
            run_script(
                "materialize_frozen_public_candidate_locus_pack.py",
                "--candidate", cid,
                "--output", packs / cid,
            )
            meta = json.loads((packs / cid / "durable_materialization.json").read_text(encoding="utf-8"))
            if meta.get("strict_locus_count") != CANDIDATE_COUNTS[cid] or meta.get("tip_id") != CANDIDATE_TIPS[cid]:
                raise ValueError(f"durable candidate pack drift: {cid}")

        run_script(
            "build_east_asia_public_augmentation_hpc_bundle.py",
            "--baseline-bundle", baseline,
            "--ea01-pack", packs / "EA01",
            "--ea02-pack", packs / "EA02",
            "--contract", ROOT / "data/evidence/east_asia_public_tree_augmentation_contract_v1.json",
            "--outdir", augmentation,
        )
        ea_handoff = outdir / "ea01_ea02_handoff"
        run_script(
            "build_east_asia_public_full_hpc_handoff.py",
            "--baseline-bundle", baseline,
            "--augmentation-bundle", augmentation,
            "--outdir", ea_handoff,
        )
        cnipg = outdir / "cnipg_bundle"
        run_script(
            "build_cirsium_nipponicum_genome_augmentation_hpc_bundle.py",
            "--baseline-bundle", ea_handoff / "baseline_bundle",
            "--genome-pack", packs / "CNIPG",
            "--gate", ROOT / "data/evidence/cirsium_nipponicum_public_genome_augmentation_gate_v1.json",
            "--outdir", cnipg,
        )

    hm, bm, cm = validate_component_manifests(outdir / "ea01_ea02_handoff", outdir / "cnipg_bundle")
    write(outdir / "90_collect_independent_gate_summaries_slurm.sh", collector_script(), 0o755)
    write(outdir / "submit_all_independent_public_gates.sh", orchestrator_script(), 0o755)
    write(outdir / "EXECUTE_ON_HPC.md", execute_readme())

    source_paths = (
        "analysis/build_maximum_public_nuclear_hpc_handoff.py",
        "analysis/build_japan_origin_global_public_panel_v2.py",
        "analysis/build_japan_origin_global_hpc_bundle_v2.py",
        "analysis/build_east_asia_public_augmentation_hpc_bundle.py",
        "analysis/build_east_asia_public_full_hpc_handoff.py",
        "analysis/build_cirsium_nipponicum_genome_augmentation_hpc_bundle.py",
        "analysis/materialize_frozen_moreyra_reconciliation.py",
        "analysis/materialize_frozen_public_candidate_locus_pack.py",
        "data/evidence/japan_origin_global_public_panel_contract_v2.json",
        "data/evidence/east_asia_public_tree_augmentation_contract_v1.json",
        "data/evidence/cirsium_nipponicum_public_genome_augmentation_gate_v1.json",
        "data/evidence/public_candidate_locus_packs_v1/manifest.json",
    )
    fingerprints = {path: sha256(ROOT / path) for path in source_paths}
    write(outdir / "source_fingerprints.json", json.dumps(fingerprints, indent=2) + "\n")

    manifest: dict[str, object] = {
        "handoff_version": "maximum_public_nuclear_hpc_handoff_v1",
        "accepted_primary_before_empirical_candidate_gates": 294,
        "baseline_public_runs": 295,
        "analysis_taxon_labels": 270,
        "candidates": {
            "EA01": {"tip_id": "PUBEA001", "strict_loci": 236, "data_type": "public_sra_target_capture"},
            "EA02": {"tip_id": "PUBEA002", "strict_loci": 239, "data_type": "public_sra_target_capture"},
            "CNIPG": {"tip_id": "AUG_ULLEUNG_CNIP2024", "strict_loci": 180, "data_type": "genome_derived_cds"},
        },
        "sample_level_candidate_ceiling": 297,
        "new_analysis_taxon_labels_at_candidate_ceiling": 0,
        "baseline_download_shared_across_all_independent_gates": True,
        "baseline_mapping_modes": ["bwa", "blastx"],
        "ea01_ea02_handoff_version": hm["handoff_version"],
        "baseline_bundle_version": bm["bundle_version"],
        "cnipg_bundle_version": cm["bundle_version"],
        "all_inputs_materialized_from_repository_evidence": True,
        "github_actions_artifact_runtime_dependency": False,
        "heavy_compute_executed_by_builder": False,
        "combined_296_or_297_tree_built_by_this_handoff": False,
        "combined_tree_requires_explicit_common_paired_locus_contract_after_independent_admission": True,
        "new_china_sampling_freeze_allowed": False,
        "final_independent_gate_product": "$MAXIMUM_PUBLIC_ROOT/independent_gate_summary.json",
    }
    write(outdir / "handoff_manifest.json", json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    build(args.outdir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
