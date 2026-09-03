# Repeated capitulum differentiation at unequal evolutionary depths without a recurring coarse historical trigger in a young thistle radiation

**Target journal:** *Journal of Evolutionary Biology* — Research Article  
**Manuscript status:** **ACTIVE V6 FINAL SCIENTIFIC TEXT**  
**Running title:** Capitulum differentiation through time

## Abstract

Repeated phenotypic differentiation within a young radiation does not by itself identify the historical process that caused it. We combined public nuclear phylogenomics, authority-backed capitulum states, published East-Asian divergence-time constraints, a 5-Myr palaeoclimate series and global sea-level reconstructions to separate four questions in *Cirsium*: how often capitulum traits changed, how deep those changes can lie, which changes can be bounded in calendar time, and whether a historical environmental regime recurs around differentiation. Orientation required four to six minimum changes across 1,000 bootstrap topologies, phyllary posture exactly three and involucre stickiness exactly five. Their relative-depth profiles differed, and zero of three trait pairs passed a robust shared-transition-localization rule. Only one orientation transition currently passes the full public-data gate from trait change to bounded chronology and palaeolocation. A central 0.79–0.74 Ma chronology gives a coherent climate trajectory, but no BIO1/BIO4/BIO12/BIO15 direction, environmental level, absolute change or temporal variability survives 94 admissible chronologies × four regional scenarios. A broader 17-BIOCLIM diagnostic across six dated lineage contexts produced 0/324 robust event-level classes, and a three-clade global sea-level diagnostic produced 0/21. Thus, repeated capitulum differentiation is substantially better identified than repeated historical cause. The data support unequal, partly unsynchronized trait histories within a dynamic Pleistocene radiation, while one recurring coarse climatic or eustatic trigger remains unidentified under public-data uncertainty.

**Keywords:** *Cirsium*; capitulum; evolutionary depth; historical differentiation; palaeoclimate; phylogenetic uncertainty; repeated evolution; sea level

# Introduction

Complex biological structures are assembled from traits that coexist in the same organism but need not share one evolutionary history. Developmental and functional integration can therefore coexist with mosaic change through time (Klingenberg, 2014; Goswami et al., 2014; Felice & Goswami, 2018; Zelditch & Goswami, 2021). A historical analysis of a complex structure should consequently distinguish at least three questions: did its component traits differentiate repeatedly, where in a radiation can those changes be placed, and when some changes can be bounded in calendar time, does the same historical environment recur around them?

The first question is usually easier than the last. Minimum-change reconstruction can identify how many state changes are required by observed tip states, but it does not identify independent origins, exact transition branches or calendar ages. Short internodes, incomplete lineage sorting, introgression and incomplete state coverage can leave multiple equally parsimonious histories (Bollback, 2006; Duchêne & Lanfear, 2015). Even a stable branch placement can still lack a usable age. Historical environmental inference then adds uncertainty in event timing, ancestral geography and environmental reconstruction. A clean narrative based on one central node age can therefore disappear once these uncertainties are propagated.

Rapid radiations make this separation especially important. A lineage can diversify during a climatically dynamic interval while the cause of a particular phenotypic transition remains unidentified. Conversely, repeated phenotypic differentiation need not imply repeated exposure to the same selective agent. Treating a broad Pleistocene background as an event-specific trigger risks turning temporal coincidence into causation.

The thistle genus *Cirsium* provides a useful system for testing these distinctions. Global nuclear phylogenomics recovered rapid Pleistocene radiations, including a large Japanese radiation with substantial gene-tree discordance (Moreyra et al., 2025). Independent East-Asian phylotranscriptomic studies provide local divergence-time constraints and document cytological and reticulate complexity (Chang et al., 2025, 2026). The capitulum contains separable traits including head orientation, phyllary posture and involucre stickiness, each with different levels of public historical coverage.

Here we reconstruct the historical problem in four nested steps. **First**, how many minimum changes are required for the best-resolved capitulum traits, and at what relative lineage depth can those changes occur? **Second**, do these traits share one robust transition-localization history? **Third**, which changes can be bounded in calendar time without converting substitutions-per-site branch lengths into ages? **Fourth**, for the best-bounded trait event and for representative dated East-Asian lineage differentiations, do climate state, change, variability or global eustatic sea-level regimes recur more strongly than matched background windows? We treat unresolved and not-evaluable outcomes as results. The objective is not to infer adaptation, but to distinguish a well-resolved history of phenotypic differentiation from a less identifiable history of cause.

