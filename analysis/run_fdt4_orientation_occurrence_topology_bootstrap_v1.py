#!/usr/bin/env python3
"""Jointly propagate taxon-level occurrence-centroid and topology uncertainty.

Each replicate resamples admitted occurrence cells with replacement within each
taxon, recomputes BIO1/BIO15 centroids, standardizes across taxa, and refits the
orientation contrast. Two covariance treatments are retained:
- canonical branch-length Comp1061 candidate 1;
- a matched raw UFBoot topology with all branches equalized (raw .ufboot has no
  fitted branch lengths).

The bootstrap is a stability diagnostic, not a posterior over historical causes.
"""
from __future__ import annotations
import argparse,json,re
from io import StringIO
from pathlib import Path
import numpy as np,pandas as pd
from Bio import Phylo
from scipy.stats import t as student_t

AXES=['chelsa_bio01','chelsa_bio15']; EXPECTED={'chelsa_bio01':-1,'chelsa_bio15':1}
def parse():
 p=argparse.ArgumentParser(); p.add_argument('--occurrences',type=Path,nargs='+',required=True); p.add_argument('--orientation',type=Path,required=True); p.add_argument('--canonical-trees',type=Path,required=True); p.add_argument('--ufboot',type=Path,required=True); p.add_argument('--min-n',type=int,default=10); p.add_argument('--reps',type=int,default=2000); p.add_argument('--seed',type=int,default=20260830); p.add_argument('--out-dir',type=Path,required=True); return p.parse_args()
def norm(x):return re.sub(r'[^A-Za-z0-9_]+','',x.replace(' ','_').replace('.',''))
def read(line):
 line=line.strip();
 if line.startswith('[') and ']' in line:line=line.split(']',1)[1].strip()
 tr=Phylo.read(StringIO(line),'newick')
 if 'OUTGROUP_saff' in {x.name for x in tr.get_terminals()}:tr.root_with_outgroup({'name':'OUTGROUP_saff'})
 return tr
def read_trees(path):return [read(x) for x in path.read_text().splitlines() if x.strip()]
def equalize(tr):
 tr=Phylo.read(StringIO(tr.format('newick')),'newick')
 for c in tr.find_clades():
  if c is not tr.root:c.branch_length=1.0
 return tr
def covariance(tr,taxa,equal=False):
 if equal:tr=equalize(tr)
 terms={x.name:x for x in tr.get_terminals()}; tips=[terms[norm(t)] for t in taxa]; root=tr.common_ancestor(tips); C=np.zeros((len(tips),len(tips)))
 for i,a in enumerate(tips):
  for j,b in enumerate(tips):
   if i==j:C[i,j]=tr.distance(root,a)
   else:
    m=tr.common_ancestor(a,b); C[i,j]=tr.distance(root,m) if m!=root else 0.0
 C+=np.eye(len(tips))*1e-8; return C
def fit(y,state,C):
 X=np.column_stack([np.ones(len(state)),state]); iv=np.linalg.pinv(C,rcond=1e-12); M=X.T@iv@X; beta=np.linalg.pinv(M,rcond=1e-12)@(X.T@iv@y); r=y-X@beta; df=len(y)-2; sig=float(r.T@iv@r/df); vc=sig*np.linalg.pinv(M,rcond=1e-12); se=float(np.sqrt(max(float(vc[1,1]),0))); p=float(2*student_t.sf(abs(float(beta[1]/se)),df)); return float(beta[1]),se,p
def summarize(q,axis):
 exp=EXPECTED[axis]
 return {'n':int(len(q)),'expected_sign_rate':float((np.sign(q.beta_D_minus_U_sd)==exp).mean()),'beta_q025_q50_q975':[float(q.beta_D_minus_U_sd.quantile(x)) for x in (.025,.5,.975)],'p_q025_q50_q975':[float(q.p.quantile(x)) for x in (.025,.5,.975)],'p_lt_0_05_fraction_descriptive':float((q.p<.05).mean())}
def main():
 a=parse(); a.out_dir.mkdir(parents=True,exist_ok=True); occ=pd.concat([pd.read_csv(p) for p in a.occurrences],ignore_index=True); cnt=occ.groupby('scientific_name_query').size(); st=pd.read_csv(a.orientation); st=st[st.analysis_state.isin(['U','D'])]; sm=dict(zip(st.accepted_taxon,st.analysis_state)); taxa=sorted(t for t,n in cnt.items() if n>=a.min_n and t in sm); state=np.array([0.0 if sm[t]=='U' else 1.0 for t in taxa]); assert len(taxa)>=6 and len(set(state))==2
 by={t:occ[occ.scientific_name_query==t].reset_index(drop=True) for t in taxa}; canonical=read_trees(a.canonical_trees)[0]; boots=read_trees(a.ufboot); assert len(boots)>=1; C0=covariance(canonical,taxa,False); Cb=[covariance(tr,taxa,True) for tr in boots]
 rng=np.random.default_rng(a.seed); rows=[]
 for rep in range(a.reps):
  cent={}
  for t,q in by.items():
   idx=rng.integers(0,len(q),len(q)); cent[t]=q.iloc[idx][AXES].mean()
  c=pd.DataFrame(cent).T.loc[taxa]; bi=rep%len(Cb)
  for axis in AXES:
   raw=c[axis].to_numpy(float); y=(raw-raw.mean())/raw.std(ddof=1)
   for mode,C in [('canonical_branch',C0),('matched_ufboot_equal',Cb[bi])]:
    beta,se,p=fit(y,state,C); rows.append({'replicate':rep+1,'ufboot_index':bi+1,'axis':axis,'mode':mode,'beta_D_minus_U_sd':beta,'se':se,'p':p})
 r=pd.DataFrame(rows); r.to_csv(a.out_dir/'orientation_occurrence_topology_bootstrap_by_rep_v1.csv',index=False)
 payload={'contract_version':'fdt4_orientation_occurrence_topology_bootstrap_v1','seed':a.seed,'replicates':a.reps,'ufboot_trees':len(boots),'n_taxa':len(taxa),'n_U':int((state==0).sum()),'n_D':int((state==1).sum()),'taxa':taxa,'axes':{},'claim_boundary':'Within-taxon occurrence resampling propagates sampling uncertainty of present-day niche centroids. Matched UFBoot equal-branch fits additionally propagate topology but not branch-length uncertainty. Fractions are stability diagnostics, not independent tests or evidence of adaptation.'}
 for axis in AXES:
  payload['axes'][axis]={}
  for mode in ['canonical_branch','matched_ufboot_equal']:
   payload['axes'][axis][mode]=summarize(r[(r.axis==axis)&(r['mode'].eq(mode))],axis)
 (a.out_dir/'fdt4_orientation_occurrence_topology_bootstrap_v1.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n'); print(json.dumps(payload,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
