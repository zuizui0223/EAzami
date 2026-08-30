# Chapter 2 space–time concordance audit v1

Status date: 2026-08-30

## Question

This audit asks a narrower question than the programme-level synthesis:

> **Does the breadth of capitulum phenotype observed across present-day space align with the depth and recurrence of the same phenotype through evolutionary history?**

The comparison is not defined as “significant in both chapters”. Breadth and depth use different estimands, so concordance is evaluated in three ordered layers:

1. **ontology concordance** — can the same biological trait be followed on both axes without converting an image proxy into a different botanical character?;
2. **pattern concordance** — does a spatially structured phenotype also show temporal lability, recurrence or phylogenetic structure?;
3. **ecological-domain concordance** — where both axes have environmental information, do they point to the same ecological domain without pretending distinct variables are identical?

`not_evaluable` and missing ontology matches are retained as missing comparability, not scored as discordance.

Machine-readable ledger: `../../data/evidence/chapter2_space_time_concordance_v1.csv`.

## Result 1 — orientation is the only current full breadth–depth bridge

Azami identifies a robust among-taxon orientation association with annual precipitation amount (BIO12): standardized beta = +0.304359, q = 0.021; the broad-space sensitivity remains positive (beta = +0.286086, P = 0.017), and the direction is retained across 52 audited historical-placement trees.

EAzami independently shows a recurrent orientation history: ML minimum = 6 changes and the 1,000-tree UFBoot range = 4–6. The median admissible relative lineage-depth envelope is 0.795–0.994. Thus the present orientation contrast is not confined to one deep lineage split; repeated state reassembly is required by the accepted topology ensemble, although exact branch placement and direction remain uncertain.

The ecological comparison points to the same **hydric domain** at a different resolution. Downward/nodding East-Asian taxa occupy niches with higher precipitation seasonality (BIO15), with the positive direction retained across all accepted topologies, all species leave-one-out fits and both admissible Taiwan occurrence-source expansions. BIO12 and BIO15 are not the same variable and are not treated as coefficient replication.

**Decision:** `bridge_supported`.

The allowed synthesis is:

> **Orientation shows cross-scale hydric correspondence: present spatial sorting and repeated temporal reassembly coexist, and both axes implicate different dimensions of rainfall regime.**

This does not establish rain adaptation, independent origins, convergence or fitness benefit.

## Result 2 — colour is spatially strong but temporally unresolved

Azami's second robust among-taxon candidate is visible corolla chroma versus shortwave radiation: beta = −0.345372, q = 0.006; broad-space beta = −0.712411, P = 0.001, with the same direction across 52 historical-placement trees.

In the Japanese time-axis analysis, however, no primary continuous colour unit receives corrected two-sided phylogenetic-structure support. Chroma itself is unsupported; high-depth lightness has a raw negative phylogenetic-distance association but it does not survive the frozen family correction and does not replicate in the source-balanced Japanese sensitivity. No resolved W/C transition history is joined to the spatial chroma result.

This is **not a contradiction**. A strong geographic/environmental sorting pattern can coexist with weak phylogenetic structure if the trait is labile, but the present Japan38 coverage is too limited to distinguish true evolutionary lability from low information.

**Decision:** `spatial_sorting_temporal_lability_unresolved`.

## Result 3 — repeated history does not imply a recoverable spatial breadth axis

Phyllary posture and stickiness show the inverse asymmetry.

- phyllary posture requires exactly 3 minimum changes across all 1,000 UFBoot trees; median relative-depth envelope = 0.695–1.000;
- stickiness requires exactly 5 minimum changes across all 1,000 UFBoot trees; median relative-depth envelope = 0.937–0.954.

But Azami does not supply a homologous spatial axis for either trait. Image-derived involucral geometry is not interchangeable with authority-coded phyllary posture, and stickiness has no calibrated continuous Azami endpoint. Their current ecology is also `not_evaluable` because state-diverse occurrence overlap is insufficient.

Therefore these traits cannot be labelled space–time discordant. Their breadth–depth relation is **unidentified**.

## Result 4 — spatial breadth does not imply one shared temporal history

The broader whole-capitulum comparison rejects the simplest coupling story.

Azami's secondary whole-capitulum analysis shows only partial alignment between within- and among-taxon association structure (Spearman rho = 0.3663). In EAzami, the three completed discrete traits do not retain one robust shared transition-localization pattern: zero of three trait pairs passes the cross-treatment rule after branch-length-aware and equal-branch topology sensitivities.

These estimands are not identical, so they are not combined into one formal statistic. Together, however, they bound the same simple model:

> **a capitulum that is diverse as a whole in present space does not appear to have been assembled through one synchronized evolutionary history.**

The current evidence instead supports an **asymmetric breadth–depth architecture**: some modules bridge both axes, some are spatially structured without a resolved history, and some have repeated histories without a comparable spatial endpoint.

## Breadth–depth hypotheses and current decisions

### BD1 — Spatial environmental sorting predicts temporal recurrence/lability

Prediction: traits with robust among-taxon environmental sorting should also be phylogenetically labile or repeatedly reconstructed.

Current evidence:
- orientation: **supports** the prediction through repeated 4–6 state changes;
- colour: **consistent but unresolved** because corrected continuous-history support is absent and discrete transition history is unresolved.

With only two robust Azami among-taxon candidates, there is no defensible cross-trait significance test. The present result is a trait-level comparison, not a correlation across traits.

### BD2 — The same ecological domain recurs across space and time

Prediction: a spatial environmental association should reappear in the ecological context of recurrent states.

Current evidence:
- orientation: **supported at the domain level** for hydric regime (BIO12 amount versus BIO15 seasonality);
- colour: **not evaluable** because a resolved colour-event ecology layer is absent.

This is domain concordance, not identity of predictors.

### BD3 — Whole-capitulum breadth reflects synchronized temporal assembly

Prediction: constituent traits that covary in present phenotype space should repeatedly change on the same evolutionary branches.

Current evidence: **not supported by the current discrete-history subset**. Zero of three pairwise transition-localization comparisons passes the frozen robustness rule.

This does not prove genetic modularity or independence. It rejects only the simple one-common-lability history under current coverage.

## Main conclusion

The strongest current result is not that space and time perfectly agree. It is that their agreement is **trait-specific**.

> **Present-day phenotypic breadth and evolutionary depth are coupled for orientation, decoupled or unresolved for colour and outline, and not yet comparable for phyllary posture, stickiness and armature. The capitulum therefore appears to gain diversity through asymmetric assembly of constituent traits rather than through one universal space–time syndrome.**

This is the direct space–time result that should sit above the separate Azami and EAzami chapter conclusions.

## What would falsify or strengthen this conclusion

The next public-data upgrade should not search broadly for new positive associations. It should increase the number of traits with homologous measurements on both axes.

Highest-value additions are:

1. map direct botanical phyllary posture/spine measurements onto the Azami spatial sample or an equivalent coordinate-bearing sample;
2. obtain a calibrated stickiness spatial endpoint if public descriptions/observations permit it;
3. resolve population-matched W/C history so colour can move from `spatial_sorting_temporal_lability_unresolved` to a true transition test;
4. increase Japan38 matched continuous phenotype coverage so absence of corrected phylogenetic structure can be separated from low power.

Until then, the breadth–depth conclusion is deliberately asymmetric rather than forced into a single concordance coefficient.
