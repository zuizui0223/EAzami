from __future__ import annotations
import csv,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SEED=ROOT/'data/evidence/fdt1_broad_functional_calibration_seed_v1.csv'
SUMMARY=ROOT/'data/evidence/fdt1_broad_functional_calibration_summary_v1.json'
EST=ROOT/'data/evidence/fdt1_meta_estimand_registry_v1.csv'
ORI=ROOT/'data/evidence/fdt1_orientation_net_fitness_two_study_meta_v1.json'
STICK_AUDIT=ROOT/'docs/FDT1_STICKINESS_PRIMARY_MANIPULATION_EVIDENCE_AUDIT_2026-08-26.md'
BRACT_AUDIT=ROOT/'docs/FDT1_BRACT_PHYLLARY_DEFENCE_PRIMARY_MANIPULATION_AUDIT_2026-08-26.md'
COLOUR_AUDIT=ROOT/'docs/FDT1_COLOUR_PIGMENT_FUNCTION_PRIMARY_AUDIT_2026-08-26.md'

def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as h:return list(csv.DictReader(h))

def test_seed_unique_and_summary_counts_match():
    rows=read_csv(SEED); s=json.loads(SUMMARY.read_text())
    assert len(rows)==s['rows']==49
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
    assert set(s['modules']['stickiness']['taxa'])=={'Bejaria resinosa','Erica plukenetii'}
    assert set(s['modules']['stickiness_glandular_trichomes']['taxa'])=={'Aquilegia vulgaris + A. pyrenaica','Datura wrightii','Passiflora foetida'}
    rows={r['study_id']:r for r in read_csv(SEED)}
    assert rows['PASS_STICK_BUD_01']['effect_readiness']=='exact_descriptive_cluster_covariance_missing'
    assert rows['ERIC_STICK_DAMAGE_COROLLA_01']['effect_readiness']=='exact_model_contrast_link_unresolved'
    assert 'do not exponentiate' in rows['ERIC_STICK_DAMAGE_COROLLA_01']['claim_boundary']


def test_stickiness_primary_audit_preserves_mechanism_and_fitness_boundaries():
    text=STICK_AUDIT.read_text(encoding='utf-8')
    assert '17.65 ± 25.11%' in text and '55.82 ± 35.82%' in text
    assert 'control - sticky corolla' in text and '2.43' in text
    assert 'still open outside the already-used Bejaria system' in text
    assert 'No new fitness effect-size row should be created' in text

def test_claim_boundaries_keep_context_separate():
    rows={r['study_id']:r for r in read_csv(SEED)}
    assert rows['SIL_UV_ANTH_01']['effect_readiness']=='context_mechanism'
    assert 'not pigment-mediated fitness causality' in rows['SIL_UV_ANTH_01']['claim_boundary']
    assert rows['IPO_ANTH_UVB_01']['effect_readiness']=='mechanism_ready'
    assert 'not intact-flower reproductive fitness' in rows['IPO_ANTH_UVB_01']['claim_boundary']
    assert rows['PED_BR_POLL_01']['direction']=='null_pollinator_effect'
    assert rows['PED_BR_PRED_01']['direction']=='intact_water_holding_bracts_lower_seed_predation'
    assert rows['PED_BR_POLL_01']['effect_readiness']=='quantitative_model_ready_link_known_logit'
    assert rows['PED_BR_FINALSET_01']['effect_readiness']=='quantitative_model_ready_link_unresolved'
    assert rows['PED_BR_PRED_01']['effect_readiness']=='quantitative_model_ready_link_unresolved'
    assert rows['PED_BR_POLL_01']['lower']=='-0.42704'
    assert rows['PED_BR_FINALSET_01']['lower']=='0.01324'
    assert rows['PED_BR_PRED_01']['upper']=='-0.05828'
    assert rows['CENT_SPINE_FILLEDSEED_01']['estimate']=='0.78'
    assert rows['CENT_SPINE_FILLEDSEED_01']['effect_readiness']=='exact_reported_relative_effect_paired_covariance_missing'
    assert rows['TARA_PHYL_ACCESS_01']['estimate']=='2.05387'
    assert rows['MONO_BR_HERB_2006']['estimate']=='4.0'
    assert rows['MONO_BR_FRUIT_2007']['direction'].endswith('_nonsignificant')
    assert rows['CHRY_CALYX_STERILE_01']['estimate']=='2.18'
    assert rows['CHRY_CALYX_STERILE_01']['lower']=='1.21'
    assert rows['CHRY_CALYX_STERILE_01']['upper']=='3.92'
    assert 'host-plant' in rows['CHRY_CALYX_STERILE_01']['claim_boundary']
    assert rows['RHEUM_BR_PRED_CONTEXT_01']['direction']=='bracts_increased_seed_predation'
    assert rows['IPUR_CHS_MAT_HEAT_01']['estimate']=='0.74'
    assert rows['IPUR_CHS_PAT_HEAT_01']['estimate']=='0.76'
    assert 'chamber_confounded' in rows['IPUR_CHS_MAT_HEAT_01']['effect_readiness']
    assert rows['TOM_ARE_ROS_HEAT_01']['estimate']=='1.5'
    assert 'Pollen does not make anthocyanins' in rows['TOM_ARE_ROS_HEAT_01']['claim_boundary']
    assert rows['MIM_ANTH_STRESS_COUNTER_01']['effect_readiness']=='context_counterexample_do_not_code_zero'

