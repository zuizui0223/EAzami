# Chang 2025/2026 phylogeny-artifact and flower-colour audit

Date: 2026-08-10

## Purpose

This audit separates four claims that had previously been mixed together:

1. a published species-level topology exists;
2. the exact sample/voucher table is recoverable;
3. flower-colour states can be attached to individual phylogenetic tips;
4. anthocyanin expression or pollinator preference was experimentally analysed.

Only claims directly supported by the accessible article and recovered official supplementary files are retained.

## Recovered official artifacts

### Chang et al. 2025 — Nipponocirsium

- DOI: `10.1186/s40529-025-00454-2`
- official Supplementary Material 1 recovered from Springer Nature;
- size: 28,699 bytes;
- SHA256: `a1c67668d001dd443292cea3dd05851cb68df6f6f94afe143459306051d848e8`;
- four supplementary tables extracted;
- no machine-readable Newick/Nexus tree was present in the recovered DOCX.

Recovered tables contain:

1. transcriptome assembly and exact collecting/voucher metadata;
2. pollen vouchers;
3. chromosome vouchers;
4. a Taiwan–Japan comparison including corolla colour and phyllary glutinosity.

The sample audit is stored in:

- `data/evidence/chang2025_nipponocirsium_accession_audit_2026-08-10.csv`

The recovered Cirsium transcriptome set contains 13 samples:

| Taxon | Samples | Corolla state used for the colour screen |
|---|---:|---|
| `C. lineare` | 2 | coloured reference |
| `C. tatakaense` | 4 | bluish-purple |
| `C. kawakamii` | 2 | white |
| `C. pengii` | 2 | bluish-purple |
| `C. suffultum` | 1 | bluish-purple |
| `C. nipponicum var. incomptum` | 1 | pale purple |
| `C. kujuense` | 1 | bluish-purple |

The published species relationship can therefore be represented, without invented branch lengths, as:

```newick
(Cirsium_lineare,((Cirsium_kujuense,(Cirsium_suffultum,Cirsium_nipponicum_var_incomptum)),(Cirsium_pengii,(Cirsium_kawakamii,Cirsium_tatakaense))));
```

### Chang et al. 2026 — Sinocirsium, Arenicola and allied East Asian thistles

- DOI: `10.1186/s12870-026-08097-6`
- the first `media.springernature.com` request returned a client-challenge HTML file rather than a DOCX;
- the equivalent official `static-content.springer.com` endpoint recovered the actual Supplementary Material 1;
- size: 4,240,091 bytes;
- SHA256: `650f42cb876e0a7b68aac61b127cb9d7586a3ea0bac4e3070adf204b852251a9`;
- six supplementary tables and 13 supplementary figures extracted;
- no machine-readable Newick/Nexus tree was present in the recovered DOCX.

The recovered supplement contains:

- exact transcriptome sample, code, coordinate, altitude, voucher and herbarium metadata;
- divergence-time/EBSP ESS diagnostics;
- flow-cytometry vouchers and genome-size measurements;
- SDM diagnostics;
- examined-specimen lists and type images.

The complete 33-tip Cirsium sample audit is stored in:

- `data/evidence/chang2026_east_asia_accession_audit_2026-08-10.csv`

Sample counts are:

| Taxon | Samples | Flower-colour resolution |
|---|---:|---|
| `C. japonicum var. albescens` | 2 | fixed-white taxon |
| `C. japonicum var. takaoense` | 6 | taxon is white/bluish-purple polymorphic, but individual transcriptome samples are not assigned to morph |
| `C. japonicum var. fukienense` | 4 | coloured; bluish/light purple variation |
| `C. japonicum var. australe` | 3 | bluish-purple |
| `C. japonicum var. japonicum` | 2 | coloured reference |
| `C. brevicaule` | 3 | white |
| `C. irumtiense` | 3 | bluish-purple |
| `C. morii` | 2 | pink/coloured |
| `C. lineare` | 2 | coloured root reference |
| `C. tatakaense` | 2 | bluish-purple |
| `C. kawakamii` | 2 | white |
| `C. pengii` | 2 | bluish-purple |

The source-backed macro-topology, again without invented branch lengths, is stored in:

- `data/phylogeny/published_topology_fragments_v0_1.csv`

A simplified representation is:

```newick
(Cirsium_lineare,((Cirsium_japonicum_var_japonicum,((Cirsium_japonicum_var_albescens,Cirsium_japonicum_var_takaoense),(Cirsium_japonicum_var_australe,Cirsium_japonicum_var_fukienense))),((Cirsium_brevicaule,Cirsium_irumtiense),(Cirsium_morii,(Cirsium_pengii,(Cirsium_kawakamii,Cirsium_tatakaense))))));
```

## Critical sample-level limitation in var. takaoense

