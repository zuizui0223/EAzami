# EAzami — from phenotype to function, history, origin and convergence in *Cirsium*

EAzami is the downstream evolutionary/functional layer of Azami. The two repositories are not parallel trait projects.

```text
Azami
phenotypic decomposition of the capitulum
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

## Canonical biological question

> **Once a complex capitulum is decomposed into component phenotypes, what do those components do, how often did their states change through evolutionary history, where did repeated states come from, and do independent origins repeatedly solve the same ecological problem?**

The active source of truth is:

- `docs/chapter2/MAINLINE_V2.md`
- `docs/chapter2/MANUSCRIPT_V2_OUTLINE.md`
- `docs/chapter2/FIGURE_TABLE_PLAN_V2.md`
- `docs/chapter2/SUBMISSION_GATES_V2.md`
- `data/evidence/chapter2_result_role_map_v2.csv`
- `PROJECT_STATUS.md`

## Azami endpoint — decompose the present

Azami treats the capitulum as a multivariate phenotype rather than one adaptive syndrome. Orientation, colour, outline/shape, involucre/phyllary architecture, armature and display-related traits are measured separately.

The key handoff is not a list of isolated correlations. It preserves within- and among-taxon organization and shows that association structure changes across biological scale. Image-derived modules remain phenotypic modules; they are not automatically functional or genetic modules.

## EAzami-I — phenotype to candidate function

A measured phenotype is promoted in stages:

```text
observed phenotype
→ candidate functional annotation
→ independent functional evidence
→ focal manipulation/performance response
→ validated functional trait
```

Current ecological constraints include:

- experimentally reduced reproductive insect herbivory increases viable/mature seed output in harmonizable *Cirsium* studies by RR **2.674** (95% CI **2.388–2.993**), establishing a large antagonist fitness channel without identifying which capitulum morphology mediates it;
- factorial selection literature rejects universal pollinator or antagonist dominance and supports a **selection mosaic** working architecture;
- orientation requires at least time-window pollination and abiotic-protection candidate pathways rather than one static visitation coefficient;
- display can increase both mutualist discovery and antagonist exposure;
- a generic `sticky = defence` rule is not retained;
- image-derived phyllary/armature geometry remains candidate morphology until direct focal validation.

## EAzami-II — trait-specific evolutionary histories

Current Japan38 nuclear-history results are reconstructed separately by trait.

- **orientation:** 20 resolved concepts; ML minimum 6 changes; UFBoot range 4–6; exact branch localization remains weak.
- **phyllary posture:** 10 resolved concepts; exactly 3 minimum changes across all 1000 UFBoot trees; JPN36 is the strongest partly localizable terminal target.
- **stickiness:** 13 resolved concepts after merged JPN24 authority repair; ML minimum 5, ML root sticky, and all 1000 UFBoot trees require exactly 5 changes.
- **colour:** the global/high-depth continuous-lightness anti-phylogenetic pattern does not replicate in the source-balanced Japan-local panel, so it is not promoted to a Japanese-radiation transition history.

The current three-module transition-overlap analysis does not support a simple one-shared-whole-capitulum historical-lability model. This does **not** prove developmental/genetic modular evolvability.

## EAzami-III — origin discrimination

Repeated tip states do not yet establish independent origins. The live alternatives include:

- ancestral retention;
- independent lineage-specific transition;
- ancestral polymorphism and sorting;
- introgression / gene flow;
- hybridization / cytoplasmic capture;
- reversal or re-expression where biologically justified.

The next discriminator links standardized phenotype to:

`nuclear population genomics + matched plastid haplotype + cytotype/genome size`.

The aim is not merely a denser tree; it is to determine where repeated phenotype states came from.

## EAzami-IV — convergence

The claim ladder is strict:

```text
repeated present state
→ independent origin supported
→ repeated ecological association
→ same or equivalent function
→ reproductive-fitness consequence
→ functional / adaptive convergence
```

Repeated parsimony changes are not convergence counts. Phenotypic convergence, functional convergence and adaptive convergence are distinct claims.

## Higher-order hypotheses

### Selection mosaic / local functional leverage

This is the leading ecological working architecture. Interaction opportunity alone is insufficient; the focal phenotype must change effective pollination, antagonist access or abiotic protection and that difference must reach fitness.

### Modular evolvability

Retained as a **higher-order endpoint hypothesis**, not the organizing premise. It becomes stronger only if multiple component traits show semi-independent histories and repeated origins reuse standing variation, introgressed variants or regulatory machinery.

### Common lability

Retained as a higher-order competitor. Snapshot residual covariance coupling is not equivalent to evolutionary common lability.

## Auxiliary cross-scale simulation lane

The 62-target Azami → EAzami simulation programme remains intact but is not the definition of evolutionary history.

- v3.1: none of five declared biological driver families passes absolute adequacy;
- PR #119: `NULL_COUPLED` is the frozen scalar-target winner;
- PR #120: the same null fails held-out support geometry, 0/64 primary matches;
- PR #123: among-only process structure improves strongly but remains inadequate;
- draft PR #122: scale-specific covariance families are the first to pass the registered seven-target adequacy screen, pending canonical freeze and independent held-out validation.

These results constrain **statistical covariance formation across scales**. They do not reconstruct trait transitions, historical origins or adaptation.

## Doctoral data gates

The existing three empirical gates remain useful under the new mainline:

1. **Origin gate:** same-individual phenotype + nuclear ancestry + plastid + cytotype.
2. **Function gate:** focal trait → interaction/protection mediator → mature/viable seed fitness.
3. **Colour molecular-reuse gate:** for independently resolved W/C transitions, ancestry + coding/regulatory haplotype + floral RNA + pigment + calibrated colour.

## Current paper boundary

A bounded Chapter 2 paper can already claim that the capitulum is not one fixed syndrome and that currently resolved component traits show different candidate functions and repeated, partly decoupled histories.

It must not yet claim:

- independent origin for every repeated state;
- functional or adaptive convergence;
- adaptive radiation;
- molecular colour reactivation;
- demonstrated modular evolvability.

## Start here

1. `docs/chapter2/MAINLINE_V2.md`
2. `docs/chapter2/MANUSCRIPT_V2_OUTLINE.md`
3. `data/evidence/chapter2_result_role_map_v2.csv`
4. `PROJECT_STATUS.md`
5. `docs/DOCTORAL_RESEARCH_CORE_PROGRAM.md`
6. `sampling/SAMPLING_DESIGN.md`

The canonical short axis is:

> **phenotype → function → history → origin → convergence**
