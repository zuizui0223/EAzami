from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "analysis"
if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))

SCRIPT = ANALYSIS / "build_cirsium_flower_colour_atlas_v0_3.py"
SPEC = importlib.util.spec_from_file_location("build_colour_atlas_v03", SCRIPT)
assert SPEC and SPEC.loader
build = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = build
SPEC.loader.exec_module(build)

BASE = ROOT / "data/evidence/cirsium_flower_colour_atlas_v0_2.csv"
EXPANSION = ROOT / "data/evidence/cirsium_flower_colour_atlas_v0_3_expansion_evidence.csv"


class ColourAtlasV03Tests(unittest.TestCase):
    def built(self):
        return build.build(BASE, EXPANSION)

    def test_v03_reaches_total_tip_gate_without_white_invention(self):
        _, rows, summary = self.built()
        self.assertEqual(len(rows), 32)
        self.assertEqual(summary["contract_version"], "cirsium_flower_colour_atlas_v0_3")
        self.assertEqual(summary["reviewed_record_count"], 31)
        self.assertEqual(summary["rate_fit_eligible_unique_taxa"], 20)
        self.assertEqual(summary["rate_fit_eligible_state_counts"], {"C": 17, "W": 3})
        self.assertTrue(summary["readiness_conditions"]["minimum_taxon_tips"])
        self.assertTrue(summary["readiness_conditions"]["minimum_coloured_tips"])
        self.assertTrue(summary["readiness_conditions"]["minimum_phylogeny_contexts"])
        self.assertFalse(summary["readiness_conditions"]["minimum_white_tips"])
        self.assertFalse(summary["transition_rate_fit_ready"])
        self.assertEqual(summary["readiness_blockers"], ["minimum_white_tips"])

    def test_six_new_fixed_coloured_taxa_are_eligible(self):
        _, rows, _ = self.built()
        expected = {
            "Cirsium suffultum",
            "Cirsium nipponicum var. incomptum",
            "Cirsium kujuense",
            "Cirsium japonicum var. japonicum",
            "Cirsium fanjingshanense",
            "Cirsium kamtschaticum",
        }
        mapped = {row["accepted_taxon"]: row for row in rows}
        for taxon in expected:
            self.assertIn(taxon, mapped)
            self.assertEqual(mapped[taxon]["binary_colour_code"], "C")
            self.assertEqual(mapped[taxon]["rate_fit_eligible"], "yes")
            self.assertEqual(mapped[taxon]["review_status"], "reviewed")

    def test_amplexifolium_is_preserved_as_polymorphic(self):
        _, rows, _ = self.built()
        row = next(r for r in rows if r["accepted_taxon"] == "Cirsium amplexifolium")
        self.assertEqual(row["binary_colour_code"], "P")
        self.assertEqual(row["colour_state"], "polymorphic")
        self.assertEqual(row["rate_fit_eligible"], "no")
        self.assertIn("not morph-linked", row["rate_fit_exclusion_reason"])

    def test_henryi_is_not_present_as_a_rate_fit_white_tip(self):
        _, rows, _ = self.built()
        henryi = [r for r in rows if r["accepted_taxon"] == "Cirsium henryi"]
        self.assertEqual(henryi, [])
        eligible_white = {
            r["accepted_taxon"]
            for r in rows
            if r["rate_fit_eligible"] == "yes" and r["binary_colour_code"] == "W"
        }
        self.assertEqual(
            eligible_white,
            {"Cirsium brevicaule", "Cirsium japonicum var. albescens", "Cirsium kawakamii"},
        )

    def test_output_round_trip(self):
        with tempfile.TemporaryDirectory() as td:
            fieldnames, rows, _ = self.built()
            out = Path(td) / "atlas.csv"
            build.write_csv(out, fieldnames, rows)
            summary = build.validator.validate(out)
            self.assertEqual(summary["rate_fit_eligible_unique_taxa"], 20)
            self.assertEqual(summary["readiness_blockers"], ["minimum_white_tips"])


if __name__ == "__main__":
    unittest.main()
