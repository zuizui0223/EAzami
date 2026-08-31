#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data/evidence/chapter2_public_trait_event_recovery_audit_v2.csv"
WHITE = ROOT / "data/evidence/chapter2_white_lineage_sister_contrast_v1.csv"
DOC = ROOT / "docs/chapter2/PUBLIC_TRAIT_EVENT_RECOVERY_AUDIT_V2.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


audit = read_csv(AUDIT)
assert audit, "empty public trait-event audit"
required_audit = {
    "record_id",
    "source_doi",
    "trait_module",
    "focal_taxa",
    "calendar_constraint",
    "calendar_lower_ma",
    "calendar_upper_ma",
    "calendar_status",
    "topology_status",
    "phenotype_resolution",
    "history_class",
    "usable_as_transition",
    "distribution_process",
    "environmental_driver_status",
    "azami_bridge",
    "next_gate",
    "claim_boundary",
}
assert required_audit.issubset(audit[0]), sorted(required_audit - set(audit[0]))
ids = [row["record_id"] for row in audit]
assert len(ids) == len(set(ids)), "duplicate record_id"
by = {row["record_id"]: row for row in audit}

expected_ids = {
    "ORI_CORE_NIPPONO_STEM",
    "COL_KAWAKAMII_TERMINAL_PRIMARY",
    "COL_KAWAKAMII_TOPOLOGY_UNION",
    "COL_BREVICAULE_TERMINAL_CONDITIONAL",
    "COL_ALBESCENS_TAKAOENSE_POLYMORPHIC",
    "PHYL_KAWAKAMII_TATAKAENSE_SISTER_CONTRAST",
    "PHYL_BREVICAULE_IRUMTIENSE_SISTER_CONTRAST",
    "DISPLAY_KAWAKAMII_TATAKAENSE_SISTER_CONTRAST",
    "DISPLAY_BREVICAULE_IRUMTIENSE_SISTER_CONTRAST",
    "DISP_NIPPONO_JAPAN_TAIWAN_SPLIT",
    "DISP_DOMINANT_JAPAN_FOUNDER",
    "STICK_DIPSACOLEPIS_RANGE_ONLY",
    "STICK_LINEARE_RANGE_ONLY",
}
assert set(ids) == expected_ids, sorted(set(ids) ^ expected_ids)

for row in audit:
    lower = row["calendar_lower_ma"].strip()
    upper = row["calendar_upper_ma"].strip()
    if lower or upper:
        assert lower and upper, f"one-sided calendar bound: {row['record_id']}"
        assert float(lower) <= float(upper), row["record_id"]
    assert row["source_doi"].strip(), row["record_id"]
    assert row["claim_boundary"].strip(), row["record_id"]

# Cross-study orientation chronology must remain explicitly non-joint and
# cannot be promoted to an event-level palaeoclimate test.
ori = by["ORI_CORE_NIPPONO_STEM"]
assert ori["history_class"] == "crossstudy_chronology_refinement"
assert ori["calendar_lower_ma"] == "" and ori["calendar_upper_ma"] == ""
assert ori["calendar_status"] == "separate_analyses_no_joint_interval"
assert ori["usable_as_transition"] == "conditional_chronology_only"
assert "paleolocation_unresolved" in ori["environmental_driver_status"]
assert "0.79" in ori["calendar_constraint"] and "0.74" in ori["calendar_constraint"]

# Only branch-bounded colour rows are admitted as conditional transition
# candidates. Sister contrasts, polymorphic lineages and range processes are not.
for record_id in {
    "COL_KAWAKAMII_TERMINAL_PRIMARY",
    "COL_KAWAKAMII_TOPOLOGY_UNION",
    "COL_BREVICAULE_TERMINAL_CONDITIONAL",
}:
    row = by[record_id]
    assert row["history_class"] == "conditional_dated_trait_transition"
    assert row["usable_as_transition"].startswith("yes_")
    assert "not_evaluable_no_commensurate_surface_RSDS_history" == row["environmental_driver_status"]

assert float(by["COL_KAWAKAMII_TERMINAL_PRIMARY"]["calendar_upper_ma"]) == 0.45
assert float(by["COL_KAWAKAMII_TOPOLOGY_UNION"]["calendar_upper_ma"]) == 0.60
assert float(by["COL_BREVICAULE_TERMINAL_CONDITIONAL"]["calendar_upper_ma"]) == 1.33

poly = by["COL_ALBESCENS_TAKAOENSE_POLYMORPHIC"]
assert poly["history_class"] == "lineage_polymorphic_nonidentifiable"
assert poly["usable_as_transition"] == "no"
assert "manufacture a transition" in poly["claim_boundary"]

