# Robust recurrence but uncertain localization of capitulum trait evolution in a young thistle radiation

**Target journal:** *Journal of Evolutionary Biology* — Research Article

**Manuscript status:** active standalone submission draft v4; scientifically complete, production bundle pending

**Running title:** Recurrence and transition localization

**Word-limit contract:** main text <=7,500 words; abstract <=250 words; 4–10 keywords

## Abstract

Repeated trait states are often counted as evolutionary events even when phylogenetic uncertainty prevents the responsible branches from being identified. We separated recurrence lower bounds from transition-placement identifiability for three capitulum traits in a young Japanese *Cirsium* radiation. Exact-concept descriptions of capitulum orientation, phyllary posture and involucre stickiness were mapped to an independently reconstructed nuclear Comp1061 maximum-likelihood phylogram and 1,000 ultrafast-bootstrap topologies. Orientation required four to six unordered changes, phyllary posture exactly three and stickiness exactly five. Count stability differed sharply from placement stability. No orientation edge was forced in every minimum reconstruction on the maximum-likelihood tree, whereas the terminal phyllary edge leading to one focal concept was forced in 75.4% of bootstrap topologies; ancestral phyllary posture nevertheless remained ambiguous. Pairwise transition-overlap diagnostics did not retain one consistently positive module relationship across branch-length-aware and equal-branch analyses. A separate four-trait, seven-taxon continuous panel supported no corrected topology-robust phylogenetic retention result. Thus, current evidence requires repeated, trait-specific histories but does not require one whole-capitulum common-lability history. These results do not establish independent origins, convergence or adaptation. Instead, the admissible histories prospectively identify phylogenomic samples with maximum discriminatory value, providing a general route from public comparative evidence to outcome-blind own-data sampling.

**Keywords:** *Cirsium*; ancestral-state reconstruction; capitulum; mosaic evolution; phylogenetic uncertainty; sampling design; trait recurrence

# Introduction

Complex structures combine traits that can share development, genetics and function, yet similarity in the present does not guarantee a common history. Morphological integration and modularity are scale-dependent concepts, and mosaic evolution can distribute change unevenly among components of one structure (Klingenberg, 2014; Goswami et al., 2014; Felice & Goswami, 2018; Zelditch & Goswami, 2021). A comparative analysis therefore needs to distinguish at least two historical properties: how many changes are required by observed states and how confidently those changes can be assigned to branches.

This distinction matters in rapid radiations. Short internodes, incomplete lineage sorting, introgression and uneven taxon coverage can leave several ancestral reconstructions equally compatible with the observations. A minimum parsimony count is then a topology-conditioned lower bound. It is not automatically a count of independent origins, and stability of the count across bootstrap trees does not guarantee that the same evolutionary event is recovered on those trees. Conversely, uncertain placement need not erase a robust conclusion that multiple changes are required.

The thistle genus *Cirsium* provides a suitable system. A broad nuclear phylogenomic study recovered rapid Pleistocene radiations, including a large Japanese radiation with substantial gene-tree discordance (Moreyra et al., 2025). The capitulum is assembled from separable traits including its orientation, the posture of surrounding phyllaries and sticky secretions of the involucre. These traits occur together in the present structure but have distinct biological definitions and can be scored from exact-concept taxonomic authorities without deriving one state from another.

We ask whether these capitulum traits require one shared evolutionary history. We first quantify trait-specific recurrence across a nuclear topology ensemble. We then measure whether particular edges are forced to change across all minimum reconstructions, thereby separating recurrence from localization. We next compare transition localization among traits under branch-length-aware and topology-only diagnostics. Finally, we show how the histories that remain admissible can be converted into prospective own-data sampling priorities. This final step is design inference, not a new empirical result: future samples are selected to discriminate histories, while the present paper remains complete under existing public evidence.

# Materials and methods

## Study design and claim hierarchy

