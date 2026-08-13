#!/usr/bin/env python3
"""Discover candidate primary literature for the EAzami Cirsium phylogeny map.

The script queries official Crossref and Europe PMC APIs, merges duplicate records,
adds transparent topic flags/relevance scores, and writes *unreviewed candidates*.
It does not alter the curated evidence registry and never promotes a topology claim
automatically.

Network-free testing and reruns are supported through JSON fixture options.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

CROSSREF_URL = "https://api.crossref.org/works"
EUROPE_PMC_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
DEFAULT_QUERIES = Path("data/evidence/cirsium_phylogeny_search_queries.txt")
DEFAULT_OUTDIR = Path("data/evidence/generated")

PHYLOGENY_TERMS = (
    "phylogen",
    "systematic",
    "species delimitation",
    "target capture",
    "target enrichment",
    "hyb-seq",
    "hybseq",
    "transcriptom",
    "ortholog",
    "astral",
)
RETICULATION_TERMS = (
    "hybrid",
    "introgress",
    "admixture",
    "allopolyploid",
    "reticulation",
    "incomplete lineage sorting",
    "cytonuclear",
    "chloroplast capture",
)
CYTOGENETIC_TERMS = (
    "chromosome",
    "karyotype",
    "polyploid",
    "aneuploid",
    "genome size",
    "flow cytometry",
    "b chromosome",
)
GENOMIC_TERMS = (
    "radseq",
    "rad-seq",
    "genome",
    "phylogenom",
    "target capture",
    "transcriptom",
    "hundreds of loci",
)
ORGANELLE_TERMS = ("chloroplast", "plastome", "plastid", "mitochondrial dna b")


@dataclass(frozen=True)
class HTTPConfig:
    mailto: str = ""
    timeout: int = 60
    retries: int = 5
    delay: float = 0.18


class JSONClient:
    def __init__(self, config: HTTPConfig) -> None:
        self.config = config
        self._last_request = 0.0

    def get_json(self, url: str, params: Mapping[str, object]) -> dict:
        query = dict(params)
        full_url = f"{url}?{urllib.parse.urlencode(query, doseq=True)}"
        for attempt in range(self.config.retries):
            elapsed = time.monotonic() - self._last_request
            if elapsed < self.config.delay:
                time.sleep(self.config.delay - elapsed)
            headers = {
                "User-Agent": (
                    "EAzami-Cirsium-literature-map/0.1 "
                    f"(mailto:{self.config.mailto or 'not-provided'})"
                ),
                "Accept": "application/json",
            }
            request = urllib.request.Request(full_url, headers=headers)
            try:
                with urllib.request.urlopen(request, timeout=self.config.timeout) as response:
                    raw = response.read()
                self._last_request = time.monotonic()
                return json.loads(raw.decode("utf-8"))
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                self._last_request = time.monotonic()
                if attempt + 1 == self.config.retries:
                    raise RuntimeError(f"Failed request: {full_url}") from exc
                wait = 2**attempt
                if isinstance(exc, urllib.error.HTTPError):
                    retry_after = exc.headers.get("Retry-After")
                    if retry_after and retry_after.isdigit():
                        wait = max(wait, int(retry_after))
                time.sleep(wait)
        raise AssertionError("unreachable")


def clean_markup(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value or "")
    value = value.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return re.sub(r"\s+", " ", value).strip()


def normalize_title(value: str) -> str:
    value = clean_markup(value).casefold()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def canonical_doi(value: str) -> str:
    value = (value or "").strip().casefold()
    value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value)
    value = re.sub(r"^doi:\s*", "", value)
    return value.rstrip(" .")


def read_queries(path: Path) -> list[str]:
    queries: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            queries.append(line)
    return queries


def first_text(value: object) -> str:
    if isinstance(value, list):
        return clean_markup(str(value[0])) if value else ""
    return clean_markup(str(value or ""))


def crossref_year(item: Mapping[str, object]) -> str:
    for key in ("published-print", "published-online", "issued", "created"):
        obj = item.get(key)
        if isinstance(obj, Mapping):
            parts = obj.get("date-parts")
            if isinstance(parts, list) and parts and isinstance(parts[0], list) and parts[0]:
                return str(parts[0][0])
            if key == "created" and obj.get("date-time"):
                return str(obj["date-time"])[:4]
    return ""


def crossref_authors(item: Mapping[str, object]) -> str:
    output: list[str] = []
    authors = item.get("author")
    if isinstance(authors, list):
        for author in authors:
            if not isinstance(author, Mapping):
                continue
            name = " ".join(
                part for part in (str(author.get("given", "")).strip(), str(author.get("family", "")).strip()) if part
            )
            if name:
                output.append(name)
    return "|".join(output)


def parse_crossref(payload: Mapping[str, object], query: str) -> list[dict[str, str]]:
    message = payload.get("message")
    if not isinstance(message, Mapping):
        return []
    items = message.get("items")
    if not isinstance(items, list):
        return []
    rows: list[dict[str, str]] = []
    for item in items:
        if not isinstance(item, Mapping):
            continue
        title = first_text(item.get("title"))
        if not title:
            continue
        rows.append(
            {
                "source": "crossref",
                "query": query,
                "title": title,
                "year": crossref_year(item),
                "doi": canonical_doi(str(item.get("DOI", ""))),
                "journal": first_text(item.get("container-title")),
                "authors": crossref_authors(item),
                "url": str(item.get("URL", "")).strip(),
                "abstract": clean_markup(str(item.get("abstract", ""))),
                "publication_type": str(item.get("type", "")).strip(),
            }
        )
    return rows


def europepmc_authors(item: Mapping[str, object]) -> str:
    author_list = item.get("authorList")
    names: list[str] = []
    if isinstance(author_list, Mapping):
        authors = author_list.get("author")
        if isinstance(authors, list):
            for author in authors:
                if isinstance(author, Mapping):
                    name = str(author.get("fullName", "")).strip()
                    if name:
                        names.append(name)
    if not names:
        author_string = str(item.get("authorString", "")).strip().rstrip(".")
        if author_string:
            names = [part.strip() for part in author_string.split(",") if part.strip()]
    return "|".join(names)


def parse_europepmc(payload: Mapping[str, object], query: str) -> list[dict[str, str]]:
    result_list = payload.get("resultList")
    if not isinstance(result_list, Mapping):
        return []
    results = result_list.get("result")
    if not isinstance(results, list):
        return []
    rows: list[dict[str, str]] = []
    for item in results:
        if not isinstance(item, Mapping):
            continue
        title = clean_markup(str(item.get("title", "")))
        if not title:
            continue
        doi = canonical_doi(str(item.get("doi", "")))
        source_id = str(item.get("id", "")).strip()
        source = str(item.get("source", "")).strip()
        url = f"https://europepmc.org/article/{source}/{source_id}" if source and source_id else ""
        rows.append(
            {
                "source": "europepmc",
                "query": query,
                "title": title,
                "year": str(item.get("pubYear", "")).strip(),
                "doi": doi,
                "journal": clean_markup(str(item.get("journalTitle", ""))),
                "authors": europepmc_authors(item),
                "url": url,
                "abstract": clean_markup(str(item.get("abstractText", ""))),
                "publication_type": clean_markup(str(item.get("pubType", ""))),
            }
        )
    return rows


def topic_flags(row: Mapping[str, str]) -> tuple[list[str], float]:
    text = " ".join((row.get("title", ""), row.get("abstract", ""), row.get("journal", ""))).casefold()
    flags: list[str] = []
    score = 0.0
    if "cirsium" in text:
        flags.append("cirsium")
        score += 4.0
    if "carduus" in text or "carduinae" in text or "cardueae" in text:
        flags.append("carduus_carduinae_context")
        score += 1.0
    if any(term in text for term in PHYLOGENY_TERMS):
        flags.append("phylogeny_systematics")
        score += 3.0
    if any(term in text for term in RETICULATION_TERMS):
        flags.append("reticulation")
        score += 2.5
    if any(term in text for term in CYTOGENETIC_TERMS):
        flags.append("cytogenetics")
        score += 1.5
    if any(term in text for term in GENOMIC_TERMS):
        flags.append("genome_scale")
        score += 2.0
    if any(term in text for term in ORGANELLE_TERMS):
        flags.append("organelle")
        score += 0.5
    if "review" in row.get("publication_type", "").casefold():
        flags.append("review_type")
        score -= 1.0
    if "cirsium" not in text and not ("carduus" in text and "phylogen" in text):
        score -= 3.0
    return flags, score


def dedupe(records: Sequence[Mapping[str, str]]) -> list[dict[str, str]]:
    merged: dict[str, dict[str, str]] = {}
    for raw in records:
        row = dict(raw)
        doi = canonical_doi(row.get("doi", ""))
        title_key = normalize_title(row.get("title", ""))
        key = f"doi:{doi}" if doi else f"title:{title_key}"
        if not title_key:
            continue
        if key not in merged:
            merged[key] = row
            continue
        current = merged[key]
        for field in ("source", "query"):
            values = {part for part in current.get(field, "").split("|") if part}
            values.update(part for part in row.get(field, "").split("|") if part)
            current[field] = "|".join(sorted(values))
        for field in ("abstract", "authors", "journal", "url", "year", "publication_type"):
            if len(row.get(field, "")) > len(current.get(field, "")):
                current[field] = row[field]
        if not current.get("doi") and doi:
            current["doi"] = doi
    output: list[dict[str, str]] = []
    for row in merged.values():
        flags, score = topic_flags(row)
        row["topic_flags"] = "|".join(flags)
        row["relevance_score"] = f"{score:.1f}"
        row["screening_status"] = "unreviewed"
        row["record_key"] = f"doi:{canonical_doi(row.get('doi', ''))}" if row.get("doi") else f"title:{normalize_title(row.get('title', ''))}"
        output.append(row)
    return sorted(output, key=lambda row: (-float(row["relevance_score"]), row.get("year", ""), row["title"].casefold()))


def write_csv(path: Path, rows: Iterable[Mapping[str, str]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def load_fixture(path: Path | None) -> dict | None:
    if path is None:
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queries", type=Path, default=DEFAULT_QUERIES)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    parser.add_argument("--rows-per-query", type=int, default=50)
    parser.add_argument("--mailto", default=os.getenv("CROSSREF_MAILTO", ""))
    parser.add_argument("--source", choices=("both", "crossref", "europepmc"), default="both")
    parser.add_argument("--crossref-fixture", type=Path)
    parser.add_argument("--europepmc-fixture", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    queries = read_queries(args.queries)
    if not queries:
        raise SystemExit("No search queries were found.")
    client = JSONClient(HTTPConfig(mailto=args.mailto))
    records: list[dict[str, str]] = []
    log_rows: list[dict[str, str]] = []
    crossref_fixture = load_fixture(args.crossref_fixture)
    europepmc_fixture = load_fixture(args.europepmc_fixture)

    for query in queries:
        if args.source in ("both", "crossref"):
            try:
                payload = crossref_fixture if crossref_fixture is not None else client.get_json(
                    CROSSREF_URL,
                    {
                        "query.bibliographic": query,
                        "rows": args.rows_per_query,
                        "select": "DOI,title,author,published-print,published-online,issued,created,container-title,URL,abstract,type",
                        **({"mailto": args.mailto} if args.mailto else {}),
                    },
                )
                found = parse_crossref(payload, query)
                records.extend(found)
                log_rows.append({"source": "crossref", "query": query, "status": "ok", "n_records": str(len(found)), "error": ""})
            except Exception as exc:
                log_rows.append({"source": "crossref", "query": query, "status": "error", "n_records": "0", "error": str(exc)})

        if args.source in ("both", "europepmc"):
            try:
                payload = europepmc_fixture if europepmc_fixture is not None else client.get_json(
                    EUROPE_PMC_URL,
                    {
                        "query": query,
                        "format": "json",
                        "pageSize": args.rows_per_query,
                        "resultType": "core",
                    },
                )
                found = parse_europepmc(payload, query)
                records.extend(found)
                log_rows.append({"source": "europepmc", "query": query, "status": "ok", "n_records": str(len(found)), "error": ""})
            except Exception as exc:
                log_rows.append({"source": "europepmc", "query": query, "status": "error", "n_records": "0", "error": str(exc)})

    candidates = dedupe(records)
    candidate_path = args.outdir / "cirsium_phylogeny_literature_candidates.csv"
    fields = (
        "record_key", "source", "query", "title", "year", "doi", "journal",
        "authors", "url", "publication_type", "abstract", "topic_flags",
        "relevance_score", "screening_status",
    )
    write_csv(candidate_path, candidates, fields)
    log_path = args.outdir / "cirsium_phylogeny_search_log.csv"
    write_csv(log_path, log_rows, ("source", "query", "status", "n_records", "error"))

    print(f"Queries: {len(queries)}")
    print(f"Raw records: {len(records)}")
    print(f"Unique candidates: {len(candidates)}")
    print(candidate_path)
    print(log_path)
    if not candidates:
        print("WARNING: no candidate records were returned", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
