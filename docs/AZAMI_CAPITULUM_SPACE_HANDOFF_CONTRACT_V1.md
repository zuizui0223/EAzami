# Azami capitulum-space handoff contract v1

Status: pre-import contract, 2026-08-27

## Purpose

EAzami will not copy new Chapter 1 capitulum-space numbers from prose. The only accepted source is the machine-readable target tables emitted by one frozen, artifact-backed `zuizui0223/azami` run together with its GitHub run ID, artifact ID/digest and full source commit SHA.

Expected Azami tables:

- `capitulum_space/capitulum_space_eazami_targets.csv`;
- `capitulum_environment/capitulum_environment_eazami_targets.csv`.

`analysis/import_azami_capitulum_space_targets.py` validates and normalizes those files. It preserves every imported row as `source_layer=azami_observation`, `causal_status=observational_noncausal`, and `simulation_role=unscored_observational_target`.

## Why imported targets are initially unscored

The current EAzami v2 toy generator produces a compact set of scalar environmental, pollinator and antagonist summaries. It does **not** yet generate the same 17-unit within/among association matrices or the same 18-endpoint environmental coefficient geometry measured by Azami.

Therefore the new Azami targets must not be forced into the existing v2 score by analogy. A later v3 mechanism contract must first define a generative output with the same estimand. Until then, the new rows are structural constraints / future discrimination targets.

This is especially important for distinguishing `full_tradeoff_common_lability` from `full_tradeoff_modular_evolvability`: the current small ranking difference is not sufficient evidence for modular evolvability. The new observed covariance geometry is valuable precisely because it can become an independent model-discrimination target once EAzami produces comparable geometry.

## Allowed imported information

- within-taxon registered-module association contrast;
- among-taxon registered-module association contrast;
- within-vs-among association-matrix similarity;
- whole-capitulum multivariate R² for predeclared environment blocks;
- cross-scale standardized coefficient-matrix cosine as descriptive geometry;
- bootstrap intervals when Azami emits them;
- exact scope/replication threshold;
- immutable run/artifact/code provenance.

## Not allowed

The import must never relabel these targets as:

- genetic covariance;
- functional modularity;
- modular evolvability;
- selection coefficients;
- plasticity or local adaptation;
- defence efficacy;
- pollinator preference;
- rain/UV/thermal/aerodynamic protection;
- causal mechanism evidence.

## Promotion to a scored v3 target

A target can become scoreable only after all of the following are explicit in a new contract:

1. the EAzami generator emits a statistic with the same biological/statistical estimand as the Azami target;
2. the tolerance or distance scaling is declared before comparing model-family outcomes;
3. the target is not duplicated by another score term;
4. uncertainty from the Azami target is used where available;
5. held-out literature evidence remains independent of the Azami fit layer;
6. model ranking is described as structural sufficiency, not causal proof.

## Current repository boundary

Azami owns the spatial observation layer. EAzami owns mechanism-family adequacy/failure diagnosis. A successful EAzami reproduction never upgrades the Azami observation to a causal result.
