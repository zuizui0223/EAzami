# EAzami / Azami series Chapter 2 current state

Status date: 2026-08-26

This file is the human-readable summary view. Module-specific machine-readable
contracts under `data/evidence/` remain authoritative for execution gates.

## Dissertation placement

This repository is the execution workspace for **Azami series Chapter 2**.

- **Chapter 1 / Azami:** global present-day image phenomics and spatial
  environment structure; observational discovery only.
- **Chapter 2 / EAzami:** literature-informed functional effects ->
  East-Asian/Japanese evolutionary history -> repeated module transitions ->
  transition-niche concordance -> dated disparity/event tests -> competing
  evolutionary simulations.
- **Downstream causal chapters/tests:** ancestry-resolved trait -> mechanism ->
  reproductive-fitness and molecular-reuse tests selected by Chapter 2.

Chapter 2 can recover repeated evolution or
`ecological-opportunity-consistent functional diversification` if its gates
pass. It cannot by itself call a focal state adaptive or the radiation adaptive
without the downstream causal fitness evidence.

## Doctoral center

> **Why did one young Japanese *Cirsium* radiation generate such large capitulum and ecological diversity so quickly, despite shallow lineage divergence?**

Central working hypothesis: **modular evolvability** — reusable standing variation, gene flow/introgression and cytotype/genome changes may allow phenotype modules to diverge faster than genome-wide lineage sorting.

This remains a hypothesis, not a conclusion. Current pattern-reduction results do not decisively distinguish modular evolvability from a common-lability full model.

Priority:
1. **Aim 1 — source of variation**.
2. **Aim 2 — adaptive function**.
3. **Aim 3 — colour mechanism**.

## Existing-data premise

- 36/38 sampled Japanese concepts are in the dominant young radiation.
- *C. lineare* is the strongest replicated secondary-history exception.
- *C. dipsacolepis* remains a candidate secondary arrival.
- large capitulum disparity occurs inside the dominant radiation.
- broad current-climate distance does not positively order capitulum distance in the current nine-taxon subset.
- ploidy is not a deterministic explanation of orientation.
- species-tip coding compresses documented W/C polymorphism.
- the heavy 294→296 raw-read tree is preserved but deferred.

## Aim 2 — quantified antagonist baseline

Canonical result:

`data/evidence/cirsium_floral_herbivory_lnrr_meta_v2.json`

Estimand:

`RR = viable/mature seed output under experimentally reduced insect herbivory / seed output under ambient herbivory`

Current harmonized coverage:

- **9 within-study contrasts**;
- **4 independent data-generation studies**;
- **2 *Cirsium* taxa/taxon concepts**.

Random-effects result:

- pooled **RR = 2.674**;
- 95% CI **2.388–2.993**;
- equivalent ambient-herbivory loss of potential seed output = **62.6%**;
- 95% CI **58.1–66.6%**;
- **I² = 1.0%**.

Resolved:

> **insect herbivory on reproductive structures imposes a large and repeatable maternal-fitness cost in the currently harmonizable *Cirsium* experiments.**

Aim 2 therefore asks which capitulum modules alter this established antagonist cost, what pollination/abiotic costs accompany those modules, and whether the effect reaches reproductive fitness.

## Cross-layer pattern reduction — current conclusion

EAzami keeps the global Azami environment/trait layer observational and uses frozen Azami patterns plus independent interaction/fitness literature as mechanism-reduction targets.

The literature-number-rich registry contains concrete pollination, antagonist, display, orientation/rain, size-predation and colour-choice targets rather than only Azami environmental signs.

### 36-target v2 screen

Best-distance ranking in the seven-family screen:

1. FULL_MODULAR_HET — **7.61**
2. FULL_MODULAR_GLOBAL — **18.95**
3. FULL_COUPLED_HET — **25.49**
4. FULL_COUPLED_GLOBAL — **29.83**

Five fixed simulation replicates per parameter draw preserved the full-model ordering:

1. FULL_MODULAR_HET — **7.75**
2. FULL_MODULAR_GLOBAL — **23.03**
3. FULL_COUPLED_HET — **27.00**
4. FULL_COUPLED_GLOBAL — **37.22**

