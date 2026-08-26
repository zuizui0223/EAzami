import importlib.util
from pathlib import Path

import pandas as pd
import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis" / "augment_fdt4_occurrences_with_published_vouchers_v1.py"
spec = importlib.util.spec_from_file_location("augment_fdt4_vouchers", SCRIPT)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


def config():
    return {
        "gbif": {
            "max_coordinate_uncertainty_m_primary": 10000,
            "spatial_thin_degrees": 0.05,
            "japan_bounds": {"lat_min": 21.5, "lat_max": 25.6, "lon_min": 119.0, "lon_max": 122.5},
        },
        "chelsa": {"predictors": {"bio01": "x", "bio04": "x", "bio12": "x", "bio15": "x"}},
    }


def existing():
    rows = []
    for taxon, latitude, longitude, key in [
        ("Cirsium morii", 24.51, 121.43, "g1"),
        ("Cirsium tatakaense", 23.47, 120.91, "g2"),
    ]:
        rows.append({
            "scientific_name_query": taxon,
            "gbif_key": key,
            "latitude": latitude,
            "longitude": longitude,
            "thin_lat": int(latitude // 0.05),
            "thin_lon": int(longitude // 0.05),
            "chelsa_bio01": 1.0,
            "chelsa_bio04": 2.0,
            "chelsa_bio12": 3.0,
            "chelsa_bio15": 4.0,
            "environment_complete": True,
        })
    return pd.DataFrame(rows)


def seed():
    common = {
        "source_class": "published_voucher",
        "source_doi": "10.example/test",
        "source_url": "https://example.test/source",
        "source_locator": "Table 2",
        "source_artifact_path": "",
        "source_artifact_sha256": "",
        "coordinate_crs": "WGS84",
        "coordinate_precision_arcminutes": 1,
        "coordinate_uncertainty_m": 2000,
        "coordinate_uncertainty_basis": "nearest_arcminute_conservative_2km",
        "basis_of_record": "PRESERVED_SPECIMEN",
        "evidence_scope": "exact_taxon_voucher_locality_coordinate",
        "chelsa_bio01": 1.1,
        "chelsa_bio04": 2.1,
        "chelsa_bio12": 3.1,
        "chelsa_bio15": 4.1,
    }
    return pd.DataFrame([
        {**common, "record_id": "m_new", "taxon": "Cirsium morii", "voucher": "m1", "locality": "new", "latitude": 24.48, "longitude": 121.43},
        {**common, "record_id": "t_dup", "taxon": "Cirsium tatakaense", "voucher": "t1", "locality": "dup", "latitude": 23.47, "longitude": 120.91},
        {**common, "record_id": "t_new", "taxon": "Cirsium tatakaense", "voucher": "t2", "locality": "new", "latitude": 23.70, "longitude": 120.95},
    ])


def unused_sampler(frame, predictors):
    raise AssertionError("seeded CHELSA values should avoid a network call")


def test_all_vouchers_are_screened_and_existing_cells_win():
    combined, summary = mod.augment_occurrences(existing(), seed(), config(), sampler=unused_sampler)
    assert len(combined) == 4
    assert not combined.duplicated(["scientific_name_query", "thin_lat", "thin_lon"]).any()
    assert set(combined["gbif_key"].astype(str)) == {"g1", "g2", "m_new", "t_new"}
    by_taxon = {row["taxon"]: row for row in summary["taxa"]}
    assert by_taxon["Cirsium morii"]["published_voucher_cells_added"] == 1
    assert by_taxon["Cirsium tatakaense"]["published_vouchers_in_existing_cells"] == 1
    assert by_taxon["Cirsium tatakaense"]["published_voucher_cells_added"] == 1


def test_seed_fails_closed_on_unverified_crs():
    bad = seed()
    bad.loc[0, "coordinate_crs"] = "unknown"
    with pytest.raises(ValueError, match="WGS84"):
        mod.validate_voucher_seed(bad, config())


def test_seed_fails_closed_above_frozen_uncertainty_limit():
    bad = seed()
    bad.loc[0, "coordinate_uncertainty_m"] = 10001
    with pytest.raises(ValueError, match="frozen primary limit"):
        mod.validate_voucher_seed(bad, config())
