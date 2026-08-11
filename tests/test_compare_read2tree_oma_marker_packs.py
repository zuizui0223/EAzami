import json
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "analysis" / "compare_read2tree_oma_marker_packs.py"
SPEC = importlib.util.spec_from_file_location("pack_compare", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
sys.modules["pack_compare"] = mod
SPEC.loader.exec_module(mod)


def write_marker(path: Path, ids):
    lines = []
    for seq_id in ids:
        lines.extend([f">{seq_id}", "MAAAAA"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_pack(root: Path, signatures):
    marker_dir = root / "marker_genes"
    marker_dir.mkdir(parents=True)
    for index, ids in enumerate(signatures, start=1):
        write_marker(marker_dir / f"marker_{index:03d}.fa", ids)
    contract = {
        "contract_version": "eazami_read2tree_oma_marker_pack_v1",
        "execution_allowed": True,
        "oma_release": "May2026",
        "reference_codes": ["CYNCS", "HELAN", "DAUCS"],
        "normalized_marker_dir": "marker_genes",
        "normalized_pack_sha256": root.name + "_sha",
    }
    path = root / "marker_pack_contract.json"
    path.write_text(json.dumps(contract), encoding="utf-8")
    return path


class MarkerPackComparisonTests(unittest.TestCase):
    def test_identical_sets_ignore_marker_filenames(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            sigs = [
                ("CYNCS00001", "HELAN00001", "DAUCS00001"),
                ("CYNCS00002", "HELAN00002", "DAUCS00002"),
            ]
            a = build_pack(root / "a", sigs)
            b = build_pack(root / "b", list(reversed(sigs)))
            rows, summary = mod.compare_packs(a, b, expected_count=2)
            self.assertEqual(summary["exact_marker_group_intersection"], 2)
            self.assertEqual(summary["marker_group_jaccard"], 1.0)
            self.assertEqual(summary["overlap_classification"], "identical_marker_sets")
            self.assertEqual(len(rows), 2)

    def test_partial_overlap_uses_oma_id_triplets(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            a = build_pack(
                root / "a",
                [
                    ("CYNCS00001", "HELAN00001", "DAUCS00001"),
                    ("CYNCS00002", "HELAN00002", "DAUCS00002"),
                ],
            )
            b = build_pack(
                root / "b",
                [
                    ("CYNCS00001", "HELAN00001", "DAUCS00001"),
                    ("CYNCS00003", "HELAN00003", "DAUCS00003"),
                ],
            )
            _, summary = mod.compare_packs(a, b, expected_count=2)
            self.assertEqual(summary["exact_marker_group_intersection"], 1)
            self.assertAlmostEqual(summary["marker_group_jaccard"], 1 / 3)
            self.assertEqual(summary["reference_sequence_id_intersection"], 3)
            self.assertAlmostEqual(summary["reference_sequence_id_jaccard"], 3 / 9)
            self.assertEqual(summary["overlap_classification"], "moderate_overlap")

    def test_wrong_reference_composition_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            contract = build_pack(
                root / "a",
                [("CYNCS00001", "HELAN00001", "DAUCS00001")],
            )
            marker = root / "a" / "marker_genes" / "marker_001.fa"
            write_marker(marker, ("CYNCS00001", "HELAN00001", "HELAN00002"))
            with self.assertRaisesRegex(ValueError, "exactly one sequence"):
                mod.marker_signatures(contract, expected_count=1)

    def test_overlap_classes(self):
        self.assertEqual(mod.overlap_class(400, 400), "identical_marker_sets")
        self.assertEqual(mod.overlap_class(300, 400), "high_overlap")
        self.assertEqual(mod.overlap_class(100, 400), "moderate_overlap")
        self.assertEqual(mod.overlap_class(99, 400), "low_overlap")


if __name__ == "__main__":
    unittest.main()
