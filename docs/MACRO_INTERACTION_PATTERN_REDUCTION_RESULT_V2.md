# Pattern-reduction simulation v2 — robust result

Status: 2026-08-20

## Question

Can one compact mechanism family reproduce **both**:

1. the frozen Azami global observation bundle; and
2. independent numerical patterns from pollination, antagonist and fitness studies?

This version strengthens v1 by replacing a single lucky best-draw comparison with a multi-seed, top-5%-accepted structural screen and held-out literature checks.

## Run contract

- target registry: `data/evidence/macro_interaction_pattern_targets_v2.csv`
- interaction ledger: `data/evidence/interaction_quantitative_pattern_ledger_v1.csv`
- total target rows: **31**
- core fit targets: **11**
- represented held-out checks: **5**
- model families: **5**
- draws: **180 × 4 seeds = 720 per family**
- ABC-like accepted set: top **5% = 36 draws per family**
- frozen result: `data/evidence/macro_interaction_pattern_reduction_result_v2.json`

This is a prior-predictive structural sufficiency analysis, not likelihood fitting or posterior model probability.

## Main ranking

| model family | accepted median core matches | accepted median distance | held-out mean reproduction |
|---|---:|---:|---:|
| full trade-off + modular evolvability | **9/11** | **0.287** | **0.706** |
| full trade-off + common lability | **9/11** | 0.297 | 0.689 |
| antagonist only | 8/11 | 0.419 | 0.417 |
| pollinator only | 8/11 | 0.429 | 0.317 |
| environment only | 7/11 | 0.586 | 0.133 |

The two full models are clearly separated from all single-driver families. Their difference from each other is small.

## Result 1 — a single driver is robustly insufficient

Across 720 draws per family, none of the three single-driver families generated the full core bundle.

Their top 5% draws also generalized poorly to held-out interaction evidence:

- environment only: **0.133** mean held-out reproduction;
- pollinator only: **0.317**;
- antagonist only: **0.417**.

The reason is biological, not just statistical:

- environment-only can recover Azami-like environment structure but cannot generate pollinator responses or the empirical herbivory fitness cost;
- pollinator-only can recover display→pollinator effects but misses antagonist cost;
- antagonist-only can recover seed-cost and enemy-exposure patterns but misses pollinator benefit and much of the environmental bundle.

Therefore the joint empirical bundle requires **environmental structure + mutualist response + antagonist cost** more clearly than any one process alone.

## Result 2 — full ecological trade-off models generalize to held-out literature

Among the top 5% core-fitting draws:

### Full trade-off + common lability

Held-out reproduction rates:

- larger display/head → greater antagonist exposure: **0.861**;
- external *C. pitcheri* seed-cost magnitude: **0.889**;
- held-out *C. purpuratum* heads-probed R²: **0.639**;
- held-out Kawamata predation R²: **0.278**;
- shared advertisement attracts both guilds analogue: **0.778**.

Mean = **0.689**.

### Full trade-off + modular evolvability

- larger display/head → greater antagonist exposure: **0.833**;
- external *C. pitcheri* seed-cost magnitude: **0.806**;
- held-out *C. purpuratum* heads-probed R²: **0.806**;
- held-out Kawamata predation R²: **0.333**;
- shared advertisement attracts both guilds analogue: **0.750**.

Mean = **0.706**.

Thus the full models do not merely fit the exact values used in the compact core. Their accepted draws also reproduce several independent interaction patterns substantially more often than the single-driver families.

## Result 3 — modularity remains plausible, not demonstrated

The robust ranking places `full_tradeoff_modular_evolvability` first because it has:

- slightly smaller accepted median pattern distance: **0.287 vs 0.297**;
- slightly higher held-out reproduction: **0.706 vs 0.689**.

However, the difference is small. In fact, `full_tradeoff_common_lability` produced the only **11/11 core draw** in this multi-seed run, with full-core frequency 1/720.

Therefore the correct inference is:

> **Joint environmental, mutualist and antagonist processes are required much more clearly than module-specific evolvability is required. Current data do not yet decisively distinguish common lability from modular evolvability.**

Modularity remains the doctoral hypothesis to test with ancestry-resolved and module-specific data, not a conclusion of the simulation.

## Result 4 — the most informative output is now model failure

The expanded literature ledger exposes mechanisms the current compact generator cannot represent:

1. **flower-colour choice** — *C. palustre* white-morph preferential pollination;
2. **trait-specific defence null** — *C. discolor* stickiness manipulation is null;
3. **strong orientation-mediated abiotic protection** — *Cremanthodium* natural nodding 56.3% vs artificial erect 15.7% achene set, ratio ≈ **3.59×**;
4. **orientation without pollinator preference** — the same *Cremanthodium* experiment detected no orientation preference by pollinators;
5. **time-window dependence** — sunflower orientation changes early-morning visits/siring, while all-day landing effects can be weak/null;
6. **state/year-dependent tolerance** — *C. undulatum* compensation depends on year and subsequent floral-herbivore pressure;
7. **pollinator/reproductive-assurance state** — exclusion experiments and interspecific *Cirsium* comparisons show that pollinator dependence is not universal.

These failures are more useful than adding arbitrary model families.

## Biological reduction reached so far

The current joint evidence can be reduced to this minimal causal scaffold:

```text
environment
   ↓
capitulum modules
   ├── advertisement ──→ pollinator benefit (saturating)
   │                  └→ antagonist exposure
   ├── orientation ───→ pollination timing
   │                  └→ rain / UV / thermal protection
   └── defence architecture ─→ successful antagonist damage

pollination benefit + abiotic protection − antagonist damage
                         ↓
                 reproductive fitness
```

The next scientific question is no longer whether environment, pollinators or antagonists matter. It is whether **module-specific pathways and state dependence** are necessary to reproduce the remaining patterns.

## Next model escalation

Do not build a large ABM yet.

The highest-value next extension is an **orientation-specific reduced model** containing only:

- early vs all-day time windows;
- head orientation;
- temperature/pollinator timing;
- rain/UV pollen protection;
- seed/achene fitness.

It can be checked directly against the held-out *Cremanthodium* 3.59× achene-set ratio and sunflower early-positive/all-day-null pattern.

A second later extension can add:

- pollinator-dependence / autonomous selfing state;
- year-dependent tolerance;
- direct validated phyllary/spine defence.

## Repository boundary

- `zuizui0223/azami` retains the frozen global observational environment–trait patterns.
- `zuizui0223/EAzami` owns this mechanism-reduction simulation and biological-interaction evidence.

A successful EAzami model does not make the Azami correlations causal.

## Claim boundary

The v2 ranking is not a Bayes factor, likelihood comparison, posterior model probability, proof of adaptation, or proof of modular evolvability. It is evidence that the **joint pattern bundle is structurally hard to generate with one driver**, and it identifies exactly which additional mechanisms need empirical or simulation-level resolution next.
