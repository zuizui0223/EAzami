# Coordinated evolutionary change without conserved trait states in a rapid thistle radiation

**Target:** Journal of Evolutionary Biology — Research Article  
**Status:** working manuscript v1; continuous topology-sensitivity sentence remains provisional.  
**Running title:** Multidimensional capitulum evolution in *Cirsium*

## Abstract

Complex phenotypes are often described by their present-day integration, yet present covariance does not reveal whether component traits retained the same states, changed independently, or were remodeled during the same evolutionary episodes. We tested these alternatives in the capitulum of Japanese *Cirsium*, a lineage dominated by a rapid Pleistocene radiation. We linked a frozen image-derived continuous phenotype ontology to an independently reconstructed public-data nuclear phylogeny. Exact taxon-concept matching recovered up to 14 Japanese concepts and supported comparative histories for eight primary continuous phenotype dimensions spanning orientation, corolla colour and capitulum shape. Across the primary and higher-depth panels, no continuous dimension retained significant two-sided phylogenetic structure after correction across traits; scalar-trait Pagel's lambda estimates were zero. Independently source-coded discrete traits nevertheless required repeated historical changes: orientation required 4–6 changes across bootstrap topologies, phyllary posture three, and stickiness five. On the maximum-likelihood phylogram, magnitudes of reconstructed change were positively correlated across the eight continuous dimensions (mean pairwise Spearman rho = 0.408, permutation P < 0.0001), although this coordination was not significantly stronger within predefined phenotype modules than between them. Discrete transition overlap was topology-sensitive rather than consistently shared across traits. **[PENDING: insert equal-branch bootstrap-topology decision for continuous branch-change coordination.]** These results separate conservation of phenotypic states from coordination in the location of evolutionary change and suggest that multidimensional disparity can accumulate through episodes of broad phenotypic remodeling without preserving a fixed capitulum syndrome.

**Keywords:** Cirsium; phenotypic integration; modularity; rapid radiation; phylogenetic signal; morphological evolution; capitulum; evolutionary lability

---

# Introduction

Organisms evolve as multivariate phenotypes rather than as isolated traits. Correlations among phenotype components can channel the directions available to evolution, while modular organization can permit parts of a complex structure to vary with partial independence. A large literature on phenotypic integration has therefore asked how strongly traits covary, whether covariance is partitioned into modules, and whether those patterns alter morphological disparity or evolvability (Klingenberg, 2014; Goswami et al., 2014). In plants, this problem is especially acute because reiterated reproductive structures vary within individuals, populations and species, so an average species-level floral phenotype can obscure biologically structured variation (Diggle, 2014). Yet a covariance pattern observed in present-day phenotypes is not itself an evolutionary history.

At least three historical properties of a complex phenotype should be distinguished. First, **state conservation** asks whether close relatives retain similar values of a trait. Second, **recurrence** asks how often a defined phenotypic state must have changed across a phylogeny. Third, **change localization** asks whether large evolutionary changes in different phenotype dimensions occurred on the same branches. These properties need not agree. Strong present-day integration does not require that every component retain phylogenetic signal, and weak state conservation does not require that evolutionary change was temporally or phylogenetically independent across traits. Macroevolutionary work on complex structures has similarly shown that integration can influence directions of disparity without mapping simply onto evolutionary rate, and that mosaic change can be understood only by locating change across components and lineages rather than by treating an organ as one state (Goswami et al., 2014; Felice & Goswami, 2018).

Rapid radiations provide a useful setting in which to separate these possibilities. Large phenotypic disparity compressed into a shallow lineage history can arise through several contrasting architectures: retention and divergence of a conserved multivariate syndrome, repeated independent changes of component traits, or episodes in which many dimensions are remodeled together even though their final states do not remain conserved. The thistle genus *Cirsium* offers such a natural experiment. A recent phylogenomic analysis based on 350 nuclear loci recovered rapid Pleistocene radiations in Japan and North America and identified a dominant Japanese radiation following dispersal from Asia (Moreyra et al., 2025). The same study also reported phylogenomic incongruence consistent with processes such as hybridization and incomplete lineage sorting, making uncertainty in the exact topology an important part of any phenotype-history analysis.

