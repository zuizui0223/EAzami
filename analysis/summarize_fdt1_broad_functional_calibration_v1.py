#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json
from collections import defaultdict
from pathlib import Path

def read(path:Path):
    with path.open(encoding='utf-8-sig',newline='') as h:
        return [dict(r) for r in csv.DictReader(h)]

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument('--input',type=Path,required=True); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
    rows=read(a.input)
    if not rows: raise ValueError('empty calibration seed')
    ids=[r['study_id'] for r in rows]
    if len(ids)!=len(set(ids)): raise ValueError('duplicate study_id')
    by=defaultdict(list)
    for r in rows: by[r['module']].append(r)
    modules={}
    for m,rs in sorted(by.items()):
        ready=[r for r in rs if r['effect_readiness'].startswith('quantitative')]
        extract=[r for r in rs if r['effect_readiness']=='effect_extraction_needed']
        modules[m]={
            'rows':len(rs),
            'quantitative_ready_rows':len(ready),
            'effect_extraction_needed_rows':len(extract),
            'taxa':sorted({r['taxon'] for r in rs}),
            'source_ids':sorted({r['source_id'] for r in rs}),
        }
    out={
        'contract_version':'fdt1_broad_functional_calibration_v1',
        'rows':len(rows),
        'modules':modules,
        'current_inference':{
            'orientation':'Direct manipulation evidence outside Asteraceae supports multiple mechanisms (effective pollination plus abiotic protection) reaching seed/fruit fitness; effect transport to Cirsium remains a hypothesis.',
            'stickiness':'A universal sticky-is-defence rule is not retained. Direct floral evidence includes strong benefit in Bejaria and a Cirsium null elsewhere in the repository, while whole-plant Datura shows substantial costs; context-dependent defence is the working hypothesis.',
            'display':'Direct manipulation supports simultaneous pollinator-attraction benefit and seed-predator cost, but numerical common-effect extraction is not yet complete for the broad-angiosperm lane.',
            'bract_defence':'Pedicularis rex directly separates functions: draining water-holding bracts left pollinator visitation unchanged but increased seed predation and reduced final seed set. This supports a defence/protection pathway rather than a generic pollinator-attraction function.',
            'colour_pigmentation':'Silene UV exclusion shows that UV exposure induces anthocyanin while simultaneously depressing pollen and whole-plant seed production. This supports UV as a plausible selection pressure and pigment-induction context, but does not demonstrate that darker pigmentation itself raises fitness.'
        },
        'next_meta_actions':[
            'extract raw/group summaries for Ipomopsis display manipulation',
            'extract comparable quantitative endpoints for Aquilegia glandular-trichome manipulation',
            'add additional independent orientation manipulations with seed/fruit endpoints',
            'expand bract/phyllary manipulations beyond water-holding bracts to physical exclusion or access mechanisms',
            'separate colour-driver experiments from direct pigment-function manipulations before pooling',
            'do not pool different response metrics until an explicit common estimand or multivariate model is preregistered'
        ],
        'claim_boundary':'Candidate calibration/effect-extraction registry only. It does not estimate a pooled across-angiosperm effect or prove adaptation in Cirsium.'
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(out,indent=2,ensure_ascii=False))
    return 0
if __name__=='__main__': raise SystemExit(main())
