# Orientation causal triangulation v2

Status date: 2026-09-04  
Role: **current causal boundary / mechanism prioritization for Chapter 2**

## Current answer

The present public-data programme does **not** identify precipitation seasonality, temperature, or another single climate axis as the historical cause of nodding/downward capitula in East-Asian *Cirsium*.

It does, however, now distinguish three levels:

1. **Present association is real enough to persist under coarse geography controls.**
2. **The association is not specific enough to isolate BIO15 as the causal axis.**
3. **A rain/wetting–reproductive-protection mechanism is experimentally real in another Asteraceae capitulum system, but the focal *Cirsium* mediator→fitness link is missing.**

## 1. What the EAzami data now establish

### Not a simple regional artefact

BIO15 remains positive after removing Taiwan and after explicit latitude/longitude adjustment:

- Japan-only D−U: **+1.057 to +1.103 SD**, 6/6 topology and 42/42 species-LOO positive;
- latitude/longitude-adjusted orientation coefficient: **+1.118 to +1.125 SD**, 6/6 topology and 54/54 species-LOO positive.

Therefore a simple `Taiwan vs Japan` or linear centroid-geography explanation is insufficient.

### But not a BIO15-specific causal axis

After simultaneously conditioning on BIO1 and geography:

- BIO15 orientation coefficient remains positive on 6/6 topology fits but only **48/54** species-LOO fits;
- adjusted BIO15 coefficient: **+0.744 to +0.778 SD**, P=0.336–0.356;
- adding orientation worsens held-out BIO15 prediction on **6/6** topologies (median ΔMSE −0.508);
- closest opposite-orientation taxon pairs give positive BIO15 D−U in only **2/4** full-panel pairs and **2/3** Japan-only pairs.

The reciprocal BIO1 coefficient remains negative in 54/54 species-LOO fits after BIO15 and geography adjustment, but also fails the inferential threshold and gives mixed nearest-pair contrasts.

The present ecological object is therefore better described as a **composite climatic/lineage regime** than as a unique BIO15 or BIO1 effect.

## 2. Direct experimental mechanism anchor in Asteraceae

The strongest directly relevant external experiment is *Cremanthodium campanulatum* (Asteraceae), another nodding capitulum system.

Natural nodding capitula were compared with capitula artificially held erect. The experiment found:

- achene set **56.3 ± 3.9%** in natural nodding heads versus **15.7 ± 3.6%** in artificial erect heads;
- ratio ≈ **3.59**;
- n=30; F=59.1; P<0.01;
- water exposure and UV-B reduced pollen viability;
- no detected pollinator preference between nodding and erect capitula.

The study therefore provides a direct capitulum-level pathway in which orientation can increase reproductive success without requiring a static pollinator-preference difference. Rain/wetting and radiation protection are biologically credible mediators.

DOI: `10.1080/17550874.2012.702793`.

This magnitude is **not** transferred to *Cirsium*.

## 3. Independent generality of an integrated orientation mechanism

A 2026 manipulation of downward *Polygonatum cyrtonema* flowers independently showed that orientation can simultaneously alter:

- effective pollinator visitation and pollen transfer;
- pollen viability and stigma receptivity under rainwater/sunlight exposure;
- seed and fruit performance.

DOI: `10.1002/ece3.73221`.

This system has a different family and floral architecture, so it supports only general mechanism plausibility, not homology or focal causation.

## 4. Mechanism discrimination after all current falsifications

| Candidate explanation | Current status | Why |
| --- | --- | --- |
| static pollinator preference only | **weakened** | large direct Asteraceae fitness effect can occur with pollinator-preference null; earlier EAzami mechanism reduction also failed this family |
| rain/wetting + UV/radiation protection | **strongest external functional prior** | direct Asteraceae orientation manipulation links the pathway to pollen viability and achene fitness; current *Cirsium* climate direction is compatible but not specific |
| thermal/time-window pollination | **plausible parallel pathway** | present cross-scale results and earlier mechanism reduction support time/scale dependence, but current data do not identify it historically |
| integrated abiotic + biotic function | **plausible** | independent manipulation systems show both pathways can coexist |
| BIO15 as unique cause | **not supported** | conditional specificity, held-out prediction and closest-pair tests fail to isolate it |
| one recurring historical climate trigger | **not identified** | only one dateable orientation event; full chronology × palaeolocation tests remain unresolved |

## 5. What is genuinely positive now

The positive causal advance is **not** “rain caused nodding *Cirsium*.”

It is narrower but useful:

> **The current *Cirsium* orientation–climate association is not a trivial coarse-geography artefact, and a mechanistically appropriate rain/wetting-protection pathway is experimentally demonstrated at the capitulum level in Asteraceae. However, the current *Cirsium* data do not isolate a single climatic axis or connect that axis through the mediator to fitness.**

This narrows the remaining mechanism space. Static pollinator preference alone and a one-variable direct-gradient story are poor explanations; abiotic reproductive protection remains a serious testable candidate.

## 6. Decisive missing link

The missing focal chain is:

```text
orientation
→ rain / wetting exposure
→ pollen retention / viability and stigma function
→ effective pollen transfer
→ viable achene set
```

measured in ancestry-matched *Cirsium*.

Until that chain is measured, Chapter 2 should present the mechanism as an experimentally grounded **candidate**, not a historical cause.

## Claim boundary

- *Cremanthodium* is an external Asteraceae mechanism anchor, not focal *Cirsium* evidence.
- Present BIO15/BIO1 values are not historical transition-time exposures.
- External effect sizes are not transferred to East-Asian *Cirsium*.
- Mechanism plausibility is not adaptation.
- Further correlated climate-variable screening is not expected to resolve the missing mediator→fitness chain.

## Machine-readable source

`data/evidence/chapter2_orientation_causal_triangulation_v2.json`
