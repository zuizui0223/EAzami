# Repeated reassembly of a complex reproductive phenotype across evolutionary depths and ecological scales in a young thistle radiation

**Target journal:** *Journal of Evolutionary Biology* — Research Article  
**Status:** V9.6 scale-conditioned ecology manuscript draft  
**Running title:** Unequal-depth capitulum reassembly

## Abstract

Complex phenotypes may retain recognizable component traits without preserving one fixed historical organization or ecological mapping. We tested this in the capitulum of a young *Cirsium* radiation by comparing orientation, phyllary posture and involucre stickiness under shared phylogenetic uncertainty. Thirty-six of 38 sampled Japanese taxon concepts occur within one dominant radiation. Orientation required four to six minimum state changes across 1,000 bootstrap topologies, phyllary posture exactly three and stickiness exactly five. Their histories were stratified across unequal relative lineage depths: phyllary was deeper-permissive than stickiness in 1,000/1,000 paired topologies and deeper than orientation in 993/1,000, while orientation was deeper-permissive than stickiness in 905/1,000. Zero of three trait pairs showed robust shared transition localization. Ecological correspondence was likewise scale-conditioned rather than syndrome-wide. Static orientation classes were weakly separated, reconstructed orientation transitions aligned with higher precipitation seasonality and lower temperature, global among-taxon image angle aligned with annual precipitation, and within-taxon image angle showed a supported temperature association in the opposite direction. A preregistered external-taxon confirmation stopped before climate extraction because strict occurrence-quality control left only one eligible upward taxon. Thus repeated capitulum differentiation is historically mosaic, while ecological correspondence depends on trait, biological scale and phenotype representation.

**Keywords:** *Cirsium*; capitulum; evolutionary depth; mosaic evolution; phenotypic integration; phylogenetic uncertainty; rapid radiation; trait evolution

# Introduction

Complex phenotypes are structured systems rather than arbitrary sets of measurements. Their component traits can covary, share developmental context and jointly determine organismal function (Klingenberg, 2014; Goswami et al., 2014; Zelditch & Goswami, 2021). Yet observing an integrated phenotype in extant organisms does not establish that its components share one evolutionary history. Traits that function together today may have changed at different times, on different branches and under different ecological circumstances.

This distinction is central to studies of phenotypic integration and modularity. Functional difference alone cannot establish historical independence: developmental coupling, pleiotropy, correlational selection or repeated whole-organ restructuring could synchronize the evolution of traits with different immediate functions. Conversely, present-day integration does not require synchronized historical change, and mosaic evolution can emerge through reorganization of component histories rather than loss of component identity (Felice & Goswami, 2018). Whether a complex phenotype preserves one historical organization is therefore an empirical question.

Three quantities separate these alternatives. **Recurrence** asks how many state changes are minimally required by observed tip states. **Evolutionary depth** asks where those changes can be placed within the hierarchy of lineage divergence. **Shared transition localization** asks whether different traits repeatedly change on the same branches. A phenotype can therefore be repeatedly modified yet remain historically synchronized, or it can be repeatedly reassembled from components whose changes occupy different depths and branches. Because ancestral-state conclusions can be sensitive to phylogenetic uncertainty, these quantities should be compared across the same topology ensemble rather than on one preferred tree alone (Duchêne & Lanfear, 2015).

Rapid radiations provide a strong test because large phenotypic differences occur within relatively shallow common ancestry. In *Cirsium*, recent nuclear phylogenomics recovered a dominant Japanese radiation with extensive gene-tree discordance, while capitula differ markedly in orientation, phyllary posture and involucre stickiness (Moreyra et al., 2025). These are homologous components of one reproductive head, making the radiation a useful system for asking whether component identity is retained while historical organization is reconfigured.

Ecological interpretation adds a second issue. Trait–environment correspondence may depend both on biological scale and on how phenotype is represented. A static difference among extant state classes may be weak even when reconstructed evolutionary transitions align with environmental change, while within-taxon variation can show a different environmental slope from among-taxon differentiation. Conversely, a present-day association need not identify the environment of trait origin. We therefore treat ecological analyses as tests of scale- and representation-dependence, not as a requirement that all three traits share one climatic driver.

