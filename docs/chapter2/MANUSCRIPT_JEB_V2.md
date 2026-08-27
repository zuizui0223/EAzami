# Coordinated evolutionary change without a conserved phenotypic syndrome in a rapid thistle radiation

**Target journal:** *Journal of Evolutionary Biology* — Research Article  
**Manuscript status:** active submission draft v2; numerical results frozen to the Chapter-2 evidence branch  
**Running title:** Multidimensional capitulum evolution in *Cirsium*

## Abstract

Complex phenotypes are often characterized by present-day integration, but covariance among traits does not reveal whether their states remain conserved or whether different traits change during the same evolutionary episodes. We separated these historical properties in the capitulum of Japanese *Cirsium*, a lineage dominated by a rapid Pleistocene radiation. A continuous phenotype ontology derived from georeferenced photographs was linked by exact taxon concepts to an independently reconstructed nuclear phylogeny. Eight continuous dimensions spanning capitulum orientation, corolla colour and capitulum shape showed no family-level robust phylogenetic state structure; Pagel's lambda estimates were zero for all scalar dimensions. Independently source-coded discrete traits nevertheless required repeated changes: orientation required 4–6 changes across bootstrap topologies, phyllary posture three, and stickiness five. In contrast to weak state conservation, reconstructed continuous change magnitudes were positively coordinated across traits on the maximum-likelihood phylogram (mean pairwise Spearman rho = 0.408, permutation P = 0.00010). Global coordination remained positive in all 1,000 equal-branch bootstrap topologies (median rho = 0.141; fifth percentile = 0.119), whereas preferential within-module coordination was not topology-robust. Discrete transition overlap was likewise topology-sensitive. Thus, a complex reproductive phenotype can undergo coordinated evolutionary remodeling without preserving a conserved multivariate syndrome.

**Keywords:** *Cirsium*; capitulum; morphological evolution; phenotypic integration; phylogenetic signal; phenomics; rapid radiation; evolutionary lability

---

# Introduction

Organisms evolve as multivariate phenotypes. Traits within a complex structure may covary because they share development, genetics, function or selection, and such integration can channel evolutionary change. Conversely, modular organization can allow subsets of a phenotype to vary with partial independence. These ideas have motivated extensive work on phenotypic integration and modularity, from quantitative-genetic analyses of flowers to comparative studies of skulls and other complex structures (Bissell & Diggle, 2010; Klingenberg, 2014; Goswami et al., 2014). Yet the word *modularity* is used for several distinct properties, and conclusions depend strongly on which property is measured (Zelditch & Goswami, 2021).

One distinction is especially important for macroevolution. Present-day covariance is not itself an evolutionary history. A set of traits may covary strongly among extant observations while retaining little phylogenetic signal, and traits that end in very different states may nevertheless have undergone large changes during the same evolutionary intervals. Conversely, similar states among relatives do not imply that all dimensions of a complex phenotype have changed together. Work on morphological integration has shown that integration can shape directions of disparity without mapping simply onto evolutionary rate, while studies of mosaic evolution have demonstrated that component regions can differ in their historical dynamics (Goswami et al., 2014; Felice & Goswami, 2018). Floral systems add another layer because reiterated plant structures can vary substantially within individuals and populations as well as among species (Diggle, 2014).

We therefore distinguish three historical properties of a multivariate phenotype. **State conservation** asks whether relatives retain similar continuous trait values. **Recurrence** asks how many changes are required to explain independently defined states across a phylogeny. **Change localization** asks whether relatively large evolutionary changes in different continuous dimensions occur on the same branches. These properties can agree, but they need not. A conserved multivariate syndrome predicts state similarity across relatives and potentially shared changes, whereas a fully modular history predicts substantial independence among components. An intermediate possibility is also plausible: multiple dimensions may be remodeled during the same evolutionary episodes even when descendant trait states are not conserved.

