#!/usr/bin/env python3
"""Validate the Chapter 2 public dated-tree recovery audit.

This validator freezes an audit boundary, not a live availability claim. The
canonical selection-pressure validator must pass first; the new files then prove
why orientation x hydric regime remains at T2 and what exact assets are required
before a T3 event-window analysis is admissible.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import validate_chapter2_selection_pressure_triangulation_v1 as base

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "data" / "evidence"
AUDIT = EVID / "chapter2_dated_tree_public_recovery_audit_v1.csv"
MANIFEST = EVID / "chapter2_dated_tree_request_manifest_v1.json"
REPORT = ROOT / "docs" / "chapter2" / "DATED_TREE_PUBLIC_RECOVERY_AUDIT_V1.md"
REQUEST = ROOT / "docs" / "chapter2" / "DATED_TREE_AUTHOR_REQUEST_DRAFT_V1.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    # The prior validator owns the canonical R/T/S/C/L evidence and the already
    # frozen PALEO-PGEM asset contract. This extension validates only the public
    # dated-tree recovery audit and author-request boundary.
    base.main()
    for path in (AUDIT, MANIFEST, REPORT, REQUEST):
        assert path.exists(), path

    rows = read_csv(AUDIT)
    assert len(rows) == 16
    keyed = {(r["audit_layer"], r["resource"]): r for r in rows}
    assert len(keyed) == len(rows)

    article = keyed[("published_article_method", "Moreyra_et_al_2025_MPE")]
    assert "RelTime" in article["public_content_recovered"]
    assert "350 nuclear loci" in article["public_content_recovered"]
    assert article["machine_readable_dated_tree_status"] == "not_deposited_in_article_landing_page"
    assert article["usable_for_exact_japan38_event_windows"] == "no"

    for layer, resource in (
        ("published_calibration_CP1", "root_constraint"),
        ("published_calibration_CP2", "cirsioid_fossil_constraint"),
        ("published_calibration_CP3", "madeira_Cirsium_latifolium_constraint"),
    ):
        assert keyed[(layer, resource)]["evidence_status"] == "primary_method_evidence"

    radiation = keyed[("published_japan_radiation_context", "node_13_jump_to_Japan")]
    assert "2.4 Ma" in radiation["public_content_recovered"]
    assert "1.7-3.6 Ma" in radiation["public_content_recovered"]
    assert radiation["evidence_status"] == "broad_calendar_context_only"

    author_repo = keyed[("author_GitHub", "ldmoreyra_A-thorny-tale")]
    assert "HybPiper QC" in author_repo["public_content_recovered"]
    assert author_repo["machine_readable_dated_tree_status"] == "no_tree_alignment_or_chronogram"

    chang = keyed[("independent_local_dated_context", "Chang_et_al_2026_BMC_Plant_Biology")]
    assert "StarBEAST3" in chang["public_content_recovered"]
    assert "50 OGs" in chang["public_content_recovered"]
    assert "52 OGs" in chang["public_content_recovered"]
    assert "50-versus-52" in chang["limitation"]
    assert chang["usable_for_exact_japan38_event_windows"] == "no"

    scaffold = keyed[("EAzami_Japan38_scaffold", "harmonized_common_locus_Japan38")]
    assert scaffold["machine_readable_dated_tree_status"] == "undated_phylogram_only"
    assert "substitutions per site" in scaffold["limitation"]
    assert "cannot be scaled by the 2.4 Ma" in scaffold["limitation"]

    decision = keyed[("primary_recovery_decision", "public_dated_tree_recovery_2026_08_30")]
    assert decision["machine_readable_dated_tree_status"] == "PUBLIC_DATED_TREE_NOT_RECOVERED_IN_AUDIT"
    assert decision["evidence_status"] == "stop_rule_active"
    assert "before any T3 event-window test" in decision["next_action"]

    manifest = read_json(MANIFEST)
    assert manifest["contract_version"] == "chapter2_dated_tree_request_manifest_v1"
    assert manifest["recovery_status"] == "PUBLIC_DATED_TREE_NOT_RECOVERED_IN_AUDIT"
    assert manifest["target_publication"]["doi"] == "10.1016/j.ympev.2025.108285"
    assert manifest["target_publication"]["bioProject"] == "PRJNA957074"
    assert manifest["published_dating_contract"]["method"] == "RelTime implemented in MEGA X"
    assert manifest["published_dating_contract"]["input_tree"].startswith("best maximum-likelihood tree")
    calibrations = {x["id"]: x for x in manifest["published_dating_contract"]["calibrations"]}
    assert set(calibrations) == {"CP1", "CP2", "CP3"}
    assert "17.7 Ma" in calibrations["CP1"]["constraint"]
    assert "minimum age 14 Ma" in calibrations["CP2"]["constraint"]
    assert "maximum age 5.6 Ma" in calibrations["CP3"]["constraint"]
    landmarks = {x["landmark"]: x for x in manifest["published_dating_contract"]["published_temporal_landmarks"]}
    japan = landmarks["main Japanese radiation jump-dispersal node 13"]
    assert japan["mean_ma"] == 2.4
    assert japan["ci95_ma"] == [1.7, 3.6]
    assert manifest["independent_rebuild_fallback"]["status"] == "DEFERRED_HEAVY_ANALYSIS_READY_FOR_CONTRACT_NOT_ROUTINE_PR_CI"
    assert "Multiplying its branch lengths or relative lineage-depth by 2.4 Ma is prohibited" in manifest["independent_rebuild_fallback"]["non_equivalence_warning"]
    assert len(manifest["promotion_gate"]["T3_requires"]) == 5
    assert "No T3 promotion until the dated-tree and paleolocation gates both pass." in manifest["stop_rules"]

    report = REPORT.read_text(encoding="utf-8")
    required_report = [
        "PUBLIC_DATED_TREE_NOT_RECOVERED_IN_AUDIT",
        "orientation × hydric regime remains at explanatory tier T2",
        "The main radiation age also cannot be multiplied by relative lineage-depth.",
        "Route A — author-source bundle, preferred",
        "Route B — independent global rebuild, fallback",
        "Route C — Chang local dated sensitivity",
        "PALEO-PGEM-Series provides the correct temporal form",
        "It would still not demonstrate rain adaptation.",
    ]
    for phrase in required_report:
        assert phrase in report, phrase

    request = REQUEST.read_text(encoding="utf-8")
    required_request = [
        "**Status:** prepared, not sent",
        "avoid extracting branch ages or topology from the published figures",
        "RelTime time-calibrated tree",
        "CP1–CP3 calibration configuration",
        "sample-label to BioSample/SRA accession and voucher crosswalk",
        "do not state that the requested tree will prove adaptation",
    ]
    for phrase in required_request:
        assert phrase in request, phrase

    forbidden_affirmations = [
        "we recovered the machine-readable dated tree",
        "orientation transitions occurred at 2.4 Ma",
        "historical rainfall caused orientation evolution",
        "rain adaptation was demonstrated",
    ]
    combined = (report + "\n" + request).casefold()
    for phrase in forbidden_affirmations:
        assert phrase.casefold() not in combined, phrase

    print("Chapter 2 dated-tree public recovery audit v1: VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
