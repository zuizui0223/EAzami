#!/usr/bin/env python3
"""Authoritative execution gate for Chang 2026 Read2Tree topology scoring.

The underlying scorer can reconstruct the eight hypotheses from the current
nearest-topology and robustness inputs. This wrapper makes the versioned frozen
CSV the execution contract: it first verifies that the frozen rows exactly match
the current source-derived rows, checks the byte-level SHA256, then runs the
scorer and annotates its JSON output with frozen-hypothesis provenance.

Use this wrapper for real Read2Tree results rather than invoking
``score_chang2026_read2tree_topology.py`` directly.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import validate_chang2026_takaoense_hypothesis_freeze as freeze

DEFAULT_FROZEN = Path("analysis/chang2026_takaoense_gene_tree_hypotheses_v1.csv")
DEFAULT_EXPECTED_SHA256 = "5dbd081b5c360f73d824221f2dbc09892666f23ecc74a706620943f4c881692f"
DEFAULT_SCORER = Path("analysis/score_chang2026_read2tree_topology.py")
DEFAULT_NEAREST = Path("analysis/chang2026_takaoense_nearest_no_regain_topologies.csv")
DEFAULT_ROBUSTNESS = Path("analysis/chang2026_takaoense_topology_robustness_summary.json")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_scientific_contract(
    *,
    frozen: Path,
    nearest: Path,
    robustness: Path,
    expected_sha256: str,
) -> dict[str, object]:
    rows = freeze.validate(nearest, robustness, frozen)
    observed_sha = sha256_file(frozen)
    if observed_sha != expected_sha256:
        raise ValueError(
            "Frozen hypothesis byte-level SHA256 changed: "
            f"expected={expected_sha256}, observed={observed_sha}"
        )
    return {
        "validated_hypothesis_count": len(rows),
        "hypothesis_ids": [row["hypothesis_id"] for row in rows],
        "frozen_hypothesis_path": str(frozen),
        "frozen_hypothesis_sha256": observed_sha,
        "source_nearest_path": str(nearest),
        "source_robustness_path": str(robustness),
        "contract_status": "validated",
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--tree", type=Path, required=True)
    p.add_argument("--panel", type=Path, required=True)
    p.add_argument("--reference-manifest", type=Path, required=True)
    p.add_argument("--outgroup", default="DAUCS")
    p.add_argument("--thresholds", default="0,50,70,90")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--hypothesis-output", type=Path, required=True)
    p.add_argument("--summary-json", type=Path, required=True)
    p.add_argument("--frozen-hypotheses", type=Path, default=DEFAULT_FROZEN)
    p.add_argument("--expected-hypothesis-sha256", default=DEFAULT_EXPECTED_SHA256)
    p.add_argument("--nearest", type=Path, default=DEFAULT_NEAREST)
    p.add_argument("--robustness-summary", type=Path, default=DEFAULT_ROBUSTNESS)
    p.add_argument("--scorer", type=Path, default=DEFAULT_SCORER)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    provenance = validate_scientific_contract(
        frozen=args.frozen_hypotheses,
        nearest=args.nearest,
        robustness=args.robustness_summary,
        expected_sha256=args.expected_hypothesis_sha256,
    )

    command = [
        sys.executable,
        str(args.scorer),
        "--tree", str(args.tree),
        "--panel", str(args.panel),
        "--reference-manifest", str(args.reference_manifest),
        "--outgroup", args.outgroup,
        "--nearest", str(args.nearest),
        "--robustness-summary", str(args.robustness_summary),
        "--thresholds", args.thresholds,
        "--output", str(args.output),
        "--hypothesis-output", str(args.hypothesis_output),
        "--summary-json", str(args.summary_json),
    ]
    subprocess.run(command, check=True)

    payload = json.loads(args.summary_json.read_text(encoding="utf-8"))
    payload["scientific_input_contract"] = provenance
    payload["scorer_invocation"] = command
    args.summary_json.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print("hypothesis_contract=validated")
    print(f"hypothesis_sha256={provenance['frozen_hypothesis_sha256']}")
    print(f"validated_hypotheses={provenance['validated_hypothesis_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
