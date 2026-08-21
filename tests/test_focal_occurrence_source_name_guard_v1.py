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

    def test_intermediate_slot_guard_rejects_isolated_extreme(self):
        frame = pd.DataFrame([
            # Locally supported intermediate cluster 0.
            {"gbif_key": 1, "latitude": 27.05, "longitude": 128.40, "cluster_id": 0,
             "niche_information_score": 0.7, "bridge_relevance": 0.85, "coverage_gain": 0.70, "niche_edge": 0.35},
            {"gbif_key": 2, "latitude": 27.10, "longitude": 128.43, "cluster_id": 0,
             "niche_information_score": 0.6, "bridge_relevance": 0.82, "coverage_gain": 0.65, "niche_edge": 0.30},
            # Locally supported intermediate cluster 1.
            {"gbif_key": 3, "latitude": 27.80, "longitude": 128.90, "cluster_id": 1,
             "niche_information_score": 0.8, "bridge_relevance": 0.84, "coverage_gain": 0.98, "niche_edge": 0.18},
            {"gbif_key": 4, "latitude": 27.82, "longitude": 128.88, "cluster_id": 1,
             "niche_information_score": 0.75, "bridge_relevance": 0.83, "coverage_gain": 0.95, "niche_edge": 0.12},
            # Isolated extreme: high raw score but no nearby corroborating occurrence and not intermediate.
            {"gbif_key": 99, "latitude": 24.94, "longitude": 125.23, "cluster_id": 2,
             "niche_information_score": 1.0, "bridge_relevance": 0.0, "coverage_gain": 1.0, "niche_edge": 1.0},
        ])
        chosen = mod.guarded_select_distinct_candidates(frame, 2, min_distance_km=50)
        self.assertEqual(len(chosen), 2)
        self.assertNotIn(99, set(chosen["gbif_key"]))
        self.assertEqual(len(set(chosen["cluster_id"])), 2)
        self.assertTrue((chosen["local_support_neighbors_75km"] >= 1).all())
        self.assertTrue((chosen["bridge_relevance"] > 0.15).all())
        self.assertTrue((chosen["intermediate_slot_score"] > 0).all())


if __name__ == "__main__":
    unittest.main()
