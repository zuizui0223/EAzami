# Orientation × BIO15 geography causal-boundary test

Status date: 2026-09-04  
Role: **validated post-result falsification / causal-boundary analysis**

## Question

The East-Asian orientation comparison shows a large present-day BIO15 contrast. The immediate alternative explanation is coarse geography: perhaps downward/nodding taxa simply occupy a different region or latitude/longitude range.

This analysis asks whether the BIO15 correspondence survives progressively stronger geographic controls without adding any new climate variables after result inspection.

## Test A — Japan-only regional persistence

Remove the two Taiwan taxa from the nine-taxon ecological panel and refit the same Brownian PGLS on the remaining seven Japan-source taxa (U=4, D=3) across the same six accepted topologies.

BIO15 results:

- D−U standardized beta: **+1.057 to +1.103 SD**;
- topology sign agreement: **6/6**;
- species-LOO sign agreement: **42/42**;
- P range: 0.191–0.206.

Thus the direction does not depend on the Taiwan-vs-Japan contrast. This is regional persistence, not an independent replication and not threshold-level confirmation.

BIO1 likewise retains the prespecified negative direction in 6/6 topologies and 42/42 Japan-only species-LOO fits, but with a smaller median effect (about −0.474 SD).

## Test B — explicit coarse geography adjustment

On all nine taxa, fit Brownian GLS with orientation together with coarse geographic covariates.

### Latitude + longitude model

BIO15 orientation coefficient:

- **+1.118 to +1.125 SD**;
- median +1.121 SD;
- P = 0.0925–0.0948;
- topology sign agreement **6/6**;
- species-LOO sign agreement **54/54**.

### Taiwan-indicator sensitivity

BIO15 orientation coefficient:

- **+1.089 to +1.116 SD**;
- median +1.103 SD;
- P = 0.0868–0.0923;
- topology sign agreement **6/6**;
- species-LOO sign agreement **54/54**.

Therefore the present BIO15 direction is not reducible to a simple Taiwan indicator or to linear centroid latitude/longitude alone.

## Test C — geography-conditioned counterfactuals

Start from the frozen 126 U=5/D=4 counterfactual orientation maps. Keep the exact observed recurrence profile, then compare maps increasingly similar to the observed geography using four frozen features of the D taxa:

- mean latitude;
- mean longitude;
- latitude SD;
- longitude SD.

A joint history+geography pool combines rank-normalized relative-depth distance with geographic distance. No environmental variable enters the matching rule.

BIO15 conditional ranks:

| Counterfactual pool | Maps | Maps at least as positive as observed | Conditional fraction | Reverse BIO15? |
| --- | ---: | ---: | ---: | --- |
| exact recurrence | 40 | 3 | **7.5%** | yes; strongest −1.784 |
| recurrence + nearest geography | 10 | 3 | **30%** | yes; strongest −0.591 |
| nearest joint history + geography | 10 | 3 | **30%** | no |

The observed BIO15 effect is therefore unusual relative to arbitrary recurrence-matched histories, but not unusual in magnitude once comparable geography is retained. Joint history+geography matching also constrains the sign in this finite pool, but absence of a reverse map is not biological impossibility.

## Classification

`bio15_persists_regionally_but_not_beyond_joint_history_geography`

## Biological interpretation

Two simpler confounding explanations are weakened:

1. **Taiwan-vs-Japan only** — rejected as a sufficient explanation because the BIO15 direction survives within Japan.
2. **linear centroid latitude/longitude only** — rejected as a sufficient explanation because the orientation coefficient remains positive across all six topologies and every species-LOO fit after adjustment.

However, the analysis still does not isolate a climatic cause. Once alternative trait maps are constrained to resemble both the observed evolutionary history and coarse geographic configuration, the observed effect magnitude is not exceptional.

The best current statement is therefore:

> **The present orientation–BIO15 correspondence is geographically persistent but remains jointly embedded in lineage history and geography.**

This is stronger than calling the pattern a simple regional artifact, but weaker than claiming an ancestry-independent precipitation-seasonality effect.

## Causal boundary

This analysis does not establish:

- precipitation seasonality as a selective agent;
- a hydric mechanism;
- adaptation or plasticity;
- the environmental state at historical orientation transitions;
- complete removal of spatial confounding by latitude/longitude;
- independent replication from the Japan-only subset.

Further causal progress requires evidence on a mechanism or on repeated transition-linked contrasts, rather than additional opportunistic climate-variable screening.

## Frozen sources

- `data/evidence/chapter2_orientation_geography_causal_boundary_contract_v1.json`
- `data/evidence/chapter2_orientation_geography_causal_boundary_result_v1.json`
- `analysis/run_chapter2_orientation_geography_causal_boundary_v1.py`
- workflow run `33841950417`
- artifact `9925207291`
- artifact SHA256 `bac3a22c9dcf1b8d839b16afc2acf105210ac7a463691e8ee214def48be5ac94`
