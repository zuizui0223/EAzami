#!/usr/bin/env python3
"""Minimum-change multi-trait screen on the independently reconstructed Japan-38 tree.

The analysis is deliberately conservative: source-backed taxon-concept states only,
missing concepts are fully ambiguous, JPN_31 is never forced, and JPN_20 is collapsed
to one concept only when its two biological samples are monophyletic.
"""
from __future__ import annotations
import argparse,csv,json,statistics
from io import StringIO
from pathlib import Path
from Bio import Phylo

STATE_UNIVERSE={
 'orientation':{'U','D'},
 'phyllary':{'appressed','ascending','spreading','recurved'},
 'stickiness':{'sticky','nonsticky'},
}

def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as h:return list(csv.DictReader(h))
def trait_state(row,trait):
    if trait=='orientation':
        x=(row.get('orientation_state') or '').strip()
        if x in {'upward_or_erect','upward_or_ascending'}:return {'U'}
        if x=='downward_or_nodding':return {'D'}
    elif trait=='phyllary':
        x=(row.get('phyllary_posture') or '').strip()
        mapping={
          'appressed':{'appressed'},'ascending':{'ascending'},'spreading':{'spreading'},
          'appressed_or_ascending':{'appressed','ascending'},
          'ascending_or_recurved':{'ascending','recurved'},
          'spreading_or_recurved':{'spreading','recurved'},
        }
        if x in mapping:return mapping[x]
    elif trait=='stickiness':
        x=(row.get('stickiness_state') or '').strip()
        if x=='sticky':return {'sticky'}
        if x=='nonsticky_or_nearly_nonsticky':return {'nonsticky'}
    return set(STATE_UNIVERSE[trait])
def concept_map(path):
    rows=read_csv(path); by={r['paper_japan_member_id']:[x for x in r['tip_ids'].split('|') if x] for r in rows}
    if len(by)!=38:raise ValueError(f'expected 38 concepts, found {len(by)}')
    return by
def load_tree(path):return Phylo.read(str(path),'newick')
def collapse_to_concepts(tree,by):
    names={t.name for t in tree.get_terminals()}
    expected={x for xs in by.values() for x in xs}|{'OUTGROUP_saff'}
    if names!=expected:raise ValueError(f'tree tip mismatch missing={sorted(expected-names)} extra={sorted(names-expected)}')
    replicated=[(m,xs) for m,xs in by.items() if len(xs)>1]
    if replicated!=[('JPN_20',by['JPN_20'])]:raise ValueError(f'unexpected replicated concepts {replicated}')
    two=by['JPN_20']; mrca=tree.common_ancestor({'name':two[0]},{'name':two[1]});desc={x.name for x in mrca.get_terminals()}
    monophyletic=desc==set(two)
    if not monophyletic:return None,False
    mrca.clades=[];mrca.name='JPN_20'
    # Rename all singleton biological tips to the frozen paper-member IDs.
    reverse={xs[0]:mid for mid,xs in by.items() if len(xs)==1}
    for tip in tree.get_terminals():
        if tip.name in reverse:tip.name=reverse[tip.name]
    # Remove the outgroup before trait parsimony so an unobserved outgroup state cannot affect the ingroup minimum.
    tree.prune(target='OUTGROUP_saff')
    final={t.name for t in tree.get_terminals()}
    if final!=set(by):raise ValueError(f'concept tree tip mismatch {sorted(final^set(by))}')
    return tree,True
def fitch_steps(tree,states,universe):
    steps=0
    def walk(clade):
        nonlocal steps
        if clade.is_terminal():return set(states.get(clade.name,universe))
        child_sets=[walk(c) for c in clade.clades]
        cur=child_sets[0]
        for nxt in child_sets[1:]:
            inter=cur & nxt
            if inter:cur=inter
            else:cur=cur|nxt;steps+=1
        return cur
    rootset=walk(tree.root)
    return steps,sorted(rootset)
def trait_states(seed_path):
    rows=read_csv(seed_path);by={r['paper_japan_member_id']:r for r in rows};out={}
    for trait in STATE_UNIVERSE:
        out[trait]={mid:trait_state(row,trait) for mid,row in by.items()}
    return out
def analyze_one(tree_path,concept_path,seed_path):
    by=concept_map(concept_path); tree=load_tree(tree_path); tree,mono=collapse_to_concepts(tree,by)
    if not mono:return {'replicate_monophyly':False,'trait_asr_ready':False}
    states=trait_states(seed_path);res={}
    for trait,universe in STATE_UNIVERSE.items():
        steps,root=fitch_steps(tree,states[trait],universe)
        resolved=sum(states[trait].get(mid,set(universe))!=set(universe) for mid in by)
        res[trait]={'resolved_concepts':resolved,'minimum_unordered_steps':steps,'minimum_root_state_set':root}
    return {'replicate_monophyly':True,'trait_asr_ready':True,'concept_tips':38,'traits':res,'claim_boundary':'Unordered minimum-change lower bounds on taxon-concept states. Missing/ambiguous states are not imputed; repeated steps are not adaptive-convergence counts.'}
def analyze_bootstrap(path,concept_path,seed_path):
    if not path or not Path(path).is_file():return None
    by=concept_map(concept_path);states=trait_states(seed_path);vals={k:[] for k in STATE_UNIVERSE};mono=0;total=0
    for raw in Path(path).read_text(encoding='utf-8').splitlines():
        line=raw.strip()
        if not line:continue
        total+=1;tree=Phylo.read(StringIO(line),'newick');tree,ok=collapse_to_concepts(tree,by)
        if not ok:continue
        mono+=1
        for trait,universe in STATE_UNIVERSE.items():vals[trait].append(fitch_steps(tree,states[trait],universe)[0])
    def q(x,p):
        x=sorted(x)
        if not x:return None
        return x[min(len(x)-1,max(0,round((len(x)-1)*p)))]
    return {'bootstrap_trees_total':total,'jpn20_monophyletic_trees':mono,'jpn20_monophyly_fraction':mono/total if total else None,'step_distributions':{t:{'n':len(v),'min':min(v) if v else None,'median':statistics.median(v) if v else None,'max':max(v) if v else None,'q05':q(v,.05),'q95':q(v,.95)} for t,v in vals.items()}}
def main():
    p=argparse.ArgumentParser();p.add_argument('--tree',type=Path,required=True);p.add_argument('--concept-map',type=Path,required=True);p.add_argument('--trait-seed',type=Path,required=True);p.add_argument('--bootstrap-trees',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=analyze_one(a.tree,a.concept_map,a.trait_seed);result['bootstrap_sensitivity']=analyze_bootstrap(a.bootstrap_trees,a.concept_map,a.trait_seed) if a.bootstrap_trees else None
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
