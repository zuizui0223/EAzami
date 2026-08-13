#!/usr/bin/env python3
"""Audit all currently discoverable public NCBI SRA records assigned to Cirsium.

The goal is not to append every run to the phylogeny. It is to identify public
nuclear sequence sources outside the frozen 294-tip Moreyra+Chang core that could
be projected into the same Compositae1061 locus space.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Mapping, Sequence

import recover_ncbi_project_runs as ncbi


def clean(value: object) -> str:
    return str(value or "").strip()


def norm(value: object) -> str:
    return clean(value).casefold().replace("-", "_").replace(" ", "_")


def read_known_runs(path: Path) -> set[str]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows or "run_accessions" not in rows[0]:
        raise ValueError("known panel must contain run_accessions")
    runs = {
        accession
        for row in rows
        for accession in clean(row.get("run_accessions")).split("|")
        if accession
    }
    if len(runs) != 295:
        raise ValueError(f"expected 295 unique known SRRs, found {len(runs)}")
    return runs


def esearch_cirsium(client: ncbi.NCBIClient, retmax: int = 100_000) -> list[str]:
    payload = client.get(
        ncbi.ESEARCH_URL,
        {
            "db": "sra",
            "term": "Cirsium[Organism]",
            "retmax": retmax,
            "retmode": "json",
        },
    )
    result = json.loads(payload.decode("utf-8"))
    search = result.get("esearchresult", {})
    count = int(search.get("count", 0))
    ids = [str(item) for item in search.get("idlist", [])]
    if count > retmax:
        raise RuntimeError(f"Cirsium SRA query returned {count} records > retmax={retmax}")
    if count != len(ids):
        raise RuntimeError(f"ESearch reported {count} Cirsium records but returned {len(ids)} UIDs")
    return ids


def compatibility_class(row: Mapping[str, str]) -> tuple[str, str]:
    strategy = norm(row.get("LibraryStrategy"))
    source = norm(row.get("LibrarySource"))
    selection = norm(row.get("LibrarySelection"))
    library = norm(row.get("LibraryName"))

    if strategy in {"rna_seq", "rnaseq"}:
        return "direct_common_locus_candidate", "RNA_seq"
    if strategy in {"wgs", "wxs"}:
        return "direct_common_locus_candidate", strategy.upper()
    if "hybrid" in selection or "capture" in selection or "target" in strategy:
        return "direct_common_locus_candidate", "target_capture_or_hybrid_selection"
    if strategy in {"other", "unknown", ""}:
        text = "_".join((strategy, source, selection, library))
        if any(token in text for token in ("hybpiper", "hybrid", "capture", "bait", "target")):
            return "direct_common_locus_candidate", "metadata_indicates_target_capture"
        return "manual_assay_review", "OTHER_or_unspecified"
    if any(token in strategy for token in ("rad", "gbs", "amplicon")):
        return "not_directly_common_locus_compatible", "reduced_representation_or_amplicon"
    return "manual_assay_review", strategy or "unclassified"


def audit(rows: Sequence[Mapping[str, str]], known_runs: set[str]) -> tuple[list[dict[str, str]], dict[str, object]]:
    if not rows:
        raise ValueError("global Cirsium SRA query returned no runinfo rows")
    out: list[dict[str, str]] = []
    for row in rows:
        run = clean(row.get("Run"))
        scientific = clean(row.get("ScientificName"))
        if not run or not scientific.casefold().startswith("cirsium"):
            continue
        cls, reason = compatibility_class(row)
        out.append(
            {
                "Run": run,
                "BioSample": clean(row.get("BioSample")),
                "BioProject": clean(row.get("BioProject")),
                "ScientificName": scientific,
                "LibraryStrategy": clean(row.get("LibraryStrategy")),
                "LibrarySource": clean(row.get("LibrarySource")),
                "LibrarySelection": clean(row.get("LibrarySelection")),
                "LibraryLayout": clean(row.get("LibraryLayout")),
                "Platform": clean(row.get("Platform")),
                "Model": clean(row.get("Model")),
                "spots": clean(row.get("spots")),
                "bases": clean(row.get("bases")),
                "size_MB": clean(row.get("size_MB")),
                "known_primary_295_srr": str(run in known_runs).lower(),
                "common_locus_compatibility_class": cls,
                "compatibility_reason": reason,
            }
        )

    extra = [row for row in out if row["known_primary_295_srr"] == "false"]
    direct = [
        row for row in extra
        if row["common_locus_compatibility_class"] == "direct_common_locus_candidate"
    ]
    direct_biosamples = {row["BioSample"] for row in direct if row["BioSample"]}
    summary: dict[str, object] = {
        "contract_version": "global_cirsium_sra_nuclear_audit_v1",
        "query": "Cirsium[Organism] in NCBI SRA",
        "global_cirsium_public_runs": len(out),
        "known_primary_panel_runs_recovered_by_global_query": sum(
            row["known_primary_295_srr"] == "true" for row in out
        ),
        "known_primary_panel_runs_total": len(known_runs),
        "extra_public_cirsium_runs": len(extra),
        "extra_direct_common_locus_candidate_runs": len(direct),
        "extra_direct_common_locus_candidate_biosamples": len(direct_biosamples),
        "extra_direct_candidate_taxa": sorted({row["ScientificName"] for row in direct}),
        "extra_direct_candidate_bioprojects": sorted({row["BioProject"] for row in direct if row["BioProject"]}),
        "extra_compatibility_class_counts": dict(sorted(Counter(
            row["common_locus_compatibility_class"] for row in extra
        ).items())),
        "extra_library_strategy_counts": dict(sorted(Counter(
            row["LibraryStrategy"] or "UNKNOWN" for row in extra
        ).items())),
        "primary_294_panel_changed": False,
        "automatic_tip_admission_allowed": False,
        "admission_rule": (
            "Extra runs are candidates only. Collapse by biological sample, verify taxon/provenance, "
            "recover the same frozen Compositae1061 loci, and pass orthology/copy-state/occupancy "
            "before adding any new individual to a maximum-public sensitivity tree."
        ),
        "new_china_sampling_freeze_allowed": False,
    }
    return out, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--known-panel", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--email", default=os.getenv("NCBI_EMAIL", ""))
    parser.add_argument("--api-key", default=os.getenv("NCBI_API_KEY"))
    args = parser.parse_args()

    known = read_known_runs(args.known_panel)
    client = ncbi.NCBIClient(ncbi.ClientConfig(email=args.email, api_key=args.api_key))
    uids = esearch_cirsium(client)
    rows = ncbi.fetch_runinfo(client, uids)
    audit_rows, summary = audit(rows, known)

    args.outdir.mkdir(parents=True, exist_ok=True)
    fields = list(audit_rows[0])
    with (args.outdir / "global_cirsium_sra_run_audit.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(audit_rows)

    extra_direct = [
        row for row in audit_rows
        if row["known_primary_295_srr"] == "false"
        and row["common_locus_compatibility_class"] == "direct_common_locus_candidate"
    ]
    with (args.outdir / "extra_direct_common_locus_candidates.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(extra_direct)

    summary["sra_uid_count"] = len(uids)
    summary["runinfo_row_count"] = len(rows)
    (args.outdir / "global_cirsium_sra_nuclear_audit_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
