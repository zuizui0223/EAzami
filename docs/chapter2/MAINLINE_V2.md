# Chapter 2 mainline v2 — phenotype → function → history → origin → convergence

Status: active source of truth for the Azami → EAzami scientific line.

## 1. One-way dependency

```text
Azami
phenotypic decomposition of the capitulum
        ↓
EAzami-I
candidate functional annotation and functional validation
        ↓
EAzami-II
trait-specific evolutionary histories
        ↓
EAzami-III
origin discrimination
        ↓
EAzami-IV
functional and adaptive convergence tests
```

The central dependency is biological, not merely computational. Azami defines the decomposed present phenotype. EAzami asks what those components do, how their states changed through time, whether repeated states are independent in origin, and only then whether repeated changes represent convergence.

## 2. Azami endpoint: decompose the present

Azami's endpoint is not a capitulum syndrome classification. The capitulum is represented by continuous or explicitly defined component traits including orientation, colour, outline/shape, involucre architecture, phyllary projection/posture, armature and display-related dimensions.

The key empirical conclusion is:

> **The capitulum is not one adaptive syndrome. Its component phenotypes are decomposable and are distributed differently across environment and biological hierarchy.**

The within- and among-taxon association structures are not identical. This is important because a trait association observed within taxa cannot automatically be promoted to an evolutionary syndrome among taxa.

## 3. EAzami-I: phenotype → candidate functional trait

A measured phenotype is not automatically a functional trait. Promotion is staged:

```text
observed phenotype
    ↓
candidate functional annotation
    ↓
independent functional evidence
    ↓
focal manipulation / performance response
    ↓
validated functional trait
```

Current candidate functional mappings are:

- orientation → time-window pollination / thermal presentation / rain-UV-wetting protection;
- display → pollinator discovery and probing / antagonist discovery and exposure;
- phyllary posture → reproductive-enemy access or exclusion / possible pollinator-access trade-off;
- armature → candidate antagonist exclusion or handling cost, not yet validated from image proxies;
- stickiness → context-dependent enemy interaction and trait cost, with no generic positive defence sign;
- colour → pollinator choice and pigment/abiotic physiology, with local availability and ancestry as mandatory context.

The strongest resolved ecological prior is the reproductive-antagonist cost: experimentally reducing insect herbivory in harmonizable Cirsium experiments increases viable/mature seed output by RR 2.674 (95% CI 2.388–2.993). This establishes the fitness relevance of the enemy channel, not the protective function of any particular capitulum trait.

The selection literature further rejects a universal pollinator- or antagonist-dominance rule. The working ecological architecture is a selection mosaic in which local functional leverage determines whether a particular trait changes effective pollination, antagonist access or abiotic protection strongly enough to reach reproductive fitness.

## 4. EAzami-II: reconstruct trait-specific histories

Once a phenotype has a defensible state definition, its history is reconstructed separately rather than as one whole-capitulum syndrome.

Current source-backed Japan38 results:

- orientation: recurrent change is robust; ML minimum 6 changes and UFBoot lower-bound range 4–6 after the JPN34 authority repair; exact branch localization remains weak;
- phyllary posture: 3 minimum changes across all 1000 UFBoot trees; JPN36 is the strongest partly localizable terminal target;
- stickiness: after the merged JPN24 exact-authority repair, 13 concepts are resolved; ML minimum = 5, root = sticky, and all 1000 frozen UFBoot topologies require exactly 5 unordered changes;
- colour: global/high-depth continuous lightness shows an anti-phylogenetic pattern, but the source-balanced Japan-local replication fails; colour is therefore not promoted to a Japanese-radiation transition history on that evidence.

The simple one-shared-whole-capitulum-lability account is not supported by the current orientation × phyllary × stickiness transition-overlap diagnostics. This is evidence for trait-specific historical structure; it is not proof of developmental or genetic modular evolvability.

## 5. EAzami-III: repeated state ≠ independent origin

A repeated tip state can arise through several histories:

1. ancestral-state retention;
2. independent lineage-specific transition;
3. ancestral polymorphism followed by differential sorting;
4. introgression / gene flow;
5. hybridization or cytoplasmic capture;
6. reversal or re-expression where a biologically justified state model supports it.

