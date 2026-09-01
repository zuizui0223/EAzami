#!/usr/bin/env python3
"""Build the final Chapter 2 public-data integration after the focal colour bridge.

This is a synthesis layer over frozen lower-level evidence. It does not rerun or
rescore trait analyses. The builder combines the orientation origin-envelope
result, the two dated-sister public-image phenotype result, the focal colour-RSDS
replication, and the existing Chapter 2 triangulation matrix.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "data" / "evidence"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def orientation_p(origin: dict[str, Any]) -> tuple[str, str, str]:
    cls = origin["cross_scenario_summary"]["classification"]
    if cls == "robust_state_trajectory_concordance_under_scenario_envelope":
        return (
            "supported_observational_alignment",
            "current_hydric_sorting_and_historical_origin_trajectory_concordant",
            "ST1_persistent_driver_strengthened_observationally",
        )
    if cls == "robust_state_trajectory_discordance_under_scenario_envelope":
        return (
            "supported_observational_discordance",
            "current_hydric_sorting_and_historical_origin_trajectory_opposed",
            "ST2_origin_maintenance_decoupling_prioritized",
        )
    if cls == "origin_trajectory_unresolved_under_public_chronology_and_paleolocation_uncertainty":
        return (
            "unresolved_under_chronology_and_paleolocation",
            "current_hydric_domain_concordance_but_origin_trajectory_unresolved",
            "ST1_vs_ST2_vs_ST3_not_identifiable",
        )
    raise ValueError(cls)


def build_rows(origin: dict[str, Any], image: dict[str, Any], rsds: dict[str, Any], tri: list[dict[str, str]]) -> list[dict[str, str]]:
    by = {(r["trait_id"], r["factor_domain"]): r for r in tri}
    hydric = by[("orientation", "hydric_regime")]
    thermal = by[("orientation", "thermal_regime")]
    phyllary = by[("phyllary_posture", "enemy_access_wetting")]
    sticky = by[("stickiness", "enemy_community_and_cost")]
    outline = by[("capitulum_outline_shape", "multivariate_environment")]
    whole = by[("whole_capitulum", "common_lability_or_single_syndrome")]

    p_status, relation, process = orientation_p(origin)
    cross = origin["cross_scenario_summary"]
    c = cross["cosine_similarity"]
    pc = cross["cosine_null_percentile"]
    colour_cls = rsds["chapter_summary"]["classification"]
    if colour_cls != "partial_current_rsds_chroma_directional_concordance":
        raise AssertionError(f"unexpected colour RSDS class: {colour_cls}")
    if image["colour_assay_gate"]["passed"] is not True:
        raise AssertionError("colour assay gate must pass before final integration")

    common = {"causal_claim_allowed": "no"}
    rows = [
        {
            **common,
            "priority_rank": "1",
            "trait_driver": "orientation × hydric exposure",
            "R_repeated_history": "strong: ML minimum 6; UFBoot minimum 4-6",
            "T_timing": "strong relative history; core-Nipponocirsium origin is bounded by a cross-study parent/child chronology scenario envelope, not an exact event age",
            "S_azami_spatial": hydric["azami_spatial_evidence"],
            "C_current_ecology": hydric["eazami_present_ecology"],
            "L_mechanism_prior": hydric["mechanism_prior"],
            "P_historical_environment": p_status,
            "F_focal_fitness": "missing: no ancestry-matched orientation -> wetting/pollen/effective contact -> viable-seed chain",
            "space_time_relation": relation,
            "process_model": process,
            "final_class": "history_resolved_current_hydric_candidate_origin_driver_unresolved" if p_status.startswith("unresolved") else relation,
            "key_quantitative_result": f"origin-envelope cosine q05={c['q05']:.4f}; median={c['median']:.4f}; q95={c['q95']:.4f}; null-percentile median={pc['median']:.4f}; class={cross['classification']}",
            "public_data_ceiling": "repeated history and current hydric correspondence are resolved more strongly than the ancestral exposure; exact transition instant, ancestral area and focal fitness remain missing",
            "chapter3_decisive_test": "gravity-calibrated orientation manipulation with rain shielding/sham controls; quantify flower wetting, pollen retention/viability, effective pollinator contact and mature viable seed in ancestry-matched replicated U/D populations",
        },
        {
            **common,
            "priority_rank": "2",
            "trait_driver": "flower colour × radiative environment",
            "R_repeated_history": "partial lineage-level replication: two publicly dated white-coloured sister systems independently recover the expected lower-chroma white state; a general East-Asian colour-transition count is not identified",
            "T_timing": "dated split contexts approximately 0.93 Ma (Arenicola) and 0.35 Ma (Taiwan), but neither split age is an exact colour-transition date",
            "S_azami_spatial": "strong global Azami among-taxon result: higher current CHELSA RSDS aligns with lower visible corolla Lab chroma (beta=-0.345372, q=0.006; broad-space beta=-0.712411, P=0.001)",
            "C_current_ecology": "lineage- and scale-dependent: Arenicola white lineage has higher RSDS and lower chroma (Azami-concordant), Taiwan white lineage has lower RSDS and lower chroma (taxon-pair reversal); pooled within-taxon beta=-0.4065, two-sided permutation P=0.1141, prespecified negative one-sided P=0.0361",
            "L_mechanism_prior": "visible/UV optical signalling, pigment physiology and irradiance responses are plausible, but visible JPEG-derived chroma does not identify pigment concentration, UV absorption or the selected mediator",
            "P_historical_environment": "not_evaluable_directly: no admitted historical surface-RSDS equivalent and no general morph-linked colour-transition chronology; current CHELSA RSDS must not be read as transition-time radiation",
            "F_focal_fitness": "missing: no ancestry-resolved irradiance/pigment/optical mediator -> reproductive-fitness experiment",
            "space_time_relation": "global among-taxon negative direction; Arenicola pair concordant; Taiwan pair discordant even after 0.05-degree locality aggregation; pooled within-taxon direction negative",
            "process_model": "universal_ST1_persistent_RSDS_driver_weakened; ST2 origin-maintenance decoupling, ST3 driver switching and hierarchical scale dependence remain open",
            "final_class": "replicated_white_state_current_RSDS_lineage_scale_dependent_historical_driver_unresolved",
            "key_quantitative_result": "white-minus-coloured chroma=-2.95 Arenicola and -6.16 Taiwan; RSDS contrast=+1814 Arenicola but -686.5 Taiwan; current pair concordance=1/2",
            "public_data_ceiling": "the repeated extant colour phenotype is recoverable in two dated lineage comparisons, but a universal current radiative explanation is falsified at the pair level and historical radiative causation is not identifiable",
            "chapter3_decisive_test": "use Arenicola and Taiwan as an intentional matched contrast: collect morph-linked genomes, calibrated visible/UV reflectance and pigment chemistry; measure floral temperature/photodamage and pollinator perception; manipulate irradiance/shading and quantify viable seed to distinguish shared mechanism from driver switching",
        },
        {
            **common,
            "priority_rank": "3",
            "trait_driver": "phyllary posture × enemy/wetting/access pathways",
            "R_repeated_history": "strong: exactly 3 minimum changes across ML and all 1000 UFBoot trees",
            "T_timing": phyllary["eazami_relative_timing"],
            "S_azami_spatial": phyllary["azami_spatial_evidence"],
            "C_current_ecology": phyllary["eazami_present_ecology"],
            "L_mechanism_prior": phyllary["mechanism_prior"],
            "P_historical_environment": "not_evaluable: no homologous posture-to-dated-environment event series",
            "F_focal_fitness": "missing",
            "space_time_relation": "measurement ontology prevents valid spatial-history concordance test",
            "process_model": "multiple_mechanisms_open",
            "final_class": "history_resolved_cause_unidentified",
            "key_quantitative_result": "3 minimum changes; deeper and terminal placements admissible",
            "public_data_ceiling": "history is resolved better than driver identity; image involucre geometry is not a substitute for botanical posture",
            "chapter3_decisive_test": "botanically calibrate phyllary posture and experimentally separate rain entry, enemy access, pollinator access and mechanical protection with viable-seed endpoints",
        },
        {
            **common,
            "priority_rank": "4",
            "trait_driver": "stickiness × biotic enemy/cost regime",
            "R_repeated_history": "strong: exactly 5 minimum changes across ML and all 1000 UFBoot trees",
            "T_timing": sticky["eazami_relative_timing"],
            "S_azami_spatial": sticky["azami_spatial_evidence"],
            "C_current_ecology": sticky["eazami_present_ecology"],
            "L_mechanism_prior": sticky["mechanism_prior"],
            "P_historical_environment": "not_evaluable: no historical enemy/community or secretion-cost time series",
            "F_focal_fitness": "missing; close-genus generic-defence evidence includes a neutralization null",
            "space_time_relation": "repeated shallow history without a commensurate public biotic driver axis",
            "process_model": "local_biotic_selection_mosaic_candidate_generic_defence_weakened",
            "final_class": "rapid_history_resolved_biotic_driver_unidentified",
            "key_quantitative_result": "5 changes; shallow/terminal mean relative-depth approximately 0.94-0.95",
            "public_data_ceiling": "rapid lineage-local reassembly is identifiable; selective agent and benefit-cost balance are not",
            "chapter3_decisive_test": "reversible neutralization/restoration with sham in ancestry-matched sticky/nonsticky populations; quantify enemies, damage, pollinator handling, production cost and mature viable seed",
        },
        {
            **common,
            "priority_rank": "5",
            "trait_driver": "orientation × thermal regime",
            "R_repeated_history": "same strong 4-6 orientation history",
            "T_timing": thermal["eazami_relative_timing"],
            "S_azami_spatial": thermal["azami_spatial_evidence"],
            "C_current_ecology": thermal["eazami_present_ecology"],
            "L_mechanism_prior": thermal["mechanism_prior"],
            "P_historical_environment": "unresolved; current within-taxon and among-lineage signs do not define transition-time thermal causation",
            "F_focal_fitness": "missing",
            "space_time_relation": "within-taxon Azami BIO1 and among-lineage EAzami BIO1 point in different directions",
            "process_model": "scale_dependent_or_confounded_competing_axis",
            "final_class": "directional_mismatch_to_explain",
            "key_quantitative_result": "EAzami downward-minus-upward BIO1 negative; Azami within-taxon broad-space association positive",
            "public_data_ceiling": "temperature remains a competing axis but cannot be promoted to a universal cold-orientation explanation",
            "chapter3_decisive_test": "measure flowering-season temperature, snow/rain and head microclimate on matched lineages; test thermal mediation separately from wetting and elevation proxies",
        },
        {
            **common,
            "priority_rank": "6",
            "trait_driver": "outline/head packing × multivariate environment",
            "R_repeated_history": "general continuous evolutionary history unresolved; however two dated white-coloured sister systems show repeated extant coarse directions",
            "T_timing": "dated lineage comparison contexts exist, but simultaneous transitions of circularity/solidity/floret exposure are not reconstructed",
            "S_azami_spatial": outline["azami_spatial_evidence"],
            "C_current_ecology": "in both dated white lineages: circularity higher, solidity higher and visible floret fraction lower; detailed aspect/width and involucre projection/taper metrics are heterogeneous or low-information",
            "L_mechanism_prior": "packing/display geometry is functionally plausible but no single validated performance axis is assigned",
            "P_historical_environment": "not_evaluable",
            "F_focal_fitness": "missing",
            "space_time_relation": "partial repeated extant remodelling without a reconstructed shared historical event",
            "process_model": "coarse_head_remodelling_hypothesis_with_lineage_specific_fine_geometry",
            "final_class": "present_breadth_plus_replicated_coarse_extant_remodelling_history_unresolved",
            "key_quantitative_result": "white lineages show circularity +0.238/+0.159, solidity +0.092/+0.099 and visible-floret fraction -0.305/-0.028 in Arenicola/Taiwan",
            "public_data_ceiling": "coarse repeated phenotype direction is measurable; correlated transition order, developmental coupling and selection are not",
            "chapter3_decisive_test": "collect calibrated 3-D/2-D capitulum geometry on ancestry-resolved material and test whether packing/display changes share development or function with colour while retaining lineage-specific fine architecture",
        },
        {
            **common,
            "priority_rank": "synthesis",
            "trait_driver": "whole capitulum × common syndrome versus modular mosaic",
            "R_repeated_history": whole["eazami_repeat_count"],
            "T_timing": whole["eazami_relative_timing"],
            "S_azami_spatial": whole["azami_spatial_evidence"],
            "C_current_ecology": "partial integration: two independently dated white lineages share low chroma/high lightness plus coarse circularity/solidity/floret-exposure directions, while fine architecture is heterogeneous and discrete orientation/phyllary/stickiness histories remain asynchronous",
            "L_mechanism_prior": "no single mechanism is expected to explain all modules; partial developmental or ecological coupling remains possible",
            "P_historical_environment": "not_applicable_as_one_shared_driver",
            "F_focal_fitness": "not closed at whole-capitulum level",
            "space_time_relation": "neither complete independence nor one synchronized syndrome: partial module covariation sits inside trait-specific histories and lineage-dependent environmental responses",
            "process_model": "modular_hierarchical_selection_mosaic_with_partial_coordinated_remodelling",
            "final_class": "partial_module_covariation_universal_synchronized_syndrome_not_supported",
            "key_quantitative_result": "zero of three discrete trait pairs passes robust shared-transition localization; present 18-D within-among association rho=0.3663; two white sister systems replicate three coarse non-colour directions",
            "public_data_ceiling": "public data identify asymmetric evolutionary depth and hierarchical environmental correspondence but cannot separate shared development, pleiotropy, correlated selection or independent response",
            "chapter3_decisive_test": "measure multiple modules on the same ancestry-resolved individuals/populations and experimentally perturb focal drivers to test whether covariance is causal, developmental, selectively correlated or incidental",
        },
    ]
    return rows


def build_story(rows: list[dict[str, str]], origin: dict[str, Any], image: dict[str, Any], rsds: dict[str, Any]) -> str:
    cross = origin["cross_scenario_summary"]
    colour = rsds["chapter_summary"]
    return f"""# Chapter 2 public-data final story and analysis plan v3

