# Cross-layer capitulum pattern reduction

Status: 2026-08-20

## One purpose

Use **independent observed patterns**, not a growing list of verbal hypotheses, to ask what minimum mechanism family can jointly reproduce the current *Cirsium* capitulum evidence.

The layers remain separate:

```text
AZAMI — observation layer
Global image phenomics
    environment ↔ orientation / colour / shape / involucre proxies
    hierarchical within-taxon variation
            ↓ frozen target patterns only

EAzami — mechanism layer
Cirsium interaction / fitness literature + focal history
            ↓
minimal generative models / simulation
            ↓
Can one mechanism family reproduce BOTH layers?
```

Azami therefore remains an observational macro paper. The simulation does **not** turn its climate associations into causal claims inside that repository.

## Target registry

Machine-readable source:

`data/evidence/capitulum_pattern_reduction_targets_v1.csv`

Targets are deliberately evidence-typed.

### A. Azami global observation patterns

The reduction test currently preserves these high-level facts rather than refitting the entire image dataset:

1. **Large below-taxon visible variation**
   - across nine primary endpoints, observed below-taxon fractions span **0.5886–0.9307**;
   - this is image-level variance, not genetic variance.

2. **No universal visible-lability axis**
   - noise-adjusted dispersion × environmental-association Spearman rho = **−0.0569**;
   - bootstrap 95% interval **−0.265 to 0.155**;
   - the hierarchical variance meta-regression is likewise near zero.

3. **Environment structure is module-specific**
   - orientation × BIO1: beta **+0.017059**;
   - chroma × BIO12: beta **+0.039324**;
   - gross outline has no globally retained grouped-SPDE support;
   - the final simulation therefore asks for clear orientation/colour/defence structure with weaker generic shape structure, not for one climate response shared by every trait.

4. **Involucre/spine-like proxies share a seasonality signal**
   - roughness × BIO4: beta **+0.0975**;
   - spread fraction × BIO4: beta **+0.0937**;
   - maximum spine-like projection × BIO4: beta **+0.0911**.

These three variables remain image-geometry proxies. Their positive seasonality association is a pattern to explain, not evidence of defence.

## B. Direct Cirsium interaction / fitness patterns

These calibrate the mechanism layer more directly.

### 1. Antagonist fitness cost is quantitatively large

The harmonized experimental seed-output meta-analysis gives:

- reduced-herbivory / ambient-herbivory seed-output RR = **2.674**;
- 95% CI **2.388–2.993**;
- equivalent ambient-herbivory loss of potential seed output = **62.6%**;
- I² ≈ **1.0%**.

This is the strongest current numerical interaction target.

### 2. Floral display attracts antagonists in C. purpuratum

Ohashi & Yahara's two populations give explicit saturating functions for seed damage probability `Pr` against total floret production `F`:

- Nikko: `Pr = 1 − exp(−0.000063 F)`, n=13, R²=0.44, P=0.013;
- Kawamata: `Pr = 1 − exp(−0.0000075 F)`, n=27, R²=0.26, P=0.007.

The approximately 8.4-fold difference in the fitted attack coefficient is itself important: **the same display size can face very different antagonist regimes among populations**.

At Nikko, 90.8% of heads were infested at the population level and the probability of a seed being preyed upon was 25.3%; individual plant damage ranged from 7.9 to 51.5%.

### 3. The same display also attracts pollinators, but sublinearly

For *C. purpuratum* / *Bombus diversus*:

- visitation rate per plant increases **deceleratingly** with floral display size;
- heads probed per visit increase less than proportionally with display size;
- 1997 head-probing slopes: high density **0.11**, low density **0.25**;
- 1998 slopes: high density **0.078**, low density **0.24**.

Thus local plant density changes the behavioural return to a large display. Larger display is not simply translated one-for-one into more effective flower use.

### 4. Floral signalling can expose a mutualist–antagonist scheduling problem

In *C. arvense* and *C. repandum*, fragrance was highest near reproductive maturity when insect activity was also high. In *C. arvense*, diel emission tracked pollinator activity and was low when florivores were active. *C. repandum* fragrance emission was about **25-fold lower** than staminate *C. arvense*.

This is not a target for the first structural simulation, but it shows that temporal regulation can solve the same attraction–enemy conflict without changing gross capitulum geometry.

### 5. Seed predation can be severe at the head scale

In *C. pitcheri*, weevil-infested capitula produced **60% fewer mature seeds** and **40% fewer unfilled seeds**, with infestation concentrated in nonterminal capitula.

In *C. arvense*, reported geographic/date ranges include **20–85% of heads attacked** and **20–80% of seeds damaged within attacked heads**.

### 6. Antagonist losses propagate through the life cycle

For *C. canescens*, one field study reported that an approximately **3-fold** insect-driven reduction in viable seeds propagated to an approximately **6-fold** reduction in seedling establishment and a **6–37-fold** reduction in eventual new adults.

The first simulation uses seed output because it is the harmonized endpoint. The longer demographic cascade remains a later validation layer.

### 7. Not every defensive-looking trait works

Neutralizing sticky exudates on *C. discolor* inflorescences did **not** increase seed predators or reduce seed production. Sticky morphology is therefore a useful negative control against assuming function from appearance.

### 8. Pollination can also constrain reproductive output

