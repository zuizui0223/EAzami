# Repeated mosaic assembly at unequal evolutionary depths in a young thistle radiation

**Target journal:** *Journal of Evolutionary Biology* — Research Article  
**Manuscript status:** **V7 WORKING SCIENTIFIC REFRAME**  
**Running title:** Mosaic capitulum assembly through time

> **Freeze note.** The manuscript uses only validated/frozen results except where explicitly marked. The paired-topology depth-ordering fractions from PR #160 are not inserted into inferential prose until the pinned Python 3.11 / Biopython 1.85 run completes.

## Abstract

Rapid radiations can generate multiple combinations of traits without revealing whether those components changed together, at the same evolutionary depth, or under one recurring environmental regime. We combined public nuclear phylogenomics, authority-backed capitulum states, cross-scale present-environment analyses, published East-Asian divergence-time constraints, a 5-Myr palaeoclimate series and global sea-level reconstructions to reconstruct the assembly of capitulum diversity in *Cirsium*. Thirty-six of 38 sampled Japanese paper concepts occur in one dominant radiation, within which authority-backed data retain multiple orientation × involucre-stickiness configurations. All three completed discrete trait histories require repeated change: orientation requires four to six minimum changes across 1,000 bootstrap topologies, phyllary posture exactly three and involucre stickiness exactly five. Their topology-only relative-depth envelopes differ sharply: median envelopes are 0.795–0.994 for orientation, 0.695–1.000 for phyllary posture and 0.937–0.954 for stickiness, while zero of three trait pairs passes a robust shared-transition-localization rule. Present environmental correspondence is also scale-dependent rather than uniform: annual precipitation is supported among taxa but not within taxa for orientation, whereas annual mean temperature is supported within taxa but not among taxa, and the East-Asian precipitation-seasonality state contrast is not mirrored by a positive within-taxon response. Historical cause is less identifiable than phenotypic assembly. Only one orientation transition passes the full public-data gate to a bounded chronology and palaeolocation envelope; its coherent central-date climate trajectory disappears after chronology and geography uncertainty are propagated. A broader 17-BIOCLIM diagnostic yields 0/324 robust lineage-event classes and a three-clade global sea-level diagnostic 0/21. Thus capitulum diversity in this young radiation was assembled through repeated, partly unsynchronized changes at unequal evolutionary depths, whereas one recurring coarse historical trigger is not recovered. The main result is therefore positive historical architecture rather than environmental absence: the assembly history of phenotype is identifiable farther back than its causal history.

**Keywords:** *Cirsium*; capitulum; mosaic evolution; evolutionary depth; rapid radiation; phylogenetic uncertainty; ecological scale; palaeoclimate

# Introduction

Complex phenotypes are not single historical characters. Traits that coexist in one structure may share developmental constraints and functional interactions while still changing on different branches or at different depths of a radiation (Klingenberg, 2014; Goswami et al., 2014; Felice & Goswami, 2018; Zelditch & Goswami, 2021). The evolutionary problem is therefore not only whether a structure differs among species, but how its component states were repeatedly assembled through time.

Rapid radiations make that problem especially acute. Phenotypic diversity can accumulate across short internal branches, incomplete lineage sorting and reticulation can blur exact event placement, and extant species can retain multiple combinations of component states. A minimum-change reconstruction may then establish that repeated differentiation is required without identifying independent origins, exact transition ages or adaptive convergence (Bollback, 2006; Duchêne & Lanfear, 2015). Historical cause is an additional layer: even if a change-bearing branch can be localized, causal environmental inference requires a usable event chronology, a defensible geographical envelope and a historical environmental reconstruction.

This distinction matters because present ecological association and historical cause are different estimands. A trait may show strong ecological organization among extant lineages while weak or differently signed relationships occur within lineages. Conversely, a historical differentiation may fall within a dynamic climatic period without occupying an exceptional environmental window. Treating one present-day coefficient, one central divergence date or one broad Pleistocene background as a repeated selective cause can therefore collapse biologically distinct scales.