# Materials and methods

## Historical evidence hierarchy

We organized the analysis as a non-exchangeable sequence:

`recurrence -> relative evolutionary depth -> calendar identifiability -> historical environmental/range context -> repeated-trigger status`.

Minimum changes were not interpreted as independent origins. Relative lineage depth was not converted into millions of years. Published lineage-divergence or dispersal ages were not treated as trait-transition ages unless topology and state information bounded a transition to that interval. Regional palaeolocation boxes were sensitivity scenarios, not ancestral-area probabilities. Historical environmental alignment was not labelled natural selection or adaptation.

A repeated historical trigger was considered evaluable only when at least two homologous trait transitions could independently pass the required chronology and palaeolocation gates. `Unresolved` indicates that admitted uncertainty scenarios cross the decision boundary; `not_evaluable` indicates that the required historical linkage is absent.

## Nuclear scaffold and trait-state admission

The focal Japanese units were paper taxon concepts linked to Moreyra et al. (2025). We used an independently reconstructed Compositae1061-compatible nuclear phylogram. A frozen 241-locus starting set yielded 236 quality-controlled loci, 176 rootable with the safflower outgroup, and a concatenated alignment of 161,654 bp. Maximum-likelihood inference used IQ-TREE 2 with ModelFinder, 1,000 ultrafast-bootstrap replicates and 1,000 SH-aLRT replicates (Kalyaanamoorthy et al., 2017; Hoang et al., 2018; Minh et al., 2020). Branch lengths are substitutions per site and were never interpreted as time.

Orientation, phyllary posture and involucre stickiness used separate biological ontologies. States entered the historical analysis only when an exact paper concept could be matched to authority-quality botanical descriptions. Ambiguous concepts remained missing. Final historical coverage was 20 concepts for orientation, 10 for phyllary posture and 13 for stickiness.

## Minimum-change burden and relative lineage depth

For the maximum-likelihood tree and each of 1,000 raw bootstrap topologies, we calculated the unordered-parsimony minimum for each trait. Dynamic programming then obtained the exact minimum and maximum mean relative lineage depth among all globally minimum-cost Sankoff histories. For a tree with *N* admitted tips and an edge subtending *d* descendants, relative lineage depth was

\[
D = \frac{N-d}{N-1}.
\]

A terminal edge therefore has \(D=1\), whereas lower values denote edges subtending broader lineages. This coordinate is topology only, not event age or evolutionary rate.

## Shared-transition localization

An equal-rates Mk diagnostic estimated branch-wise transition probability and excess over the branch prior for orientation, phyllary posture and stickiness. Pairwise Spearman correlations compared transition localization. A topology-only sensitivity set all non-root branches to equal length. A trait pair passed the descriptive shared-localization rule only when the branch-aware excess correlation was positive and the fifth percentile of the equal-branch bootstrap distribution was also positive. Failure rejects the simplest synchronized-history model under current coverage; it does not prove genetic or developmental independence.

## Calendar-time identifiability audit

The Japan38 scaffold is undated. We therefore audited public sources for machine-readable dated Newick trees, posterior tree sets, node-age tables or exact crosswalks capable of calendarizing the change-bearing Japan38 branches. Published tree graphics, broad radiation ages, relative lineage depth and dispersal dates were not substituted for event ages.

A trait event advanced to historical-environment analysis only when four links were available:

`trait transition -> bounded parent/child chronology -> palaeolocation scenarios -> historical environmental series`.

Only one current capitulum event passes this full gate: an erect/upward to nodding/downward orientation change on the core-*Nipponocirsium* stem. Other dated phenotype contrasts were retained at weaker evidence classes because lineage-divergence ages were not exact trait-transition ages.

## Orientation chronology and palaeolocation envelope

Public topology places erect *C. morii* basal to a core *Nipponocirsium* group in which sampled Japanese and Taiwanese core taxa are nodding. The parsimonious orientation change is therefore bounded after the *C. morii* split and before the Japanese-core/Taiwan-core split.

The two bounding ages come from separate public analyses and were not treated as a joint posterior. The parent split has a central estimate of 0.79 Ma with a marginal interval of 0.43–1.18 Ma, and the child split a central estimate of 0.74 Ma with an interval of 0.60–0.87 Ma (Chang et al., 2025, 2026). A deterministic grid retained only parent–child pairs separated by at least 10 kyr and retained the exact central pair, giving 94 admissible chronologies with durations of 10–580 kyr.

