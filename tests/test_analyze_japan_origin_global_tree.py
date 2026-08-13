from __future__ import annotations
import csv,hashlib,importlib.util,json,sys,tempfile,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('jogtop',ROOT/'analysis/analyze_japan_origin_global_tree.py');assert spec and spec.loader
mod=importlib.util.module_from_spec(spec);sys.modules['jogtop']=mod;spec.loader.exec_module(mod)


def write_csv(path,fields,rows):
    with path.open('w',encoding='utf-8',newline='') as h:
        w=csv.DictWriter(h,fieldnames=fields);w.writeheader();w.writerows(rows)


def fixture(root:Path,mode:str):
    main=[f'M{i:02d}' for i in range(1,25)];aren=['B1','B2','B3','I1','I2','I3'];extras=['D1','L1','C1']
    meta=[];panel=[]
    for tip in main:
        tax='Cirsium main_'+tip
        meta.append({'tip_id':tip,'panel_id':'P'+tip,'source_study':'Moreyra2025','analysis_taxon_label':tax})
        panel.append({'panel_id':'P'+tip,'region':'Japan','location':'Honshu','name_review_required':'false'})
    for tip,tax in [('B1','Cirsium brevicaule'),('B2','Cirsium brevicaule'),('B3','Cirsium brevicaule'),('I1','Cirsium irumtiense'),('I2','Cirsium irumtiense'),('I3','Cirsium irumtiense')]:
        meta.append({'tip_id':tip,'panel_id':'P'+tip,'source_study':'Chang2026','analysis_taxon_label':tax});panel.append({'panel_id':'P'+tip,'region':'Japan_Ryukyu','location':'Ryukyu','name_review_required':'false'})
    for tip,tax,region in [('D1','Cirsium dipsacolepis','Japan'),('L1','Cirsium lineare','Japan'),('C1','Cirsium continental_candidate','China')]:
        meta.append({'tip_id':tip,'panel_id':'P'+tip,'source_study':'Moreyra2025','analysis_taxon_label':tax});panel.append({'panel_id':'P'+tip,'region':region,'location':region,'name_review_required':'false'})
    mf=root/'manifest.csv';pf=root/'panel.csv';jf=root/'japan38.csv'
    write_csv(mf,['tip_id','panel_id','source_study','analysis_taxon_label'],meta)
    write_csv(pf,['panel_id','region','location','name_review_required'],panel)
    jr=[{'paper_taxon_concept':'concept_'+t,'tree_codes':'Cirsium main_'+t} for t in main]
    jr += [{'paper_taxon_concept':'dips','tree_codes':'Cirsium dipsacolepis'},{'paper_taxon_concept':'line','tree_codes':'Cirsium lineare'}]
    write_csv(jf,['paper_taxon_concept','tree_codes'],jr)
    main_s=','.join(f'{x}:0.01' for x in main);aren_s=','.join(f'{x}:0.01' for x in aren)
    if mode=='sister':
        nw=f'((({main_s}):0.10,({aren_s}):0.10):0.20,(D1:0.1,L1:0.1,C1:0.1):0.20);'
    elif mode=='separate':
        nw=f'((({main_s}):0.10,(D1:0.1,L1:0.1):0.1):0.20,(({aren_s}):0.10,C1:0.10):0.20);'
    elif mode=='nested':
        first=main[0];rest=','.join(f'{x}:0.01' for x in main[1:])
        nw=f'(({first}:0.01,(({rest}):0.05,({aren_s}):0.05):0.05):0.20,(D1:0.1,L1:0.1,C1:0.1):0.20);'
    else:raise ValueError(mode)
    tf=root/'tree.nwk';tf.write_text(nw+'\n',encoding='utf-8')
    return tf,mf,pf,jf


