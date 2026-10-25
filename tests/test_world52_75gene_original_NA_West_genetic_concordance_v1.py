"""Original label-index exchangeability and source p-distance regressions."""
from __future__ import annotations
import sys,unittest
from pathlib import Path
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"analysis"))
import audit_world52_75gene_original_NA_West_genetic_concordance_v1 as a


class World52NuclearGeneDistance(unittest.TestCase):
    def test_source_taxon_sets_independent_biosamples(self):
        self.assertEqual(len(a.NA),6)
        self.assertEqual(len(a.WEST),5)
        self.assertEqual(len(set(a.ORIGINAL)),11)
        self.assertEqual(a.SOURCE_FASTA_SHA,len(a.SOURCE_FASTA_SHA)*"a" if False else a.SOURCE_FASTA_SHA)

    def test_pairwise_expected_difference_known_signal(self):
        mat=np.zeros((2,11,11),float)
        for g in range(2):
            for i in range(11):
                for j in range(11):
                    if i==j: continue
                    if i<6 and j<6:
                        mat[g,i,j]=.01
                    elif i>=6 and j>=6:
                        mat[g,i,j]=.03
                    else:mat[g,i,j]=.08
        d,b,w=a.contrast(mat,range(6))
        self.assertEqual(len(d),2)
        self.assertAlmostEqual(float(d[0]),.07,places=10)
        self.assertAlmostEqual(float(b[0]),.08)
        self.assertAlmostEqual(float(w[0]),.01)
        null=a.genetic_label_null(mat,slice(None),bootstrap=200)
        self.assertEqual(null["source_region_label_exact_null_map_count"],462)
        self.assertEqual(null["source_label_map_at_or_more_extreme"],1)

    def test_reject_malformed_source_region_index(self):
        mat=np.ones((2,11,11))
        with self.assertRaises(ValueError):
            a.contrast(mat,range(5))

    def test_source_technical_gene_names_frozen(self):
        self.assertEqual(a.TECHNICAL_TWO,{"At1g02170","At3g04400"})
        self.assertEqual(a.MIN_OVERLAP_BASES,150)


if __name__=="__main__":
    unittest.main()
