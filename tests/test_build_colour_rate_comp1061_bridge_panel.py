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

ATLAS_PATH = ANALYSIS / "build_cirsium_flower_colour_atlas_v0_3.py"
ATLAS_SPEC = importlib.util.spec_from_file_location("atlas_v03_for_bridge", ATLAS_PATH)
assert ATLAS_SPEC and ATLAS_SPEC.loader
atlas_v03 = importlib.util.module_from_spec(ATLAS_SPEC)
sys.modules[ATLAS_SPEC.name] = atlas_v03
ATLAS_SPEC.loader.exec_module(atlas_v03)

MODULE_PATH = ANALYSIS / "build_colour_rate_comp1061_bridge_panel.py"
SPEC = importlib.util.spec_from_file_location("bridge", MODULE_PATH)
assert SPEC and SPEC.loader
bridge = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = bridge
SPEC.loader.exec_module(bridge)

BASE = ROOT / "data/evidence/cirsium_flower_colour_atlas_v0_2.csv"
EXPANSION = ROOT / "data/evidence/cirsium_flower_colour_atlas_v0_3_expansion_evidence.csv"


class ColourRateComp1061BridgeTests(unittest.TestCase):
    def test_current_atlas_partition_is_exact(self):
        fieldnames, atlas_rows, _summary = atlas_v03.build(BASE, EXPANSION)
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "atlas_v0_3.csv"
            atlas_v03.write_csv(path, fieldnames, atlas_rows)
            rows = bridge.atlas_eligible(path)
        taxa = {row["accepted_taxon"] for row in rows}
        self.assertEqual(len(taxa), 20)
        self.assertEqual(
            taxa,
            bridge.CHANG_RECON_TAXA
            | bridge.CHANG2025_DIRECT_TAXA
            | bridge.MOREYRA_TAXA,
        )

    def test_corrected_official_project_partition_is_canonical(self):
        self.assertEqual(
            bridge.EXPECTED_STUDIES,
            {"Chang2025": 3, "Chang2026": 10, "Moreyra2025": 7},
        )
        self.assertEqual(sum(bridge.EXPECTED_STUDIES.values()), 20)
        self.assertEqual(len(bridge.CHANG_RECON_TAXA), 10)
        self.assertEqual(len(bridge.CHANG2025_DIRECT_TAXA), 3)
        self.assertEqual(len(bridge.MOREYRA_TAXA), 7)

    def test_frozen_reference_is_compatibility_only(self):
        x = bridge.frozen_reference_contract(
            ROOT / "data/evidence/comp1061_original_reference_contract_v1.json"
        )
        self.assertEqual(x["locus_count"], 1061)
        self.assertTrue(x["compatibility_reanalysis_usable"])
        self.assertFalse(x["moreyra_augmented_reference_recovered"])

    def test_primary_selection_prefers_maximum_spots_not_colour(self):
        rows = []
        for i in range(20):
            taxon = f"Taxon {i:02d}"
            base = {
                "tip_id": f"Taxon_{i:02d}",
                "accepted_taxon": taxon,
                "binary_colour_code": "W" if i < 3 else "C",
                "atlas_record_id": f"A{i}",
                "phylogeny_context": "x",
                "source_study": "Chang2026",
                "source_bioproject": "PRJNA1",
                "data_type": "leaf_rnaseq",
                "experiment": "",
                "biosample": "",
                "library_layout": "PAIRED",
                "bases": "0",
                "primary_tip": "no",
                "sample_selection_rule": "rule",
                "source_evidence": "e",
                "claim_limit": "c",
                "sra_scientific_name": taxon,
            }
            candidates = [(f"SRR{i:02d}A", "10", "z")]
            if i == 0:
                candidates += [("SRR00B", "20", "a"), ("SRR00C", "20", "b")]
            for run, spots, voucher in candidates:
                row = dict(base)
                row.update(
                    {
                        "run": run,
                        "spots": spots,
                        "voucher": voucher,
                        "source_sample_code": voucher,
                    }
                )
                rows.append(row)
        primary, all_rows = bridge.choose_primary(rows)
        first = next(row for row in primary if row["accepted_taxon"] == "Taxon 00")
        self.assertEqual(first["run"], "SRR00B")
        self.assertEqual(len(primary), 20)
        self.assertEqual(sum(row["primary_tip"] == "yes" for row in all_rows), 20)

    def test_tip_id_is_newick_safe(self):
        self.assertEqual(
            bridge.safe_tip_id("Cirsium japonicum var. albescens"),
            "Cirsium_japonicum_var_albescens",
        )


if __name__ == "__main__":
    unittest.main()