Here we ask three questions. First, did orientation, phyllary posture and stickiness each change repeatedly within the young radiation? Second, were those changes distributed similarly across evolutionary depth and branch localization, as expected under a synchronized whole-capitulum history? Third, is ecological correspondence scale-invariant, or does it change among static taxon states, within-taxon variation, among-taxon differentiation and phylogeny-conditioned transitions?

Our primary prediction is historical. If the capitulum behaves as one persistent evolutionary unit, its component traits should show broadly similar placement of repeated change. If instead the capitulum has been repeatedly reassembled, recurrence can be shared while depth and transition localization diverge among traits.

# Materials and Methods

## Nuclear scaffold and trait states

The historical panel followed 38 Japanese taxon concepts represented by the nuclear phylogenomic framework of Moreyra et al. (2025). We used an independently reconstructed Compositae1061-compatible phylogram based on a frozen 241-locus starting set, yielding 236 quality-controlled loci, 176 rootable loci and a concatenated alignment of 161,654 bp. Maximum-likelihood inference used IQ-TREE 2.4.0 (Minh et al., 2020) with ModelFinder (Kalyaanamoorthy et al., 2017), 1,000 ultrafast-bootstrap replicates (Hoang et al., 2018) and 1,000 SH-aLRT replicates. Branch lengths were substitutions per site and were not interpreted as calendar time.

Thirty-six of the 38 sampled concepts occur within the dominant radiation. We analysed three source-backed discrete capitulum traits: orientation, phyllary posture and involucre stickiness. Missing and ambiguous states remained unresolved. Historical coverage comprised 20 concepts for orientation, 10 for phyllary posture and 13 for stickiness.

## Recurrence, evolutionary depth and shared transition localization

For the maximum-likelihood topology and each of 1,000 bootstrap topologies, we calculated unordered parsimony minima. These values are lower bounds on required state change and were not interpreted as counts of independent adaptive origins.

For every globally minimum-cost Sankoff history, relative lineage depth was defined for an edge subtending \(d\) descendants in a tree with \(N\) admitted tips as

\[
D=\frac{N-d}{N-1}.
\]

Terminal edges have \(D=1\), whereas smaller values permit deeper placement. Trait depth was compared directly on the same 1,000 bootstrap topologies. Because trait coverage differed, a deterministic masking sensitivity equalized observed-state coverage before repeating paired depth comparisons. The depth analyses were executed under Python 3.11 with Biopython 1.85; bootstrap trees are treated as topology-sensitivity realizations, not independent biological replicates.

Shared-transition localization was evaluated with a branch-length-aware equal-rates Mk diagnostic and a topology-only sensitivity. A trait pair passed the robust descriptive rule only when positive localization overlap persisted under both treatments. The Mk layer is used as a diagnostic of transition localization rather than as proof of independent origins or adaptation (Lewis, 2001).

## Common nine-variable present-environment comparison

All three traits were passed through one trait-blind present-environment workflow. Public GBIF occurrences were source-name checked, subjected to coordinate-quality control and thinned at 0.1 degrees. Taxon medians were extracted for BIO1, BIO4, BIO12, BIO15, short-wave radiation (RSDS), vapour-pressure deficit (VPD), surface wind, growing-season precipitation (GSP) and net primary productivity (NPP). The climatic variables were derived from the CHELSA framework (Karger et al., 2017) and the frozen project environmental assets.

The primary gate required at least three thinned occurrences per taxon. For each trait, observed multivariate state separation was ranked among every state-label map preserving observed state counts. All evaluable trait-by-environment univariate rows were retained and Benjamini-Hochberg correction was applied across the 27-row family. No orientation-specific sign hypothesis was transferred to phyllary posture or stickiness.

## Cross-scale orientation audit and external-confirmation ceiling

To test whether the orientation–environment relationship was scale-invariant, we compared the EAzami state/transition results with the already-frozen Azami image-based orientation atlas. The Azami endpoint is a signed head-axis angle relative to EXIF-oriented image vertical (0° upward, 180° downward), not a gravity-referenced inclinometer measurement. We therefore treated it as a related presentation phenotype rather than an interchangeable measurement of botanical head orientation. Existing Azami among- and within-taxon environmental coefficients were audited without refitting or selecting predictors after viewing the EAzami result.

