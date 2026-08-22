from __future__ import annotations

import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / "analysis" / "summarize_colour_rate_alignment_qc.py"
spec = importlib.util.spec_from_file_location("aln_qc", MOD); assert spec and spec.loader
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


def write_alignment(path: Path, focal_n: int = 20, include_saff: bool = True, bad_char: bool = False) -> None:
    with path.open("w") as f:
        for i in range(focal_n):
            seq = "ACGTACGT" if i else "ACGTTCGT"
            if bad_char and i == 0:
                seq = "ACGT!CGT"
            f.write(f">T{i:02d}\n{seq}\n")
        if include_saff:
            f.write(">OUTGROUP_saff\nACGTACGT\n")
        f.write(">OUTGROUP_lett\nACGTACGT\n>OUTGROUP_sunf\nACGTACGT\n")


class AlignmentQcTests(unittest.TestCase):
    def make_primary(self, root: Path) -> Path:
        p = root / "primary.csv"
        with p.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["tip_id"]); w.writeheader()
            w.writerows({"tip_id": f"T{i:02d}"} for i in range(20))
        return p

    def test_structural_qc_passes_without_signal_filtering(self):
        with tempfile.TemporaryDirectory() as td:
            r = Path(td); primary = self.make_primary(r)
            loci = [f"L{i:03d}" for i in range(100)]
            eligible = r / "eligible.txt"; eligible.write_text("\n".join(loci) + "\n")
            aln = r / "aln"; aln.mkdir()
            for j, locus in enumerate(loci):
                write_alignment(aln / f"{locus}.aln.fasta", focal_n=19 if j == 0 else 20)
            summary = m.summarize(eligible, aln, primary, r / "qc.csv", r / "qc.json")
            self.assertTrue(summary["alignment_qc_passed"])
            self.assertEqual(summary["passed_loci"], 100)
            self.assertEqual(summary["failed_loci"], 0)
            self.assertEqual(summary["root_outgroup"], "OUTGROUP_saff")
            self.assertFalse(summary["posthoc_signal_filtering_applied"])
            self.assertGreater(summary["total_variable_sites_acgt"], 0)
            rows = list(csv.DictReader((r / "qc.csv").open()))
            self.assertEqual(rows[0]["focal_sequences"], "19")
            self.assertEqual(rows[0]["reason"], "structural_qc_pass")

    def test_missing_saff_is_structural_failure_and_summary_is_written(self):
        with tempfile.TemporaryDirectory() as td:
            r = Path(td); primary = self.make_primary(r)
            loci = [f"L{i:03d}" for i in range(100)]
            eligible = r / "eligible.txt"; eligible.write_text("\n".join(loci) + "\n")
            aln = r / "aln"; aln.mkdir()
            for j, locus in enumerate(loci):
                write_alignment(aln / f"{locus}.aln.fasta", include_saff=j != 0)
            with self.assertRaisesRegex(ValueError, "1/100"):
                m.summarize(eligible, aln, primary, r / "qc.csv", r / "qc.json")
            summary = json.loads((r / "qc.json").read_text())
            self.assertFalse(summary["alignment_qc_passed"])
            self.assertEqual(summary["failed_loci"], 1)
            self.assertEqual(summary["failed_reasons"]["missing_reference:OUTGROUP_saff"], 1)

    def test_invalid_character_is_structural_failure(self):
        with tempfile.TemporaryDirectory() as td:
            r = Path(td); primary = self.make_primary(r)
            loci = [f"L{i:03d}" for i in range(100)]
            eligible = r / "eligible.txt"; eligible.write_text("\n".join(loci) + "\n")
            aln = r / "aln"; aln.mkdir()
            for j, locus in enumerate(loci):
                write_alignment(aln / f"{locus}.aln.fasta", bad_char=j == 0)
            with self.assertRaisesRegex(ValueError, "1/100"):
                m.summarize(eligible, aln, primary, r / "qc.csv", r / "qc.json")
            rows = list(csv.DictReader((r / "qc.csv").open()))
            self.assertEqual(rows[0]["reason"], "invalid_dna_characters")
            self.assertEqual(rows[0]["invalid_characters"], "!")


if __name__ == "__main__":
    unittest.main()
