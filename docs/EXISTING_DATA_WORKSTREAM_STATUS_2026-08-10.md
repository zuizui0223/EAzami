# Existing-data workstream status

Date: 2026-08-10

This page separates analyses that are already executable from tasks that genuinely require new biological material.

## A. Existing-data analyses completed or implemented

### Flower-colour history diagnostics

- minimum-transition Fitch sensitivity;
- species-level versus population-aware coding sensitivity;
- root-dependent directional loss/regain counts;
- Arenicola sister-context analysis;
- Sinocirsium parallel-loss versus loss-plus-regain enumeration;
- exploratory ER versus ARD Mk sensitivity;
- branch-scale sensitivity showing why exact branch lengths are required;
- proxy expected-information-gain sampling ranking.

### Evidence audits

- Chang 2025/2026 nuclear anchors;
- Moreyra 2025 Japanese nuclear-backbone correction;
- Japan–China bridge taxa;
- Korean white-form candidates, cytology and organelle/nuclear distinctions;
- exact-tree/source-artifact recovery matrix;
- public SRA project-tip recovery route for `PRJNA957074`.

### Reproducible metadata recovery

Implemented:

- `analysis/recover_ncbi_project_runs.py`
- `data/evidence/focal_taxa_prjna957074.txt`
- `.github/workflows/recover-ncbi-project-metadata.yml`
- `tests/test_recover_ncbi_project_runs.py`

The local offline parser/audit path was tested with the verified *C. domonii* SRA record. Full online project recovery awaits execution in an environment with NCBI access; the workflow is designed to produce and upload the complete tables after the branch is available to GitHub Actions.

### Directly verified project anchor

The exact public SRA metadata recovered for *C. domonii* are:

- `SAMN34240283`
- `SRS18284452`
- `SRX21011499`
- `SRR25265717`
- library `Cirsium-domonii_FJ318`
- Japan: Honshu

This validates the accession-level data model and offline tests, but it is not represented as completion of the full project recovery.

## B. Existing-data tasks still open

1. Execute full `PRJNA957074` runinfo recovery.
2. Recover Moreyra Supplementary Data 1 and exact Newick/branch lengths.
3. Recover Chang machine-readable tree artifacts and exact sample tables.
4. Harmonize all recovered names/synonyms with the East Asian master table.
5. Join exact tips to flower colour, ploidy and geography.
6. Rerun full-tree Mk/stochastic maps across alternative nuclear topologies.
7. Replace proxy EIG with model/posterior-based information gain.
8. Verify extant/voucher-backed Korean white morphs from herbarium or field records.

## C. Work genuinely blocked on new biological data

### Field material

Matched individual IDs linking:

- voucher and coordinates;
- standardized colour/reflectance;
- pigment tissue;
- floral RNA;
- leaf DNA;
- fresh ploidy material where possible.

### Molecular evidence

- anthocyanin/flavonoid chemistry;
- matched-stage floral RNA-seq;
- causal-region/haplotype genotyping;
- structural/cis-regulatory variation;
- allele-specific expression where informative.

### Population history

- dense white/coloured population RAD/resequencing;
- ploidy-aware genotype handling;
- introgression/ancestral-polymorphism tests;
- local ancestry around colour loci.

### Selection

Only after history and mechanism are bounded:

- pollinator/visual preference;
- UV/heat/drought/herbivory;
- genotype-specific visitation and reproductive fitness.

## D. Current hypothesis hierarchy

1. **Repeated anthocyanin loss/suppression** — strongest existing-data hypothesis.
2. **Repeated use of regulatory rather than irreversible structural changes** — mechanistically plausible, not yet demonstrated across focal systems.
3. **Ancestral polymorphism and introgression explain some apparent transitions** — serious alternatives, especially in young/reticulate lineages.
4. **True regain/reactivation** — strongest current candidate is bluish-purple var. *takaoense*, but parallel white losses remain equally parsimonious.
5. **Single ancient white origin with many regains** — currently disfavoured relative to repeated losses.

## E. Current sequencing decision rule

Do not sequence a taxon merely because its exact tip was not visible in an article search.

Promote to species-level nuclear sequencing only when:

1. complete public-project/supplement/synonym recovery still shows a genuine modern nuclear gap;
2. the taxon's position changes a colour-transition inference or supplies an independent white-flower replicate;
3. ploidy and taxonomic identity can be handled defensibly.

Use dense population RAD/resequencing when species placement already exists but the question is standing variation, introgression, population origin or colour-associated haplotypes.