We also ran a prospectively frozen external-taxon confirmation programme. Trait states were first assembled without climate data, followed by a source-complete Flora of China/NIBR census and strict GBIF occurrence-quality gates requiring explicit coordinate uncertainty <=10 km, deterministic 0.1-degree thinning, at least three thinned records per taxon and at least two taxa per orientation state. The preregistered ecological vector was higher BIO15 and lower BIO1 for downward versus upward orientation. Environmental endpoints were to be opened only if the occurrence/state-replication gate passed.

## Orientation transition-level ecological analysis

Orientation additionally had sufficient state-diverse public coverage for a phylogeny-conditioned transition analysis. After an earlier state comparison identified stable positive BIO15 and negative BIO1 directions, the upward-to-downward composite BIO15 up + BIO1 down was fixed as a **post-result focused hypothesis**, not a preregistered vector.

For each accepted topology, a symmetric two-state CTMC supplied edge transition probabilities and Brownian reconstruction supplied branch environmental differences. A transition-weighted composite statistic was ranked among every count-preserving orientation state map. Coverage sensitivities, single-taxon deletion, latitude/longitude residualization and internal-edge-only scoring were retained. The finite-map fractions are exhaustive conditional ranks, not \(P\) values from independent biological replicates.

A later Japan/Taiwan source-partition diagnostic tested coarse data-source geography only; the two source partitions were not interpreted as biological regions.

## Functional evidence and historical boundary

Functional evidence was ranked by organ homology, manipulation geometry and taxonomic proximity. For orientation, the closest direct angle manipulation is in *Cremanthodium campanulatum* (Niu & Sun, 2013), with *Cirsium purpuratum* studies providing within-genus pollination context (Ohashi & Yahara, 1998; Makino et al., 2007). For phyllary architecture, we used a close-Cardueae spine manipulation (Agrawal et al., 2000) together with direct *Cirsium* antagonist-to-seed evidence (Gijsman et al., 2020). For stickiness, we prioritized direct *Cirsium* exudate occlusion/neutralization and arthropod-guild studies (Willson et al., 1983; Thomas, 2003, 2007).

A frozen random-effects synthesis summarized mature or viable seed output in four independent *Cirsium* experimental programmes that reduced reproductive insect herbivory (Louda & Potvin, 1995; Maron et al., 2002; West & Louda, 2018; Russell et al., 2025). Numerical means and standard errors for the older Louda–Potvin experiment were recovered from the comparative table of Maron et al. (2002), and this secondary numerical provenance is retained explicitly.

Historical climate was retained only as a boundary on causal interpretation of the orientation result. The sole event linkable to bounded chronology and palaeolocation generated 376 chronology-by-region scenarios; broader climate and sea-level audits were treated as sensitivity analyses rather than headline results. Palaeoclimate surfaces came from PALEO-PGEM (Barreto et al., 2023).

# Results

## Repeated change occurs within one young radiation

Thirty-six of 38 sampled Japanese concepts occur in the dominant radiation, yet multiple combinations of orientation, phyllary posture and stickiness are present within it. Orientation required four to six minimum state changes across 1,000 bootstrap topologies, phyllary posture exactly three and stickiness exactly five. Repeated differentiation is therefore a within-radiation property rather than a contrast among ancient major lineages (Figure 1).

## Repeated histories are stratified across evolutionary depth

Paired comparison on the same 1,000 bootstrap topologies showed a strong central depth ordering. Phyllary posture was deeper-permissive than stickiness in 1,000/1,000 topologies and deeper-permissive than orientation in 993/1,000. Orientation was deeper-permissive than stickiness in 905/1,000, with seven ties. The complete central ordering

\[
phyllary < orientation < stickiness
\]

where smaller values indicate deeper permitted history, occurred in 898/1,000 topologies. Coverage-matched masking retained the central phyllary-deeper pattern against matched medians, while strict tails still overlapped (Figure 2).

Thus the three traits are not merely recurrent. Their repeated histories occupy different layers of the radiation's topology.

## Component changes are not repeatedly synchronized on the same branches

Zero of three pairwise trait comparisons passed the robust shared-transition-localization rule. The traits therefore differ both in relative depth and in the branches to which change is repeatedly assigned (Figure 3).

