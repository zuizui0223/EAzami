"""GBIF source-only point gate: filter validity and no climate leakage."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"analysis"))

import audit_global_orientation_gbif_point_coverage_v1 as gbif  # noqa: E402


class FrozenWorldwideOrientationGBIFGate(unittest.TestCase):
    def test_frozen_35_source_taxon_orientation_state_fingerprint(self):
        m,digest=gbif.cohort()
        self.assertEqual(len(m),35)
        self.assertEqual(len(digest),64)
        self.assertEqual(list(sorted(set(m.values()))),["D","U"])
        self.assertEqual(list(m.values()).count("U"),24)
        self.assertEqual(list(m.values()).count("D"),11)

    def test_do_not_accidentally_pool_other_taxa_or_broader_synonyms(self):
        self.assertTrue(gbif.exact_source_name("Cirsium vinaceum Wooton & Standl.","Cirsium vinaceum"))
        self.assertFalse(gbif.exact_source_name("Cirsium ownbeyi Wooton","Cirsium vinaceum"))
        self.assertFalse(gbif.exact_source_name("Cirsium vinaceumX", "Cirsium vinaceum"))

    def test_coordinate_qc_exact_matches_duplicate_grid_and_uncertainty(self):
        def make(key,name="Cirsium vinaceum A.Gray",lat=34.0,lon=-105.0,
                 uncertainty=2000,issues=()):
            return {"key":key,"scientificName":name,"decimalLatitude":lat,
                    "decimalLongitude":lon,"coordinateUncertaintyInMeters":uncertainty,
                    "issues":list(issues),"countryCode":"US","basisOfRecord":"HUMAN_OBSERVATION"}
        data=[
            make(1),
            make(2,lat=34.0,lon=-105.0,uncertainty=1000),
            make(3,lat=34.02,lon=-104.98,uncertainty=100),
            make(4,name="Cirsium ownbeyi",lat=35.0,lon=-100.0),
            make(5,lat=36.0,lon=-102.0,uncertainty=15000),
            make(6,lat=36.1,lon=-102.1,uncertainty=None),
            make(7,lat=34.3,lon=-104.8,issues=("COUNTRY_COORDINATE_MISMATCH",)),
            make(8,lat=36.5,lon=-103.5),
        ]
        points,c=gbif.qc_thin(data,"Cirsium vinaceum")
        self.assertEqual(c["n_fetched"],8)
        self.assertEqual(c["n_source_exact"],7)
        self.assertEqual(c["n_coordinate_quality"],4)
        self.assertEqual(c["n_unique_coordinates"],3)
        self.assertEqual(c["n_geocells_0_1deg"],2)
        self.assertEqual({x["gbif_key"] for x in points},{"3","8"})
        self.assertTrue(all(x["native_status"]=="NOT_CHECKED" for x in points))

    def test_synthetic_network_stub_does_not_mark_climate_ready(self):
        def fake(name,max_records):
            rows=[{"key":str(i+1),"scientificName":name,"decimalLatitude":10+i,
                   "decimalLongitude":20+i,"coordinateUncertaintyInMeters":400,
                   "issues":[],"countryCode":"XX"} for i in range(3)]
            return rows,{"taxon":name,"gbif_match_type":"EXACT",
                         "gbif_canonical_name":name,"gbif_status":"ACCEPTED",
                         "gbif_usage_key":42,"gbif_rank":"SPECIES",
                         "gbif_total_coordinate_present_count":3}
        with patch.object(gbif,"fetch_one",side_effect=fake):
            summary,rows,points=gbif.run(500)
        self.assertEqual(summary["n_taxa_requested"],35)
        self.assertEqual(summary["total_qc_thinned_records"],105)
        self.assertEqual(summary["n_geocell_min5_taxa"],0)
        self.assertFalse(summary["native_range_qc_complete"])
        self.assertFalse(summary["bio15_bio1_extracted"])
        self.assertFalse(summary["world_nuclear_tree_estimated"])
        self.assertFalse(summary["transition_climate_test_executed"])

    def test_bad_request_budget_is_rejected(self):
        with self.assertRaisesRegex(ValueError,"max_records"):
            gbif.run(0)


if __name__=="__main__":
    unittest.main()