This demonstrates that the v2 ordering is not a single-simulation lottery, but it does not make the distances posterior model probabilities.

### Broader multi-seed held-out screen

The separate 31-row robust screen gives:

- full modular: accepted median core distance **0.287**, held-out reproduction **0.706**;
- full common-lability: **0.297**, held-out reproduction **0.689**;
- antagonist-only: **0.419**, held-out **0.417**;
- pollinator-only: **0.429**, held-out **0.317**;
- environment-only: **0.586**, held-out **0.133**.

The common-lability full model produced the only 11/11 core draw in that run. Therefore the defensible conclusion is:

> **joint environmental structure + mutualist response + antagonist cost is structurally supported much more strongly than any single-driver family; current evidence does not yet decisively distinguish common lability from modular evolvability.**

The simulations are structural-sufficiency screens, not likelihood fits, Bayes factors, posterior model probabilities or causal proof.

## Mechanism-gap reductions now completed

### Orientation

A static `orientation → pollinator preference` mechanism is insufficient for the current cross-study pattern. The reduced orientation screen instead requires separate candidate pathways:

- time-window pollination / thermal timing;
- rain/UV/wetting protection.

The field schema therefore preserves early-day versus later/all-day bouts, head-scale microclimate, wetting, pollen presentation/viability, effective contacts and final achenes. An all-day visitation null is not treated as evidence of no orientation effect.

The six-topology branch-length/Mk gate is complete: all retained topologies require
at least five orientation-state changes, while direction, ancestor and adaptive
cause remain unresolved. The frozen FDT4 `n>=10` occurrence gate was subsequently
closed without lowering the threshold by screening all eligible published-voucher
localities: *C. morii* increased from 9 to 10 independent environment-complete
cells and *C. tatakaense* from 9 to 11.

On the resulting 11-taxon panel, the present-day PGLS association is stable across
all six topologies for higher BIO15 and lower BIO1 in D taxa. The stricter
branchwise transition-niche test does not pass across all six topologies: BIO15
has permutation `p=0.078-0.094`, while BIO1 spans `p=0.044-0.066`. Therefore:

> **retain the topology-stable BIO15/BIO1 directions, but do not call them repeated
> niche-associated convergence or adaptation. The predeclared coverage
> discriminator is closed; do not add occurrences merely to chase significance.**

FDT5-FDT7 absolute-time analyses remain closed. The accepted orientation trees
carry substitutions-per-site branch lengths, whereas the machine-readable dated
tree and its posterior have not been recovered; molecular branches must not be
relabelled as time.

The Chapter 2 semantics of M0 neutral, M1 single abiotic, M2 single biotic, M3
common-lability, M4 modular selection mosaic and M5 ecological-opportunity pulse
are now frozen in `data/evidence/fdt7_legacy_simulation_bridge_v1.json`. This is
not a one-to-one mapping from the earlier FULL_COUPLED/FULL_MODULAR structural
screens, and it does not open FDT7 execution.

Canonical diagnostic:

`data/evidence/fdt4_orientation_voucher_augmented_diagnostic_v2.json`

The independent *Lilium duchartrei* orientation experiment is retained as a
context calibration, not added to the common-effect meta-analysis. Its primary
abstract reports that seed set correlates positively with slope angle in
natural down-slope controls and negatively in flowers manipulated to face up
slope; visitation shows the same tendency. Public JSE, Wiley, ResearchGate,
Mendeley, Semantic Scholar and Crossref/TDM routes did not yield the fitted
coefficient, covariance, sample sizes, group summaries or raw data.

Decision:

> **treat the estimand as orientation x slope interaction direction. Do not
> manufacture a generic down-versus-up response ratio or call a universal
> down-slope fitness advantage.**

Reopen only with verified article models/tables or raw data obtained through a
lawful institutional or author route, preserving slope as a continuous
moderator.

Canonical access gate:

`data/evidence/fdt1_lilium_orientation_source_recovery_v1.json`

### Pollinator display × density/context