The thistle genus *Cirsium* provides a tractable test. Global nuclear phylogenomics recovered rapid Pleistocene diversification and a large Japanese radiation with substantial gene-tree discordance (Moreyra et al., 2025). Independent East-Asian phylotranscriptomic studies provide local divergence-time constraints and document cytological and reticulate complexity (Chang et al., 2025, 2026). Capitula vary in head orientation, phyllary posture and involucre stickiness, allowing component histories to be reconstructed separately rather than treating the head as one categorical syndrome.

The repository-wide evidence also motivates a positive starting point. Of 38 sampled Japanese paper concepts, 36 occur in the dominant radiation, and authority-backed states within that radiation already include multiple capitulum configurations. A smaller public-image subset likewise shows that substantial present trait and environmental disparity occurs inside the dominant radiation rather than mapping monotonically onto secondary colonization history. The primary evolutionary question is therefore how diversity was assembled within the radiation, not simply whether separate colonization histories differ.

Here we test five nested questions. **First**, does the dominant radiation contain multiple observed capitulum configurations? **Second**, how many minimum changes are required for orientation, phyllary posture and stickiness? **Third**, do the traits occupy the same relative evolutionary depth and share one transition-localization history? **Fourth**, does present environmental correspondence recur at the same biological scale, or is ecological reach itself scale-dependent? **Fifth**, when trait history can be bounded in calendar time, does one coarse historical climate or global-eustatic regime recur around differentiation? We do not equate minimum changes with independent origins, ecological correspondence with selection, or unresolved historical triggers with environmental irrelevance. Our aim is to reconstruct the architecture of phenotypic assembly and then determine how far public data can identify its causes.

# Materials and methods

## Evidence hierarchy and claim separation

The V7 analysis is organized as:

`configuration diversity -> repeated component history -> relative-depth stratification -> present ecological reach -> calendar/historical-cause identifiability`.

Each arrow is an evidence transition rather than an assumption. State diversity does not establish transitions; minimum transitions do not establish independent origins; relative lineage depth is not calendar time; present environmental association is not historical exposure; and a dated lineage context is not automatically a trait-transition age.

## Radiation context and configuration diversity

Japanese paper taxon concepts were reconciled to the public nuclear datasets used in the repository-wide origin audit. The current synthesis contains 38 sampled Japanese concepts, of which 36 are assigned to the dominant radiation; *C. lineare* is a replicated phylogenetic exception and *C. dipsacolepis* is the current second secondary-history candidate. This occupancy is descriptive sampled-history asymmetry, not a diversification-rate estimate.

For the capitulum configuration screen, only exact-concept authority descriptions were admitted. The authority seed contains 20 dominant-radiation concepts and two secondary-history comparators. Orientation and stickiness were summarized both in their source ontology and in harmonized state classes. Missing and conflicted states were retained as missing rather than imputed. The configuration screen is descriptive and does not test correlated evolution.

A separate nine-taxon public-image/context screen is retained as Supporting Information. Seven non-circular capitulum axes and four species-median CHELSA variables were standardized within the admitted subset to ask whether secondary colonization history is a simple phenotype- or environment-distance axis. These values are current descriptive state space, not evolutionary rates or historical niches.

## Nuclear scaffold and trait-state admission

The focal historical units were paper taxon concepts linked to Moreyra et al. (2025). We used the independently reconstructed Compositae1061-compatible nuclear phylogram. A frozen 241-locus starting set yielded 236 quality-controlled loci, 176 rootable with the safflower outgroup, and a concatenated alignment of 161,654 bp. Maximum-likelihood inference used IQ-TREE 2 with ModelFinder, 1,000 ultrafast-bootstrap replicates and 1,000 SH-aLRT replicates (Kalyaanamoorthy et al., 2017; Hoang et al., 2018; Minh et al., 2020). Branch lengths are substitutions per site and were never interpreted as time.

