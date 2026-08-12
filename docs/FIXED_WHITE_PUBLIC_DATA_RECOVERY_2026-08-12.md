# Fixed-white public nuclear-data recovery — 2026-08-12

## Purpose

Before generating new nuclear data for the two A1 fixed-white candidates, exhaust credible existing-data routes. The flower-colour gate still requires two additional fixed-white **species-level nuclear tips**; a conference presentation, PAFTOL interface link or taxonomic voucher does not itself satisfy that gate.

Machine-readable audit: `data/evidence/fixed_white_public_nuclear_recovery_audit_2026-08-12.csv`.

## Cirsium boninense — existing genetic study is now the first recovery route

A 2025 Japanese Plant Taxonomy Society presentation is indexed as:

> 篠﨑琢海・川井絢子・上原浩一・伊藤元己・石川直子・陶山佳久・中濱直之（2025）「遺伝子情報によるオガサワラアザミの起源解明」日本植物分類学会第24回大会，p.69.

The same presentation is independently listed by the Tohoku University Forest Ecology laboratory. This changes the operational status of *C. boninense*: it is no longer appropriate to move directly from “no exact public tree tip recovered” to new sequencing without first trying to recover the existing study's method, sample identities and reusable data/accessions.

Current bounded public search did **not** recover an exact NCBI BioProject/SRA or DDBJ plant sequence artifact under the exact taxon name. Searches for abbreviated `C. boninense` are unsafe because the fungal *Colletotrichum boninense* produces abundant unrelated sequence hits.

Kew POWO also exposes a PAFTOL/Tree-of-Life interface lead for accepted *Cirsium boninense*. That is worth resolving, but it must remain a lead until an exact sample/sequence/provenance record is recovered.

### Required order

1. Recover the full 2025 meeting abstract/poster if lawfully accessible.
2. Identify the actual molecular method, sample/voucher identities and any archive accession **from the study itself**; do not infer MIG-seq, target capture or another method from coauthor expertise.
3. Resolve the Kew PAFTOL/Tree-of-Life lead to an exact taxon/sample/sequence artifact if possible.
4. If a reusable nuclear dataset exists, test whether it can supply a defensible placement and whether >=2 independent individuals are represented.
5. Only if existing data are unavailable, unsuitable or single-individual-only should new sampling/Compositae1061 capture become the primary route.

No author contact has been sent from this repository workflow.

## Cirsium wulongense — concrete specimen anchors, no indexed nuclear asset recovered

The 2024 primary description gives a white corolla and provides two concrete Xiannü Shan specimen identifiers:

- `XLS21-095` — holotype, IBSC; isotypes CQNM;
- `XLS21-093` — additional specimen, CBNM/IBSC.

Exact-name searches of NCBI BioProject/SRA and DDBJ/ENA did not recover an indexed *C. wulongense* nuclear dataset in the bounded 2026-08-12 search. This is a **no-recovery result**, not proof that no author-held, institutional, unpublished or differently indexed data exist.

### Required order

1. Search author/institutional/herbarium-held molecular data using both the taxon name and `XLS21-095` / `XLS21-093`.
2. If existing sequence data are found, require exact specimen/sample provenance before use.
3. If no reusable nuclear data exist, obtain >=2 independent voucher-linked fixed-white individuals matching the published taxonomic concept.
4. Prefer the recovered original Compositae1061 reference for compatibility with the current 20-tip bridge; Angiosperms353 or low-coverage WGS remains an explicitly independent fallback.

The existing coloured *C. fanjingshanense* Moreyra tip is a useful regional comparator, but the morphological comparison in the species description is not an assumed sister relationship.

## Promotion boundary

Neither A1 species is currently rate-fit eligible. Existing-data recovery only changes that status after the normal fixed-white promotion contract passes:

- >=2 independent voucher/phenotype-linked individuals per new species;
- concordant identity and placement;
- acceptable homologous nuclear recovery;
- no unresolved taxonomic conflict;
- topology/filter sensitivity;
- one species-level representative selected by predeclared QC rather than by the preferred colour history.

After both species pass, the final macroevolutionary tree is rebuilt as **22 species tips (C=17, W=5)** rather than treating replicate individuals as independent transitions.
