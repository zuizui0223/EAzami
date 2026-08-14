# Sequencing panel v0.3: decisions after exact Moreyra–Chang coverage integration

Date: 2026-08-10  
Updated: 2026-08-11 after direct recovery of all six var. *takaoense* W/BP labels

## Decision rule

The East Asian design distinguishes:

1. genuine species-level nuclear gaps;
2. species already placed but lacking population or morph history;
3. published samples whose provenance or phenotype metadata must be recovered;
4. historical white-form names whose extant natural populations remain unverified.

The central rule is:

> use target capture only for a genuine transition-critical species gap; use RAD-seq or resequencing to resolve morph/population history after species placement is known; recover missing metadata before generating redundant sequences.

The integrated screen currently covers 33 master-table taxa. No active Tier-A focal taxon remains a species-placement gap.

Files:

- `analysis/build_east_asia_nuclear_coverage.py`
- `sampling/SEQUENCING_PANEL_V0_3_EXACT_COVERAGE.csv`

## Stage 0 — completed for var. takaoense

### Accession identity

All six published transcriptome vouchers map one-to-one to official PRJNA1311153 runs and BioSamples.

| Code | Voucher | Run | BioSample | Figure 1 morph |
|---|---|---|---|---|
| FC | `ccy3559` | `SRR35152718` | `SAMN50798021` | BP |
| WY | `ccy3560` | `SRR35152717` | `SAMN50798022` | W |
| FB | `ccy3629` | `SRR35152738` | `SAMN50798024` | W |
| TJ | `ccy3807` | `SRR35152736` | `SAMN50798026` | BP |
| NH | `ccy3835` | `SRR35152735` | `SAMN50798027` | BP |
| LT | `ccy3839` | `SRR35152734` | `SAMN50798028` | W |

NCBI `SampleName` and BioSample `isolate` independently preserve the collector numbers. NCBI itself contains no colour attribute.

### Direct morph evidence

The official Figure 1 PNG was recovered and frozen by hash. Panels B and C print the same six labels:

- BP: FC-3559, TJ-3807, NH-3835;
- W: WY-3560, FB-3629, LT-3839.

Thus the published transcriptome sample contains both morphs in equal numbers.

The displayed ASTRAL sample topology and Neighbor-Net both show morph-associated structure. The three BP samples group together, while the three W samples occupy the other side or successive outside branches. This makes a one-transition model within the sampled variety plausible under some root-state assumptions, but it does not establish direction, causal restoration or absence of introgression.

### Remaining non-sequencing gaps

- exact machine-readable tree and branch lengths;
- Neighbor-Net distance/network file;
- orthogroup/gene-tree inputs;
- S1 TCF versus S6 TNM herbarium conflict for `ccy3839`.

These are secondary to the now-complete W/BP mapping.

Files:

- `docs/CHANG2026_TAKAOENSE_MORPH_EVIDENCE_AUDIT_2026-08-11.md`
- `docs/requests/CHANG2026_TAKAOENSE_MORPH_REQUEST_DRAFT.md`
- `data/evidence/chang2026_takaoense_figure1_morph_assignments_2026-08-11.csv`
- `data/evidence/chang2026_takaoense_voucher_morph_evidence_2026-08-10.csv`
- `data/evidence/chang2026_takaoense_ncbi_voucher_morph_audit_2026-08-11.csv`

## Stage 1 — population genomic core

### 1. var. takaoense

The existing data now support an immediate sample-topology reanalysis before new sequencing.

Use the six labelled transcriptomes to:

1. test whether BP monophyly and W paraphyly persist across available tree methods;
2. quantify support and gene-tree discordance at the W/BP boundary;
3. compare the sample tree with Neighbor-Net reticulation;
4. include white var. *albescens* and coloured var. *fukienense*, var. *australe* and var. *japonicum* as root/state context.

These six individuals remain one plant per locality. They cannot distinguish morph ancestry from geography, population structure or reticulation. New population genomics should therefore sample:

