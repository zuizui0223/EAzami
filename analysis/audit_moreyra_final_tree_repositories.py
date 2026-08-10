#!/usr/bin/env python3
"""Audit public repositories for Moreyra et al. 2025 final phylogeny artifacts.

The audit queries bibliographic and data-repository APIs using the article DOI,
preprint DOI, title, BioProject and author repository.  It reports records and
file-like candidates but never treats a title/DOI hit as a recovered tree unless
a machine-readable phylogenetic file is explicitly listed.

Network failures remain explicit rows.  Negative results document the bounded
search performed at one point in time; they are not proof that an artifact can
never be deposited later.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

ARTICLE_DOI = "10.1016/j.ympev.2025.108285"
PREPRINT_DOI = "10.2139/ssrn.4983163"
TITLE = "A thorny tale: The origin and diversification of Cirsium (Compositae)"
BIOPROJECT = "PRJNA957074"
AUTHOR_REPOSITORY = "ldmoreyra/A-thorny-tale"
DEFAULT_OUTDIR = Path("data/evidence/generated/moreyra_final_tree_repository_audit")

TREE_EXTENSIONS = {
    ".nwk",
    ".newick",
    ".tre",
    ".tree",
    ".treefile",
    ".nex",
    ".nexus",
    ".phy",
    ".phylip",
}
ALIGNMENT_EXTENSIONS = {
    ".fa",
    ".fas",
    ".fasta",
    ".aln",
    ".phy",
    ".phylip",
    ".nex",
    ".nexus",
}
ARCHIVE_EXTENSIONS = {".zip", ".tar", ".gz", ".tgz", ".bz2", ".xz"}
TREE_TOKENS = (
    "newick",
    "nexus",
    "treefile",
    "gene_tree",
    "gene-tree",
    "species_tree",
    "species-tree",
    "astral",
    "raxml",
    "iqtree",
    "dated_tree",
    "dated-tree",
    "mcc.tree",
)

CSV_FIELDS = (
    "service",
    "query_label",
    "request_method",
    "request_url",
    "http_status",
    "status",
    "record_count",
    "matching_record_count",
    "tree_like_file_count",
    "alignment_like_file_count",
    "archive_file_count",
    "matching_identifiers",
    "matching_titles",
    "candidate_files",
    "checked_at_utc",
    "error",
    "interpretation",
)


def clean(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def normalize_text(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", " ", clean(value).casefold()).strip()


def normalize_doi(value: object) -> str:
    text = clean(value).casefold()
    text = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", text)
    text = re.sub(r"^doi:\s*", "", text)
    return text.rstrip(" .")


def matches_article(title: object = "", identifiers: Iterable[object] = ()) -> bool:
    doi_values = {normalize_doi(value) for value in identifiers if clean(value)}
    if ARTICLE_DOI in doi_values or PREPRINT_DOI in doi_values:
        return True
    normalized_title = normalize_text(title)
    target = normalize_text(TITLE)
    return bool(normalized_title) and (
        normalized_title == target
        or ("thorny tale" in normalized_title and "cirsium" in normalized_title)
    )


def extension(name: str) -> str:
    lower = clean(name).casefold()
    if lower.endswith(".tar.gz"):
        return ".gz"
    return Path(lower).suffix


def classify_file(name: object) -> set[str]:
    text = clean(name)
    lower = text.casefold()
    ext = extension(text)
    classes: set[str] = set()
    if ext in TREE_EXTENSIONS or any(token in lower for token in TREE_TOKENS):
        classes.add("tree")
    if ext in ALIGNMENT_EXTENSIONS or "alignment" in lower or "supermatrix" in lower:
        classes.add("alignment")
    if ext in ARCHIVE_EXTENSIONS:
        classes.add("archive")
    return classes


class HttpClient:
    def __init__(self, timeout: int = 60, retries: int = 4) -> None:
        self.timeout = timeout
        self.retries = retries

    def request_json(
        self,
        url: str,
        *,
        method: str = "GET",
        payload: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> tuple[int, Any]:
        data = None
        merged_headers = {
            "User-Agent": "EAzami-Moreyra-final-tree-audit/1.0",
            "Accept": "application/json, */*;q=0.1",
        }
        if headers:
            merged_headers.update(headers)
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            merged_headers["Content-Type"] = "application/json"
        for attempt in range(self.retries):
            request = urllib.request.Request(
                url, data=data, method=method, headers=merged_headers
            )
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    raw = response.read()
                    return response.status, json.loads(raw.decode("utf-8"))
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
                if attempt + 1 == self.retries:
                    raise
                delay = 2**attempt
                if isinstance(exc, urllib.error.HTTPError):
                    retry_after = exc.headers.get("Retry-After")
                    if retry_after and retry_after.isdigit():
                        delay = max(delay, int(retry_after))
                time.sleep(delay)
        raise AssertionError("unreachable")


@dataclass
class ParsedResult:
    record_count: int
    matches: list[dict[str, Any]]
    files: list[str]


def result_row(
    *,
    service: str,
    query_label: str,
    method: str,
    url: str,
    checked_at: str,
    status: str,
    http_status: int | str = "",
    parsed: ParsedResult | None = None,
    error: str = "",
    interpretation: str = "",
) -> dict[str, object]:
    parsed = parsed or ParsedResult(0, [], [])
    files = sorted({clean(name) for name in parsed.files if clean(name)})
    classes = {name: classify_file(name) for name in files}
    identifiers = sorted(
        {
            clean(identifier)
            for match in parsed.matches
            for identifier in match.get("identifiers", [])
            if clean(identifier)
        }
    )
    titles = sorted({clean(match.get("title")) for match in parsed.matches if clean(match.get("title"))})
    return {
        "service": service,
        "query_label": query_label,
        "request_method": method,
        "request_url": url,
        "http_status": http_status,
        "status": status,
        "record_count": parsed.record_count,
        "matching_record_count": len(parsed.matches),
        "tree_like_file_count": sum("tree" in classes[name] for name in files),
        "alignment_like_file_count": sum("alignment" in classes[name] for name in files),
        "archive_file_count": sum("archive" in classes[name] for name in files),
        "matching_identifiers": "|".join(identifiers),
        "matching_titles": "|".join(titles),
        "candidate_files": "|".join(files),
        "checked_at_utc": checked_at,
        "error": error,
        "interpretation": interpretation,
    }


def parse_crossref(payload: Mapping[str, Any]) -> ParsedResult:
    message = payload.get("message", {}) if isinstance(payload, Mapping) else {}
    title_values = message.get("title", []) if isinstance(message, Mapping) else []
    title = title_values[0] if isinstance(title_values, list) and title_values else ""
    identifiers = [message.get("DOI", "")]
    relations = message.get("relation", {}) if isinstance(message, Mapping) else {}
    files: list[str] = []
    relation_identifiers: list[str] = []
    if isinstance(relations, Mapping):
        for relation_type, entries in relations.items():
            if not isinstance(entries, list):
                continue
            for entry in entries:
                if not isinstance(entry, Mapping):
                    continue
                relation_id = clean(entry.get("id"))
                if relation_id:
                    relation_identifiers.append(f"{relation_type}:{relation_id}")
    all_identifiers = identifiers + relation_identifiers
    matches = (
        [{"title": title, "identifiers": all_identifiers}]
        if matches_article(title, identifiers)
        else []
    )
    return ParsedResult(1 if message else 0, matches, files)


def datacite_record(record: Mapping[str, Any]) -> dict[str, Any]:
    attributes = record.get("attributes", {}) if isinstance(record, Mapping) else {}
    titles = attributes.get("titles", []) if isinstance(attributes, Mapping) else []
    title = ""
    if isinstance(titles, list) and titles and isinstance(titles[0], Mapping):
        title = clean(titles[0].get("title"))
    identifiers = [record.get("id", ""), attributes.get("doi", "")]
    related = attributes.get("relatedIdentifiers", []) if isinstance(attributes, Mapping) else []
    if isinstance(related, list):
        identifiers.extend(
            item.get("relatedIdentifier", "")
            for item in related
            if isinstance(item, Mapping)
        )
    return {"title": title, "identifiers": identifiers}


def parse_datacite(payload: Mapping[str, Any]) -> ParsedResult:
    data = payload.get("data", []) if isinstance(payload, Mapping) else []
    records = [item for item in data if isinstance(item, Mapping)] if isinstance(data, list) else []
    matches = [record for item in records if matches_article(**(record := datacite_record(item)))]
    return ParsedResult(len(records), matches, [])


def zenodo_record(record: Mapping[str, Any]) -> tuple[dict[str, Any], list[str]]:
    metadata = record.get("metadata", {}) if isinstance(record, Mapping) else {}
    title = clean(metadata.get("title")) if isinstance(metadata, Mapping) else ""
    identifiers: list[str] = [record.get("doi", ""), record.get("conceptdoi", "")]
    related = metadata.get("related_identifiers", []) if isinstance(metadata, Mapping) else []
    if isinstance(related, list):
        identifiers.extend(
            item.get("identifier", "")
            for item in related
            if isinstance(item, Mapping)
        )
    files = [
        clean(item.get("key") or item.get("filename"))
        for item in record.get("files", [])
        if isinstance(item, Mapping)
    ]
    return {"title": title, "identifiers": identifiers}, files


def parse_zenodo(payload: Mapping[str, Any]) -> ParsedResult:
    hits = payload.get("hits", {}) if isinstance(payload, Mapping) else {}
    hit_list = hits.get("hits", []) if isinstance(hits, Mapping) else []
    records = [item for item in hit_list if isinstance(item, Mapping)] if isinstance(hit_list, list) else []
    matches: list[dict[str, Any]] = []
    files: list[str] = []
    for item in records:
        record, record_files = zenodo_record(item)
        if matches_article(record["title"], record["identifiers"]):
            matches.append(record)
            files.extend(record_files)
    total = hits.get("total", len(records)) if isinstance(hits, Mapping) else len(records)
    if isinstance(total, Mapping):
        total = total.get("value", len(records))
    return ParsedResult(int(total or 0), matches, files)


def parse_dryad(payload: Mapping[str, Any]) -> ParsedResult:
    embedded = payload.get("_embedded", {}) if isinstance(payload, Mapping) else {}
    datasets = embedded.get("stash:datasets", []) if isinstance(embedded, Mapping) else []
    records = [item for item in datasets if isinstance(item, Mapping)] if isinstance(datasets, list) else []
    matches: list[dict[str, Any]] = []
    for item in records:
        title = clean(item.get("title"))
        identifiers = [item.get("identifier", ""), item.get("relatedPublicationISSN", "")]
        if matches_article(title, identifiers):
            matches.append({"title": title, "identifiers": identifiers})
    page = payload.get("count", len(records)) if isinstance(payload, Mapping) else len(records)
    return ParsedResult(int(page or len(records)), matches, [])


def figshare_record(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "title": clean(record.get("title")),
        "identifiers": [record.get("doi", ""), record.get("resource_doi", "")],
    }


def parse_figshare(payload: Any) -> ParsedResult:
    records = [item for item in payload if isinstance(item, Mapping)] if isinstance(payload, list) else []
    matches = [record for item in records if matches_article(**(record := figshare_record(item)))]
    return ParsedResult(len(records), matches, [])


def parse_github_repository(
    branches: Any,
    tags: Any,
    releases: Any,
    commits: Any,
    tree: Mapping[str, Any],
) -> ParsedResult:
    branch_records = branches if isinstance(branches, list) else []
    tag_records = tags if isinstance(tags, list) else []
    release_records = releases if isinstance(releases, list) else []
    commit_records = commits if isinstance(commits, list) else []
    tree_records = tree.get("tree", []) if isinstance(tree, Mapping) else []
    files = [clean(item.get("path")) for item in tree_records if isinstance(item, Mapping)]
    identifiers = [
        f"branches={len(branch_records)}",
        f"tags={len(tag_records)}",
        f"releases={len(release_records)}",
        f"commits={len(commit_records)}",
    ]
    return ParsedResult(
        len(files),
        [{"title": AUTHOR_REPOSITORY, "identifiers": identifiers}],
        files,
    )


def query_specs() -> list[dict[str, Any]]:
    encoded_doi = urllib.parse.quote(ARTICLE_DOI, safe="")
    encoded_title = urllib.parse.quote(f'"{TITLE}"')
    datacite_query = urllib.parse.quote(f'titles.title:"{TITLE}" OR relatedIdentifiers.relatedIdentifier:{ARTICLE_DOI}')
    dryad_query = urllib.parse.quote(TITLE)
    return [
        {
            "service": "Crossref",
            "label": "article DOI metadata and relations",
            "method": "GET",
            "url": f"https://api.crossref.org/works/{encoded_doi}",
            "parser": parse_crossref,
            "interpretation": "Checks DOI relations for linked datasets; Crossref relations are not a file archive.",
        },
        {
            "service": "DataCite",
            "label": "title or related DOI",
            "method": "GET",
            "url": f"https://api.datacite.org/dois?query={datacite_query}&page%5Bsize%5D=100",
            "parser": parse_datacite,
            "interpretation": "A zero match means no matching DataCite record was returned at audit time.",
        },
        {
            "service": "Zenodo",
            "label": "exact title",
            "method": "GET",
            "url": f"https://zenodo.org/api/records?q={encoded_title}&size=100",
            "parser": parse_zenodo,
            "interpretation": "Inspects file names only for records matching the article title or DOI.",
        },
        {
            "service": "Dryad",
            "label": "exact article title",
            "method": "GET",
            "url": f"https://datadryad.org/api/v2/search?q={dryad_query}&per_page=100",
            "parser": parse_dryad,
            "interpretation": "Dryad search results are title/identifier screened; file enumeration requires a matching dataset.",
        },
        {
            "service": "Figshare",
            "label": "article title and resource DOI",
            "method": "POST",
            "url": "https://api.figshare.com/v2/articles/search",
            "payload": {
                "search_for": TITLE,
                "resource_doi": ARTICLE_DOI,
                "limit": 100,
                "order": "published_date",
                "order_direction": "desc",
            },
            "parser": parse_figshare,
            "interpretation": "Matching article records are screened for a dataset/resource DOI; files require a matching article detail request.",
        },
    ]


def write_csv(path: Path, rows: Iterable[Mapping[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(CSV_FIELDS), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def audit_network(client: HttpClient, checked_at: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for spec in query_specs():
        try:
            http_status, payload = client.request_json(
                spec["url"],
                method=spec["method"],
                payload=spec.get("payload"),
            )
            parsed = spec["parser"](payload)
            rows.append(
                result_row(
                    service=spec["service"],
                    query_label=spec["label"],
                    method=spec["method"],
                    url=spec["url"],
                    checked_at=checked_at,
                    status="queried",
                    http_status=http_status,
                    parsed=parsed,
                    interpretation=spec["interpretation"],
                )
            )
        except Exception as exc:
            rows.append(
                result_row(
                    service=spec["service"],
                    query_label=spec["label"],
                    method=spec["method"],
                    url=spec["url"],
                    checked_at=checked_at,
                    status="query_failed",
                    error=f"{type(exc).__name__}: {exc}",
                    interpretation=spec["interpretation"],
                )
            )
    return rows


def audit_github(client: HttpClient, checked_at: str, token: str = "") -> dict[str, object]:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    base = f"https://api.github.com/repos/{AUTHOR_REPOSITORY}"
    endpoints = {
        "branches": f"{base}/branches?per_page=100",
        "tags": f"{base}/tags?per_page=100",
        "releases": f"{base}/releases?per_page=100",
        "commits": f"{base}/commits?per_page=100",
    }
    try:
        payloads: dict[str, Any] = {}
        status_codes: list[int] = []
        for key, url in endpoints.items():
            status, payload = client.request_json(url, headers=headers)
            status_codes.append(status)
            payloads[key] = payload
        commits = payloads["commits"] if isinstance(payloads["commits"], list) else []
        if not commits:
            raise ValueError("author repository has no commit record")
        tree_url = commits[0].get("commit", {}).get("tree", {}).get("url", "")
        if not tree_url:
            raise ValueError("latest commit has no tree URL")
        status, tree = client.request_json(tree_url + "?recursive=1", headers=headers)
        status_codes.append(status)
        parsed = parse_github_repository(
            payloads["branches"],
            payloads["tags"],
            payloads["releases"],
            commits,
            tree,
        )
        return result_row(
            service="GitHub",
            query_label="author repository branches, tags, releases, commits and recursive tree",
            method="GET",
            url=base,
            checked_at=checked_at,
            status="queried",
            http_status="|".join(str(value) for value in status_codes),
            parsed=parsed,
            interpretation=(
                "Exhausts the visible history of the public author repository. "
                "One commit with three files means there is no deleted public history in this repository."
            ),
        )
    except Exception as exc:
        return result_row(
            service="GitHub",
            query_label="author repository branches, tags, releases, commits and recursive tree",
            method="GET",
            url=base,
            checked_at=checked_at,
            status="query_failed",
            error=f"{type(exc).__name__}: {exc}",
            interpretation="Could not complete author-repository history audit.",
        )


def summary(rows: Sequence[Mapping[str, object]]) -> dict[str, object]:
    queried = [row for row in rows if row["status"] == "queried"]
    matching = [row for row in queried if int(row["matching_record_count"] or 0) > 0]
    tree_candidates = [row for row in queried if int(row["tree_like_file_count"] or 0) > 0]
    return {
        "article_doi": ARTICLE_DOI,
        "preprint_doi": PREPRINT_DOI,
        "title": TITLE,
        "bioproject": BIOPROJECT,
        "services_attempted": len(rows),
        "services_queried_successfully": len(queried),
        "services_with_matching_record": [row["service"] for row in matching],
        "services_with_tree_like_file_candidate": [row["service"] for row in tree_candidates],
        "machine_readable_final_tree_recovered": False,
        "exact_final_350_locus_list_recovered": False,
        "bounded_negative_result": (
            "No machine-readable final tree or exact retained-locus list was identified in the "
            "queried public repository APIs at audit time. This is a time-stamped bounded search, "
            "not proof that no later deposit or unindexed institutional file exists."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    parser.add_argument("--checked-at", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    checked_at = args.checked_at or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    client = HttpClient()
    rows = audit_network(client, checked_at)
    rows.append(audit_github(client, checked_at, os.environ.get("GITHUB_TOKEN", "")))
    args.outdir.mkdir(parents=True, exist_ok=True)
    write_csv(args.outdir / "repository_api_audit.csv", rows)
    payload = summary(rows)
    (args.outdir / "repository_api_audit_summary.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"services_attempted={payload['services_attempted']}")
    print(f"services_queried_successfully={payload['services_queried_successfully']}")
    print(
        "services_with_matching_record="
        + "|".join(payload["services_with_matching_record"])
    )
    print(
        "services_with_tree_like_file_candidate="
        + "|".join(payload["services_with_tree_like_file_candidate"])
    )
    print(args.outdir / "repository_api_audit_summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
