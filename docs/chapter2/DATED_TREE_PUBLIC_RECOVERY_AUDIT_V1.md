# Chapter 2 dated-tree public recovery audit v1

Status date: 2026-08-30

## Decision

The next space–time cause test is correctly defined but cannot yet be executed as an exact calendar-time analysis. The public audit recovered:

- the published Moreyra et al. divergence-time method and its three calibration constraints;
- broad node-age context for the dominant Japanese radiation and the two secondary Japanese arrivals;
- all named raw-read and sample/voucher resources;
- the author’s small public HybPiper-QC repository;
- an EAzami registry spanning the public Moreyra and Chang sequence panels;
- a suitable 5-Myr palaeoclimate time series for the later event-window test.

It did **not** recover a machine-readable Moreyra concatenated ML tree, RelTime chronogram, MEGA dating session, calibration-node file, node-age table or BioGeoBEARS node-state export.

Current status:

> **PUBLIC_DATED_TREE_NOT_RECOVERED_IN_AUDIT**

Consequently, orientation × hydric regime remains at explanatory tier T2. It is not promoted to T3 historical-environment alignment.

The machine audit is:

- `../../data/evidence/chapter2_dated_tree_public_recovery_audit_v1.csv`

The exact author-data request and independent-rebuild fallback are:

- `../../data/evidence/chapter2_dated_tree_request_manifest_v1.json`

## 1. What the publication actually used

Moreyra et al. (2025) estimated divergence times with **RelTime in MEGA X**, using the best maximum-likelihood tree from their 350-locus concatenated analysis. This is not a posterior tree sample from a Bayesian relaxed-clock analysis.

The paper specifies three constraints:

1. **CP1:** mean root age 17.7 Ma under a normal distribution with a soft lower bound at 14 Ma;
2. **CP2:** minimum age 14 Ma based on a fossil cirsioid achene;
3. **CP3:** maximum age 5.6 Ma for the most recent common ancestor of the sampled *Cirsium latifolium* populations, based on the geological age of Madeira.

Exact CP2 and CP3 descendant-tip definitions require Figure S3 or, preferably, the original MEGA/calibration export. A prose description is insufficient for a reproducible node constraint on a reconstructed tree.

This audit therefore rejects any substitute calibration scheme that is not the one stated in section 2.5. In particular, no unverified calibration values may be imported from memory or another Cardueae analysis.

## 2. Calendar context recovered from the article

The dated publication provides three relevant Japanese calendar contexts.

| Lineage context | Published mean | Published 95% interval | Proper role here |
| --- | ---: | ---: | --- |
| Dominant Japanese radiation, node 13 jump dispersal to Japan | 2.4 Ma | 1.7–3.6 Ma | broad Pleistocene crown/dispersal context for most Japan38 taxa |
| Separate arrival producing *C. dipsacolepis* | ~1.0 Ma | 0.4–2.2 Ma | secondary-history comparator |
| Ancestor of *C. lineare* expanding from East Asia to Japan | ~1.4 Ma | 0.7–2.7 Ma | separate-history comparator outside the dominant radiation |

These values do not date a capitulum transition. They date lineage or dispersal contexts reported by the publication. A minimum orientation change on an internal or terminal Japan38 edge may occur anywhere between its dated parent and child nodes, and the exact parent/child ages are not available from the three article-level summaries.

The main radiation age also cannot be multiplied by relative lineage-depth. Relative lineage-depth is a descendant-tip topology coordinate rather than elapsed time, and rapid-radiation internodes are not expected to be proportional to descendant-tip count.

## 3. What is publicly deposited

### Formal article data statement

The article names:

- NCBI SRA BioProject **PRJNA957074** for raw sequence reads;
- Supplementary Table S1 for BioSample accessions, voucher information and herbarium codes.

The formal data statement does not name a repository entry for the 350-locus supermatrix, concatenated ML tree, gene trees, RelTime output, MEGA session, calibration file or BioGeoBEARS fitted object.

### Article supplement

The article landing page exposes one approximately 10-MB Word supplement containing supplementary figures and tables, including Figure S3. No separate Newick, Nexus, MEGA, CSV node-age or RData asset was identified in the public landing-page inventory.

An embedded image is not accepted as the primary chronological input. Digitizing Figure 3 or Figure S3 would introduce node-identity, branch-length and uncertainty errors and would not recover the exact RelTime output.

### Author GitHub repository

The public repository `ldmoreyra/A-thorny-tale` contains three HybPiper QC summaries:

