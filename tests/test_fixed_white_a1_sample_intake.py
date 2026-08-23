from __future__ import annotations

import csv
import importlib.util
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
INTAKE_PATH = ROOT / "sampling/FIXED_WHITE_A1_SAMPLE_INTAKE_V0_1.csv"


def load_module(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


intake = load_module("fixed_white_intake", ROOT / "analysis/validate_fixed_white_a1_sample_intake.py")
recovery = load_module("fixed_white_recovery", ROOT / "analysis/evaluate_fixed_white_a1_recovery_qc.py")


class FixedWhiteA1SampleIntakeTests(unittest.TestCase):
    def test_current_manifest_contains_planned_slots_not_fake_samples(self):
        x = intake.validate(INTAKE_PATH)
        self.assertEqual(x["slots"], 6)
        self.assertEqual(x["available_samples_by_taxon"], {
            "Cirsium boninense": 0,
            "Cirsium wulongense": 0,
        })
        self.assertFalse(x["minimum_external_reads_available"])
        self.assertFalse(x["recovery_qc_allowed"])
        self.assertFalse(x["rate_fit_tip_promotion_allowed"])

    def test_available_slot_requires_voucher_colour_and_reads(self):
        rows = list(csv.DictReader(INTAKE_PATH.open(encoding="utf-8")))
        rows[0]["acquisition_status"] = "available"
        rows[0]["immutable_sample_id"] = "BON_X1"
        with tempfile.TemporaryDirectory() as td:
            p = pathlib.Path(td) / "intake.csv"
            with p.open("w", encoding="utf-8", newline="") as h:
                w = csv.DictWriter(h, fieldnames=rows[0].keys())
                w.writeheader(); w.writerows(rows)
            with self.assertRaisesRegex(ValueError, "locality/voucher"):
                intake.validate(p)

    def test_two_available_per_taxon_unlock_only_recovery_qc(self):
        rows = list(csv.DictReader(INTAKE_PATH.open(encoding="utf-8")))
        for i in (0, 1, 3, 4):
            slot = rows[i]["sample_slot"]
            rows[i].update({
                "acquisition_status": "available",
                "immutable_sample_id": slot + "_DNA",
                "locality": "verified_locality",
                "voucher_or_herbarium_id": slot + "_VOUCHER",
                "flower_colour_link_status": "individual_linked_fixed_white",
                "read_source_type": "sra_run",
                "read_source_1": "SRR" + str(90000000 + i),
            })
        with tempfile.TemporaryDirectory() as td:
            p = pathlib.Path(td) / "intake.csv"
            with p.open("w", encoding="utf-8", newline="") as h:
                w = csv.DictWriter(h, fieldnames=rows[0].keys())
                w.writeheader(); w.writerows(rows)
            x = intake.validate(p)
        self.assertTrue(x["minimum_external_reads_available"])
        self.assertTrue(x["recovery_qc_allowed"])
        self.assertFalse(x["rate_fit_tip_promotion_allowed"])


class FixedWhiteA1RecoveryQCTests(unittest.TestCase):
    @staticmethod
    def row(sample: str, taxon: str, clean_n: int, recovered: int = 150, paralog: int = 0):
        return {
            "immutable_sample_id": sample,
            "taxon": taxon,
            "frozen_loci": "153",
            "recovered_frozen_loci": str(recovered),
            "paralog_warning_frozen_loci": str(paralog),
            "clean_recovered_frozen_loci": str(clean_n),
            "non_gap_aligned_bp": "100000",
        }

    def test_below_123_does_not_pass_individual_gate(self):
        rows = [
            self.row("BON1", "Cirsium boninense", 122),
            self.row("BON2", "Cirsium boninense", 153, recovered=153),
            self.row("WUL1", "Cirsium wulongense", 153, recovered=153),
            self.row("WUL2", "Cirsium wulongense", 153, recovered=153),
        ]
        x = recovery.evaluate_rows(rows)
        self.assertFalse(x["individual_recovery_gate_passed_for_both_taxa"])
        self.assertFalse(x["replicate_placement_qc_allowed"])
        self.assertFalse(x["rate_fit_tip_promotion_allowed"])

    def test_two_passing_per_taxon_unlock_only_replicate_placement(self):
        rows = [
            self.row("BON1", "Cirsium boninense", 123, recovered=130, paralog=7),
            self.row("BON2", "Cirsium boninense", 140, recovered=145, paralog=5),
            self.row("WUL1", "Cirsium wulongense", 130, recovered=140, paralog=10),
            self.row("WUL2", "Cirsium wulongense", 153, recovered=153, paralog=0),
        ]
        x = recovery.evaluate_rows(rows)
        self.assertTrue(x["individual_recovery_gate_passed_for_both_taxa"])
        self.assertTrue(x["replicate_placement_qc_allowed"])
        self.assertFalse(x["rate_fit_tip_promotion_allowed"])
        self.assertIn("replicate-expanded placement", x["next_gate"])

    def test_frozen_locus_universe_cannot_drift(self):
        rows = [self.row("BON1", "Cirsium boninense", 123)]
        rows[0]["frozen_loci"] = "152"
        with self.assertRaisesRegex(ValueError, "must remain 153"):
            recovery.evaluate_rows(rows)


if __name__ == "__main__":
    unittest.main()
