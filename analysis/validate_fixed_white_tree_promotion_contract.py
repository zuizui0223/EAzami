#!/usr/bin/env python3
"""Validate the predeclared transition from the 20-tip preflight tree to the final W>=5 rate tree."""
from __future__ import annotations
import argparse,json
from pathlib import Path

def validate(path:Path):
    x=json.loads(path.read_text())
    if x.get('contract_version')!='fixed_white_tree_promotion_v0_1':raise ValueError('contract version drift')
    cur=x['current_primary_rate_tree'];final=x['final_rate_tree'];place=x['placement_tree'];sel=x['representative_selection']
    if cur.get('taxon_count')!=20 or cur.get('state_counts')!={'C':17,'W':3}:raise ValueError('current 20-tip counts drift')
    taxa=x.get('target_fixed_white_taxa',[])
    if taxa!=['Cirsium boninense','Cirsium wulongense']:raise ValueError('A1 white target order/content drift')
    if x.get('minimum_independent_samples_per_new_taxon',0)<2:raise ValueError('need >=2 independent samples per white taxon')
    if place.get('minimum_sample_tips',0)<24:raise ValueError('placement tree must contain >=24 sample tips')
    if 'never counted as multiple white macroevolutionary tips' not in place.get('state_counting_rule',''):raise ValueError('pseudo-replication guard missing')
    if not sel.get('performed_only_after_placement_gate'):raise ValueError('representative selection occurs too early')
    if 'eligible recovered loci' not in sel.get('criterion',''):raise ValueError('representative criterion must be QC/completeness based')
    if not sel.get('tie_breaker'):raise ValueError('deterministic tie breaker missing')
    forbidden='|'.join(sel.get('forbidden_criteria',[])).lower()
    if 'er versus ard' not in forbidden or 'arenicola' not in forbidden:raise ValueError('hypothesis-aware representative selection guard missing')
    if final.get('taxon_count')!=22 or final.get('state_counts')!={'C':17,'W':5}:raise ValueError('final 22-tip W5 counts drift')
    if final.get('one_tip_per_species') is not True:raise ValueError('final tree must use one tip per species')
    if 're-infer' not in final.get('branch_length_rule',''):raise ValueError('final branch-length tree must be re-inferred')
    if final.get('must_pass_branch_length_acceptance') is not True or final.get('must_pass_rate_fit_preconditions') is not True:raise ValueError('final gates missing')
    return {'contract_version':x['contract_version'],'current_taxa':20,'placement_min_sample_tips':place['minimum_sample_tips'],'final_taxa':22,'final_states':final['state_counts'],'valid':True}

def main():
    p=argparse.ArgumentParser();p.add_argument('contract',type=Path);a=p.parse_args();print(json.dumps(validate(a.contract),indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
