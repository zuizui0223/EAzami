import importlib.util, json, pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'analysis'/'diagnose_pollinator_regime_structure_v1.py'
TARGETS=ROOT/'data'/'evidence'/'capitulum_pattern_reduction_targets_v2.csv'
FROZEN=ROOT/'data'/'evidence'/'pollinator_regime_structure_v1.json'
spec=importlib.util.spec_from_file_location('poll_regime',SCRIPT); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
class PollinatorRegimeStructureTest(unittest.TestCase):
    def test_structure_ranking(self):
        observed=mod.run(TARGETS,draws=100000); frozen=json.loads(FROZEN.read_text(encoding='utf-8'))
        self.assertEqual(observed['ranking'],frozen['ranking'])
        for mode, vals in frozen['results'].items():
            self.assertAlmostEqual(observed['results'][mode]['best_distance'],vals['best_distance'],places=10)
        self.assertLess(observed['results']['YEAR_MEAN_YEAR_RATIO']['best_distance'],0.10)
        self.assertGreater(observed['results']['COMMON_MEAN_COMMON_RATIO']['best_distance'],0.40)
if __name__=='__main__': unittest.main()