Orientation, phyllary posture and involucre stickiness used separate biological ontologies. States entered the historical analysis only when an exact paper concept could be matched to authority-quality botanical descriptions. Ambiguous concepts remained missing. Final historical coverage was 20 concepts for orientation, 10 for phyllary posture and 13 for stickiness.

## Minimum-change burden and relative lineage depth

For the maximum-likelihood tree and each of 1,000 raw bootstrap topologies, we calculated the unordered-parsimony minimum for each trait. Dynamic programming then obtained the exact minimum and maximum mean relative lineage depth among all globally minimum-cost Sankoff histories. For a tree with *N* admitted tips and an edge subtending *d* descendants, relative lineage depth was

\[
D = \frac{N-d}{N-1}.
\]

A terminal edge therefore has \(D=1\), whereas lower values denote edges subtending broader lineages. This coordinate is topology only, not event age or evolutionary rate.

### Paired-topology depth robustness

The marginal depth envelopes suggested a consistent ordering, but marginal summaries alone do not show whether the same topology realizations preserve that ordering. A post-result robustness analysis therefore reuses the exact frozen ML/UFBoot ensemble and state-admission rules. On each of the same 1,000 UFBoot topologies it compares the lower bound of mean relative lineage depth for phyllary versus stickiness, orientation versus stickiness and phyllary versus orientation. Smaller lower bounds denote deeper permissible mean placement among globally minimum-cost histories.

This follow-up is explicitly descriptive and post-result. Bootstrap trees are topology-sensitivity realizations, not independent biological replicates, so their fractions are not probabilities or P-values. The result is admitted to final V7 numerical prose only after execution under the frozen Python 3.11/Biopython 1.85 runtime contract.

## Shared-transition localization

An equal-rates Mk diagnostic estimated branch-wise transition probability and excess over the branch prior for orientation, phyllary posture and stickiness. Pairwise Spearman correlations compared transition localization. A topology-only sensitivity set all non-root branches to equal length. A trait pair passed the descriptive shared-localization rule only when the branch-aware excess correlation was positive and the fifth percentile of the equal-branch bootstrap distribution was also positive. Failure rejects the simplest synchronized-history model under current coverage; it does not prove genetic or developmental independence.

## Cross-scale present environmental correspondence

Present ecological correspondence was evaluated separately from historical climate. We imported the exact orientation rows from a frozen Azami artifact that decomposes continuous public-image trait–environment relationships into within-taxon and among-taxon coefficients. The source artifact contained 142 taxa with at least five observations for the among-taxon analysis and permutation-based inference. The bridge retained annual mean temperature (BIO1), temperature seasonality (BIO4), annual precipitation (BIO12) and precipitation seasonality (BIO15) without re-estimation.

These coefficients were compared, without pooling, to the frozen EAzami East-Asian downward-minus-upward orientation contrasts for BIO1 and BIO15. Cross-scale categories (`within_only`, `among_only`, `neither`, or state contrast not mirrored within taxa) describe where a current association is detectable. They do not imply a reaction norm, climatic selection or historical causation.

## Calendar-time identifiability audit

The Japan38 scaffold is undated. We audited public sources for machine-readable dated Newick trees, posterior tree sets, node-age tables or exact crosswalks capable of calendarizing the change-bearing Japan38 branches. Published tree graphics, broad radiation ages, relative lineage depth and dispersal dates were not substituted for event ages.

A trait event advanced to historical-environment analysis only when four links were available:

`trait transition -> bounded parent/child chronology -> palaeolocation scenarios -> historical environmental series`.

Only one current capitulum event passes this full gate: an erect/upward to nodding/downward orientation change on the core-*Nipponocirsium* stem. Other dated phenotype contrasts were retained at weaker evidence classes because lineage-divergence ages were not exact trait-transition ages.

## Orientation chronology, palaeolocation and regional-ordering envelope

Public topology places erect *C. morii* basal to a core *Nipponocirsium* group in which sampled Japanese and Taiwanese core taxa are nodding. The parsimonious orientation change is therefore bounded after the *C. morii* split and before the Japanese-core/Taiwan-core split.

