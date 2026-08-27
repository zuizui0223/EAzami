# Capitulum-space mechanism v3.1 contract

Status: **amended before any v3 model-family outcome was inspected**.

## Pre-outcome amendment boundary

The original v3 contract fixed the seven matched estimands, five families, four deterministic seeds and replication/held-out checks. After the first implementation job had started, but before its result, log or artifact was inspected, we identified one missing rule: a relative winner could be declared even if every family fit the frozen pattern badly, or if the focal separation was negligible.

Contract v3.1 therefore supersedes that uninspected run and adds three outcome-blind gates:

- the winning focal family must have accepted median primary distance <= 1.0;
- it must improve on the other focal family by at least 10% in median distance;
- its accepted replication-pattern rate must be >= 0.75.

The existing seed-wise stability, replication-not-worse and independent-literature-heldout-not-worse gates are retained. Only a workflow run started from `capitulum_space_mechanism_v3_1_2026-08-27` is interpretable. If any gate fails, common lability versus modular evolvability remains unresolved.

## Why v3 is needed

The merged Azami handoff provides 62 provenance-gated observations from run `33035785120`. The current EAzami v2 generator cannot score those rows honestly because it does not emit the same 17-unit within/among association matrices or the same nested core-four versus process-extension environmental estimand.

Version 3 therefore begins with an output contract, not a new ranking. Its first question is narrower than “which mechanism is true?”:

> Can a mechanism family generate the observed multilevel capitulum-space geometry and the observed scale contrast in environmental redundancy using the same simulated taxa and without endpoint-specific tuning?

Any resulting rank remains an ABC-like structural-sufficiency result.

## Observational targets

The source is immutable:

- Azami workflow run `33035785120`;
- artifact `9632715852`;
- artifact digest `sha256:51e7a26b5bd09e030b67b9342586699abaaf46e630f45b6bb4ee7bfc9152ced6`;
- analysis head `227c0e7b8c338894806785b8545c7c77c8724de1`.

The complete-18 phenotype contains 17 inferential units because hue is represented jointly. Units are grouped into the registered orientation, colour, shape, involucre-architecture and armature modules. These are measurement/phenotype modules, not established functional or genetic modules.

## Primary v3 fit layer

Only seven estimands enter the primary distance:

1. within-taxon registered-module contrast, main >=5 scope;
2. among-taxon registered-module contrast, main >=5 scope;
3. within-versus-among association-matrix Spearman, main >=5 scope;
4. process-extension partial R² beyond BIO1/BIO4/BIO12/BIO15 within taxa;
5. the same process-extension partial R² among taxa;
6. growing-season-water partial R² beyond the core within taxa;
7. the same growing-season-water partial R² among taxa.

The three structure targets use their Azami taxon-bootstrap intervals to scale a robust numerical distance. Incremental targets use partial R² together with the predeclared support state. The main >=5 scope is the fit layer.

The >=2 rows are not counted a second time. They form an out-of-primary-fit replication check requiring the same qualitative pattern: positive module organization at both scales, positive but incomplete cross-scale similarity, an unsupported process omnibus within taxa and supported process omnibus plus growing-season water increment among taxa.

## Why all 62 rows are not scored independently

The handoff contains main and sensitivity scopes, two scales, related environmental summaries and descriptive coefficient cosines. Treating all of them as independent evidence would duplicate the same observations and create an artificial advantage for models that match one correlated result family.

Therefore:

- the six main structure and sensitivity rows are separated into fit versus replication roles;
- stand-alone environment-block R² and coefficient cosines remain descriptive diagnostics;
- radiation/VPD and productivity increments remain threshold-sensitive context;
- mechanical exposure is a negative context result;
- endpoint-level A/B/C rows remain in the existing EAzami v2 observation layer and are not rescored here.

## Model families

The declared comparison retains the existing five families:

- `environment_only`;
- `pollinator_only`;
- `antagonist_only`;
- `full_tradeoff_common_lability`;
- `full_tradeoff_modular_evolvability`.

The focal comparison is between the two full-tradeoff families. Both must include environmental, pollinator and antagonist driver classes. They differ only in the lability structure allowed before outcomes:

- common lability: one taxon-level multiplier is shared across all 17 units;
- modular evolvability: taxon-level multipliers may differ among the five registered modules.

Parameters may be global, environment-block-level or registered-module-level. Per-endpoint hand tuning is prohibited. Within- and among-taxon summaries must come from the same simulated taxa.

## Simulation and ranking rule

The registered v3.1 screen uses:

- 500 draws per seed per family;
- four deterministic seeds;
- top 5% acceptance with at least 50 accepted draws;
- ranking by median primary distance, then replication-pattern rate, then the already existing independent literature held-out rate;
- absolute accepted-median distance <= 1.0 for focal adequacy;
- at least 10% relative median-distance improvement for focal promotion;
- accepted replication-pattern rate >= 0.75.

The screen is not a likelihood, posterior model probability or Bayes factor. Those labels are prohibited.

A common-versus-modular decision is allowed only when all seven matched estimands are generated, the winning family is absolutely adequate, separation is at least 10%, the winner is stable across all declared seeds, its replication rate is absolutely adequate and not worse than the alternative, and its existing independent literature-heldout rate is not worse. Otherwise the distinction remains unresolved.

## What v3 must generate

A valid generator must retain signed simulated endpoint values and derive from them:

- within-taxon endpoint association matrix;
- among-taxon endpoint association matrix;
- 17-unit strength matrices with hue treated jointly;
- registered-module contrasts at both scales;
- upper-triangle within/among matrix similarity;
- an 18-response core-four reduced environmental model;
- statistically matched nested extensions for all five process variables and growing-season water input.

Producing the correct sign for one environmental coefficient is not equivalent to reproducing the nested multivariate estimand.

## Interpretation boundary

Even a stable v3.1 ranking cannot establish:

- functional or genetic modularity;
- modular evolvability as a measured biological property;
- phenotypic plasticity or local adaptation;
- direct growing-season precipitation, radiation, VPD or productivity causation;
- pollinator-mediated selection or antagonist defence;
- a unique evolutionary mechanism.

The output is a diagnosis of which declared mechanism family is sufficient to reproduce a frozen pattern bundle under declared priors and constraints. Failure of every family to meet absolute adequacy is retained as a mechanism-gap result rather than hidden by relative ranking.

## Machine-readable files

- contract: `data/contracts/capitulum_space_mechanism_v3_contract.json`;
- contract validator: `analysis/validate_capitulum_space_mechanism_v3_contract.py`;
- gated screen entry point: `analysis/run_capitulum_space_mechanism_v3_gated.py`;
- generator: `analysis/simulate_capitulum_space_mechanism_v3.py`;
- tests: `tests/test_capitulum_space_mechanism_v3_contract.py`, `tests/test_simulate_capitulum_space_mechanism_v3.py`, and `tests/test_run_capitulum_space_mechanism_v3_gated.py`.

The contract validator resolves the seven primary targets against the imported Azami tables, verifies provenance hashes and rejects duplicated sensitivity targets. The v3.1 wrapper additionally validates the absolute adequacy and separation gates before running the family screen.
