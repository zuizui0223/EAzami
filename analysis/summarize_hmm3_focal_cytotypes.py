#!/usr/bin/env python3
"""Summarize source-backed focal cytotype evidence for HMM3.

This is deliberately a focal evidence panel, not a completed Japan-38 cytotype
matrix. Taxon-level cytotypes are not assigned to exact sequenced individuals.
"""
from __future__ import annotations
import argparse,csv,json
from collections import Counter
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input',default='data/evidence/hmm3_japan_radiation_focal_cytotypes_v1.csv')
    ap.add_argument('--output',required=True)
    a=ap.parse_args()
    with Path(a.input).open(encoding='utf-8-sig',newline='') as h: rows=list(csv.DictReader(h))
    if len(rows)!=5: raise ValueError(f'expected 5 focal rows, got {len(rows)}')
    main=[r for r in rows if r['japan_origin_role']=='dominant_main_japanese_radiation']
    exc=[r for r in rows if r['japan_origin_role']=='secondary_japanese_arrival_candidate']
    if len(main)!=4 or len(exc)!=1: raise ValueError('origin-role panel drift')
    main_x=sorted({int(r['ploidy_x']) for r in main})
    main_2n=sorted({int(r['cytotype_2n']) for r in main})
    result={
      'contract_version':'hmm3_focal_japan_radiation_cytotype_synthesis_v1',
      'focal_taxa':len(rows),
      'dominant_radiation_focal_taxa':len(main),
      'secondary_arrival_focal_taxa':len(exc),
      'dominant_radiation_ploidy_states_x':main_x,
      'dominant_radiation_2n_states':main_2n,
      'dominant_radiation_contains_multiple_ploidy_states':len(main_x)>1,
      'dominant_radiation_ploidy_state_counts':dict(sorted(Counter(r['ploidy_x']+'x' for r in main).items())),
      'secondary_arrival_candidate':{
        'taxon':exc[0]['taxon'],'ploidy_x':int(exc[0]['ploidy_x']),'cytotype_2n':int(exc[0]['cytotype_2n'])
      },
      'EAzami_problem':{
        'id':'P_MACRO_08_radiation_not_single_ploidy_state',
        'result':'The current source-backed focal panel places 2x, 4x and 6x taxon-level cytotypes inside the dominant Japanese radiation, while the dipsacolepis secondary-arrival candidate is 2x.',
        'why_problem':'A simple model in which one polyploid state uniquely characterizes or explains the dominant Japanese radiation is incompatible with the observed focal cytotype heterogeneity. The relevant macro variable is cytotype-transition history/heterogeneity, not a binary polyploid-versus-diploid label.',
        'linked_hypothesis':'HMM3'
      },
      'hmm3_refinement':'Replace any simple dominant-radiation-is-polyploid prediction with a branch-explicit test of cytotype transition density, genome-size change, reticulation and trait/niche diversification after age and sampling controls.',
      'claim_boundary':'This five-taxon panel is not a complete Japan-38 cytotype census. NMNS chromosome values are taxon-level evidence and are not assigned to the exact Moreyra sequenced individuals. Cytotype heterogeneity does not by itself cause radiation success.',
      'next_gate':'Expand source-backed cytotype coverage only where authority/voucher provenance is defensible, then map cytotype transitions onto the accepted 294/296 tree instead of imputing missing Japan-38 states.'
    }
    Path(a.output).write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=='__main__': main()
