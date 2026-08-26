import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "jpn38_sources",
    ROOT / "analysis/audit_jpn38_inat_gbif_japan_sources_v1.py",
)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class TestJPN38SourceAudit(unittest.TestCase):
    def test_license_classes(self):
        for value in [
            "cc0", "cc-by", "cc-by-sa",
            "https://creativecommons.org/licenses/by/4.0/",
            "http://creativecommons.org/licenses/by-sa/4.0/legalcode",
        ]:
            self.assertEqual(mod.classify_license(value), "open_reusable")
        self.assertEqual(mod.classify_license("cc-by-nc"), "noncommercial_only")
        self.assertEqual(mod.classify_license("https://creativecommons.org/licenses/by-nc-sa/4.0/"), "noncommercial_only")
        self.assertEqual(mod.classify_license("cc-by-nd"), "no_derivatives")
        self.assertEqual(mod.classify_license(None), "unspecified")

    def test_fukushima_exclusion_is_conservative(self):
        self.assertFalse(mod.outside_fukushima_bbox(37.4, 139.9))
        self.assertTrue(mod.outside_fukushima_bbox(43.0, 142.0))
        self.assertTrue(mod.outside_fukushima_bbox(36.2, 138.2))
        self.assertIsNone(mod.outside_fukushima_bbox(None, 140.0))

    def test_inaturalist_key_normalization(self):
        self.assertEqual(
            mod.normalize_inat_record_key("https://www.inaturalist.org/observations/12345"),
            "inat:12345",
        )
        self.assertEqual(
            mod.normalize_inat_record_key("https://www.inaturalist.org/observations/12345?foo=1"),
            "inat:12345",
        )
        self.assertIsNone(mod.normalize_inat_record_key("https://www.gbif.org/occurrence/1"))

    def test_summary_deduplicates_inat_mirror(self):
        rows = [
            {
                "source": "iNaturalist", "dedup_record_key": "inat:1", "media_license_class": "open_reusable",
                "automated_measurement_candidate": "true", "locality_cell_0_05deg": "43.00,142.00",
                "source_record_id": "1", "record_url": "https://www.inaturalist.org/observations/1",
                "observed_on": "2024-09-01", "place_text": "Hokkaido", "latitude": 43.0, "longitude": 142.0,
                "media_url": "https://example.org/a.jpg", "media_license": "cc-by", "attribution": "A", "dataset": "iNat",
            },
            {
                "source": "GBIF", "dedup_record_key": "inat:1", "media_license_class": "open_reusable",
                "automated_measurement_candidate": "true", "locality_cell_0_05deg": "43.00,142.00",
                "source_record_id": "99", "record_url": "https://www.inaturalist.org/observations/1",
                "observed_on": "2024-09-01", "place_text": "Hokkaido", "latitude": 43.0, "longitude": 142.0,
                "media_url": "https://example.org/a.jpg", "media_license": "CC BY 4.0", "attribution": "A", "dataset": "iNat via GBIF",
            },
        ]
        result = mod.summarize(rows, 1, 1)
        self.assertEqual(result["cross_source_unique_open_reusable_records"], 1)
        self.assertEqual(result["conservative_independent_open_reusable_records"], 1)
        self.assertEqual(result["conservative_independent_locality_cells_0_05deg"], 1)


if __name__ == "__main__":
    unittest.main()
