#!/usr/bin/env python3
"""Single-taxon falsification of bidirectional transition-regime tracking H2."""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

import run_chapter2_orientation_transition_regime_hypothesis_v1 as base
import run_chapter2_orientation_transition_directionality_v1 as h2


def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument('--contract',type=Path,required=True)
    p.add_argument('--h2-result',type=Path,required=True)
    p.add_argument('--orientation',type=Path,required=True)
    p.add_argument('--japan-occurrences',type=Path,required=True)
    p.add_argument('--taiwan-occurrences',type=Path,required=True)
    p.add_argument('--au-trees',type=Path,required=True)
    p.add_argument('--out-json',type=Path,required=True)
    p.add_argument('--out-csv',type=Path,required=True)
    return p.parse_args()


def med(stats,key):
    return float(np.median([float(x[key]) for x in stats]))


def main():
    a=parse_args()
    contract=json.loads(a.contract.read_text())
    h2_result=json.loads(a.h2_result.read_text())
    if contract['version']!='chapter2_orientation_transition_directionality_single_deletion_contract_v1':
        raise AssertionError('contract drift')
    if h2_result['classification']!='bidirectional_reversible_regime_supported':
        raise AssertionError('H2 source not supported/frozen')

    taxa=list(contract['strict_panel_taxa'])
    if len(taxa)!=9:
        raise AssertionError('strict panel drift')
    crosswalk=pd.read_csv(a.orientation)
    state_lookup=crosswalk.set_index('accepted_taxon')['analysis_state'].to_dict()
    occ=pd.concat([pd.read_csv(a.japan_occurrences),pd.read_csv(a.taiwan_occurrences)],ignore_index=True)
    trees=base.read_trees(a.au_trees,6)

    deletion_results=[]
    map_frames=[]
    for deleted in taxa:
        panel=[t for t in taxa if t!=deleted]
        state=state_lookup[deleted]
        expected=(int(contract['tests']['expected_map_count_if_deleted_U']) if state=='U'
                  else int(contract['tests']['expected_map_count_if_deleted_D']))
        counts,env=base.build_panel_environment(occ,panel)
        if any(int(counts.get(t,0))<10 for t in panel):
            raise AssertionError(('n>=10 drift',deleted))
        observed_states=base.panel_state_map(crosswalk,panel)
        assets=base.prepare_topology_assets(trees,panel,env)
        obs=h2.topology_directional_stats(assets,observed_states)
        f_all=all(x['forward_alignment']>0 for x in obs)
        r_all=all(x['reverse_alignment']>0 for x in obs)
        obs_floor=med(obs,'bidirectional_floor')

        norm_taxa=[base.normalize_tip(t) for t in panel]
        d_count=sum(int(observed_states[t]) for t in norm_taxa)
        combos=list(itertools.combinations(range(len(norm_taxa)),d_count))
        if len(combos)!=expected:
            raise AssertionError(('map count drift',deleted,len(combos),expected))
        rows=[]
        for combo in combos:
            dset=set(combo)
            states={t:(1 if i in dset else 0) for i,t in enumerate(norm_taxa)}
            topo=h2.topology_directional_stats(assets,states)
            floor=med(topo,'bidirectional_floor')
            rows.append({
                'deleted_taxon':deleted,
                'assignment_id':''.join('D' if i in dset else 'U' for i in range(len(norm_taxa))),
                'observed':bool(all(states[t]==observed_states[t] for t in norm_taxa)),
                'forward_median':med(topo,'forward_alignment'),
                'reverse_median':med(topo,'reverse_alignment'),
                'floor_median':floor,
            })
        frame=pd.DataFrame(rows)
        count=int((frame['floor_median']>=obs_floor-1e-12).sum())
        fraction=float(count/len(frame))
        deletion_results.append({
            'deleted_taxon':deleted,
            'deleted_state':state,
            'forward_positive_6_of_6':bool(f_all),
            'reverse_positive_6_of_6':bool(r_all),
            'forward_alignment_median':med(obs,'forward_alignment'),
            'reverse_alignment_median':med(obs,'reverse_alignment'),
            'bidirectional_floor_median':obs_floor,
            'exact_floor_rank':{'count_at_least_observed':count,'n_maps':len(frame),'exact_fraction':fraction},
            'exact_exceptionality_pass':bool(fraction<=0.05),
        })
        map_frames.append(frame)

    all_direction=all(x['forward_positive_6_of_6'] and x['reverse_positive_6_of_6'] for x in deletion_results)
    n_exact=sum(x['exact_exceptionality_pass'] for x in deletion_results)
    classification=('bidirectional_direction_not_single_taxon_dependent' if all_direction
                    else 'bidirectional_direction_depends_on_taxon')
    out={
        'version':'chapter2_orientation_transition_directionality_single_deletion_result_v1',
        'analysis_role':contract['analysis_role'],
        'classification':classification,
        'all_deletions_bidirectional_direction_pass':bool(all_direction),
        'n_exact_exceptionality_pass':int(n_exact),
        'n_deletions':len(deletion_results),
        'deletion_results':deletion_results,
        'claim_boundary':contract['claim_boundary'],
    }
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(out,indent=2)+'\n')
    pd.concat(map_frames,ignore_index=True).to_csv(a.out_csv,index=False)
    print(json.dumps(out,indent=2))


if __name__=='__main__':
    main()
