import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis" / "audit_white_morph_niche_linkage_v1.py"
spec = importlib.util.spec_from_file_location("white_morph_niche", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class WhiteMorphNicheLinkageTest(unittest.TestCase):
    def test_form_source_name_matching_is_rank_specific(self):
        self.assertTrue(
            mod.source_name_matches_query(
                "Cirsium sieboldii f. leucanthum T.Shimizu",
                "Cirsium sieboldii f. leucanthum",
            )
        )
        self.assertFalse(
            mod.source_name_matches_query(
                "Cirsium sieboldii Miq.",
                "Cirsium sieboldii f. leucanthum",
            )
        )
        self.assertTrue(
            mod.source_name_matches_query(
                "Cirsium pendulum var. albiflorum Makino",
                "Cirsium pendulum var. albiflorum",
            )
        )
        self.assertFalse(
            mod.source_name_matches_query(
                "Cirsium pendulum f. pendulum",
                "Cirsium pendulum f. albiflorum",
            )
        )

    def test_authority_is_not_part_of_canonical_prefix(self):
        self.assertEqual(
            mod.canonical_morph_prefix("Cirsium pendulum f. albiflorum (Makino) Kitam."),
            "cirsium pendulum f. albiflorum",
        )
        self.assertEqual(
            mod.canonical_morph_prefix("Cirsium sieboldii f. leucanthum T.Shimizu"),
            "cirsium sieboldii f. leucanthum",
        )


if __name__ == "__main__":
    unittest.main()