Species-level nuclear topology alone cannot separate these alternatives. The next ancestry discriminator therefore links, preferably within the same biological individual:

- nuclear population-genomic DNA;
- same-individual or tightly matched plastid haplotype;
- cytotype / genome-size information;
- standardized capitulum phenotype.

The purpose is not merely to obtain a denser tree. It is to determine where repeated phenotype states came from.

## 6. EAzami-IV: independent origin ≠ convergence

The claim ladder is deliberately strict:

```text
repeated present state
    ↓
independent origin supported
    ↓
repeated ecological association
    ↓
same or functionally equivalent performance consequence
    ↓
reproductive-fitness consequence
    ↓
functional / adaptive convergence
```

Repeated parsimony steps alone do not establish convergence. Phenotypic convergence and functional convergence are also distinct: different phenotypes may solve the same functional problem, and the same phenotype may serve multiple functions.

## 7. Higher-order synthesis

Only after multiple trait histories are reconstructed should higher-order hypotheses be evaluated.

### Modular evolvability

Retain as an endpoint hypothesis: semi-independent trait histories, reusable standing variation, introgression or regulatory reuse may permit rapid phenotype exploration during a young radiation. It is not the organizing premise and is not currently demonstrated.

### Common lability

Retain as a competitor at the higher-order level. The simple whole-capitulum form is not supported by current three-module historical overlap, but snapshot covariance coupling must not be interpreted as evolutionary common lability.

### Scale-specific covariance formation

Retain as an auxiliary generative constraint. Azami shows moderate within-taxon organization, weaker among-taxon integration and stronger among-taxon process-environment structure. v3/v4 simulations diagnose what statistical covariance architectures can reproduce this scale contrast. These simulations constrain plausible generative architecture but do not count evolutionary transitions or establish historical origin.

## 8. Role of the 62-target simulation programme

The simulation programme remains valuable, but it moves off the main biological axis.

Its role is:

> **Which statistical/covariance architectures are compatible with the observed within/among phenotypic field?**

Its current results remain intact:

- v3.1: none of five declared biological driver families passes absolute adequacy;
- one-shot scalar screen: NULL_COUPLED is the frozen scalar-target winner;
- held-out support geometry: that same null reproduces the primary pattern in 0/64 draws;
- post-heldout among-only process structure improves strongly but is inadequate;
- draft v4.1: scale-specific covariance families are the first structures to pass the registered seven-target adequacy screen, but the result is not yet canonical and still requires held-out validation.

These results support scale decoupling as a structural constraint. They are not themselves a realized evolutionary history.

## 9. Current thesis/paper result ladder

### Already established

- capitulum phenotype is decomposable rather than one fixed syndrome;
- within- and among-taxon phenotype organization differ;
- broad climate distance, colonization-history distance and ploidy class do not provide simple deterministic explanations for current capitulum disparity;
- reproductive antagonists impose a large repeatable seed-output cost in harmonizable Cirsium experiments;
- universal pollinator dominance, universal antagonist dominance and one fixed broad functional-class hierarchy are not supported;
- orientation, phyllary posture and stickiness require repeated historical changes on the current nuclear topology ensemble;
- simple whole-capitulum historical lability is not supported by the current three-module overlap diagnostic;
- global continuous lightness history does not replicate as the same anti-phylogenetic signal in the source-balanced Japanese panel.

### Strong working hypotheses, not conclusions

- local selection mosaic acting through trait-specific functional leverage;
- different covariance formation at within- versus among-taxon scales;
- standing ancestral variation / introgression / regulatory reuse as sources of repeated states;
- modular evolvability during the young Japanese radiation.

### Still required for convergence

- population-level ancestry for repeated states;
- trait-specific functional manipulation in focal Cirsium;
- same ecological regime across independent origins;
- final reproductive-fitness effect;
- for colour reactivation, pathway retention + floral expression + pigment + calibrated colour.

## 10. Canonical short formulation

### Azami

> **The capitulum is not one adaptive syndrome. Its component phenotypes are decomposable and occupy different environmental and hierarchical structures.**

### EAzami

> **For each decomposed phenotype, determine what function it can perform, when and how often its states changed, whether repeated states share or differ in origin, and only then whether independent origins repeatedly solve the same ecological problem.**

Short axis:

```text
phenotype → function → history → origin → convergence
```
