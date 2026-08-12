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

SCRIPT = ANALYSIS / "build_cirsium_flower_colour_atlas_v0_2.py"
SPEC = importlib.util.spec_from_file_location("build_colour_atlas_v02", SCRIPT)
assert SPEC and SPEC.loader
build = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = build
SPEC.loader.exec_module(build)


class ColourAtlasV02Tests(unittest.TestCase):
    def built(self):
        return build.build(
            ROOT / "data/evidence/cirsium_flower_colour_atlas_v0_1.csv",
            ROOT / "data/evidence/moreyra2025_japan_colour_text_evidence_v1.csv",
        )

    def test_v02_expands_reviewed_mapped_taxa(self):
        _, rows, summary = self.built()
        self.assertEqual(len(rows), 25)
        self.assertEqual(summary["contract_version"], "cirsium_flower_colour_atlas_v0_2")
        self.assertEqual(summary["reviewed_record_count"], 24)
        self.assertEqual(summary["rate_fit_eligible_unique_taxa"], 14)
        self.assertEqual(summary["rate_fit_eligible_state_counts"], {"C": 11, "W": 3})
        self.assertEqual(
            set(summary["rate_fit_eligible_phylogeny_contexts"]),
            {"Arenicola", "Nipponocirsium", "Sinocirsium", "Moreyra2025_Japan38"},
        )
        self.assertFalse(summary["transition_rate_fit_ready"])
        self.assertEqual(
            set(summary["readiness_blockers"]),
            {"minimum_taxon_tips", "minimum_white_tips"},
        )

    def test_fixed_moreyra_japan_tips_are_eligible(self):
        _, rows, _ = self.built()
        expected = {
            "Cirsium alpicola",
            "Cirsium gyojanum",
            "Cirsium maritimum",
            "Cirsium nippoense",
            "Cirsium yezoense",
        }
        mapped = {
            row["accepted_taxon"]: row
            for row in rows
            if row["record_id"].startswith("ATL-MJ")
        }
        self.assertTrue(expected <= set(mapped))
        for taxon in expected:
            self.assertEqual(mapped[taxon]["binary_colour_code"], "C")
            self.assertEqual(mapped[taxon]["rate_fit_eligible"], "yes")
            self.assertEqual(mapped[taxon]["evidence_status"], "official_database_text_direct")
            self.assertEqual(mapped[taxon]["phylogeny_context"], "Moreyra2025_Japan38")

    def test_white_form_taxa_remain_polymorphic(self):
        _, rows, _ = self.built()
        mapped = {
            row["accepted_taxon"]: row
            for row in rows
            if row["record_id"].startswith("ATL-MJ")
        }
        for taxon in (
            "Cirsium aomorense",
            "Cirsium sieboldii",
            "Cirsium pendulum",
        ):
            self.assertEqual(mapped[taxon]["binary_colour_code"], "P")
            self.assertEqual(mapped[taxon]["colour_state"], "polymorphic")
            self.assertEqual(mapped[taxon]["rate_fit_eligible"], "no")
            self.assertIn("not morph-linked", mapped[taxon]["rate_fit_exclusion_reason"])

    def test_pending_seed_is_superseded_not_duplicated(self):
        _, rows, summary = self.built()
        self.assertEqual(
            summary["superseded_pending_taxa"],
            ["Cirsium pendulum", "Cirsium yezoense"],
        )
        for taxon in ("Cirsium pendulum", "Cirsium yezoense"):
            relevant = [row for row in rows if row["accepted_taxon"] == taxon and row["observation_unit"] == "taxon"]
            self.assertEqual(len(relevant), 1)
            self.assertEqual(relevant[0]["review_status"], "reviewed")

    def test_output_round_trip(self):
        with tempfile.TemporaryDirectory() as td:
            fieldnames, rows, summary = self.built()
            out = Path(td) / "atlas.csv"
            build.write_csv(out, fieldnames, rows)
            validated = build.validator.validate(out)
            self.assertEqual(validated["rate_fit_eligible_unique_taxa"], 14)
            self.assertEqual(summary["record_count"], 25)


if __name__ == "__main__":
    unittest.main()
