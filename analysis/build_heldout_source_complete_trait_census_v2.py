#!/usr/bin/env python3
"""Build the preregistered source-complete East-Asian Cirsium trait census v2.

IMPORTANT: This script retrieves botanical/taxonomic source text only.
It performs no GBIF occurrence query and no environmental extraction.

China lane:
- complete lower-taxon list linked from the Flora of China Cirsium genus page;
- fetch every linked taxon page;
- code only explicit capitulum orientation and explicit stickiness wording.

Korea lane:
- enumerate every Cirsium concept printed in the selected NIBR national species-list page;
- preserve concepts even when no trait description is available in that lane;
- merge only pre-existing explicit NIBR trait evidence already frozen in v1.

Discovery-overlap exclusion is conservative at binomial level.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

FOC_GENUS = "https://efloras.org/florataxon.aspx?flora_id=2&taxon_id=107139"
NIBR_LIST = "https://www.nibr.go.kr/aiibook/access/ecatalogt.jsp?Dir=20&callmode=admin&catimage=&eclang=ko&start=161&um=s"
UA = "EAzami-source-complete-trait-census-v2/1.0"

DOWN = re.compile(r"\b(nodding|pendulous|pendent|hanging|downward(?:[- ]facing)?)\b", re.I)
UP = re.compile(r"\b(erect|upright|upward(?:[- ]facing)?)\b", re.I)
AMBIG = re.compile(
    r"\b(erect\s+or\s+nodding|nodding\s+(?:or|to)\s+erect|erect\s+to\s+nodding|"
    r"rarely\s+nodding|sometimes\s+nodding|[±+-]\s*nodding)\b", re.I
)
NONSTICKY = re.compile(r"\b(non[- ]?sticky|non[- ]?glutinous|not\s+(?:sticky|glutinous|adhesive))\b", re.I)
STICKY = re.compile(r"\b(sticky|glutinous|adhesive)\b", re.I)
CIRSIUM_NAME = re.compile(r"\bCirsium\s+[a-z][a-z-]+(?:\s+(?:var\.|subsp\.|ssp\.|f\.)\s+[a-z][a-z-]+)?", re.I)


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def binomial(name: str) -> str:
    parts = clean(name).split()
    return " ".join(parts[:2]).casefold() if len(parts) >= 2 else clean(name).casefold()


def sentence_candidates(text: str) -> list[str]:
    text = clean(text)
    parts = re.split(r"(?<=[.;])\s+|\s+(?=[A-Z][A-Za-z -]{1,25}:)", text)
    out = []
    for p in parts:
        if re.search(r"capitul|involucr|phyllar|head", p, re.I):
            out.append(clean(p))
    return out


def code_orientation(text: str) -> tuple[str, str]:
    relevant = " ".join(sentence_candidates(text))
    if AMBIG.search(relevant):
        return "ambiguous", clean(relevant)
    d = bool(DOWN.search(relevant))
    u = bool(UP.search(relevant))
    if d and u:
        return "ambiguous", clean(relevant)
    if d:
        return "downward_or_nodding", clean(relevant)
    if u:
        return "upward_or_erect", clean(relevant)
    return "unknown", clean(relevant)


def code_stickiness(text: str) -> tuple[str, str]:
    relevant = " ".join(sentence_candidates(text))
    if NONSTICKY.search(relevant):
        return "nonsticky", clean(relevant)
    if STICKY.search(relevant):
        return "sticky", clean(relevant)
    # resinous/glandular wording alone is intentionally ignored.
    return "unknown", clean(relevant)


def get(session: requests.Session, url: str) -> str:
    # eFloras currently presents a certificate chain that GitHub-hosted runners
    # reject as self-signed. This is a transport-only exception: the exact URL
    # and returned source text are still hashed and recorded; no scientific
    # inclusion/coding rule changes.
    verify = False if "efloras.org" in url else True
    r = session.get(url, timeout=90, verify=verify)
    r.raise_for_status()
    return r.text


def parse_foc_links(html: str) -> list[tuple[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    found = {}
    for a in soup.find_all("a", href=True):
        href = a["href"]
        txt = clean(a.get_text(" ", strip=True))
        if "florataxon.aspx" not in href or "flora_id=2" not in href or "taxon_id=" not in href:
            continue
        if not re.search(r"(?:^|\s)C\.\s*[a-z]", txt, re.I) and "Cirsium " not in txt:
            continue
        url = urljoin(FOC_GENUS, href)
        if "taxon_id=107139" in url:
            continue
        found[url] = txt
    return sorted([(u, t) for u, t in found.items()])


def page_name(soup: BeautifulSoup, fallback: str) -> str:
    title = clean(soup.title.get_text(" ", strip=True) if soup.title else "")
    m = re.search(r"\b(Cirsium\s+[a-z][a-z-]+(?:\s+(?:var\.|subsp\.|ssp\.|f\.)\s+[a-z][a-z-]+)?)\b", title, re.I)
    if m:
        return clean(m.group(1))
    txt = clean(soup.get_text(" ", strip=True))
    m = CIRSIUM_NAME.search(txt)
    if m:
        return clean(m.group(0))
    # fallback link text often contains C. epithet
    m = re.search(r"C\.\s*([a-z][a-z-]+)", fallback, re.I)
    if m:
        return "Cirsium " + m.group(1).lower()
    return fallback


def read_discovery_bins(paths: list[Path]) -> set[str]:
    out=set()
    for p in paths:
        if not p.exists():
            continue
        with p.open(encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                for k in ("paper_taxon_concept","accepted_taxon","nmns_taxon_concept"):
                    v=clean(r.get(k,""))
                    if v.startswith("Cirsium "):
                        out.add(binomial(v))
    return out


def parse_nibr_names(html: str) -> list[str]:
    txt = clean(BeautifulSoup(html, "html.parser").get_text(" ", strip=True))
    # The selected page is a taxonomic checklist. Keep unique Cirsium names in printed order.
    names=[]
    for m in CIRSIUM_NAME.finditer(txt):
        n=clean(m.group(0))
        if n not in names:
            names.append(n)
    return names


def load_v1_explicit(path: Path) -> dict[str, dict]:
    out={}
    if not path.exists():
        return out
    with path.open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if "Korean" not in r.get("provenance_frame","") and "Korea" not in r.get("provenance_frame",""):
                continue
            out[binomial(r["analysis_taxon"])] = r
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--contract", type=Path, required=True)
    ap.add_argument("--v1-traits", type=Path, required=True)
    ap.add_argument("--discovery", type=Path, action="append", default=[])
    ap.add_argument("--out-csv", type=Path, required=True)
    ap.add_argument("--out-json", type=Path, required=True)
    args=ap.parse_args()

    contract=json.loads(args.contract.read_text(encoding="utf-8"))
    assert contract["status"]=="FROZEN_BEFORE_V2_TRAIT_CENSUS_AND_ENVIRONMENT"
    discovery_bins=read_discovery_bins(args.discovery)
    v1k=load_v1_explicit(args.v1_traits)

    s=requests.Session()
    s.headers.update({"User-Agent":UA})
    rows=[]

    genus_html=get(s,FOC_GENUS)
    links=parse_foc_links(genus_html)
    for i,(url,label) in enumerate(links,1):
        html=get(s,url)
        soup=BeautifulSoup(html,"html.parser")
        name=page_name(soup,label)
        text=clean(soup.get_text(" ", strip=True))
        o,orelevant=code_orientation(text)
        k,krelevant=code_stickiness(text)
        overlap=binomial(name) in discovery_bins
        rows.append({
            "source_lane":"Flora_of_China",
            "analysis_taxon":name,
            "source_label":label,
            "source_url":url,
            "source_sha256":sha(text),
            "orientation_state":o,
            "stickiness_state":k,
            "relevant_trait_text":orelevant if orelevant else krelevant,
            "discovery_overlap_binomial":str(overlap).lower(),
            "eligible_for_heldout":str(not overlap).lower(),
            "coding_note":"explicit source text only; resinous gland alone ignored",
        })
        print("FOC",i,len(links),name,o,k,"overlap",overlap,flush=True)
        time.sleep(.03)

    nibr_html=get(s,NIBR_LIST)
    nibr_names=parse_nibr_names(nibr_html)
    nibr_text=clean(BeautifulSoup(nibr_html,"html.parser").get_text(" ",strip=True))
    for name in nibr_names:
        overlap=binomial(name) in discovery_bins
        old=v1k.get(binomial(name))
        o="unknown"
        k="unknown"
        note="selected NIBR national checklist enumerates concept but supplies no explicit trait state in this lane"
        src=NIBR_LIST
        rel=""
        if old and old.get("stickiness_state") in {"sticky","nonsticky"}:
            k=old["stickiness_state"]
            src=old.get("source_url") or src
            note="reused explicit NIBR trait evidence frozen before v2; no ecology used"
            rel=old.get("source_basis","") or old.get("claim_boundary","")
        if old and old.get("orientation_state") in {"downward_or_nodding","upward_or_erect"}:
            o=old["orientation_state"]
            src=old.get("source_url") or src
            note="reused explicit Korean trait evidence frozen before v2; no ecology used"
            rel=old.get("source_basis","") or old.get("claim_boundary","")
        rows.append({
            "source_lane":"NIBR_national_species_list",
            "analysis_taxon":name,
            "source_label":name,
            "source_url":src,
            "source_sha256":sha(nibr_text),
            "orientation_state":o,
            "stickiness_state":k,
            "relevant_trait_text":rel,
            "discovery_overlap_binomial":str(overlap).lower(),
            "eligible_for_heldout":str(not overlap).lower(),
            "coding_note":note,
        })

    # Deduplicate exact analysis name within lane only; cross-lane overlap is retained as provenance.
    ded=[]
    seen=set()
    for r in rows:
        key=(r["source_lane"],r["analysis_taxon"].casefold())
        if key not in seen:
            seen.add(key); ded.append(r)
    rows=ded

    args.out_csv.parent.mkdir(parents=True,exist_ok=True)
    with args.out_csv.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

    foc=[r for r in rows if r["source_lane"]=="Flora_of_China"]
    kor=[r for r in rows if r["source_lane"]=="NIBR_national_species_list"]
    elig=[r for r in rows if r["eligible_for_heldout"]=="true"]
    summary={
        "version":"heldout_east_asia_source_complete_trait_census_v2",
        "status_date":"2026-09-24",
        "environment_opened":False,
        "occurrence_opened":False,
        "source_counts":{
            "foc_linked_taxa":len(foc),
            "nibr_printed_cirsium_concepts":len(kor),
            "eligible_rows_total":len(elig),
        },
        "eligible_orientation_counts":{
            "downward_or_nodding":sum(r["orientation_state"]=="downward_or_nodding" for r in elig),
            "upward_or_erect":sum(r["orientation_state"]=="upward_or_erect" for r in elig),
            "ambiguous":sum(r["orientation_state"]=="ambiguous" for r in elig),
            "unknown":sum(r["orientation_state"]=="unknown" for r in elig),
        },
        "eligible_stickiness_counts":{
            "sticky":sum(r["stickiness_state"]=="sticky" for r in elig),
            "nonsticky":sum(r["stickiness_state"]=="nonsticky" for r in elig),
            "unknown":sum(r["stickiness_state"]=="unknown" for r in elig),
        },
        "foc_expected_taxa":46,
        "foc_completeness_pass":len(foc)==46,
        "claim_boundary":"Trait-source census only. No occurrence or environmental outcome has been queried.",
    }
    args.out_json.write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    if len(foc)!=46:
        raise SystemExit(f"FAIL: Flora of China genus page yielded {len(foc)} linked taxa, expected 46")


if __name__=="__main__":
    main()
