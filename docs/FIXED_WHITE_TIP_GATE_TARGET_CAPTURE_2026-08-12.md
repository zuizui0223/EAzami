# Fixed-white tip gate — minimal target-capture execution design

Original design date: 2026-08-12  
Current execution status: 2026-08-23

## Current status — 2026-08-23

The tree side of this gate is no longer pending. The current 20 eligible taxa have an accepted empirical Compositae1061-compatible branch-length tree built from the **frozen 153-locus set** (`data/evidence/full20_comp1061_saff_root_153_loci_v1.txt`, SHA256 `1106051eca8bfa699f16e05d92024573cb358d7dbd151b89768e76c3d56cde82`). Alignment QC is 153/153 loci, the concatenated alignment is 140,562 bp, and local topology uncertainty has been quantified with deterministic gCF/sCF plus a preregistered 3x3 AU test.

For the **current exact 20-taxon atlas**, the combined rate-fit gate is therefore blocked only by `minimum_white_tips`: C=17, W=3, while the engineering threshold is W>=5. The accepted 20-taxon tree cannot be reused unchanged after adding new rate-fit taxa; the combined gate now explicitly fails with `tree_taxon_join_mismatch` until a rebuilt tree contains exactly the expanded atlas taxa.

The active promotion contract is `data/evidence/fixed_white_tree_promotion_contract_v0_2.json`. It supersedes v0.1 for execution while retaining v0.1 as a historical snapshot.

The current A1 promotion rules are fixed before new data are observed:

- exactly two A1 taxa: *Cirsium boninense* and *Cirsium wulongense*;
- >=2 passing independent voucher/flower-colour-linked individuals per taxon; ideal 3;
- original public Compositae1061 reference, HybPiper 2.3.4, BWA, DNA;
- **no reselection of loci after seeing the new white taxa**;
- each new individual must cleanly recover at least `ceil(0.8 x 153) = 123` frozen loci;
- a new-sample paralog warning masks only that individual at that locus; it does not delete the locus from the frozen matrix;
- replicates must form a concordant species-level clade across the declared topology-sensitivity procedure before one representative can be selected;
- representative selection is QC-only: clean recovered locus count, then non-gap aligned bases, then stable sample ID;
- after both A1 species pass, rebuild the matrix on the **same 153 loci** and infer/reaccept a **22 focal species + OUTGROUP_saff = 23-tip** tree;
- rerun structural alignment QC, branch-length acceptance and topology sensitivity on that expanded tree before any rate fit.

## Why this panel exists

Flower-colour atlas v0.3 is designed so that the conservative engineering gate for later cross-species transition-rate modelling is blocked by the number of fixed-white nuclear tips. The current state is 20 eligible taxa with C=17 and W=3. Therefore two additional credible fixed-white species-tree tips would clear the numerical W>=5 atlas gate.

That numerical gate is only a project stop-rule. It is not a statistical theorem and does not make an ARD/Mk model automatically identifiable or adequate. It also does not by itself unlock rate fitting: the expanded atlas and expanded branch-length tree must contain exactly the same accepted taxa.

## A1 minimal pair

### Cirsium boninense — Ogasawara

The National Museum of Nature and Science Cirsium database explicitly describes white florets and states that the flowers are always white. A separate Ogasawara pollination-system study also codes the species as white-flowered.

A 2025 genetic study is now publicly confirmed to have used **MIG-seq** in a five-taxon comparison including *C. boninense*, *C. irumtiense*, *C. brevicaule*, *C. spinosum* and *C. maritimum*. However, reusable sample/voucher details, raw/genotype data and a Compositae1061-compatible species-tree tip have not been recovered. The MIG-seq summary therefore remains identity/origin context rather than a rate-tree tip.

Target:

