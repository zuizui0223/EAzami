# EAzami micro-to-macro hypothesis program — 2026-08-15

## Purpose

This document is the idea layer connecting molecular mechanism to macroevolution. It deliberately separates:

1. **Published conclusions** — results directly established by primary studies.
2. **EAzami meta/reanalysis findings** — patterns, contradictions, identifiability problems, or evidence-structure problems discovered by our own reanalysis of public data.
3. **EAzami hypotheses** — falsifiable hypotheses derived from category 2. These are not copied from other papers' stated future work.

The direction of travel is:

`molecular pathway → regulatory/coding change → population history → lineage transition → reticulation/ploidy → island/regional radiation → macroevolutionary transition and diversification rates`

## I. Published conclusions: what is already known

### PUBL-1. Floral flavonoid machinery exists and is strongly tissue-specific in C. japonicum

A published C. japonicum transcriptome–metabolome study recovered 29 orthologs in phenylpropanoid biosynthesis and found many flavonoid-pathway genes expressed far more strongly in flowers than leaves. This means the EAzami mechanistic question is not merely whether a flavonoid pathway exists. The sharper question is which structural or regulatory nodes differ among white and coloured states.

**Boundary:** this does not identify the causal W/C switch in var. takaoense, Arenicola, C. kawakamii, C. pendulum, or C. sieboldii.

### PUBL-2. East Asian lineages are young and cytogenetically dynamic

Chang et al. 2025 resolves Japanese and Taiwanese Nipponocirsium lineages and documents chromosome-number evolution, including tetraploid states and a diploid C. pengii. This establishes a real cytogenetic dimension to recent lineage formation.

**Boundary:** ploidy/chromosome change is not automatically the cause of flower colour.

### PUBL-3. Island fragmentation, demographic change, genome-size shifts and floral polymorphism coexist in the same young radiation

Chang et al. 2026 resolves Sinocirsium, Arenicola and Nipponocirsium as young Quaternary lineages, reports several independent 2C shifts, and links var. takaoense floral-colour polymorphism experimentally to anthocyanin expression and pollinator preference.

**Boundary:** this does not by itself reconstruct the historical direction of every W↔C transition or show a shared molecular mechanism among independent white lineages.

### PUBL-4. Most sampled Japanese Cirsium belong to one dominant Pleistocene radiation

Moreyra et al. 2025 places 36 of 38 sampled Japanese species in one dominant Japanese radiation and reconstructs separate histories for C. lineare and C. dipsacolepis. The study also reports some phylogenomic incongruence compatible with hybridization and incomplete lineage sorting.

**Boundary:** only one broad analysis directly reconstructs dispersal histories; individual exceptional histories still differ in independent replication strength.

## II. Problems discovered by EAzami meta-analysis/reanalysis

These are the primary generators of new hypotheses.

### M1. Colonization count is not diversification success

EAzami's source-typed Japanese-origin synthesis yields an extremely asymmetric result: 36/38 sampled Japanese species belong to one dominant radiation, while rare secondary/exceptional histories do not show comparable species richness. C. lineare is a replicated phylogenetic exception (3/3 analyses; 2/2 independent high-dimensional data-generation groups), whereas C. dipsacolepis still depends on one high-dimensional group and Arenicola is not currently justified as an extra colonization.

**Problem:** why did one Japanese entry generate most of the extant radiation while other entries did not?

This is a new EAzami macroevolutionary question created by the cross-study synthesis, not a leftover task from Moreyra et al.

### M2. Historical direction can be a topology-identifiability problem

For the six morph-linked var. takaoense samples, EAzami exhaustively enumerated all 945 rooted binary resolutions under a coloured root assumption.

- Published topology: minimum `1 loss + 1 regain`.
- No-regain solution on that topology: +2 additional changes.
- 270/945 topologies require regain.
- 675/945 permit a no-regain optimum.
- All rooted-RF<=2 neighbours of the displayed topology retain regain support.
- BP monophyly strongly enriches regain-compatible histories; W monophyly does not require regain.

**Problem:** molecular assays alone cannot rescue an historical claim if the genealogy that defines the ancestral state is unstable. Topology uncertainty must be propagated into molecular interpretation.

### M3. One-state-per-species coding erases recent evolution

EAzami's preliminary Fitch screen showed that collapsing W/C-polymorphic var. takaoense into one ambiguous species tip requires fewer minimum transitions than keeping white and coloured sample/population states separate. The same conceptual risk applies to documented polymorphic Japanese systems such as C. pendulum and C. sieboldii.

**Problem:** conventional species-level trait matrices may systematically underestimate transition rate and recent reversibility in young radiations.

### M4. Paper count is not replication count

EAzami's accession audit collapsed samples reused across Chang 2025/2026 and identified a public-read pseudoreplicate candidate. The accepted public nuclear baseline therefore became 294 biological tips / 295 SRRs rather than the earlier 302/303 arithmetic.

**Problem:** a macro meta-analysis can become overconfident if it counts publications, accession rows, or reused data as independent biological evidence.

### M5. Repeated phenotype is better resolved than repeated mechanism

The source-backed colour atlas contains white and W/C-polymorphic states in multiple separated nuclear contexts, including Arenicola, Sinocirsium and Nipponocirsium. The macro phenotype therefore clearly recurs more broadly than the causal molecular mechanism has been resolved.

**Problem:** 'repeated white evolution' can mean repeated use of the same mutation, repeated use of different genes in one pathway, repeated regulatory suppression, ancestral polymorphism, or introgression. Phenotypic convergence and molecular convergence must be measured at different levels.

## III. EAzami hypotheses derived from those problems

### HMM1. Latent-pathway / regulatory reversibility hypothesis

