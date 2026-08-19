import unittest

import pandas as pd

from analysis.build_azami_eazami_trait_tip_crosswalk import build_crosswalk, normalize_name


class TestAzamiEAzamiTraitCrosswalk(unittest.TestCase):
    def test_normalize_abbreviation_and_infraspecific_name(self):
        self.assertEqual(normalize_name("C. brevicaule"), "Cirsium brevicaule")
        self.assertEqual(
            normalize_name("Cirsium japonicum var. takaoense (Masam.) Kitam."),
            "Cirsium japonicum var. takaoense",
        )

    def test_exact_matching_does_not_promote_broad_species_to_variety(self):
        handoff = pd.DataFrame([
            {"taxon_name": "Cirsium japonicum", "n_usable_heads_species": 2},
            {"taxon_name": "Cirsium brevicaule", "n_usable_heads_species": 3},
        ])
        moreyra = pd.DataFrame([
            {
                "tree_code": "Cirsium japonicum",
                "published_species": "Cirsium japonicum var. horridum Nakai",
                "sra_scientific_name": "Cirsium japonicum",
                "run": "SRR1",
                "biosample": "SAM1",
            }
        ])
        japan38 = pd.DataFrame([
            {
                "paper_japan_member_id": "JPN_01",
                "paper_taxon_concept": "Cirsium japonicum var. horridum Nakai",
            }
        ])
        chang = pd.DataFrame([
            {"taxon": "C. japonicum var. takaoense", "code": "TAK", "voucher": "v1"},
            {"taxon": "C. brevicaule", "code": "BRE", "voucher": "v2"},
        ])

        result, summary = build_crosswalk(handoff, moreyra, japan38, chang2026=chang)
        japonicum = result.loc[result["taxon_name"].eq("Cirsium japonicum")].iloc[0]
        brevicaule = result.loc[result["taxon_name"].eq("Cirsium brevicaule")].iloc[0]

        self.assertEqual(japonicum["nuclear_match_sources"], "Moreyra2025")
        self.assertEqual(japonicum["chang_codes"], "")
        self.assertEqual(japonicum["japan38_binomial_match"], "yes")
        self.assertEqual(brevicaule["nuclear_match_sources"], "Chang2025_2026")
        self.assertEqual(summary["n_exact_nuclear_matched_azami_taxa"], 2)
        self.assertEqual(summary["n_japan38_paper_concepts_represented_by_azami_traits"], 1)


if __name__ == "__main__":
    unittest.main()
