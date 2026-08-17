# EAzami — rapid Japanese *Cirsium* radiation

EAzami is organized around one doctoral-level question:

> **Why did one young Japanese *Cirsium* radiation generate such large capitulum and ecological diversity so quickly, despite shallow lineage divergence?**

## Central hypothesis

**Modular evolvability:** standing ancestral variation, gene flow/introgression and cytotype/genome changes allowed pre-existing genetic/developmental modules to be reused and recombined, so capitulum phenotype could diverge faster than genome-wide lineage sorting.

This is the main thesis hypothesis. The older ten-row hypothesis registry is retained only as a supporting evidence register.

## Three doctoral Aims

1. **Aim 1 — Historical/genomic source of rapid phenotypic divergence**  
   Determine whether repeated capitulum states come from standing variation, introgression and population ancestry, with matched plastid and cytotype evidence.
2. **Aim 2 — Adaptive function of capitulum modules**  
   Test whether orientation, colour and involucre/spine modules alter interactions, protection and reproductive fitness.
3. **Aim 3 — Flower-colour reversibility as a mechanistic case**  
   Test whether repeated W↔coloured transitions reuse a retained anthocyanin pathway through regulatory/expression changes.

Full program: `docs/DOCTORAL_RESEARCH_CORE_PROGRAM.md`  
Machine-readable program: `data/evidence/doctoral_core_program_v1.csv`

## What is premise, not a separate thesis Aim

Existing data are already strong enough to treat the following as system justification:

- 36/38 sampled Japanese paper taxon concepts fall in one dominant young radiation;
- *C. lineare* is the strongest replicated secondary-history exception;
- *C. dipsacolepis* remains a secondary-arrival candidate;
- large current capitulum and environmental disparity occurs inside the dominant radiation.

A full 294/296-tip raw-read rebuild is therefore **not a prerequisite for doctoral sampling**. It remains available if branch-scaled rate inference later becomes publication-critical.

## How the old operational questions are used

`data/evidence/preliminary_hypothesis_registry_v1.csv` remains useful for bookkeeping, but its ten rows are not ten equal hypotheses.

- radiation asymmetry = premise;
- evolvability / standing variation / introgression / cytonuclear / ploidy / colour compression / Ryukyu history = Aim 1 diagnostics;
- broad climate = weakened simple alternative informing Aim 2;
- trait→fitness = Aim 2;
- anthocyanin pathway reuse = Aim 3.

Supporting map: `docs/PRELIMINARY_ANALYSIS_HYPOTHESIS_MAP.md`

## Sampling priority

### Core first: 190 minimum

- *C. brevicaule*: 60
- *C. irumtiense*: 60
- *C. pendulum*: 40
- *C. sieboldii*: 30

These four are the biological core because they test repeated rapid phenotype change at population scale.

### Comparative controls: +32

- *C. lineare*: 16
- *C. dipsacolepis*: 16

Full minimum = **222 individuals**. The controls should not reduce replication in the core 190.

Each population-genomic individual should link, where possible:

`individual_id -> locality/voucher/photo -> colour/orientation/involucre -> nuclear ancestry -> plastid haplotype -> flow-cytometry cytotype`

Aim 3 focal individuals additionally link floral RNA, pigment and standardized colour.

## Preliminary-analysis stop rule

New preliminary work is allowed only when it changes one of three decisions:

1. which population/system to sample;
2. which competing mechanism can be discriminated;
3. which claim boundary can be advanced.

More broad CHELSA screens, taxon-level ploidy correlations, untargeted SRA/BLAST fishing and routine heavy tree rebuilding are not current mainline work.

## Start here

1. `docs/DOCTORAL_RESEARCH_CORE_PROGRAM.md` — central question, central hypothesis and three Aims
2. `PROJECT_STATUS.md` — current evidence and next action
3. `data/evidence/doctoral_core_program_v1.csv` — machine-readable doctoral hierarchy
4. `docs/JAPAN_RADSEQ_PHASE_A_SAMPLING_PLAN_2026-08-16.md` — detailed population design
5. `docs/PRELIMINARY_ANALYSIS_HYPOTHESIS_MAP.md` — supporting evidence lanes
6. `docs/DEFERRED_HEAVY_ANALYSES.md` — deferred heavy-compute policy

## Repository layout

- `data/evidence/` — frozen evidence plus doctoral/supporting registries
- `docs/` — central program, claim boundaries and sampling logic
- `analysis/` — deterministic analysis code retained for reproducibility
- `sampling/` — focal sampling/reference panels
- `workflow/` — deferred/manual/HPC execution paths
- `.github/workflows/` — lightweight active CI only

The target end point is not “the biggest tree.” It is a causal explanation linking **where reusable variation came from → how capitulum modules affect fitness → how a focal module can switch repeatedly at molecular scale**.
