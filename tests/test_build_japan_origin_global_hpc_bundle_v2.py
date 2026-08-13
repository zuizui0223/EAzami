#!/usr/bin/env python3
"""Tests for the deduplicated Japan-origin HPC bundle and ASTRAL bridge."""

from __future__ import annotations

import csv
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "build_japan_origin_global_hpc_bundle_v2",
    ROOT / "analysis/build_japan_origin_global_hpc_bundle_v2.py",
)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


def panel(path: Path) -> None:
    fields = [
        "panel_id", "source_studies", "assay", "analysis_taxon_label", "voucher",
        "biosample", "run_accessions", "run_count", "japan38_member_ids",
        "shared_cross_paper_sample", "region", "location", "name_review_required",
    ]
    rows = []
    critical = (
        ["Cirsium brevicaule"] * 3
        + ["Cirsium irumtiense"] * 3
        + ["Cirsium dipsacolepis", "Cirsium lineare"]
    )
    for index in range(294):
        taxon = critical[index] if index < len(critical) else f"Cirsium synthetic_{index:03d}"
        runs = "SRR000001|SRR000002" if index == 0 else f"SRR{index + 100000:06d}"
        rows.append({
            "panel_id": f"P{index:04d}",
            "source_studies": "Moreyra2025" if index < 256 else "Chang2026",
            "assay": "target_capture" if index < 256 else "RNAseq",
            "analysis_taxon_label": taxon,
            "voucher": f"V{index}",
            "biosample": f"SAMN{index:06d}",
            "run_accessions": runs,
            "run_count": "2" if index == 0 else "1",
            "japan38_member_ids": "JPN_01" if index == 8 else "",
            "shared_cross_paper_sample": "false",
            "region": "Japan" if index < 256 else "Taiwan",
            "location": "fixture",
            "name_review_required": "true" if index == 9 else "false",
        })
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


class JapanOriginHpcV2Tests(unittest.TestCase):
    def test_astral_bridge_preserves_all_294_individuals(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "panel.csv"
            panel(source)
            rows = mod.read_panel(source)
            data = mod.sample_manifests(root, rows)
            species = mod.species_map(root, data)
            self.assertEqual(sum(int(row["n_tips"]) for row in species), 294)
            with (root / "astral_interpretation_manifest.csv").open(
                encoding="utf-8", newline=""
            ) as handle:
                bridge = list(csv.DictReader(handle))
            self.assertEqual(sum(int(row["constituent_tip_count"]) for row in bridge), 294)
            brev = next(row for row in bridge if row["analysis_taxon_label"] == "Cirsium brevicaule")
            self.assertEqual(brev["constituent_tip_count"], "3")

    def test_acceptance_and_integration_scripts_cover_four_scenarios(self) -> None:
        accept = mod.accept_script()
        self.assertIn("concat_topology.json", accept)
        self.assertIn("astral_topology.json", accept)
        self.assertIn("--tree-acceptance", accept)
        integrate = mod.integration_script()
        for scenario in (
            "bwa_concat", "bwa_astral", "blastx_concat", "blastx_astral"
        ):
            self.assertIn(scenario, integrate)
        self.assertIn("integrate_japan_origin_topology_sensitivities.py", integrate)

    def test_helper_bundle_contains_interpretation_and_gate_code(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mod.helper_sources(root)
            for filename in (
                "analyze_japan_origin_global_tree.py",
                "integrate_japan_origin_topology_sensitivities.py",
                "validate_japan_origin_astral_tree_v2.py",
                "validate_japan_origin_global_tree_v2.py",
            ):
                self.assertTrue((root / "helpers" / filename).is_file())


if __name__ == "__main__":
    unittest.main()
