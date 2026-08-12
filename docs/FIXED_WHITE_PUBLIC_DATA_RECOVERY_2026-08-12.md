# Fixed-white public nuclear-data recovery — 2026-08-12

## Purpose

Before generating new nuclear data for the two A1 fixed-white candidates, exhaust credible existing-data routes. The flower-colour gate still requires two additional fixed-white **species-level nuclear tips**; a conference presentation, image attribution, catalogue record or taxonomic voucher does not itself satisfy that gate.

Machine-readable audit: `data/evidence/fixed_white_public_nuclear_recovery_audit_2026-08-12.csv`.

## Cirsium boninense — existing 2025 genetic study is now the only strong public-data recovery route

A 2025 Japanese Plant Taxonomy Society presentation is indexed as:

> 篠﨑琢海・川井絢子・上原浩一・伊藤元己・石川直子・陶山佳久・中濱直之（2025）「遺伝子情報によるオガサワラアザミの起源解明」日本植物分類学会第24回大会，p.69.

The same presentation is independently listed by the Tohoku University Forest Ecology laboratory. J-GLOBAL indexing also includes イリオモテアザミ as a quasi-thesaurus term, making the actual study especially relevant to the Arenicola question; that indexing clue is not evidence that *C. irumtiense* was sequenced.

The full 2025 meeting proceedings is catalogued by the National Diet Library as a 110-page volume, bibliographic ID `034039888`, call number `RA241-R8`; the target contribution is p.69. This is now the concrete public-document recovery route for method/comparator/sample information.

Bounded exact-name searches did **not** recover an NCBI BioProject/SRA or DDBJ plant sequence artifact. Searches for abbreviated `C. boninense` are unsafe because the fungal *Colletotrichum boninense* produces abundant unrelated sequence hits.

### Kew/PAFTOL lead resolved: no exact current-release taxon

POWO displays `Image: PAFTOL` and a Tree-of-Life interface link for *C. boninense*. This was previously retained as an unresolved nuclear-data lead. Direct audit of the actual Kew Tree of Life Explorer release v4.0 now resolves that ambiguity:

- `sequence_manifest.txt`: no exact `Cirsium boninense`;
- `specimen_manifest.txt`: no exact `Cirsium boninense`;
- `deleted_sequences.txt`: no exact `Cirsium boninense` deletion entry for the current release;
- the same current manifests do contain multiple other *Cirsium* species, so the absence is not because the genus is missing from the release.

Therefore the POWO `Image: PAFTOL` element must **not** be treated as evidence of a current Kew nuclear sample or accepted rate-tree tip. The Kew v4.0 exact-taxonomy route is exhausted for the present audit. This does not prove that no older, differently named, unpublished or partner-held data exist.

### Required order

1. Obtain/read NDL proceedings p.69 through a lawful library route or recover the full poster/extended abstract.
2. Identify the actual molecular method, comparator taxa, sample/voucher identities and archive accession **from the study itself**; do not infer MIG-seq, target capture or another method from coauthor expertise.
3. If the 2025 study provides a reusable nuclear dataset, test whether >=2 independent *C. boninense* individuals are represented and whether their placement is concordant.
4. If data are unavailable, unsuitable or single-individual-only, obtain >=2 new voucher/flower-colour-linked nuclear samples, preferably in the recovered original Compositae1061 compatibility space or with an explicitly independent assay.

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
