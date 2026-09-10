# Structured but not scale-invariant capitulum evolution in a young thistle radiation

**Target journal:** *Journal of Evolutionary Biology* — Research Article  
**Status:** V9.4 conceptual/scientific framing; supersedes V9.3 for manuscript architecture  
**Running title:** Scale-dependent capitulum organization

## Abstract

Complex phenotypes can retain recognizable biological organization while the relationships among their component traits change across scales. Whether this scale dependence extends into evolutionary history is rarely tested within a single complex reproductive structure. We examined capitulum evolution in a young *Cirsium* radiation using public nuclear phylogenomics, source-backed states for orientation, phyllary posture and involucre stickiness, topology-aware reconstruction, a common nine-variable environmental comparison and trait-specific ecological evidence. Thirty-six of 38 sampled Japanese taxon concepts occur in one dominant radiation. Orientation required four to six minimum changes across 1,000 bootstrap topologies, phyllary posture exactly three and stickiness exactly five. Their relative evolutionary depths differed strongly: phyllary histories were deeper-permissive than stickiness in 1,000/1,000 paired topologies and deeper than orientation in 993/1,000, while orientation was deeper-permissive than stickiness in 905/1,000. Zero of three trait pairs passed a robust shared-transition-localization rule. Thus capitulum organization is structured, but its component histories are not scale-invariant or repeatedly synchronized. Ecological correspondence likewise depended on representation. A trait-blind nine-variable analysis did not identify one shared abiotic niche axis across all three traits. Orientation was weak as a static tip-state contrast but showed strong phylogeny-conditioned transition–niche concordance; stickiness retained a coherent but exploratory precipitation-related present-niche lead; phyllary present ecology remained unresolved because replicated public state coverage was insufficient. Functional evidence is consistent with orientation, phyllary posture and stickiness mediating different exposure, access and arthropod-community interfaces. We conclude that complex reproductive phenotypes may retain component identity while their organization is repeatedly reconfigured across evolutionary depth and ecological representation.

**Keywords:** *Cirsium*; capitulum; evolutionary depth; modularity; mosaic evolution; phenotypic integration; rapid radiation; scale dependence

# Introduction

Complex phenotypes are organized rather than arbitrary collections of traits. Their components covary, share developmental and functional contexts and can form recognizable modules. Yet organization need not be invariant across biological scales. Relationships observed within populations may differ among species, and the ecological dimensions associated with phenotypic variation at one level need not dominate at another. A central problem is therefore not simply whether a complex phenotype is integrated, but whether the structure of that integration persists as the scale of comparison changes.

Most work on phenotypic integration and modularity has focused on covariance among extant traits, developmental organization or differences among clades. These approaches establish that complex structures can contain semi-independent modules, but they do not by themselves show how component histories are distributed through evolutionary time. A present-day module can retain biological identity even if its constituent traits changed at different evolutionary depths or on different branches. Conversely, traits with distinct functions can still evolve together through developmental coupling, correlational selection or repeated whole-organ reorganization. Functional difference alone therefore does not predict historical independence.

Three quantities are especially useful for separating these possibilities. **Recurrence** asks how many changes are minimally required by observed states. **Evolutionary depth** asks whether those changes can be placed on deeper internal branches or are restricted toward shallow lineage history. **Shared transition localization** asks whether different traits repeatedly change on the same branches. A complex phenotype can be repeatedly modified while remaining historically synchronized, or it can be repeatedly reassembled from components whose changes are stratified across different parts of the tree.

Rapid radiations provide an unusually strong test because substantial phenotype diversity occurs within shallow common ancestry. The thistle genus *Cirsium* contains a young Japanese radiation with extensive gene-tree discordance and marked diversity in capitulum structure. Within the same homologous reproductive head, capitula vary in presentation orientation, phyllary posture and involucre stickiness. These three traits therefore provide a natural test of whether component identity is retained while historical organization is reorganized.