Together, recurrence, paired depth ordering and lack of shared localization support **mosaic historical reassembly** rather than one persistent synchronized whole-capitulum history.

## Static environmental structure is not shared across the three traits

The common nine-variable analysis did not recover one shared abiotic niche signature. Orientation included 17 taxa (5 downward, 12 upward) and had an omnibus rank of 2138/6188 (34.55%). Phyllary posture included only four taxa at the primary gate (3 ascending, 1 appressed), leaving present-environment effects unresolved because state replication was insufficient. Stickiness included 12 taxa with balanced replication (6 sticky, 6 nonsticky) and had an omnibus rank of 116/924 (12.55%). Sticky taxa showed raw precipitation-related leads for GSP (18/924 = 1.95%), BIO12 (22/924 = 2.38%) and BIO15 (70/924 = 7.58%), but none survived Benjamini-Hochberg correction across the 27-row family.

The three historical traits therefore do not collapse onto one common present-day climatic syndrome.

## Orientation is ecologically informative at the transition level

Orientation was weak as a static common9 state contrast but informative when represented as reconstructed evolutionary change. The fixed upward-to-downward BIO15-up/BIO1-down composite ranked 16/792 (2.02%) for n>=5, 19/1,716 (1.11%) for n>=3 and 4/126 (3.17%) for n>=10. The reverse transition tracked the opposite side of the same strict vector, yielding a bidirectional-floor rank of 3/126 (2.38%).

Positive forward and reverse alignment persisted in 9/9 single-taxon deletions, although exact finite-map exceptionality persisted in 3/9. The result also remained exceptional after latitude/longitude residualization, internal-edge-only scoring and their combination.

The Japan/Taiwan source-partition diagnostic did not explain the signal. The source-partition mean component was opposite to the observed direction and non-exceptional (502/792 = 63.38%), whereas the within-partition component remained positive and exceptional (20/792 = 2.53%). Preserving source-partition orientation-state counts retained the within-partition result (10/336 = 2.98%).

Thus ecological information depends on representation: orientation is weak as a static tip-state contrast but structured when environmental change is aligned to reconstructed evolutionary transitions.

## Orientation ecology is not scale invariant

The frozen Azami image atlas provided an independent scale comparison, although not a prospective held-out test. At the among-taxon level, image-based presentation angle was positively associated with annual precipitation (BIO12; beta = +0.304359). Within taxa, annual precipitation was unsupported (beta = +0.0053264, q = 0.823), whereas annual mean temperature was positively associated with a more downward image presentation (BIO1 beta = +0.0171503, q = 0.04753; spatial beta = +0.0265374, permutation P = 0.002). This within-taxon BIO1 direction is opposite to the East-Asian transition-level association of downward orientation with lower BIO1. Within-taxon BIO15 was weakly negative (beta = -0.0076180, q = 0.183), also numerically opposite to the East-Asian downward-associated higher-BIO15 direction.

The prospectively frozen external-taxon programme did not yield an ecological coefficient. Its source-complete V2 census recovered all 46 Flora of China taxa, but the frozen 13-taxon orientation panel (3 downward, 10 upward) collapsed under strict GBIF occurrence-quality control to a single eligible taxon, *Cirsium vulgare* (upward; 16 thinned records). Because the preregistered minimum of two taxa per state was not met, BIO1 and BIO15 were never extracted. This is an occurrence-metadata resolution ceiling, not an ecological null result.

Together, the evidence shows that orientation–environment correspondence is scale- and representation-dependent rather than one repeated climate coefficient (Figure 4).

## Functional evidence supports biological plausibility, not the headline novelty

Functional studies are consistent with orientation influencing reproductive exposure to wetting and radiation (Niu & Sun, 2013), phyllary architecture altering mechanical access by legitimate visitors and antagonists (Agrawal et al., 2000; Gijsman et al., 2020), and sticky involucres modifying arthropod interactions in a context-dependent manner (Willson et al., 1983; Thomas, 2003, 2007). Across four independent *Cirsium* experimental programmes, reducing reproductive insect herbivory increased viable or mature seed output 2.674-fold (95% CI 2.388–2.993), establishing antagonism as a substantial reproductive-fitness pathway in the genus.

