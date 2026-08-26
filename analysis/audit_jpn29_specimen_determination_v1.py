#!/usr/bin/env python3
"""Audit public aggregator metadata for JPN_29 specimen PE01523822 / Yonekura 6788.

The goal is to resolve, or explicitly fail to resolve, the specimen determination
history behind the Japanese voucher used for the JPN_29 nuclear tip. This script
queries public GBIF and iDigBio APIs only; it does not infer a new identification.
"""
from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

GBIF_API = "https://api.gbif.org/v1/occurrence/search"
IDIGBIO_API = "https://search.idigbio.org/v2/search/records/"
USER_AGENT = "EAzami-scientific-reproducibility/1.0 (https://github.com/zuizui0223/EAzami; specimen metadata audit)"
TARGET_CATALOG = "PE01523822"
TARGET_CATALOG_NUMERIC = "01523822"
TARGET_COLLECTOR = "Yonekura"
TARGET_NUMBER = "6788"
TARGET_TAXON = "Cirsium verutum"


def request_json(url: str, params: dict[str, object] | None = None, attempts: int = 5):
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
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
        except urllib.error.URLError as exc:
            last = exc
            if i == attempts - 1:
                raise
    raise last


def norm(value) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value or "").lower())


def present(value) -> bool:
    return value is not None and value != "" and value != []


def collector_number_match(recorded_by, record_number) -> bool:
    return "yonekura" in norm(recorded_by) and TARGET_NUMBER in norm(record_number)


def catalog_match(*values) -> bool:
    accepted = {norm(TARGET_CATALOG), norm(TARGET_CATALOG_NUMERIC)}
    return any(norm(v) in accepted for v in values if v is not None and norm(v))


def first_value(*values):
    for value in values:
        if present(value):
            return value
    return None


def compact_gbif(row: dict) -> dict:
    return {
        "key": row.get("key"),
        "scientificName": row.get("scientificName"),
        "acceptedScientificName": row.get("acceptedScientificName"),
        "taxonKey": row.get("taxonKey"),
        "basisOfRecord": row.get("basisOfRecord"),
        "institutionCode": row.get("institutionCode"),
        "collectionCode": row.get("collectionCode"),
        "catalogNumber": row.get("catalogNumber"),
        "occurrenceID": row.get("occurrenceID"),
        "recordedBy": row.get("recordedBy"),
        "recordNumber": row.get("recordNumber"),
        "country": row.get("country"),
        "stateProvince": row.get("stateProvince"),
        "locality": row.get("locality"),
        "eventDate": row.get("eventDate"),
        "identifiedBy": row.get("identifiedBy"),
        "dateIdentified": row.get("dateIdentified"),
        "identificationRemarks": row.get("identificationRemarks"),
        "taxonRemarks": row.get("taxonRemarks"),
        "references": row.get("references"),
        "media": row.get("media") or [],
    }


def compact_idigbio(item: dict) -> dict:
    data = item.get("data") or item
    index = item.get("indexTerms") or {}
    return {
        "uuid": item.get("uuid") or data.get("uuid"),
        "scientificname": first_value(index.get("scientificname"), data.get("scientificname"), data.get("dwc:scientificName")),
        "catalognumber": first_value(index.get("catalognumber"), data.get("catalognumber"), data.get("dwc:catalogNumber")),
        "occurrenceid": first_value(index.get("occurrenceid"), data.get("occurrenceid"), data.get("dwc:occurrenceID")),
        "recordedby": first_value(index.get("collector"), index.get("recordedby"), data.get("recordedby"), data.get("dwc:recordedBy")),
        "recordnumber": first_value(index.get("recordnumber"), data.get("recordnumber"), data.get("dwc:recordNumber")),
        "institutioncode": first_value(index.get("institutioncode"), data.get("institutioncode"), data.get("dwc:institutionCode")),
        "collectioncode": first_value(index.get("collectioncode"), data.get("collectioncode"), data.get("dwc:collectionCode")),
        "country": first_value(index.get("country"), data.get("country"), data.get("dwc:country")),
        "stateprovince": first_value(index.get("stateprovince"), data.get("stateprovince"), data.get("dwc:stateProvince")),
        "locality": first_value(index.get("locality"), data.get("locality"), data.get("dwc:locality")),
        "identifiedby": first_value(index.get("identifiedby"), data.get("identifiedby"), data.get("dwc:identifiedBy")),
        "dateidentified": first_value(index.get("dateidentified"), data.get("dateidentified"), data.get("dwc:dateIdentified")),
        "identificationremarks": first_value(data.get("identificationremarks"), data.get("dwc:identificationRemarks")),
        "taxonremarks": first_value(data.get("taxonremarks"), data.get("dwc:taxonRemarks")),
        "references": first_value(data.get("references"), data.get("dcterms:references")),
        "mediarecords": first_value(index.get("mediarecords"), data.get("mediarecords"), []),
    }


def run_query_set(api: str, queries: dict[str, dict[str, object]], *, idigbio=False):
    out = {}
    for name, query in queries.items():
        try:
            if idigbio:
                data = request_json(api, {"rq": json.dumps(query, separators=(",", ":")), "limit": 300})
                items = data.get("items", [])
                rows = [compact_idigbio(item) for item in items]
                count = int(data.get("itemCount", len(rows)))
            else:
                data = request_json(api, query)
                rows = [compact_gbif(r) for r in data.get("results", [])]
                count = int(data.get("count", len(rows)))
            out[name] = {"ok": True, "count": count, "rows": rows}
        except Exception as exc:
            out[name] = {"ok": False, "error": f"{type(exc).__name__}: {exc}", "count": 0, "rows": []}
    return out