Ecological correspondence introduces a second scale problem. A trait may appear weakly associated with environment when represented as a static species state but strongly associated when represented as a phylogenetically localized transition. Conversely, a present-day state contrast may be detectable without identifying the environment of trait origin. We therefore treat ecological association as representation-dependent rather than assuming that one environmental analysis captures a trait's ecological history.

Here we ask three main questions. First, do orientation, phyllary posture and stickiness each show repeated change within one young radiation? Second, are those changes distributed similarly across evolutionary depth and branch localization, or is capitulum history reorganized across components? Third, does ecological correspondence remain invariant when the same traits are represented at different biological resolutions—static tip states, phylogeny-conditioned transitions and trait-specific functional interfaces?

Our primary claim is not that different capitulum parts have different functions. That is expected. Instead, we test the stronger historical proposition that **the organization of a complex reproductive phenotype is structured but not scale-invariant: component traits recur, but their histories are stratified across different evolutionary depths and are not repeatedly synchronized on the same branches**. Ecological analyses are used to determine whether the same lack of invariance extends to trait–environment representation.

# Materials and Methods

## Nuclear scaffold and trait states

The historical panel followed 38 Japanese taxon concepts represented by the available nuclear phylogenomic framework. We used an independently reconstructed Compositae1061-compatible phylogram based on a frozen 241-locus starting set, yielding 236 quality-controlled loci, 176 rootable loci and a concatenated alignment of 161,654 bp. Maximum-likelihood inference used IQ-TREE 2 with ModelFinder, 1,000 ultrafast-bootstrap replicates and 1,000 SH-aLRT replicates. Branch lengths were substitutions per site and were not interpreted as calendar time.

Thirty-six of the 38 sampled concepts occur in the dominant Japanese radiation. We analysed three source-backed discrete capitulum traits: orientation, phyllary posture and involucre stickiness. Missing and ambiguous states remained unresolved. Historical coverage comprised 20 concepts for orientation, 10 for phyllary posture and 13 for stickiness.

## Minimum change, evolutionary depth and shared localization

For the maximum-likelihood topology and each of 1,000 bootstrap topologies, we calculated unordered parsimony minima. These are lower bounds on required state change and were not interpreted as counts of independent adaptive origins.

For every globally minimum-cost Sankoff history, relative lineage depth was defined for an edge subtending d descendants in a tree with N admitted tips as

\[
D=\frac{N-d}{N-1}.
\]

Terminal edges have D=1; smaller values permit deeper placement. Trait depth was compared directly on the same 1,000 bootstrap topologies. Because trait coverage differed, a deterministic masking sensitivity equalized observed-state coverage before repeating paired depth comparisons.

Shared-transition localization was evaluated with a branch-length-aware equal-rates Mk diagnostic and a topology-only sensitivity. A trait pair passed the robust descriptive rule only when positive localization overlap persisted under both treatments.

## Common nine-variable environmental comparison

All three traits were passed through one trait-blind present-environment workflow to test whether a common abiotic representation could explain their state structure. Public occurrences were source-name checked, subjected to coordinate-quality control and thinned at 0.1 degrees. Taxon medians were extracted for nine pre-existing environmental variables: BIO1, BIO4, BIO12, BIO15, short-wave radiation (RSDS), vapour-pressure deficit (VPD), surface wind, growing-season precipitation (GSP) and net primary productivity (NPP).

The primary gate required at least three thinned occurrences per taxon. For each trait, environmental values were standardized and the observed multivariate state separation was ranked among every state-label map preserving observed state counts. All evaluable trait-by-environment univariate rows were retained and Benjamini-Hochberg correction was applied across the 27-row family. No orientation-specific sign hypothesis was transferred to the other traits.

## Orientation transition-level ecological analysis

