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
    def write_fixture(self, td: str, *, missing_length: bool = False, bad_hash: bool = False, tree_text: str | None = None, required_outgroups: list[str] | None = None, required_references: list[str] | None = None):
        root = Path(td)
        tree = root / "tree.nwk"
        default = "((t1:0.1,t2:0.2)95:0.3,t3:0.4);\n" if not missing_length else "((t1:0.1,t2)95:0.3,t3:0.4);\n"
        tree.write_text(tree_text or default)
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
        payload={
            "tree_route":"compatibility_reanalysis",
            "tree_sha256":"0"*64 if bad_hash else sha,
            "analysis_name":"synthetic compatibility tree",
            "branch_length_interpretation":"substitutions per site",
            "rooting_definition":"synthetic explicit rooting",
            "support_metric_definition":"IQ-TREE ultrafast bootstrap labels on internal nodes",
            "source_or_pipeline_provenance":"synthetic unit-test fixture",
            "topology_uncertainty_status":"bootstrap_or_gene_tree_sensitivity"
        }
        if required_outgroups is not None: payload["required_outgroup_tips"] = required_outgroups
        if required_references is not None: payload["required_reference_tips"] = required_references
        prov.write_text(json.dumps(payload))
        return tree,atlas,tipmap,prov

    def test_accepts_complete_branch_tree(self):
        with tempfile.TemporaryDirectory() as td:
            result=m.validate(*self.write_fixture(td))
            self.assertTrue(result["tree_gate_ready"])
            self.assertEqual(result["eligible_state_counts"], {"C":2,"W":1})
            self.assertEqual(result["tree_tip_count"],3)
            self.assertFalse(result["focal_monophyly_checked"])

    def test_accepts_root_outgroups_and_additional_near_reference(self):
        with tempfile.TemporaryDirectory() as td:
            tree="((t1:0.1,t2:0.2,t3:0.3):0.4,NEAR:0.45,OUT1:0.5,OUT2:0.6);\n"
            result=m.validate(*self.write_fixture(td,tree_text=tree,required_outgroups=["OUT1","OUT2"],required_references=["OUT1","OUT2","NEAR"]))
            self.assertTrue(result["focal_monophyly_checked"])
            self.assertTrue(result["focal_monophyly_passed"])
            self.assertEqual(result["focal_monophyly_definition"],"orientation-invariant edge split")
            self.assertEqual(result["required_outgroup_tips"],["OUT1","OUT2"])
            self.assertEqual(result["required_reference_tips"],["NEAR","OUT1","OUT2"])

    def test_accepts_focal_complement_of_root_adjacent_outgroup_edge(self):
        with tempfile.TemporaryDirectory() as td:
            # The root has three children. The focal {t1,t2,t3} set is not a
            # descendant clade in this Newick orientation, but it is exactly
            # the complement of the OUT1 pendant-edge split and is monophyletic.
            tree="((t1:0.1,t2:0.2):0.3,t3:0.4,OUT1:0.5);\n"
            result=m.validate(*self.write_fixture(td,tree_text=tree,required_outgroups=["OUT1"],required_references=["OUT1"]))
            self.assertTrue(result["tree_gate_ready"])
            self.assertTrue(result["focal_monophyly_passed"])
            parser=m.NewickParser(tree); tips,_,_=parser.parse()
            self.assertNotIn(frozenset({"t1","t2","t3"}),parser.clades)
            self.assertIn(frozenset({"t1","t2","t3"}),m.edge_split_sides(parser,set(tips)))

    def test_rejects_outgroup_not_declared_as_reference(self):
        with tempfile.TemporaryDirectory() as td:
            tree="((t1:0.1,t2:0.2,t3:0.3):0.4,OUT1:0.5,OUT2:0.6);\n"
            with self.assertRaisesRegex(ValueError,"subset"):
                m.validate(*self.write_fixture(td,tree_text=tree,required_outgroups=["OUT1","OUT2"],required_references=["OUT1"]))

    def test_rejects_reference_intrusion_into_focal_clade(self):
        with tempfile.TemporaryDirectory() as td:
            tree="((t1:0.1,NEAR:0.2):0.3,(t2:0.1,t3:0.1):0.2,OUT1:0.5,OUT2:0.6);\n"
            with self.assertRaisesRegex(ValueError,"monophyletic edge split"):
                m.validate(*self.write_fixture(td,tree_text=tree,required_outgroups=["OUT1","OUT2"],required_references=["OUT1","OUT2","NEAR"]))

    def test_rejects_undeclared_extra_tree_tip(self):
        with tempfile.TemporaryDirectory() as td:
            tree="((t1:0.1,t2:0.2,t3:0.3):0.4,OUT1:0.5,OUT2:0.6,EXTRA:0.7);\n"
            with self.assertRaisesRegex(ValueError,"undeclared extra tips"):
                m.validate(*self.write_fixture(td,tree_text=tree,required_outgroups=["OUT1","OUT2"]))

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
        parser=m.NewickParser("((A:1,B:1)99:2,C:3);")
        tips,lengths,missing=parser.parse()
        self.assertEqual(tips,["A","B","C"])
        self.assertEqual(missing,0)
        self.assertEqual(len(lengths),4)
        self.assertIn(frozenset({"A","B"}),parser.clades)

if __name__ == "__main__":
    unittest.main()
