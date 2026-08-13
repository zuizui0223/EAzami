#!/usr/bin/env python3
"""Tests for the four-scenario Japan-origin sensitivity gate."""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "integrate_japan_origin_topology_sensitivities",
    ROOT / "analysis/integrate_japan_origin_topology_sensitivities.py",
)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


def write_csv(path: Path, fields: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields))
        writer.writeheader()
        writer.writerows(rows)


def interpretation(
    scenario_id: str,
    tree_method: str,
    *,
    main_monophyletic: bool = True,
    japan_monophyletic: bool = False,
    arenicola_relation: str = "arenicola_immediate_sister_to_published_main_radiation",
) -> dict[str, object]:
    def group(value: bool) -> dict[str, object]:
        return {"monophyletic": value}

    return {
        "contract_version": "japan_origin_global_topology_interpretation_v2",
        "tree_sha256": ("a" if scenario_id.startswith("bwa") else "b") * 64,
        "tree_artifact_acceptance_verified": True,
        "focal_public_individual_count": 294,
        "analysis_unit": "individual_tip" if tree_method == "concat" else "source_label_tip",
        "group_statistics": {
            "main_japanese_radiation": group(main_monophyletic),
            "all_public_japan_region_tips": group(japan_monophyletic),
            "arenicola": group(True),
            "Cirsium brevicaule": group(True),
            "Cirsium irumtiense": group(True),
        },
        "arenicola_relative_to_main_radiation": arenicola_relation,
        "published_exception_relationships": {
            "Cirsium dipsacolepis": "outside_published_main_radiation_mrca",
            "Cirsium lineare": "outside_published_main_radiation_mrca",
        },
        "dispersal_direction_inferred": False,
        "direct_ancestry_inferred": False,
        "introgression_inferred": False,
        "new_china_sampling_freeze_allowed": False,
        "candidate_row_count": 4,
    }


def candidate_rows(*, review_required: bool = False, astral: bool = False) -> list[dict[str, str]]:
    rows = []
    for group, taxon, region in (
        ("main_japanese_radiation", "Cirsium china_main", "China"),
        ("arenicola", "Cirsium china_south", "China"),
        ("Cirsium dipsacolepis", "Cirsium korea_dips", "Korea"),
        ("Cirsium lineare", "Cirsium china_line", "China"),
    ):
        rows.append({
            "focal_group": group,
            "neighbourhood_kind": "immediate_sibling_branch",
            "candidate_taxon": taxon,
            "region": region,
            "source_study": "Moreyra2025|Chang2026" if astral else "Moreyra2025",
            "tip_count": "1",
            "tip_ids": "SP0001" if astral else "JOG0001",
            "name_review_required": str(review_required and group == "arenicola").lower(),
            "sampling_priority_if_public_data_remain_unresolved": (
                "S" if group in {"main_japanese_radiation", "arenicola"} else "A"
            ),
            "interpretation_limit": "test",
        })
    return rows


def build_scenarios(
    root: Path,
    *,
    mixed_main: bool = False,
    unstable_arenicola: bool = False,
    review_required: bool = False,
) -> Path:
    scenario_rows = []
    for index, (scenario_id, (mapping, tree_method)) in enumerate(
        mod.EXPECTED_SCENARIOS.items()
    ):
        result = interpretation(
            scenario_id,
            tree_method,
            main_monophyletic=not (mixed_main and index == 3),
            arenicola_relation=(
                "arenicola_separate_from_published_main_radiation"
                if unstable_arenicola and index == 3
                else "arenicola_immediate_sister_to_published_main_radiation"
            ),
        )
        result_path = root / f"{scenario_id}.json"
        candidate_path = root / f"{scenario_id}.csv"
        result_path.write_text(json.dumps(result), encoding="utf-8")
        write_csv(
            candidate_path,
            mod.CANDIDATE_FIELDS,
            candidate_rows(review_required=review_required, astral=tree_method == "astral"),
        )
        scenario_rows.append({
            "scenario_id": scenario_id,
            "mapping_method": mapping,
            "tree_method": tree_method,
            "interpretation_json": result_path.name,
            "candidate_table": candidate_path.name,
        })
    path = root / "scenarios.csv"
    write_csv(path, mod.SCENARIO_FIELDS, scenario_rows)
    return path


class JapanOriginSensitivityGateTests(unittest.TestCase):
    def test_stable_four_scenario_result_allows_gap_conversion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = build_scenarios(Path(tmp))
            summary, rows = mod.integrate(path)
            self.assertEqual(summary["main_japanese_radiation_monophyly"], "supported_monophyletic")
            self.assertEqual(summary["all_sampled_japanese_lineages_monophyly"], "rejected_monophyly")
            self.assertTrue(summary["sensitivity_decision_ready"])
            self.assertTrue(summary["new_china_sampling_freeze_allowed"])
            self.assertEqual(len(rows), 4)
            self.assertTrue(all(row["promotion_eligible"] == "true" for row in rows))

    def test_mapping_tree_disagreement_stays_unresolved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = build_scenarios(Path(tmp), mixed_main=True)
            summary, _ = mod.integrate(path)
            self.assertEqual(
                summary["main_japanese_radiation_monophyly"],
                "unresolved_sensitivity_conflict",
            )
            self.assertFalse(summary["new_china_sampling_freeze_allowed"])

    def test_arenicola_placement_disagreement_blocks_freeze(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = build_scenarios(Path(tmp), unstable_arenicola=True)
            summary, _ = mod.integrate(path)
            self.assertFalse(summary["sensitivity_decision_ready"])
            self.assertIn("Arenicola placement", " ".join(summary["sampling_freeze_blockers"]))

    def test_unreviewed_stable_name_conflict_blocks_until_confirmed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = build_scenarios(root, review_required=True)
            blocked, _ = mod.integrate(path)
            self.assertFalse(blocked["new_china_sampling_freeze_allowed"])
            review = root / "review.csv"
            write_csv(review, ("candidate_taxon", "region", "review_status", "evidence_locator"), [{
                "candidate_taxon": "Cirsium china_south",
                "region": "China",
                "review_status": "confirmed_source_label",
                "evidence_locator": "voucher audit row 7",
            }])
            accepted, rows = mod.integrate(path, review)
            self.assertTrue(accepted["new_china_sampling_freeze_allowed"])
            aren = next(row for row in rows if row["focal_group"] == "arenicola")
            self.assertEqual(aren["name_review_status"], "confirmed_source_label")
            write_csv(review, ("candidate_taxon", "region", "review_status", "evidence_locator"), [{
                "candidate_taxon": "Cirsium china_south",
                "region": "China",
                "review_status": "excluded_from_sampling",
                "evidence_locator": "voucher audit row 7",
            }])
            excluded, _ = mod.integrate(path, review)
            self.assertFalse(excluded["new_china_sampling_freeze_allowed"])

    def test_missing_scenario_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = build_scenarios(root)
            rows = mod.read_csv(path, mod.SCENARIO_FIELDS)[:-1]
            write_csv(path, mod.SCENARIO_FIELDS, rows)
            with self.assertRaisesRegex(ValueError, "four-scenario inventory mismatch"):
                mod.integrate(path)

    def test_unaccepted_scenario_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = build_scenarios(root)
            result_path = root / "bwa_concat.json"
            result = json.loads(result_path.read_text(encoding="utf-8"))
            result["tree_artifact_acceptance_verified"] = False
            result_path.write_text(json.dumps(result), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "acceptance was not verified"):
                mod.integrate(path)


if __name__ == "__main__":
    unittest.main()
