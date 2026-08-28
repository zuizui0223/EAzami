# Capitulum configuration diversity, minimum change counts and uneven event resolution in a young thistle radiation

**Target journal:** *Journal of Evolutionary Biology* — Research Article

**Manuscript status:** active standalone submission draft v4; scientifically complete, production bundle pending

**Running title:** Minimum changes and event resolution

**Word-limit contract:** main text <=7,500 words; abstract <=250 words; 4–10 keywords

## Abstract

Rapid radiations can accumulate alternative configurations of a complex structure even when individual evolutionary events remain difficult to identify. We quantified configuration diversity, minimum state-change counts and event resolution for capitulum traits in Japanese *Cirsium*. Published phylogenomics places 36 of 38 sampled Japanese concepts in one dominant radiation, within which the authority-covered subset contains at least three harmonized orientation × stickiness configurations. Exact-concept states for orientation, phyllary posture and involucre stickiness were mapped to an independently reconstructed nuclear maximum-likelihood phylogram and 1,000 ultrafast-bootstrap topologies. Orientation required four to six unordered changes, phyllary posture exactly three and stickiness exactly five. Exact envelopes over all minimum histories revealed unequal relative lineage-depth resolution: median bootstrap envelopes were 0.795–0.994, 0.695–1.000 and 0.937–0.954, respectively, where one denotes a terminal edge and lower values denote broader descendant lineages. Stickiness required both terminal and internal changes in every bootstrap topology, and the JPN06 terminal edge was forced in 0.995 of them; orientation had no forced maximum-likelihood edge. No trait pair met a cross-treatment shared-localization rule. Thus, the radiation combines configuration diversity with multiple minimally required changes, but the histories differ in how tightly their event depth and branches are resolved. These topology-only depths are not absolute time, independent-origin counts, convergence or adaptation.

**Keywords:** *Cirsium*; ancestral-state reconstruction; capitulum; character evolution; mosaic evolution; phylogenetic uncertainty; rapid radiation

# Introduction

Complex structures combine traits that can share development, genetics and function, yet diversification can generate different combinations of those traits. Morphological integration and modularity are scale-dependent concepts, and mosaic evolution can distribute change unevenly among components of one structure (Klingenberg, 2014; Goswami et al., 2014; Felice & Goswami, 2018; Zelditch & Goswami, 2021). A historical analysis should therefore ask both how many state changes are minimally required and which evolutionary events are actually recoverable.

This distinction matters in rapid radiations. Short internodes, incomplete lineage sorting, introgression and uneven taxon coverage can leave several ancestral reconstructions equally compatible with the observations. Phylogenetic error can bias inferred transition counts, and probabilistic character mapping was developed in part to represent uncertainty in ancestral states and histories (Bollback, 2006; Duchêne & Lanfear, 2015). Yet two empirical properties remain useful even under a bounded parsimony analysis: how stable a minimum-change count is across topologies, and whether any particular edge is required to change across all equally minimal reconstructions. Stable counts need not identify stable events.

The thistle genus *Cirsium* provides a suitable system. A broad nuclear phylogenomic study recovered rapid Pleistocene radiations, including a large Japanese radiation with substantial gene-tree discordance (Moreyra et al., 2025). The capitulum is assembled from separable traits including its orientation, the posture of surrounding phyllaries and sticky secretions of the involucre. These traits occur together in the present structure but have distinct biological definitions and can form several observed configurations within the same radiation.

We ask how many state changes are minimally required in the traits that form alternative capitulum configurations within the dominant Japanese radiation and which inferred event placements remain identifiable. We first establish radiation membership and observed configuration diversity. We then quantify trait-specific minimum-change counts across a nuclear topology ensemble and measure whether particular edges are forced to change across all minimum reconstructions. We compare transition localization among traits under branch-length-aware and topology-only diagnostics and audit whether species-tip compression can hide extant state multiplicity. Finally, we convert the histories that remain admissible into prospective own-data sampling priorities. This last step is design inference, not a new empirical result.

# Materials and methods

## Study design and claim hierarchy

