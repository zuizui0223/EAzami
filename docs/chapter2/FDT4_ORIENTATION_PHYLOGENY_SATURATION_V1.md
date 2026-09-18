# FDT4 orientation phylogeny saturation v1

Status: frozen public-data sensitivity result, 2026-08-29  
Source run: GitHub Actions `33245270887` (`fdt4-orientation-phylogeny-saturation-v1`)

## What this resolves

The previous Chapter 2 ecology analysis propagated the six AU-nonrejected optimized Comp1061 trees. That was necessary, but it was not a strong ecology-panel topology test: after pruning to the taxa that pass the current occurrence gate, all six accepted trees, and in fact all nine optimized candidate trees, induce the same topology.

The new saturation analysis therefore expands uncertainty across genuinely different public phylogenetic realizations rather than merely adding more optimized candidates.

## Layers exhausted

1. **All nine optimized candidate trees.** Six are AU-nonrejected and three are retained only as adversarial stress tests. On the current GBIF n=9 and TBN-expanded n=11 panels they collapse to one induced topology.
2. **1,000 newly regenerated concatenated UFBoot trees.** Raw IQ-TREE `.ufboot` output has no fitted branch lengths in this run, so this layer is topology-only. The ecology panel contains 14 unique induced topologies at n=9 and 21 at n=11. BIO1 is negative and BIO15 positive in 1,000/1,000 trees in every panel.
3. **All 153 public Comp1061 locus trees.** 149 contain each full ecology panel. The locus trees are highly diverse: 150 induced topologies occur for the n=9 signatures and 153 for n=11. Across the 149 complete-panel trees, equal-branch topology-only PGLS gives BIO1 negative and BIO15 positive in 149/149 for every panel.
4. **ASTRAL reconstructed from all 153 public locus trees.** Its topology-only direction is BIO1 negative and BIO15 positive for every current occurrence panel.
5. **Independent Chang et al. 2026 ASTRAL topology.** On the currently joined taxon overlap, direction again agrees: native-TBN BIO1 beta = -1.436 SD (P=0.0937) and BIO15 beta = +1.358 SD (P=0.0760). This is directionally concordant but remains a small independent panel and does not cross the frozen inference threshold.

## Discordance is real

The public locus set is not a collection of nearly identical trees. Across the 18 internal branches of the full20 Comp1061 scaffold, gCF has median 7.545% (range 0.65–40.79%) and sCF median 46.92% (range 33.34–89.51%). The invariant equal-branch ecological direction therefore persists despite strong gene-tree discordance.

## What changes scientifically

The correct statement is no longer “the result is stable across six alternative topologies.” Those six alternatives do not differ on the ecology panel. The stronger and more accurate statement is:

> The BIO1-negative and BIO15-positive orientation direction persists across 1,000 concatenated bootstrap topologies, 149 complete-panel public locus-tree topologies, an ASTRAL species tree reconstructed from all 153 public loci, and the overlapping portion of an independently published 2026 ASTRAL phylogeny.

This makes **topology uncertainty a low-priority remaining explanation for the sign of the current orientation-climate correspondence**.

## What is not resolved

Using each single-locus fitted branch-length geometry as a species-level Brownian covariance lowers expected-sign rates to about 77–85%. This is not interpreted as 15–23% biological counterevidence. Short single-locus branch lengths are noisy substitutes for a species-level evolutionary distance, so this layer is retained only as a covariance-geometry stress test.

The remaining limits are therefore, in order:

1. taxon and occurrence coverage, especially Taiwan/East-Asian resolved orientation taxa;
2. the species-level branch-length / covariance model rather than topology;
3. same-individual phenotype-genotype linkage and within-species population structure;
4. historical niche, causal mechanism and fitness evidence.

The frozen Chapter 2 ecological classification remains unchanged by tree counting alone. Direction stability does not establish adaptation, historical niche causation, convergence or fitness effects.

Machine-readable summary: `data/evidence/fdt4_orientation_phylogeny_saturation_summary_v1.json`.
