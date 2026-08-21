# Cirsium boninense public MIG-seq recovery — 2026-08-21

## What changed

The previous fixed-white recovery state correctly identified a 2025 genetic study of *Cirsium boninense* but treated its molecular method as unrecovered.

A Chiba University institutional publication summary is now publicly indexed and explicitly states that the study used **MIG-seq (Multiplexed ISSR Genotyping by Sequencing)** together with statistical analysis of involucral-bract traits.

The same summary lists five study taxa as indexed:

- `Cirsium irimtiense`;
- *C. brevicaule*;
- *C. spinosum*;
- *C. maritimum*;
- *C. boninense*.

The first spelling is retained exactly as indexed and is not used as an automatic taxonomic-normalization rule.

The conference contribution is independently indexed as Japanese Society for Plant Systematics 24th meeting, p.69, with the multi-author team already recorded in the repository.

## What this does resolve

The following status is now source-backed:

```text
boninense_existing_genetic_study_identified = true
boninense_molecular_method = MIG-seq
boninense_five_taxon_comparison_publicly_indexed = true
```

This is meaningful because the study is directly relevant to the origin of the fixed-white Ogasawara lineage and includes Ryukyu/coastal *Cirsium* comparators.

## What remains unresolved

The public summary does not expose enough information to reconstruct or reuse the analysis. The following remain unrecovered:

- number of *C. boninense* individuals;
- sample/voucher identities;
- retained marker/SNP counts;
- clustering/tree/network result values;
- exact inferred sister relationship;
- raw reads or genotype matrix;
- archive accession or reusable machine-readable dataset.

Therefore:

```text
usable_nuclear_tip_recovered = false
rate_fit_tip_promotion_allowed = false
```

## Why MIG-seq does not directly clear the colour-rate tree gate

The current macroevolutionary colour-rate tree is designed around a homologous Compositae1061 common-locus branch-length analysis. MIG-seq is a reduced-representation marker approach and is not directly interchangeable with the Compositae1061 locus set.

If the detailed MIG-seq result or reusable genotype data are recovered, they can be highly informative for the **local origin / population-history hypothesis** of *C. boninense*. They do not automatically become one of the branch-length tree tips used for ER/ARD rate estimation.

## Revised A1 order

1. Recover the detailed 2025 study record (conference abstract/poster, thesis-level record, or another lawful copy) and extract sample counts, vouchers, genetic result, and accession/data statements.
2. Search explicitly for reusable MIG-seq FASTQ/genotype data using those recovered sample identifiers.
3. If a credible local MIG-seq topology can be reconstructed, use it to refine which close comparator/lineage should be prioritized; do not substitute it for the common-locus tree.
4. If no homologous reusable nuclear data become available, obtain at least two independent voucher/flower-colour-linked *C. boninense* samples for the Compositae1061-compatible placement gate.

## Sampling consequence

This update **does not add samples to core190** and does not yet authorize a new *C. boninense* sequencing count beyond the existing conditional fixed-white promotion plan.

The main information gain is that the old `method unknown` blocker is closed. The remaining blocker is now narrower: **recover the MIG-seq samples/results/data, then decide whether new homologous target-capture sampling is still necessary.**

## Sources

- Chiba University Global Studies Vol.9 (2025), institutional publication summary: `https://opac.ll.chiba-u.jp/da/curator/900123082/S24326291-9-P295.pdf`
- J-GLOBAL conference record: `https://jglobal.jst.go.jp/detail?JGLOBAL_ID=202502289420525672`
- NMNS *C. boninense* account: `https://www.kahaku.go.jp/research/db/botany/azami/detail.html?no=34`

## Claim boundary

Public indexing establishes the study method and listed comparison taxa, not its sample size, result topology, data availability, or common-locus compatibility. No sister relationship or rate-tree promotion is inferred from the abstract alone.