The parent split has a central estimate of 0.79 Ma with a marginal interval of 0.43–1.18 Ma, and the child split a central estimate of 0.74 Ma with an interval of 0.60–0.87 Ma (Chang et al., 2025, 2026). The ages came from separate analyses and were not treated as a joint posterior. A deterministic grid retained only parent–child pairs separated by at least 10 kyr and retained the exact central pair, giving 94 admissible chronologies with durations of 10–580 kyr.

Every chronology was evaluated under four predeclared regional scenarios: Taiwan, a Ryukyu corridor, southern Japan and a broader East-Asian core corridor. The design therefore contains 376 chronology × region scenarios. A secondary paired-ranking sensitivity ranked the four regions within each chronology using the already-computed state–trajectory cosine. A 75% scenario-dominance threshold was frozen before inspecting that ranking. These ranks are sensitivity-grid robustness descriptors, not ancestral-area probabilities.

## Orientation historical-climate matched-window analysis

We used PALEO-PGEM-Series public mean fields for BIO1, BIO4, BIO12 and BIO15 (Barreto et al., 2023). For every chronology–region scenario we retained mean environmental level, signed endpoint change, absolute endpoint change and within-window temporal standard deviation. Each was compared with same-duration windows from the same region. Matched-window percentiles are descriptive positions, not posterior probabilities.

A climate variable was considered a robust historical candidate only if the same extreme-side or signed decision survived the entire chronology × palaeolocation envelope. The single central 0.79–0.74 Ma chronology was retained as an illustration but was not permitted to override the uncertainty envelope.

## Global sea-level sensitivity and broader lineage diagnostics

Global eustatic sea level was treated only as broad range-reorganization context. The Spratt–Lisiecki empirical late-Pleistocene stack had incomplete coverage of admissible parent ages and was retained as a restricted sensitivity (Spratt & Lisiecki, 2016). The de Boer Plio-Pleistocene reconstruction covered all 94 admissible orientation chronologies (de Boer et al., 2014). We tested sea-level state/mean, standard deviation, range, absolute endpoint change, mean absolute 1-kyr change and maximum absolute 1-kyr change against same-duration background windows. Global sea level was never interpreted as local Taiwan–Ryukyu–Japan connectivity.

A separate lineage-level atlas asked whether representative dated East-Asian *Cirsium* differentiations repeatedly occupy one unusual palaeoclimate regime. It used 17 BIOCLIM variables, six dated lineage contexts and three representative clade groups (Nipponocirsium, Arenicola and Sinocirsium), producing 15,472 scenario × variable combinations and 324 event-level decision classes. A parallel de Boer analysis across three representative clades and seven sea-level metrics produced 21 event-metric classes. These lineage-divergence contexts are not substituted for missing trait-transition ages.

## Transparency

All admission rules, scenario definitions, positive results, negative results and claim ceilings are retained in machine-readable evidence files and Supporting Information. A repository-wide recovery ledger separately records results that remain biologically informative but are routed to supporting, mechanism-prior or companion roles. We did not remove failed diagnostics or rewrite unresolved classes as biological absence. Generative AI assisted with code and prose development; all analytical decisions and numerical claims were reviewed against source artifacts and frozen contracts.

# Results

## One dominant radiation contains multiple capitulum configurations

The focal Japanese history is concentrated within one radiation: 36 of 38 sampled Japanese paper concepts (94.7%) occur in the dominant radiation. The two current exceptions are *C. lineare*, which is repeatedly recovered as a secondary-history lineage, and *C. dipsacolepis*, the current second secondary-arrival candidate. The 36:1:1 occupancy is sampled-history asymmetry, not a diversification-rate estimate.

Capitulum states are not fixed by that broad history. The authority-backed seed contains 20 dominant-radiation concepts. Within it, orientation includes upward/erect and downward/nodding states, while involucres include sticky and non-sticky states. The source ontology retains four named orientation × stickiness combinations and at least three after harmonizing orientation categories. The two secondary-history comparators are both upward/erect but differ in stickiness. Thus neither the dominant radiation nor the secondary histories map to one observed capitulum syndrome (Fig. 1).

