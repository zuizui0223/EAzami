from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/evidence/aim2_orientation_causal_hypothesis_registry_v1.csv"
ASSIGN = ROOT / "sampling/aim2_orientation_treatment_assignment_v1.csv"
FIELD = ROOT / "sampling/aim2_capitulum_field_ledger_v1.csv"
BOUT = ROOT / "sampling/aim2_capitulum_observation_bout_ledger_v1.csv"
OUT = ROOT / "data/evidence/aim2_orientation_causal_design_v1.json"


def header(path: Path) -> set[str]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        return set(next(reader))


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def require(path: Path, required: set[str]) -> list[str]:
    missing = sorted(required - header(path))
    if missing:
        raise RuntimeError(f"{path}: missing required columns: {missing}")
    return sorted(required)


def main() -> None:
    assignment_required = {
        "orientation_experiment_id",
        "individual_id",
        "population_id",
        "capitulum_id",
        "matched_capitulum_id",
        "randomization_block",
        "assignment",
        "natural_orientation_deg",
        "target_orientation_deg",
        "achieved_orientation_deg",
        "sham_manipulation",
        "early_bout_required",
        "later_bout_required",
        "wetting_event_followup_required",
        "antagonist_followup_required",
        "final_fitness_required",
        "treatment_integrity",
        "attrition_reason",
    }
    field_required = {
        "individual_id",
        "population_id",
        "capitulum_id",
        "phenological_stage",
        "natural_orientation_deg",
        "orientation_treatment",
        "orientation_target_deg",
        "orientation_achieved_deg",
        "pollen_wetting_score",
        "pollen_viability",
        "effective_contact_count",
        "florivory_damage_fraction",
        "seed_predator_presence",
        "seed_predator_damage_fraction",
        "total_achenes",
        "filled_achenes",
        "seed_mass_mg",
        "treatment_loss_or_exclusion",
    }
    bout_required = {
        "individual_id",
        "population_id",
        "capitulum_id",
        "observation_bout_id",
        "start_time_local",
        "end_time_local",
        "time_window_class",
        "phenological_stage",
        "orientation_treatment",
        "natural_orientation_deg",
        "orientation_achieved_deg",
        "air_temperature_c",
        "head_surface_temperature_c",
        "relative_humidity_pct",
        "wind_speed_m_s",
        "incident_radiation_w_m2",
        "rainfall_mm_previous_30min",
        "capitulum_wetness_score",
        "pollen_presentation_state",
        "pollen_wetting_score",
        "pollen_viability_sample_id",
        "pollen_viability",
        "pollinator_visit_count",
        "effective_contact_count",
        "antagonist_visit_count",
        "florivory_event_count",
        "seed_predator_event_count",
        "damage_observed_during_bout",
        "treatment_integrity",
    }

    checked = {
        "assignment": require(ASSIGN, assignment_required),
        "field": require(FIELD, field_required),
        "bout": require(BOUT, bout_required),
    }

    hypothesis_rows = rows(REGISTRY)
    if [r["hypothesis_id"] for r in hypothesis_rows] != ["ORI0", "ORI1", "ORI2", "ORI3", "ORI4", "ORI5"]:
        raise RuntimeError("Orientation hypothesis registry must preserve ORI0-ORI5 order")

    pathway_readiness = {
        "ORI1_time_window_thermal_pollination": {
            "schema_ready": True,
            "required_observed_links": [
                "assignment -> achieved orientation",
                "assignment -> early head temperature / effective contact",
                "effective contact -> final filled-achene output",
            ],
            "important_negative_control": "all-day visit total may be null",
        },
        "ORI2_wetting_pollen_protection": {
            "schema_ready": True,
            "required_observed_links": [
                "assignment -> wetness / pollen wetting after wetting events",
                "assignment -> pollen viability or presentation",
                "wetting/viability state -> final filled-achene output",
            ],
            "important_negative_control": "dry observations do not falsify the pathway",
        },
        "ORI3_antagonist_exposure": {
            "schema_ready": True,
            "required_observed_links": [
                "assignment -> antagonist events / damage",
                "antagonist damage -> final filled-achene output",
            ],
            "important_negative_control": "low-enemy periods are low-information",
        },
        "ORI4_combined_partitioning": {
            "schema_ready": True,
            "required_observed_links": [
                "at least two ORI1-ORI3 process families change",
                "final reproductive output changes",
            ],
            "important_negative_control": "higher all-day visitation is not required",
        },
        "ORI0_null_compatible": {
            "schema_ready": True,
            "supportable_now": False,
            "reason": "A smallest effect of interest must be frozen after a blinded variance pilot before equivalence can support a null claim.",
        },
        "ORI5_unexplained_direct_or_unmeasured": {
            "schema_ready": True,
            "purpose": "Prevent post hoc mediator invention if reproductive output changes without a preregistered process shift.",
        },
    }

    analysis_contract = {
        "biological_unit": "individual plant / randomized block; repeated bouts are repeated measurements, not replicates",
        "primary_total_effect_estimand": "intention-to-treat effect of reorientation assignment versus sham on filled-achene output conditional on total achenes",
        "primary_total_effect_model": "binomial or beta-binomial mixed model: cbind(filled_achenes, total_achenes-filled_achenes) ~ assignment + preregistered baseline terms + population/block structure",
        "process_models": {
            "early_effective_contact": "count model with observation duration offset and assignment x time_window_class; early window is preregistered",
            "head_microclimate": "mixed model for head_surface_temperature_c relative to air temperature and time window",
            "wetting_viability": "wetting-event-stratified models for capitulum/pollen wetting and pollen viability",
            "antagonist": "count/damage model for antagonist events and florivory/seed-predator damage",
        },
        "causal_safeguards": [
            "Estimate the total assignment effect before conditioning on post-treatment mediators.",
            "Use achieved orientation only as a per-protocol / dose-response sensitivity, not as the primary causal contrast.",
            "Report treatment attrition by assignment; do not silently drop failed manipulations.",
            "Do not use all-day visitor count as the fitness endpoint.",
            "Do not claim a mediated fraction without separately justified mediation assumptions.",
        ],
        "mechanism_decision_order": [
            "test total reproductive effect",
            "test preregistered process shifts independently",
            "classify ORI1/ORI2/ORI3 or ORI4 only when process and fitness evidence align",
            "classify ORI5 when fitness changes without a preregistered process shift",
            "use ORI0 only after an equivalence bound is preregistered from blinded pilot variance",
        ],
    }

    summary = {
        "version": "v1",
        "hypothesis_count": len(hypothesis_rows),
        "hypotheses": [r["hypothesis_id"] for r in hypothesis_rows],
        "schema_checks": checked,
        "all_preregistered_process_pathways_schema_ready": all(v["schema_ready"] for v in pathway_readiness.values()),
        "pathway_readiness": pathway_readiness,
        "analysis_contract": analysis_contract,
        "field_execution_ready": True,
        "empirical_result_available": False,
        "next_gate": "randomize sham/reorientation pairs in focal Cirsium, collect early/later bouts and conditional wetting/enemy follow-up, then close the process -> seed-fitness chain",
        "claim_boundary": "Schema and analysis readiness only. This validates that the field design can record the preregistered discriminators; it does not demonstrate any orientation mechanism in Cirsium.",
    }
    OUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
