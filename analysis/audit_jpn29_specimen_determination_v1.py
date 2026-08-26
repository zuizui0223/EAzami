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


def collector_number_match(recorded_by, record_number) -> bool:
    return "yonekura" in norm(recorded_by) and TARGET_NUMBER in norm(record_number)


def catalog_match(*values) -> bool:
    target = norm(TARGET_CATALOG)
    return any(target and target == norm(v) for v in values if v is not None)


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
        "scientificname": index.get("scientificname") or data.get("scientificname"),
        "catalognumber": index.get("catalognumber") or data.get("catalognumber"),
        "occurrenceid": index.get("occurrenceid") or data.get("occurrenceid"),
        "recordedby": index.get("recordedby") or data.get("recordedby"),
        "recordnumber": index.get("recordnumber") or data.get("recordnumber"),
        "institutioncode": index.get("institutioncode") or data.get("institutioncode"),
        "collectioncode": index.get("collectioncode") or data.get("collectioncode"),
        "country": index.get("country") or data.get("country"),
        "stateprovince": index.get("stateprovince") or data.get("stateprovince"),
        "locality": index.get("locality") or data.get("locality"),
        "identifiedby": index.get("identifiedby") or data.get("identifiedby"),
        "dateidentified": index.get("dateidentified") or data.get("dateidentified"),
        "identificationremarks": data.get("identificationremarks"),
        "taxonremarks": data.get("taxonremarks"),
        "mediarecords": data.get("mediarecords") or [],
    }


def gbif_queries():
    queries = {
        "catalog_number": {"catalog_number": TARGET_CATALOG, "limit": 300},
        "collector_taxon_japan": {
            "recorded_by": TARGET_COLLECTOR,
            "scientific_name": TARGET_TAXON,
            "country": "JP",
            "limit": 300,
        },
    }
    out = {}
    for name, params in queries.items():
        try:
            data = request_json(GBIF_API, params)
            rows = [compact_gbif(r) for r in data.get("results", [])]
            out[name] = {"ok": True, "count": int(data.get("count", len(rows))), "rows": rows}
        except Exception as exc:
            out[name] = {"ok": False, "error": f"{type(exc).__name__}: {exc}", "count": 0, "rows": []}
    return out


def idigbio_queries():
    queries = {
        "catalog_number": {"catalognumber": TARGET_CATALOG},
        "collector_number": {"recordedby": TARGET_COLLECTOR, "recordnumber": TARGET_NUMBER},
    }
    out = {}
    for name, rq in queries.items():
        try:
            data = request_json(IDIGBIO_API, {"rq": json.dumps(rq, separators=(",", ":")), "limit": 100})
            items = data.get("items", [])
            rows = [compact_idigbio(item) for item in items]
            out[name] = {"ok": True, "count": int(data.get("itemCount", len(rows))), "rows": rows}
        except Exception as exc:
            out[name] = {"ok": False, "error": f"{type(exc).__name__}: {exc}", "count": 0, "rows": []}
    return out


def summarize(gbif: dict, idigbio: dict):
    gbif_rows = [r for q in gbif.values() for r in q.get("rows", [])]
    idigbio_rows = [r for q in idigbio.values() for r in q.get("rows", [])]

    exact_gbif = [r for r in gbif_rows if catalog_match(r.get("catalogNumber"), r.get("occurrenceID"))]
    exact_idigbio = [r for r in idigbio_rows if catalog_match(r.get("catalognumber"), r.get("occurrenceid"))]
    collector_gbif = [r for r in gbif_rows if collector_number_match(r.get("recordedBy"), r.get("recordNumber"))]
    collector_idigbio = [r for r in idigbio_rows if collector_number_match(r.get("recordedby"), r.get("recordnumber"))]

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
        any(v not in {None, "", []} for k, v in row.items() if k not in {"source", "scientific_name", "accepted_name"})
        for row in determination_fields
    )

    return {
        "contract_version": "jpn29_specimen_determination_public_api_audit_v1",
        "target": {
            "paper_japan_member_id": "JPN_29",
            "paper_taxon_concept": TARGET_TAXON,
            "catalog_number": TARGET_CATALOG,
            "collector": "K. Yonekura",
            "collector_number": TARGET_NUMBER,
            "voucher_label": "Japan: 16.05.2001, K. Yonekura 6788 (PE01523822)",
        },
        "sources": {"GBIF": gbif, "iDigBio": idigbio},
        "exact_catalog_hits": exact,
        "collector_number_hits": collector,
        "exact_catalog_hit_count": len(exact),
        "collector_number_hit_count": len(collector),
        "determination_fields": determination_fields,
        "determination_history_resolved": determination_informative,
        "decision": (
            "Public aggregator metadata contain determination/annotation fields that require specimen-level review."
            if determination_informative
            else "GBIF/iDigBio public metadata did not resolve a determination or annotation history for PE01523822 / Yonekura 6788. Direct herbarium-curator/specimen-image inspection remains required."
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
