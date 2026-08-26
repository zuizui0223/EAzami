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

    def test_prefecture_independence(self):
        self.assertFalse(mod.explicit_prefecture_independence("Fukushima"))
        self.assertFalse(mod.explicit_prefecture_independence("福島県"))
        self.assertTrue(mod.explicit_prefecture_independence("Yamagata"))
        self.assertTrue(mod.explicit_prefecture_independence("Hokkaido"))
        self.assertIsNone(mod.explicit_prefecture_independence(""))

    def test_basis_roles(self):
        self.assertTrue(mod.is_live_basis("HUMAN_OBSERVATION"))
        self.assertTrue(mod.is_live_basis("OBSERVATION"))
        self.assertFalse(mod.is_live_basis("PRESERVED_SPECIMEN"))
        self.assertTrue(mod.is_specimen_basis("PRESERVED_SPECIMEN"))
        self.assertFalse(mod.is_specimen_basis("HUMAN_OBSERVATION"))

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

    def test_summary_deduplicates_inat_mirror_and_excludes_specimen_colour(self):
        base = {
            "source_record_id": "1", "record_url": "https://www.inaturalist.org/observations/1",
            "observed_on": "2024-09-01", "state_province": "", "place_text": "Hokkaido",
            "latitude": 43.0, "longitude": 142.0, "locality_cell_0_05deg": "43.00,142.00",
            "media_url": "https://example.org/a.jpg", "media_license": "cc-by", "attribution": "A",
            "institution_code": "", "collection_code": "",
        }
        rows = [
            {
                **base, "source": "iNaturalist", "dedup_record_key": "inat:1",
                "basis_of_record": "HUMAN_OBSERVATION", "media_license_class": "open_reusable",
                "automated_measurement_candidate": "true", "license_blocked_live_independent_candidate": "false",
                "dataset": "iNat",
            },
            {
                **base, "source": "GBIF", "dedup_record_key": "inat:1",
                "basis_of_record": "HUMAN_OBSERVATION", "media_license_class": "open_reusable",
                "automated_measurement_candidate": "true", "license_blocked_live_independent_candidate": "false",
                "dataset": "iNat via GBIF",
            },
            {
                **base, "source": "GBIF", "source_record_id": "2", "dedup_record_key": "gbif:2",
                "record_url": "https://www.gbif.org/occurrence/2", "basis_of_record": "PRESERVED_SPECIMEN",
                "media_url": "https://example.org/specimen.jpg", "media_license_class": "open_reusable",
                "automated_measurement_candidate": "false", "license_blocked_live_independent_candidate": "false",
                "dataset": "herbarium",
            },
        ]
        result = mod.summarize(rows, 1, 2)
        self.assertEqual(result["cross_source_unique_open_reusable_records"], 2)
        self.assertEqual(result["cross_source_open_reusable_live_records"], 1)
        self.assertEqual(result["cross_source_open_reusable_specimen_records"], 1)
        self.assertEqual(result["conservative_independent_open_reusable_live_records"], 1)
        self.assertEqual(result["conservative_independent_open_reusable_live_locality_cells_0_05deg"], 1)


if __name__ == "__main__":
    unittest.main()