The supplement verifies six transcriptome accessions from Fenchihu, Tengji, Nanheng, Wutai, Fengbin and Ludao. However, neither Supplementary Table S1 nor the remaining supplementary tables identify whether each accession had a white or bluish-purple corolla.

Consequences:

- the published transcriptome tree cannot currently be converted into a morph-specific population tree;
- splitting `takaoense` into a white and a coloured tip remains a sensitivity scenario, not a direct recoding of named published accessions;
- voucher photographs, direct author confirmation, or new matched colour–DNA sampling is needed before these six accessions can test regain versus parallel loss.

## Audit of the anthocyanin-expression and pollinator-preference statements

The abstract and final conclusion of Chang et al. 2026 contain a statement linking var. `takaoense` flower-colour polymorphism to anthocyanin expression and pollinator preference. In the accessible article:

- no anthocyanin-expression method was located;
- no anthocyanin-expression result or table was located;
- no pollinator observation or preference-experiment method was located;
- no pollinator result or table was located.

The recovered official supplement likewise contains zero occurrences of:

- `anthocyanin`;
- `expression`;
- `pollinator`;
- `preference`.

The supplement instead contains genome-size, coalescent, SDM, morphology, taxonomy, voucher and specimen material.

The evidence classification is therefore:

> the paper supports taxon-level white/bluish-purple polymorphism and a reticulate phylogenetic context, but the accessible article and official supplement do not supply the experimental method or result needed to treat the molecular mechanism or pollinator preference as established by this paper.

This does not prove that no separate experiment or dataset exists. It means that a separately identifiable primary source must be found before the claim can be used as completed prior evidence.

The structured audit is stored in:

- `data/evidence/chang2026_flower_colour_claim_audit_2026-08-10.csv`

## Unified colour-history result from published topology fragments

The reproducible analysis is:

- `analysis/published_east_asia_colour_history.py`
- `analysis/published_east_asia_colour_history.csv`
- `tests/test_published_east_asia_colour_history.py`

### Nipponocirsium

With the Chang 2025 species topology and recovered colour states:

- Fitch root state: coloured;
- minimum changes: 1;
- coloured-root history: one `C -> W` loss on `C. kawakamii`;
- white-root history: three changes, including two coloured gains.

Thus `C. kawakamii` is a strong independent white-loss replicate under the published topology.

### Arenicola in its published sister-clade context

For `(brevicaule, irumtiense)` plus the sampled coloured-dominated Nipponocirsium sister clade:

- Fitch root state: coloured;
- minimum changes: 2;
- minimum coloured-root history: independent white losses in `C. brevicaule` and `C. kawakamii`;
- a regain in `C. irumtiense` is not required.

This revises the original motivating narrative: the current species-level evidence favours white loss in `C. brevicaule`, while `C. irumtiense` is better treated as coloured retention unless population history overturns that result.

### Full Chang 2026 context and takaoense coding

At taxon level, coding `takaoense` as ambiguous `{white, coloured}` yields three minimum changes.

When the two morph states are retained as separate sister tips inside a monophyletic `takaoense` sensitivity scenario:

- the root remains coloured;
- the minimum increases to four changes;
- two directional histories are equally parsimonious:
  - four independent white losses and no regain;
  - three white losses and one coloured regain.

Therefore:

> coloured `takaoense` remains the strongest current regain candidate, but regain is not required by the published topology; parallel white losses remain equally parsimonious.

## Revised evidence-driven priority

1. **var. takaoense remains first priority**, but the immediate need is morph-linked sampling or morph identification of published vouchers—not another unlabelled species-level tree.
2. **C. kawakamii–C. tatakaense** is a strong replicated loss/mechanism comparison because topology, colour contrast and ploidy context are already available.
3. **C. brevicaule–C. irumtiense** should test repeated mechanism, gene flow and population history rather than assume a regain in `C. irumtiense`.
4. Exact Newick files and branch lengths remain required for formal Mk likelihoods and stochastic mapping; topology-only parsimony is retained as a transparent diagnostic.
5. Pigment chemistry, floral RNA and causal-region analysis remain genuinely novel and necessary because they are not supplied by the recovered Chang 2026 material.

## Provenance and reproducibility

The public-artifact recovery workflow now runs on pull requests and stores a 90-day versioned artifact containing:

- downloaded source files;
- SHA256 hashes and sizes;
- extracted document text;
- extracted supplementary tables;
- explicit failures/skips for inaccessible resources.

The successful recovery used GitHub Actions run `31375296195`; artifact digest:

`sha256:f7021f030390aa9a911ffc55dcd1a0b1cc956f8ae0fbea216ac682a674d975e2`

Publisher files themselves are not committed to the repository. Only source-derived metadata, audit tables, hashes and reproducible retrieval instructions are versioned.