These results make trait-specific ecological pathways plausible but do not establish that those pathways caused the historical transitions reconstructed here.

## Present ecological correspondence does not identify historical origin environment

For the sole calendar-bounded orientation event, the present BIO15/BIO1 signs matched 99/376 historical chronology-by-region scenarios (26.3%). The broader audit yielded 0/324 robust event-level climate classes and the sea-level audit 0/21 robust classes. Historical climate is therefore retained as a boundary on interpretation, not as the principal result.

# Discussion

## Repeated reassembly, not merely repeated lability

The strongest result is historical. All three capitulum traits repeatedly changed within the same young radiation, but their histories are not organized in the same way. They differ systematically in relative lineage depth and fail to repeatedly localize changes to the same branches. This is stronger than saying that the traits are simply labile: recurrence itself is stratified across the history of the radiation.

The result is also not a tautological consequence of different trait functions. Traits with different functions could still change together through developmental coupling, pleiotropy, correlational selection or repeated whole-organ reorganization. The absence of synchronized history is therefore an empirical property of this radiation and complements broader work showing that phenotypic modules can be reorganized over evolutionary time (Goswami et al., 2014; Felice & Goswami, 2018).

## Component identity can persist while historical organization changes

Orientation, phyllary posture and stickiness remain recognizable homologous properties of the capitulum across the radiation. What changes is their historical relationship to one another. This distinction between **component identity** and **organizational invariance** provides a useful way to describe complex-phenotype evolution (Klingenberg, 2014; Zelditch & Goswami, 2021).

A complex reproductive structure can remain biologically recognizable while its constituent histories are repeatedly reorganized. In this sense, capitulum evolution is structured but not historically scale-invariant: the same components recur, but their placement across lineage depth and branch history does not preserve one fixed architecture.

## Evolutionary depth adds a missing axis to studies of repeated trait change

Comparative studies often emphasize the number or direction of repeated changes. The present analysis shows that recurrence alone can hide a second dimension: where those changes lie in the hierarchy of lineage divergence. Two traits can both recur repeatedly while one is consistently deeper-permissive and another concentrated toward shallower history.

Because the depth comparisons are paired on the same 1,000 bootstrap topologies and checked under coverage matching, the ordering cannot be reduced to unequal tree uncertainty or unequal numbers of scored taxa. Relative evolutionary depth therefore adds historical structure that change counts alone do not capture. It remains a topology-based coordinate, not an event age or evolutionary rate.

## Ecological correspondence is scale- and representation-dependent

The orientation result extends the historical argument into ecology. Static downward-versus-upward state classes are not strongly separated in the common nine-variable environment, yet reconstructed transitions align with a higher-BIO15/lower-BIO1 direction. At a different scale, global among-taxon image angle is associated with BIO12, whereas within-taxon image angle shows a supported BIO1 slope in the opposite direction from the transition-level result. The same component therefore does not carry one scale-invariant environmental coefficient.

This pattern does not imply that one representation is correct and the others are wrong. Static state means describe present ecological sorting among extant taxa; within-taxon slopes describe local phenotypic–environmental covariance; among-taxon slopes describe broader differentiation; transition-conditioned analyses ask whether reconstructed phenotypic change is aligned with environmental change on the tree. These estimands can diverge if ecological leverage changes across biological scale, if plasticity differs from evolutionary differentiation, or if the measurements capture related but non-identical aspects of presentation.

The common9 comparison prevents a selective focus on orientation alone. Under the same trait-blind environment universe, orientation, phyllary posture and stickiness show different evidence profiles, so one shared abiotic niche model is not an adequate description of the capitulum. The preregistered external-taxon programme also places a clear ceiling on stronger claims: strict public occurrence metadata could not retain replicated states, and the climate outcomes were therefore never opened. We consequently interpret the ecological result as scale-conditioned correspondence, not external confirmation or adaptation.

## Functional interfaces are interpretation and the next causal step

Existing experiments make the historical mosaic biologically plausible by pointing to different physical and biotic interfaces: reproductive exposure for orientation, access geometry for phyllaries and arthropod filtering for stickiness. But these functional differences are not the novelty of this study and are not used as proof of adaptation.

