# Doctoral evidence ladder: global capitulum diversity -> ecological mechanism -> East-Asian rapid radiation

Status: 2026-08-23

## Decision

The doctoral programme is organized as an evidence ladder rather than a list of loosely connected analyses:

```text
Azami: global observational phenotype/environment landscape
    ->
EAzami: quantitative literature/meta-analysis of ecological mechanisms
    ->
EAzami: East-Asian/Japanese rapid-radiation evolutionary history
    ->
EAzami: repeated-state tests for capitulum modules
    ->
Doctoral empirical work: ancestry-resolved trait -> mechanism -> reproductive fitness
    ->
Molecular reuse test for repeated flower-colour transitions
```

The current central ecological hypothesis is **selection mosaics acting on semi-independent capitulum modules**. The current central evolutionary hypothesis is **modular evolvability during a young, reticulating radiation**, with a shared **common-lability** axis retained as the main competing model.

The point of the literature/meta-analysis layer is not to declare focal East-Asian adaptation. Its job is to decide which general hypotheses are already supported, weakened or saturated by prior evidence, so that doctoral field/genomic work is spent only on questions that generic literature cannot answer.

---

## 1. Repository boundary: Azami and EAzami are not two versions of the same paper

### Azami = global observational discovery

`zuizui0223/azami` stops at:

```text
public images
-> continuous head-level phenotype measurements
-> within-taxon trait distributions
-> within- and among-taxon environmental structure
```

Frozen Azami conclusions used here as premises are:

- across nine primary visible endpoints, **0.589-0.931** of visible image variance occurs below source-assigned taxon means;
- orientation and visible colour show the clearest environmental structure;
- gross outline is weaker/model-dependent;
- involucre/spine-like image geometry covaries with temperature seasonality, but these are **2-D image proxies**, not validated defence traits.

Azami therefore does **not** claim genetic variance, local adaptation, pollinator causation, defence, evolutionary rate, repeated evolution or adaptive radiation.

### EAzami = mechanism and evolutionary-history zoom

EAzami begins exactly where Azami must stop:

1. test ecological mechanism hypotheses against quantitative prior literature;
2. place capitulum states in a credible East-Asian nuclear evolutionary history;
3. ask whether the same states recur independently in a young radiation;
4. test whether those states alter pollination, protection or antagonism and reach reproductive fitness;
5. for flower colour, test whether repeated states reuse retained molecular machinery.

This boundary allows the same biological observation to be used at two scales without overclaiming it: Azami describes global within/among-taxon pattern; EAzami asks how population-level ecology and ancestry can generate repeated among-lineage states.

---

## 2. What prior literature/meta-analysis has already resolved

### 2.1 A single universal driver is not an adequate general model

The generic alternative was that capitulum/floral diversity could be explained by one dominant axis: direct climate scaling, pollinator pressure, or antagonist pressure.

The current quantitative/structured synthesis does not support that simplification.

- broad direct abiotic scaling is weakened as a universal mechanism;
- reproductive assurance varies with selfing, donor spacing, flowering synchrony and density, so pollinator dependence is not equivalent to current pollen limitation;
- seed-output effects can transmit to recruitment, become context dependent, or be blocked by safe-site/disturbance/density gates;
- in five strict pollination x antagonism manipulation programmes, agent dominance is **antagonist 2 / pollinator 1 / mixed or no fixed dominance 2**;
- the heterogeneity is not removed by leave-one-program-out deletion;
- 38 standardized pollinator-mediated selection gradients from six articles do not identify a universal broad functional-class hierarchy.

**Meta-level conclusion:** the best-supported general architecture is a **selection mosaic** rather than a universal agent.

Conceptually:

```text
environment + spatial/population context
-> pollinator opportunity / reproductive assurance / enemy pressure / abiotic exposure
-> local leverage of a particular capitulum module
-> pollination / protection / antagonism
-> reproductive fitness
-> demographic recruitment gate
```

This is a causal architecture to test, not a fitted multiplicative law.

