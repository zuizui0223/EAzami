# Azami orientation cross-scale validation audit v1

Status: **FROZEN — NOT A PROSPECTIVE HELD-OUT CONFIRMATION**  
Date: 2026-09-25

## Question

After the external-taxon V1/V2 panels failed the preregistered public-occurrence resolution gate, can the existing Azami image dataset supply the missing P3 confirmation of the EAzami orientation–climate direction?

**No.** It is useful evidence, but not a new held-out confirmation.

## Why it cannot be P3

### 1. The relevant Azami outcomes were already analyzed

Azami already passed the orientation endpoint through the same nine-variable environmental atlas at both among- and within-taxon scales. BIO1, BIO12, BIO15 and GSP are therefore already observed outcomes.

Testing the EAzami BIO15-up/BIO1-down direction on those rows now would be a post-result reinterpretation, not prospective confirmation.

### 2. The phenotype is related but not identical

Azami uses:

`orientation_image_vertical_angle`

defined as a signed PCA head axis relative to **EXIF-oriented image vertical**:

- 0 degrees = up;
- 90 degrees = horizontal;
- 180 degrees = down.

The floral-pixel centroid supplies the sign. This gives a directional image-presentation measure, but the frozen ontology explicitly states that it is **not a direct gravity-referenced inclinometer angle or peduncle deflection**.

EAzami's botanical upward/downward state and Azami's image angle can therefore be compared directionally, but they are not interchangeable measurements.

## Existing within-taxon evidence

The frozen Azami within-taxon atlas contains 37,196 observations from 199 taxa for this endpoint.

### BIO1

- beta = **+0.0171503**
- P = **0.00654**
- global-family BH q = **0.04753**

Because larger angle means more downward in image coordinates, the sign is:

> **warmer local climate -> more downward image presentation**

This is opposite to the EAzami transition-level discovery, where downward states align with **lower BIO1**.

BIO1 was eligible for the frozen spatial sensitivity and the positive direction strengthened:

- spatial beta = **+0.0265374**
- spatial permutation P = **0.002**
- residual Moran P = **0.324**
- broad spatial sensitivity = pass.

### BIO15

- beta = **-0.0076180**
- raw P = **0.04553**
- BH q = **0.18310**

The numerical sign is:

> **higher precipitation seasonality -> more upward image presentation**

Again this is opposite to the EAzami downward-associated higher-BIO15 direction, although the Azami row is not FDR-supported and therefore did not enter the later spatial pass layer.

### BIO12 and GSP

Annual precipitation shows essentially no within-taxon association:

- BIO12 beta = **+0.0053264**
- P = **0.601**
- q = **0.823**.

Growing-season precipitation is weakly positive but unsupported:

- GSP beta = **+0.0038724**
- P = **0.0712**
- q = **0.217**.

## Existing among-taxon evidence is different

Azami's well-supported ecological anchor is:

> presentation angle x annual precipitation (BIO12), beta = **+0.304359**.

That is an **among-taxon** association with BIO12. It is not the same estimand as the EAzami transition-conditioned BIO15/BIO1 vector and should not be presented as a replication of it.

## Cross-scale interpretation

The combined evidence now gives a more useful biological result than a forced replication claim:

[
\text{orientation-environment correspondence is scale- and representation-dependent}
]

- static East-Asian D/U tip states are weak in common9;
- reconstructed EAzami orientation transitions align with BIO15-up/BIO1-down;
- global Azami among-taxon image angle aligns with BIO12;
- Azami within-taxon image angle does **not** reproduce the EAzami transition vector and shows a supported opposite BIO1 direction.

Therefore the ecological mapping of orientation is not a universal one-dimensional climate rule.

This is compatible with a capitulum component responding to different ecological leverage across lineage, population and observation scales; it does **not** identify adaptation or causal mechanism.

## P1-P3 status after the audit

- **P1 historical decoupling:** supported/frozen.
- **P2 trait-specific ecological correspondence:** discovery-level evidence remains.
- **P3 independent public-data confirmation:** **not available**.
  - external held-out taxa: not evaluable because strict public occurrence metadata collapse state replication;
  - Azami image data: already analyzed and measurement/estimand differs, so not prospective held-out evidence.

No further public-data rescue panel is opened.

## Next causal test

The next genuine confirmation is prospective and field-based in aza3:

[
\text{gravity-referenced orientation}
\rightarrow
\text{wetting / floral microclimate / effective pollination / antagonist exposure}
\rightarrow
\text{filled achenes}
]

This is the correct place to test whether the comparative correspondence reflects adaptive function.
