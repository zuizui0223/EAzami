# Capitulum configuration diversity, minimum change counts and ecological explanatory reach in a young thistle radiation

**Target journal:** *Journal of Evolutionary Biology* — Research Article

**Manuscript status:** active standalone submission draft v4; scientific spine complete, production bundle pending

**Running title:** Capitulum history and ecological reach

**Word-limit contract:** main text <=7,500 words; abstract <=250 words; 4–10 keywords

## Abstract

Rapid radiations can generate alternative configurations of a complex structure even when individual evolutionary events and their ecological interpretation remain difficult to resolve. We quantified configuration diversity, minimum state-change counts, relative lineage-depth and ecological explanatory reach for capitulum traits in Japanese *Cirsium*. Published phylogenomics places 36 of 38 sampled Japanese concepts in one dominant radiation, whose authority-covered subset contains at least three harmonized orientation × stickiness configurations. Orientation required four to six unordered changes, phyllary posture exactly three and stickiness exactly five across an accepted maximum-likelihood/ultrafast-bootstrap topology ensemble. Exact minimum-history envelopes showed unequal relative lineage-depth resolution, with median bootstrap envelopes of 0.795–0.994, 0.695–1.000 and 0.937–0.954, respectively. Ecology was similarly asymmetric. In a frozen nine-taxon East-Asian panel, downward/nodding orientation was associated with higher precipitation seasonality and lower annual mean temperature across all six accepted topologies, and each direction survived 54/54 species leave-one-out fits. Orientation improved held-out climate prediction over a mean-only null but not over phylogeny-only Brownian kriging, so the ecological result remained `unresolved`. Phyllary posture and stickiness were `not_evaluable` because the current climate panel lacked state-diverse overlap. Thus, multiple minimum changes are common across traits, whereas historical resolution and present ecological explanatory reach differ sharply among them.

**Keywords:** *Cirsium*; ancestral-state reconstruction; capitulum; ecological correspondence; mosaic evolution; phylogenetic uncertainty; rapid radiation; trait evolution

# Introduction

Complex structures combine traits that may share development, genetics and function, yet their components need not carry identical evolutionary histories. Morphological integration and modularity are scale-dependent concepts, and mosaic evolution can distribute change unevenly among components of one structure (Klingenberg, 2014; Goswami et al., 2014; Felice & Goswami, 2018; Zelditch & Goswami, 2021). A historical analysis of such a structure should therefore separate at least three questions: how many state changes are minimally required, where in relative lineage depth those changes can occur, and how far independent ecological data can account for the observed state pattern.

This separation is especially important in rapid radiations. Short internodes, incomplete lineage sorting, introgression and uneven taxon coverage can leave several ancestral reconstructions equally compatible with present states. Phylogenetic error can bias inferred transition counts, and probabilistic character mapping was developed in part to represent uncertainty in ancestral states and histories (Bollback, 2006; Duchêne & Lanfear, 2015). Even when a minimum-change count is stable, event placement may remain weakly resolved. Conversely, an ecological association among extant taxa can be directionally stable without adding predictive information beyond shared ancestry. Conflating these quantities risks turning a repeatable pattern into an adaptation claim that the available data do not support.

The thistle genus *Cirsium* provides a useful system for separating these questions. A broad nuclear phylogenomic study recovered rapid Pleistocene radiations, including a large Japanese radiation with substantial gene-tree discordance (Moreyra et al., 2025). The capitulum is assembled from separable traits including its orientation, the posture of surrounding phyllaries and sticky secretions of the involucre. These traits occur together in the present structure but have distinct biological definitions, form several observed configurations, and differ strongly in current public-data coverage.

We therefore ask: **How many state changes are minimally required in constituent capitulum traits, at what relative lineage depth can those minimum histories occur, and how far can existing ecological data explain the observed trait states after accounting for phylogeny?** We first establish radiation membership and observed configuration diversity. We then quantify trait-specific minimum-change counts, exact topology-only depth envelopes and named-edge resolution across an accepted phylogenetic ensemble. We test whether one transition-localization pattern is retained across the three traits. Finally, we quantify ecological explanatory reach as present-day trait–climate correspondence, topology sensitivity, species leave-one-out stability and held-out predictive gain relative to both a naive null and a phylogeny-only baseline. We retain `unresolved` and `not_evaluable` as explicit outcomes. None of these analyses establishes independent origins, convergence, adaptation or historical ecological causation.

