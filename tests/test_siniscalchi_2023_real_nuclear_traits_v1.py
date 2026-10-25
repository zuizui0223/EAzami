"""Real published North American nuclear source/traits join tests."""
from __future__ import annotations

import csv
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"analysis"))

from run_siniscalchi_2023_real_nuclear_traits_v1 import (
    acquire, build, git_blob_sha1, ASSETS, HEAD, COLOUR
)  # noqa: E402


class PublishedNorthAmericaTreeTraits(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.assets=Path(".tmp/siniscalchi-source-2023")
        cls.outdir=Path(".tmp/north-america-source-tests")
        cls.manifest=build(cls.assets,cls.outdir,skip_figure=True)

    def test_author_tree_63_tips_matches_all_original_traits(self):
        m=self.manifest
        self.assertEqual(m["total_published_tree_tips"],63)
        self.assertEqual(m["ingroup_taxa_for_model"],62)
        self.assertEqual(m["original_author_trait_counts"]["HeadPosition"],{"0":58,"1":5})
        self.assertEqual(m["original_author_trait_counts"]["CorollaColor"],{"0":5,"1":7,"2":50,"3":1})
        self.assertEqual(m["Fitch_minimum_changes"],{"HeadPosition":4,"CorollaColor":12})

    def test_onto_morphology_comes_from_original_R_codebook(self):
        self.assertEqual(HEAD,{"0":"U","1":"D"})
        self.assertEqual(COLOUR["2"],"white/pink/purple COMBINED")
        self.assertEqual(self.manifest["published_tree_outgroup"],"Cirsium_vulgare")

    def test_all_pinned_author_blobs_have_exact_git_sha1(self):
        files=acquire(self.assets)
        for p,h in ASSETS.items():
            self.assertEqual(git_blob_sha1(files[p].read_bytes()),h)

    def test_full_and_mixed_head_sensitivity_never_reassign_states(self):
        full=list(csv.DictReader((self.outdir/"na_full_author_trait_climate_join.csv").open()))
        limited=list(csv.DictReader((self.outdir/"na_mixed_head_sensitivity_trait_climate_join.csv").open()))
        self.assertEqual(len(full),len(limited))
        self.assertEqual(len(full),62)
        a={r["tip_id"]:r for r in full}
        b={r["tip_id"]:r for r in limited}
        self.assertEqual(a["Cirsium_vinaceum"]["orientation_state"],"D")
        self.assertEqual(a["Cirsium_eatonii"]["orientation_state"],"U")
        for n in ("Cirsium_eatonii","Cirsium_joannae"):
            self.assertEqual(b[n]["orientation_state"],"unresolved")
            self.assertTrue(b[n]["exclusion_reason"])
        self.assertTrue(all(r["orientation_state"]=="U" for r in full if r["tip_id"] in ("Cirsium_ownbeyi","Cirsium_longistylum","Cirsium_flodmanii")))
        self.assertTrue(all(r["orientation_state"]==b[r["tip_id"]]["orientation_state"] for r in full if r["tip_id"] not in ("Cirsium_eatonii","Cirsium_joannae")))

    def test_source_climate_is_not_falsely_labeled_paleoclimate(self):
        m=self.manifest
        self.assertFalse(m["same_sequenced_voucher_phenotyped"])
        self.assertFalse(m["chronogram_is_world_phylogeny"])
        self.assertIn("not EAzami GBIF/CHELSA",m["environmental_data"])
        self.assertTrue(all(c["resolved_D"]==5 for c in m["model_sensitivity_panels"]))


if __name__=="__main__":
    unittest.main()
