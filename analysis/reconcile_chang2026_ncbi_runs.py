#!/usr/bin/env python3
"""Reconcile Chang et al. 2026 transcriptome samples with PRJNA1311153.

The official supplement identifies 33 transcriptome samples by taxon, locality,
short code, voucher and total raw-read count, but not every row carries an SRR
accession.  This script joins that table to official NCBI SRA runinfo without
relying on geography alone.

Independent evidence channels are retained explicitly:

* exact embedded SRR accession;
* exact voucher token (for example ``ccy3559``);
* exact short sample code in sample/library metadata;
* exact or species-level taxon agreement;
* exact paired- or single-end relation between supplement raw reads and SRA spots;
* locality token agreement.

A row is called verified only when an exact accession, exact voucher, or a unique
read-count + taxon combination identifies the run.  Short code or locality alone
never verifies a match.  Candidate scores are a deterministic reconciliation aid,
not a biological parameter.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping, Sequence

DEFAULT_SUPPLEMENT = Path(
    "data/evidence/chang2026_east_asia_accession_audit_2026-08-10.csv"
)
DEFAULT_MORPHS = Path(
    "data/evidence/chang2026_takaoense_figure1_morph_assignments_2026-08-11.csv"
)
DEFAULT_OUTDIR = Path("data/evidence/generated/chang2026_ncbi_reconciliation")

MATCH_FIELDS = (
    "taxon",
    "sample_number_within_taxon",
    "location",
    "code",
    "voucher",
    "herbarium",
    "raw_reads",
    "published_figure_label",
    "flower_colour_state",
    "binary_colour_code",
    "embedded_public_accession",
    "matched_run",
    "matched_experiment",
    "matched_biosample",
    "matched_scientific_name",
    "matched_library_name",
    "matched_sample_name",
    "matched_geographic_location",
    "matched_spots",
    "read_count_relation",
    "match_score",
    "second_best_score",
    "score_margin",
    "match_status",
    "match_confidence",
    "match_evidence",
    "candidate_count_with_positive_score",
    "run_assignment_collision",
    "review_note",
)

CANDIDATE_FIELDS = (
    "taxon",
    "code",
    "voucher",
    "raw_reads",
    "candidate_rank",
    "candidate_run",
    "candidate_experiment",
    "candidate_biosample",
    "candidate_scientific_name",
    "candidate_library_name",
    "candidate_sample_name",
    "candidate_spots",
    "candidate_score",
    "candidate_evidence",
    "read_count_relation",
)

SUMMARY_FIELDS = (
    "metric",
    "value",
)

TEXT_METADATA_FIELDS = (
    "LibraryName",
    "SampleName",
    "ExperimentTitle",
    "StudyTitle",
    "SampleTitle",
    "Title",
    "Description",
    "ScientificName",
    "geographic_location",
    "geo_loc_name_country_calc",
    "collection_date",
)


def clean(value: object) -> str:
    return str(value or "").strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return [
            {key: clean(value) for key, value in row.items()}
            for row in reader
            if any(clean(value) for value in row.values())
        ]


def write_csv(
    path: Path,
    rows: Iterable[Mapping[str, object]],
    fields: Sequence[str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(fields), extrasaction="ignore"
        )
        writer.writeheader()
        writer.writerows(rows)


def normalized_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def row_value(row: Mapping[str, str], *names: str) -> str:
    index = {normalized_key(key): clean(value) for key, value in row.items()}
    for name in names:
        value = index.get(normalized_key(name), "")
        if value:
            return value
    return ""


def parse_integer(value: object) -> int | None:
    text = re.sub(r"[^0-9.+-]", "", clean(value))
    if not text:
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    if not math.isfinite(number):
        return None
    return int(round(number))


def run_spots(row: Mapping[str, str]) -> int | None:
    preferred = (
        "spots",
        "total_spots",
        "spot_count",
        "spots_with_mates",
    )
    for name in preferred:
        value = row_value(row, name)
        parsed = parse_integer(value)
        if parsed is not None:
            return parsed
    for key, value in row.items():
        if "spot" in normalized_key(key):
            parsed = parse_integer(value)
            if parsed is not None:
                return parsed
    return None


def canonical_taxon(value: str) -> str:
    text = clean(value).replace("_", " ")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"^C\.\s+", "Cirsium ", text, flags=re.I)
    text = re.sub(r"\s+", " ", text).strip().casefold()
    return text


def species_signature(value: str) -> str:
    parts = canonical_taxon(value).split()
    if len(parts) < 2:
        return ""
    genus = "cirsium" if parts[0] in {"c.", "cirsium"} else parts[0]
    return f"{genus} {parts[1]}"


def taxon_relation(source: str, candidate: str) -> str:
    source_norm = canonical_taxon(source)
    candidate_norm = canonical_taxon(candidate)
    if source_norm and source_norm == candidate_norm:
        return "exact_taxon"
    if (
        species_signature(source)
        and species_signature(source) == species_signature(candidate)
    ):
        return "same_species_broad_name"
    return "different_or_unresolved_taxon"


def exact_token(token: str, text: str) -> bool:
    token = clean(token)
    if not token or not text:
        return False
    return bool(
        re.search(
            rf"(?<![A-Za-z0-9]){re.escape(token)}(?![A-Za-z0-9])",
            text,
            flags=re.I,
        )
    )


def selected_text(row: Mapping[str, str], fields: Sequence[str]) -> str:
    values = [row_value(row, field) for field in fields]
    return " | ".join(value for value in values if value)


def locality_tokens(value: str) -> tuple[str, ...]:
    stop = {
        "taiwan",
        "japan",
        "county",
        "city",
        "prefecture",
        "province",
        "township",
        "district",
        "island",
        "mount",
        "mountain",
    }
    tokens = {
        token.casefold()
        for token in re.findall(r"[A-Za-z][A-Za-z'-]{3,}", value)
        if token.casefold() not in stop
    }
    return tuple(sorted(tokens))


def read_count_relation(raw_reads: int | None, spots: int | None) -> tuple[str, int]:
    if raw_reads is None or spots is None or raw_reads <= 0 or spots <= 0:
        return "unavailable", 0
    tolerance = max(4, int(raw_reads * 1e-6))
    if abs(raw_reads - 2 * spots) <= tolerance:
        return "exact_paired_end_raw_reads_equals_2x_spots", 250
    if abs(raw_reads - spots) <= tolerance:
        return "exact_single_end_raw_reads_equals_spots", 250
    paired_relative = abs(raw_reads - 2 * spots) / raw_reads
    single_relative = abs(raw_reads - spots) / raw_reads
    if paired_relative <= 0.005:
        return "near_paired_end_within_0.5_percent", 120
    if single_relative <= 0.005:
        return "near_single_end_within_0.5_percent", 120
    return "not_matching", 0


def score_candidate(
    source: Mapping[str, str], candidate: Mapping[str, str]
) -> dict[str, object]:
    evidence: list[str] = []
    score = 0

    run = row_value(candidate, "Run")
    experiment = row_value(candidate, "Experiment")
    biosample = row_value(candidate, "BioSample")
    scientific_name = row_value(candidate, "ScientificName")
    library_name = row_value(candidate, "LibraryName")
    sample_name = row_value(candidate, "SampleName")
    geographic_location = row_value(
        candidate, "geographic_location", "geo_loc_name_country_calc"
    )

    embedded = clean(source.get("embedded_public_accession"))
    if embedded and embedded == run:
        score += 1000
        evidence.append("exact_embedded_run_accession")

    metadata_text = selected_text(candidate, TEXT_METADATA_FIELDS)
    voucher = clean(source.get("voucher"))
    if voucher and exact_token(voucher, metadata_text):
        score += 300
        evidence.append("exact_voucher_token")

    relation = taxon_relation(clean(source.get("taxon")), scientific_name)
    if relation == "exact_taxon":
        score += 80
        evidence.append("exact_taxon")
    elif relation == "same_species_broad_name":
        score += 40
        evidence.append("same_species_broad_name")

    # Short codes are useful corroboration but never sufficient by themselves.
    code = clean(source.get("code"))
    code_text = selected_text(
        candidate,
        (
            "LibraryName",
            "SampleName",
            "ExperimentTitle",
            "SampleTitle",
            "Title",
        ),
    )
    if code and exact_token(code, code_text):
        score += 35
        evidence.append("exact_short_code_token")

    source_tokens = locality_tokens(clean(source.get("location")))
    matched_locality = [
        token for token in source_tokens if exact_token(token, metadata_text)
    ]
    if matched_locality:
        score += 25
        evidence.append("locality_token:" + "+".join(matched_locality))

    raw_reads = parse_integer(source.get("raw_reads"))
    spots = run_spots(candidate)
    count_relation, count_score = read_count_relation(raw_reads, spots)
    if count_score:
        score += count_score
        evidence.append(count_relation)

    project = row_value(candidate, "BioProject")
    if project == "PRJNA1311153":
        score += 10
        evidence.append("expected_bioproject")

    return {
        "run": run,
        "experiment": experiment,
        "biosample": biosample,
        "scientific_name": scientific_name,
        "library_name": library_name,
        "sample_name": sample_name,
        "geographic_location": geographic_location,
        "spots": spots if spots is not None else "",
        "read_count_relation": count_relation,
        "score": score,
        "evidence": "|".join(evidence),
        "taxon_relation": relation,
        "has_exact_accession": "exact_embedded_run_accession" in evidence,
        "has_exact_voucher": "exact_voucher_token" in evidence,
        "has_exact_read_count": count_relation.startswith("exact_"),
    }


def classify_match(
    source: Mapping[str, str], ranked: Sequence[Mapping[str, object]]
) -> tuple[str, str, str]:
    if not ranked or int(ranked[0]["score"]) <= 0:
        return (
            "unresolved_no_positive_candidate",
            "unresolved",
            "No candidate has positive accession/voucher/read-count/taxon evidence.",
        )

    top = ranked[0]
    top_score = int(top["score"])
    second_score = int(ranked[1]["score"]) if len(ranked) > 1 else 0
    tied = len(ranked) > 1 and top_score == second_score

    if tied:
        return (
            "ambiguous_tied_top_candidates",
            "ambiguous",
            "Two or more runs have the same highest reconciliation score.",
        )
    if bool(top["has_exact_accession"]):
        return (
            "verified_exact_run_accession",
            "verified",
            "Supplement-embedded SRR accession exactly matches official runinfo.",
        )
    if bool(top["has_exact_voucher"]):
        return (
            "verified_unique_voucher_token",
            "verified",
            "Voucher token uniquely identifies the highest-scoring official run.",
        )
    if (
        bool(top["has_exact_read_count"])
        and top["taxon_relation"] in {"exact_taxon", "same_species_broad_name"}
        and top_score - second_score >= 80
    ):
        return (
            "verified_unique_read_count_and_taxon",
            "verified",
            "Exact raw-read/SRA-spot relation plus taxon agreement uniquely identifies the run.",
        )
    if top_score >= 300 and top_score - second_score >= 80:
        return (
            "probable_composite_unique_match",
            "probable",
            "Multiple corroborating fields identify one candidate, but no exact accession/voucher rule applies.",
        )
    return (
        "ambiguous_insufficient_independent_evidence",
        "ambiguous",
        "Best candidate lacks enough independent evidence for a verified match.",
    )


def morph_index(path: Path | None) -> dict[str, dict[str, str]]:
    if path is None or not path.exists():
        return {}
    rows = read_csv(path)
    return {clean(row.get("voucher")): row for row in rows if row.get("voucher")}


def reconcile(
    supplement_rows: Sequence[Mapping[str, str]],
    runinfo_rows: Sequence[Mapping[str, str]],
    morph_rows: Mapping[str, Mapping[str, str]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    matches: list[dict[str, object]] = []
    candidates_out: list[dict[str, object]] = []

    for source in supplement_rows:
        ranked = sorted(
            (score_candidate(source, candidate) for candidate in runinfo_rows),
            key=lambda item: (
                -int(item["score"]),
                str(item["run"]),
            ),
        )
        positive = [item for item in ranked if int(item["score"]) > 0]
        top = ranked[0] if ranked else {
            "run": "",
            "experiment": "",
            "biosample": "",
            "scientific_name": "",
            "library_name": "",
            "sample_name": "",
            "geographic_location": "",
            "spots": "",
            "read_count_relation": "unavailable",
            "score": 0,
            "evidence": "",
        }
        second_score = int(ranked[1]["score"]) if len(ranked) > 1 else 0
        status, confidence, note = classify_match(source, ranked)
        morph = morph_rows.get(clean(source.get("voucher")), {})

        matches.append(
            {
                "taxon": clean(source.get("taxon")),
                "sample_number_within_taxon": clean(
                    source.get("sample_number_within_taxon")
                ),
                "location": clean(source.get("location")),
                "code": clean(source.get("code")),
                "voucher": clean(source.get("voucher")),
                "herbarium": clean(source.get("herbarium")),
                "raw_reads": clean(source.get("raw_reads")),
                "published_figure_label": clean(
                    morph.get("published_figure_label")
                ),
                "flower_colour_state": clean(morph.get("flower_colour_state")),
                "binary_colour_code": clean(morph.get("binary_colour_code")),
                "embedded_public_accession": clean(
                    source.get("embedded_public_accession")
                ),
                "matched_run": top["run"] if confidence != "unresolved" else "",
                "matched_experiment": top["experiment"] if confidence != "unresolved" else "",
                "matched_biosample": top["biosample"] if confidence != "unresolved" else "",
                "matched_scientific_name": top["scientific_name"] if confidence != "unresolved" else "",
                "matched_library_name": top["library_name"] if confidence != "unresolved" else "",
                "matched_sample_name": top["sample_name"] if confidence != "unresolved" else "",
                "matched_geographic_location": top["geographic_location"] if confidence != "unresolved" else "",
                "matched_spots": top["spots"] if confidence != "unresolved" else "",
                "read_count_relation": top["read_count_relation"],
                "match_score": top["score"],
                "second_best_score": second_score,
                "score_margin": int(top["score"]) - second_score,
                "match_status": status,
                "match_confidence": confidence,
                "match_evidence": top["evidence"],
                "candidate_count_with_positive_score": len(positive),
                "run_assignment_collision": "false",
                "review_note": note,
            }
        )

        for rank, candidate in enumerate(positive[:10], start=1):
            candidates_out.append(
                {
                    "taxon": clean(source.get("taxon")),
                    "code": clean(source.get("code")),
                    "voucher": clean(source.get("voucher")),
                    "raw_reads": clean(source.get("raw_reads")),
                    "candidate_rank": rank,
                    "candidate_run": candidate["run"],
                    "candidate_experiment": candidate["experiment"],
                    "candidate_biosample": candidate["biosample"],
                    "candidate_scientific_name": candidate["scientific_name"],
                    "candidate_library_name": candidate["library_name"],
                    "candidate_sample_name": candidate["sample_name"],
                    "candidate_spots": candidate["spots"],
                    "candidate_score": candidate["score"],
                    "candidate_evidence": candidate["evidence"],
                    "read_count_relation": candidate["read_count_relation"],
                }
            )

    by_run: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in matches:
        if row["matched_run"] and row["match_confidence"] in {"verified", "probable"}:
            by_run[str(row["matched_run"])].append(row)
    for run, assigned in by_run.items():
        if len(assigned) <= 1:
            continue
        for row in assigned:
            row["run_assignment_collision"] = "true"
            row["match_confidence"] = "ambiguous"
            row["match_status"] = "ambiguous_run_assigned_to_multiple_supplement_rows"
            row["review_note"] = (
                f"Official run {run} was assigned to {len(assigned)} supplement rows; manual review required."
            )

    return matches, candidates_out


def build_summary(
    matches: Sequence[Mapping[str, object]],
    candidates: Sequence[Mapping[str, object]],
    runinfo_rows: Sequence[Mapping[str, str]],
) -> dict[str, object]:
    confidence = Counter(str(row["match_confidence"]) for row in matches)
    statuses = Counter(str(row["match_status"]) for row in matches)
    takaoense = [
        row
        for row in matches
        if "takaoense" in str(row["taxon"]).casefold()
    ]
    return {
        "supplement_sample_rows": len(matches),
        "official_runinfo_rows": len(runinfo_rows),
        "unique_official_runs": len(
            {row_value(row, "Run") for row in runinfo_rows if row_value(row, "Run")}
        ),
        "match_confidence_counts": dict(sorted(confidence.items())),
        "match_status_counts": dict(sorted(statuses.items())),
        "verified_or_probable_rows": sum(
            row["match_confidence"] in {"verified", "probable"}
            for row in matches
        ),
        "unique_matched_runs": len(
            {
                str(row["matched_run"])
                for row in matches
                if row["matched_run"]
                and row["match_confidence"] in {"verified", "probable"}
            }
        ),
        "run_assignment_collision_rows": sum(
            row["run_assignment_collision"] == "true" for row in matches
        ),
        "candidate_rows_written": len(candidates),
        "takaoense_sample_rows": len(takaoense),
        "takaoense_verified_or_probable_rows": sum(
            row["match_confidence"] in {"verified", "probable"}
            for row in takaoense
        ),
        "takaoense_runs": [
            {
                "code": row["code"],
                "voucher": row["voucher"],
                "morph": row["published_figure_label"],
                "run": row["matched_run"],
                "biosample": row["matched_biosample"],
                "confidence": row["match_confidence"],
                "status": row["match_status"],
                "evidence": row["match_evidence"],
            }
            for row in takaoense
        ],
        "interpretation_limit": (
            "A reconciled run manifest identifies public RNA-seq inputs. It does not by itself provide orthologous gene trees, distinguish introgression from ILS, or demonstrate anthocyanin reactivation."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--supplement", type=Path, default=DEFAULT_SUPPLEMENT)
    parser.add_argument("--runinfo", type=Path, required=True)
    parser.add_argument("--morphs", type=Path, default=DEFAULT_MORPHS)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    supplement = read_csv(args.supplement)
    runinfo = read_csv(args.runinfo)
    if not supplement:
        raise SystemExit(f"No supplement rows in {args.supplement}")
    if not runinfo:
        raise SystemExit(f"No runinfo rows in {args.runinfo}")

    matches, candidates = reconcile(
        supplement,
        runinfo,
        morph_index(args.morphs),
    )
    summary = build_summary(matches, candidates, runinfo)

    args.outdir.mkdir(parents=True, exist_ok=True)
    write_csv(args.outdir / "chang2026_sample_run_reconciliation.csv", matches, MATCH_FIELDS)
    write_csv(args.outdir / "chang2026_run_candidates.csv", candidates, CANDIDATE_FIELDS)
    takaoense = [row for row in matches if "takaoense" in str(row["taxon"]).casefold()]
    write_csv(args.outdir / "chang2026_takaoense_sra_manifest.csv", takaoense, MATCH_FIELDS)
    (args.outdir / "chang2026_ncbi_reconciliation_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_csv(
        args.outdir / "chang2026_ncbi_reconciliation_summary.csv",
        (
            {"metric": key, "value": json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value}
            for key, value in summary.items()
        ),
        SUMMARY_FIELDS,
    )

    print(f"supplement_sample_rows={summary['supplement_sample_rows']}")
    print(f"official_runinfo_rows={summary['official_runinfo_rows']}")
    print(f"verified_or_probable_rows={summary['verified_or_probable_rows']}")
    print(f"takaoense_sample_rows={summary['takaoense_sample_rows']}")
    print(
        "takaoense_verified_or_probable_rows="
        f"{summary['takaoense_verified_or_probable_rows']}"
    )
    print(f"run_assignment_collision_rows={summary['run_assignment_collision_rows']}")
    print(args.outdir / "chang2026_takaoense_sra_manifest.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
