#!/usr/bin/env python3
"""Validate the Chapter 2 space-time public-data synthesis and closure ledger."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data/evidence/chapter2_space_time_public_data_closure_v1.csv"
SYNTHESIS = ROOT / "docs/chapter2/SPACE_TIME_PUBLIC_DATA_SYNTHESIS_V1.md"
README = ROOT / "docs/chapter2/README.md"

REQUIRED_COLUMNS = {
    "trait_id",
    "trait_label",
    "azami_space_status",
    "azami_space_result",
    "eazami_history_status",
    "eazami_history_result",
    "eazami_ecology_status",
    "eazami_ecology_result",
    "cross_axis_class",
    "current_allowed_claim",
    "forbidden_upgrade",
    "chapter3_discriminator",
    "canonical_sources",
}

EXPECTED_TRAITS = {
    "orientation",
    "colour_continuous",
    "phyllary_posture",
    "stickiness",
    "capitulum_outline_shape",
    "involucre_architecture_armature",
}

CANONICAL_INPUTS = (
    ROOT / "docs/chapter2/ECOLOGICAL_EXPLANATORY_REACH_V1.md",
    ROOT / "docs/chapter2/FDT4_TAIWAN_MULTISOURCE_SENSITIVITY_V1.md",
    ROOT / "data/evidence/chapter2_time_axis_compute/japan38_all_continuous_history_summary_v1.json",
    ROOT / "data/evidence/chapter2_time_axis_compute/continuous_primary_phylogenetic_structure_v1.csv",
    ROOT / "data/evidence/chapter2_trait_function_history_table_v1.csv",
)


def load_rows() -> list[dict[str, str]]:
    if not LEDGER.exists():
        raise AssertionError(f"missing closure ledger: {LEDGER}")
    with LEDGER.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise AssertionError("closure ledger has no header")
        missing = REQUIRED_COLUMNS.difference(reader.fieldnames)
        if missing:
            raise AssertionError(f"closure ledger missing columns: {sorted(missing)}")
        rows = list(reader)
    if not rows:
        raise AssertionError("closure ledger is empty")
    return rows


def validate() -> int:
    checks = 0

    rows = load_rows()
    checks += 1

    by_trait = {row["trait_id"]: row for row in rows}
    if len(by_trait) != len(rows):
        raise AssertionError("trait_id values must be unique")
    checks += 1

    if set(by_trait) != EXPECTED_TRAITS:
        raise AssertionError(
            f"unexpected trait inventory: observed={sorted(by_trait)} expected={sorted(EXPECTED_TRAITS)}"
        )
    checks += 1

    for row in rows:
        for column in REQUIRED_COLUMNS:
            if not row[column].strip():
                raise AssertionError(f"blank {column} for {row['trait_id']}")
    checks += 1

    orientation = by_trait["orientation"]
    if orientation["cross_axis_class"] != "priority_space_time_ecology_bridge":
        raise AssertionError("orientation must remain the priority space-time-ecology bridge")
    if "BIO12" not in orientation["azami_space_result"] or "BIO15" not in orientation["eazami_ecology_result"]:
        raise AssertionError("orientation ledger must preserve distinct BIO12 and BIO15 evidence")
    if "rain adaptation" not in orientation["forbidden_upgrade"]:
        raise AssertionError("orientation rain-adaptation claim ceiling was lost")
    checks += 3

    colour = by_trait["colour_continuous"]
    if colour["cross_axis_class"] != "space_only_radiation_sorting_candidate":
        raise AssertionError("colour must remain a spatial radiation candidate, not a repeated-history claim")
    if "beta=-0.345372" not in colour["azami_space_result"]:
        raise AssertionError("colour ledger lost the frozen negative RSDS-chroma direction")
    if "anthocyanin mediation" not in colour["forbidden_upgrade"]:
        raise AssertionError("colour anthocyanin claim ceiling was lost")
    checks += 3

    for trait_id in ("phyllary_posture", "stickiness"):
        row = by_trait[trait_id]
        if row["eazami_ecology_status"] != "not_evaluable":
            raise AssertionError(f"{trait_id} must remain not_evaluable under current climate overlap")
        if "no ecological relationship" not in row["forbidden_upgrade"]:
            raise AssertionError(f"{trait_id} must forbid rewriting not_evaluable as no relationship")
    checks += 2

    if not SYNTHESIS.exists():
        raise AssertionError(f"missing synthesis document: {SYNTHESIS}")
    synthesis_text = SYNTHESIS.read_text(encoding="utf-8")
    required_phrases = (
        "Azami = diversity breadth",
        "EAzami = diversity depth",
        "cross-scale hydric correspondence",
        "higher mean shortwave radiation (`rsds`) aligns with **lower CIELAB corolla chroma**",
        "Chapter 2 is not required to turn every phenotype into an adaptive story",
        "Spatial association plus repeated history is not itself adaptation or convergence",
    )
    missing_phrases = [phrase for phrase in required_phrases if phrase not in synthesis_text]
    if missing_phrases:
        raise AssertionError(f"synthesis lost canonical claims: {missing_phrases}")
    checks += 2

    if not README.exists():
        raise AssertionError(f"missing Chapter 2 README: {README}")
    readme_text = README.read_text(encoding="utf-8")
    if "SPACE_TIME_PUBLIC_DATA_SYNTHESIS_V1.md" not in readme_text:
        raise AssertionError("Chapter 2 README does not route to the space-time synthesis")
    if "chapter2_space_time_public_data_closure_v1.csv" not in readme_text:
        raise AssertionError("Chapter 2 README does not route to the closure ledger")
    checks += 2

    missing_inputs = [str(path.relative_to(ROOT)) for path in CANONICAL_INPUTS if not path.exists()]
    if missing_inputs:
        raise AssertionError(f"canonical synthesis inputs are missing: {missing_inputs}")
    checks += 1

    return checks


def main() -> None:
    checks = validate()
    print(f"chapter2 space-time public-data closure: {checks} checks passed")


if __name__ == "__main__":
    main()
