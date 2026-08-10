#!/usr/bin/env python3
"""Build the Chang 2026 Sinocirsium gene-tree and reticulation panel.

A six-tip takaoense-only tree can describe morph ordering, but it cannot provide
external coloured ancestry, a white sister comparison, or an outgroup root.  The
analysis panel therefore combines:

* six morph-labelled var. takaoense samples;
* two white var. albescens samples;
* three coloured var. australe samples;
* four coloured var. fukienense samples;
* two broad C. japonicum coloured-root-context samples;
* two C. lineare outgroups.

The expected total is 19 samples.  Public TSA/Assembly records were not recovered
by the current NCBI audit, so the reproducible source is the reconciled official
SRA run for each sample.  If a public assembly appears later, the builder records
it without changing sample identity.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Iterable, Mapping, Sequence

DEFAULT_RECONCILIATION = Path(
    "data/evidence/generated/chang2026_ncbi_reconciliation/"
    "chang2026_sample_run_reconciliation.csv"
)
DEFAULT_ASSEMBLY_AUDIT = Path(
    "data/evidence/generated/chang2026_public_transcriptome_assemblies/"
    "chang2026_public_transcriptome_assembly_audit.csv"
)
DEFAULT_NEAREST = Path(
    "analysis/chang2026_takaoense_nearest_no_regain_topologies.csv"
)
DEFAULT_ROBUSTNESS_SUMMARY = Path(
    "analysis/chang2026_takaoense_topology_robustness_summary.json"
)
DEFAULT_OUTDIR = Path(
    "data/evidence/generated/chang2026_gene_tree_panel"
)

PANEL_FIELDS = (
    "sample_id",
    "taxon",
    "code",
    "voucher",
    "morph",
    "flower_colour_state",
    "panel_role",
    "matched_run",
    "matched_experiment",
    "matched_biosample",
    "matched_spots",
    "read_count_relation",
    "run_match_status",
    "run_match_confidence",
    "public_transcriptome_status",
    "preferred_sequence_source",
    "tsa_accessions",
    "assembly_accessions",
    "de_novo_required",
    "analysis_panel",
)

HYPOTHESIS_FIELDS = (
    "hypothesis_id",
    "history_class",
    "topology_newick",
    "rooted_rf_distance_from_published",
    "minimum_changes_coloured_root",
    "optimal_histories",
    "no_regain_penalty",
    "analysis_role",
)

EXPECTED_COUNTS = {
    "cirsium japonicum": 2,
    "cirsium japonicum var. albescens": 2,
    "cirsium japonicum var. takaoense": 6,
    "cirsium japonicum var. australe": 3,
    "cirsium japonicum var. fukienense": 4,
    "cirsium lineare": 2,
}


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


def canonical_taxon(value: str) -> str:
    text = clean(value).replace("_", " ")
    text = re.sub(r"^C\.\s+", "Cirsium ", text, flags=re.I)
    return re.sub(r"\s+", " ", text).strip().casefold()


def safe_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", clean(value)).strip("_")


def panel_role(taxon: str) -> str:
    canonical = canonical_taxon(taxon)
    if canonical == "cirsium japonicum var. takaoense":
        return "focal_colour_morph"
    if canonical == "cirsium japonicum var. albescens":
        return "white_sister_control"
    if canonical in {
        "cirsium japonicum var. australe",
        "cirsium japonicum var. fukienense",
    }:
        return "coloured_flanking_introgression_control"
    if canonical == "cirsium japonicum":
        return "coloured_root_context"
    if canonical == "cirsium lineare":
        return "outgroup"
    raise ValueError(f"Unexpected panel taxon: {taxon}")


def assembly_index(rows: Sequence[Mapping[str, str]]) -> dict[str, Mapping[str, str]]:
    output: dict[str, Mapping[str, str]] = {}
    for row in rows:
        voucher = clean(row.get("voucher"))
        if not voucher:
            continue
        if voucher in output:
            raise ValueError(f"Duplicate assembly-audit voucher: {voucher}")
        output[voucher] = row
    return output


def build_panel(
    reconciliation_rows: Sequence[Mapping[str, str]],
    assembly_rows: Sequence[Mapping[str, str]],
) -> list[dict[str, str]]:
    assemblies = assembly_index(assembly_rows)
    selected = [
        row
        for row in reconciliation_rows
        if canonical_taxon(clean(row.get("taxon"))) in EXPECTED_COUNTS
    ]

    counts = Counter(canonical_taxon(clean(row.get("taxon"))) for row in selected)
    if dict(counts) != EXPECTED_COUNTS:
        raise ValueError(
            f"Unexpected taxon counts: observed={dict(counts)}, expected={EXPECTED_COUNTS}"
        )

    verified = [
        row
        for row in selected
        if clean(row.get("match_confidence")) not in {"verified", "probable"}
    ]
    if verified:
        raise ValueError(
            "Unresolved run mappings in panel: "
            + "|".join(clean(row.get("voucher")) for row in verified)
        )

    runs = [clean(row.get("matched_run")) for row in selected]
    if any(not run for run in runs):
        raise ValueError("One or more selected samples lack an official SRA run")
    duplicates = sorted(run for run, count in Counter(runs).items() if count > 1)
    if duplicates:
        raise ValueError(f"Duplicate official runs in panel: {duplicates}")

    output: list[dict[str, str]] = []
    sample_ids: set[str] = set()
    for row in selected:
        voucher = clean(row.get("voucher"))
        assembly = assemblies.get(voucher)
        if assembly is None:
            raise ValueError(f"No public-assembly audit row for voucher {voucher}")
        source = clean(assembly.get("preferred_public_source"))
        if source == "NCBI_TSA":
            preferred = clean(assembly.get("tsa_accessions"))
            de_novo = "false"
        elif source == "NCBI_Assembly":
            preferred = clean(assembly.get("assembly_accessions"))
            de_novo = "false"
        elif source == "de_novo_from_official_SRA":
            preferred = clean(row.get("matched_run"))
            de_novo = "true"
        else:
            raise ValueError(
                f"Unusable public-source decision for {voucher}: {source}"
            )

        code = clean(row.get("code"))
        sample_id = safe_id(f"{code}_{voucher}")
        if sample_id in sample_ids:
            raise ValueError(f"Duplicate normalized sample_id: {sample_id}")
        sample_ids.add(sample_id)

        output.append(
            {
                "sample_id": sample_id,
                "taxon": clean(row.get("taxon")),
                "code": code,
                "voucher": voucher,
                "morph": clean(row.get("published_figure_label")),
                "flower_colour_state": clean(row.get("flower_colour_state")),
                "panel_role": panel_role(clean(row.get("taxon"))),
                "matched_run": clean(row.get("matched_run")),
                "matched_experiment": clean(row.get("matched_experiment")),
                "matched_biosample": clean(row.get("matched_biosample")),
                "matched_spots": clean(row.get("matched_spots")),
                "read_count_relation": clean(row.get("read_count_relation")),
                "run_match_status": clean(row.get("match_status")),
                "run_match_confidence": clean(row.get("match_confidence")),
                "public_transcriptome_status": clean(
                    assembly.get("public_transcriptome_status")
                ),
                "preferred_sequence_source": preferred,
                "tsa_accessions": clean(assembly.get("tsa_accessions")),
                "assembly_accessions": clean(
                    assembly.get("assembly_accessions")
                ),
                "de_novo_required": de_novo,
                "analysis_panel": "sinocirsium17_plus_lineare2",
            }
        )

    role_order = {
        "focal_colour_morph": 0,
        "white_sister_control": 1,
        "coloured_flanking_introgression_control": 2,
        "coloured_root_context": 3,
        "outgroup": 4,
    }
    return sorted(
        output,
        key=lambda row: (
            role_order[row["panel_role"]],
            canonical_taxon(row["taxon"]),
            row["sample_id"],
        ),
    )


def build_hypotheses(
    nearest_rows: Sequence[Mapping[str, str]],
    robustness_summary: Mapping[str, object],
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = [
        {
            "hypothesis_id": "H_REG_PUBLISHED",
            "history_class": "topology_supported_candidate_regain",
            "topology_newick": clean(
                robustness_summary.get("published_topology_newick")
            ),
            "rooted_rf_distance_from_published": 0,
            "minimum_changes_coloured_root": robustness_summary.get(
                "published_minimum_changes", ""
            ),
            "optimal_histories": robustness_summary.get(
                "published_optimal_histories", ""
            ),
            "no_regain_penalty": robustness_summary.get(
                "published_no_regain_penalty", ""
            ),
            "analysis_role": (
                "Primary published six-tip morph topology; compare per-gene and quartet support against all nearest loss-only alternatives."
            ),
        }
    ]
    for index, row in enumerate(nearest_rows, start=1):
        output.append(
            {
                "hypothesis_id": f"H_LOSS_ONLY_RF4_{index:02d}",
                "history_class": "nearest_loss_only_topology",
                "topology_newick": clean(row.get("sample_topology_newick")),
                "rooted_rf_distance_from_published": clean(
                    row.get("rooted_rf_distance_from_published")
                ),
                "minimum_changes_coloured_root": clean(
                    row.get("sinocirsium_coloured_root_minimum_changes")
                ),
                "optimal_histories": clean(
                    row.get("sinocirsium_coloured_root_optimal_histories")
                ),
                "no_regain_penalty": clean(row.get("no_regain_penalty")),
                "analysis_role": (
                    "Nearest rooted resolution in which a no-regain history ties the parsimony optimum."
                ),
            }
        )
    if len(output) != 8:
        raise ValueError(
            f"Expected one published plus seven nearest alternatives, observed {len(output)}"
        )
    return output


def build_summary(
    panel: Sequence[Mapping[str, str]],
    hypotheses: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    roles = Counter(row["panel_role"] for row in panel)
    taxa = Counter(canonical_taxon(row["taxon"]) for row in panel)
    return {
        "panel_name": "Chang 2026 Sinocirsium17 + Cirsium lineare2",
        "sample_count": len(panel),
        "taxon_counts": dict(sorted(taxa.items())),
        "panel_role_counts": dict(sorted(roles.items())),
        "takaoense_sample_count": sum(
            canonical_taxon(row["taxon"])
            == "cirsium japonicum var. takaoense"
            for row in panel
        ),
        "white_takaoense_count": sum(
            canonical_taxon(row["taxon"])
            == "cirsium japonicum var. takaoense"
            and row["morph"] == "W"
            for row in panel
        ),
        "bluish_purple_takaoense_count": sum(
            canonical_taxon(row["taxon"])
            == "cirsium japonicum var. takaoense"
            and row["morph"] == "BP"
            for row in panel
        ),
        "de_novo_required_count": sum(
            row["de_novo_required"] == "true" for row in panel
        ),
        "unique_official_run_count": len(
            {row["matched_run"] for row in panel}
        ),
        "hypothesis_count": len(hypotheses),
        "primary_regain_hypothesis_count": sum(
            row["history_class"] == "topology_supported_candidate_regain"
            for row in hypotheses
        ),
        "nearest_loss_only_hypothesis_count": sum(
            row["history_class"] == "nearest_loss_only_topology"
            for row in hypotheses
        ),
        "analysis_sequence": [
            "de novo transcriptome assembly from reconciled official SRA runs",
            "protein prediction and orthogroup inference across 19 samples",
            "per-orthogroup alignments and gene trees",
            "root on Cirsium lineare and prune to six takaoense tips",
            "score published regain topology versus seven nearest loss-only alternatives",
            "quantify gene/quartet concordance and topology-driving loci",
            "test australe/fukienense affinity of coloured takaoense samples",
        ],
        "claim_limit": (
            "Gene-tree support can test topology discordance and reticulation alternatives, but a true molecular regain additionally requires linked pigment, expression and causal-variant evidence."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reconciliation", type=Path, default=DEFAULT_RECONCILIATION
    )
    parser.add_argument(
        "--assembly-audit", type=Path, default=DEFAULT_ASSEMBLY_AUDIT
    )
    parser.add_argument("--nearest", type=Path, default=DEFAULT_NEAREST)
    parser.add_argument(
        "--robustness-summary", type=Path, default=DEFAULT_ROBUSTNESS_SUMMARY
    )
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    reconciliation = read_csv(args.reconciliation)
    assemblies = read_csv(args.assembly_audit)
    nearest = read_csv(args.nearest)
    robustness = json.loads(
        args.robustness_summary.read_text(encoding="utf-8")
    )

    panel = build_panel(reconciliation, assemblies)
    hypotheses = build_hypotheses(nearest, robustness)
    summary = build_summary(panel, hypotheses)

    args.outdir.mkdir(parents=True, exist_ok=True)
    write_csv(
        args.outdir / "chang2026_sinocirsium_gene_tree_panel.csv",
        panel,
        PANEL_FIELDS,
    )
    pilot = [
        row
        for row in panel
        if canonical_taxon(row["taxon"])
        == "cirsium japonicum var. takaoense"
    ]
    write_csv(
        args.outdir / "chang2026_takaoense6_assembly_pilot.csv",
        pilot,
        PANEL_FIELDS,
    )
    write_csv(
        args.outdir / "chang2026_takaoense_gene_tree_hypotheses.csv",
        hypotheses,
        HYPOTHESIS_FIELDS,
    )
    (args.outdir / "chang2026_gene_tree_panel_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"sample_count={summary['sample_count']}")
    print(f"takaoense_sample_count={summary['takaoense_sample_count']}")
    print(f"de_novo_required_count={summary['de_novo_required_count']}")
    print(f"hypothesis_count={summary['hypothesis_count']}")
    print(args.outdir / "chang2026_sinocirsium_gene_tree_panel.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
