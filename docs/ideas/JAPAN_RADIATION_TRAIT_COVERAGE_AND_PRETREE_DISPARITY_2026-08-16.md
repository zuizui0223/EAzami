# Japan radiation trait coverage and pre-tree disparity — 2026-08-16

## Current position

The Azami→EAzami macro-to-micro bridge now has real public-image trait data rather than only a future schema.

The immediate question is not yet whether Japanese *Cirsium* is a demonstrated adaptive radiation. It is narrower and more diagnostic:

> **Does the young dominant Japanese radiation already contain capitulum-phenotype disparity comparable to or greater than that separating a replicated secondary-history lineage?**

This can be asked descriptively before the accepted 294/296 branch-length tree exists, provided the result is not promoted to an evolutionary-rate or adaptation claim.

## 1. Trait coverage recovered without new biological sampling

### Balanced Chapter-1 atlas

The 216-taxon balanced Azami atlas contains usable colour/orientation/shape summaries and exploratory involucre/spine proxies, but only 11 Japan-38 species binomials are represented.

### Strict spatial primary cohort

Reusing the existing 46,276-observation strict spatial cohort increases coverage to 15 distinct Japan-38 binomials representing 17 paper concepts.

### Original exhaustive detector-positive source

The frozen all-photo exhaustive artifact contains 286 detector-positive taxa. A dedicated Japan-38 exporter recovered:

- **18 / 36 distinct Japan-38 species binomials**;
- **20 / 38 paper taxon concepts** at binomial level;
- 9 trait taxa with >=10 detector-positive observations;
- 6 with >=20;
- 5 with >=50.

Azami workflow run `31946204603` completed successfully. Artifact `9263360258`, digest `sha256:1fa35c17d4aba672e2f8a2a0c33a3792715f7a09e1dd64d3871b25a6c7524b19`.

The exhaustive source additionally recovers *C. amplexifolium*, *C. matsumurae* and *C. microspicatum*, which were present/detected but lost by strict spatial filtering. These do not require new field sampling merely to obtain non-spatial image-trait summaries.

## 2. The remaining image-trait gap is now distinguishable from a phylogenetic gap

Eighteen Japan-38 species binomials are absent from the current Azami exhaustive source pool. This is not the same as absence from the nuclear tree.

Most already have Moreyra target-capture tips. Their immediate missing evidence is therefore **phenotype coverage**, not species placement.

The gap priorities are frozen in `data/evidence/japan38_trait_gap_recovery_priority_v1.csv`.

### A0 — recover before broad new sampling

**`C. dipsacolepis`**

- already has a high-dimensional Moreyra nuclear tip;
- is the current second secondary-arrival candidate;
- is absent from the Azami image source pool;
- therefore blocks a two-exception phenotype comparison for HMM3.

Its next action is targeted synonym-aware public image / herbarium / flora recovery for colour, orientation and outline, not new target capture for species placement.

### A1 — high information for trait × ploidy

**`C. alpicola`**

- member of the dominant radiation under the current meta-synthesis;
- existing taxon-level cytotype record = 6x / 2n=102;
- absent from the current Azami image source pool.

Recovering its phenotype would strengthen the test of whether large phenotype displacement occurs across contrasting cytotypes inside the dominant radiation.

### Manual identity gates

- `C. yuki-uenoanum` ↔ public/NCBI `C. waldsteinii` context;
- `C. effusum` ↔ public/NCBI `C. pulchellum` context.

Azami contains source observations under the latter names, but Moreyra provenance already contains identity/geography conflicts. These are sensitivity candidates only until voucher/current-name review is resolved.

### Tree-dependent recovery

The remaining 14 gaps should not all be pursued equally before the accepted nuclear tree. Their value depends on which internal branches of the dominant radiation are otherwise phenotype-empty. Once branch structure is frozen, prioritize the smallest image-recovery set that maximizes phylogenetic coverage.

## 3. Pre-tree trait-space result

A coverage-filtered descriptive comparison was run on the nine Japan-38 trait taxa with >=10 detector-positive observations using seven non-circular primary endpoints:

