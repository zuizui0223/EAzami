#!/usr/bin/env python3
"""Tests for the six-tip var. takaoense metadata screen."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "analysis"
    / "takaoense_published_morph_metadata_screen.py"
)
SPEC = importlib.util.spec_from_file_location(
    "takaoense_published_morph_metadata_screen", MODULE_PATH
)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
sys.modules["takaoense_published_morph_metadata_screen"] = mod
SPEC.loader.exec_module(mod)


class TakaoenseMorphMetadataScreenTests(unittest.TestCase):
    def test_dms_to_decimal(self) -> None:
        latitude, longitude = mod.dms_to_decimal("23°30'N, 120°41'E")
        self.assertAlmostEqual(latitude, 23.5)
        self.assertAlmostEqual(longitude, 120 + 41 / 60)

    def six_rows(self) -> list[dict[str, object]]:
        values = [
            ("FC", "ccy3559", "BP", 1364),
            ("TJ", "ccy3807", "BP", 1127),
            ("NH", "ccy3835", "BP", 991),
            ("WY", "ccy3560", "W", 977),
            ("FB", "ccy3629", "W", 21),
            ("LT", "ccy3839", "W", 73),
        ]
        return [
            {
                "code": code,
                "voucher": voucher,
                "published_figure_label": morph,
                "altitude_m": str(altitude),
            }
            for code, voucher, morph, altitude in values
        ]

    def test_exact_permutation_screen(self) -> None:
        rows = self.six_rows()
        permutations, observed, one_sided, two_sided = mod.enumerate_permutations(rows)
        self.assertEqual(len(permutations), 20)
        self.assertAlmostEqual(observed, 803.6666666666667)
        self.assertAlmostEqual(one_sided, 0.05)
        self.assertAlmostEqual(two_sided, 0.10)
        self.assertEqual(
            sum(row["at_least_observed_one_sided"] == "yes" for row in permutations),
            1,
        )
        self.assertEqual(
            sum(row["at_least_observed_absolute"] == "yes" for row in permutations),
            2,
        )

    def test_leave_one_out_difference_stays_positive(self) -> None:
        rows = self.six_rows()
        output = mod.leave_one_out(rows)
        self.assertEqual(len(output), 6)
        differences = [float(row["difference_bp_minus_w_m"]) for row in output]
        self.assertAlmostEqual(min(differences), 635.666667, places=5)
        self.assertAlmostEqual(max(differences), 1113.666667, places=5)
        self.assertTrue(all(value > 0 for value in differences))

    def test_join_requires_figure_and_ncbi_identity_agreement(self) -> None:
        assignments = []
        metadata = []
        states = {
            "ccy3559": ("FC", "BP", "bluish-purple", "C", 1364),
            "ccy3560": ("WY", "W", "white", "W", 977),
            "ccy3629": ("FB", "W", "white", "W", 21),
            "ccy3807": ("TJ", "BP", "bluish-purple", "C", 1127),
            "ccy3835": ("NH", "BP", "bluish-purple", "C", 991),
            "ccy3839": ("LT", "W", "white", "W", 73),
        }
        for index, (voucher, values) in enumerate(states.items(), start=1):
            code, label, state, binary, altitude = values
            run = f"SRR{index}"
            biosample = f"SAMN{index}"
            assignments.append(
                {
                    "accepted_taxon": "Cirsium japonicum var. takaoense",
                    "code": code,
                    "voucher": voucher,
                    "run": run,
                    "biosample": biosample,
                    "direct_figure_label": label,
                    "flower_colour_state": state,
                    "binary_colour_code": binary,
                    "figure1_panel_b_label": f"{code}({label})",
                    "figure1_panel_c_label": f"{code}({label})",
                    "source_image_sha256": "hash",
                }
            )
            metadata.append(
                {
                    "code": code,
                    "voucher": voucher,
                    "run": run,
                    "experiment": f"SRX{index}",
                    "biosample": biosample,
                    "sample_name": f"takaoense-{voucher.removeprefix('ccy')}",
                    "biosample_isolate": voucher.removeprefix("ccy"),
                    "location": "Taiwan",
                    "coordinate": "23°30'N, 120°41'E",
                    "altitude_m": str(altitude),
                    "herbarium_supplement_s1": "TNM",
                }
            )
        joined = mod.join_samples(assignments, metadata)
        self.assertEqual(len(joined), 6)
        self.assertEqual(
            {row["published_figure_label"] for row in joined}, {"W", "BP"}
        )

        metadata[0]["run"] = "SRR_DIFFERENT"
        with self.assertRaisesRegex(ValueError, "run mismatch"):
            mod.join_samples(assignments, metadata)

    def test_unexpected_morph_count_fails(self) -> None:
        rows = self.six_rows()
        rows[0]["published_figure_label"] = "W"
        with self.assertRaisesRegex(ValueError, "expects three BP"):
            mod.enumerate_permutations(rows)


if __name__ == "__main__":
    unittest.main()