- `hybpiper_stats_exonerate.tsv`;
- `paralog_report.xlsx`;
- `seq_lengths_exonerate.tsv`.

The audit did not find a concatenated alignment, best ML tree, dated tree, gene-tree bundle, calibration configuration or biogeographic result object there.

### Research portal

The independent FRIS research-portal record exposes an accepted manuscript and links the dataset record to NCBI. It does not list a dated-tree data package.

## 4. What EAzami can reconstruct independently

EAzami already has a public accession panel covering:

- 294 biological samples;
- 295 run accessions;
- 270 source-preserving taxon labels;
- 256 Moreyra samples;
- 38 Chang samples;
- 38 mapped Japanese concepts.

The Moreyra SRA audit has public read pairing for all 256 admitted Moreyra samples. This makes an independent global reconstruction technically possible.

It does **not** make it trivial or automatically equivalent to the published tree. The paper did more than download Compositae1061 reads. It manually inspected ortholog/paralog gene-tree placement, discarded problematic genes, retained loci with less than 50% missing data and at least 80% species presence, recovered introns/flanking regions, and built a final 350-alignment supermatrix. Reproducing that adjudication from raw reads is a heavy analysis and may not yield the identical locus set without the author’s selected alignments and tree files.

The current Japan38 scaffold cannot substitute for this reconstruction. It uses 236 QC loci, of which 176 are rootable with the safflower outgroup; its branch lengths are substitutions per site. It is excellent for the exact trait crosswalk, minimum-change analysis and topology uncertainty, but it is not the 350-locus global RelTime input.

## 5. Independent East-Asian dated context from Chang et al. (2026)

A separate 2026 phylotranscriptomic analysis supplies an important local temporal sensitivity. Chang et al. inferred a StarBEAST3 time tree from 50 orthologous genes and reported posterior node-age intervals for the *C. japonicum* complex, subsection Arenicola and subsection Nipponocirsium.

Relevant reported ages include:

- Sinocirsium versus the other two subsections: 1.30 Ma, 95% HPD 1.04–1.62;
- Nipponocirsium versus Arenicola: 1.02 Ma, 0.71–1.33;
- *C. brevicaule* versus *C. irumtiense*: ~0.93 Ma, 0.71–1.33;
- Japanese *C. japonicum* var. *japonicum* versus the Taiwanese clade: ~0.44 Ma, 0.31–0.66;
- shallow Taiwanese divergences: approximately 0.08–0.44 Ma.

This study is useful because it supplies an independently inferred East-Asian calendar scale and includes several taxa in the orientation/climate comparison. It is not a substitute for the full Japan38 tree because it covers a different, local taxon panel and uses a different molecular dataset and clock model.

Its public data statement currently names raw reads under BioProject PRJNA1311153 and one DOCX supplement, rather than a machine-readable posterior tree bundle. Therefore it can presently constrain local lineage-divergence context, but it cannot yet identify a trait-transition date without an exact sample–state crosswalk and posterior/tree recovery.

The article’s visual correspondence between lineage divergences and named glacial stages must also not be reworded as evidence that a particular orientation or colour transition was caused by a glaciation. Lineage splitting and trait change are separate events until mapped jointly.

## 6. Palaeoclimate input is ready after the chronology gate

PALEO-PGEM-Series provides the correct temporal form for the first abiotic event-window analysis:

- global coverage over the last 5 Myr;
- 1-kyr temporal resolution;
- 1° × 1° spatial cells;
- monthly temperature and precipitation;
- 17 derived bioclimatic variables, including BIO1, BIO12 and BIO15;
- means and uncertainty estimates across emulator runs.

This aligns with the predeclared orientation test:

- Azami spatial axis: annual precipitation amount, BIO12;
- EAzami present-niche axis: precipitation seasonality, BIO15;
- secondary scale-dependent axis: annual mean temperature, BIO1.

The climate files alone are not sufficient. An event window requires a dated parent and child, and climate extraction requires a predeclared paleolocation distribution rather than one modern descendant coordinate.

## 7. Recovery order

### Route A — author-source bundle, preferred

The minimum acceptable bundle is:

1. best concatenated ML tree used by RelTime;
2. RelTime dated tree;
3. node-age confidence table;
4. CP1–CP3 calibration configuration with exact descendant-tip sets;
5. paper sample ↔ BioSample/SRA ↔ voucher crosswalk.

Strongly preferred additions are the 350-locus supermatrix, partitions, post-orthology alignments, gene trees and BioGeoBEARS node-state outputs.