The primary estimands were (i) observed configuration richness in the admitted authority subset, (ii) the minimum number of unordered state changes for each trait and (iii) transition-placement identifiability conditional on the admitted phylogenetic ensemble. Pairwise overlap of inferred transition localization was a secondary boundary test. A separate population-resolution audit assessed whether one-tip coding hid within-species state multiplicity. Continuous-trait, niche and cytotype screens were retained in Supporting Information rather than treated as additional main questions.

We precluded four promotions. Minimum steps were not labelled independent origins; similar tip states were not labelled convergence; branch overlap was not labelled developmental or genetic integration; and trait-history patterns were not labelled adaptation or function. Outcomes from future own RAD-seq, phenotyping or experiments cannot retroactively change these definitions.

## Nuclear scaffold and taxon admission

The focal units were Japanese paper taxon concepts from Moreyra et al. (2025). We used an independently reconstructed Comp1061-compatible nuclear phylogram rather than digitizing a published figure. A frozen 241-locus starting set yielded 236 quality-controlled loci, of which 176 were rootable with the safflower outgroup; the concatenated alignment contained 161,654 bp. Maximum-likelihood analysis used IQ-TREE 2, ModelFinder, 1,000 ultrafast-bootstrap replicates and 1,000 SH-aLRT replicates (Kalyaanamoorthy et al., 2017; Hoang et al., 2018; Minh et al., 2020).

Branch lengths are substitutions per site and were not treated as absolute time. Two biological samples assigned to JPN20 were non-monophyletic in the maximum-likelihood tree and all 1,000 bootstrap trees; the concept was not forcibly collapsed. JPN31 had a frozen Japan–Ukraine identity conflict and was excluded from primary trait history. These decisions preceded the present synthesis and were retained unchanged.

## Authority-backed trait states

Orientation, phyllary posture and involucre stickiness were defined by separate biological ontologies. States were admitted only when an exact paper concept could be matched to an authority-quality taxonomic description. Ambiguous descriptions and unresolved concepts remained missing. Continuous image values were not discretized to expand state coverage.

Final coverage was 20 concepts for orientation, ten for phyllary posture and 13 for stickiness. These are exactly three completed discrete histories, not the only capitulum traits measured anywhere in the repository. Flower colour lacks a frozen W/C/P ontology linked to the sequenced Japan38 individuals, directly comparable display data cover only five of 38 exact concepts, and cytotype is an explanatory covariate rather than a capitulum trait. None was discretized post hoc to manufacture a fourth history. The orientation extension for JPN34 and stickiness extension for JPN24 were frozen before this manuscript reframe. The latter used an exact-concept National Museum of Nature and Science description and did not constitute an individual measurement.

## Radiation context and observed configurations

We retained the source-typed published synthesis of Japanese colonization history. Radiation membership was used as historical context rather than as an estimated diversification rate. Within the authority-backed dominant-radiation subset, we enumerated the distinct observed orientation × stickiness label combinations without treating missing cells as absences or collapsing upward/ascending and upward/erect authority descriptions after inspection.

## Minimum-change counts and transition-placement identifiability

For the maximum-likelihood tree and each raw bootstrap topology, we calculated the unordered parsimony minimum for each trait. We also enumerated whether each parent–child edge was forced to change across all minimum-cost ancestral assignments. The fraction of bootstrap trees in which a named terminal edge was forced quantified placement concentration. Root-state sets and ambiguity were reported separately.

The minimum-change statistic answers how many changes are minimally required on a given topology. The forced-edge statistic answers whether every equally parsimonious reconstruction assigns a change to a particular edge. Neither statistic estimates transition direction, homology, selective cause or a rate per unit time.

## Relative lineage-depth envelopes

We added a topology-only coordinate for the depth of every change-bearing edge. For an admitted tree with *N* concept tips and an edge subtending *d* descendant tips, relative lineage-depth was defined as (*N*−*d*)/(*N*−1). A terminal edge therefore equals one, whereas lower values indicate an edge subtending a broader and relatively deeper descendant lineage. Dynamic programming obtained the exact minimum and maximum mean depth across all globally minimum-cost Sankoff histories, together with exact terminal- and internal-change count envelopes. Equally parsimonious histories were not enumerated, sampled or assigned equal probability.

