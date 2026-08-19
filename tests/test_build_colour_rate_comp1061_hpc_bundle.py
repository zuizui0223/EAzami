from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "analysis"
if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))
P = ANALYSIS / "build_colour_rate_comp1061_hpc_bundle.py"
S = importlib.util.spec_from_file_location("hpc", P)
assert S and S.loader
m = importlib.util.module_from_spec(S)
sys.modules[S.name] = m
S.loader.exec_module(m)
B = ROOT / "data/evidence/colour_rate_comp1061_bridge_artifact_contract_v1.json"
L = ROOT / "data/evidence/moreyra_public_locus_set_manifest_v1.json"


class ColourRateHPCBundleTests(unittest.TestCase):
    def build_bundle(self, out: Path) -> None:
        old = sys.argv
        sys.argv = [
            "x",
            "--bridge-contract",
            str(B),
            "--locus-manifest",
            str(L),
            "--outdir",
            str(out),
        ]
        try:
            m.main()
        finally:
            sys.argv = old

    def test_contract(self):
        self.assertEqual(len(m.validate(m.load(B), m.load(L))), 20)

    def test_corrected_stage0_contract_is_canonical(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            self.build_bundle(out)
            text = (out / "00_prepare_inputs_slurm.sh").read_text()
            self.assertIn("export REPO_ROOT RESULT_ROOT ENV_PREFIX", text)
            self.assertIn("summarize_moreyra_locus_filter.py", text)
            self.assertIn("export_moreyra_locus_manifests.py", text)
            self.assertIn(
                '--input "$RESULT_ROOT/inputs/moreyra_author_repo/paralog_locus_filter_reconstruction.csv"',
                text,
            )
            self.assertNotIn("--locus-filter", text)
            self.assertIn("os.environ['RESULT_ROOT']", text)
            self.assertIn(
                "d561c6e393b1964fdd4b3acf14fda8b10f2f43923b1074cd35f86bfed07ebf73",
                text,
            )

    def test_mapping_and_claim_boundaries_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            self.build_bundle(out)
            x = json.loads((out / "execution_manifest.json").read_text())
            self.assertFalse(x["branch_length_tree_completed"])
            self.assertFalse(x["rate_fit_execution_allowed"])
            self.assertEqual(x["primary_mapping"], "bwa")
            self.assertEqual(x["mapping_sensitivity"], "blastx")
            bwa = (out / "02_hybpiper_bwa_slurm.sh").read_text()
            blast = (out / "02b_hybpiper_blastx_slurm.sh").read_text()
            self.assertIn("--bwa", bwa)
            self.assertNotIn("--bwa", blast)
            self.assertIn("--no_intronerate", bwa)
            self.assertEqual(sum(1 for _ in (out / "primary_runs.csv").open()) - 1, 20)


if __name__ == "__main__":
    unittest.main()
