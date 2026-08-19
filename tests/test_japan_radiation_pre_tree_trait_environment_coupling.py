import unittest

import pandas as pd

from analysis.test_japan_radiation_pre_tree_trait_environment_coupling import ENV, TRAITS, build


class TestPreTreeTraitEnvironmentCoupling(unittest.TestCase):
    def fixture(self):
        rows=[]
        for i,taxon in enumerate(["A","B","C","D","E"]):
            row={"taxon_name":taxon}
            for j,c in enumerate(TRAITS): row[c]=float((i+1)*(j+1)+(i%2))
            for j,c in enumerate(ENV): row[c]=float((5-i)*(j+1)+(j%2))
            rows.append(row)
        return pd.DataFrame(rows)

    def test_deterministic_permutation_and_boundaries(self):
        a=build(self.fixture(),permutations=99,seed=7)
        b=build(self.fixture(),permutations=99,seed=7)
        self.assertEqual(a,b)
        self.assertEqual(a["n_taxa"],5)
        self.assertEqual(a["n_pairwise_distances"],10)
        self.assertTrue(a["circular_hue_components_excluded"])
        self.assertIn("not evidence against all ecological adaptation",a["claim_boundary"])


if __name__=="__main__": unittest.main()