### 2.2 Reproductive antagonist pressure is quantitatively established

The narrow harmonized random-effects meta-analysis is the strongest resolved ecological result.

- 4 independent *Cirsium* data-generation studies;
- 9 within-study contrasts, collapsed to study level before across-study pooling;
- estimand: seed output under experimentally reduced insect herbivory relative to ambient herbivory;
- pooled **RR = 2.674**;
- 95% CI **2.388-2.993**;
- equivalent ambient loss of potential seed output = **62.6%**;
- heterogeneity is low (**I2 about 1%**);
- the positive effect remains under leave-one-study-out deletion.

Therefore the doctoral question is no longer "can reproductive enemies matter?". It is:

> **Which capitulum modules change this established enemy cost, and what pollination or abiotic cost accompanies that protection?**

The pooled effect does not show that orientation, spines, phyllaries or stickiness are adaptations.

### 2.3 Reproductive assurance and demographic gating remain context dependent

Prior *Cirsium* studies establish two important negative constraints on simplistic ecological stories:

1. visitor abundance or animal dependence cannot be used as a direct substitute for pollen limitation or seed fitness;
2. a seed-output effect cannot automatically be interpreted as a population-growth effect.

These results justify keeping donor spacing, flowering overlap, density and later recruitment as explicit gates rather than nuisance covariates.

### 2.4 Module-specific prior conclusions

#### Orientation

External Asteraceae manipulation shows that nodding capitula can preserve pollen/achene production under rain/UV exposure without a static pollinator preference. Other timing evidence motivates explicit early-versus-later pollinator windows. Prior evidence therefore supports **time-window pollination + abiotic protection** as a mechanism family worth discriminating, not a claim that all nodding *Cirsium* use that mechanism.

#### Display: capitulum size and head number

*Cirsium purpuratum* studies show that greater display can increase pollinator discovery/probing while predispersal seed predation also rises with floral production, and pollinator responses depend on local density/context.

The useful hypothesis is therefore a **local benefit-cost surface**, not `bigger is better`.

#### Phyllary/spine architecture

Broader Cardueae/Asteraceae evidence makes antagonist exclusion biologically plausible, but there is not yet a harmonized focal *Cirsium* trait-specific effect that proves defensive adaptation. Azami's image geometry cannot substitute for direct botanical measurements.

#### Stickiness / mucilage

A direct *Cirsium discolor* neutralization experiment did not increase seed predators or reduce seed production. Generic `sticky inflorescence = reproductive defence` is therefore **weakened** and should remain a low-priority or negative-control lane unless new focal evidence reopens it.

### Meta-analysis stop rule

The generic heterogeneous literature phase has reached its current decision ceiling. More papers of different taxa, traits and response scales are not expected to identify which agent or mechanism operates in the focal East-Asian populations.

Reopen generic meta-analysis only if a new study supplies:

- a prespecified homologous estimand that materially changes a pooled effect; or
- a manipulation capable of changing a focal mechanism or sampling decision.

---

## 3. What our own analyses can resolve before new doctoral field data

## 3.1 Global scale: where diversity exists

Azami establishes that important capitulum variation occurs both **within taxa** and **among taxa**. This changes the downstream evolutionary framing: species cannot be treated as fixed phenotype endpoints if the raw variation on which selection can act is already abundant within named taxa.

The doctoral prediction is therefore multiscale:

> population-level ecological mosaics and ancestry-linked within-species variation may supply variation that later appears as repeated among-lineage states during rapid radiation.

This remains a prediction; within-species variation is not automatically heritable ancestral polymorphism or adaptation.

## 3.2 East-Asian tree: the historical scaffold is now usable

EAzami has now completed an empirical compatibility tree route:

- frozen 153-locus nuclear matrix;
- 140,562-bp concatenated alignment;
- *Carthamus* (`OUTGROUP_saff`) root;
- accepted branch lengths in substitutions/site;
- explicit gene/site concordance sensitivity;
- six AU-nonrejected local topology alternatives retained rather than hiding uncertainty.

