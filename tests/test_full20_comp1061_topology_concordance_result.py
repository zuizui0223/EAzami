import json
import pathlib
import statistics
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULT = ROOT / "data" / "evidence" / "full20_comp1061_topology_concordance_result_v1.json"


class Full20Comp1061TopologyConcordanceResultTest(unittest.TestCase):
    def test_frozen_result_is_internally_consistent(self):
        x = json.loads(RESULT.read_text())
        branches = x["branches"]

        self.assertEqual(x["contract_version"], "full20_comp1061_topology_concordance_result_v1")
        self.assertEqual(x["source"]["workflow_run_id"], 32614242600)
        self.assertEqual(x["source"]["artifact_id"], 9486472031)
        self.assertEqual(x["source"]["frozen_loci"], 153)
        self.assertEqual(x["execution"]["gene_tree_seed"], 20260822)
        self.assertEqual(x["execution"]["gene_trees_completed"], 153)
        self.assertEqual(x["execution"]["internal_branches"], 18)
        self.assertEqual(len(branches), 18)
        self.assertEqual(len({tuple(b["split"]) for b in branches}), 18)

        gcf = [b["gCF"] for b in branches]
        scf = [b["sCF"] for b in branches]
        self.assertAlmostEqual(statistics.median(gcf), x["summary"]["gCF_median"], places=6)
        self.assertAlmostEqual(statistics.median(scf), x["summary"]["sCF_median"], places=6)

        for b in branches:
            expected = b["sCF"] > max(b["sDF1"], b["sDF2"])
            self.assertEqual(b["primary_site_plurality"], expected)

        challenged = [b for b in branches if not b["primary_site_plurality"]]
        self.assertEqual(len(challenged), 2)
        self.assertEqual(x["summary"]["primary_site_plurality_branches"], 16)
        self.assertEqual(x["summary"]["site_challenged_branches"], 2)
        self.assertEqual(
            {tuple(b["split"]) for b in challenged},
            {
                ("Cirsium_kujuense", "Cirsium_nipponicum_var_incomptum"),
                ("Cirsium_maritimum", "Cirsium_nippoense"),
            },
        )

        self.assertFalse(x["execution"]["data_driven_locus_filtering_applied"])
        self.assertFalse(x["execution"]["data_driven_branch_filtering_applied"])
        self.assertTrue(x["decision"]["topology_concordance_execution_completed"])
        self.assertTrue(x["decision"]["alternative_topology_sensitivity_required"])
        self.assertFalse(x["decision"]["rate_fit_execution_allowed"])
        self.assertEqual(x["decision"]["independent_rate_fit_blocker"], "minimum_white_tips")


if __name__ == "__main__":
    unittest.main()
