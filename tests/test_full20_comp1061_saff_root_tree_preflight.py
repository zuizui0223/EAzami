import hashlib
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PREFLIGHT = ROOT / "data" / "evidence" / "full20_comp1061_saff_root_tree_preflight_v1.json"
SOURCE = ROOT / "data" / "evidence" / "full20_comp1061_current_conservative_206_loci_v1.txt"
TREE_LOCI = ROOT / "data" / "evidence" / "full20_comp1061_saff_root_153_loci_v1.txt"


class Full20Comp1061SaffRootTreePreflightTest(unittest.TestCase):
    def test_frozen_pre_topology_locus_contract(self):
        x = json.loads(PREFLIGHT.read_text())
        source = [v.strip() for v in SOURCE.read_text().splitlines() if v.strip()]
        tree = [v.strip() for v in TREE_LOCI.read_text().splitlines() if v.strip()]

        self.assertEqual(x["contract_version"], "full20_comp1061_saff_root_tree_preflight_v1")
        self.assertEqual(len(source), 206)
        self.assertEqual(len(tree), 153)
        self.assertEqual(len(set(tree)), 153)
        self.assertLessEqual(set(tree), set(source))
        self.assertEqual(hashlib.sha256(TREE_LOCI.read_bytes()).hexdigest(), x["frozen_tree_locus_list"]["sha256"])
        self.assertEqual(x["reference_contract"]["close_root_reference"], "OUTGROUP_saff")
        self.assertEqual(x["reference_contract"]["required_reference_tips"], ["OUTGROUP_saff", "OUTGROUP_lett", "OUTGROUP_sunf"])
        self.assertEqual(x["pre_topology_locus_selection"]["final_tree_locus_count"], 153)
        self.assertEqual(x["pre_topology_locus_selection"]["excluded_for_missing_saff"], 53)
        self.assertFalse(x["pre_topology_locus_selection"]["post_topology_locus_selection_allowed"])
        self.assertFalse(x["alignment_policy"]["posthoc_signal_filtering_allowed"])
        self.assertTrue(x["tree_policy"]["topology_sensitivity_required_before_rate_fit"])
        self.assertFalse(x["tree_policy"]["rate_fit_execution_allowed"])


if __name__ == "__main__":
    unittest.main()
