# Micro → macro hypothesis program v3 — molecular resolution ladder

## What v3 adds

v3 does **not** create another hypothesis simply because a new analysis was run. It adds a new EAzami-discovered problem, P7, that tests and sharpens existing HMM1 and HMM5.

The central result is a resolution ladder:

```text
published targeted pathway panel
        ↓
functional labels in distributed genome files
        ↓
sequence-level family/homology recovery
        ↓
domain + clade + reciprocal orthology validation
        ↓
W/C lineage comparison
        ↓
causal genotype → expression → pigment → phenotype
```

These levels are not interchangeable.

## Literature conclusion

Published *C. japonicum* molecular studies already establish extensive flavonoid/phenylpropanoid machinery and strong organ-specific expression. Park et al. 2020 reports a named 29-ortholog pathway panel and flower-biased expression reaching 2.6–500× for assayed flavonoid genes. Roy et al. 2018 provides an independent 51,133-unigene transcriptome and directly annotated upstream/core flavonoid genes.

These are `published_conclusion`, not EAzami discoveries.

## EAzami result 1 — targeted-panel resolution

The predeclared 17-family bridge found:

- entry + core + branch: **9/9** directly represented in at least one source;
- anthocyanin + regulatory + transport: **1/8** (`DFR` only);
- terminal anthocyanin + MBW + transport: **0/7** in the named targeted panels.

This does not imply genomic absence.

## EAzami result 2 — distributed genome annotation resolution

Using the frozen natural-Ulleung *C. nipponicum* genome files:

- protein headers scanned: **31,263**;
- GFF3 records scanned: **554,761**;
- functional text hits: **0** for all searched families, including positive-control `CHS`, `FLS`, and `DFR`.

The protein/GFF distributions expose structural IDs/coordinates such as `Cn_g...`, not functional product names. Therefore annotation-text failure is an **annotation-linkage limitation**, not evidence that pathway genes are missing.

## EAzami result 3 — sequence homology resolution

Reviewed UniProt anchors were materialized for 11 queries and searched against the same MD5-frozen *C. nipponicum* proteome.

All **11/11** queries returned candidate homologs under the frozen BLASTP screen.

Particularly informative candidates:

- `DFR_TT3` → `Cn_g13756.t1`, 71.118% identity, query coverage 0.843, one candidate within 80% of top bitscore;
- `ANS_TT18` → `Cn_g8152.t1`, 74.636% identity, query coverage 0.963, one candidate within 80% of top bitscore;
- `FLS1` → `Cn_g15577.t1`, 67.066%, query coverage 0.994;
- `TTG1` anchor → `Cn_g24396.t1`, 77.616%, nearly full-length similarity.

Other families remain more ambiguous:

- CHS: four candidates within 80% of top bitscore;
- UGT75C1-like: two;
- MYB75-like: four;
- MATE/TT12-like: six;
- TT8-like hit covers only ~38% of the Arabidopsis query and requires domain/clade validation.

A BLAST top hit is a homology candidate, not one-to-one orthology or function.

## P7 — annotation-to-orthology resolution ladder

> **The apparent molecular gap changes depending on evidence resolution. Absence from a targeted pathway table, absence of functional labels in a distributed genome file, absence of a sequence homolog, absence of an ortholog, and functional pathway loss are different observations.**

EAzami now directly demonstrates the first three levels:

1. named targeted panels leave terminal/regulatory/transport poorly covered;
2. distributed *C. nipponicum* protein/GFF files contain no useful functional-name layer;
3. sequence homology recovers candidates for 11/11 reviewed anchors from those same unlabeled proteins.

Therefore downstream macroevolutionary analyses must not turn annotation/reporting missingness into evolutionary loss.

## HMM1 status after v3

**Status:** mechanistic plausibility strengthened; direct white-lineage test unresolved.

What changed:

- upstream/core pathway presence was already published;
- DFR/ANS and terminal/regulatory/transport candidate families can now be recovered from a public *Cirsium* genome sequence;
- hence retained machinery is empirically testable without first generating a new reference genome.

What remains unresolved:

- whether independently white lineages retain intact functional orthologs;
- whether white/coloured differences are regulatory, coding, structural, or introgressed;
- whether any candidate actually causes the phenotype.

The next falsification gate is orthology/domain validation followed by W/C-lineage structural/coding/expression comparison.

## HMM2 status after staged test

**Partial support only.**

- state compression: 4/4 reviewed polymorphic systems;
- transition-count sensitivity: 1/1 currently morph-linked system, `1 → 2` minimum changes;
- replicated transition-rate comparison: 0/4 currently testable;
- morph↔genotype linkage: 1/4 systems.

The main bottleneck is therefore not just species-tree coverage but phenotype–sequence linkage.

## HMM5 status after v3

The molecular hierarchy is now executable, but cross-lineage convergence remains unresolved.

Candidate genes/families can be compared at:

1. phenotype;
2. pathway;
3. module;
4. gene/clade;
5. nucleotide/structural variant.

The next test must compare **independent white systems**, not infer molecular convergence from the single *C. nipponicum* reference genome.

## Next existing-data execution

### Priority A — orthology/domain resolution

First validate:

- DFR `Cn_g13756.t1`;
- ANS/LDOX `Cn_g8152.t1`;
- FLS `Cn_g15577.t1`;
- CHS copy set around `Cn_g13733.t1`.

Then resolve the larger families:

- UGT75/UGT78-like;
- MYB75-like;
- TT8-like bHLH;
- TTG1-like WD40;
- GSTF12-like;
- TT12/MATE-like.

Use multiple plant references, preferably including Asteraceae where defensible, plus domain architecture and clade trees. Do not promote a single best BLAST hit to exact orthology.

### Priority B — project candidates onto W/C public data

After orthology validation, recover the validated candidates from:

- six morph-linked var. *takaoense* transcriptomes;
- white var. *albescens* controls;
- coloured Sinocirsium controls;
- Arenicola transcriptomes;
- other suitable public genomes/transcriptomes.

Separate:

- presence/copy number;
- coding divergence;
- gene genealogy;
- assay-specific expression.

### Priority C — macro bridge

Only after candidate identity is defensible, compare whether white-lineage changes converge at:

- exact nucleotide;
- gene;
- module;
- pathway.

This is the direct HMM5 test and the molecular half of HMM1.

## Claim boundary

v3 does not establish a functional anthocyanin pathway in every white lineage, nor a regain mechanism. It establishes that EAzami can recover sequence-level candidate homologs for terminal/regulatory/transport layers that were invisible at the publication-table and distributed-annotation-text levels. The scientific task has therefore moved from **“are these genes present?”** to **“which candidates are true orthologs, how are they structured across W/C lineages, and which molecular level actually tracks phenotype?”**
