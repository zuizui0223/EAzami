#!/usr/bin/env python3
"""Validate the updated public-recovery state for the fixed-white A1 panel."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as h:
        return [{k: str(v or "").strip() for k, v in row.items()} for row in csv.DictReader(h)]


def validate(recovery_path: Path, priority_path: Path) -> dict[str, object]:
    recovery = json.loads(recovery_path.read_text(encoding="utf-8"))
    priority = read_csv(priority_path)
    by_taxon = {r["taxon"]: r for r in priority}
    if set(by_taxon) != {"Cirsium boninense", "Cirsium wulongense"}:
        raise ValueError("A1 v2 must contain exactly the two fixed-white candidates")

    if recovery["taxon"] != "Cirsium boninense":
        raise ValueError("unexpected recovery taxon")
    study = recovery["genetic_study"]
    if study["method_status"] != "MIG-seq_confirmed_from_public_institutional_summary":
        raise ValueError("MIG-seq method must be explicitly source-backed")
    if "MIG-seq" not in study["method"]:
        raise ValueError("method text lost MIG-seq")
    taxa = study["comparison_taxa_as_indexed"]
    if len(taxa) != 5 or "Cirsium boninense" not in taxa or "Cirsium brevicaule" not in taxa:
        raise ValueError("five-taxon indexed comparison set changed")
    if recovery["rate_tree_compatibility"]["compositae1061_compatible_tip_recovered"] is not False:
        raise ValueError("MIG-seq summary must not be promoted to Compositae1061 tip")
    decision = recovery["current_decision"]
    if decision["usable_nuclear_tip_recovered"] is not False:
        raise ValueError("reusable nuclear tip is still unrecovered")
    if decision["rate_fit_tip_promotion_allowed"] is not False:
        raise ValueError("rate-fit promotion must remain blocked")
    if decision["new_field_sampling_triggered"] is not False:
        raise ValueError("method recovery alone must not trigger field sampling")

    bon = by_taxon["Cirsium boninense"]
    if "MIG-seq" not in bon["current_public_molecular_status"]:
        raise ValueError("A1 priority did not absorb MIG-seq recovery")
    if bon["rate_fit_tip_promotion_allowed"].lower() != "false":
        raise ValueError("boninense cannot be rate-fit eligible yet")
    if "Compositae1061" not in bon["rate_tree_compatibility"]:
        raise ValueError("A1 priority must keep the common-locus incompatibility explicit")

    wul = by_taxon["Cirsium wulongense"]
    if wul["rate_fit_tip_promotion_allowed"].lower() != "false":
        raise ValueError("wulongense remains blocked")

    return {
        "contract_version": "boninense_migseq_public_recovery_validation_v1",
        "boninense_method_confirmed": "MIG-seq",
        "comparison_taxa_count": 5,
        "sample_count_recovered": False,
        "raw_or_genotype_data_recovered": False,
        "compositae1061_tip_recovered": False,
        "rate_fit_tip_promotion_allowed": False,
        "new_core190_populations": 0,
        "next_gate": "recover MIG-seq sample/voucher/result/accession details; otherwise retain conditional >=2-individual homologous nuclear placement plan",
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--recovery", type=Path, required=True)
    p.add_argument("--priority", type=Path, required=True)
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    result = validate(a.recovery, a.priority)
    text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if a.output:
        a.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
