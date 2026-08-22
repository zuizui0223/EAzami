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
    def test_241_universe_intersects_occupancy_with_required_saff_root(self):
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
                if j<100: target_rows.append((f'saff-{loc}','ATGAAA'))
                n=16 if j<120 else 15
                fasta(retrieved/f'{loc}.FNA',[(f'T{i:02d}', 'ATGAAA') for i in range(n)])
            fasta(target,target_rows)
            out=r/'out'
            result=m.build(primary,locus_file,retrieved,target,out,0.8)
            self.assertEqual(result['eligible_loci'],100)
            self.assertEqual(result['tree_reference_tips'],['OUTGROUP_saff'])
            self.assertEqual(result['required_root_references'],['OUTGROUP_saff'])
            self.assertEqual(result['audited_distant_reference_tips'],['OUTGROUP_lett','OUTGROUP_sunf'])
            self.assertFalse(result['distant_references_included_in_tree'])
            self.assertEqual(result['tree_tip_count_if_complete'],21)
            self.assertTrue(result['tree_input_ready'])
            self.assertEqual(len((out/'eligible_loci.txt').read_text().splitlines()),100)
            tree_input=(out/'loci_unaligned/L000.fasta').read_text()
            self.assertIn('>OUTGROUP_saff',tree_input)
            self.assertNotIn('>OUTGROUP_lett',tree_input)
            self.assertNotIn('>OUTGROUP_sunf',tree_input)

    def test_accepts_current_subset_of_100_when_saff_present(self):
        with tempfile.TemporaryDirectory() as td:
            r=Path(td);primary=r/'p.csv'
            with primary.open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=['tip_id','accepted_taxon']);w.writeheader();w.writerows({'tip_id':f'T{i:02d}','accepted_taxon':f'X{i}'} for i in range(20))
            loci=[f'L{i:03d}' for i in range(100)];(r/'l.txt').write_text('\n'.join(loci)+'\n');(r/'retr').mkdir();target=[]
            for loc in loci:
                target += [(f'lett-{loc}','ATGAAA'),(f'sunf-{loc}','ATGAAA'),(f'saff-{loc}','ATGAAA')]
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
            for j,loc in enumerate(loci):
                target += [(f'lett-{loc}','ATGAAA'),(f'sunf-{loc}','ATGAAA'),(f'saff-{loc}','ATGAAA')]
                n=16 if j<99 else 15
                fasta(r/'retr'/f'{loc}.FNA',[(f'T{i:02d}','ATGAAA') for i in range(n)])
            fasta(r/'target.fa',target)
            with self.assertRaisesRegex(ValueError,'Only 99'):
                m.build(primary,r/'l.txt',r/'retr',r/'target.fa',r/'o',0.8)

    def test_missing_saff_root_reference_blocks_locus(self):
        with tempfile.TemporaryDirectory() as td:
            r=Path(td); primary=r/'p.csv'
            with primary.open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=['tip_id','accepted_taxon']);w.writeheader();w.writerows({'tip_id':f'T{i:02d}','accepted_taxon':f'X{i}'} for i in range(20))
            loci=[f'L{i:03d}' for i in range(241)];(r/'l.txt').write_text('\n'.join(loci)+'\n');(r/'retr').mkdir()
            target=[]
            for j,loc in enumerate(loci):
                target += [(f'lett-{loc}','ATGAAA'),(f'sunf-{loc}','ATGAAA')]
                if j!=0: target.append((f'saff-{loc}','ATGAAA'))
                fasta(r/'retr'/f'{loc}.FNA',[(f'T{i:02d}','ATGAAA') for i in range(20)])
            fasta(r/'target.fa',target)
            result=m.build(primary,r/'l.txt',r/'retr',r/'target.fa',r/'o',0.8)
            self.assertEqual(result['eligible_loci'],240)
            rows=list(csv.DictReader((r/'o/locus_manifest.csv').open()))
            self.assertEqual(rows[0]['reason'],'required_close_root_reference_missing_or_nonunique')

if __name__=='__main__': unittest.main()
