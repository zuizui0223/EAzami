# Mosaic capitulum evolution across distinct ecological interfaces in a young thistle radiation

**Target journal:** *Journal of Evolutionary Biology* — Research Article  
**Status:** V9.3 trait-appropriate ecology manuscript draft; supersedes V9.2 for scientific framing  
**Running title:** Ecological interfaces and capitulum mosaic evolution

## Abstract

Complex reproductive structures combine traits that interact with different parts of the environment and therefore need not share one evolutionary history. We tested this idea in a young *Cirsium* radiation using public nuclear phylogenomics, authority-backed capitulum states, trait-blind present-environment comparisons and a homology-restricted synthesis of functional experiments. Thirty-six of 38 sampled Japanese taxon concepts occur in one dominant radiation. Orientation required four to six minimum changes across 1,000 bootstrap topologies, phyllary posture exactly three and involucre stickiness exactly five. Their relative lineage-depth profiles differed, and zero of three trait pairs passed a robust shared-transition-localization rule. A common nine-variable present-environment analysis did not identify one shared abiotic niche axis for the three traits. Instead, ecological evidence differed by trait. Orientation showed its strongest signal at the phylogeny-conditioned transition level, where upward-to-downward change tracked higher precipitation seasonality and lower annual temperature; that association was retained after removing Japan–Taiwan regional means. Stickiness showed a separate, exploratory precipitation-related niche lead, whereas phyllary ecology remained unresolved because replicated public state coverage was insufficient. Independent functional evidence maps orientation to abiotic reproductive exposure, phyllaries to mechanical access and sticky involucres to guild-selective arthropod filtering. Across four *Cirsium* experimental programmes, reducing reproductive insect herbivory increased viable or mature seed output 2.674-fold (95% CI 2.388–2.993). These results support mosaic ecological evolution of a complex reproductive structure without requiring one synchronized adaptive syndrome or one shared climate driver.

**Keywords:** *Cirsium*; capitulum; ecological interface; floral herbivory; mosaic evolution; phylogenetic uncertainty; rapid radiation; trait evolution

# Introduction

Complex reproductive structures function as integrated wholes, yet their components can interact with different parts of the environment. Floral orientation can alter exposure to rain, radiation and pollinators; phyllaries and spines can alter physical access by mutualists and antagonists; sticky surfaces can deter, trap or redirect arthropods. Present-day integration therefore does not imply that all component traits were assembled together or shaped by one ecological driver.

This distinction matters because three different historical questions are often conflated. Recurrence asks how often observed states require change. Evolutionary depth asks where those changes can be placed within a radiation. Shared localization asks whether different traits repeatedly change on the same branches. A complex organ can therefore be functionally integrated in the present while its components have partly distinct historical trajectories.

Rapid radiations provide a useful setting for testing that possibility. When substantial phenotype diversity occurs within shallow common ancestry, component histories can be compared without attributing every difference to ancient lineage separation. The thistle genus *Cirsium* is particularly suitable because recent nuclear phylogenomics recovered a dominant Japanese radiation with extensive gene-tree discordance, while capitula differ strongly in orientation, phyllary posture and involucre stickiness.

The ecological interpretation of those traits is also unlikely to reduce to one environmental axis. Orientation plausibly alters abiotic reproductive exposure; phyllary posture changes the geometry of physical access to developing reproductive tissues; and sticky involucres change contact and residence of different arthropod guilds. Existing experiments in *Cirsium*, Cardueae and close Asteraceae analogues support these distinct interfaces, but the comparative ecological evidence is uneven across traits.

We therefore separate a common historical comparison from trait-appropriate ecological evidence. First, we test whether orientation, phyllary posture and stickiness each changed repeatedly within the radiation. Second, we compare their relative evolutionary depths and transition localization. Third, we pass all three traits through the same nine-variable present-environment pipeline to test whether one shared abiotic niche explanation is sufficient. Finally, we evaluate the strongest trait-specific ecological evidence available for each trait, while keeping functional interpretation separate from claims of adaptation.

