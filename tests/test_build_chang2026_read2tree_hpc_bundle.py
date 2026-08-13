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

SCRIPT = ANALYSIS / "build_chang2026_read2tree_hpc_bundle.py"
SPEC = importlib.util.spec_from_file_location("build_read2tree_hpc_bundle", SCRIPT)
assert SPEC and SPEC.loader
build = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = build
SPEC.loader.exec_module(build)

PANEL = ROOT / "sampling/chang2026_takaoense6_read2tree_panel_v1.csv"
EVIDENCE = ROOT / "data/evidence/chang2026_takaoense_morph_linked_public_samples_v1.csv"
REFS = ROOT / "sampling/read2tree_oma_reference_set_v0_2.csv"


class Read2TreeHPCBundleTests(unittest.TestCase):
    def test_panel_contract(self):
        rows = build.validate_panel(PANEL)
        self.assertEqual(len(rows), 6)
        self.assertEqual(sum(row["morph"] == "BP" for row in rows), 3)
        self.assertEqual(sum(row["morph"] == "W" for row in rows), 3)

    def test_trim_script_resolves_bundle_inputs_and_repo_root(self):
        text = build.trim_script(
            slurm=True,
            panel_name=PANEL.name,
            evidence_name=EVIDENCE.name,
        )
        self.assertIn('#SBATCH --cpus-per-task=16', text)
        self.assertIn('#SBATCH --mem=32G', text)
        self.assertIn('PANEL="${PANEL:-$SCRIPT_DIR/', text)
        self.assertIn('REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel', text)
        self.assertIn('prepare_six_trimmed_reads.sh', text)
        self.assertIn('MIN_FREE_DISK_GIB:-150', text)
        self.assertIn('trim_checkpoint=complete', text)
        self.assertNotIn('Trinity', text)

    def test_read2tree_script_uses_validated_pack_and_pinned_env(self):
        text = build.read2tree_script(
            slurm=True,
            panel_name=PANEL.name,
            evidence_name=EVIDENCE.name,
            refs_name=REFS.name,
        )
        self.assertIn('MARKER_CONTRACT:?', text)
        self.assertIn('workflow/chang2026_read2tree/envs/read2tree.yml', text)
        self.assertIn('micromamba create', text)
        self.assertIn('prepare_from_validated_marker_pack.sh', text)
        self.assertIn('run_read2tree_fast_screen.sh', text)
        self.assertIn('takaoense6_read2tree_dna.treefile', text)
        self.assertIn('read2tree_checkpoint=complete', text)

    def test_scoring_script_freezes_hypothesis_hash_and_thresholds(self):
        text = build.scoring_script(
            slurm=False,
            panel_name=PANEL.name,
            refs_name=REFS.name,
        )
        self.assertIn(build.EXPECTED_HYPOTHESIS_SHA256, text)
        self.assertIn('--thresholds 0,50,70,90', text)
        self.assertIn('run_chang2026_read2tree_scoring_contract.py', text)
        self.assertIn('scoring_checkpoint=complete', text)

    def test_submit_chain_uses_afterok_dependencies(self):
        text = build.submit_script()
        self.assertIn('dependency=afterok:"$trim_job"', text)
        self.assertIn('dependency=afterok:"$r2t_job"', text)
        self.assertIn('--chdir="$SCRIPT_DIR"', text)
        self.assertIn('MARKER_CONTRACT="$MARKER_CONTRACT"', text)

    def test_main_bundle_manifest_and_permissions(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "bundle"
            argv = sys.argv
            try:
                sys.argv = [
                    str(SCRIPT),
                    "--panel", str(PANEL),
                    "--evidence", str(EVIDENCE),
                    "--references", str(REFS),
                    "--outdir", str(out),
                ]
                self.assertEqual(build.main(), 0)
            finally:
                sys.argv = argv

            manifest = json.loads((out / "execution_manifest.json").read_text())
            self.assertEqual(manifest["sample_count"], 6)
            self.assertEqual(manifest["morph_counts"], {"BP": 3, "W": 3})
            self.assertEqual(manifest["execution_order"], ["trim", "read2tree_iqtree", "score"])
            self.assertEqual(manifest["required_external_input"]["expected_marker_count"], 400)
            self.assertEqual(manifest["required_external_input"]["expected_oma_release"], "May2026")
            self.assertEqual(
                manifest["environment_contracts"]["read2tree_source_commit"],
                "e19ad8f32a438ff7a38d9ee1d41832e1fc326a3c",
            )
            for name in (
                "run_01_trim_local.sh",
                "run_01_trim_slurm.sh",
                "run_02_read2tree_local.sh",
                "run_02_read2tree_slurm.sh",
                "run_03_score_local.sh",
                "run_03_score_slurm.sh",
                "submit_slurm_chain.sh",
            ):
                path = out / name
                self.assertTrue(path.is_file())
                self.assertTrue(path.stat().st_mode & 0o100)
            self.assertTrue((out / PANEL.name).is_file())
            self.assertTrue((out / EVIDENCE.name).is_file())
            self.assertTrue((out / REFS.name).is_file())


if __name__ == "__main__":
    unittest.main()
