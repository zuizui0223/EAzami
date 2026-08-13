import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = REPO_ROOT / "analysis"
if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))

import run_chang2026_read2tree_scoring_contract as mod


class Read2TreeScoringContractTests(unittest.TestCase):
    def test_current_frozen_hypotheses_validate_with_exact_sha(self):
        result = mod.validate_scientific_contract(
            frozen=mod.DEFAULT_FROZEN,
            nearest=mod.DEFAULT_NEAREST,
            robustness=mod.DEFAULT_ROBUSTNESS,
            expected_sha256=mod.DEFAULT_EXPECTED_SHA256,
        )
        self.assertEqual(result["validated_hypothesis_count"], 8)
        self.assertEqual(result["contract_status"], "validated")
        self.assertEqual(
            result["frozen_hypothesis_sha256"],
            mod.DEFAULT_EXPECTED_SHA256,
        )
        self.assertEqual(result["hypothesis_ids"][0], "H_REG_PUBLISHED")
        self.assertEqual(
            result["hypothesis_ids"][1:],
            [f"H_LOSS_ONLY_RF4_{i:02d}" for i in range(1, 8)],
        )

    def test_wrong_expected_sha_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "SHA256 changed"):
            mod.validate_scientific_contract(
                frozen=mod.DEFAULT_FROZEN,
                nearest=mod.DEFAULT_NEAREST,
                robustness=mod.DEFAULT_ROBUSTNESS,
                expected_sha256="0" * 64,
            )

    def test_modified_frozen_rows_are_rejected_before_hash_check(self):
        rows = mod.freeze.read_csv(mod.DEFAULT_FROZEN)
        rows[1]["topology_newick"] = "(stale,topology);"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stale.csv"
            import csv
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                writer.writeheader(); writer.writerows(rows)
            with self.assertRaisesRegex(ValueError, "differs from current sources"):
                mod.validate_scientific_contract(
                    frozen=path,
                    nearest=mod.DEFAULT_NEAREST,
                    robustness=mod.DEFAULT_ROBUSTNESS,
                    expected_sha256=mod.DEFAULT_EXPECTED_SHA256,
                )


if __name__ == "__main__":
    unittest.main()
