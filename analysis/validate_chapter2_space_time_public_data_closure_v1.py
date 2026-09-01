#!/usr/bin/env python3
"""Validate the frozen Chapter 2 space-time closure while allowing superseding routes.

The v1 ledger and V3 synthesis remain immutable historical audit products.  The
active Chapter 2 entrypoint may now route to the V6 differentiation-through-time
programme, provided that the new route preserves the old claim ceilings rather
than silently rewriting the frozen results.
"""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data/evidence/chapter2_space_time_public_data_closure_v1.csv"
SYNTHESIS = ROOT / "docs/chapter2/SPACE_TIME_PUBLIC_DATA_SYNTHESIS_V1.md"
README = ROOT / "docs/chapter2/README.md"
FINAL_V3 = ROOT / "data/evidence/chapter2_final_integrated_evidence_v3.json"
FINAL_STORY_V3 = ROOT / "docs/chapter2/PUBLIC_DATA_FINAL_CHAPTER2_STORY_AND_ANALYSIS_PLAN_V3.md"
V6_CONTRACT = ROOT / "data/evidence/chapter2_differentiation_time_axis_contract_v1.json"
V6_TRIGGER_CONTRACT = ROOT / "data/evidence/chapter2_historical_differentiation_trigger_contract_v1.json"
V6_OUTLINE = ROOT / "docs/chapter2/MANUSCRIPT_JEB_V6_REFRAME_OUTLINE.md"
V6_TRIGGER_RESULT = ROOT / "docs/chapter2/HISTORICAL_DIFFERENTIATION_TRIGGER_RESULT_V1.md"

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

    # Frozen v1 scientific checks remain unchanged.
    orientation = by_trait["orientation"]
    if orientation["cross_axis_class"] != "priority_space_time_ecology_bridge":
        raise AssertionError("orientation must remain the frozen priority space-time-ecology bridge")
    if "BIO12" not in orientation["azami_space_result"] or "BIO15" not in orientation["eazami_ecology_result"]:
        raise AssertionError("orientation ledger must preserve distinct BIO12 and BIO15 evidence")
    if "rain adaptation" not in orientation["forbidden_upgrade"]:
        raise AssertionError("orientation rain-adaptation claim ceiling was lost")
    checks += 3

    colour = by_trait["colour_continuous"]
    if colour["cross_axis_class"] != "space_only_radiation_sorting_candidate":
        raise AssertionError("frozen v1 colour ledger changed unexpectedly")
    if "beta=-0.345372" not in colour["azami_space_result"]:
        raise AssertionError("colour ledger lost the frozen negative RSDS-chroma direction")
    if "anthocyanin mediation" not in colour["forbidden_upgrade"]:
        raise AssertionError("colour anthocyanin claim ceiling was lost")
    checks += 3

    for trait_id in ("phyllary_posture", "stickiness"):
        row = by_trait[trait_id]
        if row["eazami_ecology_status"] != "not_evaluable":
            raise AssertionError(f"{trait_id} must remain not_evaluable in frozen v1")
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
        raise AssertionError(f"frozen synthesis lost canonical claims: {missing_phrases}")
    checks += 2

    if not README.exists():
        raise AssertionError(f"missing Chapter 2 README: {README}")
    readme_text = README.read_text(encoding="utf-8")
    legacy_route = (
        "SPACE_TIME_PUBLIC_DATA_SYNTHESIS_V1.md" in readme_text
        and "chapter2_space_time_public_data_closure_v1.csv" in readme_text
    )
    v3_route = (
        "PUBLIC_DATA_FINAL_CHAPTER2_STORY_AND_ANALYSIS_PLAN_V3.md" in readme_text
        and "chapter2_final_integrated_evidence_v3.json" in readme_text
    )
    v6_route = (
        "chapter2_differentiation_time_axis_contract_v1.json" in readme_text
        and "MANUSCRIPT_JEB_V6_REFRAME_OUTLINE.md" in readme_text
        and "HISTORICAL_DIFFERENTIATION_TRIGGER_RESULT_V1.md" in readme_text
    )
    if not (legacy_route or v3_route or v6_route):
        raise AssertionError("Chapter 2 README routes to neither frozen v1/V3 nor active V6 differentiation synthesis")

    if v3_route:
        if not FINAL_V3.exists() or not FINAL_STORY_V3.exists():
            raise AssertionError("README routes to V3 but V3 final synthesis assets are missing")
        final_text = FINAL_STORY_V3.read_text(encoding="utf-8")
        for phrase in (
            "hierarchical scale dependence",
            "modular hierarchical selection-mosaic model",
            "does **not** establish adaptation",
        ):
            if phrase not in final_text:
                raise AssertionError(f"V3 final story lost required boundary: {phrase}")

    if v6_route:
        for path in (V6_CONTRACT, V6_TRIGGER_CONTRACT, V6_OUTLINE, V6_TRIGGER_RESULT):
            if not path.exists() or path.stat().st_size == 0:
                raise AssertionError(f"V6 route is missing {path.relative_to(ROOT)}")
        combined = "\n".join(
            p.read_text(encoding="utf-8") for p in (V6_OUTLINE, V6_TRIGGER_RESULT, README)
        )
        for phrase in (
            "differentiation",
            "relative lineage",
            "not_evaluable",
            "reproductive fitness",
        ):
            if phrase.lower() not in combined.lower():
                raise AssertionError(f"V6 differentiation route lost boundary phrase: {phrase}")
        if "rain adaptation" in combined.lower() and "does not" not in combined.lower():
            raise AssertionError("V6 must not promote rain adaptation from historical alignment")
        checks += 2

    checks += 3

    missing_inputs = [str(path.relative_to(ROOT)) for path in CANONICAL_INPUTS if not path.exists()]
    if missing_inputs:
        raise AssertionError(f"canonical frozen synthesis inputs are missing: {missing_inputs}")
    checks += 1

    return checks


def main() -> None:
    checks = validate()
    print(f"chapter2 frozen closure + active route: {checks} checks passed")


if __name__ == "__main__":
    main()