- preferred bait set: Compositae1061, to maximize direct overlap with the frozen EAzami branch-length matrix;
- minimum 2 independent voucher-linked individuals; ideal 3;
- fresh material only with the necessary legal access/permits; herbarium DNA is an acceptable alternative if identity is secure;
- retain a voucher or unambiguous herbarium identifier, locality, collection metadata and flower-colour documentation for every DNA sample;
- do not confuse web/GenBank hits for the fungal genus/species complex *Colletotrichum boninense* with the plant *Cirsium boninense*.

### Cirsium wulongense — Chongqing

The 2024 primary taxonomic description diagnoses a white corolla. It is compared morphologically with coloured *C. fanjingshanense*, which already has an exact Moreyra nuclear tip, but that comparison must not be converted into an assumed sister relationship. No exact homologous public nuclear asset has been recovered.

Target:

- preferred bait set: Compositae1061;
- minimum 2 independent voucher-linked individuals; ideal 3;
- samples must match the published Wulong/Xiannü Shan taxonomic concept;
- retain flower-colour phenotype with the DNA sample;
- use *C. fanjingshanense* only as an existing regional coloured comparator until the nuclear tree establishes actual relationships.

If both A1 taxa pass the frozen promotion contract, the atlas white-tip count moves from W=3 to W=5, but the final 22-focal-taxon tree must then be rebuilt and reaccepted before rate fitting.

## A2 backups

- *C. hupingshanicum*: strong primary white-corolla description; no exact modern nuclear tip recovered.
- *C. sichuanense*: later primary comparisons support white corolla, but direct wording from the original description must be frozen before promotion.
- true *C. henryi*: revised concept is fixed-white and restricted to western Hubei, but the Moreyra sample labelled *C. henryi* is a Yunnan Hengduan Mountain Expedition 2464 voucher that the revision assigns to purple-flowered *C. forrestii*. The existing Moreyra label must never be counted as a white tip.

## Why two individuals rather than one

One target-capture library can place a voucher, but one mislabeled, contaminated or hybrid individual can also create a false macroevolutionary transition. This panel therefore requires at least two independent individuals per fixed-white candidate before promotion to a new species-level rate-fit tip. Discordant placements are a stop condition, not a reason to choose the sample that produces the preferred colour history.

## Required sample linkage

Every new individual must retain, where feasible:

- accepted/current taxon concept and source name;
- voucher/herbarium identifier;
- standardized flower photograph or direct flower-colour record;
- locality and coordinates;
- collection date;
- tissue/DNA identifier;
- permit/accession provenance where required;
- ploidy/cytotype measurement or at least material retained for later verification;
- raw sequencing accession after deposition.

## Placement and promotion rule

A candidate is not promoted because a capture library exists. Promotion requires:

1. at least two passing concordant voucher/phenotype-linked individuals;
2. at least 123/153 clean recovered frozen loci per passing individual;
3. no unresolved taxonomic, contamination or sample-identity conflict;
4. fixed-white phenotype supported independently of the inferred tree;
5. a replicate-expanded placement tree in which the required individuals form one species-level clade across the declared topology-sensitivity procedure;
6. deterministic QC-only representative selection after the replicate gate;
7. rebuilding and reaccepting the final exact-tip 22-species branch-length tree on the same frozen 153-locus universe.

Multiple individuals of one species are never counted as multiple macroevolutionary white tips.

## What happens after W>=5

Passing W>=5 clears the current atlas breadth gate only. Before a rate model may run, the final 22-taxon atlas and rebuilt 22-focal-taxon tree must match exactly and the expanded tree must pass its own structural/topology acceptance gates.

The later rate analysis must still account for:

- topology and branch-length uncertainty;
- non-random taxon sampling and deliberate enrichment for white taxa;
- polymorphic taxa such as *C. pendulum*, *C. sieboldii*, *C. aomorense*, *C. amplexifolium* and var. *takaoense*;
- hidden rate heterogeneity/model adequacy;
- uncertainty in inferred transition counts/rates.

The resulting transition-rate distribution can then be fed back into the Arenicola loss-versus-regain sensitivity. It must not be interpreted as proof of molecular anthocyanin reactivation.
