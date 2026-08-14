#!/usr/bin/env python3
"""Canonical HPC builder for the 20-tip Compositae1061 rate-tree preflight.

This is the only supported HPC-bundle entry point. Shared read-recovery,
HybPiper and QC shell generators live in ``colour_rate_comp1061_hpc_primitives``;
this module owns argument parsing, corrected stage-0 preparation, manifest
emission and the scientific stop rules. No runtime monkey-patching is used.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import colour_rate_comp1061_hpc_primitives as impl

BRIDGE_VERSION = impl.BRIDGE_VERSION
LOCUS_VERSION = impl.LOCUS_VERSION
REF_SHA = impl.REF_SHA
ASTRAL_COMMIT = impl.ASTRAL_COMMIT
ASTRAL_ZIP_BLOB_SHA1 = impl.ASTRAL_ZIP_BLOB_SHA1
load = impl.load
sha256 = impl.sha256
validate = impl.validate
write = impl.write
runs_csv = impl.runs_csv
env_yml = impl.env_yml
common = impl.common
fetch_script = impl.fetch_script
hybpiper_script = impl.hybpiper_script
qc_script = impl.qc_script
submit_script = impl.submit_script


def prepare_script() -> str:
    return "#!/usr/bin/env bash\n" + common() + """
mkdir -p "$RESULT_ROOT/inputs/reference" "$RESULT_ROOT/inputs/locus_sets"
"${RUN[@]}" python "$REPO_ROOT/analysis/recover_comp1061_original_hybpiper_reference.py" \
  --outdir "$RESULT_ROOT/inputs/reference"
python - <<'PY'
import json, os, pathlib
root=pathlib.Path(os.environ['RESULT_ROOT'])
c=json.loads((root/'inputs/reference/comp1061_original_reference_contract.json').read_text())
assert c['sha256']=='77d510ef101d08a7a23a4df391d077d3b7f75482c66f7f4bea6d32cf290ced2c'
assert c['locus_count']==1061
PY

# Recreate the public Moreyra locus-filter reconstruction before exporting
# named 1061/531/241 sets. The exact published 350 remains unavailable.
"${RUN[@]}" python "$REPO_ROOT/analysis/recover_moreyra_author_repository.py" \
  --outdir "$RESULT_ROOT/inputs/moreyra_author_repo" --force
"${RUN[@]}" python "$REPO_ROOT/analysis/summarize_moreyra_locus_filter.py" \
  --audit-dir "$RESULT_ROOT/inputs/moreyra_author_repo"
"${RUN[@]}" python "$REPO_ROOT/analysis/export_moreyra_locus_manifests.py" \
  --input "$RESULT_ROOT/inputs/moreyra_author_repo/paralog_locus_filter_reconstruction.csv" \
  --outdir "$RESULT_ROOT/inputs/locus_sets"

python - <<'PY'
import hashlib, os, pathlib
root=pathlib.Path(os.environ['RESULT_ROOT'])
expected={
 'moreyra_public_1061_loci.txt':('d019a37197a9549d4a8160358c93284906f4f590a098d78e81004f04bd185b75',1061),
 'moreyra_reproducible_531_candidate_loci.txt':('3d6a1994758eb6e6cf2934435d2482fbd56cad1b526b5fd17a7891e138fc3d53',531),
 'moreyra_conservative_241_no_warning_loci.txt':('d561c6e393b1964fdd4b3acf14fda8b10f2f43923b1074cd35f86bfed07ebf73',241),
}
for name,(want_sha,want_n) in expected.items():
 p=root/'inputs/locus_sets'/name
 payload=p.read_bytes()
 got=hashlib.sha256(payload).hexdigest()
 n=sum(1 for line in payload.decode().splitlines() if line.strip())
 assert got==want_sha,(name,got,want_sha)
 assert n==want_n,(name,n,want_n)
PY

cp "$BUNDLE_DIR/bridge_contract.json" "$RESULT_ROOT/inputs/"
cp "$BUNDLE_DIR/locus_set_manifest.json" "$RESULT_ROOT/inputs/"
echo inputs_checkpoint=complete
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bridge-contract", type=Path, required=True)
    parser.add_argument("--locus-manifest", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    bridge = load(args.bridge_contract)
    locus = load(args.locus_manifest)
    tips = validate(bridge, locus)
    args.outdir.mkdir(parents=True, exist_ok=True)

    runs_csv(args.outdir / "primary_runs.csv", tips)
    write(args.outdir / "env.yml", env_yml())
    (args.outdir / "bridge_contract.json").write_bytes(args.bridge_contract.read_bytes())
    (args.outdir / "locus_set_manifest.json").write_bytes(args.locus_manifest.read_bytes())

    scripts = {
        "00_prepare_inputs_slurm.sh": prepare_script(),
        "01_fetch_trim_slurm.sh": fetch_script(),
        "02_hybpiper_bwa_slurm.sh": hybpiper_script("bwa"),
        "02b_hybpiper_blastx_slurm.sh": hybpiper_script("blastx"),
        "03_retrieve_qc_slurm.sh": qc_script(),
        "submit_bwa_chain.sh": submit_script("bwa"),
        "submit_blastx_chain.sh": submit_script("blastx"),
    }
    for name, text in scripts.items():
        write(args.outdir / name, text, 0o755)

    manifest = {
        "bundle_version": "colour_rate_comp1061_hpc_bundle_v1",
        "taxa": 20,
        "states": {"C": 17, "W": 3},
        "primary_mapping": "bwa",
        "mapping_sensitivity": "blastx",
        "target_reference_sha256": REF_SHA,
        "hybpiper_version": "2.3.4",
        "astral_source": {
            "commit": ASTRAL_COMMIT,
            "zip_git_blob_sha1": ASTRAL_ZIP_BLOB_SHA1,
        },
        "current_stage_end": "retrieve_stats_paralog_qc",
        "next_tree_stage": (
            "apply current occupancy/paralog gates to frozen 241/531/1061 locus sets, "
            "add reference outgroups, align, infer IQ-TREE gene/concat trees and ASTRAL sensitivity"
        ),
        "branch_length_tree_completed": False,
        "rate_fit_execution_allowed": False,
        "claim_limit": (
            "Bundle execution through QC does not itself create an accepted branch-length rate tree. "
            "Library-type occupancy, current paralogs, outgroup/Cirsium-monophyly and matrix "
            "sensitivities must pass before tree promotion."
        ),
    }
    write(args.outdir / "execution_manifest.json", json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
