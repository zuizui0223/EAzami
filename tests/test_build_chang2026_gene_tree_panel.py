#!/usr/bin/env python3
"""Tests for the Chang 2026 Sinocirsium gene-tree panel builder."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ANALYSIS_DIR = Path(__file__).resolve().parents[1] / "analysis"
if str(ANALYSIS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_DIR))

import build_chang2026_gene_tree_panel as mod  # noqa: E402


class ChangGeneTreePanelTests(unittest.TestCase):
    def make_inputs(self):
        taxa = [
            ("C. japonicum", 2),
            ("C. japonicum var. albescens", 2),
            ("C. japonicum var. takaoense", 6),
            ("C. japonicum var. australe", 3),
            ("C. japonicum var. fukienense", 4),
            ("C. lineare", 2),
        ]
        reconciliation = []
        assemblies = []
        counter = 0
        for taxon, count in taxa:
            for index in range(1, count + 1):
                counter += 1
                voucher = f"voucher{counter:02d}"
                code = f"S{counter:02d}"
                if "takaoense" in taxon:
                    morph = "W" if index <= 3 else "BP"
                    colour = "white" if morph == "W" else "bluish-purple"
                else:
                    morph = ""
                    colour = "white" if "albescens" in taxon else "coloured"
                reconciliation.append(
                    {
                        "taxon": taxon,
                        "code": code,
                        "voucher": voucher,
                        "published_figure_label": morph,
                        "flower_colour_state": colour,
                        "matched_run": f"SRR{counter:06d}",
                        "matched_experiment": f"SRX{counter:06d}",
                        "matched_biosample": f"SAMN{counter:06d}",
                        "matched_library_layout": "PAIRED",
                        "matched_spots": str(counter * 1000),
                        "read_count_relation": (
                            "exact_paired_end_raw_reads_equals_2x_spots"
                            if counter <= 9
                            else "not_matching_reported_raw_reads"
                        ),
                        "match_status": "verified_unique_read_count_and_taxon",
                        "match_confidence": "verified",
                    }
                )
                assemblies.append(
                    {
                        "voucher": voucher,
                        "public_transcriptome_status": "not_recovered_by_current_ncbi_query",
                        "preferred_public_source": "de_novo_from_official_SRA",
                        "tsa_accessions": "",
                        "assembly_accessions": "",
                    }
                )
        return reconciliation, assemblies

    def test_builds_expected_nineteen_sample_panel(self) -> None:
        reconciliation, assemblies = self.make_inputs()
        panel = mod.build_panel(reconciliation, assemblies)
        self.assertEqual(len(panel), 19)
        self.assertEqual(len({row["matched_run"] for row in panel}), 19)
        self.assertEqual({row["library_layout"] for row in panel}, {"PAIRED"})
        self.assertEqual(
            sum(row["panel_role"] == "focal_colour_morph" for row in panel),
            6,
        )
        self.assertEqual(
            sum(row["panel_role"] == "white_sister_control" for row in panel),
            2,
        )
        self.assertEqual(
            sum(row["panel_role"] == "outgroup" for row in panel),
            2,
        )
        self.assertTrue(all(row["de_novo_required"] == "true" for row in panel))
        self.assertEqual(
            sum(row["read_count_relation"] == "not_matching_reported_raw_reads" for row in panel),
            10,
        )

    def test_published_tsa_replaces_de_novo_source(self) -> None:
        reconciliation, assemblies = self.make_inputs()
        assemblies[0] = {
            **assemblies[0],
            "public_transcriptome_status": "public_tsa_recovered",
            "preferred_public_source": "NCBI_TSA",
            "tsa_accessions": "GABC00000000",
        }
        panel = mod.build_panel(reconciliation, assemblies)
        row = next(item for item in panel if item["voucher"] == "voucher01")
        self.assertEqual(row["preferred_sequence_source"], "GABC00000000")
        self.assertEqual(row["de_novo_required"], "false")
        self.assertEqual(row["library_layout"], "PAIRED")

    def test_unresolved_run_fails(self) -> None:
        reconciliation, assemblies = self.make_inputs()
        reconciliation[0]["match_confidence"] = "ambiguous"
        with self.assertRaises(ValueError):
            mod.build_panel(reconciliation, assemblies)

    def test_duplicate_run_fails(self) -> None:
        reconciliation, assemblies = self.make_inputs()
        reconciliation[1]["matched_run"] = reconciliation[0]["matched_run"]
        with self.assertRaises(ValueError):
            mod.build_panel(reconciliation, assemblies)

    def test_missing_official_library_layout_fails(self) -> None:
        reconciliation, assemblies = self.make_inputs()
        reconciliation[0]["matched_library_layout"] = ""
        with self.assertRaisesRegex(ValueError, "LibraryLayout"):
            mod.build_panel(reconciliation, assemblies)

    def test_unsupported_official_library_layout_fails(self) -> None:
        reconciliation, assemblies = self.make_inputs()
        reconciliation[0]["matched_library_layout"] = "UNKNOWN"
        with self.assertRaisesRegex(ValueError, "LibraryLayout"):
            mod.build_panel(reconciliation, assemblies)

    def test_missing_taxon_sample_fails(self) -> None:
        reconciliation, assemblies = self.make_inputs()
        reconciliation.pop()
        assemblies.pop()
        with self.assertRaises(ValueError):
            mod.build_panel(reconciliation, assemblies)

    def test_panel_roles(self) -> None:
        self.assertEqual(
            mod.panel_role("C. japonicum var. takaoense"),
            "focal_colour_morph",
        )
        self.assertEqual(
            mod.panel_role("C. japonicum var. albescens"),
            "white_sister_control",
        )
        self.assertEqual(
            mod.panel_role("C. japonicum var. fukienense"),
            "coloured_flanking_introgression_control",
        )
        self.assertEqual(mod.panel_role("C. lineare"), "outgroup")

    def test_hypothesis_table_has_one_regain_and_seven_loss_only_rows(self) -> None:
        nearest = [
            {
                "sample_topology_newick": f"(A,B{i});",
                "rooted_rf_distance_from_published": "4",
                "sinocirsium_coloured_root_minimum_changes": "2",
                "sinocirsium_coloured_root_optimal_histories": "2L+0R",
                "no_regain_penalty": "0",
            }
            for i in range(7)
        ]
        robustness = {
            "published_topology_newick": "((A,B),C);",
            "published_minimum_changes": 2,
            "published_optimal_histories": "1L+1R",
            "published_no_regain_penalty": 2,
        }
        hypotheses = mod.build_hypotheses(nearest, robustness)
        self.assertEqual(len(hypotheses), 8)
        self.assertEqual(hypotheses[0]["hypothesis_id"], "H_REG_PUBLISHED")
        self.assertEqual(
            sum(row["history_class"] == "nearest_loss_only_topology" for row in hypotheses),
            7,
        )

    def test_summary_counts_morphs_sources_and_layouts(self) -> None:
        reconciliation, assemblies = self.make_inputs()
        panel = mod.build_panel(reconciliation, assemblies)
        nearest = [
            {
                "sample_topology_newick": f"(A,B{i});",
                "rooted_rf_distance_from_published": "4",
                "sinocirsium_coloured_root_minimum_changes": "2",
                "sinocirsium_coloured_root_optimal_histories": "2L+0R",
                "no_regain_penalty": "0",
            }
            for i in range(7)
        ]
        hypotheses = mod.build_hypotheses(
            nearest,
            {
                "published_topology_newick": "((A,B),C);",
                "published_minimum_changes": 2,
                "published_optimal_histories": "1L+1R",
                "published_no_regain_penalty": 2,
            },
        )
        summary = mod.build_summary(panel, hypotheses)
        self.assertEqual(summary["sample_count"], 19)
        self.assertEqual(summary["takaoense_sample_count"], 6)
        self.assertEqual(summary["white_takaoense_count"], 3)
        self.assertEqual(summary["bluish_purple_takaoense_count"], 3)
        self.assertEqual(summary["official_library_layout_counts"], {"PAIRED": 19})
        self.assertEqual(summary["de_novo_required_count"], 19)
        self.assertEqual(summary["hypothesis_count"], 8)


if __name__ == "__main__":
    unittest.main()