Because ancestral location before the split is unresolved, every chronology was evaluated under four predeclared regional scenarios: Taiwan, a Ryukyu corridor, southern Japan and a broader East-Asian core corridor. The design therefore contains 376 chronology × region scenarios. These are uncertainty scenarios, not posterior draws or independent biological events.

## Orientation historical-climate matched-window analysis

We used PALEO-PGEM-Series public mean fields for BIO1, BIO4, BIO12 and BIO15 (Barreto et al., 2023). For every chronology–region scenario we retained four classes of historical estimands: mean environmental level within the event window, signed endpoint change, absolute endpoint change and within-window temporal standard deviation. Each was compared with same-duration windows from the same region. Matched-window percentiles are descriptive positions, not posterior probabilities.

A climate variable was considered a robust historical candidate only if the same extreme-side or signed decision survived the entire chronology × palaeolocation envelope. The single central 0.79–0.74 Ma chronology was retained as an illustration but was not permitted to override the uncertainty envelope.

## Global sea-level sensitivity for orientation

Global eustatic sea level was treated only as broad range-reorganization context. The Spratt–Lisiecki empirical late-Pleistocene stack had incomplete coverage of admissible parent ages and was retained as a restricted sensitivity (Spratt & Lisiecki, 2016). The de Boer model-based Plio-Pleistocene reconstruction covered all 94 admissible orientation chronologies (de Boer et al., 2014). We tested sea-level state/mean, standard deviation, range, absolute endpoint change, mean absolute 1-kyr change and maximum absolute 1-kyr change against same-duration background windows. Global sea level was never interpreted as a reconstruction of local Taiwan–Ryukyu–Japan land connectivity.

## Broader lineage-differentiation climate atlas

Because repeated capitulum transitions cannot yet be calendarized individually, we ran a deliberately separate lineage-level diagnostic asking whether representative dated East-Asian *Cirsium* differentiations repeatedly occupy the same unusual palaeoclimate regime. This analysis cannot substitute for missing trait-transition ages.

The atlas used 17 BIOCLIM variables, six dated lineage contexts and three representative clade groups: Nipponocirsium, Arenicola and Sinocirsium. Each published age interval was evaluated on a deterministic age grid including its exact central estimate. Regional alternatives and two background horizons were propagated. Univariate metrics were environmental level, absolute change and local variability; multivariate metrics were 17-BIOCLIM PCA-whitened state distance, short-window displacement and within-window variability. The completed atlas tested 15,472 scenario × variable combinations and generated 324 event-level decision classes.

A recurring climate context required a robust event-level class that survived age, regional-scenario and matched-background gates and recurred across representative clade groups.

## Multi-lineage global sea-level diagnostic

The de Boer sea-level series was also evaluated across three representative dated lineage differentiations: Nipponocirsium (central 0.74 Ma; interval 0.60–0.87), Arenicola (0.93 Ma; 0.71–1.33) and Sinocirsium (0.44 Ma; 0.31–0.66). Seven sea-level metrics for each group yielded 21 event-metric classes. A recurring sea-level context required robustness to age and background-window uncertainty and recurrence across representative groups.

## Transparency

All admission rules, scenario definitions, negative results and claim ceilings are retained in machine-readable evidence files and Supporting Information. We did not remove failed diagnostics or rewrite unresolved classes as biological absence. Generative AI assisted with code and prose development; all analytical decisions and numerical claims were reviewed against frozen source artifacts.

# Results

## Capitulum traits differentiated repeatedly at unequal evolutionary depths

All three completed discrete histories required multiple changes. Orientation required six changes on the maximum-likelihood tree and four to six across 1,000 bootstrap topologies, with a median of five. Phyllary posture required exactly three changes on every corresponding topology. Stickiness required exactly five changes.

Their relative-depth structures differed. The median bootstrap depth envelope was 0.795–0.994 for orientation, 0.695–1.000 for phyllary posture and 0.937–0.954 for stickiness. Stickiness was therefore strongly shallow/terminal-biased under the current topology ensemble, whereas phyllary posture admitted substantially deeper placements and orientation spanned mixed internal-to-terminal histories (Fig. 1).

These are minimum-change lower bounds and topology-only depth coordinates. They demonstrate repeated historical differentiation but do not count independent origins or estimate transition rates.

## The capitulum does not show one robust synchronized transition history

