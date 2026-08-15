#!/usr/bin/env python3
"""Extend micro-to-macro synthesis with staged HMM2 and molecular resolution evidence.

v3 never changes the provenance of HMM1-HMM6. New molecular results test/refine
existing hypotheses; they do not manufacture HMM7 merely because another
analysis layer was added.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path


def load_json(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_csv(path: str):
    with Path(path).open(encoding="utf-8-sig", newline="") as h:
        return list(csv.DictReader(h))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="data/evidence/micro_to_macro_evidence_synthesis_v2.json")
    ap.add_argument("--matrix", default="data/evidence/micro_to_macro_evidence_matrix_v3.csv")
    ap.add_argument("--hmm2", default="data/evidence/hmm2_population_aware_transition_test_v1.json")
    ap.add_argument("--bridge", default="data/evidence/cirsium_flavonoid_molecular_bridge_summary_v1.json")
    ap.add_argument("--annotation", default="data/evidence/cnipponicum_flavonoid_annotation_term_audit_v1.json")
    ap.add_argument("--blast", default="data/evidence/cnipponicum_flavonoid_blast_candidate_summary_v1.json")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    base = load_json(args.base)
    matrix = read_csv(args.matrix)
    hmm2 = load_json(args.hmm2)
    bridge = load_json(args.bridge)
    annotation = load_json(args.annotation)
    blast = load_json(args.blast)

    if base.get("contract_version") != "micro_to_macro_evidence_synthesis_v2":
        raise ValueError("v2 synthesis drift")
    if set(base["EAzami_hypotheses"]) != {"HMM1","HMM2","HMM3","HMM4","HMM5","HMM6"}:
        raise ValueError("hypothesis set drift")

    class_counts = Counter(r["evidence_class"] for r in matrix)
    scale_counts = Counter(r["scale"] for r in matrix)
    groups = defaultdict(set)
    for r in matrix:
        if r.get("data_generation_group"):
            groups[r["evidence_class"]].add(r["data_generation_group"])

    result = deepcopy(base)
    result["contract_version"] = "micro_to_macro_evidence_synthesis_v3"
    result["evidence_matrix"] = {
        "rows": len(matrix),
        "class_counts": dict(sorted(class_counts.items())),
        "scale_counts": dict(sorted(scale_counts.items())),
        "independent_data_generation_groups_by_class": {
            k: sorted(v) for k,v in sorted(groups.items())
        },
    }

    p7 = {
        "basis": "EAzami molecular coverage + public genome annotation + sequence-homology screens",
        "reported_panel_stage": {
            "terminal_regulatory_transport_families": bridge["micro_to_macro_gap"]["terminal_regulatory_transport_families"],
            "directly_reported_in_named_targeted_panels": bridge["micro_to_macro_gap"]["terminal_regulatory_transport_directly_reported"],
        },
        "distributed_genome_annotation_stage": {
            "protein_headers_scanned": annotation["protein_headers_scanned"],
            "gff_records_scanned": annotation["gff_records_scanned"],
            "functional_term_hit_rows": annotation["total_hit_rows"],
            "positive_controls_also_zero": all(annotation["term_hit_counts"][k] == 0 for k in ["CHS","FLS","DFR"]),
        },
        "sequence_homology_stage": {
            "reviewed_queries": blast["query_count"],
            "queries_with_candidate_hit": blast["queries_with_candidate_hit"],
            "DFR_top_candidate": blast["queries"]["DFR_TT3"]["top_subject"],
            "DFR_top_identity": blast["queries"]["DFR_TT3"]["top_pident"],
            "DFR_top_qcov": blast["queries"]["DFR_TT3"]["top_qcov"],
            "ANS_top_candidate": blast["queries"]["ANS_TT18"]["top_subject"],
            "ANS_top_identity": blast["queries"]["ANS_TT18"]["top_pident"],
            "ANS_top_qcov": blast["queries"]["ANS_TT18"]["top_qcov"],
            "large_family_queries_needing_clade_domain_validation": blast["large_family_queries_requiring_clade_or_domain_validation"],
        },
        "why_problem": "The apparent molecular gap changes qualitatively with evidence resolution: absence from a named pathway panel, absence of functional labels in distributed genome files, and absence of sequence homologs are not equivalent observations.",
        "hypothesis_tested": ["HMM1","HMM5"],
    }
    result["EAzami_discovered_problems"]["P_MICRO_MACRO_07_annotation_to_orthology_resolution_ladder"] = p7

    result["HMM2_staged_test"] = {
        "state_compression_systems": [
            hmm2["stage_A_state_compression"]["systems_exposing_W_C_multiplicity_hidden_by_one_P_tip"],
            hmm2["stage_A_state_compression"]["systems_total"],
        ],
        "transition_count_testable_systems": [
            hmm2["stage_B_minimum_transition_count"]["systems_with_morph_linked_nuclear_genealogy"],
            hmm2["stage_B_minimum_transition_count"]["systems_total"],
        ],
        "takaoense_minimum_transition_change": [
            hmm2["stage_B_minimum_transition_count"]["takaoense_species_tip_minimum"],
            hmm2["stage_B_minimum_transition_count"]["takaoense_population_sample_minimum"],
        ],
        "transition_rate_testable_systems": [
            hmm2["stage_C_transition_rate"]["systems_rate_testable_now"],
            hmm2["stage_C_transition_rate"]["systems_total"],
        ],
        "morph_genotype_linkage_fraction": hmm2["morph_genotype_linkage"]["systems_with_any_morph_linked_nuclear_samples"] / hmm2["focal_polymorphic_systems"],
        "status": hmm2["hmm2_current_status"],
    }

    result["molecular_resolution_ladder"] = {
        "named_targeted_panel": "terminal anthocyanin + MBW + transport direct named coverage 0/7",
        "distributed_genome_text_annotation": "0/13 requested functional term groups, including positive-control CHS/FLS/DFR; file exposes structural IDs rather than functional product labels",
        "sequence_homology": "11/11 reviewed query anchors recover at least one C. nipponicum candidate homolog under frozen BLASTP settings",
        "orthology_function": "not yet established; enzyme and large-family candidates require domain/clade/reciprocal validation",
        "colour_lineage_causation": "not yet tested; candidates must be compared across morph-linked W/C lineages and against genome-wide ancestry/expression/pigment evidence",
    }

    result["hypothesis_evidence_status"] = {
        "HMM1": {
            "status": "mechanistic_plausibility_strengthened_direct_white_lineage_test_unresolved",
            "supporting_EAzami_results": [
                "P_MACRO_05_phenotype_mechanism_scale_gap",
                "P_MICRO_MACRO_07_annotation_to_orthology_resolution_ladder",
            ],
            "what_changed": "Existing-data analysis now recovers Cirsium genome candidates for DFR, ANS and all seven previously unlabelled terminal/regulatory/transport query families. This makes retained machinery testable and argues against treating reporting/annotation gaps as pathway loss, but it does not show that a white lineage retains functional copies or that regulation caused white colour.",
            "next_falsification_gate": "validate candidate orthology/domain architecture, then test structural integrity/coding/expression in morph-linked white versus coloured lineages",
        },
        "HMM2": {
            "status": "partial_support_state_resolution_and_single_testable_transition_count_rate_hypothesis_unresolved",
            "supporting_EAzami_results": ["P_MACRO_03_species_tip_state_aggregation"],
            "what_changed": "4/4 reviewed polymorphic systems expose state compression; 1/1 currently morph-linked system increases minimum count from 1 to 2; 0/4 support a replicated branch-length transition-rate comparison.",
            "next_falsification_gate": "recover or generate morph-linked population genealogies for at least two additional polymorphic systems",
        },
        "HMM3": {"status": "unchanged_waiting_for_294_296_tree_and_age_sampling_control"},
        "HMM4": {"status": "unchanged_waiting_for_tree_discordance_and_transition_density_table"},
        "HMM5": {
            "status": "molecular_hierarchy_now_executable_cross_lineage_convergence_unresolved",
            "supporting_EAzami_results": [
                "P_MACRO_05_phenotype_mechanism_scale_gap",
                "P_MICRO_MACRO_07_annotation_to_orthology_resolution_ladder",
            ],
            "what_changed": "Candidate homologs are recoverable for terminal, regulatory and transport families, enabling gene/module-level comparisons; no replicated white-lineage mechanism set exists yet.",
            "next_falsification_gate": "validate ortholog/clade assignments and compare independent white systems at nucleotide, gene, module and pathway levels",
        },
        "HMM6": {"status": "unchanged_preliminary_measurement_validation_and_full_tree_still_required"},
    }

    result["claim_boundary"] = (
        "Published conclusions, EAzami reanalyses, and own preliminary results remain separate. "
        "v3 adds a molecular resolution ladder but does not change HMM1-HMM6 provenance. "
        "A targeted-panel omission, missing functional annotation label, BLAST homology candidate, validated ortholog, functional gene, and causal colour-transition locus are distinct evidence levels and must not be collapsed."
    )

    Path(args.output).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
