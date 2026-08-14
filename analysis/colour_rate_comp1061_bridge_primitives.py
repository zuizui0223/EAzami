#!/usr/bin/env python3
"""Shared parsing and reconciliation primitives for the colour-rate bridge.

This module intentionally has no executable entry point and no scientific
source-study partition of its own. The canonical supported builder is
``build_colour_rate_comp1061_bridge_panel.py``; it owns the corrected
Chang2025=3 / Chang2026=10 / Moreyra2025=7 contract. Helpers here only perform
source-backed parsing, run reconciliation, deterministic sample selection and
CSV writing.
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping, Sequence

EXPECTED_TAXA = 20
EXPECTED_STATES = {"C": 17, "W": 3}
EXPECTED_DATA_TYPES = {"leaf_rnaseq": 13, "target_capture": 7}
EXPECTED_REFERENCE_SHA256 = "77d510ef101d08a7a23a4df391d077d3b7f75482c66f7f4bea6d32cf290ced2c"
EXPECTED_REFERENCE_LOCI = 1061

CHANG_RECON_TAXA = {
    "Cirsium brevicaule",
    "Cirsium irumtiense",
    "Cirsium japonicum var. albescens",
    "Cirsium japonicum var. australe",
    "Cirsium japonicum var. fukienense",
    "Cirsium japonicum var. japonicum",
    "Cirsium kawakamii",
    "Cirsium morii",
    "Cirsium pengii",
    "Cirsium tatakaense",
}
CHANG2025_DIRECT_TAXA = {
    "Cirsium suffultum",
    "Cirsium nipponicum var. incomptum",
    "Cirsium kujuense",
}
MOREYRA_TAXA = {
    "Cirsium alpicola",
    "Cirsium fanjingshanense",
    "Cirsium gyojanum",
    "Cirsium kamtschaticum",
    "Cirsium maritimum",
    "Cirsium nippoense",
    "Cirsium yezoense",
}
CHANG2025_SRA_ALIASES = {
    "Cirsium suffultum": {"Cirsium suffultum"},
    "Cirsium nipponicum var. incomptum": {
        "Cirsium nipponicum var. incomptum",
        "Cirsium incomptum",
    },
    "Cirsium kujuense": {"Cirsium kujuense"},
}

FIELDS = (
    "tip_id",
    "accepted_taxon",
    "binary_colour_code",
    "atlas_record_id",
    "phylogeny_context",
    "source_study",
    "source_bioproject",
    "data_type",
    "run",
    "experiment",
    "biosample",
    "voucher",
    "source_sample_code",
    "sra_scientific_name",
    "library_layout",
    "spots",
    "bases",
    "primary_tip",
    "sample_selection_rule",
    "source_evidence",
    "claim_limit",
)


def clean(value: object) -> str:
    return str(value or "").strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [
            {key: clean(value) for key, value in row.items()}
            for row in csv.DictReader(handle)
            if any(clean(value) for value in row.values())
        ]


def canonical_taxon(value: object) -> str:
    text = clean(value).replace("_", " ")
    text = re.sub(r"^C\.\s*", "Cirsium ", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()
    return text.casefold()


def safe_tip_id(taxon: str) -> str:
    value = re.sub(r"[^A-Za-z0-9]+", "_", taxon).strip("_")
    if not value:
        raise ValueError(f"Cannot construct tip ID for {taxon!r}")
    return value


def integer_field(row: Mapping[str, str], *names: str) -> int:
    lower = {key.casefold(): value for key, value in row.items()}
    for name in names:
        value = clean(lower.get(name.casefold()))
        if value:
            try:
                return int(float(value.replace(",", "")))
            except ValueError as exc:
                raise ValueError(f"Invalid integer field {name}={value!r}") from exc
    return 0


def value_field(row: Mapping[str, str], *names: str) -> str:
    lower = {key.casefold(): value for key, value in row.items()}
    for name in names:
        value = clean(lower.get(name.casefold()))
        if value:
            return value
    return ""


def atlas_eligible(path: Path) -> list[dict[str, str]]:
    rows = [row for row in read_csv(path) if row.get("rate_fit_eligible") == "yes"]
    if len(rows) != EXPECTED_TAXA:
        raise ValueError(f"Expected {EXPECTED_TAXA} eligible atlas taxa, observed {len(rows)}")
    taxa = [row["accepted_taxon"] for row in rows]
    if len(taxa) != len(set(taxa)):
        raise ValueError("Rate-fit atlas has duplicate eligible taxon-level records")
    states = Counter(row["binary_colour_code"] for row in rows)
    if dict(sorted(states.items())) != EXPECTED_STATES:
        raise ValueError(f"Expected eligible states {EXPECTED_STATES}, observed {dict(states)}")
    if any(row.get("observation_unit") != "taxon" for row in rows):
        raise ValueError("Bridge panel may use only taxon-level eligible atlas records")
    if any(row.get("binary_colour_code") not in {"C", "W"} for row in rows):
        raise ValueError("Polymorphic/unknown atlas records leaked into the bridge panel")

    expected_partition = CHANG_RECON_TAXA | CHANG2025_DIRECT_TAXA | MOREYRA_TAXA
    if set(taxa) != expected_partition:
        missing = sorted(expected_partition - set(taxa))
        extra = sorted(set(taxa) - expected_partition)
        raise ValueError(f"Atlas/source partition drifted; missing={missing}, extra={extra}")
    return sorted(rows, key=lambda row: row["accepted_taxon"])


def frozen_reference_contract(path: Path) -> dict[str, object]:
    x = json.loads(path.read_text(encoding="utf-8"))
    if x.get("compatibility_reanalysis_usable") is not True:
        raise ValueError("Frozen original Compositae1061 reference is not compatibility-usable")
    if x.get("sha256") != EXPECTED_REFERENCE_SHA256:
        raise ValueError("Original Compositae1061 SHA256 drifted")
    if x.get("locus_count") != EXPECTED_REFERENCE_LOCI:
        raise ValueError("Original Compositae1061 locus count drifted")
    if x.get("moreyra_augmented_reference_recovered") is not False:
        raise ValueError("Original reference was incorrectly promoted to Moreyra augmented reference")
    return x


def atlas_index(rows: Sequence[Mapping[str, str]]) -> dict[str, Mapping[str, str]]:
    return {clean(row["accepted_taxon"]): row for row in rows}


def accession_audit_by_voucher(path: Path) -> dict[str, dict[str, str]]:
    rows = read_csv(path)
    output: dict[str, dict[str, str]] = {}
    for row in rows:
        voucher = clean(row.get("voucher"))
        if not voucher:
            continue
        if voucher in output:
            raise ValueError(f"Duplicate Chang accession-audit voucher: {voucher}")
        output[voucher] = row
    return output


def make_row(
    *,
    atlas: Mapping[str, str],
    study: str,
    bioproject: str,
    data_type: str,
    run: str,
    experiment: str,
    biosample: str,
    voucher: str,
    source_sample_code: str,
    scientific_name: str,
    library_layout: str,
    spots: int,
    bases: int,
    source_evidence: str,
) -> dict[str, str]:
    if not run.startswith(("SRR", "ERR", "DRR")):
        raise ValueError(f"Unexpected run accession for {atlas['accepted_taxon']}: {run}")
    if library_layout.upper() not in {"PAIRED", "SINGLE"}:
        raise ValueError(
            f"Unsupported official library layout for {atlas['accepted_taxon']}: {library_layout!r}"
        )
    return {
        "tip_id": safe_tip_id(atlas["accepted_taxon"]),
        "accepted_taxon": atlas["accepted_taxon"],
        "binary_colour_code": atlas["binary_colour_code"],
        "atlas_record_id": atlas["record_id"],
        "phylogeny_context": atlas["phylogeny_context"],
        "source_study": study,
        "source_bioproject": bioproject,
        "data_type": data_type,
        "run": run,
        "experiment": experiment,
        "biosample": biosample,
        "voucher": voucher,
        "source_sample_code": source_sample_code,
        "sra_scientific_name": scientific_name,
        "library_layout": library_layout.upper(),
        "spots": str(spots),
        "bases": str(bases),
        "primary_tip": "no",
        "sample_selection_rule": "maximum official Spots among source-backed eligible runs; ties voucher/sample-code/run lexical; flower colour and topology excluded from selection",
        "source_evidence": source_evidence,
        "claim_limit": "Common-locus execution input only; cross-library recovery/occupancy bias and paralogy must be tested before interpreting branch lengths or colour-transition rates.",
    }


def chang_reconciliation_candidates(
    atlas_rows: Sequence[Mapping[str, str]],
    reconciliation_path: Path,
    accession_audit_path: Path,
) -> list[dict[str, str]]:
    target_by_canon = {canonical_taxon(taxon): taxon for taxon in CHANG_RECON_TAXA}
    atlas_by_name = atlas_index(atlas_rows)
    voucher_audit = accession_audit_by_voucher(accession_audit_path)
    candidates: list[dict[str, str]] = []
    for source in read_csv(reconciliation_path):
        accepted = target_by_canon.get(canonical_taxon(source.get("taxon")))
        if not accepted:
            continue
        if source.get("match_confidence") not in {"verified", "probable"}:
            continue
        voucher = clean(source.get("voucher"))
        evidence = voucher_audit.get(voucher)
        if not evidence:
            raise ValueError(f"No Chang source audit row for reconciled voucher {voucher}")
        bioproject = clean(evidence.get("bioproject"))
        if bioproject not in {"PRJNA1311153", "PRJNA1158676"}:
            raise ValueError(f"Unexpected Chang BioProject for {voucher}: {bioproject}")
        study = "Chang2026" if bioproject == "PRJNA1311153" else "Chang2025"
        candidates.append(
            make_row(
                atlas=atlas_by_name[accepted],
                study=study,
                bioproject=bioproject,
                data_type="leaf_rnaseq",
                run=source["matched_run"],
                experiment=source.get("matched_experiment", ""),
                biosample=source.get("matched_biosample", ""),
                voucher=voucher,
                source_sample_code=source.get("code", ""),
                scientific_name=source.get("matched_scientific_name", ""),
                library_layout=source.get("matched_library_layout", ""),
                spots=integer_field(source, "matched_spots"),
                bases=0,
                source_evidence="chang2026_sample_run_reconciliation + chang2026_east_asia_accession_audit",
            )
        )
    observed = {row["accepted_taxon"] for row in candidates}
    if observed != CHANG_RECON_TAXA:
        raise ValueError(
            f"Chang complete reconciliation did not cover required taxa; missing={sorted(CHANG_RECON_TAXA-observed)}"
        )
    return candidates


def chang2025_direct_candidates(
    atlas_rows: Sequence[Mapping[str, str]],
    runinfo_path: Path,
) -> list[dict[str, str]]:
    atlas_by_name = atlas_index(atlas_rows)
    aliases = {
        taxon: {canonical_taxon(alias) for alias in values}
        for taxon, values in CHANG2025_SRA_ALIASES.items()
    }
    candidates: list[dict[str, str]] = []
    for source in read_csv(runinfo_path):
        scientific = value_field(source, "ScientificName")
        canonical = canonical_taxon(scientific)
        accepted = next((taxon for taxon, names in aliases.items() if canonical in names), None)
        if not accepted:
            continue
        candidates.append(
            make_row(
                atlas=atlas_by_name[accepted],
                study="Chang2025",
                bioproject="PRJNA1158676",
                data_type="leaf_rnaseq",
                run=value_field(source, "Run"),
                experiment=value_field(source, "Experiment"),
                biosample=value_field(source, "BioSample"),
                voucher=value_field(source, "isolate", "SampleName", "LibraryName"),
                source_sample_code=value_field(source, "LibraryName", "SampleName"),
                scientific_name=scientific,
                library_layout=value_field(source, "LibraryLayout"),
                spots=integer_field(source, "spots"),
                bases=integer_field(source, "bases"),
                source_evidence="official PRJNA1158676 SRA runinfo exact accepted-name/declared-synonym match",
            )
        )
    observed = {row["accepted_taxon"] for row in candidates}
    if observed != CHANG2025_DIRECT_TAXA:
        raise ValueError(
            f"PRJNA1158676 runinfo did not cover direct Chang2025 taxa; missing={sorted(CHANG2025_DIRECT_TAXA-observed)}"
        )
    return candidates


def runinfo_by_run(path: Path) -> dict[str, dict[str, str]]:
    output: dict[str, dict[str, str]] = {}
    for row in read_csv(path):
        run = value_field(row, "Run")
        if not run:
            continue
        if run in output:
            raise ValueError(f"Duplicate official runinfo row: {run}")
        output[run] = row
    return output


def moreyra_candidates(
    atlas_rows: Sequence[Mapping[str, str]],
    audit_path: Path,
    runinfo_path: Path,
) -> list[dict[str, str]]:
    atlas_by_name = atlas_index(atlas_rows)
    runinfo = runinfo_by_run(runinfo_path)
    audit_by_taxon: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_csv(audit_path):
        tree_code = clean(row.get("tree_code"))
        if tree_code in MOREYRA_TAXA:
            audit_by_taxon[tree_code].append(row)
    if set(audit_by_taxon) != MOREYRA_TAXA:
        raise ValueError(
            f"Moreyra sample audit missing bridge taxa: {sorted(MOREYRA_TAXA-set(audit_by_taxon))}"
        )

    candidates: list[dict[str, str]] = []
    for accepted in sorted(MOREYRA_TAXA):
        rows = audit_by_taxon[accepted]
        if len(rows) != 1:
            raise ValueError(f"Expected one frozen Moreyra audit row for {accepted}, observed {len(rows)}")
        audit = rows[0]
        run = audit["run"]
        official = runinfo.get(run)
        if not official:
            raise ValueError(f"Moreyra audit run absent from PRJNA957074 runinfo: {run}")
        official_biosample = value_field(official, "BioSample")
        if audit.get("biosample") and official_biosample != audit["biosample"]:
            raise ValueError(
                f"Moreyra audit/runinfo BioSample mismatch for {accepted}: {audit['biosample']} != {official_biosample}"
            )
        candidates.append(
            make_row(
                atlas=atlas_by_name[accepted],
                study="Moreyra2025",
                bioproject="PRJNA957074",
                data_type="target_capture",
                run=run,
                experiment=value_field(official, "Experiment"),
                biosample=official_biosample,
                voucher=audit.get("voucher_and_herbarium", ""),
                source_sample_code=audit.get("library_name", ""),
                scientific_name=value_field(official, "ScientificName"),
                library_layout=value_field(official, "LibraryLayout"),
                spots=integer_field(official, "spots"),
                bases=integer_field(official, "bases"),
                source_evidence="moreyra2025_east_ne_asia_sample_audit + official PRJNA957074 SRA runinfo",
            )
        )
    return candidates


def choose_primary(
    candidates: Sequence[Mapping[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    seen_runs: set[str] = set()
    for source in candidates:
        row = dict(source)
        run = row["run"]
        if run in seen_runs:
            raise ValueError(f"Run reused across bridge candidates: {run}")
        seen_runs.add(run)
        grouped[row["accepted_taxon"]].append(row)

    if len(grouped) != EXPECTED_TAXA:
        raise ValueError(f"Expected candidates for {EXPECTED_TAXA} taxa, observed {len(grouped)}")

    primary: list[dict[str, str]] = []
    all_rows: list[dict[str, str]] = []
    for taxon in sorted(grouped):
        rows = sorted(
            grouped[taxon],
            key=lambda row: (
                -int(row["spots"] or 0),
                row["voucher"],
                row["source_sample_code"],
                row["run"],
            ),
        )
        selected_run = rows[0]["run"]
        for row in rows:
            row = dict(row)
            row["primary_tip"] = "yes" if row["run"] == selected_run else "no"
            all_rows.append(row)
            if row["primary_tip"] == "yes":
                primary.append(row)
    return primary, all_rows


def write_csv(path: Path, rows: Iterable[Mapping[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(FIELDS), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
