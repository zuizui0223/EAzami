#!/usr/bin/env python3
"""Tests for the unified East Asia nuclear coverage builder."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "analysis" / "build_east_asia_nuclear_coverage.py"
SPEC = importlib.util.spec_from_file_location("build_east_asia_nuclear_coverage", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
coverage = importlib.util.module_from_spec(SPEC)
sys.modules["build_east_asia_nuclear_coverage"] = coverage
SPEC.loader.exec_module(coverage)


class EastAsiaCoverageTests(unittest.TestCase):
    def test_canonical_taxon_expands_abbreviation(self) -> None:
        self.assertEqual(
            coverage.canonical_taxon("C. japonicum var. takaoense"),
            "cirsium japonicum var. takaoense",
        )
        self.assertEqual(
            coverage.canonical_taxon("Cirsium_japonicum  var.  takaoense"),
            "cirsium japonicum var. takaoense",
        )

    def test_moreyra_tip_remains_population_target(self) -> None:
        master = {
            "accepted_taxon": "Cirsium pendulum",
            "region": "Japan/NE Asia",
            "subsection_or_group": "Pendulum",
            "flower_colour_state": "polymorphic_purple_white",
            "ploidy_or_chromosome": "2n=34",
            "transition_role": "within_species_white_polymorphism_and_transregional_bridge",
            "radseq_priority": "A",
            "nuclear_phylogeny_status": "project_membership_unverified",
        }
        moreyra = {
            "project_tip_status": coverage.MOREYRA_EXACT,
            "supplement_tree_codes": "Cirsium pendulum",
            "biosamples": "SAMN1",
            "runs": "SRR1",
        }
        row = coverage.classify_row(master, moreyra, [], [])
        self.assertEqual(row["best_species_level_nuclear_status"], "global_target_capture_tip_verified")
        self.assertEqual(
            row["species_backbone_gap_class"],
            "species_placement_resolved_in_modern_nuclear_data",
        )
        self.assertEqual(row["population_or_morph_gap_class"], "population_or_morph_history_missing")
        self.assertEqual(row["recommended_next_data"], "population_RAD_or_resequencing_plus_ploidy")

    def test_takaoense_requires_morph_recovery_before_population_genomics(self) -> None:
        master = {
            "accepted_taxon": "Cirsium japonicum var. takaoense",
            "region": "Taiwan",
            "subsection_or_group": "Sinocirsium",
            "flower_colour_state": "polymorphic_white_bluish_purple",
            "ploidy_or_chromosome": "2n=34",
            "transition_role": "within_lineage_polymorphism",
            "radseq_priority": "A",
            "nuclear_phylogeny_status": "resolved_local_backbone",
        }
        chang = [
            {
                "bioproject": "PRJNA1311153",
                "sample_morph_resolution": "sample morph not identified in supplement",
            },
            {
                "bioproject": "PRJNA1311153",
                "sample_morph_resolution": "sample morph not identified in supplement",
            },
        ]
        row = coverage.classify_row(master, None, [], chang)
        self.assertEqual(row["chang2026_sample_count"], "2")
        self.assertEqual(row["best_species_level_nuclear_status"], "phylotranscriptomic_local_backbone")
        self.assertEqual(
            row["recommended_next_data"],
            "recover_published_morph_identity_then_population_RAD_or_resequencing",
        )

    def test_transition_critical_taxon_without_nuclear_tip_gets_two_stage_action(self) -> None:
        master = {
            "accepted_taxon": "Cirsium candidate",
            "region": "Korea",
            "subsection_or_group": "unknown",
            "flower_colour_state": "white_candidate",
            "ploidy_or_chromosome": "",
            "transition_role": "independent_white_candidate",
            "radseq_priority": "A",
            "nuclear_phylogeny_status": "not_verified_in_current_nuclear_seed",
        }
        row = coverage.classify_row(master, None, [], [])
        self.assertEqual(
            row["species_backbone_gap_class"],
            "candidate_species_gap_pending_synonym_and_other_dataset_audit",
        )
        self.assertEqual(
            row["recommended_next_data"],
            "verify_synonyms_then_Compositae1061_target_capture_then_population_genomics",
        )

    def test_multiple_sources_are_retained(self) -> None:
        master = {
            "accepted_taxon": "Cirsium lineare",
            "region": "East Asia",
            "subsection_or_group": "Spanioptilon",
            "flower_colour_state": "coloured",
            "ploidy_or_chromosome": "2n=30",
            "transition_role": "coloured_backbone_anchor",
            "radseq_priority": "B",
            "nuclear_phylogeny_status": "resolved_outgroup_anchor",
        }
        moreyra = {
            "project_tip_status": coverage.MOREYRA_EXACT,
            "supplement_tree_codes": "Cirsium lineare",
            "biosamples": "SAMN1",
            "runs": "SRR1",
        }
        c25 = [{"bioproject": "PRJNA1158676"}]
        c26 = [{"bioproject": "PRJNA1311153", "sample_morph_resolution": "outgroup/root reference"}]
        row = coverage.classify_row(master, moreyra, c25, c26)
        self.assertEqual(row["best_species_level_nuclear_status"], "multiple_modern_nuclear_sources")
        self.assertEqual(
            row["modern_nuclear_evidence_sources"],
            "Moreyra2025_PRJNA957074|Chang2025_PRJNA1158676|Chang2026_PRJNA1311153",
        )


if __name__ == "__main__":
    unittest.main()
