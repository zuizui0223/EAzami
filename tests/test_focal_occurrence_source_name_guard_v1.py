import importlib.util
import pathlib
import unittest

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis" / "run_focal_occurrence_niche_sample_information_source_guard_v1.py"
spec = importlib.util.spec_from_file_location("source_guard", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class FocalOccurrenceSourceNameGuardTest(unittest.TestCase):
    def test_source_name_match_keeps_author_and_infraspecific_variants(self):
        q = "Cirsium brevicaule"
        self.assertTrue(mod.source_name_matches_query("Cirsium brevicaule A.Gray", q))
        self.assertTrue(mod.source_name_matches_query("Cirsium brevicaule var. brevicaule", q))
        self.assertFalse(mod.source_name_matches_query("Cirsium irumtiense Kitam.", q))
        self.assertFalse(mod.source_name_matches_query("Cirsium brevicauleiforme X", q))

    def test_synonym_collapsed_record_is_excluded_before_coordinate_cleaning(self):
        raw = pd.DataFrame([
            {
                "scientific_name_query": "Cirsium brevicaule",
                "scientificName": "Cirsium brevicaule A.Gray",
                "acceptedScientificName": "Cirsium brevicaule A.Gray",
                "decimalLatitude": 28.3,
                "decimalLongitude": 129.4,
                "coordinateUncertaintyInMeters": 1000,
                "year": 2025,
                "issues": "",
            },
            {
                "scientific_name_query": "Cirsium brevicaule",
                "scientificName": "Cirsium irumtiense Kitam.",
                "acceptedScientificName": "Cirsium brevicaule A.Gray",
                "decimalLatitude": 24.45,
                "decimalLongitude": 123.0,
                "coordinateUncertaintyInMeters": 1000,
                "year": 2025,
                "issues": "",
            },
        ])
        cfg = {
            "japan_bounds": {"lat_min": 20, "lat_max": 46.5, "lon_min": 122, "lon_max": 154.5},
            "max_coordinate_uncertainty_m_primary": 10000,
            "spatial_thin_degrees": 0.05,
        }
        primary, meta = mod.guarded_clean_and_thin(raw, cfg)
        self.assertEqual(meta["n_pre_source_filter"], 2)
        self.assertEqual(meta["n_source_taxon_match"], 1)
        self.assertEqual(meta["n_source_taxon_excluded"], 1)
        self.assertEqual(len(primary), 1)
        self.assertTrue(primary.iloc[0]["scientificName"].startswith("Cirsium brevicaule"))


if __name__ == "__main__":
    unittest.main()
