"""Global 2-real-nuclear-region CTMC must retain original author U/D not S1 angle."""
from io import StringIO
import numpy as np
from Bio import Phylo
from analysis import run_chapter2_global_nuclear_ud_CTMC_4climate_v1 as m
from analysis import run_chapter2_orientation_transition_regime_fourclimate_v1 as ea

def test_source_gates_no_subspecies_automatically_binomial_proxy():
    assert m.NA_AUTHOR_TIPS==63
    assert m.NA_AUTHOR_D==5
    assert m.SOURCE_EXACT_SPECIES==56
    assert m.NA_TREE_BLOB=="6417a38793427bc7c8562dc0e2cab59b74d8c316"
    assert m.NA_STATES_BLOB=="fa127f0587b676e6e004ea121424d26069586bcb"
    assert m.COUNTRIES=={"US","CA","MX"}
    assert m.AXES==ea.AXES

def test_strict_no_fake_infraspecific_match():
    x={"GBIF_exact_species_query":"Cirsium conspicuum"}
    strict={"scientificName":"Cirsium conspicuum (Greene) Greene",
            "matchType":"EXACT","rank":"SPECIES","confidence":99,
            "usageKey":76543}
    assert m.exact_taxon_match(x,strict)==76543
    assert m.exact_taxon_match(x,{**strict,"matchType":"FUZZY"}) is None
    assert m.exact_taxon_match(x,{**strict,"scientificName":"Cirsium vinaceum"}) is None
    assert m.exact_taxon_match({"GBIF_exact_species_query":None},strict) is None

def test_geographic_filter_na_only_without_photo_or_pseudolabel():
    c={"key":1111,"countryCode":"US","species":"Cirsium conspicuum",
       "speciesKey":76543,"decimalLatitude":34.1,"decimalLongitude":-106.8}
    a=m.occurrence_row(c,"Cirsium conspicuum",76543)
    assert a["_latitude"]==34.1
    assert a["_longitude"]==-106.8
    assert "U_D" not in a and "orientation" not in a
    assert m.occurrence_row({**c,"countryCode":"JP"},"Cirsium conspicuum",76543) is None
    assert m.occurrence_row({**c,"species":"Cirsium vinaceum"},"Cirsium conspicuum",76543) is None
    assert m.occurrence_row({**c,"decimalLongitude":500},"Cirsium conspicuum",76543) is None

def test_monte_carlo_independent_author_state_maps_using_original_CTMC_branch_posterior():
    tr=Phylo.read(StringIO("((A:0.4,B:0.4):0.2,(C:0.4,D:0.4):0.2);"),"newick")
    tips={"A":0,"B":0,"C":1,"D":1}
    profiles=[
      {"A":1.0,"B":2.0,"C":3.0,"D":4.0},
      {"A":12.0,"B":10.0,"C":5.0,"D":2.0},
      {"A":3.0,"B":4.0,"C":2.0,"D":1.0},
      {"A":12.0,"B":6.0,"C":13.0,"D":8.0},
    ]
    deltas=[m.h.brownian_internal_values(tr,x)[1] for x in profiles]
    r=m.monte_carlo_null(tr,deltas,tips,draws=999,seed=20261024)
    assert r["n_nuclear_taxa"]==4 and r["original_n_D"]==2
    assert r["n_total_including_original_map"]==1000
    assert r["four_axis_direction_unsigned_norm"]["total"]==1000
    assert set(r["maxT_4axis_family_adjusted_fractions"])==set(m.AXES)
    assert 0<r["four_axis_direction_unsigned_norm"]["finite_conditioned_fraction"]<=1
    assert r["cannot_claim_independent_evolutionary_events_or_global_species_tree"]
