from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "analysis"
if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))

import summarize_public_candidate_empirical_quartet as mod  # noqa: E402


class EmpiricalQuartetTests(unittest.TestCase):
    def test_three_resolved_topologies_and_star(self):
        self.assertEqual(
            mod.classify_newick("((MRY_YOSHINOI,PUBEA001),(MRY_SAIRAMENSE,PUBEA002));"),
            "same_taxon_pairs",
        )
        self.assertEqual(
            mod.classify_newick("((MRY_YOSHINOI,MRY_SAIRAMENSE),(PUBEA001,PUBEA002));"),
            "baseline_vs_candidates",
        )
        self.assertEqual(
            mod.classify_newick("((MRY_YOSHINOI,PUBEA002),(MRY_SAIRAMENSE,PUBEA001));"),
            "crossed_pairs",
        )
        self.assertEqual(
            mod.classify_newick("(MRY_YOSHINOI,PUBEA001,MRY_SAIRAMENSE,PUBEA002);"),
            "unresolved",
        )

    def test_summary_counts_gene_tree_votes_on_informative_subset(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            common = root / "common.txt"
            common.write_text("L1\nL2\nL3\nL4\n")
            informative = root / "informative.txt"
            informative.write_text("L1\nL2\nL3\n")
            trees = root / "trees"
            trees.mkdir()
            (trees / "L1.treefile").write_text("((MRY_YOSHINOI,PUBEA001),(MRY_SAIRAMENSE,PUBEA002));")
            (trees / "L2.treefile").write_text("((MRY_YOSHINOI,PUBEA001),(MRY_SAIRAMENSE,PUBEA002));")
            (trees / "L3.treefile").write_text("((MRY_YOSHINOI,MRY_SAIRAMENSE),(PUBEA001,PUBEA002));")
            concat = root / "concat.treefile"
            concat.write_text("((MRY_YOSHINOI,PUBEA001),(MRY_SAIRAMENSE,PUBEA002));")
            out = root / "summary.json"
            summary = mod.summarize(common, trees, concat, out, informative)
            self.assertEqual(summary["four_way_common_strict_loci"], 4)
            self.assertEqual(summary["gene_tree_analysis_loci"], 3)
            self.assertEqual(summary["gene_tree_topology_counts"]["same_taxon_pairs"], 2)
            self.assertEqual(summary["gene_tree_topology_counts"]["baseline_vs_candidates"], 1)
            self.assertEqual(summary["same_taxon_pair_fraction_resolved"], 2 / 3)
            self.assertTrue(summary["concatenated_same_taxon_pairs"])
            self.assertEqual(summary["pilot_same_taxon_signal"], "consistent")
            self.assertFalse(summary["full_294_tip_promotion_allowed_from_this_pilot"])

    def test_gene_tree_loci_must_be_subset_of_common(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            common = root / "common.txt"
            common.write_text("L1\n")
            informative = root / "informative.txt"
            informative.write_text("L2\n")
            with self.assertRaisesRegex(ValueError, "not a subset"):
                mod.summarize(common, root, root / "x.treefile", root / "out.json", informative)


if __name__ == "__main__":
    unittest.main()
