#!/usr/bin/env python3
"""Homology-restricted mechanism elimination for the three focal capitulum traits.

Rule: evidence most similar in organ and manipulation geometry gets priority when
naming a physical mechanism. Broader analogs may support a domain but cannot
rescue a mechanism contradicted by a closer manipulation. This does not estimate
selection coefficients or transport effects to East-Asian Cirsium.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "data" / "evidence"


def j(name: str) -> dict:
    return json.loads((EVID / name).read_text(encoding="utf-8"))


def rows(name: str, key: str) -> dict[str, dict[str, str]]:
    with (EVID / name).open(encoding="utf-8-sig", newline="") as h:
        rr = list(csv.DictReader(h))
    return {r[key]: r for r in rr}


def build() -> dict:
    v2 = j("chapter2_trait_cause_falsification_v2.json")
    current = j("chapter2_current_claims_h1_h4_v1.json")
    focal = j("chapter2_focal_species_cause_evidence_audit_v1.json")
    fun = rows("fdt1_broad_functional_calibration_seed_extension_v1.csv", "study_id")
    cirs = rows("cirsium_interaction_evidence_seed_extension_v1.csv", "evidence_id")

    assert v2["orientation"]["leading_domain"] == "abiotic_reproductive_exposure_plus_timing"
    assert v2["phyllary"]["leading_domain"] == "mechanical_antagonist_exclusion"
    assert v2["stickiness"]["leading_domain"] == "arthropod_community_filter_by_trait_cost"
    assert current["historical_persistence"]["h4"]["overall_match"] == "99/376 = 26.3%"

    # Orientation: prioritize vertical nodding/erect Asteraceae manipulation.
    assert fun["CREM_ORIENT_POLL_01"]["direction"] == "no_preference"
    assert fun["CREM_ORIENT_TEMP_01"]["direction"] == "no_meaningful_thermal_difference"
    assert fun["CREM_ORIENT_ABIOTIC_01"]["direction"] == "water_and_UVB_reduce_viability"
    assert fun["CREM_ORIENT_ACHENE_01"]["direction"] == "nodding_higher"

    # Phyllary: prioritize close Cardueae involucre manipulation plus focal accessibility.
    assert fun["CENTA_BR_POLL_FREQ_01"]["direction"] == "no_increase_after_spine_removal"
    assert float(fun["CENTA_BR_SEED_01"]["estimate"]) == -22
    assert fun["CENTA_BR_LEPI_01"]["direction"] == "intact_spines_lower_illegitimate_visitation"
    assert focal["phyllary_JPN36"]["model_update"]["pollinator_access_primary"] == "further_weakened_as_a_necessary_condition"

    # Stickiness: prioritize direct within-Cirsium evidence.
    assert cirs["INT016"]["direction"] == "sticky_defence_benefit"
    assert cirs["INT017"]["direction"] == "null"
    assert cirs["INT018"]["direction"] == "guild_selective"

    return {
        "version": "chapter2_trait_cause_homology_restricted_v1",
        "status_date": "2026-09-06",
        "rule": "when naming a physical mechanism, prioritize evidence closest in organ, geometry and taxonomic context; broader analogs cannot rescue a mechanism unsupported by closer evidence",
        "orientation": {
            "geometry_restriction": "vertical nodding-versus-erect capitulum manipulations prioritized over azimuthal orientation or nonhomologous flower-orientation systems",
            "models": {
                "static_pollinator_preference": "weakened_as_primary_by_no_preference_in_Cremanthodium",
                "orientation_driven_floral_heating": "not_supported_in_close_Asteraceae_manipulation",
                "hydric_UVB_reproductive_protection": "leading_physical_mechanism_prior",
                "thermal_timing": "retained_as_secondary_cross_system_domain_not_a_close_geometry_mechanism"
            },
            "leading_physical_mechanism": "protection of reproductive tissues from wetting/rain and UV-B exposure",
            "link_to_focal_result": "compatible with the focal East-Asian transition-regime signal, but BIO15/BIO1 are ecological regime coordinates rather than direct wetting/UV measurements",
            "origin_boundary": "not demonstrated as the origin cause because current regime persistence is only 99/376 scenarios",
            "focal_causation": "not_proven"
        },
        "phyllary": {
            "structure_restriction": "close Cardueae involucral-spine manipulation prioritized over nonhomologous bract systems; focal JPN36 natural visitor access used only as a necessity constraint",
            "models": {
                "pollinator_access_as_primary_benefit": "further_weakened",
                "mechanical_antagonist_exclusion": "leading_physical_mechanism_prior",
                "wetting_protection": "not_evaluable_as_a_distinct_phyllary_mechanism",
                "broad_abiotic_sorting": "not_supported_current_public_panel"
            },
            "leading_physical_mechanism": "mechanical restriction of illegitimate or damaging visitor access to the reproductive head",
            "focal_constraint": "appressed JPN36 is naturally visited by multiple bee, butterfly and hawkmoth taxa, so open/spreading phyllaries are not a demonstrated prerequisite for legitimate visitor access",
            "focal_causation": "not_evaluable_without_JPN36_manipulation"
        },
        "stickiness": {
            "taxonomic_restriction": "direct Cirsium benefit/null experiments and Cirsium arthropod-guild observations prioritized over other sticky-plant systems",
            "models": {
                "universal_physical_barrier_to_seed_predators": "contradicted",
                "pollinator_interference_as_general_cost": "weakened_in_Cirsium_discolor_because_pollinators_do_not_contact_sticky_traps",
                "guild_selective_arthropod_filter": "directly_supported_as_mechanism_class_within_Cirsium",
                "production_or_resistance_cost": "external_prior_only_not_measured_in_focal_Cirsium"
            },
            "leading_physical_mechanism": "guild-selective filtering of arthropod access and residence on the involucre",
            "net_selection_model": "local arthropod-community benefit minus secretion/resistance and other trait costs",
            "focal_causation": "not_evaluable_without_JPN15_neutralization_and_local_community_fitness_measurement"
        },
        "whole_capitulum": {
            "physical_interface_model": {
                "orientation": "abiotic exposure filter",
                "phyllary": "mechanical access filter",
                "stickiness": "adhesive arthropod-community filter"
            },
            "interpretation": "the three traits can be functionally integrated in one capitulum while mediating different interfaces with the environment; this provides a biological mechanism-level interpretation of mosaic historical assembly",
            "claim_boundary": "distinct interface mechanisms do not prove separate genes, developmental modules, or a unique selective cause for every transition"
        }
    }


def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument('--output',type=Path,required=True); a=p.parse_args(); x=build(); a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8'); print(json.dumps(x,indent=2,ensure_ascii=False)); return 0

if __name__=='__main__': raise SystemExit(main())
