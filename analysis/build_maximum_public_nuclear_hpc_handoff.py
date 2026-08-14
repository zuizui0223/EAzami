#!/usr/bin/env python3
"""Build the post-empirical maximum-public nuclear HPC handoff.

The accepted primary is 294 biological tips / 295 SRRs. After the real-read
candidate audit, only EA01 and CNIPG remain independent augmentation candidates.
EA02 is retained as duplicate-readset evidence but never enters this execution
graph or increments the biological-tip ceiling.
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
CANDIDATE_COUNTS = {"EA01": 236, "CNIPG": 180}
CANDIDATE_TIPS = {"EA01": "PUBEA001", "CNIPG": "AUG_ULLEUNG_CNIP2024"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, text: str, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    path.chmod(mode)


def run_script(script: str, *args: object) -> None:
    subprocess.run([PYTHON, str(ROOT / "analysis" / script), *(str(x) for x in args)], cwd=ROOT, check=True)


def validate_components(ea01_handoff: Path, cnipg_bundle: Path) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    eh = json.loads((ea01_handoff / "handoff_manifest.json").read_text(encoding="utf-8"))
    bm = json.loads((ea01_handoff / "baseline_bundle/execution_manifest.json").read_text(encoding="utf-8"))
    cm = json.loads((cnipg_bundle / "execution_manifest.json").read_text(encoding="utf-8"))
    if eh.get("handoff_version") != "ea01_public_full_hpc_handoff_v2":
        raise ValueError("EA01 full handoff version drift")
    if eh.get("candidate_ids") != ["EA01"] or eh.get("ea02_enters_biological_tree_inputs") is not False:
        raise ValueError("EA01 post-empirical handoff drift")
    if bm.get("bundle_version") != "japan_origin_global_hpc_bundle_v2" or bm.get("biological_samples") != 294 or bm.get("public_runs") != 295:
        raise ValueError("baseline bundle drift")
    if cm.get("bundle_version") != "cirsium_nipponicum_genome_augmentation_hpc_bundle_v1":
        raise ValueError("CNIPG bundle version drift")
    if cm.get("genome_strict_loci") != 180 or cm.get("baseline_focal_tips") != 294:
        raise ValueError("CNIPG inventory drift")
    return eh, bm, cm


def collector_script() -> str:
    return r'''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-max-public-summary
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=01:00:00
set -euo pipefail
AUGMENT_ROOT="${AUGMENT_ROOT:-$PWD/results/ea01_public_augmentation}"
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
if ea.get('contract_version')!='ea01_public_augmentation_sensitivity_summary_v2':
    raise SystemExit('wrong EA01 summary contract')
ea01=bool(ea['sample_tip_promotion_allowed'])
cnipg=bool(cn['automatic_sample_tip_promotion_allowed'])
both=ea01 and cnipg
out={
  'contract_version':'maximum_public_nuclear_independent_gate_summary_v2',
  'accepted_primary_before_combined_tree':294,
  'independent_candidate_gate_results':{'EA01':ea01,'CNIPG':cnipg},
  'independent_manual_review_required':{
    'EA01':bool(ea['manual_review_required']),
    'CNIPG':bool(cn['manual_review_required']),
  },
  'excluded_duplicate_controls':{
    'EA02':'duplicate_readset_pseudoreplicate_excluded_pending_explicit_provenance'
  },
  'both_independent_gates_passed':both,
  'sample_level_candidate_ceiling_if_both_pass':296,
  'new_analysis_taxon_labels_if_both_pass':0,
  'combined_296_tree_accepted':False,
  'combined_common_paired_locus_tree_required':both,
  'new_china_sampling_freeze_allowed':False,
  'next_action':(
    'build_explicit_common_paired_locus_296_tree_before_acceptance'
    if both else
    'retain_294_primary_and_review_failed_or_unresolved_independent_candidate_gates'
  ),
  'claim_boundary':'Independent EA01 and CNIPG gates do not by arithmetic create an accepted 296-tip tree; EA02 is excluded as a biological pseudoreplicate.'
}
out_path.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
PY
'''


def orchestrator_script() -> str:
    return r'''#!/usr/bin/env bash
set -euo pipefail
HANDOFF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EA="$HANDOFF_DIR/ea01_handoff"; CN="$HANDOFF_DIR/cnipg_bundle"
REPO_ROOT="${REPO_ROOT:?Set REPO_ROOT to the EAzami checkout used to build this handoff}"
RESULT_ROOT="${RESULT_ROOT:-$PWD/results/japan_origin_global_v2}"; BASELINE_RESULT_ROOT="$RESULT_ROOT"
AUGMENT_ROOT="${AUGMENT_ROOT:-$PWD/results/ea01_public_augmentation}"
GENOME_AUGMENT_ROOT="${GENOME_AUGMENT_ROOT:-$PWD/results/cnipponicum_genome_augmentation}"
MAXIMUM_PUBLIC_ROOT="${MAXIMUM_PUBLIC_ROOT:-$PWD/results/maximum_public_nuclear}"
ENV_PREFIX="${ENV_PREFIX:-$REPO_ROOT/.conda/eazami-japan-origin-global}"
export REPO_ROOT RESULT_ROOT BASELINE_RESULT_ROOT AUGMENT_ROOT GENOME_AUGMENT_ROOT MAXIMUM_PUBLIC_ROOT ENV_PREFIX
for f in "$EA/submit_full_ea01_public_tree_augmentation.sh" "$CN/20_prepare_cnipg_paired_inputs_slurm.sh" "$CN/21_align_cnipg_paired_slurm.sh" "$CN/22_gene_trees_cnipg_paired_slurm.sh" "$CN/23_concat_cnipg_paired_slurm.sh" "$CN/24_astral_cnipg_paired_slurm.sh" "$CN/25_evaluate_cnipg_paired_slurm.sh" "$CN/26_summarize_cnipg_cross_data_type_slurm.sh" "$HANDOFF_DIR/90_collect_independent_gate_summaries_slurm.sh"; do test -s "$f"; done

ea_out=$(bash "$EA/submit_full_ea01_public_tree_augmentation.sh")
printf '%s\n' "$ea_out"
bacc=$(printf '%s\n' "$ea_out" | awk -F= '$1=="baseline_bwa_accept"{print $2}')
xacc=$(printf '%s\n' "$ea_out" | awk -F= '$1=="baseline_blastx_accept"{print $2}')
ea_summary=$(printf '%s\n' "$ea_out" | awk -F= '$1=="ea01_cross_mapping_summary"{print $2}')
for value in "$bacc" "$xacc" "$ea_summary"; do [[ "$value" =~ ^[0-9]+([_;].*)?$ ]] || { echo "failed to parse EA01 handoff job id: $value" >&2; exit 2; }; done

submit_cnipg_mode() {
  local mode="$1" baseline_accept="$2"; local prep aln gene con ast ev
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
ea01_cross_mapping_summary=$ea_summary
cnipg_bwa_evaluate=$cn_bwa_eval
cnipg_blastx_evaluate=$cn_blastx_eval
cnipg_cross_data_type_summary=$cn_summary
maximum_public_independent_gate_summary=$final
EOF
'''


def execute_readme() -> str:
    return """# Maximum public nuclear tree — post-empirical HPC handoff\n\nCurrent independent candidates are **EA01 + CNIPG only**. EA02 is excluded from biological-tip counting because the real-read audit is overwhelmingly consistent with re-deposition of the baseline *C. sairamense* read library.\n\nThis handoff reconstructs the accepted 294-tip/295-SRR baseline, runs BWA and BLASTx once, evaluates EA01 under a two-scenario same-locus gate, evaluates CNIPG under its cross-data-type gate, and writes one independent-gate summary.\n\nIf both candidates pass, the numerical ceiling is **296 tips / 0 new labels**. That is not an accepted combined tree; a fresh common-paired-locus 296 tree is still required.\n\nRun with `REPO_ROOT=/path/to/EAzami bash submit_all_independent_public_gates.sh`.\n"""


