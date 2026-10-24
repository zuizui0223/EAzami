#!/usr/bin/env python3
"""Extract paired-voucher nuclear ITS and ETS accession table from Slotta et al. 2012.

Source: https://pmc.ncbi.nlm.nih.gov/articles/PMC4844267/
Publisher-version publication DOI: 10.3390/plants1020061
Primary structured full text: Europe PMC PMC4844267/fullTextXML.

This freezes source specimen IDs BEFORE tree inference. No taxonomy-based
synonym inheritance, no genes from unrelated specimens, no geography forced.
"""
from __future__ import annotations

import argparse,csv,hashlib,json,re,urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

URL="https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4844267/fullTextXML"
ACCESSION=re.compile(r"\b(?:[A-Z]{1,3}\d{5,8})(?:\.\d+)?\b")

def fetch():
    r=urllib.request.Request(URL,headers={"User-Agent":"EAzami-nuclear-marker-provenance/1.0"})
    with urllib.request.urlopen(r,timeout=50) as response:
        return response.read()

def text(node):
    return " ".join("".join(node.itertext()).split())

def extract(xmlbytes):
    root=ET.fromstring(xmlbytes)
    hits=[]
    for table in root.findall(".//table-wrap"):
        heading=" ".join(text(e) for e in table.findall("./label")+table.findall("./caption"))
        rows=table.findall(".//tr")
        header=" ".join(text(x) for x in rows[0].findall("./th")) if rows else ""
        if "ITS" not in (heading+" "+header) or "ETS" not in (heading+" "+header):
            continue
        for tr in rows[1:]:
            vals=[text(v) for v in tr if v.tag in ("td","th")]
            if len(vals)<6:
                continue
            genus,epithet,source,voucher,its,ets=vals[:6]
            taxon=genus.strip()+" "+(epithet.split()[0] if epithet else "")
            if genus not in {"Cirsium","Carduus"} or not re.fullmatch(r"[a-z][a-z-]*",epithet.split()[0] if epithet else ""):
                continue
            A=ACCESSION.search(its)
            B=ACCESSION.search(ets)
            if not A or not B:
                continue
            a,b=A.group().split(".")[0],B.group().split(".")[0]
            if a==b:raise ValueError("same nucleotide accession assigned to both nuclear ITS and ETS")
            hits.append({
                "source_order":len(hits)+1,"source_publication":"Slotta_Horvath_Foley_2012",
                "reported_genus":genus,"reported_species_sample":epithet,"species_binomial":taxon,
                "source_collection":source,"source_voucher":voucher,"its_accession":a,"ets_accession":b,
                "ITS_and_ETS_same_published_table_row":"true",
                "species_assignment_requires_taxonomy_review":"true",
                "molecular_orthology_scope":"nuclear_ribosomal_repeat_ITS_and_ETS_not_independent_low_copy_nuclear_loci",
            })
    if not hits:
        raise ValueError("no source-matched nuclear ITS-ETS specimen pairs in original JATS tables")
    pair_keys=[(r["its_accession"],r["ets_accession"]) for r in hits]
    if len(set(pair_keys))!=len(hits):
        raise ValueError("published accession pair unexpectedly repeated")
    return hits

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--outdir",type=Path,required=True)
    a=p.parse_args()
    raw=fetch()
    rows=extract(raw)
    a.outdir.mkdir(parents=True,exist_ok=True)
    (a.outdir/"slotta2012_original_fulltext.sha256").write_text(hashlib.sha256(raw).hexdigest()+"\n")
    with (a.outdir/"slotta2012_verified_ITS_ETS_voucher_pairs.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)
    bytax=Counter(r["species_binomial"] for r in rows)
    report={
        "version":"slotta2012_source_same_specimen_nuclear_ITS_ETS_audit_v1",
        "doi":"10.3390/plants1020061",
        "original_source_xml":URL,
        "source_XML_SHA256":hashlib.sha256(raw).hexdigest(),
        "n_paired_specimens":len(rows),
        "n_paired_species_binomial_concepts":len(bytax),
        "specimens_by_genus":dict(Counter(r["reported_genus"] for r in rows)),
        "multi_sample_species":{k:v for k,v in sorted(bytax.items()) if v>1},
        "species_names":sorted(bytax),
        "source_vouchers_present":sum(bool(r["source_voucher"] and r["source_voucher"]!="----") for r in rows),
        "does_not_infer_tree":True,
        "comparison_boundaries":[
            "ITS and ETS are both multicopy nuclear ribosomal markers, not 350 independent low-copy nuclear genes",
            "Exact accession pair belongs to one publication row; names/regions remain per-source and taxon-reviewable",
            "Published 2012 sampled taxa do not represent 2025 Moreyra whole-world molecular backbone",
        ],
    }
    (a.outdir/"source_audit.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(report,indent=2,ensure_ascii=False))
if __name__=="__main__":main()
