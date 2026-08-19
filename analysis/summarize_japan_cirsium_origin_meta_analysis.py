#!/usr/bin/env python3
"""Structured evidence synthesis for the biogeographic origin of Japanese Cirsium.

This is deliberately not a classical effect-size meta-analysis: the available
phylogenomic studies do not estimate a common scalar effect and some focused
transcriptome studies share parts of a data-generation programme.  Instead we
aggregate predeclared proposition states at two levels: analysis-level support
and independent data-generation groups.  Direct biogeographic inference is
kept separate from phylogenetic compatibility so reused samples cannot create
pseudo-replication.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

EXPECTED_FIELDS = {
    "evidence_id", "study", "year", "data_generation_group", "data_type",
    "scale", "public_accession", "japanese_sampling", "japanese_species_n",
    "main_radiation_species_n", "direct_biogeography", "main_radiation_state",
    "lineare_state", "dipsacolepis_state", "arenicola_extra_arrival_state",
    "maternal_structure_state", "weight", "notes",
}


def read_matrix(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if set(reader.fieldnames or []) != EXPECTED_FIELDS:
            raise ValueError("evidence matrix schema drift")
        rows = [{k: (v or "").strip() for k, v in row.items()} for row in reader]
    if not rows or len({r["evidence_id"] for r in rows}) != len(rows):
        raise ValueError("evidence matrix is empty or has duplicated evidence IDs")
    for row in rows:
        if int(row["weight"]) not in {1, 2, 3}:
            raise ValueError(f"invalid evidence weight: {row['evidence_id']}")
    return rows


def high_dimensional_nuclear(row: dict[str, str]) -> bool:
    return int(row["weight"]) == 3 and row["data_type"].startswith("high_dimensional_nuclear")


def proposition(rows: list[dict[str, str]], field: str, support_token: str = "support") -> dict[str, object]:
    tested = [r for r in rows if r[field] not in {"", "not_tested", "sequence_anchor_only"}]
    support = [r for r in tested if r[field] == support_token]
    contradict = [r for r in tested if r[field] in {"contradict", "not_supported"}]
    support_groups = sorted({r["data_generation_group"] for r in support})
    tested_groups = sorted({r["data_generation_group"] for r in tested})
    return {
        "analyses_tested": len(tested),
        "analyses_supporting": len(support),
        "analyses_contradicting_or_not_supporting": len(contradict),
        "data_generation_groups_tested": len(tested_groups),
        "data_generation_groups_supporting": len(support_groups),
        "supporting_evidence_ids": [r["evidence_id"] for r in support],
        "tested_data_generation_groups": tested_groups,
    }


def summarize(rows: list[dict[str, str]]) -> dict[str, object]:
    high = [r for r in rows if high_dimensional_nuclear(r)]
    direct = [r for r in high if r["direct_biogeography"] == "yes"]
    broad = [r for r in direct if r["scale"] == "broad_genus"]
    if len(broad) != 1 or broad[0]["evidence_id"] != "MOREYRA2025":
        raise ValueError("expected exactly one current broad direct nuclear biogeographic analysis")
    moreyra = broad[0]
    sampled = int(moreyra["japanese_species_n"])
    main = int(moreyra["main_radiation_species_n"])
    if not (0 < main <= sampled):
        raise ValueError("invalid Moreyra Japanese radiation counts")

    lineare = proposition(high, "lineare_state")
    dipsa = proposition(high, "dipsacolepis_state")
    arenicola = proposition(high, "arenicola_extra_arrival_state")
    compatible_main = [r for r in high if r["main_radiation_state"] in {"support_direct", "compatible_partial"}]

    # The distinction below is central: the colonization event itself is inferred
    # directly only by the broad range model, while C. lineare's phylogenetic
    # separation is replicated by independent nuclear data-generation groups.
    if lineare["data_generation_groups_supporting"] < 2:
        raise ValueError("replicated nuclear support for C. lineare separation unexpectedly lost")
    if dipsa["analyses_supporting"] != 1:
        raise ValueError("C. dipsacolepis evidence count drift")
    if arenicola["analyses_supporting"] != 0:
        raise ValueError("current evidence must not pre-authorize Arenicola as an extra colonization")

    result: dict[str, object] = {
        "contract_version": "japan_cirsium_origin_meta_analysis_v1",
        "evidence_units": len(rows),
        "high_dimensional_nuclear_analyses": len(high),
        "independent_high_dimensional_nuclear_data_generation_groups": len({r["data_generation_group"] for r in high}),
        "direct_broad_nuclear_biogeographic_analyses": len(broad),
        "dominant_main_radiation": {
            "direct_study": moreyra["evidence_id"],
            "japanese_species_sampled": sampled,
            "species_in_main_radiation": main,
            "proportion_in_main_radiation": main / sampled,
            "focused_high_dimensional_nuclear_analyses_compatible": len(compatible_main) - 1,
            "interpretation": "one dominant Pleistocene Japanese radiation is directly supported by the broad target-capture range analysis and is compatible with the focused East-Asian transcriptome trees",
        },
        "cirsium_lineare": {
            **lineare,
            "direct_biogeographic_event_analyses": 1,
            "status": "very_strong_phylogenetic_exception_with_single_broad_direct_range_reconstruction",
            "interpretation": "C. lineare is repeatedly recovered outside the derived Japanese/Nipponocirsium lineages; Moreyra independently maps its East-Asia-to-Japan range expansion",
        },
        "cirsium_dipsacolepis": {
            **dipsa,
            "direct_biogeographic_event_analyses": 1,
            "status": "strong_but_single_study_secondary_arrival_hypothesis",
            "interpretation": "a separate ~1 Ma Japanese jump is directly inferred in the broad target-capture analysis, but a second high-dimensional dataset has not yet replicated this placement",
        },
        "arenicola": {
            **arenicola,
            "status": "extra_colonization_not_established",
            "interpretation": "the focused phylotranscriptome instead places Arenicola sister to Nipponocirsium (PP=1); without a broad range reconstruction this should not be counted as a fourth Japanese colonization",
        },
        "organellar_context": {
            "maternal_structure_evidence_ids": [r["evidence_id"] for r in rows if r["maternal_structure_state"] == "support"],
            "interpretation": "chloroplast heterogeneity is a useful reticulation/maternal-history diagnostic but is not counted as an independent colonization event",
        },
        "model_comparison": {
            "strict_single_origin_all_japanese_cirsium": "rejected",
            "dominant_single_pleistocene_radiation_plus_rare_secondary_entries": "best_supported",
            "many_independent_colonizations_without_dominant_radiation": "not_supported",
        },
        "origin_count_hypothesis": {
            "minimum_defensible_histories": 2,
            "minimum_defensible_components": ["dominant_main_japanese_radiation", "Cirsium_lineare_lineage"],
            "best_current_point_hypothesis_histories": 3,
            "best_current_point_components": ["dominant_main_japanese_radiation", "Cirsium_lineare_lineage", "Cirsium_dipsacolepis_secondary_arrival"],
            "four_or_more_histories_status": "unresolved_not_supported_by_current_high_dimensional_evidence",
        },
        "preferred_hypothesis": "Japanese Cirsium has an oligophyletic colonization history: one dominant Middle-Asian-derived Pleistocene radiation accounts for most sampled Japanese species, with a replicated phylogenetic exception represented by C. lineare and a likely second secondary arrival represented by C. dipsacolepis; Arenicola should remain uncounted as an additional arrival until the broad nuclear range analysis resolves it.",
        "claim_boundary": "This synthesis separates phylogenetic replication from direct biogeographic event inference and does not treat partially reused transcriptome datasets, chloroplast structure, or sparse ITS/ETS accessions as independent colonization events.",
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = summarize(read_matrix(args.matrix))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