The next causal step is the prospective **aza3** field programme: direct focal *Cirsium* manipulation of each trait followed by mechanism and reproductive-fitness endpoints. Public-data expansion is stopped: additional taxon panels, relaxed occurrence-quality thresholds and opportunistic climate predictors would no longer provide an independent test. Until prospective manipulation, the present study establishes repeated historical reassembly and scale-conditioned ecological correspondence, not the historical selective cause of each transition.

## Broader implication

The broader implication is that complex phenotypes should not be described by a single level of organization. Within-taxon covariance, among-taxon differentiation, relative evolutionary depth and transition localization can each reveal different aspects of the same biological structure. The persistence of components does not guarantee persistence of their relationships.

This reframes a common question in phenotypic integration. Rather than asking only whether a structure is integrated or modular, comparative studies can ask whether its organization is conserved across biological and evolutionary scales. In *Cirsium*, the answer is no at the historical level: the capitulum retains recognizable components, but their repeated histories are stratified and unsynchronized.

# Conclusion

A young *Cirsium* radiation repeatedly reassembled the capitulum from component traits that do not share one synchronized evolutionary history. Orientation, phyllary posture and involucre stickiness each changed repeatedly, but their histories occupy unequal relative lineage depths and do not repeatedly localize to the same branches. Ecological correspondence is also non-invariant: the three traits do not share one climatic syndrome, and orientation exposes different environmental structure across static states, within-taxon variation, among-taxon differentiation and reconstructed transitions.

The primary contribution is therefore not that capitulum parts have different functions. It is that **both the historical organization and ecological mapping of a complex reproductive phenotype depend on scale**. Recognizable components persist, but their relationships are reorganized across lineage depth, branch history and ecological representation.

# Figure legends

**Figure 1. Three capitulum components repeatedly differentiate within one young radiation.** (a) Number of Japan38 concepts with resolved source-backed states for orientation, phyllary posture and involucre stickiness. (b) Minimum unordered state changes across the frozen topology ensemble; the diamond marks the maximum-likelihood-tree value. (c) Bootstrap-median envelopes of the relative-lineage-depth bounds; \(D=1\) is terminal and lower values permit deeper placement. Relative lineage depth is a topology coordinate, not calendar time. **Alt text:** Three aligned panels show unequal trait coverage, repeated minimum state changes for all three traits, and differing relative-depth envelopes, with phyllary extending deepest and stickiness concentrated shallowest.

**Figure 2. Repeated histories are stratified across unequal evolutionary depths.** (a) Paired same-topology differences in lower relative-depth bounds; points show medians and thick intervals show 5th–95th percentiles across 1,000 topology-sensitivity realizations. Negative values mean the first trait is deeper-permissive. (b) Fraction of topologies retaining each central ordering. (c) Coverage-matched sensitivity at \(n=10\), showing that the central phyllary-deeper ordering persists against matched medians while strict tails overlap. **Alt text:** Depth contrasts are strongly negative for phyllary versus both other traits, weaker but mostly negative for orientation versus stickiness, and coverage matching retains the central phyllary-deeper ordering but not strict separation of distribution tails.

**Figure 3. Component changes are not repeatedly synchronized on the same branches.** (a) Pairwise transition-localization associations under branch-length-aware and equal-branch topology-only diagnostics. The sign and magnitude change across assumptions. (b) None of the three trait pairs passes the robust shared-localization rule requiring consistent positive localization across both layers. **Alt text:** Three paired bars compare branch-length-aware and topology-only transition associations; no pair remains consistently positive across both diagnostics, summarized as zero of three robust pairs.

**Figure 4. Orientation–environment correspondence changes with biological scale and phenotype representation.** (a) Common9 static state comparison for orientation, phyllary posture and stickiness, showing no shared abiotic syndrome. (b) Cross-scale orientation matrix comparing Azami among-taxon BIO12, Azami within-taxon BIO1/BIO15 and EAzami transition-level BIO1/BIO15 directions without placing non-exchangeable estimands on one numeric effect-size axis. (c) Exact finite-map ranks for the fixed orientation transition–niche composite across the n>=5, n>=3 and strict n>=10 coverage panels. (d) Preregistered external-confirmation gate: the 13-taxon V2 panel collapsed under strict occurrence QC to one upward taxon, so BIO1/BIO15 remained unopened. **Alt text:** Four panels show weak or unresolved static environmental separation across three capitulum traits; different orientation–environment directions among taxa, within taxa and reconstructed transitions; exceptional exact transition-regime ranks across three coverage thresholds; and an external held-out test that stops before climate extraction because only one upward taxon passes strict occurrence-quality control.

