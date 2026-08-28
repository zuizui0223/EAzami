# EAzami current state

Status date: 2026-08-28

## Active status: standalone diversity-depth reframe

Chapter 1 now supplies the conceptual **breadth** question; Chapter 2 independently estimates historical **depth**. EAzami must build its own literature/specimen/flora/public-image trait registry and cannot use Azami phenotype values or Azami significance as an admission gate.

- standalone-ready now: Comp1061 scaffold; discrete orientation/phyllary/stickiness recurrence and localization; topology ensemble; GBIF + CHELSA orientation-niche analyses; an admitted 45-record EAzami-native continuous registry; a four-trait seven-taxon direct diagnostic panel; bounded colonization/cytotype context;
- reanalysis required: Japan38 continuous trait history and reconstruction-aware null after commensurate scalar measurements cover enough Japan38 tips;
- blocked/design only: dated event correspondence, phenotypic DTT/phylomorphospace and M0-M5 evolutionary simulations;
- submission status: **STOP_STANDALONE_CONTINUOUS_COVERAGE_INSUFFICIENT**. The native-input provenance gate passed, but all five mapped Japan38 records are range-only and zero Japan38 tips have admitted scalar values.

Canonical plan: `docs/chapter2/DIVERSITY_DEPTH_STANDALONE_V1.md`. The previous present-integration package remains a frozen audit snapshot and its negative results are retained below.

The independent n=7 direct continuous-history diagnostic is complete across all six AU-nonrejected topologies. No one of the four fixed traits met the corrected topology-robust retention rule. Phyllary protrusion was consistently positive but remained unsupported after BH correction, so it is a priority for added measurement rather than a paper conclusion.

## Dissertation mainline

```text
shared continuous capitulum phenotype ontology
        |
        |-- Chapter 1 — phenotype × present-day space/environment
        |     within/among variation; geography; environmental alignment
        |
        |-- Chapter 2 — phenotype × evolutionary time/history
        |     present integration; state structure; recurrence; transition localization
        |
        `-- Chapter 3 — phenotype × function/fitness
              trait -> performance -> reproductive fitness
