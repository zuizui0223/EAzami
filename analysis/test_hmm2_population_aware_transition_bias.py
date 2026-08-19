#!/usr/bin/env python3
"""Stage the HMM2 population-aware colour-transition test using frozen public evidence.

This does not estimate a transition rate. It distinguishes:
A) observed state compression at the species-tip level;
B) topology-specific minimum-transition count sensitivity where morph-linked
   nuclear samples exist;
C) the still-blocked branch-length/population-genealogy rate test.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

TARGETS = {
    "Cirsium japonicum var. takaoense",
    "Cirsium aomorense",
    "Cirsium sieboldii",
    "Cirsium pendulum",
}


def rows(path: str):
    with Path(path).open(encoding="utf-8-sig", newline="") as h:
        return list(csv.DictReader(h))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--audit", default="data/evidence/hmm2_population_aware_transition_testability_v1.csv")
    p.add_argument("--atlas", default="data/evidence/cirsium_flower_colour_atlas_v0_2.csv")
    p.add_argument("--fitch", default="analysis/fitch_transition_sensitivity.csv")
    p.add_argument("--output", required=True)
    args = p.parse_args()

    audit = rows(args.audit)
    atlas = rows(args.atlas)
    fitch = {r["scenario"]: r for r in rows(args.fitch)}

    if {r["accepted_taxon"] for r in audit} != TARGETS:
        raise ValueError("HMM2 focal-system set drift")

    atlas_taxon = {
        r["accepted_taxon"]: r
        for r in atlas
        if r.get("observation_unit") == "taxon"
        and r.get("review_status") == "reviewed"
        and r.get("accepted_taxon") in TARGETS
    }
    missing = TARGETS - set(atlas_taxon)
    if missing:
        raise ValueError(f"reviewed taxon-level atlas records missing: {sorted(missing)}")
    if any(atlas_taxon[t].get("binary_colour_code") != "P" for t in TARGETS):
        raise ValueError("all HMM2 focal systems must remain source-backed polymorphic P records")

    tak_samples = [
        r for r in atlas
        if r.get("accepted_taxon") == "Cirsium japonicum var. takaoense"
        and r.get("observation_unit") == "sample"
        and r.get("review_status") == "reviewed"
        and r.get("assessable") == "yes"
    ]
    tak_states = sorted(r["binary_colour_code"] for r in tak_samples)
    if len(tak_samples) != 6 or tak_states.count("W") != 3 or tak_states.count("C") != 3:
        raise ValueError("takaoense 3W/3C morph-linked sample contract drift")

    sp = fitch["Sinocirsium_species_level_ambiguous_takaoense"]
    pop = fitch["Sinocirsium_population_aware_takaoense"]
    sp_n = int(sp["minimum_transitions"])
    pop_n = int(pop["minimum_transitions"])
    if (sp_n, pop_n) != (1, 2):
        raise ValueError("frozen takaoense Fitch sensitivity drift")

    stage_a = [r for r in audit if r["stage_a_state_compression"] == "yes"]
    stage_b = [r for r in audit if r["stage_b_transition_count_testable"] == "yes"]
    stage_c = [r for r in audit if r["stage_c_transition_rate_testable"] == "yes"]
    morph_linked = [r for r in audit if int(r["morph_linked_nuclear_samples"]) > 0]

    blocked = {
        r["accepted_taxon"]: {
            "nuclear_tip_or_runs": r["nuclear_tip_or_runs"],
            "reason": r["claim_boundary"],
        }
        for r in audit
        if r["stage_b_transition_count_testable"] != "yes"
    }

    result = {
        "contract_version": "hmm2_population_aware_transition_test_v1",
        "hypothesis": "HMM2_population_aware_transition_count_rate_bias",
        "focal_polymorphic_systems": len(audit),
        "stage_A_state_compression": {
            "systems_exposing_W_C_multiplicity_hidden_by_one_P_tip": len(stage_a),
            "systems_total": len(audit),
            "fraction": len(stage_a) / len(audit),
            "interpretation": "All four reviewed polymorphic systems contain W and C information that a one-tip P code cannot represent as separate extant states. This is state-resolution evidence, not a transition-rate estimate.",
        },
        "stage_B_minimum_transition_count": {
            "systems_with_morph_linked_nuclear_genealogy": len(stage_b),
            "systems_total": len(audit),
            "takaoense_species_tip_minimum": sp_n,
            "takaoense_population_sample_minimum": pop_n,
            "takaoense_delta": pop_n - sp_n,
            "takaoense_ratio": pop_n / sp_n,
            "interpretation": "In the only currently testable morph-linked system, population/sample-aware coding doubles the minimum count from 1 to 2. This is single-system direct support for the direction predicted by HMM2, not replicated proof.",
        },
        "stage_C_transition_rate": {
            "systems_rate_testable_now": len(stage_c),
            "systems_total": len(audit),
            "status": "blocked",
            "reason": "A replicated rate comparison requires morph-linked population genealogies and branch lengths/topology weights for multiple polymorphic systems.",
        },
        "morph_genotype_linkage": {
            "systems_with_any_morph_linked_nuclear_samples": len(morph_linked),
            "systems_without_morph_linked_nuclear_samples": len(audit) - len(morph_linked),
            "blocked_systems": blocked,
        },
        "hmm2_current_status": "partial_support_state_compression_4_of_4_and_transition_count_direction_1_of_1_testable; replicated_transition_rate_test_unresolved",
        "claim_boundary": "Do not convert documented within-species W/C polymorphism into a counted evolutionary transition without a genealogy. Do not assign Moreyra tips to white or coloured states when morph linkage is absent. Targeted database non-recovery is not proof that no sequence exists.",
    }

    Path(args.output).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
