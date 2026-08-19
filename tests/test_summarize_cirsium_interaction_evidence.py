import csv,json,subprocess,sys,tempfile,unittest
from pathlib import Path
REPO_ROOT=Path(__file__).resolve().parents[1]
SCRIPT=REPO_ROOT/'analysis'/'summarize_cirsium_interaction_evidence.py'
INPUT=REPO_ROOT/'data'/'evidence'/'cirsium_interaction_evidence_seed_v1.csv'
FROZEN=REPO_ROOT/'data'/'evidence'/'cirsium_interaction_evidence_summary_v1.json'
class CirsiumInteractionEvidenceTest(unittest.TestCase):
    def test_rebuild_matches_frozen_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'summary.json'
            subprocess.run([sys.executable,str(SCRIPT),'--input',str(INPUT),'--output',str(out)],check=True)
            self.assertEqual(json.loads(out.read_text()),json.loads(FROZEN.read_text()))
    def test_current_seed_has_decision_relevant_shape(self):
        rows=list(csv.DictReader(INPUT.open(encoding='utf-8',newline=''))); d=json.loads(FROZEN.read_text())
        self.assertEqual(len(rows),15)
        self.assertEqual(d['coverage']['independent_studies'],13)
        self.assertEqual(d['coverage']['taxa'],10)
        self.assertEqual(d['coverage']['direct_capitulum_rows'],13)
        self.assertEqual(d['interaction_domain_independent_studies']['pre_dispersal_seed_predation'],6)
        self.assertEqual(d['aim2_module_gate']['head_orientation']['direct_rows'],0)
        self.assertEqual(d['aim2_module_gate']['flower_colour']['direct_rows'],1)
        self.assertEqual(d['aim2_module_gate']['flower_colour']['fitness_rows'],0)
        self.assertEqual(d['aim2_module_gate']['involucre_spine']['direct_rows'],0)
        self.assertEqual(d['aim2_module_gate']['stickiness']['manipulative_rows'],1)
        self.assertEqual(d['fitness_coverage']['direct_trait_interaction_fitness_studies'],4)
        self.assertEqual(d['effect_size_meta_analysis_gate']['status'],'not_yet_authorized')
if __name__=='__main__': unittest.main()
