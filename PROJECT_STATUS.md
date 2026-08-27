# EAzami current state

Status date: 2026-08-27

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

> **Present-day capitulum integration is detectable but scale dependent. Several discrete states recur, yet recurrence count, exact transition placement and shared branch localization are distinct. Once reconstruction geometry and topology uncertainty are propagated, the current data do not support one persistent historical capitulum module.**

This statement does not imply zero phylogenetic signal, fully independent traits, independent origins, convergence, adaptation or a shared mechanism.

## Present integration inherited from Chapter 1

At the frozen >=5-observation threshold:

- within-taxon registered-module contrast = **0.164502** (0.130693–0.179475);
- among-taxon contrast = **0.088475** (0.024942–0.126171);
- within/among association-matrix similarity = **0.3663**.

The >=2 sensitivity preserves the ordering: 0.157688 within versus 0.083662 among. These are observational measurement modules, not genetic or historical modules.

## Nuclear history scaffold

- 38 paper concepts and 39 focal biological samples;
- 236 QC nuclear loci, 176 rootable loci and 161,654 aligned bp;
- 1,000 UFBoot and 1,000 SH-aLRT replicates;
- branch lengths in substitutions/site, **not absolute time**;
- JPN20 samples non-monophyletic in ML and 0/1,000 bootstrap trees, so not forcibly collapsed;
- JPN31 excluded from primary trait history because of identity/locality conflict;
- JPN29 retained in the raw tree but prohibited from a clean Japanese phenotype join until specimen identity is resolved.

Published phylogenomics places 36/38 sampled concepts in the dominant Japanese Pleistocene radiation. This is context, not a rate claim.

## Continuous phenotype history

Eight primary units cover orientation, colour and outline shape. Image values are global species-level proxies, not measurements of the sequenced Japanese vouchers.

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

Active title:

> **Present-day phenotypic integration does not imply a shared evolutionary history in a rapid thistle radiation**

Completed:

- active manuscript v3, 227-word abstract and 3,749-word main text including legends/alt text;
- complete Moreyra reference metadata;
- four main and five supplementary figures in PDF and 300-dpi PNG, visually inspected;
- complete Supporting Information with six tables, separate title-page template and cover-letter template;
- AI-use, data, ethics and claim-boundary wording;
- machine-readable result and claim registries;
- four privacy-scrubbed, accessibility-audited DOCX files with continuous line numbering where required.

Remaining author-only metadata:

- author order, affiliations, corresponding author and ORCIDs;
- funding, acknowledgements and conflict confirmation;
- public archive URL/DOI no later than revision;

## Active sources of truth

- `docs/chapter2/TIME_AXIS_MAINLINE_V3.md`
- `docs/chapter2/MANUSCRIPT_JEB_V3.md`
- `docs/chapter2/JEB_QUESTION_RESULT_FIGURE_MAP_V1.md`
- `docs/chapter2/JEB_SUPPORTING_INFORMATION_V1.md`
- `data/evidence/chapter2_jeb_main_result_table_v1.csv`
- `data/evidence/chapter2_time_axis_compute/japan38_branch_change_reconstruction_null_v1.json`
- `data/evidence/chapter2_provenance_sensitivity_compute/japan38_branch_change_provenance_sensitivity_v1.json`

Versions v1/v2 of the JEB manuscript are superseded audit history, not submission text.

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
