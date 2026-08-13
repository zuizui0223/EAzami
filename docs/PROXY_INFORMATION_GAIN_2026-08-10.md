# Proxy information-gain analysis for Chapter 2 sampling priorities

Date: 2026-08-10

## Purpose

This analysis asks a practical question before new samples are collected:

> Which missing taxon/population/data type is most likely to change the biological conclusion about repeated white-flower evolution and candidate regain/reactivation?

Because exact full-tree posterior distributions and branch lengths are not yet available, this is **not formal Bayesian expected information gain (EIG)**. It is a transparent proxy-EIG / decision-sensitivity ranking. Formal EIG should replace it after Issue #7 recovers exact nuclear trees and full probabilistic models are fitted.

## Scoring dimensions

Each candidate is scored on whether the new data can:

1. change inferred transition **direction**;
2. change minimum **transition count**;
3. resolve **within-lineage white/coloured polymorphism**;
4. discriminate **introgression / ancestral polymorphism** from de novo transition;
5. identify the **molecular mechanism**;
6. fill a genuine **nuclear phylogeny gap**;
7. add **cross-region phylogeographic leverage**;
8. provide an independent **replicate** of white-flower evolution;
9. with a small penalty for exceptional technical complexity (e.g. polyploid homeolog handling).

Weights are explicit in `analysis/proxy_information_gain_priority.py` so the ranking is auditable and can be changed in sensitivity analyses.

## Current ranking

1. **white vs coloured var. takaoense** — proxy EIG 15.5
2. **C. pendulum white vs purple in Japan** — 14.25
3. **C. sieboldii white vs purple in Japan** — 14.25
4. **C. pendulum Chinese/NE Asian bridge populations** — 12.375
5. **C. sieboldii Zhejiang bridge populations** — 12.375
6. **Arenicola flanking nuclear lineage(s)** — 10.25
7. **C. kawakamii vs C. tatakaense population genomics** — 9.0
8. **additional C. pengii population sampling** — 5.375
9. **C. shansiense species placement** — 4.875
10. **C. leducii species placement** — 4.875

## Main interpretation

The ranking strongly favours **population-level white/coloured systems and transition-orienting flanking lineages** over generic species-tree completion.

This supports the current strategy:

- do not spend the first RAD-seq effort simply adding coloured Chinese taxa that are distant from a known colour transition;
- prioritize within-lineage white/coloured comparisons because they simultaneously test transition count, mechanism and population history;
- prioritize a flanking lineage around *C. brevicaule* / *C. irumtiense* because that single placement/state can reverse the inferred direction of the focal Arenicola transition;
- treat *C. kawakamii* as a mechanistic replicate rather than a species-placement problem because the white-loss direction is already comparatively well constrained by published nuclear topology;
- use Chinese populations of *C. pendulum* and *C. sieboldii* as phylogeographic bridge samples, not merely geographic extras.

## Hypotheses sharpened by this analysis

### H1 — repeated loss is the primary existing-data hypothesis
The most efficient new observations are those testing whether independent within-lineage white forms share a homologous regulatory mechanism.

### H2 — true regain is most likely to be discovered by dense population-aware sampling, not species-level coding
The *takaoense* system remains the highest-priority candidate because collapsing its white and bluish-purple morphs into one ambiguous species tip demonstrably reduces inferred transition counts.

### H3 — Arenicola regain vs loss is primarily a topology/state-orientation problem before it is a molecular problem
Until the closest flanking nuclear lineage(s) and population history are established, *C. irumtiense* should remain a `candidate regain`, not a demonstrated regain.

### H4 — some apparent transitions will be explained by standing variation or introgression
The high ranking of Chinese/NE Asian bridge populations for *C. pendulum* and *C. sieboldii* reflects the possibility that geography and allele sharing can change the interpretation of a Japan-only white origin.

## What can be done now without new samples

1. expand the source-backed flower-colour atlas, especially white/polymorphic records;
2. recover exact published nuclear trees and branch lengths (Issue #7);
3. verify Moreyra 2025 membership/placement of *C. pendulum* and *C. sieboldii*;
4. identify the exact closest nuclear flanking taxa to the Arenicola pair;
5. rerun the proxy-EIG ranking under alternative weight sets to test robustness;
6. once exact trees are available, replace this proxy with formal posterior expected information gain.

## Caveat

The numerical score is a **decision-priority tool**, not a biological parameter. Small differences in score should not be over-interpreted. The robust result is the ordering of broad sampling classes: within-lineage polymorphism > transition-orienting bridge/flanking samples > generic backbone completion.
