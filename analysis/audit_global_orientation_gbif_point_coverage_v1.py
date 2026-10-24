#!/usr/bin/env python3
"""Climate-BLIND worldwide GBIF point-readiness audit for the frozen 35 U/D taxa.

Uses independent source-backed botanical labels before opening climate axes.
Does NOT create a taxon climate centroid or infer historical branch climate.
Strict GBIF source scientificName matching prevents synonym-based silent pooling.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

from build_global_orientation_nuclear_priority_intake_v1 import build

GBIF = "https://api.gbif.org/v1"
BAD = {
    "ZERO_COORDINATE", "COUNTRY_COORDINATE_MISMATCH",
    "COORDINATE_INVALID", "GEODETIC_DATUM_INVALID",
}
USER_AGENT = "EAzami-global-nuclear-orientation-occurrence-gate/1.0 (source-scoped)"
MAX_UNCERTAINTY_METERS = 10000
THIN_DEGREES = 0.1
MIN_THINNED = 5


def norm(s: str) -> str:
    return " ".join((s or "").strip().split()).casefold()


def exact_source_name(text: str, query: str) -> bool:
    a, b = norm(text), norm(query)
    return bool(a and b and (a == b or a.startswith(b + " ")))


def finite(v):
    try:
        x = float(v)
        return x if math.isfinite(x) else None
    except (ValueError, TypeError):
        return None


def get_json(endpoint: str, params: dict, retries: int = 4):
    full = GBIF + endpoint + "?" + urllib.parse.urlencode(params)
    last = None
    for n in range(retries):
        request = urllib.request.Request(full, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=50) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            last = exc
            if isinstance(exc, urllib.error.HTTPError) and exc.code not in (429, 500, 502, 503, 504):
                raise
            time.sleep(min(12, 2 * (n + 1)))
    raise RuntimeError("GBIF request failed after bounded retries: " + full) from last


def fetch_one(taxon: str, max_records: int):
    match = get_json("/species/match", {"name": taxon, "strict": "true"})
    meta = {
        "taxon": taxon,
        "gbif_match_type": match.get("matchType") or "",
        "gbif_canonical_name": match.get("canonicalName") or "",
        "gbif_status": match.get("status") or "",
        "gbif_usage_key": match.get("usageKey") or match.get("speciesKey") or "",
        "gbif_rank": match.get("rank") or "",
        "gbif_total_coordinate_present_count": 0,
    }
    if (meta["gbif_match_type"] != "EXACT" or
        norm(meta["gbif_canonical_name"]) != norm(taxon) or
        not meta["gbif_usage_key"]):
        return [], meta
    out, offset, total = [], 0, None
    while offset < max_records:
        limit = min(200, max_records - offset)
        z = get_json("/occurrence/search", {
            "taxonKey": int(meta["gbif_usage_key"]),
            "hasCoordinate": "true",
            "occurrenceStatus": "PRESENT",
            "limit": limit,
            "offset": offset,
        })
        if total is None:
            total = int(z.get("count") or 0)
        records = z.get("results") or []
        if not records:
            break
        out.extend(records)
        offset += len(records)
        if offset >= total or len(records) < limit:
            break
        time.sleep(.025)
    meta["gbif_total_coordinate_present_count"] = total or 0
    return out, meta


def qc_thin(records: list[dict], taxon: str):
    exact = [r for r in records if exact_source_name(r.get("scientificName") or "", taxon)]
    quality = []
    for r in exact:
        lat, lon = finite(r.get("decimalLatitude")), finite(r.get("decimalLongitude"))
        uncertainty = finite(r.get("coordinateUncertaintyInMeters"))
        if (lat is None or lon is None or uncertainty is None or uncertainty < 0 or
            uncertainty > MAX_UNCERTAINTY_METERS or not -90 <= lat <= 90 or
            not -180 <= lon <= 180 or BAD.intersection(set(r.get("issues") or []))):
            continue
        key = str(r.get("key") or "")
        if not key.isdigit():
            continue
        quality.append({
            "taxon": taxon, "gbif_key": key,
            "source_scientific_name": r.get("scientificName") or "",
            "latitude": lat, "longitude": lon,
            "coordinate_uncertainty_m": uncertainty,
            "country": r.get("country") or "",
            "country_code": r.get("countryCode") or "",
            "dataset_key": r.get("datasetKey") or "",
            "license": r.get("license") or "",
            "basis_of_record": r.get("basisOfRecord") or "",
            "year": r.get("year") or "",
            "native_status": "NOT_CHECKED",
        })
    ordered = sorted(quality, key=lambda r: (
        r["coordinate_uncertainty_m"], int(r["gbif_key"])
    ))
    coordinates = {}
    for r in ordered:
        coordinates.setdefault((r["latitude"], r["longitude"]), r)
    cells = {}
    for r in coordinates.values():
        key = (math.floor(r["latitude"] / THIN_DEGREES),
               math.floor(r["longitude"] / THIN_DEGREES))
        cells.setdefault(key, r)
    retained = sorted(cells.values(), key=lambda r: (r["taxon"], int(r["gbif_key"])))
    return retained, {
        "n_fetched": len(records),
        "n_source_exact": len(exact),
        "n_coordinate_quality": len(quality),
        "n_unique_coordinates": len(coordinates),
        "n_geocells_0_1deg": len(cells),
    }


def cohort():
    prior, _, wave, _ = build()
    candidates = {}
    for r in wave:
        if r["acquisition_tier"] != "priority_U_D_source":
            continue
        name, state = r["analysis_taxon_label"], r["orientation_candidate"]
        if name in candidates and candidates[name] != state:
            raise ValueError("multiple states for source taxon label")
        candidates[name] = state
    if len(candidates) != 35 or Counter(candidates.values()) != {"U": 24, "D": 11}:
        raise ValueError("pre-exposure cohort drift")
    canonical = "".join(name + "\t" + candidates[name] + "\n" for name in sorted(candidates))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    if digest != prior["frozen_priority_name_state_sha256"]:
        raise ValueError("priority source taxon and orientation fingerprint drift")
    return candidates, digest


def run(max_records: int):
    if max_records < 50 or max_records > 3000:
        raise ValueError("max_records must be in [50,3000]")
    candidates, digest = cohort()
    run_at = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    summary, points = [], []
    for i, taxon in enumerate(sorted(candidates), 1):
        records, meta = fetch_one(taxon, max_records=max_records)
        retained, counts = qc_thin(records, taxon)
        incomplete = len(records) < int(meta["gbif_total_coordinate_present_count"])
        row = {
            "taxon": taxon, "state": candidates[taxon],
            **meta, **counts,
            "max_records_per_taxon": max_records,
            "query_truncated_or_incomplete": incomplete,
            "geocell_min5_observed": counts["n_geocells_0_1deg"] >= MIN_THINNED,
            "climate_centroid_ready": False,
            "native_ranges_verified": False,
            "GBIF_snapshot_UTC": run_at,
        }
        summary.append(row)
        for r in retained:
            points.append({**r, "orientation_state_source": candidates[taxon]})
        print(json.dumps({
            "taxon": taxon, "state": candidates[taxon], "index": i,
            "fetched": counts["n_fetched"], "geocells": counts["n_geocells_0_1deg"],
            "truncated": incomplete, "usage_key": meta["gbif_usage_key"],
        }), flush=True)
    pass_all = [x for x in summary if x["geocell_min5_observed"]]
    pass_complete = [x for x in pass_all if not x["query_truncated_or_incomplete"]]
    result = {
        "version": "global_35taxon_orientation_gbif_climate_blind_source_gate_v1",
        "cohort_name_state_sha256": digest,
        "retrieval_UTC": run_at,
        "source": "GBIF occurrence API; precise coordinates retained only when source scientificName matches the query and uncertainty <=10km",
        "n_taxa_requested": len(candidates),
        "source_state_counts": dict(Counter(candidates.values())),
        "n_gbif_exact_species_matches": sum(x["gbif_match_type"]=="EXACT" and
                                              norm(x["gbif_canonical_name"]) == norm(x["taxon"])
                                              for x in summary),
        "n_geocell_min5_taxa": len(pass_all),
        "n_fully_enumerated_min5_taxa": len(pass_complete),
        "n_censored_taxa": sum(x["query_truncated_or_incomplete"] for x in summary),
        "state_counts_geocell_min5": dict(Counter(x["state"] for x in pass_all)),
        "state_counts_full_min5": dict(Counter(x["state"] for x in pass_complete)),
        "max_records_per_taxon": max_records,
        "min_thinned_cells": MIN_THINNED,
        "coordinate_max_uncertainty_m": MAX_UNCERTAINTY_METERS,
        "spatial_thinning_degrees": THIN_DEGREES,
        "total_fetched_records": sum(x["n_fetched"] for x in summary),
        "total_source_exact_records": sum(x["n_source_exact"] for x in summary),
        "total_qc_thinned_records": len(points),
        "native_range_qc_complete": False,
        "bio15_bio1_extracted": False,
        "world_nuclear_tree_estimated": False,
        "transition_climate_test_executed": False,
        "interpretation_limit": (
            "Present GBIF point coverage is NOT a taxon niche estimate; first freeze "
            "native-vs-introduced status, spatial/observer effort, climate version and "
            "uncertainty. Truncated occurrence searches are not full spatial samples."
        ),
    }
    return result, summary, points


def write_csv(path: Path, rows: list[dict], cols: list[str] | None = None):
    with path.open("w", encoding="utf-8", newline="") as h:
        fields = cols or list(rows[0]) if rows else cols or []
        if not fields:
            raise ValueError("cannot persist empty CSV without schema")
        w=csv.DictWriter(h,fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--outdir", type=Path, required=True)
    p.add_argument("--max-records-per-taxon", type=int, default=800)
    a=p.parse_args()
    result, summary, points=run(a.max_records_per_taxon)
    a.outdir.mkdir(parents=True,exist_ok=True)
    (a.outdir/"result.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    write_csv(a.outdir/"gbif_source_match_and_qc_by_taxon.csv",summary)
    write_csv(a.outdir/"gbif_exact_source_thinned_points.csv",points,cols=[
        "taxon","gbif_key","source_scientific_name","latitude","longitude",
        "coordinate_uncertainty_m","country","country_code","dataset_key","license",
        "basis_of_record","year","native_status","orientation_state_source"
    ])
    print(json.dumps(result,indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