Supporting continuous data point in the same direction. In the nine-taxon public-image subset, *C. lineare* lies 4.842 standardized units from the dominant-radiation trait centroid, whereas *C. sieboldii* within the dominant radiation has a leave-one-out displacement of 8.103; the largest within-dominant trait distance (6.751) exceeds the largest observed *C. lineare*–dominant distance (6.275). Current environmental space is similarly broad within the dominant radiation. These subset results are descriptive, but they reject a simple reading in which deeper colonization separation is a monotonic proxy for present capitulum or broad-climate distance.

## All three capitulum components require repeated historical change

Each completed discrete history requires multiple changes. Orientation requires six changes on the maximum-likelihood tree and four to six across 1,000 bootstrap topologies, with a median of five. Phyllary posture requires exactly three changes on every admitted topology. Stickiness requires exactly five changes on every admitted topology (Fig. 2).

The repeated-change result is therefore not confined to one trait or one best tree. It establishes repeated historical differentiation in the source-backed ontologies, but the counts remain minimum-change lower bounds rather than independent-origin or convergence counts.

## The components occupy unequal evolutionary depths

The three histories differ not only in change count but in where minimum histories can place their changes. Median UFBoot mean-depth envelopes are 0.795–0.994 for orientation, 0.695–1.000 for phyllary posture and 0.937–0.954 for stickiness. Phyllary posture therefore permits markedly deeper mean placement, stickiness forms the shallow pole, and orientation spans a broader internal-to-terminal region (Fig. 2).

Named-edge localization shows the same inequality in resolution. Current run-329 forced-edge fractions include orientation JPN36=0.227, phyllary JPN36=0.728 and stickiness JPN06=0.995. A stable minimum count is therefore not equivalent to a stable named transition.

**Paired-topology robustness — pending frozen-runtime admission.** Exact-input local reproduction of the registered follow-up reproduces every frozen marginal depth result and gives phyllary lower bound < stickiness on 1000/1000 UFBoot topologies, phyllary < orientation on 993/1000 and orientation < stickiness on 905/1000, with the full `phyllary < orientation < stickiness` ordering on 898/1000. These fractions remain excluded from the final claim set until the pinned Python 3.11/Biopython 1.85 workflow completes. If reproduced, the correct interpretation is topology-wise temporal stratification: phyllary is consistently the deeper-permissive component, stickiness the shallow pole and orientation generally intermediate but not completely ordered against stickiness.

## The capitulum does not repeatedly change as one synchronized syndrome

Zero of three discrete trait pairs passes the predeclared robust shared-transition-localization rule. Orientation–phyllary, orientation–stickiness and phyllary–stickiness all fail the equal-branch bootstrap requirement despite some positive branch-aware point estimates (Fig. 2).

Together with the configuration diversity and unequal depth profiles, this rejects the simplest synchronized whole-capitulum history. The result supports **mosaic historical assembly** in the limited sense that component changes need not repeatedly occupy the same portions of the radiation. It does not demonstrate developmental independence, separate genetic architectures or different selective agents.

## Present orientation–environment correspondence is scale-partitioned

The ecological result is not an absence of environmental association. Instead, different environmental axes are expressed at different biological scales (Fig. 3).

For annual precipitation (BIO12), the Azami within-taxon coefficient is +0.00533 with q=0.874, whereas the among-taxon coefficient is +0.30436 with q=0.00640. BIO12 is therefore classified `among_only`. The strongest current hydric association is expressed among taxa rather than as a detectable same-direction within-taxon response.

Annual mean temperature (BIO1) shows the reverse scale structure. The Azami within-taxon coefficient is +0.01715 with q=0.0349, whereas the among-taxon coefficient is −0.03024 with q=0.836. The EAzami downward-minus-upward state contrast is negative, approximately −0.975 to −0.967 SD across the accepted topology set. Temperature therefore does not provide one common coefficient across within-taxon and lineage-state scales.

