#!/usr/bin/env python3
"""Join the Moreyra Japan-38 concepts to the NMNS Japanese Cirsium database.

Only exact scientific-name matches are admitted automatically. A base-binomial
match is retained as a candidate requiring review when the paper concept is
infraspecific or the exact string is absent. Chromosome text is extracted from
the resolved official detail page without imputing ploidy from taxonomic group.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import re
import time
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup

LIST_URL = "https://www.kahaku.go.jp/research/db/botany/azami/list.html?word=all"
BASE = "https://www.kahaku.go.jp"


def get(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "EAzami-public-evidence-audit/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", errors="replace")


def normalize_space(x: str) -> str:
    return re.sub(r"\s+", " ", x).strip()


def concept_name(x: str) -> str:
    x = normalize_space(x)
    m = re.match(r"(Cirsium\s+[A-Za-z-]+(?:\s+(?:var\.|subsp\.|f\.)\s+[A-Za-z-]+)?)", x)
    return m.group(1) if m else x


def base_binomial(x: str) -> str:
    m = re.match(r"(Cirsium\s+[A-Za-z-]+)", x)
    return m.group(1) if m else x


def build_index(page: str):
    soup = BeautifulSoup(page, "html.parser")
    index = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "detail.html?no=" not in href:
            continue
        container = a
        for _ in range(4):
            if container.parent is None:
                break
            container = container.parent
        text = normalize_space(container.get_text(" ", strip=True))
        names = sorted(set(re.findall(r"Cirsium\s+[A-Za-z-]+(?:\s+(?:var\.|subsp\.|f\.)\s+[A-Za-z-]+)?", text)))
        url = href if href.startswith("http") else BASE + (href if href.startswith("/") else "/research/db/botany/azami/" + href)
        for name in names:
            index.append({"name": name, "url": url, "context": text[:1000]})
    uniq = {}
    for r in index:
        uniq[(r["name"], r["url"])] = r
    return list(uniq.values())


def extract_detail(url: str):
    page = get(url)
    soup = BeautifulSoup(page, "html.parser")
    text = normalize_space(soup.get_text(" ", strip=True))
    sci = None
    m = re.search(r"種名\s+(Cirsium\s+[A-Za-z-]+)", text)
    if m:
        sci = m.group(1)
    var = None
    m = re.search(r"変種名\s+([A-Za-z-]+)", text)
    if m and m.group(1) not in {"キャッチフレーズ", "基準産地"}:
        var = m.group(1)
    chrom_snips = []
    for m in re.finditer(r"(?:染色体数[^。]{0,80}|2n\s*[=＝][^。]{0,40})", text, flags=re.I):
        s = normalize_space(m.group(0))
        if s not in chrom_snips:
            chrom_snips.append(s)
    numbers = sorted(set(re.findall(r"2n\s*[=＝]\s*(?:(\d+)x\s*[=＝]\s*)?(\d+)", " | ".join(chrom_snips), flags=re.I)))
    parsed = []
    for x,n in numbers:
        parsed.append({"x_multiplier": int(x) if x else None, "chromosome_2n": int(n)})
    return {
        "page_scientific_name": sci,
        "page_variety_name": var,
        "chromosome_text": " | ".join(chrom_snips),
        "parsed_counts": parsed,
        "page_text_sha256": __import__('hashlib').sha256(page.encode()).hexdigest(),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--japan38", default="data/evidence/moreyra2025_japan_38_membership_audit_2026-08-10.csv")
    ap.add_argument("--output", required=True)
    ap.add_argument("--summary", required=True)
    args = ap.parse_args()

    with Path(args.japan38).open(encoding="utf-8-sig", newline="") as h:
        rows = list(csv.DictReader(h))
    if len(rows) != 38:
        raise ValueError(f"Japan-38 membership drift: {len(rows)}")

    index = build_index(get(LIST_URL))
    exact_map = {}
    binom_map = {}
    for r in index:
        exact_map.setdefault(r["name"], []).append(r)
        binom_map.setdefault(base_binomial(r["name"]), []).append(r)

    cache = {}
    out = []
    for row in rows:
        c = concept_name(row["paper_taxon_concept"])
        b = base_binomial(c)
        exact = exact_map.get(c, [])
        candidates = exact
        match = "exact_list_name" if len(exact) == 1 else ""
        if not candidates:
            base = binom_map.get(b, [])
            urls = {x["url"] for x in base}
            if len(urls) == 1:
                candidates = [next(x for x in base if x["url"] in urls)]
                match = "single_base_binomial_candidate_requires_review"
        if len({x["url"] for x in candidates}) != 1:
            out.append({
                "paper_japan_member_id": row["paper_japan_member_id"],
                "paper_taxon_concept": row["paper_taxon_concept"],
                "normalized_concept": c,
                "match_status": "unresolved_or_multiple",
                "kahaku_url": "",
                "page_scientific_name": "",
                "page_variety_name": "",
                "chromosome_text": "",
                "chromosome_2n_values": "",
                "ploidy_x_values": "",
                "admission_status": "not_admitted",
            })
            continue
        rec = candidates[0]
        url = rec["url"]
        if url not in cache:
            cache[url] = extract_detail(url)
            time.sleep(0.15)
        d = cache[url]
        counts = d["parsed_counts"]
        admitted = match == "exact_list_name" and bool(d["chromosome_text"])
        out.append({
            "paper_japan_member_id": row["paper_japan_member_id"],
            "paper_taxon_concept": row["paper_taxon_concept"],
            "normalized_concept": c,
            "match_status": match or "candidate",
            "kahaku_url": url,
            "page_scientific_name": d["page_scientific_name"] or "",
            "page_variety_name": d["page_variety_name"] or "",
            "chromosome_text": d["chromosome_text"],
            "chromosome_2n_values": "|".join(str(x["chromosome_2n"]) for x in counts),
            "ploidy_x_values": "|".join(str(x["x_multiplier"]) if x["x_multiplier"] else "" for x in counts),
            "page_text_sha256": d["page_text_sha256"],
            "admission_status": "source_backed_exact_name" if admitted else "review_required",
        })

    fields = sorted({k for r in out for k in r})
    preferred = [
        "paper_japan_member_id","paper_taxon_concept","normalized_concept","match_status","kahaku_url",
        "page_scientific_name","page_variety_name","chromosome_text","chromosome_2n_values","ploidy_x_values",
        "admission_status","page_text_sha256"
    ]
    fields = preferred + [x for x in fields if x not in preferred]
    with Path(args.output).open("w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=fields, lineterminator="\n")
        w.writeheader(); w.writerows(out)

    admitted = [r for r in out if r["admission_status"] == "source_backed_exact_name"]
    values = []
    for r in admitted:
        for x in r["chromosome_2n_values"].split("|"):
            if x:
                values.append(int(x))
    from collections import Counter
    summary = {
        "contract_version": "moreyra_japan38_kahaku_cytotype_audit_v1",
        "japan38_concepts": len(out),
        "exact_name_with_chromosome_evidence": len(admitted),
        "coverage_fraction": len(admitted)/len(out),
        "review_or_unresolved": len(out)-len(admitted),
        "admitted_2n_value_counts": dict(sorted(Counter(values).items())),
        "notable_focal_rows": {
            r["normalized_concept"]: {
                "chromosome_text": r["chromosome_text"],
                "admission_status": r["admission_status"],
                "url": r["kahaku_url"],
            }
            for r in out if any(x in r["normalized_concept"] for x in ["dipsacolepis","lineare","aomorense","sieboldii","nipponicum"])
        },
        "interpretation_rule": "Only exact scientific-name joins with explicit chromosome text are admitted automatically. The audit describes cytotype coverage among sampled taxon concepts; it does not assign cytotype to the exact sequenced individual unless voucher-level evidence exists, and it does not infer radiation causation from ploidy.",
        "next_gate": "Manually review unmatched/infraspecific concepts, then compare cytotype-transition heterogeneity within the dominant Japanese radiation versus lineare/dipsacolepis only after the accepted topology identifies membership and branch structure.",
    }
    Path(args.summary).write_text(json.dumps(summary, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