def gbif_queries():
    return run_query_set(GBIF_API, {
        "catalog_full": {"catalog_number": TARGET_CATALOG, "limit": 300},
        "catalog_numeric_pe": {"catalog_number": TARGET_CATALOG_NUMERIC, "institution_code": "PE", "limit": 300},
        "record_number_japan": {"record_number": TARGET_NUMBER, "country": "JP", "limit": 300},
        "collector_taxon_japan": {"recorded_by": TARGET_COLLECTOR, "scientific_name": TARGET_TAXON, "country": "JP", "limit": 300},
    })


def idigbio_queries():
    # iDigBio's indexed collector field is `collector`; `recordedby` is a raw DWC field.
    # Use recordnumber alone for the collector-number route, then require Yonekura in
    # the returned collector field locally to avoid exact-string assumptions.
    return run_query_set(IDIGBIO_API, {
        "catalog_full": {"catalognumber": TARGET_CATALOG},
        "catalog_numeric_pe": {"catalognumber": TARGET_CATALOG_NUMERIC, "institutioncode": "pe"},
        "record_number": {"recordnumber": TARGET_NUMBER},
        "collector": {"collector": TARGET_COLLECTOR.lower()},
    }, idigbio=True)


def deduplicate(rows: list[dict], keys: tuple[str, ...]) -> list[dict]:
    seen = set()
    out = []
    for row in rows:
        signature = tuple(norm(row.get(k)) for k in keys)
        if not any(signature):
            signature = (json.dumps(row, sort_keys=True, ensure_ascii=False),)
        if signature in seen:
            continue
        seen.add(signature)
        out.append(row)
    return out


def summarize(gbif: dict, idigbio: dict):
    gbif_rows = [r for q in gbif.values() for r in q.get("rows", [])]
    idigbio_rows = [r for q in idigbio.values() for r in q.get("rows", [])]

    exact_gbif = deduplicate(
        [r for r in gbif_rows if catalog_match(r.get("catalogNumber"), r.get("occurrenceID"))],
        ("key", "catalogNumber", "occurrenceID"),
    )
    exact_idigbio = deduplicate(
        [r for r in idigbio_rows if catalog_match(r.get("catalognumber"), r.get("occurrenceid"))],
        ("uuid", "catalognumber", "occurrenceid"),
    )
    collector_gbif = deduplicate(
        [r for r in gbif_rows if collector_number_match(r.get("recordedBy"), r.get("recordNumber"))],
        ("key", "catalogNumber", "occurrenceID"),
    )
    collector_idigbio = deduplicate(
        [r for r in idigbio_rows if collector_number_match(r.get("recordedby"), r.get("recordnumber"))],
        ("uuid", "catalognumber", "occurrenceid"),
    )

    exact = [{"source": "GBIF", **r} for r in exact_gbif] + [{"source": "iDigBio", **r} for r in exact_idigbio]
    collector = [{"source": "GBIF", **r} for r in collector_gbif] + [{"source": "iDigBio", **r} for r in collector_idigbio]
    determination_fields = []
    for r in exact + collector:
        vals = {
            "source": r.get("source"),
            "scientific_name": r.get("scientificName") or r.get("scientificname"),
            "accepted_name": r.get("acceptedScientificName"),
            "identified_by": r.get("identifiedBy") or r.get("identifiedby"),
            "date_identified": r.get("dateIdentified") or r.get("dateidentified"),
            "identification_remarks": r.get("identificationRemarks") or r.get("identificationremarks"),
            "taxon_remarks": r.get("taxonRemarks") or r.get("taxonremarks"),
            "references": r.get("references"),
        }
        determination_fields.append(vals)

    determination_informative = any(
        any(present(v) for k, v in row.items() if k not in {"source", "scientific_name", "accepted_name"})
        for row in determination_fields
    )
    routes_ok = {
        "GBIF": all(q.get("ok") for q in gbif.values()),
        "iDigBio": all(q.get("ok") for q in idigbio.values()),
    }

    return {
        "contract_version": "jpn29_specimen_determination_public_api_audit_v1",
        "target": {
            "paper_japan_member_id": "JPN_29",
            "paper_taxon_concept": TARGET_TAXON,
            "catalog_number": TARGET_CATALOG,
            "catalog_number_numeric_variant": TARGET_CATALOG_NUMERIC,
            "collector": "K. Yonekura",
            "collector_number": TARGET_NUMBER,
            "voucher_label": "Japan: 16.05.2001, K. Yonekura 6788 (PE01523822)",
        },
        "sources": {"GBIF": gbif, "iDigBio": idigbio},
        "all_query_routes_ok": routes_ok,
        "exact_catalog_hits": exact,
        "collector_number_hits": collector,
        "exact_catalog_hit_count": len(exact),
        "collector_number_hit_count": len(collector),
        "determination_fields": determination_fields,
        "determination_history_resolved": determination_informative,
        "decision": (
            "Public aggregator metadata contain determination/annotation fields that require specimen-level review."
            if determination_informative
            else (
                "GBIF/iDigBio public metadata did not resolve a determination or annotation history for PE01523822 / Yonekura 6788. Direct herbarium-curator/specimen-image inspection remains required."
                if all(routes_ok.values())
                else "At least one public-aggregator query route failed; do not treat the aggregator search as exhausted until all routes return successfully."
            )
        ),
        "claim_boundary": "Aggregator absence or sparse metadata do not reidentify the specimen. The raw nuclear tip remains retained, while a clean Japan-local phenotype join remains blocked until specimen determination is resolved.",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    gbif = gbif_queries()
    idigbio = idigbio_queries()
    result = summarize(gbif, idigbio)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
