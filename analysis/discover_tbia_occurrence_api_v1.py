#!/usr/bin/env python3
"""Discover and freeze the official TBIA occurrence API surface.

The crawler is intentionally bounded to official TBIA hosts, a small seed set and
links that look like API/documentation resources.  It records redirects, response
metadata and any OpenAPI/Swagger paths containing occurrence-related operations.
No biodiversity record is admitted by this discovery step.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import deque
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import requests

ALLOWED_HOST_SUFFIXES = ("tbia.org.tw", "tbia.github.io")
SEEDS = [
    "https://api.tbia.org.tw/",
    "https://portal.tbia.org.tw/",
    "https://www.tbia.org.tw/",
    "https://tbia.github.io/",
]
COMMON_PATHS = [
    "openapi.json", "swagger.json", "api-docs", "docs", "redoc",
    "v1/openapi.json", "v1/swagger.json", "api/openapi.json", "api/swagger.json",
    "robots.txt", "sitemap.xml",
]
API_WORDS = re.compile(r"api|swagger|openapi|occurrence|biodiversity|資料|介接", re.I)


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.title_parts: list[str] = []
        self.in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "title":
            self.in_title = True
        if tag.lower() == "a":
            for key, value in attrs:
                if key.lower() == "href" and value:
                    self.links.append(value)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data.strip())


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--out-json", type=Path, required=True)
    p.add_argument("--out-md", type=Path, required=True)
    p.add_argument("--max-pages", type=int, default=50)
    p.add_argument("--timeout", type=float, default=30.0)
    return p.parse_args()


def allowed(url: str) -> bool:
    host = (urlparse(url).hostname or "").casefold()
    return any(host == suffix or host.endswith("." + suffix) for suffix in ALLOWED_HOST_SUFFIXES)


def normalize(url: str) -> str:
    p = urlparse(url)
    return p._replace(fragment="").geturl()


def json_occurrence_paths(obj: Any) -> list[dict[str, Any]]:
    if not isinstance(obj, dict):
        return []
    paths = obj.get("paths")
    if not isinstance(paths, dict):
        return []
    out = []
    for path, methods in paths.items():
        text = json.dumps(methods, ensure_ascii=False) if isinstance(methods, dict) else str(methods)
        if re.search(r"occurrence|observation|record|物種|出現|觀測", path + " " + text, re.I):
            out.append({"path": path, "methods": sorted(k.upper() for k in methods if k.lower() in {"get", "post", "put", "delete", "patch"}) if isinstance(methods, dict) else []})
    return out


def main() -> int:
    a = parse_args()
    session = requests.Session()
    session.headers.update({"User-Agent": "EAzami-public-data-audit/1.0 (+https://github.com/zuizui0223/EAzami)"})
    queue: deque[str] = deque()
    for seed in SEEDS:
        queue.append(seed)
        for path in COMMON_PATHS:
            queue.append(urljoin(seed, path))
    seen: set[str] = set()
    pages: list[dict[str, Any]] = []
    occurrence_specs: list[dict[str, Any]] = []

    while queue and len(seen) < a.max_pages:
        url = normalize(queue.popleft())
        if url in seen or not allowed(url):
            continue
        seen.add(url)
        try:
            response = session.get(url, timeout=a.timeout, allow_redirects=True)
            final = normalize(response.url)
            ctype = response.headers.get("content-type", "").split(";", 1)[0].strip().casefold()
            body = response.text[:5_000_000]
            row: dict[str, Any] = {
                "requested_url": url,
                "final_url": final,
                "status": response.status_code,
                "content_type": ctype,
                "bytes_read": len(response.content),
                "etag": response.headers.get("etag", ""),
                "last_modified": response.headers.get("last-modified", ""),
                "title": "",
            }
            if "json" in ctype or body.lstrip().startswith(("{", "[")):
                try:
                    obj = response.json()
                except Exception:
                    obj = None
                if isinstance(obj, dict):
                    row["json_top_keys"] = sorted(obj)[:100]
                    row["openapi_version"] = obj.get("openapi") or obj.get("swagger") or ""
                    paths = json_occurrence_paths(obj)
                    if paths:
                        occurrence_specs.append({"spec_url": final, "openapi_version": row["openapi_version"], "occurrence_paths": paths})
            elif "html" in ctype or "<html" in body[:1000].casefold():
                parser = LinkParser()
                try:
                    parser.feed(body)
                except Exception:
                    pass
                row["title"] = " ".join(x for x in parser.title_parts if x)[:500]
                for href in parser.links:
                    target = normalize(urljoin(final, href))
                    if allowed(target) and API_WORDS.search(target):
                        queue.append(target)
            pages.append(row)
        except Exception as exc:
            pages.append({"requested_url": url, "final_url": "", "status": "error", "error": f"{type(exc).__name__}: {exc}"})

    successful = [x for x in pages if isinstance(x.get("status"), int) and 200 <= x["status"] < 400]
    payload = {
        "contract_version": "tbia_occurrence_api_discovery_v1",
        "status": "OCCURRENCE_SPEC_FOUND" if occurrence_specs else "NO_OPENAPI_OCCURRENCE_SPEC_FOUND_MANUAL_ENDPOINT_CONTRACT_REQUIRED",
        "allowed_hosts": list(ALLOWED_HOST_SUFFIXES),
        "seed_urls": SEEDS,
        "pages_attempted": len(pages),
        "successful_pages": len(successful),
        "occurrence_specs": occurrence_specs,
        "pages": pages,
        "next_gate": "Freeze an explicit endpoint, query schema, pagination rule, licence/source fields and taxon-name guard before downloading TBIA occurrence records.",
        "claim_boundary": "API discovery only; no record is admitted and no ecological result is changed.",
    }
    a.out_json.parent.mkdir(parents=True, exist_ok=True)
    a.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# TBIA occurrence API discovery v1", "",
        f"Status: **{payload['status']}**", "",
        f"Attempted {len(pages)} bounded official-host URLs; {len(successful)} returned 2xx/3xx.", "",
        "## Occurrence-capable specifications", "",
    ]
    if occurrence_specs:
        for spec in occurrence_specs:
            lines.append(f"### `{spec['spec_url']}`")
            lines.append("")
            lines.append(f"OpenAPI/Swagger version: `{spec['openapi_version']}`")
            lines.append("")
            for item in spec["occurrence_paths"]:
                lines.append(f"- `{','.join(item['methods']) or 'METHOD_UNDECLARED'} {item['path']}`")
    else:
        lines.append("No machine-readable OpenAPI/Swagger occurrence path was found in the bounded crawl. Inspect the successful official documentation pages and freeze a manual endpoint contract before use.")
    lines.extend(["", "## Next gate", "", payload["next_gate"], ""])
    a.out_md.parent.mkdir(parents=True, exist_ok=True)
    a.out_md.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "pages_attempted": len(pages), "occurrence_specs": len(occurrence_specs)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
