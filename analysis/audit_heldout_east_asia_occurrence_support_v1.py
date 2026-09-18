#!/usr/bin/env python3
"""Audit held-out occurrence support without extracting any environmental outcome.

This script is intentionally climate-blind. It applies the frozen exact-name,
country-provenance, coordinate-quality, deduplication and 0.1-degree thinning
rules and reports only occurrence support.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import time
import urllib.parse
import urllib.request
from pathlib import Path

GBIF = "https://api.gbif.org/v1"
BAD_ISSUES = {
    "ZERO_COORDINATE",
    "COUNTRY_COORDINATE_MISMATCH",
    "COORDINATE_INVALID",
    "GEODETIC_DATUM_INVALID",
}
PRIMARY_ORIENTATION_STATUS = "candidate_primary"
PRIMARY_STICKINESS_STATUS = "candidate_primary"


def get_json(url: str, params: dict) -> dict:
    full = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(full, headers={"User-Agent": "EAzami-heldout-occurrence-audit/1.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode("utf-8"))


def norm_name(value: str) -> str:
    return " ".join((value or "").strip().split()).casefold()


def returned_name_matches(value: str, query: str) -> bool:
    a, b = norm_name(value), norm_name(query)
    return bool(a and b and (a == b or a.startswith(b + " ")))


def countries_for(frame: str) -> list[str]:
    x = frame.casefold()
    out = []
    if "china" in x:
        out.append("CN")
    if "korea" in x:
        out.append("KR")
    return out


def fetch_taxon_occurrences(name: str, countries: list[str], max_records: int) -> tuple[list[dict], dict]:
    match = get_json(f"{GBIF}/species/match", {"name": name, "strict": "true"})
    key = match.get("usageKey") or match.get("speciesKey")
    meta = {
        "gbif_match_type": match.get("matchType"),
        "gbif_usage_key": key,
        "gbif_scientific_name": match.get("scientificName") or "",
        "gbif_canonical_name": match.get("canonicalName") or "",
    }
    if not key:
        return [], meta

    rows: list[dict] = []
    for country in countries:
        offset = 0
        while offset < max_records:
            limit = min(300, max_records - offset)
            payload = get_json(
                f"{GBIF}/occurrence/search",
                {
                    "taxon_key": int(key),
                    "country": country,
                    "has_coordinate": "true",
                    "occurrence_status": "PRESENT",
                    "limit": limit,
                    "offset": offset,
                },
            )
            got = payload.get("results") or []
            if not got:
                break
            for r in got:
                rows.append(
                    {
                        "country": country,
                        "scientificName": r.get("scientificName") or "",
                        "latitude": r.get("decimalLatitude"),
                        "longitude": r.get("decimalLongitude"),
                        "uncertainty": r.get("coordinateUncertaintyInMeters"),
                        "issues": r.get("issues") or [],
                        "key": r.get("key"),
                    }
                )
            offset += len(got)
            if offset >= int(payload.get("count") or 0) or len(got) < limit:
                break
            time.sleep(0.02)
    return rows, meta


def finite_float(v):
    try:
        x = float(v)
        return x if math.isfinite(x) else None
    except (TypeError, ValueError):
        return None


def clean(rows: list[dict], query: str, max_uncertainty: float, thin: float) -> tuple[list[dict], dict]:
    exact_name = [r for r in rows if returned_name_matches(r.get("scientificName", ""), query)]

    quality = []
    for r in exact_name:
        lat = finite_float(r.get("latitude"))
        lon = finite_float(r.get("longitude"))
        unc = finite_float(r.get("uncertainty"))
        issues = set(r.get("issues") or [])
        if lat is None or lon is None:
            continue
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            continue
        if BAD_ISSUES & issues:
            continue
        # Frozen primary rule: missing uncertainty is not primary-quality support.
        if unc is None or unc > max_uncertainty:
            continue
        z = dict(r)
        z["latitude"], z["longitude"], z["uncertainty"] = lat, lon, unc
        quality.append(z)

    # Exact coordinate deduplication: choose lowest uncertainty, then lowest GBIF key.
    quality.sort(key=lambda r: (r["latitude"], r["longitude"], r["uncertainty"], int(r.get("key") or 10**18)))
    dedup = {}
    for r in quality:
        dedup.setdefault((r["latitude"], r["longitude"]), r)
    coordinate_unique = list(dedup.values())

    # Deterministic 0.1-degree thinning.
    coordinate_unique.sort(key=lambda r: (r["uncertainty"], int(r.get("key") or 10**18)))
    cells = {}
    for r in coordinate_unique:
        cell = (math.floor(r["latitude"] / thin), math.floor(r["longitude"] / thin))
        cells.setdefault(cell, r)
    thinned = list(cells.values())

    return thinned, {
        "n_raw": len(rows),
        "n_exact_name": len(exact_name),
        "n_quality": len(quality),
        "n_coordinate_unique": len(coordinate_unique),
        "n_thinned": len(thinned),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--traits", type=Path, required=True)
    p.add_argument("--contract", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--max-records-per-country", type=int, default=3000)
    a = p.parse_args()

    contract = json.loads(a.contract.read_text(encoding="utf-8"))
    occ = contract["occurrence"]
    min_n = int(occ["minimum_thinned_occurrences_primary"])
    max_unc = float(occ["max_coordinate_uncertainty_m"])
    thin = float(occ["thin_degrees"])

    with a.traits.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    candidates = [
        r for r in rows
        if r.get("orientation_pool_status") == PRIMARY_ORIENTATION_STATUS
        or r.get("stickiness_pool_status") == PRIMARY_STICKINESS_STATUS
    ]

    out_rows = []
    for i, r in enumerate(candidates, start=1):
        name = r["analysis_taxon"]
        countries = countries_for(r["provenance_frame"])
        raw, meta = fetch_taxon_occurrences(name, countries, a.max_records_per_country)
        thinned, counts = clean(raw, name, max_unc, thin)
        out = {
            "analysis_taxon": name,
            "provenance_frame": r["provenance_frame"],
            "orientation_state": r["orientation_state"],
            "stickiness_state": r["stickiness_state"],
            "countries_queried": "|".join(countries),
            **meta,
            **counts,
            "passes_primary_occurrence_gate": counts["n_thinned"] >= min_n,
            "minimum_thinned_occurrences_primary": min_n,
            "max_coordinate_uncertainty_m": max_unc,
            "thin_degrees": thin,
            "environment_opened": False,
        }
        out_rows.append(out)
        print(json.dumps(out, ensure_ascii=False), flush=True)

    a.out.parent.mkdir(parents=True, exist_ok=True)
    fields = list(out_rows[0]) if out_rows else [
        "analysis_taxon", "n_thinned", "passes_primary_occurrence_gate", "environment_opened"
    ]
    with a.out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(out_rows)


if __name__ == "__main__":
    main()
