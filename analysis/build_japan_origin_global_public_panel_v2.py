#!/usr/bin/env python3
"""Build a deduplicated all-public nuclear panel for Japanese Cirsium origins.

This v2 builder corrects a v1 inventory error: eight Taiwan RNA-seq BioSamples/SRRs
were reused in both Chang 2025 and Chang 2026 and must be represented by one
biological tip each, not duplicated tree tips. Source provenance is merged rather
than discarded.

The primary inventory is:
- 256 unique Moreyra 2025 Cirsium BioSamples / 257 SRRs;
- 38 unique Chang RNA-seq BioSamples / 38 SRRs after cross-paper collapse;
- 294 unique biological tips / 295 unique public SRRs total.

Japan-38 paper membership is attached as provenance/sensitivity metadata. It is
not used as a tree-acceptance constraint.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping, Sequence

DEFAULT_CONTRACT = Path("data/evidence/japan_origin_global_public_panel_contract_v2.json")
DEFAULT_CH25 = Path("data/evidence/chang2025_public_run_manifest_v1.csv")
DEFAULT_CH26 = Path("data/evidence/chang2026_public_run_manifest_v1.csv")
DEFAULT_J38 = Path("data/evidence/moreyra2025_japan_38_membership_audit_2026-08-10.csv")
DEFAULT_OUTDIR = Path("results/japan_origin_global_public_panel_v2")

FIELDS = (
    "panel_id", "source_studies", "bioprojects", "assay", "source_taxon_label",
    "analysis_taxon_label", "voucher", "biosample", "run_accessions", "run_count",
    "region", "location", "name_review_required", "shared_cross_paper_sample",
    "source_record_count", "japan38_member_ids", "japan38_membership_confidence",
    "common_locus_space", "claim_boundary",
)


def clean(x: object) -> str:
    return str(x or "").strip()


def slug(x: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", clean(x)).strip("_") or "sample"


def joinvals(vals: Iterable[str]) -> str:
    return "|".join(sorted({clean(v) for v in vals if clean(v)}))


def norm_chang_taxon(x: str) -> str:
    x = clean(x)
    return "Cirsium " + x[3:] if x.startswith("C. ") else x


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = [
            {k: clean(v) for k, v in row.items()}
            for row in csv.DictReader(handle)
            if any(clean(v) for v in row.values())
        ]
    if not rows:
        raise ValueError(f"{path}: no rows")
    return rows


def load_contract(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("contract_version") != "japan_origin_global_public_panel_v2":
        raise ValueError("unexpected contract version")
    return data


def japan38_index(rows: Sequence[Mapping[str, str]]) -> dict[str, list[Mapping[str, str]]]:
    required = {
        "paper_japan_member_id", "paper_taxon_concept", "biosamples",
        "paper_japan_membership_confidence",
    }
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"Japan-38 audit missing {sorted(missing)}")
    by_biosample: dict[str, list[Mapping[str, str]]] = defaultdict(list)
    for row in rows:
        for biosample in row["biosamples"].split("|"):
            biosample = clean(biosample)
            if biosample:
                by_biosample[biosample].append(row)
    return by_biosample


def build_moreyra(
    rows: Sequence[Mapping[str, str]],
    j38: Mapping[str, Sequence[Mapping[str, str]]],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    required = {
        "tree_code", "biosample", "run", "experiment", "voucher_and_herbarium",
        "region_class", "geographic_location", "sra_link_status", "scope_class",
        "tree_code_vs_sra_name", "name_reconciliation_priority",
    }
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"Moreyra reconciliation missing {sorted(missing)}")

    cirsium = [
        row for row in rows
        if row["tree_code"].startswith("Cirsium") and row["sra_link_status"] == "linked_runinfo"
    ]
    excluded = [row for row in cirsium if row["scope_class"] == "source_conflict_target_vs_outside"]
    clean_rows = [row for row in cirsium if row["scope_class"] != "source_conflict_target_vs_outside"]

    by_biosample: dict[str, list[Mapping[str, str]]] = defaultdict(list)
    for row in clean_rows:
        if not row["biosample"]:
            raise ValueError("linked Moreyra Cirsium row lacks BioSample")
        by_biosample[row["biosample"]].append(row)

    out: list[dict[str, str]] = []
    for biosample in sorted(by_biosample):
        group = by_biosample[biosample]
        taxa = sorted({row["tree_code"] for row in group})
        if len(taxa) != 1:
            raise ValueError(f"Moreyra BioSample {biosample} retains multiple source labels: {taxa}")
        runs = sorted({row["run"] for row in group if row["run"]})
        relations = {row["tree_code_vs_sra_name"] for row in group if row["tree_code_vs_sra_name"]}
        high_review = any(row["name_reconciliation_priority"] == "high" for row in group)
        memberships = list(j38.get(biosample, []))
        out.append({
            "panel_id": f"MRY_{slug(biosample)}",
            "source_studies": "Moreyra2025",
            "bioprojects": "PRJNA957074",
            "assay": "Compositae1061_target_capture",
            "source_taxon_label": taxa[0],
            "analysis_taxon_label": taxa[0],
            "voucher": joinvals(row["voucher_and_herbarium"] for row in group),
            "biosample": biosample,
            "run_accessions": "|".join(runs),
            "run_count": str(len(runs)),
            "region": joinvals(row["region_class"] for row in group),
            "location": joinvals(row["geographic_location"] for row in group),
            "name_review_required": str(high_review or relations != {"exact"}).lower(),
            "shared_cross_paper_sample": "false",
            "source_record_count": str(len(group)),
            "japan38_member_ids": joinvals(row["paper_japan_member_id"] for row in memberships),
            "japan38_membership_confidence": joinvals(
                row["paper_japan_membership_confidence"] for row in memberships
            ),
            "common_locus_space": "Compositae1061_direct",
            "claim_boundary": (
                "Moreyra source labels and Japan-38 paper membership are provenance only; "
                "placement and Japanese monophyly are not assumed."
            ),
        })
    return out, excluded


def chang_records(
    chang25: Sequence[Mapping[str, str]],
    chang26: Sequence[Mapping[str, str]],
) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    required25 = {
        "taxon", "voucher", "biosample", "run", "library_layout",
        "geographic_location", "match_status",
    }
    missing = required25 - set(chang25[0])
    if missing:
        raise ValueError(f"Chang2025 manifest missing {sorted(missing)}")
    for row in chang25:
        if row["library_layout"] != "PAIRED" or row["match_status"] != "verified":
            raise ValueError(f"unverified Chang2025 row {row['voucher']}")
        out.append({
            "study": "Chang2025",
            "bioproject": "PRJNA1158676",
            "taxon": norm_chang_taxon(row["taxon"]),
            "voucher": row["voucher"],
            "biosample": row["biosample"],
            "run": row["run"],
            "location": row["geographic_location"],
            "name_review": "false",
        })

    required26 = {
        "taxon", "voucher", "matched_biosample", "matched_run",
        "matched_library_layout", "match_confidence", "location",
        "matched_scientific_name", "match_evidence",
    }
    missing = required26 - set(chang26[0])
    if missing:
        raise ValueError(f"Chang2026 manifest missing {sorted(missing)}")
    for row in chang26:
        if row["matched_library_layout"] != "PAIRED" or row["match_confidence"] != "verified":
            raise ValueError(f"unverified Chang2026 row {row['voucher']}")
        taxon = norm_chang_taxon(row["taxon"])
        name_review = "exact_taxon" not in row["match_evidence"] and taxon != row["matched_scientific_name"]
        out.append({
            "study": "Chang2026",
            "bioproject": "PRJNA1311153_or_reused_public_run",
            "taxon": taxon,
            "voucher": row["voucher"],
            "biosample": row["matched_biosample"],
            "run": row["matched_run"],
            "location": row["location"],
            "name_review": str(name_review).lower(),
        })
    return out


def build_chang(
    chang25: Sequence[Mapping[str, str]],
    chang26: Sequence[Mapping[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    records = chang_records(chang25, chang26)
    by_biosample: dict[str, list[Mapping[str, str]]] = defaultdict(list)
    for row in records:
        if not row["biosample"] or not row["run"]:
            raise ValueError("Chang record lacks BioSample or run")
        by_biosample[row["biosample"]].append(row)

    out: list[dict[str, str]] = []
    shared: list[dict[str, str]] = []
    for biosample in sorted(by_biosample):
        group = by_biosample[biosample]
        runs = {row["run"] for row in group}
        taxa = {row["taxon"] for row in group}
        vouchers = {row["voucher"] for row in group}
        if len(runs) != 1:
            raise ValueError(f"Chang BioSample {biosample} maps to multiple runs: {sorted(runs)}")
        if len(taxa) != 1 or len(vouchers) != 1:
            raise ValueError(
                f"Chang reused BioSample {biosample} disagrees in taxon/voucher: "
                f"{sorted(taxa)} / {sorted(vouchers)}"
            )
        studies = {row["study"] for row in group}
        shared_flag = studies == {"Chang2025", "Chang2026"}
        if len(group) > 1 and not shared_flag:
            raise ValueError(f"unexpected same-paper duplicate for {biosample}")
        run = next(iter(runs))
        taxon = next(iter(taxa))
        voucher = next(iter(vouchers))
        if shared_flag:
            shared.append({
                "biosample": biosample,
                "run": run,
                "taxon": taxon,
                "voucher": voucher,
                "source_studies": "Chang2025|Chang2026",
            })
        locations = joinvals(row["location"] for row in group)
        region = "Japan" if any(row["location"].casefold().startswith("japan") for row in group) else "Taiwan"
        out.append({
            "panel_id": f"CH_{slug(biosample)}",
            "source_studies": joinvals(studies),
            "bioprojects": joinvals(row["bioproject"] for row in group),
            "assay": "leaf_RNAseq_transcriptome",
            "source_taxon_label": taxon,
            "analysis_taxon_label": taxon,
            "voucher": voucher,
            "biosample": biosample,
            "run_accessions": run,
            "run_count": "1",
            "region": region,
            "location": locations,
            "name_review_required": str(any(row["name_review"] == "true" for row in group)).lower(),
            "shared_cross_paper_sample": str(shared_flag).lower(),
            "source_record_count": str(len(group)),
            "japan38_member_ids": "",
            "japan38_membership_confidence": "",
            "common_locus_space": "Compositae1061_homolog_projection_required",
            "claim_boundary": (
                "A reused public RNA-seq BioSample/SRR is represented by one biological tip; "
                "source-paper provenance is merged, not duplicated."
            ),
        })
    return out, shared


def validate(
    panel: Sequence[Mapping[str, str]],
    excluded: Sequence[Mapping[str, str]],
    shared: Sequence[Mapping[str, str]],
    contract: Mapping,
    japan38_rows: Sequence[Mapping[str, str]],
) -> dict[str, object]:
    expected = contract["expected_deduplicated_inventory"]
    runs: list[str] = []
    for row in panel:
        row_runs = [item for item in row["run_accessions"].split("|") if item]
        if len(row_runs) != int(row["run_count"]):
            raise ValueError(f"run_count mismatch {row['panel_id']}")
        runs.extend(row_runs)

    if len(panel) != expected["biological_samples"]:
        raise ValueError(f"biological sample count {len(panel)} != {expected['biological_samples']}")
    if len(runs) != expected["public_run_accessions"] or len(set(runs)) != len(runs):
        raise ValueError("public run inventory is not the expected unique 295 SRRs")
    if len({row["biosample"] for row in panel}) != len(panel):
        raise ValueError("BioSample duplicated across final biological tips")

    labels = len({row["analysis_taxon_label"] for row in panel})
    if labels != expected["source_preserving_analysis_taxon_labels"]:
        raise ValueError(f"label count {labels} != {expected['source_preserving_analysis_taxon_labels']}")
    moreyra_n = sum(row["source_studies"] == "Moreyra2025" for row in panel)
    chang_n = sum("Chang" in row["source_studies"] for row in panel)
    if moreyra_n != expected["Moreyra2025_unique_samples"] or chang_n != expected["Chang_unique_samples"]:
        raise ValueError("source unique-sample counts drift")
    if len(shared) != expected["Chang_cross_paper_shared_samples"]:
        raise ValueError(
            f"expected {expected['Chang_cross_paper_shared_samples']} shared Chang samples, found {len(shared)}"
        )

    member_ids = {
        member_id
        for row in panel
        for member_id in row["japan38_member_ids"].split("|")
        if member_id
    }
    expected_member_ids = {row["paper_japan_member_id"] for row in japan38_rows}
    if member_ids != expected_member_ids:
        raise ValueError(
            f"Japan-38 membership coverage mismatch missing={sorted(expected_member_ids-member_ids)} "
            f"extra={sorted(member_ids-expected_member_ids)}"
        )
    if len(expected_member_ids) != 38:
        raise ValueError("Japan-38 audit no longer has 38 paper concepts")
    if len(excluded) != 1 or excluded[0]["scope_class"] != "source_conflict_target_vs_outside":
        raise ValueError("expected exactly one preserved Moreyra source-conflict exclusion row")

    by_taxon = Counter(row["analysis_taxon_label"] for row in panel)
    for taxon, minimum in {
        "Cirsium brevicaule": 3,
        "Cirsium irumtiense": 3,
        "Cirsium dipsacolepis": 1,
    }.items():
        if by_taxon[taxon] < minimum:
            raise ValueError(f"critical taxon underrepresented: {taxon}")

    return {
        "contract_version": "japan_origin_global_public_panel_v2",
        "biological_samples": len(panel),
        "public_run_accessions": len(runs),
        "unique_biosamples": len({row["biosample"] for row in panel}),
        "unique_public_run_accessions": len(set(runs)),
        "unique_source_preserving_analysis_taxon_labels": labels,
        "Moreyra2025_unique_samples": moreyra_n,
        "Chang_unique_samples": chang_n,
        "Chang_cross_paper_shared_samples": len(shared),
        "Chang_source_record_counts": dict(sorted(Counter(
            row["source_studies"] for row in panel if "Chang" in row["source_studies"]
        ).items())),
        "japan38_paper_concepts_mapped": len(member_ids),
        "japan38_conflicted_member_ids": sorted({
            member_id
            for row in panel
            if "low_until_manual_resolution" in row["japan38_membership_confidence"]
            for member_id in row["japan38_member_ids"].split("|")
            if member_id
        }),
        "region_counts": dict(sorted(Counter(row["region"] for row in panel).items())),
        "global_common_locus_tree_executed": False,
        "new_china_sampling_freeze_allowed": False,
        "v1_302_tip_inventory_superseded": True,
        "deduplication_reason": (
            "Eight Chang 2025 BioSample/SRRs are reused in Chang 2026 and are represented "
            "once each to avoid pseudoreplication."
        ),
        "next_gate": (
            "Run the 294-tip/295-SRR common-Compositae1061 recovery and global nuclear placement "
            "before any branch-specific mainland sampling decision."
        ),
    }


def write_csv(path: Path, rows: Sequence[Mapping[str, str]], fields: Sequence[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields or rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--moreyra-reconciliation", type=Path, required=True)
    parser.add_argument("--chang2025", type=Path, default=DEFAULT_CH25)
    parser.add_argument("--chang2026", type=Path, default=DEFAULT_CH26)
    parser.add_argument("--japan38", type=Path, default=DEFAULT_J38)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    args = parser.parse_args()

    contract = load_contract(args.contract)
    moreyra_rows = read_csv(args.moreyra_reconciliation)
    chang25_rows = read_csv(args.chang2025)
    chang26_rows = read_csv(args.chang2026)
    japan38_rows = read_csv(args.japan38)
    j38 = japan38_index(japan38_rows)

    moreyra, excluded = build_moreyra(moreyra_rows, j38)
    chang, shared = build_chang(chang25_rows, chang26_rows)
    panel = moreyra + chang
    summary = validate(panel, excluded, shared, contract, japan38_rows)

    write_csv(args.outdir / "japan_origin_global_public_panel_v2.csv", panel, FIELDS)
    write_csv(
        args.outdir / "chang_cross_paper_reused_samples_v2.csv",
        shared,
        ["biosample", "run", "taxon", "voucher", "source_studies"],
    )
    (args.outdir / "moreyra_source_conflict_exclusion_v2.json").write_text(
        json.dumps(excluded, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (args.outdir / "japan_origin_global_public_panel_summary_v2.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
