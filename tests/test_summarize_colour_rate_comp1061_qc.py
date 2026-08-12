from __future__ import annotations
import csv,importlib.util,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'analysis/summarize_colour_rate_comp1061_qc.py';S=importlib.util.spec_from_file_location('q',P);assert S and S.loader;m=importlib.util.module_from_spec(S);sys.modules[S.name]=m;S.loader.exec_module(m)
class T(unittest.TestCase):
 def test_synthetic_qc(self):
  with tempfile.TemporaryDirectory() as td:
   r=Path(td); runs=r/'runs.csv'; fields=['tip_id','data_type']; rows=[{'tip_id':f'T{i}','data_type':'leaf_rnaseq' if i<13 else 'target_capture'} for i in range(20)]
   with runs.open('w',newline='') as h:w=csv.DictWriter(h,fieldnames=fields);w.writeheader();w.writerows(rows)
   ld=r/'sets';ld.mkdir();
   for f,l in [('moreyra_public_1061_loci.txt',['L1','L2','L3']),('moreyra_reproducible_531_candidate_loci.txt',['L1','L2']),('moreyra_conservative_241_no_warning_loci.txt',['L1'])]:(ld/f).write_text(''.join(x+'\n' for x in l))
   rd=r/'dna';rd.mkdir();
   (rd/'L1.FNA').write_text(''.join(f'>T{i}\nACGT\n' for i in range(20)));(rd/'L2.FNA').write_text(''.join(f'>T{i}\nACGT\n' for i in range(16)));(rd/'L3.FNA').write_text(''.join(f'>T{i}\nACGT\n' for i in range(15)))
   pr=r/'p.tsv';genes=['Species','L1','L2','L3'];
   with pr.open('w',newline='') as h:w=csv.DictWriter(h,fieldnames=genes,delimiter='\t');w.writeheader();[w.writerow({'Species':f'T{i}','L1':1,'L2':2 if i==0 else 1,'L3':1}) for i in range(20)]
   q,s,e,x=m.analyse(runs,rd,pr,ld);self.assertEqual(e['conservative_241'],['L1']);self.assertEqual(e['reproducible_531'],['L1']);self.assertNotIn('L2',e['public_1061']);self.assertFalse(x['tree_matrix_auto_promotion_allowed']);self.assertEqual(x['minimum_present_tips'],16)
if __name__=='__main__':unittest.main()
