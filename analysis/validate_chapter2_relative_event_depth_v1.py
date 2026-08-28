#!/usr/bin/env python3
"""Fail-closed validation for the Chapter 2 relative lineage-depth layer."""
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "data" / "evidence"
CONTRACT = EVIDENCE / "chapter2_relative_event_depth_contract_v1.json"
RESULT = EVIDENCE / "japan38_relative_event_depth_v1.json"
SUMMARY = EVIDENCE / "japan38_relative_event_depth_summary_v1.csv"
MANUSCRIPT = ROOT / "docs" / "chapter2" / "MANUSCRIPT_JEB_V4.md"
CONTRACT_NOTE = ROOT / "docs" / "chapter2" / "RELATIVE_EVENT_DEPTH_CONTRACT_V1.md"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def forced_fraction(result: dict, trait: str, edge_id: str) -> float:
    rows = result["ufboot1000_relative_event_depth"][trait][
        "forced_change_edge_frequencies"
    ]
    lookup = {row["edge_id"]: row["fraction"] for row in rows}
    if edge_id not in lookup:
        raise AssertionError(f"missing forced-edge frequency: {trait} {edge_id}")
    return float(lookup[edge_id])


def assert_close(observed: float, expected: float, label: str) -> None:
    if abs(float(observed) - expected) > 1e-12:
        raise AssertionError(f"{label} drift: {observed} != {expected}")


