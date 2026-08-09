# Preliminary hypotheses from existing data only

Date: 2026-08-09

This note deliberately excludes any inference that requires new field, RAD-seq, RNA-seq or pigment data. It asks what can already be said from published nuclear phylogenies plus source-backed flower-colour states.

## 1. Leading hypothesis: repeated white-flower evolution

Current source-backed white states occur in multiple, phylogenetically separated East Asian *Cirsium* systems:

- Arenicola: *C. brevicaule* (white) vs *C. irumtiense* (bluish-purple).
- Sinocirsium: var. *albescens* (fixed white) and var. *takaoense* (white + bluish-purple polymorphism), with coloured Taiwanese relatives.
- Nipponocirsium: *C. kawakamii* (white) vs *C. tatakaense* and *C. pengii* (bluish-purple).
- Japan: *C. pendulum* and *C. sieboldii* each have documented white-flowered forms within otherwise coloured species.

Because these white states occur in different nuclear-resolved lineages and also recur within species, a single ancient white origin is currently a less economical working model than repeated loss/suppression of anthocyanin pigmentation. This remains a hypothesis until the complete East Asian topology and colour atlas are analysed formally.

### Prediction P1
Formal ancestral-state reconstruction on a complete nuclear topology will infer >1 independent transition into a white state under reasonable coding schemes.

## 2. Strongest directional white-loss replicate: Taiwanese Nipponocirsium

Published phylotranscriptomics places *C. pengii* as basal in the Taiwanese Nipponocirsium clade, with *C. kawakamii* and *C. tatakaense* more closely related. Corolla states are bluish-purple in *C. pengii* and *C. tatakaense* but white in *C. kawakamii*.

Given this topology and the flanking coloured states, an independent transition to white on the *C. kawakamii* lineage is currently the simplest working hypothesis. This is stronger than the Arenicola pair because the Nipponocirsium system has an internal coloured reference on both sides of the relevant split.

### Prediction P2
*C. kawakamii* should show a white-flower molecular change not shared by both coloured Taiwanese relatives. If white evolution is regulatory and repeated, the affected node may nevertheless be homologous to that in other white lineages.

## 3. Highest-information mechanistic systems: within-lineage polymorphisms

White/coloured polymorphism within var. *takaoense*, *C. pendulum* and *C. sieboldii* provides a stronger causal design than interspecific comparisons because much of the background genomic divergence is reduced.

### Prediction P3a
If colour polymorphism is controlled by a small number of regulatory changes, white and coloured individuals within the same lineage should show stronger association around anthocyanin regulatory loci than across the genomic background.

### Prediction P3b
If the same regulatory node is repeatedly used, orthologous MYB/bHLH/WD40 or cis-regulatory modules should recur across at least two independent systems even if the exact nucleotide mutations differ.

## 4. Regain/reactivation remains unproven

Current data do not yet demonstrate a coloured lineage derived from a securely reconstructed white ancestor after excluding ancestral polymorphism and introgression.

The best present regain candidate is the white/bluish-purple polymorphism in var. *takaoense*, because var. *albescens* is a fixed-white close relative and the white morph is phylogenetically embedded in the same lineage as the bluish-purple morph. However, current published work explicitly leaves introgression, parallel mutation and ecological selection as alternatives.

The Arenicola pair (*C. brevicaule* white / *C. irumtiense* coloured) is also directionally ambiguous without denser flanking taxa and population history.

### Prediction P4
A true regain case should satisfy all of the following:
1. nuclear ancestral-state reconstruction supports a white ancestor/intermediate;
2. population history does not better support introgression of a coloured allele;
3. the white lineage retains an intact anthocyanin pathway;
4. the coloured lineage restores expression/function of that retained pathway.

Until then, use `candidate regain` rather than `reactivation` as a result label.

## 5. Alternative hypothesis: ancestral colour polymorphism + lineage sorting

The Taiwanese *C. japonicum* complex shows reticulation / incomplete-lineage-sorting signals and flower colour does not map perfectly onto lineage boundaries. Therefore some apparent repeated white/coloured transitions may be persistence and sorting of an ancestral polymorphism rather than repeated de novo mutation.

### Prediction P5
If ancestral polymorphism is important, colour-associated haplotypes should predate some species/population splits and may be shared across sister lineages without genome-wide introgression.

## 6. Alternative hypothesis: introgression of pigmentation alleles

Young East Asian radiations, known reticulation and overlapping ranges make introgression a serious alternative to both independent mutation and regain.

### Prediction P6
If a coloured or white phenotype was introgressed, the candidate pigment region should show local ancestry discordant with the genome-wide species tree, accompanied by excess allele sharing in D/f-statistics or equivalent network-aware analyses.

## 7. Working hierarchy of hypotheses

Current ranking from existing evidence:

1. **Repeated white-flower evolution / repeated anthocyanin suppression** — leading hypothesis.
2. **Regulatory rather than irreversible structural loss** — biologically plausible and testable, but not yet demonstrated in these focal systems.
3. **Ancestral polymorphism / introgression explains some apparent transitions** — serious competing hypothesis, especially in Taiwan.
4. **True coloured regain/reactivation after a white ancestor** — high-value target but currently not demonstrated.
5. **Single ancient white origin followed by many colour regains** — presently a lower-priority working model because white states are scattered across distinct lineages and within-species polymorphisms recur.

## 8. Analyses that can proceed before new data

Do now:
- complete source-backed East Asian colour-state atlas;
- recover all available modern nuclear tip coverage;
- map known states onto published nuclear topologies;
- Fitch/parsimony transition-count sensitivity analysis with polymorphic tips coded as ambiguous vs population tips;
- stochastic/ML ancestral-state reconstruction once the topology is sufficiently complete;
- topology sensitivity across published nuclear trees;
- identify which missing tip changes the inferred transition count or direction;
- rank sampling by expected information gain.

Blocked pending Issues #2–#6:
- causal molecular mechanism;
- population introgression tests for focal morphs;
- ploidy-aware RAD population history;
- true reactivation claim;
- selective-agent tests.
