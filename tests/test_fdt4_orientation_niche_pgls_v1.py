from __future__ import annotations

from io import StringIO

import numpy as np
from Bio import Phylo

from analysis.run_fdt4_orientation_niche_pgls_v1 import (
    brownian_covariance,
    fit_pgls,
    normalize_tip,
)


def test_normalize_tip_matches_comp1061_ids():
    assert normalize_tip("Cirsium japonicum var. japonicum") == "Cirsium_japonicum_var_japonicum"
    assert normalize_tip("Cirsium brevicaule") == "Cirsium_brevicaule"


def test_brownian_covariance_is_symmetric_positive_diagonal():
    tree = Phylo.read(
        StringIO("(OUTGROUP_saff:1,((A:1,B:1):1,(C:1,D:1):1):1);"),
        "newick",
    )
    tree.root_with_outgroup({"name": "OUTGROUP_saff"})
    cov = brownian_covariance(tree, ["A", "B", "C", "D"])
    assert cov.shape == (4, 4)
    assert np.allclose(cov, cov.T)
    assert np.all(np.diag(cov) > 0)
    assert cov[0, 1] > cov[0, 2]


def test_pgls_recovers_positive_downward_effect_direction():
    tree = Phylo.read(
        StringIO("(OUTGROUP_saff:1,((A:1,B:1):1,(C:1,D:1):1):1);"),
        "newick",
    )
    tree.root_with_outgroup({"name": "OUTGROUP_saff"})
    cov = brownian_covariance(tree, ["A", "B", "C", "D"])
    # A/B = U(0), C/D = D(1); D has higher environmental values.
    state = np.array([0.0, 0.0, 1.0, 1.0])
    y = np.array([-1.1, -0.9, 0.9, 1.1])
    result = fit_pgls(y, state, cov)
    assert result["beta_D_minus_U_sd"] > 0
    assert result["dof"] == 2
