import hashlib
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PREFLIGHT = ROOT / "data" / "evidence" / "full20_comp1061_topology_concordance_preflight_v1.json"
TREE = ROOT / "data" / "evidence" / "full20_comp1061_primary_tree_v1.nwk"
LOCI = ROOT / "data" / "evidence" / "full20_comp1061_saff_root_153_loci_v1.txt"


class Full20Comp1061TopologyConcordancePreflightTest(unittest.TestCase):
    def test_predeclared_topology_sensitivity_contract(self):
        x = json.loads(PREFLIGHT.read_text())
        loci = [v.strip() for v in LOCI.read_text().splitlines() if v.strip()]

        self.assertEqual(x["contract_version"], "full20_comp1061_topology_concordance_preflight_v1")
        self.assertEqual(hashlib.sha256(TREE.read_bytes()).hexdigest(), x["source_primary_tree"]["sha256"])
        self.assertEqual(len(loci), 153)
        self.assertEqual(x["source_alignments"]["frozen_loci"], 153)
        self.assertEqual(x["gene_tree_analysis"]["expected_locus_trees"], 153)
        self.assertEqual(x["site_concordance_factor"]["seed"], 20260822)
        self.assertEqual(x["site_concordance_factor"]["quartets_per_internal_branch"], 100)
        self.assertEqual(x["site_concordance_factor"]["primary_model_family"], "TIM3+F+R3")
        self.assertIsNone(x["completion_gate"]["minimum_gcf_for_acceptance"])
        self.assertIsNone(x["completion_gate"]["minimum_scf_for_acceptance"])
        self.assertFalse(x["completion_gate"]["data_driven_branch_removal_allowed"])
        self.assertFalse(x["completion_gate"]["data_driven_locus_removal_allowed"])
        self.assertTrue(x["promotion_boundary"]["topology_concordance_execution_allowed"])
        self.assertFalse(x["promotion_boundary"]["topology_sensitivity_completed"])
        self.assertFalse(x["promotion_boundary"]["rate_fit_execution_allowed"])
        self.assertEqual(x["promotion_boundary"]["independent_rate_fit_blocker"], "minimum_white_tips")


if __name__ == "__main__":
    unittest.main()
