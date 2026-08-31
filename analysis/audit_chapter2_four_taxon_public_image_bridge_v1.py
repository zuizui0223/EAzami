#!/usr/bin/env python3
"""Audit current public image/coordinate coverage for two white-coloured sister systems.

This is a metadata coverage audit.  It does not download or measure images and
cannot provide phenotype evidence.  iNaturalist and GBIF are queried separately;
GBIF records that appear to republish iNaturalist observations are marked so
that source counts are not treated as independent biological replication.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

INAT_TAXA_URL = "https://api.inaturalist.org/v1/taxa"
INAT_OBS_URL = "https://api.inaturalist.org/v1/observations"
GBIF_MATCH_URL = "https://api.gbif.org/v1/species/match"
GBIF_OCC_URL = "https://api.gbif.org/v1/occurrence/search"

TAXA = [
    {
        "system_id": "ARENICOLA_BREVICAULE_IRUMTIENSE",
        "taxon": "Cirsium brevicaule",
        "colour_state": "white",
        "pair_role": "white",
    },
    {
        "system_id": "ARENICOLA_BREVICAULE_IRUMTIENSE",
        "taxon": "Cirsium irumtiense",
        "colour_state": "bluish-purple",
        "pair_role": "coloured",
    },
    {
        "system_id": "TAIWAN_KAWAKAMII_TATAKAENSE",
        "taxon": "Cirsium kawakamii",
        "colour_state": "white",
        "pair_role": "white",
    },
    {
        "system_id": "TAIWAN_KAWAKAMII_TATAKAENSE",
        "taxon": "Cirsium tatakaense",
        "colour_state": "purple",
        "pair_role": "coloured",
    },
]

COVERAGE_THRESHOLDS = {
    "ready_for_pairwise_image_pilot": 10,
    "limited_pilot": 3,
}

MANIFEST_FIELDS = [
    "system_id",
    "focal_taxon",
    "colour_state",
    "pair_role",
    "source",
    "source_record_id",
    "source_observation_id",
    "source_photo_id",
    "source_taxon_name",
    "observed_on",
    "observer_id",
    "latitude",
    "longitude",
    "coordinate_uncertainty_m",
    "coordinate_usable_for_environment",
    "geoprivacy_or_coordinate_issue",
    "photo_license",
    "photo_url",
    "references",
    "appears_inaturalist_republished_in_gbif",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--max-records-per-source-taxon", type=int, default=1000)
    parser.add_argument("--timeout-sec", type=int, default=90)
    parser.add_argument("--sleep-sec", type=float, default=0.35)
    parser.add_argument(
        "--user-agent",
        default="eazami-public-image-bridge/1.0 (research use; contact: rachelzhang0223@gmail.com)",
    )
    return parser.parse_args()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def finite_float(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def boolish(value: Any) -> bool:
    return value is True or text(value).lower() in {"true", "1", "yes"}


def get_json(
    url: str,
    params: dict[str, Any],
    *,
    timeout_sec: int,
    user_agent: str,
    retries: int = 5,
) -> dict[str, Any]:
    query = urlencode({key: value for key, value in params.items() if value is not None}, doseq=True)
    full_url = f"{url}?{query}" if query else url
    last_error: Exception | None = None
    for attempt in range(retries):
        request = Request(full_url, headers={"User-Agent": user_agent, "Accept": "application/json"})
        try:
            with urlopen(request, timeout=timeout_sec) as response:
                payload = json.loads(response.read().decode("utf-8"))
            if not isinstance(payload, dict):
                raise RuntimeError(f"Expected JSON object from {url}, received {type(payload).__name__}")
            return payload
        except HTTPError as error:
            last_error = error
            if error.code not in {429, 500, 502, 503, 504} or attempt == retries - 1:
                raise
        except (URLError, TimeoutError, json.JSONDecodeError) as error:
            last_error = error
            if attempt == retries - 1:
                raise
        time.sleep(min(2**attempt, 12))
    raise RuntimeError(f"Failed GET {full_url}: {last_error}")


def resolve_inat_taxon(name: str, args: argparse.Namespace) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    payload = get_json(
        INAT_TAXA_URL,
        {"q": name, "rank": "species", "is_active": "true", "per_page": 100},
        timeout_sec=args.timeout_sec,
        user_agent=args.user_agent,
    )
    candidates = []
    exact: dict[str, Any] | None = None
    for result in payload.get("results", []):
        candidate = {
            "id": result.get("id"),
            "name": text(result.get("name")),
            "rank": text(result.get("rank")),
            "is_active": result.get("is_active"),
            "observations_count": result.get("observations_count"),
            "matched_term": text(result.get("matched_term")),
        }
        candidates.append(candidate)
        if candidate["name"].casefold() == name.casefold() and candidate["rank"].casefold() == "species":
            exact = result
            break
    return exact, candidates


def inat_total(taxon_id: int, args: argparse.Namespace, *, geo: bool = False, flower: bool = False) -> int:
    params: dict[str, Any] = {
        "taxon_id": taxon_id,
        "quality_grade": "research",
        "photos": "true",
        "captive": "false",
        "per_page": 1,
    }
    if geo:
        params["geo"] = "true"
    if flower:
        params["term_id"] = 12
        params["term_value_id"] = 13
    payload = get_json(
        INAT_OBS_URL,
        params,
        timeout_sec=args.timeout_sec,
        user_agent=args.user_agent,
    )
    return int(payload.get("total_results") or 0)


def inat_observations(taxon_id: int, total: int, args: argparse.Namespace) -> tuple[list[dict[str, Any]], bool]:
    target = min(total, args.max_records_per_source_taxon)
    results: list[dict[str, Any]] = []
    page = 1
    while len(results) < target:
        per_page = min(200, target - len(results))
        payload = get_json(
            INAT_OBS_URL,
            {
                "taxon_id": taxon_id,
                "quality_grade": "research",
                "photos": "true",
                "captive": "false",
                "per_page": per_page,
                "page": page,
                "order_by": "id",
                "order": "asc",
            },
            timeout_sec=args.timeout_sec,
            user_agent=args.user_agent,
        )
        batch = payload.get("results") or []
        if not batch:
            break
        results.extend(batch)
        page += 1
        time.sleep(args.sleep_sec)
    return results[:target], total > target


def parse_inat_coordinates(observation: dict[str, Any]) -> tuple[float | None, float | None]:
    geojson = observation.get("geojson") or {}
    coordinates = geojson.get("coordinates") if isinstance(geojson, dict) else None
    if isinstance(coordinates, list) and len(coordinates) >= 2:
        lon = finite_float(coordinates[0])
        lat = finite_float(coordinates[1])
        if lat is not None and lon is not None:
            return lat, lon
    location = text(observation.get("location"))
    if "," in location:
        lat_text, lon_text = location.split(",", 1)
        return finite_float(lat_text), finite_float(lon_text)
    return None, None


def preferred_inat_photo_url(photo: dict[str, Any]) -> str:
    url = text(photo.get("url") or photo.get("medium_url") or photo.get("large_url"))
    if not url:
        return ""
    return re.sub(r"/(square|small|medium|large|original)\.", "/large.", url)


def inat_manifest_rows(taxon: dict[str, Any], observations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for observation in observations:
        lat, lon = parse_inat_coordinates(observation)
        geoprivacy = text(observation.get("geoprivacy")).lower()
        obscured = boolish(observation.get("obscured"))
        usable = lat is not None and lon is not None and geoprivacy not in {"obscured", "private"} and not obscured
        user = observation.get("user") or {}
        source_taxon = observation.get("taxon") or {}
        for photo in observation.get("photos") or []:
            photo_id = photo.get("id")
            if photo_id is None:
                continue
            rows.append(
                {
                    "system_id": taxon["system_id"],
                    "focal_taxon": taxon["taxon"],
                    "colour_state": taxon["colour_state"],
                    "pair_role": taxon["pair_role"],
                    "source": "iNaturalist",
                    "source_record_id": observation.get("id"),
                    "source_observation_id": observation.get("id"),
                    "source_photo_id": photo_id,
                    "source_taxon_name": text(source_taxon.get("name")),
                    "observed_on": text(observation.get("observed_on")),
                    "observer_id": user.get("id") if isinstance(user, dict) else "",
                    "latitude": lat,
                    "longitude": lon,
                    "coordinate_uncertainty_m": observation.get("positional_accuracy"),
                    "coordinate_usable_for_environment": usable,
                    "geoprivacy_or_coordinate_issue": geoprivacy or ("obscured" if obscured else ""),
                    "photo_license": text(photo.get("license_code")),
                    "photo_url": preferred_inat_photo_url(photo),
                    "references": f"https://www.inaturalist.org/observations/{observation.get('id')}",
                    "appears_inaturalist_republished_in_gbif": False,
                }
            )
    return rows


def resolve_gbif_taxon(name: str, args: argparse.Namespace) -> dict[str, Any]:
    payload = get_json(
        GBIF_MATCH_URL,
        {"name": name, "kingdom": "Plantae", "strict": "false"},
        timeout_sec=args.timeout_sec,
        user_agent=args.user_agent,
    )
    return {
        "usageKey": payload.get("usageKey"),
        "acceptedUsageKey": payload.get("acceptedUsageKey"),
        "scientificName": text(payload.get("scientificName")),
        "canonicalName": text(payload.get("canonicalName")),
        "rank": text(payload.get("rank")),
        "status": text(payload.get("status")),
        "matchType": text(payload.get("matchType")),
        "confidence": payload.get("confidence"),
        "synonym": payload.get("synonym"),
    }


def gbif_occurrences(usage_key: int | None, args: argparse.Namespace) -> tuple[int, list[dict[str, Any]], bool]:
    if not usage_key:
        return 0, [], False
    base = {
        "taxon_key": usage_key,
        "media_type": "StillImage",
        "has_coordinate": "true",
        "occurrence_status": "PRESENT",
    }
    first = get_json(
        GBIF_OCC_URL,
        {**base, "limit": 1, "offset": 0},
        timeout_sec=args.timeout_sec,
        user_agent=args.user_agent,
    )
    total = int(first.get("count") or 0)
    target = min(total, args.max_records_per_source_taxon)
    results: list[dict[str, Any]] = []
    offset = 0
    while len(results) < target:
        limit = min(300, target - len(results))
        payload = get_json(
            GBIF_OCC_URL,
            {**base, "limit": limit, "offset": offset},
            timeout_sec=args.timeout_sec,
            user_agent=args.user_agent,
        )
        batch = payload.get("results") or []
        if not batch:
            break
        results.extend(batch)
        offset += len(batch)
        if payload.get("endOfRecords"):
            break
        time.sleep(args.sleep_sec)
    return total, results[:target], total > target


def gbif_is_inat(record: dict[str, Any]) -> bool:
    fields = [
        record.get("occurrenceID"),
        record.get("references"),
        record.get("institutionCode"),
        record.get("collectionCode"),
        record.get("datasetTitle"),
        record.get("publishingOrgKey"),
    ]
    joined = " ".join(text(value).lower() for value in fields)
    return "inaturalist" in joined or "inaturalist.org" in joined or " iNat ".lower() in joined


def gbif_manifest_rows(taxon: dict[str, Any], records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for record in records:
        lat = finite_float(record.get("decimalLatitude"))
        lon = finite_float(record.get("decimalLongitude"))
        uncertainty = finite_float(record.get("coordinateUncertaintyInMeters"))
        issues = [text(value) for value in record.get("issues") or []]
        usable = lat is not None and lon is not None and (uncertainty is None or uncertainty <= 10000)
        inat_republished = gbif_is_inat(record)
        media = record.get("media") or []
        if not media:
            media = [{}]
        for index, medium in enumerate(media):
            photo_url = text(medium.get("identifier") or medium.get("references"))
            if not photo_url and index > 0:
                continue
            rows.append(
                {
                    "system_id": taxon["system_id"],
                    "focal_taxon": taxon["taxon"],
                    "colour_state": taxon["colour_state"],
                    "pair_role": taxon["pair_role"],
                    "source": "GBIF",
                    "source_record_id": text(record.get("key") or record.get("gbifID")),
                    "source_observation_id": text(record.get("occurrenceID")),
                    "source_photo_id": text(medium.get("identifier") or index),
                    "source_taxon_name": text(record.get("scientificName")),
                    "observed_on": text(record.get("eventDate") or record.get("dateIdentified")),
                    "observer_id": text(record.get("recordedBy") or record.get("identifiedBy")),
                    "latitude": lat,
                    "longitude": lon,
                    "coordinate_uncertainty_m": uncertainty,
                    "coordinate_usable_for_environment": usable,
                    "geoprivacy_or_coordinate_issue": "|".join(filter(None, issues)),
                    "photo_license": text(medium.get("license") or record.get("license")),
                    "photo_url": photo_url,
                    "references": text(record.get("references")),
                    "appears_inaturalist_republished_in_gbif": inat_republished,
                }
            )
    return rows


def observation_month(value: str) -> str:
    match = re.match(r"^(\d{4})-(\d{2})", value)
    return match.group(2) if match else "unknown"


def licence_class(value: str) -> str:
    low = value.lower()
    if not low:
        return "missing"
    if "creativecommons.org" in low or low.startswith("cc-") or low in {"cc0"}:
        return "creative_commons"
    return "other_or_all_rights_reserved"


def coverage_class(inat_strict_observations: int, gbif_noninat_usable_records: int, resolved: bool) -> str:
    if not resolved:
        return "not_evaluable"
    maximum = max(inat_strict_observations, gbif_noninat_usable_records)
    if maximum >= COVERAGE_THRESHOLDS["ready_for_pairwise_image_pilot"]:
        return "ready_for_pairwise_image_pilot"
    if maximum >= COVERAGE_THRESHOLDS["limited_pilot"]:
        return "limited_pilot"
    return "not_evaluable"


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    coverage_rows: list[dict[str, Any]] = []
    manifest_rows: list[dict[str, Any]] = []
    resolutions: dict[str, Any] = {}

    for taxon in TAXA:
        name = taxon["taxon"]
        exact_inat, inat_candidates = resolve_inat_taxon(name, args)
        time.sleep(args.sleep_sec)
        inat_id = int(exact_inat["id"]) if exact_inat and exact_inat.get("id") is not None else None
        inat_total_rg = inat_total(inat_id, args) if inat_id else 0
        time.sleep(args.sleep_sec)
        inat_total_geo = inat_total(inat_id, args, geo=True) if inat_id else 0
        time.sleep(args.sleep_sec)
        inat_total_flowering = inat_total(inat_id, args, flower=True) if inat_id else 0
        time.sleep(args.sleep_sec)
        inat_records, inat_capped = inat_observations(inat_id, inat_total_rg, args) if inat_id else ([], False)
        irows = inat_manifest_rows(taxon, inat_records)

        gbif = resolve_gbif_taxon(name, args)
        time.sleep(args.sleep_sec)
        gbif_key = gbif.get("acceptedUsageKey") or gbif.get("usageKey")
        gbif_total, gbif_records, gbif_capped = gbif_occurrences(int(gbif_key) if gbif_key else None, args)
        grows = gbif_manifest_rows(taxon, gbif_records)

        manifest_rows.extend(irows)
        manifest_rows.extend(grows)

        inat_obs_usable = {
            row["source_observation_id"]
            for row in irows
            if row["coordinate_usable_for_environment"]
        }
        inat_obs_sampled = {row["source_observation_id"] for row in irows}
        gbif_record_rows: dict[str, list[dict[str, Any]]] = {}
        for row in grows:
            gbif_record_rows.setdefault(str(row["source_record_id"]), []).append(row)
        gbif_noninat_record_ids = {
            record_id
            for record_id, rows in gbif_record_rows.items()
            if rows and not any(boolish(row["appears_inaturalist_republished_in_gbif"]) for row in rows)
        }
        gbif_noninat_usable = {
            record_id
            for record_id, rows in gbif_record_rows.items()
            if record_id in gbif_noninat_record_ids
            and any(boolish(row["coordinate_usable_for_environment"]) and text(row["photo_url"]) for row in rows)
        }
        gbif_inat_republished = set(gbif_record_rows) - gbif_noninat_record_ids

        photo_licences = Counter(licence_class(text(row["photo_license"])) for row in [*irows, *grows])
        months = Counter(observation_month(text(row["observed_on"])) for row in irows)
        observers = {text(row["observer_id"]) for row in irows if text(row["observer_id"])}
        exact_gbif_name = text(gbif.get("canonicalName") or gbif.get("scientificName"))
        gbif_resolved = bool(gbif_key) and exact_gbif_name.casefold() == name.casefold()
        resolved = inat_id is not None or gbif_resolved
        classification = coverage_class(len(inat_obs_usable), len(gbif_noninat_usable), resolved)

        coverage_rows.append(
            {
                "system_id": taxon["system_id"],
                "taxon": name,
                "colour_state": taxon["colour_state"],
                "pair_role": taxon["pair_role"],
                "inat_exact_resolved": inat_id is not None,
                "inat_taxon_id": inat_id or "",
                "inat_research_grade_photo_total": inat_total_rg,
                "inat_research_grade_geo_total_api": inat_total_geo,
                "inat_flowering_annotated_total": inat_total_flowering,
                "inat_records_audited": len(inat_records),
                "inat_unique_observations_audited": len(inat_obs_sampled),
                "inat_strict_coordinate_usable_observations_audited": len(inat_obs_usable),
                "inat_unique_observers_audited": len(observers),
                "inat_records_capped": inat_capped,
                "inat_observation_months_audited": json.dumps(dict(sorted(months.items())), sort_keys=True),
                "gbif_exact_resolved": gbif_resolved,
                "gbif_usage_key": gbif_key or "",
                "gbif_match_type": gbif.get("matchType", ""),
                "gbif_status": gbif.get("status", ""),
                "gbif_image_coordinate_total": gbif_total,
                "gbif_records_audited": len(gbif_records),
                "gbif_noninat_records_audited": len(gbif_noninat_record_ids),
                "gbif_noninat_coordinate_usable_image_records_audited": len(gbif_noninat_usable),
                "gbif_inat_republished_records_audited": len(gbif_inat_republished),
                "gbif_records_capped": gbif_capped,
                "creative_commons_photo_rows_audited": photo_licences.get("creative_commons", 0),
                "missing_photo_licence_rows_audited": photo_licences.get("missing", 0),
                "coverage_class": classification,
                "coverage_basis": "max(iNaturalist strict audited observations, non-iNaturalist GBIF usable audited records)",
                "claim_boundary": "metadata coverage only; not phenotype evidence or independent biological replication",
            }
        )
        resolutions[name] = {
            "iNaturalist_exact": {
                "id": inat_id,
                "name": text(exact_inat.get("name")) if exact_inat else "",
                "rank": text(exact_inat.get("rank")) if exact_inat else "",
            },
            "iNaturalist_candidates": inat_candidates,
            "GBIF_match": gbif,
        }
        time.sleep(args.sleep_sec)

    coverage_fields = list(coverage_rows[0].keys())
    write_csv(args.out_dir / "chapter2_four_taxon_public_image_coverage_v1.csv", coverage_rows, coverage_fields)
    write_csv(args.out_dir / "chapter2_four_taxon_public_image_sample_manifest_v1.csv", manifest_rows, MANIFEST_FIELDS)

    by_system: dict[str, Any] = {}
    for system_id in sorted({row["system_id"] for row in coverage_rows}):
        pair = [row for row in coverage_rows if row["system_id"] == system_id]
        classes = {row["pair_role"]: row["coverage_class"] for row in pair}
        rank = {"not_evaluable": 0, "limited_pilot": 1, "ready_for_pairwise_image_pilot": 2}
        minimum = min((rank[value] for value in classes.values()), default=0)
        pair_class = {0: "not_evaluable", 1: "limited_pilot", 2: "ready_for_pairwise_image_pilot"}[minimum]
        by_system[system_id] = {
            "taxon_classes": classes,
            "pair_coverage_class": pair_class,
            "primary_pairwise_replication_ready": pair_class == "ready_for_pairwise_image_pilot",
            "limited_pairwise_pilot_possible": pair_class in {"limited_pilot", "ready_for_pairwise_image_pilot"},
        }

    summary = {
        "contract_version": "chapter2_four_taxon_public_image_bridge_audit_v1",
        "retrieved_at_utc": utc_now(),
        "sources": ["iNaturalist API v1", "GBIF species and occurrence APIs"],
        "filters": {
            "iNaturalist": "research grade + photos + noncaptive; strict coordinate usability excludes obscured/private",
            "GBIF": "StillImage + coordinates + PRESENT; iNaturalist-republished records separated",
            "max_records_per_source_taxon": args.max_records_per_source_taxon,
        },
        "coverage_thresholds": COVERAGE_THRESHOLDS,
        "taxa": coverage_rows,
        "systems": by_system,
        "n_manifest_rows": len(manifest_rows),
        "taxonomy_resolution": resolutions,
        "next_gate": "Only systems with both taxa at least limited_pilot proceed to focused image measurement; primary replicated pair analysis requires both taxa ready under the same frozen contract.",
        "claim_boundary": [
            "Metadata coverage is not phenotype evidence.",
            "Photo rows are not independent biological samples.",
            "GBIF records that republish iNaturalist are not an independent source.",
            "Coverage reflects public-platform and licensing biases.",
            "No white-lineage remodelling, environmental response, syndrome or adaptation is inferred."
        ],
    }
    (args.out_dir / "chapter2_four_taxon_public_image_bridge_audit_v1.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (args.out_dir / "chapter2_four_taxon_taxonomy_resolution_v1.json").write_text(
        json.dumps(resolutions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "status": "ok",
        "coverage": {row["taxon"]: row["coverage_class"] for row in coverage_rows},
        "systems": by_system,
        "n_manifest_rows": len(manifest_rows),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
