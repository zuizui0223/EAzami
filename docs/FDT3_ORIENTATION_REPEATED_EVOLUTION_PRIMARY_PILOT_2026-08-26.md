# FDT3 orientation repeated-evolution primary pilot for Azami-series Chapter 2 (2026-08-26)

## Decision

This bounded pilot found primary comparative studies that make floral or
inflorescence orientation a phylogenetic character, but it did **not** recover
an event record that satisfies the existing FDT3 ledger contract without
guessing a branch, transition direction, ecological regime, or topology
sensitivity.

The best next source is the 41-species *Lonicera* study of Xiang et al.
(2021): it reconstructs upward versus downward floral orientation and examines
pollinator shift, flowering phenology, temperature, orientation manipulation
and reproductive output in the same article. However, the accessible primary
record did not expose the node-by-node likelihood table or a branchwise joint
orientation--ecology event table. A paper-level statement that orientation
changed with pollinator shift is not itself an independent transition row.

Accordingly, the currently empty
`data/evidence/fdt3_repeated_evolution_event_ledger_v1.csv` must remain empty.
The decision is:

> **`NO_EVENT_ROWS_ADMITTED / SOURCE_FAMILY_IDENTIFIED / BRANCHWISE_EXTRACTION_PENDING`.**

This is a bounded extraction STOP, not evidence that repeated orientation
evolution is absent.

## Prespecified family and terminology

The family screened here was fixed before searching:

`whole-flower or whole-inflorescence orientation -> ecological context`.

Included raw states could be upward/erect, horizontal, downward/nodding,
pendant inflorescences, or resupination when the primary study explicitly
treated resupination as a component of flower presentation. Orientation of a
single organ (for example, anther placement) was retained as a near miss and
was not pooled with whole-flower posture.

Terms were kept separate:

- **repeated or homoplastic state**: the same state occurs on more than one
  reconstructed branch or is more homoplasious than expected; this may include
  gains and reversals;
- **convergence**: independent lineages are shown to reach the same derived
  state, with the relevant ancestral states and branches identified;
- **parallelism**: comparable derived changes start from comparable ancestral
  states, or the primary study demonstrates a shared developmental or molecular
  route;
- **adaptive convergence/parallelism**: in addition, comparable ecological
  regimes or functions and reproductive-fitness consequences are demonstrated.

A tip, paper, pollinator guild, morphological cluster, or experimental
contrast is not an evolutionary event.

## Search boundary

The search began with current repository material and the existing FDT3
preflight, then used bounded primary-source searches through DOI/publisher,
PubMed/PMC, Frontiers, BMC/Springer and institutional article records. Search
strings combined `floral orientation`, `flower orientation`, `inflorescence
habit`, `resupination`, `ancestral state reconstruction`, `phylogeny`,
`repeated`, `independent`, `convergence`, `pollinator`, `temperature`,
`phenology`, `altitude` and `ecology`. Citation chasing was limited to studies
that themselves reconstructed an orientation character or were necessary to
audit topology.

The screen stopped after new results resolved to duplicates, reviews,
single-species manipulations, pollination-syndrome studies without an explicit
orientation history, or nonhomologous organ-orientation studies. Reviews and
book chapters were used only to locate candidate primary studies; no event or
count was accepted from them.

Unavailable primary detail remained unavailable. In particular, the lawful
bounded record for Xiang et al. exposed the article abstract and the identities
and descriptions of Supporting Figure S1 and Tables S1--S3, but not the content
needed to reproduce individual node probabilities. That access gap was not
filled from a review, search snippet, or taxon-level visual inference.

## Candidate and source dispositions

