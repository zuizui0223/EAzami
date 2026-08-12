from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/'analysis/augment_colour_rate_comp1061_tree_stages.py'
spec=importlib.util.spec_from_file_location('augment_tree',MOD); assert spec and spec.loader
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

class AugmentTests(unittest.TestCase):
    def test_augments_qc_bundle_without_claiming_tree_complete(self):
        with tempfile.TemporaryDirectory() as td:
            b=Path(td)
            (b/'execution_manifest.json').write_text(json.dumps({'bundle_version':'v0.2','current_stage_end':'retrieve_stats_paralog_qc','branch_length_tree_completed':False,'rate_fit_execution_allowed':False}))
            import sys
            old=sys.argv
            try:
                sys.argv=['x','--bundle-dir',str(b)];m.main()
            finally:sys.argv=old
            manifest=json.loads((b/'execution_manifest.json').read_text())
            self.assertEqual(manifest['bundle_version'],'colour_rate_comp1061_hpc_bundle_v0_3_tree_stage')
            self.assertEqual(manifest['current_stage_end'],'tree_acceptance_scripts_prepared')
            self.assertFalse(manifest['branch_length_tree_completed'])
            self.assertFalse(manifest['rate_fit_execution_allowed'])
            self.assertIn('paralog',manifest['tree_stage']['current_paralog_gate'])
            self.assertEqual(manifest['tree_stage']['root_outgroups'],['OUTGROUP_lett','OUTGROUP_sunf'])
            self.assertIn('OUTGROUP_saff',manifest['tree_stage']['optional_near_reference'])
            for name in ('04_prepare_tree_inputs_slurm.sh','05_align_loci_slurm.sh','06_gene_trees_slurm.sh','07_concat_tree_slurm.sh','08_accept_tree_slurm.sh','submit_tree_chain.sh'):
                self.assertTrue((b/name).is_file(),name)
            prep=(b/'04_prepare_tree_inputs_slurm.sh').read_text()
            self.assertIn('summarize_colour_rate_comp1061_qc.py',prep)
            self.assertIn('current_conservative_241_loci.txt',prep)
            self.assertIn('paralog_report',prep)
            self.assertIn('N_CURRENT < 100',prep)
            accept=(b/'08_accept_tree_slurm.sh').read_text()
            self.assertIn('validate_colour_atlas_branch_length_tree.py',accept)
            self.assertIn('tree_route',accept)
            self.assertIn("root_outgroups=concat['root_outgroups']",accept)
            self.assertIn("references=concat['reference_tips']",accept)
            self.assertIn("'required_outgroup_tips':root_outgroups",accept)
            self.assertIn("'required_reference_tips':references",accept)
            self.assertIn('optional OUTGROUP_saff retained as a near Cardueae reference',accept)
            self.assertIn('zero current focal paralog warnings',accept)
            self.assertIn('export BUNDLE_DIR REPO_ROOT RESULT_ROOT ENV_PREFIX MODE',accept)

    def test_rejects_wrong_upstream_stage(self):
        with tempfile.TemporaryDirectory() as td:
            b=Path(td);(b/'execution_manifest.json').write_text(json.dumps({'current_stage_end':'not_qc'}))
            import sys
            old=sys.argv
            try:
                sys.argv=['x','--bundle-dir',str(b)]
                with self.assertRaisesRegex(ValueError,'Expected v0.2 QC-stage bundle'):m.main()
            finally:sys.argv=old

if __name__=='__main__':unittest.main()
