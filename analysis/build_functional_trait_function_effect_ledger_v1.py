from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLLINATOR = ROOT / "data/evidence/experimental_pollinator_selection_gradients_v1.csv"
HERBIVORY = ROOT / "data/evidence/cirsium_floral_herbivory_lnrr_meta_v2.json"
ORIENTATION = ROOT / "data/evidence/orientation_mechanism_reduction_targets_v1.csv"
PATTERNS = ROOT / "data/evidence/interaction_quantitative_pattern_ledger_v1.csv"
MULTIAGENT = ROOT / "data/evidence/multiagent_floral_selection_mosaic_registry_v1.csv"
ASSURANCE = ROOT / "data/evidence/cirsium_pollinator_assurance_meta_v1.csv"
DEMOGRAPHY = ROOT / "data/evidence/cirsium_demographic_transmission_meta_v1.csv"

PIGMENT_TRAITS = {"petal_brightness", "petal_chroma", "lip_patch_size", "lip_patch_contrast", "lip_spot_area"}
SIZE_TRAITS = {"corolla_size", "corolla_area", "corolla_projected_area", "flower_size"}

FIELDS = [
    "effect_id", "source_family", "source_row_id", "taxon", "module", "function_axis", "agent",
    "causal_stage", "evidence_design", "metric_family", "estimate", "se", "lower", "upper",
    "direction", "fitness_endpoint", "independence_cluster", "poolable_group", "poolability",
    "source", "notes", "claim_boundary"
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def pollinator_module(row: dict[str, str]) -> tuple[str, str] | None:
    if row["included_primary"] != "1":
        return None
    if row["functional_class"] == "plant_display":
        return "display_quantity", "pollinator_mediated_selection"
    if row["trait"] in PIGMENT_TRAITS:
        return "flower_colour_pigmentation", "pollinator_sensory_selection"
    if row["trait"] in SIZE_TRAITS:
        return "capitulum_or_flower_size_proxy", "pollinator_attraction_selection"
    if row["functional_class"] == "pollination_efficiency":
        return "pollination_efficiency_reference", "pollination_efficiency_selection"
    return None


def add_pollinator_rows(out: list[dict[str, str]]) -> None:
    for row in read_csv(POLLINATOR):
        mapping = pollinator_module(row)
        if mapping is None:
            continue
        module, axis = mapping
        out.append({
            "effect_id": f"POLL_{row['study_id']}",
            "source_family": "experimental_pollinator_selection_gradients_v1",
            "source_row_id": row["study_id"],
            "taxon": row["taxon"],
            "module": module,
            "function_axis": axis,
            "agent": "pollinator",
            "causal_stage": "agent_mediated_trait_to_fitness_selection",
            "evidence_design": "experimental_pollinator_mediation_standardized_selection_gradient",
            "metric_family": "delta_beta_standardized_directional_selection",
            "estimate": row["delta_beta"],
            "se": row["se_delta"],
            "lower": "",
            "upper": "",
            "direction": "positive" if float(row["delta_beta"]) > 0 else "negative" if float(row["delta_beta"]) < 0 else "null",
            "fitness_endpoint": row["fitness_endpoint"],
            "independence_cluster": row["article_cluster"],
            "poolable_group": f"pollinator_delta_beta::{module}",
            "poolability": "article_cluster_poolable_within_metric_family",
            "source": row["source_doi"],
            "notes": f"trait={row['trait']}; context={row['context']}; function_confidence={row['function_confidence']}",
            "claim_boundary": "Analog from non-Cirsium flowering plants; estimates pollinator-mediated selection, not a direct trait->mechanism response ratio."
        })


def add_herbivory_rows(out: list[dict[str, str]]) -> None:
    data = json.loads(HERBIVORY.read_text(encoding="utf-8"))
    for row in data["effect_level"]:
        out.append({
            "effect_id": f"HERB_{row['effect_id']}",
            "source_family": "cirsium_floral_herbivory_lnrr_meta_v2",
            "source_row_id": row["effect_id"],
            "taxon": row["taxon"],
            "module": "cross_module_antagonist_pressure",
            "function_axis": "reproductive_antagonist_cost",
            "agent": "reproductive_antagonist",
            "causal_stage": "agent_to_seed_fitness",
            "evidence_design": "experimental_reduced_vs_ambient_insect_herbivory",
            "metric_family": "lnRR_seed_output_reduced_vs_ambient_herbivory",
            "estimate": str(row["lnRR"]),
            "se": str(math.sqrt(float(row["var_lnRR"]))),
            "lower": "",
            "upper": "",
            "direction": "positive_reduced_herbivory",
            "fitness_endpoint": "viable_or_mature_seed_output",
            "independence_cluster": row["study"],
            "poolable_group": "antagonist_lnRR_seed_output",
            "poolability": "study_cluster_poolable_direct_effect",
            "source": row["source"],
            "notes": f"response_ratio={row['response_ratio']}; stratum={row['stratum']}",
            "claim_boundary": "Quantifies antagonist fitness cost, not the adaptive effect of any particular capitulum trait."
        })


def add_orientation_rows(out: list[dict[str, str]]) -> None:
    for row in read_csv(ORIENTATION):
        metric = row["metric"]
        exactness = "threshold_or_sign_anchor"
        poolability = "nonpoolable_structured_anchor"
        causal_stage = "trait_or_exposure_to_function"
        endpoint = "mechanism_or_fitness"
        if row["target_id"] == "OR_CREM_ACHENE":
            exactness = "direct_trait_manipulation_fitness_effect"
            poolability = "single_study_direct_effect_not_meta_ready"
            causal_stage = "trait_to_seed_fitness"
            endpoint = "achene_set"
        elif row["target_id"] == "OR_CREM_POLL_NULL":
            exactness = "direct_trait_manipulation_mechanism_null"
            poolability = "single_study_direct_effect_not_meta_ready"
            causal_stage = "trait_to_pollinator_preference"
            endpoint = "pollinator_preference"
        out.append({
            "effect_id": f"ORI_{row['target_id']}",
            "source_family": "orientation_mechanism_reduction_targets_v1",
            "source_row_id": row["target_id"],
            "taxon": row["system"],
            "module": "orientation",
            "function_axis": row["pathway"],
            "agent": "abiotic_or_pollinator",
            "causal_stage": causal_stage,
            "evidence_design": exactness,
            "metric_family": metric,
            "estimate": row["target_value"],
            "se": "",
            "lower": row["lower_bound"],
            "upper": row["upper_bound"],
            "direction": row["direction"],
            "fitness_endpoint": endpoint,
            "independence_cluster": row["source_ref"],
            "poolable_group": "",
            "poolability": poolability,
            "source": row["source_ref"],
            "notes": row["notes"],
            "claim_boundary": "Several orientation targets are transfer thresholds/sign anchors; only explicitly identified direct contrasts may be treated as quantitative effects."
        })


def add_pattern_rows(out: list[dict[str, str]]) -> None:
    keep = {"IQ01", "IQ02", "IQ03", "IQ04", "IQ05", "IQ06", "IQ13", "IQ17", "IQ22"}
    module_map = {
        "IQ01": ("display_quantity", "pollinator_attraction"),
        "IQ02": ("display_quantity", "pollinator_probing"),
        "IQ03": ("display_quantity", "antagonist_apparency"),
        "IQ04": ("display_quantity", "antagonist_apparency"),
        "IQ05": ("display_quantity", "antagonist_damage"),
        "IQ06": ("flower_colour_pigmentation", "pollinator_colour_preference"),
        "IQ13": ("stickiness_mucilage", "antagonist_exclusion"),
        "IQ17": ("capitulum_or_flower_size_proxy", "antagonist_oviposition"),
        "IQ22": ("reproductive_assurance", "pollinator_dependence")
    }
    for row in read_csv(PATTERNS):
        if row["pattern_id"] not in keep:
            continue
        module, axis = module_map[row["pattern_id"]]
        out.append({
            "effect_id": f"PAT_{row['pattern_id']}",
            "source_family": "interaction_quantitative_pattern_ledger_v1",
            "source_row_id": row["pattern_id"],
            "taxon": row["taxon_or_scope"],
            "module": module,
            "function_axis": axis,
            "agent": row["interaction_axis"],
            "causal_stage": "trait_or_interaction_pattern_to_function_or_fitness",
            "evidence_design": row["evidence_level"],
            "metric_family": row["metric"],
            "estimate": row["value"],
            "se": "",
            "lower": row["lower"],
            "upper": row["upper"],
            "direction": row["direction"],
            "fitness_endpoint": "mixed_or_process_specific",
            "independence_cluster": row["source"],
            "poolable_group": "",
            "poolability": "nonpoolable_metric_specific_anchor",
            "source": row["source"],
            "notes": row["notes"],
            "claim_boundary": "R2, regression coefficients, proportions, null tests and other metrics are retained as mechanism anchors and are not pooled across metric families."
        })


def add_structured_context_rows(out: list[dict[str, str]]) -> None:
    for row in read_csv(MULTIAGENT):
        out.append({
            "effect_id": f"MAS_{row['study_id']}", "source_family": "multiagent_floral_selection_mosaic_registry_v1", "source_row_id": row["study_id"],
            "taxon": row["taxon"], "module": "cross_module_selection_mosaic", "function_axis": "multiagent_selection_context", "agent": "pollinator_and_antagonist",
            "causal_stage": "selection_regime_context", "evidence_design": row["design"], "metric_family": "categorical_agent_dominance_context", "estimate": "", "se": "", "lower": "", "upper": "",
            "direction": row["agent_dominance"], "fitness_endpoint": row["fitness_scale"], "independence_cluster": row["program_cluster"], "poolable_group": "", "poolability": "structured_nonpoolable_context_prior",
            "source": row["source_doi"], "notes": row["quantitative_anchor"], "claim_boundary": row["claim_boundary"]
        })
    for row in read_csv(ASSURANCE):
        out.append({
            "effect_id": f"ASSURE_{row['study_id']}", "source_family": "cirsium_pollinator_assurance_meta_v1", "source_row_id": row["study_id"],
            "taxon": row["taxon_or_scope"], "module": "reproductive_assurance", "function_axis": "pollinator_dependence_and_assurance", "agent": "pollinator",
            "causal_stage": "interaction_opportunity_to_fitness_gate", "evidence_design": row["design"], "metric_family": "heterogeneous_assurance_evidence", "estimate": "", "se": "", "lower": "", "upper": "",
            "direction": row["pollinator_dependence"], "fitness_endpoint": "seed_output_or_fertilization", "independence_cluster": row["study_id"], "poolable_group": "", "poolability": "structured_nonpoolable_context_prior",
            "source": row["source"], "notes": row["quantitative_anchor"], "claim_boundary": row["claim_boundary"]
        })
    for row in read_csv(DEMOGRAPHY):
        out.append({
            "effect_id": f"DEMO_{row['study_id']}", "source_family": "cirsium_demographic_transmission_meta_v1", "source_row_id": row["study_id"],
            "taxon": row["taxon"], "module": "demographic_gate", "function_axis": "seed_to_recruitment_transmission", "agent": "demographic_context",
            "causal_stage": "seed_fitness_to_population_transmission", "evidence_design": row["design"], "metric_family": "heterogeneous_demographic_transmission", "estimate": "", "se": "", "lower": "", "upper": "",
            "direction": row["population_transmission"], "fitness_endpoint": "recruitment_or_population_growth", "independence_cluster": row["study_id"], "poolable_group": "", "poolability": "structured_nonpoolable_context_prior",
            "source": row["source"], "notes": row["quantitative_anchor"], "claim_boundary": row["claim_boundary"]
        })


def build_rows() -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    add_pollinator_rows(out)
    add_herbivory_rows(out)
    add_orientation_rows(out)
    add_pattern_rows(out)
    add_structured_context_rows(out)
    ids = [r["effect_id"] for r in out]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate effect_id in harmonized ledger")
    return out


def summarize(rows: list[dict[str, str]]) -> dict:
    poolability = Counter(r["poolability"] for r in rows)
    modules = Counter(r["module"] for r in rows)
    pool_groups: dict[str, set[str]] = defaultdict(set)
    for r in rows:
        if r["poolable_group"]:
            pool_groups[r["poolable_group"]].add(r["independence_cluster"])
    group_summary = {g: len(clusters) for g, clusters in sorted(pool_groups.items())}
    meta_ready = {g: k for g, k in group_summary.items() if k >= 3}
    return {
        "contract_version": "functional_trait_function_effect_ledger_v1",
        "row_count": len(rows),
        "module_row_counts": dict(sorted(modules.items())),
        "poolability_counts": dict(sorted(poolability.items())),
        "independent_cluster_counts_by_poolable_group": group_summary,
        "existing_meta_ready_groups_k_ge_3": meta_ready,
        "existing_gap_priorities": [
            "orientation: more direct manipulative trait->mechanism->fitness studies beyond the single Cremanthodium system",
            "phyllary/spine: direct manipulations or trait->antagonist-access->fitness studies",
            "stickiness/mucilage: independent direct neutralization/manipulation studies to test context dependence",
            "flower pigmentation: more independent pollinator-mediated selection studies and separate abiotic manipulation studies",
            "display: direct antagonist and joint pollinator-antagonist effect sizes on comparable fitness scales"
        ],
        "decision": "Existing data support several within-metric meta seeds, but no single cross-module scalar effect is scientifically authorized. The next literature search should be targeted to missing causal chains and under-replicated module-metric families.",
        "claim_boundary": "Poolability is defined by metric family, causal stage, module and independent study/article clustering; it is not evidence that pooled effects are exchangeable without further design and variance checks."
    }


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv-output", type=Path, required=True)
    parser.add_argument("--json-output", type=Path, required=True)
    args = parser.parse_args()
    rows = build_rows()
    write_csv(rows, args.csv_output)
    summary = summarize(rows)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
