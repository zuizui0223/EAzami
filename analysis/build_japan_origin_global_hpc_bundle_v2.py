#!/usr/bin/env python3
"""Build the deduplicated 294-tip/295-SRR public nuclear-tree HPC bundle.

The v2 bundle corrects the cross-paper read duplication in the old 302-tip
inventory, keeps every unique biological individual for the primary placement,
and produces both a concatenated IQ-TREE topology and an ASTRAL-III coalescent
sensitivity from the same admitted Compositae1061 loci.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "jog_legacy", ROOT / "analysis/build_japan_origin_global_hpc_bundle.py"
)
assert SPEC and SPEC.loader
legacy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(legacy)

EXPECTED_SAMPLES = 294
EXPECTED_RUNS = 295


def clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def joinvals(values: list[str]) -> str:
    return "|".join(sorted({clean(value) for value in values if clean(value)}))


def read_panel(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = [
            {key: clean(value) for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]
    required = {
        "panel_id",
        "source_studies",
        "assay",
        "analysis_taxon_label",
        "voucher",
        "biosample",
        "run_accessions",
        "run_count",
        "japan38_member_ids",
        "shared_cross_paper_sample",
        "region",
        "location",
        "name_review_required",
    }
    if not rows or not required <= set(rows[0]):
        raise ValueError(f"v2 panel requires columns {sorted(required)}")
    if len(rows) != EXPECTED_SAMPLES or len({row["biosample"] for row in rows}) != EXPECTED_SAMPLES:
        raise ValueError(f"expected {EXPECTED_SAMPLES} unique biological samples")

    all_runs: list[str] = []
    for row in rows:
        runs = [item for item in row["run_accessions"].split("|") if item]
        if len(runs) != int(row["run_count"]) or any(not item.startswith("SRR") for item in runs):
            raise ValueError(f"invalid run list for {row['panel_id']}")
        all_runs.extend(runs)
    if len(all_runs) != EXPECTED_RUNS or len(set(all_runs)) != EXPECTED_RUNS:
        raise ValueError(f"expected {EXPECTED_RUNS} unique public SRRs")
    return rows


def write(path: Path, text: str, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    path.chmod(mode)


def sample_manifests(outdir: Path, rows: list[dict[str, str]]) -> list[dict[str, str]]:
    fields = [
        "index",
        "tip_id",
        "panel_id",
        "source_study",
        "assay",
        "analysis_taxon_label",
        "voucher",
        "biosample",
        "run_accessions",
        "run_count",
        "japan38_member_ids",
        "shared_cross_paper_sample",
        "region",
        "location",
        "name_review_required",
        "constituent_tip_count",
    ]
    data: list[dict[str, str]] = []
    for index, row in enumerate(rows):
        data.append(
            {
                "index": str(index),
                "tip_id": f"JOG{index + 1:04d}",
                "panel_id": row["panel_id"],
                "source_study": row["source_studies"],
                "assay": row["assay"],
                "analysis_taxon_label": row["analysis_taxon_label"],
                "voucher": row["voucher"],
                "biosample": row["biosample"],
                "run_accessions": row["run_accessions"],
                "run_count": row["run_count"],
                "japan38_member_ids": row["japan38_member_ids"],
                "shared_cross_paper_sample": row["shared_cross_paper_sample"],
                "region": row["region"],
                "location": row["location"],
                "name_review_required": row["name_review_required"],
                "constituent_tip_count": "1",
            }
        )
    for filename, delimiter in (("sample_manifest.tsv", "\t"), ("sample_manifest.csv", ",")):
        with (outdir / filename).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, delimiter=delimiter, lineterminator="\n")
            writer.writeheader()
            writer.writerows(data)
    return data


def species_map(outdir: Path, data: list[dict[str, str]]) -> list[dict[str, str]]:
    by_taxon: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in data:
        by_taxon[row["analysis_taxon_label"]].append(row)
    rows = []
    interpretation_manifest = []
    interpretation_panel = []
    for index, taxon in enumerate(sorted(by_taxon), 1):
        members = by_taxon[taxon]
        tip_ids = sorted(row["tip_id"] for row in members)
        species_id = f"SP{index:04d}"
        source_studies = joinvals([row["source_study"] for row in members])
        regions = joinvals([row["region"] for row in members])
        locations = joinvals([row["location"] for row in members])
        review_required = str(any(
            row["name_review_required"].casefold() == "true" for row in members
        )).lower()
        rows.append({
            "species_id": species_id,
            "analysis_taxon_label": taxon,
            "tip_ids": "|".join(tip_ids),
            "n_tips": str(len(tip_ids)),
            "source_studies": source_studies,
            "regions": regions,
            "name_review_required": review_required,
        })
        interpretation_manifest.append({
            "tip_id": species_id,
            "panel_id": species_id,
            "source_study": source_studies,
            "analysis_taxon_label": taxon,
            "constituent_tip_count": str(len(tip_ids)),
        })
        interpretation_panel.append({
            "panel_id": species_id,
            "region": regions,
            "location": locations,
            "name_review_required": review_required,
        })
    with (outdir / "astral_species_map.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "species_id", "analysis_taxon_label", "tip_ids", "n_tips",
                "source_studies", "regions", "name_review_required",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    with (outdir / "astral_interpretation_manifest.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "tip_id", "panel_id", "source_study", "analysis_taxon_label",
                "constituent_tip_count",
            ],
        )
        writer.writeheader()
        writer.writerows(interpretation_manifest)
    with (outdir / "astral_interpretation_panel.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["panel_id", "region", "location", "name_review_required"],
        )
        writer.writeheader()
        writer.writerows(interpretation_panel)
    map_lines = [
        f"{row['species_id']}:{','.join(row['tip_ids'].split('|'))}" for row in rows
    ] + ["OUTGROUP_lett:OUTGROUP_lett", "OUTGROUP_sunf:OUTGROUP_sunf"]
    (outdir / "astral_map.txt").write_text("\n".join(map_lines) + "\n", encoding="utf-8")
    return rows


def patch(text: str) -> str:
    """Convert already-tested v1 shell primitives to the corrected v2 inventory."""
    return (
        text.replace("--array=0-301", "--array=0-293")
        .replace("results/japan_origin_global", "results/japan_origin_global_v2")
        .replace(
            "$REPO_ROOT/analysis/summarize_japan_origin_global_comp1061_qc.py",
            "$BUNDLE_DIR/helpers/summarize_japan_origin_global_comp1061_qc_v2.py",
        )
        .replace(
            "$REPO_ROOT/analysis/prepare_japan_origin_global_comp1061_tree_inputs.py",
            "$BUNDLE_DIR/helpers/prepare_japan_origin_global_comp1061_tree_inputs_v2.py",
        )
        .replace(
            "$REPO_ROOT/analysis/validate_japan_origin_global_tree.py",
            "$BUNDLE_DIR/helpers/validate_japan_origin_global_tree_v2.py",
        )
        .replace("302 public biological samples / 303 runs", "294 unique biological samples / 295 unique runs")
        .replace("EAzami 302-sample", "EAzami 294-tip")
        .replace("all 302 samples", "all 294 samples")
    )


def helper_sources(outdir: Path) -> None:
    generated = {
        "summarize_japan_origin_global_comp1061_qc.py": "summarize_japan_origin_global_comp1061_qc_v2.py",
        "prepare_japan_origin_global_comp1061_tree_inputs.py": "prepare_japan_origin_global_comp1061_tree_inputs_v2.py",
        "validate_japan_origin_global_tree.py": "validate_japan_origin_global_tree_v2.py",
    }
    for source, destination in generated.items():
        text = (ROOT / "analysis" / source).read_text(encoding="utf-8")
        text = text.replace("302", "294").replace("_v1", "_v2")
        write(outdir / "helpers" / destination, text, 0o755)

    static_helpers = [
        "validate_japan_origin_astral_tree_v2.py",
        "write_japan_origin_global_tree_provenance_v2.py",
        "analyze_japan_origin_global_tree.py",
        "integrate_japan_origin_topology_sensitivities.py",
    ]
    for filename in static_helpers:
        write(
            outdir / "helpers" / filename,
            (ROOT / "analysis" / filename).read_text(encoding="utf-8"),
            0o755,
        )


def env_yml() -> str:
    text = legacy.env_yml()
    if "astral-tree" not in text:
        text = text.replace("  - biopython\n", "  - biopython\n  - astral-tree=5.7.8\n")
    return text


def astral_script() -> str:
    return (
        """#!/usr/bin/env bash