Status: 2026-09-01  
Supersedes: `PUBLIC_DATA_FINAL_CHAPTER2_STORY_AND_ANALYSIS_PLAN_V2.md` for the final synthesis layer.

## Chapter question

> **How deep is capitulum diversity in evolutionary time, what geographic and environmental processes accompanied its assembly, and does the same putative driver explain the origin, present maintenance/sorting and repeated occurrence of a phenotype across lineages?**

Chapter 1 / Azami measures breadth across present environmental state space. Chapter 2 uses public phylogeny, dated lineage comparisons, public images, occurrences and palaeoenvironmental series to push from pattern toward historical explanation. Chapter 3 begins where public data stop: direct exposure, mechanism and reproductive fitness on ancestry-resolved samples.

## What changed in v3

The colour bridge adds a new type of evidence that was absent from v2. Two publicly dated white-coloured sister systems recover the same extant colour direction: both white lineages are lower in visible Lab chroma and higher in lightness. They also share coarse non-colour directions—higher circularity, higher solidity and lower visible floret fraction—while finer outline and involucre metrics are heterogeneous.

However, the frozen Azami `higher RSDS -> lower chroma` direction is **not** universal across the two lineage comparisons. Arenicola is concordant, whereas the Taiwan pair reverses the current RSDS contrast even after locality aggregation. The pooled within-taxon slope remains negative (`beta={colour['pooled_within_taxon_secondary']['beta_std']:.4f}`, expected-negative permutation `P={colour['pooled_within_taxon_secondary']['permutation_p_expected_negative']:.4f}`), but that secondary scale does not override the prespecified 1/2 taxon-pair result.