Zero of three discrete trait pairs passed the predeclared robust shared-transition-localization rule. Orientation–phyllary, orientation–stickiness and phyllary–stickiness each failed the equal-branch bootstrap requirement despite positive branch-aware point estimates (Fig. 1). The result rejects the simplest model in which all capitulum components repeatedly change on the same branches, but it does not demonstrate complete independence.

## Repeated history is much better identified than calendar-time history

The renewed public-asset audit recovered no machine-readable dated Newick, posterior tree set or node-age table that can be crosswalked to the multiple Japan38 change-bearing branches. Consequently, only one current capitulum transition passes the full public-data gate from trait change to bounded chronology, palaeolocation scenarios and historical environment: the core-*Nipponocirsium* orientation event (Fig. 2).

Other dates remain weaker evidence classes. Flower-colour changes have conditional terminal-lineage envelopes, dated phyllary/display comparisons are extant sister contrasts rather than reconstructed transitions, and dated range processes are not stickiness-transition ages. Repeated trait history is therefore substantially better identified than repeated historical cause.

## A coherent central orientation trajectory disappears under chronology and palaeolocation uncertainty

At the central 0.79–0.74 Ma chronology, BIO1, BIO4 and BIO15 decrease in all four palaeolocation scenarios, while BIO12 increases in three of four. A central-date analysis would therefore suggest a coherent historical climate transition.

That pattern does not survive the full uncertainty envelope. Across 94 admissible age pairs × four regions, BIO1, BIO4, BIO12 and BIO15 are all directionally unresolved. No tested signed climate direction survives the complete chronology × palaeolocation gate (Fig. 3).

The matched-window analysis likewise fails to recover a non-directional rescue. Zero climate variables are consistently extreme in environmental level, zero in absolute endpoint change and zero in temporal variability. BIO1 shows the clearest tendency: regional median matched-window positions lie near 0.14 for mean level and 0.85 for temporal variability; at the central 0.79–0.74 Ma pair, BIO1 level is near the lower 5% and variability near the upper 5% in all four regions. These central/tendency patterns remain below the claim threshold because they do not survive chronology uncertainty.

Because only one orientation transition currently has a calendar-plus-palaeolocation envelope, a repeated same-trait trigger remains `not_evaluable_single_dated_transition_event`.

## Global eustatic sea level does not identify the bounded orientation trigger

The empirical Spratt–Lisiecki stack covers only 16/94 admissible orientation chronologies and therefore cannot support a full-envelope decision. The independent de Boer reconstruction covers 94/94 chronologies. No tested global sea-level metric is robustly high or low across the chronology envelope: sea-level state/mean, standard deviation, range, absolute endpoint change, mean absolute 1-kyr change and maximum absolute 1-kyr change all remain unresolved (Fig. 3).

This constrains a simple global eustatic trigger for the bounded orientation event. It does not test local island connectivity, strait opening, island area or habitat continuity.

## Broader East-Asian lineage differentiations do not share one robust climate regime

The separate 17-BIOCLIM lineage-differentiation atlas evaluated six dated contexts and 15,472 scenario × variable combinations across Nipponocirsium, Arenicola and Sinocirsium. None of the 324 event-level climate classes survived all age, regional-scenario and background-horizon gates. Robust event-level classes were therefore **0/324**, and recurring climate-context candidates were **0** (Fig. 4).

Descriptive tendencies remained below the formal threshold. Nipponocirsium and Sinocirsium contexts tended toward cooler and more temperature-variable regimes, whereas Arenicola lay nearer matched-background conditions. Multivariate climate-state distance, displacement and variability were likewise not generally extreme. The completed atlas therefore rejects one recurring **coarse tested** palaeoclimate regime across representative lineage differentiations; it does not identify or reject lineage-specific local drivers.

## Global sea-level context also fails to recur across representative lineage differentiations

Across Nipponocirsium, Arenicola and Sinocirsium, seven de Boer sea-level metrics yielded 21 event-metric classes. Robust event-metric classes were **0/21**, and no recurring global sea-level candidate survived age and matched-background-window gates (Fig. 4).

Together with the orientation-specific result, this weakens a universal coarse global eustatic explanation for the observed differentiation histories while remaining agnostic about local Taiwan–Ryukyu–Japan palaeogeography.

## Historical synthesis

The strongest commonality across the public evidence is hierarchical rather than causal (Fig. 5). Capitulum traits repeatedly differentiated within a young Pleistocene radiation, but at unequal evolutionary depths and without one robust shared transition-localization pattern. Calendar-time identifiability is sparse. The best-bounded orientation event does not show an uncertainty-robust climate or global sea-level trigger, and broader lineage-level climate and sea-level diagnostics reach the same ceiling.