```

Function is not an admission gate for Chapter 2. Chapter 1 and Chapter 2 reuse the same phenotype ontology on orthogonal axes.

## Chapter 2 current answer

> **Authority-backed capitulum states recur in trait-specific ways, but recurrence count and transition localization are distinct. The independent seven-taxon continuous panel detects no corrected topology-robust retention, and Japan38 continuous history remains not evaluable for lack of comparable scalar measurements.**

This statement does not imply zero phylogenetic signal, lability, fully independent traits, independent origins, convergence, adaptation or a shared mechanism.

## Legacy present integration audit

At the frozen >=5-observation threshold:

- within-taxon registered-module contrast = **0.164502** (0.130693–0.179475);
- among-taxon contrast = **0.088475** (0.024942–0.126171);
- within/among association-matrix similarity = **0.3663**.

The >=2 sensitivity preserves the ordering: 0.157688 within versus 0.083662 among. These are observational measurement modules from the frozen Azami handoff, not EAzami primary evidence, genetic modules or historical modules.

## Nuclear history scaffold

- 38 paper concepts and 39 focal biological samples;
- 236 QC nuclear loci, 176 rootable loci and 161,654 aligned bp;
- 1,000 UFBoot and 1,000 SH-aLRT replicates;
- branch lengths in substitutions/site, **not absolute time**;
- JPN20 samples non-monophyletic in ML and 0/1,000 bootstrap trees, so not forcibly collapsed;
- JPN31 excluded from primary trait history because of identity/locality conflict;
- JPN29 retained in the raw tree but prohibited from a clean Japanese phenotype join until specimen identity is resolved.

Published phylogenomics places 36/38 sampled concepts in the dominant Japanese Pleistocene radiation. This is context, not a rate claim.

## Legacy continuous phenotype history audit

Eight primary units cover orientation, colour and outline shape. They consume an Azami-export bridge and are retained only as method/negative-result audit history. Image values are global species-level proxies, not measurements of the sequenced Japanese vouchers.

### State structure

- original families: **0/8** corrected two-sided results at >=2 and >=5;
- original scalar Pagel lambda MLE: zero for seven scalar units;
- fixed JPN29 exclusion: eight `two_sided_not_supported` units at >=2;
- fixed JPN29 exclusion at >=5: **not_evaluable**, because only five concepts remain below the six-concept minimum.

Allowed conclusion: no robust continuous phylogenetic state structure was detected in the sparse panel.

### Shared change localization

The old independent-branch permutation P=0.00010 is invalid as headline evidence because reconstructed branches are not independent. The reconstruction-aware null starts at the tips and repeats ancestral reconstruction:

- original eight-concept panel: observed rho=**0.408006**, null median=0.380220, **P=0.3504, FAIL**;
- fixed JPN29-excluded seven-concept sensitivity: observed rho=**0.472278**, null median=0.415335, **P=0.1959, FAIL**.

The earlier positive equal-branch result across 1,000/1,000 topologies is retained as `diagnostic_only`: it includes JPN29 and has no topology-specific reconstruction-aware null.

## Discrete history

- orientation: 20 resolved, ML minimum 6, UFBoot 4–6;
- phyllary posture: ten resolved, exactly three changes across all 1,000 topologies;
- stickiness: 13 resolved, exactly five changes across all 1,000 topologies.

These are recurrence lower bounds. Placement identifiability differs:

- orientation has no individually forced ML edge; JPN36 terminal fraction 0.201;
- phyllary JPN36 terminal fraction 0.754, with root posture ambiguous;
- stickiness placements remain partial.

Equal-branch transition-overlap medians are -0.0594 for orientation–phyllary, -0.3870 for orientation–stickiness and 0.1840 for phyllary–stickiness. No pair is consistently positive across branch-length treatments.

## JEB submission state

Target: **Journal of Evolutionary Biology — Research Article**.

Recommended standalone title:

> **Recurrence and localization are distinct dimensions of capitulum evolution in a young thistle radiation**

Current active state:

- standalone diversity-depth contract and repository-wide inventory frozen;
- EAzami-native continuous registry admitted with identity/source/rights/measurement gates;
- exact-permutation seven-taxon diagnostic complete and `not_supported`;
- discrete recurrence/localization and bounded niche layers independently executable;
- submission authorization withheld at `STOP_STANDALONE_CONTINUOUS_COVERAGE_INSUFFICIENT`;
- standalone manuscript and figures not yet rebuilt.

The former V3 manuscript, figures, Supporting Information and privacy-scrubbed DOCX files remain a reproducible audit snapshot. They must not be submitted as the current standalone paper.

## Active sources of truth

- `docs/chapter2/DIVERSITY_DEPTH_STANDALONE_V1.md`
- `data/evidence/chapter2_diversity_depth_contract_v1.json`
- `data/evidence/chapter2_diversity_depth_inventory_v1.csv`
- `data/evidence/chapter2_eazami_native_continuous_trait_registry_summary_v1.json`
- `data/evidence/chapter2_eazami_native_continuous_history_diagnostic_v1.json`

JEB manuscript versions v1-v3 are audit history, not current submission text.

## Programme routing

- Present-state v3/v4 covariance simulations: Chapter 1 Supplement or thesis methods.
- FDT1 trait-to-function evidence, FDT8 field readiness and field pilots: Chapter 3.
- Cirsium reproductive-herbivory RR = 2.674 is Chapter 3 functional context, not a Chapter 2 admission gate.
- Later origin discrimination requires nuclear population genomics, plastid haplotype and cytotype evidence from linked biological individuals where possible.
- Absolute-time transition analyses: STOP until a defensible calibration exists.

## Stop rules

- no present covariance -> persistent historical module shortcut;
- no null failure -> evolutionary independence shortcut;
- no minimum parsimony step -> independent origin or convergence shortcut;
- no topology sign stability -> biological shared-change shortcut;
- no substitutions/site -> absolute time or rate/Myr shortcut;
- no species-level image proxy -> sequenced-voucher phenotype shortcut;
- no image phenotype -> validated function shortcut.