# Materials and methods

## Study design and claim hierarchy

The active main text contains five result groups only: (1) radiation context and observed capitulum configurations, (2) trait-specific minimum-change burdens, (3) relative lineage-depth and named-edge resolution, (4) the cross-trait shared-localization boundary, and (5) ecological explanatory reach. A separate species-tip compression audit remains a Supporting Information resolution check.

The historical estimands and ecological estimands were intentionally distinct. Minimum steps were not labelled independent origins; similar tip states were not labelled convergence; shared or non-shared branch localization was not labelled developmental or genetic integration; and ecological correspondence was not labelled adaptation or selective cause. `not_evaluable` denotes insufficient state × data overlap and cannot be rewritten as absence of an ecological relationship.

## Nuclear scaffold and taxon admission

The focal units were Japanese paper taxon concepts from Moreyra et al. (2025). We used an independently reconstructed Comp1061-compatible nuclear phylogram rather than digitizing a published figure. A frozen 241-locus starting set yielded 236 quality-controlled loci, of which 176 were rootable with the safflower outgroup; the concatenated alignment contained 161,654 bp. Maximum-likelihood analysis used IQ-TREE 2, ModelFinder, 1,000 ultrafast-bootstrap replicates and 1,000 SH-aLRT replicates (Kalyaanamoorthy et al., 2017; Hoang et al., 2018; Minh et al., 2020).

Branch lengths are substitutions per site and were not treated as absolute time. Two biological samples assigned to JPN20 were non-monophyletic in the maximum-likelihood tree and all 1,000 bootstrap trees; the concept was not forcibly collapsed. JPN31 had a frozen Japan–Ukraine identity conflict and was excluded from primary trait history. These decisions preceded the present synthesis and were retained unchanged.

A separate preregistered local-topology sensitivity compared nine candidate arrangements around two uncertain relationships. Six candidates were not rejected by the AU test; the highest-likelihood candidate was retained as the maximum-likelihood reference but was not treated as uniquely true. Ecology analyses propagated these six optimized branch-length topologies.

## Authority-backed trait states

Orientation, phyllary posture and involucre stickiness were defined by separate biological ontologies. States were admitted only when an exact paper concept could be matched to an authority-quality taxonomic description. Ambiguous descriptions and unresolved concepts remained missing. Continuous image values were not discretized to expand state coverage.

Final historical coverage was 20 concepts for orientation, ten for phyllary posture and 13 for stickiness. These are exactly three completed discrete histories, not the only capitulum traits measured anywhere in the repository. Flower colour lacks a frozen W/C/P ontology linked to the sequenced Japan38 individuals, directly comparable display data cover only five of 38 exact concepts, and cytotype is an explanatory covariate rather than a capitulum trait. None was discretized post hoc to manufacture a fourth history.

## Radiation context and observed configurations

We retained the source-typed published synthesis of Japanese colonization history. Radiation membership was used as historical context rather than as an estimated diversification rate. Within the authority-backed dominant-radiation subset, we enumerated distinct observed orientation × stickiness label combinations. For the harmonized descriptive count, upward/ascending and upward/erect were both treated as upward while the source-level labels remained preserved separately.

## Minimum-change counts and transition-placement identifiability

For the maximum-likelihood tree and each of 1,000 raw bootstrap topologies, we calculated the unordered-parsimony minimum for each trait. We also asked whether each parent–child edge was forced to change across all globally minimum-cost ancestral assignments. The fraction of bootstrap trees in which a named edge was forced quantified placement concentration.

The minimum-change statistic answers how many changes are minimally required on a given topology. The forced-edge statistic asks whether every equally minimal reconstruction assigns a change to a particular edge. Neither statistic estimates transition direction, homology, selective cause or a rate per unit time.

## Relative lineage-depth envelopes

We defined a topology-only coordinate for the depth of each change-bearing edge. For an admitted tree with *N* concept tips and an edge subtending *d* descendant tips, relative lineage-depth was (*N*−*d*)/(*N*−1). A terminal edge therefore equals one; lower values indicate edges subtending broader descendant lineages.

Dynamic programming obtained the exact minimum and maximum mean relative lineage-depth across all globally minimum-cost Sankoff histories, together with exact terminal- and internal-change count envelopes. Equally parsimonious histories were not enumerated, sampled or assigned equal probability. The maximum-likelihood tree and all 1,000 raw bootstrap topologies were evaluated. Because bootstrap trees do not provide admitted absolute times, relative lineage-depth is not an event age, evolutionary rate or calendar time.