- orientation;
- Lab lightness;
- Lab chroma;
- aspect ratio;
- circularity;
- solidity;
- width-profile CV.

Circular hue sine/cosine were excluded from this Euclidean trait-space summary to avoid counting components of one circular trait as independent linear traits.

`C. lineare` was used as the replicated secondary-history comparator. The other eight currently covered taxa were treated as dominant-radiation members under the frozen Japanese-origin meta-synthesis.

Frozen output: `data/evidence/japan_radiation_pre_tree_trait_disparity_v1.json`.

Validation run `31946584374`: success. Artifact `9263459044`, digest `sha256:dc034d220271f8ea8c9cd27c1a346f50494a14091e39d95d2bef377939e96f65`.

### Result

- `C. lineare` distance from the dominant-radiation centroid = **4.842**;
- largest dominant-radiation leave-one-out displacement = **8.103**, `C. sieboldii`;
- largest within-dominant pairwise distance = **6.751**, `C. sieboldii`–`C. verutum`;
- largest observed `C. lineare`→dominant pairwise distance = **6.275**.

Therefore, in this small current-state trait subset:

> **separate colonization history is not a monotonic proxy for capitulum-phenotype distance. Larger current trait disparity can occur among members of the dominant young radiation than between the replicated secondary-history lineage and members of the dominant radiation.**

## 4. What this changes conceptually

This result strengthens, but does not prove, the idea that the successful Japanese radiation may have explored phenotype space rapidly through partly independent trait modules.

It makes a simple model less attractive:

```text
more phylogenetic / colonization separation
        ↓
more phenotype difference
```

The data instead motivate testing:

```text
young dominant radiation
        ↓
large within-radiation phenotype disparity
        +
colour / orientation / shape / involucre modules partly decoupled
        ↓
possible high evolvability
```

This feeds existing HMM3 (`radiation-success / evolvability`) and HMM6 (`cross-scale trait decoupling`). It does **not** justify a new HMM7 before tree-aware replication.

## 5. What remains unresolved with public image data alone

The present result cannot distinguish among:

- genuinely elevated evolutionary trait rates;
- one or a few large recent transitions;
- phenotype convergence;
- ancestral standing variation;
- introgression;
- allometry or habitat-correlated current-state differences;
- sampling / image-observation structure.

Those require the accepted nuclear branch-length/topology ensemble and, for some alternatives, population data.

## 6. Next public-data analyses before biological sampling

### Tree-dependent trait test

After the accepted 294/296 topology ensemble:

1. map the recovered primary traits to direct/reconciled nuclear tips;
2. propagate measurement uncertainty and missing taxa;
3. estimate trait disparity and branch-scaled change within the dominant radiation;
4. compare against `C. lineare` and, after trait recovery, `C. dipsacolepis`;
5. repeat across topology/branch-length sensitivities.

### Targeted image recovery

Before new field collection for morphology, exhaust legal/public sources for:

1. `C. dipsacolepis`;
2. `C. alpicola`;
3. manual identity candidates after provenance resolution;
4. branch-informative dominant-radiation gaps selected after the tree.

### Niche layer

Build matched occurrence/environment summaries for the same lineages. Ask whether the large within-radiation trait disparity is accompanied by niche-space divergence rather than merely phenotype divergence.

## 7. Where genuinely new biological data become necessary

No amount of additional public-image recovery can establish:

- morph↔genotype ancestry in `pendulum` / `sieboldii`;
- standing variation versus introgression in focal systems;
- population cytotype distributions;
- ploidy-aware local ancestry;
- trait → interaction → fitness causation;
- genotype → floral expression → pigment → phenotype mechanisms.

Those remain the explicit reasons for Phase-A RAD/plastid/flow-cytometry sampling and later focal experiments.

## Claim boundary

This document records a **pre-tree descriptive meta-result and a data-acquisition decision**. It does not establish accelerated trait evolution, convergence, adaptive radiation, trait causation, or direct ancestry. The phrase `adaptive radiation` remains a hypothesis-level endpoint until comparative branch-scaled trait/niche results and representative fitness evidence are available.
