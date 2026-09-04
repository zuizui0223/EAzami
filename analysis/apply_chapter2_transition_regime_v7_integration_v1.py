#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "docs" / "chapter2" / "MANUSCRIPT_JEB_V7_WORKING.md"
FIGMAP = ROOT / "docs" / "chapter2" / "JEB_V7_FIGURE_MAP.md"


def replace_exact(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise AssertionError(f"{label}: expected exactly one match, found {n}")
    return text.replace(old, new, 1)


def insert_before(text: str, marker: str, block: str, unique_token: str) -> str:
    if unique_token in text:
        raise AssertionError(f"integration already present: {unique_token}")
    if marker not in text:
        raise AssertionError(f"marker missing: {marker}")
    return text.replace(marker, block.rstrip() + "\n\n" + marker, 1)


def replace_section(text: str, heading: str, next_heading: str, body: str) -> str:
    start = text.find(heading)
    if start < 0:
        raise AssertionError(f"section heading missing: {heading}")
    end = text.find(next_heading, start + len(heading))
    if end < 0:
        raise AssertionError(f"next section heading missing: {next_heading}")
    return text[:start] + heading + "\n\n" + body.strip() + "\n\n" + text[end:]


def update_manuscript(text: str) -> str:
    old_abs = (
        "Present orientation–environment correspondence was scale-partitioned and history-embedded: "
        "the BIO15 contrast was unusual among all 126 state-count-preserving counterfactual maps (5/126) "
        "but not after conditioning on matched recurrence and near-matched relative depth (3/10). "
        "Historical cause was less identifiable: only one orientation transition reached a bounded chronology "
        "and palaeolocation envelope, and no recurring coarse climate or global sea-level regime survived propagated uncertainty."
    )
    new_abs = (
        "Present orientation–environment correspondence was scale-partitioned, and orientation also showed transition-level present-niche tracking: "
        "U→D and D→U probabilities aligned with opposite sides of a fixed BIO15/BIO1 regime, while the U→D pattern survived combined latitude/longitude residualization and internal-edge-only scoring (3/126 maps). "
        "Yet that present regime was not supported across the historical uncertainty envelope of the only calendarized U→D event."
    )
    text = replace_exact(text, old_abs, new_abs, "abstract transition-regime promotion")

    old_intro = (
        "We then compare the observed East-Asian orientation contrast with exhaustive counterfactual state maps that preserve the same state frequency and, "
        "in progressively stricter pools, the observed recurrence profile and similar relative-depth geometry. Finally, we determine how far available public data "
        "can identify calendar-time and historical environmental context."
    )
    new_intro = (
        "We then compare the observed East-Asian orientation contrast with exhaustive counterfactual state maps that preserve the same state frequency and, "
        "in progressively stricter pools, the observed recurrence profile and similar relative-depth geometry. We next test a fixed transition-level present-niche hypothesis for orientation, "
        "evaluate opposite-direction tracking, and subject the U→D result to strict-coverage, regional, single-taxon, linear-geography and internal-edge falsifications. "
        "Finally, for the only calendarized U→D event, we test whether the fixed present-niche regime persists across chronology and palaeolocation uncertainty before assessing broader historical-cause limits."
    )
    text = replace_exact(text, old_intro, new_intro, "introduction analysis roadmap")

    text = replace_exact(
        text,
        "`diversity within the radiation -> repeated component histories -> relative evolutionary depth -> shared-transition localization -> present ecological scale -> history-conditioned counterfactual ecology -> calendar/historical-cause boundary`.",
        "`diversity within the radiation -> repeated component histories -> relative evolutionary depth -> shared-transition localization -> present ecological scale -> history-conditioned counterfactual ecology -> fixed transition-regime concordance -> historical regime-persistence falsification -> calendar/historical-cause boundary`.",
        "evidence hierarchy",
    )

    methods = r'''## Fixed transition-regime concordance and falsification tests

We next tested a specific transition-level ecological hypothesis rather than screening additional environmental predictors. The frozen U→D vector was higher precipitation seasonality and lower annual mean temperature (`BIO15 up + BIO1 down`). For each accepted topology, a symmetric two-state CTMC provided edge joint probabilities for U→D and D→U change. Brownian squared-change reconstruction provided branch differences in standardized present-day taxon-centroid BIO15 and BIO1. For each axis we weighted environmental branch change by `P(U→D) - P(D→U)` and standardized by total expected transition mass; the primary composite was `(S_BIO15 - S_BIO1)/sqrt(2)`. The n>=5 panel contained 12 taxa (7 U, 5 D), with n>=3 as a 13-taxon sensitivity and the original n>=10 nine-taxon panel retained as a strict-coverage test. Every count-preserving state map was enumerated (792, 1,716 and 126 maps, respectively), the CTMC rate was refitted for every map, and the median statistic across the six accepted topologies was ranked within the complete finite map universe.

A reverse-direction test asked whether D→U probability tracked the exact opposite present-niche vector. This was treated as bidirectional present-niche tracking under the declared estimator, not as demonstrated genetic or developmental reversibility. Several fixed falsifications then tested whether the U→D result could be reduced to simple alternatives. We evaluated the strict occurrence gate and a Japan-only n>=5 panel; deleted each strict-panel taxon once; residualized each environmental centroid against `1 + latitude + longitude`; rescored only internal child edges while retaining full-tree CTMC and Brownian reconstruction; and finally combined linear-geography residualization with internal-edge-only scoring. These are post-result robustness tests, not independent confirmations. Failure to remain <=5% after taxon deletion was reported at its actual finite-map resolution rather than recoded as biological failure.

The coarse public-data programme had a frozen stop rule after the combined geography-plus-internal-edge stress test. No additional correlated climate variables or post-result robustness variants were allowed to rescue or strengthen the transition-regime result. Further causal resolution was routed to focal mediator/fitness data or event-linked historical evidence.

For the sole calendarized core-*Nipponocirsium* U→D event, we separately tested persistence of the present regime at origin. The fixed historical sign criterion was `BIO15 delta > 0` and `BIO1 delta < 0`. Existing PALEO-PGEM rows were evaluated across all 94 admissible chronology pairs and four fixed palaeolocation scenarios (376 scenarios), with support requiring >=75% matching chronologies in each region. This sign-persistence test is distinct from present-niche reconstruction and does not convert present ecological tracking into historical climatic causation.'''
    text = insert_before(
        text,
        "## Ecological evaluability of phyllary posture and stickiness",
        methods,
        "## Fixed transition-regime concordance and falsification tests",
    )

    results = r'''## Orientation transitions track a fixed East-Asian present-niche regime

The fixed U→D transition-regime hypothesis was supported under exhaustive count-preserving state-map tests. In the n>=5 panel of 12 taxa, the composite `BIO15 up + BIO1 down` statistic was positive on all six accepted topologies and only 16/792 (2.02%) state maps were at least as large as observed. The n>=3 sensitivity was similarly extreme (19/1716 = 1.11%). The strict n>=10 panel also retained the result (4/126 = 3.17%). In that strict panel, neither component alone crossed the frozen 5% boundary (BIO15, 7/126 = 5.56%; lower BIO1, 8/126 = 6.35%), whereas the predeclared composite did. The supported object is therefore a two-axis present-niche regime rather than a precipitation-seasonality-only or temperature-only effect.

The same regime was tracked in the opposite direction. Under the strict panel, the forward U→D alignment median was 0.320891 and the reverse D→U alignment median was 0.339529; both were positive on 6/6 topologies and the exact bidirectional-floor rank was 3/126 (2.38%). Deleting any one of the nine strict-panel taxa retained the expected direction across all six topologies, although exact finite-map extremeness was deletion-sensitive. Thus the directional pattern is distributed across the panel rather than generated by one taxon.

The U→D pattern survived several fixed falsifications. The Japan-only n>=5 panel remained directionally positive but was not exceptional (10/56 = 17.86%), setting a regional boundary. After removing linear latitude/longitude structure from BIO15 and BIO1, the strict-panel composite remained positive on 6/6 topologies and ranked 5/126 (3.97%). When terminal child edges were excluded from the scored statistic, the strict result ranked 3/126 (2.38%), with the 12-taxon sensitivity at 29/792 (3.66%). Applying geography residualization and internal-edge-only scoring simultaneously produced the same strict rank, 3/126 (2.38%), and the same n>=5 rank, 29/792 (3.66%). The transition-regime correspondence is therefore not reducible, under the declared reconstruction, to one taxon, relaxed occurrence coverage, a simple linear geographic gradient, or terminal-edge contribution; it is nevertheless not a universal Japan-only rule.

These exact fractions are finite randomization ranks and the robustness analyses are post-result. Internal environmental values are reconstructions from present-day niche centroids, not observed ancestral climates. The result supports repeated transition–present-niche concordance, not selection, adaptation, transition-time exposure or a physiological mediator.'''
    text = insert_before(
        text,
        "## A three-trait depth-ecological-reach relationship is not currently identifiable",
        results,
        "## Orientation transitions track a fixed East-Asian present-niche regime",
    )

    historical = r'''## The present transition regime is not supported as the bounded origin regime

The fixed present-niche regime did not persist across the uncertainty envelope of the sole calendarized U→D event. Requiring the historical endpoint signs `BIO15 delta > 0` and `BIO1 delta < 0`, only 99/376 (26.3%) chronology × palaeolocation scenarios matched both signs. Match fractions were 20/94 (21.3%) in Taiwan, 9/94 (9.6%) in the Ryukyu corridor, 41/94 (43.6%) in southern Japan and 29/94 (30.9%) in the East-Asian core corridor; only 6/94 chronology pairs matched in all four regions.

At the central 0.79–0.74 Ma chronology, BIO1 decreased in all four regions, consistent with one component of the present regime, but BIO15 also decreased in all four regions, opposite the present U→D direction. The present transition–niche regime therefore should not be projected backward as the origin trigger of the bounded core-*Nipponocirsium* event. This is an origin-versus-current-regime decoupling result, not evidence that environment was irrelevant at origin.'''
    text = insert_before(
        text,
        "## Coarse historical climate and sea-level regimes do not provide a recurring rescue",
        historical,
        "## The present transition regime is not supported as the bounded origin regime",
    )

    discussion = r'''The cross-scale orientation result first shows that one environment–trait coefficient cannot stand in for all biological scales. Annual precipitation appears mainly among taxa, annual mean temperature mainly within taxa, and precipitation seasonality produces a stable East-Asian state contrast without a matching positive within-taxon response. Present ecological structure is therefore scale-partitioned rather than one universal hydric or thermal reaction rule.

The history-conditioned counterfactual analysis then shows why arbitrary label permutation is not enough. Relative to arbitrary 5U/4D placement, the observed BIO15 contrast is unusual: only 5 of 126 state-count-preserving maps (3.97%) are at least as positive. That rarity weakens to 3/40 (7.5%) when recurrence is matched and to 3/10 (30%) when recurrence and relative-depth geometry are closely matched. A recurrence-matched reverse world reaches a signed statistic of -1.784, yet no opposite-direction BIO15 map occurred in the nearest-history pool. These results retain the earlier interpretation of **history-conditioned ecological correspondence** and show why apparent ecological extremeness depends on what evolutionary geometry the null is allowed to ignore.

The transition-regime analysis adds a different positive result. Instead of asking whether the observed tip contrast is extreme, it asks whether inferred orientation transition direction repeatedly aligns with a fixed present-niche vector. The U→D composite is exceptional in the 12-taxon exhaustive map universe and in the strict nine-taxon panel, and the reverse D→U direction tracks the opposite side of the same regime. Because neither strict BIO15 nor strict BIO1 alone is as exceptional as their predeclared composite, the result is better described as transition tracking of a **composite climatic regime** than as a single-axis effect.

The falsification sequence narrows the interpretation further. The U→D direction remains after deleting any one strict-panel taxon, after removing linear latitude/longitude structure, after excluding terminal edges from scoring, and after applying geography residualization and internal-edge exclusion together. The combined strict rank is 3/126 (2.38%), while the 12-taxon sensitivity is 29/792 (3.66%). Thus the signal is not simply a terminal-tip mean difference or a first-order geographic gradient under the declared CTMC/Brownian reconstruction. However, Japan-only n>=5 is not exceptional (10/56 = 17.86%) and deletion-level exact extremeness is sensitive, so the defensible biological object is a distributed **East-Asian lineage/regional transition-regime correspondence**, not a universal Japan-only rule.

Crucially, present transition tracking does not identify the environment of origin. The same fixed BIO15/BIO1 regime matches only 99/376 (26.3%) scenarios for the one calendarized U→D event and fails in all four regions at the central 0.79–0.74 Ma chronology because BIO15 moves in the opposite direction. Present ecological tracking and origin-time environmental regime are therefore empirically separable in this system. This is stronger than saying only that historical cause is unresolved: the current regime is specifically **not supported as a persistent origin regime** across the admitted historical uncertainty envelope.

Taken together, present ecology is **scale- and history-dependent**, transition-linked, and origin-decoupled. The result is consistent with present maintenance, sorting or state–niche matching without requiring the same coarse regime to have generated the original transition. It still does not identify rain/wetting, radiation, temperature, pollinators or another mediator, and it does not establish adaptation or selection.'''
    text = replace_section(
        text,
        "## Present ecology is scale- and history-dependent",
        "## Biotic interaction evidence constrains mechanism hypotheses without identifying historical cause",
        discussion,
    )

    old_lim = (
        "The orientation cross-scale analyses join distinct estimands and are not pooled. The counterfactual ecology analysis is post-result, uses a nine-taxon species-level centroid panel, "
        "and conditions only on state frequency, recurrence, and topology-only relative-depth geometry; it does not condition on all unmeasured lineage properties, geography, or same-individual phenotype–environment covariance."
    )
    new_lim = (
        "The orientation cross-scale analyses join distinct estimands and are not pooled. The counterfactual and transition-regime analyses are post-result falsification layers built from species-level present-niche centroids. "
        "The linear geography test removes only first-order latitude/longitude structure, and internal-edge environmental values remain Brownian reconstructions from extant tips; these analyses do not remove all spatial or lineage confounding, same-individual phenotype–environment covariance, or uncertainty about ancestral environments."
    )
    text = replace_exact(text, old_lim, new_lim, "limitations transition-regime boundary")

    conclusion = r'''A young Japanese *Cirsium* radiation contains multiple capitulum configurations assembled through repeated changes in orientation, phyllary posture, and involucre stickiness. The three components do not share one robust synchronized transition history, and their minimum histories occupy unequal evolutionary depths: paired topology comparisons place phyllary deeper than stickiness across all 1,000 topology realizations and deeper than orientation across 993, while orientation is deeper than stickiness across 905. Equalizing observed-state coverage preserves the central phyllary-deeper ordering but reveals overlap in the deepest tails.

Orientation adds a second, more specific result. Present ecology is scale- and history-dependent, and inferred U↔D transition directions track opposite sides of a fixed BIO15/BIO1 present-niche regime. The U→D correspondence survives strict coverage, deletion of any one strict-panel taxon, linear latitude/longitude residualization, internal-edge-only scoring, and their combined stress; the combined strict exact rank is 3/126 (2.38%). Yet the pattern is not a universal Japan-only rule, and the same present regime is not supported across the 376-scenario historical envelope of the only calendarized U→D event. The principal result is therefore a separation among a **well-resolved history of repeated mosaic phenotypic assembly**, a **specific present transition–niche regime for orientation**, and an **origin-time causal history that remains less identifiable and does not simply reproduce the current regime**.'''
    text = replace_section(text, "# Conclusion", "# References", conclusion)
    return text


def update_figure_map(text: str) -> str:
    fig3 = r'''The figure now has four linked questions: at what biological scale does orientation correspond to environment; whether transition direction tracks a fixed present-niche regime; which falsifications that regime survives; and how the earlier history-conditioned null changes the interpretation of tip-level extremeness.

### Panel 3A — cross-scale effect/support matrix
Three rows = BIO12, BIO15, BIO1. Three evidence columns = Azami within-taxon, Azami among-taxon, EAzami East-Asian state comparison.

- BIO12: within +0.00533, q=0.874; among +0.30436, q=0.00640 — `among_only`.
- BIO15: within -0.00762, q=0.121; among +0.0670, q=0.599; East-Asian D-U +1.320 to +1.330 SD, sign stable 6/6 topologies and 54/54 topology x species-LOO fits.
- BIO1: within +0.01715, q=0.0349; among -0.03024, q=0.836; East-Asian D-U approximately -0.975 to -0.967 SD, 54/54 sign stable.

Keep the three columns visually distinct because they are non-exchangeable estimands.

### Panel 3B — fixed transition-regime test
Source: `chapter2_orientation_transition_regime_hypothesis_result_v1.json` plus the strict-panel robustness result.

Plot exact finite-map ranks for the predeclared `BIO15 up + BIO1 down` U->D composite:

- n>=5, 12 taxa: **16/792 = 2.02%**;
- n>=3, 13 taxa: **19/1716 = 1.11%**;
- strict n>=10, 9 taxa: **4/126 = 3.17%**.

Show strict single-axis ranks as a small annotation:

- BIO15 alone: **7/126 = 5.56%**;
- lower BIO1 alone: **8/126 = 6.35%**;
- composite: **4/126 = 3.17%**.

Also annotate the bidirectional strict result: U->D and D->U both positive on 6/6 topologies; exact bidirectional-floor rank **3/126 = 2.38%**. Label this `present-niche tracking`, not adaptation or climatic causation.

### Panel 3C — falsification ladder for U->D tracking
Use a compact stress-test matrix, not multiple hypothesis numbers.

- strict n>=10: **4/126 = 3.17%** — pass;
- Japan-only n>=5: **10/56 = 17.86%** — directional but not exceptional;
- delete each strict-panel taxon: direction retained in **9/9** deletion panels; exact extremeness deletion-sensitive;
- linear latitude/longitude residualization: **5/126 = 3.97%** — pass;
- internal-edge-only scoring: **3/126 = 2.38%** — pass;
- geography residualization + internal-edge-only: **3/126 = 2.38%** — pass;
- combined-stress n>=5 sensitivity: **29/792 = 3.66%** — pass.

Visual message: the transition-regime direction is not a one-taxon, simple linear geography, or terminal-edge artefact under the declared reconstruction, but it is region-sensitive.

### Panel 3D — history-conditioned tip-contrast calibration
Retain the earlier counterfactual conditioning ladder for BIO15 as a methodological boundary:

- same state frequency: **5/126 = 3.97%**;
- same recurrence: **3/40 = 7.5%**;
- recurrence + nearest relative depth: **3/10 = 30%**.

Label the x-axis `state frequency -> recurrence -> recurrence + relative depth`. These are finite conditional ranks, not P values. Note that a recurrence-matched reverse world reaches -1.784 but no reverse BIO15 world occurs in the nearest-history pool.

### Figure 3 boundary

The transition-regime analyses use reconstructed branches from present-day niche centroids. Geography residualization removes only linear latitude/longitude structure, and internal-edge support is not observed ancestral climate. The analyses do not establish selection, adaptation, historical exposure or a mediator. **No three-trait** depth x ecological-reach regression is allowed.

**Figure 3 claim:** Present orientation ecology is scale-partitioned and history-embedded, while transition direction additionally tracks a fixed East-Asian composite present-niche regime that survives the declared strict-coverage, single-taxon, simple-geography and internal-edge falsifications but is not a universal Japan-only rule.'''
    text = replace_section(
        text,
        "# Figure 3 — Orientation ecology is scale- and history-conditioned",
        "# Figure 4 — Bounded orientation history: tendency versus uncertainty",
        fig3,
    )

    text = replace_exact(
        text,
        "### Panel 4D — full uncertainty decision\nNo tested BIO1/BIO4/BIO12/BIO15 direction, environmental level, absolute change or variability survives the full chronology × palaeolocation envelope.\n\n**Figure 4 claim:** The best-bounded event contains regional and climate tendencies but they are not robust to admitted timing and palaeolocation uncertainty.",
        "### Panel 4D — present-regime persistence falsification\nThe fixed current U->D sign combination (`BIO15 delta > 0`, `BIO1 delta < 0`) matches only **99/376 = 26.3%** scenarios: Taiwan 20/94, Ryukyu 9/94, southern Japan 41/94, East-Asian core 29/94. At the central 0.79–0.74 Ma chronology, BIO1 decreases in all four regions but BIO15 also decreases in all four, so the current-regime sign test fails in 4/4 central regional scenarios. No broader tested BIO1/BIO4/BIO12/BIO15 direction, level, absolute change or variability class survives the full chronology x palaeolocation envelope.\n\n**Figure 4 claim:** The best-bounded event contains regional and climate tendencies, but the fixed present transition-niche regime is not supported as a persistent origin regime across admitted timing and palaeolocation uncertainty.",
        "Figure 4 regime-persistence update",
    )

    text = text.replace(
        "4. present ecological correspondence — scale-partitioned and history-conditioned for orientation;",
        "4. present ecological correspondence — scale-partitioned, history-conditioned and transition-linked for orientation;",
    )
    return text


def main() -> None:
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    figmap = FIGMAP.read_text(encoding="utf-8")
    manuscript_new = update_manuscript(manuscript)
    figmap_new = update_figure_map(figmap)
    MANUSCRIPT.write_text(manuscript_new, encoding="utf-8")
    FIGMAP.write_text(figmap_new, encoding="utf-8")
    print("updated", MANUSCRIPT)
    print("updated", FIGMAP)


if __name__ == "__main__":
    main()
