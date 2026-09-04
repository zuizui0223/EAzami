#!/usr/bin/env python3
"""Single-taxon deletion falsification for the fixed transition-regime H1."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from run_chapter2_orientation_transition_regime_hypothesis_v1 import (
    build_panel_environment,
    exact_panel_test,
    panel_state_map,
    prepare_topology_assets,
    read_json,
    read_trees,
)


def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument('--contract',type=Path,required=True)
    p.add_argument('--robustness-result',type=Path,required=True)
    p.add_argument('--orientation',type=Path,required=True)
    p.add_argument('--japan-occurrences',type=Path,required=True)
    p.add_argument('--taiwan-occurrences',type=Path,required=True)
    p.add_argument('--au-trees',type=Path,required=True)
    p.add_argument('--out-json',type=Path,required=True)
    p.add_argument('--out-csv',type=Path,required=True)
    return p.parse_args()


def main():
    args=parse_args()
    contract=read_json(args.contract)
    robust=read_json(args.robustness_result)
    if contract['version']!='chapter2_orientation_transition_regime_single_deletion_contract_v1':
        raise AssertionError('contract drift')
    if robust['version']!='chapter2_orientation_transition_regime_robustness_result_v1':
        raise AssertionError('robustness source drift')
    strict=robust['strict_n10'] if 'strict_n10' in robust else robust['tests']['strict_n10']
    taxa=list(strict.get('taxa_order', [
        'Cirsium alpicola','Cirsium brevicaule','Cirsium irumtiense',
        'Cirsium japonicum var. australe','Cirsium japonicum var. japonicum',
        'Cirsium kamtschaticum','Cirsium kawakamii','Cirsium suffultum','Cirsium yezoense']))
    if len(taxa)!=9:
        raise AssertionError('strict panel n drift')

    crosswalk=pd.read_csv(args.orientation)
    state_lookup=crosswalk.set_index('accepted_taxon')['analysis_state'].to_dict()
    jp=pd.read_csv(args.japan_occurrences)
    tw=pd.read_csv(args.taiwan_occurrences)
    occ=pd.concat([jp,tw],ignore_index=True)
    trees=read_trees(args.au_trees,6)

    deletion_results=[]
    map_frames=[]
    for deleted in taxa:
        panel=[t for t in taxa if t!=deleted]
        deleted_state=state_lookup[deleted]
        if deleted_state not in {'U','D'}:
            raise AssertionError(('deleted unresolved state',deleted,deleted_state))
        expected_maps=(contract['tests']['expected_map_count_if_deleted_U'] if deleted_state=='U'
                       else contract['tests']['expected_map_count_if_deleted_D'])
        counts,env=build_panel_environment(occ,panel)
        if any(int(counts.get(t,0))<10 for t in panel):
            raise AssertionError(('n>=10 drift',deleted))
        states=panel_state_map(crosswalk,panel)
        assets=prepare_topology_assets(trees,panel,env)
        result,frame=exact_panel_test('delete_'+deleted.replace(' ','_'),panel,states,assets,int(expected_maps))
        direction_pass=all(x>0 for x in result['observed']['topology_composite'])
        exact_pass=result['exact_primary_rank']['exact_fraction']<=0.05
        deletion_results.append({
            'deleted_taxon':deleted,
            'deleted_state':deleted_state,
            'n_taxa':result['n_taxa'],
            'n_U':result['n_U'],
            'n_D':result['n_D'],
            'composite_median':result['observed']['composite_median'],
            'topology_composite':result['observed']['topology_composite'],
            'direction_pass':direction_pass,
            'exact_primary_rank':result['exact_primary_rank'],
            'exact_exceptionality_pass':exact_pass,
            'bio15_rank':result['secondary_axis_ranks']['bio15'],
            'lower_bio1_rank':result['secondary_axis_ranks']['bio1_lower_expected'],
        })
        frame=frame.copy(); frame['deleted_taxon']=deleted
        map_frames.append(frame)

    all_direction=all(x['direction_pass'] for x in deletion_results)
    all_exact=all(x['exact_exceptionality_pass'] for x in deletion_results)
    if all_direction and all_exact:
        classification='transition_regime_direction_and_exceptionality_robust_to_every_single_taxon_deletion'
    elif all_direction:
        classification='transition_regime_direction_not_single_taxon_dependent_but_exceptionality_sensitive'
    else:
        classification='transition_regime_direction_depends_on_at_least_one_taxon'

    out={
        'version':'chapter2_orientation_transition_regime_single_deletion_result_v1',
        'analysis_role':contract['analysis_role'],
        'fixed_hypothesis':contract['fixed_hypothesis'],
        'classification':classification,
        'all_deletions_direction_pass':all_direction,
        'all_deletions_exact_exceptionality_pass':all_exact,
        'n_exact_exceptionality_pass':sum(x['exact_exceptionality_pass'] for x in deletion_results),
        'n_deletions':len(deletion_results),
        'deletion_results':deletion_results,
        'claim_ceiling':contract['claim_ceiling'],
    }
    args.out_json.parent.mkdir(parents=True,exist_ok=True)
    args.out_json.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    pd.concat(map_frames,ignore_index=True).to_csv(args.out_csv,index=False)
    print(json.dumps(out,indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
