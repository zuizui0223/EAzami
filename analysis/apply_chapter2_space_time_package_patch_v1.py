#!/usr/bin/env python3
"""Apply the frozen space-time package patch to JEB V4/V2 sources.

The script never changes the frozen source files in place. It emits versioned
production Markdown so every wording change remains reproducible and auditable.
"""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CH = ROOT / "docs" / "chapter2"

INTRO_BRIDGE = (
    "\n\nCoordinate-bearing public photographs make it possible to examine a decomposed "
    "capitulum phenotype along two orthogonal axes. A companion spatial analysis maps "
    "the breadth of present-day continuous phenotype–environment structure, whereas the "
    "present study asks how constituent states are assembled and reassembled through "
    "phylogenetic history. The two axes are intentionally independent: a trait need not "
    "show a strong spatial association to have a repeated history, and a strong spatial "
    "association need not have a resolved repeated history.\n"
)

METHODS_SENS = """
\n## Occurrence-source sensitivity

The GBIF-only n≥10 occurrence panel remained the frozen primary. We separately audited Taiwan Biodiversity Network (TBN v2.6) records under unchanged taxon-state definitions, Taiwan scope, coordinate-quality rules and 0.05-degree spatial thinning. Two admissible sensitivity tiers were retained: direct TBN-native records and a broader source-name-guarded tier excluding explicit GBIF mirrors. The primary analysis was not replaced according to which tier crossed P<0.05. The sensitivity estimand was whether effect direction, species leave-one-out stability and the threshold-based ecological classification changed under alternative occurrence-source definitions used to estimate present-day taxon niche centroids.
"""

RESULTS_SENS = """
\n## Orientation direction is robust but threshold support is occurrence-source sensitive

Direct TBN-native additions increased the panel to 11 taxa (U=6, D=5) without lowering the n≥10 gate. Across all six accepted topologies, BIO1 remained negative (D−U = −1.001 to −0.994 SD; P=0.04819–0.04904) and BIO15 remained positive (+1.136 to +1.143 SD; P=0.03789–0.03980); both directions survived 66/66 topology × species leave-one-out fits. This tier was `tendency_supported` under the frozen rule. A broader source-name-guarded TBN tier retained the same 11 taxa but yielded BIO1 = −0.915 to −0.909 SD (P=0.06525–0.06598) and BIO15 = +1.078 to +1.084 SD (P=0.04874–0.05110), again with 6/6 topology and 66/66 leave-one-out sign agreement; this tier was `unresolved`. Thus, biological direction was robust to accepted topology, single-species deletion and occurrence-source expansion, whereas threshold crossing was sensitive to the admissible occurrence-source definition used to estimate present-day niche centroids. The direct-TBN tier was not promoted to the primary after observing its P values.
"""

DISCUSSION_BRIDGE = """
\nThe public-data programme separates diversity breadth from diversity depth. In the spatial Azami analysis, orientation is sorted among taxa along annual precipitation amount, whereas in the East-Asian EAzami comparison the downward state is consistently associated with higher precipitation seasonality. BIO12 and BIO15 represent distinct dimensions of the hydric regime, so these results are not a replication of one coefficient. Together they establish a cross-scale hydric correspondence that motivates the hypothesis that capitulum orientation may be sensitive to multiple components of reproductive exposure to rainfall, while flowering-period interception, pollen performance and reproductive fitness remain unmeasured. Visible corolla chroma provides the complementary asymmetric case: it is strongly sorted among taxa along shortwave radiation in the spatial analysis, but its Japanese time-axis history remains unresolved. The space–history evidence chain is therefore trait-specific rather than a universal capitulum syndrome. Phyllary posture and stickiness retain repeated-history results while their current ecology remains `not_evaluable`.
"""

ABSTRACT_SENTENCE = (
    " Independent Taiwan occurrence-source sensitivities retained both BIO15 and BIO1 "
    "directions across all accepted topologies and species leave-one-out fits, while the "
    "threshold-based class changed between `tendency_supported` and `unresolved`."
)