Precipitation seasonality (BIO15) supplies a third pattern. The Azami within-taxon coefficient is weakly negative and not FDR-supported (−0.00762, q=0.121), and the among-taxon coefficient is unsupported (+0.0670, q=0.599). Yet the EAzami downward-minus-upward contrast is +1.320 to +1.330 SD with sign agreement across 6/6 accepted topologies and 54/54 topology × species-LOO fits. Thus the stable East-Asian state contrast is not mirrored by a positive within-taxon response.

The resulting classification is `orientation_environment_association_is_scale_partitioned`. Current ecological correspondence is real but non-exchangeable across scales, weakening a universal direct-gradient or reaction-norm interpretation. It does not establish climatic selection.

## Repeated component history is much better identified than calendar-time history

The renewed public-asset audit recovered no machine-readable dated Newick, posterior tree set or node-age table that can be crosswalked to the multiple Japan38 change-bearing branches. Consequently, only one current capitulum transition passes the full public-data gate from trait change to bounded chronology, palaeolocation scenarios and historical environment: the core-*Nipponocirsium* orientation event (Fig. 4).

Other dates remain weaker evidence classes. Flower-colour changes have conditional terminal-lineage envelopes, dated phyllary/display comparisons are extant sister contrasts rather than reconstructed transitions, and dated range processes are not stickiness-transition ages. The information hierarchy therefore narrows sharply when moving from repeated change and relative depth to calendar-time history.

## The bounded orientation event contains regional and climatic tendencies but no robust trigger

At the central 0.79–0.74 Ma chronology, BIO1, BIO4 and BIO15 decrease in all four palaeolocation scenarios, while BIO12 increases in three of four. A point-estimate analysis would therefore produce a coherent historical climate story.

Within the full 94-chronology sensitivity grid, southern Japan is also the descriptive leading region: it ranks first in 48/94 scenarios and has a higher state–trajectory cosine than Taiwan in 61/94, the Ryukyu corridor in 61/94 and the East-Asian core corridor in 64/94. These fractions do not cross the frozen 75% dominance gate and are not ancestral-area probabilities.

More importantly, the central climate trajectory does not survive the full chronology × palaeolocation envelope. BIO1, BIO4, BIO12 and BIO15 are all directionally unresolved. Zero variables are consistently extreme in environmental level, zero in absolute endpoint change and zero in temporal variability. BIO1 remains the clearest descriptive tendency: regional median matched-window positions are near 0.14 for level and 0.85 for temporal variability, and the central chronology is unusually cold and variable across all four regional scenarios. Those patterns remain hypothesis-generating because chronology uncertainty crosses the decision boundary (Fig. 4).

The de Boer global sea-level series covers all 94 admissible chronologies, but none of the tested sea-level state, variability or change metrics survives the full chronology gate. The Spratt–Lisiecki empirical series covers only 16/94 admissible chronologies. Global eustasy therefore does not identify the bounded orientation trigger, while local palaeogeographic connectivity remains untested.

## Broader lineage differentiations do not recover one recurring coarse trigger

The 17-BIOCLIM lineage-differentiation atlas evaluated six dated contexts and 15,472 scenario × variable combinations across Nipponocirsium, Arenicola and Sinocirsium. None of 324 event-level climate classes survives all age, regional-scenario and background-horizon gates. Robust event-level classes are therefore 0/324 and recurring climate-context candidates 0 (Fig. 5).

Descriptive tendencies remain: Nipponocirsium and Sinocirsium contexts tend toward cooler and more temperature-variable regimes, whereas Arenicola lies nearer matched-background conditions. These are lineage-specific contextual tendencies, not a recurring trigger.

The independent three-clade de Boer sea-level diagnostic reaches the same boundary. Across seven metrics and three representative differentiations, robust event-metric classes are 0/21 and recurring global sea-level candidates 0. The simplest model of one repeated coarse climatic state, climate-change magnitude, climate volatility or global-eustatic regime is therefore not recovered.

