# Mosaic capitulum evolution across distinct ecological interfaces in a young thistle radiation

**Target journal:** *Journal of Evolutionary Biology* — Research Article  
**Status:** V9.1 integrity-revised manuscript draft; supersedes V9 for scientific reporting  
**Running title:** Ecological interfaces and capitulum mosaic evolution

## Abstract

Complex reproductive structures can integrate traits that mediate different ecological interactions and therefore need not share one evolutionary history. We tested this idea in a young East-Asian *Cirsium* radiation by combining public nuclear phylogenomics, authority-backed capitulum states, transition-level present-niche analysis and a homology-restricted synthesis of functional experiments. Thirty-six of 38 sampled Japanese taxon concepts occur in one dominant radiation containing multiple capitulum configurations. Orientation required four to six minimum changes across 1,000 bootstrap topologies, phyllary posture exactly three and involucre stickiness exactly five. Their relative lineage-depth profiles differed: phyllary was deeper-permissive than stickiness in 1,000/1,000 paired topologies and deeper than orientation in 993/1,000; zero of three trait pairs passed a robust shared-transition-localization rule. Orientation additionally tracked a composite present niche of higher precipitation seasonality and lower annual temperature. The strict finite-map rank was 4/126, and 3/126 after combined geography-residualized and internal-edge scoring, although the Japan-only rank was 10/56 and exact exceptionality persisted in only 3/9 single-taxon deletions. Functional evidence supports distinct ecological interfaces: orientation with abiotic reproductive exposure, phyllaries with mechanical access, and sticky involucres with guild-selective arthropod filtering. Across four *Cirsium* experimental programmes, reducing reproductive insect herbivory increased viable or mature seed output 2.674-fold (95% CI 2.388–2.993). Together these results support mosaic ecological evolution of a complex reproductive structure while placing explicit regional and historical bounds on the ecological inference.

**Keywords:** *Cirsium*; capitulum; ecological interface; floral herbivory; mosaic evolution; phylogenetic uncertainty; rapid radiation; trait evolution

# Introduction

Complex reproductive structures must function as integrated wholes, yet their components can interact with different parts of the environment. Floral orientation can alter exposure to rain, radiation and pollinators; phyllaries and spines can alter physical access by mutualists and antagonists; sticky surfaces can deter, trap or redirect arthropods. Treating such a structure as one adaptive syndrome therefore requires more than present-day co-occurrence of traits. The component histories themselves must be sufficiently synchronized, or there must be evidence that a common ecological process repeatedly organizes them.

Studies of phenotypic integration and modularity have long emphasized that covariance among extant traits need not imply a single underlying developmental or evolutionary process (Klingenberg, 2014; Goswami et al., 2014; Felice & Goswami, 2018; Zelditch & Goswami, 2021). Floral ecology adds a further complication because multiple agents can impose reinforcing, opposing or context-dependent selection on the same reproductive structure. Pollinators, florivores, predispersal seed predators and abiotic stress can therefore generate a selection mosaic rather than one universally dominant driver.

Rapid radiations provide a useful setting for testing this idea. When substantial phenotype diversity occurs within shallow common ancestry, component traits can be compared without confounding every difference with deep lineage separation. If different traits repeatedly change at different positions and depths in the same radiation, a whole-organ syndrome becomes a poor historical description even if extant heads remain functionally integrated.

The thistle genus *Cirsium* is well suited to this problem. Broad nuclear phylogenomics recovered rapid Pleistocene radiations including a dominant Japanese radiation with extensive gene-tree discordance (Moreyra et al., 2025). Independent East-Asian work documents recent divergence, cytological heterogeneity and reticulate history. Within the capitulum, head orientation ranges from erect or upward-facing to nodding or downward-facing; phyllaries differ in posture and armature; and involucres vary from strongly sticky to effectively nonsticky. These are homologous components of one reproductive structure but they plausibly regulate different ecological interfaces.

Existing functional work makes that ecological heterogeneity concrete. In a close Asteraceae system, experimentally changing capitulum orientation altered achene production, while water and UV-B exposure reduced pollen viability and no static pollinator preference between manipulated angles was detected. In Cardueae, manipulating involucral spines altered access by illegitimate visitors and final seed production. Within *Cirsium*, reproductive insect herbivory can impose large seed-fitness costs, while sticky involucral exudates show benefit in some contexts, no detectable benefit in others and different effects among arthropod guilds.

