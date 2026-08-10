#!/usr/bin/env python3
"""Build a deterministic East Asian raw-read reconstruction pilot for Moreyra 2025.

This is a *preflight and manifest builder*, not a claim that the full published
analysis has been reproduced.  It selects 12 public PRJNA957074 biological
samples spanning Japan, China, the Russian Far East, Inner Northeast Asia and
Mongolia.  The panel exercises ordinary exact-name samples and one explicit
name-reconciliation case (``C. coryletorum`` / submitted ``C. vlassovianum``).

The output supplies stable sample/run identifiers and SRA download commands for
an HPC or local HybPiper smoke test.  Raw reads are intentionally not downloaded
in pull-request CI.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping, Sequence

DEFAULT_INPUT = Path(
    "data/evidence/moreyra2025_east_ne_asia_sample_audit_2026-08-10.csv"
)
DEFAULT_OUTDIR = Path("data/evidence/generated/moreyra_reanalysis_pilot")

REQUIRED_FIELDS = {
    "tree_code",
    "published_species",
    "biosample",
    "voucher_and_herbarium",
    "sra_scientific_name",
    "library_name",
    "experiment",
    "run",
    "region_class",
    "scope_class",
    "sra_link_status",
    "tree_code_vs_sra_name",
    "name_reconciliation_priority",
}

PILOT_TARGETS = (
    {
        "tree_code": "Cirsium domonii",
        "biosample": "SAMN34240283",
        "role": "Japanese_rapid_radiation_anchor",
        "rationale": "verified wild Honshu focal tip",
        "allow_high_name_conflict": False,
    },
    {
        "tree_code": "Cirsium dipsacolepis",
        "biosample": "SAMN44017836",
        "role": "separate_Japanese_invasion_anchor",
        "rationale": "verified wild Shikoku tip outside the main Japanese radiation context",
        "allow_high_name_conflict": False,
    },
    {
        "tree_code": "Cirsium lineare",
        "biosample": "SAMN44017876",
        "role": "cross_study_coloured_anchor",
        "rationale": "repeatedly sampled modern nuclear anchor in Moreyra and Chang datasets",
        "allow_high_name_conflict": False,
    },
    {
        "tree_code": "Cirsium yezoense",
        "biosample": "SAMN44017952",
        "role": "Japanese_coloured_bridge_control",
        "rationale": "wild Honshu control relevant to the Japan-Zhejiang bridge",
        "allow_high_name_conflict": False,
    },
    {
        "tree_code": "Cirsium argyracanthum",
        "biosample": "SAMN44017818",
        "role": "China_Tibet_anchor",
        "rationale": "clean Chinese target-capture sample spanning a distant East Asian lineage",
        "allow_high_name_conflict": False,
    },
    {
        "tree_code": "Cirsium fanjingshanense",
        "biosample": "SAMN34240294",
        "role": "China_Guizhou_anchor",
        "rationale": "clean southwestern Chinese sample for cross-region recovery diagnostics",
        "allow_high_name_conflict": False,
    },
    {
        "tree_code": "Cirsium fargesii",
        "biosample": "SAMN44017847",
        "role": "China_Hubei_anchor",
        "rationale": "clean central Chinese sample for geographic and lineage breadth",
        "allow_high_name_conflict": False,
    },
    {
        "tree_code": "Cirsium kamtschaticum",
        "biosample": "SAMN44017865",
        "role": "Russian_Far_East_northern_bridge",
        "rationale": "Kamchatka-Chukotka bridge lineage with exact submitted name",
        "allow_high_name_conflict": False,
    },
    {
        "tree_code": "Cirsium coryletorum",
        "biosample": "SAMN34240275",
        "role": "Russian_Far_East_name_reconciliation_test",
        "rationale": (
            "Sikhote-Alin sample published as C. coryletorum and submitted as "
            "C. vlassovianum; retained deliberately to test name-safe joins"
        ),
        "allow_high_name_conflict": True,
    },
    {
        "tree_code": "Cirsium pendulum",
        "biosample": "SAMN34240327",
        "role": "Trans_Baikal_focal_bridge",
        "rationale": "continental nuclear anchor for the Japanese white-purple population system",
        "allow_high_name_conflict": False,
    },
    {
        "tree_code": "Cirsium serratuloides",
        "biosample": "SAMN34240336",
        "role": "Inner_NE_Asia_bridge",
        "rationale": "Buryatia/Inner Northeast Asia bridge with exact submitted name",
        "allow_high_name_conflict": False,
    },
    {
        "tree_code": "Cirsium vlassovianum",
        "biosample": "SAMN34240350",
        "role": "Mongolia_focal_bridge",
        "rationale": "Mongolian counterpart to the Sikhote-Alin name-reconciliation sample",
        "allow_high_name_conflict": False,
    },
)

OUTPUT_FIELDS = (
    "pilot_order",
    "sample_id",
    "pilot_role",
    "tree_code",
    "published_species",
    "sra_scientific_name",
    "library_name",
    "biosample",
    "experiments",
    "runs",
    "run_count",
    "region_class",
    "scope_class",
    "tree_code_vs_sra_name",
    "name_reconciliation_priority",
    "name_reconciliation_required",
    "voucher_and_herbarium",
    "rationale",
    "public_locus_sets",
)


def clean(value: object) -> str:
    return str(value or "").strip()


def slug(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9]+", "_", clean(value)).strip("_")
    return value or "sample"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = [
            {key: clean(value) for key, value in row.items()}
            for row in reader
            if any(clean(value) for value in row.values())
        ]
    if not rows:
        raise ValueError(f"{path}: no rows")
    missing = REQUIRED_FIELDS - set(rows[0])
    if missing:
        raise ValueError(f"{path}: missing columns {sorted(missing)}")
    return rows


def unique_join(values: Iterable[str]) -> str:
    return "|".join(sorted({clean(value) for value in values if clean(value)}))


def select_target(
    rows: Sequence[Mapping[str, str]], target: Mapping[str, object], order: int
) -> dict[str, str]:
    tree_code = str(target["tree_code"])
    biosample = str(target["biosample"])
    matches = [
        row
        for row in rows
        if row["tree_code"] == tree_code and row["biosample"] == biosample
    ]
    if not matches:
        raise ValueError(f"Missing pilot target {tree_code} / {biosample}")
    if any(row["sra_link_status"] != "linked_runinfo" for row in matches):
        raise ValueError(f"Pilot target lacks linked public runinfo: {tree_code}")
    if any(not row["run"] for row in matches):
        raise ValueError(f"Pilot target lacks an SRA run: {tree_code}")
    if any(
        row["scope_class"] not in {"core_east_asia", "northeast_asia_bridge"}
        for row in matches
    ):
        raise ValueError(f"Pilot target falls outside the intended geographic scope: {tree_code}")
    high_conflict = any(
        row["name_reconciliation_priority"] == "high" for row in matches
    )
    if high_conflict and not bool(target["allow_high_name_conflict"]):
        raise ValueError(f"Unexpected high-priority name conflict: {tree_code}")

    first = sorted(matches, key=lambda row: (row["run"], row["experiment"]))[0]
    relations = unique_join(row["tree_code_vs_sra_name"] for row in matches)
    priorities = unique_join(row["name_reconciliation_priority"] for row in matches)
    runs = unique_join(row["run"] for row in matches)
    experiments = unique_join(row["experiment"] for row in matches)
    return {
        "pilot_order": str(order),
        "sample_id": f"MRY_EA_{order:02d}_{slug(tree_code)}",
        "pilot_role": str(target["role"]),
        "tree_code": tree_code,
        "published_species": unique_join(row["published_species"] for row in matches),
        "sra_scientific_name": unique_join(
            row["sra_scientific_name"] for row in matches
        ),
        "library_name": unique_join(row["library_name"] for row in matches),
        "biosample": biosample,
        "experiments": experiments,
        "runs": runs,
        "run_count": str(len(runs.split("|"))),
        "region_class": unique_join(row["region_class"] for row in matches),
        "scope_class": unique_join(row["scope_class"] for row in matches),
        "tree_code_vs_sra_name": relations,
        "name_reconciliation_priority": priorities,
        "name_reconciliation_required": str(
            relations != "exact" or priorities == "high"
        ).lower(),
        "voucher_and_herbarium": unique_join(
            row["voucher_and_herbarium"] for row in matches
        ),
        "rationale": str(target["rationale"]),
        "public_locus_sets": (
            "public_1061|reproducible_531|conservative_241|paralog_homeolog_aware"
        ),
    }


def build_panel(rows: Sequence[Mapping[str, str]]) -> list[dict[str, str]]:
    panel = [
        select_target(rows, target, order)
        for order, target in enumerate(PILOT_TARGETS, start=1)
    ]
    sample_ids = [row["sample_id"] for row in panel]
    biosamples = [row["biosample"] for row in panel]
    runs = [run for row in panel for run in row["runs"].split("|")]
    if len(sample_ids) != len(set(sample_ids)):
        raise ValueError("Duplicate pilot sample IDs")
    if len(biosamples) != len(set(biosamples)):
        raise ValueError("Duplicate pilot BioSamples")
    if len(runs) != len(set(runs)):
        raise ValueError("One SRA run is assigned to multiple pilot samples")
    return panel


def render_download_script(panel: Sequence[Mapping[str, str]]) -> str:
    run_lines = [run for row in panel for run in row["runs"].split("|")]
    quoted_runs = "\n".join(run_lines)
    return f"""#!/usr/bin/env bash