This creates a direct empirical example of hierarchical scale dependence: a global among-taxon association, local within-taxon response and sister-lineage state contrast need not have identical signs.

## Evidence chain

1. **R — recurrence / replicated history:** how often must the phenotype change, or where only a full history is unavailable, is the same extant phenotype independently recoverable in multiple dated lineage comparisons?
2. **T — temporal geometry:** are changes internal or terminal, and which lineages are bounded by public dates without pretending a split date is the trait-transition instant?
3. **S — present spatial breadth:** what does Azami recover across present environmental state space?
4. **C — current ecological correspondence:** does the same direction recur among focal lineages and within lineages, or is it scale/lineage dependent?
5. **P — historical trajectory:** do dated transition windows align with the candidate environmental trajectory after chronology, paleolocation and matched-window uncertainty?
6. **F — mechanism and fitness:** what remains impossible without own samples?

## Final process model

The public data no longer support treating `same phenotype = same driver` as a default assumption. The best current synthesis is:

> **Capitulum diversity is assembled modularly at different evolutionary depths, while environmental correspondence is hierarchical and lineage dependent. Some modules show broad present sorting, some show repeated historical reassembly, and similar extant phenotypes can occur under different lineage-level environmental states. This favours a modular hierarchical selection-mosaic model over one universal synchronized capitulum syndrome or one persistent driver for every repeated phenotype.**