# References

Agrawal, A. A., Rudgers, J. A., Botsford, L. W., Cutler, D., Gorin, J. B., Lundquist, C. J., Spitzer, B. W., & Swann, A. L. (2000). Benefits and constraints on plant defense against herbivores: spines influence the legitimate and illegitimate flower visitors of yellow star thistle, *Centaurea solstitialis* L. (Asteraceae). *The Southwestern Naturalist*, 45, 1–5. https://doi.org/10.2307/3672545

Barreto, E., Holden, P. B., Edwards, N. R., & Rangel, T. F. (2023). PALEO-PGEM-Series: A spatial time series of the global climate over the last 5 million years (Plio-Pleistocene). *Global Ecology and Biogeography*, 32, 1034–1045. https://doi.org/10.1111/geb.13683

Duchêne, S., & Lanfear, R. (2015). Phylogenetic uncertainty can bias the number of evolutionary transitions estimated from ancestral state reconstruction methods. *Journal of Experimental Zoology Part B: Molecular and Developmental Evolution*, 324, 517–524. https://doi.org/10.1002/jez.b.22638

Felice, R. N., & Goswami, A. (2018). Developmental origins of mosaic evolution in the avian cranium. *Proceedings of the National Academy of Sciences USA*, 115, 555–560. https://doi.org/10.1073/pnas.1716437115

Gijsman, F., Havens, K., & Vitt, P. (2020). Effect of capitulum position and weevil infestation on seed production of threatened monocarpic perennial, *Cirsium pitcheri*. *Global Ecology and Conservation*, 22, e00945. https://doi.org/10.1016/j.gecco.2020.e00945

Goswami, A., Smaers, J. B., Soligo, C., & Polly, P. D. (2014). The macroevolutionary consequences of phenotypic integration: from development to deep time. *Philosophical Transactions of the Royal Society B*, 369, 20130254. https://doi.org/10.1098/rstb.2013.0254

Hoang, D. T., Chernomor, O., von Haeseler, A., Minh, B. Q., & Vinh, L. S. (2018). UFBoot2: improving the ultrafast bootstrap approximation. *Molecular Biology and Evolution*, 35, 518–522. https://doi.org/10.1093/molbev/msx281

Kalyaanamoorthy, S., Minh, B. Q., Wong, T. K. F., von Haeseler, A., & Jermiin, L. S. (2017). ModelFinder: fast model selection for accurate phylogenetic estimates. *Nature Methods*, 14, 587–589. https://doi.org/10.1038/nmeth.4285

Karger, D. N., Conrad, O., Böhner, J., Kawohl, T., Kreft, H., Soria-Auza, R. W., Zimmermann, N. E., Linder, H. P., & Kessler, M. (2017). Climatologies at high resolution for the earth's land surface areas. *Scientific Data*, 4, 170122. https://doi.org/10.1038/sdata.2017.122

Klingenberg, C. P. (2014). Studying morphological integration and modularity at multiple levels: concepts and analysis. *Philosophical Transactions of the Royal Society B*, 369, 20130249. https://doi.org/10.1098/rstb.2013.0249

Lewis, P. O. (2001). A likelihood approach to estimating phylogeny from discrete morphological character data. *Systematic Biology*, 50, 913–925. https://doi.org/10.1080/106351501753462876

Louda, S. M., & Potvin, M. A. (1995). Effect of inflorescence-feeding insects on the demography and lifetime fitness of a native plant. *Ecology*, 76, 229–245. https://doi.org/10.2307/1940645

Makino, T. T., Ohashi, K., & Sakai, S. (2007). How do floral display size and the density of surrounding flowers influence the likelihood of bumble bee revisitation to a plant? *Functional Ecology*, 21, 87–95. https://doi.org/10.1111/j.1365-2435.2006.01211.x