The maximum-likelihood tree and all 1,000 raw bootstrap topologies were evaluated. Because bootstrap trees do not supply admitted time or substitution lengths, the metric is not absolute time, an event age or an evolutionary rate. The calculation, exact tree and bootstrap hashes, Biopython 1.85 runtime and post-JPN24 trait matrix were frozen before result admission.

A pre-publication provenance audit found that four previously quoted localization fractions (0.201, 0.754, 0.67 and 0.40) reproduced on superseded tree run 32845725038 although the v1 summary labelled them as run 32923076873. We therefore regenerated all placement and depth statistics from the accepted run-329 hashes. The older values are retained only as a reproducible audit and are not treated as current results.

## Module-overlap diagnostics

An equal-rates Mk diagnostic on the maximum-likelihood phylogram estimated branch-wise transition probability and excess over the branch prior. Spearman correlations summarized pairwise overlap for orientation–phyllary, orientation–stickiness and phyllary–stickiness. A topology-only sensitivity repeated the comparison over bootstrap trees after setting every non-root branch length to one. A pair met the descriptive cross-treatment robustness rule only if branch-aware excess overlap was positive and the fifth percentile of its equal-branch topology distribution was also positive. Saturation warnings and negative results were retained.

## Species-tip resolution audit

We retained a frozen audit of four documented white/coloured polymorphic systems. Stage A asked whether one species-tip code could represent the extant state multiplicity. Stage B compared minimum counts only where morph-linked nuclear samples existed. Non-morph-linked sequence accessions were not assigned a colour state, and database non-recovery was not treated as biological absence.

## Prospective sampling design

We converted inferential uncertainty into an outcome-blind Chapter 3 priority table. A sample was prioritized when an admitted own topology or same-individual phenotype could distinguish two or more histories still compatible with Chapter 2. Every priority included a predeclared falsifier, required linked measurements, and rights/conservation gates.

The proposed all-Japan same-library RAD-seq product is a topology/network sensitivity, not an unconditional replacement species tree. Cross-species admission requires shared-locus, replicate-concordance, ploidy and reticulation gates. If these fail, inference is restricted to population ancestry or within-cytotype comparisons, while the Comp1061 target-capture framework remains the species scaffold.

# Results

## Alternative configurations occur within the dominant radiation

Published phylogenomic evidence placed 36 of 38 sampled Japanese concepts (94.7%) in the dominant radiation. After harmonizing upward/ascending and upward/erect as upward for this descriptive count, the authority-backed subset contained at least three orientation × stickiness configurations: downward with nonsticky/nearly nonsticky, upward with nonsticky/nearly nonsticky and upward with sticky. The source ontology retained four named combinations because upward/ascending and upward/erect descriptions were not silently rewritten. The two sampled secondary-history comparators were both upward/erect but differed in stickiness. Thus, observed capitulum configuration did not map one-to-one onto the broad colonization-history class.

## All three traits require multiple minimum changes

Orientation required six changes on the maximum-likelihood tree and four to six changes across 1,000 bootstrap topologies (median five). Its minimum root state was upward/erect across the bootstrap ensemble. Phyllary posture required exactly three changes on the maximum-likelihood tree and every bootstrap topology, but its minimum root set contained ascending, recurved and spreading postures. Stickiness, after the JPN24 authority extension, required exactly five changes on all 1,000 topologies and had a sticky maximum-likelihood root state.

Thus, every focal ontology requires more than one state change on every admitted topology. Nevertheless, the different counts do not indicate different evolutionary rates because the tree is not dated, coverage differs among traits and the statistics are lower bounds.

## Minimum histories differ in relative lineage depth and placement resolution

On the maximum-likelihood topology, the exact mean relative lineage-depth envelopes were 0.767–1.000 for orientation, 0.695–1.000 for phyllary posture and 0.943–0.954 for stickiness. Across bootstrap topologies, the median lower–upper envelopes were 0.795–0.994, 0.695–1.000 and 0.937–0.954; their median widths were 0.200, 0.305 and 0.017, respectively. Thus, the five-change stickiness history was much more tightly constrained in relative depth than either orientation or phyllary posture.