## Cross-trait transition-localization diagnostic

An equal-rates Mk diagnostic on the maximum-likelihood phylogram estimated branch-wise transition probability and excess over the branch prior. Spearman correlations summarized pairwise overlap for orientation–phyllary, orientation–stickiness and phyllary–stickiness. A topology-only sensitivity repeated the comparison across bootstrap trees after setting every non-root branch length to one. A pair met the descriptive cross-treatment robustness rule only when branch-aware excess overlap was positive and the fifth percentile of its equal-branch topology distribution was also positive.

## Ecological explanatory reach

We evaluated ecology only where frozen occurrence and state data supplied an estimable comparison. Occurrence records were source-name guarded, spatially thinned, required complete CHELSA climate extraction, and were summarized to taxon-level centroids. The primary admission gate required at least ten independent thinned environment-complete occurrences per taxon. Four CHELSA axes were retained from the frozen screen: annual mean temperature (BIO1), temperature seasonality (BIO4), annual precipitation (BIO12) and precipitation seasonality (BIO15).

The primary orientation panel contained nine taxa, five upward/erect and four downward/nodding. For each of the six AU-nonrejected optimized Comp1061 topologies, we constructed a Brownian shared-path covariance matrix for the nine taxa. Each climate centroid was standardized, and generalized least squares estimated the standardized D-minus-U effect. BIO15 and BIO1 were retained as the primary and secondary ecological axes because they provided the consistent directional lead in the frozen screen; BIO4 and BIO12 remained sensitivity axes.

We quantified robustness in three additional ways. First, species leave-one-out analysis refit the same phylogenetic model after removing each taxon, yielding 54 fits per axis across six topologies. We recorded whether the sign of the D-minus-U effect matched the full-panel sign. Second, an exploratory branchwise diagnostic estimated a symmetric two-state orientation process and Brownian continuous-niche reconstruction on each accepted topology, then compared transition-probability-weighted branch climate shifts against 499 tip-state permutations. Third, we compared held-out climate prediction under three nested information sets: (i) a mean-only null using the training-set mean, (ii) phylogeny-only Brownian conditional prediction with an intercept, and (iii) Brownian conditional prediction with both intercept and orientation state. Positive ΔMSE means the phylogeny+orientation model had lower held-out squared error than the named baseline.

The archived ecological topology bundle did not preserve raw Comp1061 ultrafast-bootstrap trees. We therefore report an ecology-specific raw-bootstrap sign rate as `not_evaluable` rather than substituting the six AU topologies for 1,000 UFBoot replicates. The historical minimum-count and relative-depth analyses remain based on the independent 1,000-topology Japan38 bootstrap ensemble.

For phyllary posture and stickiness, we intersected the frozen n≥10 climate panel with unambiguous authority-backed states. An ecological comparison was admitted only if at least two state classes remained. Mechanisms such as enemy exclusion, wetness protection, pollinator access or production cost were not inferred from climate proxies.

## Supplementary species-tip resolution audit

We retained a frozen audit of four documented white/coloured polymorphic systems to ask whether one species-tip code could represent extant state multiplicity. Nuclear-genealogy consequences were evaluated only where morph-linked samples existed. This analysis is a resolution audit rather than an additional main result.

# Results

## Alternative configurations occur within the dominant radiation

Published phylogenomic evidence placed 36 of 38 sampled Japanese concepts (94.7%) in the dominant radiation. The authority-covered subset contained at least three harmonized orientation × stickiness configurations: downward with nonsticky/nearly nonsticky, upward with nonsticky/nearly nonsticky and upward with sticky. The source ontology retained four named combinations because upward/ascending and upward/erect descriptions were not silently rewritten. Thus, observed capitulum configuration did not map one-to-one onto the broad colonization-history class.

## All three focal traits require multiple minimum changes

Orientation required six changes on the maximum-likelihood tree and four to six unordered changes across 1,000 bootstrap topologies, with a median of five. Phyllary posture exactly three changes were required on the maximum-likelihood tree and all 1,000 bootstrap topologies. Stickiness exactly five changes were required after the JPN24 authority extension on the maximum-likelihood tree and all 1,000 bootstrap topologies.