A 2025 exclusion experiment including *C. discolor* found complete pollinator exclusion produced **55% total reproductive failure**, whereas failure was **<7%** in other treatments; among heads producing viable seed, any exclusion reduced seed output.

The implication is not that every *Cirsium* is equally pollen limited. It is that the model needs a real pollinator-benefit channel, not antagonist defence alone.

### 9. Flower colour can alter pollination

*C. palustre* provides direct evidence of preferential pollination of the white morph. The current target registry stores the direction only because a harmonized numerical effect size has not yet been frozen.

## C. Asteraceae mechanism priors — external calibration, not Cirsium evidence

These are intentionally lower-priority targets.

### Capitulum size and seed predation

Fenner et al. monitored **20 common Asteraceae species, three populations per species**. Infestation increased with capitulum size among species, and in all three species examined in detail the same positive size–infestation relationship occurred within species. Capitulum lifespan and flowering synchrony did not explain infestation.

This supports a general display/defence trade-off but is not treated as a *Cirsium*-specific effect size.

### Nodding orientation and abiotic protection

In *Cremanthodium campanulatum*:

- natural nodding achene set = **56.3 ± 3.9%**;
- artificially erect achene set = **15.7 ± 3.6%**;
- F=59.1, P<0.01, n=30;
- pollinators showed no preference between orientation treatments.

This gives a useful external pattern: **orientation can have a large fitness effect through protection without increasing pollinator attraction**.

### Sunflower orientation shows the same separation of mechanisms

In *Helianthus annuus*, east-facing capitula had earlier morning pollen presentation and pollinator visits and out-sired west-facing plants in **5 of 7** trials; a sixth trial showed the same nonsignificant direction. A later 2024 field study found **no all-day pollinator-landing effect of head azimuth**.

Together these constrain interpretation: orientation effects can be strongly time- and microclimate-dependent rather than a simple all-day attraction multiplier.

## Initial reduction simulation

Canonical script:

`analysis/simulate_capitulum_pattern_reduction_v1.py`

Frozen output:

`data/evidence/capitulum_pattern_reduction_simulation_v1.json`

The first model family is deliberately small:

1. `ENV_ONLY` — environment/abiotic response only;
2. `ENV_POLL` — environment + pollinator channel;
3. `ENV_ANT` — environment + antagonist channel;
4. `FULL_COUPLED` — environment + pollinator + antagonist, but all modules share one latent within-taxon lability axis;
5. `FULL_MODULAR` — the same three mechanism classes, with module-specific within-taxon variance.

Each model receives **500 broad parameter draws**. A draw passes only if it simultaneously satisfies a selected subset of independent patterns:

- Azami below-taxon variance range;
- near-zero common cross-module lability coupling;
- stronger orientation/colour/defence environmental structure than generic shape structure;
- Cirsium herbivory-removal RR inside the observed 95% interval;
- positive display→predation relationship;
- positive but decelerating display→pollination relationship;
- a large orientation-protection effect under a high-stress external Asteraceae calibration.

### Result

| model | accepted / 500 | best remaining failures |
|---|---:|---|
| ENV_ONLY | 0 | common lability + pollinator + antagonist targets |
| ENV_POLL | 0 | common lability + antagonist targets |
| ENV_ANT | 0 | common lability + pollinator target |
| FULL_COUPLED | 0 | **common lability only** |
| FULL_MODULAR | **2** | none |

The useful result is not the tiny acceptance percentage itself. It is the **failure sequence**:

```text
environment only
    + pollination still misses antagonist pattern
    + antagonism still misses pollination pattern
    + both can reproduce interaction patterns
    BUT one shared lability axis conflicts with Azami
    ↓
module-specific variation removes the last structural conflict
```

## Interpretation boundary

This is a **pattern-reduction screen**, not proof of modular evolvability.

The simulation was designed to ask whether a very small set of mechanism classes can coexist with the observed pattern vector. Thresholds such as `|cross-module lability correlation| <= 0.15` are operational acceptance rules, not posterior biological estimates. Different functional forms may generate the same summaries.

What it does establish is a useful next question:

> Can a quantitatively fitted model with environment, pollinator benefit and antagonist cost reproduce the observed cross-scale pattern **without** allowing trait modules to vary semi-independently?

The current minimal answer is **not in this model family**.

## Next quantitative upgrades

1. Replace binary acceptance thresholds with a distance/likelihood or ABC score using full uncertainty intervals.
2. Reanalyse public raw *C. altissimum* experiments before adding a fifth seed-output study; do not use figure-read model predictions as independent RR data.
3. Expand the pollination side using directly recoverable head-level seed output or effective-pollination statistics rather than visitor counts alone.
4. Add population-specific antagonist pressure because the two *C. purpuratum* attack coefficients differ by ~8.4-fold.
5. After focal field data arrive, replace the external *Cremanthodium* orientation calibration with ancestry-linked *Cirsium* orientation→wetting/pollen→fitness measurements.
6. Only then compare whether observed Azami environment–trait slopes emerge from the same fitted interaction model rather than being imposed as target signs.

## Repository boundary

- **Azami:** owns the observational environment–trait and within-taxon pattern measurements.
- **EAzami:** owns the mechanism registry, interaction meta-analysis, field tests and pattern-reduction simulation.

Do not move simulation-derived causal language back into the Azami submission manuscript.
