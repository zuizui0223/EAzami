# Japanese Cirsium origins — maximal public-data test (2026-08-12)

## Question

Before commissioning broad new sampling in China, determine how much of the origin of Japanese *Cirsium* can be resolved from already-public nuclear data.

The published Moreyra 2025 result is the prior, not the result of this new reanalysis: among the 38 Japanese taxa sampled in that study, 36 were interpreted as a major rapid Japanese radiation, whereas *C. dipsacolepis* and *C. lineare* represent separate Japanese invasion histories. This does **not** establish that the complete Japanese flora is monophyletic or that every Japanese lineage derives from the same colonisation.

The most important missing test is Ryukyu Arenicola. *C. brevicaule* and *C. irumtiense* were absent from the Moreyra Japan-38 sample but have three public Chang 2026 transcriptomes each. Ogasawara *C. boninense* still lacks a reusable exact modern nuclear tip.

## Public-first panel

`analysis/build_japan_origin_max_public_panel.py` combines the currently curated public evidence without pretending that different assays are already directly comparable.

### Layer 1 — Moreyra 2025

Use every currently curated East/Northeast Asian PRJNA957074 biological sample with linked runinfo, grouped by BioSample rather than by run.

- Japan: dense main-radiation sampling plus the published *dipsacolepis* and *lineare* exception anchors;
- China: currently available continental source/sister candidates;
- Russian Far East, Inner Northeast Asia and Mongolia: geographic bridge samples.

The known `C. yuki-uenoanum` Japan-voucher / NCBI `C. waldsteinii` Ukraine geography conflict is retained in an exclusion ledger and is not admitted automatically. High-priority taxon-name conflicts are retained under their source labels and flagged for review rather than silently renamed.

### Layer 2 — Chang 2025

All audited PRJNA1158676 samples are retained as a transcriptome bridge, including Japanese Nipponocirsium and Taiwanese relatives. Exact SRA-run joining is a separate provenance step where the current audit gives only the BioProject/voucher layer.

### Layer 3 — Chang 2026

All audited PRJNA1311153 samples are retained, with special roles for:

- *C. brevicaule*: 3 public Ryukyu samples;
- *C. irumtiense*: 3 public Ryukyu samples;
- *C. morii*: Arenicola sister-context control;
- *C. lineare*: cross-assay separate-invasion anchor;
- Japanese *C. japonicum* and Taiwan complexes: East-Asian bridge context.

An embedded SRR/SRX/SAMN identifier is preserved where supplied. Rows without an embedded identifier remain in an explicit BioProject-run-resolution queue. Their run IDs must be recovered with the existing NCBI recovery/reconciliation code before heavy execution.

## Hypotheses to test

The joint common-locus analysis will predeclare the following alternatives.

1. **All sampled Japanese-flora lineages are monophyletic.** Current published evidence predicts rejection, but the complete Japanese-flora question has not yet been tested because Ryukyu/Ogasawara coverage is incomplete.
2. **The Moreyra main Japanese radiation remains a coherent clade after continental sampling is densified.** This is the strongest published prior.
3. ***C. dipsacolepis* and *C. lineare* remain separate Japanese invasion histories.** This tests the published biogeographic interpretation in the public-read compatibility reanalysis.
4. **Arenicola placement:** *C. brevicaule–C. irumtiense* lies (a) inside the main Japanese radiation, (b) sister to it, or (c) on an independent southern/continental invasion branch. This is the highest-information result for deciding whether new Southeast-China/Taiwan bridge sampling is necessary.
5. **Reticulation sensitivity:** apparent geographic origins are checked against paralog/homeolog and network-sensitive results before being interpreted as simple colonisation events.

## Common-locus requirement

No topology comparison is allowed by concatenating unrelated assay outputs directly. Moreyra target capture and Chang transcriptomes must first be projected into the same validated Compositae1061 homolog space. Use the recovered original Compositae1061 reference and retain separate diagnostics for:

- conservative no-current-paralog loci;
- broader reproducible loci;
- paralog/homeolog-aware sensitivity.

A cross-assay locus must pass current occupancy/QC after all admitted samples are included. The final retained-locus count is an output, not a predeclared claim.

## Decision rule for new Chinese sampling

**Do not freeze a broad China collection list before the maximal public tree.**

After the public-only tree/network is available, rank unsampled Chinese taxa by information gain:

1. exact sister/source neighbourhood of the main Japanese radiation;
2. exact sister/source neighbourhood of Arenicola;
3. branches separating *dipsacolepis* and *lineare* from the main radiation;
4. geographic/taxonomic bridges where public samples are missing or conflicted;
5. otherwise defer redundant Chinese sampling.

If public Chinese PRJNA957074 samples already bracket a relevant Japanese node robustly, new Chinese sampling is not automatically required. If a node remains bounded by a long unsampled continental branch, target 2–3 verified individuals from the missing lineage rather than performing generic China-wide collection.

## Claim boundary

The generated manifest is **not** a phylogenetic result. Until common-locus recovery and joint inference are completed:

- do not claim all Japanese *Cirsium* are monophyletic;
- do not claim Arenicola belongs to the main Japanese radiation;
- do not infer a continental source from geography alone;
- do not treat replicate individuals as independent colonisation events;
- do not use the public-panel design to strengthen flower-colour regain/loss claims.

The immediate output is an evidence-maximising execution panel that postpones new Chinese sampling until the public data reveal which continental gaps actually control the inference.