The final current classification is:

`repeated_differentiation_resolved_but_recurring_tested_environmental_trigger_not_identified_under_public_data`.

# Discussion

## Repeated differentiation is a stronger result than repeated historical cause

The central result is an asymmetry in historical identifiability. The repeated differentiation of orientation, phyllary posture and stickiness is well supported, and their relative-depth profiles are meaningfully different. Yet the historical-cause layer is much less resolved because most change-bearing branches cannot be placed on an absolute time axis from public machine-readable data.

Repeated evolution is often followed immediately by a search for a recurring selective agent. Our results show that these are different empirical problems. A trait can repeatedly differentiate while event timing, event geography or historical exposure remains too uncertain to support one common cause. The appropriate conclusion is not that environment was unimportant, but that repeated differentiation and repeated historical causation require different evidence.

## Unequal depth supports mosaic historical assembly

The depth envelopes add information that transition counts alone cannot provide. Stickiness combines an invariant five-change minimum with a shallow, tightly bounded depth profile, whereas phyllary posture has only three required changes but admits deeper placement. Orientation lies between these extremes. Zero of three shared-localization tests further rejects the simplest synchronized whole-capitulum history.

This result concerns historical placement, not genetic modularity. Shared development, correlated selection, ancestral polymorphism or introgression can exist even when the admitted transitions do not repeatedly occupy the same branches. The safest interpretation is a mosaic historical assembly in which capitulum components differentiated at different depths.

## The central-date orientation story is a falsification example, not the conclusion

The orientation event demonstrates why central estimates should not substitute for uncertainty propagation. The central 0.79–0.74 Ma chronology produces an intuitively coherent climate pattern. Once the published marginal age intervals and four palaeolocation scenarios are propagated, every tested climate direction becomes unresolved. Expanding the test to environmental level, absolute change and temporal variability also fails to produce a robust signature.

This does not mean that the central pattern is meaningless. It is a descriptive hypothesis-generating regime context, especially for low and variable BIO1. But the analysis shows that the attractive point-estimate story is not the historical result. The result is that its direction and extremeness do not survive the admitted uncertainty.

## No recurring coarse trigger narrows the remaining hypothesis space

The negative historical result is reproduced at two levels. For the focal orientation event, no tested climate or global eustatic metric survives the full uncertainty gate. Across representative East-Asian lineage differentiations, 0/324 climate classes and 0/21 sea-level event-metric classes are robust. This weakens the model that one coarse climate state, climate-change magnitude, climate volatility or global sea-level regime repeatedly generated differentiation.

It does not imply that historical environment or geography had no role. The tests are coarse. PALEO-PGEM mean fields do not reconstruct local mountain microclimate, habitat continuity or biotic communities. Global sea level does not reconstruct local bathymetry, land bridges, strait opening or island area. Local fragmentation, transient connectivity, lineage-specific exposure and biotic interactions therefore remain untested or incompletely measured rather than rejected.

The important stopping rule is that further opportunistic screening of coarse historical environmental variables is unlikely to improve identifiability. New causal resolution requires genuinely new event timing, event geography or trait-linked ancestry, not another broad environmental predictor.

## Calendar identifiability is the principal public-data ceiling

The Japan38 phylogram can support recurrence and relative-depth inference, but its branch lengths are substitutions per site. A broad radiation age cannot be multiplied by relative lineage depth, and published lineage splits cannot be assigned to every trait change without an exact topology/state crosswalk. The current environmental information is therefore richer than the event-timing information.

This explains why Chapter 2 should stop at the present boundary. The paper has identified what public data can resolve—repeated differentiation, unequal depth and a small number of bounded historical contexts—and what they cannot resolve—a recurring tested historical trigger for the capitulum traits.

## Implications for rapid phenotypic radiation

The results support a young-radiation view in which phenotypic differentiation accumulates at different evolutionary depths without mapping onto one recurring external regime. A dynamic Pleistocene background can create ecological and geographical opportunity without every trait transition occupying an exceptional climate or sea-level window.

This is not a claim of adaptive radiation. We do not estimate trait-dependent diversification, natural selection, reproductive fitness or independent convergence. Instead, the analysis provides a historical architecture: repeated phenotypic differentiation is real, its components are unevenly placed through the radiation, and one universal coarse historical trigger is not recovered under uncertainty.

## Limitations and claim boundary