Our central claim is deliberately narrow: **a complex reproductive structure can be historically reassembled from components that differ both in evolutionary history and in the ecological interfaces they mediate**.

# Materials and Methods

## Nuclear scaffold and trait states

The focal historical panel followed 38 Japanese taxon concepts represented by Moreyra et al. (2025). We used an independently reconstructed Compositae1061-compatible nuclear phylogram. A frozen 241-locus starting set yielded 236 quality-controlled loci, 176 rootable with safflower and a concatenated alignment of 161,654 bp. Maximum-likelihood inference used IQ-TREE 2 with ModelFinder, 1,000 ultrafast-bootstrap replicates and 1,000 SH-aLRT replicates. Branch lengths were substitutions per site and were not treated as calendar time.

Thirty-six of 38 sampled Japanese concepts occur in the dominant radiation. We analysed three source-backed discrete traits: capitulum orientation, phyllary posture and involucre stickiness. Missing or ambiguous records remained unresolved. Historical coverage was 20 concepts for orientation, 10 for phyllary posture and 13 for stickiness.

## Minimum-change reconstruction, evolutionary depth and shared localization

For the maximum-likelihood topology and each of 1,000 bootstrap topologies, we calculated unordered parsimony minima. These are lower bounds on required state changes, not counts of independent origins.

For every globally minimum-cost Sankoff history, relative lineage depth was defined for a tree with N admitted tips and an edge subtending d descendants as

\[
D=\frac{N-d}{N-1}.
\]

Terminal edges have D=1 and smaller values permit deeper placement. Trait depths were compared directly on the same 1,000 bootstrap topologies. A masking sensitivity equalized observed-state coverage. Shared-transition localization was evaluated with an equal-rates Mk diagnostic and a topology-only sensitivity; a pair passed the descriptive robust rule only when positive localization persisted under both treatments.

## Common nine-variable present-environment comparison

To avoid giving orientation a privileged environmental panel, all three historical traits were passed through one trait-blind occurrence and environment workflow. The provenance frame matched the Japan38 phylogeny; Japan was treated as a sampling frame rather than a biological region class. Public GBIF occurrences were source-name checked, restricted to coordinate uncertainty <=10 km where possible, thinned at 0.1 degrees and summarized by taxon medians.

The environmental universe was fixed before execution to the nine variables already present in the Chapter 2 common-environment contract: BIO1, BIO4, BIO12, BIO15, mean short-wave radiation (RSDS), mean vapour-pressure deficit (VPD), mean surface wind, growing-season precipitation (GSP) and net primary productivity (NPP). The primary gate required at least three thinned occurrences per taxon. A phyllary >=1 occurrence sensitivity was diagnostic only.

For each trait, taxon environmental values were standardized and state separation was scored in the nine-dimensional environment space. Every state-label map preserving observed state counts was enumerated, giving a complete finite-map rank for the observed omnibus statistic. All evaluable trait-by-environment univariate rows were retained and Benjamini-Hochberg correction was applied across the 27-row family. Orientation-derived directional hypotheses were not transferred to phyllary or stickiness.

## Orientation transition-level present-niche analysis

Orientation also had sufficient public coverage for a phylogeny-conditioned transition analysis. The upward-to-downward composite BIO15 up + BIO1 down was fixed after an earlier state-comparison analysis showed stable directions and is therefore a post-result focused hypothesis rather than a preregistered vector.

For each accepted topology, a symmetric two-state CTMC provided edge transition probabilities and Brownian reconstruction supplied branch environmental differences. A transition-weighted composite statistic was ranked among every count-preserving orientation state map. Coverage sensitivities, single-taxon deletion, linear latitude/longitude residualization and internal-edge-only scoring were retained.

A post-result scale diagnostic then decomposed each taxon environment into Japan/Taiwan source-partition means and within-partition deviations without changing the environmental vector, taxon panel or estimator. A stricter null preserved orientation-state counts separately within the two source partitions. This diagnostic tests coarse source-partition confounding; it does not define Japan and Taiwan as biological regions.

