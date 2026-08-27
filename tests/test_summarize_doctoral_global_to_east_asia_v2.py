from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data/evidence/doctoral_global_to_east_asia_evidence_ladder_v2.csv"
SUMMARY_PATH = ROOT / "data/evidence/doctoral_global_to_east_asia_summary_v2.json"
SCRIPT = ROOT / "analysis/summarize_doctoral_global_to_east_asia_v2.py"


class DoctoralEvidenceLadderV2Tests(unittest.TestCase):
    def test_frozen_ladder_has_expected_order_and_boundaries(self):
        rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8", newline="")))
        self.assertEqual([r["order_id"] for r in rows], [f"L{i}" for i in range(10)])
        by = {r["order_id"]: r for r in rows}
        self.assertIn("Azami is observational phenomics", by["L0"]["claim_boundary"])
        self.assertIn("RR=2.674", by["L2"]["meta_or_literature_result"])
        self.assertIn("minimum of 5 orientation changes", by["L3"]["eazami_self_analysis"])
        self.assertIn("C=17/W=3", by["L4"]["eazami_self_analysis"])
        self.assertEqual(by["L6"]["meta_status"], "weakened_general_hypothesis")
        self.assertIn("common-lability", by["L8"]["new_hypothesis_or_prediction"])
        self.assertIn("adaptive radiation", by["L8"]["claim_boundary"].lower())

    def test_recomputed_summary_matches_frozen_summary(self):
        frozen = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as td:
            # The script writes to the canonical path, so preserve and restore it.
            old = SUMMARY_PATH.read_bytes()
            try:
                subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True, capture_output=True, text=True)
                recomputed = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
            finally:
                SUMMARY_PATH.write_bytes(old)
        self.assertEqual(frozen, recomputed)

    def test_summary_keeps_meta_and_empirical_frontiers_separate(self):
        x = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
        self.assertEqual(x["dissertation_placement"]["series"], "Azami")
        self.assertEqual(x["dissertation_placement"]["chapter"], 2)
        self.assertIn("global_spatial_observational", x["dissertation_placement"]["chapter_1_boundary"])
        self.assertIn("repeated_transition", x["dissertation_placement"]["chapter_2_unit"])
        self.assertIn("Chapter 1", x["architecture"][0])
        self.assertIn("Chapter 2", x["architecture"][1])
        self.assertIn("defensive_envelope", x["chapter_2_gate_state"]["FDT1"])
        self.assertIn("readiness_registry_only", x["chapter_2_gate_state"]["FDT2"])
        self.assertIn("23_study_clusters", x["chapter_2_gate_state"]["FDT2"])
        self.assertIn("zero_primary_external_transition_event", x["chapter_2_gate_state"]["FDT3"])
        self.assertIn("not_all_topology_robust", x["chapter_2_gate_state"]["FDT4"])
        self.assertIn("closed_without_machine_readable_dated_tree", x["chapter_2_gate_state"]["FDT5_FDT7_absolute_time"])
        self.assertEqual(x["meta_conclusions"]["selection_mosaic"], "working_general_support")
        self.assertEqual(x["meta_conclusions"]["stickiness_general_defence"], "weakened")
        self.assertIn("external_mechanism_and_fitness_calibrated", x["meta_conclusions"]["phyllary_spine_defence"])
        self.assertIn("bounded_extraction_ready", x["meta_conclusions"]["reproductive_flavonoid_thermoprotection"])
        self.assertEqual(
            x["self_analysis_resolutions"]["orientation"],
            "minimum_five_state_changes_on_all_six_topologies_direction_and_ancestor_unresolved",
        )
        self.assertEqual(x["competing_hypothesis"], "shared_common_lability_axis")
        self.assertEqual(
            x["doctoral_frontier"]["adaptive_radiation_gate"],
            "requires_causal_trait_mechanism_reproductive_fitness_link",
        )


if __name__ == "__main__":
    unittest.main()
