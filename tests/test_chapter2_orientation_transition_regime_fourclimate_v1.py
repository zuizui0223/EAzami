"""Replay original EAzami CTMC U/D edge posterior, NOT global photo-angle PGLS."""
from io import StringIO
import numpy as np
import pandas as pd
import pytest
from Bio import Phylo
from analysis import run_chapter2_orientation_transition_regime_fourclimate_v1 as m

def test_existing_scientific_method_is_imported_not_replaced():
    assert m.AXES==("chelsa_bio18","chelsa_bio05","chelsa_rsds_mean","elevation_m")
    assert m.PANELS["n5_primary"]==("5",12,7,5,792)
    assert m.PANELS["n3_sensitivity"]==("3",13,7,6,1716)
    assert m.PANELS["n10_strict"]==("10",9,5,4,126)
    assert m.SOURCE_N_JP==693 and m.SOURCE_N_TW==55
    assert m.SOURCE_SHA["chelsa_rsds_mean"]=="cc1ad14a70a1a940be3d01d918d4c3f7e35db95b86b12af9be5487e1bbc1fc7d"

def test_real_eazami_discrete_CTMC_posterior_signed_branch_scores():
    tree=Phylo.read(StringIO("((A:0.4,B:0.4):0.2,(C:0.4,D:0.4):0.2);"),"newick")
    state={"A":0,"B":0,"C":1,"D":1}
    sample={
        "A":[3.,20.,10.,45.],"B":[5.,18.,13.,40.],
        "C":[12.,15.,8.,20.],"D":[14.,13.,7.,14.]}
    deltas=[]
    for i in range(4):
        _,e=m.h.brownian_internal_values(tree,{k:v[i] for k,v in sample.items()})
        deltas.append(e)
    score,diag=m.score_map(tree,state,deltas)
    assert len(score)==4
    assert np.isfinite(score).all()
    assert diag["posterior_expected_transition_change_mass"]>0
    assert score[0]>0  # increasing warm-quarter precipitation in D lineage

def test_original_count_preserving_exact_state_null_not_s1_photo_regression():
    tree=Phylo.read(StringIO("((A:0.4,B:0.4):0.2,(C:0.4,D:0.4):0.2);"),"newick")
    shifts=[
      {"A":1.0,"B":2.0,"C":4.0,"D":6.0},
      {"A":7.0,"B":6.0,"C":5.0,"D":3.0},
      {"A":4.0,"B":8.0,"C":5.0,"D":7.0},
      {"A":7.0,"B":4.0,"C":3.0,"D":8.0},
    ]
    deltas=[m.h.brownian_internal_values(tree,v)[1] for v in shifts]
    taxa=["A","B","C","D"]
    obs={"A":0,"B":0,"C":1,"D":1}
    r=m.full_null(taxa,obs,[(tree,deltas)])
    assert r["n_state_maps"]==6
    assert r["null_4axis_joint_norm"]["n_count_preserving_maps"]==6
    assert len(r["null_axes_abs_exact_two_sided_conditional_ranks"])==4
    assert all(v["not_independent_biological_p_value"] for v in r["null_axes_maxT_family_adjusted_conditional_ranks"].values())
    assert r["directions_not_chosen_to_make_transition_test_significant"]
    region=m.full_null(taxa,obs,[(tree,deltas)],region_map={
       "groupA":({"A","C"},1),"groupB":({"B","D"},1)})
    assert region["n_state_maps"]==4

def test_complete_original_climate_sites_keep_original_name_concepts_without_proxy_values():
    assert "chelsa_bio12" not in m.AXES
    assert "chelsa_bio01" not in m.AXES
    assert "chelsa_bio15" not in m.AXES
    assert set(m.SRC_FILENAMES)=={"chelsa_bio18","chelsa_bio05","elevation_m"}
