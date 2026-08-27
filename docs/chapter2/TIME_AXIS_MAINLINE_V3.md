# Chapter 2 mainline v3 — phenotype through evolutionary time

Status: proposed replacement mainline for Chapter 2 after Chapter 1 is fixed as phenotype × space/environment.

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
```

Chapter 2 is not restricted to traits that were environmentally significant in Chapter 1. A trait can be historically informative even if its present-day environment association is weak or absent.

## 2. Chapter 1 endpoint

Chapter 1 establishes the empirical phenotype ontology and its present-day spatial structure:

- category-free or minimally discretized continuous image traits;
- explicit within- versus among-taxon variation;
- georeferenced phenotype distributions;
- six predeclared environmental blocks;
- spatial and phylogenetic controls where supported by the Chapter 1 design;
- partial whole-capitulum organization rather than one fixed syndrome.

Its endpoint is the reconstructed present phenotypic field, not adaptation itself.

## 3. Chapter 2 question

> **How was multidimensional capitulum phenotype assembled and reassembled through evolutionary history?**

The primary sequence is:

```text
continuous phenotype ontology
        ↓
phylogenetic structure by trait
        ↓
ancestral / branch-wise phenotype reconstruction
        ↓
trait-specific recurrence or conservatism
        ↓
cross-trait historical coupling
        ↓
phenotypic disparity through evolutionary time
```

Function, fitness and ecological mechanism are not prerequisites for these historical analyses. They become later evidence needed to explain why a historical pattern occurred or to promote recurrence to adaptive convergence.

## 4. Existing evidence already supporting the time-axis paper

### 4.1 A young radiation contains large present phenotype disparity

The current Japan synthesis places 36/38 sampled Japanese concepts in one dominant radiation. In the coverage-limited quantitative comparison, the largest phenotype separation inside that dominant radiation exceeds the distance between the secondary-history comparator *C. lineare* and the dominant-radiation centroid. Therefore phenotype distance is not a simple monotonic function of colonization-history separation.

This supplies the opening historical question: how did large capitulum disparity accumulate within a shallow radiation?

### 4.2 Nuclear history scaffold exists

The accepted Japan38 Comp1061 compatibility reconstruction contains:

- 39 focal biological samples / 40 tips including the outgroup;
- 241-locus QC universe;
- 236 current QC loci;
- 176 rootable loci;
- 161,654 bp concatenated alignment;
- 1000 UFBoot and 1000 SH-aLRT replicates.

Branch lengths are substitutions/site, not absolute time. Therefore the current paper may use phylogenetic structure, relative branch order, branch-scaled change and recurrence, but not absolute transition ages without an additional accepted chronogram.

### 4.3 Multiple component traits already require repeated change

Current canonical source-backed results:

- orientation: 20 resolved concepts; ML minimum 6; UFBoot range 4–6; exact branch placement weak;
- phyllary posture: 10 resolved; exactly 3 minimum changes on all 1000 UFBoot trees;
- stickiness: 13 resolved after JPN24; ML minimum 5; root sticky; exactly 5 changes on all 1000 UFBoot trees.

These are recurrence lower bounds, not convergence counts.

### 4.4 Component histories do not collapse to one shared historical axis

The existing orientation × phyllary × stickiness overlap diagnostic found no module pair consistently positive across branch-length-aware and topology-only layers. This weakens the simple one-shared-whole-capitulum historical-lability model.

The overlap calculation must be recomputed with the latest JPN34 orientation and JPN24 stickiness coverage before manuscript freeze.

### 4.5 Continuous traits can also be analysed historically

Continuous colour is the existing proof of concept. LAB lightness, chroma and circular hue were placed directly on the substitution-length tree without forcing white/coloured categories. High-depth lightness showed an anti-phylogenetic pattern, whereas chroma and hue did not show the same signal. The source-balanced Japan-local replication then failed the directional lightness result.

This negative result is useful: historical structure is trait- and evidence-scale-specific rather than universally convergent.

## 5. Missing analysis that now defines the Chapter 2 mainline

### Step A — recover the same continuous phenotype universe for Japan38

Use the frozen Azami GEB-v2 `continuous_trait_universe_observation_long.csv` and exact Japan38 concept mapping to export per-concept summaries for all 18 continuous endpoints. Preserve infraspecific rank, do not impute missing taxa and do not discretize continuous traits.

### Step B — estimate trait-specific phylogenetic structure

For every sufficiently covered continuous endpoint, estimate a common set of historical diagnostics:

- Pagel's lambda or equivalent phylogenetic signal;
- Blomberg-type signal where sample size permits;
- patristic distance versus pairwise phenotype difference;
- leave-one-concept-out sensitivity;
- evidence-depth thresholds based on actual image replication.

Question:

> Which phenotype dimensions track ancestry and which escape it?

### Step C — reconstruct continuous phenotype history

For sufficiently covered endpoints:

- ancestral continuous states under explicitly compared models;
- branch-wise phenotype change;
- phylomorphospace;
- branch-length-scaled disparity.

BM/OU/other models are comparative statistical descriptions, not adaptive-process proof.

### Step D — test cross-trait historical coupling

Compare branch-wise changes among phenotype dimensions and update the discrete transition-overlap analysis. The main contrast is not snapshot covariance, but whether traits that coexist in the same capitulum also change together on the same evolutionary branches.

Question:

> Does present phenotypic integration imply a shared evolutionary history?

### Step E — quantify phenotype disparity through relative time

Use the accepted phylogram for branch-scaled / relative-history summaries. Do not claim absolute Ma timing from substitutions/site. A dated-tree analysis remains an optional later promotion gate.

## 6. Primary paper claims if the new analyses succeed

The strongest bounded endpoint is:

> **The Cirsium capitulum is not only phenotypically decomposable across present-day space; its component traits also carry distinct evolutionary structures through time. Some dimensions are phylogenetically conserved, some recurrent, and currently resolved discrete traits do not share one synchronized history.**

This does not require proving adaptation, functional convergence or modular evolvability.

## 7. What is not part of the Chapter 2 core estimand

The following are valuable but answer different questions:

- trait → function meta-analysis;
- pollinator versus antagonist selection mosaic;
- reproductive-herbivory fitness meta-analysis;
- demographic transmission gates;
- current within/among covariance generator screens (`NULL_COUPLED`, v4.1 scale decoupling);
- population-genomic origin discrimination;
- focal manipulation and reproductive-fitness validation.

Their destinations are frozen separately in `META_SIM_DISPOSITION_V1.md` and `chapter2_analysis_disposition_v1.csv`.

## 8. Chapter 1 → Chapter 2 short formulation

### Chapter 1

> **How is multidimensional capitulum phenotype structured across present-day space and environment?**

### Chapter 2

> **How is the same multidimensional capitulum phenotype structured through evolutionary history?**

The shared methodological contribution is that both questions retain continuous phenotype dimensions and variation instead of returning to a single categorical syndrome.
