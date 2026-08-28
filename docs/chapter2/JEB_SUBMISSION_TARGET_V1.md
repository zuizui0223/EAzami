# Chapter 2 JEB submission target v5

Status date: 2026-08-28

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

The contribution combines an evolutionary-history result with an inference boundary:

1. 36/38 sampled Japanese concepts belong to one dominant radiation, whose authority-covered subset contains at least three harmonized capitulum configurations;
2. orientation, phyllary posture and stickiness each require multiple minimum changes;
3. minimum-change count, relative lineage-depth and named-edge localization are different estimands;
4. no one shared transition-localization pattern is robust across the three traits;
5. orientation has a topology- and species-LOO-stable climate direction, but does not add predictive power beyond phylogeny-only;
6. phyllary posture and stickiness are explicitly `not_evaluable` with current climate/state overlap rather than treated as ecological negatives.

The main inferential advance is the separation of **correspondence** from **explanatory reach**. A stable trait–environment direction can survive topology and species deletion while still failing to improve prediction beyond ancestry.

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
- branchwise direction is concordant but permutation thresholds are not crossed;
- ΔMSE versus mean-only null is positive: BIO15 +0.224 to +0.230; BIO1 +0.364 to +0.370;
- ΔMSE versus phylogeny-only is negative: BIO15 −0.108 to −0.102; BIO1 −0.199 to −0.192.

Decision: orientation=`unresolved`; phyllary posture=`not_evaluable`; stickiness=`not_evaluable`.

This result supports an asymmetric ecological explanatory reach claim, not adaptation or historical ecological causation.

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
4. Ecological explanatory reach: effect direction, topology/LOO stability, null versus phylogeny-only predictive gain and trait-level evaluation.

Active map: `docs/chapter2/JEB_QUESTION_RESULT_FIGURE_MAP_V4.md`.

Species-tip compression and continuous/cytotype/colour diagnostics belong in `JEB_SUPPORTING_INFORMATION_V2.md`.

## Go/no-go gate

### Scientific gates

- [x] public Comp1061 scaffold and exclusions frozen;
- [x] orientation, phyllary and post-JPN24 stickiness counts frozen;
- [x] minimum counts, relative depth and named-edge localization reported separately;
- [x] branch-length-aware and equal-branch overlap disagreement retained;
- [x] ecological direction propagated across six accepted topologies;
- [x] species leave-one-out direction quantified;
- [x] held-out prediction compared separately against mean-only null and phylogeny-only;
- [x] phyllary/stickiness ecology fail closed as `not_evaluable`;
- [x] Chapter 2/3 dependency direction retained;
- [x] no RAD-seq, field, dated-tree or own continuous result required for the conclusion.

### Package gates

- [x] active v4 Markdown manuscript updated to the ecological-reach spine and abstract within limits;
- [x] active question/result/figure map updated to v4;
- [x] Supporting Information logic updated to v2;
- [ ] Figures 1–4 rebuilt and visually audited;
- [ ] anonymous line-numbered DOCX built;
- [ ] reference and primary-source cross-check complete;
- [ ] title-page author, funding, correspondence and declarations completed;
- [ ] data-availability and archive statement frozen.

## Cover-letter emphasis

Lead with the biological result: one dominant young radiation contains multiple capitulum configurations and each of three constituent traits requires multiple minimum changes. Then state the ecological inference result: orientation shows a highly stable climate direction, yet adding orientation fails to improve prediction beyond phylogeny-only, while the other two traits are not evaluable at the current climate gate.

This is stronger than ending with a list of possible causes because it quantifies exactly how far current ecology explains the pattern and where it stops.

Do not lead with field-function hypotheses, a desired RAD-seq tree or the unsupported continuous diagnostics.

## Claim boundary

The submission may claim configuration diversity within the dominant radiation, multiple minimum changes in three constituent traits, unequal event resolution, absence of a cross-treatment-robust common localization pattern, and asymmetric present-day ecological explanatory reach.

It may not claim independent origins, convergence, evolutionary independence, developmental/genetic modularity, adaptive function, historical niche causation, absolute event times or that future targeted data constitute independent replication. `not_evaluable` cannot be rewritten as no relationship.
