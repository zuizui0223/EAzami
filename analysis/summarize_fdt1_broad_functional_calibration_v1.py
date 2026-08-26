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
            'orientation':'Direct manipulation evidence outside Asteraceae supports multiple mechanisms (effective pollination plus abiotic protection) reaching seed/fruit fitness; effect transport to Cirsium remains a hypothesis. The Lilium study is retained only as an orientation-by-slope interaction direction because bounded access checks recovered no model coefficient/covariance and the abstract does not identify a generic orientation response ratio.',
            'stickiness':'A universal sticky-is-defence rule is not retained. Direct reproductive-structure manipulations now independently support reduced enemy damage/access in Bejaria, Erica and the compound Passiflora glandular-bract package, while a Cirsium null remains elsewhere in the repository and whole-plant Datura shows substantial costs. Aquilegia supplies exact multi-population trichome-removal effects with supported species-by-treatment interactions. Erica lacks a recoverable model link/sample size, Passiflora lacks plant-level paired covariance and confounds adhesion with enclosure, and neither adds a safe fruit/seed fitness effect.',
            'display':'Direct manipulation supports simultaneous pollinator-attraction benefit and seed-predator cost directions. A bounded public-source audit verified primary and author abstracts but recovered no numerical treatment summaries; a similarly named author PDF was a different article and is rejected. Display remains direction-only, not a net adaptation estimate.',
            'bract_defence':'Direct reproductive-envelope manipulations now replicate antagonist access/damage effects across Pedicularis, the Cardueae spine experiment in Centaurea, Taraxacum phyllaries, the compound visual-plus-physical Monotropsis bract package and the liquid Chrysothemis calyx. Final seed/fruit directions also occur in Pedicularis, Centaurea and Monotropsis, while Rheum supplies an opposite enemy-direction counterexample. These are functional analogues, not one homologous effect: the Pedicularis seed link, Centaurea paired covariance, Monotropsis variances and Chrysothemis host clustering remain unresolved. No focal Cirsium manipulation validates the Azami image proxy or closes antagonist and pollinator pathways to filled achenes.',
            'colour_pigmentation':'The colour gate is now stratified. Silene still supplies UV exposure and pigment-induction context rather than pigment-causal fitness. A 64-cell, n=1342 Ipomoea purpurea CHS-null factorial table directly calibrates whole-flavonoid-pathway genotype by heat effects on mature-fruit success, but temperature has one chamber and the pathway/tissue effect is not visible petal anthocyanin. Tomato F3H complementation plus antioxidant rescue supports pollen-flavonol control of ROS under heat, and hp2 supplies a pleiotropic independent seed calibration. Mimulus is retained as a direct negative genotype-by-stress counterexample. E14 is bounded-extraction ready; exact petal-anthocyanin E13 remains partial.'
        },
        'next_meta_actions':[
            'obtain verified Ipomopsis full text or author tables through a lawful institutional or author route; do not use the rejected mismatched PDF or infer means from P-value signs',
            'recover the Erica model link/sample size and Passiflora plant-level paired covariance if a quantitative enemy-damage pool is pursued; retain adhesive, glandular and compound-envelope trait families separately',
            'add an independent direct reproductive-stickiness manipulation with final fruit or seed output before any cross-study fitness pool',
            'obtain the verified Lilium orientation-by-slope coefficient and covariance through a lawful institutional or author route, or add another independent orientation manipulation with seed/fruit endpoints',
            'for the defensive-envelope module, stop broad searching: recover the Pedicularis seed-model family/link, Centaurea paired data, Monotropsis plant-level variance and Chrysothemis host clustering; keep physical spines, liquid barriers and concealment packages in separate strata',
            'fit only a bounded chamber-confounding sensitivity to the extracted Ipomoea purpurea 64-cell table; reanalyze tomato pollen data at experiment level and keep pollen flavonols separate from visible petal anthocyanin; stop broad colour searching',
            'do not pool different response metrics until an explicit common estimand or multivariate model is preregistered'
        ],
        'claim_boundary':'Candidate calibration/effect-extraction registry only. It does not estimate a pooled across-angiosperm effect or prove adaptation in Cirsium.'
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(out,indent=2,ensure_ascii=False))
    return 0
if __name__=='__main__': raise SystemExit(main())
