#!/usr/bin/env python3
"""Tests for the Chang 2026 heavy-workflow preflight contract."""

from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = REPO_ROOT / "analysis"
if str(ANALYSIS_DIR) not in sys.path: sys.path.insert(0, str(ANALYSIS_DIR))
import build_chang2026_gene_tree_panel as panel_builder  # noqa: E402
import validate_chang2026_gene_tree_workflow_contract as mod  # noqa: E402


class ChangGeneTreeWorkflowContractTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name); self.panel=self.root/"panel.csv"; self.hypotheses=self.root/"hypotheses.csv"; self.panel_rows=self._panel_rows(); self._write_csv(self.panel,self.panel_rows); self.hypothesis_rows=self._hypothesis_rows(); self._write_csv(self.hypotheses,self.hypothesis_rows); self.snakefile=REPO_ROOT/"workflow"/"chang2026_gene_trees"/"Snakefile"
    def tearDown(self): self.temp.cleanup()
    @staticmethod
    def _write_csv(path,rows):
        with path.open("w",encoding="utf-8",newline="") as h: w=csv.DictWriter(h,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    def _panel_rows(self):
        specs=[("C. japonicum var. takaoense","focal_colour_morph",6),("C. japonicum var. albescens","white_sister_control",2),("C. japonicum var. australe","coloured_flanking_introgression_control",3),("C. japonicum var. fukienense","coloured_flanking_introgression_control",4),("C. japonicum","coloured_root_context",2),("C. lineare","outgroup",2)]; focal=[("FC","ccy3559","BP"),("TJ","ccy3807","BP"),("NH","ccy3835","BP"),("WY","ccy3560","W"),("FB","ccy3629","W"),("LT","ccy3839","W")]; rows=[]; counter=0
        for taxon,role,count in specs:
            for within in range(count):
                counter+=1
                if role=="focal_colour_morph": code,voucher,morph=focal[within]
                else: code=f"S{counter:02d}"; voucher=f"ccy{8000+counter}"; morph=""
                run=f"SRR{counter:08d}"; rows.append({"sample_id":f"{code}_{voucher}","taxon":taxon,"code":code,"voucher":voucher,"morph":morph,"flower_colour_state":"white" if morph=="W" or "albescens" in taxon else "bluish-purple" if morph=="BP" else "coloured","panel_role":role,"matched_run":run,"matched_experiment":f"SRX{counter:08d}","matched_biosample":f"SAMN{counter:08d}","library_layout":"PAIRED","matched_spots":str(counter*1000),"read_count_relation":"exact_paired_end_raw_reads_equals_2x_spots" if counter<=9 else "not_matching_reported_raw_reads","run_match_status":"verified_unique_voucher_token","run_match_confidence":"verified","public_transcriptome_status":"not_recovered_by_current_ncbi_query","preferred_sequence_source":run,"tsa_accessions":"","assembly_accessions":"","de_novo_required":"true","analysis_panel":"sinocirsium17_plus_lineare2"})
        return rows
    def _hypothesis_rows(self):
        nearest=REPO_ROOT/"analysis"/"chang2026_takaoense_nearest_no_regain_topologies.csv"; summary=REPO_ROOT/"analysis"/"chang2026_takaoense_topology_robustness_summary.json"
        with nearest.open(encoding="utf-8-sig",newline="") as h: nearest_rows=list(csv.DictReader(h))
        return panel_builder.build_hypotheses(nearest_rows,json.loads(summary.read_text(encoding="utf-8")))
    def test_actual_snakefile_has_complete_ordered_dag(self):
        rules,runners,envs=mod.validate_workflow_files(self.snakefile); self.assertEqual(rules,list(mod.EXPECTED_RULES)); self.assertEqual(set(runners),set(mod.EXPECTED_RUNNERS)); self.assertEqual(set(envs),set(mod.EXPECTED_ENVS)); self.assertIn("run_chang2026_restartable_transcriptome_assembly.py",runners)
    def test_contract_accepts_nineteen_samples_and_eight_hypotheses(self):
        config,summary=mod.build_contract(self.panel,self.hypotheses,self.snakefile,self.root/"results"); self.assertEqual(summary["panel_rows"],19); self.assertEqual(summary["unique_official_runs"],19); self.assertEqual(summary["official_library_layout_counts"],{"PAIRED":19}); self.assertEqual(summary["focal_morph_counts"],{"BP":3,"W":3}); self.assertEqual(summary["hypothesis_count"],8); self.assertEqual(len(summary["outgroup_sample_ids"]),2); self.assertFalse(summary["heavy_computation_executed"]); self.assertEqual(summary["contract_version"],"chang2026_gene_tree_workflow_v3_restartable_sra"); self.assertIn("prefetch",summary["sra_execution_contract"]); self.assertIn("no --full_cleanup",summary["trinity_execution_contract"]); self.assertEqual(config["panel_csv"],str(self.panel.resolve()))
    def test_read_count_mismatch_does_not_invalidate_official_layout(self):
        config,summary=mod.build_contract(self.panel,self.hypotheses,self.snakefile,self.root/"results"); self.assertEqual(sum(r["read_count_relation"]=="not_matching_reported_raw_reads" for r in self.panel_rows),10); self.assertEqual(summary["official_library_layout_counts"],{"PAIRED":19}); self.assertTrue(config["panel_csv"].endswith("panel.csv"))
    def test_official_single_layout_fails_current_heavy_contract(self):
        rows=[dict(r) for r in self.panel_rows]; rows[0]["library_layout"]="SINGLE"; wrong=self.root/"single_layout.csv"; self._write_csv(wrong,rows)
        with self.assertRaisesRegex(ValueError,"not PAIRED"): mod.build_contract(wrong,self.hypotheses,self.snakefile,self.root/"results")
    def test_duplicate_hypothesis_topology_fails(self):
        rows=[dict(r) for r in self.hypothesis_rows]; rows[1]["topology_newick"]=rows[0]["topology_newick"]; duplicate=self.root/"duplicate.csv"; self._write_csv(duplicate,rows)
        with self.assertRaisesRegex(ValueError,"duplicate topologies"): mod.validate_hypothesis_contract(duplicate)
    def test_wrong_panel_role_count_fails(self):
        rows=[dict(r) for r in self.panel_rows]; rows[0]["panel_role"]="white_sister_control"; wrong=self.root/"roles.csv"; self._write_csv(wrong,rows)
        with self.assertRaisesRegex(ValueError,"Unexpected panel roles"): mod.build_contract(wrong,self.hypotheses,self.snakefile,self.root/"results")
    def test_rule_parser_rejects_missing_stage(self):
        observed=mod.extract_rule_names(self.snakefile.read_text(encoding="utf-8").replace("rule orthofinder:","# removed orthofinder:")); self.assertNotEqual(observed,list(mod.EXPECTED_RULES))


if __name__=="__main__": unittest.main()