A preceding phenomic analysis provided an unusual opportunity to ask this historical question without collapsing the capitulum into categorical floral types. Georeferenced photographs were used to define and measure continuous capitulum components, including orientation, colour and shape, and to quantify both within- and among-taxon organization. That analysis showed that the present capitulum is multidimensional and only partially organized: associations among component traits differ between within- and among-taxon scales. Here we use the **same measured phenotype ontology** but ask an independent question. We do not restrict the historical analysis to traits that showed environmental associations, and we do not require an ecological function to be assigned before a phenotype can enter evolutionary analysis. Instead, we ask how the measured phenotype itself is distributed through evolutionary history.

We tested five linked questions. **(1)** Do continuous capitulum components retain phylogenetic state structure? Under a conserved-state expectation, close relatives should be phenotypically similar and scalar traits should show positive phylogenetic signal. **(2)** Do independently source-coded discrete capitulum states require repeated changes? **(3)** Are magnitudes of continuous phenotypic change concentrated on the same branches, even if tip values themselves are weakly conserved? **(4)** If branch-wise changes are coordinated, is that coordination stronger within the phenotype modules defined independently from present-day measurements? **(5)** Are apparent shared histories robust to phylogenetic-topology uncertainty? Together these tests distinguish a conserved capitulum syndrome, fully independent component histories, and the intermediate possibility of coordinated evolutionary remodeling without stable conservation of trait states.

# Materials and methods

## Study system and evolutionary context

The focal panel was derived from the 38 Japanese taxon concepts sampled in the broad phylogenomic study of Moreyra et al. (2025). Published synthesis places 36 of these 38 concepts within one dominant Japanese radiation, with rare secondary histories. We treated this published biogeographic result as evolutionary context rather than using published figure topology as the analytical tree.

For the focal historical analyses we used the independently reconstructed Japan38 Comp1061 compatibility phylogeny frozen in EAzami. The reconstruction contains 39 focal biological samples plus a safflower outgroup, used 236 quality-controlled nuclear loci of which 176 were rootable with the outgroup, and produced a 161,654-bp concatenated alignment. IQ-TREE 2.4 was run with ModelFinder, 1,000 ultrafast bootstrap replicates and 1,000 SH-aLRT replicates. Branch lengths are substitutions per site and are **not absolute time**. One published concept, JPN_20, is represented by two non-monophyletic biological samples in the maximum-likelihood tree and in 0/1,000 bootstrap trees; it was therefore not forcibly collapsed into one phenotype tip. JPN_31 was excluded from primary phenotype-history inference because of a frozen identity/locality conflict.

## Recovering continuous phenotype data without recategorization

We reused the frozen Azami Chapter 1 continuous-trait artifact rather than building a new trait dataset for the phylogeny. The source contains 46,276 unique strict-spatial observations and 1,018,072 long-format trait rows. A compute-only bridge matched these observations to the Japan38 paper concepts using exact normalized taxon concepts. Botanical author strings were ignored, but infraspecific rank was preserved; broad species-level images were never substituted for a named variety or subspecies. No missing trait was imputed and no continuous measurement was discretized to increase coverage.

The bridge recovered at least one continuous phenotype for 14 exact Japan38 concepts. Primary image-derived endpoints had substantially better coverage than candidate involucre and armature endpoints. Orientation reached 14 exact concepts overall, eight with at least two observations and six with at least five. Each of four primary capitulum-shape endpoints reached 14 concepts overall, ten at >=2 observations and six at >=5. Continuous colour metrics similarly reached 14 concepts overall, ten at >=2 and six at >=5. Candidate involucre/armature metrics reached only five exact concepts and two at >=2 observations; these were retained as a documented coverage limitation and not promoted into radiation-wide continuous history.

The continuous historical analysis therefore contained eight primary inferential units: vertical orientation angle; CIELAB lightness; CIELAB chroma; circular hue represented jointly by sine and cosine; capitulum-outline aspect ratio; outline circularity; outline solidity; and width-profile coefficient of variation. The primary evidence threshold required at least two frozen observations per taxon-concept endpoint. A >=5-observation panel was analysed as a high-depth sensitivity.

