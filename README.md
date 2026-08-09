# EAzami — East Asian *Cirsium* flower-colour evolution

Chapter 2 project for reconstructing repeated loss and possible re-expression of floral anthocyanin pigmentation in East Asian *Cirsium*.

## Core question

> How repeatedly has floral anthocyanin pigmentation been lost and regained in East Asian *Cirsium*, and do repeated transitions use the same molecular mechanisms?

The project focuses initially on Japan, the Ryukyu Islands, Taiwan and China. It is the fine-scale evolutionary follow-up to the global image-derived trait work in `zuizui0223/azami`.

## Chapter logic

1. Build a population-aware flower-colour atlas from literature, herbarium material, public photographs and field observations.
2. Map flower-colour states onto existing phylogenomic backbones rather than rebuilding a species-level phylogeny from scratch.
3. Identify independent pigment-loss events, within-lineage polymorphisms and candidate regain/reactivation branches.
4. Select replicated transition systems for pigment chemistry, floral transcriptomics and population genomics.
5. Test selection only after evolutionary direction and molecular mechanism are sufficiently resolved.

## Primary hypotheses

- **H1 — repeated loss:** floral anthocyanin loss evolved independently multiple times in East Asian *Cirsium*.
- **H2 — regain/reactivation:** at least some coloured lineages descend from an inferred white ancestor or white intermediate.
- **H3 — regulatory reuse:** repeated white-flower transitions disproportionately involve regulatory suppression of a conserved anthocyanin pathway rather than repeated irreversible loss of structural genes.
- **H4 — repeated molecular route:** independent regain events, if present, reactivate homologous regulatory modules or ancestral functional haplotypes.

`Regain` and `reactivation` are hypotheses, not assumed states. They require concordant support from ancestral-state reconstruction, population history and molecular evidence.

## Initial focal systems

- Ryukyu Arenicola: *C. brevicaule* (white) and *C. irumtiense* (coloured)
- Taiwan *C. japonicum* complex: especially *var. albescens* and colour-polymorphic *var. takaoense*
- Additional Japanese and Chinese white/coloured sister-lineage or within-taxon polymorphism candidates discovered by the atlas

## Repository structure

- `docs/RESEARCH_PLAN.md` — aims, hypotheses, analyses and decision rules
- `data/schema/flower_colour_records.csv` — observation-level flower-colour schema
- `data/schema/taxon_transition_candidates.csv` — transition-screening schema
- `sampling/SAMPLING_DESIGN.md` — field and molecular sampling logic
- `analysis/validate_colour_atlas.py` — atlas schema/QC validator
- `molecular/` — pigment, RNA-seq and genomic workflows
- `manuscript/` — Chapter 2 manuscript materials

## First executable milestone

Create a vetted East Asian *Cirsium* table in which every flower-colour claim has taxonomic, geographic and evidence provenance. The first analysis should estimate:

- the number of supported independent white-flower origins;
- the distribution of white/coloured polymorphism within lineages;
- candidate coloured → white → coloured reversals;
- the 3–5 best replicated systems for mechanistic follow-up.

No WGS cohort should be finalized before this transition screen is complete.
