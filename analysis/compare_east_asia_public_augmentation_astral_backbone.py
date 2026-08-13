#!/usr/bin/env python3
"""Compare source-label ASTRAL backbones on the baseline species IDs."""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
from evaluate_east_asia_public_augmentation_tree_pair import NewickParser, split_set

def main()->int:
    p=argparse.ArgumentParser();p.add_argument('--baseline-tree',type=Path,required=True);p.add_argument('--augmented-tree',type=Path,required=True);p.add_argument('--baseline-species-map',type=Path,required=True);p.add_argument('--scenario-id',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    with a.baseline_species_map.open(encoding='utf-8-sig',newline='') as h: rows=list(csv.DictReader(h))
    shared={str(r.get('species_id','')).strip() for r in rows if str(r.get('species_id','')).strip()}
    if len(shared)<4 or len(shared)!=len(rows): raise ValueError('invalid baseline species map')
    b=NewickParser(a.baseline_tree.read_text()).parse();u=NewickParser(a.augmented_tree.read_text()).parse()
    bs=split_set(b,shared); us=split_set(u,shared); rf=len(bs^us); denom=len(bs)+len(us)
    out={'contract_version':'east_asia_public_augmentation_astral_backbone_v1','scenario_id':a.scenario_id,'shared_baseline_source_label_species':len(shared),'baseline_nontrivial_splits':len(bs),'augmented_pruned_nontrivial_splits':len(us),'unrooted_rf_distance_on_shared_species':rf,'normalized_rf_distance_on_shared_species':rf/denom if denom else 0.0,'exact_shared_species_backbone_invariance':rf==0,'tree_tip_promotion_allowed_from_this_comparison_alone':False}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