These are topology-conditioned lower bounds. The different counts cannot be read as different evolutionary rates because the tree is not dated, coverage differs among traits and transition direction is not identified by the minimum-count statistic.

## Minimum histories differ in relative lineage-depth and named-edge resolution

On the maximum-likelihood topology, exact mean relative lineage-depth envelopes were 0.767–1.000 for orientation, 0.695–1.000 for phyllary posture and 0.943–0.954 for stickiness. Across bootstrap topologies, median lower–upper envelopes were 0.795–0.994, 0.695–1.000 and 0.937–0.954; median widths were 0.200, 0.305 and 0.017, respectively. Stickiness therefore had a much tighter admissible depth range than either orientation or phyllary posture.

Named-edge resolution showed the same asymmetry but was not identical to depth resolution. No orientation edge was individually forced on the maximum-likelihood tree; JPN36 was the most frequent focal terminal edge but was forced in only 0.227 of bootstrap topologies. The JPN36 terminal phyllary edge was forced in 0.728. For stickiness, JPN06, JPN36 and JPN30 terminal edges were forced in 0.995, 0.707 and 0.545 of topologies, respectively, and one nine-tip internal edge in 0.681. Every bootstrap topology required at least one terminal and one internal stickiness change in every minimum history. Minimum-count stability, relative event depth and named-edge localization were therefore empirically separable.

A provenance audit showed that the previously quoted 0.201, 0.754, 0.67 and 0.40 localization fractions reproduce on superseded tree run 32845725038, not on the accepted run-329/post-JPN24 state. Those values are audit history only.

## No common transition-localization pattern spans the three traits

On the branch-length-aware maximum-likelihood tree, orientation–phyllary, orientation–stickiness and phyllary–stickiness transition-excess correlations were 0.362, 0.202 and 0.084. Their equal-branch bootstrap medians were −0.059, −0.387 and 0.184, with fifth percentiles of −0.206, −0.392 and −0.073, respectively. Zero of three trait pairs met the cross-treatment robustness rule.

The current data therefore do not require one shared whole-capitulum transition-localization pattern. This is a boundary on a common-lability model, not proof that the traits are evolutionarily independent or separate genetic/developmental modules.

## Ecological explanatory reach is asymmetric among traits

Orientation supplied a stable present-day climate direction but not a complete ecological explanation. Across all six accepted topologies, downward/nodding taxa occurred at higher precipitation seasonality: BIO15 D-minus-U effects ranged from 1.320 to 1.330 SD, with P=0.05054–0.05239. They also occurred at lower annual mean temperature: BIO1 effects ranged from −0.975 to −0.967 SD, with P=0.09604–0.09793. Accepted-topology sign agreement was 6/6 for both axes.

The directions were also insensitive to removal of individual taxa. BIO15 and BIO1 each retained the full-panel sign in 54/54 species leave-one-out fits. The independent branchwise diagnostic had the same direction on all six topologies: U-to-D change probability aligned with a +0.268 SD shift toward higher BIO15 and a −0.199 SD shift toward lower BIO1. However, permutation P ranges were 0.094–0.124 and 0.108–0.136, respectively.

Prediction distinguished ecological correspondence from additional explanatory reach. Relative to a mean-only null, adding phylogeny and orientation improved held-out prediction for both focal axes: BIO15 ΔMSE=+0.224 to +0.230 and BIO1 ΔMSE=+0.364 to +0.370. Yet phylogeny alone performed better than the trait-aware model. Relative to phylogeny-only Brownian kriging, BIO15 ΔMSE was −0.108 to −0.102 and BIO1 ΔMSE was −0.199 to −0.192, where positive values would indicate improvement from adding orientation. Thus, orientation carried a highly stable directional climate correspondence, but the extra trait term did not improve prediction beyond ancestry. We therefore classified orientation as `unresolved`, not as no relationship and not as a supported ecological explanation.

Phyllary posture and stickiness were `not_evaluable` at the same frozen ecological gate. Of the taxa with n≥10 climate occurrences, only two had unambiguous phyllary posture and both were ascending. Only two had evaluable stickiness and both were nonsticky/nearly nonsticky. No state-diverse phylogeny-aware climate contrast was therefore estimable for either trait. Their failure to yield a climate result reflects data overlap, not evidence that ecology is unimportant.