#SBATCH --job-name=EAzami-jogv2-astral
#SBATCH --cpus-per-task=4
#SBATCH --mem=96G
#SBATCH --time=12:00:00
"""
        + patch(legacy.common())
        + """MODE="${MODE:-bwa}"
TREE="$RESULT_ROOT/tree_$MODE"
OUT="$TREE/astral"
mkdir -p "$OUT"
GT="$OUT/gene_trees.tre"
: > "$GT"
while IFS= read -r LOCUS; do
  test -s "$TREE/gene_trees/$LOCUS.treefile"
  cat "$TREE/gene_trees/$LOCUS.treefile" >> "$GT"
  printf '\n' >> "$GT"
done < "$TREE/inputs/eligible_loci.txt"
test -s "$GT"
MAP="$OUT/astral_map_runtime.txt"
cp "$BUNDLE_DIR/astral_map.txt" "$MAP"
if grep -q 'OUTGROUP_saff' "$GT"; then
  echo 'OUTGROUP_saff:OUTGROUP_saff' >> "$MAP"
fi
"${RUN[@]}" astral -Xmx90G -i "$GT" -a "$MAP" -o "$OUT/japan_origin_global_astral.tree" 2> "$OUT/astral.log"
test -s "$OUT/japan_origin_global_astral.tree"
"""
    )


def accept_script() -> str:
    return (
        """#!/usr/bin/env bash
