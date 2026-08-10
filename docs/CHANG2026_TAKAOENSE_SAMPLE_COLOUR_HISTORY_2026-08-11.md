# Chang et al. 2026 var. *takaoense* sample topology and flower-colour history

Date: 2026-08-11

## Main result

The direct Figure 1 labels and sample topology change the parsimony interpretation of the strongest current regain candidate.

The six published var. *takaoense* transcriptomes are:

- bluish-purple `(BP)`: FC-3559, TJ-3807, NH-3835;
- white `(W)`: WY-3560, FB-3629, LT-3839.

Figure 1 panel C displays their sample topology as:

```text
(((((NH_BP, TJ_BP), FC_BP), LT_W), FB_W), WY_W)
```

Panel B's Neighbor-Net independently groups the same three BP-labelled samples and the same three W-labelled samples.

## Narrow six-sample result

Ignoring outside taxa, Fitch parsimony assigns a white root to the six-sample tree and requires one change.

- fixed white root: one `W -> C` transition;
- fixed coloured root: three changes, with two equally parsimonious directional histories:
  - three `C -> W` losses and no regain;
  - two losses and one regain.

Therefore the six samples alone still do not orient the transition without an external root-state assumption.

## Adding white var. albescens

When the white var. *albescens* pair is placed as the sister group to the exact six-sample var. *takaoense* topology and the parent node is fixed as coloured:

- minimum: two losses and one regain, three changes total;
- best no-regain history: four changes;
- no-regain penalty: `+1` change.

This makes regain the unique minimum-change history for that local published topology.

## Exact sample-aware Sinocirsium result

The source-backed broader Sinocirsium topology is represented as:

```text
C. japonicum_C
  sister to
((albescens_W, exact takaoense sample tree),
 (australe_C, fukienense_C))
```

With a coloured Sinocirsium root:

- minimum history: one `C -> W` loss followed by one `W -> C` transition;
- total minimum changes: `2`;
- every minimum-change assignment contains a regain;
- best no-regain history: `4` changes;
- no-regain penalty: `+2` changes.

Thus, **on the displayed exact sample topology and a coloured broader root, a W-to-coloured transition in var. *takaoense* is required by parsimony**.

## Full East Asian focal result

The exact var. *takaoense* sample topology was then inserted into the existing source-backed focal topology containing Arenicola and Taiwanese Nipponocirsium.

With a coloured root:

- minimum: three losses and one regain;
- total minimum changes: `4`;
- best no-regain history: `6` changes;
- no-regain penalty: `+2` changes.

This differs from the earlier generic population-aware sensitivity, which placed one W and one C tip as an unresolved sister pair and therefore allowed two equally parsimonious histories:

- four losses, zero regains;
- three losses, one regain.

The exact Figure 1 sample branching removes that equal-parsimony no-regain solution in the current topology-only screen.

## Frozen outputs

- `analysis/chang2026_takaoense_sample_colour_history.py`
- `analysis/chang2026_takaoense_sample_colour_history.csv`
- `tests/test_chang2026_takaoense_sample_colour_history.py`
- `data/evidence/chang2026_takaoense_sample_colour_history_summary_2026-08-11.json`
- `.github/workflows/validate-chang2026-takaoense-colour-history.yml`

Validation:

- workflow run: `31430965810`;
- eight exact-topology tests passed;
- artifact ID: `9079080760`;
- artifact SHA256: `cee4baa1aa0d9b0717554cddc6b69ec3fbb88063a5b0a8e00967273d49854f84`.

## Why this is not yet proof of molecular reactivation

The result is substantially stronger than the previous unresolved-topology sensitivity, but the valid statement is still:

> The exact published sample topology makes a var. *takaoense* W-to-coloured transition necessary in every minimum-change history under a coloured broader Sinocirsium root.

It does **not** yet show that an anthocyanin pathway was functionally lost and later restored.

The same phenotype/topology pattern could still be produced by:

- retention of an ancestral coloured haplotype within a predominantly white lineage;
- introgression of coloured ancestry from another Sinocirsium lineage;
- geography-associated population structure;
- reticulate relationships not represented by one bifurcating tree;
- incorrect or weakly supported short internodes;
- a regulatory difference that never involved complete pathway loss.

The paper itself highlights reticulation, and the Neighbor-Net must therefore be treated as biological evidence rather than decorative support for a tree-only narrative.

## Strong altitude confounding in the published six

The direct morph labels also reveal complete altitude-rank separation:

- BP mean altitude: `1160.67 m`;
- W mean altitude: `357.00 m`;
- BP minus W mean difference: `803.67 m`;
- all three BP samples occur above all three W samples;
- exact one-sided label-allocation probability: `0.05`;
- exact two-sided probability: `0.10`;
- leave-one-sample-out mean differences remain `635.67–1113.67 m`.

This is a useful sampling clue, not a causal test. The six localities were not randomly sampled, contain one plant each, and confound morph, altitude, geography and genomic ancestry.

Files:

- `analysis/takaoense_published_morph_metadata_screen.py`
- `analysis/takaoense_published_morph_metadata_screen_summary.json`
- `analysis/takaoense_published_morph_altitude_screen.csv`
- `data/evidence/chang2026_takaoense_morph_linked_public_samples_v1.csv`

## Revised biological inference

### Previously

> Coloured var. *takaoense* was the strongest regain candidate, but regain was not required because the morph-specific internal topology was unknown.

### Now

> The exact Figure 1 sample topology places the three BP samples together within a white-rooted six-sample pattern. When embedded in the coloured-root Sinocirsium context, one loss plus one regain is the unique minimum-change history; a no-regain explanation requires two additional changes.

### Still unresolved

- whether the coloured state is a derived regulatory restoration;
- whether the coloured haplotype was retained ancestrally or introgressed;
- whether the displayed sample internodes are stable across gene-tree and network analyses;
- branch-length-aware Mk and stochastic-mapping results;
- population-level association after controlling geography and altitude;
- floral anthocyanin expression and pigment chemistry.

## Immediate next analyses

1. obtain the machine-readable Chang tree, branch lengths and support definitions;
2. reconstruct or reanalyse the six public young-leaf transcriptomes with the direct W/BP labels;
3. quantify gene-tree concordance and topology weighting at the W/BP boundary;
4. test local ancestry and introgression using var. *fukienense*, var. *australe*, var. *japonicum* and var. *albescens* as candidate source/context lineages;
5. sample morphs within the same or nearby populations to break the present altitude/geography confounding;
6. collect matched flower RNA, pigment chemistry, reflectance, leaf DNA and ploidy.

## Claim boundary

The current result supports the phrase:

> **topology-supported candidate regain**

or:

> **a W-to-coloured transition required by minimum-change reconstruction under the published sample topology and coloured-root model**

It does not yet support:

> **demonstrated anthocyanin reactivation**

or:

> **adaptive regain caused by altitude or pollinator selection**.