This route preserves the publication’s actual topology, manual orthology decisions and RelTime setup.

### Route B — independent global rebuild, fallback

If Route A remains unavailable, the fallback is a versioned heavy-analysis lane:

1. freeze sample/duplicate admissions against Table S1;
2. recover Compositae1061 targets from the public SRA panel;
3. explicitly reproduce or replace the manual orthology/paralogy decisions;
4. audit whether the published 350-locus final set can be recovered;
5. infer the concatenated ML tree;
6. apply the published CP1–CP3 RelTime constraints with exact nodes;
7. validate the published Cirsium crown and Japanese temporal landmarks;
8. map exact Japan38 descendant sets to the dated tree;
9. recover or reconstruct ancestral-area uncertainty;
10. execute the frozen PALEO-PGEM event-window test.

This lane is not routine pull-request CI. It requires large SRA recovery and phylogenomic inference. Its result is an independent reconstruction unless it passes an explicit exact-reproduction standard.

### Route C — Chang local dated sensitivity

For the East-Asian subset, recover the Chang posterior/maximum-clade-credibility tree or independently rebuild its 50-OG StarBEAST3 analysis from PRJNA1311153. Map exact orientation and colour observations to sampled accessions. Use it as an independent local time sensitivity, not as a replacement for the dominant Japan38 radiation history.

## 8. Validation landmarks for an independent rebuild

Before a reconstructed dated tree enters the trait-event analysis, it must recover a compatible temporal scale. At minimum, the following publication landmarks must be audited rather than silently assumed:

- Cirsium crown approximately 9.5 Ma, 95% CI 7.2–12.2;
- main Japanese radiation approximately 2.4 Ma, 1.7–3.6;
- *C. dipsacolepis* arrival approximately 1.0 Ma, 0.4–2.2;
- *C. lineare* ancestor expansion approximately 1.4 Ma, 0.7–2.7.

Failure to reproduce one value does not automatically invalidate an independently processed tree, but the difference must be attributed to topology, taxon admission, orthology, calibration placement or dating implementation before the tree is used to claim event-level environmental alignment.

## 9. What becomes possible when the gate passes

For each admissible orientation transition edge:

1. obtain a parent–child age interval rather than a midpoint date;
2. propagate alternative minimum histories and topology uncertainty;
3. propagate dated-tree uncertainty;
4. propagate alternative paleolocation scenarios;
5. extract BIO12, BIO15 and BIO1 time series with emulator uncertainty;
6. calculate climate level, net change, absolute change, variability and extremes inside the interval;
7. compare with matched non-transition windows preserving duration and branch opportunity.

A positive result would mean:

> repeated orientation-event windows align with the predeclared paleohydric regime more than expected under matched historical opportunity.

That would move orientation × hydric regime from T2 to T3. It would still not demonstrate rain adaptation. Mechanism and reproductive fitness remain T4 and T5.

## 10. Stop rules retained

- Do not transform relative lineage-depth into Ma.
- Do not place every dominant-radiation transition at 2.4 Ma.
- Do not infer an internal node date by digitizing a published tree figure as the primary chronology.
- Do not substitute present descendant niches for ancestral environments.
- Do not assign an ancestral branch to one modern coordinate.
- Do not use the local Chang tree as if it covered the complete Japan38 radiation.
- Do not describe lineage divergence during a glacial period as a demonstrated trait response to glaciation.
- Do not promote orientation × hydric regime beyond T2 until both dated-event and paleolocation gates pass.

## Current conclusion

The temporal analysis is no longer conceptually vague. We know exactly what can already be said and what remains missing:

- orientation changed at least four to six times, but the event ages are not recovered;
- most focal Japanese history falls within a Pleistocene radiation whose broad origin is approximately 2.4 Ma;
- independent East-Asian work places several relevant lineage divergences between approximately 1.30 and 0.08 Ma;
- PALEO-PGEM can quantify hydric and thermal level, change and variability through those calendar windows;
- the machine-readable dated trees, exact node crosswalks and ancestral-location uncertainty needed for trait-event alignment have not yet been recovered.

Therefore the current strongest cause statement remains:

> **Hydric exposure is the leading cause candidate for repeated orientation evolution because spatial BIO12 sorting, repeated orientation history and present BIO15 correspondence agree independently. Exact historical-environment alignment is the next decisive public-data layer, not an assumption already supplied by the broad 2.4-Ma radiation age.**
