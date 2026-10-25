"""Ensure all nine original published trait characters map to a real nuclear tree."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"analysis"))
from render_siniscalchi_2023_nine_traits_v1 import TRAITS, render


class PublishedNineTraitTreeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=Path(".tmp/north-america-nine-source")
        cls.out=Path(".tmp/north-america-nine-figure")
        cls.result=render(cls.source,cls.out)

    def test_original_all_nine_source_traits_present(self):
        self.assertEqual(self.result["n_original_morphological_characters"],9)
        self.assertEqual(self.result["n_source_nuclear_tips"],63)
        self.assertEqual(len(self.result["characters"]),9)
        self.assertEqual(set(TRAITS),{
            "CorollaThroat","CorollaColor","Duration","GlutinousRidge",
            "Habit","HeadPosition","InnerPhyllaryColor",
            "OuterPhyllaryPosition","StyleBranchColor",
        })

    def test_fixed_source_derived_minimum_steps(self):
        rows={x["character"]:x for x in self.result["characters"]}
        want={
            "CorollaThroat":4, "CorollaColor":12, "Duration":14,
            "GlutinousRidge":11, "Habit":3, "HeadPosition":4,
            "InnerPhyllaryColor":12, "OuterPhyllaryPosition":14,
            "StyleBranchColor":10,
        }
        self.assertEqual({k:v["minimum_fitch_changes"] for k,v in rows.items()},want)
        self.assertEqual(rows["HeadPosition"]["state_counts"],{"0":58,"1":5})
        self.assertEqual(rows["CorollaColor"]["state_counts"],{"0":5,"1":7,"2":50,"3":1})

    def test_figure_and_source_ontology_exported(self):
        for name in ("north_america_nuclear_ALL_NINE_traits.png",
                     "north_america_nuclear_ALL_NINE_traits.svg",
                     "nine_trait_phylogeny_parsimony_report.json",
                     "nine_trait_original_legend_and_parsimony.md"):
            self.assertGreater((self.out/name).stat().st_size,100)
        self.assertFalse(self.result["inferred_world_nuclear_tree"])
        self.assertIn("white, pink and purple together",(self.out/"nine_trait_original_legend_and_parsimony.md").read_text())


if __name__=="__main__":
    unittest.main()
