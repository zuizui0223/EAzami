#!/usr/bin/env python3
"""Audit TBN v2.6 for additional Taiwan orientation occurrence support.

This is a coverage audit only. It does not change the frozen n>=10 gate, PGLS,
or the Chapter 2 ecological classification. All seven Taiwan orientation taxa are
queried with the same rules to avoid outcome-targeted record harvesting.
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


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--gbif-occurrences", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--timeout", type=float, default=60.0)
    return p.parse_args()


def text(value: Any) -> str:
    return " ".join(str(value or "").replace("\u00d7", "x").split())


def strip_html(value: Any) -> str:
    return text(re.sub(r"<[^>]+>", " ", str(value or "")))


def taxon_name_matches(value: Any, query: str) -> bool:
    source = strip_html(value).casefold()
    target = text(query).casefold()
    return bool(source and (source == target or source.startswith(target + " ")))


def payload_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("data")
    if isinstance(rows, list):
        return [x for x in rows if isinstance(x, dict)]
    rows = payload.get("results")
    if isinstance(rows, list):
        return [x for x in rows if isinstance(x, dict)]
    return []


def next_url(payload: dict[str, Any]) -> str:
    links = payload.get("links")
    if isinstance(links, dict):
        return text(links.get("next"))
    return ""


def get_json(session: requests.Session, url: str, *, params: dict[str, Any] | None, timeout: float) -> dict[str, Any]:
    r = session.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    if not isinstance(data, dict):
        raise RuntimeError(f"Expected JSON object from {r.url}")
    return data


def resolve_taxon(session: requests.Session, query: str, timeout: float) -> tuple[str | None, list[dict[str, Any]]]:
    payload = get_json(session, f"{API_ROOT}/taxon", params={"name": query, "limit": 1000}, timeout=timeout)
    rows = payload_rows(payload)
    exact = []
    for row in rows:
        candidate = row.get("simplifiedScientificName") or row.get("scientificName") or row.get("taxonName")
        if taxon_name_matches(candidate, query):
            exact.append(row)
    if not exact:
        return None, rows
    exact.sort(key=lambda r: (0 if text(r.get("simplifiedScientificName")).casefold() == query.casefold() else 1, text(r.get("taxonUUID"))))
    return text(exact[0].get("taxonUUID")) or None, exact


def fetch_occurrences(session: requests.Session, taxon_uuid: str, timeout: float) -> list[dict[str, Any]]:
    url = f"{API_ROOT}/occurrence"
    params: dict[str, Any] | None = {"taxonUUID": taxon_uuid, "limit": 1000}
    rows: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    for _ in range(100):
        payload = get_json(session, url, params=params, timeout=timeout)
        rows.extend(payload_rows(payload))
        nxt = next_url(payload)
        if not nxt or nxt in seen_urls:
            break
        seen_urls.add(nxt)
        url, params = nxt, None
    return rows


def as_float(value: Any) -> float | None:
    try:
        x = float(value)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def thin_cell(lat: float, lon: float, thin: float) -> tuple[int, int]:
    return math.floor(lat / thin), math.floor(lon / thin)


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    cfg = json.loads(args.config.read_text(encoding="utf-8"))
    gbif = pd.read_csv(args.gbif_occurrences)
    bounds = cfg["gbif"]["japan_bounds"]
    thin = float(cfg["gbif"]["spatial_thin_degrees"])
    max_unc = float(cfg["gbif"]["max_coordinate_uncertainty_m_primary"])
    taxa = [text(x["scientific_name"]) for x in cfg["taxa"]]

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
    session.headers.update({"User-Agent": "EAzami-TBN-coverage-audit/1.0"})
    match_rows: list[dict[str, Any]] = []
    occurrence_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []

    for taxon in taxa:
        taxon_uuid, matches = resolve_taxon(session, taxon, args.timeout)
        match_rows.append({
            "query_taxon": taxon,
            "taxon_uuid": taxon_uuid or "",
            "exact_match_count": len(matches),
            "match_names": " | ".join(text(x.get("simplifiedScientificName") or x.get("scientificName")) for x in matches),
        })
        raw = fetch_occurrences(session, taxon_uuid, args.timeout) if taxon_uuid else []
        valid_cells: set[tuple[int, int]] = set()
        strict_cells: set[tuple[int, int]] = set()
        new_cells: set[tuple[int, int]] = set()
        new_strict_cells: set[tuple[int, int]] = set()
        valid_rows = 0
        source_match_rows = 0
        for row in raw:
            source_name = row.get("simplifiedScientificName") or row.get("scientificName") or ""
            if not taxon_name_matches(source_name, taxon):
                continue
            source_match_rows += 1
            lat = as_float(row.get("decimalLatitude"))
            lon = as_float(row.get("decimalLongitude"))
            if lat is None or lon is None:
                continue
            if not (float(bounds["lat_min"]) <= lat <= float(bounds["lat_max"]) and float(bounds["lon_min"]) <= lon <= float(bounds["lon_max"])):
                continue
            valid_rows += 1
            unc = as_float(row.get("coordinateUncertaintyInMeters"))
            strict = unc is not None and unc <= max_unc
            cell = thin_cell(lat, lon, thin)
            valid_cells.add(cell)
            if strict:
                strict_cells.add(cell)
            if cell not in gbif_cells[taxon]:
                new_cells.add(cell)
                if strict:
                    new_strict_cells.add(cell)
            occurrence_rows.append({
                "query_taxon": taxon,
                "taxon_uuid": taxon_uuid or "",
                "occurrence_id": text(row.get("occurrenceID") or row.get("UUID")),
                "external_id": text(row.get("externalID")),
                "scientific_name": strip_html(source_name),
                "decimal_latitude": lat,
                "decimal_longitude": lon,
                "coordinate_uncertainty_m": unc if unc is not None else "",
                "strict_le_10km": strict,
                "thin_lat": cell[0],
                "thin_lon": cell[1],
                "new_vs_gbif_thin_cell": cell not in gbif_cells[taxon],
                "event_date": text(row.get("eventDate")),
                "basis_of_record": text(row.get("basisOfRecord")),
                "dataset_uuid": text(row.get("datasetUUID")),
                "source": text(row.get("source")),
                "license": text(row.get("license")),
            })
        summary_rows.append({
            "taxon": taxon,
            "tbn_taxon_uuid": taxon_uuid or "",
            "tbn_raw_records": len(raw),
            "tbn_source_name_matches": source_match_rows,
            "tbn_valid_coordinate_rows": valid_rows,
            "tbn_valid_thin_cells": len(valid_cells),
            "tbn_strict_le_10km_thin_cells": len(strict_cells),
            "gbif_primary_thin_cells": len(gbif_cells[taxon]),
            "tbn_new_thin_cells_vs_gbif": len(new_cells),
            "tbn_new_strict_thin_cells_vs_gbif": len(new_strict_cells),
            "union_thin_cells_inclusive": len(gbif_cells[taxon] | valid_cells),
            "union_thin_cells_with_tbn_strict_additions": len(gbif_cells[taxon] | new_strict_cells),
        })

    pd.DataFrame(match_rows).to_csv(args.out_dir / "tbn_taxon_match_audit.csv", index=False)
    pd.DataFrame(occurrence_rows).to_csv(args.out_dir / "tbn_occurrence_cells_source_guarded.csv", index=False)
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(args.out_dir / "tbn_gbif_union_coverage_audit.csv", index=False)
    payload = {
        "contract_version": "fdt4_taiwan_tbn_occurrence_expansion_audit_v1",
        "status": "coverage_audit_only_not_primary_reanalysis",
        "tbn_api": API_ROOT,
        "taxa_queried": taxa,
        "filters": {
            "exact_source_taxon_name_guard": True,
            "bounds": bounds,
            "spatial_thin_degrees": thin,
            "strict_coordinate_uncertainty_m": max_unc,
        },
        "summary": summary.to_dict(orient="records"),
        "claim_boundary": "TBN is audited as an independent public occurrence source for all seven Taiwan orientation taxa. No PGLS or Chapter 2 classification is changed by this audit alone.",
    }
    (args.out_dir / "tbn_gbif_union_coverage_audit.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(summary.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