Here we ask four linked questions. First, do orientation, phyllary posture and stickiness each show repeated change within the young radiation? Second, do the three traits occupy similar evolutionary depths and repeatedly localize changes to the same branches? Third, does the best-resolved trait, orientation, show a transition-level relationship with present ecological niche, and how sensitive is that relationship to regional restriction and taxon deletion? Fourth, do independent functional experiments support distinct ecological interfaces for the three traits, and is the antagonist pathway strong enough to matter for reproductive fitness in *Cirsium*?

Our central claim is deliberately narrower than adaptive convergence: **a complex reproductive structure can be historically reassembled from traits that repeatedly change while mediating different abiotic and biotic interfaces**.

# Materials and Methods

## Nuclear scaffold and trait states

The focal historical panel followed the 38 Japanese taxon concepts represented by Moreyra et al. (2025). We used an independently reconstructed Compositae1061-compatible nuclear phylogram. A frozen 241-locus starting set yielded 236 quality-controlled loci, 176 rootable with safflower, and a concatenated alignment of 161,654 bp. Maximum-likelihood inference used IQ-TREE 2 with ModelFinder, 1,000 ultrafast-bootstrap replicates and 1,000 SH-aLRT replicates. Branch lengths were substitutions per site and were not interpreted as calendar time.

Thirty-six of the 38 sampled Japanese concepts occur in the dominant radiation. We analysed three source-backed discrete traits: capitulum orientation, phyllary posture and involucre stickiness. Missing and ambiguous records remained unresolved. Final historical coverage was 20 concepts for orientation, 10 for phyllary posture and 13 for stickiness.

## Minimum-change reconstruction and relative lineage depth

For the maximum-likelihood topology and each of 1,000 bootstrap topologies, we calculated the unordered parsimony minimum for each trait. These are lower bounds on required state changes, not counts of independent origins or adaptive convergence events.

For every globally minimum-cost Sankoff history we calculated bounds on mean relative lineage depth. For a tree with \(N\) admitted tips and an edge subtending \(d\) descendants,

\[
D=\frac{N-d}{N-1}.
\]

Terminal edges have \(D=1\); smaller values permit deeper placement. Trait depths were compared directly on the same 1,000 bootstrap topologies. A separate masking sensitivity equalized observed-state coverage to test whether the central depth ordering could arise simply from different numbers of resolved concepts.

## Shared-transition localization

An equal-rates Mk diagnostic estimated branch-wise transition probability and excess over branch prior. Pairwise Spearman correlations compared transition localization among the three traits. We paired the branch-length-aware maximum-likelihood result with a topology-only sensitivity in which non-root branches were assigned equal length. A pair passed the descriptive robust shared-localization rule only when positive localization persisted under both treatments.

## Orientation present-niche analysis

Orientation had the strongest state-diverse ecological coverage. Spatially thinned occurrence records with complete CHELSA extraction were summarized to taxon environmental centroids.

The upward-to-downward composite `BIO15 up + BIO1 down` was **fixed after the earlier East-Asian state-comparison analysis identified stable positive BIO15 and negative BIO1 directions**. It is therefore a post-result focused hypothesis, not a prospectively preregistered climatic vector. Once fixed, no additional climate variables were searched to strengthen this transition-level test.

For each accepted topology, a symmetric two-state CTMC provided edge probabilities of upward-to-downward and downward-to-upward change. Brownian reconstruction of standardized taxon environmental centroids supplied branch environmental differences. We calculated a transition-weighted composite statistic for the fixed BIO15/BIO1 vector.

Every count-preserving orientation state map was enumerated. We ranked the observed statistic within complete finite map sets for n≥5, n≥3 and strict n≥10 occurrence panels. Sensitivity analyses included a Japan-only n≥5 panel, deletion of each strict-panel taxon in turn, linear latitude/longitude residualization, internal-edge-only scoring and their combined stress. Exact finite-map fractions are conditional ranks, not biological-replicate P values.

## Functional evidence synthesis

Functional evidence was prioritized by similarity in organ, manipulation geometry and taxonomic context. Direct *Cirsium* evidence was preferred when available; close Cardueae or Asteraceae experiments were used where direct focal-genus manipulation was absent. Effect sizes from external taxa were not transported to East-Asian *Cirsium*.