def build(outdir: Path) -> dict[str, object]:
    if outdir.exists(): shutil.rmtree(outdir)
    outdir.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix="eazami-max-public-v2-") as td:
        stage=Path(td); reconciliation=stage/"moreyra2025_all_sample_reconciliation.csv"; panel_dir=stage/"panel"; baseline=stage/"baseline_bundle"; packs=stage/"candidate_packs"; aug=stage/"ea01_augmentation_bundle"
        run_script("materialize_frozen_moreyra_reconciliation.py", "--output", reconciliation)
        if sha256(reconciliation)!=MOREYRA_SHA256: raise ValueError("Moreyra reconciliation checksum drift")
        run_script("build_japan_origin_global_public_panel_v2.py", "--moreyra-reconciliation", reconciliation, "--outdir", panel_dir)
        run_script("build_japan_origin_global_hpc_bundle_v2.py", "--panel", panel_dir/"japan_origin_global_public_panel_v2.csv", "--outdir", baseline)
        for cid in ("EA01","CNIPG"):
            run_script("materialize_frozen_public_candidate_locus_pack.py", "--candidate", cid, "--output", packs/cid)
            meta=json.loads((packs/cid/"durable_materialization.json").read_text(encoding="utf-8"))
            if meta.get("strict_locus_count")!=CANDIDATE_COUNTS[cid] or meta.get("tip_id")!=CANDIDATE_TIPS[cid]: raise ValueError(f"durable candidate pack drift: {cid}")
        run_script("build_ea01_public_augmentation_hpc_bundle.py", "--baseline-bundle", baseline, "--ea01-pack", packs/"EA01", "--contract", ROOT/"data/evidence/ea01_public_tree_augmentation_contract_v2.json", "--evaluator-contract", ROOT/"data/evidence/east_asia_public_tree_augmentation_contract_v1.json", "--outdir", aug)
        ea01_handoff=outdir/"ea01_handoff"
        run_script("build_ea01_public_full_hpc_handoff.py", "--baseline-bundle", baseline, "--augmentation-bundle", aug, "--outdir", ea01_handoff)
        cnipg=outdir/"cnipg_bundle"
        run_script("build_cirsium_nipponicum_genome_augmentation_hpc_bundle.py", "--baseline-bundle", ea01_handoff/"baseline_bundle", "--genome-pack", packs/"CNIPG", "--gate", ROOT/"data/evidence/cirsium_nipponicum_public_genome_augmentation_gate_v1.json", "--outdir", cnipg)

    eh,bm,cm=validate_components(outdir/"ea01_handoff",outdir/"cnipg_bundle")
    write(outdir/"90_collect_independent_gate_summaries_slurm.sh",collector_script(),0o755)
    write(outdir/"submit_all_independent_public_gates.sh",orchestrator_script(),0o755)
    write(outdir/"EXECUTE_ON_HPC.md",execute_readme())
    source_paths=(
      "analysis/build_maximum_public_nuclear_hpc_handoff.py",
      "analysis/build_japan_origin_global_public_panel_v2.py",
      "analysis/build_japan_origin_global_hpc_bundle_v2.py",
      "analysis/build_ea01_public_augmentation_hpc_bundle.py",
      "analysis/build_ea01_public_full_hpc_handoff.py",
      "analysis/prepare_ea01_public_augmentation_tree_inputs.py",
      "analysis/summarize_ea01_public_augmentation_sensitivities.py",
      "analysis/build_cirsium_nipponicum_genome_augmentation_hpc_bundle.py",
      "analysis/materialize_frozen_moreyra_reconciliation.py",
      "analysis/materialize_frozen_public_candidate_locus_pack.py",
      "data/evidence/japan_origin_global_public_panel_contract_v2.json",
      "data/evidence/ea01_public_tree_augmentation_contract_v2.json",
      "data/evidence/cirsium_nipponicum_public_genome_augmentation_gate_v1.json",
      "data/evidence/east_asia_public_candidate_disposition_v2.json",
      "data/evidence/public_candidate_empirical_quartet_2026-08-14.json",
      "data/evidence/public_candidate_locus_packs_v1/manifest.json",
    )
    write(outdir/"source_fingerprints.json",json.dumps({p:sha256(ROOT/p) for p in source_paths},indent=2)+"\n")
    manifest: dict[str,object]={
      "handoff_version":"maximum_public_nuclear_hpc_handoff_v2",
      "accepted_primary_before_empirical_candidate_gates":294,
      "baseline_public_runs":295,
      "analysis_taxon_labels":270,
      "independent_candidates":{
        "EA01":{"tip_id":"PUBEA001","strict_loci":236,"data_type":"public_sra_target_capture"},
        "CNIPG":{"tip_id":"AUG_ULLEUNG_CNIP2024","strict_loci":180,"data_type":"genome_derived_cds"},
      },
      "excluded_duplicate_controls":{
        "EA02":{"tip_id":"PUBEA002","strict_loci":239,"counts_as_independent_tip":False,"status":"duplicate_readset_pseudoreplicate_excluded_pending_explicit_provenance"}
      },
      "sample_level_candidate_ceiling":296,
      "new_analysis_taxon_labels_at_candidate_ceiling":0,
      "baseline_download_shared_across_all_independent_gates":True,
      "baseline_mapping_modes":["bwa","blastx"],
      "ea01_handoff_version":eh["handoff_version"],
      "baseline_bundle_version":bm["bundle_version"],
      "cnipg_bundle_version":cm["bundle_version"],
      "all_inputs_materialized_from_repository_evidence":True,
      "github_actions_artifact_runtime_dependency":False,
      "heavy_compute_executed_by_builder":False,
      "combined_296_tree_built_by_this_handoff":False,
      "combined_tree_requires_explicit_common_paired_locus_contract_after_independent_admission":True,
      "new_china_sampling_freeze_allowed":False,
      "final_independent_gate_product":"$MAXIMUM_PUBLIC_ROOT/independent_gate_summary.json",
    }
    write(outdir/"handoff_manifest.json",json.dumps(manifest,indent=2)+"\n"); print(json.dumps(manifest,indent=2)); return manifest


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--outdir",type=Path,required=True); args=parser.parse_args(); build(args.outdir); return 0


if __name__=="__main__": raise SystemExit(main())
