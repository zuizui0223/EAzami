# Capitulum-space mechanism v3.1 result

Status: **registered screen completed; all declared families fail absolute adequacy; common lability versus modular evolvability remains unresolved**.

## Immutable execution

- workflow run: `33040972884`;
- workflow head: `fb658d3a846d3c1e290dd3a96b64ac121bcb824d`;
- artifact: `9633915699`;
- artifact digest: `sha256:fb66b22b073a406432b02fba207e8ebe0c79b3e12d092ba48078ad1752e7d4dc`;
- result JSON SHA-256: `73d48a52fed65ff11f7132c22874742c244c2ed76b25804e79c612c16d53165f`;
- draw table SHA-256: `24b19df06c4b014c10263614aded966eaf062a8fbd0a53ef10013ce280db3533`;
- contract: `capitulum_space_mechanism_v3_1_2026-08-27`;
- 500 draws × four deterministic seeds × five families = 10,000 prior draws;
- accepted layer: best 5%, 100 draws per family.

The preceding implementation run `33040362543` was superseded before its output was inspected because the original contract lacked absolute-adequacy and minimum-separation gates. Only the v3.1 run above is interpreted.

## Registered outcome

The relative ranking by accepted median primary distance was:

1. `pollinator_only` — 1.4002;
2. `antagonist_only` — 1.4728;
3. `full_tradeoff_common_lability` — 1.7118;
4. `environment_only` — 1.7520;
5. `full_tradeoff_modular_evolvability` — 2.0191.

However, the preregistered absolute-adequacy threshold was an accepted median distance <= 1.0. **No family passed it.** The result is therefore not “pollinator only wins”. It is:

> **None of the five declared generators is sufficient to reproduce the complete frozen capitulum-space pattern bundle.**

`pollinator_only` ranked first only because it came closest to the weak observed among-taxon module contrast while reproducing the within-taxon contrast. Its accepted replication-pattern rate was only 0.677, below the required 0.75, and it strongly underproduced the observed among-taxon process-environment and growing-season-water increments.

## Common lability versus modular evolvability

Among the two full-tradeoff families, common lability had the lower accepted median distance in all four seeds:

- common lability: 1.7118;
- modular evolvability: 2.0191;
- relative median improvement for common lability: 15.2%;
- common-lability replication-pattern rate: 0.840.

Thus the relative-distance, minimum-separation, seed-stability and replication gates favoured common lability. Two preregistered promotion gates nevertheless failed:

1. **absolute adequacy failed** — 1.7118 exceeded 1.0;
2. **independent held-out performance was worse** — existing v2 held-out rate was 0.6889 for common lability versus 0.7056 for modular evolvability.

The registered decision is therefore:

> **common lability versus modular evolvability: unresolved.**

This prevents a relative ranking from being misreported as evidence for a biological lability architecture.

## Where the current generators fail

The dominant mismatch is not the sign of one environmental coefficient. It is the **scale geometry of trait integration**.

Observed main-scope targets were:

- within-taxon module contrast: 0.1645;
- among-taxon module contrast: 0.0885;
- within/among matrix similarity: 0.3663;
- process partial R² beyond core four: 0.0135 within taxa and 0.2150 among taxa;
- growing-season-water partial R²: 0.0020 within taxa and 0.0787 among taxa.

The accepted draws generally reproduced positive within-taxon organization but produced too much among-taxon integration:

| Family | accepted median within contrast | accepted median among contrast | accepted median among process partial R² | accepted median among GSP partial R² |
|---|---:|---:|---:|---:|
| pollinator only | 0.1630 | 0.3131 | 0.1114 | 0.0279 |
| antagonist only | 0.1652 | 0.3935 | 0.1091 | 0.0271 |
| common lability | 0.1953 | 0.5240 | 0.1855 | 0.0351 |
| environment only | 0.1917 | 0.5296 | 0.2257 | 0.0389 |
| modular evolvability | 0.6028 | 0.6969 | 0.1847 | 0.0477 |

The modular generator failed most strongly because its module-specific latent factors and lability multipliers made endpoints within registered modules much more tightly associated than observed at both biological scales. The current common-lability and environment-only generators reproduced much of the among-taxon process increment but likewise coupled taxon-level traits too strongly within modules. Pollinator-only and antagonist-only generators had weaker among-module integration but lacked sufficient among-taxon process-environment structure.

## Mechanism-gap diagnosis

The frozen observation bundle requires a combination absent from all five current generators:

1. **moderate organization within taxa**;
2. **substantially weaker integration among taxa**;
3. **only partial alignment of within- and among-taxon association geometry**;
4. **little process-environment increment within taxa**;
5. **substantial process-environment and growing-season-water increment among taxa**.

A model that applies the same module factor or lability architecture at both scales naturally overcouples among-taxon traits. The next model should therefore not merely add another driver. It must permit **scale-specific covariance formation**.

Candidate missing structures to test, without yet treating them as true mechanisms, are:

- local or developmental module covariance that contributes within taxa but averages out among taxa;
- taxon-level trait turnover that is more mosaic than module-coherent;
- historical or phylogenetic trait-specific offsets that rotate the among-taxon matrix;
- an explicit observation layer that can create within-image measurement covariance without being inherited as taxon-level biological integration;
- environmental effects whose among-taxon component is strong but distributed across partially independent trait directions rather than one module-wide loading.

These alternatives must be represented as separate predeclared model families. The v3.1 failure does not license post-hoc tuning of module factors until the existing seven targets fit.

## Consequence for the Azami → EAzami connection

Azami established that the capitulum phenotype is partially organized and that environmental redundancy changes across scales. EAzami v3.1 shows that the current environment-only, biotic-only and two full-tradeoff lability generators do not jointly reproduce that pattern.

This is a useful negative result. It changes the handoff from:

> choose common or modular lability

into:

> identify the mechanism that decouples moderate within-taxon organization from weak among-taxon integration while preserving stronger among-taxon process-environment structure.

The next EAzami development should therefore target **scale-specific covariance generation**, not simply add more predictors or declare the relatively best family adequate.

## Machine-readable result

The compact frozen summary is `data/evidence/capitulum_space_mechanism_v3_1_result_summary.json`. The complete accepted-draw output remains in artifact `9633915699` and is reproducible from the merged contract, generator, four seeds and workflow.

## Claim boundary

This screen is an ABC-like prior-predictive structural-sufficiency analysis. It is not a likelihood, posterior model probability, Bayes factor, proof of pollinator control, evidence for functional or genetic modularity, an estimate of modular evolvability, a selection test, an adaptation test, a plasticity test or identification of a unique causal mechanism. The result refutes adequacy of the declared generator families under the frozen priors and targets; it does not refute every possible environmental, pollinator, antagonist, common-lability or modular mechanism.
