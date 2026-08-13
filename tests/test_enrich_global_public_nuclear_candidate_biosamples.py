from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))
SPEC = importlib.util.spec_from_file_location(
    "biosample_provenance", ROOT / "analysis/enrich_global_public_nuclear_candidate_biosamples.py"
)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules["biosample_provenance"] = mod
SPEC.loader.exec_module(mod)


class BioSampleProvenanceTests(unittest.TestCase):
    def test_exact_and_manual_name_review_are_separated(self):
        queue = [
            {
                "candidate_id": "AUGSRA_SAMN1", "tip_id_if_admitted": "AUGSRA_SAMN1",
                "biosample": "SAMN1", "scientific_name": "Cirsium setidens"
            },
            {
                "candidate_id": "AUGSRA_SAMN2", "tip_id_if_admitted": "AUGSRA_SAMN2",
                "biosample": "SAMN2", "scientific_name": "Cirsium japonicum var. ussuriense"
            },
        ]
        attrs = {
            "SAMN1": {
                "biosample_organism": "Cirsium setidens",
                "geo_loc_name": "South Korea",
                "specimen_voucher": "ABC123",
            },
            "SAMN2": {
                "biosample_organism": "Cirsium japonicum",
                "geo_loc_name": "China",
            },
        }
        rows, summary = mod.provenance_rows(queue, attrs)
        by_bs = {row["biosample"]: row for row in rows}
        self.assertEqual(by_bs["SAMN1"]["provenance_review_status"], "exact_taxon_metadata_concordant")
        self.assertTrue(by_bs["SAMN1"]["organism_exact_match"])
        self.assertEqual(by_bs["SAMN1"]["specimen_voucher"], "ABC123")
        self.assertEqual(by_bs["SAMN2"]["provenance_review_status"], "cirsium_taxon_name_manual_review")
        self.assertFalse(by_bs["SAMN2"]["organism_exact_match"])
        self.assertTrue(by_bs["SAMN2"]["organism_cirsium_genus_concordant"])
        self.assertEqual(summary["exact_taxon_metadata_concordant"], 1)
        self.assertEqual(summary["cirsium_taxon_name_manual_review"], 1)
        self.assertFalse(summary["automatic_tree_tip_promotion_allowed"])

    def test_non_cirsium_or_missing_record_blocks_provenance_gate(self):
        queue = [
            {"candidate_id": "X1", "tip_id_if_admitted": "X1", "biosample": "SAMN1", "scientific_name": "Cirsium a"},
            {"candidate_id": "X2", "tip_id_if_admitted": "X2", "biosample": "SAMN2", "scientific_name": "Cirsium b"},
        ]
        attrs = {"SAMN1": {"biosample_organism": "Fungus example"}}
        rows, summary = mod.provenance_rows(queue, attrs)
        self.assertEqual(rows[0]["provenance_review_status"], "biosample_organism_conflict")
        self.assertEqual(rows[1]["provenance_review_status"], "biosample_record_not_recovered")
        self.assertEqual(summary["biosample_organism_conflicts"], 1)
        self.assertEqual(summary["biosample_records_not_recovered"], 1)

    def test_attribute_aliases_are_preserved(self):
        record = {
            "geographic location": "Japan",
            "voucher_id": "V-1",
            "date collected": "2024-06-01",
        }
        self.assertEqual(mod.first(record, "geo_loc_name", "geographic_location"), "Japan")
        self.assertEqual(mod.first(record, "specimen_voucher", "voucher_id"), "V-1")
        self.assertEqual(mod.first(record, "collection_date", "date_collected"), "2024-06-01")


if __name__ == "__main__":
    unittest.main()