Rapid radiations provide a stringent setting for distinguishing these alternatives because large phenotypic disparity is compressed into a shallow lineage history. The thistle genus *Cirsium* provides such a system. A recent phylogenomic analysis of 299 plants from 251 taxa using 350 nuclear loci reconstructed rapid Pleistocene radiations in Japan and North America (Moreyra et al., 2025). In Japan, 36 of 38 sampled taxon concepts belonged to one dominant radiation associated with a continental dispersal into the archipelago around the beginning of the Pleistocene, while rare sampled lineages represented separate historical arrivals. The same study reported phylogenomic incongruence consistent with processes including hybridization and incomplete lineage sorting, making topology uncertainty important when testing trait-history hypotheses.

A companion phenomic programme made it possible to ask this historical question without reducing capitulum diversity to coarse floral categories or one species-level trait value. Georeferenced photographs were processed into repeated continuous measurements of orientation, corolla colour, capitulum shape and candidate involucral geometry. The present-day capitulum was multidimensional, with stronger registered measurement-module organization within taxa than among taxa and only partial correspondence between within- and among-taxon association matrices. Those results concern the present phenotypic field. Here we use the **same phenotype ontology** on an orthogonal axis: evolutionary history. Importantly, we do not restrict historical analysis to traits that were environmentally associated in the companion spatial analysis, and a trait does not require a validated ecological function before entering the phylogenetic analysis.

We tested five linked questions. **First**, do continuous capitulum dimensions retain phylogenetic state structure? **Second**, do independently source-coded discrete capitulum states require repeated changes? **Third**, are magnitudes of continuous phenotypic change concentrated on the same branches even when tip states are weakly conserved? **Fourth**, if change is coordinated, is it preferentially coordinated within phenotype modules defined independently from present-day measurements? **Fifth**, do apparent shared histories survive phylogenetic-topology uncertainty? Together these questions distinguish a conserved phenotypic syndrome, fully independent component histories and coordinated evolutionary remodeling without stable conservation of trait states.

# Materials and methods

## Study system and historical context

The focal taxon panel was derived from the 38 Japanese taxon concepts included by Moreyra et al. (2025). Their broader phylogenomic and biogeographic results were used as evolutionary context, including the inference that 36 of the 38 sampled Japanese concepts belong to one dominant Pleistocene radiation. We did not digitize a published phylogeny figure or treat that figure as the analytical tree.

For focal trait-history analyses we used an independently reconstructed Japan38 Comp1061 compatibility phylogeny. The reconstruction contained 39 focal biological samples corresponding to the 38 paper concepts plus a safflower outgroup. A frozen 241-locus Comp1061 universe yielded 236 quality-controlled nuclear loci, of which 176 were rootable with the outgroup, and a concatenated alignment of 161,654 bp. The maximum-likelihood analysis used IQ-TREE 2 with ModelFinder, 1,000 ultrafast-bootstrap replicates and 1,000 SH-aLRT replicates (Kalyaanamoorthy et al., 2017; Hoang et al., 2018; Minh et al., 2020).

Branch lengths in this compatibility tree are substitutions per site and are not absolute time. One paper concept, JPN_20 (*C. nipponicum* var. *incomptum*), was represented by two biological samples that were non-monophyletic in the maximum-likelihood tree and in 0/1,000 bootstrap trees; those samples were not forcibly collapsed into a single phenotype tip. JPN_31 was excluded from primary phenotype-history inference because a frozen audit identified a conflict between the paper taxon concept and the public-sample identity/locality metadata.

## Recovering continuous phenotype data without recategorization

We reused the frozen continuous-trait output of the companion phenomic analysis rather than assembling a new species-level trait database around the phylogeny. The source dataset contained 46,276 unique strict-spatial image observations and 1,018,072 long-format trait rows. A compute-only bridge matched these observations to Japan38 paper concepts using exact normalized taxon concepts. Botanical author strings were ignored for matching, but infraspecific rank was preserved: a broad species-level image record could not substitute for a named variety or subspecies. No missing phenotype was imputed and no continuous measurement was discretized to increase phylogenetic coverage.

