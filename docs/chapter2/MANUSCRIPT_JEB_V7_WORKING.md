# Repeated mosaic assembly at unequal evolutionary depths in a young thistle radiation

**Target journal:** *Journal of Evolutionary Biology* — Research Article  
**Manuscript status:** **V7 WORKING SCIENTIFIC TEXT**  
**Running title:** Mosaic capitulum assembly through time

> **Freeze note.** This draft uses only validated/frozen results except where explicitly marked. The paired-topology depth-ordering fractions from PR #160 are not inserted into inferential prose until the pinned Python 3.11 / Biopython 1.85 workflow completes.

## Abstract

Complex phenotypes can be integrated in extant organisms without having been assembled through one synchronized evolutionary history. We tested this distinction in the capitulum of a young East-Asian *Cirsium* radiation by combining public nuclear phylogenomics, authority-backed states for three discrete traits, present-day cross-scale ecological analyses and bounded historical-environment reconstructions. Thirty-six of 38 sampled Japanese paper concepts fall within the dominant radiation, which contains multiple capitulum configurations. Within this radiation, head orientation required four to six minimum changes across 1,000 bootstrap topologies, phyllary posture exactly three and involucre stickiness exactly five. Their topology-only relative-depth profiles differed strongly: median bootstrap envelopes were 0.795–0.994 for orientation, 0.695–1.000 for phyllary posture and 0.937–0.954 for stickiness, and zero of three trait pairs passed a robust shared-transition-localization rule. Present ecological correspondence was also scale-dependent rather than described by one repeated environment-response coefficient. For orientation, annual precipitation was supported among taxa but not within taxa, annual mean temperature was supported within taxa but not among taxa, and a stable East-Asian precipitation-seasonality state contrast was not reproduced as a positive within-taxon association. Historical causes were substantially less identifiable. Only one orientation transition currently passes the full public-data chain to a bounded chronology and palaeolocation envelope; no tested climate or global sea-level metric survives the complete uncertainty gate, while broader lineage-level diagnostics yield 0/324 robust climate classes and 0/21 robust sea-level event classes. These results support repeated, mosaic phenotypic assembly at unequal evolutionary depths while separating that well-resolved history of assembly from a less-resolved history of cause.

**Keywords:** *Cirsium*; capitulum; evolutionary depth; mosaic evolution; phenotypic integration; phylogenetic uncertainty; repeated differentiation

# Introduction

Complex biological structures are composed of traits that act together in the same organism but need not share one evolutionary history. Developmental or functional integration in the present therefore does not imply synchronized change through the past (Klingenberg, 2014; Goswami et al., 2014; Felice & Goswami, 2018; Zelditch & Goswami, 2021). A historical analysis of a complex phenotype should consequently distinguish at least three problems: whether its components changed repeatedly, whether those changes occupy similar depths and branches within a radiation, and whether present ecological correspondence can be projected backward to one recurring historical cause.

These questions have different identifiability requirements. Minimum-change reconstruction can establish that observed tip states require repeated differentiation, but it does not count independent origins or identify exact transition ages. Relative placement on a topology can distinguish deeper from more terminal histories without converting branch lengths into time. Ecological associations can identify present organization while remaining confounded with lineage history, geography or biological scale. Historical-cause inference adds still more uncertainty because event timing, ancestral geography and palaeoenvironment must all be linked to the same trait transition. Treating these layers as interchangeable can turn a well-supported phenotypic history into an apparently inconclusive search for one selective agent.

Rapid radiations are especially informative for separating these layers. Closely related lineages diversify over short internodes, incomplete lineage sorting and introgression can leave multiple admissible histories, and different phenotype components may change at different points in the radiation. A dynamic climatic or geographical background can organize ecological opportunity without requiring every trait transition to occur under the same exceptional historical regime.

The thistle genus *Cirsium* provides a useful system for this problem. Global nuclear phylogenomics recovered rapid Pleistocene radiations, including a large Japanese radiation with substantial gene-tree discordance (Moreyra et al., 2025). Independent East-Asian phylotranscriptomic studies provide local divergence-time constraints and document cytological and reticulate complexity (Chang et al., 2025, 2026). The capitulum contains separable axes including head orientation, phyllary posture and involucre stickiness, with different public-data coverage and plausible ecological functions.

