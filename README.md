# EAzami — East Asian *Cirsium* hypothesis-resolution layer

EAzami is no longer organized around “build the largest tree first.” Its current purpose is to use existing East Asian/Japanese evidence to identify **which evolutionary hypotheses are already constrained, which remain non-identifiable, and exactly what biological data must be collected next**.

## Start here

1. **Hypothesis → preliminary analysis → missing data map**  
   `docs/PRELIMINARY_ANALYSIS_HYPOTHESIS_MAP.md`
2. **Machine-readable hypothesis registry**  
   `data/evidence/preliminary_hypothesis_registry_v1.csv`
3. **Current project state**  
   `PROJECT_STATUS.md`
4. **Full population-sampling design**  
   `docs/JAPAN_RADSEQ_PHASE_A_SAMPLING_PLAN_2026-08-16.md`
5. **Deferred heavy-compute policy**  
   `docs/DEFERRED_HEAVY_ANALYSES.md`

## Scientific program

```text
Azami Chapter 1
Global public-image macro patterns
        ↓ hypotheses
EAzami preliminary resolution
Existing-data tests + explicit non-identifiability
        ↓ only discriminating new data
Population / mechanism studies
ancestry + plastid + cytotype + trait + expression + pigment + interaction + fitness
```

## What is already supported enough for sampling decisions

- A young Japanese rapid radiation is strongly supported.
- 36/38 sampled Japanese paper taxon concepts fall in the dominant radiation; `C. lineare` is the strongest replicated secondary-history exception and `C. dipsacolepis` remains a secondary-arrival candidate.
- Large current capitulum disparity occurs inside the dominant radiation.
- A separate colonization history is not automatically the most morphologically or environmentally divergent.
- Broad current CHELSA distance does not positively track capitulum distance in the current nine-taxon subset.
- Ploidy does not deterministically set head orientation.
- One colonization history does not correspond to one capitulum syndrome.
- Species-tip coding compresses documented W/C polymorphism; only takaoense currently has direct morph-linked high-dimensional nuclear samples.
- Anthocyanin-pathway retention/regulatory reuse is biologically plausible, but mechanism is not demonstrated.

These are **preliminary decision results**, not proof of adaptive radiation, evolutionary-rate acceleration, or causal evolvability.

## Current live hypotheses

The canonical registry contains ten operational questions:

- `H-RAD1` — radiation-success asymmetry;
- `H-EVOL1` — modular evolvability inside the dominant radiation;
- `H-CLIM1` — broad-climate explanation of capitulum disparity;
- `H-PL1` — ploidy as deterministic morphology explanation;
- `H-COL1` — species-tip compression of colour transitions;
- `H-RET1` — standing variation / introgression as trait-reuse mechanisms;
- `H-MECH1` — anthocyanin pathway retention/regulatory reuse;
- `H-CYTO1` — focal cytonuclear discordance;
- `H-ADAPT1` — trait → interaction → fitness causation;
- `H-RYK1` — Arenicola island-population colour history.

Each hypothesis has an explicit current verdict, existing-data limit, next data requirement, and stop rule in `data/evidence/preliminary_hypothesis_registry_v1.csv`.

## Preliminary-analysis policy

A new preliminary analysis is added only if its outcome changes the next observation or claim boundary.

Routine PR CI is limited to committed-evidence validation and small deterministic analyses. Repeated SRA downloads, transcriptome assembly, large HybPiper/IQ-TREE/ASTRAL/Read2Tree runs, and already-frozen proteome/BLAST recovery are **not routine preliminary CI**.

The corresponding heavy execution code and scientific evidence remain available under `analysis/`, `workflow/`, `data/evidence/`, and Git history. See `docs/DEFERRED_HEAVY_ANALYSES.md`.

## Heavy nuclear tree status

The accepted public inventory remains **294 biological tips / 295 unique SRRs / 270 source-preserving labels**, with EA01 and CNIPG as independent augmentation candidates and EA02 excluded as a duplicate-readset pseudoreplicate.

The Slurm/large-memory 294→296 reconstruction path is preserved, but **it is deferred and is not a prerequisite for the current sampling plan**. It should be reopened only if branch-scaled diversification/trait-rate inference or candidate admission becomes decision-critical.

## What new data are actually needed

Current non-identifiable questions require linked biological observations, not more broad preliminary computation:

- morph↔genotype linkage beyond takaoense;
- standing variation vs introgression;
- population cytotype distributions and ploidy-aware ancestry;
- same-individual nuclear + plastid histories;
- trait → interaction → fitness effects;
- genotype → floral expression → pigment → phenotype mechanisms.

The full population-history target remains **222 minimum / 298 recommended individuals** across `C. pendulum`, `C. sieboldii`, `C. lineare`, `C. dipsacolepis`, `C. brevicaule`, and `C. irumtiense`.

A staged first tranche can prioritize takaoense W/BP, pendulum W/coloured, and brevicaule/irumtiense if field logistics require a smaller first collection.

## Repository layout

- `data/evidence/` — frozen results, contracts, hypothesis registry
- `docs/` — current scientific interpretation, claim boundaries, sampling logic
- `analysis/` — deterministic analysis code retained for reproducibility
- `sampling/` — focal sampling/reference panels
- `workflow/` — deferred/manual/HPC execution paths
- `tests/` — local deterministic tests
- `.github/workflows/` — **lightweight active CI only**

Historical exploratory workflow implementations remain available from Git history rather than running as parallel routine CI.
