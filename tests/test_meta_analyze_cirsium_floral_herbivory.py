import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis" / "meta_analyze_cirsium_floral_herbivory.py"
INPUT = ROOT / "data" / "evidence" / "cirsium_floral_herbivory_experimental_effects_v1.csv"
FROZEN = ROOT / "data" / "evidence" / "cirsium_floral_herbivory_meta_pilot_v1.json"


class CirsiumFloralHerbivoryMetaTest(unittest.TestCase):
    def test_rebuild_matches_frozen_result(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "result.json"
            subprocess.run(
                [sys.executable, str(SCRIPT), "--input", str(INPUT), "--output", str(output)],
                check=True,
            )
            observed = json.loads(output.read_text(encoding="utf-8"))
            expected = json.loads(FROZEN.read_text(encoding="utf-8"))
            self.assertEqual(observed, expected)

    def test_pilot_has_real_quantitative_signal_and_guardrails(self) -> None:
        result = json.loads(FROZEN.read_text(encoding="utf-8"))
        self.assertEqual(result["coverage"]["included_effect_rows"], 5)
        self.assertEqual(result["coverage"]["independent_study_clusters"], 4)
        self.assertEqual(
            result["coverage"]["pending_raw_data_studies"],
            ["AdhikariRussell2014", "WestLouda2021"],
        )
        meta = result["random_effects"]
        self.assertGreater(meta["pooled_r"], 0)
        self.assertGreater(meta["ci95_r"][0], 0)
        self.assertAlmostEqual(meta["pooled_r"], 0.380907309405, places=12)
        self.assertAlmostEqual(meta["I2_percent"], 68.352585105279, places=12)
        for row in result["leave_one_study_out"]:
            self.assertGreater(row["pooled_r"], 0)
            self.assertGreater(row["ci95_r"][0], 0)
        self.assertEqual(
            result["publication_gate"]["status"],
            "pilot_quantitative_meta_not_publication_grade",
        )


if __name__ == "__main__":
    unittest.main()
