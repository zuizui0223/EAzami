from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "analysis" / "recover_ncbi_project_runs.py"
SPEC = importlib.util.spec_from_file_location("recover_ncbi_project_runs", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class RecoveryHelpersTest(unittest.TestCase):
    def setUp(self) -> None:
        self.rows = [
            {
                "Run": "SRR25265717",
                "Experiment": "SRX21011499",
                "SRAStudy": "SRP449379",
                "BioProject": "PRJNA957074",
                "Sample": "SRS18284452",
                "BioSample": "SAMN34240283",
                "ScientificName": "Cirsium domonii",
                "LibraryName": "Cirsium-domonii_FJ318",
            },
            {
                "Run": "SRR99999999",
                "Experiment": "SRX99999999",
                "SRAStudy": "SRP449379",
                "BioProject": "PRJNA957074",
                "Sample": "SRS99999999",
                "BioSample": "SAMN99999999",
                "ScientificName": "Cirsium domonii",
                "LibraryName": "Cirsium-domonii_rep2",
            },
        ]

    def test_canonical_taxon_is_conservative(self) -> None:
        self.assertEqual(
            MODULE.canonical_taxon("  Cirsium_domoniI  "),
            "cirsium domonii",
        )
        self.assertEqual(
            MODULE.canonical_taxon("Cirsium domonii (voucher FJ318)"),
            "cirsium domonii",
        )
        self.assertNotEqual(
            MODULE.canonical_taxon("Cirsium paludigenum"),
            MODULE.canonical_taxon("Cirsium sieboldii"),
        )

    def test_taxon_summary_counts_unique_accessions(self) -> None:
        summary = MODULE.summarize_taxa(self.rows)
        self.assertEqual(len(summary), 1)
        self.assertEqual(summary[0]["scientific_name"], "Cirsium domonii")
        self.assertEqual(summary[0]["n_runs"], 2)
        self.assertEqual(summary[0]["n_biosamples"], 2)

    def test_focal_audit_does_not_call_nonmatch_absent(self) -> None:
        audit = MODULE.focal_audit(
            ["Cirsium domonii", "Cirsium pendulum"], self.rows
        )
        by_taxon = {row["query_taxon"]: row for row in audit}
        self.assertEqual(
            by_taxon["Cirsium domonii"]["project_tip_status"],
            "exact_sra_project_tip_verified",
        )
        self.assertEqual(
            by_taxon["Cirsium pendulum"]["project_tip_status"],
            "not_recovered_in_project_runinfo",
        )
        self.assertIn(
            "not proof of biological absence",
            by_taxon["Cirsium pendulum"]["interpretation"],
        )

    def test_parse_runinfo_csv(self) -> None:
        payload = (
            "Run,Experiment,SRAStudy,BioProject,Sample,BioSample,ScientificName,LibraryName\n"
            "SRR25265717,SRX21011499,SRP449379,PRJNA957074,SRS18284452,"
            "SAMN34240283,Cirsium domonii,Cirsium-domonii_FJ318\n"
        ).encode("utf-8")
        rows = MODULE.parse_csv_payload(payload)
        self.assertEqual(rows[0]["Run"], "SRR25265717")
        self.assertEqual(rows[0]["ScientificName"], "Cirsium domonii")


if __name__ == "__main__":
    unittest.main()
