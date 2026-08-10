#!/usr/bin/env python3
"""Recover and reconcile Moreyra et al. 2025 sample evidence.

The script deliberately keeps three evidence layers separate:

1. the publisher Supplementary Data 1 sample/voucher table;
2. public NCBI SRA/BioSample run metadata for PRJNA957074;
3. a curated East Asian accepted-name/synonym map.

It does not infer absence from a failed name match. Outputs classify records as
supplement-and-SRA matches, supplement-only, SRA-only, synonym matches, or not
recovered. The DOCX parser uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping, Sequence

DEFAULT_SUPPLEMENT_URL = (
    "https://ars.els-cdn.com/content/image/"
    "1-s2.0-S1055790325000028-mmc1.docx"
)
DEFAULT_NAME_MAP = Path(
    "data/evidence/moreyra2025_east_asia_name_map_2026-08-11.csv"
)
DEFAULT_OUTDIR = Path("data/evidence/generated/moreyra2025")

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}

TABLE_INVENTORY_FIELDS = (
    "table_index",
    "n_rows",
    "n_columns",
    "keyword_score",
    "selected_as_sample_table",
    "preview",
)

FOCAL_AUDIT_FIELDS = (
    "accepted_taxon",
    "aliases",
    "focal_region",
    "priority_class",
    "supplement_match_status",
    "supplement_names_returned",
    "supplement_row_count",
    "ncbi_match_status",
    "ncbi_names_returned",
    "ncbi_biosamples",
    "ncbi_runs",
    "combined_evidence_state",
    "interpretation",
)


def canonical_doi(value: str) -> str:
    value = (value or "").strip().casefold()
    value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value)
    return value.rstrip(" .")


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").replace("\xa0", " ")).strip()


def canonical_taxon(value: str) -> str:
    """Normalize a submitted taxon name conservatively for lookup.

    Rank terms are retained but authorship following a likely binomial/trinomial
    is removed. This is name reconciliation, not taxonomic acceptance.
    """

    value = clean_text(value).replace("_", " ")
    value = re.sub(r"[×x]\s*", "x ", value)
    tokens = value.split()
    if not tokens:
        return ""

    rank_terms = {"subsp.", "ssp.", "var.", "f.", "forma"}
    keep: list[str] = []
    if tokens:
        keep.append(tokens[0])
    if len(tokens) > 1:
        keep.append(tokens[1])
    if len(tokens) > 3 and tokens[2].casefold() in rank_terms:
        keep.extend((tokens[2], tokens[3]))
    elif len(tokens) > 2 and tokens[2].casefold() not in {
        "l.", "dc.", "nakai", "kitam.", "maxim.", "matsum."
    }:
        # Preserve a third epithet only when it looks lower-case and not authorship.
        if tokens[2] and tokens[2][0].islower():
            keep.append(tokens[2])
    return " ".join(keep).casefold().rstrip(".,")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def download(url: str, path: Path, retries: int = 5, timeout: int = 120) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".part")
    headers = {
        "User-Agent": "EAzami-Moreyra2025-evidence-recovery/1.0",
        "Accept": "application/vnd.openxmlformats-officedocument.wordprocessingml.document,*/*",
    }
    for attempt in range(retries):
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                with temp.open("wb") as handle:
                    shutil.copyfileobj(response, handle)
            temp.replace(path)
            return
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            if temp.exists():
                temp.unlink()
            if attempt + 1 == retries:
                raise RuntimeError(f"Unable to download {url}") from exc


def paragraph_text(element: ET.Element) -> str:
    return clean_text("".join(node.text or "" for node in element.findall(".//w:t", NS)))


def extract_docx_tables(path: Path) -> list[list[list[str]]]:
    with zipfile.ZipFile(path) as archive:
        try:
            document = archive.read("word/document.xml")
        except KeyError as exc:
            raise ValueError(f"Not a valid DOCX: {path}") from exc
    root = ET.fromstring(document)
    tables: list[list[list[str]]] = []
    for table in root.findall(".//w:tbl", NS):
        rows: list[list[str]] = []
        for row in table.findall("./w:tr", NS):
            values: list[str] = []
            for cell in row.findall("./w:tc", NS):
                paragraphs = [paragraph_text(p) for p in cell.findall(".//w:p", NS)]
                values.append(clean_text(" ".join(p for p in paragraphs if p)))
            rows.append(values)
        tables.append(rows)
    return tables


SAMPLE_TABLE_TERMS = {
    "sample": 4,
    "taxon": 4,
    "species": 4,
    "biosample": 8,
    "voucher": 7,
    "accession": 5,
    "country": 3,
    "locality": 3,
    "collector": 3,
    "herbarium": 3,
    "bioproject": 4,
}


def table_keyword_score(rows: Sequence[Sequence[str]]) -> int:
    text = " ".join(" ".join(row) for row in rows[:12]).casefold()
    score = sum(weight for term, weight in SAMPLE_TABLE_TERMS.items() if term in text)
    score += min(len(rows) // 25, 12)
    return score


def select_sample_table(tables: Sequence[Sequence[Sequence[str]]]) -> int:
    if not tables:
        raise ValueError("Supplement contains no tables")
    scores = [
        (table_keyword_score(rows), len(rows), max((len(r) for r in rows), default=0), i)
        for i, rows in enumerate(tables)
    ]
    return max(scores)[3]


def normalize_header(value: str, fallback: str) -> str:
    value = clean_text(value).casefold()
    value = re.sub(r"[^a-z0-9]+", "_", value).strip("_")
    return value or fallback


def detect_header_row(rows: Sequence[Sequence[str]]) -> int:
    best = (float("-inf"), 0)
    terms = tuple(SAMPLE_TABLE_TERMS)
    for i, row in enumerate(rows[:15]):
        text = " ".join(row).casefold()
        nonempty = sum(bool(clean_text(cell)) for cell in row)
        unique = len({clean_text(cell).casefold() for cell in row if clean_text(cell)})
        term_hits = sum(term in text for term in terms)
        score = term_hits * 8 + nonempty + unique * 0.25
        if score > best[0]:
            best = (score, i)
    return best[1]


def normalized_table(rows: Sequence[Sequence[str]]) -> list[dict[str, str]]:
    if not rows:
        return []
    header_index = detect_header_row(rows)
    header = list(rows[header_index])
    width = max(max((len(row) for row in rows), default=0), len(header))
    header += [""] * (width - len(header))

    names: list[str] = []
    counts: Counter[str] = Counter()
    for i, value in enumerate(header, start=1):
        base = normalize_header(value, f"column_{i}")
        counts[base] += 1
        names.append(base if counts[base] == 1 else f"{base}_{counts[base]}")

    output: list[dict[str, str]] = []
    for raw in rows[header_index + 1 :]:
        values = list(raw) + [""] * (width - len(raw))
        row = {name: clean_text(values[i]) for i, name in enumerate(names)}
        if any(row.values()):
            output.append(row)
    return output


def first_matching_field(row: Mapping[str, str], patterns: Sequence[str]) -> str:
    for key, value in row.items():
        if any(pattern in key for pattern in patterns) and clean_text(value):
            return clean_text(value)
    return ""


TAXON_RE = re.compile(
    r"\b(?:Cirsium|Carduus|Lophiolepis|Afrocirsium|Afrocarduus)\s+"
    r"[A-Za-z-]+(?:\s+(?:subsp\.|ssp\.|var\.|f\.)\s+[A-Za-z-]+)?",
    flags=re.IGNORECASE,
)


def extract_taxon(row: Mapping[str, str]) -> str:
    direct = first_matching_field(
        row,
        ("taxon", "species", "scientific_name", "accepted_name"),
    )
    match = TAXON_RE.search(direct)
    if match:
        return clean_text(match.group(0))
    text = " | ".join(row.values())
    match = TAXON_RE.search(text)
    return clean_text(match.group(0)) if match else direct


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return [
            {key: clean_text(value or "") for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


def write_csv(path: Path, rows: Iterable[Mapping[str, object]], fields: Sequence[str] | None = None) -> None:
    rows = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        fields = tuple(rows[0]) if rows else ()
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def read_name_map(path: Path) -> list[dict[str, str]]:
    rows = read_csv(path)
    required = {"accepted_taxon", "aliases", "focal_region", "priority_class"}
    if rows and required - set(rows[0]):
        raise ValueError(f"Name map missing fields: {sorted(required - set(rows[0]))}")
    return rows


def name_lookup(name_map: Sequence[Mapping[str, str]]) -> dict[str, tuple[str, str]]:
    lookup: dict[str, tuple[str, str]] = {}
    for row in name_map:
        accepted = row["accepted_taxon"]
        values = [accepted] + [part.strip() for part in row.get("aliases", "").split(";")]
        for value in values:
            canonical = canonical_taxon(value)
            if canonical:
                lookup[canonical] = (accepted, "accepted" if value == accepted else "alias")
    return lookup


def group_ncbi(rows: Sequence[Mapping[str, str]]) -> dict[str, list[Mapping[str, str]]]:
    grouped: dict[str, list[Mapping[str, str]]] = defaultdict(list)
    for row in rows:
        taxon = row.get("ScientificName") or row.get("scientific_name") or ""
        grouped[canonical_taxon(taxon)].append(row)
    return grouped


def combine_state(supplement_n: int, ncbi_n: int, used_alias: bool) -> tuple[str, str]:
    if supplement_n and ncbi_n:
        state = "supplement_and_public_sra_verified"
        text = "Published sample evidence and exact/alias-linked public SRA metadata were both recovered."
    elif supplement_n:
        state = "supplement_only_public_run_not_matched"
        text = "Published supplement evidence was recovered, but no accepted/alias name match was found in current project runinfo."
    elif ncbi_n:
        state = "public_sra_only_supplement_tip_not_matched"
        text = "Public project metadata were recovered, but no accepted/alias match was found in the normalized supplement table."
    else:
        state = "not_recovered_after_current_name_audit"
        text = "No current accepted/alias match was recovered; this is not proof of biological absence from the published tree."
    if used_alias:
        state += "_via_alias"
        text += " At least one match used a curated synonym or alternative submitted name."
    return state, text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--supplement-url", default=DEFAULT_SUPPLEMENT_URL)
    parser.add_argument("--supplement", type=Path)
    parser.add_argument("--runinfo", type=Path)
    parser.add_argument("--name-map", type=Path, default=DEFAULT_NAME_MAP)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    supplement = args.supplement or (args.outdir / "Moreyra2025_Supplementary_Data_1.docx")
    if args.supplement is None and (args.force or not supplement.exists()):
        download(args.supplement_url, supplement)

    tables = extract_docx_tables(supplement)
    selected = select_sample_table(tables)
    inventory = []
    for i, rows in enumerate(tables):
        width = max((len(row) for row in rows), default=0)
        preview = " || ".join(" | ".join(row) for row in rows[:3])[:1500]
        inventory.append(
            {
                "table_index": i + 1,
                "n_rows": len(rows),
                "n_columns": width,
                "keyword_score": table_keyword_score(rows),
                "selected_as_sample_table": "yes" if i == selected else "no",
                "preview": preview,
            }
        )
        raw_fields = [f"column_{j + 1}" for j in range(width)]
        raw_rows = [
            {raw_fields[j]: clean_text((list(row) + [""] * (width - len(row)))[j]) for j in range(width)}
            for row in rows
        ]
        write_csv(args.outdir / f"supplement_table_{i + 1:03d}_raw.csv", raw_rows, raw_fields)
    write_csv(args.outdir / "supplement_table_inventory.csv", inventory, TABLE_INVENTORY_FIELDS)

    samples = normalized_table(tables[selected])
    enriched_samples: list[dict[str, str]] = []
    for row in samples:
        taxon = extract_taxon(row)
        enriched = dict(row)
        enriched["recovered_taxon_name"] = taxon
        enriched["canonical_taxon_name"] = canonical_taxon(taxon)
        enriched["recovered_biosample"] = first_matching_field(row, ("biosample",))
        enriched["recovered_voucher"] = first_matching_field(row, ("voucher",))
        enriched["recovered_locality"] = first_matching_field(
            row, ("country", "locality", "location", "origin", "region")
        )
        enriched_samples.append(enriched)
    sample_fields = tuple(enriched_samples[0]) if enriched_samples else ()
    write_csv(args.outdir / "supplement_sample_table_normalized.csv", enriched_samples, sample_fields)

    name_map = read_name_map(args.name_map)
    lookup = name_lookup(name_map)
    supplement_by_accepted: dict[str, list[dict[str, str]]] = defaultdict(list)
    supplement_alias_used: dict[str, bool] = defaultdict(bool)
    for row in enriched_samples:
        match = lookup.get(row["canonical_taxon_name"])
        if match:
            accepted, match_type = match
            supplement_by_accepted[accepted].append(row)
            supplement_alias_used[accepted] |= match_type == "alias"

    ncbi_rows = read_csv(args.runinfo) if args.runinfo else []
    ncbi_grouped = group_ncbi(ncbi_rows)
    ncbi_by_accepted: dict[str, list[Mapping[str, str]]] = defaultdict(list)
    ncbi_alias_used: dict[str, bool] = defaultdict(bool)
    for canonical, rows in ncbi_grouped.items():
        match = lookup.get(canonical)
        if match:
            accepted, match_type = match
            ncbi_by_accepted[accepted].extend(rows)
            ncbi_alias_used[accepted] |= match_type == "alias"

    audits: list[dict[str, object]] = []
    for mapping in name_map:
        accepted = mapping["accepted_taxon"]
        supp = supplement_by_accepted.get(accepted, [])
        ncbi = ncbi_by_accepted.get(accepted, [])
        used_alias = supplement_alias_used[accepted] or ncbi_alias_used[accepted]
        state, interpretation = combine_state(len(supp), len(ncbi), used_alias)
        audits.append(
            {
                "accepted_taxon": accepted,
                "aliases": mapping["aliases"],
                "focal_region": mapping["focal_region"],
                "priority_class": mapping["priority_class"],
                "supplement_match_status": "matched" if supp else "not_recovered",
                "supplement_names_returned": "|".join(sorted({row["recovered_taxon_name"] for row in supp})),
                "supplement_row_count": len(supp),
                "ncbi_match_status": "matched" if ncbi else "not_recovered",
                "ncbi_names_returned": "|".join(sorted({row.get("ScientificName", "") for row in ncbi})),
                "ncbi_biosamples": "|".join(sorted({row.get("BioSample", "") for row in ncbi if row.get("BioSample")})),
                "ncbi_runs": "|".join(sorted({row.get("Run", "") for row in ncbi if row.get("Run")})),
                "combined_evidence_state": state,
                "interpretation": interpretation,
            }
        )
    write_csv(args.outdir / "east_asia_focal_taxon_audit.csv", audits, FOCAL_AUDIT_FIELDS)

    east_asia_samples: list[dict[str, str]] = []
    for accepted, rows in supplement_by_accepted.items():
        mapping = next(row for row in name_map if row["accepted_taxon"] == accepted)
        for row in rows:
            item = {
                "accepted_taxon": accepted,
                "focal_region": mapping["focal_region"],
                "priority_class": mapping["priority_class"],
                **row,
            }
            east_asia_samples.append(item)
    east_fields = tuple(east_asia_samples[0]) if east_asia_samples else ()
    write_csv(args.outdir / "east_asia_supplement_samples.csv", east_asia_samples, east_fields)

    summary = {
        "supplement_url": args.supplement_url,
        "supplement_filename": supplement.name,
        "supplement_size_bytes": supplement.stat().st_size,
        "supplement_sha256": sha256_file(supplement),
        "table_count": len(tables),
        "selected_sample_table_index": selected + 1,
        "normalized_sample_rows": len(enriched_samples),
        "rows_with_recovered_taxon": sum(bool(row["canonical_taxon_name"]) for row in enriched_samples),
        "name_map_records": len(name_map),
        "focal_supplement_matches": sum(bool(supplement_by_accepted.get(row["accepted_taxon"])) for row in name_map),
        "focal_ncbi_matches": sum(bool(ncbi_by_accepted.get(row["accepted_taxon"])) for row in name_map),
        "ncbi_run_rows": len(ncbi_rows),
        "state_counts": Counter(row["combined_evidence_state"] for row in audits),
    }
    (args.outdir / "recovery_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, default=dict) + "\n",
        encoding="utf-8",
    )

    report = [
        "# Moreyra et al. 2025 public-evidence recovery",
        "",
        f"- Supplement SHA256: `{summary['supplement_sha256']}`",
        f"- Supplement size: {summary['supplement_size_bytes']:,} bytes",
        f"- DOCX tables: {summary['table_count']}",
        f"- Selected sample-table index: {summary['selected_sample_table_index']}",
        f"- Normalized sample rows: {summary['normalized_sample_rows']}",
        f"- Public SRA run rows: {summary['ncbi_run_rows']}",
        f"- Focal name-map records: {summary['name_map_records']}",
        f"- Focal supplement matches: {summary['focal_supplement_matches']}",
        f"- Focal NCBI matches: {summary['focal_ncbi_matches']}",
        "",
        "A non-match means only that the current accepted-name and alias audit did not recover a record.",
        "It is not evidence that the taxon is biologically absent from the published tree.",
    ]
    (args.outdir / "recovery_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False, default=dict))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
