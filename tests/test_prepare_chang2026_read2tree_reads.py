from __future__ import annotations

import csv
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ANALYSIS = REPO / "analysis"
if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))
MODULE = ANALYSIS / "prepare_chang2026_read2tree_reads.py"
SPEC = importlib.util.spec_from_file_location("prepare_chang2026_read2tree_reads", MODULE)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


class Read2TreeReadPrepTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.panel = self.root / "pilot.csv"
        fields = [
            "sample_id", "taxon", "morph", "panel_role", "matched_run",
            "library_layout", "run_match_confidence", "preferred_sequence_source",
            "de_novo_required",
        ]
        rows = []
        for i in range(6):
            run = f"SRR{i+1:08d}"
            rows.append({
                "sample_id": f"S{i+1}",
                "taxon": "C. japonicum var. takaoense",
                "morph": "BP" if i < 3 else "W",
                "panel_role": "focal_colour_morph",
                "matched_run": run,
                "library_layout": "PAIRED",
                "run_match_confidence": "verified",
                "preferred_sequence_source": run,
                "de_novo_required": "true",
            })
        with self.panel.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def tearDown(self):
        self.tmp.cleanup()

    def plan(self):
        row = mod.heavy.validate_panel(self.panel, expected_samples=6)[0]
        return mod.command_plan_for_row(
            row,
            outdir=self.root / "reads",
            fasterq_threads=8,
            fastp_threads=8,
        )

    def test_committed_panel_is_direct_evidence_validated(self):
        rows = mod.frozen_panel.validate(
            REPO / "sampling/chang2026_takaoense6_read2tree_panel_v1.csv",
            REPO / "data/evidence/chang2026_takaoense_morph_linked_public_samples_v1.csv",
        )
        self.assertEqual(len(rows), 6)
        self.assertEqual({row["morph"] for row in rows}, {"BP", "W"})
        self.assertEqual({row["matched_run"] for row in rows}, {
            "SRR35152718", "SRR35152736", "SRR35152735",
            "SRR35152717", "SRR35152738", "SRR35152734",
        })

    def test_paths_match_read2tree_trimmed_contract(self):
        plan = self.plan()
        self.assertTrue(
            Path(str(plan["trimmed_read_1"])).as_posix().endswith(
                "samples/S1/trimmed/S1.R1.trim.fastq.gz"
            )
        )
        self.assertTrue(
            Path(str(plan["trimmed_read_2"])).as_posix().endswith(
                "samples/S1/trimmed/S1.R2.trim.fastq.gz"
            )
        )
        self.assertEqual(tuple(mod.READ_STAGES), ("prefetch", "vdb_validate", "fasterq", "pigz", "fastp"))
        self.assertNotIn("trinity", mod.READ_STAGES)

    def test_dry_run_never_calls_external_stage(self):
        plan = self.plan()
        original = mod.heavy.run_stage
        try:
            mod.heavy.run_stage = lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("external stage called"))
            result = mod.prepare_one(plan, dry_run=True)
        finally:
            mod.heavy.run_stage = original
        self.assertEqual(result["status"], "planned_dry_run")

    def test_existing_trimmed_pair_skips_network_and_trinity(self):
        plan = self.plan()
        for key in ("trimmed_read_1", "trimmed_read_2", "fastp_json"):
            path = Path(str(plan[key]))
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"x")
        original = mod.heavy.run_stage
        try:
            mod.heavy.run_stage = lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("stage should not run"))
            result = mod.prepare_one(plan, dry_run=False)
        finally:
            mod.heavy.run_stage = original
        self.assertEqual(result["status"], "skipped_existing_trimmed_reads")
        self.assertEqual(result["completed_stage"], "fastp")

    def test_partial_raw_pair_is_rejected_before_network(self):
        plan = self.plan()
        raw1 = Path(str(plan["raw_read_1"]))
        raw1.parent.mkdir(parents=True, exist_ok=True)
        raw1.write_bytes(b"x")
        result = mod.prepare_one(plan, dry_run=False)
        self.assertEqual(result["status"], "failed")
        self.assertIn("Partial paired FASTQ state", result["error"])


if __name__ == "__main__":
    unittest.main()