class JapanOriginTopologyTests(unittest.TestCase):
    def test_arenicola_sister_to_published_main_radiation(self):
        with tempfile.TemporaryDirectory() as td:
            tree,m,p,j=fixture(Path(td),'sister');result,cands=mod.analyze(tree,m,p,j,None,False)
            self.assertTrue(result['group_statistics']['main_japanese_radiation']['monophyletic'])
            self.assertTrue(result['group_statistics']['arenicola']['monophyletic'])
            self.assertEqual(result['arenicola_relative_to_main_radiation'],'arenicola_immediate_sister_to_published_main_radiation')
            self.assertFalse(result['dispersal_direction_inferred']);self.assertFalse(result['new_china_sampling_freeze_allowed'])
            self.assertGreater(len(cands),0)

    def test_separate_continental_neighbourhood_becomes_shortlist_not_origin_claim(self):
        with tempfile.TemporaryDirectory() as td:
            tree,m,p,j=fixture(Path(td),'separate');result,cands=mod.analyze(tree,m,p,j,None,False)
            self.assertEqual(result['arenicola_relative_to_main_radiation'],'arenicola_separate_from_published_main_radiation')
            rows=[r for r in cands if r['focal_group']=='arenicola' and r['candidate_taxon']=='Cirsium continental_candidate']
            self.assertEqual(len(rows),1);self.assertEqual(rows[0]['region'],'China');self.assertEqual(rows[0]['sampling_priority_if_public_data_remain_unresolved'],'S')
            self.assertFalse(result['direct_ancestry_inferred']);self.assertFalse(result['introgression_inferred'])

    def test_intercalated_arenicola_breaks_published_main_monophyly(self):
        with tempfile.TemporaryDirectory() as td:
            tree,m,p,j=fixture(Path(td),'nested');result,_=mod.analyze(tree,m,p,j,None,False)
            self.assertFalse(result['group_statistics']['main_japanese_radiation']['monophyletic'])
            self.assertEqual(result['arenicola_relative_to_main_radiation'],'arenicola_nested_within_published_main_radiation_mrca')

    def test_requires_accepted_tree_when_acceptance_file_supplied(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);tree,m,p,j=fixture(root,'sister');a=root/'accept.json';a.write_text('{"tree_artifact_accepted": false}')
            with self.assertRaisesRegex(ValueError,'artifact acceptance'):mod.analyze(tree,m,p,j,a,False)

    def test_accepted_tree_is_sha_bound_and_rerooted_on_references(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);tree,m,p,j=fixture(root,'sister')
            focal=tree.read_text(encoding='utf-8').strip().rstrip(';')
            tree.write_text(f'({focal}:0.1,(OUTGROUP_lett:0.1,OUTGROUP_sunf:0.1):0.2);\n',encoding='utf-8')
            acceptance=root/'accept.json'
            acceptance.write_text(json.dumps({
                'contract_version':'synthetic_tree_acceptance_v1',
                'tree_sha256':hashlib.sha256(tree.read_bytes()).hexdigest(),
                'reference_tips':['OUTGROUP_lett','OUTGROUP_sunf'],
                'tree_artifact_accepted':True,
            }),encoding='utf-8')
            result,_=mod.analyze(tree,m,p,j,acceptance,False)
            self.assertTrue(result['tree_artifact_acceptance_verified'])
            self.assertEqual(result['reference_tips_used_for_rooting'],['OUTGROUP_lett','OUTGROUP_sunf'])
            self.assertTrue(result['group_statistics']['main_japanese_radiation']['monophyletic'])

    def test_acceptance_sha_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);tree,m,p,j=fixture(root,'sister');a=root/'accept.json'
            a.write_text(json.dumps({'tree_artifact_accepted':True,'tree_sha256':'0'*64}),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'SHA does not match'):
                mod.analyze(tree,m,p,j,a,False)

    def test_candidate_retains_name_review_gate(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);tree,m,p,j=fixture(root,'separate')
            rows=mod.read_csv(p)
            next(row for row in rows if row['panel_id']=='PC1')['name_review_required']='true'
            write_csv(p,['panel_id','region','location','name_review_required'],rows)
            _,candidates=mod.analyze(tree,m,p,j,None,False)
            row=next(item for item in candidates if item['candidate_taxon']=='Cirsium continental_candidate')
            self.assertEqual(row['name_review_required'],'true')

    def test_candidate_aggregates_source_provenance_by_taxon_and_region(self):
        tree=mod.NewickParser('((G1,G2),(C1,C2));').parse();index=mod.tip_index(tree)
        meta={
            'C1':{'analysis_taxon_label':'Cirsium candidate','region':'China','source_study':'Moreyra2025','name_review_required':'false'},
            'C2':{'analysis_taxon_label':'Cirsium candidate','region':'China','source_study':'Chang2026','name_review_required':'false'},
        }
        rows=mod.build_candidates(index,{'arenicola':{'G1','G2'}},set(index),meta)
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['tip_count'],'2')
        self.assertEqual(rows[0]['source_study'],'Chang2026|Moreyra2025')

if __name__=='__main__':unittest.main()