# Discussion

## The primary result is historical assembly, not trigger failure

The strongest result is that substantial capitulum diversity occurs within one dominant young radiation and that its components have repeated, non-identical histories. Orientation, phyllary posture and stickiness all require multiple minimum changes. Their relative-depth envelopes differ, named-edge identifiability differs and no trait pair repeatedly shares one robust transition-localization pattern.

This changes how the environmental results should be read. The study does not begin with a failed search for cause. It begins with a positive reconstruction of phenotypic assembly and then asks how much of that history can be causally annotated. The answer becomes progressively weaker only at the later evidence layers.

## Unequal evolutionary depth supports mosaic assembly

Transition counts alone would make the three traits look similarly labile. Relative depth separates them. Stickiness combines an invariant five-change minimum with a comparatively shallow, narrow depth profile. Phyllary posture has only three required changes but admits substantially deeper placement. Orientation has a broader mixed profile. The paired-topology follow-up is designed to determine how strongly these differences persist on the same topology realizations rather than only in marginal summaries.

The phrase **mosaic historical assembly** is intentionally narrower than developmental or genetic modularity. Traits can share developmental pathways, correlated selection, standing ancestral variation or introgressed ancestry even when reconstructed changes do not repeatedly occupy the same branches. What the historical data reject is the simplest synchronized syndrome model, not all biological integration.

## Configuration diversity arose primarily within the dominant radiation

The 36/38 radiation concentration matters because it places the historical changes in a common macroevolutionary setting. The public-image subset further shows that present capitulum and environmental distances within the dominant radiation can exceed the separation of the replicated secondary lineage *C. lineare*. Broad colonization history is therefore not a sufficient one-dimensional explanation for current phenotype.

This is consistent with substantial diversification after entry into the dominant Japanese lineage, but it is not a diversification-rate test and does not establish adaptive radiation. Rate, reticulation and population-genetic mechanisms remain separate questions.

## Ecological reach is scale-dependent

The cross-scale orientation result provides an important bridge between present ecology and historical assembly. Annual precipitation is supported among taxa but not within taxa. Annual mean temperature is supported within taxa but not among taxa and points in a different direction from the East-Asian state contrast. BIO15 shows a stable East-Asian orientation-state contrast without a matching positive within-taxon association.

Thus the environmental signal cannot be represented by one universal orientation–climate coefficient. Among-taxon structure may reflect lineage history, geography, unmeasured traits or selection; within-taxon structure may reflect local sorting or plasticity; neither can be automatically substituted for the other. This helps explain why a present ecological association can be strong while a recurring historical trigger remains unidentified.

The result also clarifies the relationship to Chapter 1. Present ecological organization is informative about where phenotypes occur now, whereas Chapter 2 asks how those phenotypes were assembled through a radiation. The scales are complementary rather than interchangeable.

## A central historical narrative can be coherent and still fail uncertainty propagation

The core-*Nipponocirsium* orientation event is the best example. The central 0.79–0.74 Ma chronology has a coherent signed climate trajectory, and southern Japan is the most frequent leading regional scenario. Those signals are biologically useful hypotheses.

But neither result survives the predeclared uncertainty rules strongly enough to become the historical conclusion. Signed climate direction, environmental level, absolute change and variability all cross decision boundaries across the chronology × regional envelope, and southern Japan fails the 75% dominance gate. A central date or plurality region therefore cannot substitute for uncertainty propagation.

## The historical-cause ceiling narrows rather than empties the hypothesis space

The broader 0/324 climate and 0/21 global sea-level results weaken one specific family of explanations: a single coarse environmental regime recurring across representative differentiations. They do not imply that environment or geography was unimportant.

The tested data are coarse. PALEO-PGEM mean fields do not reconstruct local mountain microclimate, habitat continuity or biotic communities. Global sea level does not reconstruct local bathymetry, strait opening, island area or short-lived corridors. Pollinators, antagonists and lineage-specific exposure can also generate selection without leaving one recurring BIOCLIM or eustatic signature.