This is an explanatory model, not proof of natural selection or adaptation.

## Orientation: strongest historical-depth module, origin environment still unresolved

Orientation requires 4–6 minimum changes. Present global and East-Asian evidence independently points to the hydric domain, but the chronology × paleolocation origin-envelope classification is `{cross['classification']}`. Therefore repeated history and current hydric sorting are better resolved than the actual ancestral exposure that generated the core-Nipponocirsium transition. A universal persistent-rainfall origin model is not established.

## Colour: repeated phenotype direction, non-universal current radiative context

The two dated sister comparisons recover the white-state phenotype in the same direction:

- Arenicola: chroma white-minus-coloured `-2.95`, lightness `+6.86`;
- Taiwan: chroma `-6.16`, lightness `+8.24`.

But current RSDS gives:

- Arenicola: white-minus-coloured `+1814` stored raster units, matching Azami's negative RSDS–chroma direction;
- Taiwan: `-686.5`, the opposite pair-level environmental direction, and `-1703` after 0.05-degree locality aggregation.

Thus the repeated white phenotype cannot currently be explained by one universal present-day RSDS rule. The main live explanations are origin–maintenance decoupling, driver switching, lineage-specific environmental covariance and scale-dependent sorting. Historical radiative causation remains non-identifiable because a directly comparable historical surface-RSDS series and general morph-linked colour transition history are absent.

