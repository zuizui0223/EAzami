# EAzami current state

Status date: 2026-08-27

## Canonical mainline

```text
Azami
phenotypic decomposition
        ↓
EAzami-I
phenotype → candidate function → validated functional trait
        ↓
EAzami-II
trait-specific evolutionary histories
        ↓
EAzami-III
origin discrimination
        ↓
EAzami-IV
functional / adaptive convergence
```

Active source of truth:

- `docs/chapter2/MAINLINE_V2.md`
- `docs/chapter2/MANUSCRIPT_V2_OUTLINE.md`
- `data/evidence/chapter2_result_role_map_v2.csv`
- `docs/RESEARCH_PLAN.md`

The 62-target simulation programme is now an **auxiliary cross-scale generative-constraint lane**, not the definition of evolutionary history.

## Azami endpoint inherited by EAzami

> **The capitulum is not one adaptive syndrome. Its component phenotypes are decomposable and occupy different environmental and hierarchical structures.**

Key inherited constraints:

- component phenotypes are measured separately rather than collapsed into one syndrome;
- within-taxon module organization is stronger than among-taxon organization;
- within/among association geometry is only partially aligned;
- broad current-climate distance, colonization-history separation and ploidy do not provide simple deterministic explanations for current capitulum disparity.

## EAzami-I — phenotype to function

A measured image phenotype is not automatically a functional trait.

Promotion path:

`observed phenotype → candidate functional annotation → independent evidence → focal manipulation/performance → validated functional trait`.

### Current candidate functions

- **orientation** — time-window pollination / thermal presentation / rain-UV-wetting protection;
- **display** — pollinator discovery/probing + antagonist discovery/exposure;
- **phyllary posture** — reproductive-enemy access/exclusion + possible pollinator-access cost;
- **armature** — candidate enemy exclusion/handling cost, pending direct botanical validation;
- **stickiness** — context-dependent enemy interaction/cost; no universal defence sign;
- **colour** — local availability-dependent pollinator choice + pigment/abiotic physiology.

### Strongest resolved ecological prior

Strict Cirsium reproductive-herbivory meta-analysis:

- 9 within-study contrasts;
- 4 independent data-generation studies;
- pooled viable/mature-seed RR under reduced versus ambient herbivory = **2.674**;
- 95% CI **2.388–2.993**;
- equivalent ambient loss of potential seed output = **62.6%**;
- I² ≈ **1%**.

Resolved conclusion:

> Reproductive insect antagonists can impose a large, repeatable maternal-fitness cost in Cirsium.

Unresolved:

> Which capitulum phenotype changes that cost, and what mutualist or abiotic trade-off accompanies it?

### Selection architecture

The strict factorial literature contains pollinator-dominant, antagonist-dominant and mixed/no-fixed-dominance systems. A universal agent-dominance model is not supported.

Leading ecological working architecture:

`local interaction opportunity × trait-specific functional leverage × fitness transmission gate`.

This is a hypothesis architecture, not a universal fitted equation.

## EAzami-II — trait-specific evolutionary histories

### Nuclear history scaffold

Canonical Japan38 Comp1061 compatibility tree:

- 39 focal biological samples;
- 40 tips including outgroup;
- 241 locus universe / 236 QC loci / 176 rootable loci;
- 161,654-bp concatenated alignment;
- IQ-TREE 2.4.0;
- UFBoot 1000 / SH-aLRT 1000;
- branch lengths = substitutions/site, **not absolute time**;
- JPN20 two biological samples are non-monophyletic in ML and 0/1000 UFBoot trees and are not forcibly collapsed.

### Orientation

Current result after JPN34 authority repair:

- resolved concepts = **20**;
- ML minimum unordered steps = **6**;
- UFBoot step range = **4–6**, median 5;
- recurrence is robust;
- exact branch localization remains weak; no individually forced ML transition edge.

Conclusion:

> Orientation changed repeatedly in the sampled Japanese radiation, but the exact historical branches and adaptive meaning remain unresolved.

### Phyllary posture

- resolved concepts = **10**;
- minimum changes = **3**;
- all 1000 UFBoot trees require exactly 3 changes;
- JPN36 terminal transition is forced in 75.4% of UFBoot trees.

Conclusion:

> Phyllary posture has a topology-robust repeated history, with JPN36 the strongest current ancestry-aware focal target.

### Stickiness

Canonical main result:

- resolved concepts = 12;
- ML minimum = **5**;
- UFBoot = **4–5**, median 5.

JPN24 authority extension, currently pending merge:

- assigned JPN24 = sticky from exact NMNS authority;
- resolved concepts = **13**;
- scientific recomputation gives ML = 5 and **all 1000 UFBoot trees = 5**;
- previous final CI failure was a readiness-schema assertion, not a scientific recomputation failure; a technical CI fix is in progress.

### Cross-module history

No orientation × phyllary × stickiness pair is consistently positive across branch-length-aware and topology-only transition-overlap diagnostics.

Current conclusion:

> **The simple one-shared-whole-capitulum historical-lability model is not supported.**

Boundary:

> This does not demonstrate developmental or genetic modular evolvability.

### Colour as negative-control history

Global/high-depth continuous lightness shows strong anti-phylogenetic structure, but the source-balanced Japan7 panel does not replicate the same directional signal.

Current decision:

