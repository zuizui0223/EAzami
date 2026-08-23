#!/usr/bin/env python3
"""Validate the external-data intake state for fixed-white A1 samples.

This validator is deliberately fail-closed. Planned slots do not count as data.
A slot becomes ``available`` only when an immutable sample id, voucher/provenance,
individual-linked white-flower evidence, and a usable paired-read source are all
present.  Passing this intake gate still does not satisfy the 123/153 recovery,
replicate-placement, or expanded-tree gates.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

EXPECTED = {
    "Cirsium boninense": {"BON-01": True, "BON-02": True, "BON-03": False},
    "Cirsium wulongense": {"WUL-01": True, "WUL-02": True, "WUL-03": False},
}
ALLOWED_STATUS = {"not_acquired", "available"}
ALLOWED_SOURCE = {"sra_run", "paired_fastq_paths", "paired_fastq_urls"}
REQUIRED = {
    "sample_slot", "taxon", "slot_role", "required_for_minimum", "acquisition_status",
    "preferred_material_anchor", "immutable_sample_id", "locality", "voucher_or_herbarium_id",
    "flower_colour_link_status", "read_source_type", "read_source_1", "read_source_2",
    "raw_archive_accession", "notes",
}


def clean(x: object) -> str:
    return str(x or "").strip()


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("sample intake has no header")
        rows = [{k: clean(v) for k, v in r.items()} for r in reader if any(clean(v) for v in r.values())]
        return list(reader.fieldnames), rows


def validate(path: Path) -> dict[str, object]:
    fields, rows = read_rows(path)
    missing = REQUIRED - set(fields)
    if missing:
        raise ValueError(f"missing intake columns: {sorted(missing)}")
    if len(rows) != 6:
        raise ValueError(f"expected six A1 intake slots, observed {len(rows)}")

    seen_slots: set[str] = set()
    sample_ids: set[str] = set()
    available_by_taxon: dict[str, int] = defaultdict(int)
    status_counts = Counter()

    for row in rows:
        taxon = row["taxon"]
        slot = row["sample_slot"]
        if taxon not in EXPECTED or slot not in EXPECTED[taxon]:
            raise ValueError(f"unexpected A1 slot: {taxon}/{slot}")
        if slot in seen_slots:
            raise ValueError(f"duplicate sample slot: {slot}")
        seen_slots.add(slot)
        required = row["required_for_minimum"].lower() == "yes"
        if required != EXPECTED[taxon][slot]:
            raise ValueError(f"required/optional role drifted for {slot}")
        if not row["preferred_material_anchor"]:
            raise ValueError(f"{slot}: material identity anchor is required")

        status = row["acquisition_status"]
        if status not in ALLOWED_STATUS:
            raise ValueError(f"{slot}: unsupported acquisition_status {status!r}")
        status_counts[status] += 1

        if status == "not_acquired":
            # Do not let planned slots accumulate sample-like identifiers that can be mistaken for data.
            forbidden = [
                row["immutable_sample_id"], row["voucher_or_herbarium_id"], row["read_source_type"],
                row["read_source_1"], row["read_source_2"], row["raw_archive_accession"],
            ]
            if any(forbidden):
                raise ValueError(f"{slot}: not_acquired slot contains acquired-data identifiers")
            continue

        sid = row["immutable_sample_id"]
        if not sid:
            raise ValueError(f"{slot}: available sample lacks immutable_sample_id")
        if sid in sample_ids:
            raise ValueError(f"duplicate immutable_sample_id: {sid}")
        sample_ids.add(sid)
        if not row["locality"] or not row["voucher_or_herbarium_id"]:
            raise ValueError(f"{slot}: available sample lacks locality/voucher provenance")
        if row["flower_colour_link_status"] != "individual_linked_fixed_white":
            raise ValueError(f"{slot}: flower colour must be linked to the sequenced individual")
        source = row["read_source_type"]
        if source not in ALLOWED_SOURCE:
            raise ValueError(f"{slot}: unsupported read_source_type {source!r}")
        if source == "sra_run":
            if not row["read_source_1"] or row["read_source_2"]:
                raise ValueError(f"{slot}: sra_run requires one run accession in read_source_1")
        else:
            if not row["read_source_1"] or not row["read_source_2"]:
                raise ValueError(f"{slot}: paired FASTQ source requires read_source_1 and read_source_2")
        available_by_taxon[taxon] += 1

    expected_slots = {slot for slots in EXPECTED.values() for slot in slots}
    if seen_slots != expected_slots:
        raise ValueError("A1 intake slot set drifted")

    minimum_available = all(available_by_taxon[taxon] >= 2 for taxon in EXPECTED)
    return {
        "contract_version": "fixed_white_a1_sample_intake_v0_1",
        "slots": len(rows),
        "taxa": list(EXPECTED),
        "mandatory_slots_per_taxon": 2,
        "ideal_slots_per_taxon": 3,
        "status_counts": dict(status_counts),
        "available_samples_by_taxon": {t: available_by_taxon[t] for t in EXPECTED},
        "minimum_external_reads_available": minimum_available,
        "recovery_qc_allowed": minimum_available,
        "rate_fit_tip_promotion_allowed": False,
        "next_gate": "run frozen-153 individual recovery QC once external reads are available",
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("intake", type=Path)
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    out = validate(a.intake)
    text = json.dumps(out, indent=2, ensure_ascii=False) + "\n"
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
