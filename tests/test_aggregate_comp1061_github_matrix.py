from __future__ import annotations

import csv
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / "analysis/aggregate_comp1061_github_matrix.py"
SPEC = importlib.util.spec_from_file_location("agg_comp1061", MOD)
assert SPEC and SPEC.loader
m = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = m
SPEC.loader.exec_module(m)


class AggregateComp1061GithubMatrixTests(unittest.TestCase):
    def fixture(self, td: str, missing: str | None = None):
        root = Path(td)
        runs = root / "runs.csv"
        with runs.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["tip_id"])
            writer.writeheader()
            writer.writerows([{"tip_id": "Tip_A"}, {"tip_id": "Tip_B"}])
        artifacts = root / "artifacts"
        for tip, loci, paralogs in [
            ("Tip_A", {"g1": "AAAA", "g2": "CCCC"}, {"g1": "1", "g2": "2"}),
            ("Tip_B", {"g1": "AAAT"}, {"g1": "1", "g2": "0"}),
        ]:
            if tip == missing:
                continue
            sample = artifacts / f"artifact-{tip}" / "sample_compact" / tip
            retrieved = sample / "retrieved_dna"
            retrieved.mkdir(parents=True)
            (sample / "sample_metadata.json").write_text(json.dumps({"tip_id": tip}))
            for locus, seq in loci.items():
                (retrieved / f"{locus}.FNA").write_text(f">{tip}\n{seq}\n")
            with (sample / "paralog_report.tsv").open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["Species", "g1", "g2"], delimiter="\t", lineterminator="\n")
                writer.writeheader()
                writer.writerow({"Species": tip, **paralogs})
        return artifacts, runs

    def test_aggregates_fasta_and_paralog_rows(self):
        with tempfile.TemporaryDirectory() as td:
            artifacts, runs = self.fixture(td)
            out = Path(td) / "out"
            result = m.aggregate(artifacts, runs, out)
            self.assertEqual(result["aggregated_samples"], 2)
            self.assertEqual(result["aggregated_locus_files"], 2)
            g1 = (out / "retrieved_dna/g1.FNA").read_text()
            self.assertIn(">Tip_A", g1)
            self.assertIn(">Tip_B", g1)
            fields, rows = m.read_tsv(out / "paralog_report.tsv")
            self.assertEqual(fields, ["Species", "g1", "g2"])
            self.assertEqual({r["Species"] for r in rows}, {"Tip_A", "Tip_B"})

    def test_missing_sample_artifact_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            artifacts, runs = self.fixture(td, missing="Tip_B")
            with self.assertRaisesRegex(ValueError, "compact sample mismatch"):
                m.aggregate(artifacts, runs, Path(td) / "out")

    def test_duplicate_sample_artifact_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            artifacts, runs = self.fixture(td)
            source = next(artifacts.rglob("sample_metadata.json"))
            dup = artifacts / "duplicate" / source.parent.name
            dup.mkdir(parents=True)
            (dup / "sample_metadata.json").write_text(source.read_text())
            with self.assertRaisesRegex(ValueError, "duplicate compact artifact"):
                m.aggregate(artifacts, runs, Path(td) / "out")


if __name__ == "__main__":
    unittest.main()
