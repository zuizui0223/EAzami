# Chapter 2 research plan — phenotype → function → history → origin → convergence

## Current source of truth

The active Chapter 2 scientific mainline is:

- `docs/chapter2/MAINLINE_V2.md`
- `data/evidence/chapter2_result_role_map_v2.csv`

The existing manuscript package remains under `docs/chapter2/`, but `MANUSCRIPT_V1.md` is now a prior simulation-centred draft to be rewritten against MAINLINE_V2 rather than the organizing source of truth.

The previous flower-colour loss/regain plan remains archived at:

`docs/archive/RESEARCH_PLAN_FLOWER_COLOUR_LEGACY_2026-08-27.md`

Colour is retained as one trait-specific history/mechanism module, not as the Chapter 2 organizing question.

## Central dependency

```text
Azami
phenotypic decomposition
        ↓
EAzami-I
candidate functional annotation / validation
        ↓
EAzami-II
trait-specific evolutionary history
        ↓
EAzami-III
origin discrimination
        ↓
EAzami-IV
functional / adaptive convergence
```

Azami and EAzami are not parallel trait projects.

### Azami

> **The capitulum is not one adaptive syndrome. Its component phenotypes are decomposable and occupy different environmental and hierarchical structures.**

Azami defines the phenotype components and their present-day within/among structure. It does not assign adaptive function or reconstruct evolutionary origin.

### EAzami

> **For each decomposed phenotype, determine what function it can perform, when and how often its states changed, whether repeated states share or differ in origin, and only then whether independent origins repeatedly solve the same ecological problem.**

## Stage 1 — phenotype to candidate functional trait

A measured image phenotype is not automatically a functional trait. The required promotion path is:

```text
observed phenotype
→ candidate functional annotation
→ independent functional evidence
→ focal manipulation / performance response
→ validated functional trait
```

Current evidence supports the following candidate axes:

- orientation: time-window pollination, thermal presentation, rain/UV/wetting protection;
- display: pollinator discovery/probing and antagonist discovery/exposure;
- phyllary posture: reproductive-enemy access/exclusion and possible pollinator-access cost;
- armature: candidate enemy exclusion/handling cost, pending direct botanical validation;
- stickiness: context-dependent enemy interaction/cost with no universal defence sign;
- colour: pollinator choice and pigment/abiotic physiology under local availability and ancestry context.

The strongest resolved ecological prior is that reproductive insect herbivory can impose a large maternal-fitness cost in Cirsium (pooled viable/mature-seed RR under reduced versus ambient herbivory = 2.674, 95% CI 2.388–2.993). This establishes the importance of the antagonist channel, not the protective function of any particular phenotype.

## Stage 2 — trait-specific evolutionary histories

Use the accepted nuclear phylogenomic topology ensemble and source-backed state definitions. Reconstruct each trait separately rather than forcing one whole-capitulum syndrome history.

Current history results:

- orientation: repeated change, ML minimum 6 and UFBoot range 4–6 after the JPN34 authority extension; branch localization remains weak;
- phyllary posture: exactly 3 minimum changes across all 1000 UFBoot trees; JPN36 is the strongest current partly localizable target;
- stickiness: canonical main ML minimum 5 with UFBoot range 4–5; JPN24 authority extension yields 13 resolved concepts and 5 changes on every UFBoot topology but is not yet merged;
- colour: global/high-depth continuous lightness overdispersion does not replicate as the same source-balanced Japan-local pattern, so colour history is not promoted by that route.

The simple whole-capitulum common-lability alternative is not supported by the current three-module transition-overlap diagnostic. This does not prove genetic/developmental modular evolvability.

## Stage 3 — discriminate origins of repeated states

Repeated present states can arise through:

- ancestral retention;
- independent lineage-specific change;
- ancestral polymorphism and sorting;
- introgression / gene flow;
- hybridization / cytoplasmic capture;
- reversal or re-expression where justified.

Species-level topology cannot distinguish all of these. The next ancestry layer therefore links standardized phenotype to:

- nuclear population-genomic DNA;
- same-individual or tightly matched plastid haplotype;
- cytotype / genome-size information.

The objective is not simply a denser tree. It is to identify where repeated phenotype states came from.

## Stage 4 — test convergence

The claim ladder is:

```text
repeated state
→ independent origin
→ repeated ecological association
→ same / equivalent functional consequence
→ reproductive-fitness consequence
→ functional or adaptive convergence
```

Repeated parsimony changes alone are not convergence counts. A phenotype can be multifunctional, and different phenotypes may provide the same function.

## Auxiliary lane — cross-scale generative constraints

The 62-target simulation programme is retained but no longer defines EAzami's primary meaning of history.

Its question is:

> **Which covariance/process architectures are statistically compatible with the observed within/among phenotypic field?**

Current results remain valid:

- v3.1: no declared biological driver family passes absolute adequacy;
- scalar one-shot: `NULL_COUPLED` is the frozen scalar-target winner;
- held-out support test: `NULL_COUPLED` fails the primary scale-specific pattern in 0/64 draws;
- post-heldout diagnostic: among-only process structure improves strongly but is still inadequate;
- draft v4.1: scale-specific covariance families are the first structures to pass the registered seven-target adequacy screen, but the result is not yet canonical or independently held-out validated.

These simulations diagnose scale-specific covariance formation. They do not reconstruct transition number, ancestral state or historical origin.

## Higher-order endpoint hypotheses

### Modular evolvability

Retain as an endpoint hypothesis generated by partly independent trait histories, standing variation, introgression and regulatory reuse. Do not use it as the premise that organizes every analysis.

### Common lability

Retain as a competing higher-order explanation. Distinguish evolutionary common lability from contemporaneous residual covariance coupling.

### Selection mosaic

Retain as the leading ecological working architecture: local interaction opportunity and trait-specific functional leverage determine which component matters in a given population, while downstream demographic context can gate whether seed-fitness differences propagate to recruitment.

## Current completion boundary

### Already established

- phenotypic decomposition and within/among scale asymmetry;
- strong reproductive-antagonist fitness cost in harmonizable Cirsium experiments;
- no universal pollinator/antagonist dominance;
- repeated orientation, phyllary and stickiness histories on the current nuclear topology ensemble;
- failure of simple whole-capitulum historical lability;
- failure of the global colour-overdispersion pattern to replicate as the same Japan-local historical signal;
- several simple deterministic explanations (broad climate distance, colonization-history distance, ploidy class) are inadequate for current capitulum disparity.

### Still required

- focal Cirsium trait-function validation;
- population-level origin discrimination;
- ecological-regime matching across independent origins;
- final reproductive-fitness links;
- molecular retention/expression evidence for any colour reactivation claim.

## Operational rule

Every new analysis or sample must advance one of four biological transitions:

1. phenotype → function;
2. function/state → evolutionary history;
3. repeated state → historical origin;
4. independent origin → convergence.

Analyses that only add another descriptive model without changing one of these transitions are lower priority.