Trait coverage is incomplete and species/concept-level state coding compresses within-lineage polymorphism. The Japan38 scaffold is an undated phylogram rather than a chronogram. The orientation chronology combines marginal intervals from separate studies and is a deterministic uncertainty envelope, not a joint posterior. Palaeolocation regions are sensitivity scenarios, not ancestral-area probabilities. PALEO-PGEM uses coarse public mean fields without full emulator/downscaling uncertainty. The broader climate atlas uses lineage-divergence contexts that are explicitly not capitulum-transition ages. Global sea level is not local palaeogeography.

Accordingly, we do not claim adaptation, natural selection, independent convergence, exact transition ages, local land bridges or absence of environmental influence. We claim that repeated capitulum differentiation and unequal evolutionary depth are identifiable, whereas one recurring tested coarse historical trigger is not.

# Conclusion

Capitulum traits in the young Japanese and East-Asian *Cirsium* radiation differentiated repeatedly but at unequal evolutionary depths. Orientation requires four to six minimum changes, phyllary posture exactly three and stickiness exactly five, and zero of three trait pairs shares a robust transition-localization pattern. The historical record becomes much less identifiable when moving from relative depth to calendar time. Only one orientation transition currently passes the full public-data gate to a bounded chronology and palaeolocation envelope. Its central-date climate trajectory is coherent, but no signed climate direction, environmental level, absolute change, temporal variability or global sea-level metric survives the full uncertainty gate. Broader 17-BIOCLIM and three-clade sea-level diagnostics likewise recover **0/324** and **0/21** robust event classes, respectively. The strongest conclusion is therefore a separation of historical knowledge: **repeated trait differentiation is well resolved; repeated historical cause is not**. This is the public-data endpoint of Chapter 2.

# Data and code availability

Canonical machine-readable evidence is stored under `data/evidence/` in the EAzami repository. The active V6 sources of truth are `chapter2_historical_differentiation_final_summary_v1.json`, `chapter2_historical_differentiation_evidence_ledger_v1.csv`, `chapter2_orientation_differentiation_environment_v2_summary.json`, `chapter2_lineage_differentiation_environment_atlas_v1_summary.json`, `chapter2_lineage_differentiation_sealevel_v1.json`, `chapter2_public_dated_tree_recovery_audit_v2.json` and `japan38_relative_event_depth_v1.json`. The exact archival DOI/accession and submission commit will be added at submission freeze.

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

Minh, B. Q., Schmidt, H. A., Chernomor, O., Schrempf, D., Woodhams, M. D., von Haeseler, A., & Lanfear, R. (2020). IQ-TREE 2: new models and efficient methods for phylogenetic inference in the genomic era. *Molecular Biology and Evolution*, 37, 1530–1534. https://doi.org/10.1093/molbev/msaa015

Moreyra, L. D., Susanna, A., Calleja, J. A., Ackerfield, J. R., Arabacı, T., Blanco-Gavaldà, C., Brochmann, C., Dirmenci, T., Fujikawa, K., Galbany-Casals, M., Gao, T., Gizaw, A., Mehregan, I., Vilatersana, R., Viruel, J., Yıldız, B., Leliaert, F., Seregin, A. P., & Roquet, C. (2025). A thorny tale: The origin and diversification of *Cirsium* (Compositae). *Molecular Phylogenetics and Evolution*, 204, 108285. https://doi.org/10.1016/j.ympev.2025.108285

Spratt, R. M., & Lisiecki, L. E. (2016). A Late Pleistocene sea level stack. *Climate of the Past*, 12, 1079–1092. https://doi.org/10.5194/cp-12-1079-2016

Zelditch, M. L., & Goswami, A. (2021). What does modularity mean? *Evolution & Development*, 23, 377–403. https://doi.org/10.1111/ede.12390

# Submission completion gates

1. Freeze a five-figure V6 package around recurrence/depth, calendar identifiability, orientation uncertainty, cross-lineage trigger tests and the final evidence hierarchy.
2. Keep V5 present-day environment/colour analyses outside the V6 main scientific spine; retain them only as audit history or Supporting Information boundary material where necessary.
3. Validate every V6 numerical claim against the frozen historical-differentiation evidence artifacts.
4. Build the anonymous line-numbered DOCX and title-page/SI package after V6 text and figures are frozen.
5. Add author list, affiliations, ORCIDs, funding, conflicts, acknowledgements, archival DOI/accession and exact submission commit.

No Chapter 3, field, RAD-seq, mechanism or reproductive-fitness result is a submission gate for this manuscript.
