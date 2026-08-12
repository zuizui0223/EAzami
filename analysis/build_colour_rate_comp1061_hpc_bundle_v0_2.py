#!/usr/bin/env python3
"""Corrected v0.2 driver for the 20-tip Compositae1061 HPC bundle.

v0.1 correctly froze the scientific inputs and HybPiper mapping modes, but a
pre-execution audit found three shell-contract bugs in stage 0:

1. RESULT_ROOT was a shell variable but not exported to the inline Python hash
   check;
2. the Moreyra public audit had to be followed by
   ``summarize_moreyra_locus_filter.py`` before named locus manifests could be
   exported;
3. ``export_moreyra_locus_manifests.py`` accepts ``--input``, not the stale
   ``--locus-filter`` option used by the first generated script.

This wrapper patches only those execution-contract details.  The 20 frozen
runs, BWA-primary/BLASTx-sensitivity design and scientific claim boundaries are
unchanged.
"""

from __future__ import annotations

import sys

import build_colour_rate_comp1061_hpc_bundle as impl

ORIGINAL_COMMON = impl.common


def common_v0_2() -> str:
    text = ORIGINAL_COMMON()
    needle = 'ENV_PREFIX="${ENV_PREFIX:-$REPO_ROOT/.conda/eazami-colour-rate-comp1061}"\n'
    replacement = needle + 'export REPO_ROOT RESULT_ROOT ENV_PREFIX\n'
    if needle not in text:
        raise RuntimeError("Unable to patch v0.1 common shell header")
    return text.replace(needle, replacement, 1)


def prepare_script_v0_2() -> str:
    return "#!/usr/bin/env bash\n" + common_v0_2() + """
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
# named 1061/531/241 sets.  The exact published 350 remains unavailable.
"${RUN[@]}" python "$REPO_ROOT/analysis/recover_moreyra_author_repository.py" \
  --outdir "$RESULT_ROOT/inputs/moreyra_author_repo" --force
"${RUN[@]}" python "$REPO_ROOT/analysis/summarize_moreyra_locus_filter.py" \
  --audit-dir "$RESULT_ROOT/inputs/moreyra_author_repo"
"${RUN[@]}" python "$REPO_ROOT/analysis/export_moreyra_locus_manifests.py" \
  --input "$RESULT_ROOT/inputs/moreyra_author_repo/paralog_locus_filter_reconstruction.csv" \
  --outdir "$RESULT_ROOT/inputs/locus_sets"

python - <<'PY'
import hashlib, json, os, pathlib
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


def main() -> None:
    # All scripts produced by the v0.1 implementation resolve ``common`` at
    # call time, so patching the module globals upgrades fetch/HybPiper/QC
    # scripts as well as the stage-0 script.
    impl.common = common_v0_2
    impl.prepare_script = prepare_script_v0_2
    impl.main()


if __name__ == "__main__":
    main()