def validate() -> dict:
    for path in (CONTRACT, RESULT, SUMMARY, MANUSCRIPT, CONTRACT_NOTE):
        if not path.exists() or path.stat().st_size == 0:
            raise AssertionError(f"missing or empty artifact: {path.relative_to(ROOT)}")

    contract = load_json(CONTRACT)
    result = load_json(RESULT)
    if contract["status"] != (
        "frozen_with_audited_runtime_and_provenance_amendment_before_result_admission"
    ):
        raise AssertionError("relative lineage-depth contract is not frozen")
    if contract["runtime_contract"]["biopython_version"] != "1.85":
        raise AssertionError("Biopython runtime pin drift")
    if result["source_contract"] != "data/evidence/chapter2_relative_event_depth_contract_v1.json":
        raise AssertionError("result points to the wrong contract")
    verified = result["input_verification"]
    frozen = contract["frozen_inputs"]
    for key in (
        "tree_run_id", "tree_artifact", "ml_tree_sha256", "ufboot_sha256",
        "concept_map_canonical_lf_sha256",
        "base_trait_seed_canonical_lf_sha256",
        "authority_extension_canonical_lf_sha256",
    ):
        if verified[key] != frozen[key]:
            raise AssertionError(f"frozen input drift: {key}")
    if verified["bootstrap_trees_total"] != 1000:
        raise AssertionError("UFBoot ensemble is incomplete")
    if verified["runtime"]["biopython_version"] != "1.85":
        raise AssertionError("result runtime drift")

    if result["trait_scope"]["completed_discrete_histories"] != [
        "orientation", "phyllary", "stickiness"
    ]:
        raise AssertionError("completed discrete trait scope drift")
    if result["trait_scope"]["resolved_concepts"] != {
        "orientation": 20, "phyllary": 10, "stickiness": 13
    }:
        raise AssertionError("resolved concept coverage drift")
    if set(result["trait_scope"]["excluded_from_discrete_history"]) != {
        "flower_colour", "display", "cytotype"
    }:
        raise AssertionError("an unready fourth discrete history was promoted")

    ml = result["ml_relative_event_depth"]
    boot = result["ufboot1000_relative_event_depth"]
    expected_steps = {
        "orientation": (6, 4.0, 5.0, 6.0),
        "phyllary": (3, 3.0, 3.0, 3.0),
        "stickiness": (5, 5.0, 5.0, 5.0),
    }
    for trait, (ml_steps, minimum, median, maximum) in expected_steps.items():
        if ml[trait]["minimum_steps"] != ml_steps:
            raise AssertionError(f"{trait} ML minimum-step drift")
        values = boot[trait]["metric_summaries"]["minimum_steps"]
        if (values["min"], values["median"], values["max"]) != (
            minimum, median, maximum
        ):
            raise AssertionError(f"{trait} UFBoot minimum-step drift")

    expected_ml_depth = {
        "orientation": (0.7666666666666666, 1.0),
        "phyllary": (0.6952380952380953, 1.0),
        "stickiness": (0.9428571428571428, 0.9542857142857143),
    }
    expected_boot_medians = {
        "orientation": (0.7952380952380952, 0.9942857142857143, 0.2),
        "phyllary": (0.6952380952380953, 1.0, 0.3047619047619047),
        "stickiness": (0.937142857142857, 0.9542857142857143, 0.017142857142857237),
    }
    for trait, interval in expected_ml_depth.items():
        observed = ml[trait]["mean_relative_lineage_depth_interval"]
        assert_close(observed[0], interval[0], f"{trait} ML depth lower")
        assert_close(observed[1], interval[1], f"{trait} ML depth upper")
        lower, upper, width = expected_boot_medians[trait]
        metrics = boot[trait]["metric_summaries"]
        assert_close(
            metrics["mean_relative_lineage_depth_lower_bound"]["median"],
            lower,
            f"{trait} bootstrap depth lower median",
        )
        assert_close(
            metrics["mean_relative_lineage_depth_upper_bound"]["median"],
            upper,
            f"{trait} bootstrap depth upper median",
        )
        assert_close(
            metrics["mean_relative_lineage_depth_envelope_width"]["median"],
            width,
            f"{trait} bootstrap depth width median",
        )

    expected_forced = {
        ("orientation", "JPN_36"): 0.227,
        ("phyllary", "JPN_36"): 0.728,
        ("stickiness", "JPN_06"): 0.995,
        ("stickiness", "JPN_36"): 0.707,
        ("stickiness", "JPN_30"): 0.545,
        (
            "stickiness",
            "JPN_04|JPN_08|JPN_11|JPN_12|JPN_14|JPN_17|JPN_23|JPN_26|JPN_38",
        ): 0.681,
    }
    for (trait, edge), expected in expected_forced.items():
        assert_close(forced_fraction(result, trait, edge), expected, f"{trait} {edge}")

    if boot["stickiness"][
        "fraction_trees_requiring_terminal_change_in_every_minimum_history"
    ] != 1.0:
        raise AssertionError("stickiness terminal-event requirement drift")
    if boot["stickiness"][
        "fraction_trees_requiring_internal_change_in_every_minimum_history"
    ] != 1.0:
        raise AssertionError("stickiness internal-event requirement drift")

    legacy = result["legacy_provenance_boundary"]
    if legacy["superseded_tree_run_id"] != 32845725038:
        raise AssertionError("superseded transition run boundary drift")
    if legacy["admission_rule"].startswith("Do not attach") is False:
        raise AssertionError("legacy transition fractions were not fail-closed")

    with SUMMARY.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 30:
        raise AssertionError(f"relative lineage-depth CSV must contain 30 rows, got {len(rows)}")

    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    required = [
        "relative lineage-depth",
        "0.227",
        "0.728",
        "0.995",
        "0.707",
        "0.937–0.954",
        "not absolute time",
        "exactly three completed discrete histories",
    ]
    missing = [token for token in required if token not in manuscript]
    if missing:
        raise AssertionError(f"active manuscript omits frozen depth results: {missing}")
    prohibited = [
        "run 32923076873 yielded 0.754",
        "0.754 of the current bootstrap",
        "relative lineage-depth estimates event age",
    ]
    found = [token for token in prohibited if token in manuscript]
    if found:
        raise AssertionError(f"active manuscript crosses provenance/time boundary: {found}")

    return {
        "status": "VALID",
        "traits": 3,
        "bootstrap_trees": 1000,
        "minimum_steps": {trait: ml[trait]["minimum_steps"] for trait in ml},
        "current_forced_fractions": {
            f"{trait}:{edge}": expected for (trait, edge), expected in expected_forced.items()
        },
        "claim_ceiling": result["claim_ceiling"],
    }


def main() -> int:
    print(json.dumps(validate(), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
