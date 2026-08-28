# Chapter 2 JEB submission target v6

Status date: 2026-08-29

Primary target: **Journal of Evolutionary Biology (JEB), Research Article**

Fallback: **Evolutionary Journal of the Linnean Society, Research Article**

Scientific status: **COMPLETE_EXISTING_PUBLIC_HISTORY_AND_BOUNDED_ECOLOGICAL_REACH**

Submission status: **HOLD_JEB_PACKAGE_REBUILD_ONLY**

## Active title and question

> **Capitulum configuration diversity, minimum change counts and ecological explanatory reach in a young thistle radiation**

The paper asks:

> **How many state changes are minimally required in constituent capitulum traits, at what relative lineage depth can those minimum histories occur, and how far can existing ecological data explain the observed trait states after accounting for phylogeny?**

The paper therefore ends with an empirical ecological result rather than a list of prospective causal candidates.

## Why JEB is the first target

The contribution combines an evolutionary-history result with a bounded ecological interpretation:

1. 36/38 sampled Japanese concepts belong to one dominant radiation, whose authority-covered subset contains at least three harmonized capitulum configurations;
2. orientation, phyllary posture and stickiness each require multiple minimum changes;
3. minimum-change count, relative lineage-depth and named-edge localization are different estimands;
4. no one shared transition-localization pattern is robust across the three traits;
5. orientation has a topology- and species-LOO-stable climate direction for BIO15 and BIO1, but the current n=9 panel remains below the frozen inferential threshold;
6. phyllary posture and stickiness are explicitly `not_evaluable` with current climate/state overlap rather than treated as ecological negatives;
7. an independent nuclear-DNA audit shows that the Japan38 Comp1061 tree is the primary **harmonized common-locus scaffold**, not the only nuclear evidence available for Japanese/East-Asian *Cirsium*.

The main ecological point is deliberately modest: **current data can identify a stable ecological correspondence for orientation and can state precisely where explanatory resolution stops.** The manuscript does not require a predictive model competition to make that result.

## Nuclear-scaffold interpretation after independent evidence audit

The active Japan38 history remains based on the accepted Comp1061 scaffold because it supplies one homologous-locus framework across the complete admitted Japan38 panel. It must not be described as the sole nuclear evidence.

Independent nuclear information recovered outside Moreyra 2025 includes:

- 2012 Korean multi-locality *C. pendulum* / *C. setidens* 18S–ITS–5.8S–ITS2–partial-28S sequence data;
- 2015 Korean nrDNA evidence in which downward *C. shantarense* groups with upward *C. japonicum* despite the capitulum-orientation difference;
- the 2017–2021 Japanese KAKEN `17K07524` MIG-seq/RAD programme, which reports strong within-population variation, isolation by distance and weak named-species separation in a diploid Kaga-subsection panel;
- a reusable 2022 *C. maritimum* MIG-seq Genepop matrix on Dryad, overlapping Japan38 JPN_17 at the species-name level;
- 2018 and 2020 *C. japonicum* transcriptome resources with 51,133 and 104,890 unigenes, respectively;
- a 2024 *C. nipponicum* nuclear reference genome;
- independent 2025/2026 East-Asian phylotranscriptomic species-tree/network analyses.

These sources constrain taxon delimitation, population compression, local topology and later mechanism work, but heterogeneous rDNA, MIG-seq, transcriptome and genome resources are not pooled into the Japan38 branch-length tree.

Active audit: `docs/chapter2/EAST_ASIA_INDEPENDENT_NUCLEAR_EVIDENCE_AUDIT_V1.md` and `data/evidence/east_asia_independent_nuclear_evidence_audit_v1.csv`.

## Current scientific spine

### Historical layer

- dominant-radiation context: 36/38 sampled concepts and at least three harmonized orientation × stickiness configurations;
- orientation: 20 resolved concepts; ML=6; UFBoot=4–6; median UFBoot relative-depth envelope 0.795–0.994; JPN36 forced fraction=0.227;
- phyllary posture: 10 resolved; exactly 3 changes; median depth envelope 0.695–1.000; JPN36=0.728;
- stickiness: 13 resolved; exactly 5 changes; median depth envelope 0.937–0.954; JPN06=0.995 and JPN36=0.707;
- zero of three trait pairs meets the cross-treatment shared-localization rule.

### Ecological explanatory reach

Frozen East-Asian orientation panel: n=9, U=5/D=4, with >=10 independent thinned environment-complete occurrences per taxon.

- BIO15: D−U=+1.320 to +1.330 SD; P=0.05054–0.05239;
- BIO1: D−U=−0.975 to −0.967 SD; P=0.09604–0.09793;
- sign agreement: 6/6 accepted topologies and 54/54 species-LOO fits for each focal axis;
- branchwise direction is concordant on all six accepted topologies, but permutation thresholds are not crossed;
- orientation=`unresolved`; phyllary posture=`not_evaluable`; stickiness=`not_evaluable`.

The previously computed held-out mean-null / phylogeny-only comparisons remain available as diagnostics, but they are **not required for the main ecological-reach decision**. The principal result is the direction, its phylogenetic/topological robustness, and the explicit limit imposed by current taxon/state coverage.