This is not an exact reproduction of the augmented Moreyra et al. matrix, but it is sufficient as a source-frozen compatibility framework for current repeated-state preflight analyses.

## 3.3 Orientation: repeated state change is now a result, not merely a hypothesis

The conservative orientation crosswalk resolves 17/20 current focal taxa:

- upward/erect = 9;
- downward/nodding = 8;
- three ambiguous/conflicting taxa remain missing rather than being forced into a binary state.

Across **all six AU-nonrejected topology candidates**, the minimum parsimony requirement is exactly **5 orientation-state changes**.

The Mk sensitivity does **not** resolve direction:

- ER is preferred over ARD by AICc across the evaluated cells;
- there is no supported directional rate asymmetry;
- root upward probability remains close to equivocal;
- ancestral orientation is unresolved.

Thus the current defensible evolutionary conclusion is:

> **erect/upward and nodding/downward states changed repeatedly in the sampled East-Asian panel.**

The words `parallel`, `convergent` and `adaptive` remain blocked because the states are taxon-concept annotations rather than same-voucher/population phenotypes and because ecological causation has not been demonstrated.

## 3.4 Flower colour: tree solved, transition-direction gate not solved

The current exact rate-fit atlas contains:

- C = 17;
- W = 3.

The tree side is ready, but the predeclared breadth gate requires W >= 5. Two additional fixed-white homologous nuclear species tips are still required before a final 22-focal-taxon tree can be rebuilt and reaccepted.

Therefore the current data can support ecological W/C function comparisons in ancestry-matched situations, but they cannot yet identify a robust macroevolutionary C->W versus W->C rate or declare *C. irumtiense* a colour regain.

The active high-value colour hypothesis remains:

> **white states may sometimes preserve anthocyanin machinery by regulatory suppression, allowing coloured expression to reappear when the ecological selection mosaic changes.**

This must be tested across at least two credible independent W/C transitions rather than inferred from one Arenicola contrast.

---

## 4. Why the East-Asian zoom matters for rapid radiation

Published phylogenomics supports a major continental-Asian -> Japan jump dispersal at about **2.4 Ma** (95% interval 1.7-3.6 Ma), followed by rapid Japanese diversification. The published interpretation allows both geographic and ecological speciation.

The significance of the system is not simply that Japan has many *Cirsium* species. It provides a relatively shallow evolutionary interval in which large capitulum disparity, incomplete lineage sorting/reticulation and repeated trait states can be compared without requiring deep divergence among every phenotype.

This makes East Asia a natural test of two competing explanations.

### Model A — modular evolvability

```text
standing ancestral variation / introgression / developmental reuse
-> semi-independent capitulum modules
-> local selection mosaics favour different module states
-> repeated state changes across shallow lineages
-> ecological divergence can accumulate faster than genome-wide lineage sorting
```

### Model B — common lability

```text
one shared whole-phenotype lability axis
-> correlated trait variability
-> apparent repeated module changes without genuinely independent ecological modules
```

Current evidence is enough to motivate the comparison, not decide it. Orientation now provides one robust repeated-state module. Colour, display and validated defence need equivalent evolutionary/function evidence before modular evolvability can be preferred over common lability.

### Adaptive-radiation boundary

Use **rapid radiation** as the current system conclusion.

Do not use **adaptive radiation** as a recovered result until at least one repeated focal capitulum trait is linked causally through a preregistered ecological mechanism to reproductive fitness. Repeated states alone are not evidence of adaptation.

---

## 5. Module-by-module doctoral frontier

## 5.1 Orientation — first causal module

**Already resolved:** repeated state change, minimum five changes across all six accepted topologies.

**Still unresolved:** whether independent changes repeatedly solve the same ecological problem.

Primary causal alternatives:

