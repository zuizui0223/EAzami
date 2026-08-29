#!/usr/bin/env python3
"""Build bounded non-climate explanatory constraints for Chapter 2.

This is not a multivariable causal model. It converts already-frozen evidence
layers into explicit decisions about which simple alternatives current data can
contradict, which assumptions are constrained, and which factors remain not
evaluable as Japan38 comparative predictors.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as h:
        return list(csv.DictReader(h))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cytotype", type=Path, required=True)
    p.add_argument("--configurations", type=Path, required=True)
    p.add_argument("--nuclear-audit", type=Path, required=True)
    p.add_argument("--interactions", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()

    cyt = read_json(a.cytotype)
    cfg = read_json(a.configurations)
    nuc = read_csv(a.nuclear_audit)
    inter = read_json(a.interactions)

    assert cyt["n_source_backed_cytotype_concepts"] == 9
    assert cyt["upward_or_ascending_observed_ploidy_levels"] == [2, 4, 6]
    assert set(cyt["diploid_observed_orientation_states"]) == {
        "downward_or_nodding", "upward_or_erect"
    }
    assert cfg["n_dominant_orientation_stickiness_combinations"] >= 3
    assert cfg["n_secondary_orientation_stickiness_combinations"] >= 2

    by_id = {r["evidence_id"]: r for r in nuc}
    for rid in ["NUC03", "NUC06"]:
        assert rid in by_id
    assert "MIG-seq" in by_id["NUC03"]["nuclear_data_type"]
    assert "MIG-seq" in by_id["NUC06"]["nuclear_data_type"]

    gates = inter["aim2_module_gate"]
    assert gates["head_orientation"]["direct_rows"] == 0
    assert gates["involucre_spine"]["direct_rows"] == 0
    assert gates["stickiness"]["direct_rows"] == 1

    payload = {
        "contract_version": "chapter2_nonclimate_explanatory_constraints_v1",
        "estimand": "bounded constraints from existing non-climate data; not causal attribution",
        "factors": {
            "cytotype_ploidy": {
                "status": "deterministic_one_to_one_model_contradicted_descriptively",
                "coverage_concepts": cyt["n_source_backed_cytotype_concepts"],
                "dominant_with_known_orientation": cyt["n_dominant_with_known_orientation"],
                "upward_or_ascending_ploidy_levels": cyt["upward_or_ascending_observed_ploidy_levels"],
                "diploid_orientation_states": cyt["diploid_observed_orientation_states"],
                "interpretation": "Orientation is not deterministically assigned by ploidy in the current source-backed panel.",
                "claim_boundary": "Sparse records do not establish statistical independence or a causal ploidy effect."
            },
            "broad_colonization_history": {
                "status": "one_to_one_configuration_mapping_contradicted_descriptively",
                "dominant_orientation_stickiness_combinations": cfg["n_dominant_orientation_stickiness_combinations"],
                "secondary_orientation_stickiness_combinations": cfg["n_secondary_orientation_stickiness_combinations"],
                "interpretation": "Observed capitulum configurations do not map one-to-one onto the broad dominant-radiation versus secondary-history class.",
                "claim_boundary": "This does not identify transition direction, rate or selective cause."
            },
            "population_genetic_structure": {
                "status": "species_tip_homogeneity_assumption_constrained",
                "independent_evidence_ids": ["NUC03", "NUC06"],
                "interpretation": "Independent Japanese reduced-representation nuclear evidence shows biologically relevant population structure below named species tips in at least parts of Japanese Cirsium.",
                "claim_boundary": "The independent datasets are not same-voucher focal-trait histories and do not explain one Chapter 2 trait across Japan38."
            },
            "independent_nuclear_topology": {
                "status": "alternative_nuclear_evidence_landscape_present",
                "audit_records": len(nuc),
                "interpretation": "The Comp1061 reconstruction is the harmonized full-panel scaffold, not the only nuclear evidence; older rDNA and local phylogenomic/network evidence constrain topology interpretation at other scales.",
                "claim_boundary": "Heterogeneous marker systems cannot be pooled into one branch-length tree without an explicit model."
            },
            "pollinator_antagonist_context": {
                "status": "not_evaluable_as_joined_japan38_comparative_predictor",
                "head_orientation_direct_cirsium_rows": gates["head_orientation"]["direct_rows"],
                "phyllary_spine_direct_cirsium_rows": gates["involucre_spine"]["direct_rows"],
                "stickiness_direct_cirsium_rows": gates["stickiness"]["direct_rows"],
                "interpretation": "Genus-level interaction evidence supplies mechanism priors, but no dense harmonized Japan38 trait-by-interaction matrix currently supports a phylogeny-aware explanatory test comparable to the climate screen.",
                "claim_boundary": "Do not infer no biotic effect from this data-join limitation."
            }
        },
        "chapter2_use": "Show what existing non-climate data already rule out or constrain without expanding the paper into underpowered causal model competition.",
        "claim_boundary": "Constraint is not causal explanation; not_evaluable is not evidence of no relationship."
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