for record_id in {
    "PHYL_KAWAKAMII_TATAKAENSE_SISTER_CONTRAST",
    "PHYL_BREVICAULE_IRUMTIENSE_SISTER_CONTRAST",
    "DISPLAY_KAWAKAMII_TATAKAENSE_SISTER_CONTRAST",
    "DISPLAY_BREVICAULE_IRUMTIENSE_SISTER_CONTRAST",
}:
    row = by[record_id]
    assert row["history_class"] == "dated_sister_phenotype_contrast"
    assert row["usable_as_transition"] == "no_trait_transition_not_reconstructed"

for record_id in {
    "DISP_NIPPONO_JAPAN_TAIWAN_SPLIT",
    "DISP_DOMINANT_JAPAN_FOUNDER",
}:
    row = by[record_id]
    assert row["history_class"] == "biogeographic_process"
    assert row["usable_as_transition"] == "no"
    assert "not" in row["claim_boundary"].lower()

for record_id in {"STICK_DIPSACOLEPIS_RANGE_ONLY", "STICK_LINEARE_RANGE_ONLY"}:
    row = by[record_id]
    assert row["history_class"] == "range_process_trait_age_unlinked"
    assert row["usable_as_transition"] == "no"
    assert "not" in row["claim_boundary"].lower()

white = read_csv(WHITE)
assert len(white) == 2, "white sister-contrast registry must contain exactly two systems"
assert len({row["system_id"] for row in white}) == 2
required_white = {
    "system_id",
    "source_doi",
    "white_taxon",
    "contrasting_coloured_taxon",
    "split_central_ma",
    "split_lower_ma",
    "split_upper_ma",
    "colour_history_status",
    "white_colour_state",
    "coloured_state",
    "white_phyllary_metric",
    "white_phyllary_value",
    "coloured_phyllary_metric",
    "coloured_phyllary_value",
    "phyllary_direction_in_white",
    "white_floret_length_cm",
    "coloured_floret_length_cm",
    "floret_length_direction_in_white",
    "interpretive_class",
    "claim_boundary",
}
assert required_white.issubset(white[0]), sorted(required_white - set(white[0]))
white_by = {row["system_id"]: row for row in white}

arenicola = white_by["ARENICOLA_BREVICAULE_IRUMTIENSE"]
assert float(arenicola["white_phyllary_value"]) == 2.24
assert float(arenicola["coloured_phyllary_value"]) == 1.44
assert float(arenicola["white_floret_length_cm"]) > float(arenicola["coloured_floret_length_cm"])
assert arenicola["floret_length_direction_in_white"] == "longer"

taiwan = white_by["TAIWAN_KAWAKAMII_TATAKAENSE"]
assert float(taiwan["white_phyllary_value"]) == 1.80
assert float(taiwan["coloured_phyllary_value"]) == 1.04
assert taiwan["floret_length_direction_in_white"].startswith("longer")
assert int(taiwan["white_floret_count"]) == 138
assert int(taiwan["coloured_floret_count"]) == 254
assert int(taiwan["white_phyllary_count"]) == 99
assert int(taiwan["coloured_phyllary_count"]) == 154

# The repeated direction is a hypothesis generator only; the two studies use
# non-identical phyllary metrics and do not reconstruct simultaneous changes.
assert arenicola["white_phyllary_metric"] != taiwan["white_phyllary_metric"]
for row in white:
    assert "syndrome" in row["claim_boundary"].lower() or "correlated evolution" in row["claim_boundary"].lower()
    assert "adapt" in row["claim_boundary"].lower() or "selection" in row["claim_boundary"].lower()

text = DOC.read_text(encoding="utf-8")
for phrase in (
    "A dated lineage split is not automatically a dated trait transition",
    "white-flower syndrome",
    "range reorganisation",
    "Chapter 3",
    "public-data",
):
    assert phrase in text, phrase

print(
    json.dumps(
        {
            "status": "ok",
            "n_audit_records": len(audit),
            "conditional_dated_transition_records": [
                row["record_id"]
                for row in audit
                if row["history_class"] == "conditional_dated_trait_transition"
            ],
            "n_white_sister_systems": len(white),
            "repeated_extant_direction": {
                "white_lineage_florets": "longer in both systems",
                "white_lineage_phyllary_differentiation": "greater/longer in both systems",
                "claim_class": "hypothesis_generator_not_correlated_evolution",
            },
            "orientation_event_environment": "not_evaluable_paleolocation_unresolved",
        },
        indent=2,
    )
)
