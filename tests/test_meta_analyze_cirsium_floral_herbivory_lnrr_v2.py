import json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'analysis/meta_analyze_cirsium_floral_herbivory_lnrr_v2.py'
INPUT=ROOT/'data/evidence/cirsium_floral_herbivory_lnrr_effects_v2.csv'
FROZEN=ROOT/'data/evidence/cirsium_floral_herbivory_lnrr_meta_v2.json'

class MetaV2Test(unittest.TestCase):
    def test_rebuild(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'out.json'
            subprocess.run([sys.executable,str(SCRIPT),'--input',str(INPUT),'--output',str(out)],check=True)
            self.assertEqual(json.loads(out.read_text()),json.loads(FROZEN.read_text()))
    def test_result(self):
        d=json.loads(FROZEN.read_text())
        self.assertEqual(d['coverage']['effect_rows'],9)
        self.assertEqual(d['coverage']['independent_study_clusters'],4)
        m=d['random_effects']
        self.assertAlmostEqual(m['response_ratio'],2.673636515996,places=12)
        self.assertAlmostEqual(m['ambient_seed_output_reduction_fraction'],0.625977579968,places=12)
        self.assertLess(m['I2_percent'],5)
        self.assertGreater(m['ci95_response_ratio'][0],1)
        for x in d['leave_one_study_out']:
            self.assertGreater(x['ci95_response_ratio'][0],1)
if __name__=='__main__': unittest.main()
