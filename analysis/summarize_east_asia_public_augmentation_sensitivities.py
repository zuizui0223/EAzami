#!/usr/bin/env python3
"""Aggregate paired EA01/EA02 tree sensitivities into a frozen promotion gate.

This is deliberately conservative. Exact shared-backbone invariance provides
an automatic route; any non-zero RF or loss of same-taxon neighbourhood support
forces manual review rather than post-hoc threshold relaxation.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

CANDIDATES=("EA01","EA02")
SINGLE={"EA01":"ea01_295","EA02":"ea02_295"}
JOINT="ea01_ea02_296"
MODES=("bwa","blastx")


def load(path:Path)->dict:
    if not path.is_file(): raise ValueError(f'missing evaluation artifact: {path}')
    data=json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data,dict): raise ValueError(f'invalid JSON object: {path}')
    return data


def require_bool(data:dict,key:str,path:Path)->bool:
    value=data.get(key)
    if not isinstance(value,bool): raise ValueError(f'{path}: {key} is not boolean')
    return value


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument('--bwa-paired-summary',type=Path,required=True)
    p.add_argument('--blastx-paired-summary',type=Path,required=True)
    p.add_argument('--bwa-evaluation',type=Path,required=True)
    p.add_argument('--blastx-evaluation',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    summaries={'bwa':load(a.bwa_paired_summary),'blastx':load(a.blastx_paired_summary)}
    joint_by_mode={m:int(x.get('joint_paired_loci',0)) for m,x in summaries.items()}
    minimum_by_mode={m:int(x.get('minimum_joint_paired_loci',100)) for m,x in summaries.items()}
    for mode in MODES:
        if joint_by_mode[mode]<minimum_by_mode[mode]: raise ValueError(f'{mode} paired locus gate failed before tree aggregation: {joint_by_mode[mode]} < {minimum_by_mode[mode]}')
    dirs={'bwa':a.bwa_evaluation,'blastx':a.blastx_evaluation}
    loaded={}
    for mode,d in dirs.items():
        for cid in CANDIDATES:
            for scenario in (SINGLE[cid],JOINT):
                key=(mode,cid,scenario,'concat')
                path=d/f'{scenario}_{cid}_concat.json'
                x=load(path)
                if x.get('candidate_id')!=cid: raise ValueError(f'{path}: candidate drift')
                if int(x.get('shared_baseline_focal_tips',0))!=294: raise ValueError(f'{path}: shared baseline tip count drift')
                loaded[key]=(path,x)
        for scenario in ('ea01_295','ea02_295',JOINT):
            key=(mode,'ASTRAL',scenario,'astral')
            path=d/f'{scenario}_astral_backbone.json'
            x=load(path)
            if x.get('scenario_id')!=scenario: raise ValueError(f'{path}: scenario drift')
            loaded[key]=(path,x)

    candidate_out={}
    for cid in CANDIDATES:
        checks={}
        rf={}
        for mode in MODES:
            for scenario in (SINGLE[cid],JOINT):
                path,x=loaded[(mode,cid,scenario,'concat')]
                checks[f'{mode}_{scenario}_concat_exact_backbone']=require_bool(x,'exact_shared_tip_backbone_invariance',path)
                checks[f'{mode}_{scenario}_same_taxon_nearest']=require_bool(x,'same_taxon_among_nearest_baseline_tips',path)
                rf[f'{mode}_{scenario}_concat_rf']=int(x.get('unrooted_rf_distance_on_shared_baseline_tips',-1))
            for scenario in (SINGLE[cid],JOINT):
                path,x=loaded[(mode,'ASTRAL',scenario,'astral')]
                checks[f'{mode}_{scenario}_astral_exact_backbone']=require_bool(x,'exact_shared_species_backbone_invariance',path)
                rf[f'{mode}_{scenario}_astral_rf']=int(x.get('unrooted_rf_distance_on_shared_species',-1))
        passed=all(checks.values())
        candidate_out[cid]={
            'checks':checks,
            'rf_diagnostics':rf,
            'strict_automatic_sample_tip_promotion_gate_passed':passed,
            'sample_tip_promotion_allowed':passed,
            'manual_review_required':not passed,
            'new_analysis_taxon_label_added':False,
        }

    both=all(candidate_out[c]['sample_tip_promotion_allowed'] for c in CANDIDATES)
    out={
        'contract_version':'east_asia_public_augmentation_sensitivity_summary_v1',
        'joint_paired_loci_by_mapping':joint_by_mode,
        'minimum_joint_paired_loci_by_mapping':minimum_by_mode,
        'mapping_modes':list(MODES),
        'tree_sensitivities':['concatenated_iqtree','source_label_astral'],
        'automatic_gate_policy':'Exact shared-backbone invariance plus same-taxon nearest-neighbour replication in both BWA and BLASTx, in both single-candidate and joint-candidate scenarios. Any failure triggers manual review; thresholds are not relaxed automatically.',
        'candidates':candidate_out,
        'both_candidate_sample_tip_promotion_allowed':both,
        'resulting_sample_level_tip_count_if_both_promoted':296 if both else None,
        'new_analysis_taxon_labels_added_if_both_promoted':0,
        'primary_294_tree_superseded':both,
        'new_china_sampling_freeze_allowed':False,
    }
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