The focal Japanese diversity is concentrated within one young radiation rather than being partitioned only among deep lineages. Thirty-six of 38 sampled Japanese paper concepts occur in the dominant radiation, and authority-backed states within that radiation retain multiple combinations of orientation, phyllary posture and stickiness. The central evolutionary question is therefore how capitulum diversity was assembled within the radiation.

Here we first reconstruct minimum histories for the three best-resolved discrete traits and quantify where those histories can lie in relative lineage depth. We then ask whether trait pairs repeatedly localize changes to the same branches. Using orientation as the best-resolved ecological bridge, we test whether present environmental correspondence is expressed consistently across within-taxon, among-taxon and East-Asian state-comparison scales. Finally, we ask how far the available public data can identify calendar-time and historical environmental context. Our central distinction is between **phenotypic assembly**, which the current data resolve relatively well, and **historical cause**, which requires a stronger evidence chain.

# Materials and methods

## Evidence hierarchy and claim boundaries

The V7 analysis was organized as:

`diversity within the radiation -> repeated component histories -> relative evolutionary depth -> shared-transition localization -> present ecological scale -> calendar/historical-cause boundary`.

Minimum changes were treated as unordered lower bounds rather than independent origins. Relative lineage depth was treated as a topology-only coordinate, not millions of years or an evolutionary rate. Present ecological associations were not interpreted as historical selection. Published lineage-divergence ages were not assigned to capitulum transitions without an explicit topology/state bridge. Palaeolocation regions were deterministic sensitivity scenarios rather than ancestral-area probabilities.

## Nuclear scaffold and focal radiation

The focal Japanese units were 38 paper taxon concepts linked to Moreyra et al. (2025). We used an independently reconstructed Compositae1061-compatible nuclear phylogram. A frozen 241-locus starting set yielded 236 quality-controlled loci, 176 rootable with the safflower outgroup, and a concatenated alignment of 161,654 bp. Maximum-likelihood inference used IQ-TREE 2 with ModelFinder, 1,000 ultrafast-bootstrap replicates and 1,000 SH-aLRT replicates (Kalyaanamoorthy et al., 2017; Hoang et al., 2018; Minh et al., 2020). Branch lengths are substitutions per site and were never interpreted as time.

Thirty-six of 38 sampled Japanese paper concepts occur in the dominant radiation. Authority-backed trait records show multiple capitulum configurations within that radiation; thus the focal diversity is not a comparison among wholly separate deep lineages. A smaller public-image/current-environment screen is retained as supporting context rather than an evolutionary-rate test.

## Trait-state admission and minimum-change reconstruction

Orientation, phyllary posture and involucre stickiness used separate biological ontologies. States entered the historical analysis only when an exact paper concept could be linked to authority-quality botanical descriptions. Missing and ambiguous states were retained as unresolved rather than imputed. Final historical coverage was 20 concepts for orientation, 10 for phyllary posture and 13 for stickiness.

For the maximum-likelihood tree and each of 1,000 raw bootstrap topologies, we calculated the unordered-parsimony minimum. These values quantify the smallest number of state changes required by each admitted topology and state matrix; they are not adaptive-convergence counts.

## Relative lineage depth

For every globally minimum-cost Sankoff history, we bounded the mean relative lineage depth of its changes. For a tree with *N* admitted tips and an edge subtending *d* descendant tips,

\[
D = \frac{N-d}{N-1}.
\]

A terminal edge has \(D=1\); lower values indicate edges subtending broader, relatively deeper lineages. Dynamic programming returned exact lower and upper bounds across all equally minimum-cost histories without assigning frequencies to those histories. The bootstrap ensemble summarizes sensitivity to topology, not independent biological replication.

