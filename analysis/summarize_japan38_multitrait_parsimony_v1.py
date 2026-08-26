#!/usr/bin/env python3
"""Minimum-change multi-trait screen on the independently reconstructed Japan-38 tree.

The analysis is deliberately conservative: source-backed taxon-concept states only,
missing concepts are fully ambiguous, concepts excluded from primary trait ASR are
pruned, and replicated concepts are collapsed only when monophyletic. A replicated
concept that is fully unresolved for every analysed trait may be pruned without
blocking trait parsimony, because an all-ambiguous terminal cannot contribute a
Fitch step. Replicate monophyly is still reported as a separate tree diagnostic.
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
def concept_info(path):
    rows=read_csv(path)
    by={r['paper_japan_member_id']:[x for x in r['tip_ids'].split('|') if x] for r in rows}
    allowed={r['paper_japan_member_id']:(r.get('trait_asr_primary_allowed','true').strip().lower()!='false') for r in rows}
    if len(by)!=38:raise ValueError(f'expected 38 concepts, found {len(by)}')
    return by,allowed
def load_tree(path):return Phylo.read(str(path),'newick')
def trait_states(seed_path):
    rows=read_csv(seed_path);by={r['paper_japan_member_id']:r for r in rows};out={}
    for trait in STATE_UNIVERSE:
        out[trait]={mid:trait_state(row,trait) for mid,row in by.items()}
    return out
def resolved_for_any_trait(states,mid):
    return any(states[trait].get(mid,set(universe))!=set(universe) for trait,universe in STATE_UNIVERSE.items())
def prepare_trait_tree(tree,by,allowed,states):
    names={t.name for t in tree.get_terminals()}
    expected={x for xs in by.values() for x in xs}|{'OUTGROUP_saff'}
    if names!=expected:raise ValueError(f'tree tip mismatch missing={sorted(expected-names)} extra={sorted(names-expected)}')
    replicated=[(m,xs) for m,xs in by.items() if len(xs)>1]
    if replicated!=[('JPN_20',by['JPN_20'])]:raise ValueError(f'unexpected replicated concepts {replicated}')
    mid,two=replicated[0]
    mrca=tree.common_ancestor({'name':two[0]},{'name':two[1]});desc={x.name for x in mrca.get_terminals()}
    monophyletic=desc==set(two)
    replicate_resolved=resolved_for_any_trait(states,mid)
    excluded=[]
    if not replicate_resolved:
        # A fully ambiguous replicated concept cannot add a Fitch step. Prune every
        # biological replicate so non-monophyly remains a tree diagnostic rather than
        # an irrelevant blocker of the currently observed trait analysis.
        for tip in two:tree.prune(target=tip)
        excluded.append(mid)
        replicate_mode='pruned_fully_unresolved_replicated_concept'
    elif monophyletic:
        mrca=tree.common_ancestor({'name':two[0]},{'name':two[1]});mrca.clades=[];mrca.name=mid
        replicate_mode='collapsed_monophyletic_replicated_concept'
    else:
        return None,{
          'replicate_monophyly':False,'replicate_resolved_for_any_trait':True,
          'trait_asr_ready':False,'replicate_mode':'blocked_observed_nonmonophyletic_replicate',
          'replicate_mrca_descendants':sorted(desc),'excluded_concepts':[]}
    # Exclude concepts that the frozen reconciliation disallows from primary trait ASR.
    for concept,xs in by.items():
        if allowed.get(concept,True) or len(xs)!=1:continue
        if any(t.name==xs[0] for t in tree.get_terminals()):tree.prune(target=xs[0])
        excluded.append(concept)
    reverse={xs[0]:mid for mid,xs in by.items() if len(xs)==1 and allowed.get(mid,True)}
    for tip in tree.get_terminals():
        if tip.name in reverse:tip.name=reverse[tip.name]
    tree.prune(target='OUTGROUP_saff')
    expected_concepts={mid for mid in by if allowed.get(mid,True) and mid not in excluded}
    final={t.name for t in tree.get_terminals()}
    if final!=expected_concepts:raise ValueError(f'concept tree tip mismatch missing={sorted(expected_concepts-final)} extra={sorted(final-expected_concepts)}')
    return tree,{
      'replicate_monophyly':monophyletic,
      'replicate_resolved_for_any_trait':replicate_resolved,
      'trait_asr_ready':True,
      'replicate_mode':replicate_mode,
      'replicate_mrca_descendants':sorted(desc),
      'excluded_concepts':sorted(set(excluded)),
      'concept_tips':len(final)}
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
def analyze_one(tree_path,concept_path,seed_path):
    by,allowed=concept_info(concept_path);states=trait_states(seed_path);tree=load_tree(tree_path)
    tree,diag=prepare_trait_tree(tree,by,allowed,states)
    if not diag['trait_asr_ready']:return diag
    res={}
    for trait,universe in STATE_UNIVERSE.items():
        steps,root=fitch_steps(tree,states[trait],universe)
        resolved=sum(allowed.get(mid,True) and mid not in diag['excluded_concepts'] and states[trait].get(mid,set(universe))!=set(universe) for mid in by)
        res[trait]={'resolved_concepts':resolved,'minimum_unordered_steps':steps,'minimum_root_state_set':root}
    return {**diag,'source_concepts_total':38,'traits':res,'claim_boundary':'Unordered minimum-change lower bounds on source-backed taxon-concept states. Fully unresolved replicated concepts and concepts disallowed by the frozen reconciliation are pruned; missing/ambiguous states are not imputed; repeated steps are not adaptive-convergence counts.'}
def analyze_bootstrap(path,concept_path,seed_path):
    if not path or not Path(path).is_file():return None
    by,allowed=concept_info(concept_path);states=trait_states(seed_path);vals={k:[] for k in STATE_UNIVERSE};mono=0;total=0;analyzed=0;blocked=0
    modes={}
    for raw in Path(path).read_text(encoding='utf-8').splitlines():
        line=raw.strip()
        if not line:continue
        total+=1;tree=Phylo.read(StringIO(line),'newick');tree,diag=prepare_trait_tree(tree,by,allowed,states)
        if diag['replicate_monophyly']:mono+=1
        modes[diag['replicate_mode']]=modes.get(diag['replicate_mode'],0)+1
        if not diag['trait_asr_ready']:
            blocked+=1;continue
        analyzed+=1
        for trait,universe in STATE_UNIVERSE.items():vals[trait].append(fitch_steps(tree,states[trait],universe)[0])
    def q(x,p):
        x=sorted(x)
        if not x:return None
        return x[min(len(x)-1,max(0,round((len(x)-1)*p)))]
    return {'bootstrap_trees_total':total,'bootstrap_trees_analyzed':analyzed,'bootstrap_trees_blocked':blocked,'jpn20_monophyletic_trees':mono,'jpn20_monophyly_fraction':mono/total if total else None,'replicate_modes':modes,'step_distributions':{t:{'n':len(v),'min':min(v) if v else None,'median':statistics.median(v) if v else None,'max':max(v) if v else None,'q05':q(v,.05),'q95':q(v,.95)} for t,v in vals.items()}}
def main():
    p=argparse.ArgumentParser();p.add_argument('--tree',type=Path,required=True);p.add_argument('--concept-map',type=Path,required=True);p.add_argument('--trait-seed',type=Path,required=True);p.add_argument('--bootstrap-trees',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=analyze_one(a.tree,a.concept_map,a.trait_seed);result['bootstrap_sensitivity']=analyze_bootstrap(a.bootstrap_trees,a.concept_map,a.trait_seed) if a.bootstrap_trees else None
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
