#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "data" / "evidence"
MANUSCRIPT = ROOT / "docs" / "chapter2" / "MANUSCRIPT_JEB_V9_5_ORGANIZATION_SPINE.md"
FIGMAP = ROOT / "docs" / "chapter2" / "V9_5_FIGURE_MAP_AND_SUBMISSION_GATE.md"
BIB = ROOT / "docs" / "chapter2" / "V9_5_BIBLIOGRAPHY_AUDIT.md"


def load_json(name: str) -> dict:
    return json.loads((EVID / name).read_text(encoding="utf-8"))


def words(text: str) -> int:
    return len(re.findall(r"\b[\w'’*-]+\b", text))


def require(text: str, token: str) -> None:
    if token not in text:
        raise AssertionError(f"required V9.5 token missing: {token!r}")


def forbid(text: str, token: str) -> None:
    if token.lower() in text.lower():
        raise AssertionError(f"forbidden V9.5 overclaim present: {token!r}")


def main() -> None:
    text = MANUSCRIPT.read_text(encoding="utf-8")
    fig = FIGMAP.read_text(encoding="utf-8")
    bib = BIB.read_text(encoding="utf-8")
    hist = load_json("chapter2_historical_differentiation_final_summary_v1.json")
    depth = load_json("chapter2_depth_ordering_robustness_result_v1.json")
    coverage = load_json("chapter2_depth_coverage_matched_sensitivity_result_v1.json")
    common9 = load_json("chapter2_three_trait_common9_result_v1.json")
    claims = load_json("chapter2_current_claims_h1_h4_v1.json")

    require(text, "# Repeated reassembly of a complex reproductive phenotype across unequal evolutionary depths in a young thistle radiation")
    abstract = text.split("## Abstract\n\n", 1)[1].split("\n\n**Keywords:**", 1)[0]
    if words(abstract) > 250:
        raise AssertionError(f"abstract exceeds JEB 250-word limit: {words(abstract)}")
    keywords = text.split("**Keywords:**", 1)[1].split("\n", 1)[0]
    keyword_n = len([x for x in keywords.split(";") if x.strip()])
    if not 4 <= keyword_n <= 10:
        raise AssertionError(f"keyword count outside 4-10: {keyword_n}")
    main_before_refs = text.split("# References", 1)[0]
    if words(main_before_refs) > 7500:
        raise AssertionError(f"main text exceeds 7500 words: {words(main_before_refs)}")

    rec = hist["recurrence_and_depth"]
    assert rec["orientation"]["minimum_changes_ufboot_range"] == [4, 6]
    assert rec["phyllary_posture"]["minimum_changes"] == 3
    assert rec["stickiness"]["minimum_changes"] == 5
    assert rec["shared_transition_localization"].startswith("0/3")
    for token in ("four to six", "exactly three", "exactly five", "Zero of three"):
        require(text, token)

    pair = {(r["deeper_candidate"], r["shallower_candidate"]): r for r in depth["pairwise_results"]}
    assert pair[("phyllary", "stickiness")]["fraction_prespecified_deeper_direction"] == 1.0
    assert pair[("phyllary", "orientation")]["fraction_prespecified_deeper_direction"] == 0.993
    assert pair[("orientation", "stickiness")]["fraction_prespecified_deeper_direction"] == 0.905
    assert depth["complete_lower_bound_ordering"]["count"] == 898
    for token in ("1,000/1,000", "993/1,000", "905/1,000", "898/1,000"):
        require(text, token)

    assert coverage["overall_classification"] == "unequal_depth_retained_against_matched_medians_but_strict_tail_overlap_remains"
    require(text, "Coverage-matched masking retained the central phyllary-deeper pattern")

    assert common9["primary"]["orientation"]["omnibus_nine_environment_rank"] == "2138/6188 = 34.55%"
    assert common9["primary"]["stickiness"]["omnibus_nine_environment_rank"] == "116/924 = 12.55%"
    assert common9["multiplicity"]["supported_rows_q_lt_0_05"] == 0
    for token in ("2138/6188 (34.55%)", "116/924 (12.55%)", "state replication was insufficient"):
        require(text, token)

    h1 = claims["orientation_transition_regime"]["h1"]
    h2 = claims["orientation_transition_regime"]["h2"]
    h3 = claims["orientation_transition_regime"]["h3"]
    assert h1["n5_12_taxa_exact_rank"] == "16/792 = 2.02%"
    assert h1["n3_13_taxa_exact_rank"] == "19/1716 = 1.11%"
    assert h1["strict_n10_exact_rank"] == "4/126 = 3.17%"
    assert h2["exact_bidirectional_floor_rank"] == "3/126 = 2.38%"
    assert h3["exact_exceptionality_pass"] == "3/9"
    for token in ("16/792 (2.02%)", "19/1,716 (1.11%)", "4/126 (3.17%)", "3/126 (2.38%)", "3/9"):
        require(text, token)

    # Catch affirmative overclaims without rejecting explicit boundary statements such as
    # "not interpreted as independent adaptive origins".
    for bad in (
        "independent origins were demonstrated",
        "we demonstrate independent adaptive origins",
        "adaptation was demonstrated",
        "we demonstrate adaptation",
        "BIO15 causes orientation",
        "BIO1 causes orientation",
        "phyllary has no ecological relationship",
        "stickiness follows a universal precipitation law",
        "relative lineage depth is calendar time",
    ):
        forbid(text, bad)
    # Explicit claim-boundary language must remain present.
    require(text, "not interpreted as counts of independent adaptive origins")
    require(text, "not the historical selective cause")

    for token in ("Figure 1", "Figure 2", "Figure 3", "Figure 4", "0/3", "1000/1000", "coverage-matched"):
        require(fig, token)

    for doi in (
        "10.1016/j.ympev.2025.108285",
        "10.1080/17550874.2012.702793",
        "10.2307/3672545",
        "10.22543/0090-0222.2085",
        "10.2307/1940645",
        "10.1890/0012-9658(2002)083[3382:CDEOIA]2.0.CO;2",
        "10.1007/s00442-017-4027-9",
        "10.1002/ecs2.70310",
    ):
        require(bib, doi)

    print(f"V9.5 validation passed; abstract_words={words(abstract)}, keywords={keyword_n}, main_words={words(main_before_refs)}")


if __name__ == "__main__":
    main()
