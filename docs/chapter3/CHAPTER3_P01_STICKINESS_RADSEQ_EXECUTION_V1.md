# Chapter 3 P01 — JPN06–JPN15 stickiness-history falsification

Status: **PRE-DATA CONTRACT FROZEN**  
Issue: #154

## Primary question

Does the Chapter 2 historical placement of stickiness survive own-data ancestry and network sensitivities?

The current public scaffold supports exactly five minimum stickiness changes, with JPN06 (*Cirsium dipsacolepis*, nonsticky) concentrated on a terminal change and JPN06–JPN15 (*C. lineare*, sticky) forming the canonical sister contrast. P01 prospectively tests that placement; it does not test adaptation by itself.

## Sampling target

| Concept | Taxon | Minimum | Recommended | Population replication |
|---|---|---:|---:|---|
| JPN06 | *C. dipsacolepis* | 16 | 24 | 2 minimum, 3 recommended |
| JPN15 | *C. lineare* | 16 | 24 | 2 minimum, 3 recommended |
| **Total** |  | **32** | **48** | geographically separated populations |

Do not treat historical occurrence points as viable sampling sites without current verification. Population census, land access, collection permission and conservation status are gates, not post hoc metadata.

## Same-individual design

Every admitted individual must link one immutable `individual_id` across phenotype, voucher, tissue, cytotype and authorization records. Taxon-level authority states cannot replace missing individual phenotype observations.

Required phenotype package:

- involucre stickiness scored on the focal individual;
- gland/exudate documentation;
- orientation;
- phyllary posture;
- phenological stage;
- raw calibrated image record where feasible.

Required genomic/context package:

- RAD tissue;
- voucher;
- population ID and deidentified locality ID;
- cytotype / genome-size status;
- authorization record key.

## Analysis order

1. **Within-taxon QC first.** Establish population replication, read/locus quality and within-population consistency independently for JPN06 and JPN15.
2. **Ploidy-aware admission.** Do not force mixed cytotypes through one diploid SNP matrix. Screen genome-size/cytotype discordance, excess depth, allele count and heterozygosity.
3. **Shared-locus sensitivity.** Build permissive and strict homologous-locus sets. Quantify whether restriction-site dropout or missingness drives the JPN06–JPN15 relation.
4. **Ancestry and reticulation.** Estimate population structure/admixture and retain network alternatives; do not force a bifurcating tree if the data support reticulation.
5. **Topology/history sensitivity.** On each admitted topology/network-derived tree sensitivity, remap stickiness and recompute minimum changes plus JPN06 terminal localization.
6. **Decision.** Retain, revise or fail closed according to the frozen contract.

## Primary falsifiers

The current public history is revised if, after the QC gates pass:

- JPN06 and JPN15 are not retained as a stable sister relationship across admitted own-data sensitivities; or
- the JPN06 terminal concentration materially disperses or moves to an alternative edge; or
- the focal placement depends on a permissive locus set and reverses under strict-locus, ploidy-aware or network sensitivity.

If cross-species RAD admission fails because shared orthology, ploidy or reticulation is inadequate, report only population ancestry/within-cytotype structure and retain Comp1061 as the primary cross-species scaffold.

## Interpretation matrix

| Own-data result | Historical interpretation | Next step |
|---|---|---|
| Sister + terminal placement retained | Chapter 2 stickiness placement strengthened as an ancestry-resolved design target | run within-JPN15 neutralization vs sham function/fitness test |
| Sister retained, terminal placement disperses | stickiness history requires revision; sister contrast alone is insufficient | remap states with expanded same-individual panel |
| Sister relation fails | current canonical contrast is not ancestry matched | identify the nearest admitted ancestry-matched sticky/nonsticky contrast before manipulation |
| Cross-species RAD gates fail | no cross-species topology claim | retain Comp1061; use RAD only for population structure/admixture |

## Separate causal test

Only if an ancestry-matched sticky contrast survives should function be tested. The causal experiment is within-JPN15 stickiness neutralization versus sham, with prespecified enemy access/damage and reproductive-fitness endpoints. This is a separate estimand from RAD-seq history.

## Claim boundary

P01 can retain, revise or falsify a historical placement. It cannot by itself demonstrate defence, natural selection, adaptation, convergence or independent origins.
