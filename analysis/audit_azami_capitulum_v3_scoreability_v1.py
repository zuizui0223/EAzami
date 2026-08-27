#!/usr/bin/env python3
"""Audit whether the current model generator can be scored against the 62 Azami targets."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

SCHEMA_MARKER = 'AZAMI_CAPITULUM_V3_OBSERVATION_SCHEMA = "azami_capitulum_v3_estimand_contract_v1"'


def load_targets(space: Path, environment: Path, incremental: Path) -> pd.DataFrame:
    a = pd.read_csv(space)
    b = pd.read_csv(environment)
    c = pd.read_csv(incremental)
    c = c.assign(value=pd.to_numeric(c["partial_r2"], errors="raise"))
    a = a.assign(target_class="structure")
    b = b.assign(target_class=b["target_id"].astype(str).map(
        lambda x: "environment_geometry" if x.startswith("environment_block_cross_scale_cosine:") else "environment_block_r2"
    ))
    c = c.assign(target_class="environment_incremental")
    common = ["target_id", "scope", "scale", "value", "target_class"]
    out = pd.concat([a[common], b[common], c[common]], ignore_index=True)
    if len(out) != 62:
        raise RuntimeError(f"expected 62 imported targets, found {len(out)}")
    if out.duplicated(["target_id", "scope", "scale"]).any():
        raise RuntimeError("duplicate imported target key")
    return out


def audit(contract: dict, targets: pd.DataFrame, generator_text: str) -> tuple[pd.DataFrame, dict]:
    schema = contract["observation_schema"]
    endpoints = schema["response_endpoints"]
    env = schema["environment_predictors"]
    marker_present = SCHEMA_MARKER in generator_text
    named_endpoint_coverage = sum(name in generator_text for name in endpoints)
    named_environment_coverage = sum(name in generator_text for name in env)
    exact_generator_ready = marker_present and named_endpoint_coverage == len(endpoints) and named_environment_coverage == len(env)

    rows = []
    for row in targets.to_dict("records"):
        rows.append({
            **row,
            "statistics_adapter_ready": True,
            "current_generator_exact_observation_schema_ready": exact_generator_ready,
            "scoreable_now": exact_generator_ready,
            "blocker": "" if exact_generator_ready else "current_generator_does_not_emit_exact_18endpoint_9environment_observation_rows",
            "prohibited_substitution": "do_not_map_v2_scalar_summaries_by_semantic_similarity",
        })
    ledger = pd.DataFrame(rows)
    counts = ledger.groupby("target_class").size().to_dict()
    summary = {
        "contract_version": contract["contract_version"],
        "target_count": int(len(ledger)),
        "target_class_counts": {str(k): int(v) for k, v in counts.items()},
        "statistics_adapter_ready_targets": int(ledger["statistics_adapter_ready"].sum()),
        "current_v2_exact_scoreable_targets": int(ledger["scoreable_now"].sum()),
        "current_v2_exact_unscoreable_targets": int((~ledger["scoreable_now"]).sum()),
        "generator_schema_marker_present": marker_present,
        "exact_endpoint_names_present_in_generator": int(named_endpoint_coverage),
        "exact_environment_names_present_in_generator": int(named_environment_coverage),
        "decision": "statistics_layer_ready_generator_layer_blocked" if not exact_generator_ready else "exact_generator_schema_ready",
        "next_blocker": "emit observation-level rows on the frozen environment design under a separately versioned v3 model generator" if not exact_generator_ready else "run model-family prior-predictive scoring",
        "claim_boundary": "Scoreability is an interface property. It does not establish model fit, causal mechanism or adaptation.",
    }
    return ledger, summary


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--contract", type=Path, default=Path("data/evidence/azami_capitulum_v3_estimand_contract_v1.json"))
    p.add_argument("--space", type=Path, default=Path("data/evidence/source/azami_capitulum_space_eazami_targets_run33035785120.csv"))
    p.add_argument("--environment", type=Path, default=Path("data/evidence/source/azami_capitulum_environment_eazami_targets_run33035785120.csv"))
    p.add_argument("--incremental", type=Path, default=Path("data/evidence/source/azami_capitulum_environment_incremental_eazami_targets_run33035785120.csv"))
    p.add_argument("--generator", type=Path, default=Path("analysis/simulate_capitulum_pattern_reduction_v2.py"))
    p.add_argument("--ledger", type=Path, required=True)
    p.add_argument("--summary", type=Path, required=True)
    a = p.parse_args()
    contract = json.loads(a.contract.read_text(encoding="utf-8"))
    targets = load_targets(a.space, a.environment, a.incremental)
    ledger, summary = audit(contract, targets, a.generator.read_text(encoding="utf-8"))
    a.ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.to_csv(a.ledger, index=False)
    a.summary.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
