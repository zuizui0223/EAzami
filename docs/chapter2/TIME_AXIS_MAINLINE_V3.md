# Chapter 2 mainline v3 — phenotype through evolutionary time

Status: **canonical Chapter 2 scientific mainline; core time-axis analyses completed and frozen.**

## 1. Chapter symmetry

The dissertation interface is intentionally symmetric.

```text
shared input
georeferenced photographs → continuous capitulum phenotypes

Chapter 1
phenotype × present-day space/environment
        ↓
where is each phenotype distributed, at which biological scale, and along which environmental gradients?

Chapter 2
phenotype × evolutionary time/history
        ↓
how is the same multidimensional phenotype distributed across ancestry, branches and repeated evolutionary change?

Chapter 3
phenotype × function/fitness
        ↓
what does each component do, and how does it affect performance and reproductive fitness?
```

Chapter 2 is not restricted to traits that were environmentally significant in Chapter 1. Function is not an admission gate for historical analysis.

## 2. Historical properties are separated explicitly

Chapter 2 distinguishes four related but non-equivalent properties:

1. **state conservation** — do close relatives retain similar continuous phenotype values?
2. **recurrence** — how many state changes are required for independently defined discrete traits?
3. **change localization** — do large continuous phenotype changes occur on the same evolutionary branches?
4. **module specificity** — if change is coordinated, is it preferentially confined to the present-day measurement modules?

The fifth requirement is robustness to phylogenetic topology uncertainty.

This separation avoids treating present covariance, phylogenetic signal, repeated discrete states and branch-wise lability as interchangeable meanings of integration.

## 3. Chapter 1 endpoint

Chapter 1 establishes the phenotype ontology and its present-day spatial structure:

- continuous or minimally discretized image traits rather than one floral category;
- explicit below-taxon and among-taxon variation;
- georeferenced phenotype distributions;
- predeclared environmental blocks;
- spatial and phylogenetic controls where allowed by the Chapter-1 design;
- partial whole-capitulum organization rather than one fixed syndrome.

Its endpoint is a reconstructed present phenotypic field, not adaptation itself.

## 4. Nuclear history scaffold

The accepted Japan38 Comp1061 compatibility reconstruction contains:

- 38 paper concepts;
- 39 focal biological samples;
- 40 tips including the outgroup;
- 241-locus frozen universe;
- 236 QC loci;
- 176 rootable loci;
- 161,654-bp concatenated alignment;
- 1000 UFBoot and 1000 SH-aLRT replicates.

Branch lengths are substitutions/site, **not absolute time**. Therefore the paper uses phylogenetic structure, relative branch order, recurrence and branch-scaled change, but not absolute transition ages or rate/Myr.

JPN20 remains non-monophyletic and is not forcibly collapsed. JPN31 is excluded from primary phenotype-history inference because of its frozen identity/locality conflict.

Published phylogenomics provides broader context: 36/38 sampled Japanese concepts belong to the dominant Pleistocene radiation.

## 5. Recovering the same continuous phenotype universe

The frozen Azami GEB-v2 trait artifact was re-used rather than rebuilding a trait table around the phylogeny.

Source:

- 46,276 strict-spatial image observations;
- 1,018,072 long-format trait rows;
- 18 continuous endpoints.

Exact Japan38 bridge:

- 14 concepts with at least one continuous phenotype;
- orientation: 8 concepts at >=2 observations, 6 at >=5;
- four primary shape dimensions: 10 at >=2, 6 at >=5;
- continuous colour: 10 at >=2, 6 at >=5;
- candidate involucre/armature endpoints: only 2 concepts at >=2, therefore not promoted to radiation-wide continuous history.

No missing phenotype was imputed, no infraspecific concept was silently replaced by a broad species record, and no continuous trait was discretized merely to increase historical coverage.

Primary continuous inferential units:

1. orientation angle;
2. LAB lightness;
3. LAB chroma;
4. circular hue;
5. outline aspect ratio;
6. outline circularity;
7. outline solidity;
8. width-profile CV.

## 6. Result A — weak phylogenetic state conservation

At both >=2 and >=5 observation thresholds:

- **0/8** primary units pass the BH-corrected two-sided phylogenetic-structure family;
- Pagel lambda MLE = **0** for every scalar unit.

The >=5 lightness subset shows a strong directional anti-phylogenetic diagnostic (rho = -0.707; exact two-sided P = 0.0444; negative-tail P = 0.00139), but the two-sided eight-unit BH q = 0.356, so it is not promoted to a family-level colour-history claim.

Supported conclusion:

> **Continuous capitulum trait states are weakly conserved by relatedness in the current exact-concept Japanese panel.**

Low phylogenetic signal is not itself evidence of convergence.

## 7. Result B — repeated discrete histories

Independent authority-backed state ontologies show recurrence:

- orientation: 20 resolved; ML minimum 6; UFBoot range 4–6, median 5;
- phyllary posture: 10 resolved; exactly 3 minimum changes on all 1000 UFBoot topologies;
- stickiness: 13 resolved after the merged JPN24 repair; ML minimum 5; exactly 5 changes on all 1000 UFBoot topologies.

These values are recurrence lower bounds. They do not identify independent origin or adaptive convergence.

