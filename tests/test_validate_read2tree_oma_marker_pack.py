import csv,io,importlib.util,sys,tarfile,tempfile,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'analysis'/'validate_read2tree_oma_marker_pack.py';spec=importlib.util.spec_from_file_location('markerpack',P);mod=importlib.util.module_from_spec(spec);sys.modules['markerpack']=mod;spec.loader.exec_module(mod)
def aa_seq(n=10):return 'M'+'A'*(n-1)
def dna_seq(n=10):return 'ATG'+'GCT'*(n-1)
class MarkerPackTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.manifest=self.root/'refs.csv';rows=[{'oma_release':'May2026','oma_code':'CYNCS','scientific_name':'Cynara cardunculus var. scolymus','ncbi_taxid':'59895','reference_role':'closest_cardueae_reference','verified_in_oma':'true','verification_url':'https://example/CYNCS'},{'oma_release':'May2026','oma_code':'HELAN','scientific_name':'Helianthus annuus','ncbi_taxid':'4232','reference_role':'asteraceae_reference','verified_in_oma':'true','verification_url':'https://example/HELAN'},{'oma_release':'May2026','oma_code':'DAUCS','scientific_name':'Daucus carota subsp. sativus','ncbi_taxid':'79200','reference_role':'campanulid_outgroup','verified_in_oma':'true','verification_url':'https://example/DAUCS'}]
        with self.manifest.open('w',newline='',encoding='utf-8') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    def tearDown(self):self.tmp.cleanup()
    def make_archive(self,marker_count=3,missing_dna=False,bad_code=False,bad_frame=False,unsafe=False):
        archive=self.root/'markers.tgz'
        with tarfile.open(archive,'w:gz') as tar:
            for idx in range(1,marker_count+1):
                marker=f'OMAGroup_{1000+idx}';aa=[];dna=[]
                for code in ('CYNCS','HELAN','DAUCS'):
                    actual='XXXXX' if bad_code and idx==1 and code=='DAUCS' else code;ident=f'{actual}{idx:05d}';aa += [f'>{ident} | OMA{1000+idx}',aa_seq()];seq=dna_seq()+('A' if bad_frame and idx==1 and code=='DAUCS' else '');dna += [f'>{ident} | OMA{1000+idx}',seq]
                for ext,text in [('.fa','\n'.join(aa)+'\n'),('.fna','\n'.join(dna)+'\n')]:
                    if missing_dna and idx==1 and ext=='.fna':continue
                    name=f'marker_genes/{marker}{ext}';name='../evil.fa' if unsafe and idx==1 and ext=='.fa' else name;data=text.encode();info=tarfile.TarInfo(name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
        return archive
    def run_valid(self,archive,count=3):return mod.validate_and_normalize(archive=archive,reference_manifest=self.manifest,outdir=self.root/'out',oma_release='May2026',export_date='2026-08-11',export_url='https://example/export',minimum_species_coverage=1.0,maximum_markers=count,expected_marker_count=count)
    def test_valid_pack_normalizes_and_hashes(self):
        c=self.run_valid(self.make_archive());self.assertTrue(c['execution_allowed']);self.assertEqual(c['reference_codes'],['CYNCS','HELAN','DAUCS']);self.assertEqual(c['marker_count'],3);self.assertTrue((self.root/'out'/'dna_ref.fa').is_file())
    def test_missing_paired_dna_fails(self):
        with self.assertRaises(ValueError):self.run_valid(self.make_archive(missing_dna=True))
    def test_wrong_reference_code_fails(self):
        with self.assertRaises(ValueError):self.run_valid(self.make_archive(bad_code=True))
    def test_frame_inconsistency_fails(self):
        with self.assertRaises(ValueError):self.run_valid(self.make_archive(bad_frame=True))
    def test_unsafe_member_fails(self):
        with self.assertRaises(ValueError):self.run_valid(self.make_archive(unsafe=True))
    def test_wrong_release_manifest_fails(self):
        with self.assertRaises(ValueError):mod.validate_reference_manifest(self.manifest,'Jul2024')
    def test_coverage_must_be_one(self):
        with self.assertRaises(ValueError):mod.validate_and_normalize(archive=self.make_archive(),reference_manifest=self.manifest,outdir=self.root/'x',oma_release='May2026',export_date='2026-08-11',export_url='',minimum_species_coverage=0.9,maximum_markers=3,expected_marker_count=3)
if __name__=='__main__':unittest.main()
