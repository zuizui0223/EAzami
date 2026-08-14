from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis/build_maximum_public_nuclear_hpc_handoff.py"
SPEC = importlib.util.spec_from_file_location("maximum_public_handoff", SCRIPT)
assert SPEC and SPEC.loader
m = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = m
SPEC.loader.exec_module(m)


class MaximumPublicNuclearHandoffTests(unittest.TestCase):
    def test_builds_all_independent_gates_from_repository_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "handoff"
            manifest = m.build(out)

            self.assertEqual(manifest["handoff_version"], "maximum_public_nuclear_hpc_handoff_v1")
            self.assertEqual(manifest["accepted_primary_before_empirical_candidate_gates"], 294)
            self.assertEqual(manifest["baseline_public_runs"], 295)
            self.assertEqual(manifest["analysis_taxon_labels"], 270)
            self.assertEqual(manifest["sample_level_candidate_ceiling"], 297)
            self.assertEqual(manifest["new_analysis_taxon_labels_at_candidate_ceiling"], 0)
            self.assertTrue(manifest["baseline_download_shared_across_all_independent_gates"])
            self.assertTrue(manifest["all_inputs_materialized_from_repository_evidence"])
            self.assertFalse(manifest["github_actions_artifact_runtime_dependency"])
            self.assertFalse(manifest["heavy_compute_executed_by_builder"])
            self.assertFalse(manifest["combined_296_or_297_tree_built_by_this_handoff"])
            self.assertTrue(manifest["combined_tree_requires_explicit_common_paired_locus_contract_after_independent_admission"])
            self.assertFalse(manifest["new_china_sampling_freeze_allowed"])

            ea = out / "ea01_ea02_handoff"
            cn = out / "cnipg_bundle"
            self.assertTrue((ea / "submit_full_public_tree_and_augmentation.sh").is_file())
            self.assertTrue((ea / "baseline_bundle" / "execution_manifest.json").is_file())
            self.assertTrue((ea / "augmentation_bundle" / "execution_manifest.json").is_file())
            self.assertEqual(len(list((ea / "augmentation_bundle/candidate_packs/EA01/loci").glob("*.fasta"))), 236)
            self.assertEqual(len(list((ea / "augmentation_bundle/candidate_packs/EA02/loci").glob("*.fasta"))), 239)
            self.assertEqual(len(list((cn / "genome_pack/loci").glob("*.fasta"))), 180)

            top = (out / "submit_all_independent_public_gates.sh").read_text()
            self.assertIn("baseline_bwa_accept", top)
            self.assertIn("baseline_blastx_accept", top)
            self.assertIn("--dependency=afterok:\"$baseline_accept\"", top)
            self.assertIn("cnipg_cross_data_type_summary", top)
            self.assertIn("maximum_public_independent_gate_summary", top)

            collector = (out / "90_collect_independent_gate_summaries_slurm.sh").read_text()
            self.assertIn("combined_296_or_297_tree_accepted':False", collector)
            self.assertIn("combined_common_paired_locus_tree_required", collector)
            self.assertIn("new_china_sampling_freeze_allowed':False", collector)

            fingerprints = json.loads((out / "source_fingerprints.json").read_text())
            self.assertIn("analysis/build_maximum_public_nuclear_hpc_handoff.py", fingerprints)
            self.assertIn("data/evidence/public_candidate_locus_packs_v1/manifest.json", fingerprints)


if __name__ == "__main__":
    unittest.main()
