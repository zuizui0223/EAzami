# Chang 2026 var. *takaoense* topology-robustness audit

Date: 2026-08-11

## Correction made in this audit

The repository previously contained two overlapping six-tip topology-sensitivity implementations. The older `chang2026_takaoense_topology_robustness.py` referenced superseded symbols from an earlier version of the sample-colour script and was no longer executable from the current repository head. Its committed `nearest_no_regain_topologies.csv` was therefore stale.

An independent rooted-cluster audit showed that the old first candidate (`T0064`) is rooted RF distance 8 from the current Figure 1 topology, not 4. The downstream seven-topology null set used for gene-tree scoring therefore needed to be regenerated.

The corrected implementation now imports the current Figure 1 source of truth:

```text
(((((NH_3835_BP,TJ_3807_BP),FC_3559_BP),LT_3839_W),FB_3629_W),WY_3560_W)
```

and the current exhaustive 945-tree enumerator.

Rooted RF is explicitly defined as the **symmetric difference in nontrivial rooted descendant clusters**.

## What remains unchanged

The main qualitative sensitivity result is unchanged:

- 945 rooted binary topologies enumerated;
- 270/945 require at least one W→C transition at the coloured-root Sinocirsium parsimony minimum;
- 675/945 permit a no-regain optimum;
- the exact displayed topology has minimum `1 loss + 1 regain`;
- the exact displayed topology has a `+2` no-regain penalty;
- all 9 topologies at rooted RF ≤2 require regain;
- the nearest no-regain optimum remains rooted RF distance 4;
- exactly seven no-regain topologies occur at that minimum distance.

Thus the valid biological headline remains:

> **The displayed var. takaoense sample topology supports candidate regain and is locally robust to one rooted split change, but regain is not robust to unresolved internal topology across the full topology space.**

## Correct nearest seven loss-only alternatives

The corrected nearest set is:

1. `T0403` — `((((FB,LT),(NH,TJ)),FC),WY)`
2. `T0409` — `((((FB,LT),FC),(NH,TJ)),WY)`
3. `T0755` — `((((NH,TJ),LT),FC),(FB,WY))`
4. `T0846` — `(((FB,LT),WY),((NH,TJ),FC))`
5. `T0894` — `(((FB,WY),LT),((NH,TJ),FC))`
6. `T0901` — `(((FC,LT),(NH,TJ)),(FB,WY))`
7. `T0944` — `(((LT,WY),FB),((NH,TJ),FC))`

All preserve the NH–TJ sister pair. Three (`T0846`, `T0894`, `T0944`) make both BP and W monophyletic and have a two-change optimum in which `2 losses + 0 regain` ties `1 loss + 1 regain`. The other four have a three-change optimum with a loss-only `3L+0R` history among the ties.

These seven, and not the stale `T0064`-series rows, are the null topologies that must be used by:

- the per-gene Trinity/OrthoFinder scorer;
- the Read2Tree fast-screen scorer;
- any quartet or concordance analysis that compares the displayed candidate-regain topology with the nearest loss-only alternatives.

## Corrected group statistics

| Topology subset | n | regain required | no-regain equal optimum |
|---|---:|---:|---:|
| all rooted topologies | 945 | 270 | 675 |
| BP monophyletic | 45 | 36 | 9 |
| W monophyletic | 45 | 0 | 45 |
| NH–TJ sister preserved | 105 | 66 | 39 |
| BP monophyletic + NH–TJ | 15 | 12 | 3 |
| rooted RF ≤2 | 9 | 9 | 0 |
| rooted RF ≤4 | 51 | 44 | 7 |
| exact displayed topology | 1 | 1 | 0 |

The distribution of rooted RF distance from the current displayed topology is:

- RF 0: 1
- RF 2: 8
- RF 4: 42
- RF 6: 188
- RF 8: 706

## Why this matters

The stale seven-topology set did not alter the global 270/945 sensitivity count, but it **did** affect the identity of the pre-registered loss-only alternatives used for empirical gene-tree weighting. That is a downstream design-critical error, so the hypothesis set is corrected before any heavy computation is interpreted.

The correction strengthens provenance rather than the regain claim. The same claim limit remains:

- topology does not establish anthocyanin reactivation;
- introgression and ancestral polymorphism remain alternatives;
- uniform topology enumeration is not a posterior;
- empirical gene-tree/network support is still required.

## Reproducible files

- `analysis/chang2026_takaoense_topology_robustness.py`
- `tests/test_chang2026_takaoense_topology_robustness.py`
- `analysis/chang2026_takaoense_topology_robustness_groups.csv`
- `analysis/chang2026_takaoense_nearest_no_regain_topologies.csv`
- `analysis/chang2026_takaoense_topology_robustness_summary.json`

The generated 945-row table remains an analysis artifact rather than a manually maintained scientific input.
