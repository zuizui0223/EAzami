# Orientation mechanism reduction — result v1

Status: 2026-08-20

## Question

Can the cross-study orientation pattern be reduced to one static `orientation → pollinator preference` effect, or are separate time-dependent pollination and abiotic-protection pathways needed?

The target bundle deliberately combines different comparison contexts without claiming homology:

- Azami: orientation has a positive within-taxon temperature association;
- *Cremanthodium campanulatum*: natural nodding vs artificial erect achene set **56.3% vs 15.7%** (RR ≈ **3.59**) with no detected pollinator orientation preference;
- *Helianthus annuus*: east-facing heads receive earlier morning visits and have a siring advantage;
- later/all-day sunflower landing effects can be weak or null.

## Model families

1. `static_pollinator_only`
2. `abiotic_protection_only`
3. `thermal_timing_only`
4. `combined_static_pollinator_abiotic`
5. `combined_time_abiotic`

All families retain an environment→orientation background because macro-interaction v2 already showed that a viable full explanation needs the environment layer.

## Result

| family | accepted median core match | median distance | full 5/5 rate | held-out mean |
|---|---:|---:|---:|---:|
| combined time-window pollination + abiotic protection | **5/5** | **0.039** | **0.183** | **1.000** |
| abiotic protection only | 4/5 | 0.127 | 0 | 0.500 |
| thermal timing only | 4/5 | 0.402 | 0 | 0.500 |
| static pollinator + abiotic protection | 3/5 | 0.556 | 0.0013 | 0.867 |
| static pollinator only | 3/5 | 0.809 | 0 | 0.407 |

The best combined time+abiotic draw generated:

- orientation–temperature `r = +0.182`;
- *Cremanthodium*-analogue nodding/erect achene RR = **3.618**;
- nodding–erect pollinator difference = **0**;
- protected/exposed pollen-viability RR = **3.618**;
- sunflower-analogue early visit RR = **1.584**;
- all-day visit RR = **1.0004**;
- siring RR = **1.321**.

These are simulated summaries, not empirical estimates.

## What fails

### Static pollinator preference alone

It can create an early orientation effect, but cannot simultaneously produce:

- a large achene benefit with pollinator preference near zero; and
- an early visit difference that disappears in the all-day total.

Its accepted median core match is only **3/5**.

### Abiotic protection alone

It reproduces the *Cremanthodium* side very cleanly:

- best achene RR **3.584**;
- pollinator difference **0**;
- all-day visit RR **1**.

But it necessarily misses the sunflower early-morning visitation/siring pathway. Median = **4/5**.

### Thermal timing alone

It reproduces:

- early visit increase;
- all-day near-null;
- siring sign.

But it cannot generate the large nodding-head achene benefit when pollinator preference is absent. Median = **4/5**.

### Static pollinator + abiotic protection

This family can rarely hit all five targets, but only **0.13%** of draws do so and its accepted-set median falls to **3/5**. A persistent static visitation preference conflicts with the empirical combination of strong fitness protection, pollinator null, and time-window-specific orientation effects.

## Reduction reached

Within this declared toy generator, the cross-study orientation bundle is most parsimoniously represented as **two separable pathways**:

```text
orientation / environment
   ├── thermal timing ──→ early pollen presentation / early visitation ──→ male fitness
   └── rain / UV protection ──→ pollen viability ──→ achene / seed fitness

all-day visitation can remain approximately unchanged
```

This gives a much more specific doctoral hypothesis than `head orientation affects pollinators`.

## Consequence for Aim 2 field design

The orientation experiment should therefore measure the pathways separately rather than only counting total visits:

1. natural and experimentally achieved head angle;
2. time-stamped visits, especially early-day versus whole-day;
3. head/floral temperature;
4. rain/wetting exposure;
5. pollen wetting and viability;
6. effective anther/stigma contact;
7. final total and filled achenes.

If Cirsium orientation acts mainly through abiotic protection, visit counts can be null while fitness effects remain large. If it acts mainly through timing, an all-day visit total can erase a biologically important early effect.

## Claim boundary

This is a structural-sufficiency comparison across literature-derived mechanisms. It does **not** show that *Cirsium* uses the *Cremanthodium* or sunflower mechanism, does not establish adaptation, and does not make the Azami orientation–temperature correlation causal.

Its value is experimental discrimination: the current evidence says **do not reduce orientation to one static visitation coefficient**.