Four *C. purpuratum* heads-probed slopes show residual under one shared mean and one shared density ratio. Exact log-space decomposition shows that context flexibility can remove the training residual, but the fully context-specific four-parameter form is saturated for four observations.

Predictive shrinkage/leave-one-out validation gives:

- shared density-only LOO log-RMSE = **0.244791**;
- partial-pooling LOO log-RMSE = **0.239090**;
- improvement = **2.33%**;
- effective df = **2.484**.

Decision:

> **do not promote unpooled year/site pollinator parameters into the full macro-interaction simulation yet.**

Instead the Aim 2 bout ledger records focal display, quantitative local plant/head density, `heads_probed_total`, visits and effective contacts so the context term can be estimated from replicated focal-system data with partial pooling.

### Stickiness / glandular-trichome calibration

The formerly direction-only *Aquilegia* trichome-removal experiment is now a
quantitative eight-population extraction from one coordinated study cluster
(total design `n=300`). Descriptive population-level lnRR synthesis gives:

- herbivory damage after trichome removal: **RR = 1.656** (95% normal CI
  **1.339-2.047**);
- healthy fruit set with intact trichomes versus removal: **RR = 1.077**
  (95% normal CI **0.991-1.171**).

The article's hierarchical tests support overall treatment effects on damage
(`p=0.007`) and healthy fruit set (`p=0.001`), but species-by-treatment
interactions are also supported (`p=0.041` and `p=0.016`). All four
*A. vulgaris* populations have positive effects in both pathways, whereas
*A. pyrenaica* directions are mixed.

Decision:

> **retain a direct trichome -> enemy exclusion -> reproductive-fitness pathway,
> but model it as context dependent. The eight populations are not eight
> independent studies, and the magnitude is not transferable to Cirsium
> capitulum stickiness.**

Canonical result:

`data/evidence/fdt1_aquilegia_trichome_population_synthesis_v1.json`

A bounded primary-source audit then found two independent reproductive-
stickiness manipulations. Added corolla stickiness in *Erica plukenetii* sharply
reduced nectar-robbing damage while the sticky-stem location control was null.
Removing the entire sticky glandular bract package in *Passiflora foetida*
increased bud damage from 17.65% to 55.82%, but developing-fruit damage was null.

Decision:

> **promote `stickiness -> enemy damage/access` to a replicated but
> nonhomologous mechanism calibration. Do not pool a magnitude: the Erica model
> link/sample size and Passiflora paired-plant covariance are unavailable, and
> Passiflora removes enclosure with adhesion. Neither study adds a final
> fruit/seed fitness effect.**

Canonical audit:

`docs/FDT1_STICKINESS_PRIMARY_MANIPULATION_EVIDENCE_AUDIT_2026-08-26.md`

### Bract/phyllary defence calibration

The *Pedicularis rex* water-holding-bract manipulation retains a coherent
pathway: draining left pollinator visitation unchanged, increased seed
predation and reduced final seed set. The official primary tables provide exact
treatment coefficients and SEs for all three endpoints. The visitor model is
reported as binomial-logit; the seed-set/predation model link is not named in
the accessible methods.

A bounded independent primary-source audit now adds four direct reproductive-
envelope experiments. The closest focal analogue is the Cardueae *Centaurea
solstitialis* paired spine-removal experiment: removal increased illegitimate
lepidopteran visits and reduced filled-seed percentage by a reported 22%.
*Taraxacum* phyllary cutting removed a slug-access delay, *Monotropsis* bract
removal increased reproductive herbivory in two years and reduced mature-fruit
ratio in one year, and draining the *Chrysothemis* water calyx increased floral
sterilization odds (OR 2.18, 95% CI 1.21-3.92). *Rheum* is retained as an
opposite-direction counterexample in which showy bracts increased seed
predation.

Decision:

> **promote defensive-envelope access/damage and final-fitness direction to
> independently replicated functional calibrations, but do not pool a common
> magnitude. Physical spines, liquid barriers and visual-plus-physical bract
> packages are nonhomologous; key covariance, variance, link and host-clustering
> information remains missing. No focal *Cirsium* manipulation validates the
> Azami image proxy or demonstrates a phyllary/spine adaptation.**

Canonical audit:

