from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data/evidence/chapter3_p01_stickiness_radseq_contract_v1.json"
SCHEMA = ROOT / "data/evidence/chapter3_p01_same_individual_schema_v1.csv"
MANIFEST = ROOT / "data/templates/chapter3_p01_recommended_sample_manifest_v1.csv"
DECISIONS = ROOT / "data/evidence/chapter3_p01_decision_matrix_v1.csv"
PLAN = ROOT / "docs/chapter3/CHAPTER3_P01_STICKINESS_RADSEQ_EXECUTION_V1.md"


def main() -> None:
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert c["status"] == "PRE_DATA_FROZEN"
    assert c["issue"] == 154
    assert c["parent_scientific_state"]["source_pr"] == 153
    assert c["parent_scientific_state"]["source_head"] == "857f2d25a03dbbf6f6c0297011735b38aa36e9f3"

    focal = {x["paper_concept"]: x for x in c["focal_concepts"]}
    assert set(focal) == {"JPN_06", "JPN_15"}
    assert focal["JPN_06"]["minimum_individuals"] == 16
    assert focal["JPN_15"]["minimum_individuals"] == 16
    assert focal["JPN_06"]["recommended_individuals"] == 24
    assert focal["JPN_15"]["recommended_individuals"] == 24
    assert c["total_sampling_target"]["minimum_individuals"] == 32
    assert c["total_sampling_target"]["recommended_individuals"] == 48

    required_gates = {
        "independent_population_replication",
        "shared_homologous_locus_coverage",
        "restriction_site_dropout_sensitivity",
        "ploidy_aware_calling_or_within_cytotype_sensitivity",
        "homeolog_paralog_collapse_screen",
        "admixture_diagnostic",
        "network_sensitivity",
        "strict_locus_sensitivity",
    }
    assert required_gates.issubset(set(c["radseq_admission_gates"]))
    assert len(c["predeclared_falsifiers"]) >= 3

    with SCHEMA.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    required_fields = {r["field"] for r in rows if r["required"] == "yes"}
    contract_fields = set(c["same_individual_required_fields"])
    assert contract_fields.issubset(required_fields), contract_fields - required_fields
    assert {"individual_id", "stickiness_state", "rad_tissue_id", "voucher_id", "cytotype_status"}.issubset(required_fields)

    with MANIFEST.open(encoding="utf-8", newline="") as fh:
        manifest = list(csv.DictReader(fh))
    assert len(manifest) == 48
    counts = Counter(r["taxon_concept"] for r in manifest)
    assert counts == {"JPN06": 24, "JPN15": 24}
    core = Counter(r["taxon_concept"] for r in manifest if r["minimum_core"] == "yes")
    assert core == {"JPN06": 16, "JPN15": 16}
    pop_counts = Counter((r["taxon_concept"], r["population_slot"]) for r in manifest)
    for taxon in ("JPN06", "JPN15"):
        assert [pop_counts[(taxon, p)] for p in ("P1", "P2", "P3")] == [8, 8, 8]
    assert len({r["planned_slot"] for r in manifest}) == 48
    assert all(r["authorization_status"] == "required" for r in manifest)

    with DECISIONS.open(encoding="utf-8", newline="") as fh:
        decisions = list(csv.DictReader(fh))
    assert [r["gate_id"] for r in decisions] == [f"G{i:02d}" for i in range(1, 12)]
    by_id = {r["gate_id"]: r for r in decisions}
    assert by_id["G08"]["chapter2_effect"] == "revise"
    assert by_id["G09"]["chapter2_effect"] == "revise"
    assert by_id["G10"]["chapter2_effect"] == "revise"
    assert "neutralization" in by_id["G11"]["next_action"]

    text = PLAN.read_text(encoding="utf-8")
    for phrase in (
        "PRE-DATA CONTRACT FROZEN",
        "32",
        "48",
        "Primary falsifiers",
        "within-JPN15 stickiness neutralization versus sham",
        "cannot by itself demonstrate defence",
    ):
        assert phrase in text, phrase

    print("chapter3_p01_stickiness_radseq_contract_v1: PASS")


if __name__ == "__main__":
    main()