SI_TAIWAN = """
\n## Table S4b — Taiwan occurrence-source sensitivity

The GBIF-only panel remains the frozen primary. Alternative TBN tiers test source sensitivity without lowering the n≥10 gate or changing accepted phylogenetic topologies.

| Occurrence tier | n (U/D) | BIO15 D−U | BIO1 D−U | Topology sign | Species-LOO sign | Frozen-rule class |
| --- | --- | --- | --- | --- | --- | --- |
| GBIF-only primary | 9 (5/4) | +1.320 to +1.330 SD; P=0.05054–0.05239 | −0.975 to −0.967 SD; P=0.09604–0.09793 | 6/6 both axes | 54/54 both axes | `unresolved` |
| direct TBN-native | 11 (6/5) | +1.136 to +1.143 SD; P=0.03789–0.03980 | −1.001 to −0.994 SD; P=0.04819–0.04904 | 6/6 both axes | 66/66 both axes | `tendency_supported` |
| broader non-GBIF-mirror TBN | 11 (6/5) | +1.078 to +1.084 SD; P=0.04874–0.05110 | −0.915 to −0.909 SD; P=0.06525–0.06598 | 6/6 both axes | 66/66 both axes | `unresolved` |

The effect direction is topology-, taxon-deletion- and occurrence-source-stable, whereas threshold crossing is sensitive to the admissible occurrence-source definition. The direct-TBN tier is not outcome-selected as a replacement primary. These are present-day niche-centroid sensitivities, not ancestral-climate reconstruction or evidence of adaptation.
"""


def insert_once(text: str, marker: str, insertion: str, *, before: bool = True) -> str:
    if insertion.strip() in text:
        return text
    if marker not in text:
        raise ValueError(f"patch marker not found: {marker!r}")
    if before:
        return text.replace(marker, insertion + "\n" + marker, 1)
    return text.replace(marker, marker + insertion, 1)


def patch_manuscript(text: str) -> str:
    if ABSTRACT_SENTENCE.strip() not in text:
        marker = "Thus, repeated minimum changes are common across traits, whereas historical resolution and the amount that existing ecology can explain differ sharply among them."
        if marker not in text:
            raise ValueError("abstract marker not found")
        replacement = (
            "Thus, repeated minimum changes are common across traits, whereas historical resolution, ecological evaluability and inferential-threshold support differ sharply among them."
            + ABSTRACT_SENTENCE
        )
        text = text.replace(marker, replacement, 1)

    text = insert_once(text, "# Materials and methods", INTRO_BRIDGE, before=True)
    text = insert_once(text, "## Supporting non-climate constraints", METHODS_SENS, before=True)

    result_anchor = "Phyllary posture and stickiness were `not_evaluable`"
    if RESULTS_SENS.strip() not in text:
        idx = text.find(result_anchor)
        if idx < 0:
            raise ValueError("results ecology anchor not found")
        heading_idx = text.rfind("\n## ", 0, idx)
        # Insert after the full orientation ecology subsection by locating the next heading.
        next_heading = text.find("\n## ", idx)
        if next_heading < 0:
            raise ValueError("next results heading not found")
        text = text[:next_heading] + RESULTS_SENS + text[next_heading:]

    discussion_anchor = "# Conclusion"
    text = insert_once(text, discussion_anchor, DISCUSSION_BRIDGE, before=True)

    prohibited = [
        "rain adaptation",
        "rain-protection adaptation",
        "adaptive convergence",
    ]
    for phrase in prohibited:
        if phrase in DISCUSSION_BRIDGE.lower():
            raise AssertionError(f"prohibited phrase introduced: {phrase}")
    return text


def patch_si(text: str) -> str:
    return insert_once(text, "## Table S5 — Predictive diagnostic retained as sensitivity, not the main ecological decision", SI_TAIWAN, before=True)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--manuscript-in", type=Path, default=CH / "MANUSCRIPT_JEB_V4.md")
    p.add_argument("--si-in", type=Path, default=CH / "JEB_SUPPORTING_INFORMATION_V2.md")
    p.add_argument("--manuscript-out", type=Path, default=CH / "MANUSCRIPT_JEB_V5.md")
    p.add_argument("--si-out", type=Path, default=CH / "JEB_SUPPORTING_INFORMATION_V3.md")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    manuscript = patch_manuscript(args.manuscript_in.read_text(encoding="utf-8"))
    si = patch_si(args.si_in.read_text(encoding="utf-8"))
    args.manuscript_out.parent.mkdir(parents=True, exist_ok=True)
    args.si_out.parent.mkdir(parents=True, exist_ok=True)
    args.manuscript_out.write_text(manuscript, encoding="utf-8")
    args.si_out.write_text(si, encoding="utf-8")
    print(args.manuscript_out)
    print(args.si_out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
