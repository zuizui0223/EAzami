#!/usr/bin/env python3
"""Probe original cross-continental Cirsium nuclear ITS/ETS accessions at public APIs.

No phylogenetic inference or specimen name assignment is performed here.
"""
import json, re, urllib.request, urllib.error, xml.etree.ElementTree as ET

URLS={
    "2012_fulltext_europepmc":"https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4844267/fullTextXML",
    "2012_fulltext_europepmc_ebi":"https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4844267/fullTextXML",
    "NCBI_nuclear_ITS_fasta":"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=JX867618&rettype=fasta&retmode=text",
    "ENA_nuclear_ITS_fasta":"https://www.ebi.ac.uk/ena/browser/api/fasta/JX867618",
    "2020_Ackerfield_appendix_HTML":"https://onlinelibrary.wiley.com/doi/full/10.1111/jse.12692",
}
def fetch(url):
    request=urllib.request.Request(url,headers={"User-Agent":"EAzami-academic-crosscontinent-ITS-ETS/1.0"})
    with urllib.request.urlopen(request,timeout=35) as r:
        return r.read(4_500_000).decode("utf-8",errors="replace")
def main():
    out={}
    for name,url in URLS.items():
        try:
            s=fetch(url)
            info={"success":True,"characters":len(s),"fasta_id_found":("JX867618" in s),
                  "has_ITS_ETS":bool(re.search(r"\bITS\b.*\bETS\b",s,re.S|re.I)),
                  "head":s[:240].replace("\n"," ")}
            if "fulltext" in name and s.lstrip().startswith("<?xml"):
                root=ET.fromstring(s)
                tables=root.findall(".//table-wrap")
                info["table_count"]=len(tables)
                info["table_headers"]=[
                    " ".join(" ".join(t.itertext()).split())[:250] for t in tables[:3]
                ]
                info["2012_table_its_accessions"]=len(re.findall(r"JX8676[0-9]{2}",s))
            if "appendix" in name:
                info["appendix_I_found"]=bool(re.search(r"Appendix\s*I\b",s))
                info["2020_accessions_found"]=len(re.findall(r"MN335[0-9]{3}",s))
            out[name]=info
        except Exception as e:
            out[name]={"success":False,"exception_type":type(e).__name__,"error":str(e)[:240]}
    print(json.dumps(out,indent=2,ensure_ascii=False))
    if not any(out[x]["success"] for x in ("NCBI_nuclear_ITS_fasta","ENA_nuclear_ITS_fasta")):
        raise SystemExit("No nucleotide FASTA API available: cannot build empirical nuclear tree")
if __name__=="__main__":main()