def test_bract_primary_audit_preserves_design_dependence_and_focal_boundary():
    text=BRACT_AUDIT.read_text(encoding='utf-8')
    assert '15 individual plants' in text and '`22%` reduction' in text
    assert '84.64 ± 44.68 s' in text and '41.21 ± 28.63 s' in text
    assert 'control herbivory' in text and '`55%`' in text and '`35%`' in text
    assert 'odds ratio `2.18`' in text and 'pending_host_plant_clustering_resolution' in text
    assert 'No additional focal *Cirsium* phyllary/spine manipulation was recovered' in text
    assert 'The next action is not broader searching' in text

def test_colour_primary_audit_separates_pollen_flavonol_from_visible_petal_colour():
    text=COLOUR_AUDIT.read_text(encoding='utf-8')
    assert '`1342` pollination pairs overall' in text
    assert 'one chamber per temperature' in text
    assert 'pollen-flavonol/ROS mechanism' in text
    assert 'Visible petal anthocyanin itself is still not causally isolated' in text
    assert 'direct negative *Mimulus guttatus* experiment' in text
    assert 'Broader searching should not be used to blur that missing design' in text

def test_estimand_registry_does_not_force_heterogeneous_pooling():
    rows=read_csv(EST); ids=[r['estimand_id'] for r in rows]
    assert len(ids)==len(set(ids))==15
    by={r['estimand_id']:r for r in rows}
    assert by['E07']['preferred_effect_family']=='lnRR'
    assert by['E10']['current_pooling_status']=='MECHANISM_REPLICATED_NOT_POOL_READY'
    assert 'independent Erica' in by['E10']['current_evidence_state']
    assert 'not homologous' in by['E10']['claim_boundary']
    assert 'Erica model link' in by['E10']['minimum_next_requirement']
    assert by['E08']['current_pooling_status']=='MECHANISM_REPLICATED_NOT_POOL_READY'
    assert 'Centaurea paired values' in by['E08']['minimum_next_requirement']
    assert 'not homologous' in by['E08']['claim_boundary']
    assert by['E09']['current_pooling_status']=='FITNESS_REPLICATED_NOT_POOL_READY'
    assert 'Centaurea paired covariance' in by['E09']['minimum_next_requirement']
    assert 'one year only' in by['E09']['claim_boundary']
    assert by['E13']['current_pooling_status']=='CONDITIONAL_READY_FLAVONOL_REPRODUCTIVE_TISSUE'
    assert 'visible-petal anthocyanin effect' in by['E13']['claim_boundary']
    assert by['E14']['current_pooling_status']=='READY_FOR_BOUNDED_EFFECT_EXTRACTION'
    assert '64-cell genotype' in by['E14']['current_evidence_state']
    assert 'chambers or 64 cells' in by['E14']['claim_boundary']
    assert by['E15']['preferred_effect_family']=='delta_beta_or_multivariate_gradient'

def test_orientation_meta_is_feasibility_diagnostic_not_general_effect():
    x=json.loads(ORI.read_text())
    assert x['k']==2
    assert all(e['RR']>1 for e in x['effects'])
    assert x['heterogeneity']['I2_percent']>90
    assert x['random_effect_DL']['ci95_RR_normal'][0] < 1 < x['random_effect_DL']['ci95_RR_normal'][1]
    assert 'feasibility diagnostic' in x['interpretation']
    assert 'universally adaptive' in x['claim_boundary']
