#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,math
from pathlib import Path


def read(path:Path):
    with path.open(encoding='utf-8-sig',newline='') as h:
        return list(csv.DictReader(h))

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument('--input',type=Path,required=True); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
    rows=read(a.input)
    if len(rows)<2: raise ValueError('need >=2 independent studies')
    effects=[]
    for r in rows:
        m1=float(r['treatment_natural_or_protective_mean']); se1=float(r['treatment_natural_or_protective_se'])
        m0=float(r['forced_or_alternative_mean']); se0=float(r['forced_or_alternative_se'])
        if min(m1,m0,se1,se0)<=0: raise ValueError('lnRR delta-method requires positive means and SEs')
        y=math.log(m1/m0)
        se=math.sqrt((se1/m1)**2+(se0/m0)**2)
        effects.append({'study_id':r['study_id'],'taxon':r['taxon'],'family':r['family'],'endpoint':r['endpoint'],'lnRR':y,'se_lnRR':se,'RR':math.exp(y),'ci95_RR':[math.exp(y-1.96*se),math.exp(y+1.96*se)]})
    ys=[x['lnRR'] for x in effects]; vs=[x['se_lnRR']**2 for x in effects]; ws=[1/v for v in vs]
    sw=sum(ws); fixed=sum(w*y for w,y in zip(ws,ys))/sw; fixed_se=math.sqrt(1/sw)
    Q=sum(w*(y-fixed)**2 for w,y in zip(ws,ys)); df=len(ys)-1
    C=sw-sum(w*w for w in ws)/sw
    tau2=max(0.0,(Q-df)/C) if C>0 else 0.0
    wr=[1/(v+tau2) for v in vs]; swr=sum(wr); mu=sum(w*y for w,y in zip(wr,ys))/swr; se=math.sqrt(1/swr)
    I2=max(0.0,(Q-df)/Q)*100 if Q>0 else 0.0
    out={
      'contract_version':'fdt1_orientation_net_fitness_two_study_meta_v1',
      'k':len(effects),
      'effects':effects,
      'fixed_effect':{'lnRR':fixed,'se':fixed_se,'RR':math.exp(fixed),'ci95_RR':[math.exp(fixed-1.96*fixed_se),math.exp(fixed+1.96*fixed_se)]},
      'random_effect_DL':{'tau2':tau2,'lnRR':mu,'se':se,'RR':math.exp(mu),'ci95_RR_normal':[math.exp(mu-1.96*se),math.exp(mu+1.96*se)]},
      'heterogeneity':{'Q':Q,'df':df,'I2_percent':I2},
      'interpretation':'Both independent manipulations favour the natural downward/nodding orientation for seed/achene success, but effect magnitude is highly heterogeneous. With k=2, the pooled mean is a feasibility diagnostic rather than a publishable general effect; moderator/context expansion is the priority.',
      'claim_boundary':'Approximate delta-method lnRR from reported means and SEs. Achene set and seed set are homologous proportional reproductive-success endpoints but from different families. Do not treat the k=2 pooled effect as evidence that downward orientation is universally adaptive or as a Cirsium effect.'
    }
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
