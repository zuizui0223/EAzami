from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "cnip_pack", ROOT / "analysis/build_cirsium_nipponicum_comp1061_locus_pack.py"
)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules["cnip_pack"] = mod
SPEC.loader.exec_module(mod)


class CnipPackTests(unittest.TestCase):
    def test_target_id_to_locus(self):
        self.assertEqual(mod.locus_from_target_id("lett-123"), "123")
        self.assertEqual(mod.locus_from_target_id("sunf-gene_A"), "gene_A")
        self.assertEqual(mod.locus_from_target_id("saff-X"), "X")
        self.assertIsNone(mod.locus_from_target_id("Cirsium-X"))

    def test_translation(self):
        self.assertEqual(mod.translate_cds("ATGGCTTAA"), "MA*")
        self.assertEqual(mod.norm_aa("MA*"), "MA")
        self.assertEqual(mod.translate_cds("ATGG"), "")

    def test_read_hits_keeps_best_hsp_per_query_subject(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "hits.tsv"
            p.write_text(
                "lett-L1\tgeneA\t90\t100\t1e-30\t200\t80\n"
                "lett-L1\tgeneA\t95\t100\t1e-40\t250\t90\n"
                "sunf-L1\tgeneA\t92\t100\t1e-35\t220\t85\n"
                "lett-L2\tgeneB\t90\t100\t1e-20\t180\t70\n",
                encoding="utf-8",
            )
            hits = mod.read_hits(p, {"L1"})
            self.assertEqual(hits["L1"]["geneA"]["lett-L1"]["bitscore"], 250.0)
            stats = mod.candidate_stats(hits["L1"]["geneA"])
            self.assertEqual(stats["reference_query_count"], 2)
            self.assertEqual(stats["score"], 470.0)
            self.assertEqual(stats["minimum_qcov"], 85.0)
            self.assertNotIn("L2", hits)

    def test_frozen_locus_list_requires_exactly_241_unique(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "loci.txt"
            p.write_text("".join(f"L{i}\n" for i in range(241)), encoding="utf-8")
            self.assertEqual(len(mod.read_locus_list(p)), 241)
            p.write_text("L1\nL1\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "241"):
                mod.read_locus_list(p)


if __name__ == "__main__":
    unittest.main()
