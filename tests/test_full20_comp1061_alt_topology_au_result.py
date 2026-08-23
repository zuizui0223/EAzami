import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULT = ROOT / "data" / "evidence" / "full20_comp1061_alt_topology_au_result_v1.json"


class Full20Comp1061AlternativeTopologyAUResultTest(unittest.TestCase):
    def test_frozen_au_result_is_internally_consistent(self):
        x = json.loads(RESULT.read_text())
        rows = x["candidates"]
        alpha = x["test_contract"]["au_rejection_alpha"]

        self.assertEqual(x["contract_version"], "full20_comp1061_alt_topology_au_result_v1")
        self.assertEqual(x["source"]["workflow_run_id"], 32614839764)
        self.assertEqual(x["source"]["artifact_id"], 9486643703)
        self.assertEqual(x["source"]["candidate_set_sha256"], "359e87c0a2b057d7c3aa6bd6e1600487431234dbc78c7c42b246769633caac18")
        self.assertEqual(x["test_contract"]["candidate_count"], 9)
        self.assertEqual(x["test_contract"]["rell_replicates"], 10000)
        self.assertEqual(x["test_contract"]["au_seed"], 20260822)
        self.assertEqual(len(rows), 9)
        self.assertEqual([r["index"] for r in rows], list(range(1, 10)))
        self.assertEqual(len({r["candidate_id"] for r in rows}), 9)

        for row in rows:
            self.assertEqual(row["au_rejected"], row["p_AU"] < alpha)

        nonrejected = [r for r in rows if not r["au_rejected"]]
        rejected = [r for r in rows if r["au_rejected"]]
        self.assertEqual(len(nonrejected), 6)
        self.assertEqual(len(rejected), 3)
        self.assertEqual(x["summary"]["au_nonrejected_candidates"], 6)
        self.assertEqual(x["summary"]["au_rejected_candidates"], 3)

        best = max(rows, key=lambda r: r["logL"])
        self.assertEqual(best["candidate_id"], x["summary"]["maximum_likelihood_candidate"])
        self.assertEqual(best["index"], 1)
        best_alt = max(rows[1:], key=lambda r: r["logL"])
        self.assertEqual(best_alt["candidate_id"], x["summary"]["best_alternative_candidate"])
        self.assertEqual(best_alt["index"], 3)

        # The only AU-rejected local state is the second NNI around the
        # kujuense/incomptum edge, in every maritimum/nippoense context.
        self.assertEqual({r["kujuense_incomptum"] for r in rejected}, {"swap_second"})
        self.assertEqual(
            {r["maritimum_nippoense"] for r in rejected},
            {"primary", "swap_first", "swap_second"},
        )
        self.assertEqual(
            {r["kujuense_incomptum"] for r in nonrejected},
            {"primary", "swap_first"},
        )
        for ki_state in ("primary", "swap_first"):
            surviving_mn = {
                r["maritimum_nippoense"]
                for r in nonrejected
                if r["kujuense_incomptum"] == ki_state
            }
            self.assertEqual(surviving_mn, {"primary", "swap_first", "swap_second"})

        closest_rejected = max(rejected, key=lambda r: r["p_AU"])
        self.assertEqual(closest_rejected["index"], 7)
        self.assertAlmostEqual(closest_rejected["p_AU"], 0.0478)

        self.assertTrue(x["decision"]["alternative_topology_sensitivity_completed"])
        self.assertTrue(x["decision"]["primary_tree_retained_as_maximum_likelihood_reference"])
        self.assertFalse(x["decision"]["primary_topology_uniquely_supported"])
        self.assertTrue(x["decision"]["topology_uncertainty_must_propagate_downstream"])
        self.assertFalse(x["decision"]["data_driven_candidate_filtering_applied"])
        self.assertFalse(x["decision"]["data_driven_locus_filtering_applied"])
        self.assertFalse(x["decision"]["rate_fit_execution_allowed"])
        self.assertEqual(x["decision"]["independent_rate_fit_blocker"], "minimum_white_tips")


if __name__ == "__main__":
    unittest.main()