## Whole capitulum: partial coordinated remodelling, not a universal syndrome

The two white sister systems add evidence for coarse repeated head remodelling—circularity and solidity increase while visible floret fraction decreases. Yet aspect/width metrics and detailed involucre projection/taper proxies are heterogeneous or low-information, and orientation, phyllary posture and stickiness have different historical counts and depth envelopes.

Therefore the current evidence rejects both extremes:

- **not one universal synchronized capitulum syndrome**, because histories and fine geometry differ;
- **not complete independence**, because some coarse head directions repeat with the colour state in two dated lineage systems.

The appropriate target for Chapter 3 is the mechanism generating partial module covariance.

## Final trait × driver classes

| rank | trait × driver | final public-data class |
|---:|---|---|
""" + "\n".join(f"| {r['priority_rank']} | {r['trait_driver']} | `{r['final_class']}` |" for r in rows) + """

## Why BM/OU remain secondary

BM/OU are useful baselines only for a commensurate continuous phenotype with adequate dated-tip coverage. They do not answer the current central question—whether repeated trait changes or repeated extant states occur under the same environmental process. For discrete histories, branch/event models are primary; for colour and coarse image geometry, additional morph-linked dated sampling is required before moving-optimum or regime models are identifiable.

## Chapter 3 priorities generated by Chapter 2

1. **Orientation × hydric exposure:** close the strongest missing causal chain from actual wetting through pollen/effective contact to viable seed.
2. **Arenicola versus Taiwan colour natural experiment:** deliberately exploit the same white-state phenotype under opposite current pair-level RSDS contrasts. Test whether pigment/genetic mechanism is shared while selective environment differs, or whether both mechanism and driver differ.
3. **Coarse head remodelling:** determine whether circularity/solidity/floret exposure covary through shared development, correlated selection or image-level geometry only.
4. **Phyllary and stickiness:** test competing enemy, wetting, access and cost mechanisms rather than borrowing climate associations from other modules.

## Public-data stop rule

Chapter 2 stops where the remaining claim would require one of the following unavailable links: exact trait-transition timing, ancestral location, homologous historical environmental exposure, direct functional mediator or reproductive fitness. Missing identification is retained as a result, not converted into `no effect`.

## Claim ceiling

The synthesis supports repeated history, replicated extant phenotype directions, scale-dependent current environmental correspondence and explicit non-identifiability boundaries. It does **not** establish adaptation, convergence, common developmental mechanism, event-specific environmental causation or reproductive-fitness benefit.
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--orientation-origin", type=Path, required=True)
    ap.add_argument("--out-csv", type=Path, required=True)
    ap.add_argument("--out-json", type=Path, required=True)
    ap.add_argument("--out-story", type=Path, required=True)
    args = ap.parse_args()

    origin = read_json(args.orientation_origin)
    image = read_json(EVID / "chapter2_four_taxon_azami_measurement_result_v1.json")
    rsds = read_json(EVID / "chapter2_colour_rsds_focal_concordance_result_v1.json")
    tri = read_csv(EVID / "chapter2_selection_pressure_triangulation_v1.csv")
    rows = build_rows(origin, image, rsds, tri)

    write_csv(args.out_csv, rows)
    payload = {
        "contract_version": "chapter2_final_integrated_evidence_v3",
        "status_date": "2026-09-01",
        "orientation_origin_classification": origin["cross_scenario_summary"]["classification"],
        "colour_public_image_assay_gate": image["colour_assay_gate"]["passed"],
        "colour_current_rsds_classification": rsds["chapter_summary"]["classification"],
        "n_rows": len(rows),
        "rows": rows,
        "chapter_model": "modular_hierarchical_selection_mosaic_with_partial_coordinated_remodelling",
        "claim_boundary": "No row establishes adaptation, convergence, common developmental mechanism, exact event-specific environmental causation or reproductive-fitness benefit.",
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    args.out_story.parent.mkdir(parents=True, exist_ok=True)
    args.out_story.write_text(build_story(rows, origin, image, rsds), encoding="utf-8")

    print(json.dumps({
        "status": "ok",
        "orientation_origin": payload["orientation_origin_classification"],
        "colour_rsds": payload["colour_current_rsds_classification"],
        "chapter_model": payload["chapter_model"],
        "classes": {r["trait_driver"]: r["final_class"] for r in rows},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
