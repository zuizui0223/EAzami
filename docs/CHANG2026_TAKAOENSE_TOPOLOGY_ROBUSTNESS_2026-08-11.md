# Chang 2026 var. *takaoense* topology-robustness analysis

Date: 2026-08-11

## Question

The six published *Cirsium japonicum* var. *takaoense* transcriptome tips are now morph-labelled directly from Chang et al. (2026) Figure 1:

- bluish-purple: FC-3559, TJ-3807, NH-3835;
- white: WY-3560, FB-3629, LT-3839.

The exact sample topology is:

```text
(((((NH-3835 BP, TJ-3807 BP), FC-3559 BP), LT-3839 W), FB-3629 W), WY-3560 W)
```

With the broader Sinocirsium root fixed as coloured, this topology has a two-change optimum containing one white loss and one coloured regain. A no-regain history requires four changes, so its parsimony penalty is +2.

The present analysis asks whether that result is robust to uncertainty in the six-tip topology.

## Analysis design

`analysis/chang2026_takaoense_topology_robustness.py` enumerates all **945 rooted binary topologies** for the six labelled tips.

Each topology is embedded in the same source-backed scaffold:

```text
(C. japonicum,
  (((C. j. var. albescens BT, KZ), six-tip takaoense topology),
   (C. j. var. australe, C. j. var. fukienense)))
```

For every resolution the script records:

- rooted Robinson–Foulds distance from the published Figure 1 topology;
- monophyly of the three bluish-purple tips;
- monophyly of the three white tips;
- preservation of the published NH–TJ sister pair;
- minimum changes with the Sinocirsium root fixed coloured;
- all optimal loss/regain combinations;
- minimum score with regains prohibited;
- the no-regain parsimony penalty.

No branch lengths are invented. This remains a topology-only analysis.

## Main results

| Topology set | Topologies | Regain required at every global optimum | Fraction | No-regain penalty distribution |
|---|---:|---:|---:|---|
| Exact published topology | 1 | 1 | 100% | +2: 1 |
| Published topology plus one split perturbation (rooted RF ≤ 2) | 9 | 9 | 100% | +1: 4; +2: 5 |
| Published topology plus wider local perturbations (rooted RF ≤ 4) | 51 | 44 | 86.3% | 0: 7; +1: 35; +2: 9 |
| Bluish-purple tips constrained monophyletic | 45 | 36 | 80.0% | 0: 9; +1: 24; +2: 12 |
| White tips constrained monophyletic | 45 | 0 | 0% | 0: 45 |
| All rooted binary topologies | 945 | 270 | 28.6% | 0: 675; +1: 252; +2: 18 |

### Local robustness

Every topology differing from Figure 1 by at most one nontrivial rooted cluster still requires at least one regain in all minimum-change histories.

Thus the regain inference is **not destroyed by a single local rearrangement**. The exact +2 no-regain penalty may weaken to +1, but a loss-only history remains suboptimal throughout this nearest-neighbour set.

### Nearest loss-only alternatives

The closest topologies in which a no-regain history becomes globally optimal occur at rooted RF distance **4**. There are seven such resolutions.

All seven make the three white tips monophyletic. Six place the coloured tips as a successive external grade; one also retains a monophyletic coloured clade as the sister of the white clade.

Therefore, the nearest way to eliminate regain is not a tiny swap within the coloured group. It requires replacing the published pattern of a coloured clade nested inside a white grade with a topology containing a white clade.

### What the morph counts alone show

Three coloured and three white tips do not by themselves imply regain. Across all 945 possible resolutions, only 270 require regain.

The informative evidence is the **ordering of the morphs on the published topology**:

1. the three bluish-purple samples form a clade;
2. that clade is nested successively within LT-W, FB-W and WY-W;
3. the broader Sinocirsium context is coloured.

## Biological interpretation

### Supported statement

> The exact published sample topology provides a locally robust, topology-supported candidate regain: a no-regain explanation remains at least one extra change worse under every single-split perturbation.

### Unsupported statement

> Floral anthocyanin production has been demonstrated to evolve de novo or to be functionally reactivated in coloured var. *takaoense*.

Topology cannot distinguish a true regulatory regain from:

- introgression of a coloured haplotype;
- retention and sorting of ancestral colour polymorphism;
- gene-tree discordance or an alternative population topology;
- homeolog/cytotype effects;
- phenotype–environment structure in the six sampled localities.

The six published samples also show complete observed altitude separation: all three white samples are from 21–977 m, while all three bluish-purple samples are from 991–1,364 m. This does not invalidate the phylogenetic result, but it prevents treating the six-tip contrast as an unconfounded colour-association experiment.

## Consequence for the next analysis

The next existing-data target is now sharply defined. It is not another species-placement tree. It is a **gene-tree and reticulation audit around the six var. takaoense samples**.

Priority tests are:

1. quantify per-gene support for the published nested-BP topology versus the nearest seven white-clade loss-only alternatives;
2. calculate quartet/gene concordance and identify loci driving each alternative;
3. compare plastid and nuclear placements without substituting plastid history for the species tree;
4. inspect whether coloured samples share disproportionate ancestry with var. *australe* or var. *fukienense*;
5. obtain dense within- and among-population sampling to separate colour from altitude and geography;
6. link DNA, floral RNA, pigment chemistry, reflectance, voucher and ploidy in the same plants.

## Reproducible outputs

- `analysis/chang2026_takaoense_topology_robustness.py`
- `tests/test_chang2026_takaoense_topology_robustness.py`
- `analysis/chang2026_takaoense_topology_robustness_groups.csv`
- `analysis/chang2026_takaoense_nearest_no_regain_topologies.csv`
- `analysis/chang2026_takaoense_topology_robustness_summary.json`
- full 945-topology table generated in CI and retained as a workflow artifact

## Current conclusion

The resolved Figure 1 topology makes coloured var. *takaoense* substantially stronger than a generic “possible regain” example. Its signal survives every one-split rooted perturbation and requires at least two split changes before a loss-only history can tie the optimum.

At the same time, the exhaustive topology space shows why the wording must remain disciplined: **regain is supported by a particular population ordering, not guaranteed by the observed colour counts, and not yet separated from reticulation or ancestral variation.**
