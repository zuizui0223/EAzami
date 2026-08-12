#!/usr/bin/env python3
"""Join frozen verified Arenicola SRA runs into the maximal Japan-origin panel.

The base maximal panel deliberately distinguishes source metadata from exact run
resolution.  This augmenter promotes only the six Chang 2026 Arenicola rows
whose voucher-to-run assignments were verified by the independent complete
NCBI reconciliation workflow and frozen in
``data/evidence/chang2026_arenicola_public_run_manifest_v1.csv``.

No other Chang row is resolved by inference here.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

DEFAULT_PANEL=Path("data/evidence/generated/japan_origin_max_public_panel/japan_origin_max_public_panel_v1.csv")
DEFAULT_ARENICOLA=Path("data/evidence/chang2026_arenicola_public_run_manifest_v1.csv")
DEFAULT_OUTPUT=Path("data/evidence/generated/japan_origin_max_public_panel/japan_origin_max_public_panel_v1_run_resolved.csv")

REQUIRED_PANEL={"panel_id","source_study","analysis_taxon_label","voucher","biosample","public_identifiers","run_accessions","run_resolution_state"}
REQUIRED_RUN={"taxon","voucher","biosample","run","library_layout","match_confidence","match_status","source_workflow_run","source_artifact_id","source_artifact_sha256"}
EXPECTED={
    "ccy4163":("Cirsium brevicaule","SRR35152730","SAMN50798032"),
    "ccy4166":("Cirsium brevicaule","SRR35152729","SAMN50798033"),
    "ccy4295":("Cirsium brevicaule","SRR35152725","SAMN50798036"),
    "ccy4078":("Cirsium irumtiense","SRR35152732","SAMN50798030"),
    "ccy4111":("Cirsium irumtiense","SRR35152731","SAMN50798031"),
    "ccy4296":("Cirsium irumtiense","SRR35152724","SAMN50798037"),
}


def clean(x: object)->str: return str(x or "").strip()

def read_csv(path:Path):
    with path.open(encoding="utf-8-sig",newline="") as h:
        r=csv.DictReader(h); fields=list(r.fieldnames or [])
        rows=[{k:clean(v) for k,v in row.items()} for row in r if any(clean(v) for v in row.values())]
    return fields,rows

def unique_join(values): return "|".join(sorted({clean(v) for v in values if clean(v)}))


def validate_runs(rows):
    if not rows: raise ValueError("Arenicola run manifest is empty")
    missing=REQUIRED_RUN-set(rows[0])
    if missing: raise ValueError(f"Arenicola run manifest missing {sorted(missing)}")
    by={r["voucher"]:r for r in rows}
    if set(by)!=set(EXPECTED): raise ValueError(f"Arenicola voucher set changed: {sorted(by)}")
    if len({r["run"] for r in rows})!=6 or len({r["biosample"] for r in rows})!=6:
        raise ValueError("Arenicola runs/BioSamples must be one-to-one")
    for voucher,(taxon,run,bio) in EXPECTED.items():
        r=by[voucher]
        if (r["taxon"],r["run"],r["biosample"])!=(taxon,run,bio):
            raise ValueError(f"Frozen Arenicola identity changed for {voucher}")
        if r["library_layout"]!="PAIRED" or r["match_confidence"]!="verified":
            raise ValueError(f"Arenicola run is not verified paired-end: {voucher}")
    artifacts={r["source_artifact_sha256"] for r in rows}
    if len(artifacts)!=1: raise ValueError("Arenicola run manifest has mixed artifact provenance")
    return by


def augment(panel_rows, run_rows):
    by=validate_runs(run_rows)
    seen=set(); out=[]
    for src in panel_rows:
        row=dict(src)
        if row.get("source_study")=="Chang2026" and row.get("voucher") in by:
            v=row["voucher"]; rr=by[v]
            if row.get("analysis_taxon_label")!=rr["taxon"]:
                raise ValueError(f"Panel/run taxon mismatch for {v}")
            row["biosample"]=rr["biosample"]
            row["run_accessions"]=rr["run"]
            row["public_identifiers"]=unique_join([row.get("public_identifiers"),rr["biosample"],rr["run"]])
            row["run_resolution_state"]="resolved_public_runs"
            seen.add(v)
        out.append(row)
    if seen!=set(EXPECTED):
        raise ValueError(f"Not all Arenicola vouchers joined: {sorted(set(EXPECTED)-seen)}")
    return out


def summarize(rows):
    states=Counter(r["run_resolution_state"] for r in rows)
    ry=[r for r in rows if r["analysis_taxon_label"] in {"Cirsium brevicaule","Cirsium irumtiense"}]
    if len(ry)!=6 or any(r["run_resolution_state"]!="resolved_public_runs" for r in ry):
        raise ValueError("All six Arenicola rows must be run-resolved")
    return {
        "contract_version":"japan_origin_arenicola_run_augmentation_v1",
        "panel_rows":len(rows),
        "run_resolution_state_counts":dict(sorted(states.items())),
        "arenicola_rows":len(ry),
        "arenicola_unique_runs":len({r["run_accessions"] for r in ry}),
        "arenicola_unique_biosamples":len({r["biosample"] for r in ry}),
        "arenicola_all_verified_run_resolved":True,
        "joint_common_locus_tree_executed":False,
        "new_china_sampling_freeze_allowed":False,
    }


def main():
    p=argparse.ArgumentParser();p.add_argument("--panel",type=Path,default=DEFAULT_PANEL);p.add_argument("--arenicola",type=Path,default=DEFAULT_ARENICOLA);p.add_argument("--output",type=Path,default=DEFAULT_OUTPUT);a=p.parse_args()
    fields,panel=read_csv(a.panel); missing=REQUIRED_PANEL-set(fields)
    if missing: raise SystemExit(f"panel missing {sorted(missing)}")
    _,runs=read_csv(a.arenicola)
    out=augment(panel,runs); summary=summarize(out)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open("w",encoding="utf-8",newline="") as h:
        w=csv.DictWriter(h,fieldnames=fields);w.writeheader();w.writerows(out)
    sp=a.output.with_name("japan_origin_max_public_panel_v1_run_resolved_summary.json")
    sp.write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2,ensure_ascii=False));return 0

if __name__=="__main__": raise SystemExit(main())
