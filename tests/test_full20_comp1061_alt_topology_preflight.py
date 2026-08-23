import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PREFLIGHT = ROOT / "data" / "evidence" / "full20_comp1061_alt_topology_preflight_v1.json"
RESULT = ROOT / "data" / "evidence" / "full20_comp1061_topology_concordance_result_v1.json"
TREE = ROOT / "data" / "evidence" / "full20_comp1061_primary_tree_v1.nwk"
BUILDER = ROOT / "analysis" / "build_comp1061_challenged_nni_candidates.py"


class Full20Comp1061AlternativeTopologyPreflightTest(unittest.TestCase):
    def test_predeclared_au_contract_and_candidate_generator(self):
        p = json.loads(PREFLIGHT.read_text())
        r = json.loads(RESULT.read_text())

        self.assertEqual(p["contract_version"], "full20_comp1061_alt_topology_preflight_v1")
        self.assertEqual(p["source_concordance_result"]["workflow_run_id"], 32614242600)
        self.assertEqual(p["source_alignment"]["workflow_run_id"], 32575064385)
        self.assertEqual(p["source_alignment"]["frozen_loci"], 153)
        self.assertEqual(p["candidate_contract"]["candidate_count"], 9)
        self.assertEqual(p["candidate_contract"]["tip_count"], 21)
        self.assertEqual(p["candidate_contract"]["nontrivial_splits_per_tree"], 18)
        self.assertFalse(p["candidate_contract"]["data_driven_candidate_filtering_allowed"])
        self.assertEqual(p["au_test"]["rell_replicates"], 10000)
        self.assertEqual(p["au_test"]["seed"], 20260822)
        self.assertEqual(p["au_test"]["model_family"], "TIM3+F+R3")
        self.assertEqual(p["au_test"]["au_rejection_alpha"], 0.05)
        self.assertFalse(p["promotion_boundary"]["rate_fit_execution_allowed"])

        flagged = {tuple(x["split"]) for x in r["uncertainty_flag"]["flagged_splits"]}
        declared = {tuple(x["split"]) for x in p["challenged_edges"]}
        self.assertEqual(flagged, declared)
        self.assertEqual(len(declared), 2)

        with tempfile.TemporaryDirectory() as td:
            outdir = pathlib.Path(td) / "candidates"
            subprocess.run(
                [
                    sys.executable,
                    str(BUILDER),
                    "--tree",
                    str(TREE),
                    "--concordance-result",
                    str(RESULT),
                    "--preflight",
                    str(PREFLIGHT),
                    "--outdir",
                    str(outdir),
                ],
                check=True,
            )
            manifest = json.loads((outdir / "candidate_manifest.json").read_text())
            trees = [x for x in (outdir / "candidate_trees.nwk").read_text().splitlines() if x.strip()]

        self.assertEqual(manifest["candidate_count"], 9)
        self.assertEqual(manifest["tip_count"], 21)
        self.assertEqual(manifest["nontrivial_splits_per_tree"], 18)
        self.assertEqual(len(trees), 9)
        self.assertEqual(
            manifest["primary_split_fingerprint_sha256"],
            p["candidate_contract"]["expected_primary_split_fingerprint_sha256"],
        )
        self.assertEqual(
            manifest["candidate_set_sha256"],
            p["candidate_contract"]["expected_candidate_set_sha256"],
        )
        self.assertEqual(len({x["split_fingerprint_sha256"] for x in manifest["candidates"]}), 9)
        self.assertFalse(manifest["data_driven_candidate_filtering_applied"])
        self.assertFalse(manifest["rate_fit_execution_allowed"])

        changed = [len(x["removed_primary_splits"]) for x in manifest["candidates"]]
        self.assertEqual(changed.count(0), 1)
        self.assertEqual(changed.count(1), 4)
        self.assertEqual(changed.count(2), 4)
        for row in manifest["candidates"]:
            self.assertEqual(len(row["removed_primary_splits"]), len(row["added_splits"]))

        by_states = {tuple(row["states"].values()): row for row in manifest["candidates"]}
        self.assertEqual(
            by_states[("swap_first", "primary")]["added_splits"],
            [["Cirsium_nipponicum_var_incomptum", "Cirsium_suffultum"]],
        )
        self.assertEqual(
            by_states[("swap_second", "primary")]["added_splits"],
            [["Cirsium_kujuense", "Cirsium_suffultum"]],
        )
        self.assertEqual(
            by_states[("primary", "swap_first")]["added_splits"],
            [["Cirsium_alpicola", "Cirsium_gyojanum", "Cirsium_nippoense", "Cirsium_yezoense"]],
        )
        self.assertEqual(
            by_states[("primary", "swap_second")]["added_splits"],
            [["Cirsium_alpicola", "Cirsium_gyojanum", "Cirsium_maritimum", "Cirsium_yezoense"]],
        )


if __name__ == "__main__":
    unittest.main()
