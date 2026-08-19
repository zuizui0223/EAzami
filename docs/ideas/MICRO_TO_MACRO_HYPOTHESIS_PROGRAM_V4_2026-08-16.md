# Micro-to-macro hypothesis program v4 — meta-analysis ceiling and linked-data gates

Date: 2026-08-16  
Status: additive synthesis. **V3 remains frozen; this document does not rewrite its evidence calls.**

## Purpose

Push the current public/existing-data program to its inference ceiling, then explicitly separate:

1. what can already be concluded by descriptive cross-source synthesis;
2. what is merely waiting for an existing computation/artifact;
3. what genuinely remains unidentified without newly **linked** biological data.

This is a descriptive evidence synthesis, not an effect-size meta-analysis.

Machine-readable synthesis: `data/evidence/cross_scale_identifiability_meta_v1.json`.

## Inputs

- `docs/ideas/MICRO_TO_MACRO_HYPOTHESIS_PROGRAM_V3_2026-08-15.md`
- `docs/HMM2_POPULATION_AWARE_TRANSITION_TEST_2026-08-15.md`
- `docs/JAPAN_ADAPTIVE_RADIATION_EVIDENCE_STATUS_2026-08-16.md`
- `data/evidence/japan_adaptive_radiation_evidence_ladder_v1.csv`
- `docs/JAPAN_RADSEQ_PHASE_A_SAMPLING_PLAN_2026-08-16.md`
- `data/evidence/cirsium_flavonoid_molecular_bridge_summary_v1.json`
- molecular-family validation updates recorded in issue #22

---

## Meta-result 1 — the sampled Japanese history is quantitatively concentrated

The current Japanese nuclear-history summary partitions 38 sampled taxon concepts as:

- dominant Japanese radiation: **36**;
- *C. lineare* history: **1**;
- *C. dipsacolepis* history: **1**.

Therefore:

- dominant share = `36 / 38` = **94.74%**;
- dominant : pooled secondary histories = `36 : 2` = **18 : 1**;
- Simpson concentration, `sum(p_i^2)` = **0.8989**;
- inverse-Simpson effective number of represented history classes = **1.1125**.

### Interpretation

The sampled Japanese taxon concepts are extremely concentrated in one inferred nuclear-history class. This sharpens the qualitative statement that the Japanese assemblage is dominated by one radiation.

### Hard boundary

These numbers are **not diversification rates**. They do not correct for branch duration, extinction, incomplete sampling, or unequal opportunity to diversify. Rate inference still requires a dated branch-length tree plus explicit sampling fractions/coverage.

---

## Meta-result 2 — component evidence is ahead of coupling evidence

In the Japanese adaptive-radiation evidence ladder:

- E1–E7 = **7/7 non-unresolved** component/presence nodes;
- E8–E10 = **3/3 unresolved** higher-order coupling nodes.

The supported/partially supported components already include the dominant radiation, temporal compression, ecological/trait divergence examples, nuclear–plastid discordance, cytotype heterogeneity, and the short-branch/species-tree problem.

The unresolved layer is the coupling:

- reticulation/ploidy ↔ radiation success;
- flower-colour transition rate ↔ radiation;
- Azami chapter-1 macro signal ↔ specific molecular mechanism.

This is a useful ceiling result: **collecting another unlinked record of a component has lower value than linking existing components on the same biological units.**

---

## Meta-result 3 — HMM2 is now linkage-limited, not species-list-limited

The population-aware transition audit finds:

- **4/4** reviewed W/C-polymorphic systems show state-resolution compression under one-state-per-taxon coding;
- only **1/4** currently has direct morph-linked public nuclear samples;
- therefore direct morph↔genotype linkage coverage is **25%**, with **3/4** systems still linkage-limited.

For the one currently testable system, *C. japonicum* var. *takaoense*:

- collapsed species-level minimum = **1** transition;
- sample-aware minimum = **2** transitions;
- observed sensitivity = **+1** minimum transition.

This supports the predicted direction of HMM2 in one system, but it is **not** a replicated 2× transition-rate result.

The missing object is no longer simply another species tip. It is a sequenced individual whose colour morph, voucher and population provenance are known.

---

## Meta-result 4 — pathway presence is no longer the main molecular unknown

Existing published-panel synthesis already shows strong coverage of upstream/core flavonoid machinery, while the public-genome validation work recorded in issue #22 further recovered:

- *C. nipponicum* candidates for **11/11** reference rows;
- first-pass family discrimination for **4/4** focal families: DFR, ANS/LDOX, CHS and FLS.

Thus the working molecular question should move away from:

> “Does *Cirsium* have the relevant pathway machinery?”

and toward:

> “Which homologous change is associated with W/C state in matched lineages/individuals, and is it coding, copy-state, cis-regulatory or trans-regulatory?”

Still unresolved from current linked data:

