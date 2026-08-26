import hashlib
import json
import unittest
from pathlib import Path

from Bio import Phylo

ROOT = Path(__file__).resolve().parents[1]
TREE = ROOT / "data/evidence/japan38_comp1061_primary_tree_v1.nwk"
ACC = ROOT / "data/evidence/japan38_comp1061_primary_tree_acceptance_v1.json"
HIST = ROOT / "data/evidence/japan38_multitrait_history_summary_v1.json"
COLOUR = ROOT / "data/evidence/japan38_colour_continuous_history_summary_v1.json"


class TestJapan38CanonicalEvidenceV1(unittest.TestCase):
    def test_tree_acceptance_contract(self):
        acceptance = json.loads(ACC.read_text(encoding="utf-8"))
        digest = hashlib.sha256(TREE.read_bytes()).hexdigest()
        self.assertEqual(digest, acceptance["tree_sha256"])
        self.assertEqual(acceptance["software"], "IQ-TREE 2.4.0")
        self.assertEqual(acceptance["seed"], 20260825)
        self.assertEqual(acceptance["model_finder_best_bic_model"], "TIM3+F+I+R4")
        self.assertEqual(acceptance["focal_biological_samples"], 39)
        self.assertEqual(acceptance["tree_tip_count"], 40)
        self.assertEqual(acceptance["qc_locus_universe"], 241)
        self.assertEqual(acceptance["current_qc_loci"], 236)
        self.assertEqual(acceptance["rootable_loci"], 176)
        self.assertEqual(acceptance["alignment_length_bp"], 161654)
        self.assertFalse(acceptance["jpn20_monophyletic_ml"])
        self.assertEqual(acceptance["jpn20_monophyly_fraction_ufboot"], 0.0)

        tree = Phylo.read(str(TREE), "newick")
        names = {tip.name for tip in tree.get_terminals()}
        self.assertEqual(len(names), 40)
        self.assertIn("OUTGROUP_saff", names)
        self.assertEqual(len([x for x in names if x.startswith("J38S")]), 39)

    def test_multitrait_history_contract(self):
        x = json.loads(HIST.read_text(encoding="utf-8"))
        self.assertEqual(x["trait_history_concepts"], 36)
        h = x["minimum_change_history"]
        self.assertEqual((h["orientation"]["resolved_concepts"], h["orientation"]["ml_minimum_unordered_steps"]), (19, 6))
        self.assertEqual((h["phyllary_posture"]["resolved_concepts"], h["phyllary_posture"]["ml_minimum_unordered_steps"]), (10, 3))
        self.assertEqual((h["stickiness"]["resolved_concepts"], h["stickiness"]["ml_minimum_unordered_steps"]), (12, 5))
        self.assertEqual(h["orientation"]["ufboot_root_U_fraction"], 1.0)
        self.assertAlmostEqual(x["transition_identifiability"]["phyllary_posture"]["JPN_36_ufboot_forced_fraction"], 0.754)
        self.assertAlmostEqual(x["transition_identifiability"]["stickiness"]["JPN_06_ufboot_forced_fraction"], 0.67)
        self.assertIn("not supported", x["common_lability_diagnostic"]["decision"])

    def test_continuous_colour_contract(self):
        x = json.loads(COLOUR.read_text(encoding="utf-8"))
        self.assertEqual(x["exact_concepts_with_continuous_colour"], 14)
        for subset in x["pagel_lambda_mle"].values():
            self.assertTrue(all(value == 0.0 for value in subset.values()))
        hi = x["lightness_phylogenetic_overdispersion"]["minimum_observations_10"]
        self.assertEqual(hi["taxa"], 5)
        self.assertAlmostEqual(hi["rho"], -0.8545)
        self.assertAlmostEqual(hi["exact_two_sided_p"], 0.00833)


if __name__ == "__main__":
    unittest.main()
