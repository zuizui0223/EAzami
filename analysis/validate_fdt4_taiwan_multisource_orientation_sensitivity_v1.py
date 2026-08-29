#!/usr/bin/env python3
"""Fail-closed validation for FDT4 Taiwan multi-source orientation sensitivity."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "data" / "evidence" / "fdt4_taiwan_multisource_orientation_sensitivity_v1.json"
PRIMARY = ROOT / "data" / "evidence" / "chapter2_ecological_explanatory_reach_v1.json"


def close(a: float, b: float, tol: float = 1e-12) -> None:
    if abs(float(a) - float(b)) > tol:
        raise AssertionError(f"numeric drift: {a} != {b}")


def main() -> int:
    x = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    p = json.loads(PRIMARY.read_text(encoding="utf-8"))

    if x["status"] != "SOURCE_SENSITIVE_SUPPORT_CLASS_PRIMARY_UNCHANGED":
        raise AssertionError("multi-source sensitivity status drift")
    if x["refresh_design"]["filters_relaxed"] is not False:
        raise AssertionError("filters were relaxed")
    if x["refresh_design"]["frozen_min_n"] != 10:
        raise AssertionError("frozen n>=10 gate drift")
    if x["refresh_design"]["spatial_thin_degrees"] != 0.05:
        raise AssertionError("spatial thinning drift")
    if x["refresh_design"]["coordinate_uncertainty_m_max"] != 10000:
        raise AssertionError("coordinate uncertainty gate drift")

    primary = x["frozen_primary"]
    if primary["status"] != "unresolved" or primary["n_taxa"] != 9:
        raise AssertionError("frozen primary summary drift")
    if p["orientation"]["status"] != "unresolved" or p["orientation"]["n_taxa"] != 9:
        raise AssertionError("main Chapter 2 primary was silently promoted")

    native = x["native_tbn_tier"]
    broad = x["non_gbif_tbn_tier"]
    if native["frozen_rule_status"] != "tendency_supported":
        raise AssertionError("native TBN sensitivity status drift")
    if broad["frozen_rule_status"] != "unresolved":
        raise AssertionError("broader non-GBIF TBN sensitivity status drift")
    if native["n_taxa"] != 11 or broad["n_taxa"] != 11:
        raise AssertionError("multi-source panel size drift")
    if (native["n_U"], native["n_D"]) != (6, 5) or (broad["n_U"], broad["n_D"]) != (6, 5):
        raise AssertionError("multi-source state balance drift")

    for tier in (native, broad):
        for axis in ("bio01", "bio15"):
            if tier[axis]["accepted_topology_sign_agreement"] != 1.0:
                raise AssertionError(f"{axis} topology sign agreement drift")
            if tier[axis]["species_loo_sign_agreement"] != 1.0:
                raise AssertionError(f"{axis} species LOO sign agreement drift")
            if tier[axis]["species_loo_evaluations"] != 66:
                raise AssertionError(f"{axis} species LOO evaluation count drift")

    if max(native["bio01"]["p_range"]) >= 0.05 or max(native["bio15"]["p_range"]) >= 0.05:
        raise AssertionError("native direct-TBN tier no longer crosses frozen threshold")
    if min(broad["bio01"]["p_range"]) < 0.05:
        raise AssertionError("broad tier BIO1 unexpectedly crosses threshold")
    if not (min(broad["bio15"]["p_range"]) < 0.05 <= max(broad["bio15"]["p_range"])):
        raise AssertionError("broad tier BIO15 no longer straddles threshold")

    close(native["bio01"]["beta_D_minus_U_sd_range"][0], -1.000777533308253)
    close(native["bio15"]["beta_D_minus_U_sd_range"][1], 1.142632619504463)
    close(broad["bio01"]["beta_D_minus_U_sd_range"][0], -0.9150138298039913)
    close(broad["bio15"]["beta_D_minus_U_sd_range"][1], 1.0842466179861467)

    if x["decision"]["primary_status_change"] is not False:
        raise AssertionError("sensitivity was silently promoted to primary")
    if "occurrence-source" not in x["decision"]["new_result"]:
        raise AssertionError("source-sensitivity interpretation missing")

    print("fdt4_taiwan_multisource_orientation_sensitivity_valid=true")
    print("primary_status=unresolved")
    print("native_tbn_status=tendency_supported")
    print("non_gbif_tbn_status=unresolved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
