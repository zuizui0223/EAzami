#!/usr/bin/env python3
"""Build the final public-data Chapter 2 trait × driver endpoint matrix.

The matrix is a synthesis endpoint, not a new significance screen.  It preserves
resolved recurrence, chronology and historical-environment results, carries the
Azami present-space bridge, and assigns an explicit public-data ceiling and
Chapter 3 handoff for every capitulum module.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def origin_decision(origin: dict[str, Any]) -> tuple[str, str, str]:
    classification = origin["cross_scenario_summary"]["classification"]
    if classification == "robust_state_trajectory_concordance_under_scenario_envelope":
        return (
            "multi_layer_concordant_candidate",
            "historical origin trajectory concordant with the frozen Azami state-space vector across the chronology and paleolocation envelope",
            "persistent_driver_ST1_strengthened_observationally",
        )
    if classification == "robust_state_trajectory_discordance_under_scenario_envelope":
        return (
            "present_sorting_historical_origin_decoupled",
            "historical origin trajectory robustly opposite to the frozen Azami state-space vector across the scenario envelope",
            "origin_maintenance_decoupling_ST2_prioritized",
        )
    if classification == "origin_trajectory_unresolved_under_public_chronology_and_paleolocation_uncertainty":
        return (
            "history_resolved_origin_driver_unidentified_at_public_resolution",
            "historical origin trajectory changes sign or tail status across admissible chronology and paleolocation scenarios",
            "ST1_vs_ST2_vs_ST3_not_identifiable",
        )
    raise ValueError(f"Unknown origin classification: {classification}")


def q(v: float) -> str:
    return f"{float(v):.6f}"


def build_rows(origin: dict[str, Any]) -> list[dict[str, str]]:
    orientation_class, orientation_history, orientation_process = origin_decision(origin)
    cross = origin["cross_scenario_summary"]
    c = cross["cosine_similarity"]
    p = cross["cosine_null_percentile"]

    common = {
        "chapter_role": "final_public_data_explanatory_depth",
        "causal_claim_allowed": "no",
    }
    rows = [
        {
            **common,
            "priority_rank": "1",
            "trait_module": "orientation",
            "driver_domain": "hydric_exposure_with_thermal_alternative",
            "breadth_azami": "among-taxon orientation angle increases with BIO12; beta=+0.304359, global-family q=0.021; broad-space and historical-placement sensitivities retain the positive direction",
            "depth_recurrence": "ML minimum 6; UFBoot minimum 4-6",
            "depth_timing": "full Japan38 relative internal-to-terminal envelope; public origin scenario lies on core-Nipponocirsium stem after erect C. morii and before Japanese-core/Taiwan-core split",
            "distribution_process": "core Nipponocirsium range/clade reorganization creates exposure opportunity; exact ancestral region unresolved across Taiwan, Ryukyu, southern Japan and broad East-Asian corridor scenarios",
            "present_eazami_ecology": "nodding/downward taxa occupy higher BIO15 and lower BIO1 present niches; signs stable across accepted topology and species-LOO sets, threshold source-sensitive",
            "historical_environment": orientation_history,
            "space_time_statistic": (
                f"origin-envelope cosine q05={q(c['q05'])}; median={q(c['median'])}; q95={q(c['q95'])}; "
                f"null-percentile median={q(p['median'])}; classification={cross['classification']}"
            ),
            "alternative_falsification": "restricted Taiwan descendant branch shows no unusual BIO12 variability, BIO15 direction opposite present D-high niche, BIO1 warming, no wet-side BIO13/BIO16 specificity; global sea-level volatility not exceptional",
            "final_result_class": orientation_class,
            "process_model_status": orientation_process,
            "public_data_ceiling": "repeated history is resolved, but exact origin date, ancestral area, transition instant, direct flower wetting and fitness are not",
            "chapter3_test": "measure gravity-calibrated orientation, flowering-period rain exposure, capitulum wetting, pollen retention/viability, effective visitor contact and mature viable seed across replicated U/D populations; manipulate orientation or rain shielding with sham controls",
        },
        {
            **common,
            "priority_rank": "2",
            "trait_module": "flower_colour",
            "driver_domain": "radiative_optical_environment",
            "breadth_azami": "visible corolla CIELAB chroma decreases with RSDS; beta=-0.345372, global-family q=0.006; broad-space beta=-0.712411, P=0.001; placement-tree directions stable",
            "depth_recurrence": "two conditional C-to-W minimum-history terminal events on the public six-taxon dated scaffold; broader Japan/East-Asia colour recurrence unresolved because morphs and sequenced tips are not one-to-one",
            "depth_timing": "C. brevicaule terminal window 0-0.93 Ma; C. kawakamii terminal window 0-0.47 Ma; neither identifies the exact transition instant",
            "distribution_process": "central Ryukyu post-split Arenicola lineage and within-Taiwan Nipponocirsium terminal diversification; colour polymorphism and reticulation limit lineage mapping",
            "present_eazami_ecology": "continuous colour/lightness/chroma/hue diagnostics do not retain corrected topology-robust phylogenetic structure at current matched coverage",
            "historical_environment": "direct historical surface-RSDS equivalent is absent; PALEO-PGEM temperature/precipitation cannot be relabelled as radiation history",
            "space_time_statistic": "not_evaluable_directly_commensurate",
            "alternative_falsification": "separate orbital/insolation models would add a new model layer; current RGB chroma does not identify pigment amount, UV absorption or spectral contrast",
            "final_result_class": "strong_present_space_candidate_historical_driver_not_evaluable",
            "process_model_status": "persistent_radiative_driver_unresolved",
            "public_data_ceiling": "spatial radiation sorting is strong, but repeated morph-linked dated history and directly comparable historical radiation are absent",
            "chapter3_test": "sample white/pink morph-linked populations; measure reflectance including UV, pigment chemistry, tissue temperature/photodamage, pollinator visibility and fitness under irradiance or shading manipulations",
        },
        {
            **common,
            "priority_rank": "3",
            "trait_module": "phyllary_posture",
            "driver_domain": "wetting_enemy_access_mechanical_protection",
            "breadth_azami": "Azami involucre image geometry exists, but projection/roughness/taper are not homologous to authority-coded ascending/spreading/recurved posture",
            "depth_recurrence": "exactly 3 minimum changes across all 1000 UFBoot trees",
            "depth_timing": "relative-depth envelope includes deeper and terminal placements; no reconciled public calendar-time event set",
            "distribution_process": "range-history context can be classified only after posture-bearing branches are reconciled to dated subclades",
            "present_eazami_ecology": "not evaluable under the frozen taxon-overlap climate gate",
            "historical_environment": "no homologous trait-to-environment trajectory test; wetting, florivore/seed-predator access, pollinator access and mechanical protection remain competing mechanisms",
            "space_time_statistic": "not_comparable_measurement_ontology",
            "alternative_falsification": "image projection proxies must not be treated as botanical posture; analog protective-bract literature is not focal Cirsium proof",
            "final_result_class": "history_resolved_cause_unidentified",
            "process_model_status": "multiple_mechanisms_open",
            "public_data_ceiling": "repeated/deeper history is resolved but homologous spatial phenotype and dated event ecology are absent",
            "chapter3_test": "botanically calibrate posture and manipulate phyllary access/position without damage; quantify rain entry, enemy attack, pollinator access and viable seed with sham controls",
        },
        {
            **common,
            "priority_rank": "4",
            "trait_module": "stickiness",
            "driver_domain": "biotic_enemy_cost_selection_mosaic",
            "breadth_azami": "no homologous continuous or discrete Azami stickiness endpoint",
            "depth_recurrence": "exactly 5 minimum changes across all 1000 UFBoot trees; strongly shallow/terminal-biased",
            "depth_timing": "relative terminal concentration is resolved; C. dipsacolepis and C. lineare dispersal intervals are process context, not stickiness-transition dates",
            "distribution_process": "secondary arrival and lineage-specific range histories offer natural-experiment context but cannot be equated with trait change",
            "present_eazami_ecology": "not evaluable with current climate overlap; climate is an alternative/negative explanation rather than a proxy for enemies",
            "historical_environment": "no historical enemy-community series; generic sticky-defence prediction has mixed/null focal-analog evidence",
            "space_time_statistic": "not_evaluable_biotic_driver",
            "alternative_falsification": "recurrence does not establish defence; test benefits against costs to pollinator handling, self-contamination and resource allocation",
            "final_result_class": "rapid_history_resolved_biotic_driver_unidentified",
            "process_model_status": "local_selection_mosaic_candidate",
            "public_data_ceiling": "rapid lineage-specific reassembly is supported, but public data cannot identify the enemy or cost regime",
            "chapter3_test": "ancestry-matched sticky/nonsticky contrasts and reversible neutralization/restoration; measure arthropod access, damage, effective pollination and mature viable seed",
        },
        {
            **common,
            "priority_rank": "5",
            "trait_module": "outline_and_involucre_architecture",
            "driver_domain": "thermal_hydric_radiative_mechanical_resource_multidimensional",
            "breadth_azami": "multiple continuous image-derived endpoints show broad present diversity and heterogeneous environmental associations across the frozen nine-predictor atlas",
            "depth_recurrence": "no adequately covered commensurate Japan38 scalar history; sparse continuous diagnostics fail corrected retention",
            "depth_timing": "not evaluable",
            "distribution_process": "not linkable to transition-bearing dated branches at current phenotype coverage",
            "present_eazami_ecology": "descriptive disparity pilots exist but are not evolutionary disparity-through-time or causal process evidence",
            "historical_environment": "not evaluable",
            "space_time_statistic": "not_evaluable_time_axis_coverage",
            "alternative_falsification": "do not manufacture BM/OU support from sparse tips or substitute whole-head composites for missing homologous endpoints",
            "final_result_class": "present_breadth_resolved_evolutionary_depth_not_evaluable",
            "process_model_status": "continuous_history_data_limited",
            "public_data_ceiling": "present breadth is measurable; matched continuous time-axis phenotype coverage is insufficient",
            "chapter3_test": "collect taxon-balanced calibrated continuous geometry on phylogenetically informative samples before BM/OU or moving-optimum models; validate mechanical, resource and interaction functions",
        },
    ]
    return rows


def write_markdown(rows: list[dict[str, str]], origin: dict[str, Any], path: Path) -> None:
    cross = origin["cross_scenario_summary"]
    lines = [
        "# Chapter 2 public-data endpoint matrix v1",
        "",
        "Status: generated from the frozen Chapter 2 public evidence assets.",
        "",
        "## Chapter-level result",
        "",
        "> Present capitulum breadth is associated with asymmetric evolutionary depth among component traits, while the causes of that depth are identifiable to different degrees. Orientation provides the strongest space–time bridge, but its origin environment remains conditional on chronology and paleolocation resolution; colour is space-strong/history-limited; phyllary posture and stickiness are history-strong/driver-limited.",
        "",
        "## Orientation origin-envelope decision",
        "",
        f"`{cross['classification']}`",
        "",
        "## Trait × driver endpoints",
        "",
        "| rank | trait | driver domain | recurrence/depth | final public-data class | Chapter 3 causal target |",
        "|---:|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['priority_rank']} | {r['trait_module']} | {r['driver_domain']} | "
            f"{r['depth_recurrence']} | `{r['final_result_class']}` | {r['chapter3_test']} |"
        )
    lines += [
        "",
        "## Interpretation rules",
        "",
        "1. `multi_layer_concordant_candidate` is an observational candidate, not adaptation proof.",
        "2. Discordance is retained as origin–maintenance decoupling evidence rather than discarded as a failed result.",
        "3. `history_resolved_cause_unidentified` means evolutionary recurrence/depth is supported but comparable driver evidence is absent.",
        "4. `not_evaluable` is a data-resolution result, not biological zero.",
        "5. Chapter 3 must close actual exposure, mechanism and reproductive-fitness links.",
        "",
        "## Doctoral handoff",
        "",
        "- Chapter 1: breadth across current environmental states.",
        "- Chapter 2: depth, range-exposure process, historical trajectories and identifiability limits from public data.",
        "- Chapter 3: own-sample causal tests prioritized by the matrix above.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--origin-result",
        type=Path,
        default=ROOT / "data/evidence/chapter2_orientation_origin_envelope_result_v1.json",
    )
    ap.add_argument("--out-csv", type=Path, required=True)
    ap.add_argument("--out-json", type=Path, required=True)
    ap.add_argument("--out-md", type=Path, required=True)
    args = ap.parse_args()

    origin = load_json(args.origin_result)
    rows = build_rows(origin)
    fields = list(rows[0].keys())
    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    result = {
        "contract_version": "chapter2_public_data_endpoint_matrix_v1",
        "orientation_origin_envelope_classification": origin["cross_scenario_summary"]["classification"],
        "n_trait_modules": len(rows),
        "rows": rows,
        "chapter2_endpoint": "ranked public-data candidate-and-limit map before Chapter 3 mechanism and fitness tests",
        "claim_boundary": "No row establishes selection, adaptation, convergence, exact transition timing or fitness. Missing comparability is retained as non-identifiability rather than a biological null.",
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    write_markdown(rows, origin, args.out_md)

    print(json.dumps({
        "status": "ok",
        "orientation_classification": result["orientation_origin_envelope_classification"],
        "n_trait_modules": len(rows),
        "final_classes": {r["trait_module"]: r["final_result_class"] for r in rows},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
