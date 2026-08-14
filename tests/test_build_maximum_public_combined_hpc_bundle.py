from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "analysis"
if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))

import build_maximum_public_nuclear_hpc_handoff as maximum_handoff  # noqa: E402
import build_maximum_public_combined_hpc_bundle as combined_hpc  # noqa: E402
import summarize_maximum_public_combined_sensitivities as summarizer  # noqa: E402


class MaximumPublicCombinedHPCBundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        cls.handoff = cls.root / "handoff"
        maximum_handoff.build(cls.handoff)
        cls.bundle = cls.root / "combined_bundle"
        cls.manifest = combined_hpc.build(cls.handoff, cls.bundle)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_bundle_contract_is_fail_closed(self):
        m = self.manifest
        self.assertEqual(m["bundle_version"], "maximum_public_combined_hpc_bundle_v1")
        self.assertEqual(m["prerequisite_independent_gate_contract"], "maximum_public_nuclear_independent_gate_summary_v1")
        self.assertEqual(m["independent_candidates_required_to_pass"], ["EA01", "EA02", "CNIPG"])
        self.assertEqual(m["baseline_focal_tips"], 294)
        self.assertEqual(m["scenario_count"], 8)
        self.assertEqual(m["final_scenario"], "ea01_ea02_cnipg_297")
        self.assertEqual(m["mapping_modes"], ["bwa", "blastx"])
        self.assertEqual(m["minimum_four_way_common_loci"], 100)
        self.assertTrue(m["all_scenarios_same_locus_set_within_mode"])
        self.assertTrue(m["blastx_ea01_ea02_packs_from_independent_heavy_run"])
        self.assertTrue(m["cnipg_pack_fixed_across_mapping_modes"])
        self.assertFalse(m["combined_297_acceptance_pre_authorized"])
        self.assertEqual(m["new_analysis_taxon_labels_added"], 0)
        self.assertFalse(m["new_china_sampling_freeze_allowed"])
        self.assertFalse(m["heavy_compute_executed_by_builder"])

        required = {
            "40_prepare_combined_inputs_slurm.sh",
            "41_align_combined_slurm.sh",
            "42_gene_trees_combined_slurm.sh",
            "43_concat_combined_slurm.sh",
            "44_astral_combined_slurm.sh",
            "45_evaluate_combined_slurm.sh",
            "46_summarize_combined_slurm.sh",
            "submit_combined_after_independent_pass.sh",
        }
        self.assertTrue(required <= {p.name for p in self.bundle.glob("*.sh")})
        submit = (self.bundle / "submit_combined_after_independent_pass.sh").read_text()
        self.assertIn("independent_candidate_gate_results", submit)
        self.assertIn("combined_296_or_297_tree_accepted", submit)
        self.assertIn("combined_common_paired_locus_tree_required", submit)
        self.assertIn("submit_mode bwa", submit)
        self.assertIn("submit_mode blastx", submit)

    def _synthetic_mode(self, root: Path, mode: str, *, fail_scenario: str | None = None) -> None:
        mode_root = root / mode
        paired = mode_root / "paired_inputs"
        evaluation = mode_root / "evaluation"
        paired.mkdir(parents=True)
        evaluation.mkdir(parents=True)
        (paired / "combined_input_summary.json").write_text(json.dumps({
            "contract_version": "maximum_public_combined_tree_inputs_v1",
            "independent_gate_prerequisite_passed": True,
            "four_way_common_paired_loci": 120 if mode == "bwa" else 110,
            "minimum_four_way_common_loci": 100,
            "all_eight_scenarios_use_identical_locus_set": True,
            "scenario_count": 8,
            "combined_tree_acceptance_pre_authorized": False,
        }))
        for scenario, candidates in summarizer.SCENARIOS.items():
            for cid in candidates:
                passed = scenario != fail_scenario
                (evaluation / f"{scenario}_{cid}_concat.json").write_text(json.dumps({
                    "shared_baseline_focal_tips": 294,
                    "unrooted_rf_distance_on_shared_baseline_tips": 0 if passed else 2,
                    "exact_shared_tip_backbone_invariance": passed,
                    "same_taxon_among_nearest_baseline_tips": True,
                    "candidate_nearest_baseline_tip_ids": ["JOG0001"],
                }))
            passed = scenario != fail_scenario
            (evaluation / f"{scenario}_astral_backbone.json").write_text(json.dumps({
                "unrooted_rf_distance_on_shared_species": 0 if passed else 2,
                "exact_shared_species_backbone_invariance": passed,
            }))

    def test_summarizer_accepts_only_all_modes_all_subset_scenarios(self):
        root = self.root / "synthetic_pass"
        self._synthetic_mode(root, "bwa")
        self._synthetic_mode(root, "blastx")
        result = summarizer.summarize(root)
        self.assertTrue(result["all_modes_all_subset_scenarios_passed"])
        self.assertTrue(result["combined_297_sample_tree_acceptance_allowed"])
        self.assertEqual(result["resulting_sample_level_tip_count_if_accepted"], 297)
        self.assertEqual(result["new_analysis_taxon_labels_added_if_accepted"], 0)
        self.assertFalse(result["new_china_sampling_freeze_allowed"])
        self.assertFalse(result["flower_colour_history_claim_changed_by_this_gate"])
        self.assertFalse(result["manual_review_required"])

    def test_one_subset_failure_keeps_primary_at_294(self):
        root = self.root / "synthetic_fail"
        self._synthetic_mode(root, "bwa")
        self._synthetic_mode(root, "blastx", fail_scenario="ea01_cnipg_296")
        result = summarizer.summarize(root)
        self.assertFalse(result["all_modes_all_subset_scenarios_passed"])
        self.assertFalse(result["combined_297_sample_tree_acceptance_allowed"])
        self.assertEqual(result["resulting_sample_level_tip_count_if_accepted"], 294)
        self.assertTrue(result["manual_review_required"])


if __name__ == "__main__":
    unittest.main()