At least one continuous phenotype was recovered for 14 exact Japan38 concepts. Coverage differed strongly between established primary endpoints and newer candidate involucral/armature metrics. Orientation was available for 14 exact concepts overall, eight with at least two observations and six with at least five. Four primary capitulum-shape dimensions each reached 14 concepts overall, ten at >=2 observations and six at >=5. Continuous corolla-colour metrics likewise reached 14 concepts overall, ten at >=2 and six at >=5. Candidate involucre and armature endpoints reached only five exact concepts overall and two at >=2 observations; these were retained as an explicit coverage result rather than promoted into a radiation-wide continuous history.

The primary continuous historical analysis therefore used eight inferential units: vertical orientation angle; CIELAB lightness; CIELAB chroma; circular hue represented jointly by sine and cosine; capitulum-outline aspect ratio; outline circularity; outline solidity; and width-profile coefficient of variation. The main evidence threshold required at least two frozen observations per exact taxon-concept endpoint. A >=5-observation panel provided a high-depth sensitivity.

## Continuous trait-state phylogenetic structure

For each scalar continuous unit represented by at least six exact concepts, the compatibility tree was pruned to eligible concepts. We estimated Pagel's lambda under a Brownian covariance model (Pagel, 1999). Because branch lengths were substitutions per site, lambda was interpreted only as a phylogenetic-structure diagnostic.

We also quantified the association between phylogenetic and phenotypic distance. For each scalar unit we calculated Spearman correlation between pairwise patristic distance and absolute pairwise phenotype difference. Phenotype labels were permuted across tips to obtain positive, negative and two-sided null distributions. All label permutations were enumerated for panels of eight or fewer concepts; larger panels used Monte Carlo label permutations. The two-sided test defined the primary inference family, and Benjamini-Hochberg correction was applied across the eight primary inferential units separately at each observation threshold. Leave-one-concept-out analyses assessed stability of correlation direction.

Circular hue was never linearized into an arbitrary unwrapped angle. Sine/cosine vectors were normalized, pairwise hue difference was measured as chord distance, and the same patristic-distance label-permutation framework was applied.

## Authority-backed discrete recurrence

Continuous image measurements were not converted into artificial categories to obtain transition counts. Discrete history used a separate source-backed ontology for traits whose biological states were independently defined from botanical authority evidence: capitulum orientation, phyllary posture and involucre stickiness. Missing and ambiguous states remained missing. After the current authority repairs, orientation was resolved for 20 concepts, phyllary posture for ten and stickiness for 13.

For the maximum-likelihood tree and each raw ultrafast-bootstrap topology, we calculated the minimum number of unordered state changes required by observed tip states. These values are topology-conditioned parsimony lower bounds. They do not by themselves count independent origins or adaptive convergence.

A separate equal-rates Mk diagnostic estimated branch-wise transition posteriors for each discrete trait and asked whether traits tended to place transitions on the same branches. The branch-length-aware maximum-likelihood analysis was supplemented by a topology-only sensitivity in which every non-root branch of each raw bootstrap topology was assigned length one. This deliberately removed substitution-length information rather than inventing lengths unavailable in the raw bootstrap trees.

## Continuous branch-wise change localization

State conservation and change localization were analysed separately. The common >=2-observation panel contained eight exact concepts with complete data across all eight primary continuous units. Scalar tip values were standardized by among-tip standard deviation. Under a Brownian covariance model on the maximum-likelihood phylogram, conditional expected internal-node states were reconstructed. For each parent-child branch, scalar change magnitude was the absolute difference between reconstructed states divided by the square root of substitution-length branch length. Circular hue was reconstructed in sine and cosine components, normalized at each node and expressed as parent-child chord distance divided by square-root branch length.

The resulting branch-by-trait matrix contained 14 branches and eight phenotype dimensions. We calculated the Spearman correlation matrix among the eight branch-change vectors. The primary global statistic was the mean of all 28 pairwise correlations. Its null distribution was generated by independently permuting branch values within each phenotype dimension 10,000 times.

To test whether coordinated change followed the present-day measurement modules, we compared mean within-module and between-module branch-change correlations. Module labels were defined independently in the companion phenomic analysis. Significance of the within-minus-between contrast was evaluated using all unique permutations of those module labels across the eight continuous units.

## Topology sensitivity of coordinated continuous change