## Functional evidence and reproductive-herbivory synthesis

Functional evidence was prioritized by organ homology, manipulation geometry and taxonomic proximity. Direct *Cirsium* evidence was preferred when available; close Cardueae or Asteraceae experiments were used where focal-genus manipulation was absent. External effect sizes were not transported to East-Asian taxa.

For orientation, the closest manipulation compared natural nodding and artificially erect capitula in *Cremanthodium campanulatum*, including achene production and pollen vulnerability to water and UV-B. For phyllary architecture, the closest structural manipulation was involucral-spine removal in *Centaurea solstitialis*, combined with direct *Cirsium* evidence linking antagonist access to reproductive loss. For stickiness, direct *Cirsium* neutralization and natural-history studies were prioritized.

We also retained the frozen random-effects meta-analysis of viable or mature seed output under experimentally reduced versus ambient reproductive insect herbivory. Nine within-study contrasts were collapsed to four independent programmes spanning *C. canescens* and *C. occidentale* var. *occidentale*. Numerical means and standard errors for the older Louda & Potvin experiment were recovered from the comparative table in Maron et al. (2002), and that secondary numerical provenance is retained explicitly.

## Historical-environment boundary analysis

Historical climate was used only to bound interpretation of the orientation result. The sole current orientation event linkable from transition to bounded chronology and palaeolocation produced 94 admissible chronology pairs crossed with four regional scenarios (376 scenarios). A broader diagnostic evaluated 17 BIOCLIM variables across six dated lineage contexts, and a separate sea-level diagnostic evaluated three representative contexts.

# Results

## Repeated capitulum reassembly occurs within one young radiation

Thirty-six of 38 sampled Japanese concepts belong to the dominant radiation, yet multiple combinations of orientation, phyllary posture and stickiness occur within it. Orientation required four to six minimum changes across 1,000 bootstrap topologies, phyllary posture exactly three and stickiness exactly five.

## The three traits occupy unequal evolutionary depths and lack synchronized transition histories

Paired comparison on the same 1,000 bootstrap topologies placed phyllary deeper-permissive than stickiness in 1,000/1,000 topologies and deeper than orientation in 993/1,000. Orientation was deeper-permissive than stickiness in 905/1,000. The complete central ordering phyllary < orientation < stickiness occurred in 898/1,000 topologies. Coverage-matched masking retained the central phyllary-deeper pattern while showing overlap in the strict deepest tails.

Zero of three pairwise trait comparisons passed the robust shared-transition-localization rule. Thus, all three components repeatedly changed, but they did not repeatedly behave as one synchronized historical syndrome.

## A common nine-variable environment does not explain all three traits in the same way

The common9 analysis showed different ecological evidence profiles across the three traits rather than one shared abiotic niche signature.

Orientation included 17 taxa (5 downward, 12 upward). Its nine-dimensional omnibus rank was 2138/6188 (34.55%), and the strongest static single-axis separation was GSP at 1005/6188 (16.24%). Thus, simple tip-state environmental separation was not strong in the common9 panel.

Phyllary posture included only four taxa at the primary gate (3 ascending, 1 appressed), giving an omnibus rank of 4/4. Lowering the occurrence gate to one record yielded six taxa, but appressed and spreading states remained singleton lineages and the omnibus rank was 28/30. Present-environment effects are therefore not identifiable for phyllary posture with current public state replication.

Stickiness included 12 taxa with balanced replication (6 sticky, 6 nonsticky). Its nine-dimensional omnibus rank was 116/924 (12.55%). Raw single-axis leads were coherent across precipitation-related variables: sticky minus nonsticky was +1.278 SD for GSP (18/924 = 1.95%), +1.311 SD for BIO12 (22/924 = 2.38%) and +1.048 SD for BIO15 (70/924 = 7.58%). However, no univariate row survived Benjamini-Hochberg correction across the 27-row family (GSP and BIO12 q=0.321). These are therefore exploratory precipitation-related leads rather than confirmatory discoveries.

