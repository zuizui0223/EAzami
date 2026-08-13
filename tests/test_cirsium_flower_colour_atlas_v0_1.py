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

BUILD_PATH = ANALYSIS / "build_cirsium_flower_colour_atlas_v0_1.py"
BUILD_SPEC = importlib.util.spec_from_file_location("build_colour_atlas_v01", BUILD_PATH)
assert BUILD_SPEC and BUILD_SPEC.loader
build = importlib.util.module_from_spec(BUILD_SPEC)
sys.modules[BUILD_SPEC.name] = build
BUILD_SPEC.loader.exec_module(build)

VALIDATE_PATH = ANALYSIS / "validate_colour_atlas.py"
VALIDATE_SPEC = importlib.util.spec_from_file_location("validate_colour_atlas", VALIDATE_PATH)
assert VALIDATE_SPEC and VALIDATE_SPEC.loader
validate = importlib.util.module_from_spec(VALIDATE_SPEC)
sys.modules[VALIDATE_SPEC.name] = validate
VALIDATE_SPEC.loader.exec_module(validate)


class ColourAtlasV01Tests(unittest.TestCase):
    def source_rows(self):
        return build.build(
            ROOT / "data/evidence/arenicola_flower_colour_history_evidence_v1.csv",
            ROOT / "data/evidence/chang2026_sinocirsium_taxon_colour_evidence_v1.csv",
            ROOT / "data/evidence/chang2026_takaoense_morph_linked_public_samples_v1.csv",
            ROOT / "data/japan_colour_evidence_seed.csv",
        )

    def test_builder_keeps_source_layers_separate(self):
        rows = self.source_rows()
        self.assertEqual(len(rows), 19)
        units = {row["observation_unit"] for row in rows}
        self.assertEqual(units, {"taxon", "sample"})
        eligible = [row for row in rows if row["rate_fit_eligible"] == "yes"]
        self.assertEqual(len(eligible), 9)
        self.assertTrue(all(row["observation_unit"] == "taxon" for row in eligible))
        self.assertEqual(
            {row["phylogeny_context"] for row in eligible},
            {"Arenicola", "Nipponocirsium", "Sinocirsium"},
        )

    def test_source_backed_sinocirsium_adds_two_coloured_and_one_white_tip(self):
        rows = [row for row in self.source_rows() if row["record_id"].startswith("ATL-S")]
        self.assertEqual(len(rows), 3)
        states = {row["accepted_taxon"]: row["binary_colour_code"] for row in rows}
        self.assertEqual(
            states,
            {
                "Cirsium japonicum var. albescens": "W",
                "Cirsium japonicum var. australe": "C",
                "Cirsium japonicum var. fukienense": "C",
            },
        )
        self.assertTrue(all(row["rate_fit_eligible"] == "yes" for row in rows))
        fuk = next(row for row in rows if row["accepted_taxon"].endswith("var. fukienense"))
        self.assertIn("within binary C", fuk["polymorphic_context"])

    def test_takaoense_has_taxon_polymorphism_plus_six_direct_samples(self):
        rows = [
            row for row in self.source_rows()
            if row["accepted_taxon"] == "Cirsium japonicum var. takaoense"
        ]
        self.assertEqual(len(rows), 7)
        aggregate = next(row for row in rows if row["record_id"] == "ATL-T00")
        self.assertEqual(aggregate["observation_unit"], "taxon")
        self.assertEqual(aggregate["binary_colour_code"], "P")
        self.assertEqual(aggregate["rate_fit_eligible"], "no")

        samples = [row for row in rows if row["observation_unit"] == "sample"]
        self.assertEqual(len(samples), 6)
        self.assertEqual(sum(row["binary_colour_code"] == "W" for row in samples), 3)
        self.assertEqual(sum(row["binary_colour_code"] == "C" for row in samples), 3)
        self.assertTrue(all(row["review_status"] == "reviewed" for row in rows))
        self.assertTrue(all(row["rate_fit_eligible"] == "no" for row in rows))
        self.assertTrue(all(row["rate_fit_exclusion_reason"] for row in rows))

    def test_japan_seed_preserves_polymorphic_and_unknown(self):
        rows = [row for row in self.source_rows() if row["record_id"].startswith("ATL-J")]
        self.assertEqual(len(rows), 3)
        pendulum = next(row for row in rows if row["accepted_taxon"] == "Cirsium pendulum")
        self.assertEqual(pendulum["colour_state"], "polymorphic")
        self.assertEqual(pendulum["binary_colour_code"], "P")
        self.assertEqual(pendulum["review_status"], "pending")
        dips = next(row for row in rows if row["accepted_taxon"] == "Cirsium dipsacolepis")
        self.assertEqual(dips["binary_colour_code"], "U")
        self.assertEqual(dips["assessable"], "no")

    def test_generated_atlas_validates_and_is_not_rate_fit_ready(self):
        rows = self.source_rows()
        validate.validate_rows(build.FIELDS, rows)
        summary = validate.readiness_summary(rows)
        self.assertEqual(summary["record_count"], 19)
        self.assertEqual(summary["reviewed_record_count"], 16)
        self.assertEqual(summary["rate_fit_eligible_unique_taxa"], 9)
        self.assertEqual(summary["rate_fit_eligible_state_counts"], {"C": 6, "W": 3})
        self.assertEqual(
            summary["rate_fit_eligible_phylogeny_contexts"],
            ["Arenicola", "Nipponocirsium", "Sinocirsium"],
        )
        self.assertFalse(summary["transition_rate_fit_ready"])
        self.assertIn("minimum_taxon_tips", summary["readiness_blockers"])
        self.assertIn("minimum_white_tips", summary["readiness_blockers"])
        self.assertNotIn("minimum_coloured_tips", summary["readiness_blockers"])
        self.assertNotIn("minimum_phylogeny_contexts", summary["readiness_blockers"])

    def test_polymorphic_taxon_cannot_be_promoted_to_rate_fit(self):
        rows = self.source_rows()
        target = next(row for row in rows if row["accepted_taxon"] == "Cirsium pendulum")
        target["rate_fit_eligible"] = "yes"
        target["rate_fit_exclusion_reason"] = ""
        target["review_status"] = "reviewed"
        target["source_url"] = "https://example.invalid/direct"
        target["phylogeny_tip_candidate"] = "yes"
        target["evidence_status"] = "official_database_text_direct"
        with self.assertRaisesRegex(ValueError, "rate_fit_eligible=yes"):
            validate.validate_rows(build.FIELDS, rows)

    def test_sample_level_record_cannot_be_promoted_to_species_rate_fit(self):
        rows = self.source_rows()
        target = next(
            row for row in rows
            if row["accepted_taxon"] == "Cirsium japonicum var. takaoense"
            and row["observation_unit"] == "sample"
        )
        target["rate_fit_eligible"] = "yes"
        target["rate_fit_exclusion_reason"] = ""
        target["evidence_status"] = "direct_taxon_text"
        with self.assertRaisesRegex(ValueError, "observation_unit=taxon"):
            validate.validate_rows(build.FIELDS, rows)

    def test_builder_output_round_trips_validator(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "atlas.csv"
            summary = Path(td) / "summary.json"
            rows = self.source_rows()
            build.write_csv(output, rows)
            result = validate.validate(output, summary_path=summary)
            self.assertTrue(summary.is_file())
            self.assertEqual(result["rate_fit_eligible_unique_taxa"], 9)


if __name__ == "__main__":
    unittest.main()