We preregistered a branch-length-free topology sensitivity before inspecting its outcome. Each of the 1,000 raw ultrafast-bootstrap topologies was pruned to the same eight-concept continuous panel and every non-root branch was assigned length one. Continuous ancestral reconstruction and branch-change correlations were then recalculated.

Global coordination was classified as topology-robust positive only if at least 95% of usable bootstrap topologies had a positive global mean pairwise correlation and the empirical fifth percentile was greater than zero. The same rule was applied independently to the within-minus-between module contrast.

## Absolute-time boundary

We did not transform the compatibility phylogram into a dated trait tree. A prior calibration audit found that published age information could not be mapped to the exact compatibility topology as a defensible multi-anchor calibration. Consequently, all focal conclusions concern phylogenetic structure, recurrence and relative branch localization. We make no claim about absolute transition ages or evolutionary rates per million years.

# Results

## Continuous phenotype recovery supports a primary time-axis panel

The exact-concept bridge recovered continuous phenotype data for 14 Japan38 concepts. Coverage was sufficient for eight primary orientation/colour/shape units but not for candidate continuous involucre/armature endpoints. In the main >=2 panel, orientation included eight concepts and each colour/shape unit included ten. At >=5 observations, all eight units included six concepts. Only five concepts were complete for all 18 frozen endpoints, supporting the endpoint-wise analysis rather than restricting all inference to a five-taxon complete-case matrix.

## Continuous trait states are weakly conserved by phylogenetic relatedness

No primary continuous inferential unit showed significant two-sided phylogenetic structure after correction across the eight-unit family at either evidence-depth threshold. Pagel's lambda maximum-likelihood estimate was zero for every scalar unit at both thresholds.

In the >=2 panel, patristic-distance correlations ranged from weak positive values for orientation (rho = 0.103) and chroma (rho = 0.069) to negative values for several shape dimensions, including outline solidity (rho = -0.437). None passed the corrected two-sided family.

The >=5 panel exposed directional anti-phylogenetic tendencies without supporting a family-level claim. Lightness showed rho = -0.707 with exact two-sided P = 0.0444 and exact negative-tail P = 0.00139, but the two-sided BH-adjusted q was 0.356. Several shape dimensions were also negative and had consistently negative leave-one-out correlations, yet none passed the corrected two-sided family. The supported result is therefore that **none of the eight measured continuous capitulum states shows robust conserved phylogenetic structure in the current exact-concept Japanese panel**.

## Discrete capitulum states require repeated historical changes

Discrete-state analyses gave a complementary result. Orientation required six minimum unordered changes on the maximum-likelihood tree and four to six across 1,000 bootstrap topologies (median five). Phyllary posture required exactly three minimum changes on every bootstrap topology. Stickiness, after the JPN_24 authority repair, was resolved for 13 concepts and required five minimum changes on the maximum-likelihood tree and in all 1,000 bootstrap topologies. These are recurrence lower bounds rather than convergence counts.

## Continuous phenotype changes are coordinated on the maximum-likelihood phylogram

Despite weak conservation of continuous tip states, reconstructed branch-change magnitudes were positively associated across phenotype dimensions on the maximum-likelihood phylogram. The mean of all 28 pairwise Spearman correlations was **0.408006**. Independent branch permutation gave **P = 0.00010**.

Strong associations occurred both within and across present-day measurement modules. Orientation change correlated with lightness change at rho = 0.666 and with width-profile variation at rho = 0.745. Lightness change correlated with both aspect ratio and circularity at rho = 0.771. Among shape dimensions, circularity and solidity were strongly associated (rho = 0.793).

Mean within-module branch-change correlation was 0.495 and mean between-module correlation was 0.367, giving an observed contrast of 0.128. Exact permutation of module labels did not support preferential within-module coordination (P = 0.168). The maximum-likelihood result therefore indicates broad coordinated change rather than coordination confined to the present-day module partition.

## Broad coordinated change survives topology uncertainty and removal of branch-length information

The global pattern remained positive when substitution-length information was removed. On the equal-branch maximum-likelihood topology, mean pairwise branch-change correlation was 0.141. All 1,000 raw bootstrap topologies were usable. Across them, the global mean pairwise correlation had median **0.141287**, fifth percentile **0.118995**, 95th percentile **0.199615**, and was positive in **1,000/1,000** topologies. The global coordinated-change result therefore passed the preregistered topology-robust-positive criterion.

