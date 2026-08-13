from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "paired_aug", ROOT / "analysis/prepare_cirsium_nipponicum_augmentation_tree_inputs.py"
)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules["paired_aug"] = mod
SPEC.loader.exec_module(mod)


def fasta(path: Path, rows: list[tuple[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as h:
        for name, seq in rows:
            h.write(f">{name}\n{seq}\n")


class PairedAugmentationTests(unittest.TestCase):
    def test_exact_paired_inputs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            primary = root / "primary"
            pack = root / "pack"
            out = root / "out"
            primary.mkdir(); pack.mkdir()
            (primary / "eligible_loci.txt").write_text("L1\nL2\nL3\n")
            (pack / "strict_recovered_loci.txt").write_text("L2\nL3\nL4\n")
            for locus in ("L1", "L2", "L3"):
                fasta(primary / "loci_unaligned" / f"{locus}.fasta", [("JOG0001", "ATG"), ("OUTGROUP_lett", "ATG")])
            for locus in ("L2", "L3", "L4"):
                fasta(pack / "loci" / f"{locus}.fasta", [(mod.AUG_TIP, "ATGCCC")])
            summary = mod.prepare(primary, pack, out, minimum_overlap=2)
            self.assertEqual(summary["paired_overlap_loci"], 2)
            self.assertEqual((out / "baseline294" / "eligible_loci.txt").read_text(), "L2\nL3\n")
            baseline = mod.read_fasta(out / "baseline294" / "loci_unaligned" / "L2.fasta")
            augmented = mod.read_fasta(out / "augmented295" / "loci_unaligned" / "L2.fasta")
            self.assertEqual(augmented[:-1], baseline)
            self.assertEqual(augmented[-1][0], mod.AUG_TIP)
            self.assertFalse(summary["primary_294_tree_superseded"])

    def test_overlap_gate_is_fatal(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); primary = root / "p"; pack = root / "a"
            primary.mkdir(); pack.mkdir()
            (primary / "eligible_loci.txt").write_text("L1\n")
            (pack / "strict_recovered_loci.txt").write_text("L1\n")
            fasta(primary / "loci_unaligned" / "L1.fasta", [("JOG0001", "ATG")])
            fasta(pack / "loci" / "L1.fasta", [(mod.AUG_TIP, "ATG")])
            with self.assertRaisesRegex(ValueError, "require >= 2"):
                mod.prepare(primary, pack, root / "o", minimum_overlap=2)


if __name__ == "__main__":
    unittest.main()