Orientation additionally had sufficient state-diverse public coverage for a phylogeny-conditioned transition analysis. After an earlier state comparison identified stable positive BIO15 and negative BIO1 directions, the upward-to-downward composite BIO15 up + BIO1 down was fixed as a post-result focused hypothesis.

For each accepted topology, a symmetric two-state CTMC supplied edge transition probabilities and Brownian reconstruction supplied branch environmental differences. A transition-weighted composite statistic was ranked among every count-preserving orientation state map. Coverage sensitivities, single-taxon deletion, linear latitude/longitude residualization and internal-edge-only scoring were retained.

A later source-partition diagnostic decomposed environmental values into Japan/Taiwan source-partition means and within-partition deviations. Japan and Taiwan were not treated as biological regions; this analysis tested whether coarse data-source geography alone generated the orientation signal.

## Functional evidence and antagonist fitness synthesis

Functional evidence was ranked by organ homology, manipulation geometry and taxonomic proximity. For orientation, the closest direct angle manipulation was in *Cremanthodium campanulatum*; for phyllary architecture, the closest structural manipulation was involucral-spine removal in *Centaurea solstitialis* combined with direct *Cirsium* antagonist–fitness evidence; for stickiness, direct *Cirsium* neutralization and arthropod-guild observations were prioritized.

A frozen random-effects meta-analysis summarized viable or mature seed output under experimentally reduced versus ambient reproductive insect herbivory in *Cirsium*. Nine within-study contrasts were collapsed to four independent data-generation programmes before pooling.

## Historical-environment boundary

Historical climate was used only to bound causal interpretation of the orientation result. The sole current orientation event linkable to bounded chronology and palaeolocation yielded 94 admissible chronology pairs crossed with four regional scenarios (376 scenarios). A broader audit examined 17 BIOCLIM variables across six dated lineage contexts and a separate sea-level diagnostic examined three representative contexts.

# Results

## Repeated capitulum change is concentrated within one young radiation

Thirty-six of 38 sampled Japanese concepts occur in the dominant radiation, yet multiple combinations of orientation, phyllary posture and stickiness are present within it. Orientation required four to six minimum state changes across 1,000 bootstrap topologies, phyllary posture exactly three and stickiness exactly five. Repeated reorganization is therefore a within-radiation property rather than a contrast among ancient major lineages.

## Component histories are stratified across evolutionary depth

The three traits showed strongly different relative-depth profiles. On paired comparisons using the same 1,000 bootstrap topologies, phyllary posture was deeper-permissive than stickiness in 1,000/1,000 topologies and deeper-permissive than orientation in 993/1,000. Orientation was deeper-permissive than stickiness in 905/1,000, with seven ties. The complete central ordering

\[
phyllary < orientation < stickiness
\]

where smaller values denote deeper permitted history, occurred in 898/1,000 topologies. Coverage-matched masking retained the central phyllary-deeper pattern, showing that the ordering is not explained simply by unequal numbers of resolved states.

The result is therefore stronger than the statement that the traits are merely labile. **Repeated change is historically stratified: different components occupy different layers of the radiation's topology.**

## Capitulum components do not repeatedly change as one synchronized historical unit

Zero of three pairwise trait comparisons passed the robust shared-transition-localization rule. Thus the traits are not only different in depth; they also fail to repeatedly place changes on the same branches.

Together, recurrence, paired depth ordering and lack of shared localization support **mosaic historical assembly**. The same complex reproductive structure retains recognizable component traits, but its organization is not invariant across evolutionary history.

## Ecological correspondence is representation-dependent rather than shared across traits

