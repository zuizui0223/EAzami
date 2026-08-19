#!/usr/bin/env python3
"""Build a frozen accession-level panel for testing Japanese Cirsium origin models."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOREYRA_DIR = ROOT / "data/evidence/moreyra2025_cirsium_reconciliation_v1"
CHANG25 = ROOT / "data/evidence/chang2025_public_run_manifest_v1.csv"
CHANG26 = ROOT / "data/evidence/chang2026_public_run_manifest_v1.csv"
PRIORITY = ROOT / "data/evidence/japan_cirsium_origin_priority_public_sequences_v1.csv"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as h:
        return [{k: (v or "").strip() for k, v in r.items()} for r in csv.DictReader(h)]


def moreyra_rows() -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for path in sorted(MOREYRA_DIR.glob("part_*.csv")):
        out.extend(rows(path))
    return out


def one(data: list[dict[str, str]], key: str, value: str) -> dict[str, str]:
    hit = [r for r in data if r.get(key) == value]
    if len(hit) != 1:
        raise ValueError(f"expected one {key}={value!r}; found {len(hit)}")
    return hit[0]


def subset(data: list[dict[str, str]], key: str, value: str) -> list[dict[str, str]]:
    return [r for r in data if r.get(key) == value]


def build(output: Path) -> dict[str, object]:
    m = moreyra_rows()
    c25 = rows(CHANG25)
    c26 = rows(CHANG26)
    p = rows(PRIORITY)

    dips = one(m, "tree_code", "Cirsium dipsacolepis")
    line_jp = one(m, "tree_code", "Cirsium lineare")
    line_tw = subset(c25, "taxon", "Cirsium lineare")
    brev = subset(c26, "taxon", "C. brevicaule")
    irum = subset(c26, "taxon", "C. irumtiense")
    japonicum = subset(c26, "taxon", "C. japonicum var. japonicum")

    expected = {
        "dipsacolepis": "SRR30887259",
        "lineare_japan": "SRR30887240",
        "lineare_taiwan": {"SRR30617342", "SRR30617347"},
        "brevicaule": {"SRR35152730", "SRR35152729", "SRR35152725"},
        "irumtiense": {"SRR35152732", "SRR35152731", "SRR35152724"},
        "japonicum_japan": {"SRR35152727", "SRR35152726"},
    }
    if dips["run"] != expected["dipsacolepis"]:
        raise ValueError("C. dipsacolepis run drift")
    if line_jp["run"] != expected["lineare_japan"]:
        raise ValueError("Japanese C. lineare run drift")
    if {r["run"] for r in line_tw} != expected["lineare_taiwan"]:
        raise ValueError("Taiwan C. lineare run drift")
    if {r["matched_run"] for r in brev} != expected["brevicaule"]:
        raise ValueError("C. brevicaule run drift")
    if {r["matched_run"] for r in irum} != expected["irumtiense"]:
        raise ValueError("C. irumtiense run drift")
    if {r["matched_run"] for r in japonicum} != expected["japonicum_japan"]:
        raise ValueError("Japanese C. japonicum run drift")

    all_runs = [
        dips["run"], line_jp["run"],
        *(r["run"] for r in line_tw),
        *(r["matched_run"] for r in brev),
        *(r["matched_run"] for r in irum),
        *(r["matched_run"] for r in japonicum),
    ]
    if len(all_runs) != len(set(all_runs)):
        raise ValueError("critical origin panel contains duplicate SRA runs")

    marker = {r["run_or_accession"]: r for r in p if r["taxon"] == "Cirsium lineare" and r["data_type"] == "nuclear_ribosomal"}
    if set(marker) != {"AF443727", "AF443779"}:
        raise ValueError("C. lineare ITS/ETS anchor drift")
    if any("Hubei" not in r["geographic_source"] for r in marker.values()):
        raise ValueError("C. lineare Hubei marker provenance missing")

    result: dict[str, object] = {
        "contract_version": "japan_cirsium_origin_falsification_panel_v2",
        "accepted_primary_tree_before_test": 294,
        "maximum_public_candidate_ceiling": 296,
        "critical_sra_runs": len(all_runs),
        "critical_sra_runs_unique": True,
        "lineare": {
            "japan_target_capture": {
                "run": line_jp["run"], "biosample": line_jp["biosample"],
                "voucher": line_jp["voucher_and_herbarium"],
            },
            "taiwan_transcriptomes": [
                {"run": r["run"], "biosample": r["biosample"], "voucher": r["voucher"], "location": r["geographic_location"]}
                for r in line_tw
            ],
            "china_hubei_nrdna": ["AF443727", "AF443779"],
            "sequence_anchor_regions": ["Japan", "Taiwan", "China_Hubei"],
            "high_dimensional_data_generation_groups": ["moreyra_target_capture", "chang_transcriptome_program"],
            "test": "C. lineare must remain outside the dominant Japanese radiation across BWA/BLASTx and concatenation/ASTRAL; Taiwan samples should remain with the same broad lineare lineage rather than Nipponocirsium.",
        },
        "dipsacolepis": {
            "run": dips["run"], "biosample": dips["biosample"], "voucher": dips["voucher_and_herbarium"],
            "independent_high_dimensional_replication_beyond_moreyra": 0,
            "test": "C. dipsacolepis must remain outside the dominant Japanese radiation and acquire a stable continental nearest-neighbour bracket before a third origin is promoted beyond working-hypothesis status.",
        },
        "arenicola": {
            "brevicaule_runs": sorted(expected["brevicaule"]),
            "irumtiense_runs": sorted(expected["irumtiense"]),
            "published_high_dimensional_state": "Arenicola_sister_to_Nipponocirsium",
            "test": "Do not count a fourth colonization unless Arenicola is independently bracketed by a continental lineage outside the dominant Japanese radiation under the broad nuclear tree/network sensitivity.",
        },
        "sinocirsium_bridge": {
            "japanese_japonicum_runs": sorted(expected["japonicum_japan"]),
            "test": "Use the two Japanese C. japonicum var. japonicum transcriptomes to distinguish a Japan-main-radiation affinity from a separate Taiwan-East-Asia bridge history.",
        },
        "origin_model_decision_rule": {
            "strict_single_origin": "rejected_if_lineare_exception_is_retained",
            "minimum_two_histories": "supported_if_lineare_exception_is_retained",
            "three_histories": "promote_if_lineare_exception_and_dipsacolepis_secondary_placement_are_both_stable",
            "four_or_more_histories": "promote_only_if_an_additional_lineage_such_as_Arenicola_is_independently_continental_bracketed",
        },
        "safeguards": [
            "do not infer origin count from chloroplast structure alone",
            "do not count Chang 2025 and Chang 2026 as independent data-generation programmes when samples/data are reused",
            "do not relax locus or topology gates post hoc",
            "do not freeze broad China sampling until continental sister branches are identified by the public nuclear tree",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    build(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
