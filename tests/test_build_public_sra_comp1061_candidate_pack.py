from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from analysis.build_public_sra_comp1061_candidate_pack import build


class PublicSraCandidatePackTests(unittest.TestCase):
    def test_strict_pack_uses_recovery_and_candidate_specific_paralog_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            loci = [f"L{i:03d}" for i in range(241)]
            (root / "loci.txt").write_text("".join(x + "\n" for x in loci), encoding="utf-8")

            manifest = root / "manifest.csv"
            with manifest.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=[
                        "candidate_id", "tip_id", "scientific_name", "biosample", "run",
                        "bioproject", "library_strategy", "pilot_execute",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "candidate_id": "EA01",
                        "tip_id": "PUBEA001",
                        "scientific_name": "Cirsium testense",
                        "biosample": "SAMN1",
                        "run": "SRR1",
                        "bioproject": "PRJNA1",
                        "library_strategy": "Targeted-Capture",
                        "pilot_execute": "true",
                    }
                )

            retrieved = root / "retrieved"
            retrieved.mkdir()
            for locus in loci[:101]:
                (retrieved / f"{locus}.FNA").write_text(
                    f">PUBEA001\nATGATGATG\n", encoding="utf-8"
                )

            paralog = root / "paralog.tsv"
            with paralog.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["Species", *loci], delimiter="\t")
                writer.writeheader()
                row = {"Species": "PUBEA001", **{locus: "1" for locus in loci}}
                row[loci[0]] = "2"
                writer.writerow(row)

            summary = build(manifest, "EA01", root / "loci.txt", retrieved, paralog, root / "out")
            self.assertEqual(summary["recovered_frozen_loci"], 101)
            self.assertEqual(summary["paralog_warning_loci"], 1)
            self.assertEqual(summary["strict_no_warning_recovered_loci"], 100)
            self.assertTrue(summary["pilot_locus_pack_ready"])
            self.assertFalse(summary["tree_tip_promotion_allowed"])
            self.assertEqual(len(list((root / "out/loci").glob("*.fasta"))), 100)

    def test_nonpilot_candidate_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            loci = [f"L{i:03d}" for i in range(241)]
            (root / "loci.txt").write_text("".join(x + "\n" for x in loci), encoding="utf-8")
            manifest = root / "manifest.csv"
            manifest.write_text(
                "candidate_id,tip_id,scientific_name,biosample,run,bioproject,library_strategy,pilot_execute\n"
                "EA06,PUBEA006,Cirsium minganense,SAMN6,SRR6,PRJNA6,WGS,false\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "not admitted"):
                build(manifest, "EA06", root / "loci.txt", root, root / "none.tsv", root / "out")


if __name__ == "__main__":
    unittest.main()