Maron, J. L., Combs, J. K., & Louda, S. M. (2002). Convergent demographic effects of insect attack on related thistles in coastal vs. continental dunes. *Ecology*, 83, 3382–3392. https://doi.org/10.1890/0012-9658(2002)083[3382:CDEOIA]2.0.CO;2

Minh, B. Q., Schmidt, H. A., Chernomor, O., Schrempf, D., Woodhams, M. D., von Haeseler, A., & Lanfear, R. (2020). IQ-TREE 2: new models and efficient methods for phylogenetic inference in the genomic era. *Molecular Biology and Evolution*, 37, 1530–1534. https://doi.org/10.1093/molbev/msaa015

Moreyra, L. D., Susanna, A., Calleja, J. A., Ackerfield, J. R., Arabacı, T., Blanco-Gavaldà, C., Brochmann, C., Dirmenci, T., Fujikawa, K., Galbany-Casals, M., Gao, T., Gizaw, A., Mehregan, I., Vilatersana, R., Viruel, J., Yıldız, B., Leliaert, F., Seregin, A. P., & Roquet, C. (2025). A thorny tale: The origin and diversification of *Cirsium* (Compositae). *Molecular Phylogenetics and Evolution*, 204, 108285. https://doi.org/10.1016/j.ympev.2025.108285

Niu, Y., & Sun, H. (2013). A nodding capitulum enhances the reproductive success of *Cremanthodium campanulatum* (Asteraceae) at high elevations in the Sino-Himalayan Mountains. *Plant Ecology & Diversity*, 6, 487–494. https://doi.org/10.1080/17550874.2012.702793

Ohashi, K., & Yahara, T. (1998). Effects of variation in flower number on pollinator visits in *Cirsium purpuratum* (Asteraceae). *American Journal of Botany*, 85, 219–224. https://doi.org/10.2307/2446309

Russell, F. L., Taylor, M. R., & Louda, S. M. (2025). Microsite availability, not floral herbivory, limits recruitment in peripheral native thistle populations. *Ecosphere*, 16, e70310. https://doi.org/10.1002/ecs2.70310

Thomas, P. A. (2003). Sticky exudates on the inflorescences of *Cirsium discolor* (Asteraceae) and *Penstemon digitalis* (Scrophulariaceae) as possible defense against seed predators. *The Great Lakes Entomologist*, 36, 112–121. https://doi.org/10.22543/0090-0222.2085

Thomas, P. A. (2007). Arthropods utilizing sticky inflorescences of *Cirsium discolor* and *Penstemon digitalis*. *The Great Lakes Entomologist*, 40, 169–176. https://doi.org/10.22543/0090-0222.2188

West, N. M., & Louda, S. M. (2018). Cumulative herbivory outpaces compensation for early floral damage on a monocarpic perennial thistle. *Oecologia*, 186, 495–506. https://doi.org/10.1007/s00442-017-4027-9

Willson, M. F., Anderson, P. K., & Thomas, P. A. (1983). Bracteal exudates in two *Cirsium* species as possible deterrents to insect consumers of seeds. *The American Midland Naturalist*, 110, 212–214.

Zelditch, M. L., & Goswami, A. (2021). What does modularity mean? *Evolution & Development*, 23, 377–403. https://doi.org/10.1111/ede.12390

# Transparency and data availability

All numerical claims in the manuscript are linked to versioned machine-readable evidence in the project repository and are checked by an automated manuscript–evidence validator. The public-data analyses use previously published sequence data, public occurrence/environmental data and source-backed botanical trait records; no new field or experimental data are presented here. An immutable archival snapshot will be minted after manuscript, figure and supporting-information synchronization.

Generative-AI assistance was used for code drafting, manuscript restructuring and editorial revision. All analyses, source boundaries, numerical claims and references were checked against the underlying evidence by the authors, who take responsibility for the final content.

## Submission-preparation notes (remove before final manuscript)
- Initial main-text file must be line-numbered, double-anonymous, and include references plus figures/tables near first citation.
- The four figure legends above contain required `Alt text:` descriptions; the production DOCX should embed the corresponding rendered figures near first citation.
- The immutable archive identifier and anonymous review-repository link remain final pre-submission gates.