Preferential within-module coordination did not pass the same rule. The within-minus-between contrast had median **0.112435**, but its fifth percentile was **-0.095160** and only **94.6%** of bootstrap topologies were positive. Thus topology uncertainty supports general coordination of continuous remodeling while failing to support a stable module boundary around that coordination.

## Discrete transition overlap is not topology-robust

The latest discrete transition-overlap analysis used all current authority repairs: 20 orientation, ten phyllary and 13 stickiness states. On the substitution-length maximum-likelihood tree, orientation and stickiness had a positive transition-posterior excess association (rho = 0.202, one-sided P = 0.0042), whereas orientation-phyllary excess was weaker (rho = 0.362, P = 0.0894) and phyllary-stickiness excess was small (rho = 0.084, P = 0.2704).

These patterns did not survive the equal-branch bootstrap topology ensemble. Orientation-phyllary overlap had median rho = -0.059 and was positive in 34.9% of usable trees. Orientation-stickiness had median rho = -0.387 and was positive in only 0.9%. Phyllary-stickiness was more often positive (median rho = 0.184; positive in 78.2%), but its fifth percentile remained negative. No discrete pair therefore showed a consistently positive shared-transition history across branch-length-aware and topology-only layers.

# Discussion

## State conservation and change localization are different evolutionary properties

The central result is a mismatch between two properties often compressed into broad discussions of phenotypic integration. Current trait states carried little robust phylogenetic structure, yet the magnitudes of change reconstructed on branches were positively coordinated across phenotype dimensions. The direction of this coordination survived every bootstrap topology after branch lengths were equalized. A lineage's present position on one phenotype axis therefore provides little stable information about its relatives' final states, while branches associated with relatively large change in one dimension tend also to be associated with relatively large change in others.

We interpret this as **coordinated evolutionary remodeling without conserved state integration**. The phrase is deliberately descriptive. It does not imply that the same developmental pathway, genetic architecture or selective pressure caused changes in all traits. It instead distinguishes *where change is concentrated* from *which states are retained*. This distinction is useful because a multivariate phenotype can lose phylogenetic conservatism while still exhibiting historical coupling in the timing or placement of its largest changes.

The magnitude difference between analyses reinforces that caution. Mean coupling was 0.408 on the substitution-length maximum-likelihood phylogram but only 0.141 on the equal-branch topology ensemble. Substitution-length information therefore amplifies the maximum-likelihood pattern. Nevertheless, the equal-branch fifth percentile remained positive and all 1,000 topologies retained a positive global mean, demonstrating that the qualitative signal is not an artefact of one topology or a few unusual branch lengths.

## Coordinated remodeling does not define one fixed evolutionary module partition

The historical coordination was broad rather than confined to the measurement modules identified from present-day phenotypes. On the maximum-likelihood phylogram, within-module correlations exceeded between-module correlations only modestly and the module-label test was nonsignificant. Across bootstrap topologies, the module contrast was usually positive but failed the preregistered robustness rule because its fifth percentile was negative and the fraction positive was 0.946 rather than at least 0.95.

This result argues against equating present-day covariance modules with immutable evolutionary modules. Some cross-module pairs were among the strongest associations, whereas some within-colour relationships were weak or negative. That does not make the present modules biologically meaningless; it means that the partition describing contemporary association structure does not fully delimit the historical localization of change.

This interpretation is consistent with broader work showing that morphological integration can alter evolutionary trajectories without mapping simply onto rate or disparity, and that modularity depends on the level and property being measured (Klingenberg, 2014; Goswami et al., 2014; Zelditch & Goswami, 2021). Our result adds a related distinction: weak conservation of component states can coexist with coordinated branch-localized remodeling.

## Recurrent discrete states do not reduce to one shared transition history

The independently coded discrete layer gives a second reason not to treat the capitulum as one historical state. Orientation, phyllary posture and stickiness all require repeated changes, but their transition-posterior overlap is not stable to topology and branch-length treatment. The strongest example is orientation and stickiness: the substitution-length maximum-likelihood tree yields positive overlap after accounting for branch prior, while the equal-branch bootstrap ensemble yields a strongly negative median association.

