#!/usr/bin/env python3
"""Conservative Japan-38 cytotype audit using provenance-frozen NMNS detail URLs.

No Kahaku page number is guessed. URLs come only from the existing EAzami
flower-colour atlas. Only exact accepted-taxon matches are auto-admitted.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,re,time,urllib.request
from collections import Counter
from pathlib import Path
from bs4 import BeautifulSoup


def norm(x): return re.sub(r"\s+"," ",(x or "")).strip()
def concept(x):
    x=norm(x); m=re.match(r"(Cirsium\s+[A-Za-z-]+(?:\s+(?:var\.|subsp\.|f\.)\s+[A-Za-z-]+)?)",x)
    return m.group(1) if m else x

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"EAzami-public-evidence-audit/1.0"})
    with urllib.request.urlopen(req,timeout=60) as r: raw=r.read()
    return raw.decode("utf-8",errors="replace")

def detail(url):
    page=fetch(url); text=norm(BeautifulSoup(page,"html.parser").get_text(" ",strip=True))
    snippets=[]
    for pat in [r"染色体(?:数)?[^。]{0,160}",r"2n\s*[=＝][^。]{0,100}"]:
        for m in re.finditer(pat,text,re.I):
            s=norm(m.group(0))
            if s and s not in snippets: snippets.append(s)
    ctext=" | ".join(snippets)
    parsed=[]
    for x,n in sorted(set(re.findall(r"2n\s*[=＝]\s*(?:(\d+)x\s*[=＝]\s*)?(\d+)",ctext,re.I))):
        parsed.append((int(x) if x else None,int(n)))
    return ctext,parsed,len(text),hashlib.sha256(page.encode()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--japan38",default="data/evidence/moreyra2025_japan_38_membership_audit_2026-08-10.csv")
    ap.add_argument("--atlas",default="data/evidence/cirsium_flower_colour_atlas_v0_2.csv")
    ap.add_argument("--output",required=True); ap.add_argument("--summary",required=True)
    a=ap.parse_args()
    with Path(a.japan38).open(encoding="utf-8-sig",newline="") as h: jp=list(csv.DictReader(h))
    if len(jp)!=38: raise ValueError(f"Japan-38 drift: {len(jp)}")
    urlmap={}
    with Path(a.atlas).open(encoding="utf-8-sig",newline="") as h:
        for r in csv.DictReader(h):
            name=concept(r.get("accepted_taxon")); url=(r.get("source_url") or "").strip()
            if name and "kahaku.go.jp/research/db/botany/azami/detail.html?no=" in url:
                urlmap.setdefault(name,{})[url]=r.get("record_id","")
    cache={}; out=[]
    for r in jp:
        name=concept(r["paper_taxon_concept"]); hits=urlmap.get(name,{})
        if len(hits)!=1:
            out.append({"paper_japan_member_id":r["paper_japan_member_id"],"paper_taxon_concept":r["paper_taxon_concept"],"normalized_concept":name,"kahaku_url":"","atlas_record_id":"","chromosome_text":"","chromosome_2n_values":"","ploidy_x_values":"","admission_status":"no_unique_exact_atlas_url","visible_text_chars":"","page_text_sha256":""}); continue
        url=next(iter(hits)); rid=hits[url]
        if url not in cache: cache[url]=detail(url); time.sleep(.1)
        ctext,counts,nchars,sha=cache[url]
        out.append({"paper_japan_member_id":r["paper_japan_member_id"],"paper_taxon_concept":r["paper_taxon_concept"],"normalized_concept":name,"kahaku_url":url,"atlas_record_id":rid,"chromosome_text":ctext,"chromosome_2n_values":"|".join(str(n) for _,n in counts),"ploidy_x_values":"|".join(str(x) if x else "" for x,_ in counts),"admission_status":"source_backed_exact_name" if ctext else "exact_url_no_chromosome_text_recovered","visible_text_chars":nchars,"page_text_sha256":sha})
    fields=list(out[0])
    with Path(a.output).open("w",encoding="utf-8",newline="") as h:
        w=csv.DictWriter(h,fieldnames=fields,lineterminator="\n"); w.writeheader(); w.writerows(out)
    admitted=[r for r in out if r["admission_status"]=="source_backed_exact_name"]
    vals=[]
    for r in admitted:
        vals += [int(x) for x in r["chromosome_2n_values"].split("|") if x]
    summary={"contract_version":"moreyra_japan38_kahaku_cytotype_audit_v2","japan38_concepts":38,"concepts_with_unique_exact_atlas_kahaku_url":sum(bool(r["kahaku_url"]) for r in out),"exact_name_with_chromosome_evidence":len(admitted),"coverage_fraction":len(admitted)/38,"admitted_2n_value_counts":{str(k):v for k,v in sorted(Counter(vals).items())},"notable_focal_rows":{r["normalized_concept"]:{"chromosome_text":r["chromosome_text"],"admission_status":r["admission_status"],"url":r["kahaku_url"]} for r in out if any(x in r["normalized_concept"] for x in ["dipsacolepis","lineare","aomorense","sieboldii","nipponicum"])},"interpretation_rule":"Only exact Japan-38 taxon concepts with a provenance-frozen Kahaku detail URL and explicit chromosome text are admitted. This is taxon-level cytotype context, not the exact sequenced individual's cytotype, and it is not evidence that ploidy caused radiation success.","next_gate":"If chromosome text is not exposed in the current detail-page HTML, retain the URL provenance and recover cytotype from an independently citable chromosome source rather than inferring it. Compare cytotype transitions with radiation only after the accepted 294/296 topology is available."}
    Path(a.summary).write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8"); print(json.dumps(summary,indent=2,ensure_ascii=False))
if __name__=="__main__": main()
