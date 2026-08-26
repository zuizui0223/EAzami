#!/usr/bin/env python3
"""Direct iDigBio combined-route check for K. Yonekura 6788.

This closes the pagination gap left by broad record-number and collector queries:
query the indexed collector and recordnumber fields together, so a zero result is
an actual server-side intersection rather than absence from the first 300 rows.
"""
from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://search.idigbio.org/v2/search/records/"
UA = "EAzami-scientific-reproducibility/1.0 (https://github.com/zuizui0223/EAzami; JPN29 combined specimen route)"
RQ = {"collector": "yonekura", "recordnumber": "6788"}


def request_json(attempts: int = 5):
    params = urllib.parse.urlencode({"rq": json.dumps(RQ, separators=(",", ":")), "limit": 100})
    url = API + "?" + params
    delays = (0, 3, 7, 15, 30)
    last = None
    for i in range(attempts):
        if delays[i]:
            time.sleep(delays[i])
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
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


def val(item: dict, *keys):
    index = item.get("indexTerms") or {}
    data = item.get("data") or {}
    for key in keys:
        for source in (index, data):
            value = source.get(key)
            if value not in (None, "", []):
                return value
    return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    data = request_json()
    items = data.get("items", [])
    rows = []
    for item in items:
        rows.append({
            "uuid": item.get("uuid"),
            "scientificname": val(item, "scientificname", "dwc:scientificName"),
            "catalognumber": val(item, "catalognumber", "dwc:catalogNumber"),
            "collector": val(item, "collector", "recordedby", "dwc:recordedBy"),
            "recordnumber": val(item, "recordnumber", "dwc:recordNumber"),
            "institutioncode": val(item, "institutioncode", "dwc:institutionCode"),
            "country": val(item, "country", "dwc:country"),
            "identifiedby": val(item, "identifiedby", "dwc:identifiedBy"),
            "dateidentified": val(item, "dateidentified", "dwc:dateIdentified"),
            "identificationremarks": val(item, "identificationremarks", "dwc:identificationRemarks"),
            "taxonremarks": val(item, "taxonremarks", "dwc:taxonRemarks"),
        })
    result = {
        "contract_version": "jpn29_idigbio_combined_route_v1",
        "query": RQ,
        "item_count": int(data.get("itemCount", len(items))),
        "returned_rows": len(rows),
        "rows": rows,
        "decision_boundary": "This server-side collector+recordnumber intersection closes the first-300 pagination gap in the broad iDigBio routes. It does not reidentify the specimen."
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
