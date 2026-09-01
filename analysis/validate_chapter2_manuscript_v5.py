#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CH = ROOT / "docs" / "chapter2"
EVID = ROOT / "data" / "evidence"
MANUSCRIPT = CH / "MANUSCRIPT_JEB_V5.md"
FIGMAP = CH / "JEB_QUESTION_RESULT_FIGURE_MAP_V5.md"
FINAL = EVID / "chapter2_final_integrated_evidence_v3.json"
ORIGIN = EVID / "chapter2_orientation_origin_envelope_result_v1.json"
IMAGE = EVID / "chapter2_four_taxon_azami_measurement_result_v1.json"
RSDS = EVID / "chapter2_colour_rsds_focal_concordance_result_v1.json"


def section(text: str, start: str, end: str) -> str:
    a = text.index(start) + len(start)
    b = text.index(end, a)
    return text[a:b]


def count_words(text: str) -> int:
    text = re.sub(r"https?://\S+", "", text)
    return len(re.findall(r"\b[\w’'−–.-]+\b", text, flags=re.UNICODE))


def main() -> int:
    for path in (MANUSCRIPT, FIGMAP, FINAL, ORIGIN, IMAGE, RSDS):
        assert path.exists(), path

    text = MANUSCRIPT.read_text(encoding="utf-8")
    fig = FIGMAP.read_text(encoding="utf-8")
    final = json.loads(FINAL.read_text(encoding="utf-8"))
    origin = json.loads(ORIGIN.read_text(encoding="utf-8"))
    image = json.loads(IMAGE.read_text(encoding="utf-8"))
    rsds = json.loads(RSDS.read_text(encoding="utf-8"))

    assert text.startswith("# Modular evolutionary depth and lineage-dependent environmental correspondence")
    assert "active standalone submission draft v5" in text
    assert final["chapter_model"] == "modular_hierarchical_selection_mosaic_with_partial_coordinated_remodelling"
    assert final["n_rows"] == 7

    abstract = section(text, "## Abstract\n", "**Keywords:**")
    abstract_words = count_words(abstract)
    assert abstract_words <= 250, abstract_words

    main_text = text.split("# References", 1)[0]
    main_words = count_words(main_text)
    assert main_words <= 7500, main_words

    rows = {r["trait_driver"]: r for r in final["rows"]}
    orient = rows["orientation × hydric exposure"]
    colour = rows["flower colour × radiative environment"]
    whole = rows["whole capitulum × common syndrome versus modular mosaic"]

    # Orientation history and origin envelope must match the final V3 source.
    assert "four to six minimum changes" in text
    assert "0.795–0.994" in text
    assert "0.695–1.000" in text
    assert "0.937–0.954" in text
    assert "94 admissible chronology scenarios" in text
    assert "376 region × chronology" in text
    assert "−0.799" in text and "−0.065" in text and "+0.609" in text
    assert origin["chronology"]["n_valid_age_pairs"] == 94
    assert origin["cross_scenario_summary"]["n_region_by_chronology_scenarios"] == 376
    assert origin["cross_scenario_summary"]["classification"] in orient["key_quantitative_result"]
    assert "origin environment remained unresolved" in text

    # Colour bridge must preserve the directional replication and the 1/2 RSDS result.
    assert image["colour_assay_gate"]["passed"] is True
    assert image["repeated_same_direction_across_two_sister_systems"]["corolla_lab_chroma"] == "white_lower"
    assert image["repeated_same_direction_across_two_sister_systems"]["shape_circularity"] == "white_higher"
    assert image["repeated_same_direction_across_two_sister_systems"]["shape_solidity"] == "white_higher"
    assert image["repeated_same_direction_across_two_sister_systems"]["visible_floret_fraction_extended"] == "white_lower"
    assert rsds["chapter_summary"]["classification"] == "partial_current_rsds_chroma_directional_concordance"
    assert rsds["chapter_summary"]["primary_concordant_systems"] == 1
    assert "+1814" in text and "−686.5" in text and "−1703" in text
    assert "beta=−0.4065" in text
    assert "1/2 pair-level primary" in text
    assert "lineage- and scale-dependent current correspondence" in text
    assert "universal_ST1_persistent_RSDS_driver_weakened" in colour["process_model"]

    # Whole-capitulum conclusion must stay intermediate rather than switching to either extreme.
    assert whole["final_class"] == "partial_module_covariation_universal_synchronized_syndrome_not_supported"
    assert "neither complete trait independence nor one synchronized syndrome" in text.lower()
    assert "partial coordinated remodelling" in text.lower()
    assert "rho=0.3663" in text

    required_methods = [
        "Public chronology and palaeolocation envelope for orientation",
        "Public-image natural experiments for flower colour and head geometry",
        "Focal current RSDS concordance in the two colour systems",
        "Integrated whole-capitulum synthesis",
        "Transparency, Supporting Information and generative-AI assistance",
    ]
    for phrase in required_methods:
        assert phrase in text, phrase

    # Submission transparency must be explicit in the anonymous main text.
    transparency = [
        "Generative AI assisted with code and prose development",
        "AI tools did not determine botanical states",
        "did not generate or alter the underlying observational data",
        "Supporting Information (Figs. S1–S9; Tables S2.1–S12)",
    ]
    for phrase in transparency:
        assert phrase in text, phrase

    # Every active main figure and its corresponding SI family must be called from the text.
    for i in range(1, 6):
        assert f"(Fig. {i}" in text, f"missing main-text Figure {i} call"
    for si_call in [
        "Supporting Information Figs. S1–S2",
        "Supporting Information Fig. S2",
        "Supporting Information Figs. S3–S5",
        "Supporting Information Figs. S6–S7",
        "Supporting Information Fig. S8",
        "Supporting Information Fig. S9 and Tables S10–S12",
    ]:
        assert si_call in text, si_call

    required_refs = [
        "Barreto, E., Holden, P. B., Edwards, N. R., & Rangel, T. F. (2023)",
        "Chang, C.-Y., Liao, P.-C., Tzeng, H.-Y., Kusumi, J., Su, Z.-H., & Tseng, Y.-H. (2025)",
        "Chang, C.-Y., Liao, P.-C., Tzeng, H.-Y., Kusumi, J., Su, Z.-H., & Tseng, Y.-H. (2026)",
        "Karger, D. N., Conrad, O., Böhner, J.",
        "Moreyra, L. D., Susanna, A.",
    ]
    for phrase in required_refs:
        assert phrase in text, phrase

    forbidden = [
        "we demonstrate rain adaptation",
        "we demonstrate adaptive convergence",
        "radiation caused white flowers",
        "the colour transition occurred at 0.93 ma",
        "the colour transition occurred at 0.35 ma",
        "bio12 and bio15 are the same",
        "one synchronized capitulum syndrome is supported",
        "the traits are completely independent",
        "historical rsds reconstruction shows",
    ]
    low = text.casefold()
    for phrase in forbidden:
        assert phrase.casefold() not in low, phrase

    # Figure map must preserve the same primary estimands and five-figure structure.
    for i in range(1, 6):
        assert f"## Figure {i}" in fig
    for phrase in [
        "376 origin scenarios",
        "Pair-level Azami-direction concordance = **1/2**",
        "partial coordinated remodelling inside modular, lineage-dependent histories",
        "Do not average Arenicola and Taiwan RSDS contrasts",
        "Do not call repeated white-state chroma a demonstrated pigment pathway",
    ]:
        assert phrase in fig, phrase

    print(json.dumps({
        "status": "VALID",
        "abstract_words": abstract_words,
        "main_text_words_before_references": main_words,
        "orientation_origin": origin["cross_scenario_summary"]["classification"],
        "colour_rsds": rsds["chapter_summary"]["classification"],
        "chapter_model": final["chapter_model"],
        "figure_calls": 5,
        "ai_disclosure": True,
        "supporting_information_cited": True,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
