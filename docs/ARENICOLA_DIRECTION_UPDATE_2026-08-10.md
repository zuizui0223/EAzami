# Arenicola direction update from published sister-clade context

Date: 2026-08-10

## Published phylogenetic context

Chang et al. (2026) resolves subsect. Arenicola as sister to subsect. Nipponocirsium, with both together sister to Sinocirsium. Arenicola contains only *C. brevicaule* and *C. irumtiense*. Within Nipponocirsium, *C. morii* is the earliest diverging lineage, followed by the *C. pengii* / *C. tatakaense* / *C. kawakamii* clade.

## Source-backed flower-colour states

- *C. brevicaule*: white
- *C. irumtiense*: bluish-purple / coloured
- *C. morii*: pink / light purple (coloured)
- *C. pengii*: bluish-purple (coloured)
- *C. tatakaense*: bluish-purple / purple (coloured)
- *C. kawakamii*: white

The important correction is that the closest published sister context for Arenicola is not an unknown single flanking taxon. It is the already-resolved Nipponocirsium clade, whose basal and most sampled members are coloured except for the independently white *C. kawakamii*.

## Existing-data parsimony result

Using the simplified published topology

`((brevicaule_W, irumtiense_C), (morii_C, (pengii_C, (kawakamii_W, tatakaense_C))))`

Fitch parsimony reconstructs the combined root as coloured and requires two minimum colour transitions.

The most economical interpretation is therefore:

1. an independent C -> W transition on *C. brevicaule*;
2. an independent C -> W transition on *C. kawakamii*.

A white ancestor followed by a W -> C regain on *C. irumtiense* is no longer equally parsimonious once the published sister-clade context is included.

## Revised hypothesis status

### Stronger
**H-Arenicola-loss:** *C. brevicaule* represents an independent loss/suppression of floral anthocyanin from a coloured ancestral context.

### Weaker
**H-irumtiense-regain:** *C. irumtiense* represents reactivation after a white ancestor.

This remains biologically possible under a more complex history (ancestral polymorphism, introgression, hidden lineage extinction, or topology uncertainty), but is not the preferred existing-data explanation.

## Sampling consequence

The previous high priority assigned to finding an unspecified `Arenicola flanking lineage` should be reduced. Existing phylotranscriptomics already provides the relevant sister-clade context.

RAD/population sampling in Arenicola remains useful, but for a different question:
- test whether the *brevicaule* white state is genetically homogeneous across its range;
- test gene flow / introgression between *brevicaule* and *irumtiense*;
- determine whether colour-associated haplotypes are retained, introgressed, or independently derived;
- test whether the white mechanism matches independent white systems such as *C. kawakamii* and white *takaoense*.

Thus Arenicola stays important as a mechanistic replicate, but not because a missing sister taxon is needed to orient the transition.

## Current working conclusion

The existing published nuclear topology now favors repeated independent white-flower loss in at least two regional systems (*C. brevicaule* and *C. kawakamii*) more strongly than a white-ancestor / multiple-regain scenario. Formal likelihood/stochastic mapping still requires exact published tree files and branch lengths (Issue #7).