- no promotion of the global lightness pattern to a Japanese-radiation colour-transition history;
- no further sampling/reprocessing solely to rescue the anti-phylogenetic sign;
- Ryukyu white/coloured direction and C. irumtiense reactivation remain unresolved.

## EAzami-III — origin discrimination

Repeated present states are not yet independent-origin claims.

Competing origins retained:

- ancestral retention;
- independent lineage-specific change;
- ancestral polymorphism and differential sorting;
- introgression / gene flow;
- hybridization / cytoplasmic capture;
- reversal or re-expression where biologically justified.

Next ancestry discriminator, preferably linked in the same biological individuals:

- standardized phenotype;
- **nuclear population-genomic DNA**;
- same-individual or tightly matched **plastid haplotype**;
- **cytotype / genome-size** information.

Objective:

> Determine where repeated phenotype states came from, not merely build a denser species tree.

## EAzami-IV — convergence

Claim ladder:

`repeated state → independent origin → repeated ecological association → same/equivalent function → reproductive-fitness consequence → functional/adaptive convergence`.

Current position:

- recurrence reached for orientation/phyllary/stickiness;
- independent origin not yet established population-wise;
- focal trait function not yet broadly validated in Cirsium;
- adaptive convergence not established.

## Higher-order hypotheses

### Modular evolvability

Status: **endpoint hypothesis, not organizing premise**.

It becomes stronger only if multiple component traits show partly independent histories and repeated origins reuse standing variation, introgressed variants or retained regulatory/developmental machinery.

### Common lability

Status: higher-order competitor.

The simple whole-capitulum historical form is weakened by current transition-overlap results. Snapshot residual covariance coupling must not be called evolutionary common lability.

### Selection mosaic / local functional leverage

Status: leading ecological working architecture.

Current literature rejects universal pollinator or antagonist dominance and a universal broad functional-class hierarchy.

## Auxiliary cross-scale generative-constraint lane

Purpose:

> Which statistical covariance/process architectures can reproduce the observed within/among phenotypic field?

### v3.1 mechanism screen

None of five declared driver families passed absolute adequacy.

Dominant mismatch:

- simulated among-taxon integration was too strong relative to observed weak among-taxon integration.

### Frozen 62-target one-shot

`NULL_COUPLED` is the preregistered scalar-target structural-sufficiency winner:

- rank 1 in 16/16 primary paired draws;
- min2 sensitivity also rank 1.

Boundary:

> This does not mean environment has no biological effect.

### Held-out falsification

The frozen NULL fails the independently held-out scale-specific support geometry:

- primary 8-cell pattern = **0/64**;
- exact 20-cell pattern = **0/64**;
- mismatch concentrated in replication-stable among-taxon process/GSP support.

### Post-heldout diagnostic

`PROCESS_AMONG_ONLY_SHARED_COUPLED` improves on NULL in **22/24** paired draws but reaches median only **6/8** primary cells, below adequacy.

Conclusion:

> Among-only process structure is directionally useful but insufficient.

### Draft v4.1

Scale-specific covariance families are the first to pass the registered seven-target adequacy screen in the successful draft artifact. This result is **provisional/unmerged** and still requires canonical freeze and held-out validation before scientific promotion.

Role under the new mainline:

> independent support for scale-specific covariance formation, not reconstruction of evolutionary transition history.

## Current bounded Chapter 2 paper

Current-data paper endpoint:

> **The Cirsium capitulum is not one fixed adaptive syndrome. Its decomposed phenotype components have different candidate functional pathways and repeated, partly decoupled histories on the current nuclear topology ensemble. Repeated states are established as recurrence lower bounds, while historical origin and adaptive convergence remain explicit next tests.**

Submission gates:

`docs/chapter2/SUBMISSION_GATES_V2.md`.

Main figure plan:

`docs/chapter2/FIGURE_TABLE_PLAN_V2.md`.

## Next executable scientific priorities

1. **Close JPN24 stickiness integration** without changing the authority state or scientific result.
2. **Repair only the remaining authority-level history gap:** JPN15 phyllary posture, and leave unknown if no exact source maps safely to the ontology.
3. **Build the paper phenotype→candidate-function evidence table** from the existing functional registries.
4. **Prepare Figure 3:** one nuclear tree with separate orientation/phyllary/stickiness panels; no composite syndrome.
5. **Protect the next empirical ancestry layer:** same-individual phenotype + nuclear population genomics + plastid + cytotype.
6. **Run focal functional tests** only where the trait and manipulation are defensible; do not infer causality from species contrasts.

## Field priorities retained

- JPN36: reversible/damage-free phyllary-access feasibility and manipulation after authorization/census/device gates;
- JPN15: within-species stickiness neutralization versus sham when permitted/controlled;
- JPN06: nonsticky 100/100 sister context and only secondary sufficiency/addition tests after material-equivalence validation;
- orientation: improve transition localization before ancestry-specific branch claims, while retaining timing/protection endpoints for focal experiments.

## Stop rules

- no new generic climate model unless it changes phenotype→function, history, origin or convergence discrimination;
- no re-testing whether Cirsium reproductive enemies can reduce seed output; test which phenotype changes the cost;
- no image-derived defence claim without direct botanical/functional validation;
- no repeated-state → adaptive-convergence shortcut;
- no coloured-descendant → reactivation shortcut;
- no `modular evolvability` premise before the lower evidence ladder is satisfied;
- no simulation adequacy → realized evolutionary history shortcut.
