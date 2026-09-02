#!/usr/bin/env python3
"""Audit the public NOAA de Boer 5.3-Myr reconstruction before analytical use."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    return p.parse_args()


def norm(s:str)->str:
    return re.sub(r'[^a-z0-9]+','',s.lower())


def main():
    args=parse_args()
    lines=args.source.read_text(encoding='utf-8-sig',errors='replace').splitlines()
    header_candidates=[]
    for i,line in enumerate(lines):
        if '\t' not in line:
            continue
        fields=[x.strip() for x in line.lstrip('#').split('\t')]
        if len(fields)<2:
            continue
        low=[norm(x) for x in fields]
        if any('age' in x for x in low):
            header_candidates.append({
                'line_number':i+1,
                'fields':fields,
                'next_line':lines[i+1] if i+1 < len(lines) else ''
            })
    if not header_candidates:
        raise AssertionError('No tab-delimited age-bearing header candidate found')
    def sea_like(field:str)->bool:
        n=norm(field)
        return ('sea' in n and ('lev' in n or 'level' in n)) or n in {'sl','slm','rsl','rslm','sealev','sealevel','sealevelm'}
    # A real data header should be followed by a numeric row. Prefer that over NOAA
    # variable-description tables, which also contain age/sea-level words.
    def numeric_next(h):
        cells=h['next_line'].split('\t')
        try:
            float(cells[0])
            return True
        except Exception:
            return False
    selected=next((h for h in header_candidates if numeric_next(h) and any(sea_like(f) for f in h['fields'])),None)
    if selected is None:
        selected=next((h for h in header_candidates if numeric_next(h)),header_candidates[0])
    age_fields=[f for f in selected['fields'] if 'age' in norm(f)]
    sea_fields=[f for f in selected['fields'] if sea_like(f)]
    result={
      'audit_version':'chapter2_deboer2014_sealevel_source_audit_v1',
      'status_date':'2026-09-02',
      'source_file':args.source.name,
      'n_lines':len(lines),
      'header_candidates':header_candidates,
      'selected_header_line':selected['line_number'],
      'selected_fields':selected['fields'],
      'selected_next_line':selected['next_line'],
      'age_field_candidates':age_fields,
      'sea_level_field_candidates':sea_fields,
      'n_header_candidates':len(header_candidates),
      'source_metadata':{
        'dataset':'NOAA/WDS Global 5 Million Year Sea Level, Temperature, and d18Osw Reconstructions',
        'dataset_doi':'10.25921/xs31-nt56',
        'associated_publication_doi':'10.1038/ncomms3999',
        'declared_coverage':'0-5.3 Ma',
        'role':'model-based full-chronology sea-level sensitivity; not local connectivity reconstruction'
      },
      'parser_status':'ready_for_full_analysis' if len(age_fields)>=1 and len(sea_fields)==1 and numeric_next(selected) else 'needs_manual_column_selection',
      'claim_boundary':[
        'This is a model-based global reconstruction and is not interchangeable with the Spratt-Lisiecki 0-798 ka stack.',
        'Global eustatic sea level does not reconstruct local Ryukyu/Taiwan connectivity.',
        'Source audit alone carries no differentiation-trigger inference.'
      ]
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    main()