A post-result paired-topology robustness analysis (PR #160) reuses the same 1,000 bootstrap topologies and compares the lower bound of mean relative lineage depth between traits on each topology. These bootstrap fractions are topology-sensitivity descriptors, not probabilities or independent replicates. Numerical fractions enter the manuscript only after the pinned Python 3.11 / Biopython 1.85 validation completes.

## Minimum-change burden audit

We retained a descriptive minimum-change burden audit to guard against over-reading unequal depth as a statement about evolutionary rate. Minimum steps were divided by the number of resolved concepts only to ask whether depth differences were trivially reducible to coverage. Because orientation and stickiness are binary characters while phyllary posture is a four-state character, these ratios are not fully commensurable and were not interpreted as lability or transition rates.

## Shared-transition localization

An equal-rates Mk diagnostic estimated branch-wise transition probability and excess over the branch prior for orientation, phyllary posture and stickiness. Pairwise Spearman correlations compared transition localization. A separate topology-only sensitivity assigned equal length to every non-root branch. A trait pair passed the descriptive robust shared-localization rule only if the branch-aware excess correlation was positive and the fifth percentile of the equal-branch bootstrap distribution was also positive. Failure rejects the simplest synchronized-history model under current coverage; it does not demonstrate genetic or developmental independence.

## Cross-scale orientation–environment analysis

Present ecology was treated as a separate layer from historical causation. The analysis joined the frozen East-Asian orientation state comparison with an independently produced Azami within/among alignment artifact. The shared focal axes were annual precipitation (BIO12), precipitation seasonality (BIO15) and annual mean temperature (BIO1).

For each axis we retained the within-taxon standardized association, the among-taxon standardized association and, where available, the EAzami downward-minus-upward state contrast. False-discovery-rate support in the Azami analysis and topology/species-leave-one-out sign robustness in the EAzami state comparison were preserved without pooling non-identical estimands.

## Ecological evaluability of the other discrete traits

The original ecological-reach analysis used a frozen gate of at least 10 independent thinned environment-complete occurrences per taxon. A later resolution audit asked whether the `not_evaluable` classifications for phyllary posture and stickiness were caused solely by that threshold, using the exact same frozen occurrence assets and no new environmental variables.

At n>=10, both traits retained only two resolved taxa and a single state. Lowering the gate to n>=5 or n>=3 restored a sticky/nonsticky contrast only through one sticky lineage, while phyllary posture remained state-degenerate in the frozen environment panel. A separate environment-free occurrence pilot nevertheless showed that broader public geography contains state-diverse phyllary support and balanced sticky/nonsticky support. This audit was used only to diagnose resolution; it did not convert a single-lineage contrast into a trait effect.

## Calendar-time identifiability and bounded orientation event

The Japan38 scaffold is undated. We audited public sources for machine-readable dated trees, posterior tree sets, node-age tables or exact crosswalks capable of calendarizing change-bearing branches. A capitulum event advanced to historical-environment analysis only when four links were available:

`trait transition -> bounded parent/child chronology -> palaeolocation scenarios -> historical environmental series`.

Only one current capitulum event passes this full gate: an erect/upward to nodding/downward orientation change on the core-*Nipponocirsium* stem. Public topology places erect *C. morii* basal to a core group in which sampled Japanese and Taiwanese core taxa are nodding. The transition is bounded after a parent split with a central estimate of 0.79 Ma and before a child split with a central estimate of 0.74 Ma (Chang et al., 2025, 2026).

The published marginal age intervals were propagated as a deterministic grid retaining 94 admissible parent–child chronology pairs separated by at least 10 kyr. Four predeclared palaeolocation scenarios—Taiwan, Ryukyu corridor, southern Japan and East-Asian core—generated 376 chronology × region scenarios. These are sensitivity scenarios, not posterior draws.

A secondary paired-ranking analysis ranked the four regions within each chronology using the already-computed state–trajectory cosine. A 75% scenario-dominance threshold was frozen before inspecting the ranking. The resulting fractions describe scenario-wise ranking robustness and were never interpreted as ancestral-area probabilities.

## Historical climate and sea-level diagnostics

PALEO-PGEM-Series fields for BIO1, BIO4, BIO12 and BIO15 were summarized within each chronology–region event window (Barreto et al., 2023). Tested estimands were mean environmental level, signed endpoint change, absolute endpoint change and within-window temporal variability, each compared with same-duration windows from the same region.

Global eustatic context was evaluated using the Spratt–Lisiecki empirical late-Pleistocene stack as a restricted sensitivity and the longer de Boer Plio-Pleistocene reconstruction as the full-coverage series (Spratt & Lisiecki, 2016; de Boer et al., 2014). Global sea level was not interpreted as local Taiwan–Ryukyu–Japan connectivity.

Because most capitulum transitions lack calendar ages, a separate lineage-level atlas asked whether six representative dated East-Asian differentiation contexts repeatedly occupy the same unusual 17-BIOCLIM regime. A parallel three-clade sea-level diagnostic evaluated seven metrics across Nipponocirsium, Arenicola and Sinocirsium. These lineage-level analyses do not substitute for trait-transition ages.

## Transparency

All admission rules, scenario definitions, unresolved outcomes and claim ceilings are retained in machine-readable evidence files. Analyses that are exploratory, auxiliary or mechanistic priors are routed separately from the focal historical-assembly claim. Generative AI assisted with code and prose development; numerical claims and analytical decisions were checked against the declared evidence artifacts.

# Results

## Multiple capitulum configurations occur within the dominant young radiation

Thirty-six of 38 sampled Japanese paper concepts occur within the dominant radiation. Authority-backed records show multiple combinations of orientation, phyllary posture and involucre stickiness within this same radiation rather than one fixed capitulum syndrome. The historical problem is therefore differentiation within a young radiation, not merely contrast among distantly related lineages.

## Three capitulum components each differentiated repeatedly

All three completed discrete histories required multiple changes. Orientation required six minimum changes on the maximum-likelihood tree and four to six across 1,000 bootstrap topologies, with a median of five. Phyllary posture required exactly three changes on every topology. Stickiness required exactly five changes.

A simple minimum-change burden check does not justify an equal-lability claim. On the maximum-likelihood tree, orientation and phyllary each yield 0.300 minimum steps per resolved concept (6/20 and 3/10), whereas stickiness yields 0.385 (5/13). Phyllary is also a four-state character while orientation and stickiness are binary. These values are descriptive coverage diagnostics, not evolutionary rates.

## Trait histories occupy unequal evolutionary depths

The topology-only relative-depth structures differed strongly. Median bootstrap depth envelopes were 0.795–0.994 for orientation, 0.695–1.000 for phyllary posture and 0.937–0.954 for stickiness. Phyllary posture therefore admits substantially deeper minimum histories, stickiness is concentrated toward the shallow/terminal pole, and orientation occupies an intermediate and broader range.

The depth difference is not erased by a trivial coverage-adjusted minimum-change count. Orientation and phyllary have the same simple maximum-likelihood steps/resolved-concept ratio but distinct depth profiles, whereas stickiness is both somewhat more step-dense and substantially shallower. The defensible result is unequal depth; equal evolutionary changeability is not established.

The paired-topology post-result analysis in PR #160 quantifies the ordering directly on the same 1,000 bootstrap topologies. Its exact fractions will be inserted after the pinned-runtime workflow validates the result.

## The capitulum does not show one robust synchronized transition history

Zero of three discrete trait pairs passed the robust shared-transition-localization rule. Orientation–phyllary, orientation–stickiness and phyllary–stickiness each failed the equal-branch bootstrap requirement despite some positive branch-aware point estimates. Thus, the simplest model in which all capitulum components repeatedly change on the same branches is not supported.

This is a historical localization result rather than proof of developmental independence. Shared developmental architecture, correlated selection, ancestral polymorphism or introgression can coexist with the observed mismatch in admitted transition histories. We therefore describe the pattern as **mosaic historical assembly**.

## Orientation–environment correspondence is partitioned across biological scales

Orientation did not show one repeated environment-response coefficient across scales. For annual precipitation (BIO12), the Azami among-taxon association was positive and FDR-supported (standardized beta = 0.30436, q = 0.00640), whereas the within-taxon association was near zero and unsupported (beta = 0.00533, q = 0.874). This is an among-taxon-only pattern.

For precipitation seasonality (BIO15), the East-Asian downward-minus-upward state contrast was large and directionally stable (+1.320 to +1.330 SD; 6/6 accepted topologies and 54/54 topology × species-leave-one-out fits had the same sign). In Azami, however, the within-taxon coefficient was weakly negative and not FDR-supported (beta = -0.00762, q = 0.121), while the among-taxon coefficient was unsupported (beta = 0.0670, q = 0.599). The East-Asian state contrast is therefore not reproduced as a positive within-taxon response.

Annual mean temperature (BIO1) showed a different scale partition. The Azami within-taxon association was positive and FDR-supported (beta = 0.01715, q = 0.0349), while the among-taxon association was unsupported (beta = -0.03024, q = 0.836). In contrast, the East-Asian downward-minus-upward state difference was negative (approximately -0.975 to -0.967 SD) and retained the same sign in all 54 topology × species-leave-one-out fits.

Together, these results support scale-partitioned present ecological organization rather than one universal hydric or thermal reaction rule. They do not identify climatic selection or the historical environment at orientation transitions.

## A three-trait depth–ecological-reach relationship is not currently identifiable

The ecological resolution audit changed the interpretation of the phyllary and stickiness zero-yield results without converting them into new trait effects. At n>=10, the frozen environment panel retained two phyllary taxa, both ascending, and two stickiness taxa, both nonsticky. Lowering the gate to n>=5 added one additional ascending phyllary taxon, so phyllary remained state-degenerate. Stickiness became state-diverse at n>=5, but the contrast consisted of one sticky lineage against two nonsticky lineages and therefore remained lineage-confounded.

A separate environment-free public-occurrence pilot recovered broader state-diverse geography, including balanced 6/6 sticky/nonsticky support. Public occurrence absence is therefore not the sole limitation; targeted panel composition also matters. Because only orientation currently has a replicated, scale-aware ecological-reach result, no three-point regression or correlation between evolutionary depth and ecological explanatory reach is identified from the present public panel.

## Calendar-time history is much less identifiable than relative assembly history

The public-asset audit recovered no machine-readable chronogram or node-age crosswalk capable of assigning ages to the multiple Japan38 change-bearing branches. Only the core-*Nipponocirsium* orientation event currently passes the full public-data chain to a bounded chronology and palaeolocation envelope.

Within the 94 chronology pairs × four regional scenarios, southern Japan is the descriptive leading regional scenario but not a dominant one: it ranks first in 48/94 chronology scenarios and exceeds Taiwan and the Ryukyu corridor in 61/94 paired scenarios and East-Asian core in 64/94. These fractions describe scenario-wise ranking robustness; they are not ancestral-area probabilities and do not cross the frozen 75% dominance gate.

At the central 0.79–0.74 Ma chronology, BIO1, BIO4 and BIO15 decrease in all four regional scenarios, while BIO12 increases in three of four. This coherent central trajectory does not survive the full chronology × palaeolocation envelope. No tested BIO1/BIO4/BIO12/BIO15 signed direction, environmental level, absolute change or temporal-variability class is robust across all admitted scenarios.

## Coarse historical climate and sea-level regimes do not provide a recurring rescue

For the bounded orientation event, no tested global sea-level metric is robust across the full chronology envelope. The empirical Spratt–Lisiecki stack covers only a restricted subset of admissible chronologies; the de Boer reconstruction provides complete coverage but likewise yields no robust event-level sea-level state or change metric.

The broader 17-BIOCLIM lineage-differentiation atlas evaluated 15,472 scenario × variable combinations and produced 324 event-level decision classes. Robust classes were 0/324. The three-clade global sea-level diagnostic produced 0/21 robust event-metric classes. These results weaken a single recurring **coarse tested** palaeoclimate or global eustatic regime while leaving lineage-specific local geography, microclimate and biotic interactions unresolved.

# Discussion

## The main result is a history of assembly, not a failed search for one trigger

The strongest result is that a multidimensional capitulum was repeatedly assembled within a young radiation. Orientation, phyllary posture and stickiness each require multiple historical changes, yet their minimum histories occupy different relative depths and do not repeatedly localize to one shared set of branches. The historical architecture is therefore more informative than a single statement that no recurring climate trigger was found.

This reframing matters because the data answer the assembly question much more strongly than the cause question. Minimum-change counts and topology-only depth can be propagated across 1,000 phylogenetic realizations. In contrast, historical-cause inference requires an event age and palaeolocation for each transition, a chain currently available for only one capitulum event.

## Unequal depth is not the same as unequal or equal rate

Stickiness is the shallow pole of the current three-trait comparison, phyllary posture admits the deepest placements, and orientation is intermediate. However, these results do not estimate evolutionary rates. Minimum steps per resolved concept are coverage diagnostics, not branch-time-normalized transition intensities, and the state ontologies differ among traits.

The important observation is more limited: the depth difference is not erased by a trivial coverage-adjusted count. Orientation and phyllary have the same simple maximum-likelihood minimum-change burden but distinct depth profiles. Thus the temporal geometry of change carries information beyond how many minimum changes are required, while equal lability remains unestablished.

## Mosaic historical assembly does not imply developmental independence

The 0/3 shared-localization result rejects the simplest synchronized whole-capitulum history under current data. It does not establish separate genetic modules or independent selective regimes. A structure can remain functionally integrated while its components respond at different branches and scales. This distinction is especially relevant in a rapid radiation in which ancestral polymorphism, introgression and short internodes can decouple present covariance from a simple sequence of shared transitions.

The appropriate biological interpretation is therefore **mosaic historical assembly**: component traits contribute to one capitulum phenotype but their admitted historical changes are not repeatedly synchronized.

## Present ecology is organized, but at different biological scales

The cross-scale orientation result helps explain why a simple direct-gradient story is inadequate. Annual precipitation appears mainly among taxa, annual mean temperature mainly within taxa, and precipitation seasonality produces a stable East-Asian state contrast without a matching positive within-taxon response. Present ecological structure is real, but the relevant scale changes among environmental axes.

This argues against treating a present species-level state contrast as a universal within-lineage response coefficient. An among-taxon association may reflect ancestry, geography or lineage-linked ecology, whereas a within-taxon association addresses a different source of variation. Their disagreement is therefore biologically informative rather than a failed replication.

The current data do not support a quantitative three-trait relationship between evolutionary depth and ecological explanatory reach. Phyllary ecology remains state-degenerate in the frozen environment panel, and stickiness becomes state-diverse only through a single sticky lineage at relaxed thresholds. A depth–predictability relation is consequently a prospective hypothesis for replicated field or state-balanced data, not a current Chapter 2 result.

## Biotic interaction evidence is a mechanism prior, not a focal historical cause

Independent *Cirsium* studies show that capitulum-level antagonists and pollinators can impose strong and context-dependent reproductive consequences. Companion evidence also documents flower-head antagonist exposure in Japanese *Cirsium*, phenology/geography-structured antagonist regimes and downstream recruitment context. These results demonstrate that biologically plausible non-abiotic pathways exist in the focal genus and region.

They do not identify the mechanism that generated any reconstructed orientation, phyllary or stickiness transition. The direct reproductive-herbivory meta-analysis and Japanese antagonist evidence therefore remain mechanism priors rather than focal historical-cause results. In particular, the pooled experimental reproductive-herbivory effect magnitude is not transferred as a measured East-Asian effect.

## The historical-cause ceiling is itself informative

The core-*Nipponocirsium* orientation event demonstrates the difference between a coherent point-estimate narrative and a robust historical inference. A central 0.79–0.74 Ma chronology suggests a directional climate transition, but no tested direction or extremeness survives the complete chronology × palaeolocation envelope. Southern Japan leads the regional ranking descriptively without dominating the deterministic scenario grid.

The same stopping point appears in broader diagnostics: 0/324 robust climate event classes and 0/21 robust sea-level event classes. This does not show that environment was unimportant. It shows that coarse public environmental series do not resolve one repeated historical cause when timing and geography uncertainty are propagated.

Further opportunistic addition of broad environmental predictors is therefore unlikely to improve the focal inference. Higher causal resolution requires new event-linked data: dated ancestry, trait-linked population histories, local palaeogeography or direct ecological measurements in ancestry-matched systems.

## Implications for rapid phenotypic radiation

A young radiation can accumulate multidimensional phenotypic differentiation without one component history standing in for the whole phenotype. The present results suggest a hierarchy in which trait components change repeatedly, occupy different relative depths and retain scale-dependent present ecology, while their specific historical causes remain less identifiable.

This is not an adaptive-radiation claim. We do not estimate trait-dependent diversification, natural selection, independent convergence or transition-time fitness. The contribution is instead an empirical architecture for phenotypic differentiation through time: **repeated assembly, unequal depth, incomplete synchronization and scale-dependent ecological correspondence**.

## Limitations and claim boundary

Trait coverage is incomplete and authority-level species/concept states compress within-lineage polymorphism. The Japan38 scaffold is an undated phylogram rather than a chronogram. Relative lineage depth is topology-only. The three traits have different state ontologies, preventing simple cross-trait rate interpretation. The orientation cross-scale analyses join distinct estimands and are not pooled. Phyllary and stickiness ecological resolution is presently insufficient for a cross-trait depth–ecology test. The bounded orientation chronology combines marginal intervals from separate studies and a deterministic palaeolocation scenario grid rather than a joint posterior. PALEO-PGEM fields are coarse and global sea level is not local palaeogeography. Broader lineage-level dates are not capitulum-transition ages.

We therefore do not claim adaptation, independent convergence, equal or unequal evolutionary rates, exact event ages, ancestral-area probabilities, local land bridges or environmental irrelevance. We claim repeated component differentiation, unequal topology-only depth, absence of one robust synchronized transition pattern, scale-partitioned present orientation ecology and a substantially lower identifiability of recurring historical cause.

# Conclusion

A young Japanese *Cirsium* radiation contains multiple capitulum configurations assembled through repeated changes in orientation, phyllary posture and involucre stickiness. The three components do not share one robust synchronized transition history and their minimum histories occupy unequal evolutionary depths, with phyllary posture admitting deeper placements, stickiness concentrated toward the shallow pole and orientation intermediate. Present ecological correspondence is detectable but scale-dependent: annual precipitation, precipitation seasonality and temperature do not reproduce one common orientation–environment relationship across within-taxon, among-taxon and East-Asian comparisons. Calendar-time and historical-exposure inference is much less resolved; only one orientation transition reaches the full public-data chain and no recurring coarse climate or global sea-level regime survives the admitted uncertainty. The principal result is therefore a separation between a **well-resolved history of mosaic phenotypic assembly** and a **less-resolved history of cause**.

# Data and code availability

Canonical machine-readable evidence is stored under `data/evidence/` in the EAzami repository. V7 source layers include `japan38_relative_event_depth_v1.json`, `chapter2_orientation_environment_scale_partition_v1.json`, `chapter2_orientation_origin_region_ranking_result_v1.json`, `chapter2_positive_result_recovery_v1.csv` and the declared historical climate/sea-level evidence artifacts. The paired-topology depth-ordering result from PR #160 will be added to this list only after its pinned-runtime validation completes. PR #162 is routed as an auxiliary ecological-resolution audit and PR #163 as companion mechanistic evidence. The archival DOI/accession and submission commit will be added at submission freeze.

# Generative-AI disclosure

Generative AI assisted with code and prose development. All outputs were reviewed against primary sources, frozen analytical contracts and machine-readable results. AI tools did not determine botanical states, alter frozen decision rules, generate the underlying observational data or receive authorship.

# References

Barreto, E., Holden, P. B., Edwards, N. R., & Rangel, T. F. (2023). PALEO-PGEM-Series: A spatial time series of the global climate over the last 5 million years (Plio-Pleistocene). *Global Ecology and Biogeography*, 32, 1034–1045. https://doi.org/10.1111/geb.13683

Bollback, J. P. (2006). SIMMAP: stochastic character mapping of discrete traits on phylogenies. *BMC Bioinformatics*, 7, 88. https://doi.org/10.1186/1471-2105-7-88

Chang, C.-Y., Liao, P.-C., Tzeng, H.-Y., Kusumi, J., Su, Z.-H., & Tseng, Y.-H. (2025). Chromosome number variation and phylogenetic divergence of East Asian *Cirsium* sect. *Onotrophe* subsect. *Nipponocirsium* (Compositae), with a new species from Taiwan. *Botanical Studies*, 66, 8. https://doi.org/10.1186/s40529-025-00454-2

Chang, C.-Y., Liao, P.-C., Tzeng, H.-Y., Kusumi, J., Su, Z.-H., & Tseng, Y.-H. (2026). Phylotranscriptomics and genome-size evidence clarify the Taiwanese *Cirsium japonicum* complex and delimit *C. brevicaule* and allied East Asian thistles. *BMC Plant Biology*, 26, 545. https://doi.org/10.1186/s12870-026-08097-6

de Boer, B., Lourens, L. J., & van de Wal, R. S. W. (2014). Persistent 400,000-year variability of Antarctic ice volume and the carbon cycle is revealed throughout the Plio-Pleistocene. *Nature Communications*, 5, 2999. https://doi.org/10.1038/ncomms3999

Duchêne, S., & Lanfear, R. (2015). Phylogenetic uncertainty can bias the number of evolutionary transitions estimated from ancestral state reconstruction methods. *Journal of Experimental Zoology Part B: Molecular and Developmental Evolution*, 324, 517–524. https://doi.org/10.1002/jez.b.22638

Felice, R. N., & Goswami, A. (2018). Developmental origins of mosaic evolution in the avian cranium. *Proceedings of the National Academy of Sciences USA*, 115, 555–560. https://doi.org/10.1073/pnas.1716437115

Goswami, A., Smaers, J. B., Soligo, C., & Polly, P. D. (2014). The macroevolutionary consequences of phenotypic integration: from development to deep time. *Philosophical Transactions of the Royal Society B*, 369, 20130254. https://doi.org/10.1098/rstb.2013.0254

Hoang, D. T., Chernomor, O., von Haeseler, A., Minh, B. Q., & Vinh, L. S. (2018). UFBoot2: improving the ultrafast bootstrap approximation. *Molecular Biology and Evolution*, 35, 518–522. https://doi.org/10.1093/molbev/msx281

Kalyaanamoorthy, S., Minh, B. Q., Wong, T. K. F., von Haeseler, A., & Jermiin, L. S. (2017). ModelFinder: fast model selection for accurate phylogenetic estimates. *Nature Methods*, 14, 587–589. https://doi.org/10.1038/nmeth.4285

Klingenberg, C. P. (2014). Studying morphological integration and modularity at multiple levels: concepts and analysis. *Philosophical Transactions of the Royal Society B*, 369, 20130249. https://doi.org/10.1098/rstb.2013.0249

Minh, B. Q., Schmidt, H. A., Chernomor, D., Schrempf, D., Woodhams, M. D., von Haeseler, A., & Lanfear, R. (2020). IQ-TREE 2: new models and efficient methods for phylogenetic inference in the genomic era. *Molecular Biology and Evolution*, 37, 1530–1534. https://doi.org/10.1093/molbev/msaa015

Moreyra, L. D., Susanna, A., Calleja, J. A., Ackerfield, J. R., Arabacı, T., Blanco-Gavaldà, C., Brochmann, C., Dirmenci, T., Fujikawa, K., Galbany-Casals, M., Gao, T., Gizaw, A., Mehregan, I., Vilatersana, R., Viruel, J., Yıldız, B., Leliaert, F., Seregin, A. P., & Roquet, C. (2025). A thorny tale: The origin and diversification of *Cirsium* (Compositae). *Molecular Phylogenetics and Evolution*, 204, 108285. https://doi.org/10.1016/j.ympev.2025.108285

Spratt, R. M., & Lisiecki, L. E. (2016). A Late Pleistocene sea level stack. *Climate of the Past*, 12, 1079–1092. https://doi.org/10.5194/cp-12-1079-2016

Zelditch, M. L., & Goswami, A. (2021). What does modularity mean? *Evolution & Development*, 23, 377–403. https://doi.org/10.1111/ede.12390

# V7 completion gates

1. Complete the pinned-runtime CI for PR #160 and insert the paired-topology depth-ordering fractions only if reproduced.
2. Validate every V7 numerical claim against the frozen V7 evidence files.
3. Generate the five figures in `JEB_V7_FIGURE_MAP.md` order.
4. Keep PR #162 in Supporting Information as a resolution audit and PR #163 as companion mechanistic evidence.
5. Freeze manuscript/figures, then build the anonymous line-numbered DOCX and title-page/SI submission package.
