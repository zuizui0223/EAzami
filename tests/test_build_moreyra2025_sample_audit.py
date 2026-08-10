#!/usr/bin/env python3
"""Offline tests for the Moreyra 2025 supplement-to-SRA audit."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "analysis" / "build_moreyra2025_sample_audit.py"
SPEC = importlib.util.spec_from_file_location("build_moreyra2025_sample_audit", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


class MoreyraAuditTests(unittest.TestCase):
    def test_region_scope_separates_far_east_from_caucasus(self) -> None:
        self.assertEqual(
            mod.classify_region("Russia: Primorskiy territory", ""),
            ("Russian_Far_East", "northeast_asia_bridge"),
        )
        self.assertEqual(
            mod.classify_region("Russia", "Caucasus: North Ossetia"),
            ("Russia_other", "outside_scope"),
        )
        self.assertEqual(
            mod.classify_region("Japan: Honshu", ""),
            ("Japan", "core_east_asia"),
        )

    def test_name_relation_preserves_conflicts(self) -> None:
        self.assertEqual(
            mod.name_relation("Cirsium domonii", "Cirsium domonii")[0],
            "exact",
        )
        self.assertEqual(
            mod.name_relation("Cirsium verutum", "Lophiolepis verutum")[0],
            "generic_reassignment_only",
        )
        self.assertEqual(
            mod.name_relation("Cirsium coryletorum", "Cirsium vlassovianum")[0],
            "different_submitted_or_published_name",
        )

    def test_join_keeps_supplement_row_without_run(self) -> None:
        supplement = [
            {
                "Tree code names": "Cirsium missing",
                "Species": "Cirsium missing Author",
                "Accession number": "",
                "Voucher and herbarium code": "Japan",
            }
        ]
        rows = mod.reconcile_samples(supplement, [])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["sra_link_status"], "supplement_no_biosample")
        self.assertEqual(rows[0]["scope_class"], "core_east_asia")

    def test_focal_audit_detects_exact_and_name_mismatch(self) -> None:
        supplement = [
            {
                "Tree code names": "Cirsium pendulum",
                "Species": "Cirsium pendulum Fisch.",
                "Accession number": "SAM1",
                "Voucher and herbarium code": "Russia: Trans-Baikal",
            },
            {
                "Tree code names": "Cirsium coryletorum",
                "Species": "Cirsium coryletorum",
                "Accession number": "SAM2",
                "Voucher and herbarium code": "Russia: Sikhote-Alin",
            },
        ]
        runinfo = [
            {
                "Run": "SRR1",
                "Experiment": "SRX1",
                "BioProject": "PRJNA1",
                "BioSample": "SAM1",
                "ScientificName": "Cirsium pendulum",
                "LibraryName": "lib1",
            },
            {
                "Run": "SRR2",
                "Experiment": "SRX2",
                "BioProject": "PRJNA1",
                "BioSample": "SAM2",
                "ScientificName": "Cirsium vlassovianum",
                "LibraryName": "lib2",
            },
        ]
        reconciled = mod.reconcile_samples(supplement, runinfo)
        audit = {
            row["query_taxon"]: row
            for row in mod.focal_audit(
                ["Cirsium pendulum", "Cirsium coryletorum"], reconciled
            )
        }
        self.assertEqual(
            audit["Cirsium pendulum"]["project_tip_status"],
            "exact_sra_project_tip_verified",
        )
        self.assertEqual(
            audit["Cirsium coryletorum"]["project_tip_status"],
            "supplement_tree_tip_verified_runinfo_name_mismatch",
        )


if __name__ == "__main__":
    unittest.main()