- 20–30 white and 20–30 bluish-purple plants;
- at least two populations per state;
- mixed populations where they exist;
- nearby paired populations when mixed populations are absent;
- flow-cytometrically verified cytotypes;
- matched flower reflectance, pigment chemistry, floral RNA and leaf DNA.

Competing models:

- parallel white losses;
- a shared white origin followed by derived BP restoration;
- ancestral W/BP polymorphism;
- introgression of a coloured haplotype;
- geography-associated structure unrelated to causal colour loci.

### 2. C. pendulum

The exact Moreyra sample is from Trans-Baikal and supplies a continental nuclear anchor. It does not replace Japanese white populations, nearby Japanese purple controls or Korea–Northeast China–Primorye bridges.

Use population RAD-seq or resequencing, not another species-placement sample.

### 3. C. sieboldii

The Moreyra tip is exact at the submitted-name level but was cultivated at the Botanical Garden of Barcelona, with wild provenance unresolved. Sample Japanese white/purple populations and Zhejiang explicitly.

### 4. C. kawakamii–C. tatakaense

Both species are 2n=64 and represented in two modern phylotranscriptomic studies. Use ploidy-aware local ancestry plus matched floral expression and pigment data to distinguish independent regulatory loss, homeolog sorting and introgression.

### 5. C. brevicaule–C. irumtiense

The existing sister context favours white loss in `C. brevicaule`, not regain in `C. irumtiense`. New population data should test gene flow, ancestral polymorphism and whether the white mechanism is homologous to independent white lineages.

## Stage 2 — conditional Korean and Northeast Asian systems

Historical white-form names are candidate-discovery evidence, not proof of extant polymorphism.

### C. vlassovianum

Species-level nuclear evidence exists from Sikhote-Alin and Mongolia. If white populations are verified, proceed directly to geographically stratified population genomics after resolving the `C. coryletorum` relationship.

### C. setidens and C. rhinoceros

These remain candidate species-level gaps, but not active sequencing priorities until extant natural white material is confirmed. If confirmed and no other modern nuclear dataset is found:

1. obtain Compositae1061 placement;
2. then sample W/coloured populations densely.

### C. schantarense

An older ITS placement exists, but no exact modern Moreyra/Chang tip was recovered. Verify white records and taxonomy before target capture or regional population genomics.

## Stage 3 — broader colour and backbone candidates

### C. taiwanense

The yellow 2n=32 lineage becomes relevant only if Chapter 2 expands from white/anthocyanin loss to broader pigment-pathway evolution.

### Chinese coloured taxa and other Taiwan gaps

`C. shansiense`, `C. leducii`, `C. ferum`, `C. suzukii`, `C. hosokawae` and the `C. arisanense` forms should not be sequenced merely because an exact integrated-source tip is absent. First establish accepted-name status, direct colour evidence and whether placement changes a transition inference.

## Modality decision rule

| Evidence state | Next data or action |
|---|---|
| accession and morph identity resolved; sample topology available | reuse existing reads and test topology before sequencing |
| species placement verified; population history missing | RAD-seq or resequencing |
| species placement verified; colour mechanism missing | pigment chemistry + floral RNA + candidate-region analysis |
| extant white morph unverified | voucher/field verification before sequencing |
| transition-critical modern nuclear tip genuinely absent | Compositae1061 target capture |
| mixed or uncertain cytotypes | flow cytometry/chromosomes before genotype calling |
| plastome only | retain maternal history; obtain nuclear placement only when transition-informative |

## Implication for Chapter 2

The project is no longer an attempt to construct one East Asian RAD tree. The working architecture is:

1. reuse existing Compositae1061 and phylotranscriptomic species backbones;
2. recover accession and phenotype metadata before generating new data;
3. close only verified transition-critical species gaps with compatible target capture;
4. use labelled existing samples as anchors;
5. use dense population genomics to identify W/BP ancestry and gene flow;
6. use pigment chemistry and floral expression to identify the molecular switch;
7. claim regain only after ancestral standing variation, geography and introgression are disfavoured.

This design spends new sequencing on unresolved biological history rather than rediscovering known sample identities.
