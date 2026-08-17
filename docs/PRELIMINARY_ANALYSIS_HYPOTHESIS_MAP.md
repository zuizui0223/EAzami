# EAzami preliminary-analysis hypothesis map

Status: 2026-08-17

## Purpose

EAzami preliminary analysis exists to decide **what biological data to collect next**, not to maximize the amount of computation or to rebuild the largest possible tree before sampling.

The canonical machine-readable registry is:

`data/evidence/preliminary_hypothesis_registry_v1.csv`

Every new preliminary analysis should map to one hypothesis ID in that registry and state three things before it is run:

1. what decision changes if the result is positive;
2. what decision changes if the result is negative;
3. what new biological data are required if the result remains unresolved.

If none of those decisions changes, the analysis is not on the current mainline.

## Current hypothesis map

| ID | Question | Preliminary evidence now | Current verdict | Next decisive data |
|---|---|---|---|---|
| H-RAD1 | Did one Japanese lineage undergo a strongly asymmetric rapid radiation? | Japanese-origin meta-analysis; 36/38 occupancy | **strong descriptive** | No new data needed for the descriptive claim. A branch-length/time tree is optional only if rate acceleration becomes decision-critical. |
| H-EVOL1 | Can the dominant radiation produce large capitulum disparity by modular trait reuse? | Trait-space disparity; authority module combinations; module climate screens | **strengthened, not demonstrated** | Population ancestry + morphology + plastid + cytotype in repeated focal systems |
| H-CLIM1 | Does broad current climate distance explain capitulum disparity? | CHELSA environmental disparity and trait×environment permutation screens | **not supported in current subset** | Focal microclimate and biotic interaction measurements, not more broad CHELSA-only models |
| H-PL1 | Does ploidy deterministically set capitulum state? | Japan-38 cytotype × orientation overlap | **deterministic model rejected** | Same-individual flow cytometry + population ancestry if testing facilitation/evolvability |
| H-COL1 | Does species-tip coding underestimate recent W/C transitions? | Four polymorphic systems; takaoense sample-aware minimum count | **partial support** | Morph-linked nuclear samples for pendulum, sieboldii, aomorense where feasible |
| H-RET1 | Do standing variation and/or introgression enable repeated trait reuse? | Reticulation/ILS context + state-compression evidence | **unresolved** | Population RAD/resequencing + same-individual plastid in repeated focal systems |
| H-MECH1 | Is colour reversibility enabled by pathway retention/regulatory reuse? | C. nipponicum pathway homologs + takaoense DFR/ANS detectability | **plausibility only** | Coding haplotypes + floral RNA + pigment + standardized colour from the same individuals |
| H-CYTO1 | How much cytonuclear discordance exists in focal Japanese radiations? | Literature/public evidence only | **unresolved** | Nuclear + plastid from the same individuals/populations |
| H-ADAPT1 | Are capitulum modules adaptive drivers? | Macro/pre-tree disparity and ecological screens | **unresolved** | Trait manipulation / interaction / reproductive-fitness experiments |
| H-RYK1 | What produced white brevicaule and coloured irumtiense across the Ryukyus? | Arenicola species-level colour-history synthesis | **directional history only** | 4–5 island populations/taxon with ancestry + plastid + cytotype + traits |

## What the existing preliminary analyses have already accomplished

### Radiation

- 36/38 sampled Japanese paper taxon concepts belong to the dominant radiation.
- `C. lineare` is the strongest replicated secondary-history exception.
- `C. dipsacolepis` remains the next secondary-arrival candidate.
- The 36:1:1 pattern is a **sampled radiation-success asymmetry**, not an age-corrected diversification rate.

This is sufficient for choosing contrasting focal systems. Do **not** make a full 294-tip raw-read reconstruction a prerequisite for field sampling.

### Capitulum disparity

The current nine-taxon quantitative subset already shows that:

- a secondary colonization history is not automatically the most morphologically divergent;
- large capitulum disparity occurs within the dominant young radiation;
- a single colonization history does not map to one orientation/stickiness syndrome.

