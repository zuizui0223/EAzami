from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / "analysis/validate_colour_atlas_branch_length_tree.py"
spec = importlib.util.spec_from_file_location("tree_gate", MOD)
assert spec and spec.loader
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


class TreeGateTests(unittest.TestCase):
    def write_fixture(self, td: str, *, missing_length: bool = False, bad_hash: bool = False):
        root = Path(td)
        tree = root / "tree.nwk"
        tree.write_text("((t1:0.1,t2:0.2)95:0.3,t3:0.4);\n" if not missing_length else "((t1:0.1,t2)95:0.3,t3:0.4);\n")
        atlas = root / "atlas.csv"
        fields = ["accepted_taxon","observation_unit","rate_fit_eligible","binary_colour_code"]
        with atlas.open("w", newline="") as f:
            w=csv.DictWriter(f,fieldnames=fields); w.writeheader();
            w.writerows([
                {"accepted_taxon":"A","observation_unit":"taxon","rate_fit_eligible":"yes","binary_colour_code":"W"},
                {"accepted_taxon":"B","observation_unit":"taxon","rate_fit_eligible":"yes","binary_colour_code":"C"},
                {"accepted_taxon":"C","observation_unit":"taxon","rate_fit_eligible":"yes","binary_colour_code":"C"},
            ])
        tipmap = root / "map.csv"
        with tipmap.open("w", newline="") as f:
            w=csv.DictWriter(f,fieldnames=["tree_tip","accepted_taxon","mapping_status"]); w.writeheader();
            w.writerows([
                {"tree_tip":"t1","accepted_taxon":"A","mapping_status":"exact"},
                {"tree_tip":"t2","accepted_taxon":"B","mapping_status":"reviewed_synonym"},
                {"tree_tip":"t3","accepted_taxon":"C","mapping_status":"exact"},
            ])
        sha=hashlib.sha256(tree.read_bytes()).hexdigest()
        prov=root/"prov.json"
        prov.write_text(json.dumps({
            "tree_route":"compatibility_reanalysis",
            "tree_sha256":"0"*64 if bad_hash else sha,
            "analysis_name":"synthetic compatibility tree",
            "branch_length_interpretation":"substitutions per site",
            "rooting_definition":"rooted on t3 for synthetic test",
            "support_metric_definition":"IQ-TREE ultrafast bootstrap labels on internal nodes",
            "source_or_pipeline_provenance":"synthetic unit-test fixture",
            "topology_uncertainty_status":"bootstrap_or_gene_tree_sensitivity"
        }))
        return tree,atlas,tipmap,prov

    def test_accepts_complete_branch_tree(self):
        with tempfile.TemporaryDirectory() as td:
            result=m.validate(*self.write_fixture(td))
            self.assertTrue(result["tree_gate_ready"])
            self.assertEqual(result["eligible_state_counts"], {"C":2,"W":1})
            self.assertEqual(result["tree_tip_count"],3)

    def test_rejects_missing_branch_length(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,"without branch lengths"):
                m.validate(*self.write_fixture(td, missing_length=True))

    def test_rejects_provenance_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,"tree_sha256"):
                m.validate(*self.write_fixture(td, bad_hash=True))

    def test_rejects_missing_eligible_tip_mapping(self):
        with tempfile.TemporaryDirectory() as td:
            tree,atlas,tipmap,prov=self.write_fixture(td)
            rows=list(csv.DictReader(tipmap.open()))[:-1]
            with tipmap.open("w",newline="") as f:
                w=csv.DictWriter(f,fieldnames=["tree_tip","accepted_taxon","mapping_status"]);w.writeheader();w.writerows(rows)
            with self.assertRaisesRegex(ValueError,"missing from tip map"):
                m.validate(tree,atlas,tipmap,prov)

    def test_internal_support_is_not_counted_as_tip(self):
        tips,lengths,missing=m.NewickParser("((A:1,B:1)99:2,C:3);").parse()
        self.assertEqual(tips,["A","B","C"])
        self.assertEqual(missing,0)
        self.assertEqual(len(lengths),4)

if __name__ == "__main__":
    unittest.main()
