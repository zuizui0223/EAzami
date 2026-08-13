from __future__ import annotations
import csv, importlib.util, json, sys, tempfile, unittest
from pathlib import Path
MODULE=Path(__file__).resolve().parents[1]/"analysis"/"summarize_chang2026_transcriptome_qc.py"; SPEC=importlib.util.spec_from_file_location("summarize_chang2026_transcriptome_qc",MODULE); assert SPEC and SPEC.loader; mod=importlib.util.module_from_spec(SPEC); sys.modules[SPEC.name]=mod; SPEC.loader.exec_module(mod)
class QcTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name); self.panel=self.root/"panel.csv"; self.results=self.root/"results"; row={"sample_id":"NH_ccy3835","taxon":"C. japonicum var. takaoense","morph":"BP","matched_run":"SRR35152735","matched_spots":"2"}
        with self.panel.open("w",newline="",encoding="utf-8") as h: w=csv.DictWriter(h,fieldnames=list(row)); w.writeheader(); w.writerow(row)
        root=self.results/"samples"/"NH_ccy3835"; (root/"trimmed").mkdir(parents=True); (root/"trinity").mkdir(); (root/"transdecoder").mkdir(); (root/"resources").mkdir(); (self.results/"prefixed_proteomes").mkdir()
        fastp={"summary":{"before_filtering":{"total_reads":4},"after_filtering":{"total_reads":4,"q20_rate":0.99,"q30_rate":0.95,"gc_content":0.42}}}; (root/"trimmed"/"NH_ccy3835.fastp.json").write_text(json.dumps(fastp)); (root/"trinity"/"Trinity.fasta").write_text(">t1\nAAAA\n>t2\nAAAAAA\n"); (root/"transdecoder"/"Trinity.fasta.transdecoder.pep").write_text(">p1\n"+"M"*120+"\n>p2\n"+"M"*80+"\n"); (self.results/"prefixed_proteomes"/"NH_ccy3835.faa").write_text(">NH_ccy3835|p1\nMMMM\n"); (root/"resources"/"trinity.time.txt").write_text("Elapsed (wall clock) time (h:mm:ss or m:ss): 1:02.50\nMaximum resident set size (kbytes): 1048576\n")
    def tearDown(self): self.tmp.cleanup()
    def test_n50_and_mechanical_gate(self):
        self.assertEqual(mod.n50([4,6]),6); meta=mod.expected_index(self.panel,None)["NH_ccy3835"]; row=mod.summarize_sample(meta,self.results); self.assertTrue(row["mechanical_gate_pass"]); self.assertEqual(row["fastp_before_reads"],4); self.assertEqual(row["transcript_count"],2); self.assertEqual(row["peptides_ge_100aa"],1); self.assertEqual(row["trinity_peak_rss_gib"],1.0); self.assertAlmostEqual(row["trinity_elapsed_seconds"],62.5)
    def test_wrong_read_count_fails(self):
        p=self.results/"samples"/"NH_ccy3835"/"trimmed"/"NH_ccy3835.fastp.json"; data=json.loads(p.read_text()); data["summary"]["before_filtering"]["total_reads"]=3; p.write_text(json.dumps(data)); row=mod.summarize_sample(mod.expected_index(self.panel,None)["NH_ccy3835"],self.results); self.assertFalse(row["mechanical_gate_pass"]); self.assertIn("neq_expected",row["gate_fail_reasons"])
if __name__=="__main__": unittest.main()
