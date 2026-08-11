# Arenicola flower-colour history — hypothesis gate (2026-08-12)

## Question

Does the white/coloured contrast between *Cirsium brevicaule* and *C. irumtiense* represent:

1. a coloured ancestor followed by white loss in *C. brevicaule*;
2. a white ancestor followed by coloured regain in *C. irumtiense*;
3. ancestral white/coloured polymorphism followed by lineage sorting; or
4. a history modified by introgression/gene flow?

The historical treatment of *C. irumtiense* as *C. brevicaule* var. *irumtiense* motivates close comparison but **is not an ancestor–descendant statement**. It is therefore never encoded as a tree edge or root-state constraint.

## Source-backed states and topology

The frozen evidence table is:

- `data/evidence/arenicola_flower_colour_history_evidence_v1.csv`

Tip coding used here:

| taxon | state | source role |
|---|---:|---|
| *C. brevicaule* | W | white corolla, Chang et al. 2026 |
| *C. irumtiense* | C | bluish-purple/purple corolla, Chang et al. 2026 |
| *C. morii* | C | light-purple corolla, Chang et al. 2025 |
| *C. pengii* | C | bluish-purple corolla, Chang et al. 2025 |
| *C. kawakamii* | W | white corolla, Chang et al. 2025 |
| *C. tatakaense* | C | bluish-purple corolla, Chang et al. 2025 |

Chang et al. 2026 supports *C. brevicaule* + *C. irumtiense* as Arenicola and Arenicola as sister to Nipponocirsium. The current topology-only screen uses this sister relationship and retains alternative resolutions within the three-taxon Nipponocirsium core as sensitivity cases.

## Exact equal-cost parsimony result

Reproducible analysis:

- `analysis/arenicola_colour_history_sensitivity.py`
- `analysis/arenicola_colour_history_sensitivity_v1.csv`
- `analysis/arenicola_colour_history_sensitivity_v1.json`

### 1. Arenicola pair alone

For only the two extant sister species:

```text
        ┌─ brevicaule  W
MRCA ───┤
        └─ irumtiense  C
```

There are two equally optimal histories, each requiring one change:

```text
MRCA=C : C -> W on brevicaule       cost = 1
MRCA=W : W -> C on irumtiense       cost = 1
```

Therefore **the pair alone is directionally unresolved**. The historical varietal classification cannot break this tie.

### 2. Published Arenicola + Nipponocirsium sister context

With the source-backed sister context and the published `pengii`-basal Nipponocirsium core:

| scenario | minimum changes | delta from optimum |
|---|---:|---:|
| unconstrained | 2 | 0 |
| force Arenicola MRCA = C | 2 | 0 |
| force Arenicola MRCA = W | 3 | +1 |
| force deep root = C | 2 | 0 |
| force deep root = W | 3 | +1 |

The unconstrained optimum is unique at the state level:

- deep root = C;
- Arenicola MRCA = C;
- `C -> W` on *C. brevicaule*;
- `C -> W` on *C. kawakamii*.

Thus the current sister context gives **one-parsimony-step support for the white-loss hypothesis** over forcing a white Arenicola ancestor.

This is a weak topology-conditioned preference, not proof that regain did not occur.

### 3. Nipponocirsium core-resolution sensitivity

Three resolutions were tested while keeping *C. morii* as the basal Nipponocirsium tip:

- published `pengii` basal;
- alternative `kawakamii` basal;
- alternative `tatakaense` basal.

For all three, the unconstrained solution remains:

- minimum changes = 2;
- Arenicola MRCA = C.

The current parsimony preference is therefore not caused only by the exact resolution of that three-taxon core.

### 4. Deep-root sensitivity

When the Arenicola + Nipponocirsium deep root is externally forced to W, the optimal Arenicola MRCA switches to W and the *C. irumtiense* branch carries `W -> C`.

This is important: the inferred direction can change when deeper ancestral-state information changes. Until an adequately broad colour atlas and branch-length/tree ensemble are available, the current parsimony result must not be converted into a posterior probability of loss or regain.

## Current working interpretation

Use the following wording:

> The *C. brevicaule–C. irumtiense* pair alone does not polarize flower-colour evolution: a single white loss and a single coloured regain are equally parsimonious. Adding the currently published, coloured-rich Nipponocirsium sister context favors a coloured Arenicola ancestor and white loss in *C. brevicaule* by one additional parsimony step over forcing a white Arenicola ancestor. Therefore coloured regain in *C. irumtiense* remains an explicit competing hypothesis rather than a rejected hypothesis.

Do **not** write that the former varietal rank demonstrates derivation of *C. irumtiense* from extant *C. brevicaule*.

## What would actually discriminate the hypotheses

### Species-tree / ancestral-state gate

1. Recover the exact machine-readable Chang 2026 species-tree topology and branch lengths if publicly available or from authors.
2. Build a broader, source-backed flower-colour atlas around Arenicola and adjacent East Asian lineages.
3. Run Mk-model and stochastic-mapping sensitivity across credible nuclear topologies rather than one hand-coded tree.
4. Keep nuclear and plastid histories separate because introgression/chloroplast capture can decouple them.

### Population-history gate

For multiple *brevicaule* and *irumtiense* populations, estimate:

- neutral nuclear structure and kinship;
- demographic divergence and migration;
- D/f-statistics or related introgression tests where sampling permits;
- local ancestry and candidate-region genealogy;
- haplotype sharing and age;
- cytotype/ploidy-aware variation;
- plastid maternal history as a separate layer.

The alternatives remain:

- **H-loss:** coloured ancestor, white loss in *brevicaule*;
- **H-regain:** white ancestor/intermediate, colour regain in *irumtiense*;
- **H-standing:** ancestral colour polymorphism sorted geographically;
- **H-gene-flow:** coloured alleles/history altered by introgression.

### Molecular regain gate

A branch should not be promoted to demonstrated molecular regain from topology alone. New field individuals should link, from the same plant where possible:

- genomic DNA;
- floral RNA;
- anthocyanin/pigment chemistry;
- calibrated visible + UV reflectance;
- voucher/locality;
- flow-cytometric or chromosome-based ploidy.

A convincing regain result requires population ancestry to support a white ancestor/intermediate, alternative introgression/standing-variation explanations to be disfavoured, and a recoverable anthocyanin pathway with a derived regulatory/coding change linked to restored floral pigment production.

## Validation

GitHub Actions workflow:

- `.github/workflows/validate-arenicola-colour-history.yml`

First successful validation run:

- run `31542399876`
- all compile, unit-test, recomputation and claim-boundary checks passed.

## Claim boundary

This analysis is a topology-only, equal-cost discrete-character sensitivity screen. It does not use a recovered published branch-length tree and does not estimate transition-rate posteriors. It cannot by itself distinguish de novo reactivation, standing ancestral alleles or introgression, and it is not evidence that the anthocyanin pathway was molecularly reactivated in *C. irumtiense*.