## Trait-level phylogenetic state structure

For each scalar continuous unit with at least six exact concepts, we pruned the compatibility tree to the eligible concepts and estimated Pagel's lambda under a Brownian covariance model. Because branch lengths are substitutions per site, lambda was treated only as a phylogenetic-structure diagnostic. We separately calculated Spearman correlation between pairwise patristic distance and absolute pairwise phenotype difference. Significance was evaluated by permuting phenotype labels across tips; all label permutations were used for panels of eight or fewer concepts and Monte Carlo permutations were used for larger panels. We reported both positive and negative tails and used the two-sided test for the primary family-level inference. Benjamini-Hochberg correction was applied across the eight primary inferential units separately within each evidence-depth threshold.

Circular hue was not linearized into one arbitrary angle. Instead, sine/cosine vectors were normalized and pairwise phenotype distance was defined as chord distance. The same label-permutation logic was then applied to patristic versus hue distance. Leave-one-concept-out analyses assessed sign stability for every unit.

## Discrete-state recurrence

Continuous measurements were not converted into categorical states merely to estimate transition counts. Instead, we used a separate authority-backed evidence contract for traits whose discrete biological state ontology was independently defined: capitulum orientation, phyllary posture and involucre stickiness. Missing or ambiguous states remained missing. After the latest authority repairs, orientation was resolved for 20 concepts, phyllary posture for ten and stickiness for 13.

For each bootstrap topology we calculated the minimum number of unordered state changes required by the observed tip states. These values are topology-conditioned parsimony lower bounds, not counts of adaptive convergence. We separately retained the equal-rates Mk transition-posterior overlap analysis to ask whether transitions in different discrete traits tended to localize on the same branches. Because raw ultrafast-bootstrap trees do not provide the focal ML branch lengths, a topology-only sensitivity set every non-root branch to equal length rather than inventing substitution lengths.

## Continuous branch-wise change

To ask a different question from state conservation, we quantified where large continuous changes were reconstructed on the phylogeny. The common >=2-observation panel contained eight concepts with complete data across all eight primary inferential units. Scalar tip values were standardized by their among-tip standard deviation. Under a Brownian covariance model on the maximum-likelihood phylogram, we calculated conditional expected states for internal nodes. For each parent-child branch, change magnitude was the absolute difference between reconstructed states divided by the square root of the substitution-length branch. Circular hue was reconstructed in sine/cosine components, normalized at each node, and expressed as parent-child chord distance per square-root branch length.

We then calculated a Spearman correlation matrix among the eight branch-change vectors. The primary summary was the mean of all 28 pairwise correlations. A null distribution was produced by independently permuting branch values within each phenotype dimension 10,000 times. To test whether coordinated change followed the phenotype modules identified in Chapter 1, we compared the mean within-module versus between-module branch-change correlation and evaluated the contrast using all unique permutations of the registered module labels across the eight units.

## Topology sensitivity of coordinated continuous change

**[Analysis implemented; result pending final workflow completion.]** For each of the 1,000 raw ultrafast-bootstrap topologies, we prune to the same eight-concept continuous panel and set all non-root branches to one. We reconstruct the same standardized continuous changes and recalculate global mean pairwise branch-change correlation and the within-minus-between module contrast. Before inspection, global coordination was defined as topology-robust positive only if at least 95% of usable bootstrap topologies yielded a positive global mean correlation and the empirical fifth percentile exceeded zero. The same rule was applied separately to module specificity.

## Absolute-time boundary

We did not convert the compatibility phylogram into a dated trait tree. An earlier fail-closed calibration audit found that published age information did not provide a sufficiently defensible multi-anchor mapping for the exact compatibility topology. Consequently, all focal historical conclusions concern phylogenetic structure, relative placement and repeated changes, not absolute trait-transition ages or rates per million years.

# Results

## Continuous phenotype coverage supports a primary time-axis panel but not all candidate traits

