from __future__ import annotations

import csv
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "jogv2", ROOT / "analysis/build_japan_origin_global_public_panel_v2.py"
)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules["jogv2"] = mod
SPEC.loader.exec_module(mod)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


class JapanOriginGlobalV2Tests(unittest.TestCase):
    def test_cross_paper_reuse_collapses_to_one_tip(self):
        chang25 = [
            {
                "taxon": "Cirsium lineare", "voucher": "v1", "biosample": "SAMN1",
                "run": "SRR1", "library_layout": "PAIRED", "geographic_location": "Taiwan: x",
                "match_status": "verified",
            },
            {
                "taxon": "Cirsium kujuense", "voucher": "v2", "biosample": "SAMN2",
                "run": "SRR2", "library_layout": "PAIRED", "geographic_location": "Japan: y",
                "match_status": "verified",
            },
        ]
        chang26 = [
            {
                "taxon": "C. lineare", "voucher": "v1", "matched_biosample": "SAMN1",
                "matched_run": "SRR1", "matched_library_layout": "PAIRED", "match_confidence": "verified",
                "location": "TAIWAN. x", "matched_scientific_name": "Cirsium lineare",
                "match_evidence": "exact_taxon",
            },
            {
                "taxon": "C. brevicaule", "voucher": "v3", "matched_biosample": "SAMN3",
                "matched_run": "SRR3", "matched_library_layout": "PAIRED", "match_confidence": "verified",
                "location": "JAPAN. Amami", "matched_scientific_name": "Cirsium brevicaule",
                "match_evidence": "exact_taxon",
            },
        ]
        rows, shared = mod.build_chang(chang25, chang26)
        self.assertEqual(len(rows), 3)
        self.assertEqual(len(shared), 1)
        self.assertEqual(shared[0]["biosample"], "SAMN1")
        row = next(item for item in rows if item["biosample"] == "SAMN1")
        self.assertEqual(row["source_studies"], "Chang2025|Chang2026")
        self.assertEqual(row["run_accessions"], "SRR1")
        self.assertEqual(row["source_record_count"], "2")
        self.assertEqual(row["shared_cross_paper_sample"], "true")

    def test_reused_sample_disagreement_is_fatal(self):
        chang25 = [{
            "taxon": "Cirsium lineare", "voucher": "v1", "biosample": "SAMN1", "run": "SRR1",
            "library_layout": "PAIRED", "geographic_location": "Taiwan: x", "match_status": "verified",
        }]
        chang26 = [{
            "taxon": "C. morii", "voucher": "v1", "matched_biosample": "SAMN1", "matched_run": "SRR1",
            "matched_library_layout": "PAIRED", "match_confidence": "verified", "location": "TAIWAN. x",
            "matched_scientific_name": "Cirsium morii", "match_evidence": "exact_taxon",
        }]
        with self.assertRaisesRegex(ValueError, "disagrees in taxon/voucher"):
            mod.build_chang(chang25, chang26)

    def test_japan38_index_allows_one_paper_concept_to_map_to_two_tips(self):
        rows = [{
            "paper_japan_member_id": "JPN_20",
            "paper_taxon_concept": "Cirsium nipponicum var. incomptum",
            "biosamples": "SAMNA|SAMNB",
            "paper_japan_membership_confidence": "high",
        }]
        idx = mod.japan38_index(rows)
        self.assertEqual(idx["SAMNA"][0]["paper_japan_member_id"], "JPN_20")
        self.assertEqual(idx["SAMNB"][0]["paper_japan_member_id"], "JPN_20")


if __name__ == "__main__":
    unittest.main()
