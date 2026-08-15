#!/usr/bin/env python3
import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def nonempty(value):
    return bool((value or "").strip())


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--matrix", default="data/evidence/micro_to_macro_evidence_matrix_v1.csv")
    p.add_argument("--atlas", default="data/evidence/cirsium_flower_colour_atlas_v0_2.csv")
    p.add_argument("--origin", default="data/evidence/japan_cirsium_origin_meta_analysis_v1.json")
    p.add_argument("--takaoense", default="analysis/chang2026_takaoense_topology_robustness_summary.json")
    p.add_argument("--output", required=True)
    args = p.parse_args()

    matrix = read_csv(args.matrix)
    atlas = read_csv(args.atlas)
    origin = load_json(args.origin)
    tak = load_json(args.takaoense)

    class_counts = Counter(r["evidence_class"] for r in matrix)
    scale_counts = Counter(r["scale"] for r in matrix)
    groups_by_class = defaultdict(set)
    for row in matrix:
        if nonempty(row.get("data_generation_group")):
            groups_by_class[row["evidence_class"]].add(row["data_generation_group"])

    reviewed_taxon = [
        r for r in atlas
        if r.get("observation_unit") == "taxon"
        and r.get("review_status") == "reviewed"
        and r.get("assessable") == "yes"
    ]
    taxon_state_counts = Counter(r.get("binary_colour_code", "") for r in reviewed_taxon)
    recurrent_contexts = sorted({
        r.get("phylogeny_context", "").strip()
        for r in reviewed_taxon
        if r.get("binary_colour_code") in {"W", "P"}
        and nonempty(r.get("phylogeny_context"))
    })
    polymorphic_taxa = sorted({
        r.get("accepted_taxon", "").strip()
        for r in reviewed_taxon
        if r.get("binary_colour_code") == "P"
        and nonempty(r.get("accepted_taxon"))
    })

    tak_samples = [
        r for r in atlas
        if r.get("accepted_taxon") == "Cirsium japonicum var. takaoense"
        and r.get("observation_unit") == "sample"
        and r.get("review_status") == "reviewed"
        and r.get("assessable") == "yes"
    ]
    tak_sample_states = Counter(r.get("binary_colour_code", "") for r in tak_samples)

    dominant = origin["dominant_main_radiation"]
    lineare = origin["cirsium_lineare"]
    dips = origin["cirsium_dipsacolepis"]
    aren = origin["arenicola"]

    problems = {
        "P_MACRO_01_colonization_diversification_asymmetry": {
            "basis": "EAzami Japan-origin meta-analysis",
            "result": f"{dominant['species_in_main_radiation']}/{dominant['japanese_species_sampled']} sampled Japanese species are in one dominant radiation while rare exceptional histories remain",
            "why_problem": "arrival count is not equivalent to diversification success",
            "hypothesis": "HMM3",
        },
        "P_MACRO_02_topology_direction_identifiability": {
            "basis": "EAzami exhaustive takaoense topology screen",
            "result": f"{tak['all_topologies_regain_required_count']}/{tak['rooted_binary_topology_count']} rooted resolutions require regain; the rest permit a no-regain optimum",
            "why_problem": "directional trait-history claims depend on topology support, not phenotype coding alone",
            "hypothesis": "HMM1|HMM2",
        },
        "P_MACRO_03_species_tip_state_aggregation": {
            "basis": "EAzami colour atlas + preliminary Fitch screen",
            "result": f"reviewed source-backed polymorphic taxon records={len(polymorphic_taxa)}; takaoense sample states W={tak_sample_states.get('W',0)} C={tak_sample_states.get('C',0)}",
            "why_problem": "one-state-per-species coding can erase within-lineage transitions",
            "hypothesis": "HMM2",
        },
        "P_MACRO_04_evidence_nonindependence": {
            "basis": "EAzami source-typed evidence matrix",
            "result": f"published rows={class_counts.get('published_conclusion',0)} but independent published data-generation groups={len(groups_by_class.get('published_conclusion',set()))}",
            "why_problem": "paper counts and accession rows can overstate independent replication",
            "hypothesis": "HMM3|HMM4",
        },
        "P_MACRO_05_phenotype_mechanism_scale_gap": {
            "basis": "EAzami source-backed colour atlas + molecular literature",
            "result": f"white/polymorphic states occur across {len(recurrent_contexts)} reviewed phylogeny-context labels, while causal molecular mechanisms are not comparably resolved across those lineages",
            "why_problem": "phenotypic convergence can be strong even when molecular convergence is unknown or heterogeneous",
            "hypothesis": "HMM1|HMM5",
        },
    }

    hypotheses = {
        "HMM1": {
            "name": "latent-pathway / regulatory reversibility",
            "derived_from": ["P_MACRO_02_topology_direction_identifiability", "P_MACRO_05_phenotype_mechanism_scale_gap"],
            "prediction": "recent independent white lineages often retain structural flavonoid machinery and differ at regulatory/expression nodes more often than by shared destructive pathway loss",
            "falsifier": "multiple well-resolved recent white lineages independently show irreversible loss/disruption of core pathway genes with no retained functional route",
        },
        "HMM2": {
            "name": "population-aware transition-rate inflation relative to species-tip coding",
            "derived_from": ["P_MACRO_02_topology_direction_identifiability", "P_MACRO_03_species_tip_state_aggregation"],
            "prediction": "population/sample-aware coding yields more and younger W<->C transitions than one-state-per-species coding across replicated polymorphic systems",
            "falsifier": "after topology uncertainty is propagated, population-aware coding does not increase transition count or shifts only one idiosyncratic system",
        },
        "HMM3": {
            "name": "radiation-success / evolvability",
            "derived_from": ["P_MACRO_01_colonization_diversification_asymmetry", "P_MACRO_04_evidence_nonindependence"],
            "prediction": "the dominant Japanese radiation shows higher genomic discordance/reticulation and-or faster trait or niche diversification than secondary histories after age and sampling controls",
            "falsifier": "secondary histories show comparable evolvability metrics and diversification after age/sampling correction, leaving colonization timing/opportunity sufficient",
        },
        "HMM4": {
            "name": "reticulation-phenotypic-transition coupling",
            "derived_from": ["P_MACRO_01_colonization_diversification_asymmetry", "P_MACRO_04_evidence_nonindependence"],
            "prediction": "lineage-level gene-tree/cytonuclear discordance and ploidy/genome-size shifts positively covary with population-aware floral transition density",
            "falsifier": "transition density is unrelated or negatively related to discordance across supported topology ensembles and leave-one-clade-out analyses",
        },
        "HMM5": {
            "name": "phenotypic convergence / molecular heterogeneity",
            "derived_from": ["P_MACRO_05_phenotype_mechanism_scale_gap"],
            "prediction": "convergence is stronger at phenotype/pathway/module level than at exact gene/nucleotide level across independent white systems",
            "falsifier": "the same causal gene and homologous mutation class repeatedly explains independent white systems more strongly than module-level heterogeneity",
        },
    }

    result = {
        "contract_version": "micro_to_macro_evidence_synthesis_v1",
        "evidence_matrix": {
            "rows": len(matrix),
            "class_counts": dict(sorted(class_counts.items())),
            "scale_counts": dict(sorted(scale_counts.items())),
            "independent_data_generation_groups_by_class": {
                k: sorted(v) for k, v in sorted(groups_by_class.items())
            },
        },
        "macro_trait_atlas": {
            "reviewed_assessable_taxon_records": len(reviewed_taxon),
            "taxon_state_counts": dict(sorted(taxon_state_counts.items())),
            "white_or_polymorphic_phylogeny_contexts": recurrent_contexts,
            "polymorphic_taxa": polymorphic_taxa,
            "takaoense_reviewed_sample_records": len(tak_samples),
            "takaoense_sample_state_counts": dict(sorted(tak_sample_states.items())),
        },
        "japan_origin_meta": {
            "dominant_radiation_fraction": dominant["proportion_in_main_radiation"],
            "dominant_radiation_species": dominant["species_in_main_radiation"],
            "japanese_species_sampled": dominant["japanese_species_sampled"],
            "lineare_analysis_support": [lineare["analyses_supporting"], lineare["analyses_tested"]],
            "lineare_independent_group_support": [lineare["data_generation_groups_supporting"], lineare["data_generation_groups_tested"]],
            "dipsacolepis_independent_groups": dips["data_generation_groups_supporting"],
            "arenicola_extra_colonization_supporting_analyses": aren["analyses_supporting"],
        },
        "takaoense_topology_meta": {
            "rooted_topologies": tak["rooted_binary_topology_count"],
            "regain_required": tak["all_topologies_regain_required_count"],
            "regain_required_fraction": tak["all_topologies_regain_required_fraction"],
            "published_history": tak["published_optimal_histories"],
            "published_no_regain_penalty": tak["published_no_regain_penalty"],
            "bp_monophyletic_regain_required": [tak["bp_monophyletic_regain_required_count"], tak["bp_monophyletic_topology_count"]],
            "w_monophyletic_regain_required": [tak["w_monophyletic_regain_required_count"], tak["w_monophyletic_topology_count"]],
        },
        "EAzami_discovered_problems": problems,
        "EAzami_hypotheses": hypotheses,
        "claim_boundary": "Published conclusions, EAzami reanalysis findings, and EAzami hypotheses are stored separately. Hypotheses are derived from EAzami-observed cross-scale problems; they are not copied from the future-work sections of source papers.",
    }

    Path(args.output).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