The exact-concept bridge recovered continuous data for 14 of the Japan38 concepts. Coverage was sufficient to compare orientation, three continuous colour units and four capitulum-shape units, but not the candidate continuous involucre/armature endpoints. The main >=2 panel included eight concepts for orientation and ten for each colour/shape unit; the >=5 sensitivity included six concepts for all eight units. Only five taxon concepts had complete data for all 18 frozen endpoints, demonstrating why the historical analysis was performed endpoint-wise rather than restricting all analyses to a five-taxon complete-case matrix.

## Individual continuous trait values show little robust phylogenetic structure

No primary continuous inferential unit showed significant two-sided phylogenetic structure after correction across the eight-unit family at either evidence-depth threshold. Pagel's lambda maximum-likelihood estimate was zero for all seven scalar units in both the >=2 and >=5 panels. In the main >=2 panel, patristic-distance correlations ranged from positive values for orientation (rho = 0.103) and chroma (rho = 0.069) to negative values for several shape dimensions, including solidity (rho = -0.437); none remained significant after family correction.

The higher-depth panel exposed directional anti-phylogenetic tendencies in some dimensions without licensing a family-level claim. Lightness showed rho = -0.707 with an exact two-sided P = 0.0444 and an exact negative-tail P = 0.00139, but its BH-adjusted two-sided value was 0.356. Shape solidity and width-profile variation also showed consistently negative leave-one-out correlations but did not pass the corrected two-sided family. Thus the strongest supported conclusion is not that a particular dimension is phylogenetically overdispersed, but that **none of the eight primary continuous trait states showed robust conserved phylogenetic structure in the current Japanese exact-concept panel**.

## Independently defined discrete states require repeated historical changes

The discrete history gave a complementary result. Orientation required six minimum unordered changes on the maximum-likelihood tree and four to six across 1,000 ultrafast-bootstrap topologies (median five). Phyllary posture required exactly three changes in every bootstrap topology. Following the JPN_24 authority repair, stickiness was resolved for 13 concepts and required exactly five minimum changes on all 1,000 bootstrap topologies; the ML minimum root state was sticky. These are recurrence lower bounds and do not distinguish independent adaptive convergence from retention, reversal, sorting or reticulate histories.

## Continuous phenotype changes are coordinated on the maximum-likelihood phylogram

Despite weak trait-state phylogenetic structure, reconstructed magnitudes of continuous change were positively associated across phenotype dimensions on the focal maximum-likelihood phylogram. Across the 28 trait pairs, mean branch-change Spearman correlation was **0.4080**. Independent branch permutation gave a one-sided probability below 0.0001 (P = 0.00010 with the plus-one estimator). Several cross-module associations were as strong as associations among shape variables: orientation change correlated with lightness change at rho = 0.666 and with width-profile change at rho = 0.745; lightness change correlated with aspect ratio and circularity at rho = 0.771 in both cases.

Coordination was not confined to the modules defined from present-day phenotype organization. Mean within-module branch-change correlation was 0.495 and mean between-module correlation was 0.367, a contrast of 0.128. Exact permutation of module labels did not support an elevated within-module correlation (P = 0.168). Thus the current ML result indicates **broad coordination of change rather than module-restricted coordinated change**.

## Discrete transition overlap is not topology-robust

The latest discrete transition-overlap analysis incorporated all current authority repairs (20 orientation, ten phyllary and 13 stickiness states). On the substitution-length ML tree, orientation and stickiness showed positive transition-posterior excess over the branch prior (rho = 0.202, one-sided P = 0.0042), while orientation-phyllary excess was weaker (rho = 0.362, P = 0.0894) and phyllary-stickiness excess was small (rho = 0.084, P = 0.2704).

However, these apparent overlaps did not survive the branch-length-free topology sensitivity. Across bootstrap topologies, orientation-phyllary overlap had median rho = -0.059 and was positive in 34.9% of usable trees. Orientation-stickiness was strongly negative (median rho = -0.387; 5th–95th percentile approximately -0.392 to -0.187) and positive in only 0.9% of trees. Phyllary-stickiness was more often positive (median rho = 0.184; positive in 78.2%) but its fifth percentile remained negative. No trait pair therefore showed a consistently positive shared discrete-transition history across branch-length-aware and topology-only layers.

