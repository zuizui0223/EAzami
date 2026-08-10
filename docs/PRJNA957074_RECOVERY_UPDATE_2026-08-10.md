# PRJNA957074 sample-recovery update

Date: 2026-08-10

## Purpose

The Moreyra nuclear phylogeny is already a major species-level backbone, but the exact sample/tip list is still partly hidden behind Supplementary Data 1 and unrecovered tree files. The practical problem is therefore not simply “missing phylogeny”. It has three distinct parts:

1. **file-recovery gap** — the taxon is already present in a published/deposited dataset but the local project has not yet recovered its exact accession or tree tip;
2. **population-level gap** — species placement exists, but the white/coloured populations required for the flower-colour question were never sampled;
3. **true nuclear gap** — no modern multi-locus nuclear placement remains after project metadata, supplements, synonyms and other recent datasets have been checked.

New RAD/target-capture sequencing should address category 3, or category 2 when population history is the biological question. It should not duplicate category 1.

## Directly verified record

One exact Moreyra-project record is now fully anchored:

- taxon: *Cirsium domonii*
- BioProject: `PRJNA957074`
- BioSample: `SAMN34240283`
- SRA sample: `SRS18284452`
- experiment: `SRX21011499`
- run: `SRR25265717`
- library: `Cirsium-domonii_FJ318`
- locality: Japan: Honshu

This proves that public SRA metadata can reconstruct actual target-capture tips at sample/run resolution.

## Why ordinary web search is insufficient

Targeted searches recovered the *C. domonii* page but did not reliably expose the full project. Search-engine non-recovery for *C. pendulum*, *C. sieboldii*, Korean candidates or other taxa is therefore coded as `exact_project_tip_unresolved`, never as absence.

The official recovery route is now implemented in `analysis/recover_ncbi_project_runs.py`:

1. query SRA Entrez for all UIDs linked to a BioProject;
2. fetch official SRA `runinfo` metadata in chunks;
3. summarize unique scientific names, BioSamples, experiments and runs;
4. compare the complete result against a versioned focal-taxon list;
5. optionally enrich the rows from BioSample XML with collection locality/date.

The script uses only the Python standard library, throttles requests, retries transient failures and has an offline mode for testing or reprocessing a downloaded run table.

Example after setting an NCBI contact email:

```bash
export NCBI_EMAIL="your-address@example.org"
python analysis/recover_ncbi_project_runs.py \
  --bioproject PRJNA957074 \
  --enrich-biosample
```

Expected generated files:

- `data/evidence/generated/PRJNA957074_runinfo.csv`
- `data/evidence/generated/PRJNA957074_taxon_summary.csv`
- `data/evidence/generated/PRJNA957074_focal_taxon_audit.csv`

A manual workflow, `.github/workflows/recover-ncbi-project-metadata.yml`, runs the same recovery after the workflow is available to GitHub Actions and uploads the results as an artifact.

## Verification and current execution limit

The offline parser, summarizer and focal-audit functions were tested with the exact *C. domonii* SRA record. The active execution environment used to prepare this branch did not provide outbound DNS access to NCBI, so the full 299-plant project table has **not yet been claimed as recovered**. The code/workflow is in place; the complete generated artifact remains an explicit pending result.

## Related 2023 source

The 2023 African mountain-thistle target-capture study used the same BioProject and reports a Supplementary Table S1 with sample/BioSample/voucher information for a substantial subset of the project. Recovering that supplement is a useful second route, but it does not automatically replace the larger sample table used by Moreyra et al. 2025. The project-run table remains the authoritative way to identify all public SRA records.

## Current evidence-level interpretation of focal taxa

### Exact project sample verified

- *C. domonii*

### Published placement or discussion, exact run pending

- *C. dipsacolepis*
- *C. lineare*
- *C. tamastoloniferum*
- *C. pendulum*
- *C. japonicum*

A main-text mention is not treated as proof of inclusion unless the paper explicitly places the species or an accession is recovered.

### Project-tip status still unresolved

- *C. sieboldii*
- *C. yezoense*
- *C. setidens*
- *C. rhinoceros*
- *C. schantarense*
- *C. vlassovianum*
- *C. nipponicum*

For these taxa, a complete runinfo recovery must precede any claim of a true nuclear gap.

### Already resolved by separate modern nuclear datasets

- *C. brevicaule* and *C. irumtiense* — Chang et al. 2026
- *C. kawakamii*, *C. tatakaense*, *C. pengii* and associated Nipponocirsium anchors — Chang et al. 2025

Their priority is population genomics and flower-colour mechanism, not generic species placement.

## Decision consequences

Once the full project metadata are recovered:

1. mark every focal taxon as exact project tip present/absent;
2. harmonize accepted names, varieties and synonyms before counting absences;
3. join exact tips to the East Asian flower-colour atlas and ploidy table;
4. remove false RAD targets that are already present in the 350-locus tree;
5. retain species-level sequencing only for true colour-relevant nuclear gaps;
6. retain dense RAD sampling for species already placed when population structure, introgression or standing variation is the question.

This keeps Chapter 2 centred on inference about repeated loss/regain rather than on indiscriminate taxon accumulation.
