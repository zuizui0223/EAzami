# Arenicola direction update from published sister-clade context

Original date: 2026-08-10  
Corrected: 2026-08-12

> **2026-08-12 correction:** the earlier version of this note stated the sister-context result too strongly. The pair *C. brevicaule–C. irumtiense* itself is exactly directionally unresolved under equal-cost parsimony. The published Nipponocirsium sister context gives only a one-change preference for a coloured Arenicola MRCA. The current canonical analysis is `docs/ARENICOLA_FLOWER_COLOUR_HISTORY_2026-08-12.md`.

## Published phylogenetic context

Chang et al. (2026) resolves subsect. Arenicola as sister to subsect. Nipponocirsium. Arenicola contains *C. brevicaule* and *C. irumtiense*. Within Nipponocirsium, *C. morii* is the earliest sampled lineage; the remaining sampled core contains *C. pengii*, *C. tatakaense* and *C. kawakamii*.

## Source-backed flower-colour states

- *C. brevicaule*: white
- *C. irumtiense*: bluish-purple / coloured
- *C. morii*: pink / light purple / coloured
- *C. pengii*: bluish-purple / coloured
- *C. tatakaense*: bluish-purple / coloured
- *C. kawakamii*: white

The frozen evidence table is now:

- `data/evidence/arenicola_flower_colour_history_evidence_v1.csv`

## Direction cannot be inferred from historical varietal rank

Historical treatment of *C. irumtiense* as *C. brevicaule* var. *irumtiense* establishes a history of close taxonomic treatment, but it does **not** establish that the extant *C. brevicaule* lineage is ancestral to extant *C. irumtiense*.

The current phylogenetic model treats them as sister descendants of an unsampled MRCA. The former varietal rank is therefore never used as a root-state prior or ancestor–descendant edge.

## Pair-only result

For the two extant Arenicola species alone:

```text
        ┌─ brevicaule W
MRCA ───┤
        └─ irumtiense C
```

Both histories require one change:

1. `MRCA=C`: `C -> W` on *C. brevicaule*;
2. `MRCA=W`: `W -> C` on *C. irumtiense*.

Therefore:

> **the pair alone is exactly unpolarized (`Arenicola MRCA = C|W`).**

This is the key correction to the older narrative.

## Published sister-context result

Using the source-backed Arenicola + Nipponocirsium topology and states, exact enumeration gives:

| scenario | minimum changes | delta |
|---|---:|---:|
| unconstrained | 2 | 0 |
| force Arenicola MRCA=C | 2 | 0 |
| force Arenicola MRCA=W | 3 | +1 |
| force deeper root=C | 2 | 0 |
| force deeper root=W | 3 | +1 |

The unconstrained minimum has:

- deeper root = C;
- Arenicola MRCA = C;
- `C -> W` on *C. brevicaule*;
- `C -> W` on *C. kawakamii*.

Thus the currently sampled coloured-rich sister context gives **one parsimony step of support** to the white-loss history relative to forcing a white Arenicola ancestor.

A one-step difference is a directional clue, not proof of loss and not rejection of regain.

## Topology sensitivity inside Nipponocirsium

Three resolutions of the `pengii/kawakamii/tatakaense` core were tested while retaining *C. morii* as the basal sampled Nipponocirsium lineage:

- published `pengii`-basal resolution;
- alternative `kawakamii`-basal resolution;
- alternative `tatakaense`-basal resolution.

All three retain:

- minimum changes = 2;
- Arenicola MRCA = C.

The one-step preference is therefore not an artefact of only the exact three-tip core resolution used in the original simplified tree.

## Deep-root sensitivity

If the deeper Arenicola + Nipponocirsium ancestor is externally forced to W, the optimal Arenicola MRCA also becomes W and the *C. irumtiense* branch carries `W -> C`.

Therefore independent information about deeper ancestral state, exact branch lengths, unsampled/hidden lineages and broader colour-state distribution can alter the inferred direction.

## Revised hypothesis status

Do **not** rank H-regain as effectively dismissed.

Retain four alternatives:

1. **H-loss:** coloured ancestor; white loss/suppression in *C. brevicaule*.
2. **H-regain:** white ancestor/intermediate; coloured regain in *C. irumtiense*.
3. **H-standing:** ancestral white/coloured polymorphism followed by sorting.
4. **H-gene-flow:** introgression/gene flow modifies the colour-associated genealogy.

Current topology-only evidence gives weak directional support to H-loss (`2` vs `3` changes), while H-regain remains biologically and phylogenetically testable.

## Sampling consequence

Arenicola remains a high-priority system because the pair provides a sharp loss-versus-regain natural contrast rather than merely a generic repeated-loss replicate.

Population sampling should test:

- neutral structure and demographic separation across the Miyako Strait;
- migration and introgression;
- local ancestry and colour-associated haplotypes;
- cytotype/ploidy;
- separate plastid maternal history;
- floral RNA and anthocyanin pathway state;
- pigment chemistry and calibrated reflectance.

Where possible, genomic DNA, floral RNA, pigment chemistry, reflectance, voucher and ploidy should be linked to the same individual.

## Current working conclusion

> *C. brevicaule* and *C. irumtiense* alone do not identify whether the evolutionary change was white loss or coloured regain. The currently published Nipponocirsium sister context weakly favours a coloured Arenicola ancestor and white loss in *C. brevicaule* by one parsimony step, but a white-root sensitivity reverses the preferred Arenicola state. Accordingly, coloured regain in *C. irumtiense* remains an explicit competing hypothesis that requires population ancestry and floral molecular evidence to resolve.

Canonical implementation/results:

- `analysis/arenicola_colour_history_sensitivity.py`
- `analysis/arenicola_colour_history_sensitivity_v1.csv`
- `analysis/arenicola_colour_history_sensitivity_v1.json`
- `docs/ARENICOLA_FLOWER_COLOUR_HISTORY_2026-08-12.md`

Validation run `31542399876` completed successfully.