`docs/FDT1_BRACT_PHYLLARY_DEFENCE_PRIMARY_MANIPULATION_AUDIT_2026-08-26.md`

### Display calibration source gate

The *Ipomopsis aggregata* display manipulation remains valuable but
direction-only. PubMed and the archived author abstract independently verify
larger-display pollinator attraction (`p<0.01` for first visit), higher
pre-dispersal seed predation on many-flowered plants (`p<0.001`), and wording
that the enemy cost did not offset the potential maternal gain. The bounded
public recovery did not yield treatment sample sizes, group summaries, or
uncertainty.

A legacy author PDF with a plausible filename was inspected and rejected by
content and SHA256: it is a different 1997 *Oecologia* article on *Lesquerella
fendleri*, not the Brody and Mitchell *Ipomopsis* article.

Decision:

> **retain only the joint pollinator-benefit / seed-predator-cost direction.
> Do not calculate a display effect size, infer means from P-value signs, treat
> the abstract's "potential fitness gain" as a measured net effect, or ingest
> the rejected mismatched PDF.**

Reopen numerical extraction only after a verified full-text copy or
author-supplied tables are obtained through a lawful institutional or author
route.

Canonical recovery gate:

`data/evidence/fdt1_ipomopsis_display_source_recovery_v1.json`

### Flower colour

The former sign-only *C. palustre* prior `white preferred` is now quantitative. Six significant white-preference bee-type × population cases reconstructed from Mogford Fig. 24 give

`white selection ratio = white visit share / white morph share`

with:

- conditional range **1.1516–1.6118**;
- geometric mean **1.3019**.

This is a **soft, significance-conditioned calibration**, not a pooled effect: the cases are clustered within one study system and included because significant white preference was reported.

Decision:

> **do not hard-code `white always preferred`; measure the same availability-normalized selection ratio in the W/coloured focal system.**

The field schema now preserves focal `colour_class`, local same/alternative-colour open-head availability, pollinator visits and effective contacts within a defined colour-choice context.

Canonical note:

`docs/AIM2_CIRSIUM_PALUSTRE_COLOUR_PREFERENCE_2026-08-21.md`

The FDT1 abiotic pigment-function gate is now explicitly separate from this
pollinator-choice calibration. A bounded primary audit recovered a complete
64-cell (`n=1342` plant-day pollination pairs) *Ipomoea purpurea* CHS-null
genotype x temperature x light table. The authors report approximately 26%
lower fertilization success for mutant recipients at high maternal temperature
and 24% lower success for mutant pollen on hot recipients, with no corresponding
genotype difference in the cool comparison. Tomato complementation and
antioxidant rescue independently support a pollen-flavonol -> ROS -> heat-stage
pollen-performance mechanism, while an `hp2` experiment reaches a seed endpoint.
Direct *Mimulus* stress experiments are retained as a counterexample.

Decision:

> **promote whole-flavonoid reproductive thermoprotection to bounded effect
> extraction, not pooled meta-analysis. Keep visible petal anthocyanin function
> unresolved: CHS/F3H/DET1 perturbations are pleiotropic, tomato pollen does not
> contain anthocyanin, and the *Ipomoea* and `hp2` temperature contrasts each
> use one chamber/greenhouse per environment.**

Canonical audit and extract:

- `docs/FDT1_COLOUR_PIGMENT_FUNCTION_PRIMARY_AUDIT_2026-08-26.md`
- `data/evidence/fdt1_ipomoea_purpurea_chs_heat_cell_extract_v1.csv`
- `data/evidence/fdt1_ipomoea_purpurea_chs_heat_extract_summary_v1.json`

The non-inferential margin check gives the same interaction direction under
equal-cell and reported-`n` weighting. At high maternal temperature, the
mutant/wild-type ratio is 0.706/0.714 for the maternal genotype and 0.737/0.737
for the paternal genotype. At low maternal temperature the corresponding ratios
are above 1 (1.085/1.063 and 1.049/1.040). Ratio-of-ratios values are 0.650-
0.672 for the maternal contrast and 0.703-0.708 for the paternal contrast.
These are arithmetic margins only: no confidence interval or sampling variance
is assigned.

