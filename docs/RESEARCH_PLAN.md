# EAzami research plan — space, evolutionary history, then function

Status date: 2026-08-27

## Dissertation architecture

The same decomposed capitulum phenotype ontology is used repeatedly; the axis changes by chapter.

```text
continuous image-derived phenotype
        │
        ├── Chapter 1 — phenotype × present-day space/environment
        │     within/among variation, geography, environmental alignment
        │
        ├── Chapter 2 — phenotype × evolutionary time/history
        │     phylogenetic structure, recurrence, branch-wise change, historical coupling
        │
        └── Chapter 3 — phenotype × function/fitness
              trait → performance → reproductive fitness

Chapter 2 repeated histories
        ↓
origin discrimination with population ancestry + plastid + cytotype
        ↓
convergence / adaptive convergence synthesis
```

This ordering supersedes the previous `phenotype → function → history` Chapter-2 plan. A trait does not need a validated ecological function to be admitted to historical analysis.

## Chapter 1 endpoint

Chapter 1 reconstructs the **present phenotypic field** from photographs rather than accepting categorical/species-level trait databases as the endpoint.

Core contribution:

1. define capitulum features as continuous measurements rather than broad categories;
2. preserve repeated observations and below-taxon variation;
3. exploit georeferenced observations to map phenotype in space;
4. test environmental hypotheses using predeclared environmental blocks;
5. compare within- and among-taxon environmental/phenotypic structure;
6. separate environmental alignment from space/phylogeny before discussing adaptive possibilities.

Final Chapter-1 interpretation:

> **The capitulum is not one present-day adaptive syndrome. Its component phenotypes are decomposable and their associations and environmental alignment differ across biological scales.**

Chapter 2 starts from the same phenotype definitions, not only from Chapter-1 significant environment associations.

## Chapter 2 central question

> **How is a multidimensional capitulum assembled through evolutionary history?**

The chapter separates three historical properties that are often conflated:

- **state conservation** — do relatives retain similar continuous phenotype values?
- **recurrence** — how many changes are required for independently defined discrete states?
- **change localization** — do large changes in different phenotype dimensions occur on the same evolutionary branches?

This allows three competing architectures to be distinguished:

1. a conserved multivariate syndrome;
2. fully independent component histories;
3. coordinated episodes of broad remodeling without stable conservation of final trait states.

## Chapter 2 data recovery

### Continuous phenotype bridge

The frozen Azami Chapter-1 artifact is reused, rather than building a new trait dataset around the phylogeny.

Source:

- 46,276 strict-spatial observations;
- 1,018,072 long-format trait rows;
- 18 measured continuous endpoints.

Exact Japan38 concept bridge:

- 14 concepts with at least one continuous phenotype;
- orientation: 8 concepts at >=2 observations, 6 at >=5;
- four shape dimensions: 10 at >=2, 6 at >=5;
- colour: 10 at >=2, 6 at >=5;
- candidate involucre/armature endpoints: only 2 concepts at >=2, therefore not promoted to radiation-wide continuous history.

No broad-species substitution for infraspecific concepts, no missing-value imputation and no forced discretization are allowed.

### Nuclear scaffold

Japan38 Comp1061 compatibility reconstruction:

- 38 paper concepts → 39 focal biological samples;
- 40 tree tips including safflower outgroup;
- 236 QC nuclear loci / 176 rootable loci;
- 161,654-bp concatenated alignment;
- 1000 UFBoot + 1000 SH-aLRT;
- branches in substitutions/site, not absolute time.

JPN20 remains non-monophyletic and is not forcibly collapsed. JPN31 remains excluded from primary phenotype history because of its frozen identity/locality conflict.

## Chapter 2 analysis and current results

### A. Continuous trait-state structure

Eight primary continuous inferential units:

- orientation angle;
- LAB lightness;
- LAB chroma;
- circular hue;
- outline aspect ratio;
- outline circularity;
- outline solidity;
- width-profile CV.

Result:

- 0/8 pass the BH-corrected two-sided phylogenetic-structure family at >=2;
- 0/8 pass at >=5;
- Pagel lambda MLE = 0 for every scalar unit at both thresholds.

Conclusion:

> **Current continuous phenotype states are weakly conserved by relatedness in the exact-concept Japanese panel.**

The strong high-depth negative lightness diagnostic remains secondary because it does not survive the eight-unit two-sided family.

### B. Discrete recurrence

Use only independently source-backed discrete ontologies; continuous image metrics are never binned merely to create transition counts.

Current frozen results:

- orientation: 20 resolved; ML minimum 6; UFBoot 4–6;
- phyllary posture: 10 resolved; exactly 3 changes in all 1000 UFBoot trees;
- stickiness: 13 resolved; ML minimum 5; exactly 5 changes in all 1000 UFBoot trees.

Interpretation: repeated-state lower bounds, not adaptive-convergence counts.

### C. Continuous branch-change coordination

On the ML substitution-length phylogram, BM-conditional standardized change magnitudes are correlated across phenotype dimensions:

- mean pairwise branch-change rho = **0.408006**;
- permutation P = **0.00010**.

This is a different estimand from present-day trait covariance and from phylogenetic conservation of tip values.

### D. Continuous topology sensitivity

Across 1000 equal-branch UFBoot topologies:

- global mean pairwise rho median = **0.141287**;
- 5th percentile = **0.118995**;
- 95th percentile = **0.199615**;
- fraction positive = **1.000**.

Thus broad coordinated change is topology-robust under the preregistered positivity rule.

Module specificity is not:

- within-minus-between median = **0.112435**;
- 5th percentile = **-0.095160**;
- fraction positive = **0.946**.

