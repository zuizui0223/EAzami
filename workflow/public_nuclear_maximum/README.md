# Maximum public nuclear HPC entry point

This directory tracks the top-level public nuclear execution path for issue #18.

## Current biological state after the real-read audit

Accepted primary:

- **294 biological tips**;
- **295 public SRRs**;
- **270 analysis taxon labels**.

Current independent candidates:

- EA01 / `PUBEA001` — *C. nipponicum* var. *yoshinoi*, 236/241 strict loci;
- CNIPG / `AUG_ULLEUNG_CNIP2024` — natural-Ulleung *C. nipponicum*, 180/241 strict loci.

EA02 / `PUBEA002` is no longer an independent candidate. Real-read comparison against the accepted baseline *C. sairamense* sample showed raw-read and recovered-sequence signatures overwhelmingly consistent with reuse/re-deposition of the same underlying read library. It is retained only as a duplicate-control pending explicit contrary provenance.

Current public sample-level ceiling: **296**, not 297. The accepted primary remains 294.

Evidence:

- `data/evidence/public_candidate_empirical_quartet_2026-08-14.json`
- `data/evidence/east_asia_public_candidate_disposition_v2.json`

## Historical v1 bundle

The pre-empirical v1 orchestrator was designed when EA01, EA02 and CNIPG were all treated as possible independent tips. It remains reproducible for provenance and regression testing but is **not a supported heavy-execution path**.

Prepare-only reproduction is still allowed:

```bash
PREPARE_ONLY=1 bash workflow/public_nuclear_maximum/prepare_and_submit.sh /path/to/legacy_v1_handoff
```

Real Slurm submission through that wrapper now fails closed because it still contains the superseded EA02-independent-tip graph.

## Next supported heavy stage

Build a post-empirical maximum-public handoff containing only:

1. the accepted 294-tip baseline;
2. EA01 under the full BWA/BLASTx shared-294 RF + same-taxon-neighbour + source-label ASTRAL gate;
3. CNIPG under its two-mode cross-data-type 294-vs-295 gate.

Only if EA01 and CNIPG pass independently should a common paired-locus **296-tip** combined analysis be launched. Arithmetic alone never accepts 296.

New broad China sampling remains outside this execution stage.