## 8. Result C — continuous change localization is coordinated

On the substitution-length maximum-likelihood phylogram, the common complete primary panel contains eight exact concepts and 14 branches.

For each continuous unit, BM-conditional parent-child change magnitude was standardized; hue was retained as circular chord change. Across the 28 pairwise trait comparisons:

- global mean branch-change Spearman rho = **0.408006**;
- independent branch permutation **P = 0.00010**.

Thus weak conservation of final states does not imply fully independent histories. Branches with relatively large change in one phenotype dimension tend also to carry large changes in others.

## 9. Result D — broad coordination is topology-robust

The continuous analysis was repeated across all 1000 raw UFBoot topologies after setting every non-root branch to 1.0, removing substitution-length information.

Global mean pairwise branch-change rho:

- usable trees = **1000/1000**;
- median = **0.141287**;
- q05 = **0.118995**;
- q95 = **0.199615**;
- fraction positive = **1.000**.

The preregistered robust-positive rule required q05 > 0 and fraction positive >=0.95. The global coordinated-change signal **passes**.

Supported conclusion:

> **Broad coordinated evolutionary remodeling survives topology uncertainty and removal of substitution-length branch information.**

## 10. Result E — present-day modules do not define a robust historical boundary

On the ML phylogram:

- within-module mean rho = **0.494994**;
- between-module mean rho = **0.366802**;
- within-minus-between = **0.128192**;
- exact module-label permutation P = **0.167857**.

Across 1000 equal-branch bootstrap topologies:

- within-minus-between median = **0.112435**;
- q05 = **-0.095160**;
- fraction positive = **0.946**.

The preregistered module-specific robust-positive rule therefore **fails**.

Supported conclusion:

> **Evolutionary change can be broadly coordinated without being stably confined to the present-day measurement modules.**

This does not demonstrate developmental or genetic modularity.

## 11. Result F — discrete transition overlap is topology-sensitive

With latest authority coverage, branch-length-aware ML transition posteriors can show apparent positive overlap, especially for orientation × stickiness. The equal-branch UFBoot ensemble changes that pattern:

- orientation × phyllary: median rho = **-0.0594**, fraction positive = **0.349**;
- orientation × stickiness: median rho = **-0.3870**, fraction positive = **0.009**;
- phyllary × stickiness: median rho = **0.1840**, fraction positive = **0.782**; q05 remains negative.

No discrete pair has a consistently positive shared-transition history across branch-length-aware and topology-only analyses.

The simple one-shared-whole-capitulum discrete-lability model is therefore not supported.

## 12. Integrated Chapter 2 conclusion

The evidence rejects both extreme simplifications.

### Not a fixed conserved syndrome

- continuous states lack robust phylogenetic state conservation;
- several independently defined discrete traits require repeated changes.

### Not fully independent component histories

- continuous change localization is positively coordinated;
- the global coordination survives every tested bootstrap topology.

### But not a fixed historical module either

- present-day module labels do not define a topology-robust boundary around coordinated change;
- discrete state-transition overlap is heterogeneous and topology-sensitive.

The bounded interpretation is:

> **A complex capitulum can lose phylogenetic conservation of its component states while retaining coordinated episodes of broad phenotypic remodeling. Present-day modules do not map cleanly onto stable historical modules.**

This is a historical pattern claim. It does not identify one shared developmental mechanism, genetic architecture, selective regime, adaptation or absolute evolutionary rate.

## 13. Submission

Primary target: **Journal of Evolutionary Biology — Research Article**.

Working title:

> **Coordinated evolutionary change without a conserved phenotypic syndrome in a rapid thistle radiation**

Active manuscript: `MANUSCRIPT_JEB_V2.md`.

Main figure logic is frozen in `JEB_QUESTION_RESULT_FIGURE_MAP_V1.md`.

## 14. What is not part of the Chapter 2 core estimand

### Move to Chapter 3 — phenotype × function/fitness

- trait → function meta-analysis;
- pollinator versus antagonist selection mosaic;
- reproductive-herbivory fitness meta-analysis;
- selection leverage;
- demographic transmission;
- focal functional manipulations.

These answer **why** historical changes matter, not whether the historical pattern exists.

### Move to Chapter 1 Supplement / thesis structural methods

- current within/among covariance generator screens;
- NULL_COUPLED scalar-target result;
- held-out 0/64 support-geometry failure;
- among-only process diagnostic;
- provisional scale-specific covariance v4.1.

These model the present phenotype field and do not locate evolutionary transitions on the tree.

### Later origin/convergence layer

Repeated states still require:

`standardized phenotype + nuclear population genomics + plastid haplotype + cytotype`.

Only after independent origin, repeated ecological association, equivalent function and reproductive fitness can recurrence be promoted to functional/adaptive convergence.

## 15. Stop rules

- no present covariance → realized evolutionary history shortcut;
- no low phylogenetic signal → convergence shortcut;
- no repeated state → independent origin/adaptive convergence shortcut;
- no coordinated branch change → shared developmental/genetic mechanism shortcut;
- no substitutions/site → absolute time or rate/Myr shortcut;
- no image phenotype → validated function shortcut;
- no simulation adequacy → realized evolutionary history shortcut.