For orientation, the closest manipulation compared natural nodding and artificially erect capitula in *Cremanthodium campanulatum* (Asteraceae; DOI 10.1080/17550874.2012.702793), measuring achene production, pollen vulnerability to water and UV-B, pollinator preference and internal floral temperature. For phyllary architecture, the closest structural manipulation was involucral-spine removal in *Centaurea solstitialis* (Cardueae; DOI 10.2307/3672545), combined with direct *Cirsium* evidence linking antagonist access to reproductive loss. For stickiness, we prioritized direct *Cirsium* neutralization and natural-history studies, including Willson, Anderson & Thomas (1983) and Thomas (2003, 2007).

## Reproductive-herbivory meta-analysis

We used the frozen random-effects meta-analysis of viable or mature seed output under experimentally reduced versus ambient insect herbivory:

\[
RR=\frac{\text{seed output under reduced herbivory}}{\text{seed output under ambient herbivory}}.
\]

Nine within-study contrasts were collapsed to four independent data-generation programmes covering *C. canescens* and *C. occidentale* var. *occidentale*: Louda & Potvin (1995), Maron et al. (2002), West & Louda (2018) and Russell et al. (2025). **The numerical means and standard errors for the older Louda & Potvin experiment were recovered from the comparative table in Maron et al. (2002), which reports that independent experiment; this secondary numerical provenance is retained explicitly and treated as a sensitivity limitation rather than as direct extraction from the 1995 primary paper.** Multiple contrasts from the same programme were collapsed before across-study pooling.

## Historical-environment boundary analysis

Historical climate was retained only as a boundary on the orientation interpretation. The sole current orientation event that could be linked from transition to bounded chronology and palaeolocation generated 94 admissible chronology pairs crossed with four regional scenarios (376 scenarios). We tested whether the fixed present orientation signs (`BIO15 positive`, `BIO1 negative`) persisted through that envelope. A broader diagnostic evaluated 17 BIOCLIM variables across six dated lineage contexts, and a separate global sea-level diagnostic evaluated three representative lineage contexts.

# Results

## Repeated capitulum reassembly occurs within one young radiation

Thirty-six of 38 sampled Japanese concepts belong to the dominant radiation, yet multiple combinations of orientation, phyllary posture and stickiness occur within it. Orientation required six minimum changes on the maximum-likelihood tree and four to six across the 1,000 bootstrap topologies, with a median of five. Phyllary posture required exactly three changes across the topology ensemble and stickiness exactly five.

## The three traits occupy unequal evolutionary depths

Bootstrap-median relative-depth envelopes were 0.795–0.994 for orientation, 0.695–1.000 for phyllary posture and 0.937–0.954 for stickiness. Paired comparison on the same 1,000 bootstrap topologies placed phyllary deeper-permissive than stickiness in 1,000/1,000 topologies and deeper than orientation in 993/1,000. Orientation was deeper-permissive than stickiness in 905/1,000, with seven ties. The complete central ordering `phyllary < orientation < stickiness` occurred in 898/1,000 topologies. Coverage-matched masking retained the central phyllary-deeper pattern while showing overlap in the strict deepest tails.

## Capitulum components do not repeatedly change as one synchronized syndrome

Zero of three pairwise trait comparisons passed the robust shared-transition-localization rule. Combined with unequal depth profiles, this supports mosaic historical assembly: components of one reproductive structure repeatedly changed, but not as one synchronized historical unit.

## Orientation tracks a present ecological regime, with a regional boundary

The fixed upward-to-downward composite of higher precipitation seasonality and lower annual mean temperature was exceptional among exhaustive count-preserving state maps in the full East-Asian panels. The observed ranks were 16/792 (2.02%) for n≥5, 19/1,716 (1.11%) for n≥3 and 4/126 (3.17%) under the strict n≥10 gate. The reverse direction tracked the opposite side of the same strict vector, giving a bidirectional-floor rank of 3/126 (2.38%).

The signal was **not exceptional when the n≥5 analysis was restricted to Japan alone**: 10/56 maps (17.86%) were at least as extreme. The ecological correspondence is therefore regional in scope and depends on the broader East-Asian contrast rather than being a strong Japan-internal climatic gradient.

