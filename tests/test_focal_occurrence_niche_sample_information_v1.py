import importlib.util
import pathlib
import unittest

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis" / "build_focal_occurrence_niche_sample_information_v1.py"
spec = importlib.util.spec_from_file_location("focal_niche", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class FocalOccurrenceNicheSamplingTest(unittest.TestCase):
    def test_haversine_and_bridge(self):
        self.assertAlmostEqual(mod.haversine_km(0, 0, 0, 0), 0.0, places=8)
        self.assertGreater(mod.haversine_km(28.3, 129.4, 26.5, 127.9), 200)
        anchors = pd.DataFrame([
            {"latitude": 28.32, "longitude": 129.37},
            {"latitude": 26.50, "longitude": 127.95},
        ])
        mid = mod.line_bridge_relevance(27.41, 128.66, anchors)
        end = mod.line_bridge_relevance(28.32, 129.37, anchors)
        self.assertGreater(mid, 0.9)
        self.assertEqual(end, 0.0)

    def test_clean_and_thin_prefers_strict_coordinates(self):
        rows = []
        for i in range(12):
            rows.append({
                "scientific_name_query": "Cirsium test",
                "decimalLatitude": 27.0 + (i // 2) * 0.06,
                "decimalLongitude": 128.0 + (i // 2) * 0.06,
                "coordinateUncertaintyInMeters": 1000 if i < 10 else None,
                "year": 2020 + (i % 2),
                "issues": "",
            })
        raw = pd.DataFrame(rows)
        cfg = {
            "japan_bounds": {"lat_min": 20, "lat_max": 46.5, "lon_min": 122, "lon_max": 154.5},
            "max_coordinate_uncertainty_m_primary": 10000,
            "spatial_thin_degrees": 0.05,
        }
        primary, meta = mod.clean_and_thin(raw, cfg)
        self.assertEqual(meta["primary_quality_mode"], "strict_le_10km")
        self.assertEqual(meta["n_strict_coordinate"], 10)
        self.assertTrue(primary["strict_coordinate_quality"].all())
        self.assertFalse(primary.duplicated(["scientific_name_query", "thin_lat", "thin_lon"]).any())

    def test_clean_and_thin_fallback_is_explicit(self):
        raw = pd.DataFrame([
            {
                "scientific_name_query": "Cirsium rare",
                "decimalLatitude": 25 + i * 0.1,
                "decimalLongitude": 125 + i * 0.1,
                "coordinateUncertaintyInMeters": None,
                "year": 2020,
                "issues": "",
            }
            for i in range(6)
        ])
        cfg = {
            "japan_bounds": {"lat_min": 20, "lat_max": 46.5, "lon_min": 122, "lon_max": 154.5},
            "max_coordinate_uncertainty_m_primary": 10000,
            "spatial_thin_degrees": 0.05,
        }
        primary, meta = mod.clean_and_thin(raw, cfg)
        self.assertEqual(meta["primary_quality_mode"], "inclusive_missing_uncertainty_fallback")
        self.assertEqual(len(primary), 6)

    def test_distinct_candidate_selection(self):
        frame = pd.DataFrame([
            {"latitude": 27.0, "longitude": 128.0, "cluster_id": 0, "niche_information_score": 0.9},
            {"latitude": 27.01, "longitude": 128.01, "cluster_id": 1, "niche_information_score": 0.8},
            {"latitude": 27.8, "longitude": 128.8, "cluster_id": 1, "niche_information_score": 0.7},
            {"latitude": 26.8, "longitude": 128.9, "cluster_id": 2, "niche_information_score": 0.6},
        ])
        chosen = mod.select_distinct_candidates(frame, 2, min_distance_km=50)
        self.assertEqual(len(chosen), 2)
        self.assertEqual(len(set(chosen["cluster_id"])), 2)
        a, b = chosen.iloc[0], chosen.iloc[1]
        self.assertGreaterEqual(
            mod.haversine_km(a.latitude, a.longitude, b.latitude, b.longitude), 50
        )

    def test_robust_unit_range(self):
        x = mod.robust_unit(pd.Series([1, 2, 3, 100]))
        self.assertTrue(np.all((x >= 0) & (x <= 1)))
        self.assertEqual(float(x.iloc[0]), 0.0)


if __name__ == "__main__":
    unittest.main()
