from __future__ import annotations
import csv,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SEED=ROOT/'data/evidence/fdt1_broad_functional_calibration_seed_v1.csv'
SUMMARY=ROOT/'data/evidence/fdt1_broad_functional_calibration_summary_v1.json'
EST=ROOT/'data/evidence/fdt1_meta_estimand_registry_v1.csv'
ORI=ROOT/'data/evidence/fdt1_orientation_net_fitness_two_study_meta_v1.json'

def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as h:return list(csv.DictReader(h))

def test_seed_unique_and_summary_counts_match():
    rows=read_csv(SEED); s=json.loads(SUMMARY.read_text())
    assert len(rows)==s['rows']==26
    assert len({r['study_id'] for r in rows})==len(rows)
    assert set(s['modules'])=={'bract_defence','colour_pigmentation','display','orientation','stickiness','stickiness_glandular_trichomes'}
    for module,info in s['modules'].items():
        mr=[r for r in rows if r['module']==module]
        assert len(mr)==info['rows']
        assert sorted({r['taxon'] for r in mr})==sorted(info['taxa'])
        assert sorted({r['source_id'] for r in mr})==sorted(info['source_ids'])
        assert sum(r['effect_readiness'].startswith('quantitative') for r in mr)==info['quantitative_ready_rows']
        assert sum(r['effect_readiness']=='effect_extraction_needed' for r in mr)==info['effect_extraction_needed_rows']

def test_floral_stickiness_is_not_pooled_with_whole_plant_glandular_systems():
    s=json.loads(SUMMARY.read_text())
    assert s['modules']['stickiness']['taxa']==['Bejaria resinosa']
    assert set(s['modules']['stickiness_glandular_trichomes']['taxa'])=={'Aquilegia vulgaris + A. pyrenaica','Datura wrightii'}

def test_claim_boundaries_keep_context_separate():
    rows={r['study_id']:r for r in read_csv(SEED)}
    assert rows['SIL_UV_ANTH_01']['effect_readiness']=='context_mechanism'
    assert 'not pigment-mediated fitness causality' in rows['SIL_UV_ANTH_01']['claim_boundary']
    assert rows['IPO_ANTH_UVB_01']['effect_readiness']=='mechanism_ready'
    assert 'not intact-flower reproductive fitness' in rows['IPO_ANTH_UVB_01']['claim_boundary']
    assert rows['PED_BR_POLL_01']['direction']=='null_pollinator_effect'
    assert rows['PED_BR_PRED_01']['direction']=='intact_water_holding_bracts_lower_seed_predation'

def test_estimand_registry_does_not_force_heterogeneous_pooling():
    rows=read_csv(EST); ids=[r['estimand_id'] for r in rows]
    assert len(ids)==len(set(ids))==15
    by={r['estimand_id']:r for r in rows}
    assert by['E07']['preferred_effect_family']=='lnRR'
    assert by['E14']['current_pooling_status']=='NOT_READY'
    assert by['E15']['preferred_effect_family']=='delta_beta_or_multivariate_gradient'

def test_orientation_meta_is_feasibility_diagnostic_not_general_effect():
    x=json.loads(ORI.read_text())
    assert x['k']==2
    assert all(e['RR']>1 for e in x['effects'])
    assert x['heterogeneity']['I2_percent']>90
    assert x['random_effect_DL']['ci95_RR_normal'][0] < 1 < x['random_effect_DL']['ci95_RR_normal'][1]
    assert 'feasibility diagnostic' in x['interpretation']
    assert 'universally adaptive' in x['claim_boundary']