set -euo pipefail

# Generated by analysis/build_moreyra_reanalysis_pilot.py.
# This script downloads public reads only; it does not reproduce the published
# manual orthology decisions or final 350-locus matrix.

OUTDIR="${{OUTDIR:-moreyra_east_asia_pilot_reads}}"
THREADS="${{THREADS:-8}}"
mkdir -p "$OUTDIR/sra" "$OUTDIR/fastq" "$OUTDIR/tmp"

for tool in prefetch fasterq-dump; do
  command -v "$tool" >/dev/null 2>&1 || {{
    echo "Missing required SRA Toolkit command: $tool" >&2
    exit 2
  }}
done

cat > "$OUTDIR/runs.txt" <<'RUNS'
{quoted_runs}
RUNS

while IFS= read -r run; do
  [[ -n "$run" ]] || continue
  prefetch "$run" --output-directory "$OUTDIR/sra"
  fasterq-dump "$OUTDIR/sra/$run/$run.sra" \\
    --outdir "$OUTDIR/fastq" \\
    --temp "$OUTDIR/tmp/$run" \\
    --threads "$THREADS" \\
    --split-files
  if command -v pigz >/dev/null 2>&1; then
    pigz -p "$THREADS" "$OUTDIR/fastq/${{run}}"*.fastq
  else
    gzip "$OUTDIR/fastq/${{run}}"*.fastq
  fi
