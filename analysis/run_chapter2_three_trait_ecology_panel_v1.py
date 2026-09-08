#!/usr/bin/env python3
from __future__ import annotations
import argparse, itertools, json, math, time
from pathlib import Path
import numpy as np, pandas as pd, requests, rasterio

GBIF='https://api.gbif.org/v1'
BAD={'ZERO_COORDINATE','COUNTRY_COORDINATE_MISMATCH','COORDINATE_INVALID','GEODETIC_DATUM_INVALID'}
UNIVERSE={'orientation':{'U','D'},'phyllary':{'appressed','ascending','spreading','recurved'},'stickiness':{'sticky','nonsticky'}}

def args():
 p=argparse.ArgumentParser(); p.add_argument('--seed',type=Path,required=True); p.add_argument('--extension',type=Path,required=True); p.add_argument('--contract',type=Path,required=True); p.add_argument('--out-json',type=Path,required=True); p.add_argument('--out-taxa',type=Path,required=True); return p.parse_args()
def norm(x): return ' '.join(str(x or '').strip().split())
def match_name(src,q):
 s,q=norm(src).casefold(),norm(q).casefold(); return bool(s and q and (s==q or s.startswith(q+' ')))
def states(r,t):
 if t=='orientation':
  x=str(r.get('orientation_state') or '').strip()
  if x in {'upward_or_erect','upward_or_ascending'}: return {'U'}
  if x=='downward_or_nodding': return {'D'}
 if t=='phyllary':
  x=str(r.get('phyllary_posture') or '').strip(); m={'appressed':{'appressed'},'ascending':{'ascending'},'spreading':{'spreading'},'recurved':{'recurved'},'appressed_or_ascending':{'appressed','ascending'},'ascending_or_recurved':{'ascending','recurved'},'spreading_or_recurved':{'spreading','recurved'}}
  if x in m:return m[x]
 if t=='stickiness':
  x=str(r.get('stickiness_state') or '').strip()
  if x=='sticky':return {'sticky'}
  if x=='nonsticky_or_nearly_nonsticky':return {'nonsticky'}
 return set(UNIVERSE[t])
def fetch_occ(s,q,maxn=3000):
 m=s.get(f'{GBIF}/species/match',params={'name':q},timeout=60);m.raise_for_status(); mj=m.json(); key=mj.get('usageKey') or mj.get('speciesKey')
 if not key:return pd.DataFrame()
 rows=[]; off=0
 while off<maxn:
  lim=min(300,maxn-off); r=s.get(f'{GBIF}/occurrence/search',params={'taxon_key':int(key),'country':'JP','has_coordinate':'true','occurrence_status':'PRESENT','limit':lim,'offset':off},timeout=60);r.raise_for_status(); z=r.json(); got=z.get('results') or []
  if not got: break
  for a in got: rows.append({'scientificName':a.get('scientificName',''),'latitude':a.get('decimalLatitude'),'longitude':a.get('decimalLongitude'),'uncertainty':a.get('coordinateUncertaintyInMeters'),'issues':a.get('issues') or [],'key':a.get('key')})
  off+=len(got)
  if off>=int(z.get('count',0)) or len(got)<lim:break
  time.sleep(.01)
 return pd.DataFrame(rows)
def clean(raw,q,thin=.1):
 if raw.empty:return raw
 x=raw.loc[raw.scientificName.map(lambda v:match_name(v,q))].copy(); x['latitude']=pd.to_numeric(x.latitude,errors='coerce');x['longitude']=pd.to_numeric(x.longitude,errors='coerce');x['uncertainty']=pd.to_numeric(x.uncertainty,errors='coerce')
 valid=x.latitude.between(20,46.5)&x.longitude.between(122,154.5); bad=x.issues.map(lambda z:bool(BAD.intersection(set(z if isinstance(z,list) else []))));x=x.loc[valid&~bad]
 strict=x.uncertainty.notna()&(x.uncertainty<=10000)
 if strict.sum()>=1:x=x.loc[strict]
 else:x=x.loc[x.uncertainty.isna()|(x.uncertainty<=10000)]
 if x.empty:return x
 x=x.assign(tlat=np.floor(x.latitude/thin).astype(int),tlon=np.floor(x.longitude/thin).astype(int),us=x.uncertainty.fillna(1e12)).sort_values(['tlat','tlon','us','key']).drop_duplicates(['tlat','tlon'])
 return x.reset_index(drop=True)
def sample(frame,url):
 coords=list(zip(frame.longitude.astype(float),frame.latitude.astype(float)))
 with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif,.tiff',GDAL_HTTP_MULTIRANGE='YES',GDAL_HTTP_TIMEOUT='120',GDAL_HTTP_MAX_RETRY='4',GDAL_HTTP_RETRY_DELAY='3'):
  with rasterio.open('/vsicurl/'+url) as src:
   raw=np.array([float(v[0]) for v in src.sample(coords,indexes=1,masked=False)],float); nd=src.nodata
   if nd is not None:raw[np.isclose(raw,float(nd))]=np.nan
   sc=float(src.scales[0]) if src.scales else 1.; off=float(src.offsets[0]) if src.offsets else 0.; return raw*sc+off
