from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "analysis/build_colour_rate_comp1061_bridge_panel.py"
SPEC = importlib.util.spec_from_file_location("bridge", MODULE_PATH)
assert SPEC and SPEC.loader
bridge = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = bridge
SPEC.loader.exec_module(bridge)


class ColourRateComp1061BridgeTests(unittest.TestCase):
    def test_current_atlas_partition_is_exact(self):
        rows = bridge.atlas_eligible(
            ROOT / "data/evidence/cirsium_flower_colour_atlas_v0_3.csv"
        )
        taxa = {row["accepted_taxon"] for row in rows}
        self.assertEqual(len(taxa), 20)
        self.assertEqual(
            taxa,
            bridge.CHANG_RECON_TAXA
            | bridge.CHANG2025_DIRECT_TAXA
            | bridge.MOREYRA_TAXA,
        )

    def test_frozen_reference_is_compatibility_only(self):
        x = bridge.frozen_reference_contract(
            ROOT / "data/evidence/comp1061_original_reference_contract_v1.json"
        )
        self.assertEqual(x["locus_count"], 1061)
        self.assertTrue(x["compatibility_reanalysis_usable"])
        self.assertFalse(x["moreyra_augmented_reference_recovered"])

    def test_primary_selection_prefers_maximum_spots_not_colour(self):
        base = {
            "tip_id": "Taxon_A",
            "accepted_taxon": "Taxon A",
            "binary_colour_code": "W",
            "atlas_record_id": "A",
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
        }
        rows = []
        for run, spots, voucher in (("SRR1", "10", "z"), ("SRR2", "20", "a"), ("SRR3", "20", "b")):
            row = dict(base)
            row.update({"run": run, "spots": spots, "voucher": voucher, "source_sample_code": voucher, "sra_scientific_name": "Taxon A"})
            rows.append(row)
        primary, all_rows = bridge.choose_primary(rows)
        self.assertEqual(primary[0]["run"], "SRR2")
        self.assertEqual(sum(row["primary_tip"] == "yes" for row in all_rows), 1)

    def test_tip_id_is_newick_safe(self):
        self.assertEqual(
            bridge.safe_tip_id("Cirsium japonicum var. albescens"),
            "Cirsium_japonicum_var_albescens",
        )


if __name__ == "__main__":
    unittest.main()
