import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "analysis" / "summarize_cirsium_interaction_evidence.py"
INPUT = REPO_ROOT / "data" / "evidence" / "cirsium_interaction_evidence_seed_v1.csv"
FROZEN = REPO_ROOT / "data" / "evidence" / "cirsium_interaction_evidence_summary_v1.json"


class CirsiumInteractionEvidenceTest(unittest.TestCase):
    def test_rebuild_matches_frozen_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "summary.json"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--input",
                    str(INPUT),
                    "--output",
                    str(output),
                ],
                check=True,
            )
            self.assertEqual(
                json.loads(output.read_text(encoding="utf-8")),
                json.loads(FROZEN.read_text(encoding="utf-8")),
            )

    def test_current_seed_has_decision_relevant_shape(self) -> None:
        with INPUT.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        summary = json.loads(FROZEN.read_text(encoding="utf-8"))

        self.assertEqual(len(rows), 11)
        self.assertEqual(summary["coverage"]["independent_studies"], 10)
        self.assertEqual(summary["coverage"]["taxa"], 9)
        self.assertEqual(summary["coverage"]["direct_capitulum_rows"], 9)
        self.assertEqual(
            summary["interaction_domain_independent_studies"][
                "pre_dispersal_seed_predation"
            ],
            4,
        )
        self.assertEqual(
            summary["aim2_module_gate"]["head_orientation"]["direct_rows"], 0
        )
        self.assertEqual(
            summary["aim2_module_gate"]["flower_colour"]["direct_rows"], 0
        )
        self.assertEqual(
            summary["aim2_module_gate"]["involucre_spine"]["direct_rows"], 0
        )
        self.assertEqual(
            summary["aim2_module_gate"]["stickiness"]["manipulative_rows"], 1
        )
        self.assertEqual(
            summary["effect_size_meta_analysis_gate"]["status"],
            "not_yet_authorized",
        )


if __name__ == "__main__":
    unittest.main()