The primary estimands were (i) the minimum number of unordered state changes for each trait and (ii) transition-placement identifiability conditional on the admitted phylogenetic ensemble. The secondary estimand was pairwise overlap of inferred transition localization. A small direct continuous-trait panel and existing orientation–niche analyses were retained as bounded diagnostics, not as gates for the primary paper.

We precluded four promotions. Minimum steps were not labelled independent origins; repeated states were not labelled convergence; branch overlap was not labelled developmental or genetic integration; and trait-history patterns were not labelled adaptation or function. Outcomes from future own RAD-seq, phenotyping or experiments cannot retroactively change these definitions.

## Nuclear scaffold and taxon admission

The focal units were Japanese paper taxon concepts from Moreyra et al. (2025). We used an independently reconstructed Comp1061-compatible nuclear phylogram rather than digitizing a published figure. A frozen 241-locus starting set yielded 236 quality-controlled loci, of which 176 were rootable with the safflower outgroup; the concatenated alignment contained 161,654 bp. Maximum-likelihood analysis used IQ-TREE 2, ModelFinder, 1,000 ultrafast-bootstrap replicates and 1,000 SH-aLRT replicates (Kalyaanamoorthy et al., 2017; Hoang et al., 2018; Minh et al., 2020).

Branch lengths are substitutions per site and were not treated as absolute time. Two biological samples assigned to JPN20 were non-monophyletic in the maximum-likelihood tree and all 1,000 bootstrap trees; the concept was not forcibly collapsed. JPN31 had a frozen Japan–Ukraine identity conflict and was excluded from primary trait history. These decisions preceded the present synthesis and were retained unchanged.

## Authority-backed trait states

Orientation, phyllary posture and involucre stickiness were defined by separate biological ontologies. States were admitted only when an exact paper concept could be matched to an authority-quality taxonomic description. Ambiguous descriptions and unresolved concepts remained missing. Continuous image values were not discretized to expand state coverage.

Final coverage was 20 concepts for orientation, ten for phyllary posture and 13 for stickiness. The orientation extension for JPN34 and stickiness extension for JPN24 were frozen before this manuscript reframe. The latter used an exact-concept National Museum of Nature and Science description and did not constitute an individual measurement.

## Recurrence and transition-placement identifiability

For the maximum-likelihood tree and each raw bootstrap topology, we calculated the unordered parsimony minimum for each trait. We also enumerated whether each parent–child edge was forced to change across all minimum-cost ancestral assignments. The fraction of bootstrap trees in which a named terminal edge was forced quantified placement concentration. Root-state sets and ambiguity were reported separately.

The recurrence statistic answers how many changes are minimally required on a given topology. The forced-edge statistic answers whether every equally parsimonious reconstruction assigns a change to a particular edge. Neither statistic estimates transition direction, homology, selective cause or a rate per unit time.

## Module-overlap diagnostics

An equal-rates Mk diagnostic on the maximum-likelihood phylogram estimated branch-wise transition probability and excess over the branch prior. Spearman correlations summarized pairwise overlap for orientation–phyllary, orientation–stickiness and phyllary–stickiness. A topology-only sensitivity repeated the comparison over bootstrap trees after setting every non-root branch length to one. We required qualitative agreement across these layers before describing a shared module history. Saturation warnings and negative results were retained.

## Independent continuous and niche diagnostics

An EAzami-owned registry contained 45 direct authority or public-source records: 35 scalar values and ten ranges retained as context only. Four directly measured traits—capitulum length, capitulum width, phyllary length and phyllary protrusion—covered the same seven East Asian taxa. For every trait on six AU-nonrejected topologies, we calculated the correlation between patristic distance and absolute trait difference, enumerated all 7! label permutations, and applied Benjamini–Hochberg correction across four traits within topology. The fixed rule required a corrected positive result on all six topologies. This source- and lineage-clustered panel could not be transferred to the Japanese radiation.

Existing six-topology orientation–niche PGLS and branchwise niche-concordance results were audited without retuning. They were used only to bound environmental interpretation because their focal sample sizes were small and the branchwise producer remained unrecovered.

