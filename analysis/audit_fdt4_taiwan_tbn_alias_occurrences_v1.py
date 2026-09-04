#!/usr/bin/env python3
"""Audit TBN v2.6 through a frozen taxonomic-alias contract.

This sensitivity does not mutate the frozen exact-name TBN audit. Each of the seven
Taiwan orientation concepts is passed through the same contract machinery. Parent-
taxon lookup is allowed only when an occurrence-level name explicitly matches the
focal infraspecific concept. Configured UUIDs are authoritative; search results are
then audit context rather than an implicit expansion of the lookup set.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any

import pandas as pd
import requests

API_ROOT = "https://www.tbn.org.tw/api/v26"
NAME_FIELDS = (
    "simplifiedScientificName",
    "scientificName",
    "originalScientificName",
    "verbatimScientificName",
    "originalNameUsage",
    "acceptedScientificName",
    "originalVernacularName",
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--contract", type=Path, required=True)
    p.add_argument("--gbif-occurrences", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--timeout", type=float, default=60.0)
    return p.parse_args()


def text(v: Any) -> str:
    return " ".join(str(v or "").replace("\u00d7", "x").split())


def strip_html(v: Any) -> str:
    return text(re.sub(r"<[^>]+>", " ", str(v or "")))


def canonical_name(v: Any) -> str:
    x = strip_html(v).casefold()
    x = x.replace(" forma ", " f. ").replace(" variety ", " var. ")
    x = re.sub(r"\s+", " ", x).strip()
    return x


def name_prefix_matches(value: Any, allowed: list[str]) -> bool:
    source = canonical_name(value)
    if not source:
        return False
    for target in allowed:
        t = canonical_name(target)
        if source == t or source.startswith(t + " "):
            return True
    return False


def payload_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("data", "results"):
        rows = payload.get(key)
        if isinstance(rows, list):
            return [r for r in rows if isinstance(r, dict)]
    return []


def next_url(payload: dict[str, Any]) -> str:
    links = payload.get("links")
    return text(links.get("next")) if isinstance(links, dict) else ""


def get_json(session: requests.Session, url: str, *, params: dict[str, Any] | None, timeout: float) -> dict[str, Any]:
    r = session.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    if not isinstance(data, dict):
        raise RuntimeError(f"Expected JSON object from {r.url}")
    return data


def search_taxa(session: requests.Session, query: str, timeout: float) -> list[dict[str, Any]]:
    return payload_rows(get_json(session, f"{API_ROOT}/taxon", params={"name": query, "limit": 1000}, timeout=timeout))


def fetch_occurrences(session: requests.Session, taxon_uuid: str, timeout: float) -> list[dict[str, Any]]:
    url = f"{API_ROOT}/occurrence"
    params: dict[str, Any] | None = {"taxonUUID": taxon_uuid, "limit": 1000}
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for _ in range(100):
        payload = get_json(session, url, params=params, timeout=timeout)
        rows.extend(payload_rows(payload))
        nxt = next_url(payload)
        if not nxt or nxt in seen:
            break
        seen.add(nxt)
        url, params = nxt, None
    return rows


def as_float(v: Any) -> float | None:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def thin_cell(lat: float, lon: float, thin: float) -> tuple[int, int]:
    return math.floor(lat / thin), math.floor(lon / thin)


def occurrence_name_match(row: dict[str, Any], allowed: list[str]) -> tuple[bool, str, str]:
    for field in NAME_FIELDS:
        value = row.get(field)
        if name_prefix_matches(value, allowed):
            return True, field, strip_html(value)
    return False, "", ""


def in_bbox(lat: float, lon: float, bbox: dict[str, Any]) -> bool:
    return (
        float(bbox["lat_min"]) <= lat <= float(bbox["lat_max"])
        and float(bbox["lon_min"]) <= lon <= float(bbox["lon_max"])
    )


def geographic_admitted(rule: dict[str, Any], row: dict[str, Any], lat: float, lon: float, global_filters: dict[str, Any]) -> tuple[bool, str]:
    global_ok = in_bbox(lat, lon, global_filters)
    guard = rule.get("geographic_guard") or {}
    county = text(row.get("county"))

    # A restrictive range guard (currently albescens) must be satisfied even when
    # the coordinate is inside the broad Taiwan rectangle.
    allowed_counties = {text(x).casefold() for x in guard.get("allowed_counties", [])}
    fallback_bbox = guard.get("fallback_bbox")
    if allowed_counties or fallback_bbox:
        county_ok = bool(county) and county.casefold() in allowed_counties
        bbox_ok = bool(fallback_bbox) and in_bbox(lat, lon, fallback_bbox)
        if not (county_ok or bbox_ok):
            return False, "rejected_by_restrictive_taxon_range_guard"
        if not global_ok:
            return False, "rejected_outside_global_bbox"
        return True, "taxon_range_guard"

    # Some explicitly documented Taiwanese offshore counties fall outside the
    # primary rectangle. They are admitted only by exact county, not by widening
    # the whole rectangle toward mainland China.
    extra = {text(x).casefold() for x in guard.get("additional_allowed_counties_outside_global_bbox", [])}
    if global_ok:
        return True, "global_bbox"
    if county and county.casefold() in extra:
        return True, "explicit_offshore_county"
    return False, "rejected_outside_geographic_contract"


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    filt = contract["global_filters"]
    thin = float(filt["spatial_thin_degrees"])
    max_unc = float(filt["max_coordinate_uncertainty_m"])
    gbif = pd.read_csv(args.gbif_occurrences)
    taxa = [r["analysis_taxon"] for r in contract["rules"]]

    gbif_cells: dict[str, set[tuple[int, int]]] = {t: set() for t in taxa}
    for _, row in gbif.iterrows():
        taxon = text(row.get("scientific_name_query"))
        if taxon not in gbif_cells:
            continue
        lat = as_float(row.get("latitude", row.get("decimalLatitude")))
        lon = as_float(row.get("longitude", row.get("decimalLongitude")))
        if lat is not None and lon is not None:
            gbif_cells[taxon].add(thin_cell(lat, lon, thin))

    session = requests.Session()
    session.headers.update({"User-Agent": "EAzami-TBN-alias-audit/1.1"})
    resolution_rows: list[dict[str, Any]] = []
    occurrence_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []

    for rule in contract["rules"]:
        taxon = rule["analysis_taxon"]
        lookup_names = list(rule.get("lookup_taxon_names", []))
        allowed = list(rule["allowed_occurrence_names"])
        configured_uuids = {text(x) for x in rule.get("lookup_uuids", []) if text(x)}
        uuids = set(configured_uuids)
        searched: list[dict[str, Any]] = []
        matched_search_uuids: set[str] = set()
        for query in rule.get("lookup_queries", []):
            for row in search_taxa(session, query, args.timeout):
                searched.append(row)
                candidate = row.get("simplifiedScientificName") or row.get("scientificName") or row.get("taxonName")
                if name_prefix_matches(candidate, lookup_names):
                    u = text(row.get("taxonUUID"))
                    if u:
                        matched_search_uuids.add(u)
        # If a UUID has been explicitly frozen in the contract, search cannot
        # silently widen it. Search resolution is used only for taxa with no
        # configured UUID, notably the fail-closed C. pengii check.
        if not configured_uuids:
            uuids.update(matched_search_uuids)

        resolution_rows.append({
            "analysis_taxon": taxon,
            "lookup_mode": rule["lookup_mode"],
            "configured_uuids": " | ".join(sorted(configured_uuids)),
            "resolved_uuids": " | ".join(sorted(uuids)),
            "search_match_uuids_not_implicitly_added": " | ".join(sorted(matched_search_uuids - uuids)),
            "search_rows": len(searched),
            "matched_search_names": " | ".join(sorted({strip_html(r.get('simplifiedScientificName') or r.get('scientificName') or r.get('taxonName')) for r in searched if name_prefix_matches(r.get('simplifiedScientificName') or r.get('scientificName') or r.get('taxonName'), lookup_names)})),
            "equivalence_basis": rule["equivalence_basis"],
        })

        raw_by_key: dict[str, dict[str, Any]] = {}
        for u in sorted(uuids):
            for row in fetch_occurrences(session, u, args.timeout):
                key = text(row.get("occurrenceID") or row.get("UUID") or row.get("externalID"))
                if not key:
                    key = json.dumps(row, sort_keys=True, ensure_ascii=False)
                raw_by_key.setdefault(key, row)

        source_matches = 0
        valid_rows = 0
        geographic_rejections = 0
        valid_cells: set[tuple[int, int]] = set()
        strict_cells: set[tuple[int, int]] = set()
        new_cells: set[tuple[int, int]] = set()
        new_strict_cells: set[tuple[int, int]] = set()
        for row in raw_by_key.values():
            ok, matched_field, matched_name = occurrence_name_match(row, allowed)
            if not ok:
                continue
            source_matches += 1
            lat = as_float(row.get("decimalLatitude"))
            lon = as_float(row.get("decimalLongitude"))
            if lat is None or lon is None:
                continue
            geo_ok, geo_rule = geographic_admitted(rule, row, lat, lon, filt)
            if not geo_ok:
                geographic_rejections += 1
                continue
            valid_rows += 1
            unc = as_float(row.get("coordinateUncertaintyInMeters"))
            strict = unc is not None and unc <= max_unc
            cell = thin_cell(lat, lon, thin)
            valid_cells.add(cell)
            if strict:
                strict_cells.add(cell)
            new = cell not in gbif_cells[taxon]
            if new:
                new_cells.add(cell)
                if strict:
                    new_strict_cells.add(cell)
            occurrence_rows.append({
                "query_taxon": taxon,
                "lookup_mode": rule["lookup_mode"],
                "matched_name_field": matched_field,
                "matched_source_name": matched_name,
                "geographic_admission_rule": geo_rule,
                "taxon_uuid": text(row.get("taxonUUID")),
                "occurrence_id": text(row.get("occurrenceID") or row.get("UUID")),
                "external_id": text(row.get("externalID")),
                "scientific_name": strip_html(row.get("simplifiedScientificName") or row.get("scientificName")),
                "decimal_latitude": lat,
                "decimal_longitude": lon,
                "county": text(row.get("county")),
                "municipality": text(row.get("municipality")),
                "coordinate_uncertainty_m": unc if unc is not None else "",
                "strict_le_10km": strict,
                "thin_lat": cell[0],
                "thin_lon": cell[1],
                "new_vs_gbif_thin_cell": new,
                "event_date": text(row.get("eventDate")),
                "basis_of_record": text(row.get("basisOfRecord")),
                "dataset_uuid": text(row.get("datasetUUID")),
                "source": text(row.get("source")),
                "license": text(row.get("license")),
            })

        summary_rows.append({
            "taxon": taxon,
            "lookup_mode": rule["lookup_mode"],
            "resolved_uuid_count": len(uuids),
            "tbn_raw_unique_records": len(raw_by_key),
            "occurrence_name_matches": source_matches,
            "geographic_rejections": geographic_rejections,
            "valid_coordinate_rows": valid_rows,
            "valid_thin_cells": len(valid_cells),
            "strict_le_10km_thin_cells": len(strict_cells),
            "gbif_primary_thin_cells": len(gbif_cells[taxon]),
            "new_thin_cells_vs_gbif": len(new_cells),
            "new_strict_thin_cells_vs_gbif": len(new_strict_cells),
            "union_thin_cells_with_strict_alias_additions": len(gbif_cells[taxon] | new_strict_cells),
        })

    pd.DataFrame(resolution_rows).to_csv(args.out_dir / "tbn_alias_taxon_resolution_audit.csv", index=False)
    pd.DataFrame(occurrence_rows).to_csv(args.out_dir / "tbn_alias_occurrence_cells_source_guarded.csv", index=False)
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(args.out_dir / "tbn_alias_gbif_union_coverage.csv", index=False)
    payload = {
        "contract_version": "fdt4_taiwan_tbn_alias_occurrence_audit_v1",
        "status": "supporting_alias_sensitivity_not_primary_replacement",
        "source_contract": contract["contract_version"],
        "tbn_api": API_ROOT,
        "summary": summary.to_dict(orient="records"),
        "claim_boundary": "Only predeclared accepted-name/rank-token/original-name mappings are admitted. Configured UUIDs cannot be widened by search. Parent-taxon records require an occurrence-level focal name match, and taxon-specific published range guards are enforced without relaxing the n, uncertainty or thinning gates.",
    }
    (args.out_dir / "tbn_alias_occurrence_audit_v1.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(summary.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
