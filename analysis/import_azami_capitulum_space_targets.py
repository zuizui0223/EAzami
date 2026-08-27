#!/usr/bin/env python3
"""Import frozen Azami capitulum-space targets into EAzami without hand editing.

This bridge deliberately preserves the Azami observation layer. It validates the
machine-readable target tables emitted by an artifact-backed Azami run, attaches
immutable provenance, and writes one normalized EAzami registry. It does not
score mechanism families and does not convert observational associations into
selection coefficients or functional effects.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

SPACE_REQUIRED = {
    "target_id", "scope", "scale", "value", "ci95_low", "ci95_high", "handoff_status"
}
ENV_REQUIRED = {"target_id", "scope", "scale", "value", "handoff_status"}
ALLOWED_SPACE_TARGETS = {
    "capitulum_within_module_integration_contrast",
    "capitulum_among_module_integration_contrast",
    "capitulum_cross_scale_association_matrix_similarity",
}
ALLOWED_HANDOFF_STATUS = {
    "observational_structure_target",
    "observational_environment_block_target",
    "descriptive_effect_geometry_target",
}
ALLOWED_SCALES = {"within_taxon", "among_taxon", "within_vs_among"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require_columns(frame: pd.DataFrame, required: set[str], label: str) -> None:
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"{label} missing columns: {missing}")


def validate_common(frame: pd.DataFrame, label: str) -> None:
    if frame.empty:
        raise ValueError(f"{label} is empty")
    if frame.duplicated(["target_id", "scope", "scale"]).any():
        raise ValueError(f"{label} has duplicate target_id/scope/scale rows")
    if not set(frame["scale"]).issubset(ALLOWED_SCALES):
        bad = sorted(set(frame["scale"]).difference(ALLOWED_SCALES))
        raise ValueError(f"{label} has unsupported scales: {bad}")
    if not set(frame["handoff_status"]).issubset(ALLOWED_HANDOFF_STATUS):
        bad = sorted(set(frame["handoff_status"]).difference(ALLOWED_HANDOFF_STATUS))
        raise ValueError(f"{label} has unsupported handoff statuses: {bad}")
    values = pd.to_numeric(frame["value"], errors="coerce")
    if values.isna().any():
        raise ValueError(f"{label} contains non-numeric target values")


def validate_space(frame: pd.DataFrame) -> None:
    require_columns(frame, SPACE_REQUIRED, "capitulum-space targets")
    validate_common(frame, "capitulum-space targets")
    unexpected = sorted(set(frame["target_id"]).difference(ALLOWED_SPACE_TARGETS))
    if unexpected:
        raise ValueError(f"Unexpected capitulum-space target IDs: {unexpected}")
    lows = pd.to_numeric(frame["ci95_low"], errors="coerce")
    highs = pd.to_numeric(frame["ci95_high"], errors="coerce")
    values = pd.to_numeric(frame["value"], errors="coerce")
    if (lows.isna() | highs.isna()).any():
        raise ValueError("Capitulum-space targets require numeric bootstrap intervals")
    if ((values < lows) | (values > highs)).any():
        raise ValueError("Capitulum-space point estimate must lie inside its bootstrap interval")


def validate_environment(frame: pd.DataFrame) -> None:
    require_columns(frame, ENV_REQUIRED, "environment-space targets")
    validate_common(frame, "environment-space targets")
    allowed_prefixes = (
        "environment_block_r2:",
        "environment_block_cross_scale_cosine:",
    )
    bad = sorted(x for x in frame["target_id"] if not str(x).startswith(allowed_prefixes))
    if bad:
        raise ValueError(f"Unexpected environment target IDs: {bad}")


def normalize(
    space: pd.DataFrame,
    env: pd.DataFrame,
    *,
    source_run_id: str,
    source_artifact_id: str,
    source_artifact_digest: str,
    source_head_sha: str,
    space_sha: str,
    env_sha: str,
) -> pd.DataFrame:
    space = space.copy()
    env = env.copy()
    env["ci95_low"] = pd.NA
    env["ci95_high"] = pd.NA
    combined = pd.concat([
        space[["target_id", "scope", "scale", "value", "ci95_low", "ci95_high", "handoff_status"]],
        env[["target_id", "scope", "scale", "value", "ci95_low", "ci95_high", "handoff_status"]],
    ], ignore_index=True)
    combined.insert(0, "source_layer", "azami_observation")
    combined["simulation_role"] = "unscored_observational_target"
    combined["causal_status"] = "observational_noncausal"
    combined["source_repository"] = "zuizui0223/azami"
    combined["source_run_id"] = str(source_run_id)
    combined["source_artifact_id"] = str(source_artifact_id)
    combined["source_artifact_digest"] = source_artifact_digest
    combined["source_head_sha"] = source_head_sha
    combined["source_space_table_sha256"] = space_sha
    combined["source_environment_table_sha256"] = env_sha
    combined["claim_boundary"] = (
        "Azami phenotype-space observation target only; not genetic/functional modularity, "
        "plasticity, adaptation, selection coefficient, or causal mechanism."
    )
    return combined


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--capitulum-space", type=Path, required=True)
    p.add_argument("--environment-space", type=Path, required=True)
    p.add_argument("--source-run-id", required=True)
    p.add_argument("--source-artifact-id", required=True)
    p.add_argument("--source-artifact-digest", required=True)
    p.add_argument("--source-head-sha", required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    args = p.parse_args()

    if not args.source_artifact_digest.startswith("sha256:"):
        raise ValueError("source artifact digest must use sha256: prefix")
    if len(args.source_head_sha) != 40:
        raise ValueError("source head SHA must be a full 40-character commit SHA")

    space = pd.read_csv(args.capitulum_space, low_memory=False)
    env = pd.read_csv(args.environment_space, low_memory=False)
    validate_space(space)
    validate_environment(env)
    space_sha = sha256(args.capitulum_space)
    env_sha = sha256(args.environment_space)
    combined = normalize(
        space, env,
        source_run_id=args.source_run_id,
        source_artifact_id=args.source_artifact_id,
        source_artifact_digest=args.source_artifact_digest,
        source_head_sha=args.source_head_sha,
        space_sha=space_sha,
        env_sha=env_sha,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(args.out, index=False)
    report = {
        "status": "validated_observational_handoff",
        "n_targets": int(len(combined)),
        "n_structure_targets": int(combined["handoff_status"].eq("observational_structure_target").sum()),
        "n_environment_block_targets": int(combined["handoff_status"].eq("observational_environment_block_target").sum()),
        "n_descriptive_geometry_targets": int(combined["handoff_status"].eq("descriptive_effect_geometry_target").sum()),
        "source_run_id": str(args.source_run_id),
        "source_artifact_id": str(args.source_artifact_id),
        "source_artifact_digest": args.source_artifact_digest,
        "source_head_sha": args.source_head_sha,
        "space_table_sha256": space_sha,
        "environment_table_sha256": env_sha,
        "simulation_role": "unscored_observational_target",
        "boundary": "Importer validates provenance only; a later explicit model contract must decide whether and how any target is scoreable.",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
