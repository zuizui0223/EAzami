#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "data" / "evidence"
DOC = ROOT / "docs" / "chapter2"
MAN = DOC / "MANUSCRIPT_JEB_V9_6_SCALE_CONDITIONED_ECOLOGY.md"
FIG = DOC / "V9_6_FIGURE_MAP_AND_CLAIM_ARCHITECTURE.md"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require(text: str, token: str) -> None:
    if token not in text:
        raise AssertionError(f"required token missing: {token!r}")


def forbid(text: str, token: str) -> None:
    if token.casefold() in text.casefold():
        raise AssertionError(f"forbidden claim present: {token!r}")


def words(text: str) -> int:
    return len(re.findall(r"\b[\w'’*-]+\b", text))


def main() -> None:
    text = MAN.read_text(encoding="utf-8")
    fig = FIG.read_text(encoding="utf-8")
    hist = load_json(EVID / "chapter2_historical_differentiation_final_summary_v1.json")
    depth = load_json(EVID / "chapter2_depth_ordering_robustness_result_v1.json")
    common = load_json(EVID / "chapter2_three_trait_common9_result_v1.json")
    azami = load_json(EVID / "azami_orientation_crossscale_validation_audit_v1.json")
    held = (DOC / "HELDOUT_ORIENTATION_OCCURRENCE_GATE_V2_RESULT.md").read_text(encoding="utf-8")

    require(text, "V9.6 scale-conditioned ecology manuscript draft")
    abstract = text.split("## Abstract\n\n", 1)[1].split("\n\n**Keywords:**", 1)[0]
    keywords = text.split("**Keywords:**", 1)[1].split("\n", 1)[0]
    keyword_n = len([x for x in keywords.split(";") if x.strip()])
    body = text.split("# References", 1)[0]
    if words(abstract) > 250:
        raise AssertionError(f"abstract exceeds 250 words: {words(abstract)}")
    if not 4 <= keyword_n <= 10:
        raise AssertionError(f"keyword count outside 4-10: {keyword_n}")
    if words(body) > 7500:
        raise AssertionError(f"main text exceeds 7500 words: {words(body)}")

    # Current JEB anonymous-main routing.
    require(text, "## Transparency and reproducibility")
    require(text, "Generative-AI assistance was used")
    require(text, "Supporting Information")
    if text.index("## Transparency and reproducibility") > text.index("# Results"):
        raise AssertionError("AI/transparency disclosure must remain in Materials and Methods before Results")
    for forbidden_submission_section in (
        "# Transparency and data availability",
        "## Submission-preparation notes",
        "# Data Availability",
        "# Acknowledgements",
        "# Funding",
        "# Conflict of Interest",
    ):
        if forbidden_submission_section in text:
            raise AssertionError(f"anonymous main retains title-page-only material: {forbidden_submission_section}")

    # Historical core must remain unchanged.
    rec = hist["recurrence_and_depth"]
    assert rec["orientation"]["minimum_changes_ufboot_range"] == [4, 6]
    assert rec["phyllary_posture"]["minimum_changes"] == 3
    assert rec["stickiness"]["minimum_changes"] == 5
    assert rec["shared_transition_localization"].startswith("0/3")
    pair = {(x["deeper_candidate"], x["shallower_candidate"]): x for x in depth["pairwise_results"]}
    assert pair[("phyllary","stickiness")]["fraction_prespecified_deeper_direction"] == 1.0
    assert pair[("phyllary","orientation")]["fraction_prespecified_deeper_direction"] == 0.993
    assert pair[("orientation","stickiness")]["fraction_prespecified_deeper_direction"] == 0.905
    assert depth["complete_lower_bound_ordering"]["count"] == 898
    for token in ("four to six", "exactly three", "exactly five", "1,000/1,000", "993/1,000", "905/1,000", "Zero of three"):
        require(text, token)

    # Common static ecological comparison.
    assert common["primary"]["orientation"]["n_taxa"] == 17
    assert common["primary"]["phyllary"]["n_taxa"] == 4
    assert common["primary"]["stickiness"]["n_taxa"] == 12
    assert common["multiplicity"]["supported_rows_q_lt_0_05"] == 0
    for token in ("2138/6188", "116/924", "27-row family"):
        require(text, token)

    # Existing Azami cross-scale evidence: not prospective P3.
    assert azami["decision"] == "NOT_ELIGIBLE_AS_PROSPECTIVE_P3"
    within = azami["azami_existing_within_taxon"]
    among = azami["azami_existing_among_taxon"]
    assert within["BIO1"]["q_fdr"] < 0.05
    assert within["BIO1"]["spatial_permutation_p"] == 0.002
    assert within["BIO15"]["q_fdr"] > 0.05
    assert within["BIO12"]["q_fdr"] > 0.8
    assert among["BIO12"]["beta_std"] > 0.3
    for token in (
        "+0.304359",
        "+0.0171503",
        "+0.0265374",
        "-0.0076180",
        "q = 0.183",
        "opposite",
        "not a prospective held-out test",
    ):
        require(text, token)

    # Held-out external panel must be reported as resolution failure before ecology.
    for token in (
        "13-taxon orientation panel",
        "3 downward, 10 upward",
        "Cirsium vulgare",
        "16 thinned records",
        "BIO1 and BIO15 were never extracted",
        "occurrence-metadata resolution ceiling",
    ):
        require(text, token)
    assert "downward/nodding: **0 taxa**" in held
    assert "upward/erect: **1 taxon**" in held

    # Ecological synthesis and stop rule.
    for token in (
        "scale- and representation-dependent",
        "Public-data expansion is stopped",
        "additional taxon panels",
        "aza3",
    ):
        require(text, token)
    deletion = load_json(EVID / "chapter2_orientation_transition_regime_single_deletion_result_v1.json")
    assert deletion["n_deletions"] == 9
    assert deletion["n_exact_exceptionality_pass"] == 2
    require(text, "9/9 single-taxon deletions")
    require(text, "exact finite-map exceptionality persisted in 2/9")
    forbid(text, "exact finite-map exceptionality persisted in 3/9")

    for bad in (
        "external confirmation supports",
        "independent held-out confirmation was successful",
        "orientation adaptation is demonstrated",
        "BIO15 causes orientation",
        "temperature causes orientation",
        "stickiness is a universal defence",
    ):
        forbid(text, bad)

    # Figure routing.
    for token in (
        "Figure 4",
        "Azami among-taxon BIO12",
        "Azami within-taxon BIO1",
        "EAzami transition-level",
        "D=0, U=1",
        "environment unopened",
    ):
        require(fig, token)

    print(json.dumps({
        "status":"ok",
        "abstract_words":words(abstract),
        "main_text_words_before_references":words(body),
        "keyword_count":keyword_n,
        "historical_core":"unchanged",
        "ecology":"scale_and_representation_dependent",
        "heldout_external":"not_evaluable_environment_unopened",
        "azami_p3":"not_eligible_as_prospective_confirmation"
    }, indent=2))


if __name__ == "__main__":
    main()