Therefore the current historical result is broad phenotypic remodeling, not stable module-bounded remodeling.

### E. Discrete transition overlap

Latest equal-branch topology sensitivity:

- orientation × phyllary median rho = -0.0594; positive in 34.9%;
- orientation × stickiness median rho = -0.3870; positive in 0.9%;
- phyllary × stickiness median rho = 0.1840; positive in 78.2%.

No discrete pair is consistently positive across branch-length-aware and topology-only analyses.

## Chapter 2 paper claim

Current bounded conclusion:

> **The Japanese Cirsium capitulum does not behave as a conserved multivariate state, yet evolutionary change is not fully independent across its components. Multiple continuous phenotype dimensions undergo large changes on shared branches, while present-day module labels and discrete transition overlap do not define a stable whole-capitulum historical module.**

Conceptual contribution:

> **State conservation and change localization are different properties of multivariate evolutionary history. A complex phenotype can lose phylogenetic conservation of component states while retaining coordinated episodes of remodeling.**

Do not call this developmental/genetic modularity, adaptation, adaptive convergence, or an absolute evolutionary rate result.

## Submission target

Primary target: **Journal of Evolutionary Biology**, Research Article.

The submission is framed around a general problem in evolutionary biology rather than one genus:

- present integration does not uniquely define historical integration;
- state conservation, recurrence and change localization can disagree;
- topology uncertainty is propagated explicitly;
- informative negative results are part of the inference.

Working title:

> **Coordinated evolutionary change without a conserved phenotypic syndrome in a rapid thistle radiation**

Working manuscript:

- `docs/chapter2/MANUSCRIPT_JEB_V1.md`

Main submission constraints:

- <=7,500 words for a JEB Research Article;
- <=250-word English abstract;
- 4–10 keywords;
- Introduction / Materials and methods / Results / Discussion structure.

## Chapter 2 figure order

### Figure 1 — Concept and system

`present-day integration ≠ state conservation ≠ change localization`

Then place Japan38 in the dominant Pleistocene radiation context.

### Figure 2 — Continuous phenotype state structure

Eight continuous units with lambda / patristic-distance diagnostics at >=2 and >=5.

Headline: no unit has family-level robust phylogenetic state structure.

### Figure 3 — Discrete recurrence

Three separate tree/state panels:

- orientation;
- phyllary posture;
- stickiness.

Do not draw a composite syndrome state.

### Figure 4 — Coordinated continuous branch change

- 8 × 8 branch-change correlation matrix;
- selected branch-change profiles;
- ML global mean rho;
- 1000-topology distribution.

Headline: broad coordinated remodeling is topology-robust, module specificity is not.

### Supplement

- full taxon-concept bridge;
- continuous coverage audit;
- all unit-specific tests and leave-one-out diagnostics;
- full UFBoot topology distributions;
- discrete transition-overlap sensitivities;
- failed absolute-time calibration audit;
- phylogeny provenance and identity gates.

## What happens to existing meta-analysis

Do not delete it and do not force it into Chapter 2.

Move to **Chapter 3 — phenotype × function/fitness** as primary evidence:

- FDT1 trait-to-function evidence ledger;
- Cirsium reproductive-herbivory meta-analysis: RR 2.674, 95% CI 2.388–2.993;
- multi-agent selection mosaic;
- selection leverage;
- demographic transmission;
- display, orientation, stickiness and protective-envelope calibrations.

Chapter 2 Discussion can cite these only as hypotheses for **why** historical change may occur. They are not required to establish the historical pattern.

## What happens to existing simulation

### Current v3/v4 simulations

Route to **Chapter 1 Supplement / thesis structural-methods lane**:

- v3.1 generator-family gap;
- NULL_COUPLED scalar-target winner;
- held-out support pattern 0/64;
- among-only process diagnostic;
- provisional scale-specific covariance v4.1.

Reason: these simulate formation of the present within/among phenotype field. They do not locate evolutionary transitions on phylogenetic branches.

### Future historical simulation

A later simulation can return to Chapter 2/Synthesis only after empirical history is frozen. It must explicitly use tree/history information and ask which evolutionary processes reproduce the observed trait-state and branch-change history.

## Later origin-discrimination layer

Repeated present states can reflect:

- ancestral retention;
- independent lineage-specific change;
- ancestral polymorphism / sorting;
- introgression / gene flow;
- hybridization / cytoplasmic capture;
- reversal / re-expression.

Next discriminator should preferably link the same individuals:

`standardized phenotype + nuclear population genomics + plastid haplotype + cytotype`.

This is a later origin question, not a prerequisite for the current Chapter-2 historical-pattern paper.

## Convergence ladder

`repeated state → independent origin → repeated ecological association → same/equivalent function → reproductive fitness → functional/adaptive convergence`.

Chapter 2 reaches recurrence and change localization. It does not yet reach independent origin or adaptive convergence.

## Immediate actions

1. finish and internally audit `MANUSCRIPT_JEB_V1.md` against frozen evidence files;
2. build Figures 1–4 without introducing new biological claims;
3. update repository entry points so Chapter 2 is no longer described as function-first;
4. keep JPN15 phyllary posture unknown unless an exact authority maps safely to the ontology;
5. stop new Chapter-2 climate/generator fishing;
6. preserve functional meta-analysis for Chapter 3 and population genomics/plastid/cytotype for the later origin gate.

## Stop rules

- no current covariance → evolutionary-history shortcut;
- no low phylogenetic signal → convergence shortcut;
- no repeated parsimony state → independent origin shortcut;
- no coordinated branch change → shared developmental/genetic mechanism shortcut;
- no substitutions/site → absolute time or rate/Myr;
- no phenotype association → validated function;
- no current simulation fit → realized evolutionary history.
