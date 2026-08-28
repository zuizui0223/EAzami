# EAzami current state

Status date: 2026-08-28

## Active status: Chapter 2 public-history core complete

Chapter 1 now supplies the conceptual **breadth** question; Chapter 2 independently estimates historical **depth**. EAzami must build its own literature/specimen/flora/public-image trait registry and cannot use Azami phenotype values or Azami significance as an admission gate.

- standalone-ready now: 36/38 dominant-radiation context; at least three harmonized orientation x stickiness configurations in the authority-covered dominant subset; discrete orientation/phyllary/stickiness minimum-change counts and event resolution; topology ensemble; a validated species-tip compression audit;
- supporting only: GBIF + CHELSA orientation-niche analyses; an admitted 45-record EAzami-native continuous registry; a four-trait seven-taxon diagnostic panel; bounded cytotype context;
- bounded, not completion gates: Japan38 continuous history, dated event correspondence, DTT and evolutionary simulations;
- routed to Chapter 3: own Japan-wide RAD-seq, same-individual phenotype/cytotype, population structure and field causality;
- scientific status: **COMPLETE_EXISTING_PUBLIC_HISTORY_CORE**;
- submission status: **HOLD_JEB_PACKAGE_REBUILD_ONLY**.

Canonical plan: `docs/chapter2/DIVERSITY_DEPTH_STANDALONE_V1.md`. The compressed result selection is `docs/chapter2/CHAPTER2_CORE_RESULT_RECOVERY_V1.md` plus `data/evidence/chapter2_core_result_recovery_v1.csv`. The previous present-integration package remains a frozen audit snapshot and its negative results are retained below.

The active main text is limited to five result groups. Completed continuous, niche and cytotype diagnostics remain available in Supporting Information, but none is used to manufacture an additional headline.

## Dissertation mainline

```text
shared continuous capitulum phenotype ontology
        |
        |-- Chapter 1 — phenotype × present-day space/environment
        |     within/among variation; geography; environmental alignment
        |
        |-- Chapter 2 — phenotype × evolutionary time/history
        |     public minimum-change counts; transition localization; topology uncertainty
        |
        `-- Chapter 3 — own RAD-seq × linked phenotype/function
              history discrimination -> mechanism -> reproductive fitness
```

Function is not an admission gate for Chapter 2. Chapter 1 and Chapter 2 reuse the same phenotype ontology on orthogonal axes.

## Chapter 2 current answer

> **A dominant young radiation contains multiple capitulum configurations and each of three constituent traits requires multiple minimum changes, but public evidence resolves minimum counts more reliably than individual event placements.**

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

These are topology-conditioned minimum-change lower bounds. Placement identifiability differs:

- orientation has no individually forced ML edge; JPN36 terminal fraction 0.201;
- phyllary JPN36 terminal fraction 0.754, with root posture ambiguous;
- stickiness placements remain partial.

Equal-branch transition-overlap medians are -0.0594 for orientation–phyllary, -0.3870 for orientation–stickiness and 0.1840 for phyllary–stickiness. No pair is consistently positive across branch-length treatments.

## JEB submission state

Target: **Journal of Evolutionary Biology — Research Article**.

Active standalone title:

> **Capitulum configuration diversity, minimum change counts and uneven event resolution in a young thistle radiation**

Current active state:

- standalone diversity-depth contract and repository-wide inventory frozen;
- EAzami-native continuous registry admitted with identity/source/rights/measurement gates;
- exact-permutation seven-taxon diagnostic complete and `not_supported`;
- discrete minimum-change/localization and bounded niche layers independently executable;
- active standalone manuscript rebuilt as `docs/chapter2/MANUSCRIPT_JEB_V4.md`;
- submission authorization held only for revised figures, anonymous DOCX, reference audit and author declarations.

The former V3 manuscript, figures, Supporting Information and privacy-scrubbed DOCX files remain a reproducible audit snapshot. They must not be submitted as the current standalone paper.

## Active sources of truth

- `docs/chapter2/DIVERSITY_DEPTH_STANDALONE_V1.md`
- `docs/chapter2/CHAPTER2_CORE_RESULT_RECOVERY_V1.md`
- `data/evidence/chapter2_diversity_depth_contract_v1.json`
- `data/evidence/chapter2_core_result_recovery_v1.csv`
- `data/evidence/chapter2_diversity_depth_inventory_v1.csv`
- `data/evidence/chapter2_eazami_native_continuous_trait_registry_summary_v1.json`
- `data/evidence/chapter2_eazami_native_continuous_history_diagnostic_v1.json`
- `docs/chapter2/MANUSCRIPT_JEB_V4.md`
- `data/evidence/chapter2_to_chapter3_radseq_bridge_v1.json`
- `data/evidence/chapter2_to_chapter3_sampling_priorities_v1.csv`
- `docs/chapter2/CHAPTER2_RESOLUTION_AWARE_EVIDENCE_SPLIT_V1.md`
- `data/evidence/chapter2_resolution_classification_v1.csv`
- `data/evidence/meta_simulation_resolution_audit_v1.csv`

JEB manuscript versions v1-v3 are audit history; v4 is current submission text.

## Programme routing

- Present-state v3/v4 covariance simulations: Chapter 1 Supplement or thesis methods.
- Japan-wide own RAD-seq sensitivity plus same-individual phenotype/cytotype: Chapter 3 historical discrimination.
- FDT1 trait-to-function evidence, FDT8 field readiness and field pilots: Chapter 3 causal layer.
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
