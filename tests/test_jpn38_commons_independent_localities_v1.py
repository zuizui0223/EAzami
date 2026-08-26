import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "commons_audit", ROOT / "analysis/audit_jpn38_commons_independent_localities_v1.py"
)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class TestCommonsAudit(unittest.TestCase):
    def test_clean_html(self):
        self.assertEqual(mod.clean_html("<b>福島県</b>&nbsp;会津"), "福島県 会津")

    def test_open_license(self):
        self.assertTrue(mod.open_license("CC BY-SA 4.0"))
        self.assertTrue(mod.open_license("CC BY 3.0"))
        self.assertTrue(mod.open_license("GFDL 1.2"))
        self.assertFalse(mod.open_license("All rights reserved"))

    def test_japan_text(self):
        self.assertTrue(mod.japan_text("福島県会津地方 日本"))
        self.assertTrue(mod.japan_text("photographed in Japan"))
        self.assertFalse(mod.japan_text("Korea"))


if __name__ == "__main__":
    unittest.main()
