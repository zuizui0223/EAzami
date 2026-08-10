# Chang et al. 2026 `var. takaoense`: exact displayed topology and topology uncertainty

Date: 2026-08-11

## Evidence now recovered

The official Springer Nature Figure 1 image directly identifies all six published `Cirsium japonicum var. takaoense` transcriptome tips.

### Bluish-purple `(BP)`

- `FC-3559` — voucher `ccy3559` — `SRR35152718`
- `TJ-3807` — voucher `ccy3807` — `SRR35152736`
- `NH-3835` — voucher `ccy3835` — `SRR35152735`

### White `(W)`

- `WY-3560` — voucher `ccy3560` — `SRR35152717`
- `FB-3629` — voucher `ccy3629` — `SRR35152738`
- `LT-3839` — voucher `ccy3839` — `SRR35152734`

The same W/BP suffixes are printed independently in Figure 1 panel B (Neighbor-Net) and panel C (ASTRAL species tree). Voucher, run and BioSample identity is linked through exact numeric identifiers rather than locality inference.

## Exact displayed six-tip topology

Panel C displays the six `takaoense` tips as:

```text
(((((NH_BP,TJ_BP),FC_BP),LT_W),FB_W),WY_W)
```

This topology has:

- a monophyletic three-tip BP clade;
- three successive W tips outside that BP clade;
- non-monophyletic W samples;
- one unconstrained Fitch change and a W Fitch root within the six-tip subtree.

No branch lengths are inferred from the figure.

## Directional result on the displayed topology

### Within the six-sample subtree

If the six-tip root is fixed to W:

- minimum changes: 1;
- direction: `0 losses + 1 regain`.

If the six-tip root is fixed to coloured:

- minimum changes: 3;
- two equal histories remain:
  - `3 losses + 0 regains`;
  - `2 losses + 1 regain`.

Therefore, the six-tip subtree alone still does not orient the transition without its broader context.

### White `albescens` plus exact `takaoense`

With a coloured root outside the white `albescens`–`takaoense` grouping:

- minimum: `2 losses + 1 regain`;
- best no-regain history: 4 changes;
- no-regain penalty: `+1`.

### Sample-aware Sinocirsium

Using the source-backed coloured `japonicum`, `australe` and `fukienense` context:

- minimum: `1 loss + 1 regain`;
- every minimum-change history contains W→C;
- best no-regain history: 4 changes;
- no-regain penalty: `+2`.

### Full focal East Asian context

Adding Arenicola and Taiwanese Nipponocirsium:

- minimum: `3 losses + 1 regain`;
- every minimum-change history contains W→C;
- best no-regain history: 6 changes;
- no-regain penalty: `+2`.

This replaces the earlier generic two-tip `takaoense` sensitivity, which allowed four-loss/no-regain and three-loss/one-regain histories at equal parsimony.

Reproducible outputs:

- `analysis/chang2026_takaoense_sample_colour_history.py`
- `analysis/chang2026_takaoense_sample_colour_history.csv`
- `data/evidence/chang2026_takaoense_sample_colour_history_summary_2026-08-11.json`

## Why exact displayed topology is not enough

The paper reports pronounced reticulation, and several short internal branches among the `takaoense` samples are weakly supported. A pectinate display can therefore yield a directional parsimony result that is sensitive to how weak nodes are resolved.

To make this uncertainty explicit, all rooted fully bifurcating trees on the same six labelled tips were enumerated.

The number of such trees is:

```text
(2n - 3)!! = 9!! = 945, for n = 6
```

Each topology was embedded in the same source-backed coloured-root Sinocirsium context. No topology was assigned a probability or empirical weight.

## Exhaustive 945-topology sensitivity

| Topology class | Regain required? | No-regain penalty | Number | Fraction of 945 |
|---|---|---:|---:|---:|
| BP non-monophyletic, W non-monophyletic | no | 0 | 630 | 0.6667 |
| BP non-monophyletic, W non-monophyletic | yes | +1 | 234 | 0.2476 |
| BP non-monophyletic, W monophyletic | no | 0 | 36 | 0.0381 |
| BP monophyletic, W non-monophyletic | yes | +1 | 18 | 0.0190 |
| BP monophyletic, W non-monophyletic | yes | +2 | 18 | 0.0190 |
| BP monophyletic, W monophyletic | no | 0 | 9 | 0.0095 |

Totals:

- regain required at the minimum: **270/945** topologies (`28.57%`);
- no-regain allowed at the same minimum: **675/945** (`71.43%`);
- BP monophyletic: 45 topologies;
- W monophyletic: 45 topologies;
- both morphs monophyletic: 9 topologies;
- BP monophyletic and W non-monophyletic: 36 topologies, all regain-required.

Among the 270 regain-required resolutions:

- 252 have a `+1` no-regain penalty;
- 18 have a `+2` penalty;
- the displayed topology belongs to the latter, stronger class.

Reproducible outputs:

- `analysis/chang2026_takaoense_topology_uncertainty.py`
- `analysis/chang2026_takaoense_topology_uncertainty.csv`
- `analysis/chang2026_takaoense_topology_uncertainty_summary.json`
- `tests/test_chang2026_takaoense_topology_uncertainty.py`

The complete 945-row topology ledger is produced as a workflow artifact rather than committed as a main repository table.

## Correct inference hierarchy

### Strongly supported

- both W and BP individuals were sequenced within `var. takaoense`;
- the displayed Figure 1 topology groups all three BP samples;
- on that displayed topology and a coloured broader root, W→C is required at the parsimony minimum;
- avoiding regain on the displayed topology costs two additional changes.

### Supported but explicitly topology-dependent

> `var. takaoense` is a topology-supported candidate regain under the displayed published sample tree.

### Not robust to arbitrary weak-node resolution

A regain is not required under most alternative rooted six-tip resolutions. The `270/945` fraction is not a posterior probability; it shows the size of the topology region in which the directional conclusion survives.

### Not demonstrated

- a true molecular loss-and-restoration event;
- a causal anthocyanin regulatory reactivation;
- exclusion of introgression;
- exclusion of ancestral coloured standing variation;
- adaptive selection on colour.

## Consequence for existing-data analysis

The next analysis must estimate empirical support for competing resolutions rather than accept the displayed tree as fixed.

Issue #14 tracks:

- raw-read QC of the six morph-labelled transcriptomes;
- expressed-locus ancestry and PCA;
- per-locus gene trees and topology concordance;
- BP-clade stability;
- introgression/reticulation tests using `albescens`, `australe`, `fukienense` and `japonicum` controls;
- recoverable candidate coding variation;
- topology-weighted update of the directional-history result.

Young-leaf RNA-seq can inform ancestry and expressed coding variation, but cannot establish floral anthocyanin expression or regulatory restoration.

## Consequence for field sampling

The six published samples are geographically and altitudinally structured. Future sampling must break that confounding by targeting:

- mixed W/BP populations;
- geographically close W/BP pairs;
- high-elevation W populations;
- low-elevation BP populations;
- replicated populations and cytotypes;
- matched phenotype, pigment, floral RNA, leaf DNA and voucher material.

## Current wording for Chapter 2

Use:

> The published morph-labelled sample topology identifies `var. takaoense` as the strongest current candidate for a white-to-coloured transition. On the displayed tree, regain is required at the coloured-root parsimony minimum and a no-regain history costs two extra changes. However, exhaustive weak-topology sensitivity shows that this direction is not generally robust to alternative six-tip resolutions, so raw-read ancestry, reticulation and population-genomic tests are required before calling a true evolutionary regain.

Do not use:

> Anthocyanin pigmentation has been proven to re-evolve in `var. takaoense`.
