#!/usr/bin/env python3
"""Strict climate-blind occurrence gate for the frozen V2 orientation panel."""
from __future__ import annotations

import argparse
import csv
import json
import math
import time
import urllib.parse
import urllib.request
from pathlib import Path

GBIF="https://api.gbif.org/v1"
BAD={"ZERO_COORDINATE","COUNTRY_COORDINATE_MISMATCH","COORDINATE_INVALID","GEODETIC_DATUM_INVALID"}


def norm(s: str) -> str:
    return " ".join((s or "").strip().split())


def get_json(url: str, params: dict) -> dict:
    full=url+"?"+urllib.parse.urlencode(params)
    req=urllib.request.Request(full,headers={"User-Agent":"EAzami-heldout-orientation-occurrence-v2/1.0"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def returned_name_matches(value: str, query: str) -> bool:
    a,b=norm(value).casefold(),norm(query).casefold()
    return bool(a and b and (a==b or a.startswith(b+" ")))


def finite(v):
    try:
        x=float(v)
        return x if math.isfinite(x) else None
    except (TypeError,ValueError):
        return None


def fetch(name: str, country: str, max_records: int=3000):
    match=get_json(f"{GBIF}/species/match",{"name":name,"strict":"true"})
    meta={
        "gbif_match_type":match.get("matchType") or "",
        "gbif_usage_key":match.get("usageKey") or match.get("speciesKey"),
        "gbif_scientific_name":match.get("scientificName") or "",
        "gbif_canonical_name":match.get("canonicalName") or "",
    }
    if meta["gbif_match_type"]!="EXACT" or not meta["gbif_usage_key"]:
        return [],meta
    rows=[]; off=0
    while off<max_records:
        lim=min(300,max_records-off)
        z=get_json(f"{GBIF}/occurrence/search",{
            "taxon_key":int(meta["gbif_usage_key"]),
            "country":country,
            "has_coordinate":"true",
            "occurrence_status":"PRESENT",
            "limit":lim,
            "offset":off,
        })
        got=z.get("results") or []
        if not got: break
        for r in got:
            rows.append({
                "scientificName":r.get("scientificName") or "",
                "latitude":r.get("decimalLatitude"),
                "longitude":r.get("decimalLongitude"),
                "uncertainty":r.get("coordinateUncertaintyInMeters"),
                "issues":r.get("issues") or [],
                "key":r.get("key"),
            })
        off += len(got)
        if off>=int(z.get("count") or 0) or len(got)<lim: break
        time.sleep(.02)
    return rows,meta


def clean(rows,query,max_unc,thin):
    exact=[r for r in rows if returned_name_matches(r.get("scientificName",""),query)]
    quality=[]
    for r in exact:
        lat,lon,unc=finite(r.get("latitude")),finite(r.get("longitude")),finite(r.get("uncertainty"))
        issues=set(r.get("issues") or [])
        if lat is None or lon is None or unc is None: continue
        if not (-90<=lat<=90 and -180<=lon<=180): continue
        if unc>max_unc or BAD.intersection(issues): continue
        z=dict(r);z["latitude"]=lat;z["longitude"]=lon;z["uncertainty"]=unc
        quality.append(z)
    quality.sort(key=lambda r:(r["latitude"],r["longitude"],r["uncertainty"],int(r.get("key") or 10**18)))
    coord={}
    for r in quality: coord.setdefault((r["latitude"],r["longitude"]),r)
    uniq=list(coord.values())
    uniq.sort(key=lambda r:(r["uncertainty"],int(r.get("key") or 10**18)))
    cells={}
    for r in uniq:
        cell=(math.floor(r["latitude"]/thin),math.floor(r["longitude"]/thin))
        cells.setdefault(cell,r)
    thinned=list(cells.values())
    return thinned,{
        "n_raw":len(rows),
        "n_exact_name":len(exact),
        "n_quality":len(quality),
        "n_coordinate_unique":len(uniq),
        "n_thinned":len(thinned),
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--panel",type=Path,required=True)
    ap.add_argument("--contract",type=Path,required=True)
    ap.add_argument("--out-csv",type=Path,required=True)
    ap.add_argument("--out-json",type=Path,required=True)
    args=ap.parse_args()
    c=json.loads(args.contract.read_text(encoding="utf-8"))
    assert c["status"]=="FROZEN_BEFORE_V2_GBIF_OCCURRENCE_QUERY"
    with args.panel.open(encoding="utf-8",newline="") as f:
        panel=list(csv.DictReader(f))
    assert len(panel)==c["n_candidates"]
    country=c["provenance"]["country_code"]
    max_unc=float(c["occurrence_qc"]["max_coordinate_uncertainty_m"])
    thin=float(c["occurrence_qc"]["deterministic_thin_degrees"])
    min_n=int(c["occurrence_qc"]["minimum_thinned_occurrences_per_taxon"])

    out=[]
    for i,r in enumerate(panel,1):
        name=r["analysis_taxon"]
        raw,meta=fetch(name,country)
        thinned,counts=clean(raw,name,max_unc,thin)
        row={
            "analysis_taxon":name,
            "orientation_state":r["orientation_state"],
            "country":country,
            **meta,
            **counts,
            "passes_primary_occurrence_gate":len(thinned)>=min_n,
            "minimum_thinned_occurrences_primary":min_n,
            "max_coordinate_uncertainty_m":max_unc,
            "thin_degrees":thin,
            "environment_opened":False,
        }
        out.append(row)
        print(json.dumps(row,ensure_ascii=False),flush=True)

    passing=[r for r in out if r["passes_primary_occurrence_gate"]]
    counts={
        state:sum(r["orientation_state"]==state for r in passing)
        for state in c["evaluability"]["required_states"]
    }
    min_state=int(c["evaluability"]["minimum_taxa_per_state"])
    evaluable=all(counts.get(s,0)>=min_state for s in c["evaluability"]["required_states"])
    result={
        "version":"heldout_orientation_occurrence_support_v2",
        "status_date":"2026-09-24",
        "environment_opened":False,
        "n_candidates":len(panel),
        "n_taxa_passing":len(passing),
        "state_counts_passing":counts,
        "minimum_taxa_per_state":min_state,
        "confirmatory_ecology_evaluable":evaluable,
        "surviving_taxa":[r["analysis_taxon"] for r in passing],
        "stop_decision":"freeze_surviving_panel_then_open_BIO1_BIO15" if evaluable else "stop_external_taxon_confirmation_without_environment",
    }

    args.out_csv.parent.mkdir(parents=True,exist_ok=True)
    with args.out_csv.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(out[0]))
        w.writeheader();w.writerows(out)
    args.out_json.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