**Derivation:** M2 + M5, informed by the published existence and floral tissue specificity of the C. japonicum flavonoid pathway.

**Hypothesis:** in young East Asian Cirsium radiations, many recent white states are produced by suppression of a retained anthocyanin/flavonoid programme rather than irreversible destruction of the pathway. This makes colour evolution more reversible than a structural-loss model predicts.

**Predictions:**
- recent independent white lineages often retain intact core structural genes;
- regulatory/expression differences recur more often than homologous destructive coding mutations;
- candidate coloured reversals restore use of retained machinery rather than reconstructing the pathway de novo;
- deep independent white lineages may show more heterogeneous molecular routes than within-lineage polymorphisms.

**Falsifier:** replicated recent white lineages show independent irreversible loss of essential core pathway genes with no retained functional route.

### HMM2. Population-aware transition-rate hypothesis

**Derivation:** M2 + M3.

**Hypothesis:** macroevolutionary W↔C transition rates inferred from one-state-per-species matrices are biased downward in young polymorphic radiations.

**Predictions:**
- population/sample-aware coding yields more transitions than species-tip coding;
- added transitions are concentrated near recent branches and polymorphic lineages;
- the difference remains after topology uncertainty is propagated;
- the effect replicates beyond var. takaoense.

**Falsifier:** population-aware coding does not increase transition count/rate after topology weighting, or the effect is unique to one idiosyncratic taxon.

### HMM3. Radiation-success / evolvability hypothesis

**Derivation:** M1 + M4.

**Hypothesis:** colonization opportunity alone does not explain Japanese Cirsium diversity. The lineage that generated the dominant radiation possessed or maintained greater evolvability, expressed through some combination of standing variation, gene-tree discordance/reticulation, genome-size/ploidy dynamics, and ecological trait divergence.

**Predictions:** after controlling for clade age and sampling, the dominant Japanese radiation shows at least one of:
- greater gene-tree discordance/reticulation;
- higher population-aware floral transition density;
- more genome-size/ploidy transitions;
- faster niche or trait divergence;
than secondary Japanese histories such as C. lineare and C. dipsacolepis.

**Falsifier:** secondary histories show comparable evolvability/diversification metrics once age and sampling are controlled, leaving timing/ecological opportunity sufficient.

### HMM4. Reticulation–phenotypic-transition coupling hypothesis

**Derivation:** M1 + M4, with published hybridization/ILS and cytogenetic evidence treated as priors.

**Hypothesis:** genomic discordance is not only a nuisance in the tree. In young radiations it may index a larger pool of standing/introgressed variants on which floral evolution can act. Therefore lineages with more reticulation/discordance should show more population-aware floral-state transitions.

**Predictions:** lineage-level gene-tree discordance, cytonuclear discordance and/or ploidy/genome-size shifts positively covary with flower-colour transition density after clade-age and sampling controls.

**Falsifier:** no positive coupling appears across supported topology ensembles and leave-one-clade-out analyses.

### HMM5. Phenotypic convergence / molecular heterogeneity hypothesis

**Derivation:** M5.

**Hypothesis:** independent white phenotypes converge most strongly at phenotype and biochemical-pathway level, less strongly at regulatory-module/gene level, and least strongly at exact nucleotide level.

**Prediction:** a cross-system causal catalogue will show increasing convergence as molecular resolution is coarsened from nucleotide → gene → module → pathway → phenotype.

**Falsifier:** the same homologous gene/mutation class repeatedly explains most independent white systems.

## IV. Existing-data macro meta-analysis to run before new sampling

### Analysis A — population-aware colour-history sensitivity

Run identical topology ensembles with:
1. fixed species states;
2. polymorphic species states;
3. population/sample states.

Report transition counts, direction, branch depth and uncertainty side by side.

### Analysis B — radiation asymmetry

When the accepted 294/296 tree is available, compare the dominant Japanese radiation with C. lineare and C. dipsacolepis using descendant richness, branch structure, gene-tree discordance, reduced-network support, ploidy/genome-size changes, trait transitions and public-occurrence niche divergence.

### Analysis C — discordance × transition density

Build an East Asian lineage table with:
- lineage/clade age;
- sampled richness;
- gene-tree concordance/discordance proxy;
- nuclear–plastid discordance;
- ploidy/genome-size shifts;
- population-aware W↔C transition density.

Use age/sampling-aware regression and leave-one-clade-out sensitivity.

### Analysis D — molecular convergence hierarchy

For each independent white system, score causal evidence at five levels:
1. exact nucleotide;
2. gene;
3. regulatory module;
4. pathway;
5. phenotype.

Keep `unknown` as unknown; leaf non-expression is not deletion.

## V. What the 294→296 tree is for now

Issue #18 no longer ends at 'build a bigger tree'. Its downstream scientific role is to:

- determine whether the 36/38 dominant-radiation pattern remains stable;
- verify C. lineare and C. dipsacolepis exception placement;
- test whether Arenicola creates an additional colonization history;
- supply branch lengths and topology ensembles for HMM2;
- supply the clade structure needed for HMM3/HMM4;
- identify the continental branch where new China sampling would have maximum hypothesis-discrimination value.

## VI. Claim discipline

Use these labels explicitly:

- `published_conclusion`
- `EAzami_reanalysis_result`
- `EAzami_meta_problem`
- `EAzami_hypothesis`
- `unresolved`

Never write an EAzami hypothesis as if it had already been demonstrated. Never promote another paper's Discussion/future-work sentence to an EAzami hypothesis unless an EAzami result independently generates the same prediction.

## Linked execution issues

- #18 maximum public nuclear tree
- #20 micro-to-macro synthesis
- #21 macro meta-analysis
- #22 molecular bridge meta-analysis
- existing mechanism/population issues #2–#10 and transcriptome issues #14/#17
