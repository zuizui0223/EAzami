#!/usr/bin/env python3
from __future__ import annotations
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / 'data/evidence/japan38_nmns_capitulum_trait_seed_v1.csv'
OUT = ROOT / 'data/evidence/fdt4_multitrait_readiness_v1.json'


def known(v: str) -> bool:
    return bool(v) and v not in {'unknown', 'source_conflict_index_downward_detail_erect'}


def main() -> None:
    rows = list(csv.DictReader(SEED.open(encoding='utf-8')))
    orientation = [r for r in rows if known(r['orientation_state'])]
    phyllary = [r for r in rows if known(r['phyllary_posture'])]
    sticky = [r for r in rows if known(r['stickiness_state'])]
    both_def = [r for r in rows if known(r['phyllary_posture']) and known(r['stickiness_state'])]
    payload = {
        'contract_version': 'fdt4_multitrait_readiness_v1',
        'status_date': '2026-08-25',
        'source': str(SEED.relative_to(ROOT)),
        'rows_in_nmns_seed': len(rows),
        'coverage': {
            'orientation_resolved': len(orientation),
            'phyllary_resolved': len(phyllary),
            'stickiness_resolved': len(sticky),
            'phyllary_and_stickiness_resolved': len(both_def),
        },
        'resolved_taxa': {
            'phyllary': [r['paper_taxon_concept'] for r in phyllary],
            'stickiness': [r['paper_taxon_concept'] for r in sticky],
            'phyllary_and_stickiness': [r['paper_taxon_concept'] for r in both_def],
        },
        'module_decision': {
            'orientation': 'evolutionary-history screen already running on 20-tip nuclear ensemble; keep as tranche-1 benchmark, not sole programme',
            'phyllary_spine': 'next macroevolution module once a machine-readable Japan38/expanded nuclear tree is recovered; current authority coverage is sufficient for a first categorical screen but not for adaptation claims',
            'stickiness': 'next negative-control macroevolution module once Japan38/expanded nuclear tree is recovered; use separate from phyllary/spine',
            'display': 'functional meta evidence is strong, but Japan-wide taxon-level direct display phenotypes are not yet in the current NMNS seed; needs trait-table build before evolutionary mapping',
            'colour': 'historical question is high value but fixed-white lineage coverage remains limiting; do not force W/C ASR before white-tip gate is improved',
        },
        'current_blocker': 'No machine-readable Moreyra Japan38/expanded nuclear tree is currently stored in the repository. Do not infer phyllary/stickiness transition histories from the authority table alone.',
        'next_actions': [
            'recover/store a machine-readable Japan38 or broader Moreyra nuclear topology with sample-to-taxon provenance',
            'map phyllary and stickiness as separate categorical modules on that tree',
            'build a direct taxon-level display table (capitulum size and head number) from authority/voucher sources before any display ASR',
            'retain orientation branchwise BIO15/BIO1 result as benchmark and compare cross-module transition covariance only after at least two additional modules have valid histories',
        ],
        'claim_boundary': 'Coverage readiness only. Counts do not establish phylogenetic signal, repeated evolution, correlated evolution, ecological function, or adaptation.'
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(json.dumps(payload['coverage'], indent=2))

if __name__ == '__main__':
    main()