done < "$OUTDIR/runs.txt"
"""


def write_outputs(outdir: Path, panel: Sequence[Mapping[str, str]]) -> dict[str, object]:
    outdir.mkdir(parents=True, exist_ok=True)
    sample_path = outdir / "moreyra_east_asia_12_sample_pilot.csv"
    with sample_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(OUTPUT_FIELDS))
        writer.writeheader()
        writer.writerows(panel)

    runs = [run for row in panel for run in row["runs"].split("|")]
    (outdir / "moreyra_east_asia_12_sample_runs.txt").write_text(
        "".join(f"{run}\n" for run in runs), encoding="utf-8"
    )
    script_path = outdir / "download_public_reads.sh"
    script_path.write_text(render_download_script(panel), encoding="utf-8")
    script_path.chmod(0o755)

    region_counts = Counter(row["region_class"] for row in panel)
    summary = {
        "pilot_name": "Moreyra_2025_East_Asia_12_sample_raw_read_smoke_test",
        "bioproject": "PRJNA957074",
        "biological_samples": len(panel),
        "unique_runs": len(runs),
        "region_counts": dict(sorted(region_counts.items())),
        "samples_requiring_name_reconciliation": [
            row["sample_id"]
            for row in panel
            if row["name_reconciliation_required"] == "true"
        ],
        "locus_sets": {
            "public_universe": 1061,
            "reproducible_pre_manual_candidates": 531,
            "conservative_no_warning_high_occupancy": 241,
            "manual_review_high_occupancy": 290,
        },
        "raw_reads_downloaded_in_ci": False,
        "full_published_analysis_reproduced": False,
        "next_execution_environment": "local workstation or HPC with SRA Toolkit and HybPiper",
    }
    (outdir / "pilot_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = read_rows(args.input)
    panel = build_panel(rows)
    summary = write_outputs(args.outdir, panel)
    print(f"biological_samples={summary['biological_samples']}")
    print(f"unique_runs={summary['unique_runs']}")
    for region, count in summary["region_counts"].items():
        print(f"region_{region}={count}")
    print(
        "samples_requiring_name_reconciliation="
        + str(len(summary["samples_requiring_name_reconciliation"]))
    )
    print(args.outdir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
