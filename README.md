# EAzami — East Asian *Cirsium* flower-colour evolution

Chapter 2 project for reconstructing repeated loss and possible re-expression of floral anthocyanin pigmentation in East Asian *Cirsium* while improving the nuclear phylogenetic framework needed to test those transitions.

## Core questions

> How repeatedly has floral anthocyanin pigmentation been lost and regained in East Asian *Cirsium*, and do repeated transitions use the same molecular mechanisms?

> Which gaps or uncertainties in existing East Asian *Cirsium* phylogenies prevent those flower-colour histories from being tested, and which taxa/populations should be prioritized for nuclear RAD-seq?

The project focuses initially on Japan, the Ryukyu Islands, Taiwan and China. It is the fine-scale evolutionary follow-up to the global image-derived trait work in `zuizui0223/azami`.

## Chapter logic

1. Build a population-aware flower-colour atlas from literature, herbarium material, public photographs and field observations.
2. Audit existing East Asian phylogenomic backbones at the exact taxa/populations needed for colour-transition inference.
3. Prioritize missing or weakly resolved lineages for nuclear RAD-seq, with flower-colour transition information as the first priority and broader East Asian backbone completion as the second.
4. Reconstruct independent pigment-loss events, within-lineage polymorphisms and candidate regain/reactivation branches across a phylogenetic sensitivity set.
5. Select replicated transition systems for pigment chemistry, floral transcriptomics and population genomics/WGS.
6. Test selection only after evolutionary direction and molecular mechanism are sufficiently resolved.

## Why RAD-seq is part of Chapter 2

Existing phylogenies are backbones, not automatically complete answers. East Asian *Cirsium* includes young, polyploid and potentially reticulate lineages; plastid DNA represents one inherited history and can have limited resolution or disagree with nuclear history. Broad nuclear RAD-seq is therefore a parallel project goal, not merely a downstream technique.

RAD-seq sampling is hypothesis-driven. The project does **not** sequence every taxon equally. Missing taxa/populations are ranked by:

1. whether their placement distinguishes alternative flower-colour histories;
2. whether they fill an important nuclear-backbone gap;
3. ploidy/reticulation risk;
4. geographic backbone value across Japan–Ryukyu–Taiwan–China; and
5. need for population replication.

A candidate lineage that distinguishes `coloured -> white` from `coloured -> white -> coloured` is automatically Tier A.

## Primary hypotheses

- **H1 — repeated loss:** floral anthocyanin loss evolved independently multiple times in East Asian *Cirsium*.
- **H2 — regain/reactivation:** at least some coloured lineages descend from an inferred white ancestor or white intermediate.
- **H3 — regulatory reuse:** repeated white-flower transitions disproportionately involve regulatory suppression of a conserved anthocyanin pathway rather than repeated irreversible loss of structural genes.
- **H4 — repeated molecular route:** independent regain events, if present, reactivate homologous regulatory modules or ancestral functional haplotypes.
- **H5 — phylogenetic incompleteness matters:** some apparent colour transitions will change when transition-critical taxa/populations are added to a nuclear backbone.
- **H6 — reticulate history matters:** at least some flower-colour patterns are better explained by introgression/ancestral polymorphism than by simple repeated mutation on a single bifurcating tree.

`Regain` and `reactivation` are hypotheses, not assumed states. They require concordant support from ancestral-state reconstruction, population history and molecular evidence.

## Initial focal systems

- Ryukyu Arenicola: *C. brevicaule* (white) and *C. irumtiense* (coloured)
- Taiwan *C. japonicum* complex: especially *var. albescens* and colour-polymorphic *var. takaoense*
- Additional Japanese and Chinese white/coloured sister-lineage or within-taxon polymorphism candidates discovered by the atlas

## Repository structure

- `docs/RESEARCH_PLAN.md` — aims, hypotheses, analyses and decision rules
- `docs/PHYLOGENY_GAP_AND_RADSEQ_PLAN.md` — nuclear-backbone gap audit and RAD-seq strategy
- `data/schema/flower_colour_records.csv` — observation-level flower-colour schema
- `data/schema/taxon_transition_candidates.csv` — transition-screening schema
- `data/schema/phylogeny_gap_audit.csv` — existing-phylogeny coverage and sequencing-priority ledger
- `sampling/SAMPLING_DESIGN.md` — field and molecular sampling logic
- `analysis/validate_colour_atlas.py` — atlas schema/QC validator
- `analysis/prioritize_radseq_sampling.py` — deterministic RAD-seq priority ranking
- `molecular/` — pigment, RNA-seq and genomic workflows
- `manuscript/` — Chapter 2 manuscript materials

## First executable milestones

### Milestone A — colour atlas

Create a vetted East Asian *Cirsium* table in which every flower-colour claim has taxonomic, geographic and evidence provenance.

### Milestone B — phylogeny-gap audit

For every accepted taxon and transition-critical population, record whether it is represented by adequate nuclear data, only plastid data, weak/uncertain placement, or no usable placement.

### Milestone C — first RAD-seq panel

Rank samples into:

- **Tier A:** directly tests a loss/regain hypothesis;
- **Tier B:** fills major East Asian nuclear-backbone gaps;
- **Tier C:** replication and lower marginal-information samples.

### Milestone D — transition reconstruction

Estimate:

- supported independent white-flower origins;
- white/coloured polymorphism within lineages;
- candidate coloured → white → coloured reversals;
- transitions sensitive to topology or reticulation;
- the 3–5 best replicated systems for mechanistic follow-up.

No expensive WGS/mechanistic cohort should be finalized before the colour-transition screen and phylogeny-gap audit are complete.
