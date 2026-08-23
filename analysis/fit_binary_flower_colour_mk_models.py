#!/usr/bin/env python3
"""Fit binary ER/ARD Mk models only after all empirical preconditions pass.

States are C (anthocyanin-coloured) and W (white). Unknown/unmapped tree tips
(e.g. reference outgroups) are treated as missing character data while their
topology/rooting is retained.

Rate optimisation uses adaptive log-rate bounds. The original fixed upper bound
(log q=4) can truncate high-rate fits on short substitution-per-site trees, so
bounds are expanded before point estimates or ancestral-state probabilities are
reported. The optimiser diagnostics record whether a final boundary remains.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass, field
from pathlib import Path

STATE_INDEX={"C":0,"W":1}

@dataclass
class Node:
    name:str=""
    length:float|None=None
    children:list["Node"]=field(default_factory=list)

class Parser:
    def __init__(self,text:str): self.s=text.strip(); self.i=0
    def ws(self):
        while self.i<len(self.s) and self.s[self.i].isspace(): self.i+=1
    def label(self):
        self.ws(); start=self.i
        while self.i<len(self.s) and self.s[self.i] not in ':,();': self.i+=1
        return self.s[start:self.i].strip()
    def length(self):
        self.ws()
        if self.i>=len(self.s) or self.s[self.i] != ':': return None
        self.i+=1; start=self.i
        while self.i<len(self.s) and self.s[self.i] not in ',();': self.i+=1
        x=float(self.s[start:self.i].strip())
        if not math.isfinite(x) or x<0: raise ValueError('invalid branch length')
        return x
    def subtree(self):
        self.ws()
        if self.s[self.i]=='(':
            self.i+=1; kids=[self.subtree()]
            while True:
                self.ws()
                if self.s[self.i]==',': self.i+=1; kids.append(self.subtree())
                else: break
            if self.s[self.i]!=')': raise ValueError('unbalanced Newick')
            self.i+=1; name=self.label(); length=self.length(); return Node(name,length,kids)
        name=self.label()
        if not name: raise ValueError('empty tip')
        return Node(name,self.length(),[])
    def parse(self):
        root=self.subtree(); self.ws()
        if self.i<len(self.s) and self.s[self.i]==';':self.i+=1
        self.ws()
        if self.i!=len(self.s):raise ValueError('trailing Newick content')
        return root

def transition(t:float,q_cw:float,q_wc:float):
    if q_cw<=0 or q_wc<=0: raise ValueError('rates must be >0')
    s=q_cw+q_wc; e=math.exp(-s*t); pi_c=q_wc/s; pi_w=q_cw/s
    return ((pi_c+pi_w*e, pi_w*(1-e)),(pi_c*(1-e),pi_w+pi_c*e))

def log_likelihood(root:Node,states:dict[str,str],q_cw:float,q_wc:float,root_prior:str='equilibrium')->float:
    def rec(n:Node):
        if not n.children:
            st=states.get(n.name)
            if st is None:return (1.0,1.0)
            if st not in STATE_INDEX:raise ValueError(f'invalid state {st!r}')
            return (1.0,0.0) if st=='C' else (0.0,1.0)
        like=[1.0,1.0]
        for child in n.children:
            cl=rec(child)
            if child.length is None: raise ValueError(f'missing branch length below {child.name or "internal node"}')
            p=transition(child.length,q_cw,q_wc)
            contrib=(p[0][0]*cl[0]+p[0][1]*cl[1],p[1][0]*cl[0]+p[1][1]*cl[1])
            like[0]*=contrib[0];like[1]*=contrib[1]
        return tuple(like)
    lk=rec(root)
    if root_prior=='flat':prior=(0.5,0.5)
    elif root_prior=='equilibrium':
        s=q_cw+q_wc;prior=(q_wc/s,q_cw/s)
    else:raise ValueError('root_prior must be flat or equilibrium')
    total=prior[0]*lk[0]+prior[1]*lk[1]
    if total<=0:return float('-inf')
    return math.log(total)

def load_states(atlas:Path,tipmap:Path):
    with atlas.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
    taxon_state={r['accepted_taxon']:r['binary_colour_code'].upper() for r in rows if r.get('rate_fit_eligible','').lower()=='yes'}
    with tipmap.open(encoding='utf-8-sig',newline='') as f: maps=list(csv.DictReader(f))
    out={}
    for r in maps:
        tax=r['accepted_taxon']; tip=r['tree_tip']
        if tax in taxon_state: out[tip]=taxon_state[tax]
    if set(taxon_state)-{r['accepted_taxon'] for r in maps}: raise ValueError('eligible atlas taxa missing from tip map')
    return out,taxon_state

def require_gates(preconditions:Path,tree_acceptance:Path):
    p=json.loads(preconditions.read_text()); t=json.loads(tree_acceptance.read_text())
    if p.get('execution_allowed') is not True: raise RuntimeError('empirical rate-fit preconditions are not satisfied: '+','.join(p.get('blockers',[])))
    if t.get('tree_gate_ready') is not True: raise RuntimeError('branch-length tree acceptance gate is not satisfied')
    return p,t

def _near_bound(x:float,lo:float,hi:float,margin:float=0.05)->bool:
    return x-lo<margin or hi-x<margin

def fit_models(root:Node,states:dict[str,str],root_prior='equilibrium'):
    try:
        from scipy.optimize import minimize, minimize_scalar
        from scipy.stats import chi2
    except ImportError as exc: raise RuntimeError('scipy is required for empirical Mk fitting') from exc

    initial=(-9.0,4.0); lo,hi=initial; min_lo=-20.0; max_hi=14.0
    expansion_rounds=0
    while True:
        bounds=(lo,hi)
        er=minimize_scalar(lambda x:-log_likelihood(root,states,math.exp(x),math.exp(x),root_prior),bounds=bounds,method='bounded',options={'xatol':1e-10})
        ard=minimize(lambda x:-log_likelihood(root,states,math.exp(x[0]),math.exp(x[1]),root_prior),x0=[er.x,er.x],method='L-BFGS-B',bounds=[bounds,bounds])
        if not er.success or not ard.success: raise RuntimeError(f'optimizer failure ER={er.success} ARD={ard.success}')
        xs=[float(er.x),float(ard.x[0]),float(ard.x[1])]
        hit_low=any(x-lo<0.05 for x in xs)
        hit_high=any(hi-x<0.05 for x in xs)
        new_lo=max(min_lo,lo-2.0) if hit_low else lo
        new_hi=min(max_hi,hi+2.0) if hit_high else hi
        if (new_lo,new_hi)==(lo,hi): break
        lo,hi=new_lo,new_hi; expansion_rounds+=1
        if expansion_rounds>12: raise RuntimeError('adaptive Mk bound expansion did not converge')

    final_boundary=any(_near_bound(x,lo,hi) for x in xs)
    ll_er=-float(er.fun);ll_ard=-float(ard.fun);q_er=math.exp(float(er.x));q_cw,q_wc=map(lambda z:math.exp(float(z)),ard.x)
    n=sum(v in STATE_INDEX for v in states.values())
    def metrics(ll,k):
        aic=2*k-2*ll;aicc=aic+(2*k*(k+1)/(n-k-1) if n>k+1 else float('inf'));return aic,aicc
    aic_er,aicc_er=metrics(ll_er,1);aic_ard,aicc_ard=metrics(ll_ard,2);lr=max(0.0,2*(ll_ard-ll_er))
    optimizer={
        'initial_log_rate_bounds':list(initial),
        'final_log_rate_bounds':[lo,hi],
        'bound_expansion_rounds':expansion_rounds,
        'final_boundary_hit':final_boundary,
        'legacy_upper_rate':math.exp(initial[1]),
    }
    return {
        'contract_version':'binary_flower_colour_mk_fit_v2_adaptive_bounds','root_prior':root_prior,'n_observed_tips':n,
        'optimizer':optimizer,
        'ER':{'q_C_to_W':q_er,'q_W_to_C':q_er,'logLik':ll_er,'k':1,'AIC':aic_er,'AICc':aicc_er},
        'ARD':{'q_C_to_W':q_cw,'q_W_to_C':q_wc,'loss_to_regain_ratio':q_cw/q_wc,'logLik':ll_ard,'k':2,'AIC':aic_ard,'AICc':aicc_ard},
        'comparison':{'delta_AIC_ARD_minus_ER':aic_ard-aic_er,'delta_AICc_ARD_minus_ER':aicc_ard-aicc_er,'LR_statistic':lr,'LR_df':1,'LR_pvalue':float(chi2.sf(lr,1))},
        'claim_limit':'Model fit alone does not establish causal molecular reactivation, adaptation, or introgression. Interpret rate asymmetry only with topology/branch-length sensitivity, optimizer-bound diagnostics and model adequacy.'
    }

def main():
    p=argparse.ArgumentParser();p.add_argument('--tree',type=Path,required=True);p.add_argument('--atlas',type=Path,required=True);p.add_argument('--tip-map',type=Path,required=True);p.add_argument('--preconditions',type=Path,required=True);p.add_argument('--tree-acceptance',type=Path,required=True);p.add_argument('--root-prior',choices=['equilibrium','flat'],default='equilibrium');p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    require_gates(a.preconditions,a.tree_acceptance);states,_=load_states(a.atlas,a.tip_map);root=Parser(a.tree.read_text()).parse();result=fit_models(root,states,a.root_prior);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
