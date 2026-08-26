#!/usr/bin/env python3
"""Audit whether additional capitulum modules can enter Japan38 history analysis.

The audit is intentionally strict. Botanical authorities are ignored when comparing
concept labels, but infraspecific rank is preserved. Thus Cirsium japonicum var.
albescens never substitutes for var. horridum, and C. suffultum never substitutes
for C. pseudosuffultum. Mixed size metrics are retained as separate measurement
classes rather than discretized into an invented common state.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as h:
        return list(csv.DictReader(h))


def concept_key(text: str) -> str:
    """Return genus + species + optional infraspecific rank/epithet.

    Authority strings may occur between the species epithet and ``var.`` in the
    Moreyra audit, so rank tokens are searched globally rather than assumed to be
    adjacent to the species epithet.
    """
    clean = " ".join((text or "").replace("×", "x").split())
    m = re.match(r"^([A-Z][A-Za-z-]+)\s+([a-z][A-Za-z-]+)", clean)
    if not m:
        raise ValueError(f"cannot parse taxon concept: {text!r}")
    genus, species = m.group(1), m.group(2)
    for rank in ("subsp.", "ssp.", "var.", "f."):
        rm = re.search(rf"(?:^|\s){re.escape(rank)}\s+([a-z][A-Za-z-]+)", clean)
        if rm:
            normalized_rank = "subsp." if rank == "ssp." else rank
            return f"{genus} {species} {normalized_rank} {rm.group(1)}"
    return f"{genus} {species}"


def display_audit(audit_rows, display_rows):
    members = {}
    duplicate_keys = {}
    for row in audit_rows:
        key = concept_key(row["paper_taxon_concept"])
        if key in members:
            duplicate_keys.setdefault(key, [members[key]["paper_japan_member_id"]]).append(
                row["paper_japan_member_id"]
            )
        else:
            members[key] = row
    if duplicate_keys:
        raise ValueError(f"non-unique normalized Japan38 concepts: {duplicate_keys}")

    exact = []
    unmatched = []
    metric_groups = {}
    for row in display_rows:
        key = concept_key(row["taxon"])
        match = members.get(key)
        if match is None:
            unmatched.append(
                {
                    "taxon": row["taxon"],
                    "normalized_concept": key,
                    "region": row.get("region", ""),
                    "size_metric": row.get("size_metric", ""),
                }
            )
            continue
        item = {
            "paper_japan_member_id": match["paper_japan_member_id"],
            "paper_taxon_concept": match["paper_taxon_concept"],
            "display_taxon": row["taxon"],
            "normalized_concept": key,
            "size_metric": row["size_metric"],
            "diameter_cm": row.get("diameter_cm", ""),
            "length_cm": row.get("length_cm", ""),
            "width_cm": row.get("width_cm", ""),
            "arrangement": row.get("arrangement", ""),
            "orientation": row.get("orientation", ""),
            "source": row.get("source", ""),
            "claim_boundary": row.get("claim_boundary", ""),
        }
        exact.append(item)
        metric_groups.setdefault(row["size_metric"], []).append(item)

    exact.sort(key=lambda x: x["paper_japan_member_id"])
    comparable = {
        metric: {
            "n_exact_concepts": len(rows),
            "paper_japan_member_ids": sorted(r["paper_japan_member_id"] for r in rows),
            "taxa": sorted(r["normalized_concept"] for r in rows),
        }
        for metric, rows in sorted(metric_groups.items())
    }
    largest_metric = max(comparable, key=lambda x: comparable[x]["n_exact_concepts"]) if comparable else None
    largest_n = comparable[largest_metric]["n_exact_concepts"] if largest_metric else 0
    return {
        "source_rows": len(display_rows),
        "exact_japan38_concepts": len(exact),
        "exact_fraction_of_japan38": len(exact) / len(audit_rows) if audit_rows else None,
        "exact_matches": exact,
        "metric_groups": comparable,
        "largest_comparable_metric_group": largest_metric,
        "largest_comparable_metric_group_n": largest_n,
        "unmatched_source_rows": unmatched,
    }


def high_leverage_targets(readiness, exact_ids):
    d = readiness["trait_completion_design"]
    ordered = [
        (d["observed_state_validation"]["cross_module_first"], "cross_module_observed_state_validation"),
        (d["observed_state_validation"]["stickiness_second"], "stickiness_observed_state_validation"),
        (d["orientation"]["primary"], "orientation_missing_state_primary"),
        (d["phyllary"]["primary"], "phyllary_missing_state_primary"),
        (d["stickiness"]["primary"], "stickiness_missing_state_primary"),
    ]
    out = []
    seen = set()
    for mid, role in ordered:
        if mid in seen:
            continue
        seen.add(mid)
        out.append(
            {
                "paper_japan_member_id": mid,
                "existing_direct_display_size": mid in exact_ids,
                "role": role,
            }
        )
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--membership-audit", type=Path, required=True)
    p.add_argument("--display-seed", type=Path, required=True)
    p.add_argument("--azami-bridge-summary", type=Path, required=True)
    p.add_argument("--readiness", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()

    audit = read_csv(a.membership_audit)
    display = read_csv(a.display_seed)
    if len(audit) != 38:
        raise ValueError(f"expected 38 Japan concepts, found {len(audit)}")
    d = display_audit(audit, display)
    bridge = json.loads(a.azami_bridge_summary.read_text(encoding="utf-8"))
    readiness = json.loads(a.readiness.read_text(encoding="utf-8"))
    exact_ids = {r["paper_japan_member_id"] for r in d["exact_matches"]}
    leverage = high_leverage_targets(readiness, exact_ids)

    result = {
        "contract_version": "japan38_direct_module_coverage_audit_v1",
        "japan38_concepts": len(audit),
        "display_size_direct": d,
        "azami_image_trait_bridge": {
            "concepts_with_exact_azami_taxon_concept_coverage": bridge[
                "japan38_trait_coverage"
            ]["concepts_with_exact_azami_taxon_concept_coverage"],
            "concepts_with_any_azami_binomial_trait_coverage": bridge[
                "japan38_trait_coverage"
            ]["concepts_with_any_azami_binomial_trait_coverage"],
            "covered_binomial_taxa": bridge["japan38_trait_coverage"][
                "covered_binomial_taxa"
            ],
            "row_level_colour_join_available_in_this_audit": False,
            "interpretation": (
                "The retained EAzami bridge summary proves only the coverage ceiling. "
                "It does not identify which exact Japan38 concepts have usable colour "
                "states, so a colour history is not constructed from this summary alone."
            ),
        },
        "high_leverage_targets_missing_direct_display": [
            r for r in leverage if not r["existing_direct_display_size"]
        ],
        "display_history_readiness": (
            "not_promoted_sparse_exact_coverage"
            if d["exact_japan38_concepts"] < len(audit)
            else "complete_exact_coverage"
        ),
        "display_interpretation": (
            f"Direct display size currently reaches {d['exact_japan38_concepts']}/38 Japan38 concepts. "
            f"The largest internally comparable metric class contains {d['largest_comparable_metric_group_n']} concepts. "
            "This is useful calibration evidence but is too sparse for a radiation-wide display history without "
            "aggressive imputation or arbitrary discretization."
        ),
        "next_measurement_contract": (
            "Add standardized direct involucre/capitulum size on identity-resolved Japan38 material, prioritizing "
            "the current cross-module validation and trait-completion targets, and keep plant-level head number "
            "as a separate measurement rather than substituting qualitative arrangement categories."
        ),
        "claim_boundary": (
            "Exact normalized concept overlap and metric comparability audit only. Authority strings are ignored, "
            "but infraspecific rank is preserved; near-name species and broad-species substitutions are forbidden. "
            "No missing trait is imputed and no continuous display metric is discretized."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