This is enough to motivate H-EVOL1. More broad image-space screens are not needed unless they change focal taxon selection.

### Broad climate

Current capitulum distance is not positively coupled to four broad CHELSA axes in the nine-taxon subset. This weakens a one-axis broad-climate explanation but does not reject adaptation to pollinators, antagonists, rainfall at finer scales, UV, or microclimate.

The next ecological data should therefore add **new ecological dimensions**, not repeat broader versions of the same CHELSA screen.

### Ploidy

2x, 4x and 6x occur among source-backed dominant-radiation taxa, and head orientation is not deterministic by ploidy. Taxon-level cytotype correlations have reached their preliminary ceiling.

The next meaningful ploidy data are population-linked flow-cytometry measurements on the same individuals used for ancestry analysis.

### Flower colour

Species-tip coding compresses documented W/C polymorphism in all four reviewed systems. Only takaoense currently has direct morph-linked high-dimensional nuclear samples; in that system the minimum transition count changes from 1 to 2 when sample states are retained.

The next decisive information is **morph↔genotype linkage in additional systems**, not more species-tip ASR.

### Molecular mechanism

DFR/ANS and other anthocyanin-pathway homologs are recoverable, and both W and BP takaoense public young-leaf RNA runs contain DFR/ANS homologous reads. This establishes plausibility of pathway retention, not floral regulation or causation.

Additional untargeted SRA/BLAST fishing is not a current priority. Mechanistic work resumes when matched floral material is available.

## Preliminary-analysis stop rules

A preliminary line stops when one of these conditions is reached:

- **supported enough to choose sampling** → collect the discriminating biological data;
- **simple model weakened/rejected** → do not keep adding variants of the same model;
- **unresolved because identities are not linked** → collect linked individuals rather than doing more species-level computation;
- **causal question reached** → move to experiment rather than more correlation;
- **only a branch-scaled rate question remains** → defer heavy tree computation until that rate changes a real decision.

## No routine heavy preliminary compute

Routine pull-request CI should be limited to deterministic checks on committed evidence and small statistical reproductions.

The following are **not** routine preliminary CI:

- SRA download / `fasterq-dump` / VDB searches;
- transcriptome assembly;
- HybPiper recovery across large panels;
- broad IQ-TREE / ASTRAL reconstruction;
- Read2Tree or large orthology pipelines;
- rebuilding HPC bundles whose contracts are already frozen;
- repeatedly downloading proteomes/references to reproduce already frozen candidate screens.

Those execution paths remain recoverable from analysis code, workflow directories, frozen evidence, and Git history. They are run only when a registered hypothesis requires them for a concrete decision.

## Current data-acquisition order

### First decision-oriented tranche

Prioritize linked population material rather than broad taxon accumulation:

1. `C. japonicum var. takaoense`: W vs BP, ancestry + colour/mechanism anchor;
2. `C. pendulum`: W vs coloured replicate;
3. `C. brevicaule` + `C. irumtiense`: central vs southern Ryukyu ancestry/colour system.

A practical first tranche is around **100 individuals** if logistics require staging: approximately 40 takaoense, 30 pendulum, and 30 Arenicola split between the two species. This is a decision-oriented first tranche, not a replacement for the full frozen panel.

### Full population-history panel

The current full design remains **222 minimum / 298 recommended individuals** across pendulum, sieboldii, lineare, dipsacolepis, brevicaule and irumtiense. See:

`docs/JAPAN_RADSEQ_PHASE_A_SAMPLING_PLAN_2026-08-16.md`

Each focal individual should, where feasible, link:

`individual_id → locality/GPS → voucher/photo → capitulum traits → nuclear ancestry → plastid haplotype → cytotype`

Focal colour-mechanism individuals additionally link floral RNA and pigment.

## Claim boundary

This registry organizes preliminary evidence and sampling decisions. It does not promote the current descriptive radiation, trait disparity, reticulation, ploidy, or colour results to proof of adaptive radiation, evolutionary-rate acceleration, or causal evolvability.