All four audited colour-polymorphic systems in the supplementary resolution analysis contained extant white and coloured states that one species-tip code could not represent separately. Only one system had morph-linked nuclear samples, and there population-aware coding increased the minimum count from one to two. This result reinforces the observation-resolution boundary but is not a replicated rate or ecological result.

# Discussion

## Multiple minimum changes are common, but histories are not equally resolved

The dominant Japanese *Cirsium* radiation contains multiple capitulum configurations, and every focal trait ontology requires more than one minimum state change under every admitted topology. This is a positive historical result even though the exact identity and direction of individual events remain partly unresolved. The data require multiple changes in orientation, phyllary posture and stickiness; they do not establish how many of those changes were independent origins, reversals, retention/sorting of ancestral variation or consequences of introgression.

The exact depth envelopes sharpen this distinction. Stickiness combines an invariant count of five with a narrow relative-depth envelope and several strongly concentrated edges. Phyllary posture combines an invariant count of three with the widest depth envelope. Orientation remains uncertain in both its four-to-six count and event placement. A single reconstructed history would conceal these differences.

## Ecological correspondence is not equivalent to ecological explanation

The orientation result illustrates why ecological explanatory reach should be quantified rather than inferred from an association alone. BIO15 and BIO1 had the same signs on every accepted topology and every species leave-one-out fit. The branchwise diagnostic also pointed in the same directions. By a robustness-only criterion, this pattern would look compelling.

The predictive comparison changes the interpretation. Orientation helped distinguish held-out climates from a mean-only null, but shared ancestry already contained more predictive information; adding orientation to the phylogenetic predictor made held-out prediction worse. This does not make the climate correspondence spurious. Instead, it shows that the present dataset cannot distinguish an ecological contribution from environmental structure already aligned with lineage history. The correct label is therefore `unresolved`.

This distinction matters for claims of adaptation. A topology-stable extant association can be generated by several histories: repeated response to similar environments, phylogenetically structured niche retention, correlated unmeasured traits, or combinations of these processes. Event-specific environmental matching would require better historical niche information or independently replicated lineage contrasts. Fitness consequences would require direct functional measurements. Neither is supplied by the present analysis.

## Ecological explanatory reach differs among capitulum components

The three traits also differ in what existing data can evaluate. Orientation reaches a quantitative climate comparison because state and occurrence coverage overlap across both states. Phyllary posture and stickiness do not. Their `not_evaluable` status is therefore biologically informative about the current evidence architecture: repeated minimum changes can be established before ecological explanation is possible.

This asymmetry prevents a misleading conclusion in which orientation is called climate-associated while phyllary and stickiness are called climate-independent. For phyllary posture, the next informative data are direct posture measurements across state-diverse taxa plus wetness, enemy-access and pollinator-access context. For stickiness, the next informative data must distinguish climate association from enemy exclusion, pollinator cost and production cost. Climate proxies alone cannot identify those mechanisms.

## One present structure need not have one historical or ecological trajectory

Orientation, phyllary posture and stickiness jointly form the capitulum, but Zero of three trait pairs met the cross-treatment rule for a common transition-localization pattern, and their ecological evaluability also differs. The bounded conclusion is therefore that one present structure contains components with unequal recoverable histories and unequal explanatory reach. This is not proof of modular evolvability, developmental independence or different selective agents.

The result nevertheless provides a clean bridge to direct tests. JPN06–JPN15 remains the highest-information stickiness history contrast because JPN06 has a strongly concentrated terminal placement and the two concepts are sisters on the canonical maximum-likelihood tree. JPN36 remains the leading phyllary history target. Orientation requires broader Japan-wide sampling because no one branch is strongly identifiable. These priorities arise from current uncertainty rather than from choosing systems that already fit an adaptive story.

## From Chapter 2 to Chapter 3

Chapter 2 now ends at ecological explanatory reach, not at a list of causal candidates. Existing public data establish minimum-change burdens, relative event-depth resolution and a bounded climate correspondence for orientation. They also state exactly where explanation stops.

Chapter 3 estimates different objects. Same-individual phenotype and genomic data can test whether current species-level state assignments and branch placements survive population resolution and reticulation. Field measurements and manipulations can test orientation-mediated wetting or presentation, phyllary-mediated access, and the competing benefit/null/cost models for stickiness. Those experiments may support or reject particular functions, but they do not retroactively turn the Chapter 2 correlations into causal evidence.

# Conclusion