## Prospective sampling design

We converted inferential uncertainty into an outcome-blind Chapter 3 priority table. A sample was prioritized when an admitted own topology or same-individual phenotype could distinguish two or more histories still compatible with Chapter 2. Every priority included a predeclared falsifier, required linked measurements, and rights/conservation gates.

The proposed all-Japan same-library RAD-seq product is a topology/network sensitivity, not an unconditional replacement species tree. Cross-species admission requires shared-locus, replicate-concordance, ploidy and reticulation gates. If these fail, inference is restricted to population ancestry or within-cytotype comparisons, while the Comp1061 target-capture framework remains the species scaffold.

# Results

## All three traits require repeated changes

Orientation required six changes on the maximum-likelihood tree and four to six changes across 1,000 bootstrap topologies (median five). Its minimum root state was upward/erect across the bootstrap ensemble. Phyllary posture required exactly three changes on the maximum-likelihood tree and every bootstrap topology, but its minimum root set contained ascending, recurved and spreading postures. Stickiness, after the JPN24 authority extension, required exactly five changes on all 1,000 topologies and had a sticky maximum-likelihood root state.

Thus, repeated changes are not a peculiarity of one capitulum ontology. Nevertheless, the different counts do not indicate different evolutionary rates because the tree is not dated, coverage differs among traits and the statistics are lower bounds.

## Stable recurrence does not imply stable placement

No orientation edge was individually forced across every minimum reconstruction on the maximum-likelihood tree. JPN36 was the most frequently forced terminal orientation edge across bootstrap topologies, but its fraction was only 0.201. In contrast, the JPN36 terminal phyllary edge was forced in 0.754 of bootstrap trees. This concentrated placement coexisted with uncertainty in ancestral phyllary posture. In the pre-extension stickiness placement audit, the JPN06 and JPN36 terminal fractions were 0.67 and 0.40, respectively; the JPN24 extension subsequently stabilized the total count at five but was not used to claim every placement had become known.

The comparisons therefore reveal two independent uncertainty axes. Orientation has a clear recurrence lower bound but weak event localization. Phyllary posture has a stable count and one comparatively concentrated terminal placement, yet an ambiguous root. Stickiness has a stable final count and only partial placement information.

## The data do not require one common-lability history

On the branch-length-aware maximum-likelihood tree, orientation–phyllary, orientation–stickiness and phyllary–stickiness transition-excess correlations were 0.368, 0.244 and 0.041. Only the orientation–stickiness diagnostic had a small stratified one-sided probability, but the stickiness model was saturation-prone. The equal-branch bootstrap diagnostic did not preserve this pattern: median correlations were negative for orientation–phyllary and orientation–stickiness and positive for phyllary–stickiness, with no module pair consistently positive across both treatments.

The simple alternative in which the whole capitulum shares one common lability history is therefore not supported. This result does not demonstrate that the traits are evolutionarily independent or that they form separate genetic or developmental modules.

## Continuous and environmental layers remain bounded diagnostics

None of the four direct continuous traits passed the corrected all-six-topology retention rule. Phyllary protrusion was positive on all six topologies (rho 0.329–0.363), positive in every leave-one-out case and had a descriptive Pagel lambda estimate of one. Its exact positive-tail probabilities were 0.067–0.083 and corrected q-values were 0.269–0.331, so it remained a measurement-priority hint rather than support.

The nine-taxon orientation–niche PGLS supported no climate axis. BIO15 was borderline across six topologies (P=0.0505–0.0524). Existing branchwise permutation probabilities were 0.094–0.124 for BIO15 and 0.108–0.136 for BIO1. These results do not establish climate-associated transition recurrence and were not required to complete the primary historical argument.

## Historical uncertainty identifies prospective samples

