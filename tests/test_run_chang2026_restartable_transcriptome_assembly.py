from __future__ import annotations

import csv
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ANALYSIS = Path(__file__).resolve().parents[1] / "analysis"
if str(ANALYSIS) not in sys.path: sys.path.insert(0, str(ANALYSIS))
MODULE = ANALYSIS / "run_chang2026_restartable_transcriptome_assembly.py"
SPEC = importlib.util.spec_from_file_location("run_chang2026_restartable_transcriptome_assembly", MODULE); assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC); sys.modules[SPEC.name] = mod; SPEC.loader.exec_module(mod)


class RestartableRunnerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.root = Path(self.tmp.name); self.panel = self.root / "pilot.csv"
        fields = ["sample_id","taxon","morph","panel_role","matched_run","library_layout","run_match_confidence","preferred_sequence_source","de_novo_required"]
        rows=[]
        for i in range(6):
            run=f"SRR{i+1:08d}"; rows.append({"sample_id":f"S{i+1}","taxon":"C. japonicum var. takaoense","morph":"BP" if i<3 else "W","panel_role":"focal_colour_morph","matched_run":run,"library_layout":"PAIRED","run_match_confidence":"verified","preferred_sequence_source":run,"de_novo_required":"true"})
        with self.panel.open("w",encoding="utf-8",newline="") as h: w=csv.DictWriter(h,fieldnames=fields); w.writeheader(); w.writerows(rows)
    def tearDown(self): self.tmp.cleanup()
    def plan(self):
        row=mod.validate_panel(self.panel,expected_samples=6)[0]
        return mod.command_plan(row,outdir=self.root/"results",fasterq_threads=8,fastp_threads=8,trinity_threads=16,trinity_memory_gb=96,python_executable="python",prefix_script=self.root/"prefix.py")
    def test_six_sample_contract_and_selection(self):
        rows=mod.validate_panel(self.panel,expected_samples=6); self.assertEqual(len(rows),6); self.assertEqual([r["sample_id"] for r in mod.select_rows(rows,["S4"])],["S4"])
    def test_commands_fix_dry_run_only_execution_gaps(self):
        plan=self.plan(); self.assertIn("--max-size",plan["commands"]["prefetch"]); self.assertEqual(plan["commands"]["vdb_validate"][0],"vdb-validate"); self.assertIn("-e",plan["commands"]["fasterq"]); self.assertIn("-t",plan["commands"]["fasterq"]); self.assertNotIn("--threads",plan["commands"]["fasterq"]); self.assertNotIn("--skip-technical",plan["commands"]["fasterq"]); self.assertNotIn("--full_cleanup",plan["commands"]["trinity"]); self.assertTrue(str(plan["trinity_fasta"]).endswith("/trinity/Trinity.fasta"))
    def test_dry_run_calls_no_external_program(self):
        plan=self.plan(); plan["commands"]={stage:["DO_NOT_EXECUTE"] for stage in mod.STAGES}; result=mod.execute_one(plan,dry_run=True,force=False,delete_raw_after_success=False,delete_sra_after_success=False); self.assertEqual(result["status"],"planned_dry_run")
    def test_partial_fastq_pair_is_rejected(self):
        plan=self.plan(); sra=Path(plan["sra_dir"]); sra.mkdir(parents=True); mod.mark_done(plan,"prefetch"); mod.mark_done(plan,"vdb_validate"); raw1=Path(plan["raw_read_1"]); raw1.parent.mkdir(parents=True); raw1.write_bytes(b"x")
        result=mod.execute_one(plan,dry_run=False,force=False,delete_raw_after_success=False,delete_sra_after_success=False); self.assertEqual(result["status"],"failed"); self.assertIn("Partial paired FASTQ state",result["error"])


if __name__ == "__main__": unittest.main()