The edge-level result agreed with this contrast. No orientation edge was individually forced on the maximum-likelihood tree; JPN36 was the most frequent terminal edge but occurred in only 0.227 of bootstrap topologies. The JPN36 terminal phyllary edge was forced in 0.728. For stickiness after the JPN24 extension, JPN06, JPN36 and JPN30 terminal edges were forced in 0.995, 0.707 and 0.545 of topologies, and one nine-tip internal edge in 0.681. Every bootstrap topology required at least one terminal and one internal stickiness change in every minimum history. By contrast, a terminal phyllary change was required in 0.734 of topologies but no topology required an internal phyllary change across all minimum histories. Counts, relative event depth and named-edge localization therefore form three separable resolution coordinates.

## No single transition-localization pattern spans the three traits

On the branch-length-aware maximum-likelihood tree, orientation–phyllary, orientation–stickiness and phyllary–stickiness transition-excess correlations were 0.362, 0.202 and 0.084. Their equal-branch bootstrap medians were -0.059, -0.387 and 0.184, and their fifth percentiles were -0.206, -0.392 and -0.073, respectively. Zero of three trait pairs met the cross-treatment robustness rule.

The simple alternative in which the whole capitulum shares one common transition-localization pattern is therefore not supported. This bounds the minimum-change result but is not evidence that the traits are evolutionarily independent or form separate genetic or developmental modules.

## Species-tip compression hides event information

All four audited colour-polymorphic systems contained white and coloured state information that one species-tip code could not represent as separate extant states. Only the *C. japonicum* var. *takaoense* system currently had morph-linked nuclear samples. In that one testable system, population-aware coding increased the minimum count from one to two. The direction is direct but single-system evidence; no replicated transition-rate comparison was possible.

## Event-resolution gaps identify prospective samples

The highest-information focal Chapter 3 history test is the JPN06–JPN15 stickiness contrast. JPN06 is forced as a terminal change in 0.995 of current bootstrap topologies, and these nonsticky and sticky concepts are sisters with 100/100 support on the canonical maximum-likelihood tree. Population-aware own data can test whether both the terminal placement and ancestry match survive topology and network sensitivities. The species contrast alone remains non-causal. JPN36 phyllary posture is the second focal history test because an own topology ensemble can directly test whether its current 0.728 terminal-placement concentration persists; its better non-destructive field feasibility is a separate Chapter 3 execution consideration.

Orientation requires broad Japan-wide topology discrimination rather than selection of one causal sister pair. Same-individual measurement of all three modules across the genomic panel addresses a different limitation: current authority states are not observations from the sequenced individuals. A final priority, taxon-balanced direct measurement of phyllary protrusion, tests the weak seven-taxon retention hint without treating it as prior support.

# Discussion

## Configuration diversity with multiple minimum changes within a rapid radiation

The dominant Japanese radiation contains several observed capitulum configurations, and all three focal trait ontologies require more than one state change under every admitted topology. The positive result is therefore configuration diversity accompanied by non-zero, multiple minimum-change histories in each constituent trait, rather than merely failure to recover one shared history. The present data do not jointly reconstruct configuration transitions and do not show whether the inferred changes reflect independent origins, reversals, sorting of ancestral variation or introgression.

## Minimum-count stability and event resolution are distinct properties

The certainty of a minimum-change count can differ from both relative event-depth resolution and certainty about named branches. Phyllary posture has an invariant count of three but the widest median depth envelope, whereas stickiness combines an invariant count of five with a narrow depth envelope and several concentrated branches. Orientation retains uncertainty in both the count and event depth. Analyses that report only one reconstructed history or one event count would conceal these differences.

This distinction is broadly relevant to rapid radiations. Bootstrap topologies may preserve a minimum count while redistributing changes among short or discordant branches. The population-resolution audit adds a second source of compression: a phylogeny can be fixed while species-tip coding still hides extant states and additional minimum changes. Reporting count stability and event resolution separately prevents uncertainty in one estimand from either erasing or exaggerating support in the other.