The common nine-variable analysis did not recover one shared abiotic niche axis for the three traits. Orientation included 17 taxa (5 downward, 12 upward) and had an omnibus rank of 2138/6188 (34.55%); its strongest static axis, GSP, ranked 1005/6188 (16.24%). Phyllary posture had only four taxa at the primary gate (3 ascending, 1 appressed), so present-environment effects were not identifiable as a replicated trait effect. Stickiness included 12 taxa with balanced state replication (6 sticky, 6 nonsticky) and had an omnibus rank of 116/924 (12.55%). Sticky taxa showed coherent raw precipitation-related leads for GSP (+1.278 SD; 18/924 = 1.95%), BIO12 (+1.311 SD; 22/924 = 2.38%) and BIO15 (+1.048 SD; 70/924 = 7.58%), but none survived Benjamini-Hochberg correction across the 27-row family.

Thus the three traits cannot be reduced to a single present-day climatic syndrome under the common representation.

## Orientation changes reveal ecological information that static state contrasts do not

Although orientation showed weak static separation in the common9 analysis, its phylogeny-conditioned transition representation was strongly structured. The fixed upward-to-downward BIO15-up/BIO1-down composite ranked 16/792 (2.02%) for n>=5, 19/1,716 (1.11%) for n>=3 and 4/126 (3.17%) for n>=10. The reverse transition tracked the opposite side of the same strict vector, yielding a bidirectional-floor rank of 3/126 (2.38%).

Positive forward and reverse alignment persisted in all 9/9 single-taxon deletions, although exact finite-map exceptionality persisted in 3/9. The result remained exceptional after latitude/longitude residualization, internal-edge-only scoring and their combination.

The Japan/Taiwan source-partition diagnostic did not explain the result. The between-partition mean component was opposite to the observed direction and non-exceptional (502/792 = 63.38%), whereas the within-partition component remained positive and exceptional (20/792 = 2.53%). Preserving source-partition orientation-state counts retained the within-partition result (10/336 = 2.98%).

The key contrast is therefore between representations: **orientation is weak as a static tip-state environmental contrast but informative when ecological change is aligned to reconstructed evolutionary transitions**.

## Functional evidence supplies biological interpretation but not the primary novelty

Functional studies are consistent with the three traits mediating different interfaces. Orientation is most plausibly linked to reproductive exposure to wetting and radiation; phyllary architecture to mechanical access by legitimate visitors and antagonists; and stickiness to context-dependent filtering of arthropod guilds. Across four independent *Cirsium* experimental programmes, reducing reproductive insect herbivory increased viable or mature seed output 2.674-fold (95% CI 2.388–2.993), establishing antagonism as a substantial reproductive-fitness channel in the genus.

These functional differences make mosaic history biologically plausible, but they are not themselves the central novelty of the study. The historical result arises from direct comparison of recurrence, depth and transition localization within the same radiation.

## Present ecological correspondence does not identify historical origin environment

For the sole calendar-bounded orientation event, the present BIO15/BIO1 signs matched 99/376 historical chronology-by-region scenarios (26.3%). The broader audit yielded 0/324 robust event-level climate classes and the sea-level audit 0/21 robust classes. We therefore use historical climate only as a boundary: present ecological organization is detectable, but the origin environment is not identified by these coarse public reconstructions.

# Discussion

## Complex-phenotype organization is structured but not scale-invariant through evolutionary history

The main result is not simply that orientation, phyllaries and sticky involucres have different functions. Rather, the same three components provide a direct test of whether a complex phenotype preserves one historical organization. They do not. All three repeatedly changed, but their histories occupy different relative depths and fail to repeatedly localize to the same branches.

This distinguishes **component identity** from **organizational invariance**. Orientation remains orientation, phyllary posture remains a homologous phyllary property and stickiness remains an involucral surface property across the radiation. Yet the relationships among their histories are reorganized across the tree. A complex phenotype can therefore remain biologically recognizable without preserving one fixed historical architecture.

This result also avoids an overly simple modularity argument. Different functions do not logically require different histories: developmental coupling, pleiotropy, correlational selection or repeated whole-organ shifts could have synchronized trait change. The observed lack of synchronization is therefore empirical rather than tautological.

## Evolutionary depth adds information that recurrence alone cannot provide

