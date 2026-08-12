from __future__ import annotations

import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/'analysis/prepare_colour_rate_comp1061_tree_inputs.py'
spec=importlib.util.spec_from_file_location('tree_inputs',MOD); assert spec and spec.loader
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


def fasta(path:Path, rows):
    with path.open('w') as f:
        for h,s in rows: f.write(f'>{h}\n{s}\n')

class TreeInputsTests(unittest.TestCase):
    def test_241_universe_filters_by_current_occupancy_and_records_saff_coverage(self):
        with tempfile.TemporaryDirectory() as td:
            r=Path(td)
            primary=r/'primary.csv'
            fields=['tip_id','accepted_taxon']
            with primary.open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({'tip_id':f'T{i:02d}','accepted_taxon':f'Taxon {i:02d}'} for i in range(20))
            loci=[f'L{i:03d}' for i in range(241)]
            locus_file=r/'loci.txt';locus_file.write_text('\n'.join(loci)+'\n')
            retrieved=r/'retrieved';retrieved.mkdir()
            target=r/'target.fa'
            target_rows=[]
            for j,loc in enumerate(loci):
                target_rows += [(f'lett-{loc}','ATGAAA'),(f'sunf-{loc}','ATGAAA')]
                if j<50: target_rows.append((f'saff-{loc}','ATGAAA'))
                n=16 if int(loc[1:])<120 else 15
                fasta(retrieved/f'{loc}.FNA',[(f'T{i:02d}', 'ATGAAA') for i in range(n)])
            fasta(target,target_rows)
            out=r/'out'
            result=m.build(primary,locus_file,retrieved,target,out,0.8)
            self.assertEqual(result['eligible_loci'],120)
            self.assertEqual(result['eligible_loci_with_saff_reference'],50)
            self.assertEqual(result['required_root_references'],['OUTGROUP_lett','OUTGROUP_sunf'])
            self.assertEqual(result['optional_near_reference'],'OUTGROUP_saff')
            self.assertTrue(result['tree_input_ready'])
            self.assertEqual(len((out/'eligible_loci.txt').read_text().splitlines()),120)

    def test_accepts_current_subset_smaller_than_241(self):
        with tempfile.TemporaryDirectory() as td:
            r=Path(td);primary=r/'p.csv'
            with primary.open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=['tip_id','accepted_taxon']);w.writeheader();w.writerows({'tip_id':f'T{i:02d}','accepted_taxon':f'X{i}'} for i in range(20))
            loci=[f'L{i:03d}' for i in range(100)];(r/'l.txt').write_text('\n'.join(loci)+'\n');(r/'retr').mkdir();target=[]
            for loc in loci:
                target += [(f'lett-{loc}','ATGAAA'),(f'sunf-{loc}','ATGAAA')]
                fasta(r/'retr'/f'{loc}.FNA',[(f'T{i:02d}','ATGAAA') for i in range(20)])
            fasta(r/'target.fa',target)
            result=m.build(primary,r/'l.txt',r/'retr',r/'target.fa',r/'o',0.8)
            self.assertEqual(result['supplied_current_locus_count'],100)
            self.assertEqual(result['eligible_loci'],100)

    def test_requires_100_eligible_loci(self):
        with tempfile.TemporaryDirectory() as td:
            r=Path(td); primary=r/'p.csv'
            with primary.open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=['tip_id','accepted_taxon']);w.writeheader();w.writerows({'tip_id':f'T{i:02d}','accepted_taxon':f'X{i}'} for i in range(20))
            loci=[f'L{i:03d}' for i in range(241)]; (r/'l.txt').write_text('\n'.join(loci)+'\n'); (r/'retr').mkdir()
            target=[]
            for loc in loci:
                target += [(f'lett-{loc}','ATGAAA'),(f'sunf-{loc}','ATGAAA')]
                n=16 if int(loc[1:])<99 else 15
                fasta(r/'retr'/f'{loc}.FNA',[(f'T{i:02d}','ATGAAA') for i in range(n)])
            fasta(r/'target.fa',target)
            with self.assertRaisesRegex(ValueError,'Only 99'):
                m.build(primary,r/'l.txt',r/'retr',r/'target.fa',r/'o',0.8)

    def test_missing_root_reference_blocks_locus(self):
        with tempfile.TemporaryDirectory() as td:
            r=Path(td); primary=r/'p.csv'
            with primary.open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=['tip_id','accepted_taxon']);w.writeheader();w.writerows({'tip_id':f'T{i:02d}','accepted_taxon':f'X{i}'} for i in range(20))
            loci=[f'L{i:03d}' for i in range(241)];(r/'l.txt').write_text('\n'.join(loci)+'\n');(r/'retr').mkdir()
            target=[]
            for j,loc in enumerate(loci):
                target.append((f'lett-{loc}','ATGAAA'))
                if j!=0: target.append((f'sunf-{loc}','ATGAAA'))
                fasta(r/'retr'/f'{loc}.FNA',[(f'T{i:02d}','ATGAAA') for i in range(20)])
            fasta(r/'target.fa',target)
            result=m.build(primary,r/'l.txt',r/'retr',r/'target.fa',r/'o',0.8)
            self.assertEqual(result['eligible_loci'],240)

if __name__=='__main__': unittest.main()
