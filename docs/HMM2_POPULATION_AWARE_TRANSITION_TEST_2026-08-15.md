# HMM2 population-aware transition test — 2026-08-15

## Question

Does one-state-per-species coding underestimate recent white/coloured evolutionary history in young polymorphic *Cirsium* lineages?

This is an EAzami hypothesis test, not a restatement of another paper's future-work section.

## Evidence levels

### Stage A — state-resolution compression

Four reviewed, source-backed W/C-polymorphic systems are currently available:

- *Cirsium japonicum* var. *takaoense*;
- *C. aomorense*;
- *C. sieboldii*;
- *C. pendulum*.

All four are represented as taxon-level `P` states in `cirsium_flower_colour_atlas_v0_2.csv`. A single `P` tip preserves the fact of polymorphism but cannot represent the two observed extant states as separate leaves of a genealogy.

This is a **state-resolution result**, not proof of four evolutionary transitions.

### Stage B — minimum-transition count sensitivity

Only var. *takaoense* currently has direct morph-linked public nuclear samples: 3 W + 3 C/BP samples with exact SRA/BioSample/voucher links.

The frozen Fitch screen gives:

- species-level ambiguous var. *takaoense*: minimum **1** transition;
- population/sample-aware var. *takaoense*: minimum **2** transitions.

Thus, in the one currently testable system, retaining sample states increases the minimum transition count by **+1**, or 2× relative to the collapsed species-tip screen.

This is direct support for the **direction** predicted by HMM2, but it is still one system.

### Stage C — replicated transition-rate test

Not yet identified from existing public data.

For the three Japanese polymorphic species, the nuclear backbone is present but the sequenced tip is not linked to the white/coloured morph:

- *C. aomorense*: Moreyra run `SRR30887235`, morph unknown;
- *C. sieboldii*: `SRR30887308`, cultivated source, morph unknown;
- *C. pendulum*: `SRR25265649`, Russian sample, morph unknown.

A targeted NCBI search on 2026-08-15 did not recover a sequence explicitly linked to the named Japanese white forms. Record this as **not recovered by the targeted search**, never as evidence of absence.

Therefore a replicated transition-rate comparison remains blocked until multiple systems have morph-linked population genealogies and branch lengths/topology weights.

## Current inference

HMM2 receives **partial support**:

1. state compression is directly present in 4/4 reviewed polymorphic systems;
2. the predicted increase in minimum transition count is observed in 1/1 currently testable morph-linked system;
3. replicated transition-rate bias is unresolved, because 3/4 systems lack morph↔genotype linkage.

Do not summarize this as “population-aware analysis proves transition rates are doubled.” The current direct result is a one-system minimum-count sensitivity plus a four-system state-resolution audit.

## New problem exposed by the test

The limiting factor is no longer simply missing species in the phylogeny. It is **morph–genotype linkage**.

A species may already have a high-dimensional nuclear tip and a documented white form, yet remain unusable for population-aware character-history inference if the sequenced individual is not the documented morph.

This creates a second form of macroevolutionary resolution bias:

> species-tip coding compresses state diversity, while sample provenance determines whether that hidden diversity can be restored computationally.

## Next existing-data gate

1. keep searching public accessions and specimen metadata for morph-linked *aomorense*, *sieboldii* and *pendulum* material;
2. once the accepted 294/296 nuclear tree is available, quantify how treating the three taxa as `P`, unknown sequenced morph, or separately sampled W/C populations changes ancestral-state uncertainty;
3. do not assign their current Moreyra tips W or C post hoc.

If no public morph-linked data exist, these three systems become high-information population sampling targets rather than reasons to relax the HMM2 evidence standard.
