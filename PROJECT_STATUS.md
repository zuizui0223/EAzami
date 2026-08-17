# EAzami current state

Status date: 2026-08-17

## Main goal

The current mainline is **not** to maximize preliminary computation or to finish a 294/296-tip raw-read reconstruction before making biological decisions.

The current goal is:

> identify which hypotheses about the Japanese *Cirsium* radiation are already constrained by existing data, state exactly why the remaining hypotheses are non-identifiable, and collect only the biological data that discriminate those alternatives.

Canonical decision map:

- `docs/PRELIMINARY_ANALYSIS_HYPOTHESIS_MAP.md`
- `data/evidence/preliminary_hypothesis_registry_v1.csv`

## Accepted historical / public state

The public nuclear inventory remains:

- **294 biological tips**;
- **295 unique public SRRs**;
- **270 source-preserving analysis taxon labels**.

EA01 and CNIPG remain independent augmentation candidates. EA02 remains a duplicate-readset control and does not increment biological-tip count. The maximum public candidate ceiling remains 296 tips if both independent gates eventually pass.

This heavy reconstruction path is preserved but **deferred**. It is no longer a prerequisite for Phase-A sampling.

## Preliminary conclusions already sufficient for decisions

### H-RAD1 — radiation-success asymmetry

- 36/38 sampled Japanese paper taxon concepts are in the dominant radiation.
- `C. lineare` is the strongest replicated secondary-history exception.
- `C. dipsacolepis` remains a secondary-arrival candidate.
- 36:1:1 under the three-history point hypothesis is descriptive occupancy, not an age-corrected diversification rate.

**Decision:** sufficient to choose dominant-radiation and secondary-history focal contrasts. Do not delay sampling for a full raw-read tree.

### H-EVOL1 — modular evolvability

Current pre-tree trait data show large capitulum disparity within the dominant radiation. The secondary-history comparator `C. lineare` is not uniquely isolated in trait space, and the authority seed contains multiple orientation/stickiness combinations within the dominant history.

**Decision:** modular evolvability is strengthened as a hypothesis, not demonstrated. The next evidence must link morphology to population ancestry rather than add more broad trait-space screens.

### H-CLIM1 — broad current climate explanation

For the current nine-taxon quantitative subset, seven-axis capitulum distance × four-axis CHELSA distance gives Spearman rho about **-0.215** with no positive-coupling support. Orientation and colour are approximately uncoupled from broad climate distance; shape is negative but not a significant adaptation result.

**Decision:** stop expanding broad CHELSA-only preliminary models. Add microhabitat and biotic interaction data in focal systems instead.

### H-PL1 — deterministic ploidy explanation

Source-backed dominant-radiation cytotypes include 2x, 4x and 6x. Upward/ascending heads occur across all three ploidy levels and diploids include both upward and downward states.

**Decision:** ploidy does not deterministically set capitulum orientation. Future ploidy work must use population-linked flow cytometry and ancestry if testing facilitation/evolvability.

### H-COL1 — species-tip colour compression

Four reviewed W/C-polymorphic systems all lose state multiplicity under one species-tip `P` code. Only takaoense currently has morph-linked high-dimensional nuclear samples; there the minimum transition count changes from 1 to 2 when sample states are retained.

**Decision:** stop additional species-tip colour ASR as a preliminary exercise. Obtain morph↔genotype linkage in additional systems.

### H-RET1 — standing variation vs introgression

Current public data establish plausibility of ILS/reticulation and show state compression, but cannot assign the origin of recurrent trait variants.

**Decision:** population RAD/resequencing + same-individual plastid is required. More broad phylogenomic fishing does not identify the mechanism.

### H-MECH1 — retained pathway / regulatory reuse

C. nipponicum candidate homologs are recovered across the reviewed pathway panel; DFR/ANS homologous reads are detectable in both W and BP takaoense public young-leaf RNA runs.

**Decision:** pathway retention is plausible only. Stop repeated untargeted SRA/BLAST screens. Next evidence is matched coding haplotypes + floral RNA + pigment + phenotype.

### H-ADAPT1 — adaptive radiation

Current macro/pre-tree analyses show disparity and reject several simple explanations, but do not establish selection or fitness effects.

**Decision:** no further macro correlation is allowed to substitute for adaptation. The decisive step is focal trait → interaction → reproductive-fitness experimentation after ancestry is resolved.

## Active preliminary CI

Routine pull-request checks should now focus on lightweight, hypothesis-linked validation:

- Japanese-origin meta/falsification summaries;
- pre-tree trait and environmental disparity;
- total and module-specific trait×environment coupling;
- HMM2 population-aware colour sensitivity;
- HMM3 focal cytotype synthesis;
- Japan-38 cytotype/authority/trait joins;
- current micro-to-macro v3 synthesis;
- canonical preliminary hypothesis registry.

## Deferred heavy computation

The following categories are not current preliminary requirements:

- public SRA reacquisition and VDB screens;
- transcriptome assembly/resource planning;
- large HybPiper + IQ-TREE + ASTRAL reconstruction;
- Read2Tree / large orthology pipelines;
- repeated HPC bundle construction;
- re-downloading proteomes/references to reproduce already frozen candidate screens.

See `docs/DEFERRED_HEAVY_ANALYSES.md`.

## New biological data required

### Highest-information first tranche

A staged first collection can prioritize:

1. takaoense W/BP — morph-linked ancestry and mechanism anchor;
2. pendulum W/coloured — independent Japanese replicate;
3. brevicaule + irumtiense — Ryukyu population-history/colour system.

If logistics require a compact first tranche, approximately **100 individuals** across those systems is enough to begin discriminating H-COL1/H-RET1/H-RYK1, while remaining explicitly a pilot/staged tranche rather than the final panel.

### Full population-history design

The current full target remains **222 minimum / 298 recommended individuals** across:

- `C. pendulum`;
- `C. sieboldii`;
- `C. lineare`;
- `C. dipsacolepis`;
- `C. brevicaule`;
- `C. irumtiense`.

Each individual should link, where feasible:

`individual_id → GPS/locality → voucher/photo → colour/orientation/involucre traits → nuclear ancestry → plastid haplotype → cytotype`

Focal colour-mechanism samples additionally link floral RNA and pigment.

## Stop rules

- Do not run a preliminary analysis unless it maps to a registry hypothesis and changes a decision.
- Do not repeat a weakened broad-climate model with more similar raster combinations.
- Do not use taxon-level ploidy correlations to infer causal evolvability.
- Do not collapse polymorphic taxa to fixed species states for convenience.
- Do not treat image geometry as direct botanical truth without validation.
- Do not use a heavy nuclear tree as a prerequisite for sampling unless a branch-scaled rate/topology result changes the sampling decision.
- Do not call the current Japanese radiation a demonstrated adaptive radiation.

## Navigation

- Hypothesis map: `docs/PRELIMINARY_ANALYSIS_HYPOTHESIS_MAP.md`
- Registry: `data/evidence/preliminary_hypothesis_registry_v1.csv`
- Deferred heavy analyses: `docs/DEFERRED_HEAVY_ANALYSES.md`
- Pre-tree synthesis: `docs/JAPAN_RADIATION_PRETREE_META_SYNTHESIS_2026-08-16.md`
- Sampling plan: `docs/JAPAN_RADSEQ_PHASE_A_SAMPLING_PLAN_2026-08-16.md`
- Macro→micro roadmap: `docs/AZAMI_EAZAMI_MACRO_TO_MICRO_ROADMAP_2026-08-16.md`
- Historical full nuclear execution state: `docs/CURRENT_STATE_2026-08-14.md`
