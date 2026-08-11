#!/usr/bin/env python3
"""Tests for the Chang 2026 heavy-workflow preflight contract."""

from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = REPO_ROOT / "analysis"
if str(ANALYSIS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_DIR))

import build_chang2026_gene_tree_panel as panel_builder  # noqa: E402
import validate_chang2026_gene_tree_workflow_contract as mod  # noqa: E402


class ChangGeneTreeWorkflowContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.panel = self.root / "panel.csv"
        self.hypotheses = self.root / "hypotheses.csv"
        self.panel_rows = self._panel_rows()
        self._write_csv(self.panel, self.panel_rows)
        self.hypothesis_rows = self._hypothesis_rows()
        self._write_csv(self.hypotheses, self.hypothesis_rows)
        self.snakefile = (
            REPO_ROOT / "workflow" / "chang2026_gene_trees" / "Snakefile"
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    def _panel_rows(self) -> list[dict[str, str]]:
        specifications = [
            ("C. japonicum var. takaoense", "focal_colour_morph", 6),
            ("C. japonicum var. albescens", "white_sister_control", 2),
            (
                "C. japonicum var. australe",
                "coloured_flanking_introgression_control",
                3,
            ),
            (
                "C. japonicum var. fukienense",
                "coloured_flanking_introgression_control",
                4,
            ),
            ("C. japonicum", "coloured_root_context", 2),
            ("C. lineare", "outgroup", 2),
        ]
        focal = [
            ("FC", "ccy3559", "BP"),
            ("TJ", "ccy3807", "BP"),
            ("NH", "ccy3835", "BP"),
            ("WY", "ccy3560", "W"),
            ("FB", "ccy3629", "W"),
            ("LT", "ccy3839", "W"),
        ]
        rows: list[dict[str, str]] = []
        counter = 0
        for taxon, role, count in specifications:
            for within in range(count):
                counter += 1
                if role == "focal_colour_morph":
                    code, voucher, morph = focal[within]
                else:
                    code = f"S{counter:02d}"
                    voucher = f"ccy{8000 + counter}"
                    morph = ""
                run = f"SRR{counter:08d}"
                rows.append(
                    {
                        "sample_id": f"{code}_{voucher}",
                        "taxon": taxon,
                        "code": code,
                        "voucher": voucher,
                        "morph": morph,
                        "flower_colour_state": "white"
                        if morph == "W" or "albescens" in taxon
                        else "bluish-purple"
                        if morph == "BP"
                        else "coloured",
                        "panel_role": role,
                        "matched_run": run,
                        "matched_experiment": f"SRX{counter:08d}",
                        "matched_biosample": f"SAMN{counter:08d}",
                        "matched_spots": str(counter * 1000),
                        "read_count_relation": (
                            "exact_paired_end_raw_reads_equals_2x_spots"
                        ),
                        "run_match_status": "verified_unique_voucher_token",
                        "run_match_confidence": "verified",
                        "public_transcriptome_status": (
                            "not_recovered_by_current_ncbi_query"
                        ),
                        "preferred_sequence_source": run,
                        "tsa_accessions": "",
                        "assembly_accessions": "",
                        "de_novo_required": "true",
                        "analysis_panel": "sinocirsium17_plus_lineare2",
                    }
                )
        return rows

    def _hypothesis_rows(self) -> list[dict[str, object]]:
        nearest = REPO_ROOT / "analysis" / (
            "chang2026_takaoense_nearest_no_regain_topologies.csv"
        )
        summary = REPO_ROOT / "analysis" / (
            "chang2026_takaoense_topology_robustness_summary.json"
        )
        with nearest.open(encoding="utf-8-sig", newline="") as handle:
            nearest_rows = list(csv.DictReader(handle))
        return panel_builder.build_hypotheses(
            nearest_rows,
            json.loads(summary.read_text(encoding="utf-8")),
        )

    def test_actual_snakefile_has_complete_ordered_dag(self) -> None:
        rules, runner_hashes, env_hashes = mod.validate_workflow_files(
            self.snakefile
        )
        self.assertEqual(rules, list(mod.EXPECTED_RULES))
        self.assertEqual(set(runner_hashes), set(mod.EXPECTED_RUNNERS))
        self.assertEqual(set(env_hashes), set(mod.EXPECTED_ENVS))

    def test_contract_accepts_nineteen_samples_and_eight_hypotheses(self) -> None:
        config, summary = mod.build_contract(
            self.panel,
            self.hypotheses,
            self.snakefile,
            self.root / "results",
        )
        self.assertEqual(summary["panel_rows"], 19)
        self.assertEqual(summary["unique_official_runs"], 19)
        self.assertEqual(summary["focal_morph_counts"], {"BP": 3, "W": 3})
        self.assertEqual(summary["hypothesis_count"], 8)
        self.assertEqual(
            summary["hypothesis_class_counts"],
            {
                "nearest_loss_only_topology": 7,
                "topology_supported_candidate_regain": 1,
            },
        )
        self.assertEqual(len(summary["outgroup_sample_ids"]), 2)
        self.assertFalse(summary["heavy_computation_executed"])
        self.assertEqual(config["panel_csv"], str(self.panel.resolve()))
        self.assertEqual(config["hypotheses_csv"], str(self.hypotheses.resolve()))

    def test_duplicate_hypothesis_topology_fails(self) -> None:
        rows = [dict(row) for row in self.hypothesis_rows]
        rows[1]["topology_newick"] = rows[0]["topology_newick"]
        duplicate = self.root / "duplicate_hypotheses.csv"
        self._write_csv(duplicate, rows)
        with self.assertRaisesRegex(ValueError, "duplicate topologies"):
            mod.validate_hypothesis_contract(duplicate)

    def test_wrong_panel_role_count_fails(self) -> None:
        rows = [dict(row) for row in self.panel_rows]
        rows[0]["panel_role"] = "white_sister_control"
        wrong = self.root / "wrong_roles.csv"
        self._write_csv(wrong, rows)
        with self.assertRaisesRegex(ValueError, "Unexpected panel roles"):
            mod.build_contract(
                wrong,
                self.hypotheses,
                self.snakefile,
                self.root / "results",
            )

    def test_rule_parser_rejects_missing_stage(self) -> None:
        text = self.snakefile.read_text(encoding="utf-8")
        observed = mod.extract_rule_names(
            text.replace("rule orthofinder:", "# removed orthofinder:")
        )
        self.assertNotEqual(observed, list(mod.EXPECTED_RULES))


if __name__ == "__main__":
    unittest.main()
