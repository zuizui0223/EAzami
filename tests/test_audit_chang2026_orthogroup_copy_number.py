from __future__ import annotations
import csv,importlib.util,sys,tempfile,unittest
from pathlib import Path
MODULE=Path(__file__).resolve().parents[1]/"analysis"/"audit_chang2026_orthogroup_copy_number.py"; SPEC=importlib.util.spec_from_file_location("audit_chang2026_orthogroup_copy_number",MODULE); assert SPEC and SPEC.loader; mod=importlib.util.module_from_spec(SPEC); sys.modules[SPEC.name]=mod; SPEC.loader.exec_module(mod)
class CopyAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name); self.panel=self.root/"panel.csv"; rows=[{"sample_id":f"S{i:02d}","panel_role":"focal_colour_morph" if i<=6 else "control"} for i in range(1,20)]
        with self.panel.open("w",newline="",encoding="utf-8") as h: w=csv.DictWriter(h,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
        result=self.root/"Results_x"; (result/"Orthogroups").mkdir(parents=True); (result/"Orthogroups"/"Orthogroups_SingleCopyOrthologues.txt").write_text("OG0001\n"); self.seq=result/"Orthogroup_Sequences"; self.seq.mkdir()
    def tearDown(self): self.tmp.cleanup()
    def write(self,name,counts):
        with (self.seq/f"{name}.fa").open("w") as h:
            for sample,count in counts.items():
                for copy in range(count): h.write(f">{sample}|g{copy}\nMPEP\n")
    def test_copy_classes_preserve_focal_multicopy_as_unresolved(self):
        all1={f"S{i:02d}":1 for i in range(1,20)}; self.write("OG0001",all1); control=all1.copy(); control["S10"]=2; self.write("OG0002",control); focal=all1.copy(); focal["S01"]=2; self.write("OG0003",focal); missing=all1.copy(); missing["S02"]=0; self.write("OG0004",missing)
        rows,summary=mod.audit(self.root,self.panel); states={r["orthogroup_id"]:r["status"] for r in rows}; self.assertEqual(states["OG0001"],"strict_complete_one_copy"); self.assertEqual(states["OG0002"],"focal_one_copy_control_multicopy"); self.assertEqual(states["OG0003"],"focal_multicopy"); self.assertEqual(states["OG0004"],"focal_missing"); self.assertEqual(summary["focal_multicopy_count"],1); self.assertIn("never choose one focal homeolog",summary["copy_aware_sensitivity_rule"])
if __name__=="__main__": unittest.main()
