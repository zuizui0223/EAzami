#!/usr/bin/env python3
"""Freeze the final Taiwan taxonomic-alias occurrence sensitivity artifact.

The input is a GitHub Actions artifact from the already successful source-guarded
workflow.  This script locates files by contract_version rather than by assuming an
unstable archive directory layout, validates their roles, and writes a compact
machine-readable result plus a human-readable report.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--artifact-root", type=Path, required=True)
    p.add_argument("--out-json", type=Path, required=True)
    p.add_argument("--out-md", type=Path, required=True)
    p.add_argument("--source-run", type=int, required=True)
    p.add_argument("--source-artifact-id", type=int, required=True)
    return p.parse_args()


def load_jsons(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    out = []
    for path in root.rglob("*.json"):
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(obj, dict):
            out.append((path, obj))
    return out


def find_contract(items: list[tuple[Path, dict[str, Any]]], version: str) -> list[tuple[Path, dict[str, Any]]]:
    return [(p, x) for p, x in items if x.get("contract_version") == version]


def axis_summary(reach: dict[str, Any], axis: str) -> dict[str, Any]:
    item = reach["orientation"]["axes"][axis]
    return {
        "beta_D_minus_U_sd_range": item["beta_D_minus_U_sd_range"],
        "p_range": item["p_range"],
        "accepted_species_tree_sign_agreement": item["accepted_topology_sign_agreement"],
        "species_loo_sign_agreement": item["species_loo_sign_agreement"],
        "species_loo_evaluations": item["species_loo_evaluations"],
    }


def reach_summary(path: Path, reach: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_path": str(path),
        "status": reach["orientation"]["status"],
        "n_taxa": reach["orientation"]["n_taxa"],
        "n_U": reach["orientation"]["n_U"],
        "n_D": reach["orientation"]["n_D"],
        "bio01": axis_summary(reach, "chelsa_bio01"),
        "bio12": axis_summary(reach, "chelsa_bio12"),
        "bio15": axis_summary(reach, "chelsa_bio15"),
    }


def choose_reaches(items: list[tuple[Path, dict[str, Any]]]) -> dict[str, tuple[Path, dict[str, Any]]]:
    candidates = find_contract(items, "chapter2_ecological_explanatory_reach_v1")
    chosen: dict[str, tuple[Path, dict[str, Any]]] = {}
    for path, obj in candidates:
        low = path.as_posix().casefold()
        if "alias_native" in low:
            chosen["alias_native"] = (path, obj)
        elif "alias_broad" in low:
            chosen["alias_broad"] = (path, obj)
    if set(chosen) != {"alias_native", "alias_broad"}:
        raise RuntimeError(f"could not uniquely identify alias reach outputs: {sorted(chosen)}")
    return chosen


def topology_summary(items: list[tuple[Path, dict[str, Any]]]) -> dict[str, Any]:
    candidates = find_contract(items, "fdt4_orientation_phylogeny_saturation_v1")
    if not candidates:
        raise RuntimeError("no topology saturation result in artifact")
    # Prefer the panel-matched alias run by requiring at least one panel with >11 taxa.
    selected = None
    for path, obj in candidates:
        nmax = max((v.get("n_taxa", 0) for v in obj.get("panels", {}).values()), default=0)
        if nmax > 11:
            selected = (path, obj)
            break
    if selected is None:
        selected = candidates[-1]
    path, obj = selected
    layers = obj.get("layers", {})
    compact: dict[str, Any] = {
        "source_path": str(path),
        "panels": obj.get("panels", {}),
        "ensemble_sizes": obj.get("ensemble_sizes", {}),
        "topology_diversity": obj.get("topology_diversity", {}),
        "ufboot_branch_length_status": obj.get("ufboot_branch_length_status"),
        "sign_rates": {},
    }
    for ensemble in ("concatenated_ufboot", "locus_tree_complete", "astral153_from_public_loci", "chang2026_astral_alias_overlap"):
        if ensemble not in layers:
            continue
        compact["sign_rates"][ensemble] = {}
        for panel, modes in layers[ensemble].items():
            compact["sign_rates"][ensemble][panel] = {}
            for mode, axes in modes.items():
                if not isinstance(axes, dict):
                    continue
                compact["sign_rates"][ensemble][panel][mode] = {
                    axis: axes[axis].get("expected_sign_rate")
                    for axis in ("chelsa_bio01", "chelsa_bio15") if axis in axes
                }
    return compact


def write_md(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Taiwan alias-aware public-occurrence saturation result v1",
        "",
        f"Source workflow run: `{payload['provenance']['workflow_run_id']}`; artifact ID: `{payload['provenance']['artifact_id']}`.",
        "",
        "## Alias-expanded ecological panels",
        "",
        "| Tier | n taxa | U/D | frozen-rule status | BIO1 beta range | BIO1 P range | BIO12 beta range | BIO12 P range | BIO15 beta range | BIO15 P range |",
        "| --- | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for name in ("alias_native", "alias_broad"):
        x = payload["occurrence_tiers"][name]
        fmt = lambda a: f"{a[0]:.6g} to {a[1]:.6g}"
        lines.append(
            f"| {name} | {x['n_taxa']} | {x['n_U']}/{x['n_D']} | `{x['status']}` | "
            f"{fmt(x['bio01']['beta_D_minus_U_sd_range'])} | {fmt(x['bio01']['p_range'])} | "
            f"{fmt(x['bio12']['beta_D_minus_U_sd_range'])} | {fmt(x['bio12']['p_range'])} | "
            f"{fmt(x['bio15']['beta_D_minus_U_sd_range'])} | {fmt(x['bio15']['p_range'])} |"
        )
    lines.extend([
        "",
        "## Phylogeny saturation",
        "",
        "The alias-expanded panel was propagated through the regenerated concatenated UFBoot ensemble, complete public locus trees, ASTRAL from the 153 loci and the independent Chang 2026 overlap topology. Raw `.ufboot` trees are topology-only; single-locus fitted branch lengths remain a covariance-geometry stress test rather than a preferred species-level metric.",
        "",
        "## Interpretation boundary",
        "",
        payload["decision"],
        "",
        "This result does not replace the frozen GBIF-only primary by selecting a favourable source tier. It quantifies how taxonomic-name recovery and public occurrence coverage alter the estimable panel and distinguishes BIO12 amount from BIO15 seasonality.",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    a = parse_args()
    items = load_jsons(a.artifact_root)
    reaches = choose_reaches(items)
    tiers = {name: reach_summary(*pair) for name, pair in reaches.items()}
    topo = topology_summary(items)
    payload = {
        "contract_version": "fdt4_taiwan_alias_public_occurrence_result_v1",
        "status": "FROZEN_SUPPORTING_SENSITIVITY_PRIMARY_UNCHANGED",
        "provenance": {
            "workflow_run_id": a.source_run,
            "artifact_id": a.source_artifact_id,
            "artifact_json_files_scanned": len(items),
        },
        "occurrence_tiers": tiers,
        "topology_saturation": topo,
        "decision": "Taxonomic-alias recovery is an admissible public-data sensitivity, not an outcome-selected primary replacement. BIO12, BIO15 and BIO1 are reported separately, and panel-matched topology saturation is retained as a robustness layer rather than counted as independent ecological replication.",
        "claim_boundary": "Present-day correspondence only; no adaptation, fitness effect, historical climate causation or independent convergence is established.",
    }
    a.out_json.parent.mkdir(parents=True, exist_ok=True)
    a.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_md(payload, a.out_md)
    print(json.dumps({"status": payload["status"], "tiers": {k: {q: v[q] for q in ("status", "n_taxa", "n_U", "n_D")} for k, v in tiers.items()}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