Canonical descriptive check:

`data/evidence/fdt1_ipomoea_purpurea_chs_heat_descriptive_margins_v1.json`

### Chapter 2 trait-to-function interface

The FDT1 results are now frozen into a 15-row machine-readable loading contract
covering display, orientation, defensive envelope, stickiness and colour. Each
row declares the functional axis, evidence state, allowed Chapter 2 use,
uncertainty rule, counterevidence and claim ceiling. No row is a validated fixed
numeric *Cirsium* tip loading. In particular, Azami lightness cannot inherit the
pollen-flavonol thermoprotection loading, and Azami spine-like geometry cannot
inherit the external envelope-defence loading before direct botanical proxy
validation.

Canonical interface:

`data/evidence/fdt1_trait_function_loading_contract_v1.csv`

## FDT2 context and geographic-moderator gate

The 49 FDT1 response rows have now been audited as **23 independent
primary-source study clusters**. Every source has an explicit setting,
geographic-evidence status, imposed-exposure description, unit/clustering rule,
allowed FDT2 use and missingness boundary.

Current machine result:

- usable one-site exact treatment coordinates: **3/23** source clusters;
- exact multi-site geography retained within papers: **2/23**, not independent
  studies;
- directional exposure calibration: **10/23**;
- chamber/greenhouse/bench/plot-confounded exposure contexts: **5/23**;
- geographic-meta-regression-ready homologous source families: **0**.

Decision:

> **FDT2 is `READINESS_REGISTRY_ONLY / STOP_BEFORE_MODERATOR_MODEL`. No
> latitude slope, geographic response surface or pooled temperature/UV/rain/
> light moderator is estimated. Named regions remain ungeocoded, missing
> context remains missing, and rows within one DOI remain one study cluster.**

This is a Chapter 2 result rather than a failed detour: it shows that the
external functional literature can calibrate mechanism directions but cannot
reconstruct the environmental history of the East-Asian radiation. That
history must come from focal *Cirsium* trait provenance, vetted occurrences,
niche axes and a dated phylogeny.

Canonical audit and gate:

- `docs/FDT2_PRIMARY_STUDY_CONTEXT_AUDIT_2026-08-26.md`;
- `data/evidence/fdt2_source_context_registry_v1.csv`;
- `data/evidence/fdt2_context_readiness_summary_v1.json`.

## FDT3 repeated-evolution event preflight

The current repository has been checked for event-ready external evidence
before treating any paper, taxon or response as an independent origin. Six
material classes were found: FDT1/FDT2 functional calibration, focal *Cirsium*
phylogeny literature, the focal orientation repeated-state analysis, the
six-module hypothesis registry, comparative method/theory anchors and a bounded
seven-source orientation primary pilot.

Decision:

> **The external event ledger contains 0 extracted transition events. FDT3 is
> `NOT_READY_ZERO_PRIMARY_EVENT_LEDGER_ROWS_SOURCE_FAMILY_IDENTIFIED`. Current focal orientation evidence
> remains FDT4 evidence; functional experiments remain FDT1/FDT2 evidence; and
> neither is silently promoted to cross-plant convergence or adaptation.**

The row-empty ledger is intentional. Its fixed schema requires ancestral and
derived functional states, topology/direction uncertainty, a separate
ecological transition, study-cluster identity, independent-origin status and
separate molecular/fitness validation. Missing age or validation must remain
missing.

The primary pilot audited seven sources. *Lonicera* is the priority family
because one study combines 41-species orientation reconstruction, pollinator
shift, phenology/temperature and experimental seed output. No branch event was
admitted because Supporting Figure S1/Table S3 node probabilities and a
branchwise joint event list were not available. *Heliconia* is retained as a
homoplasy/topology-remapping target; *Lilium*, *Aquilegia*, *Salvia* and
Malpighiaceae candidates remain trait-history or ontology near misses.

Canonical preflight and empty event contract:

