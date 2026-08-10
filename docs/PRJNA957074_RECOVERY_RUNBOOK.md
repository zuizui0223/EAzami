# PRJNA957074 recovery runbook

This runbook turns the public NCBI project into versioned evidence tables for EAzami.

## 1. Configure NCBI contact information

```bash
export NCBI_EMAIL="your-address@example.org"
# optional
export NCBI_API_KEY="..."
```

The script throttles requests more conservatively when no API key is supplied.

## 2. Run the project recovery

```bash
python analysis/recover_ncbi_project_runs.py \
  --bioproject PRJNA957074 \
  --focal-taxa data/evidence/focal_taxa_prjna957074.txt \
  --outdir data/evidence/generated \
  --enrich-biosample
```

## 3. Validate outputs

Expected files:

```text
data/evidence/generated/PRJNA957074_runinfo.csv
data/evidence/generated/PRJNA957074_taxon_summary.csv
data/evidence/generated/PRJNA957074_focal_taxon_audit.csv
```

Checks:

```bash
python -m unittest tests/test_recover_ncbi_project_runs.py
python - <<'PY'
import csv
from pathlib import Path

p = Path('data/evidence/generated/PRJNA957074_runinfo.csv')
rows = list(csv.DictReader(p.open(encoding='utf-8')))
assert rows, 'empty runinfo table'
assert all(r['BioProject'] == 'PRJNA957074' for r in rows)
assert len({r['Run'] for r in rows}) == len(rows), 'duplicate run accessions'
print('runs', len(rows))
print('taxa', len({r['ScientificName'] for r in rows}))
PY
```

## 4. Do not equate a non-match with absence

For every focal non-match:

1. search accepted name and historical synonym;
2. inspect varieties/forms that may have been submitted as a broader species;
3. check the 2023 and 2025 supplementary sample tables;
4. check whether the published tree includes a sample without public reads;
5. only then mark `modern_nuclear_gap_confirmed`.

Examples requiring synonym/infraspecific review:

- *C. sieboldii* / *C. paludigenum*;
- *C. yezoense* / *C. zhejiangense*;
- *C. japonicum* varieties;
- historical Korean white forms now synonymized under species names.

## 5. Join recovered taxa to the project master table

Create a versioned join with at least:

- accepted taxon;
- submitted scientific name;
- BioSample/experiment/run;
- voucher/library name;
- country/locality;
- flower-colour state and evidence confidence;
- ploidy/cytotype;
- current transition role;
- species-level versus population-level sequencing need.

## 6. Freeze sequencing decisions only after the join

Decision classes:

- `existing_nuclear_tip_population_data_needed`
- `existing_nuclear_tip_control_only`
- `file_recovery_pending`
- `true_nuclear_gap_colour_critical`
- `true_nuclear_gap_generic_backbone`
- `white_morph_evidence_pending`

Only `true_nuclear_gap_colour_critical` automatically supports new species-level nuclear sequencing. Existing tips can still require dense RAD/resequencing when population history, introgression or a colour-associated locus is the target.

## 7. Manual GitHub Actions route

After the workflow is available to GitHub Actions, run **Recover NCBI project metadata** with project `PRJNA957074`. Download the resulting artifact, review the focal audit and then version the accepted tables in a separate evidence commit/PR.
