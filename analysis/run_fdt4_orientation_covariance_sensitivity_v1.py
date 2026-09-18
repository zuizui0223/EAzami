#!/usr/bin/env python3
"""Profile orientation-climate PGLS across phylogenetic covariance strength.

For each supplied Comp1061 branch-length tree, Pagel-style lambda scales only the
off-diagonal shared-path covariance from lambda=0 (no phylogenetic covariance)
to lambda=1 (the fitted Brownian phylogram). A fixed grid is reported together
with a REML-profiled lambda. This is a covariance-model sensitivity, not evidence
that lambda describes the historical process that generated the trait.
"""
from __future__ import annotations
import argparse,json,math,re
from io import StringIO
from pathlib import Path
import numpy as np,pandas as pd
from Bio import Phylo
from scipy.optimize import minimize_scalar
from scipy.stats import t as student_t

AXES=['chelsa_bio01','chelsa_bio15']
EXPECTED={'chelsa_bio01':-1,'chelsa_bio15':1}
LGRID=[0.0,0.25,0.5,0.75,1.0]

def parse():
 p=argparse.ArgumentParser(); p.add_argument('--occurrences',type=Path,nargs='+',required=True); p.add_argument('--orientation',type=Path,required=True); p.add_argument('--trees',type=Path,required=True); p.add_argument('--min-n',type=int,default=10); p.add_argument('--out-dir',type=Path,required=True); return p.parse_args()
def norm(x): return re.sub(r'[^A-Za-z0-9_]+','',x.replace(' ','_').replace('.',''))
def trees(path):
 out=[]
 for line in path.read_text().splitlines():
  line=line.strip()
  if not line: continue
  if line.startswith('[') and ']' in line: line=line.split(']',1)[1].strip()
  tr=Phylo.read(StringIO(line),'newick')
  if 'OUTGROUP_saff' in {x.name for x in tr.get_terminals()}: tr.root_with_outgroup({'name':'OUTGROUP_saff'})
  out.append(tr)
 return out
def base_cov(tr,taxa):
 terms={x.name:x for x in tr.get_terminals()}; tips=[terms[norm(t)] for t in taxa]; root=tr.common_ancestor(tips); n=len(tips); C=np.zeros((n,n))
 for i,a in enumerate(tips):
  for j,b in enumerate(tips):
   if i==j:C[i,j]=tr.distance(root,a)
   else:
    m=tr.common_ancestor(a,b); C[i,j]=tr.distance(root,m) if m!=root else 0.0
 scale=max(float(np.max(np.diag(C))),1.0); C+=np.eye(n)*scale*1e-10; return C
def lcov(C,l):
 D=np.diag(np.diag(C)); return D+l*(C-D)
def gls(y,state,V):
 X=np.column_stack([np.ones(len(state)),state]); inv=np.linalg.pinv(V,rcond=1e-12); M=X.T@inv@X; beta=np.linalg.pinv(M,rcond=1e-12)@(X.T@inv@y); r=y-X@beta; df=len(y)-2; sse=float(r.T@inv@r); sig=sse/df; vc=sig*np.linalg.pinv(M,rcond=1e-12); se=float(np.sqrt(max(float(vc[1,1]),0))); tv=float(beta[1]/se); return float(beta[1]),se,float(2*student_t.sf(abs(tv),df)),sse,M
def reml_nll(l,y,state,C):
 V=lcov(C,l); X=np.column_stack([np.ones(len(state)),state]); inv=np.linalg.pinv(V,rcond=1e-12); M=X.T@inv@X; b=np.linalg.pinv(M,rcond=1e-12)@(X.T@inv@y); r=y-X@b; sse=float(r.T@inv@r); df=len(y)-X.shape[1]
 if sse<=0:return 1e99
 s1,ldV=np.linalg.slogdet(V); s2,ldM=np.linalg.slogdet(M)
 if s1<=0 or s2<=0:return 1e99
 return float(ldV+ldM+df*np.log(sse/df))
def main():
 a=parse(); a.out_dir.mkdir(parents=True,exist_ok=True); occ=pd.concat([pd.read_csv(p) for p in a.occurrences],ignore_index=True); cnt=occ.groupby('scientific_name_query').size(); eligible=set(cnt[cnt>=a.min_n].index); cent=occ.groupby('scientific_name_query')[AXES].mean()
 st=pd.read_csv(a.orientation); st=st[st.analysis_state.isin(['U','D'])]; sm=dict(zip(st.accepted_taxon,st.analysis_state)); taxa=sorted(eligible&set(sm)); state=np.array([0.0 if sm[t]=='U' else 1.0 for t in taxa]); assert len(taxa)>=6 and len(set(state))==2
 trs=trees(a.trees); rows=[]
 for ti,tr in enumerate(trs,1):
  C=base_cov(tr,taxa)
  for axis in AXES:
   raw=cent.loc[taxa,axis].to_numpy(float); y=(raw-raw.mean())/raw.std(ddof=1)
   for l in LGRID:
    beta,se,p,_,_=gls(y,state,lcov(C,l)); rows.append({'tree_index':ti,'axis':axis,'fit':'fixed_grid','lambda':l,'beta_D_minus_U_sd':beta,'se':se,'p':p})
   opt=minimize_scalar(lambda x:reml_nll(x,y,state,C),bounds=(0,1),method='bounded',options={'xatol':1e-8}); l=float(opt.x); beta,se,p,_,_=gls(y,state,lcov(C,l)); rows.append({'tree_index':ti,'axis':axis,'fit':'profile_REML','lambda':l,'beta_D_minus_U_sd':beta,'se':se,'p':p})
 r=pd.DataFrame(rows); r.to_csv(a.out_dir/'orientation_covariance_sensitivity_by_fit_v1.csv',index=False)
 payload={'contract_version':'fdt4_orientation_covariance_sensitivity_v1','n_taxa':len(taxa),'n_U':int((state==0).sum()),'n_D':int((state==1).sum()),'taxa':taxa,'trees':len(trs),'lambda_grid':LGRID,'axes':{},'claim_boundary':'Lambda sensitivity tests covariance-strength dependence on the same branch-length trees. It does not identify the true evolutionary covariance process, and P-value fractions across trees/lambda are not independent replications.'}
 for axis in AXES:
  q=r[r.axis==axis]; g=q[q.fit=='fixed_grid']; m=q[q.fit=='profile_REML']; sign=EXPECTED[axis]
  payload['axes'][axis]={
   'fixed_grid_fits':len(g),'expected_sign_rate':float((np.sign(g.beta_D_minus_U_sd)==sign).mean()),'beta_range':[float(g.beta_D_minus_U_sd.min()),float(g.beta_D_minus_U_sd.max())],'p_range':[float(g.p.min()),float(g.p.max())],'all_fixed_grid_p_lt_0_05':bool((g.p<0.05).all()),
   'profile_REML_lambda_range':[float(m['lambda'].min()),float(m['lambda'].max())],'profile_REML_beta_range':[float(m.beta_D_minus_U_sd.min()),float(m.beta_D_minus_U_sd.max())],'profile_REML_p_range':[float(m.p.min()),float(m.p.max())]
  }
 (a.out_dir/'fdt4_orientation_covariance_sensitivity_v1.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n'); print(json.dumps(payload,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