Single-taxon deletion retained positive forward and reverse alignment in all 9/9 strict-panel deletions, but exact finite-map exceptionality remained within the declared threshold in only **3/9** deletions. Thus, the **direction** of the composite relationship is not driven by one taxon, whereas its exact extremeness is taxon-sensitive at current sample size.

The full-panel upward-to-downward result remained exceptional after linear latitude/longitude residualization (5/126 = 3.97%), after internal-edge-only scoring (3/126 = 2.38%) and after combining both stresses (3/126 = 2.38%). The supported claim is therefore a regionally bounded, directionally stable East-Asian present-niche relationship, not a universal or Japan-internal climate rule.

## Reproductive antagonists impose a large fitness cost in *Cirsium*

Across four independent experimental *Cirsium* programmes, reducing reproductive insect herbivory increased viable or mature seed output by a pooled response ratio of **2.674** (95% CI **2.388–2.993**). This corresponds to an estimated 62.6% reduction in potential viable or mature seed output under ambient herbivory (95% interval 58.1–66.6%). Between-study heterogeneity for this narrowly harmonized estimand was low (`I² = 1.0%`). Leave-one-program-out pooled response ratios remained between 2.60 and 2.73 and every 95% interval remained above one.

This establishes a large antagonist fitness channel in *Cirsium* but does not identify which capitulum trait causes protection.

## Functional evidence maps the traits onto different ecological interfaces

For orientation, the closest Asteraceae manipulation showed that experimentally erect heads produced fewer achenes than naturally nodding heads, while water and UV-B reduced pollen viability. No pollinator preference between manipulated angles and no meaningful orientation-driven internal-temperature difference were detected. Together with the East-Asian niche result, the leading ecological interpretation is an **abiotic reproductive-exposure filter**, especially through wetting/rain and radiation exposure.

For phyllary architecture, involucral-spine removal in *Centaurea solstitialis* reduced deterrence of illegitimate Lepidoptera and reduced filled seed production by 22%, without increasing legitimate bee/fly visitation. Within *Cirsium*, antagonist access to reproductive heads is associated with large reductions in seed production. The leading interpretation is therefore a **mechanical access filter**.

Stickiness showed a different pattern. Direct *Cirsium* neutralization produced benefit in one context and null outcomes in others, while arthropod guilds differed in whether they contacted, avoided, bypassed or used sticky structures. Sticky involucres are therefore best interpreted as a **guild-selective arthropod-community filter with context-dependent net benefit**, not a universal seed-predator barrier.

## Historical climate does not support projection of the present regime to origin

For the sole calendar-bounded orientation event, the fixed present signs matched **99/376 scenarios (26.3%)**. Match frequency differed among regional scenarios: Taiwan 20/94 (21.3%), Ryukyu corridor 9/94 (9.6%), southern Japan 41/94 (43.6%) and the East-Asian core corridor 29/94 (30.9%). Only 6/94 chronologies matched all four regions and 14/94 matched at least three of four.

The broader climate audit yielded **0/324 robust event-level classes** across 17 BIOCLIM variables and six dated lineage contexts, while the sea-level audit yielded **0/21 robust event-metric classes**. These results do not show that climate was irrelevant. They show that current public data do not support projection of one recurring coarse climatic or eustatic regime onto the historical origin of the focal trait states.

# Discussion

## Mosaic ecological evolution links history to distinct interfaces

The central result is positive: orientation, phyllary posture and stickiness all changed repeatedly within one young radiation, but their changes occupy different relative depths and do not repeatedly localize to the same branches. The best available functional evidence also maps the three traits onto different interfaces between the capitulum and its environment.

This combination provides a coherent ecological explanation for mosaic history. The capitulum must simultaneously present flowers to mutualists, protect reproductive tissues from abiotic exposure, restrict damaging access to developing seeds and interact with a heterogeneous arthropod community. These pressures need not covary among regions or lineages. Consequently, different components can be reorganized at different points in the radiation while the extant capitulum remains functionally integrated as one reproductive unit.

## Orientation is an East-Asian ecological pattern, not a universal climate rule

Orientation provides the strongest focal bridge between history and present ecology, but its scope is now explicit. The composite `BIO15 up + BIO1 down` relationship is unusual in the full East-Asian state-map universe and remains after simple geographic residualization and internal-edge restriction. However, it is not exceptional in the Japan-only analysis, and exact exceptionality survives only 3/9 single-taxon deletion panels despite 9/9 directional stability.

