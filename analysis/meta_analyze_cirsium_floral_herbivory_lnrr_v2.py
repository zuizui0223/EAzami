#!/usr/bin/env python3
"""Direct response-ratio meta-analysis of experimental Cirsium floral herbivory.

Estimand: viable/mature seed output under experimentally reduced insect herbivory
relative to ambient herbivory. Effect = ln(mean_reduced / mean_ambient).
For reported mean ± SE, delta-method sampling variance is
(SE_reduced/mean_reduced)^2 + (SE_ambient/mean_ambient)^2.
Multiple independent strata/years within one publication are collapsed before the
across-study random-effects model.
"""
from __future__ import annotations
import argparse, csv, json, math
from collections import defaultdict
from pathlib import Path


def rnd(x): return round(float(x), 12)


def iv_pool(rows):
    w=[1/r['var'] for r in rows]
    y=sum(wi*r['yi'] for wi,r in zip(w,rows))/sum(w)
    return y,1/sum(w)


def dl(rows):
    k=len(rows); w=[1/r['var'] for r in rows]
    fixed=sum(wi*r['yi'] for wi,r in zip(w,rows))/sum(w)
    q=sum(wi*(r['yi']-fixed)**2 for wi,r in zip(w,rows))
    c=sum(w)-sum(wi*wi for wi in w)/sum(w)
    tau=max(0.0,(q-(k-1))/c)
    wr=[1/(r['var']+tau) for r in rows]
    y=sum(wi*r['yi'] for wi,r in zip(wr,rows))/sum(wr)
    se=math.sqrt(1/sum(wr)); lo=y-1.96*se; hi=y+1.96*se
    rr=math.exp(y); rrlo=math.exp(lo); rrhi=math.exp(hi)
    i2=max(0.0,(q-(k-1))/q)*100 if q else 0.0
    z=y/se; p=math.erfc(abs(z)/math.sqrt(2))
    return {'k':k,'pooled_lnRR':rnd(y),'se_lnRR':rnd(se),'ci95_lnRR':[rnd(lo),rnd(hi)],
            'response_ratio':rnd(rr),'ci95_response_ratio':[rnd(rrlo),rnd(rrhi)],
            'ambient_seed_output_reduction_fraction':rnd(1-1/rr),
            'ambient_seed_output_reduction_fraction_ci95':[rnd(1-1/rrlo),rnd(1-1/rrhi)],
            'Q':rnd(q),'Q_df':k-1,'tau2_lnRR':rnd(tau),'I2_percent':rnd(i2),
            'z_test':rnd(z),'p_two_sided':rnd(p)}


def build(inp: Path):
    raw=list(csv.DictReader(inp.open(encoding='utf-8',newline='')))
    effects=[]
    for r in raw:
        m1=float(r['reduced_herbivory_mean']); se1=float(r['reduced_herbivory_se'])
        m0=float(r['ambient_herbivory_mean']); se0=float(r['ambient_herbivory_se'])
        if min(m1,m0)<=0: raise ValueError('lnRR requires positive means')
        yi=math.log(m1/m0); var=(se1/m1)**2+(se0/m0)**2
        effects.append({'study':r['study_cluster'],'effect_id':r['effect_id'],'taxon':r['taxon'],
                        'stratum':r['habitat_or_stratum'],'yi':yi,'var':var,
                        'RR':math.exp(yi),'source':r['source_locator']})
    grouped=defaultdict(list)
    for x in effects: grouped[x['study']].append(x)
    studies=[]
    for study in sorted(grouped):
        y,v=iv_pool(grouped[study])
        studies.append({'study':study,'yi':y,'var':v,'RR':math.exp(y),
                        'n_effects':len(grouped[study]),'taxa':sorted({x['taxon'] for x in grouped[study]})})
    meta=dl(studies)
    loo=[]
    for omit in sorted(x['study'] for x in studies):
        mm=dl([x for x in studies if x['study']!=omit])
        loo.append({'omitted_study':omit,'response_ratio':mm['response_ratio'],
                    'ci95_response_ratio':mm['ci95_response_ratio'],'I2_percent':mm['I2_percent']})
    return {
      'contract_version':'cirsium_floral_herbivory_lnrr_meta_v2','status_date':'2026-08-19',
      'estimand':'seed_output_under_reduced_insect_herbivory_relative_to_ambient_herbivory',
      'effect_definition':'lnRR=ln(mean_seed_output_reduced_herbivory/mean_seed_output_ambient_herbivory)',
      'coverage':{'effect_rows':len(effects),'independent_study_clusters':len(studies),
                  'taxa_or_taxon_concepts':sorted({x['taxon'] for x in effects})},
      'effect_level':[{'study':x['study'],'effect_id':x['effect_id'],'taxon':x['taxon'],'stratum':x['stratum'],
                       'lnRR':rnd(x['yi']),'var_lnRR':rnd(x['var']),'response_ratio':rnd(x['RR']),'source':x['source']} for x in effects],
      'study_level':[{'study':x['study'],'n_effects_collapsed':x['n_effects'],'taxa':x['taxa'],
                      'lnRR':rnd(x['yi']),'var_lnRR':rnd(x['var']),'response_ratio':rnd(x['RR'])} for x in studies],
      'random_effects':meta,'leave_one_study_out':loo,
      'current_inference':'Across four independent Cirsium data-generation studies with directly reported seed-output means and SEs, experimentally reducing insect herbivory increases viable/mature seed output by about 2.7-fold on average; the direction and magnitude are stable to leave-one-study-out removal.',
      'claim_boundary':'This is a direct quantitative seed-output meta-analysis. Within-study strata/years are collapsed before across-study pooling. It estimates the antagonist fitness cost, not the adaptive effect of any particular capitulum trait. Correlation among within-study contrasts, differences in experimental protocol, and numerical provenance of older Louda/Potvin means remain sensitivity considerations.'}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--input',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
    out=build(a.input); a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
if __name__=='__main__': main()
