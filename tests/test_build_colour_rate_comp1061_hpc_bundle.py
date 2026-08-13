from __future__ import annotations
import importlib.util,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'analysis/build_colour_rate_comp1061_hpc_bundle.py'; S=importlib.util.spec_from_file_location('hpc',P); assert S and S.loader
m=importlib.util.module_from_spec(S); sys.modules[S.name]=m; S.loader.exec_module(m)
B=ROOT/'data/evidence/colour_rate_comp1061_bridge_artifact_contract_v1.json'; L=ROOT/'data/evidence/moreyra_public_locus_set_manifest_v1.json'
class T(unittest.TestCase):
 def test_contract(self): self.assertEqual(len(m.validate(m.load(B),m.load(L))),20)
 def test_bundle(self):
  with tempfile.TemporaryDirectory() as td:
   out=Path(td); old=sys.argv; sys.argv=['x','--bridge-contract',str(B),'--locus-manifest',str(L),'--outdir',str(out)]
   try:m.main()
   finally:sys.argv=old
   x=json.loads((out/'execution_manifest.json').read_text()); self.assertFalse(x['branch_length_tree_completed']); self.assertFalse(x['rate_fit_execution_allowed']); self.assertEqual(x['primary_mapping'],'bwa')
   self.assertIn('--bwa',(out/'02_hybpiper_bwa_slurm.sh').read_text()); self.assertNotIn('--bwa',(out/'02b_hybpiper_blastx_slurm.sh').read_text())
   self.assertIn('--no_intronerate',(out/'02_hybpiper_bwa_slurm.sh').read_text()); self.assertEqual(sum(1 for _ in (out/'primary_runs.csv').open())-1,20)
if __name__=='__main__': unittest.main()