The highest-information Chapter 3 test is JPN36 phyllary posture: an own nuclear topology ensemble can directly test whether the current 0.754 terminal-placement concentration persists. The second is the JPN06–JPN15 stickiness contrast. These nonsticky and sticky concepts are sisters with 100/100 support on the canonical maximum-likelihood tree; population-aware own data can test whether that ancestry match survives topology and network sensitivities. The species contrast alone remains non-causal.

Orientation requires broad Japan-wide topology discrimination rather than selection of one causal sister pair. Same-individual measurement of all three modules across the genomic panel addresses a different limitation: current authority states are not observations from the sequenced individuals. A final priority, taxon-balanced direct measurement of phyllary protrusion, tests the weak seven-taxon retention hint without treating it as prior support.

# Discussion

## Recurrence and localization are distinct evolutionary properties

Our central result is not simply that capitulum states changed more than once. It is that the certainty of a recurrence lower bound can be substantially greater than certainty about the branches on which changes occurred. Orientation and phyllary posture illustrate the contrast: both require repeated changes, but only the latter contains a strongly concentrated terminal placement. Analyses that report only one reconstructed history or one event count would conceal this difference.

This distinction is broadly relevant to rapid radiations. Bootstrap topologies may preserve a minimum count while redistributing changes among short or discordant branches. Reporting count and placement separately prevents uncertainty in one estimand from either erasing or exaggerating support in the other.

## One present structure need not have one historical trajectory

Orientation, phyllary posture and stickiness jointly form the capitulum, but the current data do not require a shared branch history. That is a bounded rejection of a simple common-lability alternative, not proof of modular evolvability. Developmental integration, genetic covariance and functional coupling are different estimands and require measurements at the individual, population or experimental level (Klingenberg, 2014; Zelditch & Goswami, 2021).

The negative continuous and niche diagnostics sharpen the same boundary. They do not show absence of signal or ecological relevance. Instead, they identify where current taxon balance, direct measurement and reproducibility are insufficient. Retaining those failures avoids constructing a stronger story by switching endpoints after the results are known.

## From comparative uncertainty to own-data design

Comparative studies often end by requesting more taxa. Here, uncertainty specifies which data are valuable and what outcome would matter. JPN36 is prioritized because own topology can falsify a concentrated phyllary placement. JPN06 and JPN15 are prioritized because their current sister relationship makes a state contrast unusually informative, while network analysis can reveal whether that match is misleading. Broad orientation sampling is prioritized because no single edge is currently identifiable.

This is not circular confirmation. Chapter 3 will estimate a different object from independently collected individuals and may revise the exact Chapter 2 histories. Because focal samples were selected from pre-existing uncertainty, later results must be described as targeted resolution or falsification rather than independent replication. The Chapter 2 conclusion survives either outcome: present public evidence requires repeated trait-specific changes and leaves unevenly localized histories.

## Boundaries for phylogenomics and function

A Japan-wide RAD-seq tree is attractive because it supplies geographically verified own material and population replication. Across divergent or mixed-ploidy taxa, however, restriction-site dropout and homeolog handling can create a data-dependent tree. We therefore define the RAD product as a sensitivity phylogeny/network unless homologous-locus and cytotype gates are passed. This prevents a desired technology from becoming an assumed estimand.

Function remains outside the present paper. The JPN36 non-destructive phyllary-access pilot and JPN15 stickiness-neutralization design can test manipulability and later causal pathways, but neither makes a historical transition adaptive. Mechanism and fitness require their own shams, allocation rules, endpoints and conservation authorizations.

# Conclusion

Authority-backed capitulum traits require repeated but trait-specific changes in a young Japanese *Cirsium* radiation. Recurrence lower bounds can be robust while transition locations remain uncertain, and no module pair currently supports one shared history across complementary branch treatments. The result is a complete, conditional historical inference rather than a claim of convergence or adaptation. By converting remaining histories into falsifiable sampling priorities, the analysis also provides a principled prelude to a Japan-wide own-data phylogenomic chapter without making that future chapter a prerequisite for the present paper.

# References

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
