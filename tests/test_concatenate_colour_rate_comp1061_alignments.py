from __future__ import annotations

import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/'analysis/concatenate_colour_rate_comp1061_alignments.py'
spec=importlib.util.spec_from_file_location('concat_mod',MOD); assert spec and spec.loader
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

class ConcatTests(unittest.TestCase):
    def test_concatenation_uses_saff_as_sole_reference(self):
        with tempfile.TemporaryDirectory() as td:
            r=Path(td); loci=[f'L{i:03d}' for i in range(100)]
            (r/'eligible.txt').write_text('\n'.join(loci)+'\n')
            with (r/'primary.csv').open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=['tip_id']);w.writeheader();w.writerows({'tip_id':f'T{i:02d}'} for i in range(20))
            aln=r/'aln';aln.mkdir()
            for j,loc in enumerate(loci):
                rows=[]
                for i in range(20):
                    if not (j==0 and i==19): rows.append((f'T{i:02d}','ATG'))
                rows.append(('OUTGROUP_saff','ATG'))
                with (aln/f'{loc}.aln.fasta').open('w') as f:
                    for h,s in rows:f.write(f'>{h}\n{s}\n')
            out=r/'concat.fa'; parts=r/'parts.csv'; summary=r/'summary.json'
            import sys
            old=sys.argv
            try:
                sys.argv=['x','--eligible-loci',str(r/'eligible.txt'),'--alignment-dir',str(aln),'--primary-runs',str(r/'primary.csv'),'--output',str(out),'--partitions',str(parts),'--summary',str(summary)]
                self.assertEqual(m.main(),0)
            finally:sys.argv=old
            text=out.read_text();self.assertIn('---',text);self.assertIn('>OUTGROUP_saff',text)
            self.assertNotIn('>OUTGROUP_lett',text);self.assertNotIn('>OUTGROUP_sunf',text)
            meta=json.loads(summary.read_text());self.assertEqual(meta['loci'],100);self.assertEqual(meta['alignment_length'],300)
            self.assertEqual(meta['root_outgroups'],['OUTGROUP_saff'])
            self.assertEqual(meta['reference_tips'],['OUTGROUP_saff'])
            self.assertEqual(meta['tree_tip_count'],21)

    def test_missing_saff_alignment_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            r=Path(td);loci=[f'L{i:03d}' for i in range(100)];(r/'eligible.txt').write_text('\n'.join(loci)+'\n')
            with (r/'primary.csv').open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=['tip_id']);w.writeheader();w.writerows({'tip_id':f'T{i:02d}'} for i in range(20))
            aln=r/'aln';aln.mkdir()
            for j,loc in enumerate(loci):
                with (aln/f'{loc}.aln.fasta').open('w') as f:
                    for i in range(20):f.write(f'>T{i:02d}\nATG\n')
                    if j!=0:f.write('>OUTGROUP_saff\nATG\n')
            import sys
            old=sys.argv
            try:
                sys.argv=['x','--eligible-loci',str(r/'eligible.txt'),'--alignment-dir',str(aln),'--primary-runs',str(r/'primary.csv'),'--output',str(r/'out'),'--partitions',str(r/'parts'),'--summary',str(r/'summary')]
                with self.assertRaisesRegex(ValueError,'OUTGROUP_saff'):m.main()
            finally:sys.argv=old

    def test_rejects_distant_reference_if_reintroduced(self):
        with tempfile.TemporaryDirectory() as td:
            r=Path(td); loci=[f'L{i:03d}' for i in range(100)]; (r/'eligible.txt').write_text('\n'.join(loci)+'\n')
            with (r/'primary.csv').open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=['tip_id']);w.writeheader();w.writerows({'tip_id':f'T{i:02d}'} for i in range(20))
            aln=r/'aln';aln.mkdir()
            for loc in loci:
                with (aln/f'{loc}.aln.fasta').open('w') as f:
                    for i in range(20):f.write(f'>T{i:02d}\nATG\n')
                    f.write('>OUTGROUP_saff\nATG\n>OUTGROUP_lett\nATG\n')
            import sys
            old=sys.argv
            try:
                sys.argv=['x','--eligible-loci',str(r/'eligible.txt'),'--alignment-dir',str(aln),'--primary-runs',str(r/'primary.csv'),'--output',str(r/'out'),'--partitions',str(r/'parts'),'--summary',str(r/'summary')]
                with self.assertRaisesRegex(ValueError,'unexpected alignment labels'):m.main()
            finally:sys.argv=old

    def test_rejects_under_100_loci(self):
        with tempfile.TemporaryDirectory() as td:
            r=Path(td);(r/'eligible.txt').write_text('L1\n')
            with (r/'p.csv').open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=['tip_id']);w.writeheader();w.writerow({'tip_id':'T'})
            import sys
            old=sys.argv
            try:
                sys.argv=['x','--eligible-loci',str(r/'eligible.txt'),'--alignment-dir',str(r),'--primary-runs',str(r/'p.csv'),'--output',str(r/'o'),'--partitions',str(r/'p'),'--summary',str(r/'s')]
                with self.assertRaisesRegex(ValueError,'<100'):m.main()
            finally:sys.argv=old

if __name__=='__main__':unittest.main()
