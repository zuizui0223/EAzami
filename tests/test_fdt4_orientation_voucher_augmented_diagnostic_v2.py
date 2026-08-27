import hashlib
import json
import math
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data" / "evidence" / "fdt4_orientation_voucher_augmented_diagnostic_v2.json"
TABLE = ROOT / "data" / "evidence" / "fdt4_orientation_voucher_augmented_branchwise_by_topology_v2.csv"
SEED = ROOT / "data" / "evidence" / "fdt4_taiwan_published_voucher_occurrence_seed_v1.csv"


def test_voucher_gate_closes_without_lowering_threshold():
    result = json.loads(CONTRACT.read_text(encoding="utf-8"))
    augmentation = result["voucher_augmentation"]
    assert augmentation["published_vouchers_screened"] == 7
    assert augmentation["Cirsium_morii"]["vouchers_in_existing_cells"] == 2
    assert augmentation["Cirsium_morii"]["cells_after"] == 10
    assert augmentation["Cirsium_tatakaense"]["cells_after"] == 11
    assert augmentation["gate_decision"] == "closed_without_lowering_the_frozen_threshold"


def test_present_day_association_passes_but_branchwise_concordance_does_not():
    result = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert result["pgls_11_taxa_across_six_topologies"]["chelsa_bio15"]["all_six_topologies_p_lt_0_05"] is True
    assert result["pgls_11_taxa_across_six_topologies"]["chelsa_bio01"]["all_six_topologies_p_lt_0_05"] is True
    branchwise = result["branchwise_11_taxa_across_six_topologies"]
    assert branchwise["chelsa_bio15"]["all_six_topologies_p_lt_0_05"] is False
    assert branchwise["chelsa_bio01"]["all_six_topologies_p_lt_0_05"] is False
    assert branchwise["chelsa_bio01"]["topology_range_crosses_0_05"] is True
    assert branchwise["robust_repeated_transition_niche_concordance_supported"] is False


def test_frozen_table_and_seed_are_complete_and_unique():
    table = pd.read_csv(TABLE)
    assert len(table) == 12
    assert set(table["topology_index"]) == set(range(1, 7))
    assert set(table["axis"]) == {"chelsa_bio15", "chelsa_bio01"}
    assert not table.duplicated(["topology_index", "axis"]).any()
    seed = pd.read_csv(SEED)
    assert len(seed) == 7
    assert not seed["record_id"].duplicated().any()
    assert not seed[["taxon", "voucher"]].duplicated().any()
    assert set(seed["coordinate_crs"]) == {"WGS84"}
    assert set(seed.loc[seed["taxon"] == "Cirsium morii", "voucher"]) == {
        "ccy779",
        "ccy3360",
        "ccy4365",
    }
    assert set(seed.loc[seed["taxon"] == "Cirsium tatakaense", "voucher"]) == {
        "ccy3338",
        "ccy3456",
        "ccy3458",
        "ccy4022",
    }


def test_frozen_table_ranges_and_seed_hash_match_contract():
    result = json.loads(CONTRACT.read_text(encoding="utf-8"))
    table = pd.read_csv(TABLE)
    branchwise = result["branchwise_11_taxa_across_six_topologies"]
    assert set(table["n_taxa"]) == {11}
    assert set(table["n_U"]) == {6}
    assert set(table["n_D"]) == {5}
    assert list(table["expected_orientation_transitions"].agg(["min", "max"])) == branchwise[
        "expected_orientation_transitions_range"
    ]
    for axis in ("chelsa_bio15", "chelsa_bio01"):
        rows = table.loc[table["axis"] == axis]
        expected = branchwise[axis]
        for observed, frozen in zip(
            rows["directional_shift_sd"].agg(["min", "max"]),
            expected["directional_shift_sd_range"],
        ):
            assert math.isclose(observed, frozen, rel_tol=0.0, abs_tol=1e-15)
        assert list(rows["two_sided_permutation_p"].agg(["min", "max"])) == expected[
            "two_sided_permutation_p_range"
        ]
    seed_sha256 = hashlib.sha256(SEED.read_bytes()).hexdigest()
    assert seed_sha256 == result["source_lineage"]["published_voucher_seed_sha256"]