| ID | primary source and exact locator | phylogenetic orientation result | ecological regime or association, coded separately | topology, direction and age boundary | disposition |
|---|---|---|---|---|---|
| ORP01 | [Xiang, Guo & Yang 2021, DOI 10.1111/jse.12554](https://doi.org/10.1111/jse.12554), Abstract; Supporting Fig. S1; Supporting Tables S1--S3 | An equal-rates ancestral-state analysis distinguished upward- and downward-facing flowers for 41 *Lonicera* species. Supporting Fig. S1 contains numbered nodes and node pies; Table S3 is the node-likelihood table. The abstract reports transitions between orientations in association with pollinator shift. | Pollinator type was evaluated with orientation history. Seven species supplied three-year field data on flowering phenology, daily temperature and floral angle; reorientation reduced pollination and seed production. These are comparative/experimental associations, not reconstructed ecological branch states. | The accessible record did not yield the individual node probabilities, the branchwise orientation transition list, or a joint trait--ecology stochastic map. No event age interval is reported in the inspected locator. Transition direction and independence cannot be reconstructed from the abstract alone. | **Best source-family candidate; not event-row-ready.** Obtain the primary Supporting Fig. S1 and Table S3 through a lawful full-text route, then extract all nodes under a declared probability threshold before inspecting ecological concordance. |
| ORP02 | [Iles et al. 2017, DOI 10.1016/j.ympev.2016.12.001](https://doi.org/10.1016/j.ympev.2016.12.001), Abstract and character-evolution analysis of resupination × erect/pendant inflorescence habit; topology audit: [Kress, Fér & Carlsen 2025, DOI 10.3897/phytokeys.251.130409](https://doi.org/10.3897/phytokeys.251.130409), “A new genome-based phylogeny of *Heliconia*” | In a dated seven-marker phylogeny sampling about 75% of accepted *Heliconia*, resupination and inflorescence habit were more homoplasious than the old classification implied, and their evolution was strongly correlated. The inferred root combination was resupinate flowers plus erect inflorescences. | Pollinator discrimination, pollen placement and perching/hovering were the functional hypotheses. The comparative model coupled two orientation components, not an independently reconstructed pollinator or habitat regime. | The 2025 phylogenomic study states that bootstrap support for almost all clades in the 2017 phylogeny was very low and supplies a substantially better-supported topology, but it does not repeat the 2017 orientation-history analysis. Counts or branches from the old reconstruction therefore cannot be promoted without remapping traits on the new topology. | **Repeated-state source, ecology-coupling STOP.** No branch event admitted. Reanalyse the original trait matrix on the 2025 topology ensemble before event extraction. |
| ORP03 | [Gao, Harris & He 2015, DOI 10.1186/s12862-015-0405-2](https://doi.org/10.1186/s12862-015-0405-2), Results “Ancestral state reconstruction,” Fig. 7c--e | A reduced ITS tree reconstructed nodding, horizontal and upward flower orientation. Nodding was inferred for the *Lilium* ancestor; the paper identifies a shift involving recurved/campanulate, nodding flowers in the N--N lily ancestor and reports orientation--corolla-shape correspondence. | Elevational range was reconstructed separately. Low-elevation ancestors and later radiations into other elevation bands were reported, but no branchwise test coupled each orientation transition to an elevation-regime transition. | Plastid and ITS histories conflict in this system. The text does not enumerate a topology-robust set of repeated orientation branches, and one described clade shift is not repeated evolution. Ages refer to clade divergences, not uncertainty intervals for orientation events. | **Trait-history calibration only.** No independent-origin row and no adaptive-convergence term. |
| ORP04 | [Yuan & Gao 2024, DOI 10.3389/fpls.2024.1371237](https://doi.org/10.3389/fpls.2024.1371237), Methods 2.6; Results 3.5; Fig. 6B,D; Supporting Tables S6--S7 | Floral posture and habitat altitude were reconstructed on a simplified chloroplast-genome tree. The authors describe recurrent, independent upward-facing flat flowers and call morphology in *Lilium* parallel; the abstract's explicit “at least three” count concerns campanulate flower form, not posture alone. | Altitude was reconstructed as a separate character, and posture/morphology were described as associated with altitude bands. The study does not provide a branchwise correlated-transition model or fitness validation. | Nuclear ITS and chloroplast trees conflict; the chloroplast tree was selected for reconstruction. Individual posture-event branches and their support are not enumerated in the text, and the term parallel combines posture with flower form. | **Directionally suggestive, not event-row-ready.** Do not transfer the three-origin corolla-form count to orientation. |
| ORP05 | [Whittall & Hodges 2007, DOI 10.1038/nature05857](https://doi.org/10.1038/nature05857), main phylogeny/pollinator-shift analysis and Supplementary Information | The primary analysis reconstructs bee, hummingbird and hawkmoth pollination shifts and tests nectar-spur evolution. Later Aquilegia syntheses state that shifts to hawkmoth pollination involved upright flowers, but the bounded primary paper does not provide a separately auditable branchwise orientation reconstruction. | Pollinator guild is reconstructed and independent pollinator shifts are explicit. Single-species orientation manipulations demonstrate hawkmoth responses, but experiments are not macroevolutionary events. | Inferring one orientation transition for every pollinator shift would make a syndrome assumption and import orientation history from later synthesis. | **Near miss: ecological history without a separable orientation event ledger.** No row. |
| ORP06 | [Rose et al. 2024, DOI 10.1093/aob/mcae073](https://doi.org/10.1093/aob/mcae073), Methods “Crossing data and mechanical isolation”; Results Figs. 5--6 | The paper reconstructs three switches from pleurotribic to nototribic flowers within core *Salvia* subg. *Audibertia*, while the deeper root state is ambiguous. | Range overlap and crossing ability were analysed, and the proposed general mechanical-isolation effect was not supported. | “Flower orientation” here is primarily lateral versus vertical **stamen/anther placement**, not the whole-flower gravitational posture used by Azami/EAzami. Strong genomic discordance is retained in the paper. | **Near miss: nonhomologous organ orientation.** Preserve the negative ecological result, but exclude from this family and ledger. |
| ORP07 | [Zhang, Kramer & Davis 2012, DOI 10.1371/journal.pone.0036033](https://doi.org/10.1371/journal.pone.0036033), morphology-based character reconstruction and CYC2 expression analyses | Repeated Old World reversals in the orientation of the floral symmetry plane accompany parallel floral phenotypes in Malpighiaceae. | Pollinator-mediated floral symmetry is the functional setting; molecular expression is compared. No whole-flower gravity-axis ecological transition is reconstructed. | The orientation is the spatial orientation of the symmetry plane/banner petal, not upward/horizontal/downward flower posture or inflorescence habit. | **Near miss: different orientation ontology.** No row. |

## Event-ready rows

None.

The event ledger requires a primary branch or node, ancestral and derived
orientation states, declared direction/topology uncertainty, an independent
origin group, and ecology coded separately. The candidate sources support one
or more paper-level statements about homoplasy, reconstructed character history
or ecological association, but none supplied all of those fields at event level
under the bounded accessible evidence.

The following tempting substitutions are explicitly prohibited:

| tempting substitute | why it is not an event |
|---|---|
| 41 *Lonicera* tips or numbered nodes | tips/nodes are denominators and candidate locations; only supported changes on distinct branches are events |
| every *Aquilegia* hawkmoth shift | pollinator transition cannot be copied into orientation without a separate orientation reconstruction |
| a *Heliconia* loss count reported by a later synthesis | the count was not extracted from the primary branch table, and the 2017 topology is now known to have broadly low bootstrap support |
| three *Lilium* campanulate origins | corolla form is not floral posture; the count cannot be reassigned to orientation |
| three *Salvia* nototribic switches | these are stamen/anther placement changes under a different orientation ontology |
| seven-species field contrasts in *Lonicera* | experimental species/contrasts validate function but do not create seven independent evolutionary origins |

## Reopening route

The next valid FDT3 action is narrow and predeclared:

1. recover Xiang et al. Supporting Fig. S1 and Table S3 through a lawful
   institutional or author route;
2. before reading ecological matches, freeze a node-state probability rule and
   rules for treating terminal versus internal changes, reversals and unresolved
   nodes;
3. extract every candidate branch from the 41-species tree, including rejected
   and directionally unresolved branches, into a source-specific staging table;
4. only then join the independently coded pollinator, phenology and temperature
   records; experimental fitness results remain validation fields, not event
   multiplicity; and
5. separately remap *Heliconia* orientation traits on the 2025 phylogenomic
   topology if that family is retained.

Until those steps are complete, FDT3 may say that primary comparative systems
exist and that orientation is evolutionarily labile in several clades. It may
not estimate an external independent-origin frequency, fit trait--ecology event
coupling, or call the recurrent states convergent, parallel, or adaptive.

**STOP: `0_EVENT_ROWS; 1_PRIORITY_SOURCE_FAMILY; NO_BRANCH_INFERENCE_FROM_ABSTRACTS_OR_SYNDROMES; EMPTY_LEDGER_RETAINED`.**
