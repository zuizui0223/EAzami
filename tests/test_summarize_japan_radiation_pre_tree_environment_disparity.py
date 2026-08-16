import unittest

import pandas as pd

from analysis.summarize_japan_radiation_pre_tree_environment_disparity import ENV, build


class TestPreTreeEnvironmentDisparity(unittest.TestCase):
    def test_summary_boundaries(self):
        taxa=["A","B","C","Cirsium lineare"]
        rows=[]
        for i,t in enumerate(taxa):
            row={"taxon_name":t,"japan_origin_role":"lineare_replicated_exception" if t=="Cirsium lineare" else "dominant_main_japanese_radiation","n_azami_balanced_observations":3+i}
            for j,c in enumerate(ENV): row[c]=float((i+1)*(j+2)+(j%2))
            rows.append(row)
        s=build(pd.DataFrame(rows))
        self.assertEqual(s["n_taxa"],4)
        self.assertEqual(s["n_dominant_radiation_taxa"],3)
        self.assertEqual(s["secondary_history_comparator"],"Cirsium lineare")
        self.assertIn("not complete niche distributions",s["claim_boundary"])

if __name__=="__main__": unittest.main()
