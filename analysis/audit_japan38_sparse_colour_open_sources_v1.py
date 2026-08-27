#!/usr/bin/env python3
"""Audit open Japan-local live-photo sources for sparse exact Japan38 colour concepts.

This is metadata discovery only. It resolves each frozen exact taxon name through
public iNaturalist and GBIF APIs, excludes specimen media, keeps item-level media
licenses separate, de-duplicates GBIF mirrors of iNaturalist where possible, and
reports independent 0.05-degree locality cells. No external image is downloaded or
measured in this stage.
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

INAT_TAXA = "https://api.inaturalist.org/v1/taxa"
INAT_OBS = "https://api.inaturalist.org/v1/observations"
GBIF_MATCH = "https://api.gbif.org/v1/species/match"
GBIF_OCC = "https://api.gbif.org/v1/occurrence/search"
JAPAN_PLACE_ID = 6737
USER_AGENT = "EAzami-scientific-reproducibility/1.0 (https://github.com/zuizui0223/EAzami; public biodiversity metadata audit)"
LIVE_BASIS = {"HUMAN_OBSERVATION", "OBSERVATION", "MACHINE_OBSERVATION"}
SPECIMEN_BASIS = {"PRESERVED_SPECIMEN", "FOSSIL_SPECIMEN", "MATERIAL_SAMPLE"}


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


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
        except (urllib.error.HTTPError, urllib.error.URLError) as exc:
            last = exc
            code = getattr(exc, "code", None)
            if code not in {None, 429, 500, 502, 503, 504} or i == attempts - 1:
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


def locality_cell(lat, lon, step=0.05):
    lat = finite_float(lat)
    lon = finite_float(lon)
    if lat is None or lon is None:
        return ""
    return f"{round(lat / step) * step:.2f},{round(lon / step) * step:.2f}"


def normalize_inat_key(*values):
    for value in values:
        if not value:
            continue
        m = re.search(r"inaturalist\.org/observations/(\d+)", str(value))
        if m:
            return f"inat:{m.group(1)}"
    return None


def exact_inat_taxon(name: str):
    data = request_json(INAT_TAXA, {"q": name, "rank": "species", "per_page": 100})
    hits = [x for x in data.get("results", []) if str(x.get("name", "")).strip().lower() == name.lower()]
    if not hits:
        return None
    hits.sort(key=lambda x: (not bool(x.get("is_active", True)), int(x.get("id", 0))))
    hit = hits[0]
    return {"id": int(hit["id"]), "name": hit.get("name"), "preferred_common_name": hit.get("preferred_common_name")}


def gbif_match(name: str):
    data = request_json(GBIF_MATCH, {"name": name, "strict": "true"})
    confidence = int(data.get("confidence") or 0)
    usage_key = data.get("usageKey")
    if not usage_key or confidence < 90:
        return None
    return {
        "usage_key": int(usage_key),
        "scientific_name": data.get("scientificName") or data.get("canonicalName"),
        "status": data.get("status"),
        "match_type": data.get("matchType"),
        "confidence": confidence,
    }


def fetch_inat(mid: str, target: str, taxon):
    if taxon is None:
        return [], 0
    rows = []
    total = None
    page = 1
    while page <= 50:
        data = request_json(INAT_OBS, {
            "taxon_id": taxon["id"],
            "place_id": JAPAN_PLACE_ID,
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
            taxon_name = ((obs.get("taxon") or {}).get("name") or "")
            record_url = obs.get("uri") or (f"https://www.inaturalist.org/observations/{obs_id}" if obs_id else "")
            for photo in obs.get("photos") or []:
                license_value = photo.get("license_code") or ""
                rows.append({
                    "paper_japan_member_id": mid,
                    "target_taxon_name": target,
                    "source": "iNaturalist",
                    "source_record_id": str(obs_id or ""),
                    "dedup_record_key": f"inat:{obs_id}" if obs_id else record_url,
                    "record_url": record_url,
                    "source_taxon_name": taxon_name,
                    "basis_of_record": "HUMAN_OBSERVATION",
                    "observed_on": obs.get("observed_on") or obs.get("time_observed_at") or "",
                    "place_text": obs.get("place_guess") or "",
                    "state_province": "",
                    "latitude": lat,
                    "longitude": lon,
                    "locality_cell_0_05deg": locality_cell(lat, lon),
                    "media_id": str(photo.get("id") or ""),
                    "media_url": photo.get("url") or "",
                    "media_license": license_value,
                    "media_license_class": classify_license(license_value),
                    "attribution": photo.get("attribution") or "",
                    "dataset": "iNaturalist direct API",
                })
        if not results or len(results) < 200 or page * 200 >= (total or 0):
            break
        page += 1
    return rows, int(total or 0)


def fetch_gbif(mid: str, target: str, match):
    if match is None:
        return [], 0
    rows = []
    offset = 0
    total = None
    while offset < 10000:
        data = request_json(GBIF_OCC, {
            "taxon_key": match["usage_key"],
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
            dedup = normalize_inat_key(occurrence_id, record_url) or (f"gbif:{key}" if key else occurrence_id or record_url)
            basis = (occ.get("basisOfRecord") or "").upper()
            lat = finite_float(occ.get("decimalLatitude"))
            lon = finite_float(occ.get("decimalLongitude"))
            state = occ.get("stateProvince") or ""
            for media in occ.get("media") or []:
                license_value = media.get("license") or ""
                rows.append({
                    "paper_japan_member_id": mid,
                    "target_taxon_name": target,
                    "source": "GBIF",
                    "source_record_id": str(key or ""),
                    "dedup_record_key": dedup,
                    "record_url": record_url,
                    "source_taxon_name": occ.get("scientificName") or "",
                    "basis_of_record": basis,
                    "observed_on": occ.get("eventDate") or occ.get("dateIdentified") or "",
                    "place_text": " | ".join(x for x in [state, occ.get("locality")] if x),
                    "state_province": state,
                    "latitude": lat,
                    "longitude": lon,
                    "locality_cell_0_05deg": locality_cell(lat, lon),
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


def is_live(row):
    return (row.get("basis_of_record") or "").upper() in LIVE_BASIS


def is_specimen(row):
    return (row.get("basis_of_record") or "").upper() in SPECIMEN_BASIS


def compact_candidates(rows):
    # Prefer iNaturalist direct rows over GBIF mirrors, then one row per unique media URL.
    by_key = defaultdict(list)
    for row in rows:
        by_key[row["dedup_record_key"]].append(row)
    kept = []
    for key, group in by_key.items():
        direct = [r for r in group if r["source"] == "iNaturalist"]
        chosen_group = direct or group
        seen_media = set()
        for row in chosen_group:
            media = row.get("media_url") or row.get("media_id")
            if media in seen_media:
                continue
            seen_media.add(media)
            kept.append(row)
    return sorted(kept, key=lambda r: (r["paper_japan_member_id"], r["dedup_record_key"], r["media_url"]))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--targets", type=Path, required=True)
    p.add_argument("--candidate-output", type=Path, required=True)
    p.add_argument("--summary-output", type=Path, required=True)
    args = p.parse_args()

    targets = read_csv(args.targets)
    all_rows = []
    resolution = {}
    api_totals = {}
    for target in targets:
        mid = target["paper_japan_member_id"]
        name = target["taxon_name"]
        inat = exact_inat_taxon(name)
        gbif = gbif_match(name)
        resolution[mid] = {"taxon_name": name, "inaturalist": inat, "gbif": gbif}
        inat_rows, inat_total = fetch_inat(mid, name, inat)
        gbif_rows, gbif_total = fetch_gbif(mid, name, gbif)
        all_rows.extend(inat_rows)
        all_rows.extend(gbif_rows)
        api_totals[mid] = {"inaturalist_photo_observations": inat_total, "gbif_stillimage_records": gbif_total}

    candidates = [
        r for r in all_rows
        if r["media_license_class"] == "open_reusable"
        and is_live(r)
        and not is_specimen(r)
        and bool(r.get("media_url"))
    ]
    compact = compact_candidates(candidates)

    fields = [
        "paper_japan_member_id", "target_taxon_name", "source", "source_record_id", "dedup_record_key",
        "record_url", "source_taxon_name", "basis_of_record", "observed_on", "place_text", "state_province",
        "latitude", "longitude", "locality_cell_0_05deg", "media_id", "media_url", "media_license",
        "media_license_class", "attribution", "dataset",
    ]
    args.candidate_output.parent.mkdir(parents=True, exist_ok=True)
    with args.candidate_output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows([{k: r.get(k, "") for k in fields} for r in compact])

    per_target = {}
    for target in targets:
        mid = target["paper_japan_member_id"]
        rows = [r for r in compact if r["paper_japan_member_id"] == mid]
        record_keys = {r["dedup_record_key"] for r in rows if r["dedup_record_key"]}
        cells = {r["locality_cell_0_05deg"] for r in rows if r["locality_cell_0_05deg"]}
        per_target[mid] = {
            "taxon_name": target["taxon_name"],
            "role": target["role"],
            "current_exact_colour_n": int(target["current_exact_colour_n"]),
            **api_totals[mid],
            "open_reusable_live_media_rows_after_dedup": len(rows),
            "open_reusable_live_record_keys_after_dedup": len(record_keys),
            "open_reusable_georeferenced_locality_cells_0_05deg": len(cells),
            "candidate_record_keys": sorted(record_keys),
            "candidate_locality_cells": sorted(cells),
        }

    result = {
        "contract_version": "japan38_sparse_colour_open_source_sweep_v1",
        "status_date": "2026-08-27",
        "scope": "metadata-only public source discovery for exact sparse Japan38 colour concepts",
        "targets": [r["paper_japan_member_id"] for r in targets],
        "taxon_resolution": resolution,
        "per_target": per_target,
        "total_open_reusable_live_candidate_rows_after_dedup": len(compact),
        "decision_rule": "A candidate is not promoted from metadata alone. Image-level locality/taxon provenance and the frozen Azami confidence floor must be verified in a separate predeclared measurement gate; new concepts should have at least two independent locality/date series before becoming population-matched history inputs.",
        "claim_boundary": "Open-license metadata discovery only. No external image has been measured here; record counts do not establish population phenotype, fixed colour state, ancestry, adaptation, convergence, or transition direction."
    }
    args.summary_output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