The contrast between continuous and discrete analyses is not contradictory. Discrete ontologies ask whether defined state boundaries are crossed. Continuous branch-change analysis retains magnitude information. A branch can remodel several continuous phenotype dimensions without crossing discrete boundaries in all of them, while repeated state changes can occur without implying globally independent underlying continuous dynamics. Using both layers therefore reveals more of the historical architecture than forcing all traits into one data type.

## Rapid radiation provides the historical setting, not an adaptation claim

Japanese *Cirsium* is particularly informative because most sampled taxon concepts fall within one Pleistocene radiation (Moreyra et al., 2025). Substantial phenotypic variation has therefore accumulated over a relatively shallow lineage history. The combined pattern—weak continuous state conservation, repeated discrete changes and topology-robust broad coordination of continuous change—is consistent with extensive reorganization of a complex reproductive structure during rapid lineage diversification.

This paper does not infer adaptive radiation. Rapid lineage accumulation and phenotypic remodeling do not establish ecological causation. The historical pattern defines a stronger target for later ecological work: rather than asking generically whether the whole capitulum is adaptive, one can ask why particular evolutionary episodes involved broad remodeling, which ecological problems were present, and whether different traits contributed equivalent or distinct functions.

## Image phenomics changes what can be asked historically

The historical analysis depended on retaining continuous phenotype information before the phylogenetic analysis. Conventional trait databases often store one species value or a categorical state. Here the same georeferenced image observations used for present-day phenomics could be rejoined to exact phylogenetic taxon concepts, allowing orientation, colour and shape to remain continuous rather than being converted into coarse floral types.

This also exposed where public phenomics currently fails. New continuous involucre and armature metrics had only two exact Japan38 concepts with at least two observations and therefore could not support radiation-wide continuous history. We retained that absence as a measurement result instead of silently substituting broad species identities or invented categories. Authority sources provided an independent route for biologically explicit discrete states, but those states answer a different historical question. The combination of public-image phenomics and authority-coded traits is useful precisely because their inferential targets remain separate.

## Boundaries and next evidence layers

Several boundaries limit interpretation. The compatibility tree is a phylogram, so branch lengths are substitutions per site rather than time. Internal continuous states are Brownian conditional expectations rather than observed ancestors. The strongest multivariate branch-change analysis uses eight exact concepts and 14 branches; topology replication protects against reliance on one tree but does not replace denser taxon coverage. Discrete recurrence counts are parsimony lower bounds and do not distinguish independent origin from ancestral polymorphism, incomplete lineage sorting, introgression, reversal or other reticulate histories. Finally, no image-derived phenotype is promoted to a validated functional trait here.

These limits determine the next evidence layers. Population-level nuclear ancestry linked to matched plastid haplotypes and cytotype information is needed to discriminate origins of repeated states. Functional manipulation linked to effective interaction and reproductive fitness is needed to determine why particular phenotypes matter. Only after independent origin and repeated ecological/functional consequences are established should repeated histories be promoted to convergence or adaptive convergence.

## Relationship to existing meta-analysis and simulation programmes

Two substantial EAzami programmes are retained but intentionally kept outside the focal estimand. First, quantitative syntheses of pollination, reproductive antagonism, display, orientation and demographic transmission belong primarily to the next **phenotype × function/fitness** chapter. They can motivate hypotheses for why historical remodeling occurred, but they are not required to establish the historical pattern.

Second, Azami-compatible v3/v4 simulations address how the **present within- and among-taxon phenotypic field** can arise under different covariance and environmental-process architectures. Those results are therefore routed to Chapter 1 Supplement or the dissertation's structural-methods layer rather than described as evolutionary transition simulations. A future historical simulation would need to condition explicitly on the empirical tree, trait-state history and ecological history before it could test generative evolutionary scenarios.

# Conclusion

