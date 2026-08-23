# Fixed-white public nuclear-data recovery — 2026-08-12

Original audit date: 2026-08-12  
Current execution status: 2026-08-23

## Current status — 2026-08-23

The public-data route has advanced, but it has **not produced either missing homologous rate-tree tip**.

- *Cirsium boninense*: the 2025 genetic study is now publicly confirmed to use **MIG-seq**, with an indexed five-taxon comparison including *C. boninense*, *C. irumtiense*, *C. brevicaule*, *C. spinosum* and *C. maritimum*. The method therefore no longer needs to be guessed or recovered from p.69. However, the public material recovered so far does not provide the sample/voucher detail, reusable raw/genotype data or Compositae1061-compatible sequence needed for rate-tree promotion.
- *Cirsium wulongense*: the primary study remains morphology-only, and no exact public homologous nuclear asset has been recovered.
- active A1 promotion contract: `data/evidence/fixed_white_tree_promotion_contract_v0_2.json`.
- current promoted A1 species: **0/2**.
- current atlas: C=17, W=3; numerical target C=17, W=5.
- current rate fitting remains blocked.

The dated machine-readable audit `data/evidence/fixed_white_public_nuclear_recovery_audit_2026-08-12.csv` is retained as the bounded 8/12 search record. The later *C. boninense* method recovery is frozen separately in `data/evidence/boninense_migseq_public_recovery_v1.json` and `data/evidence/fixed_white_a1_priority_v2.csv`.

## Purpose

Before generating new nuclear data for the two A1 fixed-white candidates, exhaust credible existing-data routes. A conference presentation, image attribution, catalogue record, morphology-only taxonomic paper, MIG-seq method statement or taxonomic voucher does not itself satisfy the gate. Promotion requires reusable homologous nuclear data tied to independently supported fixed-white species-level identities and must pass the frozen promotion contract.

Author contact is still separated from the public-data lane. Nothing in this repository claims that an author request has been sent.

## Cirsium boninense — MIG-seq confirmed, reusable rate-tree data still unrecovered

A 2025 Japanese Plant Taxonomy Society presentation is indexed as:

> 篠﨑琢海・川井絢子・上原浩一・伊藤元己・石川直子・陶山佳久・中濱直之（2025）「遺伝子情報によるオガサワラアザミの起源解明」日本植物分類学会第24回大会，p.69.

Subsequent public institutional material resolves the method as **MIG-seq** and indexes a five-taxon comparison containing *C. boninense*, *C. irumtiense*, *C. brevicaule*, *C. spinosum* and *C. maritimum*. This is useful evidence about the existence and broad design of a genetic study, but it is not a Compositae1061 rate-tree tip.

The full 2025 meeting proceedings remains catalogued by the National Diet Library as:

- NDL bibliographic ID `034039888`;
- call number `RA241-R8`;
- target contribution p.69.

The value of p.69 has therefore changed. It is no longer needed to establish the molecular method. It may still be useful if it contains exact sample counts, vouchers, localities, result details or archive/accession information absent from the public summary.

Bounded exact-name searches have not recovered a reusable NCBI BioProject/SRA, DDBJ/ENA, genotype matrix or equivalent plant sequence asset that can be joined to the frozen Compositae1061 matrix. Searches for abbreviated `C. boninense` remain unsafe because the fungal *Colletotrichum boninense* complex produces abundant unrelated hits.

### Kew/PAFTOL route

POWO displays `Image: PAFTOL` and a Tree-of-Life interface link for *C. boninense*. Direct audit of the Kew Tree of Life Explorer release used by this project found no exact `Cirsium boninense` in its current sequence/specimen manifests or deleted-sequence list. The UI attribution is therefore not treated as a recovered nuclear rate-tree tip.

This is an indexed non-recovery result, not proof that no older, differently named, unpublished or partner-held data exist.

### Current public-only order for boninense

1. Search for exact sample/voucher/result/accession details associated with the confirmed MIG-seq study; method identification is already complete.
2. If p.69 can be lawfully read, use it specifically to recover sample counts, voucher/locality detail, result structure and archive/accession information rather than to infer the method.
3. If a reusable dataset appears, test whether it contains >=2 independent *C. boninense* individuals with identity/phenotype linkage and whether it can satisfy the active homologous promotion contract.
4. MIG-seq data may inform identity/origin or replicate diagnostics, but it cannot silently replace the frozen 153-locus Compositae1061 branch-length matrix.
5. If no suitable public homologous data are available, the direct empirical route is >=2 new voucher/flower-colour-linked Compositae1061-compatible individuals.

## Cirsium wulongense — morphology-only study; public homologous nuclear route remains negative

The 2024 primary description provides the concrete Xiannü Shan collections:

- `XLS21-095` — holotype, IBSC; isotypes CQNM; 14 Aug 2021, 1780 m;
- `XLS21-093` — additional specimen, CBNM/IBSC; 14 Aug 2021, 1651 m.

The published Materials and methods section reports specimen collection and morphological/herbarium comparison. It does not report DNA extraction, sequencing, molecular markers, phylogenetic analysis or a sequence-generation workflow. The primary publication therefore cannot provide the missing nuclear tip.

Exact-name public sequence searches and bounded exact-voucher web/index searches have not recovered an exact reusable nuclear dataset. The lack of a public digitized voucher record is not evidence that the physical sheets are absent.

The primary description also reports a Zunyi, Guizhou locality based on Plant Photo Bank of China image `2837783`. This is a future-sampling lead only; it is not a voucher-linked nuclear replicate.

### Current public-only order for wulongense

1. Treat the 2024 article molecular-data route as closed: it is morphology-only.
2. Continue exact-name and exact-voucher checks for public molecular/specimen assets around `XLS21-095` and `XLS21-093`.
3. Retain the Guizhou PPBC locality as an independent geographic sampling lead, without counting it as a sequence/voucher replicate.
4. If no reusable public homologous asset emerges, obtain >=2 independently verified fixed-white individuals using the active Compositae1061-compatible sampling contract.

The existing coloured *C. fanjingshanense* Moreyra tip is only a regional comparator; the morphological comparison in the species description is not an assumed sister relationship.

## Promotion boundary — current active rule

Neither A1 species is currently rate-fit eligible. Public-data recovery changes that status only after the active v0.2 promotion contract passes. In particular:

- >=2 independent voucher/flower-colour-linked passing individuals per species;
- >=123/153 clean recovered frozen loci per passing individual;
- the 153-locus universe cannot be reselected after seeing the new white taxa;
- new-sample paralog warnings mask the affected individual/locus instead of deleting the locus;
- replicate identity and placement must be concordant before species-level collapse;
- one representative per species is selected by deterministic QC, never by preferred colour history or rate result;
- after both species pass, all alignments and the branch-length tree are rebuilt on the same frozen 153 loci for **22 focal species + OUTGROUP_saff**;
- the expanded tree must be reaccepted and its topology uncertainty re-evaluated;
- the final tree taxon set must exactly match the expanded rate-fit atlas.

Thus a public discovery that merely raises the white-tip count is insufficient by itself. The final rate-analysis unlock is a joint **data + identity + exact-tip rebuilt-tree** gate.
