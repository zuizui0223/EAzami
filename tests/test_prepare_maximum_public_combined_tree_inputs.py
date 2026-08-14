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
import prepare_maximum_public_combined_tree_inputs as combined  # noqa: E402


class MaximumPublicCombinedTreeInputsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        cls.handoff = cls.root / "handoff"
        maximum_handoff.build(cls.handoff)
        cls.baseline = cls.handoff / "ea01_ea02_handoff/baseline_bundle"
        cls.ea01 = cls.handoff / "ea01_ea02_handoff/augmentation_bundle/candidate_packs/EA01"
        cls.ea02 = cls.handoff / "ea01_ea02_handoff/augmentation_bundle/candidate_packs/EA02"
        cls.cnipg = cls.handoff / "cnipg_bundle/genome_pack"
        cls.primary = cls.root / "primary_inputs"
        (cls.primary / "loci_unaligned").mkdir(parents=True)

        def loci(path: Path):
            return [x for x in (path / "strict_recovered_loci.txt").read_text().splitlines() if x]

        e1 = loci(cls.ea01)
        e2 = set(loci(cls.ea02))
        cn = set(loci(cls.cnipg))
        common = [x for x in e1 if x in e2 and x in cn]
        if len(common) < 100:
            raise AssertionError(f"durable four-way candidate intersection unexpectedly below 100: {len(common)}")
        cls.common100 = common[:100]
        (cls.primary / "eligible_loci.txt").write_text("".join(x + "\n" for x in cls.common100))

        import csv
        with (cls.baseline / "sample_manifest.csv").open() as handle:
            first = next(csv.DictReader(handle))["tip_id"]
        for locus in cls.common100:
            (cls.primary / "loci_unaligned" / f"{locus}.fasta").write_text(
                f">{first}\nACGTACGT\n>OUTGROUP_lett\nACGTACGA\n>OUTGROUP_sunf\nACGTACGG\n"
            )

        cls.gate = cls.root / "independent_gate_summary.json"
        cls.gate.write_text(json.dumps({
            "contract_version": "maximum_public_nuclear_independent_gate_summary_v1",
            "accepted_primary_before_combined_tree": 294,
            "independent_candidate_gate_results": {"EA01": True, "EA02": True, "CNIPG": True},
            "independent_manual_review_required": {"EA01": False, "EA02": False, "CNIPG": False},
            "all_three_independent_gates_passed": True,
            "sample_level_candidate_ceiling_if_all_three_pass": 297,
            "new_analysis_taxon_labels_if_all_three_pass": 0,
            "combined_296_or_297_tree_accepted": False,
            "combined_common_paired_locus_tree_required": True,
            "new_china_sampling_freeze_allowed": False,
        }, indent=2) + "\n")

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def prepare(self, gate: Path | None = None, minimum: int = 100):
        out = self.root / f"combined_{self._testMethodName}_{minimum}"
        return combined.prepare(
            primary_inputs=self.primary,
            baseline_manifest=self.baseline / "sample_manifest.csv",
            baseline_species_map=self.baseline / "astral_species_map.csv",
            ea01_pack=self.ea01,
            ea02_pack=self.ea02,
            cnipg_pack=self.cnipg,
            independent_gate_summary=gate or self.gate,
            outdir=out,
            minimum_common_loci=minimum,
        ), out

    def test_all_eight_scenarios_use_one_common_locus_set(self):
        summary, out = self.prepare()
        self.assertTrue(summary["independent_gate_prerequisite_passed"])
        self.assertEqual(summary["four_way_common_paired_loci"], 100)
        self.assertEqual(summary["scenario_count"], 8)
        self.assertTrue(summary["all_eight_scenarios_use_identical_locus_set"])
        self.assertEqual(summary["new_analysis_taxon_labels_added"], 0)
        self.assertFalse(summary["combined_tree_acceptance_pre_authorized"])
        self.assertFalse(summary["new_china_sampling_freeze_allowed"])
        self.assertEqual(summary["scenario_focal_tip_counts"]["baseline294"], 294)
        self.assertEqual(summary["scenario_focal_tip_counts"]["ea01_ea02_cnipg_297"], 297)
        self.assertEqual(len((out / "ea01_ea02_cnipg_297/eligible_loci.txt").read_text().splitlines()), 100)
        self.assertEqual(len((out / "ea01_ea02_cnipg_297/primary_runs.csv").read_text().splitlines()) - 1, 297)
        self.assertEqual(len(list((out / "ea01_ea02_cnipg_297/loci_unaligned").glob("*.fasta"))), 100)

        import csv
        rows = list(csv.DictReader((out / "ea01_ea02_cnipg_297/astral_species_map.csv").open()))
        by_taxon = {row["analysis_taxon_label"]: row for row in rows}
        self.assertIn("PUBEA001", by_taxon["Cirsium nipponicum var. yoshinoi"]["tip_ids"])
        self.assertIn("PUBEA002", by_taxon["Cirsium sairamense"]["tip_ids"])
        self.assertIn("AUG_ULLEUNG_CNIP2024", by_taxon["Cirsium nipponicum"]["tip_ids"])

    def test_independent_gate_failure_blocks_combined_inputs(self):
        bad = self.root / "bad_gate.json"
        data = json.loads(self.gate.read_text())
        data["independent_candidate_gate_results"]["EA02"] = False
        data["all_three_independent_gates_passed"] = False
        data["combined_common_paired_locus_tree_required"] = False
        bad.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "all three independent candidate gates must pass"):
            self.prepare(gate=bad)

    def test_minimum_common_locus_threshold_cannot_be_relaxed(self):
        with self.assertRaisesRegex(ValueError, "cannot be relaxed below 100"):
            self.prepare(minimum=99)


if __name__ == "__main__":
    unittest.main()