def unique_perms(labels):
 labs=list(labels); counts={v:labs.count(v) for v in sorted(set(labs))}; n=len(labs); idx=range(n)
 if len(counts)==2:
  a,b=list(counts); na=counts[a]
  for ca in itertools.combinations(idx,na):
   ca=set(ca);yield [a if i in ca else b for i in idx]
 else:
  vals=list(counts)
  def rec(remaining,j,out):
   if j==len(vals)-1:
    z=out.copy()
    for i in remaining:z[i]=vals[j]
    yield z;return
   v=vals[j]
   for c in itertools.combinations(sorted(remaining),counts[v]):
    z=out.copy();nr=set(remaining)
    for i in c:z[i]=v;nr.remove(i)
    yield from rec(nr,j+1,z)
  yield from rec(set(idx),0,[None]*n)
def stat_multivar(X,labels):
 labs=sorted(set(labels)); mu=X.mean(axis=0); s=0.
 for l in labs:
  a=X[np.array(labels)==l]; s+=len(a)*float(np.sum((a.mean(axis=0)-mu)**2))
 return s/len(X)
def exact_rank(X,labels):
 obs=stat_multivar(X,labels); vals=[]
 for p in unique_perms(labels):vals.append(stat_multivar(X,p))
 return obs,int(sum(v>=obs-1e-12 for v in vals)),len(vals)
def univar(X,labels,cols):
 out={}; labs=sorted(set(labels))
 if len(labs)!=2:return out
 a,b=labs
 for j,c in enumerate(cols):
  obs=float(np.mean(X[np.array(labels)==b,j])-np.mean(X[np.array(labels)==a,j])); vals=[]
  for p in unique_perms(labels): vals.append(float(np.mean(X[np.array(p)==b,j])-np.mean(X[np.array(p)==a,j])))
  out[c]={'contrast':f'{b}-{a}','observed':obs,'two_sided_rank_count':int(sum(abs(v)>=abs(obs)-1e-12 for v in vals)),'n_maps':len(vals)}
 return out
def analyze(taxa,trait,minn,envs):
 sc=f'{trait}_singleton_state'; x=taxa.loc[(taxa[sc]!='')&(taxa.n_thinned>=minn)].copy(); labels=x[sc].tolist(); states=sorted(set(labels))
 ret={'n_taxa':len(x),'state_counts':{s:labels.count(s) for s in states},'taxa':x.taxon_name.tolist(),'minimum_occurrences':minn,'status':'not_evaluable'}
 if len(x)<3 or len(states)<2:return ret
 E=x[envs].to_numpy(float); good=np.isfinite(E).all(axis=1);x=x.loc[good].copy();labels=x[sc].tolist();E=E[good]
 if len(x)<3 or len(set(labels))<2:return ret
 Z=(E-E.mean(0))/E.std(0,ddof=1); Z=np.nan_to_num(Z)
 obs,k,n=exact_rank(Z,labels); ret.update({'status':'evaluated','n_taxa':len(x),'state_counts':{s:labels.count(s) for s in sorted(set(labels))},'omnibus_stat':obs,'rank_count':k,'n_maps':n,'exact_fraction':k/n,'univariate':univar(Z,labels,envs)})
 if min(ret['state_counts'].values())<2:ret['resolution_warning']='At least one state is represented by a single taxon; treat as lineage-confounded/resolution-limited.'
 return ret
def main():
 a=args(); c=json.loads(a.contract.read_text()); seed=pd.read_csv(a.seed,dtype=str).fillna(''); ext=pd.read_csv(a.extension,dtype=str).fillna(''); df=pd.concat([seed,ext],ignore_index=True).drop_duplicates('paper_japan_member_id',keep='last')
 reg=[]
 for r in df.to_dict('records'):
  o={'paper_japan_member_id':r['paper_japan_member_id'],'taxon_name':r['nmns_taxon_concept']}; any1=False
  for t in UNIVERSE:
   st=states(r,t);o[t+'_singleton_state']=next(iter(st)) if len(st)==1 else '';o[t+'_allowed_states']='|'.join(sorted(st));any1|=len(st)==1
  if any1:reg.append(o)
 s=requests.Session();s.headers.update({'User-Agent':'EAzami three-trait ecology panel'}); rows=[]; envs=list(c['environment']['variables']); urls=c['environment']['urls']
 for i,r in enumerate(reg):
  q=r['taxon_name']; thin=clean(fetch_occ(s,q),q); out=dict(r);out['n_thinned']=len(thin)
  if len(thin):
   for e in envs: thin[e]=sample(thin,urls[e])
   out.update({e:float(np.nanmedian(thin[e])) for e in envs});out['centroid_lat']=float(np.nanmedian(thin.latitude));out['centroid_lon']=float(np.nanmedian(thin.longitude))
  else:
   out.update({e:np.nan for e in envs});out['centroid_lat']=np.nan;out['centroid_lon']=np.nan
  rows.append(out);print(i+1,len(reg),q,len(thin),flush=True)
 taxa=pd.DataFrame(rows)
 res={'version':'chapter2_three_trait_ecology_result_v1','status_date':'2026-09-08','environment_variables':envs,'primary':{},'sensitivity':{},'claim_boundary':c['claim_ceiling']}
 for t in UNIVERSE:res['primary'][t]=analyze(taxa,t,3,envs)
 res['sensitivity']['phyllary_min1']=analyze(taxa,'phyllary',1,envs)
 res['classification']={t:res['primary'][t]['status'] for t in UNIVERSE}
 a.out_json.parent.mkdir(parents=True,exist_ok=True);a.out_json.write_text(json.dumps(res,indent=2,ensure_ascii=False)+'\n');taxa.to_csv(a.out_taxa,index=False);print(json.dumps(res,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