- `data/evidence/fdt3_existing_material_preflight_v1.csv`;
- `data/evidence/fdt3_repeated_evolution_event_ledger_v1.csv`;
- `data/evidence/fdt3_existing_material_preflight_v1.json`;
- `data/evidence/fdt3_orientation_primary_pilot_v1.csv`;
- `docs/FDT3_ORIENTATION_REPEATED_EVOLUTION_PRIMARY_PILOT_2026-08-26.md`.

## Aim 2 functional order

1. **head orientation first** — timing/protection pathways and reproductive fitness;
2. **W/coloured comparison second** — availability-normalized colour choice, effective contact, abiotic context and fitness, nested with Aim 3;
3. **phyllary/spine conditional third** — only after direct botanical validation and a defensible manipulation;
4. **stickiness lower priority / negative-control evidence**, not a generic defence proxy.

The image-derived involucre/spine metrics remain morphological proxies; existing antagonist costs do not prove these proxies are defensive traits.

## Sampling

Core minimum = **190**:
- *C. brevicaule* 60
- *C. irumtiense* 60
- *C. pendulum* 40
- *C. sieboldii* 30

Controls +32:
- *C. lineare* 16
- *C. dipsacolepis* 16

Full minimum = **222**, recommended fuller design = **298**.

Aim 2 measurements remain nested within the same ancestry-resolved populations. Exact P001–P014 localities remain field/current-source verified rather than invented.

## Three unresolved new-data gates

Doctoral execution remains compressed to **three unresolved new-data gates**; the mechanism reductions sharpen Gate 2 but do not add a fourth gate.

1. **Aim 1:** same-individual phenotype + population ancestry + plastid + cytotype to resolve standing variation vs introgression vs lineage-specific origin.
2. **Aim 2:** determine which ancestry-linked capitulum modules alter antagonist cost, pollination/protection pathways and reproductive fitness.
3. **Aim 3:** same-individual floral-stage RNA + coding/regulatory haplotype + pigment + calibrated colour in at least two independent W/C transitions.

Canonical execution files:

- `data/evidence/doctoral_next_data_minimum_v1.csv`;
- `docs/DOCTORAL_NEXT_DATA_GATE_2026-08-19.md`;
- `sampling/SAMPLING_DESIGN.md`.

## Gate 2 operationalization

Aim 2 uses four linked levels:

1. individual/sample identity — `sampling/aim13_individual_sample_ledger_v1.csv`;
2. focal capitulum/treatment and final fitness — `sampling/aim2_capitulum_field_ledger_v1.csv`;
3. repeated time-stamped microclimate + display/density/colour context + pollinator + antagonist observation — `sampling/aim2_capitulum_observation_bout_ledger_v1.csv`;
4. plant-season display/predation — `sampling/aim2_plant_display_predation_ledger_v1.csv`.

Repeated bouts are not biological replicates. Final achene/seed output remains in the focal-head table. Pollinator and antagonist channels stay separate.

Detailed protocol:

`docs/AIM2_TRANCHE1_JOINT_OBSERVATION_PROTOCOL_2026-08-20.md`

## What must be secured during flowering

- immutable individual/population IDs and voucher-linked phenotype;
- calibrated visible/UV colour plus focal `colour_class`;
- natural orientation and direct phyllary/spine traits;
- time-stamped head-scale microclimate where measurable;
- focal display, quantitative local density and local colour availability;
- pollinator visits, heads probed and effective contacts as separate quantities;
- antagonist records on the same functional individuals/heads;
- total and filled achenes / mature seed output;
- Aim 3 floral RNA at late bud/pigmentation onset and pre-anthesis/fresh anthesis;
- separate pigment tissue linked to the same individual.

## Stop rules

- no heavy tree prerequisite for field sampling;
- no more broad climate-only preliminary models;
- no SRA/BLAST fishing as a substitute for morph-linked population/floral data;
- no broad interaction pooling simply because several studies exist;
- do not re-test whether insect antagonists can reduce *Cirsium* seed output; test **which module changes the cost**;
- no unpooled year/site pollinator parameter from four context slopes;
- no `white always preferred` parameter from significance-conditioned *C. palustre* cases;
- no colour-preference claim without local morph availability;
- no “adaptive radiation” claim until Aim 2 links a focal trait through interaction/protection to reproductive fitness.
