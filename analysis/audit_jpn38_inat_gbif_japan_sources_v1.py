#!/usr/bin/env python3
"""Audit Japan-local Cirsium pendulum photo sources from iNaturalist and GBIF.

Metadata only. No external images are downloaded. The goal is to separate live
photo observations from preserved-specimen media before any image enters the Azami
colour pipeline, while enforcing explicit media licensing and locality independence.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

INAT_API = "https://api.inaturalist.org/v1/observations"
GBIF_API = "https://api.gbif.org/v1/occurrence/search"
INAT_TAXON_ID = 559940
INAT_JAPAN_PLACE_ID = 6737
GBIF_TAXON_KEY = 3113714
USER_AGENT = "EAzami-scientific-reproducibility/1.0 (https://github.com/zuizui0223/EAzami; public biodiversity metadata audit)"

FUKUSHIMA_BBOX = {
    "lat_min": 36.75,
    "lat_max": 37.98,
    "lon_min": 139.16,
    "lon_max": 141.05,
}
LIVE_BASIS = {"HUMAN_OBSERVATION", "OBSERVATION", "MACHINE_OBSERVATION"}
SPECIMEN_BASIS = {"PRESERVED_SPECIMEN", "FOSSIL_SPECIMEN", "MATERIAL_SAMPLE"}


def request_json(base: str, params: dict[str, object], attempts: int = 5):
    url = base + "?" + urllib.parse.urlencode(params, doseq=True)
    delays = (0, 3, 7, 15, 30)
    last = None
    for i in range(attempts):
        if delays[i]:
            time.sleep(delays[i])
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=45) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code not in {429, 500, 502, 503, 504} or i == attempts - 1:
                raise
            retry_after = exc.headers.get("Retry-After")
            if retry_after and retry_after.isdigit():
                time.sleep(min(int(retry_after), 60))
        except urllib.error.URLError as exc:
            last = exc
            if i == attempts - 1:
                raise
    raise last


def classify_license(value: str | None) -> str:
    s = (value or "").strip().lower().replace("_", "-")
    if not s:
        return "unspecified"
    if s in {"cc0", "cc-0"} or "publicdomain/zero" in s or "creativecommons.org/publicdomain" in s:
        return "open_reusable"
    if "cc-by-nc" in s or "/by-nc" in s or "by-nc/" in s:
        return "noncommercial_only"
    if "cc-by-nd" in s or "/by-nd" in s or "by-nd/" in s:
        return "no_derivatives"
    if s in {"cc-by", "cc-by-sa"}:
        return "open_reusable"
    if "creativecommons.org/licenses/by/" in s or "creativecommons.org/licenses/by-sa/" in s:
        return "open_reusable"
    if "all rights reserved" in s or s in {"arr", "copyright"}:
        return "restricted"
    return "other_or_unknown"


def finite_float(value):
    try:
        x = float(value)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def outside_fukushima_bbox(lat, lon) -> bool | None:
    lat = finite_float(lat)
    lon = finite_float(lon)
    if lat is None or lon is None:
        return None
    b = FUKUSHIMA_BBOX
    return not (b["lat_min"] <= lat <= b["lat_max"] and b["lon_min"] <= lon <= b["lon_max"])


def explicit_prefecture_independence(state_province: str | None):
    s = (state_province or "").strip()
    if not s:
        return None
    if re.search(r"fukushima|福島", s, flags=re.I):
        return False
    return True


def locality_cell(lat, lon, step=0.05):
    lat = finite_float(lat)
    lon = finite_float(lon)
    if lat is None or lon is None:
        return ""
    return f"{round(lat / step) * step:.2f},{round(lon / step) * step:.2f}"


def normalize_inat_record_key(url: str | None):
    if not url:
        return None
    m = re.search(r"inaturalist\.org/observations/(\d+)", str(url))
    return f"inat:{m.group(1)}" if m else None


def is_live_basis(value: str | None) -> bool:
    return (value or "").upper() in LIVE_BASIS


def is_specimen_basis(value: str | None) -> bool:
    return (value or "").upper() in SPECIMEN_BASIS


def fetch_inaturalist():
    rows = []
    page = 1
    total = None
    while page <= 20:
        data = request_json(INAT_API, {
            "taxon_id": INAT_TAXON_ID,
            "place_id": INAT_JAPAN_PLACE_ID,
            "photos": "true",
            "verifiable": "any",
            "per_page": 200,
            "page": page,
            "order_by": "id",
            "order": "asc",
        })
        if total is None:
            total = int(data.get("total_results", 0))
        results = data.get("results", [])
        for obs in results:
            obs_id = obs.get("id")
            geo = obs.get("geojson") or {}
            coords = geo.get("coordinates") or [None, None]
            lon = finite_float(coords[0]) if len(coords) > 0 else None
            lat = finite_float(coords[1]) if len(coords) > 1 else None
            record_url = obs.get("uri") or (f"https://www.inaturalist.org/observations/{obs_id}" if obs_id else "")
            for photo in obs.get("photos") or []:
                license_code = photo.get("license_code") or ""
                rows.append({
                    "source": "iNaturalist",
                    "source_record_id": str(obs_id or ""),
                    "dedup_record_key": f"inat:{obs_id}" if obs_id else record_url,
                    "record_url": record_url,
                    "taxon_name": ((obs.get("taxon") or {}).get("name") or ""),
                    "basis_of_record": "HUMAN_OBSERVATION",
                    "state_province": "",
                    "institution_code": "",
                    "collection_code": "",
                    "quality_grade": obs.get("quality_grade") or "",
                    "observed_on": obs.get("observed_on") or obs.get("time_observed_at") or "",
                    "place_text": obs.get("place_guess") or "",
                    "latitude": lat,
                    "longitude": lon,
                    "coordinate_accuracy_m": obs.get("positional_accuracy"),
                    "media_id": str(photo.get("id") or ""),
                    "media_url": photo.get("url") or "",
                    "media_license": license_code,
                    "media_license_class": classify_license(license_code),
                    "attribution": photo.get("attribution") or "",
                    "dataset": "iNaturalist direct API",
                })
        if not results or len(results) < 200 or page * 200 >= (total or 0):
            break
        page += 1
    return rows, int(total or 0)


def fetch_gbif():
    rows = []
    offset = 0
    total = None
    while offset < 3000:
        data = request_json(GBIF_API, {
            "taxon_key": GBIF_TAXON_KEY,
            "country": "JP",
            "media_type": "StillImage",
            "limit": 300,
            "offset": offset,
        })
        if total is None:
            total = int(data.get("count", 0))
        results = data.get("results", [])
        for occ in results:
            key = occ.get("key")
            occurrence_id = occ.get("occurrenceID") or ""
            record_url = occ.get("references") or (f"https://www.gbif.org/occurrence/{key}" if key else "")
            inat_key = normalize_inat_record_key(occurrence_id) or normalize_inat_record_key(record_url)
            dedup_key = inat_key or (f"gbif:{key}" if key else occurrence_id or record_url)
            lat = finite_float(occ.get("decimalLatitude"))
            lon = finite_float(occ.get("decimalLongitude"))
            basis = (occ.get("basisOfRecord") or "").upper()
            state_province = occ.get("stateProvince") or ""
            for media in occ.get("media") or []:
                license_value = media.get("license") or ""
                rows.append({
                    "source": "GBIF",
                    "source_record_id": str(key or ""),
                    "dedup_record_key": dedup_key,
                    "record_url": record_url,
                    "taxon_name": occ.get("scientificName") or "",
                    "basis_of_record": basis,
                    "state_province": state_province,
                    "institution_code": occ.get("institutionCode") or "",
                    "collection_code": occ.get("collectionCode") or "",
                    "quality_grade": occ.get("identificationVerificationStatus") or "",
                    "observed_on": occ.get("eventDate") or occ.get("dateIdentified") or "",
                    "place_text": " | ".join(x for x in [state_province, occ.get("locality")] if x),
                    "latitude": lat,
                    "longitude": lon,
                    "coordinate_accuracy_m": occ.get("coordinateUncertaintyInMeters"),
                    "media_id": media.get("identifier") or "",
                    "media_url": media.get("identifier") or media.get("references") or "",
                    "media_license": license_value,
                    "media_license_class": classify_license(license_value),
                    "attribution": media.get("creator") or media.get("rightsHolder") or "",
                    "dataset": occ.get("datasetTitle") or occ.get("datasetName") or "",
                })
        offset += len(results)
        if not results or offset >= (total or 0):
            break
    return rows, int(total or 0)


def add_gate_fields(rows):
    for row in rows:
        row["locality_cell_0_05deg"] = locality_cell(row.get("latitude"), row.get("longitude"))
        outside = outside_fukushima_bbox(row.get("latitude"), row.get("longitude"))
        pref_independent = explicit_prefecture_independence(row.get("state_province"))
        row["conservative_independent_from_fukushima"] = "" if outside is None else str(bool(outside)).lower()
        row["explicit_prefecture_independent_from_fukushima"] = "" if pref_independent is None else str(bool(pref_independent)).lower()
        row["media_is_live_observation"] = str(is_live_basis(row.get("basis_of_record"))).lower()
        row["media_is_specimen"] = str(is_specimen_basis(row.get("basis_of_record"))).lower()
        geographic_independent = outside is True or (outside is None and pref_independent is True)
        row["automated_measurement_candidate"] = str(
            row.get("media_license_class") == "open_reusable"
            and is_live_basis(row.get("basis_of_record"))
            and geographic_independent
            and bool(row.get("media_url"))
        ).lower()
        row["license_blocked_live_independent_candidate"] = str(
            row.get("media_license_class") == "noncommercial_only"
            and is_live_basis(row.get("basis_of_record"))
            and geographic_independent
            and bool(row.get("media_url"))
        ).lower()
    return rows


def summarize(rows, inat_total, gbif_total):
    by_source = defaultdict(list)
    for r in rows:
        by_source[r["source"]].append(r)
    open_rows = [r for r in rows if r["media_license_class"] == "open_reusable"]
    open_records = {r["dedup_record_key"] for r in open_rows if r["dedup_record_key"]}
    open_specimen_records = {
        r["dedup_record_key"] for r in open_rows
        if r["dedup_record_key"] and is_specimen_basis(r.get("basis_of_record"))
    }
    open_live_records = {
        r["dedup_record_key"] for r in open_rows
        if r["dedup_record_key"] and is_live_basis(r.get("basis_of_record"))
    }
    candidate_rows = [r for r in rows if r["automated_measurement_candidate"] == "true"]
    candidate_records = {r["dedup_record_key"] for r in candidate_rows if r["dedup_record_key"]}
    candidate_cells = {r["locality_cell_0_05deg"] for r in candidate_rows if r["locality_cell_0_05deg"]}
    license_blocked_rows = [r for r in rows if r["license_blocked_live_independent_candidate"] == "true"]
    license_blocked_records = {r["dedup_record_key"] for r in license_blocked_rows if r["dedup_record_key"]}
    license_blocked_cells = {r["locality_cell_0_05deg"] for r in license_blocked_rows if r["locality_cell_0_05deg"]}

    def source_summary(name, total_records):
        srows = by_source.get(name, [])
        return {
            "api_records_reported": total_records,
            "media_rows": len(srows),
            "open_reusable_media_rows": sum(r["media_license_class"] == "open_reusable" for r in srows),
            "open_reusable_record_keys": len({r["dedup_record_key"] for r in srows if r["media_license_class"] == "open_reusable" and r["dedup_record_key"]}),
            "open_reusable_specimen_record_keys": len({r["dedup_record_key"] for r in srows if r["media_license_class"] == "open_reusable" and is_specimen_basis(r.get("basis_of_record")) and r["dedup_record_key"]}),
            "open_reusable_live_record_keys": len({r["dedup_record_key"] for r in srows if r["media_license_class"] == "open_reusable" and is_live_basis(r.get("basis_of_record")) and r["dedup_record_key"]}),
            "noncommercial_only_media_rows": sum(r["media_license_class"] == "noncommercial_only" for r in srows),
            "unspecified_or_restricted_media_rows": sum(r["media_license_class"] in {"unspecified", "restricted", "other_or_unknown", "no_derivatives"} for r in srows),
        }

    def compact(rows_to_emit):
        out = []
        seen = set()
        for r in sorted(rows_to_emit, key=lambda x: (x["dedup_record_key"], x["source"], x["media_url"])):
            key = (r["dedup_record_key"], r["source"], r["media_url"])
            if key in seen:
                continue
            seen.add(key)
            out.append({k: r.get(k) for k in [
                "source", "source_record_id", "dedup_record_key", "record_url", "basis_of_record",
                "observed_on", "state_province", "place_text", "latitude", "longitude",
                "locality_cell_0_05deg", "media_url", "media_license", "media_license_class",
                "attribution", "institution_code", "collection_code", "dataset"
            ]})
        return out

    return {
        "contract_version": "jpn38_inat_gbif_japan_source_audit_v1",
        "taxon": "Cirsium pendulum",
        "inat_taxon_id": INAT_TAXON_ID,
        "inat_japan_place_id": INAT_JAPAN_PLACE_ID,
        "gbif_taxon_key": GBIF_TAXON_KEY,
        "fukushima_bbox_conservative_exclusion": FUKUSHIMA_BBOX,
        "sources": {
            "iNaturalist": source_summary("iNaturalist", inat_total),
            "GBIF": source_summary("GBIF", gbif_total),
        },
        "combined_media_rows": len(rows),
        "cross_source_unique_open_reusable_records": len(open_records),
        "cross_source_open_reusable_specimen_records": len(open_specimen_records),
        "cross_source_open_reusable_live_records": len(open_live_records),
        "conservative_independent_open_reusable_live_records": len(candidate_records),
        "conservative_independent_open_reusable_live_locality_cells_0_05deg": len(candidate_cells),
        "license_blocked_noncommercial_independent_live_records": len(license_blocked_records),
        "license_blocked_noncommercial_independent_live_locality_cells_0_05deg": len(license_blocked_cells),
        "automated_measurement_candidates": compact(candidate_rows),
        "permission_or_license_change_candidates": compact(license_blocked_rows),
        "decision": (
            "At least one conservatively independent Japanese open-license live-photo source is available for JPN_38 recovery."
            if candidate_records else
            "No conservatively independent Japanese open-license live-photo source was recovered. Open GBIF media are separated from preserved-specimen scans, and noncommercial live-photo records are retained only as permission/license candidates."
        ),
        "specimen_boundary": "Preserved-specimen images are never promoted to corolla-colour measurement because drying and preservation can alter colour. They may support locality/taxonomic context only.",
        "license_boundary": "Only CC0, CC BY and CC BY-SA media are automated-measurement candidates. CC BY-NC media are not auto-used here even when locality is suitable; they are retained as possible permission/license-change targets.",
        "geographic_boundary": "Coordinates outside a conservative whole-Fukushima bounding box are independent of the previous Fukushima/Aizu series. If coordinates are absent, an explicitly non-Fukushima stateProvince can establish coarse independence for source triage but not a precise population locality.",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--csv-output", type=Path, required=True)
    p.add_argument("--json-output", type=Path, required=True)
    args = p.parse_args()

    inat_rows, inat_total = fetch_inaturalist()
    gbif_rows, gbif_total = fetch_gbif()
    rows = add_gate_fields(inat_rows + gbif_rows)
    rows.sort(key=lambda r: (r["source"], r["dedup_record_key"], r["media_url"]))

    args.csv_output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "source", "source_record_id", "dedup_record_key", "record_url", "taxon_name",
        "basis_of_record", "state_province", "institution_code", "collection_code",
        "quality_grade", "observed_on", "place_text", "latitude", "longitude",
        "coordinate_accuracy_m", "locality_cell_0_05deg", "conservative_independent_from_fukushima",
        "explicit_prefecture_independent_from_fukushima", "media_is_live_observation", "media_is_specimen",
        "media_id", "media_url", "media_license", "media_license_class", "attribution", "dataset",
        "automated_measurement_candidate", "license_blocked_live_independent_candidate",
    ]
    with args.csv_output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    result = summarize(rows, inat_total, gbif_total)
    args.json_output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