By projecting the same continuous capitulum phenotype ontology from spatial phenomics onto a nuclear evolutionary history, we separated conservation of trait states from localization of phenotypic change. Continuous states were weakly structured by relatedness, independently defined discrete states repeatedly changed, and large continuous changes were coordinated across every tested bootstrap topology. Yet that coordination was not robustly confined to present-day modules, and discrete transition overlap did not define one shared history. **A complex reproductive phenotype can therefore undergo coordinated evolutionary remodeling without preserving a conserved phenotypic syndrome.** This result provides a direct bridge from phenotype across space to phenotype through evolutionary history while leaving function, historical origin and adaptation as separately testable questions.

# References

Alcantara, S., de Oliveira, F. B., & Lohmann, L. G. (2013). Phenotypic integration in flowers of neotropical lianas: diversification of form with stasis of underlying patterns. *Journal of Evolutionary Biology*, 26, 2283–2295. https://doi.org/10.1111/jeb.12228

Bissell, E. K., & Diggle, P. K. (2010). Modular genetic architecture of floral morphology in *Nicotiana*: quantitative genetic and comparative phenotypic approaches to floral integration. *Journal of Evolutionary Biology*, 23, 1744–1758. https://doi.org/10.1111/j.1420-9101.2010.02040.x

Diggle, P. K. (2014). Modularity and intra-floral integration in metameric organisms: plants are more than the sum of their parts. *Philosophical Transactions of the Royal Society B*, 369, 20130253. https://doi.org/10.1098/rstb.2013.0253

Felice, R. N., & Goswami, A. (2018). Developmental origins of mosaic evolution in the avian cranium. *Proceedings of the National Academy of Sciences USA*, 115, 555–560. https://doi.org/10.1073/pnas.1716437115

Goswami, A., Smaers, J. B., Soligo, C., & Polly, P. D. (2014). The macroevolutionary consequences of phenotypic integration: from development to deep time. *Philosophical Transactions of the Royal Society B*, 369, 20130254. https://doi.org/10.1098/rstb.2013.0254

Hoang, D. T., Chernomor, O., von Haeseler, A., Minh, B. Q., & Vinh, L. S. (2018). UFBoot2: improving the ultrafast bootstrap approximation. *Molecular Biology and Evolution*, 35, 518–522. https://doi.org/10.1093/molbev/msx281

Kalyaanamoorthy, S., Minh, B. Q., Wong, T. K. F., von Haeseler, A., & Jermiin, L. S. (2017). ModelFinder: fast model selection for accurate phylogenetic estimates. *Nature Methods*, 14, 587–589. https://doi.org/10.1038/nmeth.4285

Klingenberg, C. P. (2014). Studying morphological integration and modularity at multiple levels: concepts and analysis. *Philosophical Transactions of the Royal Society B*, 369, 20130249. https://doi.org/10.1098/rstb.2013.0249

Minh, B. Q., Schmidt, H. A., Chernomor, O., Schrempf, D., Woodhams, M. D., von Haeseler, A., & Lanfear, R. (2020). IQ-TREE 2: new models and efficient methods for phylogenetic inference in the genomic era. *Molecular Biology and Evolution*, 37, 1530–1534. https://doi.org/10.1093/molbev/msaa015

Moreyra, L. D., et al. (2025). A thorny tale: The origin and diversification of *Cirsium* (Compositae). *Molecular Phylogenetics and Evolution*, 204, 108285. https://doi.org/10.1016/j.ympev.2025.108285

Pagel, M. (1999). Inferring the historical patterns of biological evolution. *Nature*, 401, 877–884. https://doi.org/10.1038/44766

Zelditch, M. L., & Goswami, A. (2021). What does modularity mean? *Evolution & Development*, 23, 377–403. https://doi.org/10.1111/ede.12390

# Submission completion gates

1. Generate Figures 1–5 directly from the frozen headline result table and topology outputs.
2. Add figure captions and Supporting Information crosswalk.
3. Add data-availability and code-availability statements with immutable artifact/commit identifiers.
4. Normalize the Moreyra author list and final journal reference style.
5. Run a final word-count and abstract-count check against JEB limits.
6. Audit every use of `convergence`, `adaptation`, `module`, `rate`, and `time` against the frozen claim boundaries.