## Topology robustness of continuous coordinated change

**[PENDING TOPOLOGY-SENSITIVITY RESULT.]** This section will determine whether the positive ML branch-change result remains the abstract headline or is moved to a sensitivity result.

# Discussion

## State conservation and localization of change are different properties

The clearest result is that two questions often conflated under “phenotypic integration” gave different answers. Individual continuous trait values did not show robust phylogenetic state structure in the current panel, yet their reconstructed changes on the ML phylogram were positively coordinated. In other words, knowing where a lineage sits on one phenotype axis did not strongly predict its state from ancestry, but branches inferred to have undergone large change in one dimension often underwent large change in others. This distinction matters because present-day covariance and phylogenetic signal describe distributions of states, whereas branch-wise analyses describe the localization of change.

If the positive branch-change result survives the bootstrap-topology sensitivity, the data support an evolutionary architecture that is neither a conserved capitulum syndrome nor fully independent component evolution. A useful description is **coordinated phenotypic lability**: episodes of broad remodeling can affect several dimensions of a complex organ even when the final trait states are not persistently conserved among descendant lineages. Such an architecture is compatible with the broader idea that integration can shape directions of phenotypic evolution without mapping directly onto simple differences in evolutionary rate (Goswami et al., 2014). We emphasize that coordinated change identifies neither the developmental source of covariance nor the selective cause of an episode.

## Repeated discrete states do not reduce to one shared history

The discrete state layer reinforces the importance of decomposing the capitulum, but in a different way. Orientation, phyllary posture and stickiness all require repeated changes, yet their transition-posterior overlap is strongly topology-dependent. The result is especially instructive for orientation and stickiness: the substitution-length ML tree yields positive excess overlap, whereas equal-branch bootstrap topologies yield a predominantly negative association. Treating only the ML tree as known would therefore overstate evidence for one shared lability history.

The contrast between continuous and discrete analyses should not be treated as a contradiction. Discrete ontologies reduce a phenotype to thresholded states and focus on the location of state transitions, whereas continuous branch-change analysis retains magnitude information. Broad remodeling can therefore be coordinated without forcing several threshold-defined states to cross their boundaries on the same branch. Conversely, recurrent discrete-state changes need not imply that the underlying continuous phenotype was evolving independently at all times.

## A rapid radiation can generate disparity without stable syndrome conservation

Japanese *Cirsium* provides an informative setting for this distinction because most sampled Japanese diversity belongs to a shallow Pleistocene radiation. Prior EAzami synthesis also showed that present capitulum disparity within the dominant radiation is not a simple monotonic function of separation from the rarer secondary historical lineages. Combined with weak state-level phylogenetic structure and recurrent discrete changes, the emerging picture is one of substantial phenotype reorganization within a young lineage history rather than retention of a few fixed lineage syndromes.

This interpretation remains deliberately separate from adaptive radiation. Neither rapid lineage accumulation nor repeated phenotypic change demonstrates that trait divergence was caused by ecological adaptation. The present paper asks how phenotype was assembled through lineage history. The ecological and fitness consequences of that history are a subsequent question.

## Why continuous image phenomics changes the historical question

The historical analysis was possible because the phenotype was not reconstructed from a conventional species-level trait table. Chapter 1 retained continuous variation from georeferenced photographs and defined an explicit endpoint ontology before the focal phylogenetic analysis. For Chapter 2, we could therefore ask whether continuous orientation, colour and shape dimensions carried different historical signals without converting them into coarse species categories. This also exposed an important limitation: the newer continuous involucre and armature measurements currently have too little exact Japan38 coverage for defensible radiation-wide history. Rather than filling those gaps by species-name substitution or discretization, we treated the missing historical modules as a measurement frontier.

The contrast between the continuous and authority-coded datasets is therefore useful methodologically. Public imagery can provide broad continuous phenotype measurements but must be identity-matched carefully to phylogenetic concepts, while botanical authority sources can provide biologically explicit categorical states for taxa lacking enough standardized images. Their inferential targets differ, and combining them only at the level of biological interpretation avoids manufacturing a falsely complete matrix.

