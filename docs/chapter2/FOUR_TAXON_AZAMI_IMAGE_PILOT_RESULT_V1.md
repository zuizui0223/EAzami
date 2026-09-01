# Chapter 2 four-taxon Azami-compatible public-image pilot v1

Status: 2026-09-01

## Question

Can two publicly dated white-coloured sister systems be measured with the same frozen Azami Chapter 1 image algorithms, and do they recover the same broad phenotype direction beyond colour?

Systems:

1. *Cirsium brevicaule* (white) vs *C. irumtiense* (bluish-purple), split context ~0.93 Ma.
2. *C. kawakamii* (white) vs *C. tatakaense* (purple), split context ~0.35 Ma.

The dated splits are lineage-divergence contexts, not exact colour-transition dates.

## Execution contract

- source platform: iNaturalist only;
- observations/photos selected deterministically before phenotype measurement;
- duplicate photo IDs removed before measurement;
- head crops chosen only from pinned-Azami foreground-mask quality, sharpness and resolution;
- known white/coloured state, environment and measured endpoint values are not used for crop choice;
- four taxa are balanced to 14 observations each after the neutral-quality gate;
- measurement code is pinned to Azami commit `03ed29f1f476ca0d0a1ea8e14e75cb0050a213ef`;
- OpenCV 4.14 is used to preserve the runtime array contract of the frozen Azami implementation rather than editing the frozen algorithm.

## Assay gate

Predeclared gate:

> the white lineage must have lower Azami-compatible corolla Lab chroma in both sister systems, with at least three usable observations per role.

**Result: PASS.**

- Arenicola: white-minus-coloured chroma = **-2.95**, n = 7 vs 8, bootstrap 95% interval -21.92 to 4.71, Cliff's delta -0.286.
- Taiwan: white-minus-coloured chroma = **-6.16**, n = 3 vs 3, bootstrap 95% interval -19.48 to 3.46, Cliff's delta -0.556.

The gate is directional and assessability-based; it is not a significance requirement. Both intervals include zero, so this is assay validation plus replicated direction, not strong independent statistical support in each system.

White lineages also have higher lightness in both systems (+6.86 and +8.24).

## Coarse whole-head directions after the assay gate

Three non-colour image-level endpoints show the same direction in both sister systems:

| endpoint | Arenicola white-coloured | Taiwan white-coloured | repeated direction |
|---|---:|---:|---|
| shape circularity | +0.238 | +0.159 | white higher |
| shape solidity | +0.092 | +0.099 | white higher |
| visible floret fraction | -0.305 | -0.028 | white lower |

For Arenicola, the circularity and solidity bootstrap intervals exclude zero. For Taiwan they do not. Visible floret fraction intervals include zero in both systems.

Thus the defensible result is **repeated extant phenotype direction**, not a common correlated transition.

## What did not replicate

- aspect ratio: opposite directions across the two systems;
- width-profile CV: opposite directions;
- detailed involucre projection/taper proxies: either opposite directions or too few usable observations (typically 1-2 per role) for a stable cross-system interpretation.

Therefore the data do **not** support a universal white-flower whole-capitulum syndrome or a shared detailed involucre architecture.

## Chapter 2 meaning

This result adds a new bridge between the public-data breadth and depth chapters:

`dated sister systems -> same Azami measurement ontology -> repeated extant phenotype direction`.

The strongest public-data hypothesis generated here is narrower than a syndrome claim:

> White lineages in two phylogenetically separated, dated sister systems may be embedded in a coarser rearrangement of visible head packing/display (more circular/solid outline and a lower visible floret fraction), while finer outline and involucre geometry remain lineage-specific.

The next public-data test is not to add more post-hoc image traits. It is to test the pre-existing Azami environmental prediction: whether the focal observations reproduce the global **higher RSDS -> lower chroma** direction under the same current CHELSA RSDS layer.

## Claim boundary

Do not infer from this pilot:

- the exact timing/order of colour and outline changes;
- independent origin of every measured endpoint;
- a shared developmental mechanism;
- correlated evolution;
- a white-flower syndrome;
- convergence, selection or adaptation.

The pilot uses public convenience-sampled photographs, and within-taxon observations are not independent macroevolutionary replicates.