Repository-wide mechanism analyses show that these alternatives are empirically plausible—the genus has strong reproductive costs from antagonists in published experiments and public molecular data can recover candidate floral pigment machinery—but such evidence is deliberately not promoted to historical cause for the focal transitions. New causal resolution requires event-linked ancestry, exposure and fitness rather than another broad proxy screen.

## An information hierarchy for rapid phenotypic radiation

The results reveal a hierarchy of historical knowledge:

1. **configuration diversity** is directly observable;
2. **repeated minimum change** is robust for three traits;
3. **relative depth** separates their historical placement;
4. **named transitions** are less consistently localized;
5. **calendar time** is available for very few trait events;
6. **historical cause** is least identifiable.

This hierarchy is itself a biological and methodological result. Rapid radiation does not erase evolutionary history uniformly. The phenotype can retain a recoverable architecture of repeated assembly even when the exact causes of individual events are not reconstructable from public data.

## Limitations and claim boundary

Trait coverage is incomplete and concept-level state coding compresses within-lineage polymorphism. The Japan38 scaffold is an undated phylogram rather than a chronogram. The continuous disparity context uses a smaller nine-taxon public-image subset. The orientation within/among coefficients and EAzami state contrasts are different estimands and are not pooled. The orientation chronology combines marginal intervals from separate studies and is a deterministic uncertainty envelope, not a joint posterior. Palaeolocation regions are sensitivity scenarios, not ancestral-area probabilities. PALEO-PGEM uses coarse public mean fields. The broader climate atlas uses lineage-divergence contexts that are not capitulum-transition ages. Global sea level is not local palaeogeography.

Accordingly, we do not claim adaptation, natural selection, independent convergence, developmental/genetic modularity, exact transition ages, local land bridges or absence of environmental influence. We claim that multiple capitulum configurations occur within the dominant young radiation; three independently defined components require repeated change; those histories differ in relative evolutionary depth and do not repeatedly share one synchronized localization pattern; present ecological correspondence is scale-dependent; and one recurring tested coarse historical trigger is not identified under current public-data uncertainty.

# Conclusion

A young Japanese *Cirsium* radiation contains multiple capitulum configurations assembled through repeated changes in head orientation, phyllary posture and involucre stickiness. These components are not historical copies of one another: their minimum-change burdens, topology-only relative depths and named-edge resolution differ, and zero of three trait pairs retains one robust shared transition-localization pattern. Present ecological structure is detectable but partitioned across biological scales rather than summarized by one universal orientation–environment coefficient. Historical inference then loses resolution: only one orientation transition currently reaches a bounded chronology and palaeolocation envelope, and neither that event nor broader dated lineage contexts recover one recurring coarse climatic or global-eustatic trigger under uncertainty. The central result is therefore a separation of historical knowledge: **phenotypic assembly is well enough resolved to reveal repeated mosaic change at unequal evolutionary depths, whereas its recurring causes are not**.

# Data and code availability

Canonical machine-readable evidence is stored under `data/evidence/` in the EAzami repository. V7 adds the positive-result recovery ledger (`chapter2_positive_result_recovery_v1.csv`) and the validated orientation scale-partition result (`chapter2_orientation_environment_scale_partition_v1.json`) to the existing historical-differentiation evidence package. PR #160 contains the paired-topology relative-depth robustness contract and code; its numerical output will be promoted to the frozen V7 package only after the pinned-runtime workflow completes. The archival DOI/accession and submission commit will be added at submission freeze.

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

# Remaining V7 gates

1. Complete PR #160 under the pinned runtime and replace the provisional paired-depth paragraph with the frozen output.
2. Freeze a V7 five-figure map in the same positive-first order as the Results.
3. Add V7 validator checks for configuration diversity, depth ordering, scale partition and the historical trigger ceiling.
4. After scientific freeze, build the anonymous line-numbered DOCX, title page and Supporting Information package.
