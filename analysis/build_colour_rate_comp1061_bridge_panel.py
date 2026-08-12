#!/usr/bin/env python3
"""Build a 20-taxon cross-study Compositae1061 bridge panel.

The flower-colour atlas v0.3 contains 20 fixed-state, rate-fit-eligible taxa,
but they are split across Chang leaf RNA-seq and Moreyra target-capture data.
This builder joins those taxa to official SRA runs without using flower colour
or an inferred topology to choose samples.

Primary sample rule (predeclared before locus recovery):

1. source/taxon identity must match a frozen evidence route;
2. official SRA metadata must resolve the run and library layout;
3. for taxa with multiple eligible runs, choose the run with the *largest*
   official Spots value to favour locus recovery;
4. ties are broken by voucher/sample-code/run lexical order.

All eligible replicates are retained in a second manifest so the primary
single-tip tree can later be checked against replicate-inclusive sensitivity.

This creates an execution input contract only.  It does not recover reads,
run HybPiper, infer a tree, or unlock transition-rate fitting.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping, Sequence

EXPECTED_TAXA = 20
EXPECTED_STATES = {"C": 17, "W": 3}
EXPECTED_DATA_TYPES = {"leaf_rnaseq": 13, "target_capture": 7}
EXPECTED_STUDIES = {"Chang2025": 6, "Chang2026": 7, "Moreyra2025": 7}
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
    target_by_canon = {
        canonical_taxon(taxon): taxon for taxon in CHANG_RECON_TAXA
    }
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
        accepted = next(
            (taxon for taxon, names in aliases.items() if canonical in names), None
        )
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


def choose_primary(candidates: Sequence[Mapping[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
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


def validate_primary(primary: Sequence[Mapping[str, str]]) -> dict[str, object]:
    if len(primary) != EXPECTED_TAXA:
        raise ValueError(f"Primary bridge must contain {EXPECTED_TAXA} tips")
    if len({row["tip_id"] for row in primary}) != EXPECTED_TAXA:
        raise ValueError("Primary tip IDs are not unique")
    if len({row["run"] for row in primary}) != EXPECTED_TAXA:
        raise ValueError("Primary bridge runs are not unique")
    states = Counter(row["binary_colour_code"] for row in primary)
    if dict(sorted(states.items())) != EXPECTED_STATES:
        raise ValueError(f"Primary state counts drifted: {dict(states)}")
    data_types = Counter(row["data_type"] for row in primary)
    if dict(sorted(data_types.items())) != EXPECTED_DATA_TYPES:
        raise ValueError(f"Primary data-type counts drifted: {dict(data_types)}")
    studies = Counter(row["source_study"] for row in primary)
    if dict(sorted(studies.items())) != EXPECTED_STUDIES:
        raise ValueError(f"Primary source-study counts drifted: {dict(studies)}")
    if any(row["primary_tip"] != "yes" for row in primary):
        raise ValueError("Primary manifest contains non-primary row")
    if any(row["accepted_taxon"].casefold().endswith("takaoense") for row in primary):
        raise ValueError("Polymorphic var. takaoense leaked into fixed-state primary bridge")
    return {
        "taxon_count": len(primary),
        "state_counts": dict(sorted(states.items())),
        "data_type_counts": dict(sorted(data_types.items())),
        "study_counts": dict(sorted(studies.items())),
        "paired_runs": sum(row["library_layout"] == "PAIRED" for row in primary),
        "single_runs": sum(row["library_layout"] == "SINGLE" for row in primary),
        "total_spots": sum(int(row["spots"] or 0) for row in primary),
        "total_bases": sum(int(row["bases"] or 0) for row in primary),
    }


def write_csv(path: Path, rows: Iterable[Mapping[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(FIELDS), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def build(
    *,
    atlas_path: Path,
    reference_contract_path: Path,
    chang_reconciliation_path: Path,
    chang_accession_audit_path: Path,
    chang2025_runinfo_path: Path,
    moreyra_audit_path: Path,
    moreyra_runinfo_path: Path,
) -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, object]]:
    atlas_rows = atlas_eligible(atlas_path)
    reference = frozen_reference_contract(reference_contract_path)
    candidates = (
        chang_reconciliation_candidates(
            atlas_rows, chang_reconciliation_path, chang_accession_audit_path
        )
        + chang2025_direct_candidates(atlas_rows, chang2025_runinfo_path)
        + moreyra_candidates(atlas_rows, moreyra_audit_path, moreyra_runinfo_path)
    )
    primary, replicates = choose_primary(candidates)
    observed = validate_primary(primary)
    summary = {
        "contract_version": "colour_rate_comp1061_bridge_panel_v0_1",
        "reference_contract": str(reference_contract_path),
        "comp1061_reference_sha256": reference["sha256"],
        "comp1061_locus_count": reference["locus_count"],
        "primary_sample_rule": "maximum official Spots within each source-backed taxon; ties voucher/sample-code/run lexical; flower colour and topology excluded",
        "primary": observed,
        "replicate_candidate_rows": len(replicates),
        "taxa_with_multiple_candidate_runs": sorted(
            taxon
            for taxon, count in Counter(row["accepted_taxon"] for row in replicates).items()
            if count > 1
        ),
        "execution_ready_for_read_recovery": True,
        "branch_length_tree_completed": False,
        "rate_fit_execution_allowed": False,
        "required_tree_sensitivities": [
            "1061_all_public_reference_loci",
            "531_reproducible_warning_occupancy_candidates_when_mappable",
            "241_conservative_no_warning_high_occupancy_loci_when_mappable",
            "replicate_inclusive_or_per_taxon_alternative_sample_sensitivity",
            "target_capture_vs_leaf_rnaseq_occupancy_and_missingness_audit",
            "paralog_copy_conflict_audit",
        ],
        "claim_limit": (
            "The bridge panel only freezes taxon/run selection in a shared Compositae1061 coordinate system. "
            "It does not imply equivalent locus recovery between target-capture and leaf RNA-seq, does not create "
            "a branch-length tree, and does not permit empirical flower-colour transition-rate inference."
        ),
    }
    return primary, replicates, summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--atlas", type=Path, required=True)
    parser.add_argument("--reference-contract", type=Path, required=True)
    parser.add_argument("--chang-reconciliation", type=Path, required=True)
    parser.add_argument("--chang-accession-audit", type=Path, required=True)
    parser.add_argument("--chang2025-runinfo", type=Path, required=True)
    parser.add_argument("--moreyra-audit", type=Path, required=True)
    parser.add_argument("--moreyra-runinfo", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    primary, replicates, summary = build(
        atlas_path=args.atlas,
        reference_contract_path=args.reference_contract,
        chang_reconciliation_path=args.chang_reconciliation,
        chang_accession_audit_path=args.chang_accession_audit,
        chang2025_runinfo_path=args.chang2025_runinfo,
        moreyra_audit_path=args.moreyra_audit,
        moreyra_runinfo_path=args.moreyra_runinfo,
    )
    args.outdir.mkdir(parents=True, exist_ok=True)
    write_csv(args.outdir / "colour_rate_comp1061_primary_20tip_panel.csv", primary)
    write_csv(args.outdir / "colour_rate_comp1061_replicate_sensitivity_manifest.csv", replicates)
    (args.outdir / "colour_rate_comp1061_bridge_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"primary_taxa={summary['primary']['taxon_count']}")
    print("state_counts=" + json.dumps(summary["primary"]["state_counts"], sort_keys=True))
    print("data_type_counts=" + json.dumps(summary["primary"]["data_type_counts"], sort_keys=True))
    print("study_counts=" + json.dumps(summary["primary"]["study_counts"], sort_keys=True))
    print(f"replicate_candidate_rows={summary['replicate_candidate_rows']}")
    print(f"comp1061_reference_sha256={summary['comp1061_reference_sha256']}")
    print("branch_length_tree_completed=false")
    print("rate_fit_execution_allowed=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
