# Azami → EAzami macro-to-micro research roadmap — 2026-08-16

## Program structure

```text
Azami / Chapter 1
Global public-image macro screen
        ↓ hypotheses, trait distributions, auxiliary involucre/spine proxies
EAzami / Chapter 2
East Asian nuclear history + explicit transition reconstruction
        ↓ replicated focal transitions
Population / mechanism studies
Ancestry + gene flow + expression + pigment + interaction + fitness
```

The capitulum is treated as a modular ecological interface. Colour, orientation, outline and involucral architecture may respond to different historical and selective processes.

## Stage 1 — Azami / Chapter 1

Azami is the global hypothesis-generation layer. It does not yet provide a resolved *Cirsium* species history.

### Primary Chapter 1 traits

- orientation relative to EXIF-oriented image vertical;
- visible corolla Lab/chroma and circular hue;
- capitulum outline aspect ratio, circularity, solidity and width-profile variation.

### Exploratory auxiliary traits already analysed

Chapter 1 already contains a high-resolution involucre/spine image-proxy layer:

- `involucre_projection_roughness`;
- `involucre_spread_fraction`;
- `spine_peak_count_proxy`;
- `spine_relative_length_max_proxy`.

These have explicit image QC and have already been integrated into continuous environment screening, including within-species and between-species analyses. The Chapter 1 fixed-scope plan places them in the exploratory supplement, with auxiliary historical/PGLS sensitivity, rather than the confirmatory headline set.

They are **image-geometry proxies**, not direct botanical measurements of phyllary angle, spine length, spine orientation or stiffness.

Therefore the downstream task is not to “add spines for the first time.” It is to carry the existing proxy results into a resolved phylogenetic framework, test their historical structure, and validate whether they correspond to explicit botanical characters.

### Chapter 1 claim boundary

Chapter 1 may support global macroecological patterns and hypothesis generation. It must not claim:

- a resolved species tree;
- definitive ancestral states or transition counts;
- pollinator/herbivore/climate-adaptation causation;
- genetic variance or evolutionary rate from image variance;
- molecular flower-colour loss/regain mechanisms.

## Stage 2 — EAzami / Chapter 2 functional evolutionary reconstruction

Chapter 2 combines quantitative trait-to-function priors with the East-Asian
history, repeated module transitions, niche-transition tests and predeclared
simulation alternatives. It does not repeat Chapter 1's global spatial
association analysis and does not infer adaptation from state recurrence alone.

### Current nuclear state

Accepted public primary:

- 294 biological tips;
- 295 unique public SRRs;
- 270 source-preserving analysis taxon labels.

Independent augmentation candidates: **EA01 + CNIPG**. EA02 is a duplicate-readset control and does not increment biological-tip count. Maximum current public ceiling is **296 tips**, subject to the explicit common-locus combined gate.

### Historical questions

1. **Japanese origin structure** — test 2 vs 3 vs 4+ histories, with the current point hypothesis of one dominant radiation plus rare secondary entries.
2. **Flower-colour history** — quantify repeated white↔coloured transitions while preserving population polymorphism and topology uncertainty.
3. **Orientation history** — estimate ancestral/transition uncertainty for the image-derived orientation axis and later botanical/field validation.
4. **Outline evolution** — model continuous shape history with within-taxon measurement uncertainty.
5. **Involucre/spine evolution** — map the existing Azami auxiliary proxies onto the accepted nuclear tree before replacing or refining them with direct botanical measurements.
6. **Modular evolution** — test whether colour, orientation, outline and involucral architecture evolve independently or repeatedly covary.

### Existing auxiliary proxy → botanical validation ladder

```text
Azami image proxy
(involucre roughness / spread / spine-like protrusion)
        ↓ phylogenetic mapping
Does the proxy carry reproducible historical signal?
        ↓ targeted validation
Direct phyllary spreading/recurvature angle
Actual spine length / orientation / stiffness
        ↓ ecology
Pollinator access / florivory / seed predation / protection
```

Visible involucral stickiness/glandularity remains a separate trait family that has not been incorporated into the Chapter 1 confirmatory system and requires its own assessability/provenance protocol.

## Stage 3 — focal systems

Priority systems remain:

1. *C. japonicum* var. *takaoense* W vs BP;
2. *C. pendulum* Japanese white vs coloured;
3. *C. sieboldii* Japanese white vs coloured;
4. *C. brevicaule* vs *C. irumtiense*;
5. var. *albescens* plus coloured Taiwan controls.

Mechanistic ladder:

```text
population ancestry / gene flow
→ coding / structural candidate state
→ floral expression
→ pigment chemistry
→ visible phenotype
→ pollinator / antagonist interaction
→ fitness
```

## Azami→EAzami trait bridge

The bridge should preserve one row per taxon × endpoint × evidence scope rather than one forced species state.

Minimum fields:

- source and accepted taxon names;
- trait module and endpoint;
- state type (`continuous`, `discrete`, `circular`, `polymorphic`);
- estimate/state and uncertainty/range;
- observation count and spatial/population coverage when available;
- assessability/QC status;
- direct nuclear-tip match status;
- evidence source and claim boundary.

For the involucre/spine auxiliary traits, include an explicit `proxy_status` field so image geometry cannot later be mistaken for direct botanical measurement.

## Analysis order after the nuclear tree

1. flower colour transition-history analysis;
2. orientation ancestral/transition analysis;
3. continuous outline history;
4. map existing involucre/spine proxies onto the same topology ensemble;
5. test modular/correlated evolution across colour, orientation, outline and involucral architecture;
6. validate high-information proxy transitions with direct phyllary/spine measurements;
7. add genuinely new traits such as stickiness only after assessability/provenance are established;
8. promote replicated transitions to population and fitness experiments.

## Current gates

### Established

- Chapter 1 primary macro pattern;
- Chapter 1 exploratory involucre/spine proxy layer;
- current 294-tip public nuclear inventory and deduplication;
- EA01/CNIPG 296-ceiling execution contracts;
- Japanese-origin 2 vs 3 vs 4+ hypothesis hierarchy;
- repeated white-flower working interpretation;
- W/BP linkage for six public *takaoense* samples;
- DFR/ANS assay-level recoverability in current W and BP public young-leaf RNA runs.

### Blocked by heavy execution

- accepted 294-tip BWA/BLASTx trees;
- source-label ASTRAL topology ensemble;
- EA01/CNIPG empirical admission;
- final 296 combined tree if both pass.

### Not yet executed

- cross-repository trait-tip bridge;
- colour/orientation/outline ASR on the accepted EAzami nuclear tree;
- phylogenetic mapping of existing involucre/spine proxies;
- direct botanical validation of phyllary/spine characters;
- correlated-evolution tests among modules;
- focal fitness experiments.

## Stop rules

- Do not use the current grafted Azami tree as definitive ASR.
- Do not force polymorphic taxa into one fixed state.
- Do not infer adaptation from macro correlation alone.
- Do not call the existing involucre/spine proxy analysis “new” or “unanalysed.”
- Do not equate image proxies with botanical phyllary/spine states without validation.
- Do not freeze broad new China sampling before the public nuclear tree brackets unresolved histories.
