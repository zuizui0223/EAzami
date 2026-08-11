#!/usr/bin/env python3
"""Validate and freeze the Chang 2026 gene-tree workflow execution contract.

This validator sits between the generated 19-sample/8-hypothesis package and the
heavy Snakemake execution. It confirms that:

* all 19 samples have unique, verified official SRA runs;
* all 19 current runs are officially ``LibraryLayout=PAIRED``;
* supplement read-count discrepancies do not override official layout metadata;
* the six focal tips contain exactly three W and three BP samples;
* one published candidate-regain and seven nearest loss-only hypotheses are
  present and topologically distinct;
* the Snakefile contains the complete five-stage analysis DAG;
* every referenced runner script and conda environment exists; and
* a deterministic Snakemake config can be written with checksummed inputs.

The contract does not download reads or execute external bioinformatics tools.
It is intended for CI and for preflight validation on a workstation or HPC.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Mapping

import run_chang2026_layout_aware_transcriptome_assembly as assembly_runner
import score_chang2026_gene_tree_hypotheses as scorer

DEFAULT_SNAKEFILE = Path("workflow/chang2026_gene_trees/Snakefile")
DEFAULT_CONFIG_OUTPUT = Path(
    "data/evidence/generated/chang2026_gene_tree_panel/"
    "chang2026_gene_tree_workflow_config.json"
)
DEFAULT_SUMMARY_OUTPUT = Path(
    "data/evidence/generated/chang2026_gene_tree_panel/"
    "chang2026_gene_tree_workflow_contract.json"
)
DEFAULT_RESULTS_DIR = Path("results/chang2026_gene_tree_workflow")

EXPECTED_RULES = (
    "all",
    "assemble_transcriptomes",
    "orthofinder",
    "prepare_single_copy_orthogroups",
    "infer_rooted_gene_trees",
    "score_competing_takaoense_histories",
)
EXPECTED_RUNNERS = (
    "run_chang2026_layout_aware_transcriptome_assembly.py",
    "run_chang2026_transcriptome_assembly.py",
    "prefix_fasta_headers.py",
    "prepare_chang2026_single_copy_orthogroups.py",
    "run_chang2026_single_copy_gene_trees.py",
    "score_chang2026_gene_tree_hypotheses.py",
)
EXPECTED_ENVS = (
    "assembly.yml",
    "orthofinder.yml",
    "gene_trees.yml",
    "scoring.yml",
)
EXPECTED_ROLES = {
    "coloured_flanking_introgression_control": 7,
    "coloured_root_context": 2,
    "focal_colour_morph": 6,
    "outgroup": 2,
    "white_sister_control": 2,
}
DEFAULT_RESOURCES = {
    "assembly_jobs": 1,
    "fasterq_threads": 8,
    "fastp_threads": 8,
    "trinity_threads": 16,
    "trinity_memory_gb": 96,
    "orthofinder_threads": 24,
    "orthofinder_search_threads": 24,
    "gene_tree_jobs": 8,
    "gene_tree_threads_per_job": 1,
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def extract_rule_names(text: str) -> list[str]:
    return re.findall(r"^rule\s+([A-Za-z_][A-Za-z0-9_]*)\s*:", text, flags=re.M)


def repo_root_from_snakefile(snakefile: Path) -> Path:
    resolved = snakefile.resolve()
    if resolved.name != "Snakefile" or resolved.parent.name != "chang2026_gene_trees":
        raise ValueError(
            "Expected workflow/chang2026_gene_trees/Snakefile, observed "
            f"{resolved}"
        )
    if resolved.parent.parent.name != "workflow":
        raise ValueError(f"Snakefile is outside the expected workflow directory: {resolved}")
    return resolved.parents[2]


def validate_workflow_files(
    snakefile: Path,
) -> tuple[list[str], dict[str, str], dict[str, str]]:
    if not snakefile.is_file():
        raise ValueError(f"Snakefile does not exist: {snakefile}")
    text = snakefile.read_text(encoding="utf-8")
    rules = extract_rule_names(text)
    if rules != list(EXPECTED_RULES):
        raise ValueError(
            f"Unexpected Snakefile rules/order: observed={rules}, "
            f"expected={list(EXPECTED_RULES)}"
        )

    repo_root = repo_root_from_snakefile(snakefile)
    analysis_dir = repo_root / "analysis"
    env_dir = snakefile.resolve().parent / "envs"
    runner_hashes: dict[str, str] = {}
    env_hashes: dict[str, str] = {}

    for name in EXPECTED_RUNNERS:
        path = analysis_dir / name
        if not path.is_file():
            raise ValueError(f"Required runner script is missing: {path}")
        # The layout-aware runner imports the paired implementation rather than
        # invoking it directly from the Snakefile; both files remain frozen.
        if name == "run_chang2026_transcriptome_assembly.py":
            adapter = analysis_dir / "run_chang2026_layout_aware_transcriptome_assembly.py"
            adapter_text = adapter.read_text(encoding="utf-8")
            if "import run_chang2026_transcriptome_assembly as paired" not in adapter_text:
                raise ValueError("Layout-aware adapter no longer imports paired implementation")
        elif name not in text:
            raise ValueError(f"Snakefile does not reference required runner: {name}")
        runner_hashes[name] = sha256_file(path)

    for name in EXPECTED_ENVS:
        path = env_dir / name
        if not path.is_file():
            raise ValueError(f"Required conda environment is missing: {path}")
        if f'envs/{name}' not in text:
            raise ValueError(f"Snakefile does not reference required environment: {name}")
        env_hashes[name] = sha256_file(path)

    return rules, runner_hashes, env_hashes


def read_hypothesis_rows(path: Path) -> list[dict[str, str]]:
    return scorer.read_csv(path)


def validate_hypothesis_contract(path: Path) -> tuple[list[dict[str, object]], dict[str, int]]:
    hypotheses = scorer.hypothesis_metadata(path)
    rows = read_hypothesis_rows(path)
    topology_strings = [row.get("topology_newick", "") for row in rows]
    if len(topology_strings) != len(set(topology_strings)):
        raise ValueError("Competing hypothesis table contains duplicate topologies")
    classes = Counter(str(row.get("history_class", "")) for row in rows)
    expected_classes = {
        "nearest_loss_only_topology": 7,
        "topology_supported_candidate_regain": 1,
    }
    if dict(classes) != expected_classes:
        raise ValueError(
            f"Unexpected hypothesis classes: observed={dict(classes)}, "
            f"expected={expected_classes}"
        )
    if rows[0].get("hypothesis_id") != scorer.PUBLISHED_HYPOTHESIS:
        raise ValueError("Published candidate-regain topology is not the first hypothesis")
    loss_rows = [
        row for row in rows if row.get("history_class") == "nearest_loss_only_topology"
    ]
    if any(str(row.get("rooted_rf_distance_from_published")) != "4" for row in loss_rows):
        raise ValueError("One or more nearest loss-only hypotheses are not at rooted RF 4")
    return hypotheses, dict(classes)


def make_config(
    panel: Path,
    hypotheses: Path,
    results_dir: Path,
    *,
    resources: Mapping[str, int] | None = None,
) -> dict[str, object]:
    return {
        "panel_csv": str(panel.resolve()),
        "hypotheses_csv": str(hypotheses.resolve()),
        "results_dir": str(results_dir.resolve()),
        "keep_raw_reads": False,
        "bootstrap_replicates": 1000,
        "alrt_replicates": 1000,
        "support_thresholds": [0, 50, 70, 90],
        "resources": dict(resources or DEFAULT_RESOURCES),
    }


def build_contract(
    panel: Path,
    hypotheses: Path,
    snakefile: Path,
    results_dir: Path,
) -> tuple[dict[str, object], dict[str, object]]:
    panel_rows = assembly_runner.validate_panel(panel)
    focal, roles, morphs = scorer.panel_metadata(panel)
    hypothesis_rows, hypothesis_classes = validate_hypothesis_contract(hypotheses)
    rules, runner_hashes, env_hashes = validate_workflow_files(snakefile)

    role_counts = Counter(roles.values())
    if dict(role_counts) != EXPECTED_ROLES:
        raise ValueError(
            f"Unexpected panel roles: observed={dict(role_counts)}, "
            f"expected={EXPECTED_ROLES}"
        )
    focal_morphs = Counter(morphs[sample_id] for sample_id in focal)
    if dict(focal_morphs) != {"BP": 3, "W": 3}:
        raise ValueError(f"Unexpected focal morph counts: {dict(focal_morphs)}")

    layouts = Counter(str(row.get("library_layout", "")).upper() for row in panel_rows)
    if dict(layouts) != {"PAIRED": 19}:
        raise ValueError(
            "Current Chang heavy workflow requires 19 official paired-end runs; "
            f"observed={dict(layouts)}"
        )

    outgroups = sorted(
        sample_id
        for sample_id, role in roles.items()
        if role == "outgroup"
    )
    if len(outgroups) != 2:
        raise ValueError(f"Expected two C. lineare outgroups, observed {outgroups}")

    config = make_config(panel, hypotheses, results_dir)
    summary: dict[str, object] = {
        "contract_version": "chang2026_gene_tree_workflow_v2_official_layout",
        "panel_rows": len(panel_rows),
        "unique_sample_ids": len({row["sample_id"] for row in panel_rows}),
        "unique_official_runs": len({row["matched_run"] for row in panel_rows}),
        "official_library_layout_counts": dict(sorted(layouts.items())),
        "library_layout_source": "official NCBI SRA LibraryLayout",
        "panel_role_counts": dict(sorted(role_counts.items())),
        "focal_sample_count": len(focal),
        "focal_morph_counts": dict(sorted(focal_morphs.items())),
        "outgroup_sample_ids": outgroups,
        "hypothesis_count": len(hypothesis_rows),
        "hypothesis_class_counts": dict(sorted(hypothesis_classes.items())),
        "snakefile_rules": rules,
        "panel_sha256": sha256_file(panel),
        "hypotheses_sha256": sha256_file(hypotheses),
        "snakefile_sha256": sha256_file(snakefile),
        "runner_sha256": dict(sorted(runner_hashes.items())),
        "conda_environment_sha256": dict(sorted(env_hashes.items())),
        "heavy_computation_executed": False,
        "execution_gate": (
            "The contract validates official layout, inputs and DAG structure. "
            "Raw-read download, assembly, orthology and gene-tree inference "
            "remain explicit external steps."
        ),
    }
    return config, summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--hypotheses", type=Path, required=True)
    parser.add_argument("--snakefile", type=Path, default=DEFAULT_SNAKEFILE)
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS_DIR)
    parser.add_argument("--config-output", type=Path, default=DEFAULT_CONFIG_OUTPUT)
    parser.add_argument("--summary-output", type=Path, default=DEFAULT_SUMMARY_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config, summary = build_contract(
        args.panel,
        args.hypotheses,
        args.snakefile,
        args.results_dir,
    )
    args.config_output.parent.mkdir(parents=True, exist_ok=True)
    args.config_output.write_text(
        json.dumps(config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"panel_rows={summary['panel_rows']}")
    print(f"unique_official_runs={summary['unique_official_runs']}")
    print(
        "official_library_layout_counts="
        + json.dumps(summary["official_library_layout_counts"], sort_keys=True)
    )
    print(f"focal_morph_counts={json.dumps(summary['focal_morph_counts'], sort_keys=True)}")
    print(f"hypothesis_count={summary['hypothesis_count']}")
    print("snakefile_rules=" + "|".join(summary["snakefile_rules"]))
    print(f"snakefile_sha256={summary['snakefile_sha256']}")
    print(args.config_output)
    print(args.summary_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
