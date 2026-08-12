#!/usr/bin/env python3
"""Validate the 302-sample branch-length tree before Japanese-origin inference.

Acceptance checks the empirical tree artifact, not a preferred geographic
hypothesis.  Japanese monophyly, Arenicola placement and invasion counts are
results to be tested and are therefore deliberately *not* acceptance criteria.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from pathlib import Path

def clean(x):return str(x or '').strip()
def sha256(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as h:return [{k:clean(v) for k,v in r.items()} for r in csv.DictReader(h)]
class Parser:
    def __init__(self,text):self.s=text.strip();self.i=0;self.tips=[];self.lengths=[];self.missing=0;self.clades=[]
    def ws(self):
        while self.i<len(self.s) and self.s[self.i].isspace():self.i+=1
    def label(self):
        self.ws()
        if self.i<len(self.s) and self.s[self.i] in "'\"":
            q=self.s[self.i];self.i+=1;out=[]
            while self.i<len(self.s):
                c=self.s[self.i];self.i+=1
                if c==q:break
                out.append(c)
            return ''.join(out).strip()
        st=self.i
        while self.i<len(self.s) and self.s[self.i] not in ':,();':self.i+=1
        return self.s[st:self.i].strip()
    def length(self,required):
        self.ws()
        if self.i>=len(self.s) or self.s[self.i]!=':':
            if required:self.missing+=1
            return
        self.i+=1;self.ws();st=self.i
        while self.i<len(self.s) and self.s[self.i] not in ',();':self.i+=1
        raw=self.s[st:self.i].strip()
        try:v=float(raw)
        except ValueError:raise ValueError(f'invalid branch length {raw!r}')
        if not math.isfinite(v) or v<0:raise ValueError(f'invalid branch length {v}')
        self.lengths.append(v)
    def subtree(self,is_root=False):
        self.ws()
        if self.s[self.i]=='(':
            self.i+=1;d=set(self.subtree())
            while True:
                self.ws()
                if self.i<len(self.s) and self.s[self.i]==',':self.i+=1;d.update(self.subtree());continue
                break
            if self.i>=len(self.s) or self.s[self.i]!=')':raise ValueError('unbalanced Newick')
            self.i+=1;self.label();self.length(not is_root);self.clades.append(frozenset(d));return d
        lab=self.label()
        if not lab:raise ValueError('empty tip')
        self.tips.append(lab);self.length(True);return {lab}
    def parse(self):
        self.subtree(True);self.ws()
        if self.i<len(self.s) and self.s[self.i]==';':self.i+=1
        self.ws()
        if self.i!=len(self.s):raise ValueError('trailing Newick content')
        if len(self.tips)!=len(set(self.tips)):raise ValueError('duplicate tree tips')
        return self

def validate(tree,manifest,provenance):
    rows=read_csv(manifest)
    if len(rows)!=302 or len({r['tip_id'] for r in rows})!=302:raise ValueError('manifest must contain 302 unique tip_id values')
    expected={r['tip_id'] for r in rows};p=Parser(tree.read_text(encoding='utf-8')).parse();prov=json.loads(provenance.read_text(encoding='utf-8'));tr=set(p.tips)
    if p.missing:raise ValueError(f'{p.missing} non-root edges lack branch lengths')
    if not p.lengths or not any(x>0 for x in p.lengths):raise ValueError('no positive empirical branch lengths')
    refs=set(prov.get('required_reference_tips',[]));roots=set(prov.get('required_outgroup_tips',[]))
    if roots!={'OUTGROUP_lett','OUTGROUP_sunf'}:raise ValueError(f'root outgroups drift: {sorted(roots)}')
    if not roots<=refs:raise ValueError('root outgroups must be reference tips')
    if prov.get('tree_sha256')!=sha256(tree):raise ValueError('tree SHA mismatch')
    missing=expected-tr;extra=tr-expected-refs
    if missing:raise ValueError(f'{len(missing)} global sample tips absent from tree')
    if extra:raise ValueError(f'undeclared extra tree tips: {sorted(extra)[:10]}')
    if refs-tr:raise ValueError(f'required references absent: {sorted(refs-tr)}')
    if frozenset(expected) not in p.clades:raise ValueError('302 focal samples are not monophyletic relative to declared references; reference intrusion blocks acceptance')
    by_tax={}
    for r in rows:by_tax.setdefault(r['analysis_taxon_label'],0);by_tax[r['analysis_taxon_label']]+=1
    for tax,nmin in {'Cirsium brevicaule':3,'Cirsium irumtiense':3,'Cirsium dipsacolepis':1,'Cirsium lineare':1}.items():
        if by_tax.get(tax,0)<nmin:raise ValueError(f'critical taxon underrepresented in manifest: {tax}')
    required_prov=('analysis_name','branch_length_interpretation','rooting_definition','support_metric_definition','source_or_pipeline_provenance','topology_uncertainty_status')
    for k in required_prov:
        if not clean(prov.get(k)):raise ValueError(f'provenance lacks {k}')
    return {'contract_version':'japan_origin_global_tree_acceptance_v1','tree_sha256':sha256(tree),'global_sample_tips':302,'reference_tips':sorted(refs),'branch_length_edge_count':len(p.lengths),'critical_taxon_sample_counts':{k:by_tax.get(k,0) for k in ('Cirsium brevicaule','Cirsium irumtiense','Cirsium dipsacolepis','Cirsium lineare')},'reference_intrusion_passed':True,'tree_artifact_accepted':True,'japanese_monophyly_inference_made':False,'arenicola_placement_inference_made':False,'new_china_sampling_freeze_allowed':False,'claim_limit':'Artifact acceptance does not test or assert Japanese monophyly, Arenicola membership, invasion number or geographic source. Those are downstream topology/biogeographic results.'}
def main():
    p=argparse.ArgumentParser();p.add_argument('--tree',type=Path,required=True);p.add_argument('--manifest',type=Path,required=True);p.add_argument('--provenance',type=Path,required=True);p.add_argument('--output',type=Path);a=p.parse_args();x=validate(a.tree,a.manifest,a.provenance);text=json.dumps(x,indent=2,ensure_ascii=False)+'\n';print(text,end='');
    if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(text,encoding='utf-8')
    return 0
if __name__=='__main__':raise SystemExit(main())
