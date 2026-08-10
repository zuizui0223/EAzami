# Moreyra et al. 2025 — reconstruction of the 38 Japanese sampled taxon concepts

Date: 2026-08-10

## Why this audit was needed

Moreyra et al. (2025) state that their global target-capture analysis included **38 Japanese species, 30 endemic**, and that all but two formed a rapid-radiation clade following a Pleistocene dispersal to Japan. The article text gives the count but does not list the 38 names in one main-text table.

Supplementary Table S1 and PRJNA957074 are now recovered. Their sampling metadata allow the article-level count to be reconstructed, but the result must be called **38 paper taxon concepts**, not 38 frozen current accepted names, because:

- several samples are identified at variety rank;
- two tree codes map to the same published taxon concept;
- some taxa were sampled from botanical gardens;
- two Japanese-distributed species were sampled outside Japan;
- tree code, published species and NCBI scientific name conflict for several samples;
- one putative Japanese sample has a critical Japan–Ukraine metadata conflict.

The full table is:

- `data/evidence/moreyra2025_japan_38_membership_audit_2026-08-10.csv`

## Count reconstruction

The article's count can be reproduced as:

| Membership class | Paper taxon concepts | Interpretation |
|---|---:|---|
| Direct Japanese voucher and/or BioSample locality | 30 | clean Japanese provenance under the published taxon concept |
| Direct Japanese concept with serious metadata conflict | 1 | retained in the paper count, excluded from clean downstream use |
| Cultivated Japanese taxon | 4 | `C. buergeri`, `C. microspicatum`, `C. nipponicum`, `C. sieboldii` |
| Cultivated Japanese taxon with unresolved name conflict | 1 | `C. effusum` tree code / NCBI `C. pulchellum` |
| Japanese-distributed species sampled outside Japan | 2 | `C. kamtschaticum`, `C. pendulum` |
| **Total** | **38** | matches the article statement |

A crucial deduplication is required: tree codes `C. tanakae` and `C. tonense` both have the published species assignment `C. nipponicum var. incomptum`. They count as one paper taxon concept in the Japan-38 reconstruction, not two.

## Direct Japanese material

Thirty-one paper taxon concepts have Japanese provenance in the supplement or public BioSample record. Thirty are usable as high-confidence paper-membership records. The thirty-first is retained only as an unresolved paper concept:

- tree code: `Cirsium yuki-uenoanum`;
- published species: `Cirsium yuki-uenoanum Kadota`;
- supplement voucher: Japan;
- BioSample: `SAMN44017949`;
- NCBI scientific name: `Cirsium waldsteinii`;
- NCBI geography: Ukraine.

This record is not permitted to anchor Japanese flower-colour history until the original voucher, accession assignment and tree tip are manually checked.

## Cultivated material

Five paper concepts were represented by cultivated accessions rather than a direct wild Japanese locality.

### Supported Japanese taxa

- `C. buergeri` — Kyoto Botanical Garden; current Japanese database treats it as a Japanese endemic.
- `C. microspicatum` — Tokyo Metropolitan Medicinal Plants Garden; current Japanese database treats it as a Japanese endemic of Honshu.
- `C. nipponicum` — Tokyo Metropolitan Medicinal Plants Garden; current Japanese database records it from northern Honshu.
- `C. sieboldii` — Botanical Garden of Barcelona; current Japanese database treats it as a Japanese endemic of Honshu and Shikoku.

These are defensible members of the article's Japanese sample count, but cultivated provenance remains distinct from wild population representation.

### Unresolved `C. effusum`

The tree code is `C. effusum`, the material came from Tokyo Metropolitan Medicinal Plants Garden, and NCBI calls the sample `C. pulchellum`. Japanese taxonomic documentation also shows historical ambiguity in the use of the name `C. effusum`.

Therefore this row is retained as one of the 38 **paper taxon concepts**, but it is not yet joined to the flower-colour atlas under a frozen accepted name.

## Japanese-distributed taxa sampled on the continent

Two species help reconcile the article count although their sequenced samples were collected outside Japan:

- `C. kamtschaticum` — sampled in Chukotka/Kamchatka; current distribution evidence includes Hokkaido.
- `C. pendulum` — sampled in Trans-Baikal; current Japanese evidence records it from northern Honshu and Hokkaido, as well as Korea, northeast China and Siberia.

These are especially useful as continental bridge tips, but the sampled individuals cannot substitute for Japanese population data.

## Consequence for Chapter 2

### What no longer needs new species-level placement sequencing

The 38-member audit confirms that a substantial Japanese nuclear framework already exists. New target capture should not be proposed merely because a taxon was sampled from a garden, the continent, or under an older name.

For a species already represented by a verified Moreyra paper concept, the default action is:

1. reconcile the name and voucher;
2. recover its exact final tree position when the Moreyra tree becomes available;
3. join source-backed flower colour and cytotype;
4. use population-scale RAD-seq or resequencing if morph or geographic history is unresolved.

### High-priority population systems retained

- `C. pendulum`: continental nuclear tip exists; Japanese white/coloured population history is missing.
- `C. sieboldii`: species-level nuclear tip exists; Japanese white/coloured morphs and Zhejiang bridge populations are missing.
- `C. nipponicum`: species-level nuclear tip and reference genome exist; regional population/cytotype history is not solved by one cultivated accession.

### Residual species-level gaps

The Japan-38 reconstruction does not fill taxa absent from Moreyra and Chang. Transition-critical gaps must still be evaluated independently, including Korean white-form candidates and East Asian taxa outside the recovered backbones.

## Status terminology

Use the following terms consistently:

- `paper_taxon_concept` — the unit counted in the Moreyra article/sample table;
- `tree_code` — the actual label used in the analysis;
- `published_species` — the taxon name in Supplementary Table S1;
- `ncbi_scientific_name` — the submitted public-read name;
- `current_accepted_taxon` — authority-backed decision still to be completed;
- `clean_Japanese_tip` — a reconciled taxon with non-conflicting voucher and sample identity.

The 38-count audit freezes paper membership. It does **not** replace the authority-backed accepted-name freeze.

## Next step

Once the final Moreyra tree files are recovered, map all 38 paper taxon concepts to tree tips, preserve unresolved names as separate audit states, and join the flower-colour atlas. Formal ancestral-state reconstruction should exclude or sensitivity-test the unresolved `yuki-uenoanum` / `waldsteinii` record and any cultivated accession whose identity cannot be verified.