## What the current study does not establish

Several boundaries are central to the interpretation. First, the focal compatibility tree is a phylogram: branch lengths are substitutions per site, not million years. The branch-change statistic is consequently a structural diagnostic rather than an absolute evolutionary rate. Second, internal continuous states are Brownian conditional expectations rather than observed ancestors. Third, recurrence counts are parsimony lower bounds and do not distinguish independent origin from ancestral polymorphism, incomplete lineage sorting, introgression, reversal or other histories. Fourth, no image-derived phenotype is promoted to an adaptive functional trait in this chapter.

These limitations define the next evidence layers rather than invalidating the present result. Population-level nuclear ancestry linked to matched plastid haplotypes and cytotype information is needed to determine the origin of repeated states. Trait manipulation and reproductive-fitness measurements are needed to establish function and adaptive consequence. Those analyses are intentionally separated from the present phenotype-history paper.

## Relationship to the existing meta-analysis and simulation programmes

Two substantial EAzami analysis programmes are retained but not used as substitutes for evolutionary history. First, the trait-to-function meta-analysis and associated syntheses quantify candidate pollination, antagonist, protection and demographic pathways. These results belong primarily to the next function/fitness chapter; in the present paper they motivate future explanations for historical patterns but do not define which phenotype enters the phylogeny. Second, the Azami-compatible v3/v4 simulations concern the generation of the **present within/among phenotype covariance field**. They are therefore retained as Chapter 1 supplementary/structural analyses rather than being interpreted as historical transition simulations. A future simulation explicitly conditioned on an empirical tree, trait-transition history and ecological history would be a distinct historical analysis and could return to the Chapter 2 synthesis.

# Conclusion

By placing the same continuous capitulum phenotype ontology used for spatial phenomics onto an evolutionary phylogeny, we separated conservation of trait states from localization of phenotypic change. Continuous trait states were weakly structured by phylogenetic relatedness, multiple independently defined capitulum states were recurrent, and the maximum-likelihood phylogram suggested coordinated change across multiple continuous phenotype dimensions without a correspondingly strong module-specific pattern. **[Final sentence contingent on bootstrap-topology sensitivity.]** This framework turns a complex reproductive organ from a categorical syndrome into a set of measurable histories and provides a direct bridge from phenomics across space to phenotypic assembly through evolutionary time.

# References currently supporting the Introduction

- Diggle, P. K. (2014). Modularity and intra-floral integration in metameric organisms: plants are more than the sum of their parts. *Philosophical Transactions of the Royal Society B*, 369, 20130253. https://doi.org/10.1098/rstb.2013.0253
- Felice, R. N., & Goswami, A. (2018). Developmental origins of mosaic evolution in the avian cranium. *Proceedings of the National Academy of Sciences*, 115, 555–560. https://doi.org/10.1073/pnas.1716437115
- Goswami, A., et al. (2014). The macroevolutionary consequences of phenotypic integration: from development to deep time. *Philosophical Transactions of the Royal Society B*, 369. [full bibliographic details to normalize before submission]
- Klingenberg, C. P. (2014). Studying morphological integration and modularity at multiple levels: concepts and analysis. *Philosophical Transactions of the Royal Society B*, 369, 20130249. https://doi.org/10.1098/rstb.2013.0249
- Moreyra, L. D., et al. (2025). A thorny tale: The origin and diversification of *Cirsium* (Compositae). *Molecular Phylogenetics and Evolution*, 204, 108285. https://doi.org/10.1016/j.ympev.2025.108285

# Manuscript completion gates

1. Freeze continuous equal-branch UFBoot topology sensitivity and update title/abstract/results once.
2. Persist latest discrete overlap outputs in the PR after the previous push-conflict-only failure.
3. Add a figure-ready table linking exact-concept coverage to the 8-unit history panel.
4. Build Figures 1–4 from frozen outputs.
5. Normalize bibliography and add a small set of recent integration/modularity references; do not inflate literature beyond the question.
6. Keep main text <=7,500 words and abstract <=250 words for JEB.
