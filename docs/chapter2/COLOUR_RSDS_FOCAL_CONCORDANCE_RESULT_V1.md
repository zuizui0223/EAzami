# Chapter 2 focal colour–RSDS concordance result v1

Status: 2026-09-01

## Question

Does the frozen Azami present-day pattern—higher CHELSA surface shortwave radiation (`RSDS`) associated with lower visible corolla Lab chroma—reappear inside two publicly dated white–coloured sister systems?

This analysis was deliberately restricted to the single Azami candidate `corolla_lab_chroma ~ chelsa_rsds_mean`. No environmental-variable screen was performed.

## Primary result: partial concordance, not universal replication

### Arenicola — concordant

`C. brevicaule` (white) vs `C. irumtiense` (bluish-purple):

- median RSDS white minus coloured = **+1814 raw raster units**; bootstrap 95% **+663.1 to +1957**;
- median chroma white minus coloured = **-2.95**; bootstrap 95% **-22.33 to +4.71**;
- therefore `higher RSDS + lower chroma` is directionally concordant with the frozen Azami among-taxon result.

After collapsing repeated localities to taxon × 0.05° cell medians, the direction remains:

- RSDS difference **+1712**, bootstrap 95% **+6.5 to +1930**;
- chroma difference **-2.71**.

Thus the Arenicola correspondence is not explained solely by repeated observations from the same localities.

### Taiwan — discordant at the taxon-pair level

`C. kawakamii` (white) vs `C. tatakaense` (purple):

- median RSDS white minus coloured = **-686.5 raw raster units**; bootstrap 95% **-1513 to -172**;
- median chroma white minus coloured = **-6.16**; bootstrap 95% **-19.48 to +3.46**.

The white lineage is lower-chroma as expected, but it occupies **lower**, not higher, current RSDS than its coloured sister. This is opposite the frozen Azami among-taxon prediction.

The RSDS reversal becomes stronger after 0.05° cell aggregation:

- RSDS difference **-1703**, bootstrap 95% **-2607 to -368**.

The cell-level chroma comparison has only one usable cell per taxon and therefore cannot provide a useful uncertainty estimate, but the current RSDS reversal itself is locality-robust.

## Cross-system classification

- prespecified taxon-pair concordance: **1/2 systems**;
- 0.05° locality-collapsed concordance: **1/2 systems**;
- classification: **`partial_current_rsds_chroma_directional_concordance`**.

Therefore the public data reject the simple universal statement:

> repeated white lineages currently occupy the high-RSDS side of the same global colour gradient.

The correct Chapter 2 result is lineage-dependent current environmental correspondence.

## Secondary within-taxon result

Across the 21 observations with usable chroma, after demeaning both chroma and RSDS within each of the four taxa:

- standardized slope = **-0.407**;
- two-sided within-taxon permutation P = **0.114**;
- prespecified expected-negative one-sided permutation P = **0.036**.

Arenicola alone is also negative (`beta=-0.381`, expected-negative P=0.067), while the tiny Taiwan usable subset is negative but uninformative (`n=6`, expected-negative P=0.335).

This secondary result is suggestive of a negative local/within-lineage colour–RSDS response even though the Taiwan **among-lineage state contrast** is reversed. It must remain secondary because the primary analysis was the taxon-pair state comparison and usable colour sample size is small.

## Why this matters for the breadth × depth story

The combination is more informative than either a global correlation or a failed replication alone:

1. Azami shows a robust global among-taxon `RSDS↑ -> chroma↓` pattern.
2. Two independently dated sister systems both recover the expected white = lower-chroma phenotype with the same Azami measurement ontology.
3. Arenicola also reproduces the global RSDS direction.
4. Taiwan does not: the white taxon is lower-RSDS than its coloured sister.
5. Within taxa, the pooled slope remains negative in the Azami direction.

Thus **the colour–environment relationship is scale- and lineage-dependent**. Present environmental sorting may operate within lineages while among-lineage state differences reflect additional geography, ancestry, correlated environments, historical origins, or different selective mosaics.

This pattern weakens a universal persistent-RSDS-driver model and keeps several process models open:

- persistent driver in some lineages;
- origin–maintenance decoupling;
- lineage-specific environmental covariance;
- driver switching / selection mosaics.

The public data do not identify which one generated the historical colour transitions.

## RSDS source-scale note

The pinned Azami sampler returns the stored CHELSA raster values. The source raster reports a scale metadata value of `0.001`. All signs, medians on the stored scale, and standardized slopes are therefore directly commensurate with the frozen Azami pipeline; multiplying every value by the fixed scale would not change any directional or standardized inference. No physical unit is assigned here without a separate CHELSA unit audit.

## Claim boundary

Do not infer:

- historical solar/radiative causation of either colour transition;
- direct solar selection from current RSDS;
- that RSDS is independent of elevation, geography, ancestry or correlated climate;
- that the pooled secondary within-taxon P-value overrides the prespecified 1/2 taxon-pair result;
- convergence, selection or adaptation.

Current CHELSA RSDS is not a reconstruction of surface radiation at the historical colour-transition time.
