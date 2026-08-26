import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "jpn29_audit", ROOT / "analysis/audit_jpn29_specimen_determination_v1.py"
)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class TestJPN29SpecimenAudit(unittest.TestCase):
    def test_catalog_match(self):
        self.assertTrue(mod.catalog_match("PE01523822"))
        self.assertTrue(mod.catalog_match("PE-01523822"))
        self.assertFalse(mod.catalog_match("PE01523823"))

    def test_collector_number_match(self):
        self.assertTrue(mod.collector_number_match("K. Yonekura", "6788"))
        self.assertTrue(mod.collector_number_match("Koji Yonekura", "No. 6788"))
        self.assertFalse(mod.collector_number_match("K. Yonekura", "6789"))

    def test_summary_does_not_reidentify_without_determination_fields(self):
        gbif={"catalog_number":{"rows":[],"count":0,"ok":True},"collector_taxon_japan":{"rows":[],"count":0,"ok":True}}
        idi={"catalog_number":{"rows":[],"count":0,"ok":True},"collector_number":{"rows":[],"count":0,"ok":True}}
        out=mod.summarize(gbif,idi)
        self.assertFalse(out["determination_history_resolved"])
        self.assertIn("Direct herbarium-curator", out["decision"])


if __name__ == "__main__":
    unittest.main()
