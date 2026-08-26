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

    def test_locality_text_classification(self):
        self.assertTrue(mod.japan_word("photographed in Japan"))
        self.assertTrue(mod.fukushima_aizu_text("タカアザミ 福島県会津地方"))
        self.assertTrue(mod.korea_text("Cirsium pendulum in Kimpo, Korea"))
        self.assertFalse(mod.korea_text("Cirsium pendulum"))
        self.assertFalse(mod.japan_word("Cirsium pendulum"))


if __name__ == "__main__":
    unittest.main()
