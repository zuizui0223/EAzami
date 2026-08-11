from __future__ import annotations
import importlib.util, sys, unittest
from pathlib import Path
MODULE=Path(__file__).resolve().parents[1]/"analysis"/"build_chang2026_hpc_pilot_bundle.py"; SPEC=importlib.util.spec_from_file_location("build_chang2026_hpc_pilot_bundle",MODULE); assert SPEC and SPEC.loader; mod=importlib.util.module_from_spec(SPEC); sys.modules[SPEC.name]=mod; SPEC.loader.exec_module(mod)
class BundleTests(unittest.TestCase):
    def test_selects_smallest_focal_resource_sample(self):
        panel=[]; resources=[]
        for i in range(6):
            sid=f"S{i}"; panel.append({"sample_id":sid,"morph":"BP" if i<3 else "W","taxon":"taxon"}); resources.append({"sample_id":sid,"execution_group":"takaoense6_pilot","estimated_working_disk_gib":str(10+i),"run":f"SRR{i}","library_layout":"PAIRED","spots":"10","paired_read_count":"20","bases":"100","gigabases":"0.1","sra_size_gib":"1","estimated_uncompressed_fastq_max_gib":"2"})
        chosen=mod.choose_pilot(panel,resources); self.assertEqual(chosen["sample_id"],"S0"); self.assertEqual(chosen["minimum_free_disk_gib_for_first_run"],25)
    def test_execution_script_preserves_inputs_and_runs_qc(self):
        text=mod.bash_script({"sample_id":"NH_ccy3835","minimum_free_disk_gib_for_first_run":50},"pilot.csv","resources.csv",slurm=False); self.assertIn("--preflight-only",text); self.assertIn("summarize_chang2026_transcriptome_qc.py",text); self.assertNotIn("--delete-raw-after-success",text); self.assertNotIn("--delete-sra-after-success",text)
if __name__=="__main__": unittest.main()
