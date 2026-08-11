import csv, tempfile, unittest, importlib.util, sys
from pathlib import Path

P=Path(__file__).resolve().parents[1]/'analysis'/'build_chang2026_read2tree_pilot.py'
spec=importlib.util.spec_from_file_location('r2tplan',P); mod=importlib.util.module_from_spec(spec); sys.modules['r2tplan']=mod; spec.loader.exec_module(mod)

class Read2TreePilotTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory(); self.root=Path(self.t.name)
        self.panel=self.root/'panel.csv'; self.refs=self.root/'refs.csv'
        rows=[]
        focal=[('FC','ccy3559','BP'),('TJ','ccy3807','BP'),('NH','ccy3835','BP'),('WY','ccy3560','W'),('FB','ccy3629','W'),('LT','ccy3839','W')]
        for i,(code,voucher,morph) in enumerate(focal,1):
            rows.append({'sample_id':f'{code}_{voucher}','matched_run':f'SRR{i:08d}','library_layout':'PAIRED','panel_role':'focal_colour_morph','morph':morph})
        with self.panel.open('w',newline='',encoding='utf-8') as h:
            w=csv.DictWriter(h,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
        refs=[
            {'oma_code':'CYNCS','scientific_name':'Cynara cardunculus var. scolymus','reference_role':'closest_cardueae_reference','verified_in_oma':'true'},
            {'oma_code':'HELAN','scientific_name':'Helianthus annuus','reference_role':'asteraceae_reference','verified_in_oma':'true'},
            {'oma_code':'DAUCS','scientific_name':'Daucus carota subsp. sativus','reference_role':'campanulid_outgroup','verified_in_oma':'true'},
        ]
        with self.refs.open('w',newline='',encoding='utf-8') as h:
            w=csv.DictWriter(h,fieldnames=list(refs[0])); w.writeheader(); w.writerows(refs)
    def tearDown(self): self.t.cleanup()
    def test_panel(self):
        rows=mod.validate_panel(self.panel); self.assertEqual(len(rows),6)
    def test_plan(self):
        rows=mod.validate_panel(self.panel); plan,s=mod.build_plan(rows,reads_root=self.root/'reads',reads_stage='trimmed',marker_dir=self.root/'markers',dna_reference=self.root/'dna.fa',output_dir=self.root/'out')
        self.assertEqual(len(plan),9); self.assertEqual(sum(x['stage']=='2map' for x in plan),6); self.assertEqual(s['morph_counts'],{'BP':3,'W':3})
        nh=[x for x in plan if x['sample_id']=='NH_ccy3835'][0]
        self.assertIn('--species_name NH_ccy3835',nh['command']); self.assertIn("--read_type '-ax sr'",nh['command'])
        self.assertIn('concat_merge_dna.phy', plan[-1]['command'])
    def test_refs(self): self.assertEqual([r['oma_code'] for r in mod.validate_reference_manifest(self.refs)],['CYNCS','HELAN','DAUCS'])
    def test_wrong_morphs_fail(self):
        rows=mod.read_csv(self.panel); rows[-1]['morph']='BP'
        bad=self.root/'bad.csv'
        with bad.open('w',newline='',encoding='utf-8') as h:
            w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
        with self.assertRaises(ValueError): mod.validate_panel(bad)

if __name__=='__main__': unittest.main()