## Orientation is strongest at the transition level rather than as a static state contrast

The fixed upward-to-downward composite of higher precipitation seasonality and lower annual mean temperature was exceptional among exhaustive count-preserving state maps. The observed ranks were 16/792 (2.02%) for n>=5, 19/1,716 (1.11%) for n>=3 and 4/126 (3.17%) for n>=10. The reverse transition tracked the opposite side of the same strict vector, giving a bidirectional-floor rank of 3/126 (2.38%).

Single-taxon deletion retained positive forward and reverse alignment in 9/9 strict-panel deletions, although exact finite-map exceptionality remained within the declared threshold in 3/9. The result also remained exceptional after latitude/longitude residualization, internal-edge-only scoring and their combination.

The post-result source-partition decomposition showed that the signal was not generated by mean Japan-versus-Taiwan climate differences. The between-partition mean component was opposite to the observed direction and non-exceptional (502/792 = 63.38%), whereas the within-partition component remained positive and exceptional (20/792 = 2.53%). Under the stricter null preserving orientation-state counts separately within the two source partitions, the within-partition component ranked 10/336 (2.98%).

## Reproductive antagonists impose a large fitness cost in *Cirsium*

Across four independent experimental *Cirsium* programmes, reducing reproductive insect herbivory increased viable or mature seed output by a pooled response ratio of 2.674 (95% CI 2.388–2.993). Leave-one-program-out pooled response ratios remained between 2.60 and 2.73 and every 95% interval remained above one. This establishes a large antagonist fitness channel in the genus but does not identify which capitulum trait causes protection.

## Functional evidence supports different ecological interfaces

For orientation, the closest Asteraceae manipulation showed fewer achenes in experimentally erect than naturally nodding heads, while water and UV-B reduced pollen viability and no static pollinator preference between manipulated angles was detected. The leading interpretation is therefore an **abiotic reproductive-exposure interface**.

For phyllary architecture, involucral-spine removal in *Centaurea solstitialis* reduced deterrence of illegitimate Lepidoptera and reduced filled seed production, while direct *Cirsium* evidence shows that antagonist access can strongly reduce seed production. The leading interpretation is a **mechanical access interface**.

For stickiness, direct *Cirsium* neutralization produced benefit in some contexts and null outcomes in others, and arthropod guilds differed in their interaction with sticky structures. Together with the exploratory precipitation-associated niche lead, stickiness is best treated as a **guild-selective arthropod-community interface with context-dependent net effect**, not a universal defence.

## Historical climate does not justify projecting present ecology back to origin

For the sole calendar-bounded orientation event, the fixed present signs matched 99/376 scenarios (26.3%). The broader climate audit yielded 0/324 robust event-level classes across 17 BIOCLIM variables and six dated lineage contexts, while the sea-level audit yielded 0/21 robust classes. These results bound the orientation interpretation: present ecological correspondence is detectable, but one recurring coarse historical climate trigger is not identified.

# Discussion

## Mosaic history and ecological heterogeneity point to the same biological picture

The central result is that three components of one reproductive structure repeatedly changed within the same young radiation, yet their changes occupy different relative depths and do not repeatedly localize to the same branches. A common nine-variable abiotic panel also fails to reduce the three traits to one shared present-day niche axis. These two observations point in the same direction: the capitulum is better described as a mosaic assembled from components that face different ecological problems than as one persistent adaptive syndrome.

This interpretation does not require every trait to have the same kind of ecological evidence. Indeed, forcing identical tests onto all traits would obscure the biology. Orientation is currently best resolved at the transition level; stickiness has replicated tip-state coverage and a coherent but exploratory precipitation-related lead; phyllary posture has strong historical and functional information but insufficient replicated public state coverage for a comparative present-environment test.

## Orientation shows phylogeny-conditioned ecological sorting