The biologically defensible interpretation is therefore **regional ecological sorting** rather than a universal climate rule. Taiwan and the broader East-Asian contrast contribute materially to the pattern. This regional boundary is informative because it suggests that orientation ecology is organized at a geographic scale broader than within-Japan variation alone.

The composite itself should also be interpreted cautiously. It was fixed after earlier state-comparison results identified stable BIO15-positive and BIO1-negative directions, so it is a post-result focused hypothesis rather than a prospective preregistration. The finite-map analysis is valuable because it asks a sharper question after that discovery, but it should not be presented as independent confirmation of a hypothesis specified before all ecological results were known.

Mechanistically, BIO15 and BIO1 are best regarded as ecological coordinates rather than direct causal agents. The closest manipulation suggests a more proximal route involving exposure of pollen and reproductive tissues to water and UV-B. Direct *Cirsium* angle manipulation is still required to establish that mechanism in the focal genus.

## Antagonist pathways are strong but structurally heterogeneous

The meta-analysis shows that reproductive insects can impose a large seed-fitness cost in *Cirsium*. That establishes antagonism as an evolutionarily consequential pathway. It does not imply that every structural trait evolved as defence.

Phyllary architecture and stickiness illustrate why the pathway must be decomposed. Phyllaries plausibly regulate **mechanical access**, whereas stickiness behaves as a **community filter** whose net effect depends on guild composition. These are different ecological mechanisms even when both influence antagonists. Their distinct histories are therefore biologically plausible without invoking one generic defence syndrome.

The meta-analytic magnitude also has a geographic limitation: all four directly harmonizable programmes concern North American *Cirsium*. We therefore use the pooled RR only to establish a genus-level antagonist fitness channel, not to transfer a numerical effect size to East-Asian populations. The Louda & Potvin numerical inputs additionally come through the comparative table in Maron et al. (2002), which is why that provenance is made explicit in Methods.

## Historical non-persistence is a boundary, not the headline

The historical climate analysis prevents a stronger claim that the present orientation regime was also the origin regime. Only 99/376 chronology-by-region scenarios match the present BIO15/BIO1 signs, and the broader 17-BIOCLIM and sea-level audits recover no robust recurring class.

This negative boundary does not displace the positive ecological result. Instead it separates **present ecological organization** from **historical selective cause**. The first is detectable for orientation at an East-Asian regional scale; the second remains unresolved with current public chronology, palaeolocation and palaeoenvironmental resolution.

## Conclusion

A young East-Asian *Cirsium* radiation repeatedly reassembled the capitulum from components that do not share one synchronized evolutionary history. Orientation, phyllary posture and involucre stickiness changed repeatedly, occupy unequal relative lineage depths and do not repeatedly localize transitions to the same branches. Functional evidence further points to different ecological roles: orientation as an abiotic reproductive-exposure interface, phyllaries as a mechanical access interface and stickiness as a context-dependent arthropod-community interface. Reproductive antagonists can impose a large seed-fitness cost in *Cirsium*, making these biotic pathways evolutionarily consequential.

The orientation–climate association is real but bounded: it is strongest across the broader East-Asian panel, is not exceptional in the Japan-only test, and has taxon-sensitive exact extremeness despite stable direction. The present regime also does not persist robustly across the historical uncertainty envelope. We therefore interpret capitulum diversification as **mosaic ecological evolution across distinct interfaces**, while restricting causal claims to the scale and geography actually supported by the data.

## Reference anchors to synchronize before submission

The final bibliography should be populated from the repository source registries. Core cited anchors include: Moreyra et al. (2025); Chang et al. (2025, 2026); Klingenberg (2014); Goswami et al. (2014); Felice & Goswami (2018); Zelditch & Goswami (2021); Louda & Potvin (1995); Maron et al. (2002); West & Louda (2018); Russell et al. (2025); Willson, Anderson & Thomas (1983); Thomas (2003, 2007); the *Cremanthodium campanulatum* orientation manipulation (DOI 10.1080/17550874.2012.702793); the *Centaurea solstitialis* involucral-spine manipulation (DOI 10.2307/3672545); and the direct *Cirsium pitcheri* antagonist-fitness study (DOI 10.1016/j.gecco.2020.e00945).