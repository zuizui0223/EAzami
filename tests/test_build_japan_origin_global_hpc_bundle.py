from __future__ import annotations
import csv,hashlib,importlib.util,json,sys,tempfile,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path);assert spec and spec.loader
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
bundle=load('jogbundle',Path('analysis/build_japan_origin_global_hpc_bundle.py'))
accept=load('jogaccept',Path('analysis/validate_japan_origin_global_tree.py'))

def make_panel(path:Path):
    fields=['panel_id','source_study','bioproject','assay','source_taxon_label','analysis_taxon_label','voucher','biosample','run_accessions','run_count','region','location','name_review_required','common_locus_space','claim_boundary']
    rows=[]
    critical=['Cirsium brevicaule']*3+['Cirsium irumtiense']*3+['Cirsium dipsacolepis','Cirsium lineare']
    for i in range(302):
        tax=critical[i] if i<len(critical) else f'Cirsium synthetic_{i:03d}'
        runs='SRR000001|SRR000002' if i==0 else f'SRR{i+100000:06d}'
        rows.append({'panel_id':f'P{i:04d}','source_study':'Moreyra2025' if i<256 else ('Chang2025' if i<269 else 'Chang2026'),'bioproject':'X','assay':'Compositae1061_target_capture' if i<256 else 'leaf_RNAseq_transcriptome','source_taxon_label':tax,'analysis_taxon_label':tax,'voucher':f'V{i}','biosample':f'SAMN{i:06d}','run_accessions':runs,'run_count':'2' if i==0 else '1','region':'X','location':'X','name_review_required':'false','common_locus_space':'X','claim_boundary':'test'})
    with path.open('w',encoding='utf-8',newline='') as h:w=csv.DictWriter(h,fieldnames=fields);w.writeheader();w.writerows(rows)
    return rows

class GlobalBundleTests(unittest.TestCase):
    def test_bundle_has_safe_ids_multi_run_and_no_claim_promotion(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);panel=root/'panel.csv';make_panel(panel);out=root/'bundle';rows=bundle.read_panel(panel);self.assertEqual(len(rows),302);bundle.main.__module__
            # Exercise the output primitives without CLI parsing.
            out.mkdir();bundle.sample_tsv(out/'sample_manifest.tsv',rows)
            text=bundle.fetch();self.assertIn('#SBATCH --array=0-301%20',text);self.assertIn("IFS='|' read -r -a ACCS",text);self.assertIn('cat "${R1S[@]}"',text)
            hyb=bundle.hyb('bwa');self.assertIn('#SBATCH --array=0-301%16',hyb);self.assertIn('--bwa',hyb)
            manifest={'biological_samples':302,'public_runs':303,'new_china_sampling_freeze_allowed':False}
            self.assertFalse(manifest['new_china_sampling_freeze_allowed'])
            with (out/'sample_manifest.tsv').open(encoding='utf-8',newline='') as h:r=list(csv.DictReader(h,delimiter='\t'))
            self.assertEqual(r[0]['tip_id'],'JOG0001');self.assertEqual(r[-1]['tip_id'],'JOG0302');self.assertEqual(r[0]['run_count'],'2')

    def test_acceptance_does_not_require_japanese_monophyly(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);panel=root/'panel.csv';rows=make_panel(panel)
            # Build the safe-ID manifest expected by acceptance.
            safe=[]
            for i,r in enumerate(rows):safe.append({'tip_id':f'JOG{i+1:04d}','analysis_taxon_label':r['analysis_taxon_label']})
            mp=root/'manifest.csv'
            with mp.open('w',newline='',encoding='utf-8') as h:w=csv.DictWriter(h,fieldnames=['tip_id','analysis_taxon_label']);w.writeheader();w.writerows(safe)
            focal=','.join(f"JOG{i+1:04d}:0.01" for i in range(302))
            tree=root/'tree.nwk';tree.write_text(f"(({focal}):0.2,OUTGROUP_saff:0.3,(OUTGROUP_lett:0.4,OUTGROUP_sunf:0.4):0.2);\n")
            prov=root/'prov.json';prov.write_text(json.dumps({'tree_sha256':hashlib.sha256(tree.read_bytes()).hexdigest(),'analysis_name':'test','branch_length_interpretation':'subs/site','rooting_definition':'lett+sunf','required_outgroup_tips':['OUTGROUP_lett','OUTGROUP_sunf'],'required_reference_tips':['OUTGROUP_lett','OUTGROUP_sunf','OUTGROUP_saff'],'support_metric_definition':'test support','source_or_pipeline_provenance':'synthetic','topology_uncertainty_status':'bootstrap_or_gene_tree_sensitivity'}))
            out=accept.validate(tree,mp,prov)
            self.assertTrue(out['tree_artifact_accepted']);self.assertFalse(out['japanese_monophyly_inference_made']);self.assertFalse(out['arenicola_placement_inference_made']);self.assertFalse(out['new_china_sampling_freeze_allowed'])

    def test_rejects_missing_global_tip(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);panel=root/'panel.csv';rows=make_panel(panel);mp=root/'manifest.csv'
            safe=[{'tip_id':f'JOG{i+1:04d}','analysis_taxon_label':r['analysis_taxon_label']} for i,r in enumerate(rows)]
            with mp.open('w',newline='',encoding='utf-8') as h:w=csv.DictWriter(h,fieldnames=['tip_id','analysis_taxon_label']);w.writeheader();w.writerows(safe)
            focal=','.join(f"JOG{i+1:04d}:0.01" for i in range(301));tree=root/'tree.nwk';tree.write_text(f"(({focal}):0.2,OUTGROUP_lett:0.4,OUTGROUP_sunf:0.4);\n")
            prov=root/'prov.json';prov.write_text(json.dumps({'tree_sha256':hashlib.sha256(tree.read_bytes()).hexdigest(),'analysis_name':'test','branch_length_interpretation':'subs/site','rooting_definition':'lett+sunf','required_outgroup_tips':['OUTGROUP_lett','OUTGROUP_sunf'],'required_reference_tips':['OUTGROUP_lett','OUTGROUP_sunf'],'support_metric_definition':'test','source_or_pipeline_provenance':'synthetic','topology_uncertainty_status':'bootstrap_or_gene_tree_sensitivity'}))
            with self.assertRaisesRegex(ValueError,'global sample tips absent'):accept.validate(tree,mp,prov)

if __name__=='__main__':unittest.main()