1. `orientation -> time-window temperature/presentation -> effective pollination -> filled achenes`;
2. `orientation -> rain/wetting/UV exposure -> pollen/reproductive-organ protection -> filled achenes`;
3. `orientation -> antagonist discovery/access -> damage -> filled achenes` as a separate competing path.

Required data:

- same-voucher/population orientation;
- sham-controlled reorientation;
- early/later observation windows rather than all-day visitation only;
- effective stigma/anther contact and pollen state;
- wetting/rain/UV exposure and pollen integrity;
- antagonist exposure/damage kept separate;
- final filled achenes.

A fitness effect without movement in the preregistered mechanisms remains an allowed unexplained outcome rather than evidence for a preferred mechanism.

## 5.2 Flower colour — history, ecology and molecular reuse are three separate questions

### Evolutionary-history question

How many independent W/C transitions exist, and in which direction did they occur?

Need:

- two additional credible fixed-white homologous nuclear tips to clear W=5;
- exact 22-focal-taxon branch-length tree rebuild/reacceptance;
- topology/model-adequacy sensitivity;
- population-aware colour validation.

### Ecological-function question

Does W/C phenotype alter effective pollination or abiotic response in overlapping, ancestry-controlled contexts?

Need:

- calibrated visible + UV colour;
- visitor guild and effective contact rather than visitation alone;
- relevant local abiotic measurements;
- filled-achene fitness.

### Molecular re-expression question

Do repeated transitions reuse retained anthocyanin machinery?

Need, for at least two independent transitions:

```text
ancestry
-> coding/regulatory haplotype
-> matched floral RNA
-> pigment chemistry
-> calibrated colour
```

Only this chain can turn `possible regain` into evidence for recurrent molecular reuse.

## 5.3 Phyllary/spine — validate the trait before testing defence

Required order:

1. replace Azami image proxies with direct botanical phyllary spread/spine length/direction;
2. verify repeatable focal within-population variation;
3. if the trait is manipulable without dominant wounding artefacts, test antagonist access/damage;
4. simultaneously measure pollinator effective contact and filled achenes.

Prediction:

```text
more excluding architecture
-> antagonist access/damage down
-> seed fitness up
```

with a possible counter-path:

```text
more excluding architecture
-> pollinator access/effective contact down
-> seed fitness down
```

## 5.4 Stickiness / mucilage — low priority unless reopened

Current direct prior evidence weakens a general defence claim. Do not make this a standalone doctoral Aim.

Reopen only if focal East-Asian material shows strong repeatable variation linked to enemy exposure or if new comparable manipulations overturn the current null prior.

## 5.5 Display — mutualist benefit versus antagonist cost

Prediction:

```text
head number / capitulum size + local flowering density
-> pollinator discovery/probing and effective contact
AND
-> antagonist discovery/predation
-> net filled-achene fitness
```

The target is a context-dependent optimum or benefit-cost surface, not a positive main effect of display size.

Required data must stay at the correct level:

- whole-plant head number and local flowering density;
- capitulum size;
- visits, heads probed and effective contacts kept distinct;
- seasonal antagonist exposure/damage;
- final filled achenes.

---

## 6. The multiscale bridge: within species and among species are both required

The global and East-Asian programmes should use the same hierarchy rather than treat species and populations as separate stories.

### Within species / among populations

Ask how environment, pollinator opportunity, antagonist pressure, reproductive assurance and ancestry predict module variation and fitness.

Required individual linkage:

```text
individual_id
-> population/locality/voucher
-> colour/orientation/phyllary/display
-> nuclear ancestry
-> plastid haplotype
-> cytotype
-> interaction/protection measurements
-> reproductive fitness
```

### Among species / lineages

Ask whether states validated at population level recur independently on the accepted nuclear history and whether independent transitions recur in similar ecological contexts.

The critical connection is:

> **within-population variation supplies the ecological and ancestry-resolved process; among-lineage repeated states supply evolutionary replication.**

Neither level substitutes for the other.

---

## 7. What is now an existing-data question versus a doctoral empirical question

### Existing data / computation can still resolve

