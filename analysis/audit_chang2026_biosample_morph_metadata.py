#!/usr/bin/env python3
"""Audit PRJNA1311153 BioSample metadata for sample-level flower colour.

Chang et al. (2026) Figure 1 marks six ``Cirsium japonicum var. takaoense``
tips as white-corolla (W) or bluish-purple-corolla (BP), whereas Supplementary
Table S1 does not expose the mapping. This script inspects official NCBI SRA
runinfo and the complete BioSample attribute dictionaries for direct phenotype,
flower-colour, morph, pigment, or voucher evidence.

Assignments are deliberately conservative:

* no morph is inferred from locality, elevation, herbarium, read count, or tree
  position;
* a colour state is accepted only from an explicit NCBI attribute containing a
  white or purple/bluish-purple expression;
* conflicting or generic colour-polymorphism text remains unresolved;
* a published voucher is linked to a public run only through an explicit
  voucher/sample identifier or an unambiguous exact SampleName suffix, never
  through locality alone when a stronger identifier is available.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from recover_ncbi_project_runs import (
    ClientConfig,
    NCBIClient,
    biosample_attributes,
)

DEFAULT_SEED = Path(
    "data/evidence/chang2026_east_asia_accession_audit_2026-08-10.csv"
)
DEFAULT_OUTDIR = Path("data/evidence/generated/chang2026_biosample_morph_audit")
TARGET_TAXON = "Cirsium japonicum var. takaoense"

AUDIT_FIELDS = (
    "accepted_taxon",
    "location",
    "code",
    "coordinate",
    "altitude_m",
    "voucher",
    "herbarium_supplement_s1",
    "run",
    "experiment",
    "biosample",
    "sra_scientific_name",
    "sample_name",
    "library_name",
    "biosample_isolate",
    "run_match_basis",
    "biosample_attribute_count",
    "morph_relevant_attributes",
    "direct_ncbi_colour_label",
    "flower_colour_state",
    "binary_colour_code",
    "assignment_confidence",
    "review_status",
    "evidence_source",
    "notes",
)

LONG_FIELDS = (
    "biosample",
    "run",
    "experiment",
    "scientific_name",
    "sample_name",
    "library_name",
    "attribute_name",
    "attribute_value",
    "morph_relevant",
)

RELEVANT_PATTERN = re.compile(
    r"flower|floral|corolla|colo(?:u)?r|morph|phenotype|pigment|anthocyanin|"
    r"white|purple|violet|lilac|pink",
    flags=re.IGNORECASE,
)
WHITE_PATTERN = re.compile(r"(?<![A-Za-z])white(?:[- ]flower(?:ed)?)?(?![A-Za-z])", re.I)
PURPLE_PATTERN = re.compile(
    r"(?<![A-Za-z])(?:bluish[- ]?purple|blue[- ]?purple|purple|violet|lilac)"
    r"(?:[- ]flower(?:ed)?)?(?![A-Za-z])",
    re.I,
)


def clean(value: object) -> str:
    return str(value or "").strip()


def compact(value: object) -> str:
    return re.sub(r"\s+", " ", clean(value).replace("_", " ")).strip()


def canonical_taxon(value: object) -> str:
    text = compact(value).casefold()
    if text.startswith("c. "):
        text = "cirsium " + text[3:]
    return text


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [
            {key: clean(value) for key, value in row.items()}
            for row in csv.DictReader(handle)
            if any(clean(value) for value in row.values())
        ]


def write_csv(
    path: Path,
    rows: Iterable[Mapping[str, object]],
    fields: Sequence[str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def target_seed_rows(rows: Sequence[Mapping[str, str]]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for row in rows:
        if canonical_taxon(row.get("taxon")) != canonical_taxon(TARGET_TAXON):
            continue
        output.append(
            {
                "accepted_taxon": TARGET_TAXON,
                "location": clean(row.get("location")),
                "code": clean(row.get("code")),
                "coordinate": clean(row.get("coordinate")),
                "altitude_m": clean(row.get("altitude_m")),
                "voucher": clean(row.get("voucher")),
                "herbarium_supplement_s1": clean(row.get("herbarium")),
            }
        )
    return sorted(output, key=lambda row: row["voucher"])


def token_present(token: str, text: str) -> bool:
    if not token:
        return False
    return bool(
        re.search(
            rf"(?<![A-Za-z0-9]){re.escape(token)}(?![A-Za-z0-9])",
            text,
            flags=re.IGNORECASE,
        )
    )


def voucher_numeric_id(value: object) -> str:
    """Extract the numeric collector/isolate identifier from values such as ccy3559."""
    match = re.fullmatch(r"(?:ccy)?\s*[-_ ]?(\d+)", clean(value), flags=re.IGNORECASE)
    return match.group(1) if match else ""


def exact_takaoense_sample_suffix(voucher: object, sample_name: object) -> bool:
    """Match ``ccy3559`` only to an explicit ``...takaoense-3559`` SampleName."""
    numeric = voucher_numeric_id(voucher)
    sample = compact(sample_name)
    if not numeric or "takaoense" not in sample.casefold():
        return False
    return bool(re.search(rf"(?:^|[-_ ]){re.escape(numeric)}$", sample, flags=re.IGNORECASE))


def locality_tokens(location: str) -> list[str]:
    """Return only explicit named localities, never coordinates or regions."""
    value = compact(location)
    if ":" in value:
        value = value.split(":", 1)[1]
    tokens = [part.strip() for part in re.split(r"[,;/]", value) if part.strip()]
    return [token for token in tokens if len(token) >= 4]


def run_search_text(row: Mapping[str, str]) -> str:
    return " | ".join(compact(value) for value in row.values() if clean(value))


def candidate_target_runs(rows: Sequence[Mapping[str, str]]) -> list[dict[str, str]]:
    target = canonical_taxon(TARGET_TAXON)
    output = []
    for row in rows:
        name = canonical_taxon(row.get("ScientificName"))
        text = run_search_text(row).casefold()
        if name == target or "takaoense" in name or "takaoense" in text:
            output.append(dict(row))
    return output


def score_seed_run(seed: Mapping[str, str], run: Mapping[str, str]) -> tuple[int, str]:
    """Score provenance identifiers only; colour never participates in matching."""
    text = run_search_text(run)
    if token_present(seed.get("voucher", ""), text):
        return 100, "exact_voucher_in_runinfo"
    if exact_takaoense_sample_suffix(seed.get("voucher", ""), run.get("SampleName", "")):
        return 95, "exact_voucher_numeric_suffix_in_takaoense_sample_name"
    if token_present(seed.get("code", ""), text):
        return 80, "exact_sample_code_in_runinfo"
    locations = locality_tokens(seed.get("location", ""))
    matching_locations = [token for token in locations if token.casefold() in text.casefold()]
    if matching_locations:
        return 50, "explicit_locality_in_runinfo:" + "|".join(matching_locations)
    return 0, "unmatched"


def match_runs_to_seeds(
    seeds: Sequence[Mapping[str, str]],
    runs: Sequence[Mapping[str, str]],
) -> tuple[dict[str, tuple[dict[str, str], str]], list[dict[str, str]]]:
    matches: dict[str, tuple[dict[str, str], str]] = {}
    ambiguous: list[dict[str, str]] = []
    for seed in seeds:
        scored = []
        for run in runs:
            score, basis = score_seed_run(seed, run)
            if score:
                scored.append((score, basis, dict(run)))
        if not scored:
            continue
        best_score = max(item[0] for item in scored)
        best = [item for item in scored if item[0] == best_score]
        if len(best) == 1:
            _, basis, run = best[0]
            matches[seed["voucher"]] = (run, basis)
        else:
            ambiguous.append(
                {
                    "voucher": seed["voucher"],
                    "code": seed["code"],
                    "best_score": str(best_score),
                    "candidate_runs": "|".join(
                        sorted({item[2].get("Run", "") for item in best})
                    ),
                    "candidate_biosamples": "|".join(
                        sorted({item[2].get("BioSample", "") for item in best})
                    ),
                    "basis": "|".join(sorted({item[1] for item in best})),
                }
            )
    return matches, ambiguous


def attribute_is_relevant(name: str, value: str) -> bool:
    return bool(RELEVANT_PATTERN.search(f"{name} {value}"))


def direct_colour_state(relevant: Sequence[tuple[str, str]]) -> tuple[str, str, str]:
    """Return published-style label, normalized state, and review status."""
    text = " | ".join(f"{name}: {value}" for name, value in relevant)
    white = bool(WHITE_PATTERN.search(text))
    purple = bool(PURPLE_PATTERN.search(text))
    if white and not purple:
        return "W", "white", "assigned_from_explicit_ncbi_attribute"
    if purple and not white:
        return "BP", "bluish-purple", "assigned_from_explicit_ncbi_attribute"
    if white and purple:
        return "", "", "ambiguous_or_polymorphic_ncbi_attribute"
    return "", "", "no_explicit_ncbi_colour_attribute"


def flatten_attributes(
    runs: Sequence[Mapping[str, str]],
    attributes: Mapping[str, Mapping[str, str]],
) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for run in runs:
        biosample = clean(run.get("BioSample"))
        for name, value in sorted(attributes.get(biosample, {}).items()):
            output.append(
                {
                    "biosample": biosample,
                    "run": clean(run.get("Run")),
                    "experiment": clean(run.get("Experiment")),
                    "scientific_name": clean(run.get("ScientificName")),
                    "sample_name": clean(run.get("SampleName")),
                    "library_name": clean(run.get("LibraryName")),
                    "attribute_name": name,
                    "attribute_value": value,
                    "morph_relevant": (
                        "yes" if attribute_is_relevant(name, value) else "no"
                    ),
                }
            )
    return output


def build_audit_rows(
    seeds: Sequence[Mapping[str, str]],
    matches: Mapping[str, tuple[Mapping[str, str], str]],
    attributes: Mapping[str, Mapping[str, str]],
) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for seed in seeds:
        pair = matches.get(seed["voucher"])
        if pair:
            run, basis = pair
            biosample = clean(run.get("BioSample"))
            record = attributes.get(biosample, {})
        else:
            run, basis, biosample, record = {}, "unmatched", "", {}
        relevant = [
            (name, value)
            for name, value in sorted(record.items())
            if attribute_is_relevant(name, value)
        ]
        label, state, status = direct_colour_state(relevant)
        if not pair:
            status = "run_or_biosample_not_matched_to_voucher"
        binary = "W" if label == "W" else ("C" if label == "BP" else "")
        confidence = "high" if label else "unresolved"
        output.append(
            {
                **seed,
                "run": clean(run.get("Run")),
                "experiment": clean(run.get("Experiment")),
                "biosample": biosample,
                "sra_scientific_name": clean(run.get("ScientificName")),
                "sample_name": clean(run.get("SampleName")),
                "library_name": clean(run.get("LibraryName")),
                "biosample_isolate": clean(record.get("isolate")),
                "run_match_basis": basis,
                "biosample_attribute_count": str(len(record)),
                "morph_relevant_attributes": " | ".join(
                    f"{name}={value}" for name, value in relevant
                ),
                "direct_ncbi_colour_label": label,
                "flower_colour_state": state,
                "binary_colour_code": binary,
                "assignment_confidence": confidence,
                "review_status": status,
                "evidence_source": (
                    "NCBI BioSample XML and SRA runinfo for PRJNA1311153"
                ),
                "notes": (
                    "Voucher identity may use an explicit SampleName/isolate identifier. "
                    "No colour assignment from locality, elevation, herbarium, read count, "
                    "or inferred phylogenetic position."
                ),
            }
        )
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runinfo", type=Path, required=True)
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    parser.add_argument("--email", default=os.getenv("NCBI_EMAIL", ""))
    parser.add_argument("--api-key", default=os.getenv("NCBI_API_KEY"))
    parser.add_argument(
        "--offline-attributes-json",
        type=Path,
        help="Use a frozen BioSample attribute mapping instead of NCBI network calls.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    seed_rows = target_seed_rows(read_csv(args.seed))
    if len(seed_rows) != 6:
        raise SystemExit(f"Expected six takaoense seed rows, observed {len(seed_rows)}")

    runinfo = read_csv(args.runinfo)
    target_runs = candidate_target_runs(runinfo)
    matches, ambiguous = match_runs_to_seeds(seed_rows, target_runs)

    if args.offline_attributes_json:
        attributes = json.loads(
            args.offline_attributes_json.read_text(encoding="utf-8")
        )
    else:
        client = NCBIClient(ClientConfig(args.email, args.api_key))
        attributes = biosample_attributes(
            client,
            [row.get("BioSample", "") for row in target_runs],
        )

    long_rows = flatten_attributes(target_runs, attributes)
    audit_rows = build_audit_rows(seed_rows, matches, attributes)
    args.outdir.mkdir(parents=True, exist_ok=True)
    write_csv(args.outdir / "takaoense_biosample_attributes_long.csv", long_rows, LONG_FIELDS)
    write_csv(args.outdir / "takaoense_biosample_morph_audit.csv", audit_rows, AUDIT_FIELDS)
    write_csv(
        args.outdir / "takaoense_run_match_ambiguities.csv",
        ambiguous,
        ("voucher", "code", "best_score", "candidate_runs", "candidate_biosamples", "basis"),
    )

    explicit = [row for row in audit_rows if row["direct_ncbi_colour_label"]]
    relevant_long = [row for row in long_rows if row["morph_relevant"] == "yes"]
    summary = {
        "bioproject": "PRJNA1311153",
        "seed_vouchers": len(seed_rows),
        "project_runinfo_rows": len(runinfo),
        "candidate_takaoense_run_rows": len(target_runs),
        "voucher_run_matches": len(matches),
        "ambiguous_voucher_run_matches": len(ambiguous),
        "biosamples_with_attribute_records": len(attributes),
        "attribute_rows": len(long_rows),
        "morph_relevant_attribute_rows": len(relevant_long),
        "direct_sample_colour_assignments": len(explicit),
        "assigned_vouchers": [row["voucher"] for row in explicit],
        "unresolved_vouchers": [
            row["voucher"] for row in audit_rows if not row["direct_ncbi_colour_label"]
        ],
        "interpretation": (
            "The six published voucher identifiers can be linked to six public runs through "
            "explicit SampleName/isolate identifiers. A zero colour-assignment count means "
            "that official NCBI metadata do not expose sample-level W/BP labels; it does "
            "not imply that Figure 1 lacks them."
        ),
    }
    summary_path = args.outdir / "biosample_morph_audit_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"project_runinfo_rows={summary['project_runinfo_rows']}")
    print(f"candidate_takaoense_run_rows={summary['candidate_takaoense_run_rows']}")
    print(f"voucher_run_matches={summary['voucher_run_matches']}")
    print(f"biosamples_with_attribute_records={summary['biosamples_with_attribute_records']}")
    print(f"morph_relevant_attribute_rows={summary['morph_relevant_attribute_rows']}")
    print(f"direct_sample_colour_assignments={summary['direct_sample_colour_assignments']}")
    print(summary_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