Orientation is the strongest bridge between reconstructed history and present ecology. Static downward-versus-upward separation is not exceptional in the common9 panel, yet transition probability aligns with the BIO15-up/BIO1-down vector. This difference matters: the ecological information is associated with where and in which direction orientation changes are placed on the phylogeny, not simply with a large average environmental difference between extant state classes.

The post-result Japan/Taiwan decomposition should be interpreted only as a confounding diagnostic. Japan and Taiwan are source partitions, not biologically privileged regions. Their mean climate difference does not generate the signal, and preserving their observed orientation-state counts does not remove it. The transition-level association is instead carried by taxon-level climatic differences within those source partitions.

BIO15 and BIO1 remain ecological coordinates rather than demonstrated causal agents. The functional literature makes wetting, rain exposure and radiation plausible mechanisms, but those mechanisms require focal manipulation for causal confirmation.

## Stickiness provides an independent ecological lead, but not a climate law

Stickiness is important because it shows that orientation is not the only trait with present ecological information. The balanced 6-versus-6 panel consistently places sticky taxa toward wetter precipitation-related niches on GSP, BIO12 and BIO15. The nine-dimensional omnibus is not exceptional and no single axis survives the 27-row multiplicity correction, so this result should remain an exploratory lead.

Biologically, a precipitation association is compatible with several non-exclusive processes: exudate persistence, arthropod activity, plant productivity or correlated community composition. The existing *Cirsium* manipulation literature therefore remains essential. It indicates that sticky structures can alter interactions with arthropod guilds but that net benefit is context dependent. The present-niche lead narrows where that context dependence may be worth testing; it does not establish an abiotic mechanism by itself.

## Phyllary ecology is a data-resolution problem, not an ecological null result

Phyllary posture remains the clearest example of why ecological evidence must be separated from data availability. Its evolutionary history is estimable, and functional analogues strongly motivate a mechanical access interpretation, but present-environment comparison is currently dominated by one appressed lineage. Adding more environmental variables cannot solve a lack of replicated character states.

The appropriate conclusion is therefore not that phyllary posture lacks ecological structure. Rather, public occurrence and trait-state coverage do not yet identify a taxon-level present-environment effect independently of lineage identity.

## Distinct interfaces make mosaic evolution biologically plausible

The three evidence ladders are different but complementary. Orientation currently reaches history -> transition-level present niche -> functional analogue. Stickiness reaches history -> replicated present niche lead -> direct *Cirsium* manipulation and guild-dependent natural history. Phyllary posture reaches history -> structural access mechanism -> antagonist fitness pathway.

This asymmetry is itself informative. A complex organ can be historically assembled from components whose ecological consequences are expressed through different mechanisms and are observable at different scales. The common9 analysis shows why one shared climate explanation is insufficient; the functional evidence shows why trait-specific ecological interfaces are plausible.

## Historical climate is a boundary rather than the main result

The failure to recover one recurring historical climate class should not dominate the paper. Its role is to prevent overinterpretation of the positive present-day results. Present ecological sorting can be real while the conditions that generated a trait originally remain unresolved. EAzami therefore distinguishes historical assembly, current ecological correspondence and historical selective cause rather than treating them as interchangeable evidence.

# Conclusion

A young *Cirsium* radiation repeatedly reassembled the capitulum from components that do not share one synchronized evolutionary history. Orientation, phyllary posture and involucre stickiness changed repeatedly, occupy unequal relative lineage depths and do not repeatedly localize transitions to the same branches. A common nine-variable abiotic environment does not collapse those traits onto one shared niche axis. Instead, ecological evidence is trait-specific: orientation shows phylogeny-conditioned transition-niche concordance, stickiness shows an independent but exploratory precipitation-related niche lead, and phyllary posture remains limited by replicated public state coverage while retaining a plausible mechanical-access function from experimental analogues.

Together with the large reproductive cost of insect antagonists in *Cirsium*, these results support **mosaic ecological evolution across distinct interfaces** rather than one conserved adaptive syndrome. Causal adaptation claims remain reserved for focal manipulations that connect trait, mechanism and reproductive fitness.