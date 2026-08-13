#!/usr/bin/env python3
"""Tests for the deterministic Moreyra East Asia raw-read pilot builder."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "analysis" / "build_moreyra_reanalysis_pilot.py"
SPEC = importlib.util.spec_from_file_location("build_moreyra_reanalysis_pilot", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
sys.modules["build_moreyra_reanalysis_pilot"] = mod
SPEC.loader.exec_module(mod)


class MoreyraReanalysisPilotTests(unittest.TestCase):
    @staticmethod
    def row(
        tree_code: str,
        biosample: str,
        run: str,
        *,
        region: str = "Japan",
        scope: str = "core_east_asia",
        relation: str = "exact",
        priority: str = "low",
    ) -> dict[str, str]:
        return {
            "tree_code": tree_code,
            "published_species": tree_code,
            "biosample": biosample,
            "voucher_and_herbarium": f"voucher {tree_code}",
            "sra_scientific_name": tree_code,
            "library_name": tree_code.replace(" ", "-") + "_LIB",
            "experiment": "SRX1",
            "run": run,
            "region_class": region,
            "scope_class": scope,
            "sra_link_status": "linked_runinfo",
            "tree_code_vs_sra_name": relation,
            "name_reconciliation_priority": priority,
        }

    def test_select_exact_target(self) -> None:
        target = {
            "tree_code": "Cirsium testii",
            "biosample": "SAMN1",
            "role": "test_anchor",
            "rationale": "test",
            "allow_high_name_conflict": False,
        }
        result = mod.select_target(
            [self.row("Cirsium testii", "SAMN1", "SRR1")], target, 1
        )
        self.assertEqual(result["biosample"], "SAMN1")
        self.assertEqual(result["runs"], "SRR1")
        self.assertEqual(result["name_reconciliation_required"], "false")

    def test_high_conflict_requires_explicit_permission(self) -> None:
        target = {
            "tree_code": "Cirsium coryletorum",
            "biosample": "SAMN2",
            "role": "name_test",
            "rationale": "test",
            "allow_high_name_conflict": False,
        }
        row = self.row(
            "Cirsium coryletorum",
            "SAMN2",
            "SRR2",
            region="Russian_Far_East",
            scope="northeast_asia_bridge",
            relation="different_submitted_or_published_name",
            priority="high",
        )
        with self.assertRaises(ValueError):
            mod.select_target([row], target, 1)
        target["allow_high_name_conflict"] = True
        result = mod.select_target([row], target, 1)
        self.assertEqual(result["name_reconciliation_required"], "true")

    def test_multiple_runs_are_grouped_per_biosample(self) -> None:
        target = {
            "tree_code": "Cirsium testii",
            "biosample": "SAMN1",
            "role": "test_anchor",
            "rationale": "test",
            "allow_high_name_conflict": False,
        }
        rows = [
            self.row("Cirsium testii", "SAMN1", "SRR2"),
            self.row("Cirsium testii", "SAMN1", "SRR1"),
        ]
        result = mod.select_target(rows, target, 1)
        self.assertEqual(result["runs"], "SRR1|SRR2")
        self.assertEqual(result["run_count"], "2")

    def test_missing_target_fails(self) -> None:
        target = {
            "tree_code": "Cirsium absentii",
            "biosample": "SAMN404",
            "role": "missing",
            "rationale": "test",
            "allow_high_name_conflict": False,
        }
        with self.assertRaises(ValueError):
            mod.select_target([], target, 1)

    def test_download_script_contains_all_runs_and_no_hybpiper_claim(self) -> None:
        panel = [
            {
                "runs": "SRR1|SRR2",
            },
            {
                "runs": "SRR3",
            },
        ]
        script = mod.render_download_script(panel)
        for run in ("SRR1", "SRR2", "SRR3"):
            self.assertIn(run, script)
        self.assertIn("prefetch", script)
        self.assertIn("fasterq-dump", script)
        self.assertIn("does not reproduce", script)

    def test_write_outputs_marks_analysis_as_not_reproduced(self) -> None:
        panel = [
            {
                "pilot_order": "1",
                "sample_id": "MRY_EA_01_test",
                "pilot_role": "test",
                "tree_code": "Cirsium testii",
                "published_species": "Cirsium testii",
                "sra_scientific_name": "Cirsium testii",
                "library_name": "test",
                "biosample": "SAMN1",
                "experiments": "SRX1",
                "runs": "SRR1",
                "run_count": "1",
                "region_class": "Japan",
                "scope_class": "core_east_asia",
                "tree_code_vs_sra_name": "exact",
                "name_reconciliation_priority": "low",
                "name_reconciliation_required": "false",
                "voucher_and_herbarium": "voucher",
                "rationale": "test",
                "public_locus_sets": "public_1061",
            }
        ]
        with tempfile.TemporaryDirectory() as tmp:
            summary = mod.write_outputs(Path(tmp), panel)
            self.assertFalse(summary["raw_reads_downloaded_in_ci"])
            self.assertFalse(summary["full_published_analysis_reproduced"])
            self.assertEqual(summary["biological_samples"], 1)
            self.assertEqual(summary["unique_runs"], 1)
            self.assertTrue((Path(tmp) / "download_public_reads.sh").exists())


if __name__ == "__main__":
    unittest.main()
