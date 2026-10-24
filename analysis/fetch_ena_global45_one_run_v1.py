#!/usr/bin/env python3
"""Fetch only a pinned public Moreyra Compositae1061 source run from ENA.

Source genome-wide pilot FASTQs are MD5 checked and never uploaded to GitHub.
"""
from __future__ import annotations
import argparse,hashlib,json,time,urllib.request
from pathlib import Path
from probe_ena_global_comp1061_5tip_realreads_v1 import audit

def fetch(run, outdir):
    info=audit()
    entries=[r for r in info["readsets"] if r["SRR"]==run]
    if len(entries)!=1:raise ValueError("requested SRA not in source-frozen 5")
    e=entries[0]
    outdir.mkdir(parents=True,exist_ok=True)
    digests=[]
    for i,(url,want,bytes_) in enumerate(zip(e["ena_fastq_links"],e["ena_md5"],e["ena_sizes"]),1):
        if url.startswith("ftp.sra.ebi.ac.uk/"):
            url="https://"+url
        if not url.startswith("https://ftp.sra.ebi.ac.uk/"):
            raise ValueError("unexpected read CDN host: "+url)
        target=outdir/f"R{i}.fastq.gz"
        for attempt in range(3):
            try:
                md5=hashlib.md5()
                request=urllib.request.Request(url,headers={"User-Agent":"EAzami-Comp1061-crosscontinent-source-read-validation/1.0"})
                with urllib.request.urlopen(request,timeout=120) as h,target.open("wb") as f:
                    while True:
                        chunk=h.read(2*1024*1024)
                        if not chunk:break
                        f.write(chunk)
                        md5.update(chunk)
                if target.stat().st_size!=bytes_ or md5.hexdigest()!=want:
                    raise ValueError("ENA-published FASTQ size or MD5 mismatch")
                digests.append(md5.hexdigest())
                break
            except Exception as exc:
                if target.exists():target.unlink()
                print("SRA_SOURCE_READ_RETRY",run,i,attempt,str(exc),flush=True)
                if attempt==2:raise
                time.sleep(3+attempt*6)
        print("ENA_VERIFIED_READ",run,i,round(bytes_/1e6,2),"MB",flush=True)
    result={"contract":"world45_frozen_moreyra_source_read_MD5_v1","run":run,
      "taxon":e["source_taxon"],"bioSample":e["biosample"],
      "pairs":2,"md5_checked":digests,"size_bytes":e["run_total_fastq_bytes"],
      "unobserved_shape_on_same_voucher":True}
    (outdir/"fastq_source_verification.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))

def main():
    p=argparse.ArgumentParser();p.add_argument("--run",required=True);p.add_argument("--outdir",type=Path,required=True);a=p.parse_args()
    fetch(a.run,a.outdir)
if __name__=="__main__":main()