### Non-climate explanatory factors currently testable

- **Cytotype/ploidy:** nine source-backed concepts currently show that orientation is not deterministically assigned by ploidy; upward/ascending states occur at 2x, 4x and 6x, and diploids include both upward and downward states. This is a bounded rejection of a one-to-one ploidy explanation, not proof of independence.
- **Population/genetic structure:** pre-2025 Japanese MIG-seq/RAD work and the public *C. maritimum* MIG-seq dataset show that species-tip coding can hide substantial population structure. These sources constrain how confidently a named-species state can be equated with one genomic unit, but they do not yet explain one focal trait across Japan38.
- **Biogeographic/lineage history:** the dominant-radiation versus secondary-arrival context is already incorporated as historical structure. Current configurations do not map one-to-one onto that broad history class.
- **Pollinator/enemy context:** existing *Cirsium* literature supplies functional priors, but there is not yet a sufficiently joined Japan38 taxon-level pollinator/enemy matrix to promote those factors to the same comparative result tier as climate.

## Current JEB format contract

The official JEB author-guideline audit frozen on 2026-08-28 requires or allows:

- Research Article main text <=7,500 words;
- abstract <=250 words;
- 4–10 keywords;
- double-anonymous review;
- separate identifying title page;
- line-numbered main manuscript;
- Supporting Information supplied with the manuscript;
- generative-AI use disclosed in the cover letter and Methods or Acknowledgements;
- public data/archive compliance by the journal's required stage.

Official source: https://academic.oup.com/jeb/pages/author-guidelines

## Active figure order

1. Dominant-radiation context, trait coverage and observed configurations.
2. Trait-specific minimum-change distributions and relative lineage-depth envelopes.
3. Current run-329 forced-edge localization plus cross-trait shared-localization boundary.
4. Ecological explanatory reach: effect direction, topology/LOO stability and trait-level `unresolved / not_evaluable` classification; cytotype and independent nuclear evidence remain compact contextual boundaries rather than extra headline panels unless needed for reviewer clarity.

Active map: `docs/chapter2/JEB_QUESTION_RESULT_FIGURE_MAP_V4.md`.

Species-tip compression, independent nuclear evidence, continuous/cytotype/colour diagnostics and predictive diagnostics belong primarily in Supporting Information.

## Go/no-go gate

### Scientific gates

- [x] public Comp1061 scaffold and exclusions frozen;
- [x] orientation, phyllary and post-JPN24 stickiness counts frozen;
- [x] minimum counts, relative depth and named-edge localization reported separately;
- [x] branch-length-aware and equal-branch overlap disagreement retained;
- [x] ecological direction propagated across six accepted topologies;
- [x] species leave-one-out direction quantified;
- [x] phyllary/stickiness ecology fail closed as `not_evaluable`;
- [x] independent pre-2025 / non-Moreyra nuclear evidence audited and separated by estimand;
- [x] Comp1061 wording corrected to `primary harmonized common-locus scaffold`, not `only nuclear evidence`;
- [x] Chapter 2/3 dependency direction retained;
- [x] no new RAD-seq, field, dated-tree or own continuous result required for the conclusion.

### Package gates

- [x] active v4 Markdown manuscript updated to the ecological-reach spine and abstract within limits;
- [x] active question/result/figure map updated to v4;
- [x] Supporting Information logic updated to v2;
- [ ] manuscript/SI wording fully synchronized with the independent nuclear audit;
- [ ] Figures 1–4 rebuilt and visually audited;
- [ ] anonymous line-numbered DOCX built;
- [ ] reference and primary-source cross-check complete;
- [ ] title-page author, funding, correspondence and declarations completed;
- [ ] data-availability and archive statement frozen.

## Cover-letter emphasis

Lead with the biological result: one dominant young radiation contains multiple capitulum configurations and each of three constituent traits requires multiple minimum changes. Then state the bounded ecological result: orientation shows a highly stable direction along precipitation-seasonality and annual-temperature gradients, whereas current data are insufficient to promote that correspondence to adaptation or to evaluate phyllary/stickiness ecology.

The independent nuclear audit supports the robustness framing: the common-locus Japan38 scaffold is embedded in a broader pre-existing nuclear evidence landscape, while population-scale data warn against interpreting one species tip as complete within-species history.

Do not lead with field-function hypotheses, a desired RAD-seq tree, predictive model competition or unsupported continuous diagnostics.

## Claim boundary

The submission may claim configuration diversity within the dominant radiation, multiple minimum changes in three constituent traits, unequal event resolution, absence of a cross-treatment-robust common localization pattern, and asymmetric present-day ecological explanatory reach.

It may also state that independent nuclear evidence predating or external to Moreyra 2025 exists at rDNA, reduced-representation population, transcriptome, reference-genome and local phylogenomic scales, while the accepted Comp1061 tree remains the harmonized common-locus scaffold for the full Japan38 comparison.

It may not claim independent origins, convergence, evolutionary independence, developmental/genetic modularity, adaptive function, historical niche causation, absolute event times or that future targeted data constitute independent replication. `not_evaluable` cannot be rewritten as no relationship.