The dominant young Japanese *Cirsium* radiation contains multiple capitulum configurations and requires multiple minimum changes in orientation, phyllary posture and stickiness. The three traits differ in both historical resolution and ecological explanatory reach. Stickiness has the tightest relative lineage-depth envelope, phyllary posture has a stable count but broad depth ambiguity, and orientation has weaker event localization. Orientation nevertheless shows a topology- and species-LOO-stable association with higher precipitation seasonality and lower annual mean temperature. That trait information improves prediction relative to a mean-only null but not relative to phylogeny-only Brownian kriging, so its ecological explanation remains unresolved. Phyllary posture and stickiness are not evaluable with the current climate/state overlap. The resulting sequence is therefore **minimum change count → relative event depth → ecological explanatory reach → explicit own-data boundary**. No new RAD-seq, phenotype, dated-tree or field result is a submission gate for this manuscript.

# References

Bollback, J. P. (2006). SIMMAP: stochastic character mapping of discrete traits on phylogenies. *BMC Bioinformatics*, 7, 88. https://doi.org/10.1186/1471-2105-7-88

Duchêne, S., & Lanfear, R. (2015). Phylogenetic uncertainty can bias the number of evolutionary transitions estimated from ancestral state reconstruction methods. *Journal of Experimental Zoology Part B: Molecular and Developmental Evolution*, 324, 517–524. https://doi.org/10.1002/jez.b.22638

Felice, R. N., & Goswami, A. (2018). Developmental origins of mosaic evolution in the avian cranium. *Proceedings of the National Academy of Sciences USA*, 115, 555–560. https://doi.org/10.1073/pnas.1716437115

Goswami, A., Smaers, J. B., Soligo, C., & Polly, P. D. (2014). The macroevolutionary consequences of phenotypic integration: from development to deep time. *Philosophical Transactions of the Royal Society B*, 369, 20130254. https://doi.org/10.1098/rstb.2013.0254

Hoang, D. T., Chernomor, O., von Haeseler, A., Minh, B. Q., & Vinh, L. S. (2018). UFBoot2: improving the ultrafast bootstrap approximation. *Molecular Biology and Evolution*, 35, 518–522. https://doi.org/10.1093/molbev/msx281

Kalyaanamoorthy, S., Minh, B. Q., Wong, T. K. F., von Haeseler, A., & Jermiin, L. S. (2017). ModelFinder: fast model selection for accurate phylogenetic estimates. *Nature Methods*, 14, 587–589. https://doi.org/10.1038/nmeth.4285

Klingenberg, C. P. (2014). Studying morphological integration and modularity at multiple levels: concepts and analysis. *Philosophical Transactions of the Royal Society B*, 369, 20130249. https://doi.org/10.1098/rstb.2013.0249

Minh, B. Q., Schmidt, H. A., Chernomor, O., Schrempf, D., Woodhams, M. D., von Haeseler, A., & Lanfear, R. (2020). IQ-TREE 2: new models and efficient methods for phylogenetic inference in the genomic era. *Molecular Biology and Evolution*, 37, 1530–1534. https://doi.org/10.1093/molbev/msaa015

Moreyra, L. D., Susanna, A., Calleja, J. A., Ackerfield, J. R., Arabacı, T., Blanco-Gavaldà, C., Brochmann, C., Dirmenci, T., Fujikawa, K., Galbany-Casals, M., Gao, T., Gizaw, A., Mehregan, I., Vilatersana, R., Viruel, J., Yıldız, B., Leliaert, F., Seregin, A. P., & Roquet, C. (2025). A thorny tale: The origin and diversification of *Cirsium* (Compositae). *Molecular Phylogenetics and Evolution*, 204, 108285. https://doi.org/10.1016/j.ympev.2025.108285

Zelditch, M. L., & Goswami, A. (2021). What does modularity mean? *Evolution & Development*, 23, 377–403. https://doi.org/10.1111/ede.12390

# Submission completion gates

1. Rebuild the four-figure set so Figure 4 reports ecological explanatory reach rather than prospective ecology only.
2. Build the anonymous line-numbered DOCX and separate identifying title page.
3. Complete primary-source reference, data-availability, author-declaration and prohibited-claim audits.
4. Update Supporting Information with the null/phylogeny-only predictive comparison and the phyllary/stickiness `not_evaluable` gates.

No new RAD-seq, phenotype, dated-tree or field result is a submission gate for this manuscript.
