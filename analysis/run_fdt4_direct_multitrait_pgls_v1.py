#!/usr/bin/env python3
"""Screen direct capitulum-width and phyllary-protrusion measurements on AU trees.

Exploratory FDT4 diagnostic only. Uses only taxa with directly comparable measured
capitulum width and phyllary protrusion. This is not an adaptation test.
"""
from __future__ import annotations
import argparse,csv,json,re
from io import StringIO
from pathlib import Path
import numpy as np
from Bio import Phylo
from scipy.stats import t as student_t

def norm(x:str)->str:return re.sub(r'[^A-Za-z0-9_]+','',x.replace(' ','_').replace('.',''))
def rows(p):
    with p.open(encoding='utf-8-sig',newline='') as h:return list(csv.DictReader(h))
def val(x):
    s=str(x or '').strip()
    if not s or '-' in s:return None
    return float(s)
def trees(path,n=6):
    out=[]
    lines=[x.strip() for x in path.read_text().splitlines() if x.strip()]
    for line in lines[:n]:
        if line.startswith('[') and ']' in line:line=line.split(']',1)[1].strip()
        tr=Phylo.read(StringIO(line),'newick');tr.root_with_outgroup({'name':'OUTGROUP_saff'});out.append(tr)
    return out
def cov(tr,names):
    term={x.name:x for x in tr.get_terminals()};tips=[term[x] for x in names];root=tr.common_ancestor(tips)
    C=np.zeros((len(tips),len(tips)))
    for i,a in enumerate(tips):
        for j,b in enumerate(tips):
            if i==j:C[i,j]=tr.distance(root,a)
            else:
                m=tr.common_ancestor(a,b);C[i,j]=tr.distance(root,m) if m!=root else 0.0
    return C+np.eye(len(tips))*1e-10
def fit(y,x,C):
    X=np.column_stack([np.ones(len(x)),x]);V=np.linalg.inv(C);b=np.linalg.solve(X.T@V@X,X.T@V@y)
    r=y-X@b;df=len(y)-2;s2=float(r.T@V@r/df);vb=s2*np.linalg.inv(X.T@V@X);se=float(np.sqrt(vb[1,1]));t=float(b[1]/se);p=float(2*student_t.sf(abs(t),df))
    return float(b[1]),p
def z(a):
    a=np.asarray(a,float);return (a-a.mean())/a.std(ddof=1)
def main():
    p=argparse.ArgumentParser();p.add_argument('--display',type=Path,required=True);p.add_argument('--phyllary',type=Path,required=True);p.add_argument('--orientation',type=Path,required=True);p.add_argument('--au-trees',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    D={r['taxon']:val(r['width_cm']) for r in rows(a.display) if r['size_metric']=='measured_capitulum_length_width'}
    P={r['taxon']:val(r['phyllary_protrusion_mm']) for r in rows(a.phyllary)}
    O={r['accepted_taxon']:r['analysis_state'] for r in rows(a.orientation) if r['analysis_state'] in {'U','D'}}
    taxa=sorted(t for t in set(D)&set(P)&set(O) if D[t] is not None and P[t] is not None)
    if len(taxa)!=7:raise ValueError(f'expected frozen seven-taxon overlap, got {taxa}')
    names=[norm(t) for t in taxa];state=np.array([1.0 if O[t]=='D' else 0.0 for t in taxa]);dw=z([D[t] for t in taxa]);pp=z([P[t] for t in taxa])
    out={'taxa':taxa,'by_topology':[]}
    for i,tr in enumerate(trees(a.au_trees),1):
        C=cov(tr,names);bd,pd=fit(dw,state,C);bp,ppv=fit(pp,state,C);bc,pc=fit(pp,dw,C)
        out['by_topology'].append({'topology':i,'display_width_by_orientation_beta':bd,'display_width_by_orientation_p':pd,'phyllary_by_orientation_beta':bp,'phyllary_by_orientation_p':ppv,'phyllary_by_display_width_beta':bc,'phyllary_by_display_width_p':pc})
    out['claim_boundary']='Exploratory seven-taxon direct-measurement PGLS only; no adaptation or convergence claim.'
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
