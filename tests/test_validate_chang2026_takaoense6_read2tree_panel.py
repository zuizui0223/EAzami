import csv
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "analysis" / "validate_chang2026_takaoense6_read2tree_panel.py"
SPEC = importlib.util.spec_from_file_location("panel_validate", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
sys.modules["panel_validate"] = mod
SPEC.loader.exec_module(mod)


class PanelValidatorTests(unittest.TestCase):
    def build_files(self, root: Path):
        evidence = root / "data/evidence/chang2026_takaoense_morph_linked_public_samples_v1.csv"
        evidence.parent.mkdir(parents=True)
        panel = root / "sampling/chang2026_takaoense6_read2tree_panel_v1.csv"
        panel.parent.mkdir(parents=True)

        evidence_rows = []
        panel_rows = []
        focal = [
            ("FC", "ccy3559", "BP", "SRR35152718", "SAMN50798021"),
            ("TJ", "ccy3807", "BP", "SRR35152736", "SAMN50798026"),
            ("NH", "ccy3835", "BP", "SRR35152735", "SAMN50798027"),
            ("WY", "ccy3560", "W", "SRR35152717", "SAMN50798022"),
            ("FB", "ccy3629", "W", "SRR35152738", "SAMN50798024"),
            ("LT", "ccy3839", "W", "SRR35152734", "SAMN50798028"),
        ]
        for code, voucher, morph, run, biosample in focal:
            evidence_rows.append(
                {
                    "code": code,
                    "voucher": voucher,
                    "published_figure_label": morph,
                    "run": run,
                    "biosample": biosample,
                    "evidence_status": "morph_and_public_accession_directly_linked",
                }
            )
            panel_rows.append(
                {
                    "sample_id": f"{code}_{voucher}",
                    "matched_run": run,
                    "library_layout": "PAIRED",
                    "panel_role": "focal_colour_morph",
                    "morph": morph,
                    "code": code,
                    "voucher": voucher,
                    "biosample": biosample,
                    "source_evidence": mod.SOURCE_EVIDENCE_LABEL,
                }
            )
        with evidence.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(evidence_rows[0]))
            writer.writeheader()
            writer.writerows(evidence_rows)
        with panel.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(panel_rows[0]))
            writer.writeheader()
            writer.writerows(panel_rows)
        return panel, evidence

    def test_matching_panel_validates(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            panel, evidence = self.build_files(root)
            rows = mod.validate(panel, evidence)
            self.assertEqual(len(rows), 6)
            self.assertEqual({row["morph"] for row in rows}, {"BP", "W"})

    def test_stale_run_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            panel, evidence = self.build_files(root)
            rows = mod.read_csv(panel)
            rows[0]["matched_run"] = "SRR00000000"
            with panel.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
            with self.assertRaisesRegex(ValueError, "differs from direct evidence"):
                mod.validate(panel, evidence)

    def test_indirect_evidence_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            panel, evidence = self.build_files(root)
            rows = mod.read_csv(evidence)
            rows[0]["evidence_status"] = "inferred_from_locality"
            with evidence.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
            with self.assertRaisesRegex(ValueError, "not direct"):
                mod.validate(panel, evidence)


if __name__ == "__main__":
    unittest.main()