- direct fixed-white versus coloured causal comparison;
- same-locus versus different-locus convergence;
- cis versus trans regulation;
- same-individual genotype ↔ expression ↔ pigment causality.

Candidate recovery is not evidence of historical W/C causation.

---

## P8 — cross-scale linkage bottleneck

**Type:** program-level identifiability result, not a biological hypothesis.

### Result

The dominant remaining uncertainty is **cross-layer linkage rather than component presence**.

Molecular candidates, phenotype variation, phylogenetic structure, discordance, ploidy/cytotype diversity and macroevolutionary trait signals often exist separately. Higher-order claims remain unidentified because those measurements are not consistently linked on the same individuals, populations or phylogenetically positioned lineages.

### Study-design consequence

For causal/cross-scale questions, expected information gain is now higher from **matched individual/population measurements** than from adding more unlinked taxa, papers or pathway-presence records.

This changes the default decision rule:

> Do not ask only “what variable is missing?” Ask “which link between already-observed variables is missing?”

---

## What can still be done without new biological sampling

Before collecting new material, continue to exhaust these existing-data gates:

1. recover/finalize the accepted dated branch-length tree and sampling fractions, then convert the 36:1:1 descriptive asymmetry into a time-aware diversification comparison;
2. continue public accession/specimen searches for morph-linked *C. aomorense*, *C. sieboldii* and *C. pendulum* samples;
3. use the validated molecular-family candidates to define homologous locus panels and gene-tree/copy-number tests;
4. keep macro→micro trait-bridge rows explicit about whether a value is observed, inferred, missing, or merely unlinked.

If these are solved from existing artifacts, they should **not** be counted as reasons for new field collection.

---

## Data gates that remain irreducible or near-irreducible

### G1 — replicated morph↔genotype linkage

Needed:

- same-individual colour morph;
- DNA;
- voucher;
- coordinates/elevation;
- replicated W/C populations.

Highest-value Phase-A systems remain *C. pendulum* and *C. sieboldii* under the existing RAD-seq sampling plan. The point is not simply sample count: the phenotype and sequence must be joined on the same individual.

**Why new data may be required:** 3/4 reviewed polymorphic systems currently lack direct morph-linked public nuclear samples.

### G2 — same-sample ploidy/cytotype linkage

Needed:

- ploidy tissue or measurement tied to the same individuals/populations used for genomic and phenotype analyses.

**Why new data may be required:** public evidence establishes cytotype diversity in the radiation, but exact sample-level ploidy for the focal sampling targets was not recovered in the current audit.

### G3 — direct W/C molecular causation

Needed:

- homologous candidate-locus comparison across fixed-white and coloured lineages;
- phenotype + DNA linked to the same individuals;
- floral RNA and pigment assays only when a genomic association or direct regulatory hypothesis makes them informative.

**Why new data may be required:** existing public sequence data are much better at demonstrating pathway-family presence than at providing matched W/C causal contrasts.

### G4 — diversification-rate inference

Needed:

- accepted dated branch-length tree;
- explicit sampling fractions/coverage for each compared history class.

**Important:** this is not necessarily a field-data gate. It may close by recovering or computing the existing tree/HPC artifact. Until then, `36/38` remains a concentration statistic, not a rate estimate.

### G5 — strict adaptation/selection causation

Needed **only if** the paper intends to claim measured local adaptation or a fitness-mediated mechanism, rather than ecological divergence associated with a rapid radiation:

- phenotype × environment linked to fitness;
- selection gradients and/or reciprocal/common-garden evidence in focal populations.

**Why new data may be required:** rapid radiation + ecological divergence + trait variation can coexist without identifying the fitness-mediated causal mechanism.

### G6 — Azami macro→micro mechanism

Needed:

- populated trait-bridge rows linking chapter-1 macro state to specimen/population-level molecular or regulatory measurements in phylogenetically positioned *Cirsium* units.

**Why new data may be required:** A2 / lambda / BM / OU macro states constrain pattern but do not identify genes, copies or regulatory events.

---

## Priority after this meta-analysis

1. **G1 + G2 first** — highest immediate cross-layer information gain and already aligned with RAD-seq Phase A.
2. **G4 next if still open** — exhaust existing tree/HPC/public artifacts before collecting biology.
3. **G3** — build direct W/C molecular comparison on top of linked genomic samples.
4. **G6** — fill the macro→micro bridge only with traceable biological units.
5. **G5 only when needed** — do not launch expensive fitness experiments merely to strengthen a descriptive radiation claim.

---

## Decision rule for future issues/ideas

Separate these two states explicitly:

- **analysis-limited:** the data/artifact plausibly already exists, but the computation or recovery is unfinished;
- **data-limited:** the target causal/cross-scale contrast is impossible because the measurements were never linked on the same biological units.

New biological collection is justified only for the second class after the first has been exhausted.
