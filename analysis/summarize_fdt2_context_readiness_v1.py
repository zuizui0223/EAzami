#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


REQUIRED_COLUMNS = {
    "context_id",
    "source_id",
    "taxon",
    "module",
    "fdt1_seed_rows",
    "study_design",
    "study_setting",
    "study_geography",
    "latitude",
    "longitude",
    "elevation_m",
    "geography_basis",
    "geography_readiness",
    "experimental_exposure_axis",
    "exposure_assignment_unit",
    "independent_exposure_replicates",
    "exposure_readiness",
    "comparable_estimand_family",
    "effect_variance_status",
    "fdt2_use",
    "source_url",
    "claim_boundary",
}

FORBIDDEN_GEOGRAPHY_BASES = {"author_affiliation", "species_range_inference"}
ALLOWED_USES = {
    "descriptor_only",
    "directional_exposure_calibration_only",
    "mechanism_context_only",
    "not_usable",
    "geographic_meta_regression",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"missing CSV header: {path}")
        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise ValueError(f"missing columns: {sorted(missing)}")
        return [dict(row) for row in reader]


def validate_contexts(
    contexts: list[dict[str, str]], fdt1_rows: list[dict[str, str]]
) -> None:
    if not contexts:
        raise ValueError("empty FDT2 context registry")
    if len({row["context_id"] for row in contexts}) != len(contexts):
        raise ValueError("duplicate context_id")
    if len({row["source_id"] for row in contexts}) != len(contexts):
        raise ValueError("FDT2 v1 requires one source-cluster row per source_id")

    expected_counts = Counter(row["source_id"] for row in fdt1_rows)
    observed_sources = {row["source_id"] for row in contexts}
    if observed_sources != set(expected_counts):
        missing = sorted(set(expected_counts) - observed_sources)
        extra = sorted(observed_sources - set(expected_counts))
        raise ValueError(f"source mismatch: missing={missing}, extra={extra}")

    for row in contexts:
        source_id = row["source_id"]
        if int(row["fdt1_seed_rows"]) != expected_counts[source_id]:
            raise ValueError(f"wrong FDT1 row count for {source_id}")
        if bool(row["latitude"]) != bool(row["longitude"]):
            raise ValueError(f"latitude/longitude must be paired for {source_id}")
        if row["geography_basis"] in FORBIDDEN_GEOGRAPHY_BASES:
            raise ValueError(f"forbidden geography basis for {source_id}")
        if row["fdt2_use"] not in ALLOWED_USES:
            raise ValueError(f"unknown FDT2 use for {source_id}")
        if not row["claim_boundary"]:
            raise ValueError(f"missing claim boundary for {source_id}")

        if row["fdt2_use"] == "geographic_meta_regression":
            if row["comparable_estimand_family"] in {"", "none"}:
                raise ValueError(f"missing comparable estimand for {source_id}")
            if row["effect_variance_status"] != "recoverable":
                raise ValueError(f"missing recoverable variance for {source_id}")
            if row["geography_readiness"] not in {
                "reported_exact_coordinates",
                "reported_site_linkable_to_environment",
            }:
                raise ValueError(f"insufficient study geography for {source_id}")

        exposure_use = row["fdt2_use"] == "directional_exposure_calibration_only"
        if exposure_use and row["experimental_exposure_axis"] in {"", "none"}:
            raise ValueError(f"missing experimental exposure axis for {source_id}")


def summarize(contexts: list[dict[str, str]]) -> dict[str, object]:
    use_counts = Counter(row["fdt2_use"] for row in contexts)
    geo_counts = Counter(row["geography_readiness"] for row in contexts)
    exposure_counts = Counter(row["exposure_readiness"] for row in contexts)
    module_sources: dict[str, int] = dict(
        sorted(Counter(row["module"] for row in contexts).items())
    )
    meta_ready = [
        row["source_id"]
        for row in contexts
        if row["fdt2_use"] == "geographic_meta_regression"
    ]
    exposure_direction = [
        row["source_id"]
        for row in contexts
        if row["fdt2_use"] == "directional_exposure_calibration_only"
    ]
    return {
        "contract_version": "fdt2_context_readiness_v1",
        "unit_of_accounting": "one published source/study cluster, not one FDT1 response row",
        "source_clusters": len(contexts),
        "module_source_counts": module_sources,
        "geography_readiness_counts": dict(sorted(geo_counts.items())),
        "exposure_readiness_counts": dict(sorted(exposure_counts.items())),
        "fdt2_use_counts": dict(sorted(use_counts.items())),
        "geographic_meta_regression_ready_sources": meta_ready,
        "directional_exposure_calibration_sources": exposure_direction,
        "gate_decision": {
            "geographic_meta_regression": (
                "READY" if meta_ready else "NOT_READY_NO_HOMOLOGOUS_GEOREFERENCED_EFFECT_FAMILY"
            ),
            "experimental_exposure_synthesis": (
                "DIRECTIONAL_CALIBRATION_ONLY"
                if exposure_direction
                else "NOT_READY"
            ),
            "next_valid_action": (
                "Build an outcome-and-variance ledger only within a preregistered "
                "homologous module x mediator x fitness-stage family; do not fit a "
                "latitude slope or pool current cross-module responses."
            ),
        },
        "claim_boundary": (
            "FDT2 v1 audits recoverable study geography and imposed exposure. It does "
            "not estimate a geographic response surface, transport an external effect "
            "to a Cirsium tip, or treat missing context as zero exposure."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--context", type=Path, required=True)
    parser.add_argument("--fdt1", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    contexts = read_csv(args.context)
    # FDT1 has a different schema, so read it without applying the context contract.
    with args.fdt1.open(encoding="utf-8-sig", newline="") as handle:
        fdt1_rows = [dict(row) for row in csv.DictReader(handle)]
    validate_contexts(contexts, fdt1_rows)
    result = summarize(contexts)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