- maintain and test the accepted East-Asian topology uncertainty set;
- refine source-backed population/taxon trait states where lawful evidence exists;
- add homologous fixed-white nuclear data if public data become available;
- rebuild the 22-tip colour tree once the input gate is met;
- compare environmental contexts around independently supported transitions;
- formulate and preregister shared-latent versus module-specific models before seeing final focal fitness results.

### Existing data cannot resolve

- which ecological agent dominates selection in each focal East-Asian population;
- whether orientation's repeated changes are parallel adaptations to timing/protection;
- whether W/C differences causally alter effective pollination or fitness;
- whether *C. irumtiense* is a true colour re-expression after white loss;
- whether phyllary/spines are defensive adaptations in focal *Cirsium*;
- where the display fitness optimum lies in each population;
- whether regulatory/molecular machinery is reused across independent colour transitions;
- whether rapid radiation is demonstrably adaptive;
- whether modular evolvability outpredicts common lability once ancestry and fitness are observed.

These unresolved items belong in the single doctoral execution issue, not in Azami and not in additional generic meta-analysis.

---

## 8. Doctoral programme after evidence reduction

### Aim 1 — evolutionary history and source of repeated states

Question:

> Are repeated capitulum states generated from standing ancestral variation, introgression/reticulation and cytotype/cytonuclear history within the young East-Asian radiation?

Core evidence:

`phenotype -> nuclear ancestry -> plastid -> cytotype -> independent transition history`

Orientation is the first module with a robust repeated-state signal; colour is the next high-value transition system after the fixed-white gate is cleared.

### Aim 2 — ecological function and adaptive significance

Question:

> Which capitulum modules alter local pollination, protection and antagonist pathways, and do those changes reach reproductive fitness under different selection mosaics?

Priority:

1. orientation manipulation;
2. W/coloured ecological function where flowering overlaps;
3. display benefit-cost measurements nested in the same plants;
4. phyllary/spine after direct botanical validation;
5. stickiness only if reopened.

### Aim 3 — flower-colour reversibility and molecular reuse

Question:

> Do independent W/C transitions repeatedly use retained anthocyanin regulatory/developmental machinery rather than independent pathway destruction and reconstruction?

This is the mechanistic flagship only after Aim 1 establishes independent transitions.

---

## 9. Current thesis statement

The strongest current synthesis is:

> **Global thistle image phenomics shows that capitulum diversity is extensive within as well as among taxa and that orientation and visible colour are especially environmentally structured. Quantitative prior literature rejects a universal climate- or pollinator-only explanation and instead supports context-dependent selection mosaics in which pollination, reproductive assurance, antagonism, abiotic protection and demographic gates can differ among populations. The young East-Asian/Japanese Cirsium radiation then provides an evolutionary replication system: an accepted nuclear framework already shows at least five repeated orientation-state changes across every retained topology. The doctoral programme tests whether such repeated states are generated by reusable semi-independent capitulum modules, whether local selection mosaics make those states adaptive, and whether repeated flower-colour transitions reuse retained molecular machinery.**

This remains a programme hypothesis until the ancestry-resolved ecological fitness and molecular gates are closed.

## Canonical machine-readable sources

- `data/evidence/doctoral_global_to_east_asia_evidence_ladder_v2.csv`
- `data/evidence/doctoral_global_to_east_asia_summary_v2.json`
- `data/evidence/doctoral_meta_resolution_gate_v1.json`
- `data/evidence/cirsium_floral_herbivory_lnrr_meta_v2.json`
- `data/evidence/doctoral_ecological_hypothesis_registry_v2.csv`
- `data/evidence/orientation_comp1061_posttree_ensemble_preflight_v1.json`
- `data/evidence/flower_colour_rate_tree_contract_v0_2.json`
- `data/evidence/fixed_white_tree_promotion_contract_v0_2.json`

The 2026-08-22 global-to-East-Asia synthesis remains provenance; this document is the current evidence-order interface.
