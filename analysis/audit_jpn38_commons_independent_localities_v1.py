#!/usr/bin/env python3
"""Audit Wikimedia Commons Cirsium pendulum files for independent Japan-local evidence.

Metadata only: no external images are downloaded or committed. The purpose is to
separate additional photographs from genuinely independent locality evidence before
expanding the JPN_38 colour calibration.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

CATEGORY = "Category:Cirsium pendulum"
API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "EAzami-scientific-reproducibility/1.0 (https://github.com/zuizui0223/EAzami; Commons metadata audit)"


def clean_html(value: str | None) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", value or "")).split())


def open_license(license_short: str) -> bool:
    value = (license_short or "").upper()
    return any(token in value for token in ("CC BY", "CC0", "GFDL"))


def japan_word(text: str) -> bool:
    value = text or ""
    return "日本" in value or re.search(r"\bJapan\b", value, flags=re.I) is not None


def fukushima_aizu_text(text: str) -> bool:
    value = text or ""
    return ("福島" in value or "Fukushima" in value) and ("会津" in value or "Aizu" in value)


def korea_text(text: str) -> bool:
    value = text or ""
    return any(token.lower() in value.lower() for token in ("Korea", "Kimpo", "Gimpo", "韓国", "김포"))


def request_json(params: dict[str, str], attempts: int = 5):
    query = dict(params)
    query.setdefault("format", "json")
    query.setdefault("formatversion", "2")
    query.setdefault("maxlag", "5")
    url = API + "?" + urllib.parse.urlencode(query)
    delays = (0, 5, 10, 20, 30)
    last = None
    for i in range(attempts):
        if delays[i]:
            time.sleep(delays[i])
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code != 429 or i == attempts - 1:
                raise
            retry_after = exc.headers.get("Retry-After")
            if retry_after and retry_after.isdigit():
                time.sleep(min(int(retry_after), 60))
    raise last


def category_files(category: str):
    data = request_json({
        "action": "query",
        "list": "categorymembers",
        "cmtitle": category,
        "cmnamespace": "6",
        "cmlimit": "100",
    })
    rows = data.get("query", {}).get("categorymembers", [])
    titles = [row["title"] for row in rows]
    if not titles:
        raise RuntimeError(f"No file members returned for {category}")
    return titles


def file_metadata(titles: list[str]):
    data = request_json({
        "action": "query",
        "prop": "imageinfo",
        "iiprop": "url|extmetadata",
        "titles": "|".join(titles),
    })
    pages = data.get("query", {}).get("pages", [])
    if len(pages) != len(titles):
        raise RuntimeError(f"Metadata count mismatch titles={len(titles)} pages={len(pages)}")
    by_title = {page["title"]: page for page in pages}
    missing = sorted(set(titles) - set(by_title))
    if missing:
        raise RuntimeError(f"Missing metadata pages: {missing}")
    return by_title


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--category", default=CATEGORY)
    p.add_argument("--csv-output", type=Path, required=True)
    p.add_argument("--json-output", type=Path, required=True)
    args = p.parse_args()

    titles = sorted(category_files(args.category))
    metadata = file_metadata(titles)
    out = []
    for title in titles:
        page = metadata[title]
        info = page["imageinfo"][0]
        meta = info.get("extmetadata", {})
        description = clean_html(meta.get("ImageDescription", {}).get("value", ""))
        license_short = clean_html(meta.get("LicenseShortName", {}).get("value", ""))
        artist = clean_html(meta.get("Artist", {}).get("value", ""))
        date = clean_html(meta.get("DateTimeOriginal", {}).get("value", "")) or clean_html(meta.get("DateTime", {}).get("value", ""))
        source = clean_html(meta.get("Credit", {}).get("value", "")) or clean_html(meta.get("CreditLine", {}).get("value", ""))
        gps_lat = clean_html(meta.get("GPSLatitude", {}).get("value", ""))
        gps_lon = clean_html(meta.get("GPSLongitude", {}).get("value", ""))
        categories = clean_html(meta.get("Categories", {}).get("value", ""))
        aizu = fukushima_aizu_text(description)
        korea = korea_text(description)
        explicit_japan = japan_word(description) or aizu
        out.append({
            "commons_title": title,
            "page_url": "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"), safe=":_/"),
            "description": description,
            "date": date,
            "artist": artist,
            "license_short_name": license_short,
            "open_license": open_license(license_short),
            "explicit_japan_locality": explicit_japan,
            "known_fukushima_aizu": aizu,
            "explicit_korea_locality": korea,
            "gps_latitude": gps_lat,
            "gps_longitude": gps_lon,
            "source_credit": source,
            "categories": categories,
            "original_image_url": info.get("url", ""),
        })

    args.csv_output.parent.mkdir(parents=True, exist_ok=True)
    with args.csv_output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(out[0]))
        writer.writeheader()
        writer.writerows(out)

    known_aizu = [r for r in out if r["known_fukushima_aizu"]]
    other_japan = [r for r in out if r["explicit_japan_locality"] and not r["known_fukushima_aizu"]]
    explicit_korea = [r for r in out if r["explicit_korea_locality"]]
    unresolved = [
        r for r in out
        if not r["explicit_japan_locality"]
        and not r["explicit_korea_locality"]
        and not (r["gps_latitude"] and r["gps_longitude"])
    ]
    dalgial_same_date = [r for r in out if r["artist"] == "Dalgial" and r["date"] == "2008-09-15"]
    result = {
        "contract_version": "jpn38_commons_independent_locality_audit_v1",
        "category": args.category,
        "files_total": len(out),
        "open_license_files": sum(bool(r["open_license"]) for r in out),
        "explicit_japan_locality_files": sum(bool(r["explicit_japan_locality"]) for r in out),
        "known_fukushima_aizu_files": len(known_aizu),
        "other_explicit_japan_files": len(other_japan),
        "other_explicit_japan_titles": [r["commons_title"] for r in other_japan],
        "explicit_korea_files": len(explicit_korea),
        "explicit_korea_titles": [r["commons_title"] for r in explicit_korea],
        "location_unresolved_files": len(unresolved),
        "location_unresolved_titles": [r["commons_title"] for r in unresolved],
        "dalgial_2008_09_15_files": len(dalgial_same_date),
        "independent_japan_locality_candidates": len(other_japan),
        "decision": "The Commons category provides no explicit Japan locality independent of the already-used Fukushima/Aizu series. One Dalgial file is explicitly Kimpo, Korea; four same-author/same-date Dalgial files lack locality metadata and are not assigned to Korea or Japan by inference.",
        "decision_boundary": "A different filename or photograph is not an independent population replicate. Promote only files whose metadata explicitly establish a Japan locality distinct from Fukushima/Aizu, or whose coordinates can independently establish such a locality.",
        "claim_boundary": "Commons metadata audit only. Absence of explicit locality metadata is missing provenance, not evidence that the photograph was taken outside Japan. Same author/date association with an explicitly Korean file is not used to impute geography for unlabeled files."
    }
    args.json_output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