#SBATCH --job-name=EAzami-jogv2-accept
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=02:00:00
"""
        + patch(legacy.common())
        + """MODE="${MODE:-bwa}"
TREE="$RESULT_ROOT/tree_$MODE"
TREEFILE="$TREE/concat/japan_origin_global_concat.treefile"
ASTRAL="$TREE/astral/japan_origin_global_astral.tree"
test -s "$TREEFILE"
test -s "$ASTRAL"
mkdir -p "$TREE/interpretation"
"${RUN[@]}" python "$BUNDLE_DIR/helpers/write_japan_origin_global_tree_provenance_v2.py" \
  --tree "$TREEFILE" \
  --concat-summary "$TREE/concat/concat_summary.json" \
  --output "$TREE/tree_provenance.json"
"${RUN[@]}" python "$BUNDLE_DIR/helpers/validate_japan_origin_global_tree_v2.py" \
  --tree "$TREEFILE" \
  --manifest "$BUNDLE_DIR/sample_manifest.csv" \
  --provenance "$TREE/tree_provenance.json" \
  --output "$TREE/tree_acceptance.json"
"${RUN[@]}" python "$BUNDLE_DIR/helpers/validate_japan_origin_astral_tree_v2.py" \
  --tree "$ASTRAL" \
  --species-map "$BUNDLE_DIR/astral_species_map.csv" \
  --output "$TREE/astral/tree_acceptance.json"
"${RUN[@]}" python "$BUNDLE_DIR/helpers/analyze_japan_origin_global_tree.py" \
  --tree "$TREEFILE" \
  --manifest "$BUNDLE_DIR/sample_manifest.csv" \
  --source-panel "$BUNDLE_DIR/sample_manifest.csv" \
  --japan38-audit "$REPO_ROOT/data/evidence/moreyra2025_japan_38_membership_audit_2026-08-10.csv" \
  --tree-acceptance "$TREE/tree_acceptance.json" \
  --output "$TREE/interpretation/concat_topology.json" \
  --candidates "$TREE/interpretation/concat_candidates.csv"
"${RUN[@]}" python "$BUNDLE_DIR/helpers/analyze_japan_origin_global_tree.py" \
  --tree "$ASTRAL" \
  --manifest "$BUNDLE_DIR/astral_interpretation_manifest.csv" \
  --source-panel "$BUNDLE_DIR/astral_interpretation_panel.csv" \
  --japan38-audit "$REPO_ROOT/data/evidence/moreyra2025_japan_38_membership_audit_2026-08-10.csv" \
  --tree-acceptance "$TREE/astral/tree_acceptance.json" \
  --output "$TREE/interpretation/astral_topology.json" \
  --candidates "$TREE/interpretation/astral_candidates.csv"
"""
    )


def integration_script() -> str:
    return (
        """#!/usr/bin/env bash
#SBATCH --job-name=EAzami-jogv2-integrate
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=01:00:00
"""
        + patch(legacy.common())
        + """OUT="$RESULT_ROOT/sensitivity_acceptance"
mkdir -p "$OUT"
for MODE in bwa blastx; do
  test -s "$RESULT_ROOT/tree_$MODE/interpretation/concat_topology.json"
  test -s "$RESULT_ROOT/tree_$MODE/interpretation/concat_candidates.csv"
  test -s "$RESULT_ROOT/tree_$MODE/interpretation/astral_topology.json"
  test -s "$RESULT_ROOT/tree_$MODE/interpretation/astral_candidates.csv"
done
SCENARIOS="$OUT/topology_sensitivity_scenarios.csv"
cat > "$SCENARIOS" <<EOF
scenario_id,mapping_method,tree_method,interpretation_json,candidate_table
bwa_concat,bwa,concat,$RESULT_ROOT/tree_bwa/interpretation/concat_topology.json,$RESULT_ROOT/tree_bwa/interpretation/concat_candidates.csv
bwa_astral,bwa,astral,$RESULT_ROOT/tree_bwa/interpretation/astral_topology.json,$RESULT_ROOT/tree_bwa/interpretation/astral_candidates.csv
blastx_concat,blastx,concat,$RESULT_ROOT/tree_blastx/interpretation/concat_topology.json,$RESULT_ROOT/tree_blastx/interpretation/concat_candidates.csv
blastx_astral,blastx,astral,$RESULT_ROOT/tree_blastx/interpretation/astral_topology.json,$RESULT_ROOT/tree_blastx/interpretation/astral_candidates.csv
EOF
ARGS=(--scenarios "$SCENARIOS" --output "$OUT/sensitivity_acceptance.json" --stable-candidates "$OUT/stable_sister_candidates.csv")
if [[ -n "${NAME_REVIEW:-}" ]]; then
  test -s "$NAME_REVIEW"
  ARGS+=(--name-review "$NAME_REVIEW")
