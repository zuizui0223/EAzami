import unittest

import pandas as pd

from analysis.test_japan_radiation_pre_tree_module_environment_coupling import (
    ENV,
    MODULES,
    build,
)


class TestModuleEnvironmentCoupling(unittest.TestCase):
    def fixture(self):
        rows = []
        for i, taxon in enumerate(["A", "B", "C", "D", "E"]):
            row = {"taxon_name": taxon}
            for module_columns in MODULES.values():
                for j, column in enumerate(module_columns):
                    row[column] = float((i + 1) * (j + 2) + (i % 2))
            for j, column in enumerate(ENV):
                row[column] = float((5 - i) * (j + 1) + (j % 2))
            rows.append(row)
        return pd.DataFrame(rows)

    def test_deterministic_and_module_boundaries(self):
        a = build(self.fixture(), permutations=99, seed=17)
        b = build(self.fixture(), permutations=99, seed=17)
        self.assertEqual(a, b)
        self.assertEqual(set(a["modules"]), {"orientation", "colour", "shape"})
        self.assertEqual(a["modules"]["orientation"]["n_axes"], 1)
        self.assertEqual(a["modules"]["colour"]["n_axes"], 2)
        self.assertEqual(a["modules"]["shape"]["n_axes"], 4)
        self.assertIn("no evolutionary rate", a["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
