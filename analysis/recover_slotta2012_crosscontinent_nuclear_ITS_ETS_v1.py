#!/usr/bin/env python3
"""Download AND VERIFY same-specimen Cirsium ITS+ETS nuclear ribosomal sequences.

Exact specimen-level accession pairs are extracted, without inferred joins,
from Slotta, Horvath & Foley 2012 DOI 10.3390/plants1020061 Table 1.

Nuclear rDNA ITS and ETS are physically linked, multicopy markers. Results
do NOT replicate independent 350 low-copy Compositae nuclear loci used by
Moreyra 2025, or establish a robust full Cirsium world species tree.
"""
from __future__ import annotations

import argparse,csv,hashlib,io,json,re,time,urllib.error,urllib.parse,urllib.request
from collections import Counter,defaultdict
from pathlib import Path

from Bio import SeqIO

from audit_slotta2012_nuclear_ITS_ETS_source_vouchers_v1 import fetch,extract

EUTIL="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
AMBS=set("ACGTRYSWKMBDHVN")
MATCH=re.compile(r"\b(Cirsium|Carduus)\s+([a-z][a-z-]+)\b",re.I)


def get(url:str,retries=4)->str:
    last=None
    for attempt in range(retries):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"EAzami-academic-real-ITS-ETS-reference/1.0"})
            with urllib.request.urlopen(req,timeout=65) as resp:
                return resp.read().decode("utf-8")
        except (OSError,TimeoutError,urllib.error.HTTPError) as e:
            last=e
            time.sleep(2+attempt*3)
    raise RuntimeError("original NCBI accession fetch failed: "+url) from last


def obtain(ids, batch_size=30):
    if len(ids)!=len(set(ids)):
        raise ValueError("accession list contains duplicates")
    result={}
    for lo in range(0,len(ids),batch_size):
        batch=ids[lo:lo+batch_size]
        qs=urllib.parse.urlencode({"db":"nuccore","id":",".join(batch),"rettype":"fasta","retmode":"text"})
        text=get(EUTIL+"?"+qs)
        records=list(SeqIO.parse(io.StringIO(text),"fasta"))
        if not records:
            raise ValueError("empty NCBI accession batch "+repr(batch))
        for record in records:
            ac=record.id.split(".")[0]
            if ac not in batch or ac in result:
                raise ValueError("unexpected/duplicate accession in NCBI batch: "+ac)
            result[ac]={"sequence":str(record.seq).upper().replace("U","T"),"description":record.description}
        print("NCBI_BATCH",lo,len(batch),len(records),flush=True)
        time.sleep(.41)
    return result