We do not propose a new ancestral-state reconstruction algorithm. The general advance is a reporting and study-design framework that treats minimum-count stability, topology-only lineage depth and named-edge localization as separate empirical coordinates, compares them across constituent traits of one biological structure and links each unresolved coordinate to a prospective observation that can falsify it. The narrow mixed internal–terminal stickiness history, invariant but depth-ambiguous phyllary history and weakly localized orientation history occupy distinct regions of this resolution space.

## One present structure need not have one historical trajectory

Orientation, phyllary posture and stickiness jointly form the capitulum, but the current data do not require a shared branch history. That is a bounded rejection of a simple common-lability alternative, not proof of modular evolvability. Developmental integration, genetic covariance and functional coupling are different estimands and require measurements at the individual, population or experimental level (Klingenberg, 2014; Zelditch & Goswami, 2021).

Continuous, niche and cytotype diagnostics are retained in Supporting Information because they bound explanations rather than define the discovery. None licenses a claim that broad climate, ploidy or phylogenetic retention is absent; each instead specifies a measurement or coverage limitation.

The histories nevertheless nominate trait-specific ecological hypotheses. Orientation retains rainfall/wetting, thermal and pollinator-presentation candidates; only BIO15 and BIO1 supply a topology-stable but threshold-unresolved public niche lead. Phyllary posture nominates enemy exclusion, wetness protection and a pollinator-access trade-off. Stickiness retains competing enemy-benefit, null, pollinator-cost and production-cost models. These are prospective causal alternatives, not explanations of the reconstructed events, because no event has an admitted absolute age or linked historical environment.

## From comparative uncertainty to own-data design

Comparative studies often end by requesting more taxa. Here, the observed resolution coordinates specify which data are valuable and what outcome would matter. JPN06 and JPN15 have the strongest focal topology leverage because the current stickiness placement is highly concentrated and their sister relationship creates an ancestry-matched state contrast. JPN36 can falsify a concentrated phyllary placement and supplies the more feasible non-destructive field pilot. Broad orientation sampling is prioritized because no single edge is currently identifiable, and same-individual phenotype sampling addresses species-tip compression.

This is not circular confirmation. Chapter 3 will estimate a different object from independently collected individuals and may revise the exact Chapter 2 histories. Because focal samples were selected from pre-existing uncertainty, later results must be described as targeted resolution or falsification rather than independent replication. The Chapter 2 conclusion survives either outcome: present public evidence requires multiple minimum changes in each trait and leaves their placements unevenly localized.

## Boundaries for phylogenomics and function

A Japan-wide RAD-seq tree is attractive because it supplies geographically verified own material and population replication. Across divergent or mixed-ploidy taxa, however, restriction-site dropout and homeolog handling can create a data-dependent tree. We therefore define the RAD product as a sensitivity phylogeny/network unless homologous-locus and cytotype gates are passed. This prevents a desired technology from becoming an assumed estimand.

Function remains outside the present paper. The JPN36 non-destructive phyllary-access pilot and JPN15 stickiness-neutralization design can test manipulability and later causal pathways, but neither makes a historical transition adaptive. Mechanism and fitness require their own shams, allocation rules, endpoints and conservation authorizations.

# Conclusion

The dominant young Japanese *Cirsium* radiation combines multiple observed capitulum configurations with multiple minimally required changes in orientation, phyllary posture and stickiness. Their histories separate into an invariant and tightly depth-constrained stickiness pattern, an invariant but depth-ambiguous phyllary pattern and a weakly localized orientation pattern; no trait pair met the cross-treatment rule for one common transition-localization pattern. Species-tip compression supplied a second, independently visible limit on event recovery. This is a positive account of configuration diversity, minimum-change burdens and trait-specific historical resolution, not a claim that configurations were independently reassembled, converged or adapted. The remaining admissible histories prospectively define the own genomic and same-individual phenotype samples required in the next chapter.

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

1. Freeze the revised four-figure set and alternative text against the v4 result registry.
2. Build the anonymous line-numbered DOCX and separate identifying title page.
3. Complete primary-source reference, data-availability, author-declaration and prohibited-claim audits.

No new RAD-seq, phenotype, dated-tree or field result is a submission gate for this manuscript.
