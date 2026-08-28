#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data" / "evidence" / "east_asia_independent_nuclear_evidence_audit_v1.csv"
DOC = ROOT / "docs" / "chapter2" / "EAST_ASIA_INDEPENDENT_NUCLEAR_EVIDENCE_AUDIT_V1.md"


def rows():
    with LEDGER.open(encoding="utf-8", newline="") as h:
        return list(csv.DictReader(h))


def main() -> int:
    data = rows()
    ids = [r["evidence_id"] for r in data]
    expected = [f"NUC{i:02d}" for i in range(1, 14)]
    if ids != expected:
        raise AssertionError(f"nuclear evidence audit membership/order drift: {ids}")

    by = {r["evidence_id"]: r for r in data}
    if "pendulum" not in by["NUC01"]["taxon_scope"] or "setidens" not in by["NUC01"]["taxon_scope"]:
        raise AssertionError("2012 Korean rDNA evidence lost")
    if "orientation" not in by["NUC02"]["chapter2_use"]:
        raise AssertionError("2015 orientation-relevant ITS evidence lost")
    if "17K07524" not in by["NUC03"]["source_locator"]:
        raise AssertionError("Japanese pre-2025 MIG-seq/RAD project lost")
    if "MIG-seq" not in by["NUC06"]["nuclear_data_type"] or "JPN_17" not in by["NUC06"]["japan38_or_focal_overlap"]:
        raise AssertionError("C. maritimum reusable population nuclear dataset lost")
    if "reference_genome" != by["NUC07"]["scale"]:
        raise AssertionError("C. nipponicum reference-genome resource lost")
    if "104890" not in by["NUC13"]["nuclear_data_type"]:
        raise AssertionError("2020 C. japonicum transcriptome resource lost")

    pre2025 = [r for r in data if str(r["year"]).split("-")[0].isdigit() and int(str(r["year"]).split("-")[0]) < 2025]
    if len(pre2025) < 9:
        raise AssertionError(f"expected >=9 pre-2025 independent nuclear records, found {len(pre2025)}")

    phylogenetic = [r for r in data if r["scale"] not in {"functional_transcriptome", "functional_transcriptome_plus_metabolome", "reference_genome"}]
    if len(phylogenetic) < 9:
        raise AssertionError("too few phylogenetic/population nuclear evidence records")

    text = DOC.read_text(encoding="utf-8")
    required = [
        "not exhaustive",
        "harmonized common-locus nuclear framework",
        "17K07524",
        "Genepop_Cmaritimum.txt",
        "C. shantarense",
        "104,890 unigenes",
        "not Japan as a whole",
        "Japan–Korea–China–Russian Far East",
    ]
    missing = [x for x in required if x not in text]
    if missing:
        raise AssertionError(f"nuclear audit narrative missing: {missing}")

    print("east_asia_independent_nuclear_audit_valid=true")
    print(f"records={len(data)}")
    print(f"pre2025_records={len(pre2025)}")
    print(f"phylogenetic_or_population_records={len(phylogenetic)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