Counts of state changes identify repeated differentiation but not its historical structure. The paired-depth analysis shows that recurrence is layered. Phyllary history is consistently deeper-permissive, stickiness is concentrated toward shallower placements and orientation is intermediate. Because these comparisons are made on the same 1,000 topologies and survive coverage matching, the result is not a trivial consequence of different numbers of scored taxa.

This provides a general way to describe complex-phenotype evolution: components can share a common organ and a common radiation while occupying different **historical scales**. The important quantity is therefore not only how often traits change, but where in the hierarchy of lineage divergence those changes can be placed.

## Ecological association also depends on biological representation

The orientation result extends the scale argument from history to ecology. Static downward-versus-upward state classes are not strongly separated in the common nine-variable environment, yet reconstructed transition probability is associated with a specific environmental direction. The ecological pattern therefore becomes visible when phenotype is represented as evolutionary change rather than as an extant-state average.

This does not mean that transition-level analysis is universally superior. Instead it shows that ecological correspondence can depend on the level at which phenotype is represented. State means, within-lineage variation and reconstructed evolutionary change answer different biological questions and should not be expected to expose the same environmental axis.

The common9 analysis strengthens this interpretation by preventing a selective focus on orientation alone. Under the same trait-blind environment universe, the three traits show different evidence profiles: orientation is strongest in transition space, stickiness retains exploratory precipitation-related tip-niche structure and phyllary posture remains limited by replicated state coverage. One shared climate representation is therefore not an adequate description of the whole capitulum.

## Functional interfaces explain plausibility, not novelty

The ecological-interface literature is useful because it explains why a historically mosaic capitulum is biologically reasonable. Orientation can influence abiotic reproductive exposure, phyllary architecture can regulate mechanical access and sticky surfaces can restructure arthropod interactions. These mechanisms give meaning to the historical differences, but the paper does not depend on claiming that different functions are surprising.

Instead, the functional evidence defines the next causal step. Direct focal *Cirsium* manipulations of orientation, phyllary posture and stickiness are required to test whether these proposed filters actually cause changes in pollen performance, effective visitation, antagonist damage and reproductive fitness. Until then, the present study establishes historical organization and ecological correspondence, not adaptive causation.

## A broader implication: complex phenotypes may preserve modules while reorganizing relationships across scale

The results support a general distinction between the persistence of biological components and the persistence of their relationships. A complex structure can retain recognizable modules while the strengths, ecological correlates and historical placement of those modules change with scale. Treating one observed level as the invariant architecture of the phenotype risks conflating organization with scale-specific expression of organization.

For comparative biology, this suggests a practical programme: evaluate complex phenotypes at multiple levels rather than asking whether they are simply integrated or modular. Within-taxon covariance, among-taxon differentiation, evolutionary depth and transition localization can each reveal different aspects of the same biological structure. Concordance across levels becomes an empirical result rather than an assumption.

## Historical climate is a boundary, not the main result

The historical climate analyses prevent projection of the present orientation association onto trait origin. They do not weaken the historical-organization result. The paper's strongest inference is therefore asymmetric: the structure of phenotypic assembly is better resolved than the selective conditions that produced each event.

# Conclusion

Capitulum evolution in a young *Cirsium* radiation is **structured but not scale-invariant**. Orientation, phyllary posture and involucre stickiness each changed repeatedly, but those changes occupy unequal evolutionary depths and do not repeatedly localize to the same branches. Ecological correspondence likewise depends on representation: a common static environmental analysis does not yield one shared climatic syndrome, while orientation becomes informative when aligned to reconstructed transitions.

The central contribution is therefore a historical one. Complex reproductive phenotypes can retain recognizable components while the organization among those components is repeatedly reconfigured across evolutionary depth. Functional differences among capitulum traits make that pattern biologically plausible, but focal manipulation is the next step required to convert historical and ecological correspondence into causal explanation.