def read_and_quality(outdir:Path):
    sourcebytes=fetch()
    source=extract(sourcebytes)
    accession_to_taxa=defaultdict(set)
    for r in source:
        for key in ("its_accession","ets_accession"):
            accession_to_taxa[r[key]].add(r["species_binomial"])
    colliding={k:sorted(x) for k,x in accession_to_taxa.items() if len(x)>1}
    accessions=sorted(accession_to_taxa)
    if len(source)<55 or len(accessions)<110:
        raise ValueError("source publication accession coverage unexpectedly incomplete")
    read=obtain(accessions)

    all_rows,passed=[],[]
    sequences={}
    for row in source:
        item=dict(row)
        status="admitted"
        notes=[]
        its,ets=read.get(row["its_accession"]),read.get(row["ets_accession"])
        if its is None or ets is None:
            status="missing_NCBI_nuclear_sequence"
        if row["its_accession"] in colliding or row["ets_accession"] in colliding:
            status="cross_species_accession_conflict"
        if its is not None and ets is not None:
            for locus,r in [("ITS",its),("ETS",ets)]:
                match=MATCH.search(r["description"])
                seq=r["sequence"]
                if match is None or " ".join(match.groups()).casefold()!=row["species_binomial"].casefold():
                    status="NCBI_header_source_taxon_mismatch"
                    notes.append(f"{locus}:NCBI_taxon={match.group(0) if match else 'NA'}")
                minlen=300 if locus=="ITS" else 200
                if len(seq)<minlen or len(seq)>1600 or not set(seq)<=AMBS:
                    status="locus_length_or_nucleotide_ambiguity_QC"
                    notes.append(f"{locus}:length={len(seq)},alphabet={len(set(seq)-AMBS)}")
                unamb=sum(v in "ACGT" for v in seq)/max(1,len(seq))
                if unamb<.90:
                    status="less_than_90pct_unambiguous_DNA"
                    notes.append(f"{locus}:unambiguous={unamb:.3f}")
                item[f"{locus}_length"]=len(seq)
                item[f"{locus}_SHA256"]=hashlib.sha256(seq.encode()).hexdigest()
                item[f"{locus}_NCBI_description"]=r["description"]
        item["quality_gate"]=status
        item["QC_note"]="|".join(notes)
        item["tip_id"]=f"SLO{int(row['source_order']):03d}_"+row["species_binomial"].replace(" ","_")
        all_rows.append(item)
        if status=="admitted":
            passed.append(item)
            sequences[item["tip_id"]]={"ITS":its["sequence"],"ETS":ets["sequence"]}

    if len(passed)<35:
        raise ValueError("too few exact same-specimen NCBI ITS and ETS pairs; do not invent pairs")
    if not any(x["species_binomial"].startswith("Carduus ") for x in passed):
        raise ValueError("no source-backed Carduus outgroup retained")
    if len({x["tip_id"] for x in passed})!=len(passed):
        raise ValueError("source sample IDs not unique")

    outdir.mkdir(parents=True,exist_ok=True)
    def writecsv(path,rows):
        with path.open("w",newline="",encoding="utf-8") as h:
            w=csv.DictWriter(h,fieldnames=list(rows[0]))
            w.writeheader();w.writerows(rows)
    writecsv(outdir/"full_source_voucher_nuclear_genbank_QC.csv",all_rows)
    writecsv(outdir/"admitted_specimen_nuclear_ITS_ETS.csv",passed)
    for locus in ("ITS","ETS"):
        with (outdir/f"{locus}_unaligned.fasta").open("w") as h:
            for tip in sorted(sequences):
                seq=sequences[tip][locus]
                h.write(f">{tip}\n{seq}\n")
    result={
        "version":"Cirsium_transcontinental_real_genbank_ITS_ETS_same_voucher_v1",
        "original_paper":"Slotta, Horvath & Foley 2012 DOI 10.3390/plants1020061",
        "publisher_fulltext_SHA256":hashlib.sha256(sourcebytes).hexdigest(),
        "publication_voucher_rows_with_both_accessions":len(source),
        "distinct_GenBank_accessions_queried":len(accessions),
        "distinct_sequences_retrieved":len(read),
        "QC_status":dict(sorted(Counter(x["quality_gate"] for x in all_rows).items())),
        "admitted_specimen_tips":len(passed),
        "admitted_source_species_binomials":len(set(x["species_binomial"] for x in passed)),
        "admitted_names":sorted(set(x["species_binomial"] for x in passed)),
        "outgroup_tips":[x["tip_id"] for x in passed if x["species_binomial"].startswith("Carduus ")],
        "cross_species_accession_reuse":colliding,
        "source_methods":"GenBank original FASTA sequences, ITS and ETS paired within exactly same original publication voucher row",
        "molecular_data_type":"nuclear multicopy ribosomal ITS and ETS, linked repeats, not hundreds of independent capture loci",
        "nuclear_tree_completed":False,
        "native_geographic_populations_ascertained":False,
        "whole_worldwide_Cirsium_nuclear_tree_completed":False
    }
    (outdir/"source_sequence_audit.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2),flush=True)
    return result


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--outdir",type=Path,required=True)
    args=ap.parse_args()
    read_and_quality(args.outdir)

if __name__=="__main__":
    main()