fi
"${RUN[@]}" python "$BUNDLE_DIR/helpers/integrate_japan_origin_topology_sensitivities.py" "${ARGS[@]}"
"""
    )


def submit_tree() -> str:
    return """#!/usr/bin/env bash
set -euo pipefail
MODE="${MODE:-bwa}"
prep=$(sbatch --parsable --export=ALL,MODE="$MODE" 04_prepare_tree_inputs_slurm.sh)
aln=$(sbatch --parsable --dependency=afterok:$prep --export=ALL,MODE="$MODE" 05_align_loci_slurm.sh)
gene=$(sbatch --parsable --dependency=afterok:$aln --export=ALL,MODE="$MODE" 06_gene_trees_slurm.sh)
con=$(sbatch --parsable --dependency=afterok:$aln --export=ALL,MODE="$MODE" 07_concat_tree_slurm.sh)
ast=$(sbatch --parsable --dependency=afterok:$gene --export=ALL,MODE="$MODE" 08_astral_species_tree_slurm.sh)
acc=$(sbatch --parsable --dependency=afterok:$con:$ast --export=ALL,MODE="$MODE" 09_accept_trees_slurm.sh)
printf 'prep=%s\nalign=%s\ngene=%s\nconcat=%s\nastral=%s\naccept=%s\n' "$prep" "$aln" "$gene" "$con" "$ast" "$acc"
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()

    rows = read_panel(args.panel)
    args.outdir.mkdir(parents=True, exist_ok=True)
    data = sample_manifests(args.outdir, rows)
    species = species_map(args.outdir, data)
    helper_sources(args.outdir)
    write(args.outdir / "env.yml", env_yml())

    scripts = {
        "00_prepare_inputs_slurm.sh": patch(legacy.prep()),
        "01_fetch_trim_slurm.sh": patch(legacy.fetch()),
        "02_hybpiper_bwa_slurm.sh": patch(legacy.hyb("bwa")),
        "02b_hybpiper_blastx_slurm.sh": patch(legacy.hyb("blastx")),
        "03_retrieve_qc_slurm.sh": patch(legacy.qc()),
        "04_prepare_tree_inputs_slurm.sh": patch(legacy.treeprep()),
        "05_align_loci_slurm.sh": patch(legacy.align()),
        "06_gene_trees_slurm.sh": patch(legacy.gene()),
        "07_concat_tree_slurm.sh": patch(legacy.concat()),
        "08_astral_species_tree_slurm.sh": astral_script(),
        "09_accept_trees_slurm.sh": accept_script(),
        "10_integrate_sensitivity_gate_slurm.sh": integration_script(),
        "submit_bwa_chain.sh": patch(legacy.submit_data("bwa")),
        "submit_blastx_chain.sh": patch(legacy.submit_data("blastx")),
        "submit_tree_chain.sh": submit_tree(),
    }
    for name, text in scripts.items():
        write(args.outdir / name, text, 0o755)

    manifest = {
        "bundle_version": "japan_origin_global_hpc_bundle_v2",
        "biological_samples": EXPECTED_SAMPLES,
        "public_runs": EXPECTED_RUNS,
        "source_preserving_taxon_labels": len(species),
        "cross_paper_read_duplicates_removed": 8,
        "safe_tip_ids": True,
        "primary_mapping": "bwa",
        "mapping_sensitivity": "blastx",
        "hybpiper_version": "2.3.4",
        "frozen_primary_locus_universe": 241,
        "primary_current_occupancy_gate": 0.80,
        "current_paralog_gate": "zero HybPiper >1-copy warnings across all 294 samples",
        "minimum_primary_loci_to_launch": 100,
        "automatic_filter_relaxation_allowed": False,
        "tree_products": [
            "294-tip concatenated IQ-TREE ML tree",
            "source-label ASTRAL-III 5.7.8 species tree",
            "per-locus IQ-TREE gene trees",
        ],
        "tree_completed": False,
        "japanese_origin_inference_completed": False,
        "sensitivity_acceptance_contract": "japan_origin_topology_sensitivity_acceptance_v1",
        "sensitivity_scenarios": [
            "bwa_concat", "bwa_astral", "blastx_concat", "blastx_astral"
        ],
        "sensitivity_integration_command": "sbatch 10_integrate_sensitivity_gate_slurm.sh",
        "new_china_sampling_freeze_allowed": False,
    }
    write(args.outdir / "execution_manifest.json", json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
